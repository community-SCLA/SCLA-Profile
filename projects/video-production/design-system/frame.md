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
  fallback: "'Proxima Nova', 'Avenir Next', Avenir, 'Segoe UI', system-ui, sans-serif"
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
  cta-pill: "background gold, text #ffffff 700, padding 26px 64px, radius 100px"
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
| Lesson title card | `scla-title.html` | Navy | Opening any lesson |
| Key-point build | `scla-points.html` | Light | Up to 4 points, staggered |
| Process / steps | `scla-steps.html` | Light | Sequential frameworks, up to 4 steps |
| Quote card | `scla-quote.html` | Navy card on light | The lesson's central line |
| Stat highlight | `scla-stat.html` | Split navy/light | One number that matters |
| CTA outro | `scla-outro.html` | Navy | Next step + wordmark close |

`index.html` at the project root is the demo reel — all six templates in
sequence with real Early Career Boost lesson content. Treat it as the living
style guide; render it after any template change.

## Tone (from brand/voice-and-tone.md)

Warm-but-demanding, plain language, communal ("we", "your people"), always a
concrete next move. On-screen text is short and active — the narration carries
sentences; the frame carries moves. Never "exclusive/elite" framing, never
"just" as a minimizer, no passive voice on screen.
