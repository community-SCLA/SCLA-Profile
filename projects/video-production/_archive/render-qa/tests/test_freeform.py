#!/usr/bin/env python3
"""test_freeform.py — firing proofs for the freeform (agent-native) gate path.

The §1 finding of docs/HANDOFF-agent-native-verdict-2026-07-30.md: a freeform
build carries no data-narration, so every parse_scenes() consumer exited 0
having graded NOTHING — the same nothing-graded failure this repo has hit four
times. The fix is the beat-manifest adapter in hfp_common (audio_request.json +
timing.json) plus on-frame markup extraction. Every case below proves a
re-pointed rule actually FIRES on freeform input; the clean fixture proves the
adapter does not false-flag.

Run:  python3 tests/test_freeform.py   (exit 0 = all pass)
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))

import check_continuity
import check_copy
import check_motion
from hfp_common import load_beats, onframe_strings

sys.path.insert(0, str(Path(__file__).resolve().parent))
from firing import fires as _fires

PASS = FAIL = 0
TMP = Path(tempfile.gettempdir()) / "scla-freeform-tests"


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
    return [getattr(p, "rule_id", "unclassified") for p in problems]


INDEX = """<div id="root" data-duration="30">
  <div class="clip" data-composition-src="compositions/main.html"
       data-composition-id="main" data-start="0" data-duration="30"
       data-track-index="0"></div>
</div>"""

CLEAN_COMP = """<template>
  <style>#root { background: #0a1e2f; } .big { font-size: 72px; }</style>
  <div id="root">
    <div class="big" data-role="heading">Four Kinds of Transition</div>
    <p>Same core strengths, new context.</p>
  </div>
</template>
<script>
  window.__timelines = window.__timelines || {};
  var tl = window.__timelines["main"] = gsap.timeline({ paused: true });
  tl.fromTo("#root .big", { opacity: 0 }, { opacity: 1, duration: 0.5 });
