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

import boxmodel
import check_boundaries
import check_capacity
import check_continuity
import check_copy
import check_geometry
import check_slots
import check_text
import textmetrics
import tokens
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
print("== capacity: copy that cannot fit its box ==")

# Owner's slide 16: the card grew to three lines and crossed the footer.
S = "Different learning opportunities"
check("shipped career-map geometry wraps it to 3 lines",
      textmetrics.line_count(S, 240, 34, 900) == 3,
      str(textmetrics.wrap_lines(S, 240, 34, 900)))
check("hardened geometry holds it in 2",
      textmetrics.line_count(S, 280, 30, 900) == 2,
      str(textmetrics.wrap_lines(S, 280, 30, 900)))
check("uppercase + tracking widens a label measurably",
      textmetrics.width("lesson system", 20, 700, 0.22, True)
      > textmetrics.width("lesson system", 20, 700) * 1.2)

CARD = """<html data-composition-variables='[
 {"id":"path3","type":"string","label":"Path 3","default":"[[path3]]","maxLines":2}
]'><body><template><style>
.cm-node { position: absolute; width: 340px; padding: 26px 30px; }
.cm-node .cm-role { font-size: 30px; font-weight: 900; }
</style>
<div id="root"><div class="cm-node" id="cm-node-3">
<div class="cm-role" id="cm-role-3">Path C</div></div></div>
<script>document.getElementById("cm-role-3").textContent = vars.path3;</script>
</template></body></html>"""

over = [scene_div(16, "card", "They might be different roles.", 6.36,
                  variables={"path3": "Different learning opportunities and next steps"})]
fits = [scene_div(16, "card", "They might be different roles.", 6.36,
                  variables={"path3": "Different learning opportunities"})]
f = check_capacity.check(workspace(over, {"card": CARD}))
fires("check_capacity", "maxlines",
      "a value over its maxLines budget FAILS",
      any("path3" in x for x in f), str(f))
f = check_capacity.check(workspace(fits, {"card": CARD}))
check("a value inside its budget passes", not f, str(f))


# --------------------------------------------------------------------------
print("== tokens: design-contract.md is loaded, not quoted ==")
# The literals that used to live here (safe_area() == 72, footer_reserve() ==
# 120, min_size() == (40, 20)) were the hand-copy tokens.py exists to abolish:
# they failed only if *design-contract.md* changed and never if a *video* violated the
# number, which is the opposite of what a gate is for. tests/test_tokens_coverage.py
# now asserts the real property — every normative scalar has an accessor AND a
# non-test consumer — so a token nobody reads is a red test. (2026-07-29.)
check("content-bottom is DERIVED, never declared twice",
      tokens.content_bottom() == tokens.canvas()[1] - tokens.footer_reserve())
# The floor had been pinned AT the smallest size any template used, so the gate
# was armed and structurally unable to fire. The caption the owner called "just
# too small" measured 32px — exactly compliant. A floor equal to the minimum in
# use is not a floor.
body_floor, _ = tokens.min_size()
smallest_body = min(
    float(m.group(1))
    for p in sorted((RQ.parent / "design-system" / "compositions").glob("*.html"))
    for m in [check_text.FONT_SIZE_RE.search(d)
              for sel, d in check_text.RULE_RE.findall(p.read_text())
              if check_text.classify(d) == "body"
              and not check_text.EXEMPT_RE.search(
                  p.read_text()[:p.read_text().find(sel)][-200:])]
    if m)
check("the body floor is not merely the smallest size in use",
      smallest_body >= body_floor,
      f"smallest body rule {smallest_body}px vs floor {body_floor}px")


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
print("== geometry: no text may land on other text (scene-19, 2026-07-29) ==")
# The real numbers from the shipped frame: a 320px caption box at top:855 holding
# 407px of Proxima 700, wrapping to two lines, against a sub-beat line whose band
# starts at y=907. check_layout's browser pass reported nothing at all.
LOOP = """<html data-composition-variables='[
 {"id":"step3","type":"string","label":"Step 3","default":"[[step3]]"},
 {"id":"subBeats","type":"string","label":"Sub-beats","default":""}
]'><body><template><style>
#root { position: absolute; inset: 0; }
.lp-caption { position: absolute; width: %dpx; font-size: 32px;
              font-weight: 700; line-height: 1.3; }
#lp-cap-3 { left: 800px; top: 855px; text-align: center; }
.lp-subbeat { position: absolute; left: 160px; right: 160px; bottom: 132px;
              text-align: center; font-size: 34px; font-weight: 700; }
</style>
<div id="root">
<div class="lp-caption" id="lp-cap-3" data-slot="step3">x</div>
<div class="lp-subbeat" id="lp-subbeat-proto" data-slot="subBeats"></div>
</div></template></body></html>"""

