# PITCH A — how-to-make-strong-career-decisions_early-career-boost

Lens: **metaphor-first**.

## The carrying object

**A single sheet of paper on a desk — folded shut into a narrow two-column pro-and-con strip at the open, unfolded one panel at a time into a wide five-panel decision sheet, and creased back into a reusable form at the close.**

It is drawn as physical paper, not as a diagram: a warm off-white rectangle with a visible edge and a faint drop shadow on the desk surface, its folds drawn as vertical crease rules (a hairline valley crease, a slightly darker mountain crease) that run the full height of the sheet. Everything written on it is drawn marks, not typeset panels — short ruled lines, small torn slips laid on the paper, a hand-drawn box with an empty date field, a stub of paper taped on at a slight angle. The sheet always fills the canvas: early it is shot CLOSE (the strip's two columns of tick marks legible at full frame height), and as panels open the view pulls back, so the object's detail-per-panel drops while its total ink climbs — the frame is never a small prop beside empty space.

## Four frames

**25% — the strip, close and crowded.** One narrow portrait panel fills the frame: two ruled columns of tick marks, plus and minus, packed to the bottom edge. Crease lines run off the left and right edges of frame, telling you the paper continues past what is open. The first crease is lifting — a single fold caught mid-open, showing the blank back of the next panel and nothing written on it yet. This is the "you can do much better" and "real uncertainty is normal" stretch: the sheet is all tallies and no method, and the paper it has not used yet is bigger than the paper it has.

**50% — three panels, the sheet turns landscape.** The frame has widened; the object is now horizontal. Panel 1 (the old strip) has shrunk to the left edge, its tick marks now the smallest, most crowded thing on the sheet. Panel 2 carries the decision written as one ruled question line with a small by-when box beside it. Panel 3 is the widening: torn option slips laid onto the paper in a loose column, arriving one at a time, with two later slips set slightly apart from the first group — the two extra asks. Nothing is numbered or scored.

**75% — four panels, and something is taped on.** Wider still. Panel 4 holds a short stack of ruled factor lines with the options' slips now sitting alongside them as a rough column, marks against lines rather than against a mood. Overlapping panel 4's right edge, a small stub of different paper is taped on at an angle — the cheap experiment: an interview note, a weekend's worth of scrap. One factor line has a heavier mark beside it: the assumption that mattered most. The sheet has physically grown a piece that is not part of the original fold.

**100% — the whole sheet, once, then a fresh one.** For the first and only time the full five-panel spread is visible edge to edge: strip, decision, options, factors + taped stub, and the final panel with a commit mark and an empty dated check-back box. A crease line is drawn from that last panel back to the question in panel 2, closing the sheet into a form that can be run again. Beneath it, offset by a few degrees, lies a second sheet — same fold pattern, creased, entirely blank.

## What accumulates

Four things, all visible:

1. **Panel count and silhouette.** 1 folded strip → 2 → 3 → 4 → 5. The object's outline changes shape (tall and narrow → wide and horizontal) as the argument advances; you can restore the order of any contact sheet from the paper's aspect ratio alone.
2. **Ink, monotonically.** Tick marks → a question line and a by-when box → option slips → factor rules and marks → a taped-on stub → a commit mark and a dated review box. Nothing written is ever erased or replaced; every earlier panel keeps its exact marks and holds pixel-static from the beat it entered.
3. **The opening artifact gets outmatched, not deleted.** The pro-and-con strip that filled the whole frame at 25% ends the video as the leftmost, smallest, most cramped panel of five. That demotion IS the script's "you can do much better", drawn rather than asserted.
4. **A physical addition that was not in the fold.** The taped stub is the only mark not made on the original paper — the sheet ends up bigger than the sheet it started as.

## The payoff beat

The closing beat. Two things land at once, and neither could have been drawn at 0:10: the full five-panel spread is seen as a single object for the first time (until then the frame has only ever held part of it), and the return crease from the review box back to the decision question re-reads the whole sheet — it stops being a record of one decision and becomes a blank-able form. The second, uncreased sheet beneath it is the last mark added: the same folds, ready, nothing written. The video opened on a scrap of tallies and closes on a reusable instrument made from that same piece of paper.

## Why this is not lazy

A builder cannot satisfy this with headings against a static prop, because **the prop is never static in outline**. Every step beat changes the paper's geometry — one more crease opened, a different aspect ratio, a different pull-back — so a single background asset with swapped text is structurally impossible; the frame at beat 6 has a different silhouette than the frame at beat 5.

Each panel's interior is also a **different drawn form**: tally columns, a ruled question with a date box, torn slips, factor rules with marks alongside, a taped-on stub, a commit mark and an empty dated box. Five panels, five ways of marking paper — nothing repeats, so there is no template to duplicate.

And accumulation is enforced by persistence: panel 3's slips must still be on screen, unchanged and in the same place, at 100%. A builder who re-draws the sheet per beat will visibly break continuity, and one who re-animates a settled panel trips `check_motion.py`. The only way to build this is to author the sheet's state at each beat as a strict superset of the last — which is exactly the concept's contract.

**Fidelity note for the builder:** the sheet carries only what the narration says. No counts are stamped on frame — not the number of options, not the number of factors, not a score. Nothing is rated, ranked, weighed, or balanced; there is no scale, no beam, no meter. The check-back date box stays empty.
