# design.md — brand truth for this composition

Design source of record for `build-direction-before-you-build-a-plan_early-career-boost`
(freeform / agent-native lane, `.claude/skills/render-lessons/SKILL.md` →
"Freeform build sequence"). Every normative number comes from the workspace
copy of `tokens.yml` — the gates read that copy. No SCLA scene template
participates in this build: the HTML is the authored artifact.

## Concept angle

> A title is a borrowed label, so direction is never announced — it is
> **assembled from marks the viewer already owns**: one field of small marks
> that arrives once, pinned to the experiences the script names, and is
> thereafter only ever re-sorted — scattered experience into repeated clues,
> clues into three named patterns, patterns into the four ingredients of a
> dream job.

The field is the carrying object. It arrives in Act 2 and from that moment it
is never rebuilt, never re-entered and never left; every later act moves the
*same* 48 marks into a new grouping while the text band above names what the
grouping means. Nothing is ever added to it from outside the frame, which is
the argument the lesson is actually making: the evidence for your direction
already exists, and the work is sorting it.

Grouping states, in order — each one a beat, each one derived from the script:

| Act | Beats | The field is… | The text band says |
| --- | --- | --- | --- |
| 1 — Borrowed labels | s01–s03 | absent; five job titles occupy the frame, then empty out | a title is only a label |
| 2 — The field arrives | s04–s08 | 12×4 grid arriving in six waves, one per experience the script lists; 16 marks go gold on the four questions | who you are before the title |
| 3 — Repeated clues | s09–s15 | the gold marks re-sort into four rows, one per way of contributing | how you naturally contribute |
| 4 — Three patterns | s16–s19 | the grid separates into three blocks, lighting in turn | strengths · values · energy |
| 5 — Ingredients | s20–s26 | four labelled blocks, then combined into one | dream jobs are combinations |

## Palette (dark — the decision-making register this audience is in)

Every colour literal in the CSS is a `tokens.yml` `colors:` value at some
alpha; nothing else is authored (`check_brand.py` grades exactly this).

| Role | Token | Hex | Use |
| --- | --- | --- | --- |
| Page ground | `navy-deep` | `#0a1e2f` | full-bleed background **child**, never the root itself |
| Ground lift | `navy` | `#0d2437` | radial lift behind the field, chip fills |
| Foreground | `paper` | `#ffffff` | display type, headings |
| Body / secondary | `paper` @ .78 | `rgba(255,255,255,.78)` | body copy on navy (≈8:1) |
| Structure / label | `blue` | `#3393d6` | eyebrow, rules, unlit marks, chip strokes |
| Focus accent | `gold` | `#eaab2d` | **one job only**: the marks and words the lesson is pointing at *right now* |

Gold never decorates. If gold is on the frame, it is the current claim.

## Type

Proxima Nova only, vendored `woff2` (400/700/900) from
`design-system/assets/fonts/`, `@font-face`d **inside each sub-composition's
`<template>`** — the composited render discards everything outside it. Every
`font-family` stack leads with `'Proxima Nova'`.

| Role | Size | Weight | Tracking |
| --- | --- | --- | --- |
| Display (title card) | 96px | 900 | -0.02em |
| Heading | 68px | 900 | -0.015em |
| Accent line | 54px | 700 | -0.01em |
| Body | 44–46px | 400 | 0 |
| Chip | 42px | 400 | 0 |
| Eyebrow (label class) | 26px | 700 | 0.16em, uppercase |

The 40px body floor (`tokens.yml typography.min-size.body`) holds: nothing a
viewer reads as a sentence sits below it. The eyebrow is the only sub-40px
rule and is label class by construction (uppercase **and** letter-spaced).

Hierarchy is carried by weight, size and colour — house style's serif/sans
pairing is deliberately overridden, because brand truth is Proxima Nova on
every SCLA surface and a serif here would be off-brand.

## Frame

1920×1080. The bands are fixed for the whole runtime, so the field never has to
move to make room for copy:

- **Chrome** — program eyebrow at x 120, inside the declared chrome rectangle
  (`tokens.yml chrome-regions: 100,50,700,110`). Nothing else sits above y 150.
- **Text band** — y 150 → 600. Heading at the top; body / accent lines under it.
- **Field band** — x 300 → 1620, y 620 → 936. 12 columns × 4 rows, 120px column
  pitch, 105px row pitch, 14px marks.
- Keep-outs honoured everywhere: 72px safe area, 120px frame padding, content
  ends above y 960 (`check_ink` grades real pixels, not a CSS model).

## Motion

- Arrivals are **binary + a whip from below** — `autoAlpha` 0→1 with y 26→0,
  0.45–0.6s `power3.out`. Never a fade used as an arrival.
- Reveals are pinned to real word timestamps out of `audio_meta.json`; no
  arrival is placed by eye.
- Exits are 0.28s `power2.in` and **complete before** the replacing element
  begins, so two text blocks never share pixels at any sampled instant.
- Settled content never re-animates in place. The only repeating tween in the
  build is the background radial lift's breath, declared inline where it lives.
- The field re-sorts by moving marks (`x`/`y`), never by rebuilding them: a
  mark that arrived in Act 2 is the same DOM node in Act 5.
- Deterministic only: finite repeat counts, no clocks, no randomness; mark
  positions are a pure index → (column, row) function.

## Copy discipline

Every on-frame string is lifted or condensed from the approved refined script —
no claim reaches the frame that the narration does not make. Headings are Title
Case with no terminal period and carry `data-role="heading"` so the gate can
identify them; body copy stays sentence case. On-frame copy lives in markup,
never in JS string literals.

### The two places the beat manifest departs from the refined script

Both are recorded here because `script_match` passes them at 0.26% — inside its
noise floor — and a gate that passes silently must not be the only record.

1. **`AI` → `A.I` (s23), a TTS normalisation.** It never reaches the frame; the
   on-frame line reads "Reflection and AI support". The house form `A.I.` made
   Oxana read its trailing period as a sentence end: the first take put a
   **2.2s hole** mid-line and ran 11.55s against 7.73s for the period-less
   form. Both variants were synthesised and measured before committing — bare
   `AI` is read as one syllable, so `A.I` is the only form that is both
   correctly pronounced and gap-free.

2. **s07: "…Where did you feel useful? Where did you feel proud of the
   outcome?" → "…Where did you feel useful, or did you feel proud of the
   outcome?"** — one word, `Where` → `or`. **This is an owner-rule fix the
   approved script needs and does not have.** The script's four-question run
   ends with no "and/or before the final item", so `check_copy` rule (a) fails
   the build on the beat manifest. Doctrine says the conjunction is added by
   *joining the list into one sentence*, never bolted onto a fragment — but
   every joining edit deletes four consecutive script words, which trips
   `script_match`'s `RUN_FAIL = 4`. This one-word join is the only edit that
   clears both gates. **Owner action: back-port it to
   `lesson-scripts/early-career-boost/refined/build-direction-before-you-build-a-plan_early-career-boost.txt`**,
   which is where the conjunction rule is meant to be fixed.
