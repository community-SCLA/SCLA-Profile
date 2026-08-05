# design.md — brand truth for `what-energizes-me_early-career-boost`

Design source of record for this one video. Every brand value is LOADED from
this workspace's own `tokens.yml` copy (colors, type floors, spacing, the pinned
Oxana voice, the program display name); nothing here restates a number a gate
also reads.

Lesson: `lesson-scripts/early-career-boost/ready/what-energizes-me_early-career-boost.txt`
Lane: freeform (agent-native) — no templates, no `scenes.json`, no compiler.
Starting contract: `renders-hyperframes/_concepts/what-energizes-me_early-career-boost/CONCEPT.md`.

## Concept angle

> **The Energizing Work Worksheet drawn at wall size — one pinned board fed by a
> finite reserve of experience slips that visibly empties into it, and every beat
> of the lesson is another mark made ON that board, never a second picture.**

**Persistence: beats s02 → s40, i.e. ~97% of the runtime** (s01 is the title
card, and it already plants the board's first five marks). The board is drawn
once and is never cleared, never rebuilt and never left.

**The rule, stated out loud:** *if an element cannot be justified as another way
of reading the same board, it does not exist.* Nothing enters this frame except
as a slip ON the board, a mark INSIDE a slip, a thread BETWEEN slips, a rule
ACROSS the board, or a piece of furniture pinned to one of its four margins.
There is no second illustration and no decorative object.

## Where this sharpens CONCEPT.md (stated, never silent)

1. **Struck attractors: two → four.** CONCEPT.md pins the lightning-bolt answer
   and the job title. The script strikes two more by name — "passion is vague and
   high-pressure" (s04) and "not what you think you *should* enjoy" (s26) — so the
   struck-chip row is a fifth monotone counter (1 → 2 → 3 → 4) rather than a
   one-off pair. Same mechanic, more of the script carried by it.
2. **The reserve's last three bars are spent AT the payoff**, not before it.
   CONCEPT.md wants slip population frozen from ~2:00 *and* the reserve gone at
   the close; under strict conservation those cannot both be true unless the
   final slips are the payoff's own move. So the reserve holds a visible stub of
   3 from s20 to s38 — the 75% "stub" the contract asks for — and spends it at
   s39 as the bands rule across. The receipt (an empty outline where the stack
   stood) is drawn exactly as specified.
3. **The question-pin becomes an explicit 9-notch descent** down the left margin,
   one notch per coach beat, because CONCEPT.md's judge note names the AI-coach
   stretch as the place this concept will coast. The pin is the thing that makes
   that stretch legible at thumbnail size.

## The carrying object — geometry

Canvas 1920×1080. Content lives inside the loaded keep-outs; the only element in
the top keep-out is the program eyebrow, inside the rectangle `tokens.yml`
`chrome-regions` grants by name.

| Part | Box | Notes |
| --- | --- | --- |
| Board | x 150–1770, y 126–958 | 1620×832 = **82% of the safe area**, at every beat |
| Head band | y 126–250 | the beat heading (58/900), one line |
| Head rule | y 250 | hairline, full board width, inks at s02 |
| Tag rail | y 262–328 | rail line + five word-tags, hung and unpinned from s23 |
| Column heads | y 342–394 | `Energizes` / `Drains`, a declared 2-card compare |
| Slip field | y 406–870 | 11 ruled lines; 4 grid rows left of the gutter, 3 right |
| Gutter | x 905, y 406–870 | hairline; drawn in four steps, struck at s39 |
| Left margin | x 150–250 | the question-pin's 9-notch track |
| Right margin | x 1580–1740 | the reserve stack, 32 bars, only ever falling |
| Direction edge | x 1752–1760 | faint from s15, inks solid on the final beat |
| Struck-chip row | y 890–948 | the board's foot; four attractors, ruled out and left visible |

The struck attractors sit on the board's FOOT rather than in CONCEPT.md's top
margin: in the head band their arrival transform crossed the beat heading's own
zone, and `check_layout`'s inspector reported that collision at every heading
swap. On the foot they are still "left visible rather than erased", still
monotone, and nothing overlaps.

A slip is 96×64, hairline-bordered. Its **bottom edge** carries the charge —
serrated for buzzing, dead-flat for flat — so polarity survives greyscale. Its
**interior** is 0–4 short ruled strokes; strokes are only ever added.

## What accumulates — six monotone counters

Every one is countable off a contact sheet without reading a word.

1. **Slips placed** — 0 → 32, only rises, frozen from s20 to s38 by design.
2. **Reserve bars** — 32 → 0, only falls, conserved 1:1 against (1); its empty
   outline is drawn at the close.
3. **Interior strokes** — only rises, and unevenly, so the board gains texture
   rather than population.
4. **Threads** — 0 → 60, only rises, over a population that has stopped growing.
5. **Struck chips** — 0 → 4, only rises, left visible rather than erased.
6. **Tags on the rail** — 5 → 2, falls only at the very end.

Plus one non-monotone position that reads at thumbnail size: the **question-pin**,
descending its 9 notches across the coach stretch.

The board changes its sort axis exactly ONCE, late: a left/right sort of your
past becomes a top-to-bottom set of ingredients. That re-arranges material
already on screen, which is why the closing frame is undrawable at 0:10 — at
0:10 there are five faint ticks, no board, no slips, no gutter, no threads, no
bands and no rail.

## Milestone frames — the accumulation contract

- **25% (≈s10)** — bottom-heavy, nothing sorted. Reserve at full height on the
  right. A loose heap of unsided slips along the bottom rail. Gutter drawn only
  partway from the top. Last lesson's five conditions demoted to a corner card.
  *Dominant axis: the floor.*
- **50% (≈s17)** — vertical. Gutter full height and doing real work; the heap has
  migrated up into two populated columns, the left denser but the right genuinely
  populated and staying. Every slip sided. Reserve about half. Three struck chips
  ruled out on the board's foot. No threads; every interior still blank.
  *Dominant axis: the vertical.*
- **75% (≈s31)** — a web with an uneven ink map. Population unchanged since s20.
  Threads pinned across the field, several crossing the gutter, two clusters
  bulging. The question-pin sits partway down the left margin; the slips it has
  passed carry three or four strokes while their neighbours are still blank. The
  five-tag rail hangs unpinned. The reserve is a stub of three. *Dominant axis:
  the web.*
- **100% (s40)** — horizontal, re-read. Gutter struck through. Three full-width
  bands ruled across, every slip slid into one. Three tags off the rail and
  pinned to the band heads; two greyed in place. The reserve is gone, its empty
  outline left as the receipt. The direction edge inks solid off the right margin.
  *Dominant axis: the horizontal.*

No two of those four can be mistaken for one another.

## Every beat moves a counter — and every beat moves twice

Two arrivals per beat, both on that beat's own word timings: one at its opening
word, one in its **back half**. A beat whose picture is finished halfway through
is dead air for the rest of it, so no beat has a single arrival.

| Beat | Opening arrival | Back-half arrival | Counter(s) |
| --- | --- | --- | --- |
| s01 | title card + gold rule | five condition ticks appear | — (plant) |
| s02 | title lifts; board draws and **11 ruled lines ink across it**; ticks migrate to the corner card | head rule inks full width; gutter draws 30% | board born |
| s03 | heading; `Passion` chip arrives | column heads ghost in | — |
| s04 | gutter jumps 30% → 75%; column heads ink solid | `Passion` chip struck; four corner pins | struck 0→1 |
| s05 | heading; gutter to 90% | the board's own border inks | — |
| s06 | heading | **the reserve arrives**: 32 bars, full height | reserve 32 |
| s07 | 5 slips fly out, one per named noun | last two nouns land in the heap | slips 0→5, reserve →27 |
| s08 | 5 heap slips gain serrated bottoms | +3 slips, serrated | slips →8, reserve →24 |
| s09 | 3 slips gain flat bottoms | +2 slips, flat | slips →10, reserve →22 |
| s10 | heading | +3 slips; heap re-orders so both edges read | slips →13, reserve →19 |
| s11 | heading; **gutter completes to full height** | column heads ink; column rule draws | axis set |
| s12 | heading = the worksheet's own name | the tag rail's line and the column rule ink | identity |
| s13 | heading; the struck-chip bracket inks | +2 slips | slips →15, reserve →17 |
| s14 | `A Lightning-Bolt Answer` chip arrives, struck | +2 slips | struck →2, slips →17 |
| s15 | heading; **the migration** — the whole heap flies up into two columns | direction edge appears, faint | axis change |
| s16 | `A Job Title` chip arrives, struck | +3 slips into the columns | struck →3, slips →20 |
| s17 | heading | +4 slips; every slip now sided | slips →24, reserve →8 |
| s18 | heading; +1 slip | **question-pin arrives** at the top of its track | slips →25, pin 0 |
| s19 | +1 slip | 4 slips gain their first stroke | slips →26, strokes start |
| s20 | heading; +3 slips — **population frozen here** | 5 more slips gain a first stroke | slips →29, reserve →3 |
| s21 | heading; **first 5 threads**, two crossing the gutter | +4 threads | threads →9 |
| s22 | heading; pin to notch 1; 6 slips gain a 2nd stroke | +3 threads | pin 1, threads →12 |
| s23 | heading; **the tag rail** — one tag per named word | the rail line inks blue under them | tags 5 hung |
| s24 | heading; direction edge gains 3 ticks | +3 threads | threads →15 |
| s25 | heading; 5 slips gain a stroke; pin to notch 2 | +2 threads | pin 2 |
| s26 | +3 threads | `What You Should Enjoy` chip arrives, struck | struck →4 |
| s27 | heading; 4 slips gain strokes; pin to notch 3 | +2 threads | pin 3 |
| s28 | heading; +4 threads, first cluster bulges | 4 slips gain strokes | threads →22 |
| s29 | heading; 4 slips gain strokes; pin to notch 4 | +2 threads | pin 4 |
| s30 | heading; +3 threads | second cluster bulges (+2 threads) | threads →27 |
| s31 | 4 slips gain strokes; +2 threads; pin to notch 5 | +3 threads | pin 5 |
| s32 | heading; +3 threads | 4 slips gain strokes | threads →30 |
| s33 | heading; pin to notches 6, 7, 8 — one per named moment | 6 slips gain strokes | pin 8 |
| s34 | heading; +3 threads inside the two clusters | 4 slips gain strokes | threads →33 |
| s35 | 3 slips gain a stroke; +2 threads; pin to its final notch | +3 threads | pin 9 |
| s36 | heading; 6 slips gain a 4th stroke | +3 threads | strokes peak |
| s37 | +5 cross-gutter threads; the last blank slips ink, one per named noun | 4 more slips ink; +3 threads | ink map evens |
| s38 | heading; the pin greys and stops | direction-edge ticks ink to half; +2 threads | pin spent |
| s39 | heading; **the gutter is struck; three bands rule across** | the reserve's last 3 bars are spent — 3 slips fly in, outline remains | reserve →0, slips →32 |
| s40 | heading; **every slip slides into a band** | 3 tags pin to the band heads, 2 grey out; direction edge inks solid | tags 5→2 |

Nothing that has settled ever moves again except in the two authored re-sorts
(s15, s40) and the one authored strike (s39). There is no idle motion anywhere:
the composition carries exactly one repeating tween, on a non-content background
wash, declared inline with `/* motion-allow: … */`.

## Palette

Every value comes from `tokens.yml colors:` (loaded by `check_brand.py`, which
fails any literal that is not one of them at any alpha). This is a **light**
video: the carrying object is a sheet of paper on a wall, and a paper board on a
navy ground would read as a slide rather than a worksheet.

| Role | Token | Use |
| --- | --- | --- |
| Page ground | `cultured` | the wall behind the board |
| Board ground | `paper` | the worksheet surface |
| Rules & hairlines | `border` | board border, ruled lines, slip borders |
| Structure | `blue` | gutter, threads, column heads, the tag rail |
| Type | `navy` | headings; `ink` for chips and body |
| Furniture | `muted-video` | eyebrow, worksheet label, captions |
| Focus accent | `gold` | **reserved**: the serrated (energizing) edge, the struck rules, the direction edge and the three band heads |

Gold has one job — *what the board is pointing at right now*. It never decorates.

## Type

Proxima Nova only, the vendored `woff2` 400/700/900 in `assets/fonts/`.
Hierarchy is weight, size and colour — never a second family.

| Role | Size | Weight |
| --- | --- | --- |
| Lesson title (title card) | 104px | 900 |
| Beat heading (`data-role="heading"`) | 58px | 900 |
| Struck chip | 40px | 700 |
| Column head | 30px | 900, uppercase, 0.14em |
| Tag / eyebrow / worksheet label | 26px | 700, uppercase, 0.14em |

Body floor is the tokens.yml floor (40px); the only rules below it are uppercase
tracked label furniture, which the label floor (20px) governs. Headings are
Title Case with no terminal period; every other string stays sentence case.

## Motion

- Entrances only: 0.35–0.6s, `power3.out` / `back.out(1.4)`, each pinned to the
  word timestamp that earns it. Nothing settled re-animates in place.
- The board is only ever *extended, marked, filled or re-sorted* — never rebuilt.
- One ambient breath, on the background wash alone, declared inline with
  `/* motion-allow: … */`.
