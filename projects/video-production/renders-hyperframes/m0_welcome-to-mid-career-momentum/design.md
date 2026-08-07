# design.md — m0_welcome-to-mid-career-momentum

Concept: **Lens A, "The Career Map, Checkpoint by Checkpoint"** (see `CONCEPT.md`).

## Visual carrier

One horizontal route across the frame at y=612 with five milestone nodes
(x = 240, 610, 980, 1350, 1720). Node 3 is *the mid-career checkpoint* — the
place the viewer is standing. The route is drawn once at beat b04 and is still
on screen in the last frame. Every idea in the lesson is attached to it:
a "You are here" pin above it, node captions under it, and two attachment rows
below it. The gold **course-progress rail** across the top (y=210) is the same
journey read as time, and steps forward as the lesson advances.

Nothing is ever re-drawn on a fresh canvas. Movements turn over the message
zone (heading + one supporting line) and the two attachment rows; the route,
nodes, checkpoint, pin, brandmark, eyebrow and progress rail persist.

## Frame regions (1920x1080, all ink inside x 120..1806, y 120..960)

| y | region |
| --- | --- |
| 130 | program eyebrow (left) · SCLA brandmark (right) |
| 210 | course-progress rail, gold fill, steps at b06/b14/b16/b19 |
| 288 | message heading (h1 once, then h2 per movement) |
| 440 | one supporting line, or the commitment quote, or the CTA |
| 512 | "You are here" pin + stem above the checkpoint |
| 612 | **the route** — line, five nodes, lit 6–12-month segment |
| 660 | node captions (checkpoint, then the 6-to-12-month node) |
| 700 / 734 | attachment row A — label + declared `<ul>` list |
| 818 | attachment row B — declared `<ul>` list or a note |
| 894 | attachment row C — the anchor note |

## Beat-to-frame map

| Beat | What arrives on the map |
| --- | --- |
| b01 | eyebrow, brandmark, empty progress rail, lesson title |
| b02 | supporting line naming the coach |
| b03 | row A: "You're ready for" + three pills |
| b04 | heading turns over; **the route draws in** left→right with its five nodes |
| b05 | node 3 fills gold; "You are here" pin lands; checkpoint caption; supporting line |
| b06 | progress rail label + first gold step; supporting line turns over |
| b07 | heading turns over; row A becomes the four platform tools |
| b08 | supporting line; row B: the two support routes (declared 2-item list) |
| b09 | heading turns over; rows clear — the frame goes quiet before the tangle |
| b10 | row A: what you are juggling (three pills) |
| b11 | supporting line; row B question 1 |
| b12 | row B question 2 |
| b13 | row B question 3 |
| b14 | heading turns over; questions dim; the 6-to-12-month segment lights gold; its node caption; rail steps |
| b15 | row A: the three things this track does |
| b16 | heading turns over; the commitment quote takes the supporting line, gold-ruled; questions clear |
| b17 | row B note: write and submit it |
| b18 | row C: the gold anchor note; the checkpoint node gains its anchor ring |
| b19 | heading turns over; the route completes past the last node; rail fills; gold CTA |

## Motion logic

Establish → transform → settle, once per beat and finished inside ~1.0s of the
beat start, so every beat midpoint is a settled frame and any seek lands on a
readable state.

- **Establish**: the route line and the lit segment use `scaleX` from
  `transform-origin: left` (the token `rule` behaviour, 0.6–0.9s `power3.out`).
- **Transform**: attachments arrive with `autoAlpha` + a 20–26px rise,
  `power3.out` / `back.out(1.4)` for nodes, staggered 0.12–0.16s within a row.
- **Settle**: nothing. There is no repeating tween, no `yoyo`, no `repeat`
  anywhere in this build — settled content never re-animates in place.
- Departures are `autoAlpha: 0` over 0.3s `power2.in`, started before the new
  content rises, so the two never share the frame.

## Copy discipline

On-frame copy is markup, never JS strings. Every visible line is a compression
of its own beat's narration — no new fact, count, step or promise. The program
eyebrow is `tokens.yml programs: mid-career-momentum` and the lesson title is
the canonical stem; neither is improvised. Lists are real `<ul>`/`<li>` so the
one-item-list rule can grade them. Headings are `<h1>`/`<h2>`.

## Timing

`timing.json` (from `plan_timing.py` over `audio_meta.json`) owns every number in
this composition: clip `data-start`/`data-duration`, the root duration, the
`<audio>` placements and the GSAP cue table. No timestamp is hand-tuned.

## Narration note

The beat manifest is the approved script verbatim (0.00% diff, 280/280 words)
with one punctuation-only change: the comma inside "small, consistent steps"
(b15) is dropped so the sentence's comma list ends on its "and" — the standing
`missing-conjunction-comma-list` copy rule fires on the approved script itself.
No word is added, removed or reordered.
