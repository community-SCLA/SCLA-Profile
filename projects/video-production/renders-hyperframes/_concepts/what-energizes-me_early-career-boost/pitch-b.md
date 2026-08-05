# PITCH B — what-energizes-me_early-career-boost

**Lens: accumulation-first.** The build-up below was decided before the object was named.
**Working runtime:** the script is ~483 narrated words → ~3:10 (≈190s) at the pinned voice.
Ladder marks are given at 0:30 / 1:00 / 1:30 / 2:00 / 2:30 / close; if the synthesised
runtime lands materially shorter or longer, hold the *order* of the rungs and scale the
clock. At ≥8 beats/min this is ~28–32 beats, and every rung below breaks into 4–6 of them.

## The accumulation ladder

What the frame has GAINED at each mark — physically more, denser, re-sorted, or newly connected.

- **0:30 — the surface gains occupants.** The frame starts as a ruled board carrying only
  five faint marks left over from the previous lesson ("the five conditions worth looking
  for"). Those five get demoted to a small corner card, and the board's bottom rail gains
  its first heap of loose slips — unsorted, uninked, piled, no structure above them yet.
  *Gain: empty ruled surface → occupied at the bottom edge.*
- **1:00 — the board gains a coordinate system, and every slip gains a side.** A single
  vertical gutter rule is drawn down the middle; the heap migrates up and splits into two
  populated columns; each slip's bottom edge resolves into one of two profiles. Two loud
  false attractors are struck out in the top margin and left visible, not erased.
  *Gain: geometry + polarity. Nothing was removed to get it.*
- **1:30 — the board gains density, and a vocabulary it hasn't used yet.** Many more slips
  land in BOTH columns — the drain side keeps filling too, it is never swept away — and a
  rail of five word-tags lands along the top edge, unpinned, hanging there unused.
  *Gain: more marks, plus a set of labels with nowhere to go yet.*
- **2:00 — the field gains edges.** No new slips. Threads are pinned corner-to-corner
  between slips that share something, including several that cross the gutter, and the
  first two thread-clusters visibly bulge out of the even scatter.
  *Gain: connection — the same population, now a network.*
- **2:30 — the slips gain interiors.** A question-pin steps down the left margin, one
  position at a time; each stop inks two or three slips from blank rectangles to slips
  with three or four ruled interior lines. Density moves *inside* the marks.
  *Gain: detail per slip, and a visibly uneven ink map across the board.*
- **Close (~3:10) — the board gains a second reading.** The vertical gutter is struck
  through; three full-width horizontal bands are ruled across the whole board; every slip
  slides into a band; three tags come off the rail and pin to the band heads while the
  remaining tags grey out in place; the right-margin direction edge, faint since 1:00,
  inks solid. *Gain: resolution — the sort axis itself is replaced.*

## The carrying object

**The Energizing Work Worksheet, drawn at wall size — a pinned two-column board that fills
with experience slips, gets threaded, and finally re-sorts into named horizontal bands.**

Drawn as a full-bleed ruled board holding ~80% of the safe area, one hairline vertical
gutter, two column heads in the brand display weight (tokens per
`design-system/config/tokens.yml` — no hexes restated here). An experience is a **slip**: a
3:2 rounded rectangle, hairline border, whose *bottom edge profile* carries its charge —
serrated for the ones that left you buzzing, dead-flat for the ones that left you flat —
so polarity survives greyscale and never depends on colour alone. A slip's interior is 0–4
ruled ink lines: that is how specific the example is, and it only ever goes up. Threads are
single-weight straight chords between slip corners; bands are full-width tinted lanes that
*replace* the gutter rather than sit beside it; the direction edge is a hairline arrow-rule
in the right margin that starts at 20% opacity and finishes solid.

## Four frames

- **25% (~0:48) — "keep two columns in mind."** Bottom-heavy and mostly empty: a heap of
  plain slips along the bottom rail, one vertical gutter rule half-drawn, the five-mark
  corner card top-left, wide open board above. Nothing is sorted yet.
- **50% (~1:35) — "the patterns aren't always obvious."** Top-heavy and vertical: two
  dense, roughly balanced columns of sided slips, serrated and flat edges legible at a
  glance, two struck-out attractors in the upper margin, no threads. The gutter dominates
  the frame.
- **75% (~2:23) — the coach lane.** A web: threads cross the gutter, two clusters bulge
  out of the grid, the ink map is visibly uneven (some slips near-black with four lines,
  their neighbours still blank), a question-pin sits mid-way down the left margin, and the
  five-word rail hangs across the top still unpinned.
- **100% (~3:10) — the re-read.** Horizontal: gutter struck out, three full-width bands,
  every slip re-sorted into a band, three tags pinned to band heads with the rest greyed at
  the rail, direction edge solid off the right margin.

No two of those four could be mistaken for each other, and the sheet's order is
reconstructable from the pictures alone: occupancy only rises, interior ink only rises, the
rail only ever loses tags to band heads.

## The payoff beat

**The final beat — "Two or three patterns. That's all you need to start pointing yourself
somewhere."** The gutter is struck and the board re-reads on a new axis: what was a
left/right sort of *your past* becomes a top-to-bottom set of *ingredients*, pointing right.
The five-word rail that has hung unused since 1:30 is what makes it land — the viewer has
been looking at those tags for ninety seconds with nowhere to put them, and the payoff
spends them. The closing frame is literally undrawable at 0:10: at 0:10 there are five faint
marks and no slips, no gutter, no threads, no bands, no rail.

**Fidelity guard on this beat:** the pinned tags come only from the five contribution words
the script itself names, and no on-frame copy claims those are *the viewer's* patterns —
the pinning demonstrates the mechanic the narration describes ("it reflects back the two or
three patterns it hears"). No slip count is ever shown on frame; growth is read by area
covered, never by a number the script does not say. Every drawable element traces to the
narration: five conditions, two columns, buzzing vs flat, the struck lightning-bolt and job
title, the five ways of contributing, one question at a time, two or three themes, a
direction.

## Why this is not lazy

A builder cannot satisfy this with heading swaps against a static prop, because the prop is
required to be **geometrically incompatible with itself** across the runtime. At 0:30 there
are no columns — a heap on a rail. At 1:00 the gutter exists and every slip is sided. At
2:30 slips carry interior line-counts they did not have at 2:00. At the close the gutter is
*gone* and the axis is horizontal. A single board cannot be a two-column board and a
three-band board at once, so the states have to be authored, not re-labelled.

Three of the ladder's rungs also add nothing new at all — 2:00 adds only threads to an
unchanged population, 2:30 adds only interior ink — which forecloses the cheapest legal
pass (keep adding cards, keep swapping the heading). And each rung is checkable off a
contact sheet as a monotone quantity: slip count, interior ink lines, threads, tags
remaining on the rail. If a beat range has none of those moving, it is visibly a dead
stretch and the reviewer can name it.

Motion stays clean under `check_motion.py`: everything here is an entrance, a migration, or
a re-sort of not-yet-settled content. Nothing already placed wobbles, pulses, or re-marks
in place — the board earns more, it never swaps faster.
