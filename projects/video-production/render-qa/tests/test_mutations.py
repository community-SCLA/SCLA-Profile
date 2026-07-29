#!/usr/bin/env python3
"""test_mutations.py — does each rule still catch the defect it was written for?

This is what catches "a checker stopped being a checker." The firing fixtures in
test_gates.py prove a rule CAN fire; they do not prove it still fires on a real
video. A toy fixture cannot: the natural fixture for the conjunction rule is one
scene with three items and no "or", which fires fine even under the broken
per-scene scoping that let the owner's most-repeated complaint ship. Scope and
sampling bugs only manifest at real length.

BASE FIXTURE: tests/fixtures/base/scenes.json — the 20-scene 2026-07-29
`better-decisions` plan, gate-clean and pending owner sign-off (never
"approved"; see that folder's README). The PLAN is stored, not a workspace:
build_index.py recompiles it against the live design-system/ on every run, so a
template edit that breaks it goes red instead of diverging quietly.

FOUR HARNESS RULES, each load-bearing:

  1. ASSERTIONS ARE DIFFERENTIAL AND PER-RULE. Rule R must fire on the mutant
     AND not fire on the baseline. A global pass/fail assertion stays green
     while the rule you care about is deleted, because sibling rules in the
     same checker fire on the same mutant.
  2. THE LIVE compositions/ ARE COPIED IN. Without templates, check_slots
     prints a clean PASS on zero templates and check_capacity / check_text-size
     silently no-op. A corpus that proves nothing while going green is worse
     than none.
  3. check_continuity IS CALLED WITH static=True on an uncompiled plan.
     Without it the placeholder data-duration="1" yields 18 findings on a
     gate-clean plan — 100% false positives.
  4. tempfile.mkdtemp(), never a fixed /tmp path. The fixed paths in
     run_tests.py and test_gates.py collide under parallel runs.

Checkers are called IN-PROCESS (~2s on a 2.2s suite); shelling out to
preflight.py would cost ~0.65s x N.

Run:  python3 tests/test_mutations.py   (exit 0 = all pass)
"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import boxmodel            # noqa: E402
import check_capacity      # noqa: E402
import check_continuity    # noqa: E402
import check_copy          # noqa: E402
import check_geometry      # noqa: E402
import check_slots         # noqa: E402
import check_text          # noqa: E402
import check_variety       # noqa: E402
import preflight           # noqa: E402
from hfp_common import parse_scenes  # noqa: E402

BASE_JSON = Path(__file__).resolve().parent / "fixtures" / "base" / "scenes.json"
DESIGN_SYSTEM = RQ.parent / "design-system"

PASS = FAIL = 0
TMP = Path(tempfile.mkdtemp(prefix="scla-mutations-"))


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}\n        {detail}")


# ---------------------------------------------------------------------------
def materialize(plan: dict, name: str) -> Path:
    """Compile a plan into a real workspace against the LIVE design system."""
    ws = TMP / name
    ws.mkdir(parents=True, exist_ok=True)
    shutil.copytree(DESIGN_SYSTEM / "compositions", ws / "compositions",
                    dirs_exist_ok=True)                        # harness rule 2
    shutil.copy(DESIGN_SYSTEM / "frame.md", ws / "frame.md")
    (ws / "scenes.json").write_text(json.dumps(plan, indent=2))
    r = subprocess.run([sys.executable, str(RQ / "build_index.py"), str(ws)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"build_index failed for {name}:\n{r.stdout}\n{r.stderr}")
    return ws


def rules_fired(ws: Path) -> set:
    """Every rule_id the static checkers return for this workspace.

    Typed rule_ids, not substrings: Phase 3 exists so these assertions key on
    something that does not move when a message is reworded.
    """
    out = set()
    scenes = parse_scenes((ws / "index.html").read_text())

    def add(findings):
        for f in findings:
            out.add(getattr(f, "rule_id", "unclassified"))

    add(check_copy.heading_problems(scenes))
    add(check_copy.enumeration_problems(scenes))
    add(check_continuity.check(ws, static=True))               # harness rule 3
    add(check_variety.check(ws)[0])
    add(check_capacity.check(ws))
    add(check_geometry.check(ws)[1])
    add(check_text.check_restatement(scenes)[0])
    slots, _ = check_slots.check(ws)
    for f in slots:
        out.add(f.get("rule_id", "unclassified"))
    return out


BASE_PLAN = json.loads(BASE_JSON.read_text())
base_ws = materialize(copy.deepcopy(BASE_PLAN), "baseline")
BASELINE = rules_fired(base_ws)
print(f"baseline: {len(BASE_PLAN['scenes'])} scenes, "
      f"{len(BASELINE)} rule(s) firing {sorted(BASELINE) or '(none — gate-clean)'}\n")
check("the base fixture is gate-clean (it is the control, so it must be)",
      not BASELINE, str(sorted(BASELINE)))


def mutate(label, rule_id, fn, expect_absent_from_baseline=True):
    """Apply fn to a deep copy of the plan; assert rule_id fires on the mutant
    and did NOT fire on the baseline. That pair is the whole point: a rule that
    fires on everything proves nothing."""
    plan = copy.deepcopy(BASE_PLAN)
    fn(plan)
    try:
        ws = materialize(plan, label.replace(" ", "_")[:40])
    except RuntimeError as exc:
        check(f"{label} -> {rule_id}", False, f"mutant did not compile: {exc}")
        return
    fired = rules_fired(ws)
    ok = rule_id in fired
    if expect_absent_from_baseline and rule_id in BASELINE:
        check(f"{label} -> {rule_id}", False,
              f"{rule_id} fires on the BASELINE too — the assertion is not "
              f"differential and proves nothing")
        return
    check(f"{label} -> {rule_id}", ok,
          f"expected {rule_id}; mutant fired {sorted(fired)}")


def scene_by_template(plan, template):
    for s in plan["scenes"]:
        if s["template"] == template:
            return s
    raise AssertionError(f"no {template} scene in the base plan")


# ---------------------------------------------------------------------------
print("== the nine mutations, each reproducing a real defect ==")

# 1. THE ONE THAT MATTERS. Split an enumeration 3/2/2 across three scenes. No
#    single scene reaches the >=3 threshold, so the per-scene scoping that
#    shipped the owner's most-repeated complaint passes this. The joined-stream
#    rule must still catch it.
def split_enumeration(plan):
    chips = scene_by_template(plan, "scla-chips")
    i = plan["scenes"].index(chips)
    a = copy.deepcopy(chips)
    b = copy.deepcopy(chips)
    c = copy.deepcopy(chips)
    a["id"], b["id"], c["id"] = "scene-90", "scene-91", "scene-92"
    a["narration"] = "Do you care most about learning? Security? Income?"
    b["narration"] = "Flexibility? Meaning?"
    c["narration"] = "Mentorship? Growth?"
    for s in (a, b, c):
        s["vars"] = dict(s["vars"], chips="one,two,three", subBeats="")
        s.pop("cues", None)
    plan["scenes"][i:i + 1] = [a, b, c]


mutate("enumeration split 3/2/2 across three scenes", "missing-conjunction",
       split_enumeration)

# 2. A text collision at scene 15 — deep enough that a 9-point sampler misses it.
def collide(plan):
    loop = scene_by_template(plan, "scla-loop")
    loop["vars"] = dict(loop["vars"],
                        step3="Grounded in what you value and in what you need",
                        subBeats="Use it on any career decision you ever face")


mutate("a text collision on the loop captions", "text-collision", collide)

# 3. Two scenes renamed into clones of one family -> variety.
def clone_family(plan):
    for s in plan["scenes"]:
        if s["template"] in ("scla-points", "scla-morph", "scla-condition",
                             "scla-career-map", "scla-loop", "scla-chips"):
            s["template"] = "scla-statement"
            s["vars"] = {"theme": "summit",
                         "statement": "One More Statement Scene",
                         "lines": "first line|second line",
                         "sceneIndex": s["vars"].get("sceneIndex", "00 / X")}
            s.pop("cues", None)


mutate("every content scene collapsed onto one family", "too-few-forms",
       clone_family)
mutate("every content scene collapsed onto one family", "consecutive-run",
       clone_family)
mutate("every content scene collapsed onto one family", "form-share",
       clone_family)

# 4. A chip restating its heading -> check_text.
def restate(plan):
    chips = scene_by_template(plan, "scla-chips")
    chips["vars"] = dict(chips["vars"],
                         heading="One Right Answer",
                         chips="One right answer,Another thing,A third thing")
    chips.pop("cues", None)


mutate("a chip restating its own heading", "restates-heading", restate)

# 5. Two scenes pointed at ONE shared template file — the 2026-07-27 collision
#    defect. build_index.py gives every slot its own instance file, so this
#    mutation asserts the COMPILER still does that rather than a checker.
def shared_template(plan):
    pass  # asserted below, outside mutate(): it is a compiler property


ws = materialize(copy.deepcopy(BASE_PLAN), "instances")
srcs = [t for t in (ws / "index.html").read_text().split('data-composition-src="')[1:]]
srcs = [s.split('"')[0] for s in srcs]
check("instance_templates wiring: every scene slot gets its OWN template file",
      len(srcs) == len(set(srcs)),
      f"{len(srcs)} slots share {len(set(srcs))} files: "
      f"{sorted({s for s in srcs if srcs.count(s) > 1})}")

# 6. Push a card past frame-padding -> the token armed in Phase 2.
def past_padding(plan):
    cm = scene_by_template(plan, "scla-career-map")
    cm["vars"] = dict(cm["vars"],
                      startLabel="A start label long enough to run past the inset "
                                 "and keep going well beyond it")


mutate("a career-map card pushed past its box", "slot-over-maxlines",
       past_padding)


# 6b. ...and the frame-padding token itself, at full length. The capacity gate
#     catches copy that outgrows its declared maxLines; this catches a box
#     PLACED outside the inset, which is the other half and the half that was
#     enforced by nothing until 2026-07-29. The defect is in the CSS, not the
#     plan, so it is injected into the compiled workspace rather than mutated
#     through scenes.json.
ws = materialize(copy.deepcopy(BASE_PLAN), "padding")
# build_index.py gives every slot its OWN template file and namespaces the ids
# (sm- -> sm__i2-), so inject into each statement composition using the id that
# file actually carries — a hard-coded #sm-block would silently miss every
# instance and this mutation would test nothing.
#
# TARGET THE POSITIONED CONTAINER, NOT THE HEADING. `left` moves an element
# only if it is out of normal flow; #sm-statement is a static child of the
# absolutely-positioned #sm-block, so `#sm-statement { left: 90px }` is inert
# and the mutation reported a checker failure that was really its own. The
# assertion below is the guard: the patched element must actually be
# absolutely positioned.
patched = 0
for target in sorted((ws / "compositions").glob("scla-statement*.html")):
    src = target.read_text()
    m = re.search(r'id="(sm[\w-]*-block)"', src)
    if not m:
        continue
    doc = boxmodel.Doc(src)
    node = next((n for n in doc.nodes if n["id"] == m.group(1)), None)
    check(f"{target.name}: the padding mutation's target is out of normal flow",
          node is not None
          and doc.decls(node).get("position") in ("absolute", "fixed"),
          f"#{m.group(1)} is statically positioned — `left` would be inert and "
          f"this mutation would assert nothing")
    # Move the content block hard against the left edge: inside the 120px
    # inset, still clear of the 72px keep-out, so this trips padding-breach and
    # only padding-breach.
    #
    # Injected before the LAST </style>, not the first: these templates carry
    # two style blocks (@font-face, then the rules), boxmodel resolves "later
    # rules win", and a `replace(..., 1)` landed the override in the font block
    # ahead of the template's own `left: 120px`, where it was silently
    # discarded — the exact failure this comment had warned about.
    cut = src.rindex("</style>")
    target.write_text(f"{src[:cut]}#{m.group(1)} {{ left: 90px; }}\n{src[cut:]}")
    patched += 1
check("the padding mutation actually patched the statement templates",
      patched > 0, "no scla-statement composition carried a *-block id")
fired = rules_fired(ws)
check("a body box placed inside the 120px content inset -> padding-breach",
      "padding-breach" in fired and "safe-area-breach" not in fired,
      f"fired {sorted(fired)}")

# 7. Lowercase a heading -> Title Case, armed with no fixture until this build.
def lowercase_heading(plan):
    for s in plan["scenes"]:
        if "heading" in s.get("vars", {}) and s["vars"]["heading"]:
            s["vars"]["heading"] = s["vars"]["heading"].lower()
            return
    raise AssertionError("no heading slot in the base plan")


mutate("a heading lowercased", "heading-not-title-case", lowercase_heading)

# 8. Blank a declared slot -> check_slots (the fabrication class).
def drop_slot(plan):
    pts = scene_by_template(plan, "scla-points")
    pts["vars"] = {k: v for k, v in pts["vars"].items()
                   if k not in ("point4", "point3")}


mutate("a declared slot dropped from the plan", "unfilled-slot", drop_slot)

# 9. script_match pointed at a missing script. THE LIVE BUG: this branch
#    returned pass:True with a WARN, so the render-stage half of the
#    fabrication ban disarmed itself exactly when it could not verify.
missing = TMP / "no-such-script.txt"
res = preflight.check_script_match(base_ws, script_path=missing)
check("script_match with an explicitly missing --script FAILS",
      res["pass"] is False, str(res))
res = preflight.check_script_match(base_ws, scripts_root=TMP / "empty-library")
check("script_match with NO locatable approved script FAILS (was WARN-and-pass)",
      res["pass"] is False, str(res))


# ---------------------------------------------------------------------------
print("\n== the differential guarantee ==")
# The rule the whole phase exists for. If check_copy's conjunction scoping ever
# reverts to per-scene, mutation 1 stops firing — and this states plainly that
# the joined stream is what makes it work.
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

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
