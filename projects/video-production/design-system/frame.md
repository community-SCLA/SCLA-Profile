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
  # HeyGen swap LANDED 2026-07-22 (see decisions/log.md): synth_narration.py
  #   defaults to this HeyGen starfish voice and provider — it returns native
  #   word timestamps with the synthesis (assets/voice/narration.words.json),
  #   so the separate Whisper transcribe pass no longer runs on new builds.
  #   Cost: ~1 HeyGen credit per ~10s line; quota 15000. Voice changed
  #   2026-07-22 to Oxana (owner pick); it replaces Ann — Professional, which
  #   is retired from this pipeline. Approved alternate: Seema — Professional
  #   166aa8d7acd1495a839d34024ccb1505. Both support locale en-US and neither
  #   supports pause tags — pace with sentence structure, not <break>.
  provider: heygen           # ACTIVE — synth_narration.py's default
  voice_id: 442360a3e0894fbd85024ff64cc2b928  # Oxana, en-US (chosen 2026-07-22)
  speed: 0.95
  fallback: # manual escape hatch — `synth_narration.py <ws> --provider kokoro`
    provider: kokoro # Pinned engine — NOT a CLI flag (hyperframes ≥0.7.56 removed --provider; kokoro is the built-in). Needs `npx hyperframes transcribe` after (no native word timestamps)
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
- **No per-word emphasis, and no in-place "keep-alive" motion of settled
  content.** `scla-statement` does not support timed per-word pop/underline
  (`emphasis`/`emphasisCues` — removed 2026-07-11). Settled text, chips, rows,
  nodes, numbers, and CTAs never wobble, drift, ripple, or re-mark in place —
  owner decision 2026-07-14, **reaffirmed 2026-07-15** after an unauthorized
  restoration shipped in rendered cuts (the owner saw "text jumping around"
  and vetoed it on sight). A scene that would hold pixel-static past ~5s is an
  AUTHORING defect: split it, add cued items / supporting `lines` / `subBeats`,
  or shorten the narration span — never re-animate what has settled.
- **Furniture paints at t=0.** The scene's frame furniture — canvas texture,
  ghost rings, corner marks, scene index, brandline — is visible on the very
  first frame of every scene (entrances may settle it from ~50% opacity to
  full, never from nothing). Only *content* animates in. A bare-canvas flash
  at a cut is a defect; renders before 2026-07-10 shipped white flashes at
  scene entrances because furniture entered at 1.2–1.6s.
- **Cover long holds with staged content, never in-place re-animation.** No
  scene may produce a pixel-static stretch ≥5s while narration speaks —
  `check_presence.py` trips deterministically at 5s (warns at 3s). The cover is
  always a *new* beat: the next cued item, an illustration or figure that
  enters (and may leave) on what is being said, a `subBeats` live line, or
  splitting an over-long scene into more scenes. The background depth-drift
  cycles (below) add pixel-level texture on templates with a decorative layer,
  but they are NOT the cover and never license a long hold: if a scene only
  passes the gate because its background moves, it is still a dead scene —
  re-author it. (A 2026-07-15 attempt to satisfy the gate with text
  ripples/re-marks instead of re-authoring was vetoed by the owner.)
