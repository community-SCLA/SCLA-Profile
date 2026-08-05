#!/usr/bin/env python3
"""make_timing.py — compute timing.json from the REAL clip durations.

Never hand-tune a number here. Every value below is derived from
audio_meta.json (what the engine actually returned) plus four declared
constants, so re-running after a re-synthesis reproduces the timeline exactly.

It also pads the FINAL clip's wav so the release of the last word is IN THE
FILE (check_boundaries `audio-tail-clipped`): on the freeform lane there is no
mixdown, so the video running longer is not a substitute.

    python3 make_timing.py            # writes timing.json, prints the grid
"""
import json
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent

LEAD = 0.60      # s of silence before the first word lands
GAP = 0.55       # s between one clip ending and the next starting
PRE = 0.25       # s a beat's picture leads its own audio
FINAL_HOLD = 1.80  # s of real audio after the last spoken word (rules file)
# ...and a SECOND hold, because two armed gates measure the ending from two
# different places and both must clear their floor:
#   check_boundaries `audio-tail-clipped`  wav tail after the last WORD  >= 1.5
#   preflight.check_freeform_timing        total - (audio_start + audio_dur)
#                                          i.e. video tail after the last CLIP
#                                          FILE ends                     >= 1.5
# The first is satisfied by padding the wav (above); the second cannot be —
# padding the wav moves `audio_dur` with it. So the timeline runs on past the
# audio. Net silence after the last spoken word is FINAL_HOLD + VIDEO_HOLD.
VIDEO_HOLD = 1.80


def ffprobe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def pad_final(meta, voice):
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

    # 1. the final clip carries its own hold
    last = voices[order[-1]]
    padded = pad_final(meta, last)
    last["duration_s"] = round(padded, 3)
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
