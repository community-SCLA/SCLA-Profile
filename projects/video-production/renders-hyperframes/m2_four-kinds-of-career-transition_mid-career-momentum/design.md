# Design — Four Departure Lines

## Chosen concept

Rebuilt from scratch on 2026-08-07. The previous concept (a 2x2 "crossing
field" of bordered cells, each holding a small carried-forward progress bar)
was rejected: the axis captions crowded the cells, the rotated y-axis label
collided with the row labels, and the in-cell bars read as loading indicators
rather than meaning.

The replacement drops the grid, the cell borders, the axes and the bars. Each
kind of transition is drawn as **one line leaving one baseline** — a small
multiple, four of them stacked, read top to bottom like entries in a list.

## Visual carrier

Four **departure lines** on the right half of the frame. Every line is the same
object with two variables, and those two variables are exactly the lesson's two
questions:

- **Did you choose it?** — a chosen move leaves the baseline unbroken; a forced
  move shows a hard break (a gold cut) before the new line starts.
- **How big is the leap?** — an adjacent move rises a little above the level it
  left; a genuinely new move rises far.

So Pivot = unbroken, small rise. Reinvention = unbroken, big rise. Rebuild =
broken, small rise. Forced Reinvention = broken, big rise. Nothing else encodes
anything: no legend, no axes, no fill, no bar.

Each line carries its name above it (42px) and its two answers beside it as one
quiet uppercase caption — `CHOSEN / ADJACENT` — reusing the exact chips the
questions section introduced. That is the whole key, and it sits on the object
it describes.

The grey track under each line stays visible past the departure point, so the
rise is always read against the level the person left.

## Layout

- Masthead: program eyebrow, lesson title, one gold rule. Fixed, quiet, small.
- Opening (b01–b05): copy runs **full width** at display size — the right half
  has nothing to say yet, so it is not held open and empty.
- From b06: copy moves to a fixed left column (120–820) and the right stage
  (940–1800) is the carrier's home for the rest of the lesson.

## Beat-to-frame map

| Beats | Right stage |
| --- | --- |
| b01–b05 | nothing; copy is full width |
| b06 | first question + its two chips (CHOSEN, FORCED) |
| b07 | second question label |
| b08 | its two chips (ADJACENT, GENUINELY NEW) |
| b09 | chips retire; four empty tracks take the frame — the four kinds exist |
| b10 | Pivot: name, caption, line drawn — unbroken, small rise |
| b15 | Reinvention — unbroken, big rise |
| b20 | Rebuild — broken, small rise |
| b24 | Forced Reinvention — broken, big rise |
| b29 | all four endpoints resolve to gold at once: none ranks above another |
| b30–b38 | the four lines hold; the copy column carries planning and close |

## Motion logic

One paused GSAP timeline built from the timed clip attributes. Copy beats cross
fade (out before in, never two on frame). Each line enters once: the past
segment and the departure curve draw with a stroke-dash, the endpoint dot fades
up, and the mark is then permanent and pixel-static. Nothing loops, breathes or
re-animates after it settles. The only exit in the right stage is the question
key retiring at b09, which is what hands the space to the four tracks.
