#!/usr/bin/env python3
"""test_pace.py — firing proofs for check_pace.py, the idea-rate / carrying-
object gate (BUILD-PLAN B1, 2026-08-04).

check_pace.py exists because the owner reviewed two freeform cuts of the same
lesson, approved one and called the other "SO boring", and every gate in
`render-qa/src/` passed the boring one while QUARANTINING the approved one —
the gate set measured animacy, the owner was responding to structure. Fixtures
here are synthetic (a timing.json with planted beat durations, and generated
stills for carrier-drift), same discipline as test_diversity.py: no font or
render dependency, so this suite runs anywhere.

Run:  python3 tests/test_pace.py   (exit 0 = all pass)
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))

from PIL import Image, ImageDraw

import check_pace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from firing import fires as _fires

PASS = FAIL = 0
TMP = Path(tempfile.gettempdir()) / "scla-pace-tests"
NAVY = (10, 30, 47)
W, H = 480, 270


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def fires(checker, rule, label, cond, detail=""):
    return _fires(check, checker, rule, label, cond, detail)


def rules_of(problems):
    return {getattr(p, "rule_id", "?") for p in (problems or [])}


def workspace(name, rows, total=None):
    ws = TMP / name
    shutil.rmtree(ws, ignore_errors=True)
    ws.mkdir(parents=True)
    data = {"rows": [{"id": rid, "vis_dur": d} for rid, d in rows]}
    if total is not None:
        data["total"] = total
    (ws / "timing.json").write_text(json.dumps(data))
    return ws


def still(path, offset):
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    for x in range(60 + offset, 60 + offset + 120, 3):
        draw.line((x, 90, x, 150), fill=(255, 255, 255))
    img.save(path)


def snapshots(ws, offsets):
    d = ws / "snapshots"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    for i, off in enumerate(offsets):
        still(d / f"f{i*5:07.2f}s_s{i:02d}_mid.png", off)


# ---------------------------------------------------------------------------
# 1. nothing-graded — no timing.json at all is a FAIL, never a pass.
empty = TMP / "no-timing"
shutil.rmtree(empty, ignore_errors=True)
empty.mkdir(parents=True)
report, problems = check_pace.check_timing(empty)
fires("check_pace", "nothing-graded",
      "a workspace with no timing.json returns report=None and FAILS",
      report is None and "nothing-graded" in rules_of(problems),
      f"report={report} problems={problems}")

# ---------------------------------------------------------------------------
# 2. beat-pace — few, long beats: median too high AND bpm too low at once,
#    matching the rejected reference cut's own shape (17 beats / 157.5s).
slow = workspace("slow", [(f"s{i:02d}", 10.0) for i in range(5)], total=50.0)
report, problems = check_pace.check_timing(slow)
fires("check_pace", "beat-pace",
      "5 beats of 10.0s each (median 10s > 7s ceiling, 6 bpm < 8 floor) fires",
      "beat-pace" in rules_of(problems), str(problems))
check("...and it reports the real numbers, not a template",
      report and report["median"] == 10.0 and report["bpm"] == 6.0, str(report))

# ---------------------------------------------------------------------------
# 3. long-beat-share — median and bpm both clear their floors, but two very
#    long beats still eat most of the runtime. Proves the rule earns its
#    keep: beat-pace alone would pass this build.
mixed_rows = [(f"s{i:02d}", 1.0) for i in range(18)] + [("s18", 30.0), ("s19", 30.0)]
mixed = workspace("mixed", mixed_rows, total=78.0)
report, problems = check_pace.check_timing(mixed)
check("...median/bpm clear their own floors on this fixture (median<=7, bpm>=8)",
      report["median"] <= 7.0 and report["bpm"] >= 8.0, str(report))
fires("check_pace", "long-beat-share",
      "two 30s beats inside 20 beats (77% of runtime >8s) fires on its own",
      "long-beat-share" in rules_of(problems), str(problems))
check("...and beat-pace does NOT fire on this fixture (it's a distinct rule)",
      "beat-pace" not in rules_of(problems), str(problems))

# ---------------------------------------------------------------------------
# 4. A build shaped like the APPROVED reference cut passes cleanly.
clean_rows = [(f"s{i:02d}", 5.15) for i in range(26)]
clean = workspace("clean", clean_rows, total=152.11)
report, problems = check_pace.check_timing(clean)
check("a build shaped like the approved reference cut passes with no findings",
      report is not None and not problems, str(problems))

# ---------------------------------------------------------------------------
# 5. carrier-drift — over the ceiling: every beat draws an unrelated picture.
drifting = workspace("drifting", [(f"s{i:02d}", 5.0) for i in range(6)])
snapshots(drifting, [0, 240, 40, 280, 10, 260])
report, problems = check_pace.check_stills(drifting)
fires("check_pace", "carrier-drift",
      "consecutive beats redrawing an unrelated picture each time fires "
      "over the churn ceiling",
      "carrier-drift" in rules_of(problems), str(problems))

# ...and the frozen floor: the same rule id, the opposite direction — a
# carrier-drift ceiling with no floor would license a still image, which the
# module docstring explicitly disclaims.
frozen = workspace("frozen-carrier", [(f"s{i:02d}", 5.0) for i in range(6)])
snapshots(frozen, [0, 0, 0, 0, 0, 0])
report, problems = check_pace.check_stills(frozen)
check("...and a frozen carrier (0% churn) ALSO fires carrier-drift, the low end",
      "carrier-drift" in rules_of(problems), str(problems))

# A build shaped like the approved reference cut's own churn (3.34%) passes.
band_offsets = [0, 8, 3, 11, 5, 9]  # small nudges: some churn, nowhere near either edge
carrying = workspace("carrying", [(f"s{i:02d}", 5.0) for i in range(6)])
snapshots(carrying, band_offsets)
report, problems = check_pace.check_stills(carrying)
check("a build with real but modest churn (a re-sorting carrier) passes",
      report is not None and not problems, str(problems))

# ---------------------------------------------------------------------------
# 7. twin-share — the anti-gaming backstop for beat-pace (BUILD-PLAN B2).
#    Deliberately has NO naturally-occurring failing build (it does not
#    discriminate between the two reference cuts), so it is proven ONLY here,
#    by a planted fixture: half the consecutive pairs are pixel-identical
#    ("gamed" beats — split with no visual change) and the rest carry real,
#    modest churn so this does not also trip carrier-drift's ceiling.
gamed = workspace("gamed", [(f"s{i:02d}", 5.0) for i in range(6)])
snapshots(gamed, [0, 0, 15, 15, 30, 45])
report, problems = check_pace.check_stills(gamed)
fires("check_pace", "twin-share",
      "2 of 5 consecutive pairs pixel-identical (40%, over the 25% ceiling) "
      "fires twin-share",
      "twin-share" in rules_of(problems), str(problems))
check("...and it does not also trip carrier-drift on this fixture",
      "carrier-drift" not in rules_of(problems), str(problems))
check("...report carries the raw fraction, not just the verdict",
      report and report.get("twin_share") == 0.4, str(report))

# ---------------------------------------------------------------------------
# 6. carrier-drift nothing-graded — fewer than 3 stills cannot measure drift.
sparse = workspace("sparse-stills", [(f"s{i:02d}", 5.0) for i in range(2)])
snapshots(sparse, [0, 50])
report, problems = check_pace.check_stills(sparse)
check("fewer than 3 stills returns report=None and FAILS (nothing-graded)",
      report is None and "nothing-graded" in rules_of(problems),
      f"report={report} problems={problems}")

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
