# CONCEPT — career-building-is-a-repeatable-process_early-career-boost

Winner: **Pitch B** (path + wheel). Judged against `design-system/docs/taste.md`.

## Concept angle

A **stone path laid decision by decision across the canvas** — carried from the
title card to the final frame — which at 75% surrenders the six-station
loop-wheel that turns out to have been pressing it all along.

## Milestone frames (the accumulation contract)

**25% (~0:37, "Look back at where you started" / Module recaps).**
The opening **boulder** — "one big right choice" — sits abandoned off-trail at
frame left, dimmed, and stays there all runtime. From it a walked stretch of
laid stones crosses ~a third of canvas, carrying **three milestone flags**
gained one per recap beat: M1 strengths/values/energy · M2 the five criteria ·
M3 Career Purpose Statement. Path already has history.

**50% (~1:15, "turn all of that into a practical plan").**
Laid path reaches a bright **"you are here"** edge at mid-canvas. Ahead: four
**empty stone outlines** — direction · skills · people · ninety days. The first
fills as narration names it; the rest fill across the following beats. Behind,
the walked stretch and three flags are untouched.

**~68% (~1:42, "Your map is not frozen… that is not a sign you did something
wrong").** *(grafted)* One already-laid stretch is **re-laid on a corrected
line**: the superseded stones stay visible as faded history, the new run bends
away in gold. Nothing is erased — the path now visibly records a change of mind.

**75% (~1:52, "a repeatable loop instead of a fixed plan" → "you now own a
process").** The reveal: a **six-station wheel** assembles at the leading edge,
one spoke per station — Clarify · Widen · Set Criteria · Test · Decide & Act ·
Review — and as each spoke lands, a gold tick is **added** to the stretch of
path it explains. The tool was inside the journey all along. Completed wheel
settles on the path edge and presses the next stone.

**100% (~2:30, "Every professional you admire is running some version of this
same loop. They just started earlier.").** Pull-back: full path corner to
corner — boulder, three flags, four filled plan-stones, the corrected bend, the
wheel — and **three or four fainter parallel paths** above and below, each
longer, each showing the same six-tick press pattern. One stone at your leading
edge glows gold: "take it this week."

## What accumulates

Stone count (strictly increasing) · flags 0→3 · plan slots 0→4 filled · a
corrected stretch that keeps its old line · wheel spokes 0→6 · paths 1→many.
Nothing re-animates in place; the 100% frame contains everything the runtime
earned and could not have been drawn at 0:10.

## Payoff beat

The 75% wheel assembly, re-read by the 100% pull-back: your one path becomes
one of many, all pressed by the same wheel. This is the deliberate rebuttal of
the rejected-thin cut, which **opened** with the six-dot loop and never earned
it. Here the loop does not exist before 1:45.

## Grafted from the losing pitch (A)

A's **revision beat** — a committed route struck through and redrawn on a
better line, the old line surviving as visible history. B had no beat for the
script's "your direction can and will change… not a sign you did something
wrong". Folded in at ~68% as the corrected path stretch. Nothing else grafted:
A's parchment/ink/lettering register is off-palette and unbuildable under the
gates.

## Feasibility notes for the builder

- **No texture, no lettering, no parchment.** Flat brand geometry only: stones
  are rounded rects, flags are triangle + stem, the boulder one dim polygon.
  Palette from `tokens.yml` — laid/past in blue, active and "this week" in gold.
- **Cap the stones at ~18–22 total**, ~34–44px each, added in groups per beat.
  Countability must be legible on a contact sheet, not a gravel field.
- **Do not "lift marks off" the walked stones** — that re-animates settled
  content (`check_motion.py`). Compliant equivalent: spokes draw in from the hub
  one at a time (`stroke-dasharray`), and each ADDS a new gold tick to its path
  stretch. Additive only, one pass, then static.
- **Wheel sizing is the real constraint.** Six labels at ≥40px body must sit
  clear of each other: wheel ~560–620px, placed right of centre, labels outside
  the rim with short leaders. Verify with `check_fit.py` before committing.
- **One hero per frame** — the path/wheel is it. No icons beside labels.
- **Pull-back = one scale+translate on the path group, once.** Parallel paths
  fade in at low opacity, unlabelled, and hold.
