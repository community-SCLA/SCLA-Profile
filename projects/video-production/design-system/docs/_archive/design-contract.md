# SCLA Lesson System — the design contract

**What this is for.** A builder reads this before authoring `scenes.json`, to know
what exists and how to reach it: the house visual language, the twelve templates,
the icon set, the style packages, the motion recipes, and the attribute syntax you
cannot guess. It is a menu and a vocabulary.

**What it deliberately does not contain.** Any rule a checker enforces. Gates are
rejection notices — they tell you a scene failed. This file tells you what to build.
Where those overlap, the gate is the authority and the prose was only ever a copy
that could drift, so the copy is gone.

| If you need | Go to |
| --- | --- |
| The numbers — colors, type scale, min sizes, spacing, voice, program names | `../config/tokens.yml` |
| The gated rules, each naming the checker that enforces it | `.claude/rules/video-production.md` |
| Why a decision was made | `decisions/log.md` |

## Contents

[The frame](#the-frame) · [Every scene earns its seconds](#every-scene-earns-its-seconds) ·
[Authoring contract](#authoring-contract) · [Illustration over text](#illustration-over-text) ·
[Craft discipline](#craft-discipline) · [Scene templates](#scene-templates) ·
[Style packages](#style-packages) · [Living icon library](#living-icon-library) ·
[Host-root progress rail](#host-root-progress-rail) ·
[Motion rotation](#motion-rotation--the-sanctioned-arsenal) · [On-frame voice](#on-frame-voice)

## The frame

Two canvases, both SCLA:

- **Light canvas (default lesson body)** — `paper` or `cultured` base. Light needs
  texture: a faint blue grid or dot field at 6–10%, one oversized ghost oval ring,
  2px+ structural rules. Never a blank white slide. Headings `navy` 900, body `ink`
  400, labels `blue`, highlights `gold`.
- **Navy canvas (title cards, quotes, outros)** — radial `navy` → `navy-deep`
  (radial only; linear bands under H.264). Type white 900, eyebrows and rules
  `gold`, secondary labels `blue`-tinted (#bcd3e4 for de-emphasis).

**The oval-ring motif is the house decorative language.** SCLA's icon and shape mark
are concentric ovals — every scene's ambient layer echoes it: nested ellipse strokes
(blue on light ≤14%, gold/white on navy ≤18%), breathing slowly. Use
`assets/brand/logo-shape.svg` as a large ghost element where a literal mark fits.

**Foreground metadata makes it produced, not generated:** corner registration marks,
a scene-index label (`01 / TITLE`), a tracked `SCLA · <program>` caption, hairline
rules. 8–10 elements per scene; two of them decorative.

## Every scene earns its seconds

How to keep a frame alive. The thresholds that grade it are in
`.claude/rules/video-production.md`; these are the techniques that pass them.

- **Reveal on the spoken cue, not on a timer.** When the narration enumerates, each
  item enters the moment it is spoken — cue times come from the scene's word timings,
  declared as phrases (see [Authoring contract](#authoring-contract)). Even spreads
  are a fallback, never the goal.
- **Something must keep resolving.** Once the opening beat lands, the next item,
  illustration, highlight or figure arrives timed to what the narration is saying
  *right now*. Any scene beyond ~8s stages content across its whole duration. If
  nothing can happen for the next few seconds, the scene is too long — split it.
- **Furniture paints at t=0.** Canvas texture, ghost rings, corner marks, scene index
  and brandline are visible on the very first frame — they may settle from ~55%
  opacity, never from nothing, so a cut lands as a hit rather than a dissolve. Only
  *content* animates in. A bare-canvas flash at a cut is a defect.
- **Close, then exit.** One cued resolve in the final second — a rule completes, an
  accent pops, dimmed items restore — then the content layer (never the furniture)
  slides out; entrances arrive from the opposite edge so seams read velocity-matched
  rather than cut-on-frozen-frame.
- **Focus follows the voice.** When a cued item lands, settled siblings dim to ~0.6;
  the closing beat restores them. De-emphasis driven by a *new* beat is how you direct
  attention without re-animating anything.
- **Settled content never re-animates in place** — and the motion no longer exists to
  be chosen. It was deleted from the templates, not discouraged. A pixel-static hold
  has exactly one fix: re-author the scene with a new cued beat, supporting
  `lines`/`subBeats`, or more scenes.
- **Ambient motion is texture, never the cover for a hold.** Ring-breath and the navy
  heroes' depth-drift (spec in the [motion table](#motion-rotation--the-sanctioned-arsenal))
  guarantee pixel-level animacy at the QA sampler — but a scene that only passes
  because its background moves is still a dead scene.
- **Title cards are short.** A title card holds only for the opening line. If the intro
  narration continues into content, that content is its own reveal scene. When the
  intro lists things, land those words in a kinetic list scene — the title never
  squats on a list.
- **Slow meters are defects.** A 2.4s track fill or three parallel 1.6s ramps read as
  waiting. Stagger and compress them.

## Authoring contract

You declare text and phrases. The toolchain computes every number — hand-editing one
is a defect; re-run the compiler.

- **Narration is synthesized per scene.** Every scene slot carries
  `data-narration="<its verbatim span of the refined script>"`, split only at sentence
  ends, with inner double quotes escaped as `&quot;`. `synth_narration.py` verifies the
  concatenation against the refined script before any TTS, then builds `narration.wav`
  with real boundary silence and a sample-exact boundary manifest.
  `data-anchor-end` is legacy-only — never author it on a new build.
- **Cues are anchored by phrase, never by second:**
  `data-cue-anchors='{"chipCues":["phrase", …], "pointCues":[…], "stepCues":[…],
  "iconCue":"phrase", "mapCue":"phrase"}'` — one phrase per item, pulled from the
  transcript text, in spoken order.
- **A chip or step label may not contain an internal comma.** The template splits on
  commas, so a comma inflates the element count and fails the count-vs-cue check.
  Reword, or use `&amp;`.
- **`compile_timeline.py` owns** `data-start`, `data-duration`, every numeric cue
  value, `sceneDuration`, and the audio and root durations.
- **When a sentence is too long for its scene, re-punctuate — never reword.** A single
  sentence that overruns the duration cap offers no legal cut inside it, so no
  re-authoring of `scenes.json` can clear the gate. The sanctioned repair is
  word-preserving: an em dash, colon or semicolon joining two independent clauses
  becomes a period. No word added, removed, reordered or altered — the script-match
  check must still read 0.00% afterward. Apply the same repair, regardless of
  duration, when a dash splits reveal-cues across its two clauses: neither narration
  voice supports pause tags, TTS often doesn't pause on a dash, and the cued phrase
  after it reads as glued to the clause before. A plain comma list inside one clause
  is fine — leave it alone.

## Illustration over text

On-screen text is the floor. The frame should *show* the idea, and the illustration
must be a literal, indicative picture of what the narration describes at that moment.

- **Match the picture to the words.** Narration about mapping a career path → draw a
  map and trace it. "You might be thinking what sounds good" → a figure thinking,
  entering on the cue. A generic card that doesn't reflect the sentence being spoken
  is a miss. When the narration literally names the artifact ("a tool like a career
  map"), showing a generic bullseye instead is the clearest miss the frame can make.
- **Go beyond type.** Build from the house language — SVG line-art, the oval-ring
  motif, `logo-shape.svg`, simple animated diagrams (paths, comparison scales, a
  magnifier, nodes, a thinking figure). All CSS/SVG + GSAP: deterministic, seek-safe,
  no raster assets required.
- **Bespoke illustrated scenes are the expectation**, not the exception, for any
  narration describing something concrete. Templates are the structural floor, not a
  ceiling — follow this spec, don't fork them.
- **Start bespoke from a named recipe.** Check the
  [motion table](#motion-rotation--the-sanctioned-arsenal) and the registry
  (`npx hyperframes add <name>`) first. A bespoke scene used twice gets promoted to a
  `scla-*.html` template.
- **Artwork carries the video.** Type on a flat field is not an illustration, and
  neither is the same monoline icon parked in the same right-hand slot every time. The
  reference cut earns its coverage with a real bar chart, an advancing stepper, figure
  glyphs mirrored and recoloured so the repeat reads as variation, and strike-throughs
  annotating live text. Rotate the connective tissue too — an arrow between two
  statements, a comparison scale, a split frame, a trace along a path — before
  repeating the pill row a fourth time.
- **Vary the list language.** The numbered build is one form among several: chip
  clusters flashing on cue, words sliding in from different angles, grid/card cascade,
  kinetic type beats, per-item icons.
- **A steps overview only when the narration enumerates it.** If the audio introduces
  steps one at a time, give each its own scene — hero the spoken step, never preview
  the rest on a timer.

## Craft discipline

**Color.** Gold is the single voltage — CTA fills, the count-up numeral, one rule per
scene. Past ~3 golds in a frame, demote something to blue. Blue is structural (labels,
diagrams, borders); navy is ground and headline. Never introduce a hue outside
`../config/tokens.yml`.

**Logos.** `assets/brand/SCLA-logo-icon.svg` (gold icon) reads on light *and* navy.
`SCLA-Logo.svg` (full wordmark) has navy lettering — **light backgrounds only**. On
navy, build the lockup as `scla-outro.html` does: gold icon + the organization name in
white Proxima 700. Never recolor, stretch or shadow the marks. Wordmark minimum width
on 1080p: 360px.

**Type.** Proxima Nova only, self-hosted from
`assets/fonts/proxima-nova-{400,700,900}.woff2`. The `@font-face` block must live
**inside each sub-composition's `<template>`** — the composited render discards
everything outside it. Weights: 900 display / 700 subheads-labels / 400 body; no 300
or 600, the kit doesn't ship them. Uppercase + 0.14em tracking is reserved for labels,
eyebrows and chips. A marker numeral sized by its circle opts out of the size floor
with `/* text-floor-exempt: <reason> */` on the rule.

**Numerals.** The scene index lives only in the lower-right corner — small, muted,
tracked uppercase (`05 / BROADEN`). It is metadata; never large, never elsewhere. A
**large numeral is reserved for meaning**: a genuine stat the narration is making the
point of, or the step it is currently on — tracking the *spoken* step, not deck
position. A lone cardinal with a thin label reads as a slide number.

**Quotes are for humans.** The quotation-mark treatment (`scla-quote`) is only for
words attributed to a **named person**. A thesis authored by SCLA or the program is
not a quote — present it as a bold statement, no quote glyph, no attribution.

## Scene templates

Reusable sub-compositions in `../compositions/` — instantiate via
`data-composition-src` + `data-variable-values`, never fork them. A recurring new need
is a new `scla-*.html` here plus a row in this table.

| Template | Canvas | Use for |
| --- | --- | --- |
| `scla-title` | Navy | Opening line only — never parked over content |
| `scla-points` | Light | Up to 4 points, one per spoken cue (`pointCues`) |
| `scla-steps` | Light | Sequential frameworks, up to 4 steps, activated on the spoken step (`stepCues`) |
| `scla-loop` | Light | A **repeating** process the narration frames as a cycle — 4 nodes on the oval ring, gold arc drawing clockwise. Same cue contract as `scla-steps`; use only when the audio says it repeats |
| `scla-condition` | Light | One item of an enumerated set introduced one at a time: number badge + progress dots, heading, detail chips on cue, living-icon hero. Split an enumerated set into one of these per item, not a timed 5-row list |
| `scla-statement` | Navy | A program/SCLA thesis line — bold, **unattributed**. Optional supporting `lines` develop it without a second scene |
| `scla-chips` | Light | Fast spoken lists (up to 8) as pill chips flashing on cue; `reveal:"slide"` = angles variant. Also the post-title opening enumeration |
| `scla-career-map` | Light | Comparing 3 paths against criteria: candidates draw on, gold route traces to the `winner` on `mapCue` |
| `scla-morph` | Light | A **two-option** comparison where the winner re-flows on cue (FLIP): unlearn-X-do-Y, before→after, reorder-the-priority. Not a 3-way route map |
| `scla-quote` | Navy card on light | A line attributed to a **named person** only |
| `scla-stat` | Split navy/light | One number that is genuinely the point. `ring:"on"` adds a filling gauge |
| `scla-outro` | Navy | Next step + wordmark close. `next` may quote the closing narration; `cta` is a short imperative drawn from it — the two must not restate each other |

Templates guarantee the brand, the tokens and seek-safe timing. They do **not** exempt
a scene from the animacy and illustration rules: instantiate them with cue-synced
reveals, and reach for bespoke scenes whenever the narration describes something
concrete. `../index.html` is the demo reel — the living style guide; render it after
any template change.

## Style packages

Three sanctioned looks, so lessons read as one brand without being identical. Every
template takes a `theme` variable (default `summit`), stamped as `data-theme` on
`#root`; overrides key off `#root[data-theme="..."]`.

| Package | Character | Signature moves |
| --- | --- | --- |
| `summit` | House default — gold-led | Glow upper-left on navy, rings top-right, grid texture, gold rules and markers |
| `horizon` | Calm, editorial — blue-led | Glow rises from the bottom edge, dot-field texture on light, blue rules and outlined markers, gold demoted to one note per scene |
| `cadence` | Bold, high-energy — gold-forward | Gold edge bars, stronger grids, navy header panel on steps, inverted markers, wider rules |

- **One package per video**, set via `theme` on every scene slot. Never mix looks.
- Packages are **CSS-only overrides** — GSAP timelines are identical across packages,
  and a package re-weights the same tokens, never adds hues.
- **Never pick one by hand.** `render-qa/src/theme_for.py <program-slug>` is the only
  thing that computes the assignment, including the `--offset N` an orchestrator passes
  for the Nth video of a batch.
- A new package = a new `data-theme` block in **all twelve** templates plus a row here.
  Never fork a template to make a look.

## Living icon library

Brand-native SVG line-art, drawn on with GSAP `strokeDashoffset` as the narration names
the thing, gold accent popping last. **The home of the living icon is `scla-condition`**
— its hero on the right, one per condition. The governing discipline is *"icons are
novel, not on every frame"*, **not** "condition-only": a living icon may appear on a
genuinely single-focus beat of another template, sparing, on-language, one hero per
scene, drawn on the cue.

- **Optional `icon` slots** exist on `scla-statement` (hero right, white stroke on navy,
  text column narrows), `scla-steps` (header panel top-right, replaces the ghost
  numeral) and `scla-chips`. `scla-morph` takes optional per-card icons. Empty by
  default. **Never a row of icons beside bullets or cards** — the plural slot is deleted.
- **`iconCue`** fires the draw-on the moment the narration names the thing; empty keeps
  the entrance draw.
- **Hide the wrapper until the cue.** Paths use `stroke-linecap: round` and animate from
  `strokeDashoffset 100`, which is a zero-*length* stroke — but a round cap still paints
  a filled dot. Every icon host must sit at `opacity: 0` from t=0 and flip to `1` at the
  same cue that starts the draw tween. A new icon-bearing template must repeat this.

**Geometry contract.** `viewBox="0 0 96 96"`, `fill="none"`, `stroke-width="4"`, round
caps/joins. Every drawn path gets `pathLength="100"` so the draw-on is uniform
(`strokeDasharray "100 100"`, offset 100 → 0, ~0.55s `power3.out`, ~0.13s stagger).
Main stroke `navy` `#0d2437` (`#ffffff` on navy), accent `gold` `#eaab2d`. Solid dots
pop with one `back.out`. **Rings are closed full circles:**
`M 48 16 A 32 32 0 1 1 48 80 A 32 32 0 1 1 48 16 Z`.

**Canonical set** — the `d` values live in `scla-condition.html`'s `ICONS` map, the
source of truth, mirrored verbatim into `scla-statement.html` and `scla-steps.html`.
Edit `scla-condition` first, then sync the mirrors. An icon name the library lacks
draws nothing and reports nothing, so add before you use:

`compass` · `pressure` (clock) · `insight` (bulb) · `salary` (tag) · `mentorship` +
`mentorship2` (two-people, recolored so adjacent scenes read distinct) · `growth`
(line chart) · `target` · `question` · `examine` (magnifier) · `map` (folded map with a
gold pin) · `done` (check).

Keep the set small and on-language; don't open a clip-art floodgate.

## Host-root progress rail

A thin brand-gold rail advancing across the **whole runtime** — a completion indicator,
never scene motion. It lives at the host root (`index.html`), not in any
sub-composition, because it must span every scene: a faint full-width track
`#hf-rail-track` `#cccedf` with a gold fill `#hf-rail-fill` `#eaab2d`, ~4px tall, bottom
edge inside the safe margin, clear of the scene index and the outro lockup. It is driven
proportionally off the compiler-owned `#root data-duration` — no hand-typed total, no
clock.

**`scripts/batch-prepare.sh` pre-wires it into the scaffold every build clones.** Don't
hand-build it, and don't count it as scene animacy.

## Motion rotation — the sanctioned arsenal

Curated from the HyperFrames skill pack + registry so every lesson can vary its motion
without re-researching. Read the named rule/blueprint before building; never reinvent
one from scratch. **Compose 2–4 per scene, max.**

| Need | Recipe | Notes |
| --- | --- | --- |
| Word pops/glows as spoken | `hyperframes-animation` · `asr-keyword-glow` | Not in any template — use the rule directly for a bespoke scene |
| Highlight sweep / drawn circle / scribble underline | `hyperframes-animation` · `css-marker-patterns` | 5 pure-CSS emphases, timed to the word's start |
| Pill/chip cluster popping on cues | `hyperframes-animation` · `spring-pop-entrance` | Built into `scla-chips`; ≤0.5s stagger cap |
| List/tiles beyond a numbered build | blueprint · `grid-card-assemble` | Cards cascade into a grid or vertical list |
| Phrase-by-phrase kinetic type | blueprint · `kinetic-type-beats` | For beats where the words ARE the visual |
| Text-trail / weight-step type | `hyperframes-keyframes` · text trails | Weight steps across 400/700/900 only — Proxima is **not** a variable font. Staged entrance motion only |
| Route/path/diagram traces itself | `hyperframes-animation` · `svg-path-draw` | Built into `scla-career-map`; also arrows and brand-mark draws |
| One shape morphs into another | `hyperframes-keyframes` · SVG morph | Pairs must share path structure. One morph per scene max, on-cue, seek-safe |
| Element travels along a path | `hyperframes-keyframes` · GSAP MotionPath | Figure/marker moving along a drawn route |
| Count-up / stat with graphic | `hyperframes-animation` · `counting-dynamic-scale` + `stat-bars-and-fills` | Pair with `scla-stat` |
| Living icon draws on as named | brand-native line-art · `strokeDashoffset` draw-on | Home is `scla-condition`; geometry above. One hero per scene, never sprinkled |
| Two-option A→B morph (FLIP) | `hyperframes-animation` · `card-morph-anchor` / `scale-swap-transition` | Built into `scla-morph`. Seek-safe x/y/scale tweens |
| Many items gather into one cluster | `hyperframes-keyframes` · FLIP | Bespoke; anchor to the closing cue, tween-only |
| Depth-drift parallax on a navy hero | Translate-only 2.5D drift on background layers, finite `sine.inOut` yoyo, ~2.5–3.4s period, **85–120px** (CSS/GSAP, **no Three.js**) | Built into the navy templates. Amplitude must clear the QA sampler: a 16–30px move is under one gray level per 48×27 thumbnail pixel and reads as static |
| Zoom/pan focus inside a scene | `hyperframes-animation` · `coordinate-target-zoom`, `multi-phase-camera`, `depth-of-field-blur` | Camera moves beat-to-beat inside one long scene |
| Two-option comparison | blueprint · `comparison-split` | Mirrored tilt cards + pill badges |
| Concept/network diagram | `hyperframes-animation` · `avatar-cloud-network`; blueprint `constellation-hub` | Nodes ring a center, connectors draw |
| Agenda / stations overview | blueprint · `spatial-pan-stations` | One camera traverses labeled stations |
| Iris/mask reveal | `hyperframes-keyframes` · clip/mask reveal | Clip-path entrances for images or diagrams |
| Scene-to-scene transitions | `hyperframes-animation` · `transitions/catalog.md` | Brand-safe: push, blur-through/dissolve, circle iris. Skip glitch/VHS/burn |
| Flowchart / decision tree | registry block `flowchart` / `flowchart-vertical` | SVG connector diagrams |
| Chart / data visual | registry block `data-chart` | Restyle with the tokens |
| Per-word caption styling | `hyperframes-media` · `references/captions/` | Karaoke baseline, emphasis pattern-breaks |

**Doctrine:** smooth `power3`-family eases over bouncy ones by default; every scene
keeps resolving in its back half, timed to the VO; velocity-matched seam cuts; no lazy
breathing as the only motion. **Off-limits for lessons:** WebGPU liquid-glass blocks,
VFX/glitch packs, social-platform overlays — off-brand or hostile to determinism.

## On-frame voice

The narration carries sentences; the frame carries moves. On-screen text is short and
active — never "exclusive/elite" framing, never "just" as a minimizer, no passive voice
on screen. Full voice guidance: `brand/voice-and-tone.md`.
