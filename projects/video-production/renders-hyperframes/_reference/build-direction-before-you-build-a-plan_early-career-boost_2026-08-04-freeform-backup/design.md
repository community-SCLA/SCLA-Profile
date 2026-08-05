# design.md — brand truth for this composition

Design source of record for `build-direction-before-you-build-a-plan_early-career-boost`.
Brand values come from `tokens.yml` (copied into this workspace, graded against
the spec by preflight's `composition_freshness`) and `brand/visual-identity.md`.
Freeform lane: no design-system template participates in this build — the HTML
is the authored artifact.

## Concept angle

> The evidence is already on the board. A title is one word someone else hands
> you; **direction is a pattern you read off moments you have already lived.**
> The video lays down one board of those moments and then re-reads it, rather
> than moving to a new idea each beat.

Titles enter as flat chips and grey out — labels, not evidence. The six moments
then land as cards and are read twice without being rebuilt: first the four
questions are asked of them, then each takes a gold mark as the narration turns
them into evidence. Only once they have been read does the board give way to
what it revealed — the four contributions, then the three things the module
identifies, then the ingredients of a dream job.

**Stated honestly:** the board is not literally on screen for the whole runtime.
It is laid down, read twice in place, and then hands off. What is constant is
the *move* — every act shows the same evidence being re-read, never a fresh
unrelated graphic.

This is the anti-decoration rule for the piece: if an element cannot be
justified as "another way of reading the same board," it does not exist.

## Palette (light — reflective / open register)

Deliberately the light side of the palette, opposite the dark decision-making
register used by the mid-career reference build. This lesson is about noticing
rather than choosing, and the audience is at the start of a career.

| Role              | Token          | Hex                     | Use                                                     |
| ----------------- | -------------- | ----------------------- | ------------------------------------------------------- |
| Page ground       | `paper`        | `#ffffff`               | Full-bleed background child (never on the root itself)   |
| Ground lift       | `cultured`     | `#f6f6f9`               | Radial lift behind the board, alternate panels           |
| Card fill         | `fill-subtle`  | `#e5eff6`               | Moment cards, ingredient panels                          |
| Hairline          | `border`       | `#cccedf`               | Grid, dividers, inactive card strokes                    |
| Display type      | `navy`         | `#0d2437`               | Headings, lesson title, card names                       |
| Body copy         | `ink`          | `#292f35`               | Sentences the viewer reads                               |
| Structure / label | `blue`         | `#3393d6`               | Eyebrows, axis labels, rules, section furniture          |
| Focus accent      | `gold`         | `#eaab2d`               | **Reserved**: the clue that repeats, and only that       |
| Video-safe muted  | `muted-video`  | `#5f6f96`               | Scene index, brandline, rail captions                    |

`muted` (`#98a4cc`) is the web value and fails contrast at video scale — it is
not used. Gold never decorates: on this board it means *this is the thing the
lesson is pointing at right now.*

## Type

Proxima Nova only, self-hosted `woff2` 400 / 700 / 900 from `assets/fonts/`.
Hierarchy by weight, size and colour — never by family.

| Role                | Size  | Weight | Tracking          |
| ------------------- | ----- | ------ | ----------------- |
| Lesson title        | 104px | 900    | -0.02em           |
| Section heading     | 72px  | 900    | -0.02em           |
| Card / item name    | 52px  | 900    | -0.01em           |
| Body / detail       | 42px  | 400    | 0                 |
| Eyebrow / axis      | 26px  | 700    | 0.14em, uppercase |

Body floor is **40px** (`tokens.yml typography.min-size.body`) — body here sits
at 42px, above the floor rather than at it. Headings are Title Case with no
terminal period, and every heading carries `data-role="heading"`.

## Frame

- 1920×1080. Frame padding 120px; **hard safe-area keep-out 72px** on every edge.
- Footer band is reserved: no content element below **y = 960**
  (`content-bottom`). Brandline and scene index live in that band.
- Focal element: the board, optically centred at 960×520 — held slightly high so
  the lower band can carry the sentence being spoken.
- Edge anchors: program eyebrow ("Early Career Boost") top-left; lesson title on
  the title card in markup, never a JS string.
- Background: paper ground + `cultured` radial lift behind the board + a 120px
  hairline grid at low alpha. One ambient breath on the lift layer only,
  declared inline with `/* motion-allow: … */` and a finite repeat count.

## Motion

- Entrances 0.4–0.7s, `power3.out`; the whole entrance settles by 1.2s.
- Exits 0.3s, `power2.in`; furniture stays.
- **Settled content never re-animates in place.** Cards move, re-colour and
  re-label — they are never re-entered or re-marked where they sit.
- `repeat: -1` is banned; ambient uses a finite count sized to the video.
- Every deliberate ambient exception is declared at its **call site**, not in a
  helper body.

## On-frame contract the gates read

- On-frame copy lives in **markup, never JS strings**.
- Headings are `<h1>`–`<h3>` or carry `data-role="heading"`.
- Lists are real `<ul>`/`<ol>`, or declare `data-role="list"`; a comparison
  declares `data-role="compare"` — a list drawn as bare divs is graded on
  nothing, and a one-item list is a defect.
- Colours are `tokens.yml colors:` values at any alpha; every `font-family`
  leads with the brand face.
- The final clip's wav carries `FINAL_HOLD` = **1.8s** of real trailing silence.
