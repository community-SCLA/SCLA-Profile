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

import check_boundaries
import check_continuity
import check_copy
import check_fit
import check_forms
import check_layout
import check_motion
from hfp_common import load_beats, onframe_strings, parse_scenes, sample_units

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

# The spoken half of the same guard: a marker in the BEAT MANIFEST is read
# aloud, and costs a re-synthesis to fix once the wavs exist. The retired slot checker only
# ever saw compiled template slots, so this half was ungraded on the freeform
# lane entirely.
ws = freeform_ws("spoken-placeholder", [
    {"id": "s01", "text": "Welcome to [[program name]], where you build "
                          "momentum."}])
fires("check_copy", "spoken-placeholder",
      "a merge field in the beat manifest fires — it would be SPOKEN",
      "placeholder-slot" in rules_of(check_copy.check(ws)),
      str(check_copy.check(ws)))

ws = freeform_ws("spoken-todo", [
    {"id": "s01", "text": "Your next move depends on TODO finish this line."}])
fires("check_copy", "spoken-placeholder",
      "an unresolved TODO marker in narration fires",
      "placeholder-slot" in rules_of(check_copy.check(ws)),
      str(check_copy.check(ws)))

# An ellipsis is legitimate punctuation in SPEECH, and must not be dragged in
# from the on-frame rule, where a slot whose entire value is "…" is a defect.
ws = freeform_ws("spoken-ellipsis", [
    {"id": "s01", "text": "You pause, you reflect… and then you decide."}])
