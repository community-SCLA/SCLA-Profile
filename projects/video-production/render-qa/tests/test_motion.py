#!/usr/bin/env python3
"""test_motion.py — the fake-motion bans, armed.

The ban is the most-violated rule in the repo's history: given 2026-07-14
("I fully want ripples off"), reaffirmed 07-15, and broken the next day by a
session that restored the banned motion so renders would clear the stagnation
gate. Three MP4s shipped with it and one was published. It was written in
the prose spec, in `.claude/rules/video-production.md`, AND in comments inside the
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

BOTTOM_PROGRESS_SCALE = """<style>
.progress { position:absolute; left:120px; right:120px; bottom:70px;
  height:4px; background:#ccd; }
.progress span { display:block; width:100%; height:100%; transform-origin:left; }
</style><div class="progress"><span></span></div><script>
tl.fromTo('.progress span', {scaleX:0},
  {scaleX:1,duration:138.7,ease:'none'}, 0);
</script>"""

BOTTOM_PROGRESS_WIDTH = """<style>
.progress-rail { position:absolute; left:120px; right:200px; bottom:120px;
  height:4px; background:#ccd; }
.progress-fill { height:100%; width:0; }
</style><div class="progress-rail"><div class="progress-fill"></div></div>
<script>tl.to('.progress-fill',{width:'100%',duration:119.9,ease:'none'},0);</script>"""

RENAMED_PROGRESS_ROLE = """<style>
.rail { position:fixed; left:100px; right:100px; bottom:90px; height:6px; }
</style><nav class="rail" data-role="progress"></nav>"""

RENAMED_TRACK = """<main data-duration="120"><style>
.track { position:absolute; left:100px; right:100px; bottom:90px; height:6px; }
.track i { display:block; width:100%; height:100%; transform:scaleX(0); }
</style><div class="track"><i></i></div><script>
const timeline = gsap.timeline({paused:true});
timeline.fromTo('.track i',{scaleX:0},{scaleX:1,duration:120,ease:'none'},0);
</script></main>"""

SCENE_TRACE = """<main data-duration="118"><script>
const timeline = gsap.timeline({paused:true});
clips.forEach((clip) => {
  const duration = Number(clip.dataset.duration);
  const trace = document.createElement('span');
  timeline.fromTo(trace, {scaleX:0},
    {scaleX:1,duration:Math.max(1,duration-.4),ease:'none'}, start+.2);
});
</script></main>"""

CONTENT_MAP = """<style>
.map-progress { position:absolute; left:24px; right:24px; top:55px;
  height:4px; background:#eaab2d; }
</style><div class="map-progress"></div><script>
tl.to('.map-progress',{scaleX:.8,duration:.56,ease:'power2.out'},12);
</script>"""

REPOPULATED_CARRIER = """<script>
const scenes = gsap.utils.toArray('.scene');
scenes.forEach((scene) => {
  const visual = scene.querySelector('.visual');
  const map = document.createElement('div');
  map.className = 'system-map';
  visual.append(map);
});
</script>"""

REPEATED_SCENE_CARRIER = """
<section class="clip" id="beat-a" data-start="0" data-duration="4">
  <div class="visual"><div class="map"><span>Same evidence map</span></div></div>
</section>
<section class="clip" id="beat-b" data-start="4" data-duration="4">
  <div class="visual"><div class="map"><span>Same evidence map</span></div></div>
</section>
<section class="clip" id="beat-c" data-start="8" data-duration="4">
  <div class="visual"><div class="map"><span>Same evidence map</span></div></div>
</section>
"""

DEVELOPING_SCENES = REPEATED_SCENE_CARRIER.replace(
    "<span>Same evidence map</span></div></div>\n</section>\n<section class=\"clip\" id=\"beat-b\"",
    "<span>Evidence inventory</span></div></div>\n</section>\n<section class=\"clip\" id=\"beat-b\"",
    1,
).replace(
    "<span>Same evidence map</span></div></div>\n</section>\n<section class=\"clip\" id=\"beat-c\"",
    "<span>Selection funnel</span></div></div>\n</section>\n<section class=\"clip\" id=\"beat-c\"",
    1,
)

PERSISTENT_STATES = """
<section class="clip" id="beat-a" data-continuity="evidence-map">
  <div class="visual"><div class="map"><span class="state selected">A</span><span class="state">B</span></div></div>
</section>
<section class="clip" id="beat-b" data-continuity="evidence-map">
  <div class="visual"><div class="map"><span class="state">A</span><span class="state selected">B</span></div></div>
</section>
<script>scenes.forEach(scene => { const continuity = scene.dataset.continuity; });</script>
"""
REENTERED_STATES = PERSISTENT_STATES.replace(
    ' data-continuity="evidence-map"', '')

BATCH_EMPHASIS = """<script>
const timeline = gsap.timeline({paused:true});
timeline.to('#examples .card', {
  borderColor:'#eaab2d', duration:.45, stagger:.1
}, 12);
</script>"""

POINT_EMPHASIS = """<script>
const timeline = gsap.timeline({paused:true});
timeline.to('#examples .card:nth-child(1)', {borderColor:'#eaab2d'}, 12)
  .to('#examples .card:nth-child(2)', {borderColor:'#eaab2d'}, 14.2);
</script>"""

# ---------------------------------------------------------------------------
print("== bottom playback progress never earns motion credit ==")

fires(check, "check_motion", "playback-progress-indicator",
      "a full-runtime scaleX progress bar at the bottom FAILS",
      "playback-progress-indicator" in rules(BOTTOM_PROGRESS_SCALE),
      str(check_motion.grade(BOTTOM_PROGRESS_SCALE)))
fires(check, "check_motion", "playback-progress-indicator",
      "the width-animation variant at the bottom FAILS",
      "playback-progress-indicator" in rules(BOTTOM_PROGRESS_WIDTH),
      str(check_motion.grade(BOTTOM_PROGRESS_WIDTH)))
check("renaming the bar cannot evade an explicit progress role",
      "playback-progress-indicator" in rules(RENAMED_PROGRESS_ROLE),
      str(check_motion.grade(RENAMED_PROGRESS_ROLE)))
fires(check, "check_motion", "temporal-progress-motion",
      "a renamed full-runtime .track line FAILS",
      "temporal-progress-motion" in rules(RENAMED_TRACK),
      str(check_motion.grade(RENAMED_TRACK)))
check("a top-edge per-scene trace is still temporal progress",
      "temporal-progress-motion" in rules(SCENE_TRACE),
      str(check_motion.grade(SCENE_TRACE)))
check("a meaning-bearing map away from the bottom edge remains allowed",
      "playback-progress-indicator" not in rules(CONTENT_MAP),
      str(check_motion.grade(CONTENT_MAP)))
check("the word progress in narration is not a visual progress bar",
      not rules("<p>Your progress grows through practice.</p>"))

print("== cloned carriers and batch emphasis never earn motion credit ==")
fires(check, "check_motion", "repopulated-carrier",
      "creating and appending the same carrier inside every scene FAILS",
      "repopulated-carrier" in rules(REPOPULATED_CARRIER),
      str(check_motion.grade(REPOPULATED_CARRIER)))
fires(check, "check_motion", "repeated-scene-carrier",
      "copying one illustration into adjacent short scenes FAILS",
      "repeated-scene-carrier" in rules(REPEATED_SCENE_CARRIER),
      str(check_motion.grade(REPEATED_SCENE_CARRIER)))
check("materially different adjacent illustrations remain allowed",
      "repeated-scene-carrier" not in rules(DEVELOPING_SCENES),
      str(check_motion.grade(DEVELOPING_SCENES)))
check("one declared carrier with explicit developing states remains allowed",
      "repeated-scene-carrier" not in rules(PERSISTENT_STATES),
      str(check_motion.grade(PERSISTENT_STATES)))
check("the same state changes re-entered as separate scenes still FAIL",
      "repeated-scene-carrier" in rules(REENTERED_STATES),
      str(check_motion.grade(REENTERED_STATES)))
fires(check, "check_motion", "batch-list-emphasis",
      "one paint tween sprayed across every card FAILS",
      "batch-list-emphasis" in rules(BATCH_EMPHASIS),
      str(check_motion.grade(BATCH_EMPHASIS)))
check("cueing individual cards at distinct narration times remains allowed",
      "batch-list-emphasis" not in rules(POINT_EMPHASIS),
      str(check_motion.grade(POINT_EMPHASIS)))

# ---------------------------------------------------------------------------
print("== the ban fires on content ==")

fires(check, "check_motion", "keep-alive-motion",
      "a repeating tween on the living-icon hero FAILS",
      "keep-alive-motion" in rules(tween('"#cc-iconwrap"', BOB)),
      str(rules(tween('"#cc-iconwrap"', BOB))))

check("a repeating tween on a text node FAILS",
      "keep-alive-motion" in rules(tween('"#sm-statement"', BOB)))
check("a timeline named `timeline` is graded just like one named `tl`",
      "keep-alive-motion" in rules(
          tween('"#sm-statement"', BOB).replace("tl.fromTo", "timeline.fromTo")))
check("a repeating tween on a card/node FAILS",
      "keep-alive-motion" in rules(tween('"#cm-node-1"', BOB)))
check("an array of content targets FAILS",
      "keep-alive-motion" in rules(tween('["#cd-heading", "#cd-chips"]', BOB)))
check("`repeat: -1` (infinite) on content FAILS",
      "keep-alive-motion" in rules(
          tween('"#cc-iconwrap"', '{ y: -10, duration: 2.7, repeat: -1 }')))

print("== ...and does not fire on what the motion language sanctions ==")
check("a one-shot entrance on content PASSES",
      not rules(tween('"#cc-iconwrap"', ONCE)))
check("`repeat: 0` is a one-shot, not keep-alive",
      not rules(tween('"#sm-statement"',
                      '{ y: -10, duration: 0.4, repeat: 0 }')))
check("a declared exception is honoured",
      not rules(tween('"#cc-iconwrap"', BOB).replace(
          ");", "); /* motion-allow: deliberate, owner-approved */", 1)))
check("ring-breath PASSES once DECLARED",
      not rules(tween('"#t-ring-1"', BOB).replace(
          ");", "); /* motion-allow: ring-breath texture */", 1)))

print("== a decorative NAME earns nothing (the allow-list is gone, 2026-08-04) ==")
# Until 2026-08-04 nine substrings ("ghost", "ring", "-bg", …) bought a silent
# exemption. That encoded SCLA template naming into the checker: freeform HTML
# could not earn an exemption it followed no convention for, and any element
# NAMED decoratively got one it never asked for. Measured when the list came
# out: the agent-native reference build's #bg-glow had been exempt on its name
# alone, and had never declared anything.
fires(check, "check_motion", "keep-alive-motion",
      "a ring-breath tween with NO declaration now FAILS on its name alone",
      "keep-alive-motion" in rules(tween('"#t-ring-1"', BOB)),
      str(rules(tween('"#t-ring-1"', BOB))))
fires(check, "check_motion", "keep-alive-motion",
      "an undeclared #...-ghost tween FAILS — 'ghost' is not a declaration",
      "keep-alive-motion" in rules(tween('"#cd-ghost"', BOB)),
      str(rules(tween('"#cd-ghost"', BOB))))
fires(check, "check_motion", "keep-alive-motion",
      "an undeclared '-bg' tween FAILS (the freeform #bg-glow case)",
      "keep-alive-motion" in rules(tween('"#bg-glow"', BOB)),
      str(rules(tween('"#bg-glow"', BOB))))

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
  drift("#cd-ghost", 24, 14, 3.2);  /* motion-allow: decorative ghost layer */
  drift("#cd-iconwrap", 0, -10, 2.7);
})();</script>"""
found = check_motion.grade(helper)
check("a bob laundered through the drift() helper is still caught",
      any(f["rule"] == "keep-alive-motion" and "#cd-iconwrap" in f["detail"]
          for f in found), str(found))
check("...and the DECLARED call through the SAME helper is not flagged",
      not any("#cd-ghost" in f["detail"] for f in found), str(found))
check("the finding names the helper it came through",
      any("drift()" in f["detail"] for f in found), str(found))
check("the finding points the author at the CALL SITE, not the helper body",
      any("call site" in f["detail"] for f in found), str(found))

# The blanket exemption, refused. A helper body serves every caller, so an
# allow declared there would exempt content and decoration through one comment
# — which is the drift() laundering above wearing a different hat. Only a call
# site can speak for its own selector.
blanket = """<script>(function(){
  var drift = function (sel, ax, ay, per) {
    tl.fromTo(sel, { x: 0, y: 0 }, { x: ax, y: ay, duration: per,
      ease: "sine.inOut", yoyo: true, repeat: 4 }, 0);
      /* motion-allow: all drift is decorative, trust me */
  };
  drift("#cd-ghost", 24, 14, 3.2);
  drift("#cd-iconwrap", 0, -10, 2.7);
})();</script>"""
found = check_motion.grade(blanket)
fires(check, "check_motion", "keep-alive-motion",
      "a motion-allow in the HELPER BODY exempts no call site",
      sum(1 for f in found if f["rule"] == "keep-alive-motion") == 2,
      str(found))

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

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
