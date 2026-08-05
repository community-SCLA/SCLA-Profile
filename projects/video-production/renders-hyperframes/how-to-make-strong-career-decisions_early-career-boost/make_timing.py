#!/usr/bin/env python3
"""make_timing.py — audio hygiene, then timing.json from the REAL durations.

Never hand-tune a number here. Every value below is derived from what the
engine actually returned (audio_meta.json) plus five declared constants, so
re-running after a re-synthesis reproduces the timeline exactly. Idempotent:
running it twice changes nothing.

TWO PASSES.

1. HYGIENE. `audio.mjs` hands back the provider's raw clips. Oxana puts
   0.7-1.2s of real silence between sentences INSIDE a clip and 0.1-0.4s of
   dead air at each clip edge; on this lesson that was ~22s of the runtime
   spent on silence nobody asked for, and the owner has already reported the
   in-clip form of it as "strange sound gaps / a major glitch or lag"
   (decisions/log.md 2026-07-28). The template lane's synthesiser has fixed
   this since that day — `synth_narration.compress_gaps()` caps in-clip
   silence at MAX_INSCENE_GAP and `synth_narration.trim_clip()` trims the
   edges with guards and fades. The freeform audio engine has no equivalent,
   so this pass CALLS THOSE SAME FUNCTIONS on the per-beat clips rather than
   reimplementing them: one definition of "how long a pause is allowed to be"
   for both lanes. Word timestamps are shifted with the audio, so everything
   downstream (cues, gates, the reveal timings) stays truthful.

2. TIMING. The clips are laid end to end with a declared gap; each beat's
   picture leads its own audio by PRE, and the beat windows tile the runtime.

It also pads the FINAL clip so the release of the last word is IN THE FILE
(`check_boundaries` rule `audio-tail-clipped`): on the freeform lane there is
no mixdown, so the video running longer is not a substitute.

    python3 make_timing.py            # rewrites the clips, writes timing.json
"""
import json
import sys
import wave
from array import array
from pathlib import Path

WS = Path(__file__).resolve().parent
# render-qa/src owns the audio hygiene functions; import, never copy.
sys.path.insert(0, str(WS.parents[1] / "render-qa" / "src"))
from synth_narration import (MAX_INSCENE_GAP, compress_gaps,  # noqa: E402
                             read_wav, trim_clip)

LEAD = 0.60        # s of silence before the first word lands
GAP = 0.65         # s between one clip ending and the next starting
PRE = 0.25         # s a beat's picture leads its own audio
FINAL_HOLD = 1.80  # s of real audio after the last spoken word (rules file)
# ...and a SECOND hold, because two armed gates measure the ending from two
# different places and both must clear their floor:
#   check_boundaries `audio-tail-clipped`  wav tail after the last WORD  >= 1.5
#   preflight.check_timing                 total - (audio_start + audio_dur),
#                                          i.e. video tail after the last CLIP
#                                          FILE ends                     >= 1.5
# The first is satisfied by padding the wav (below); the second cannot be —
# padding the wav moves `audio_dur` with it. So the timeline runs on past the
# audio. Net silence after the last spoken word is FINAL_HOLD + VIDEO_HOLD.
VIDEO_HOLD = 1.80


def write_wav(path, params, data):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(params.nchannels)
        w.setsampwidth(2)
        w.setframerate(params.framerate)
        w.writeframes(data.tobytes())


def hygiene(voice, is_last):
    """Cap in-clip silence, trim the edges, and (on the last clip) give the
    final word FINAL_HOLD seconds of real air. Returns the new duration."""
    path = WS / voice["path"]
    params, data = read_wav(path)
    rate, chan = params.framerate, params.nchannels
    words = [{"text": w["text"], "start": float(w["start"]),
              "end": float(w["end"])} for w in voice["words"]]
    if not words:
        return round(len(data) / chan / rate, 3)

    data, words, cut_s, n_cuts = compress_gaps(
        data, words, rate, chan, MAX_INSCENE_GAP)
    kept, trim_off = trim_clip(data, rate, chan, trim_tail=not is_last)
    words = [{"text": w["text"],
              "start": round(w["start"] - trim_off, 3),
              "end": round(w["end"] - trim_off, 3)} for w in words]

    if is_last:
        want = int(round((max(w["end"] for w in words) + FINAL_HOLD) * rate))
        have = len(kept) // chan
        if have < want:
            kept = kept + array("h", bytes((want - have) * 2 * chan))

    write_wav(path, params, kept)
    dur = round(len(kept) / chan / rate, 3)
    voice["duration_s"] = dur
    voice["words"] = [{"id": f"w{i}", **w} for i, w in enumerate(words)]
    if n_cuts:
        print(f"  {voice['id']}: capped {n_cuts} in-clip gap(s), "
              f"-{cut_s:.2f}s; trimmed {trim_off:.2f}s of lead")
    return dur


def main():
    meta = json.loads((WS / "audio_meta.json").read_text())
    req = json.loads((WS / "audio_request.json").read_text())
    order = [ln["id"] for ln in req["lines"]]
    voices = {v["id"]: v for v in meta["voices"]}

    for i, bid in enumerate(order):
        hygiene(voices[bid], is_last=(i == len(order) - 1))
    meta["total_duration_s"] = round(
        sum(voices[i]["duration_s"] for i in order), 3)
    (WS / "audio_meta.json").write_text(json.dumps(meta, indent=1) + "\n")

    rows, t = [], LEAD
    for bid in order:
        v = voices[bid]
        rows.append({"id": bid, "audio_start": round(t, 3),
                     "audio_dur": round(v["duration_s"], 3)})
        t += v["duration_s"] + GAP

    total = round(rows[-1]["audio_start"] + voices[order[-1]]["duration_s"]
                  + VIDEO_HOLD, 3)
    for i, r in enumerate(rows):
        r["vis_start"] = 0.0 if i == 0 else round(r["audio_start"] - PRE, 3)
    for i, r in enumerate(rows):
        end = rows[i + 1]["vis_start"] if i + 1 < len(rows) else total
        r["vis_dur"] = round(end - r["vis_start"], 3)

    (WS / "timing.json").write_text(
        json.dumps({"total": total, "rows": rows}, indent=1) + "\n")

    for r in rows:
        v = voices[r["id"]]
        spoken_end = r["audio_start"] + max(float(w["end"]) for w in v["words"])
        air = r["vis_start"] + r["vis_dur"] - spoken_end
        print(f"{r['id']}  vis {r['vis_start']:7.3f} +{r['vis_dur']:6.3f}   "
              f"audio {r['audio_start']:7.3f} +{r['audio_dur']:6.3f}   "
              f"air {air:5.2f}s")
    print(f"total {total}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
