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
- **Kinetic word emphasis on cue.** When a held line's key words are spoken
  ("…more *thoughtful*, less *reactive*, and *grounded*…"), each word pops on its
  timestamp — scale ~1.14 + gold flash, then settles (`scla-statement` →
  `emphasis`/`emphasisCues`). Any statement scene longer than ~6s must carry
  emphasis cues; a bare held sentence is a stagnation defect.
- **Furniture paints at t=0.** The scene's frame furniture — canvas texture,
  ghost rings, corner marks, scene index, brandline — is visible on the very
  first frame of every scene (entrances may settle it from ~50% opacity to
  full, never from nothing). Only *content* animates in. A bare-canvas flash
  at a cut is a defect; renders before 2026-07-10 shipped white flashes at
  scene entrances because furniture entered at 1.2–1.6s.
- **Late-phase resolve.** Every template carries a quiet second wave sized to
  its `sceneDuration` variable (compiler-maintained): content re-marks itself
  — chip/point/node cascades, statement drift, route-node pulses — in the back
  half of long holds, so no scene can produce a pixel-static stretch ≥5s while
  narration speaks. This is layered *on top of* cue reveals, never instead of
  them; `check_presence.py` trips deterministically at 5s (warns at 3s).

## Scene boundaries, padding & endings — the pacing rules

**Timing numbers are compiled, never hand-typed.** The author declares anchors;
`projects/video-production/render-qa/compile_timeline.py` computes every number
from `assets/voice/transcript.json` (the authoring contract, normative):

- Every scene slot carries `data-anchor-end="<the scene's last spoken phrase>"`
  — verbatim words from the transcript (punctuation/case ignored).
- Every cue variable is anchored by phrases, not seconds:
  `data-cue-anchors='{"chipCues":["phrase", …], "pointCues":[…],
  "stepCues":[…], "emphasisCues":[…], "mapCue":"phrase"}'` — one phrase per
  item, pulled from the transcript text, in spoken order.
- The compiler owns `data-start`/`data-duration`, all numeric cue values,
  `sceneDuration`, the `<audio>` duration, and the root duration — and it
  inserts the boundary silence itself (narration has only 30–60ms of natural
  sentence gap; the compiler pads to 0.6s air + 0.15s lead, 0.9s after a
  question, measured 2026-07-10). Hand-editing any of these numbers is a
  defect; re-run the compiler instead. `render-qa/preflight.py` re-derives
  everything and fails the build on any drift.

Cuts are graded at QA against `assets/voice/transcript.json`, not by feel:

- **Boundaries land on sentence ends.** Never cut mid-word or mid-sentence; the
  sentence that opens a thought belongs to the scene that illustrates it. If a
  sentence straddles a planned cut, move the boundary — don't split the sentence.
- **≥0.5s of air after the last word.** A scene may not cut until at least
  0.5s after its final spoken word's `end` time. Cutting at or before the word's
  end (the old builds cut up to 0.36s *early*, mid-word) is a defect.
- **Questions keep their inflection.** When a scene ends on a question, the cut
  waits for the rise to finish — pad after the question mark, and prefer scripting
  spoken lists to resolve as a question ("…mentorship, or growth?") rather than
  trail off.