- **Depth-drift runs in finite yoyo cycles (2026-07-14; re-tuned 2026-07-15).**
  The navy hero templates (`scla-title`, `scla-statement`, `scla-outro`,
  `scla-quote`, `scla-stat`) — and the light templates' ghost layers — drift
  their *background* layers at different rates: translate-only 2.5D parallax
  (CSS/GSAP, never Three.js), 16–30px amplitude on a ~2.5–3.4s `sine.inOut`
  yoyo period, repeated (finitely) to cover the whole scene. The original
  single whole-scene glide moved ~1px/s and was pixel-identical between QA
  samples — that regression froze six scenes on the first promoted render.
  Depth-drift is still decorative texture: it guarantees pixel-level animacy at
  the sampler, but a real narrative hold is covered by a new cued beat (the
  statement's supporting `lines`, the next item, or splitting the scene).
- **The progress rail is a completion indicator, not animacy.** The host-root gold
  rail (below) advances proportionally across the whole runtime, but at video scale
  it moves far too little per second to register as motion — `check_presence`
  ignores it. It never counts toward the ≥5s rule; scene animacy always comes from
  the sub-compositions.

## Scene boundaries, padding & endings — the pacing rules

**Timing numbers are compiled, never hand-typed.** The author declares text;
the toolchain computes every number (authoring contract, normative):

- **Narration is synthesized per scene** (`render-qa/synth_narration.py`,
  2026-07-14 — see `decisions/log.md`): every scene slot carries
  `data-narration="<its verbatim span of the refined script>"` (split only at
  sentence ends; HTML-escape inner double quotes as `&quot;`). The tool
  verifies the concatenation against the refined script before any TTS, then
  builds `narration.wav` from per-scene clips with REAL boundary silence
  (0.3s air + 0.15s lead, 0.45s air after a question) and writes the
  sample-exact boundary manifest `assets/voice/scene-times.json`.
  `data-anchor-end` is legacy-only (pre-manifest workspaces): never author it
  on a new build — the old single-take + inserted-silence flow spliced words
  mid-decay and is retired.
- **Word timings come from HeyGen natively (2026-07-22)** — the default
  `--provider heygen` path writes `assets/voice/narration.words.json`
  (already shifted to whole-file absolute time), so `npx hyperframes
  transcribe` no longer runs on new builds; `compile_timeline.py`,
  `preflight.py`, and `check_boundaries.py` all detect and prefer this file
  automatically. `--provider kokoro` (manual fallback) still has no native
  timestamps and needs the transcribe step, same as before.
- Every cue variable is anchored by phrases, not seconds:
  `data-cue-anchors='{"chipCues":["phrase", …], "pointCues":[…],
  "stepCues":[…], "mapCue":"phrase"}'` — one phrase per
  item, pulled from the Whisper transcript text, in spoken order.
- A reveal-cue **chip/step label may not contain an internal comma** — the
  template splits comma-separated values into separate elements, so a comma
  inflates the element count and fails preflight's count-vs-cue check. Reword
  (or use `&amp;`) instead of a comma inside one chip/step.
- `compile_timeline.py` owns `data-start`/`data-duration`, all numeric cue
  values, `sceneDuration`, the `<audio>` duration, and the root duration —
  boundaries come from the synthesis manifest; cue times from
  `assets/voice/transcript.json`. Hand-editing any of these numbers is a
  defect; re-run the compiler instead. `render-qa/preflight.py` re-derives
  everything and fails the build on any drift.

Cuts are graded at QA against `assets/voice/transcript.json`, not by feel:

- **Boundaries land on sentence ends.** Never cut mid-word or mid-sentence; the
  sentence that opens a thought belongs to the scene that illustrates it. If a
  sentence straddles a planned cut, move the boundary — don't split the sentence.
- **≥0.2s of air after the last word.** A scene may not cut until at least
  0.2s after its final spoken word's `end` time. Cutting at or before the word's
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
| Cycle / loop | `scla-loop.html` | Light | A **repeating** process the narration frames as a loop — up to 4 numbered nodes ride the oval-ring motif (12/3/6/9 o'clock), the gold arc draws clockwise, an arrowhead closes step 4 → 1. Same variable/cue contract as `scla-steps` (`stepCues`); reach for it over `scla-steps` only when the audio actually says the process repeats/cycles |
| Condition / principle | `scla-condition.html` | Light | One item of an enumerated set the narration introduces one at a time (condition/principle/pillar N of M): number badge + progress dots, heading, detail chips on cue (`chipCues`), and a **living icon** hero on the right (`icon`). Split an enumerated set into one of these per item, not a timed 5-row list |
| Statement card | `scla-statement.html` | Navy | A program/SCLA thesis line — bold, **unattributed**. Not a quote. No per-word emphasis and no in-place keep-alive (reaffirmed 2026-07-15) — keep statement scenes short or split them. Optional supporting `lines` (gold-bullet column, revealed on `pointCues`) develop the thesis without a second scene (see the animacy rules) |
| Chip / word cluster | `scla-chips.html` | Light | Fast spoken lists (up to 8 items) as pill chips flashing on cue (`chips`/`chipCues`); `reveal:"slide"` = angles variant. Also the post-title opening-enumeration scene |
| Career / route map | `scla-career-map.html` | Light | Comparing 3 paths/options against criteria: 3 candidate paths draw on, gold route traces to the winner on `mapCue` (`winner` picks it) |
| Morph hand-off | `scla-morph.html` | Light | A **two-option** comparison where the winner re-flows on cue (FLIP-style): unlearn-X-do-Y, before→after, wrong-vs-right, reorder-the-priority. Cards A/B enter, then the `winner` rises + turns gold (may relabel via `winnerAfter`); `actions`/`pointCues` sequence the beats. Not a 3-way route map |
| Quote card | `scla-quote.html` | Navy card on light | A line attributed to a **named person** only |
| Stat highlight | `scla-stat.html` | Split navy/light | One number that is genuinely the point — not an enumeration. Optional `ring:"on"` pairs the count-up with a filling closed-circle gauge |
| CTA outro | `scla-outro.html` | Navy | Next step + wordmark close — must hold ≥1s past the last spoken word |

Templates are the **structural floor** — they guarantee the brand, the tokens,
and seek-safe timing. They do not exempt a scene from the animacy and
illustration rules above: instantiate them with cue-synced reveals, and reach
for bespoke illustrated scenes whenever the narration describes something
concrete. `index.html` at the project root is the demo reel — the templates
in sequence with real Early Career Boost lesson content. Treat it as the living
style guide; render it after any template change.

## Living icon library

Brand-native SVG line-art icons, drawn on with GSAP `strokeDashoffset` as the
narration names the thing, gold accent popping last. **The home of the living
icon is `scla-condition`** — its hero illustration on the right, one per
condition/principle. The governing discipline (owner decision 2026-07-14,
**scope widened 2026-07-15**) is *"icons are novel, not on every frame"*, **not**
"condition-only": a living icon may also appear on a genuinely single-focus beat
of another template, as long as it stays sparing, on-language, one hero per
scene, and drawn on the cue.

- `scla-statement` and `scla-steps` now carry an **optional `icon` variable**
  (empty by default → no icon, scene unchanged). On `scla-statement` the icon is
  a hero on the right (white main stroke on the navy canvas) and the text column
  narrows to clear it; on `scla-steps` it sits in the header panel's top-right and
  **replaces the ghost numeral**. Added 2026-07-15 for the career-purpose lesson
  (question / structure / write-it beats).
- An enumerated set the narration walks one at a time is still best split into one
  `scla-condition` card per item (each with its own icon), **not** given icons in a
  single multi-row scene — see the `scla-condition` row and "Split an enumerated
  set into one of these per item".
- Still forbidden: an icon on *every* frame, or a decorative icon that doesn't
  illustrate what the beat is about. Novelty is the point.

- **Geometry contract.** `viewBox="0 0 96 96"`, `fill="none"`, `stroke-width="4"`,
  round caps/joins. Every drawn path/stroke gets `pathLength="100"` so the draw-on
  is uniform (`strokeDasharray "100 100"`, `strokeDashoffset 100 → 0`, ~0.55s
  `power3.out`, ~0.13s stagger). Main stroke `navy` (`#0d2437`; use `#ffffff` on a
  navy canvas), accent stroke/fill `gold` (`#eaab2d`). Solid dots pop with one
  `back.out`. **Rings are closed full circles** — the old 5/8 open-arc "signature"
  was dropped 2026-07-14.
- **Canonical set** (the `d` values live in `scla-condition.html`'s `ICONS` map —
  it is the source of truth; the same map is mirrored verbatim into
  `scla-statement.html` and `scla-steps.html` for their optional `icon` slot, and
  into this doc. Edit `scla-condition` first, then keep the two mirrors in sync):
  `compass`, `pressure` (clock), `insight` (bulb),
  `salary` (tag), `mentorship` + `mentorship2` (two-people, variant recolored so
  adjacent scenes read distinct), `growth` (line chart), `target`, `question`,
  `examine` (magnifier), `done` (check). Closed-circle ring shared by
  compass/pressure/target/question/done: `M 48 16 A 32 32 0 1 1 48 80 A 32 32 0 1 1 48 16 Z`.
- Adding an icon = a new entry in that `ICONS` map + a name here. Keep the set
  small and on-language (line-art, oval-ring family); don't open a clip-art floodgate.

## Host-root progress rail

A thin brand-gold rail that advances across the **whole runtime** — a completion
indicator (a documented watch-through lever), never scene motion. It lives at the
**host root** (`index.html`), not in any sub-composition, because it must span
every scene. Every build carries it (the `/render-lessons` "Assemble `index.html`
FIRST" step wires it in; there is no scaffold file to inherit from — the newest
build is the copy pattern).

- **DOM** (inside `#root`, after the scene clips, before the `<audio>`): a faint
  full-width track `#hf-rail-track` and a gold fill `#hf-rail-fill`
  (`transform-origin:left center; transform:scaleX(0)`), ~4px tall, bottom edge
  inside the safe margin, clear of the scene index and the outro lockup. Track
  `#cccedf` (white-tint on navy); fill `#eaab2d`.
- **Drive** (host `<script>`, the root `"main"` timeline — the slot the demo reel
  left empty): read the span from the compiler-owned `#root data-duration` at load
  and `fromTo("#hf-rail-fill", {scaleX:0}, {scaleX:1, duration: total, ease:"none"}, 0)`.
  Proportional and deterministic — no hand-typed total, no clock. The rail is not a
  scene clip (no `data-composition-src`), so the deterministic gates ignore it; it
  does not participate in scene coverage and never satisfies `check_presence`.

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
  rotate `summit → horizon → cadence` by the program's **started-build** count
  (count mod 3) — the number of `*.txt` in the program's
  `lesson-scripts/<program-slug>/rendered/`. Every gate-clean build's script
  lands there at B3, so this count covers delivered **and** at-gate builds
  without ever scanning `_archive/` (which the hard rules forbid routing to).
  An in-flight build claims its theme immediately — consecutive builds in one
  batch keep incrementing the count locally; counting deliveries lets
  consecutive videos ship in the same look.
- A new package = a new `data-theme` override block in **all nine** templates
  plus a row here. Never fork a template to make a look.

## Motion rotation — the sanctioned arsenal

Curated from the full HyperFrames skill pack + registry (surveyed 2026-07-09) so
every lesson can vary its motion without re-researching. Each entry names the
recipe to start from — read the rule/blueprint file (in `.agents/skills/`) before
building; never reinvent one of these from scratch. Compose 2–4 per scene, max.

| Need | Recipe (skill · rule/blueprint) | Notes |
| --- | --- | --- |
| Word pops/glows as it's spoken | `hyperframes-animation` · `asr-keyword-glow` (karaoke variant) | Not built into any template (removed from `scla-statement` 2026-07-11); use the rule directly for a bespoke scene |
| Highlight sweep / hand-drawn circle / scribble underline on a word | `hyperframes-animation` · `css-marker-patterns` | 5 pure-CSS marker emphases, timed to the word's start |
| Pill/chip cluster popping on cues | `hyperframes-animation` · `spring-pop-entrance` (staggered pills) | Built into `scla-chips`; ≤0.5s stagger cap |
| List/tiles beyond a numbered build | `hyperframes-animation` blueprint · `grid-card-assemble` | Cards/pills/list-lines cascade into a grid or vertical list |
| Phrase-by-phrase kinetic type | `hyperframes-animation` blueprint · `kinetic-type-beats`; also `techniques.md` §4 per-word slide-in | For beats where the words ARE the visual |
| Text-trail / weight-step kinetic type (upgrade) | `hyperframes-keyframes` · text trails; weight steps across the self-hosted 400/700/900 only (Proxima Nova is **not** a variable font — no VF interpolation) | **Adopted 2026-07-15.** Higher-energy type for "the words ARE the visual" beats (`scla-statement`, `scla-title`, bespoke). Staged entrance/beat motion only — never idle re-animation of settled text (animacy ban, reaffirmed 2026-07-15) |
| Route/path/diagram traces itself | `hyperframes-animation` · `svg-path-draw` (stagger multi-path ~70–80%) | Built into `scla-career-map`; also arrows, brand-mark draws |
| One shape morphs into another (SVG shape morph) | `hyperframes-keyframes` · SVG morph — morph pairs must share compatible path structure (asset prep per pair) | **Adopted 2026-07-15.** A cued transformation beat (seed→tree, ✕→✓): shows change/progress more vividly than a cut. Use sparingly — one morph per scene max, on-cue, seek-safe; never as idle motion |
| Element travels along a path | `hyperframes-keyframes` · Path travel (GSAP MotionPath) | Figure/marker moving along a drawn route |
| Count-up / stat with graphic | `hyperframes-animation` · `counting-dynamic-scale` + `stat-bars-and-fills` | Pair with `scla-stat` (built-in bar; `ring:"on"` adds a filling closed-circle gauge) |
| Living icon draws on as it's named | brand-native SVG line-art · `strokeDashoffset` draw-on, gold accent pops last (`back.out`) | Built into `scla-condition`; geometry set in "Living icon library" below. Reserved for the condition/principle hero — not sprinkled on other scenes |
| Two-option A→B morph (FLIP hand-off) | `hyperframes-animation` · `card-morph-anchor` / `scale-swap-transition` | Built into `scla-morph`: winner re-flows to top, grows, turns gold, may relabel. Seek-safe x/y/scale tweens |
| Many items gather into one cluster | `hyperframes-keyframes` · FLIP (recorded start/end → numeric x/y/scale) | The pilot's "five conditions gather into a ring" beat. Bespoke; anchor to the closing cue, tween-only |
| Depth-drift parallax on a navy hero | translate-only 2.5D drift on background layers, finite `sine.inOut` yoyo cycles (~2.5–3.4s period, **~85–120px** — small 16–30px moves <1 gray level per 48×27 QA thumbnail px and reads static, so amplitude must clear the sampler) (CSS/GSAP, **no Three.js**) | Built into the navy templates (title/statement/outro/quote/stat). Texture that also guarantees pixel-level animacy at QA sampling (re-tuned 2026-07-15; amplitude raised across all heroes to the registering band 2026-07-15) |
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
