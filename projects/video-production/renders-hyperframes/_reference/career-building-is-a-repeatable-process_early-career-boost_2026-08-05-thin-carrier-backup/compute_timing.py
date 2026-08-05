#!/usr/bin/env python3
"""Compute timing.json from audio_meta.json durations — never hand-tuned.

Beats are laid end to end in manifest order; each beat's visual window equals
its audio window. The final clip's wav carries its own trailing hold (>=1.8s
after the last spoken word), so the final visual hold is inside vis_dur.
Re-run after any re-synthesis.
"""
import json
import pathlib

WS = pathlib.Path(__file__).resolve().parent
meta = json.loads((WS / "audio_meta.json").read_text())
order = [ln["id"] for ln in json.loads((WS / "audio_request.json").read_text())["lines"]]
by_id = {v["id"]: v for v in meta["voices"]}

rows = []
t = 0.0
for beat_id in order:
    dur = float(by_id[beat_id]["duration_s"])
    rows.append({
        "id": beat_id,
        "audio_start": round(t, 3),
        "audio_dur": round(dur, 3),
        "vis_start": round(t, 3),
        "vis_dur": round(dur, 3),
    })
    t += dur

# Timing-level final hold (preflight check_timing): the video's total holds the
# last frame past the final audio clip's end. The wav-level hold (>=1.8s after
# the last spoken word) is additionally inside s37's own padded wav.
FINAL_HOLD = 1.8
out = {"total": round(t + FINAL_HOLD, 3), "rows": rows}
(WS / "timing.json").write_text(json.dumps(out, indent=2) + "\n")
print(f"timing.json: {len(rows)} rows, total {out['total']}s")