- **The video never ends on an empty frame.** The final scene must (a) start no
  later than the last sentence, (b) extend past the narration's true end
  (`ffprobe` the wav — don't trust the planned total), and (c) hold its full
  text content ≥1s after the last word. Root duration = final scene end,
  exactly. Audio outliving the last clip, or a bare-canvas tail, fails QA.
- **The opening enumeration gets its own scene.** When the intro narration lists
  things ("the right job, the right major, the right city…"), cut off the title
  card at the setup clause and land those words in a kinetic list scene
  (`scla-chips`, reveal on each phrase's cue). The title never squats on a list.

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
- **Start bespoke from a named recipe, never from scratch.** Before authoring a
  bespoke scene, check the "Motion rotation" table below and the registry
  (`npx hyperframes add <name>`) — the chip-cluster and route-trace scenes that
  slowed the first builds were both documented recipes (`spring-pop-entrance`,
  `svg-path-draw`). A bespoke scene used (or likely to be used) twice gets
  promoted to a `scla-*.html` template here.
- **Vary the list language.** `scla-points`' numbered build is one form among
  several, not the default. Rotate across: chip/word clusters flashing on cue
  (`scla-chips` pop), words sliding in from different angles (`scla-chips`
  slide), grid/card cascade, kinetic type beats, per-item icons. Two consecutive
  enumeration scenes must not reuse the same reveal form when another fits.
- **A steps overview only when the narration enumerates it.** Showing all N steps
  of a process (`scla-steps`) is allowed only at a moment the narration actually
  lists them. If the audio introduces steps one at a time ("First, define…"),
  give each step its own scene — hero the spoken step, never preview the rest
  on a timer.

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
| Statement card | `scla-statement.html` | Navy | A program/SCLA thesis line — bold, **unattributed**. Not a quote. Key words pop on cue (`emphasis`/`emphasisCues`) — required on statements >~6s |
| Chip / word cluster | `scla-chips.html` | Light | Fast spoken lists (up to 8 items) as pill chips flashing on cue (`chips`/`chipCues`); `reveal:"slide"` = angles variant. Also the post-title opening-enumeration scene |
| Career / route map | `scla-career-map.html` | Light | Comparing paths/options: 3 candidate paths draw on, gold route traces to the winner on `mapCue` (`winner` picks it) |
| Quote card | `scla-quote.html` | Navy card on light | A line attributed to a **named person** only |
| Stat highlight | `scla-stat.html` | Split navy/light | One number that is genuinely the point — not an enumeration |
| CTA outro | `scla-outro.html` | Navy | Next step + wordmark close — must hold ≥1s past the last spoken word |

Templates are the **structural floor** — they guarantee the brand, the tokens,
and seek-safe timing. They do not exempt a scene from the animacy and
illustration rules above: instantiate them with cue-synced reveals, and reach
for bespoke illustrated scenes whenever the narration describes something
concrete. `index.html` at the project root is the demo reel — all nine templates
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
- A new package = a new `data-theme` override block in **all nine** templates
  plus a row here. Never fork a template to make a look.

## Motion rotation — the sanctioned arsenal

Curated from the full HyperFrames skill pack + registry (surveyed 2026-07-09) so
every lesson can vary its motion without re-researching. Each entry names the
recipe to start from — read the rule/blueprint file (in `.agents/skills/`) before
building; never reinvent one of these from scratch. Compose 2–4 per scene, max.

| Need | Recipe (skill · rule/blueprint) | Notes |
| --- | --- | --- |
| Word pops/glows as it's spoken | `hyperframes-animation` · `asr-keyword-glow` (karaoke variant) | Built into `scla-statement` `emphasisCues`; use rule directly for bespoke |
| Highlight sweep / hand-drawn circle / scribble underline on a word | `hyperframes-animation` · `css-marker-patterns` | 5 pure-CSS marker emphases, timed to the word's start |
| Pill/chip cluster popping on cues | `hyperframes-animation` · `spring-pop-entrance` (staggered pills) | Built into `scla-chips`; ≤0.5s stagger cap |
| List/tiles beyond a numbered build | `hyperframes-animation` blueprint · `grid-card-assemble` | Cards/pills/list-lines cascade into a grid or vertical list |
| Phrase-by-phrase kinetic type | `hyperframes-animation` blueprint · `kinetic-type-beats`; also `techniques.md` §4 per-word slide-in | For beats where the words ARE the visual |
| Route/path/diagram traces itself | `hyperframes-animation` · `svg-path-draw` (stagger multi-path ~70–80%) | Built into `scla-career-map`; also arrows, brand-mark draws |
| Element travels along a path | `hyperframes-keyframes` · Path travel (GSAP MotionPath) | Figure/marker moving along a drawn route |
| Count-up / stat with graphic | `hyperframes-animation` · `counting-dynamic-scale` + `stat-bars-and-fills` | Pair with `scla-stat` |
| Zoom/pan focus inside a scene | `hyperframes-animation` · `coordinate-target-zoom`, `multi-phase-camera`, `depth-of-field-blur` | Camera moves beat-to-beat inside one long scene |
| Two-option comparison | `hyperframes-animation` blueprint · `comparison-split` | Mirrored tilt cards + pill badges |
| Concept/network diagram | `hyperframes-animation` · `avatar-cloud-network`; blueprint `constellation-hub` | Nodes ring a center, connectors draw |
| Agenda / stations overview | `hyperframes-animation` blueprint · `spatial-pan-stations` | One camera traverses labeled stations |
| Iris/mask reveal | `hyperframes-keyframes` · Clip/mask reveal | Clip-path reveals for image/diagram entrances |
| Element hand-off between beats | `hyperframes-animation` · `scale-swap-transition`, `card-morph-anchor` | Seek-safe within-scene "cuts" |
| Scene-to-scene transitions | `hyperframes-animation` · `transitions/catalog.md` | Brand-safe picks: push, blur-through/dissolve, circle iris. Skip glitch/VHS/burn |
| Flowchart / decision tree | registry block `flowchart` / `flowchart-vertical` (`npx hyperframes add`) | SVG connector diagrams |
| Chart / data visual | registry block `data-chart` | Restyle with frontmatter tokens |
| Per-word caption styling reference | `hyperframes-media` · `references/captions/motion.md` + `authoring.md` | Karaoke baseline, emphasis pattern-breaks |

**Doctrine (from `faceless-explainer` → `motion-language.md`, binding here):** smooth
`power3`-family eases over bouncy ones by default; every scene keeps resolving in
its back half, timed to the VO; velocity-matched seam cuts; no lazy breathing as
the only motion. **Off-limits for lessons:** WebGPU liquid-glass blocks, VFX/glitch
packs, social-platform overlays (`instagram-follow` etc.) — off-brand or
non-deterministic-friendly.

## Tone (from brand/voice-and-tone.md)

Warm-but-demanding, plain language, communal ("we", "your people"), always a
concrete next move. On-screen text is short and active — the narration carries
sentences; the frame carries moves. Never "exclusive/elite" framing, never
"just" as a minimizer, no passive voice on screen.
