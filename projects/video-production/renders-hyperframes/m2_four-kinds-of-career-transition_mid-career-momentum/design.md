# Design — The Crossing Field

## Chosen concept

The lesson's own instruction is the picture: *cross the two questions*. One
field is drawn once and never redrawn. Two dividing lines arrive, one per
question, and they cut the field into the four kinds. Every later beat lands
inside that same field — nothing is thrown away and restarted.

## Visual carrier

A single 2x2 field on the right two-thirds of the frame.

- The vertical divider is the first question (chosen | forced).
- The horizontal divider is the second question (adjacent | genuinely new).
- The four cells are the four kinds, each one named only when the narration
  names it, and each one carrying the same small bar: how much of the move is
  experience carried forward and how much is new ground.

The bar is the through-line. Read left to right across the four cells it says
the thing the script says: a Pivot and a Rebuild carry most of the past
forward, a Reinvention and a Forced Reinvention mostly do not.

Copy lives in a fixed left column: one heading, one supporting line, and for
the three enumerating beats a three-item list. The column changes every beat;
the field only ever gains.

## Beat-to-frame map

| Beats | Field |
| --- | --- |
| b01-b02 | field empty; the left column carries the opening |
| b03 | chosen \| forced divider, its two column heads, and the first question |
| b04 | the second question enters on the vertical caption |
| b05 | adjacent / genuinely new divider and its two row labels |
| b06 | the four empty cells appear — the crossing is complete |
| b07 | Pivot cell fills and is named (chosen, adjacent) |
| b09 | Pivot's carried/new bar and the legend |
| b11 | Reinvention cell fills and is named (chosen, new) |
| b13 | Reinvention's bar — mostly new ground |
| b14 | Rebuild cell fills and is named (forced, adjacent) |
| b16 | Rebuild's bar — mostly carried forward |
| b18 | Forced Reinvention cell fills and is named (forced, new) |
| b20 | Forced Reinvention's bar — mostly new ground |
| b21 | all four cells resolve to the same gold edge: none ranks above another |
| b22-b27 | field holds; the left column carries planning, reflection and close |

## Motion logic

One paused GSAP timeline, built from the timed clip attributes so no time is
hand-typed twice. Every entrance is a single additive move — a short rise and
fade, or a stroke drawn — and then the element is permanent and pixel-static.
Nothing loops, breathes, drifts or re-animates once settled. The left column is
the only element that leaves: it fades out before its successor fades in, so
two beats of copy are never on the frame together.
