#!/usr/bin/env python3
"""test_mutations.py — the scope-differential pin on the conjunction rule.

The full mutation harness — plant a defect in a 20-scene plan, recompile it
against the live templates, assert exactly one rule fires — retired with the
scenes.json compiler and the template lane on 2026-08-05 (decisions/log.md;
the harness and its base fixture are provenance under render-qa/_archive/).
Per-checker firing proofs live in test_gates.py / test_freeform.py and are
mandated by test_firing_coverage.py.

What stays is the one assertion no toy fixture can carry: the conjunction rule
is graded on the JOINED narration stream, never per scene. Scoped per scene it
silently disables itself — a seven-item list split 3/2/2 leaves no run reaching
the >=3 threshold, which is exactly how the owner's most-repeated complaint
("Mentorship? Growth?" with no 'or') shipped once already. Both halves are
pinned: the joined stream catches the split, AND no single scene alone does.

Run:  python3 tests/test_mutations.py   (exit 0 = all pass)
"""
import sys
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))

import check_copy          # noqa: E402

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}\n        {detail}")


print("== the differential guarantee ==")
# If check_copy's conjunction scoping ever reverts to per-scene, the first
# assertion stops firing — and the second states plainly that the joined
# stream is what makes it work.
stream_scenes = [
    {"id": "scene-90", "narration": "Do you care most about learning? Security? Income?", "variables": {}},
    {"id": "scene-91", "narration": "Flexibility? Meaning?", "variables": {}},
    {"id": "scene-92", "narration": "Mentorship? Growth?", "variables": {}},
]
joined = check_copy.enumeration_problems(stream_scenes)
check("the 3/2/2 split is caught on the JOINED stream",
      any(getattr(p, "rule_id", "") == "missing-conjunction" for p in joined),
      str(joined))
per_scene = [p for sc in stream_scenes
             for p in check_copy.enumeration_problems([sc])]
check("...and NO single scene reaches the threshold alone — which is exactly "
      "why per-scene scoping silently disabled this rule",
      not per_scene, str(per_scene))

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