VARS = {"step3": "Grounded in what you value",
        "subBeats": "Use it on any career decision"}
hits, _, painted = check_geometry.grade(LOOP % 320, VARS)
fires("check_geometry", "text-collision",
      "the shipped 320px box collides — and is caught",
      any(h["rule"] == "text-collision" for h in hits), str(hits))
check("both boxes were actually measured", len(painted) == 2, str(painted))
# The fix is a wider box so the caption stays on ONE line, not a looser gate.
hits, _, _ = check_geometry.grade(LOOP % 560, VARS)
check("a one-line caption in a 560px box passes", not hits, str(hits))

# A template the model cannot read must never read as clean.
BLIND = ('<html><body><template><style>#root{position:absolute;inset:0;}</style>'
         '<div id="root"></div></template></body></html>')
ws = workspace([scene_div(1, "blind", "n", variables={})], {"blind": BLIND})
_, probs = check_geometry.check(ws)
fires("check_geometry", "nothing-graded",
      "a scene where nothing could be graded FAILS rather than passing",
      any("nothing-graded" in p or "looked at nothing" in p for p in probs),
      str(probs))

# The parser bug that silently orphaned half of scla-stat: `</circle>` popped
# elements it never pushed, so everything after the ring SVG left the tree.
VOIDPAIR = ('<html><body><template><style>#root{position:absolute;inset:0;}'
            '#after{position:absolute;left:100px;top:100px;font-size:40px;}'
            '</style><div id="root"><svg><circle r="1"></circle></svg>'
            '<div id="after">still in the tree</div></div>'
            '</template></body></html>')
doc = boxmodel.Doc(VOIDPAIR)
chain = []
n = doc.by_id["after"]
while n:
    chain.append(n["id"] or n["tag"])
    n = n["parent"]
check("a paired void tag does not unbalance the element tree",
      "root" in chain, " < ".join(chain))

# A CSS comment inside a declaration block parsed as a declaration and silently
# displaced `left`, so the model read x=0 for an element at left:120 and
# invented breaches that were not there. A model that mis-measures is worse
# than no model. (2026-07-29, found while arming frame-padding.)
COMMENTED = ('<html><body><template><style>#root{position:absolute;inset:0;}'
             '#a{position:absolute;/* moved: 110 -> 120 on 2026-07-29 */'
             'left:120px;top:200px;font-size:40px;}</style>'
             '<div id="root"><div id="a" data-slot="s">x</div></div>'
             '</template></body></html>')
_doc = boxmodel.Doc(COMMENTED)
check("a CSS comment inside a block does not displace the box",
      _doc.decls(_doc.by_id["a"]).get("left") == "120px",
      str(_doc.decls(_doc.by_id["a"])))

# --- geometry: the bounds rules, each proven to return a finding -----------
# spacing.frame-padding was declared when the system was built and read by
# NOTHING until 2026-07-29 — tokens.py exposed frame_padding() and no caller
# ever called it. tests/test_tokens_coverage.py now keeps that from recurring;
# these prove the rules that consume the numbers actually fire.
BOUNDS = """<html data-composition-variables='[
 {"id":"body","type":"string","label":"Body","default":"[[body]]"}
]'><body><template><style>
#root { position: absolute; inset: 0; }
.bd { position: absolute; width: 600px; font-size: 40px; font-weight: 400;
      line-height: 1.3; }
</style>
<div id="root"><div class="bd" id="bd" data-slot="body">x</div>
</div></template></body></html>"""


def bounds_rules(css_pos):
    html = BOUNDS.replace("#root { position: absolute; inset: 0; }",
                          "#root { position: absolute; inset: 0; }\n"
                          f"#bd {{ {css_pos} }}")
    hits, _, _ = check_geometry.grade(html, {"body": "A line of real copy"})
    return {h["rule"] for h in hits}


