# Design — The Transition Axis

Rebuild of 2026-08-11. The previous design (a single "travel case" holding every
beat) was discarded at the owner's direction: diagonal hatch behind all type,
nothing vertically centred, labels sitting on top of illustration, and content
landing in the wrong compartment. Nothing from that version survives here.

## Carrying object

**One vertical transition axis with a fixed two-column skeleton.** It is built
once and only ever re-sorted; it is never torn down and redrawn.

Every scene composes into exactly the same regions:

```
head    x 160–1760   y 150–260    heading + optional attribution
stage   x 120–1800   y 300–960    left column | axis (x 960) | right column
foot                              full-width band, only where it earns its place
```

Each column carries the same three tiers — a small tracked label, one large
term, one supporting line — so a scene change re-sorts the frame instead of
repainting it. Measured inter-beat churn 5.96% against the 6% ceiling.

The column labels are the persistent identity: **Let go** (gold, left) and
**Carry forward** (blue, right), constant wherever that meaning holds, and a
constant pair — **What you earned / What it becomes** — across the translation
run. Those words occupy the same cells for the whole lesson.

No element is placed by a hand-tuned margin. Columns distribute with
`align-content:space-between`, so content reaches the top, middle and bottom of
the stage rather than floating as one centred island. No hatch, pattern or
texture sits behind type anywhere.

## Beat-to-frame map

| Time | Scene | What the frame does |
| --- | --- | --- |
| 0.000–12.420 | Title | The lesson title, with the two supporting claims set against it. |
| 12.420–24.610 | Two sides | The axis draws open; both sides are named at once. |
| 24.610–36.690 | The ending | "A Beginning" is struck through; "An Ending" replaces it. |
| 36.690–56.160 | Skipped | The Old Identity block crosses the axis and lands in the new role; three consequences follow. |
| 56.160–75.770 | Identity work | Cognitive and Emotional discs; permission to feel the loss. |
| 75.770–98.020 | Fifteen years | The stat is minimised as it is dismissed, then restored to full weight. |
| 98.020–110.300 | Translation | The axis becomes a gate: Hide is struck, Translate lights. |
| 110.300–120.505 | Finance | Earned term → connector → what it becomes. |
| 120.505–131.730 | Teaching | Same carrier, new pair; both translations persist as traces. |
| 131.730–150.150 | Inventory | Four dashed slots fill exactly as each is named. |
| 150.150–162.860 | Wrong order | Holding everything; the list greys out and becomes a defence. |
| 162.860–170.910 | Right order | 1 Let Go, 2 Carry Forward, both matter. |

## Motion

One paused GSAP timeline. Entrances settle once and never move again. The only
transformations that carry meaning: the axis drawing open, rules and strikes
drawing along their length, the Old Identity block crossing the axis, and the
fifteen-year stat shrinking once and being restored once. No loop, no yoyo, no
repeat, no progress rail, no attention pulse, no scene counters.

## Type and colour

Workspace `tokens.yml` only. Gold marks what is released or left behind; blue
marks what is selected and carried. Body copy never below the 40px floor;
tracked uppercase labels never below 20px.
