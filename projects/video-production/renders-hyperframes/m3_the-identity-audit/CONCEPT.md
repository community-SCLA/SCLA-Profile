# CONCEPT — m3_the-identity-audit (Career Transitions)

Two lenses were developed and scored. **Lens A — The Stack** is selected.

---

## SELECTED — Lens A: "The Stack"

**Visual thesis.** The lesson's first claim is that career identity is *layered*
— what looks like one solid thing is five. So the picture is one object: a
vertical stack of five bands on the left of the frame. It starts as a single
visible band (the title), grows downward into five, gets numbered, gets named
one layer at a time, gets interrogated, and ends fully lit. Nothing else on
screen is ever redrawn from scratch; the right-hand column is the only surface
that turns over, and it turns over one thought at a time.

**Recurring carrier object.** The five-band stack. It is present in every one of
the 31 beats, at fixed coordinates, from the first frame to the last. Every
argument move in the lesson is expressed as a change of *state* on that stack —
a band appearing, an accent lighting, a numeral landing, a name arriving — never
as a new picture.

**Beat progression (5 acts, 31 beats).**

| Act | Beats | What the stack does | What the right column carries |
| --- | --- | --- | --- |
| 1. One layer, then more | b01–b03 | band 1 alone; bands 2–5 grow in beneath it | lesson title, then the two opening claims |
| 2. Not all at once | b04–b08 | release / not-yet / reframe marks appear and clear | the good news, and what the audit is for |
| 3. The five layers | b09–b17 | numerals 1–5 land; each name arrives on its own band as it is spoken | one layer's detail at a time |
| 4. Three questions | b18–b23 | stack cools to reference state | the three audit questions accumulate |
| 5. Ritual, and close | b24–b31 | stack relights, all five accents gold | Forbes finding, three rituals, closing line |

**Three milestone frames.**

1. **b03 — "What Sits Underneath."** Band 1 sits alone with a gold accent; four
   more bands fade in beneath it in a downward stagger. This is the thesis
   frame: the single layer becomes a stack.
2. **b13 — "Relationships."** Band 3 is lit and named, bands 1–2 carry their
   names already, bands 4–5 still blank and numbered. The right column holds a
   four-item list. The frame *shows* progress through the audit without a
   progress bar.
3. **b31 — "Close This Chapter Well."** All five bands named, all five accents
   gold, a gold rule resolving beneath the stack, one closing line at right.
   The object built across three minutes is finally whole.

**Motion logic.** Establish → transform → settle, once per beat and never again.
Entrances are 0.45–0.55s opacity + 14px rise, staggered 0.14s, all settled well
inside the beat. Exits are 0.3s opacity only, and only for the right column.
Furniture (eyebrow, stack geometry) never moves after it arrives. There is no
ambient, repeating, or keep-alive motion anywhere — no tween in this build
carries `repeat` or `yoyo`.

**Primary risk.** Carrier drift in the wrong direction: because the stack holds
still, the beat-to-beat frame change could fall *under* the animacy floor on the
quiet beats (a twin pair), while the four act transitions spike it. Mitigation:
every beat owns at least one full line of new on-frame text or one new stack
element, and the act transitions are staged so that no two large changes land on
the same beat boundary.

---

## REJECTED — Lens B: "The Audit Ledger"

**Visual thesis.** The audit is a table: five layers down the side, three
questions across the top. The lesson fills the grid cell by cell.

**Recurring carrier object.** A 5x3 matrix, drawn empty at the top of the lesson
and completed by the end.

**Beat progression.** Act 1 draws one row; act 2 explains the row's three
states; act 3 fills the five row labels; act 4 opens the three columns; act 5
marks the honour column with ritual chips.

**Three milestone frames.** (1) The empty grid, ruled and labelled. (2) One row
fully marked while the other four wait. (3) The completed grid with the third
column gold.

**Motion logic.** Rules draw in with scaleX from the left; cells fill with a
mark that scales from 0.

**Primary risk — why it was rejected.** Fifteen cells plus five row labels plus
three column headers inside a 1680x840 content area forces body type well under
the 40px floor this system enforces, and the three question strings are 7–10
words each — as column headers they either wrap to four lines or shrink. The
grid also fights the script: the three questions are asked *once*, generically,
not five times per layer, so a completed 5x3 matrix would assert something the
approved script never says.

---

## Scores (1–5)

| | claim fidelity | visual evolution | attention | feasibility | total |
| --- | --- | --- | --- | --- | --- |
| **A — The Stack** | 5 | 5 | 4 | 5 | **19** |
| B — The Audit Ledger | 3 | 4 | 3 | 2 | 12 |