fires("check_geometry", "safe-area-breach",
      "content crossing the 72px keep-out FAILS",
      "safe-area-breach" in bounds_rules("left: 20px; top: 400px;"),
      str(bounds_rules("left: 20px; top: 400px;")))
fires("check_geometry", "footer-breach",
      "content running into the footer band FAILS",
      "footer-breach" in bounds_rules("left: 300px; top: 980px;"),
      str(bounds_rules("left: 300px; top: 980px;")))
fires("check_geometry", "padding-breach",
      "body content outside the 120px content inset FAILS",
      "padding-breach" in bounds_rules("left: 90px; top: 400px;"),
      str(bounds_rules("left: 90px; top: 400px;")))
check("body content inside every bound passes",
      not bounds_rules("left: 200px; top: 400px;"),
      str(bounds_rules("left: 200px; top: 400px;")))
# Declared decorative bleed is stated, never tolerated by a loosened threshold.
_bleed = BOUNDS.replace('id="bd" data-slot="body"',
                        'id="bd" data-slot="body" data-layout-allow-overflow')
check("declared bleed (data-layout-allow-overflow) is exempt",
      not check_geometry.grade(
          _bleed.replace("#root { position: absolute; inset: 0; }",
                         "#root { position: absolute; inset: 0; }\n"
                         "#bd { left: 20px; top: 400px; }"),
          {"body": "A line of real copy"})[0])
# Label-class furniture is NOT graded against the content inset: design-contract.md hands
# the outer band to the brandline, scene index and rail label by name, so a
# padding rule that graded them would fail every template in the system.
LABELISH = BOUNDS.replace(
    ".bd { position: absolute; width: 600px; font-size: 40px; font-weight: 400;",
    ".bd { position: absolute; width: 600px; font-size: 20px; font-weight: 700;"
    " text-transform: uppercase; letter-spacing: 0.14em;")
_lab = check_geometry.grade(
    LABELISH.replace("#root { position: absolute; inset: 0; }",
                     "#root { position: absolute; inset: 0; }\n"
                     "#bd { left: 90px; top: 400px; }"),
    {"body": "SCLA lesson system"})[0]
check("label-class furniture is not graded against the content inset",
      not any(h["rule"] == "padding-breach" for h in _lab), str(_lab))

# --- geometry: card gutters (owner, 2026-07-29) ----------------------------
# "two boxes even touch each other where they should be evenly spread out." The
# ink inside those cards was nowhere near colliding — it is the BORDERS that
# touched, so this is the one rule graded on layout boxes. The fixture is the
# real failure mode: two top-anchored cards on slots sized for one line, where
# the upper card's copy wraps to two and eats the gutter.
CARDS = """<html data-composition-variables='[
 {"id":"a","type":"string","label":"A","default":"[[a]]"},
 {"id":"b","type":"string","label":"B","default":"[[b]]"}
]'><body><template><style>
#root { position: absolute; inset: 0; }
.card { position: absolute; left: 700px; width: 300px; padding: 26px 30px;
        border: 2px solid #cccedf; background: #f6f6f9; }
.role { font-size: 40px; font-weight: 900; line-height: 1.2; }
#c1 { top: 300px; }
#c2 { top: 470px; }
.ghost { position: absolute; left: 700px; top: 300px; width: 300px;
         height: 300px; border: 2px solid #eee; border-radius: 50%; }
</style>
<div id="root"><div class="card" id="c1"><div class="role" data-slot="a">x</div></div>
<div class="card" id="c2"><div class="role" data-slot="b">y</div></div>
<div class="ghost" id="g1"></div><div class="ghost" id="g2"></div>
</div></template></body></html>"""


def card_rules(a, b):
    hits, _, _ = check_geometry.grade(CARDS, {"a": a, "b": b})
    return {h["rule"] for h in hits}


# One line each: 300+136 = 436, next card at 470 -> 34px gutter, clean.
check("evenly spaced one-line cards pass",
      not card_rules("Short", "Short"), str(card_rules("Short", "Short")))
# The upper card's copy wraps to two lines and eats the gutter.
fires("check_geometry", "card-gutter",
      "a card that grew into the one below it FAILS",
      "card-gutter" in card_rules("Different learning opportunities", "Short"),
      str(card_rules("Different learning opportunities", "Short")))
