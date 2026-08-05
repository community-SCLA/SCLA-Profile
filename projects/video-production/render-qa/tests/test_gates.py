#!/usr/bin/env python3
"""test_gates.py — pins the gates added 2026-07-29 after the owner rejected the
`better-decisions` build.

Every case below is one of the owner's actual complaints, reduced to a fixture.
A gate that stops catching its case here is broken, and these are the exact
defects that shipped once already.

Run:  python3 tests/test_gates.py   (exit 0 = all pass)
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
import check_text
import preflight
import textmetrics
from hfp_common import parse_scenes

sys.path.insert(0, str(Path(__file__).resolve().parent))
from firing import fires as _fires

PASS = FAIL = 0
TMP = Path(tempfile.gettempdir()) / "scla-gate-tests"


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def fires(checker, rule, label, cond, detail=""):
    """A POSITIVE-finding assertion, registered for tests/test_firing_coverage.py.
    See tests/firing.py — the (checker, rule) key is declared here, at the
    assertion, never inferred."""
    return _fires(check, checker, rule, label, cond, detail)


def scene_div(i, template, narration, dur=8.0, start=None, variables=None):
    start = i * 10.0 if start is None else start
    v = json.dumps(variables or {}).replace('"', "&quot;")
    return (f'<div id="scene-{i:02d}" data-composition-id="scene-{i:02d}" '
            f'data-composition-src="compositions/{template}.html" '
            f'data-start="{start}" data-duration="{dur}" '
            f'data-narration="{narration}" data-variable-values="{v}" '
            f'class="clip"></div>')


def workspace(scenes_html, comps=None):
    ws = TMP / f"ws{len(list(TMP.glob('ws*'))) if TMP.exists() else 0}"
    (ws / "compositions").mkdir(parents=True, exist_ok=True)
    (ws / "index.html").write_text(
        '<html><body><div id="root" data-duration="300">'
        + "".join(scenes_html) + "</div></body></html>")
    for name, body in (comps or {}).items():
        (ws / "compositions" / f"{name}.html").write_text(body)
    return ws


# --------------------------------------------------------------------------
print("== continuity: the fragmentation the owner rejected ==")

# Owner: "Slides 10, 11 and 12 really should all be a single slide."
frag = [scene_div(11, "scla-chips", "Do you care most about learning? Security? Income?", 3.86),
        scene_div(12, "scla-points", "Flexibility? Meaning?", 2.33),
        scene_div(13, "scla-chips", "Mentorship? Growth?", 2.18)]
ws = workspace(frag)
probs = check_continuity.check(ws)
fires("check_continuity", "blip",
      "a 2.2s scene is flagged as a blip",
      any("scene-13" in p and "blip" in p for p in probs), str(probs))
fires("check_continuity", "split-list",
      "the split list is named as ONE list across scenes",
      any("split across" in p for p in probs), str(probs))

# Owner: "'but it should not make the decision for you' was likely the second
# half of a sentence connected with a comma, so it should not have its own frame"
split = [scene_div(21, "scla-points", "AI can help you brainstorm options.", 11.0),
         scene_div(22, "scla-statement", "But it should not make the decision for you.", 2.49)]
probs = check_continuity.check(workspace(split))
fires("check_continuity", "split-sentence",
      "a single clause opening with 'But' is a split sentence",
      any("scene-22" in p and "single clause" in p for p in probs), str(probs))

# ...but a DEVELOPED contrast is not. This false positive was found and fixed
# while building the gate: scene-04 of the real build is 27 words over two
# sentences and 9.9s on screen.
dev = [scene_div(3, "scla-chips", "The right city.", 6.0),
       scene_div(4, "scla-statement",
                 "But most strong career decisions do not come from finding a "
                 "perfect answer. They come from choosing among several good "
                 "options with clear criteria.", 9.91)]
probs = check_continuity.check(workspace(dev))
check("a two-sentence contrast opening with 'But' is NOT flagged",
      not any("scene-04" in p and "single clause" in p for p in probs), str(probs))

# Chrome frames the lesson; it is exempt from the beat floor.
chrome = [scene_div(1, "scla-title", "Better decisions.", 3.0),
          scene_div(2, "scla-outro", "Thanks.", 3.0)]
probs = check_continuity.check(workspace(chrome))
check("title and outro are exempt from the blip floor", not probs, str(probs))

check("the blip floor is the calibrated 4.5s",
      check_continuity.MIN_SCENE_SEC == 4.5)

# The owner rejected scene-22 (9 words) and said nothing about scene-07 (24
# words), which is a list's third item and cannot merge upward without breaking
# the 12.5s pacing cap. Length is the discriminator between a tail and a beat.
long_or = [scene_div(6, "scla-points", "They focus on one factor like salary.", 5.3),
           scene_div(7, "scla-statement",
                     "Or they stay committed to a path because they have already "
                     "invested time into it, even if it is no longer the best fit.",
                     9.1)]
probs = check_continuity.check(workspace(long_or))
check("a LONG clause opening with 'Or' is a beat, not a tail",
      not any("single clause" in p for p in probs), str(probs))


# --------------------------------------------------------------------------
print("== copy: the conjunction rule the fragmentation disabled ==")

# Owner: "you can't name off a list of things without having that and/or
# connector. For this video it happens on slide 13 between mentorship and
# growth." Split 3/2/2 across scenes, NO single scene reaches the >=3 run —
# which is exactly why the per-scene version of this gate missed it.
scenes = parse_scenes((TMP / "ws0" / "index.html").read_text())
probs = check_copy.enumeration_problems(scenes)
fires("check_copy", "conjunction",
      "the missing conjunction is caught ACROSS scenes",
      any("scene-13" in p and "'Growth?'" in p for p in probs), str(probs))
check("the finding says the list spans several scenes",
      any("runs across" in p for p in probs), str(probs))

# Terminator homogeneity: a '.' sentence after a run of '?' items is the next
# thought, not the list's final item. Without this the run absorbed the
# following scene and blamed the wrong one.
absorb = [scene_div(12, "scla-points", "Flexibility? Meaning?", 5.0),
          scene_div(13, "scla-chips", "Mentorship? Growth?", 5.0),
          scene_div(14, "scla-condition", "Second, broaden your options.", 7.5)]
probs = check_copy.enumeration_problems(
    parse_scenes((workspace(absorb) / "index.html").read_text()))
check("the next thought is not absorbed into the list",
      all("scene-14" not in p for p in probs), str(probs))

# A list that DOES carry its conjunction passes — but ONLY as one sentence.
# This fixture asserted the opposite until 2026-07-29: it pinned
# "Talking to someone. Doing a project. Or testing a skill." as correct, which
# is the identical shape to the scene-02 narration the owner then rejected for
# sounding unfinished. Satisfying the conjunction rule by bolting the word onto
# a separate fragment was never the fix; joining the run is. Rule (c) owns that,
# and this pair pins both halves so neither can drift back.
split = [scene_div(20, "scla-chips",
                   "Talking to someone. Doing a project. Or testing a skill.",
                   8.0)]
probs = check_copy.enumeration_problems(
    parse_scenes((workspace(split) / "index.html").read_text()))
fires("check_copy", "dangling",
      "a period-split list with a bolted-on 'or' FAILS",
      any("dangling conjunction" in p for p in probs), str(probs))

ok = [scene_div(20, "scla-chips",
                "Talking to someone, doing a project, or testing a skill.", 8.0)]
probs = check_copy.enumeration_problems(
    parse_scenes((workspace(ok) / "index.html").read_text()))
check("the comma-joined list carrying its 'or' passes", not probs, str(probs))


# --------------------------------------------------------------------------
print("== textmetrics: the real vendored font, never an estimate ==")

# Owner's slide 16 (2026-07-28): a card grew to three lines and crossed the
# footer because capacity had been estimated from a ratio. textmetrics measures
# in the committed Proxima metrics; check_fit.py consumes it on every build.
S = "Different learning opportunities"
check("the shipped card geometry wraps it to 3 lines",
      textmetrics.line_count(S, 240, 34, 900) == 3,
      str(textmetrics.wrap_lines(S, 240, 34, 900)))
check("hardened geometry holds it in 2",
      textmetrics.line_count(S, 280, 30, 900) == 2,
      str(textmetrics.wrap_lines(S, 280, 30, 900)))
check("uppercase + tracking widens a label measurably",
      textmetrics.width("lesson system", 20, 700, 0.22, True)
      > textmetrics.width("lesson system", 20, 700) * 1.2)


# --------------------------------------------------------------------------
print("== copy: a dangling conjunction fragment (scene-02 audio, 2026-07-29) ==")
# "The right job. The right major. The right city. Or the right path." satisfied
# the conjunction rule and sounded wrong — Oxana read the closing fragment with
# rising, unfinished intonation. Owner: "it didn't sound like she completed the
# sentence… almost like she ended on a question mark."
def copy_problems(narration):
    return check_copy.enumeration_problems(
        [{"id": "scene-02", "narration": narration, "variables": {}}])


dangling = copy_problems("The right job. The right major. The right city. "
                         "Or the right path.")
fires("check_copy", "dangling-fragment",
      "a bolted-on conjunction fragment FAILS",
      any("dangling conjunction" in p for p in dangling), str(dangling))
joined = copy_problems("The right job, the right major, the right city, "
                       "or the right path.")
check("the comma-joined sentence passes", not joined, str(joined))
# Exemptions that a blunter rule got wrong, each taken from a live script.
check("a question list keeps its rising fragments",
      not any("dangling" in p for p in
              copy_problems("Do you care most about learning? Security? "
                            "Income? Or growth?")))
check("a topic label completed by the next sentence is not dangling",
      not any("dangling" in p for p in
              copy_problems("And working with AI. Knowing how to prompt it "
                            "and check it is a baseline professional skill.")))
check("an ordinary clause opening with 'But' is not dangling",
      not any("dangling" in p for p in
              copy_problems("But titles are only labels.")))


# --------------------------------------------------------------------------
print("== copy: a symbol the voice reads as its own name (2026-08-04) ==")
# Owner on an otherwise approved cut: 'the audio is pronounced "#" as "pound
# sign" instead of "hashtag"'. The channel name reached HeyGen verbatim from
# three approved scripts, and nothing between the script and the wav could see
# that a symbol is not a word.
def symbol_problems(narration):
    return check_copy.spoken_symbol_problems(
        [{"id": "s07", "narration": narration, "variables": {}}])


hashed = symbol_problems("Reach us through the #questionsupport channel.")
fires("check_copy", "unspoken-symbol",
      "a '#' in narration FAILS", any("pound sign" in p for p in hashed),
      str(hashed))
check("the finding names the spoken rewrite",
      any("'hashtag questionsupport'" in p for p in hashed), str(hashed))
check("the spoken form passes",
      not symbol_problems("Reach us through the hashtag questionsupport "
                          "channel."))
# Symbols the voice already speaks correctly stay out of it — both are live
# copy in the refined library, and flagging them would retire the rule.
check("a percentage is not flagged",
      not symbol_problems("You cut time-to-productivity by 30%."))
check("an ampersand is not flagged",
      not symbol_problems("Personal fit & energy."))
# The rule that matters most is the SCRIPT-mode one: caught there, the fix is a
# text edit instead of a re-synthesis.
_sym_script = TMP / "symbol-script.txt"
_sym_script.parent.mkdir(parents=True, exist_ok=True)
_sym_script.write_text("If you get stuck, reach us in the #questionsupport "
                       "channel.\n")
_script_probs = check_copy.check_script(_sym_script)
fires("check_copy", "script-unspoken-symbol",
      "a '#' in a refined script FAILS at refine time",
      any("pound sign" in p for p in _script_probs), str(_script_probs))
# On-frame copy keeps the symbol: the channel's written name is "#questionsupport".
check("the on-frame string is not graded for symbols",
      not check_copy.spoken_symbol_problems(
          [{"id": "beat-07", "narration": "",
            "variables": {"text#1": "The #questionsupport channel"}}]))


# --------------------------------------------------------------------------
print("== preflight: the stage folder is not the program (2026-08-04 rename) ==")
# Both title-card checks stepped over "refined"/"rendered" only, so after the
# inbox/ready/published rename every script resolved to the program 'ready' and
# the title card failed on EVERY build. The rename is the recurring failure, so
# the live library is the fixture: a stage folder nobody taught preflight about
# turns this red instead of turning a gate into noise.
check("a ready/ script resolves to its program, not to 'ready'",
      preflight.program_of(
          "lesson-scripts/mid-career-momentum/ready/m1_mini-syllabus.txt")
      == "mid-career-momentum")
check("a published/ script resolves the same way",
      preflight.program_of(
          "lesson-scripts/early-career-boost/published/what-energizes-me.txt")
      == "early-career-boost")
_live_stages = {p.parent.name for p in
                (RQ.parent / "lesson-scripts").glob("*/*/*.txt")}
check("every stage folder in the live library is known to preflight",
      _live_stages <= set(preflight.STAGE_DIRS),
      f"unknown: {sorted(_live_stages - set(preflight.STAGE_DIRS))}")


# --------------------------------------------------------------------------
# Everything below is BUILD-enforcement-rebuild-2026-07-29 Phase 1: the
# checkers that were armed with no fixture proving they ever returned a
# finding. Each case asserts a POSITIVE finding on a minimal crafted input —
# never merely that the checker passes on a good one, which is what "covered"
# used to mean here.
# --------------------------------------------------------------------------
print("== copy: Title Case, armed 2026-07-28 with no fixture until now ==")


def heading(slot, value, sid=1):
    return [{"id": f"scene-{sid:02d}", "narration": "",
             "variables": {slot: value}}]


# The owner's standing preference, and the one frame.md actively contradicted
# until Phase 0 of this build: headings are Title Case, no terminal period.
low = check_copy.heading_problems(heading("heading", "Better decisions come "
                                          "from better criteria"))
fires("check_copy", "titlecase",
      "a sentence-case heading FAILS",
      any("not Title Case" in p for p in low), str(low))
fires("check_copy", "heading-period",
      "a heading with a terminal period FAILS",
      any("ends in a period" in p
          for p in check_copy.heading_problems(
              heading("heading", "Better Decisions Come from Better Criteria."))),
      str(check_copy.heading_problems(
          heading("heading", "Better Decisions Come from Better Criteria."))))
check("a correct Title Case heading passes",
      not check_copy.heading_problems(
          heading("heading", "Better Decisions Come from Better Criteria")))

# --- (e) a lesson's part number is a filing convention, not copy -----------
# The stem `m3_using-the-resume-builder-tool-pt2` tells two halves of one
# lesson apart on disk; it reached the title card as "Using the Resume Builder
# Tool Pt2" (owner, 2026-07-29: "that is simply a reference for our purposes").
fires("check_copy", "part-reference",
      "a title carrying the filing suffix FAILS",
      any("filing suffix" in p for p in check_copy.part_reference_problems(
          heading("title", "Using the Resume Builder Tool Pt2"))),
      str(check_copy.part_reference_problems(
          heading("title", "Using the Resume Builder Tool Pt2"))))
for _bad in ("Building Your Future You Resume Pt1", "Resume Builder, Part Two",
             "The Tool (part 2)"):
    check(f"{_bad!r} is caught",
          any("filing suffix" in p
              for p in check_copy.part_reference_problems(
                  heading("title", _bad))))
# The guard that keeps the rule usable: `four-part` is authored copy and
# appears 8 times across this program. A rule that flagged it would be off
# within a week.
for _ok in ("The Resume Builder Tool and a Four-Part Lens",
            "Keep the Four-Part Structure", "Every Strong Bullet Has Four Parts",
            "Part of the Work Is Naming It"):
    check(f"{_ok!r} is NOT flagged",
          not check_copy.part_reference_problems(heading("title", _ok)),
          str(check_copy.part_reference_problems(heading("title", _ok))))
# Narration is graded too, so a future script cannot speak the filing name.
check("narration carrying the filing name is caught",
      any("filing suffix" in p for p in check_copy.part_reference_problems(
          [{"id": "scene-01", "variables": {},
            "narration": "In part two we pick the strongest bullets."}])))
# The three slots the rule names must all be graded, not just `heading`.
for _slot in ("heading", "statement", "title"):
    check(f"the '{_slot}' slot is graded for Title Case",
          any("not Title Case" in p for p in check_copy.heading_problems(
              heading(_slot, "a lowercase line of copy"))))
# Acronyms and minor words are the two ways a naive titlecaser breaks a
# correct heading — a gate that rejects good copy is as broken as one that
# passes bad copy.
check("acronyms keep their own casing",
      not check_copy.heading_problems(heading("heading", "Working with AI")))
check("minor words stay lowercase mid-heading",
      not check_copy.heading_problems(
          heading("heading", "The Cost of a Bad Fit")))


# --------------------------------------------------------------------------
print("== text: the size floor and the restatement rule ==")
# check_text had only a token-import assertion — nothing showed either rule
# returning a finding. The floor moved 32 -> 40 on 2026-07-29 precisely
# because it had been set AT the smallest size in use and could never fire.
SMALL_CSS = TMP / "small.css"
SMALL_CSS.parent.mkdir(parents=True, exist_ok=True)
SMALL_CSS.write_text(
    ".tiny-caption { font-size: 32px; font-weight: 400; }\n"
    ".ok-body { font-size: 40px; font-weight: 400; }\n"
    ".eyebrow { font-size: 20px; text-transform: uppercase; letter-spacing: 0.14em; }\n")
small, graded = check_text.check_sizes([SMALL_CSS])
fires("check_text", "min-size",
      "body copy below the tokens.yml floor FAILS",
      any("tiny-caption" in f for f in small), str(small))
check("the compliant body rule and the label rule are not flagged",
      len(small) == 1 and graded == 3, f"{graded} graded, {small}")

EXEMPT_CSS = TMP / "exempt.css"
EXEMPT_CSS.write_text(
    "/* text-floor-exempt: marker numeral sized by its circle */\n"
    ".step-num { font-size: 28px; font-weight: 900; }\n")
ex, _ = check_text.check_sizes([EXEMPT_CSS])
check("a declared exemption is honoured", not ex, str(ex))

restated = [{"id": "scene-09",
             "variables": {"heading": "Criteria Beat Instinct",
                           "subBeats": "Criteria beat instinct"}}]
rs, _ = check_text.check_restatement(restated)
fires("check_text", "restatement",
      "a sub-beat restating its heading FAILS",
      any("restates heading" in f for f in rs), str(rs))
fresh = [{"id": "scene-09",
          "variables": {"heading": "Criteria Beat Instinct",
                        "subBeats": "Write them down before you look"}}]
check("a line that adds something new passes",
      not check_text.check_restatement(fresh)[0])


# --------------------------------------------------------------------------
print("== boundaries: cuts, air, and the wav's own trailing hold ==")
# check_boundaries has run on every build since it was written with no fixture
# proving any of its seven rules returns a finding.


def boundary_ws(scenes_html, words, root_duration):
    ws = TMP / f"bw{len(list(TMP.glob('bw*'))) if TMP.exists() else 0}"
    (ws / "assets" / "voice").mkdir(parents=True, exist_ok=True)
    (ws / "assets" / "voice" / "transcript.json").write_text(json.dumps(words))
    (ws / "index.html").write_text(
        f'<html><body><div id="root" data-duration="{root_duration}">'
        + "".join(scenes_html) + "</div></body></html>")
    return ws


def rules_of(ws):
    return {v["rule"] for v in check_boundaries.check(ws)["violations"]}


# A boundary landing mid-thought: scene-01's script span ends on "criteria"
# with no terminator, which is the split the boundary rules forbid.
mid = boundary_ws(
    [scene_div(1, "scla-points", "You need clear criteria", 5.0, start=0.0),
     scene_div(2, "scla-statement", "That is the whole idea.", 5.0, start=5.0)],
    [{"text": "criteria", "start": 4.0, "end": 4.5},
     {"text": "idea.", "start": 6.0, "end": 8.5}], 10.0)
fires("check_boundaries", "mid-sentence-cut",
      "a cut that splits a sentence FAILS",
      "mid-sentence-cut" in rules_of(mid), str(rules_of(mid)))

# Cutting before the last word has finished speaking.
midword = boundary_ws(
    [scene_div(1, "scla-points", "You need clear criteria.", 5.0, start=0.0),
     scene_div(2, "scla-statement", "That is the whole idea.", 5.0, start=5.0)],
    [{"text": "criteria.", "start": 4.0, "end": 5.6},
     {"text": "idea.", "start": 6.0, "end": 8.5}], 10.0)
fires("check_boundaries", "mid-word-cut",
      "a cut landing mid-word FAILS",
      "mid-word-cut" in rules_of(midword), str(rules_of(midword)))

# <0.2s of air after the last word.
tight = boundary_ws(
    [scene_div(1, "scla-points", "You need clear criteria.", 5.0, start=0.0),
     scene_div(2, "scla-statement", "That is the whole idea.", 5.0, start=5.0)],
    [{"text": "criteria.", "start": 4.0, "end": 4.95},
     {"text": "idea.", "start": 6.0, "end": 8.5}], 10.0)
fires("check_boundaries", "insufficient-air",
      "under 0.2s of air after the last word FAILS",
      "insufficient-air" in rules_of(tight), str(rules_of(tight)))

# The producer must clear its own floor. These are two constants in two files:
# raise the gate without the synth and every build fails its own gate; raise the
# synth without the gate and the ending the owner rejected stays certified.
import check_boundaries as _cb                                    # noqa: E402
import synth_narration as _sn                                     # noqa: E402
check("synth_narration.FINAL_HOLD clears check_boundaries.MIN_FINAL_HOLD",
      _sn.FINAL_HOLD >= _cb.MIN_FINAL_HOLD,
      f"FINAL_HOLD={_sn.FINAL_HOLD} MIN_FINAL_HOLD={_cb.MIN_FINAL_HOLD}")

# The final scene cutting less than the floor after the last spoken word.
short_hold = boundary_ws(
    [scene_div(1, "scla-points", "You need clear criteria.", 5.0, start=0.0),
     scene_div(2, "scla-outro", "That is the whole idea.", 5.0, start=5.0)],
    [{"text": "criteria.", "start": 4.0, "end": 4.5},
     {"text": "idea.", "start": 6.0, "end": 9.7}], 10.0)
fires("check_boundaries", "final-hold",
      "a final scene that cuts on the last word FAILS",
      "final-hold" in rules_of(short_hold), str(rules_of(short_hold)))

# A bare-canvas tail: root outruns the last scene.
tail = boundary_ws(
    [scene_div(1, "scla-points", "You need clear criteria.", 5.0, start=0.0),
     scene_div(2, "scla-outro", "That is the whole idea.", 5.0, start=5.0)],
    [{"text": "criteria.", "start": 4.0, "end": 4.5},
     {"text": "idea.", "start": 6.0, "end": 8.0}], 12.0)
fires("check_boundaries", "tail-after-last-scene",
      "a bare-canvas tail past the last scene FAILS",
      "tail-after-last-scene" in rules_of(tail), str(rules_of(tail)))

clean = boundary_ws(
    [scene_div(1, "scla-points", "You need clear criteria.", 5.0, start=0.0),
     scene_div(2, "scla-outro", "That is the whole idea.", 5.0, start=5.0)],
    [{"text": "criteria.", "start": 4.0, "end": 4.5},
     {"text": "idea.", "start": 6.0, "end": 8.0}], 10.0)
check("a clean set of boundaries passes",
      not rules_of(clean), str(rules_of(clean)))

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
