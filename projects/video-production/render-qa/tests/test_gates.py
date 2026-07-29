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
sys.path.insert(0, str(RQ))

import boxmodel
import check_capacity
import check_continuity
import check_copy
import check_geometry
import check_text
import textmetrics
import tokens
from hfp_common import parse_scenes

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
check("a 2.2s scene is flagged as a blip",
      any("scene-13" in p and "blip" in p for p in probs), str(probs))
check("the split list is named as ONE list across scenes",
      any("split across" in p for p in probs), str(probs))

# Owner: "'but it should not make the decision for you' was likely the second
# half of a sentence connected with a comma, so it should not have its own frame"
split = [scene_div(21, "scla-points", "AI can help you brainstorm options.", 11.0),
         scene_div(22, "scla-statement", "But it should not make the decision for you.", 2.49)]
probs = check_continuity.check(workspace(split))
check("a single clause opening with 'But' is a split sentence",
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
check("the missing conjunction is caught ACROSS scenes",
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
check("a period-split list with a bolted-on 'or' FAILS",
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
check("a value over its maxLines budget FAILS",
      any("path3" in x for x in f), str(f))
f = check_capacity.check(workspace(fits, {"card": CARD}))
check("a value inside its budget passes", not f, str(f))


# --------------------------------------------------------------------------
print("== tokens: frame.md is loaded, not quoted ==")
check("safe-area is a real loaded number", tokens.safe_area() == 72)
check("footer-reserve is a real loaded number", tokens.footer_reserve() == 120)
check("content-bottom derives from the canvas",
      tokens.content_bottom() == tokens.canvas()[1] - tokens.footer_reserve())
check("check_text's floors come FROM frame.md, not a copy",
      tokens.min_size() == (40, 20))
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
check("a bolted-on conjunction fragment FAILS",
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
check("the shipped 320px box collides — and is caught",
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
check("a scene where nothing could be graded FAILS rather than passing",
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

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
