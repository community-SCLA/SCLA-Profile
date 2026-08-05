# PITCH A — skills-for-the-ai-era-future_early-career-boost

Lens: **metaphor-first**. One carrying object, drawn once, worked on for the
whole runtime.

## The carrying object

**A shoreline seen side-on — a sloping shore climbing from the lower-left to
the upper-right, stuck with labelled stakes, with a flat tide-line that only
ever climbs it.**

It is drawn as one continuous ground stroke from the lower-left corner to the
upper-right, with light diagonal hatch filling the wedge beneath it — that is
the land, and it is the only "background" the video has. The tide is a
horizontal band with a dead-straight top edge and a translucent fill, so a
stake it covers stays visible as a dimmed shape *through* the water rather
than being erased; a thin bright wet-line marks where water meets ground.
Skills are stakes: a single thick vertical stroke with a square cap and a
short label set beside it, full-ink while dry, dropped to a pale wash once the
water is over them. One taller post with a round cap is the viewer's position
on the shore, and every place it has stood stays behind it as a dashed track
of short paired dashes.

## Four frames

**At 25% — the low flat, and the first wet stake.**
The ground stroke runs the full width, mostly bare. Low on the shore, just
above the water, a tight knot of four capped stakes carries the skills the
narration has just named — judgment and decision-making, communication,
relationships, keeping learning. The tide band covers only the far lower-left
corner, and one older stake down-shore of the knot, labelled with the advice
the script itself names, is standing ankle-deep with its lower third already
under the translucent fill. The entire upper two-thirds of the frame is empty
drawn ground. Picture: a small dense cluster in the bottom-left quarter, a lot
of unclaimed slope.

**At 50% — the survey.**
The water now covers the lower third; the original knot sits just above the
wet-line, dry but behind us. The new geometry is up-shore: four plots staked
out on the higher ground with dashed rope boundaries and a corner marker each,
carrying the script's own four categories. Their boundaries deliberately cross
one another, and every plot interior is still **empty ground**. Picture:
top-right is now the busy half — angular dashed enclosures over open slope —
while the bottom-left is water and one stranded cluster. Nothing from frame
one has moved; the frame is busy in the opposite corner.

**At 75% — the crossed ground fills.**
The camera has not moved but the middle of the frame has gone dense: the
overlap regions where two plot boundaries cross are shaded, and one new
labelled stake stands in that crossed ground for each transferable skill as
the voice names it. The plot interiors that are *not* crossed stay bare —
the script says you do not need to chase all four. The position post now
stands inside the crossed ground with a dashed track running behind it, down
the slope, all the way back to the original knot. Picture: a packed
mid-to-upper band of stakes, a visible path of travel, water holding at
roughly the lower third.

**At 100% — the whole shore, pulled back.**
The drawing re-scales down so the entire coast fits one frame for the first
time. Left to right you can read: dimmed stakes lying under the translucent
tide, the wet-line, the abandoned low knot, the dashed track climbing, the
crossed ground thick with standing stakes, and — set apart from the track —
a single tall isolated rock stack with nothing planted on it and no dashes
leading to it, the one place the script says is not the goal. Beyond the
crossed ground, open unplanted slope keeps rising off the top-right, and one
more flat swell is drawn approaching the wet-line. Picture: a complete
coastal map with four legible zones of history, at a scale never used before.

## What accumulates

Three counters that only ever move one way, plus one thing that re-reads:

1. **Stakes.** The number of stakes standing on the shore only grows — the
   frame ends with several times what it opened with, each planted at the
   moment its skill is spoken and never removed.
2. **Water.** The tide-line only ever climbs. Ground that is dry at 25% is
   wet at 100%, and the stakes it covers stay drawn underneath it as pale
   shapes — the drawing keeps its own past, so "these lost value" is visible
   rather than asserted.
3. **The track.** The dashed trail behind the position post only lengthens.
   At 25% it does not exist; at 100% it is the longest single line in the
   frame and it has a direction.
4. **Re-read, not added:** the closing pull-back shows every earlier state at
   once at a new scale. The closing frame is un-drawable at 0:10 — at 0:10
   there is no submerged stake, no track, and no filled ground to shrink.

## The payoff beat

**The final pull-back, on the closing "ride the wave" line.** Up to that beat
the frame has always been a window on part of the shore; on this beat the
whole shore snaps into one view and the object completes: the wet lower
ground, the abandoned knot, the climbing track, the full crossed ground and
the next swell all read as one continuous movement up-slope. The lone rock
stack lands one beat earlier, drawn once and then simply passed by — the
track curves around it and keeps climbing, which is the argument's ending
said in shapes. This is also the shuffle test's answer: sort the contact
sheet by how high the water is and you have restored the true order.

## Why this is not lazy

A builder cannot satisfy this with headings swapped over a static prop,
because the concept's contract is *state that carries between beats*:

- A stake must be **dry in one frame and under water in a later one**. That
  requires the earlier frame's geometry to still exist, so the shore cannot be
  redrawn per beat.
- The **track only exists because the post stood somewhere else earlier**.
  There is no way to fake it from a single static layout — a lazy build
  produces a frame with no history in it and fails on sight.
- Plot interiors are **empty at 50% and full at 75%**. Same enclosures, same
  position, different contents — a heading swap changes neither.
- The closing frame is at a **different scale** from every frame before it,
  which no static prop composition can produce.
- Milestone frames for CONCEPT.md are therefore concrete and checkable:
  (M1) low knot planted, water in the corner only; (M2) four crossed plots
  staked, interiors bare; (M3) crossed ground full, track visible to the knot;
  (M4) pulled back, submerged stakes visible through water, rock stack
  bypassed. A contact sheet missing any one of these is a failed build, not a
  matter of opinion.

**Fidelity discipline (no invented facts).** Only the one past skill the
script actually names is labelled below the wet-line; the other submerged
stakes stay **unlabelled**, precisely because the narration says "the skills
it has mastered" without naming them. The four plots carry the script's own
four category descriptions, and the stakes planted in the crossed ground carry
the script's own transferable skills, one stake per skill at the moment it is
spoken — no totals, dates, percentages, job titles or ordering claims the
narration does not make. The rock stack is unlabelled and is drawn only
because the script explicitly rejects it.

**Gate fit.** The tide advances and stakes enter only on named beats and then
hold pixel-static — no idle ripple, drift or shimmer on settled content
(`check_motion.py`). Accumulation is the pace engine: planting one stake,
shading one overlap, or advancing the wet-line is a real new idea per beat
with almost no inter-beat churn, which is the approved-cut signature (high
idea-rate, low churn) rather than the rejected slow cut's constant swapping.
One hero illustration per frame throughout — the shore is the only
illustration the video has.
