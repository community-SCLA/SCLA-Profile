---
name: SCLA Lesson System
canvas: 1920x1080
colors:
  navy: "#0d2437" # Primary — dark canvases, headings on light, step nodes
  navy-deep: "#0a1e2f" # Radial edge of dark canvases, deepest panels
  blue: "#3393d6" # Secondary — section labels, structural rules, diagrams
  gold: "#eaab2d" # Accent — CTA fills, highlights, count-ups, rules. Ration it.
  ink: "#292f35" # Body copy on light canvases
  paper: "#ffffff" # Light canvas base
  cultured: "#f6f6f9" # Light canvas alt / section fill
  fill-subtle: "#e5eff6" # Cards and subtle panels on light
  border: "#cccedf" # Hairlines and dividers on light
  muted: "#98a4cc" # Web muted (Ceil) — fails contrast at video scale; see muted-video
  muted-video: "#5f6f96" # Video-safe muted — scene-index labels, rail captions on light
  logo-gold: "#F1B32E" # Gold used inside the shipped logo SVGs (do not restyle them)
  logo-blue: "#55A4DD" # Blue of logo-shape.svg (decorative mark)
typography:
  display: "proxima-nova" # Vendored woff2 in assets/fonts/ (from SCLA's Adobe kit ysq3rar)
  body: "proxima-nova"
  fallback: "'Proxima Nova', system-ui, sans-serif"
  weights: [400, 700, 900] # The kit ships exactly these three — no 300/600 on video
  scale:
    display: "96-120px / 900" # Lesson titles
    heading: "60-72px / 900" # Scene headings
    quote: "52-60px / 700"
    body: "32-38px / 400"
    label: "20-26px / 700, uppercase, letter-spacing 0.14em" # Eyebrows, chips, metadata
    stat: "200-260px / 900" # Count-ups
spacing:
  frame-padding: "120px" # Safe margin from canvas edge for primary content
  radius-card: "12px"
  radius-pill: "100px"
components:
  cta-label: "gold text 900 with leading → arrow, no fill/pill — video CTAs aren't clickable, so never style them as buttons"
  chip: "2px blue border, transparent fill, blue text, radius 100px"
  step-node: "120px circle, 4px navy ring, gold fill on activation, navy 900 number"
  point-marker: "74px circle, gold fill, navy 900 number"
  rule: "gold or blue, 3-4px, animates scaleX 0→1 from transform-origin left"
motion:
  entrance: "0.4-0.6s, power3.out / power4.out / back.out(1.4) — vary per element"
  stagger: "0.12-0.18s"
  ambient: "oval rings breathe scale 1→1.05 over 3-4s, finite yoyo repeats sized to the scene"
  ban: "repeat: -1 (use finite counts), linear full-screen gradients on navy (H.264 banding — use radial)"
voice:
  provider: kokoro # Pinned — see CLAUDE.md "Narration voice" for the decision + upgrade path
  voice_id: af_heart
  speed: 0.95
---

# SCLA Lesson System — frame-scale design spec

The video design system for SCLA lesson videos (audience: college students 18–24).
Frontmatter above is normative — quote hex/weights verbatim, never round. Source of
brand truth: `brand/visual-identity.md` and `brand/voice-and-tone.md`; this file
adapts those tokens to the video frame per the HyperFrames video-composition rules.

## The frame

Two canvases, both SCLA:

- **Light canvas (default lesson body)** — `paper` or `cultured` base. Light needs
  texture: a faint blue grid or dot field at 6–10%, one oversized ghost oval ring,
  2px+ structural rules. Never a blank white slide. Headings `navy` 900, body `ink`
  400, labels `blue`, highlights `gold`.