check("an ellipsis inside narration is punctuation, not a placeholder",
      "placeholder-slot" not in rules_of(check_copy.check(ws)),
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

# ---------------------------------------------------------------------------
# check_forms — the two owner rules rehomed off template slots (step 1.3a).
# On the template path these read data-variable-values and so die with the
# compiler; here they read element structure, which no author has to know a
# convention to produce.


def forms_ws(name, body):
    return freeform_ws(name, CLEAN_LINES, comp_html=(
        "<template><style>.x{color:#fff}</style><div id=\"root\">"
        "<div class=\"big\" data-role=\"heading\">Four Kinds of Transition</div>"
        f"{body}</div></template>"))


rep, probs = check_forms.check(forms_ws("list-one", "<ul><li>Only one</li></ul>"))
fires("check_forms", "one-item-list",
      "a <ul> with exactly ONE <li> fires one-item-list",
      "one-item-list" in rules_of(probs), str(probs))

rep, probs = check_forms.check(forms_ws(
    "list-two", "<ul><li>First point</li><li>Second point</li></ul>"))
check("a two-item list passes", not probs, str(probs))

# The nesting case a regex gets wrong: counting <li> between <ul> and </ul>
# scoops up the nested list's items and reports a real one-item list clean.
rep, probs = check_forms.check(forms_ws(
    "list-nested", "<ul><li>Only one<ul><li>sub a</li><li>sub b</li></ul>"
                   "</li></ul>"))
fires("check_forms", "one-item-list",
      "an outer list of one item is caught THROUGH a nested two-item list",
      sum(1 for r in rules_of(probs) if r == "one-item-list") == 1, str(probs))

rep, probs = check_forms.check(forms_ws(
    "list-declared", '<div data-role="list"><div>Only one</div></div>'))
fires("check_forms", "one-item-list",
      'a declared data-role="list" holding one child fires',
      "one-item-list" in rules_of(probs), str(probs))

rep, probs = check_forms.check(forms_ws(
    "compare-one", '<div data-role="compare"><div data-role="card">Stay'
                   "</div></div>"))
fires("check_forms", "one-card",
      "a comparison region holding ONE card fires one-card",
      "one-card" in rules_of(probs), str(probs))

rep, probs = check_forms.check(forms_ws(
    "compare-two", '<div data-role="compare"><div data-role="card">Stay</div>'
                   '<div data-role="card">Move</div></div>'))
check("a two-card comparison passes", not probs, str(probs))

# Markup quoted inside a <script> string is not markup. HTMLParser's CDATA
# handling gives this for free; a regex scan would have flagged it.
rep, probs = check_forms.check(forms_ws(
    "script-noise", '<script>var s = "<ul><li>x</li></ul>";</script>'))
check("a list quoted inside a <script> string does not flag", not probs,
      str(probs))

rep, probs = check_forms.check(forms_ws("no-lists", "<p>No list here.</p>"))
check("a build with no lists at all is CLEAN, not ungraded",
      rep is not None and not probs, str(probs))

# ---------------------------------------------------------------------------
# sample_units — the sampling grid every time-sampled gate walks (steps 1.5a/b).
#
# These two collapses "survived" the migration while quietly inspecting far
# less: check_layout sampled one point per composition CLIP (27 -> 3 on a
# LONGER video) and verify_render extracted 3 frames per clip (81 -> 9 stills
# for 200s, one per 22s). Both still exited 0. That is the same nothing-graded
# shape as everything else here — a gate reporting clean on what it never
# looked at — so the grid gets its own fixtures rather than being trusted
# because the code reads right. check_layout and verify_render themselves are
# declared SLOW in test_firing_coverage (browser / rendered MP4), which is
# exactly why the SHARED grid they both delegate to has to be pinned in-process.

ACT_INDEX = """<div id="root" data-duration="200">
  <div class="clip" data-composition-src="compositions/opening.html"
       data-composition-id="opening" data-start="0" data-duration="40"></div>
  <div class="clip" data-composition-src="compositions/map.html"
       data-composition-id="map" data-start="40" data-duration="120"></div>
  <div class="clip" data-composition-src="compositions/closing.html"
       data-composition-id="closing" data-start="160" data-duration="40"></div>
</div>"""

# 24 beats over 3 clips — the agent-native reference build's real shape.
BEATS_24 = [{"id": f"s{i:02d}", "text": f"Beat number {i} speaks a full line."}
            for i in range(1, 25)]
TIMING_24 = {"total": 200.0, "rows": [
    {"id": f"s{i:02d}", "audio_start": (i - 1) * 8.0, "audio_dur": 7.0,
     "vis_start": (i - 1) * 8.0, "vis_dur": 8.0} for i in range(1, 25)]}

ws = freeform_ws("grid", BEATS_24, index=ACT_INDEX, timing=TIMING_24)
units = sample_units(ws)
check("a freeform clip is an ACT: parse_scenes still sees only the 3 clips",
      len(parse_scenes((ws / "index.html").read_text())) == 3)
check("sample_units samples per BEAT (24), not per clip (3) — the 1.5a/b fix",
      len(units) == 24, f"{len(units)} unit(s)")
check("verify_render's 3-frames-per-unit now yields 72 stills, not 9",
      3 * len(units) == 72, str(3 * len(units)))
times = check_layout.scene_times(ws)
check("check_layout samples 24 midpoints, each inside its own beat",
      len(times) == 24 and all(s <= mid <= e for mid, _, s, e in times),
      str(times[:3]))

# The template path must be untouched: there, a clip IS a beat, and the grid
# has to stay the clips or every existing workspace re-samples overnight.
tmpl_index = ACT_INDEX.replace(
    '<div class="clip" data-composition-src="compositions/opening.html"',
    '<div class="clip" data-narration="One beat per clip here."'
    ' data-composition-src="compositions/opening.html"')
ws = freeform_ws("grid-template", BEATS_24, index=tmpl_index, timing=TIMING_24)
check("template path (any data-narration present) still samples per CLIP",
      len(sample_units(ws)) == 3, str(len(sample_units(ws))))

# No timings yet: the grid is EMPTY, and callers treat an empty grid as
# ungradeable. Silently sampling zero points and exiting 0 is the failure this
# whole plan exists to close.
ws = freeform_ws("grid-untimed", BEATS_24, index=ACT_INDEX)
check("no timing.json -> an EMPTY grid (ungradeable), never a silent pass",
      sample_units(ws) == [], str(sample_units(ws)))

# ---------------------------------------------------------------------------
# check_fit — plan-stage copy fit (step 1.3c), the rehome of the per-slot capacity gate's
# question onto the FRAME instead of a template slot. Advisory per STD-38, so
# these prove it FIRES, not that it blocks.
fit_budget = check_fit.budget()
check("the fit budget is LOADED from tokens.yml, not hand-copied",
      fit_budget["avail_w"] == 1920 - 2 * 72 and fit_budget["max_lines"] > 5,
      str(fit_budget))

long_body = ("Your accumulated experience across projects and teams and "
             "stakeholders is the raw material of your next move. ") * 14
rep, probs = check_fit.check(None, strings=[("main.html", "text", long_body)])
fires("check_fit", "fit-impossible",
      "copy too long for the content area AT THE MINIMUM size fires",
      "fit-impossible" in rules_of(probs), str(probs))
check("...and it is advisory (severity warning), never an error",
      all(getattr(p, "severity", "error") == "warning" for p in probs),
      str([getattr(p, "severity", "?") for p in probs]))

rep, probs = check_fit.check(None, strings=[
    ("main.html", "heading",
     "Four Kinds Of Career Transition And What Each One Asks Of You When You "
     "Have Already Built Years Of Real Experience In A Field")])
fires("check_fit", "fit-heading-long",
      "a heading that cannot be ONE line even at the floor fires (it is a "
      "title, not a sentence)",
      "fit-heading-long" in rules_of(probs), str(probs))

rep, probs = check_fit.check(None, strings=[
    ("main.html", "heading", "Four Kinds of Transition"),
    ("main.html", "text", "Same core strengths, new context.")])
check("ordinary copy passes the fit budget", not probs, str(probs))

rep, probs = check_fit.check(None, strings=[])
fires("check_fit", "nothing-graded",
      "a build with no on-frame strings FAILS rather than passing",
      rep is None and "nothing-graded" in rules_of(probs), str(probs))

# ---------------------------------------------------------------------------
# check_boundaries — the freeform adapter (step 1.5d).
#
# check() exited 2 on every freeform build ("wants narration.wav"), which took
# the ENDING FLOOR with it. That floor was bought with two owner rejections:
# MIN_FINAL_HOLD was raised 1.0 -> 1.5 because a 1.1s ending read as abrupt,
# and synth_narration gives the final clip 1.8s of real silence. An adapter
# that moved the boundary rules but left final-hold behind would un-enforce
# exactly the rule those rejections paid for — so it is fixtured first.

def audio_ws(name, beats, root):
    """beats: [(id, text, audio_start, [(w,s,e)], clip_dur, vis_start, vis_dur)]"""
    ws = TMP / name
    shutil.rmtree(ws, ignore_errors=True)
    (ws / "compositions").mkdir(parents=True)
    (ws / "compositions" / "main.html").write_text(CLEAN_COMP)
    (ws / "index.html").write_text(
        f'<div id="root" data-duration="{root}">'
        f'<div class="clip" data-composition-src="compositions/main.html"'
        f' data-composition-id="main" data-start="0"'
        f' data-duration="{root}"></div></div>')
    (ws / "audio_request.json").write_text(json.dumps({"provider": "heygen",
        "lines": [{"id": b[0], "text": b[1]} for b in beats]}))
    (ws / "audio_meta.json").write_text(json.dumps({"voices": [
        {"id": b[0], "path": f"assets/voice/{b[0]}.wav", "duration_s": b[4],
         "words": [{"text": w, "start": s, "end": e} for w, s, e in b[3]]}
        for b in beats]}))
    (ws / "timing.json").write_text(json.dumps({"total": root, "rows": [
        {"id": b[0], "audio_start": b[2], "audio_dur": b[4],
         "vis_start": b[5], "vis_dur": b[6]} for b in beats]}))
    return ws


#            id     text                 a0    words(clip-rel)          clip  vis0 visdur
CLEAN_AUDIO = [
    ("s01", "You have built years of experience.", 0.5,
     [("You", 0.2, 0.5), ("experience.", 2.6, 3.0)], 3.4, 0.0, 4.0),
    ("s02", "Your next move can build on it.", 4.5,
     [("Your", 0.2, 0.5), ("it.", 2.7, 3.0)], 4.8, 4.0, 5.5),
]
res = check_boundaries.check(audio_ws("bounds-clean", CLEAN_AUDIO, 9.5))
check("a clean freeform build GRADES (no longer exit-2) and passes",
      res["verdict"] == "PASS" and res.get("lane") == "freeform", str(res))

# The final clip's own wav holds only 0.2s past the last word.
short_tail = [CLEAN_AUDIO[0],
              ("s02", "Your next move can build on it.", 4.5,
               [("Your", 0.2, 0.5), ("it.", 2.7, 3.0)], 3.2, 4.0, 5.5)]
res = check_boundaries.check(audio_ws("bounds-tail", short_tail, 9.5))
fires("check_boundaries", "freeform-audio-tail",
      "a final clip whose FILE stops 0.2s after the last word FAILS — the "
      "video holding longer does not put the release back",
      any(v["rule"] == "audio-tail-clipped" for v in res["violations"]),
      str(res["violations"]))

# ...and the video holding a long time is explicitly not a defence: root runs
# well past the audio here, and it still fires.
check("a long VIDEO tail does not excuse a clipped AUDIO tail",
      any(v["rule"] == "audio-tail-clipped" for v in
          check_boundaries.check(audio_ws("bounds-tail2", short_tail,
                                          14.0))["violations"]))

# Video cuts 0.4s after the last word: under the 1.5s ending floor.
res = check_boundaries.check(audio_ws("bounds-hold", [
    CLEAN_AUDIO[0],
    ("s02", "Your next move can build on it.", 4.5,
     [("Your", 0.2, 0.5), ("it.", 2.7, 3.0)], 4.8, 4.0, 2.4)], 7.9))
fires("check_boundaries", "freeform-final-hold",
      "an ending that cuts 0.4s after the last spoken word FAILS the floor",
      any(v["rule"] == "final-hold" for v in res["violations"]),
      str(res["violations"]))

res = check_boundaries.check(audio_ws("bounds-air", [
    ("s01", "You have built years of experience.", 0.5,
     [("You", 0.2, 0.5), ("experience.", 2.6, 3.0)], 3.4, 0.0, 3.55),
    CLEAN_AUDIO[1]], 9.5))
fires("check_boundaries", "freeform-insufficient-air",
      "a beat cutting 0.05s after its last word FAILS the air floor",
      any(v["rule"] == "insufficient-air" for v in res["violations"]),
      str(res["violations"]))

res = check_boundaries.check(audio_ws("bounds-split", [
    ("s01", "You have built years of experience and", 0.5,
     [("You", 0.2, 0.5), ("and", 2.6, 3.0)], 3.4, 0.0, 4.0),
    CLEAN_AUDIO[1]], 9.5))
fires("check_boundaries", "freeform-mid-sentence",
      "a beat ending mid-sentence FAILS — the boundary splits a thought",
      any(v["rule"] == "mid-sentence-cut" for v in res["violations"]),
      str(res["violations"]))

empty = TMP / "forms-empty"
shutil.rmtree(empty, ignore_errors=True)
empty.mkdir(parents=True)
rep, probs = check_forms.check(empty)
fires("check_forms", "nothing-graded",
      "a workspace with no markup at all FAILS rather than passing",
      rep is None and "nothing-graded" in rules_of(probs), str(probs))

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