</script>"""


def freeform_ws(name, lines, comp_html=CLEAN_COMP, index=INDEX, timing=None,
                manifest=True):
    ws = TMP / name
    shutil.rmtree(ws, ignore_errors=True)
    (ws / "compositions").mkdir(parents=True)
    (ws / "index.html").write_text(index)
    (ws / "compositions" / "main.html").write_text(comp_html)
    if manifest:
        (ws / "audio_request.json").write_text(json.dumps(
            {"provider": "heygen", "lines": lines}))
    if timing:
        (ws / "timing.json").write_text(json.dumps(timing))
    return ws


CLEAN_LINES = [
    {"id": "s01", "text": "You have built years of experience."},
    {"id": "s02", "text": "Career moves come in four kinds, and each asks "
                          "something different of you."},
]

# ---------------------------------------------------------------------------
# The adapter itself
ws = freeform_ws("adapter", CLEAN_LINES,
                 timing={"total": 30.0, "rows": [
                     {"id": "s01", "vis_start": 0.0, "vis_dur": 12.0},
                     {"id": "s02", "vis_start": 12.0, "vis_dur": 18.0}]})
beats = load_beats(ws)
check("load_beats returns one scene-shaped dict per narration line",
      beats is not None and len(beats) == 2
      and beats[0]["narration"].startswith("You have built")
      and beats[1]["duration"] == 18.0, str(beats))
strings = onframe_strings(ws)
check("onframe_strings finds the declared heading with role=heading",
      ("main.html", "heading", "Four Kinds of Transition") in strings,
      str(strings))
check("onframe_strings finds body copy inside <template>, style stripped",
      any(r == "text" and t == "Same core strengths, new context."
          for _, r, t in strings), str(strings))
check("a clean freeform workspace passes check_copy",
      not check_copy.check(ws), str(check_copy.check(ws)))
check("a clean freeform workspace passes check_continuity",
      not check_continuity.check(ws), str(check_continuity.check(ws)))

# ---------------------------------------------------------------------------
# check_copy — narration rules re-armed on beats
ws = freeform_ws("conjunction", [
    {"id": "s01", "text": "What do you care about most?"},
    {"id": "s02", "text": "Security? Income? Flexibility? Meaning? Growth?"},
])
fires("check_copy", "freeform-conjunction",
      "a spoken list in the BEAT MANIFEST ending without and/or fires",
      "missing-conjunction" in rules_of(check_copy.check(ws)),
      str(check_copy.check(ws)))

ws = freeform_ws("retired", [
    {"id": "s01", "text": "This is part of your broader Career Accelerator "
                          "journey and it matters."}])
fires("check_copy", "freeform-retired-name",
      "a retired program name spoken in a beat fires",
      "retired-name" in rules_of(check_copy.check(ws)),
      str(check_copy.check(ws)))

# ---------------------------------------------------------------------------
# check_copy — on-frame rules from markup extraction
bad_heading = CLEAN_COMP.replace(
    '<div class="big" data-role="heading">Four Kinds of Transition</div>',
    '<div class="big" data-role="heading">Broaden your options.</div>')
ws = freeform_ws("heading", CLEAN_LINES, comp_html=bad_heading)
got = rules_of(check_copy.check(ws))
fires("check_copy", "freeform-titlecase",
      "a declared heading in sentence case fires Title Case",
      "heading-not-title-case" in got, str(got))
fires("check_copy", "freeform-heading-period",
      "a declared heading with a terminal period fires",
      "heading-terminal-period" in got, str(got))

ws = freeform_ws("placeholder", CLEAN_LINES,
                 comp_html=CLEAN_COMP.replace(
                     "Same core strengths, new context.",
                     "[[program name]] helps you decide"))
fires("check_copy", "placeholder",
      "a merge-field marker reaching the frame fires placeholder-slot",
      "placeholder-slot" in rules_of(check_copy.check(ws)),
      str(check_copy.check(ws)))

no_heading = CLEAN_COMP.replace(' data-role="heading"', "")
ws = freeform_ws("noheadings", CLEAN_LINES, comp_html=no_heading)
fires("check_copy", "no-headings",
      "a freeform build declaring zero headings fires no-headings-declared",
      "no-headings-declared" in rules_of(check_copy.check(ws)),
      str(check_copy.check(ws)))

ws = freeform_ws("nomanifest", CLEAN_LINES, manifest=False)
fires("check_copy", "nothing-graded",
      "scene slots with no narration AND no beat manifest fail loud",
      "nothing-graded" in rules_of(check_copy.check(ws)),
      str(check_copy.check(ws)))

# ---------------------------------------------------------------------------
# check_continuity — the one beat rule that transfers
ws = freeform_ws("lowercase", [
    {"id": "s01", "text": "Your next step feels less clear because"},
    {"id": "s02", "text": "the ground under it moved."}])
fires("check_continuity", "freeform-opens-lowercase",
      "a beat opening lowercase (sentence cut across synthesis units) fires",
      "opens-lowercase" in rules_of(check_continuity.check(ws)),
      str(check_continuity.check(ws)))

ws = freeform_ws("cont-nothing", CLEAN_LINES, manifest=False)
fires("check_continuity", "nothing-graded",
      "check_continuity fails loud when it can grade nothing",
      "nothing-graded" in rules_of(check_continuity.check(ws)),
      str(check_continuity.check(ws)))

# A complete clause opening on a coordinator is spoken rhetoric, not a split —
# the frame-calibrated 15-word test must NOT transfer to audio-only beats.
ws = freeform_ws("rhetoric", [
    {"id": "s01", "text": "You have accumulated years of experience."},
    {"id": "s02", "text": "But your next step probably feels less clear."}])
check("a coordinator-opening complete clause in a beat does NOT flag",
      not check_continuity.check(ws), str(check_continuity.check(ws)))

# ---------------------------------------------------------------------------
# check_motion — the glob fix (freeform names carry no scla- prefix)
loop_comp = CLEAN_COMP.replace(
    'tl.fromTo("#root .big", { opacity: 0 }, { opacity: 1, duration: 0.5 });',
    'tl.fromTo("#root .big", { y: 0 }, { y: 8, duration: 1.2, '
    'repeat: -1, yoyo: true });')
ws = freeform_ws("motion", CLEAN_LINES, comp_html=loop_comp)
report, problems = check_motion.check(ws)
fires("check_motion", "freeform-keep-alive",
      "a repeating tween on content in a freeform-named composition fires",
      report is not None and "keep-alive-motion" in rules_of(problems),
      f"report={report} problems={problems}")

ws = freeform_ws("motion-clean", CLEAN_LINES)
report, problems = check_motion.check(ws)
check("check_motion grades (not exit-2) and passes a clean freeform build",
      report is not None and report["graded"] >= 1 and not problems,
      f"report={report} problems={problems}")

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