- **Navy canvas (title cards, quotes, outros)** — radial `navy` → `navy-deep`
  (radial only; linear bands under H.264). Type white 900, eyebrows and rules
  `gold`, secondary labels `blue`-tinted (#bcd3e4 works for de-emphasis).

**The oval-ring motif is the house decorative language.** SCLA's icon and shape
mark are concentric ovals — every scene's ambient layer echoes it: nested ellipse
strokes (blue on light ≤14%, gold/white on navy ≤18%), breathing slowly. Use
`assets/brand/logo-shape.svg` as a large ghost element where a literal mark fits.

**Foreground metadata makes it produced, not generated:** corner registration
marks, a scene-index label (`01 / TITLE`), a tracked `SCLA · <program>` caption,
hairline rules. 8–10 elements per scene; two of them decorative.

## Every scene earns its seconds — the animacy rules

The frame is never allowed to sit still. A scene that finishes its entrance and
then holds a static image while the narration keeps talking is a **defect**, not
a style choice. These are hard rules, checked at the QA gate.

- **No stagnant frame beyond ~2s.** Once a scene's opening beat lands, something
  must keep resolving — the next item, an illustration, a highlight, a figure —
  timed to what the narration is saying *right now*. If nothing can happen for
  the next few seconds, the scene is too long: split it into more scenes.
- **Reveal on the spoken cue, not on a timer.** When the narration enumerates
  ("the answers people reach for are X, Y, Z…", "first… second… third…"), each
  item enters the moment it is spoken. Pull cue times from the scene's word
  timings (`assets/voice/transcript.json`) and pass them to the template's cue
  variable (`pointCues` / `stepCues`, local seconds). Even spreads are a fallback,
  never the goal.
- **Title cards are short.** A title card holds only for the opening line. If the
  intro narration continues into content (listing, contrasting, framing the
  problem), that content is its own reveal scene — do not park the title over it.
- **Long beats get sub-reveals.** Any scene longer than ~8s must stage content
  across its whole duration (progressive bullets, a building diagram, a moving
  illustration), never one entrance then ambient drift. Ring-breath is texture,
  not motion.

## Illustration over text — depict what's being said

On-screen text is the floor. The frame should *show* the idea, not just label it,
and the illustration must be a literal, indicative picture of what the narration
is describing at that moment.

- **Match the picture to the words.** Narration about mapping a career path → draw
  a map/path and trace it. "You might be thinking what sounds good" → a figure
  thinking, entering on the cue. Concrete moves listed aloud → each move gets its
  own icon/illustration arriving on its cue. A generic card that doesn't reflect
  the sentence being spoken is a miss.
- **Go beyond type.** Build illustrations from the house language — SVG line-art,
  the oval-ring motif, `logo-shape.svg`, simple animated diagrams (paths,
  comparison scales, a magnifier, nodes/networks, a thinking figure). All
  CSS/SVG + GSAP: deterministic, seek-safe, no raster assets required.
- **Bespoke illustrated scenes are the expectation**, not the exception, for any
  narration that describes something concrete. Templates are the structural
  floor (see "Scene templates"), not a ceiling — follow this spec, don't fork them.

## Scene index & numerals

- **The scene index lives only in the lower-right corner** — small, muted, tracked
  uppercase (`05 / BROADEN`). Never anywhere else, never large. It is metadata.
- **A large numeral is reserved for meaning, never deck position.** Use a hero
  numeral only when (a) it is a genuine stat the narration is making the point of
  (`scla-stat`), or (b) it is the step the narration is currently on in an
  enumerated process (`scla-steps`) — and then it tracks the *spoken* step, not
  the scene's position in the lesson. A lone cardinal with a thin label reads as a
  slide number: if the number isn't the message, don't make it the hero.
- **Quotes are for humans; program lines are statements.** The quotation-mark
  treatment (`scla-quote`) is only for words attributed to a **named person**. A
  thesis authored by SCLA or the program is not a quote — present it as a bold
  statement (`scla-statement`): no quote glyph, no person attribution.

## Color discipline

Gold is the single voltage — CTA fills, the count-up numeral, one rule per scene.
If gold appears more than ~3 times in a frame, demote something to blue. Blue is
structural (labels, diagrams, borders); navy is ground and headline; never
introduce hues outside the frontmatter.

## Logos

`assets/brand/SCLA-logo-icon.svg` (gold icon) reads on light *and* navy.
`SCLA-Logo.svg` (full wordmark) has dark navy lettering — **light backgrounds
only**. On navy, build the lockup the way `scla-outro.html` does: gold icon +
the organization name typeset in white Proxima 700. Never recolor, stretch, or
shadow the marks. Wordmark min width on 1080p: 360px.

## Type rules

Proxima Nova only, self-hosted: `@font-face` rules pointing at
`assets/fonts/proxima-nova-{400,700,900}.woff2` (pulled from SCLA's Adobe kit
`ysq3rar`, the same license serving thescla.org). The `@font-face` block must
live **inside each sub-composition's `<template>`** — the composited render
discards everything outside it. Weights: 900 display / 700 subheads-labels /
400 body. No 300 or 600 — the kit doesn't ship them. Sentence case for titles and body; uppercase +
0.14em tracking is reserved for labels/eyebrows/chips.

## Scene templates

Reusable sub-compositions in `compositions/` — instantiate via
`data-composition-src` + `data-variable-values`, don't fork them:

| Template | File | Canvas | Use for |
| --- | --- | --- | --- |
| Lesson title card | `scla-title.html` | Navy | Opening line only — keep it short, never park it over content |
| Key-point build | `scla-points.html` | Light | Up to 4 points, one per spoken cue (`pointCues`) |
| Process / steps | `scla-steps.html` | Light | Sequential frameworks, up to 4 steps, activated on the spoken step (`stepCues`) |
| Statement card | `scla-statement.html` | Navy | A program/SCLA thesis line — bold, **unattributed**. Not a quote |
| Quote card | `scla-quote.html` | Navy card on light | A line attributed to a **named person** only |
| Stat highlight | `scla-stat.html` | Split navy/light | One number that is genuinely the point — not an enumeration |
| CTA outro | `scla-outro.html` | Navy | Next step + wordmark close |

Templates are the **structural floor** — they guarantee the brand, the tokens,
and seek-safe timing. They do not exempt a scene from the animacy and
illustration rules above: instantiate them with cue-synced reveals, and reach
for bespoke illustrated scenes whenever the narration describes something
concrete. `index.html` at the project root is the demo reel — all seven templates
in sequence with real Early Career Boost lesson content. Treat it as the living
style guide; render it after any template change.

## Style packages

Three sanctioned looks, so lesson videos read as one brand without being
visually identical. Every scene template takes a `theme` variable
(default `summit`); the template stamps it as `data-theme` on `#root` and the
override CSS keys off `#root[data-theme="..."]`.

| Package | Character | Signature moves |
| --- | --- | --- |
| `summit` | The house default — gold-led | Glow upper-left on navy, rings top-right, grid texture, gold rules and markers |
| `horizon` | Calm, editorial — blue-led | Glow rises from the bottom edge of navy canvases, dot-field texture on light, blue rules/edges, outlined point markers, gold demoted to one note per scene |
| `cadence` | Bold, high-energy — gold-forward | Gold edge bars (pseudo-elements), stronger grids, navy header panel on the steps scene, navy/gold inverted markers, wider rules |

Package rules:

- **One package per video**, set via `theme` on every scene slot — never mix
  looks within a lesson.
- Packages are **CSS-only overrides**; GSAP timelines are identical across
  packages (determinism and timing untouched). Palette stays exactly the
  frontmatter — a package re-weights the same tokens, never adds hues.
- Assignment: the requester picks in the Notion queue; on "No preference",
  rotate `summit → horizon → cadence` by the program's delivered illustrated
  video count (count mod 3).
- A new package = a new `data-theme` override block in **all seven** templates
  plus a row here. Never fork a template to make a look.

## Tone (from brand/voice-and-tone.md)

Warm-but-demanding, plain language, communal ("we", "your people"), always a
concrete next move. On-screen text is short and active — the narration carries
sentences; the frame carries moves. Never "exclusive/elite" framing, never
"just" as a minimizer, no passive voice on screen.
