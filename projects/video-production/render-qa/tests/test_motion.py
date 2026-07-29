#!/usr/bin/env python3
"""test_motion.py — the keep-alive ban, armed.

The ban is the most-violated rule in the repo's history: given 2026-07-14
("I fully want ripples off"), reaffirmed 07-15, and broken the next day by a
session that restored the banned motion so renders would clear the stagnation
gate. Three MP4s shipped with it and one was published. It was written in
design-contract.md, in `.claude/rules/video-production.md`, AND in comments inside the
very templates that violated it — prose lost to a gate three times over.

On 2026-07-29 the owner's instruction was to make the motion unselectable
rather than better policed: "can we just get rid of that hyperframe element so
it's not ever used?" So the six sites were deleted from the templates, and
`check_motion.py` keeps them deleted.

These assertions are what makes that real. The live design system passing is
NOT proof — it would pass if the checker returned nothing at all. Each case
here crafts the defect and asserts a POSITIVE finding.

Run:  python3 tests/test_motion.py   (exit 0 = all pass)
"""
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_motion              # noqa: E402
from firing import fires         # noqa: E402

DESIGN_SYSTEM = RQ.parent / "design-system"

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}\n        {detail}")


def rules(html):
    return {f["rule"] for f in check_motion.grade(html)}


def tween(target, opts):
    return f"<script>(function(){{ tl.fromTo({target}, {{ y: 0 }}, {opts}, 0); }})();</script>"


BOB = '{ y: -10, duration: 2.7, ease: "sine.inOut", yoyo: true, repeat: 3 }'
ONCE = '{ y: -10, duration: 2.7, ease: "sine.inOut" }'

# ---------------------------------------------------------------------------
print("== the ban fires on content ==")

fires(check, "check_motion", "keep-alive-motion",
      "a repeating tween on the living-icon hero FAILS",
      "keep-alive-motion" in rules(tween('"#cc-iconwrap"', BOB)),
      str(rules(tween('"#cc-iconwrap"', BOB))))

check("a repeating tween on a text node FAILS",
      "keep-alive-motion" in rules(tween('"#sm-statement"', BOB)))
check("a repeating tween on a card/node FAILS",
      "keep-alive-motion" in rules(tween('"#cm-node-1"', BOB)))
check("an array of content targets FAILS",
      "keep-alive-motion" in rules(tween('["#cd-heading", "#cd-chips"]', BOB)))
check("`repeat: -1` (infinite) on content FAILS",
      "keep-alive-motion" in rules(
          tween('"#cc-iconwrap"', '{ y: -10, duration: 2.7, repeat: -1 }')))

print("== ...and does not fire on what design-contract.md sanctions ==")
check("a one-shot entrance on content PASSES",
      not rules(tween('"#cc-iconwrap"', ONCE)))
check("`repeat: 0` is a one-shot, not keep-alive",
      not rules(tween('"#sm-statement"',
                      '{ y: -10, duration: 0.4, repeat: 0 }')))
check("ring-breath on decoration PASSES",
      not rules(tween('"#t-ring-1"', BOB)))
check("ghost-layer depth drift PASSES",
      not rules(tween('"#cd-ghost"', BOB)))
check("a declared exception is honoured",
      not rules(tween('"#cc-iconwrap"', BOB).replace(
          ");", "); /* motion-allow: deliberate, owner-approved */", 1)))

print("== the laundering vector: a content tween routed through a helper ==")
# scla-condition passed the living-icon hero through the SAME drift() helper as
# the genuinely decorative #cd-ghost, which is much of why a content tween read
# as background motion for two weeks. A gate that stops at the helper body sees
# one anonymous `sel` and grades neither call.
helper = """<script>(function(){
  var drift = function (sel, ax, ay, per) {
    tl.fromTo(sel, { x: 0, y: 0 }, { x: ax, y: ay, duration: per,
      ease: "sine.inOut", yoyo: true, repeat: 4 }, 0);
  };
  drift("#cd-ghost", 24, 14, 3.2);
  drift("#cd-iconwrap", 0, -10, 2.7);
})();</script>"""
found = check_motion.grade(helper)
check("a bob laundered through the drift() helper is still caught",
      any(f["rule"] == "keep-alive-motion" and "#cd-iconwrap" in f["detail"]
          for f in found), str(found))
check("...and the decorative call through the SAME helper is not flagged",
      not any("#cd-ghost" in f["detail"] for f in found), str(found))
check("the finding names the helper it came through",
      any("drift()" in f["detail"] for f in found), str(found))

print("== an unreadable target is a coverage hole, not a pass ==")
fires(check, "check_motion", "undeclared-target",
      "a repeating tween on an unresolvable target FAILS rather than passing",
      "undeclared-target" in rules(tween("someComputedThing", BOB)),
      str(rules(tween("someComputedThing", BOB))))

print("== comments are not code ==")
# This gate's own first version matched `drift(\"#cd-iconwrap\", …)` inside the
# comment RECORDING ITS REMOVAL and reported the template still in violation —
# the same comment-blindness that let check-enforcement's invokers() count a
# checker mentioned in a comment as invoked.
commented = """<script>(function(){
  // REMOVED 2026-07-29 (owner): tl.fromTo("#cc-iconwrap", { y: 0 },
  // { y: -10, yoyo: true, repeat: 3 }, 0);
  tl.fromTo("#cc-heading", { opacity: 0 }, { opacity: 1, duration: 0.4 }, 0);
})();</script>"""
check("a removal recorded in a comment does not read as a live violation",
      not rules(commented), str(check_motion.grade(commented)))

print("== the live design system ==")
report, problems = check_motion.check(DESIGN_SYSTEM)
check("every scla-* template is clean of keep-alive motion",
      not problems, "\n        ".join(str(p) for p in problems))
check("the gate actually looked at the templates (a zero-tween PASS is a lie)",
      report and report["graded"] > 100,
      f"graded {report['graded'] if report else 0} tween(s)")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
