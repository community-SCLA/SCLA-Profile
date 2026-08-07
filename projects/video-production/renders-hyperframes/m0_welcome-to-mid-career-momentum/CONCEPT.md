# CONCEPT — m0_welcome-to-mid-career-momentum

Two lenses were proposed and scored (scores in `concept.json`). **Lens A —
"The Career Map, Checkpoint by Checkpoint" — is selected.**

---

## Lens A (SELECTED) — The Career Map, Checkpoint by Checkpoint

**Visual thesis.** The lesson says, in its own words, that this track is "the
mid-career checkpoint in your career map." So the frame *is* the map. One
horizontal route is drawn once, early, and never redrawn. Everything the lesson
says afterwards is placed onto that route: the checkpoint you are standing on,
the tools you carry, the branches you are weighing, the segment you will
actually walk next, and the commitment you pin to it. Nothing is thrown away and
nothing arrives on a fresh canvas — the picture at the end is the picture from
the beginning, fully annotated.

**Recurring carrier object.** The route: a single navy-to-gold rail running
left→right across the frame at y≈600, carrying five milestone nodes. It appears
in beat 2 and is still on screen in the final frame. The checkpoint node (node
3, the one the viewer is standing on) is the anchor everything else attaches to.

**Beat progression (19 beats, 7 movements).**

| Movement | Beats | What happens on the map |
| --- | --- | --- |
| 1. Arrival | b01–b03 | Title and program eyebrow settle; the route draws in; the "You Are Here" pin lands on the checkpoint node; a short line names the experience already behind you. |
| 2. The checkpoint | b04–b06 | The route is named as the career journey; the checkpoint node fills gold and gains its label; the progress rail along the bottom appears and takes its first step. |
| 3. What you carry | b07–b08 | Four tool chips clip onto the route under the checkpoint; a support tag attaches beside them. |
| 4. The tangle | b09–b13 | Three weight tags press down on the checkpoint; then three branch lines fan forward out of it, one per question the lesson asks. |
| 5. The next move | b14–b15 | Two branches dim; the 6–12 month segment of the route lights gold; three step markers appear along that segment. |
| 6. The commitment | b16–b18 | A commitment card pins to the lit segment and takes the 90-day statement; the pin is named as the anchor. |
| 7. Go | b19 | The route completes to the far edge and the CTA resolves. |

**Three milestone frames.**
1. *b05 (~30s)* — the full route, checkpoint node gold and labelled, dark navy
   field, one heading above it. Sparse, calm, oriented.
2. *b13 (~85s)* — the busiest frame: checkpoint carrying four tool chips, three
   weight tags and three forward branches. The visual argument for "mid-career
   can feel complicated" is made by density, not by a new picture.
3. *b17 (~112s)* — the same frame, resolved: branches dimmed to one, the next
   segment lit gold, three step markers on it, the commitment card pinned.

**Motion logic.** Establish → transform → settle, once per beat, all inside the
first ~1.0s of the beat so every midpoint frame is a settled frame.
Establish = the route drawing (scaleX from the left, the token `rule` behaviour).
Transform = attachment: a chip clips on, a node fills, a branch extends, a tag
dims. Settle = nothing. No looping, no yoyo, no keep-alive drift anywhere in the
build; when a beat has nothing new to say, it says nothing and the frame holds.

**Primary risk.** Density. By movement 4 the checkpoint carries eleven attached
objects, and the inspector treats overlapping text as fatal. Mitigation: every
attachment has a reserved lane (tool chips on one row, weight tags on another,
branches in a fan with fixed angles), and the copy attached to any object is at
most four words.

---

## Lens B (rejected) — The 90-Day Anchor Card

**Visual thesis.** The lesson ends on one artefact — a written 90-day
commitment — so start there: an index card sits centre-frame from the first
second, blank, and the whole lesson is the act of filling it in. Each beat
writes one more line onto the card or annotates its margin.

**Carrier.** The card itself, fixed at centre, growing annotations.

**Beat progression.** b01–b03 card appears blank with the lesson title on its
header; b04–b06 a progress ribbon runs down its edge; b07–b08 tool icons stamp
along the left margin; b09–b13 three question marks scribble into the margin;
b14–b15 a "next 6–12 months" band crosses the card; b16–b18 the commitment
sentence writes itself into the ruled centre; b19 the card is signed.

**Milestone frames.** b03 blank card on navy; b13 card crowded with margin
notes; b18 card with the finished commitment sentence.

**Motion logic.** Type-on and stamp-on, always inside the card's bounds.

**Primary risk.** The card is a fixed rectangle, so every idea has to be
expressed as text inside it — the lesson stops being illustrated and becomes a
document being typed. It also has nothing to say about "journey", "checkpoint",
"progress" or "branches", which is most of what the script is about.

---

## Why A

A is the lesson's own metaphor, given by the script rather than imposed on it,
and it has a natural place to put every one of the seven movements. B scores
well on continuity (the card never moves) but poorly on visual evolution: a
rectangle that fills with sentences cannot show a branch, a segment, or a
distance travelled, and by beat 13 it would be a wall of small type — which is
the exact failure the type floors exist to prevent.
