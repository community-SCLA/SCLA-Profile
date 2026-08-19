#!/usr/bin/env python3
"""Firing proofs for owner-rejected detached highlights and flex overflow."""
import sys
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_visual_structure  # noqa: E402
from firing import fires  # noqa: E402

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label} {detail}")


def rules(html):
    return {finding["rule"] for finding in check_visual_structure.grade(html)}


fixture = (Path(__file__).parent / "fixtures" / "owner-rejections" /
           "m5-detached-focus-and-flex-overflow.html").read_text()
bad = rules(fixture)
fires(check, "check_visual_structure", "detached-focus-overlay",
      "an empty absolute spotlight border fails",
      "detached-focus-overlay" in bad, str(bad))
fires(check, "check_visual_structure", "flex-child-auto-min-overflow",
      "a growing child can no longer escape a fixed-height flex column",
      "flex-child-auto-min-overflow" in bad, str(bad))

clean = fixture.replace(
    "flex: 1;", "flex: 1; min-height: 0; overflow: hidden;").replace(
    '<div class="spotlight focus-target"></div>',
    '<div class="target-result focused">Worth More</div>').replace(
    "  .spotlight {", "  .unused-spotlight-style {")
check("emphasis on the actual contained element passes", not rules(clean),
      str(check_visual_structure.grade(clean)))

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
