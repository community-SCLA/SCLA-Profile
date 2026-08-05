#!/usr/bin/env python3
"""compute_timing.py — derive timing.json from the real narration durations.

Freeform lane, step 5. Every number in timing.json is COMPUTED here from
audio_meta.json; nothing is hand-tuned. Re-run after any re-synthesis.

Policy:
  * LEAD_IN      the title card holds before the first word.
  * GAP          air between two beats inside one act.
  * ACT_GAP      air at an act boundary (a new visual state needs longer).
  * FINAL_HOLD   air after the last word. tokens: the gate floor is 1.5s and
                 the owner rejected a 1.1s ending twice; the producer target
                 is 1.8s, so this build holds 2.0s.

Visual spans tile [0, total] with no gap and no overlap, and each beat's visual
window opens LEAD slightly before its own audio so an arrival pinned to the
first word is already on the timeline.

Usage:  python3 compute_timing.py        (from the workspace root)
"""
import json
from pathlib import Path

LEAD_IN = 0.90
GAP = 0.38
ACT_GAP = 0.95
FINAL_HOLD = 2.00
LEAD = 0.25          # visual window opens this long before the beat's audio

# First beat of each act — these boundaries get ACT_GAP instead of GAP.
ACT_STARTS = {"s04", "s09", "s16", "s20"}

ws = Path(__file__).resolve().parent
meta = json.loads((ws / "audio_meta.json").read_text())
order = [ln["id"] for ln in json.loads((ws / "audio_request.json").read_text())["lines"]]
dur = {v["id"]: float(v["duration_s"]) for v in meta["voices"]}
missing = [i for i in order if i not in dur]
if missing:
    raise SystemExit(f"no synthesized audio for: {', '.join(missing)}")

rows, t = [], LEAD_IN
for i, bid in enumerate(order):
    if i:
        t += ACT_GAP if bid in ACT_STARTS else GAP
    rows.append({"id": bid, "audio_start": round(t, 3), "audio_dur": round(dur[bid], 3)})
    t += dur[bid]

total = round(t + FINAL_HOLD, 3)

for i, r in enumerate(rows):
    vis_start = 0.0 if i == 0 else round(r["audio_start"] - LEAD, 3)
    r["vis_start"] = vis_start
for i, r in enumerate(rows):
    end = total if i == len(rows) - 1 else rows[i + 1]["vis_start"]
    r["vis_dur"] = round(end - r["vis_start"], 3)

(ws / "timing.json").write_text(
    json.dumps({"total": total, "rows": rows}, indent=2) + "\n")

last = rows[-1]
print(f"beats            {len(rows)}")
print(f"total            {total}s")
print(f"last word ends   {round(last['audio_start'] + last['audio_dur'], 3)}s")
print(f"final hold       {round(total - last['audio_start'] - last['audio_dur'], 3)}s")
print(f"beat midpoints   " + ",".join(
    f"{r['vis_start'] + r['vis_dur'] / 2:.2f}" for r in rows))