# The decorative-ring exclusion is load-bearing, not incidental: two concentric
# empty bordered circles are in every second template in the system, and before
# the text-bearing condition they fired on all of them.
_, _lay, _paint = check_geometry.grade(CARDS, {"a": "Short", "b": "Short"})
_card_ids = {n["id"] for n, _ in check_geometry._card_nodes(_lay, _paint)}
check("empty decorative rings are not cards",
      _card_ids == {"c1", "c2"}, str(sorted(_card_ids)))


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
print("== slots: an unfilled slot renders FABRICATED placeholder copy ==")
# The worst failure this repo has: a slot omitted from data-variable-values
# renders the template's schema default — plausible, on-brand words the lesson
# script never said. Every other gate passes it (size and restatement are not
# provenance). check_slots.py has enforced this since it was written and had
# no fixture proving it fires.
POINTS = """<html data-composition-variables='[
 {"id":"heading","type":"string","label":"Heading","default":"[[heading]]"},
 {"id":"point1","type":"string","label":"Point 1","default":"A plausible first point"},
 {"id":"point2","type":"string","label":"Point 2 (empty to hide)","default":"A plausible second point"}
]'><body><template><div id="root"></div></template></body></html>"""

unfilled = [scene_div(5, "pts", "Two things matter here.", 8.0,
                      variables={"heading": "What Matters", "point1": "Cost"})]
found, err = check_slots.check(workspace(unfilled, {"pts": POINTS}))
fires("check_slots", "unfilled",
      "an omitted slot that would render its default FAILS",
      any("point2" in f["unfilled"] for f in found), f"{found} {err}")

placeheld = [scene_div(5, "pts", "Two things matter here.", 8.0,
                       variables={"heading": "What Matters", "point1": "Cost",
                                  "point2": "[[point2]]"})]
found, err = check_slots.check(workspace(placeheld, {"pts": POINTS}))
fires("check_slots", "placeholder",
      "placeholder text passed EXPLICITLY is the same fabrication",
      any("point2" in f["placeholder"] for f in found), f"{found} {err}")

blanked = [scene_div(5, "pts", "One thing matters here.", 8.0,
                     variables={"heading": "What Matters", "point1": "Cost",
                                "point2": ""})]
found, err = check_slots.check(workspace(blanked, {"pts": POINTS}))
check("a slot explicitly blanked with \"\" passes", not found, f"{found} {err}")

# An icon name the template's own library doesn't have draws NOTHING and reports
# nothing — `ICONS[name]` is just undefined. scene-17 of the 2026-07-29 criteria
# build asked scla-points for `map`, which existed in scla-statement and
# scla-steps but not in scla-points, and shipped with a hole where row 2's icon
# belonged. A divergence between two copies of one library is only visible to a
# gate that reads the library it is actually calling.
ICONED = POINTS.replace(
    "<div id=\"root\"></div>",
    "<div id=\"root\"></div><script>const ICONS = {"
    "compass: { paths: [{ d: \"M0 0\" }] }, target: { paths: [{ d: \"M0 0\" }] },"
    "};</script>")
BASE = {"heading": "What Matters", "point1": "Cost", "point2": "Time"}

found, err = check_slots.check(
    workspace([scene_div(5, "pts", "Two things matter here.", 8.0,
                         variables=dict(BASE, icons="compass,map"))],
              {"pts": ICONED}))
fires("check_slots", "unknown-icon",
      "an icon name the template's library does not have FAILS",
      any("map" in " ".join(f.get("unknown_icons", [])) for f in found),
      f"{found} {err}")

found, err = check_slots.check(
    workspace([scene_div(5, "pts", "Two things matter here.", 8.0,
                         variables=dict(BASE, icons="compass,target"))],
              {"pts": ICONED}))
check("icon names the library does have pass", not found, f"{found} {err}")
# A template with no library at all is not graded — most of them draw no icons,
# and failing them for a slot they never read would be a gate crying wolf.
found, err = check_slots.check(
    workspace([scene_div(5, "pts", "Two things matter here.", 8.0,
                         variables=dict(BASE, icons="anything"))],
              {"pts": POINTS}))
check("a template with no ICONS library is not graded for icon names",
      not found, f"{found} {err}")


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
      "body copy below the design-contract.md floor FAILS",
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
# with no terminator, which is the split design-contract.md forbids.
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
