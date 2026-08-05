# Pitch A — finding-creating-a-career-purpose-statement_early-career-boost

**Lens: metaphor-first.**

## The carrying object

**A blank index card lying on a crowded desk — the card gets built, line by line, out of the loose notes already scattered around it, until the card is the only thing left on the desk.**

The desk is the whole frame: a flat top-down surface, no perspective. On it live two kinds of drawn thing. First, the **loose field** — small thin ruled slips (the criteria), a scatter of solid filled marks (the energy themes), and a folded, creased sheet with fold-lines still showing (the mapped options), all sitting at the outer band of the frame in three loose piles, unaligned, overlapping at the corners. Second, the **card** — one clean rounded rectangle, brand-stroke outline, two ruled lines inside it, a single clip at its top edge. Everything is drawn in flat fills and strokes: slips are rectangles of varying width, marks are dots and short bars, the card is an outlined panel. The card is small at the start and the field is large; that ratio inverts by the end, and that inversion is the whole video.

## Four frames

**25% — the crowded desk, the empty card.**
The frame is busy at its edges and empty at its center. The three piles of prior work ring the outside: ruled slips upper-left, filled energy marks upper-right, the creased folded sheet lower-left. Dead center sits the card, clipped, small, with two blank ruled lines and nothing on them. Sliding off the right edge of the desk, half out of frame, is a much larger, much denser plaque — heavy border, tight grey lines of text, the thing the card is *not*. The card is held by a clip, not glued or framed: liftable. Nothing has moved from the piles yet.

**50% — the card as a three-slot rail, two pieces docked.**
The card has grown to own the center third of the frame and its two ruled lines have resolved into a single horizontal rail broken by two dividers — three slots. Slot 1 holds a filled energy mark that has physically left the upper-right pile (you can see the gap it came from — that pile is measurably thinner than at 25%). Slot 2 holds a ruled slip lifted out of the criteria pile, and it has been *narrowed* on arrival — a wide slip trimmed to a short one. Slot 3 is not filled from the desk at all: a fresh mark is being drawn directly into it, still faint, arriving from nowhere on the desk. Below the card's bottom edge a small **discard margin** has started: two slips set outside the card, struck through — one oversized and ornate, one all-caps and hollow.

**75% — three rough drafts, one circled.**
The card has multiplied. Three cards sit in a row across the middle band, same slot skeleton, each carrying a visibly different rough line — uneven baselines, one line overrunning its slot, one too short. They are drawn *rougher* than the single clean card at 25%: sketch strokes, unfinished corners. Behind them the desk is nearly bare — the piles have been reduced to a thin residue pushed hard into the outer frame band, and the discard margin below has grown to a short row of struck-through slips. One of the three cards is circled, and only that one carries a ring of small ticks notched into its own border, one tick per quality the narration names — the qualities are marks *on the object*, not a separate panel.

**100% — one small card, and a track back to it.**
The desk is empty. No piles, no residue, no discard margin, no drafts — every one of them is gone. A single card, now the smallest it has ever been drawn, sits pinned at a fixed point slightly off-center. Its three slot dividers are gone; one unbroken line of text reads straight across it. A single thin open track curves out of the frame and returns to the card's pin — a return path to the card, not a diagram beside it. The frame that was busiest at its edges and empty at its center is now empty at its edges and holds one dense thing in the middle: the exact inverse of frame 1.

## What accumulates

**The card gains everything the desk loses, and the transfer is visible piece by piece.** Three separate ledgers move in one direction and never reverse:

1. **The loose field depletes.** It starts as three full piles and ends bare. Every slip that docks into the card leaves a visible gap in the pile it came from — the pile at beat N is the pile at beat N−1 minus what was taken. A builder cannot re-fill it.
2. **The card fills, then fuses.** Empty ruled lines → a rail with three empty slots → two docked pieces → three docked pieces → a written rough line → one unbroken line with the slot dividers gone. Six distinguishable states of one object.
3. **The discard margin grows, then clears.** It appears the moment the narration names what is *not* in the statement, accumulates the set-aside slips, and is swept off at the end.

The closing frame could not have been drawn at the 25% mark: at 25% the card is blank and the desk is full; at 100% the card is written and the desk is bare. Nothing about the picture is a moved highlight — the objects physically change hands.

## The payoff beat

**The slot dividers drop away.** On the "pick the one that rings truest / brief, easy to remember and easy to repeat" beat, the two losing drafts fold off the desk, and on the survivor the three dividers that had held the structure apart vanish — the three docked pieces butt together into one continuous line, and the card lifts off the desk and shrinks to pocket size. The scaffolding that made the statement buildable disappears, leaving a single sentence that reads as one thing.

That is the re-read: the card that began as an empty outline surrounded by a crowded desk is now the only object on the frame, and it **contains the desk** — every pile that ringed frame 1 is inside that one small card. The final beat then adds only the return track, so the last picture is "one card, and a way back to it."

## Why this is not lazy

A builder cannot satisfy this with heading swaps against a static prop, because **the prop is stateful and its state is the argument**. Every frame is defined by three counters — how much is left in the piles, how many slots on the card are filled, how many slips are in the discard margin — and each of those must differ from the frame before it. There is no legal frame that reuses the previous frame's desk with a new heading; if the piles look the same twice in a row, the concept has been broken, not merely under-decorated.

The concrete contract for `CONCEPT.md` milestone frames:

- The loose field's slip count is **non-increasing** across the whole runtime and must strictly decrease at every beat where a piece docks.
- The card must be in a **different one of its six states** in each quarter of the runtime; states never repeat once left.
- Slots 1 and 2 must be drawn arriving **from a named pile, leaving a visible gap**; slot 3 must be drawn arriving from **nowhere on the desk** — the two entrances are different animations because the narration describes two different things.
- The discard margin must be **absent** before the "notice what is not in there" beat and **empty again** in the final frame.
- The card's scale is monotonic in one respect: it is at its largest at the mid-point and at its smallest in the closing frame.

The failure mode this concept is built against is the thin-carrier rejection: a small prop on empty frames that never gains detail. Here the frame is dense from the first beat — it is dense with the *wrong* stuff, and the video is the work of moving the density into the right place.

**Fidelity note.** Every count and grouping on screen comes from the narration itself: three things a good statement blends, three parts to the structure, three quick versions, the five qualities as ticks, one or two sentences as the card's ruled lines. The three starting piles are named by the script's own opening list — criteria, energy themes, mapped options. No count, sequence, or claim is drawn that the script does not say; the piles carry no numbers, and no arrow asserts a derivation the narration does not state.
