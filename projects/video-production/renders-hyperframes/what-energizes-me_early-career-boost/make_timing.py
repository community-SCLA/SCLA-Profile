#!/usr/bin/env python3
"""make_timing.py — compute timing.json from the REAL clip durations.

Never hand-tune a number here. Every value below is derived from
audio_meta.json (what the engine actually returned) plus five declared
constants, so re-running after a re-synthesis reproduces the timeline exactly.

It also pads the FINAL clip's wav so the release of the last word is IN THE
FILE (check_boundaries `audio-tail-clipped`): on the freeform lane there is no
mixdown, so the video running longer is not a substitute.

    python3 make_timing.py            # writes timing.json, prints the grid
"""
import json
import statistics
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent

LEAD = 0.60      # s of silence before the first word lands
# GAP is small here BY MEASUREMENT, not by taste: this lesson runs 40 short
# beats, and the HeyGen clips arrive UNTRIMMED — each already carries its own
# lead-in and tail silence. The audible pause between two beats is
# clip_tail + GAP + next clip's lead-in, so the reference build's 0.55 (17 long
# beats, trimmed clips) would land ~1.0s of dead air between one-line
# sentences. 0.38 keeps every boundary above check_boundaries' MIN_AIR (0.2)
# and MIN_QUESTION_AIR (0.35) — both re-measured below and printed — while
# holding the beat rate the pace gate asks for.
GAP = 0.38
PRE = 0.22       # s a beat's picture leads its own audio
FINAL_HOLD = 1.80  # s of real audio after the last spoken word (rules file)
# ...and a SECOND hold, because two armed gates measure the ending from two
# different places and both must clear their floor:
#   check_boundaries `audio-tail-clipped`  wav tail after the last WORD  >= 1.5
#   preflight.check_timing                 total - (audio_start + audio_dur)
#                                          i.e. video tail after the last CLIP
#                                          FILE ends                     >= 1.5
# The first is satisfied by padding the wav (below); the second cannot be —
# padding the wav moves `audio_dur` with it. So the timeline runs on past the
# audio. Net silence after the last spoken word is FINAL_HOLD + VIDEO_HOLD.
VIDEO_HOLD = 1.80


def ffprobe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def pad_final(voice):
    """Give the last clip FINAL_HOLD seconds of real silence after its last
    word, in the file. Idempotent: re-running never stacks another pad on."""
    wav = WS / voice["path"]
    last_word = max(float(w["end"]) for w in voice["words"])
    want = round(last_word + FINAL_HOLD, 3)
    have = ffprobe(wav)
    if have >= want - 0.01:
        return have
    tmp = wav.with_suffix(".padded.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(wav),
         "-af", f"apad=whole_dur={want}", str(tmp)], check=True)
    tmp.replace(wav)
    return ffprobe(wav)


def main():
    meta = json.loads((WS / "audio_meta.json").read_text())
    req = json.loads((WS / "audio_request.json").read_text())
    order = [ln["id"] for ln in req["lines"]]
    voices = {v["id"]: v for v in meta["voices"]}
    missing = [b for b in order if b not in voices]
    if missing:
        print(f"FAIL: no synthesized clip for {', '.join(missing)}", file=sys.stderr)
        return 2

    # 1. the final clip carries its own hold
    last = voices[order[-1]]
    last["duration_s"] = round(pad_final(last), 3)
    meta["total_duration_s"] = round(
        sum(voices[i]["duration_s"] for i in order), 3)
    (WS / "audio_meta.json").write_text(json.dumps(meta, indent=1) + "\n")

    # 2. lay the clips out end to end with a declared gap
    rows, t = [], LEAD
    for bid in order:
        v = voices[bid]
        rows.append({"id": bid, "audio_start": round(t, 3),
                     "audio_dur": round(v["duration_s"], 3)})
        t += v["duration_s"] + GAP

    # 3. the picture leads its own audio by PRE; beat windows tile
    total = round(rows[-1]["audio_start"] + voices[order[-1]]["duration_s"]
                  + VIDEO_HOLD, 3)
    for i, r in enumerate(rows):
        r["vis_start"] = 0.0 if i == 0 else round(r["audio_start"] - PRE, 3)
    for i, r in enumerate(rows):
        end = rows[i + 1]["vis_start"] if i + 1 < len(rows) else total
        r["vis_dur"] = round(end - r["vis_start"], 3)

    (WS / "timing.json").write_text(
        json.dumps({"total": total, "rows": rows}, indent=1) + "\n")

    airs = []
    for i, r in enumerate(rows):
        v = voices[r["id"]]
        spoken_end = r["audio_start"] + max(float(w["end"]) for w in v["words"])
        air = r["vis_start"] + r["vis_dur"] - spoken_end
        airs.append(air)
        q = "?" if v["words"] and req["lines"][i]["text"].rstrip("\"')]").endswith("?") else " "
        print(f"{r['id']}{q} vis {r['vis_start']:7.3f} +{r['vis_dur']:6.3f}   "
              f"audio {r['audio_start']:7.3f} +{r['audio_dur']:6.3f}   "
              f"air {air:5.2f}s")
    durs = [r["vis_dur"] for r in rows]
    print(f"total {total}s · {len(rows)} beats · "
          f"{len(rows) * 60 / total:.2f} beats/min · median {statistics.median(durs):.2f}s · "
          f"longest {max(durs):.2f}s · min air {min(airs[:-1]):.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
