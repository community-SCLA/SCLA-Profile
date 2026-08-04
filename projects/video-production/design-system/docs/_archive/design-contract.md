# SCLA Lesson System — the design contract

> **Normative numbers are NOT in this file.** Colors, type scale, minimum text
> sizes, spacing tokens, the pinned voice and the program display-name map live
> in `../config/tokens.yml`, which `render-qa/src/tokens.py` parses and the gates
> grade against. This document is the human-readable contract around those
> numbers. If a sentence here disagrees with `tokens.yml`, `tokens.yml` wins —
> and the sentence is a bug (see `decisions/log.md`, 2026-07-29: the pipeline
> once correctly obeyed this spec and violated the owner).
>
> Split out of frame.md on 2026-07-29. Rules below that no checker enforces
> are conventions; see `.claude/rules/video-production.md` for the mechanized set.

The video design system for SCLA lesson videos (audience: college students 18–24).
`../config/tokens.yml` is normative — quote hex/weights verbatim from it, never
round, and never restate a number here. Source of brand truth:
`brand/visual-identity.md` and `brand/voice-and-tone.md`; the token file adapts
those to the video frame per the HyperFrames video-composition rules.

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

- **No stagnant frame beyond 3.0s (WARN) / 6.0s (FAIL, raised from 5.0s 2026-08-04 —
  BUILD-PLAN A1, `render-qa/src/check_presence.py`).** Once a scene's opening beat lands, something
  must keep resolving — the next item, an illustration, a highlight, a figure —
  timed to what the narration is saying *right now*. If nothing can happen for
  the next few seconds, the scene is too long: split it into more scenes.
- **Entrance settles by 1.2s (Motion v2, 2026-07-27).** All non-cued content is
  in place ≤1.2s after the cut; hero tweens ≤0.6s. Furniture still paints at
  t=0 (opacity 0.55 → 1 in ~0.3s, so cuts land as a hit, not a dissolve). Slow
  meters (a 2.4s track fill, three parallel 1.6s stat ramps) are defects —
  stagger and compress them inside the budget.
- **Every scene ends with a closing beat (Motion v2).** One cued resolve in the
  scene's final second — a rule completes, a check/accent pops, dimmed items
  restore to full — so no scene coasts to its cut. Additive motion only: this
  is a NEW beat, not re-animation of settled content (the 2026-07-14/15 idle
  keep-alive ban stands untouched).
- **Every scene exits (Motion v2; scla-outro exempt).** At sceneDuration−0.35
  the content layer (never the furniture) slides out 0.3s `power2.in` with a
  GSAP hard-kill `set()` at the boundary (the `gsap_exit_missing_hard_kill`
  lint enforces this); entrances arrive from the opposite edge so seams read
  velocity-matched instead of cut-on-frozen-frame.
- **Focus follows the voice (compound cues, Motion v2).** When a cued item
  lands, already-settled sibling items dim to ~0.6 (0.3s); the closing beat
  restores them. De-emphasis driven by a *new* beat is sanctioned; idle wobble
  of settled content remains banned.
- **Pacing budget — deterministic (preflight-enforced, 2026-07-27).** Per
  scene, visual events = entrance settle (1.2s) + every compiled cue + the
  closing beat (duration−0.5). Largest gap between consecutive events: FAIL
  above 4.0s, WARN above 3.0s (tightened 2026-07-28 — the pilot's 4.5s empty
  heading hold passed at the old numbers). Scene duration caps: ≤12.5s standard,
  `scla-title` ≤6.5s, `scla-outro` ≤8.5s (title/outro are duration-capped and
  exempt from the gap check). A failing scene is re-authored — split it, add
  cues, or move the boundary; never satisfied with background drift.
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
  **The motion is deleted, not merely discouraged** (2026-07-29, owner: "can we
  just get rid of that hyperframe element so it's not ever used?"): the
  career-map node pulse, the living-icon bob in `scla-condition` / `scla-chips`
  / `scla-steps` / `scla-statement`, and `scla-condition`'s accent re-pop are
  gone from the templates, so there is nothing left to select.
  *(Mechanism: `render-qa/src/check_motion.py`, run by `preflight.py` in both full
  and `--static` mode and by `npm run check` over the demo reel. It grades every
  repeating tween — `yoyo`, or `repeat` other than 0 — and allows NOTHING by
  name, following a selector through a helper's call sites so a content tween
  cannot be laundered through the drift helper the way the icon bob was. Every
  exemption is declared with `/* motion-allow: <reason> */`, never assumed and
  never inferred from an id: the nine-substring allow-list (`ghost`, `ring`,
  `-bg`, …) was removed 2026-08-04 because it read a NAME as an intention, and
  because agent-authored HTML follows no such convention. For a helper-routed
  tween the declaration sits on the CALL SITE — a helper body serves every
  caller, so an allow there is a blanket exemption. Firing fixtures:
  `render-qa/tests/test_motion.py`; full-length mutation in
  `render-qa/tests/test_mutations.py`.)*
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
  ripples/re-marks instead of re-authoring was vetoed by the owner — and as of
  2026-07-29 that trade is not available: the keep-alive motion is deleted from
  the templates and a re-add is a red gate, so a stagnant scene can only be
  fixed by re-authoring it.) *(Mechanism: `render-qa/src/check_motion.py`.)*
- **Depth-drift runs in finite yoyo cycles (2026-07-14; re-tuned 2026-07-15).**
  The navy hero templates (`scla-title`, `scla-statement`, `scla-outro`,
  `scla-quote`, `scla-stat`) — and the light templates' ghost layers — drift
  their *background* layers at different rates: translate-only 2.5D parallax
  (CSS/GSAP, never Three.js), **~85–120px** amplitude on a ~2.5–3.4s
  `sine.inOut` yoyo period, repeated (finitely) to cover the whole scene.
  Amplitude has to clear the QA sampler: a 16–30px move is <1 gray level per
  48×27 thumbnail pixel and reads as static. The original
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

- **Narration is synthesized per scene** (`render-qa/src/synth_narration.py`,
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
  defect; re-run the compiler instead. `render-qa/src/preflight.py` re-derives
  everything and fails the build on any drift.

Cuts are graded at QA against `assets/voice/transcript.json`, not by feel:

- **Boundaries land on sentence ends.** Never cut mid-word or mid-sentence; the
  sentence that opens a thought belongs to the scene that illustrates it. If a
  sentence straddles a planned cut, move the boundary — don't split the sentence.
- **A sentence longer than its scene's cap is a script defect, not a pacing
  one (2026-07-27).** This rule and the duration caps can deadlock: a single
  sentence whose speech exceeds 12.5s (title 6.5s, outro 8.5s) offers no legal
  cut anywhere inside it, so no re-authoring of `scenes.json` can clear the
  pacing gate. The sanctioned repair is **word-preserving re-punctuation of the
  refined script** — an em dash, colon, or semicolon joining two independent
  clauses becomes a period, which creates a legal boundary. No word may be
  added, removed, reordered, or altered: `preflight`'s `script_match` must
  still report 0.00% afterward. Rewording is never the fix, and neither is an
  exception to the cap. Word count does not predict this — measured across 90
  built scenes the speech rate spans 2.18–3.51 w/s (median 2.85), because
  commas and dashes buy pause time; a 12-word title card has run 7.0s. Judge by
  the compiled duration, never by length on the page.
- **An em dash/colon/semicolon that splits reveal-cues across its two clauses
  gets converted to a period regardless of duration, not only when the scene
  is over cap (2026-07-27).** Neither narration voice supports pause tags
  (`design-system/AGENTS.md` → "Narration voice") — text punctuation is the
  only pacing signal that reaches the audio, and an em dash joining two
  independent clauses is a weak one: TTS often doesn't pause on it, so a cued
  phrase right after the dash reads as glued to the clause before it. The
  trigger is structural, not caps: a `chipCues`/`pointCues`/`stepCues` phrase
  in the clause *before* the dash and another *after* it. A plain
  comma-separated list inside one clause ("more impact, more recognition, or
  a role that fits you better") is unaffected — commas already read as clear
  pauses; leave those alone. Apply the same word-preserving re-punctuation as
  above (`script_match` still 0.00% afterward) only at the dash/colon/
  semicolon boundary itself.
- **≥0.2s of air after the last word.** A scene may not cut until at least
  0.2s after its final spoken word's `end` time. Cutting at or before the word's
  end (the old builds cut up to 0.36s *early*, mid-word) is a defect.
- **Questions keep their inflection.** When a scene ends on a question, the cut
  waits for the rise to finish — pad after the question mark.
- **Every spoken list of ≥3 items takes "and" or "or" before its final item
  (gated 2026-07-28).** Without the conjunction the narration doesn't resolve,
  it just stops, and the listener can't hear that the list ended. This held the
  weaker word "prefer" from 2026-07-27 until the owner reported it again against
  the 2026-07-28 build — with the same mentorship/growth example this bullet
  had been carrying all along. It applies whether the items are punctuated as
  one comma list ("more impact, more recognition, or a role that fits you
  better") or as separate fragments ("Meaning? Mentorship? Or growth?"), and it
  is a **script** rule, so the repair is in the refined `.txt`, not the frame —
  chips and on-frame labels stay bare.
  *(Gate: `render-qa/src/check_copy.py`, run by `preflight.py`.)*
- **In-scene silence is capped at 0.5s (gated 2026-07-28).** HeyGen's Oxana
  emits 0.98–1.26s of real dead air at some sentence boundaries,
  non-deterministically — measured 3× variance across four identical "Ordinal,"
  constructions in one build (0.38s / 0.48s / 0.50s / 1.14s). No punctuation or
  re-wording can control it, so it is fixed **after** synthesis:
  `synth_narration.py` compresses any in-scene inter-word gap above
  `MAX_INSCENE_GAP` and shifts that clip's remaining word timestamps to match.
  This matters twice over, because `compile_timeline.py` derives reveal cues
  from those same timestamps — an uncapped pause stalls the picture and the
  sound together, which is what the owner heard as "a major glitch or lag
  between the statement heading and the points." Scene-boundary air (0.3s /
  0.45s after a question, + 0.15s lead) is unaffected; the cap sits just above
  it so a mid-sentence pause can never outlast a scene change.
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

## Variety contract — normative, gated

Decided 2026-07-27 with Motion v2, but left as prose in the decision log and
never written here or into either skill. It did not hold: the 2026-07-28
`better-decisions` build put 21 scenes on 5 templates (8 of them
`scla-statement`, an unbroken run of 5 near-identical condition/chips slides,
six templates untouched) and every gate passed it. The owner's verdict was
"boring, doesn't have a lot of visual variety, feels a bit slow." It is now a
gate: **`render-qa/src/check_variety.py`, run by `preflight.py`.**

- **Never render a one-item list.** A list slot holding exactly one item draws
  the bullet/pill/numbered-point illustration around a single fact. You would
  never render a single bullet point. Either give it ≥2 items or move the beat
  to a form that states one idea (`scla-statement`, `scla-quote`, `scla-stat`).
  *(Gate: `render-qa/src/check_variety.py` rule 1 — hard fail.)*
- **Max 2 consecutive scenes on one template family** — unless the run is a
  genuine enumerated series. Three plain repeats is the same slide three times.
  A run may extend to 6 **only** if every scene in it advances a visible
  progress indicator, carries its *own* artwork (no asset repeats inside the
  run), and lasts ≤7s. That exemption is measured, not theoretical: the
  reference video's best passage is five consecutive `scla-condition` scenes
  that do exactly this. *(Gate: `render-qa/src/check_variety.py` rule 2 — hard fail.)*
- **≥6 distinct content forms** per lesson ≥90s, **≥7** at ≥150s (≥4 below 90s),
  counting everything but `scla-title`/`scla-outro`. *(Gate: `render-qa/src/check_variety.py` rule 3 — hard fail.)*
- **No single form carries more than 40% of the content seconds.** Passing the
  rules above while putting 42% of the video on one template still reads as
  monotony. *(Gate: `render-qa/src/check_variety.py` rule 4 — hard fail.)*
- **The unused-template list is a menu, not a suggestion.** The gate prints
  what you didn't touch. If `scla-career-map`, `scla-steps`, `scla-morph`,
  `scla-loop`, `scla-quote` or `scla-stat` fits a beat, use it — when the
  narration literally names the artifact ("a tool like a career map becomes
  helpful") and the build shows a generic bullseye instead, that is the single
  clearest miss the frame can make.
- **Artwork on ≥60% of content scenes, ≥5 distinct assets, none used more than
  twice, and never more than 2 bare scenes in a row.** This is the largest
  measured gap between the reference video and the rejected one — 79% vs 33%,
  ~11 devices vs 6 with one doubled — and it went ungated entirely until
  2026-07-28, which is how "boring" passed every check. Type on a flat field is
  not an illustration, and neither is the same monoline icon parked in the same
  right-hand slot every time. The reference earns its coverage with a real bar
  chart (axes, bars growing to different heights), an advancing 5-dot stepper,
  figure glyphs mirrored and recoloured so the repeat reads as variation, and
  red strike-throughs annotating live text.
  *(Gate: `render-qa/src/check_variety.py` rule 5 — hard fail.)*
- **Rotate the connective tissue too.** The circled/ringed point is one device
  among several. An arrow drawn from one statement to another, a comparison
  scale, a split frame, a trace along a path — reach for these before repeating
  the pill row a fourth time.

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
400 body. No 300 or 600 — the kit doesn't ship them. Uppercase + 0.14em tracking
is reserved for labels/eyebrows/chips.

- **Headings are Title Case; body is sentence case (preflight-enforced,
  2026-07-28).** A heading is the `heading` / `statement` / `title` slot — the
  line the viewer reads as the frame's headline. Every principal word is
  capitalised; articles, coordinating conjunctions and short prepositions stay
  lowercase unless they lead or close the heading ("Better Decisions Come from
  Better Criteria"). Acronyms keep their own casing (AI, SCLA). **A heading
  carries no terminal period** — `?` and `!` are fine. Body copy — points,
  lines, sub-beats, captions, chips — stays sentence case.
  This line used to read "sentence case for titles and body", which is why
  every heading in the 2026-07-28 build shipped sentence case and mixed
  terminal periods across adjacent scenes despite repeated owner correction.
  *(Gate: `render-qa/src/check_copy.py`.)*
- **Minimum on-frame text size — hard floor (preflight-enforced, 2026-07-27).**
  **Body-class text never renders below 40px** (raised from 32 on 2026-07-29 —
  see the frontmatter note); label-class furniture never
  below 20px (frontmatter `typography.min-size`). Body class = anything the
  viewer reads as a sentence — points, captions, card copy, sub-beats, notes.
  Label class = the uppercase + letter-spaced furniture only (eyebrow, scene
  index, brandline, chip, attribution). The gate classifies by that styling:
  a rule with `text-transform: uppercase` **and** `letter-spacing` is graded
  against the label floor, everything else against the body floor. Marker
  numerals sized by their circle (step node, point marker, morph card number)
  opt out with `/* text-floor-exempt: <reason> */` on the rule. Sub-32px body
  copy is unreadable at viewing distance and reads as filler — if a line only
  fits at 28px, cut the line, don't shrink it.
- **Never restate the label or heading elsewhere in the frame
  (preflight-enforced).** A sub-beat, caption, or point that repeats what the
  eyebrow or heading already says is dead weight — it adds a second, smaller
  copy of a line the viewer has already read at full size (owner call,
  2026-07-27: "having it there in the first place is totally unnecessary
  because it is already located at the top of the frame"). The gate FAILs any
  `subBeats` / caption / point whose words are a subset of, or ≥80% overlap
  with, that scene's `label` or `heading`. A sub-beat exists to carry narration
  the frame is **not** already showing; if it has nothing new to say, drop it
  and let the scene's cued items cover the span.

## Title card & outro sources (deterministic — never invent these)

The title card's `eyebrow` and `title`, and the outro's closing copy, are
DERIVED, not authored:

- **`eyebrow` = the program's display name**, read from the `programs:` map in
  `../config/tokens.yml` — a wrong or invented program name is a gate failure
  (`preflight.py`). Add a new program to that map, never here: this file is
  prose and the gate does not read it. **The banner IS the
  `lesson-scripts/<slug>/` folder name** (owner, 2026-07-29, "a MUST … a hard
  rule"): a display name is legal only if it slugifies back to its own key, so
  `early-career-boost` renders as "Early Career Boost" and nothing else. The
  2026-07-21 "Career Accelerator" on-screen rebrand is reverted — it shipped a
  banner that named a program the lesson does not belong to, and check 7b
  passed it because the map it graded against was free text.
  (Mechanism: `tokens.programs_problems()` → `preflight.py` check 7b in full
  AND `--static` mode, plus `render-qa/tests/test_programs.py` in CI, which
  also fails if a `lesson-scripts/` folder has no banner or a banner has no
  folder.)

- **`title` = the lesson title from the script stem** — the stem's title
  segment with hyphens as spaces, Title Case per the heading rule above
  ("better-decisions-come-from-better-criteria" → "Better Decisions Come from
  Better Criteria"). Never the opening narration sentence, never a paraphrase
  (checked by `preflight.py`; casing checked by `check_copy.py`).
- **Outro `cta`/`next`**: drawn from the closing narration — `next` may quote
  it; `cta` is a short imperative pulled from it. The two must not restate
  each other.

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
- **`iconCue` (optional, Motion v2 2026-07-27):** every icon slot takes an
  optional cue (author it by phrase in `data-cue-anchors` as `"iconCue"`; the
  compiler resolves it) so the draw-on fires the moment the narration names the
  thing — a real mid-scene beat instead of fixed entrance decoration at t=0.7s.
  Empty keeps the legacy entrance draw.
- **Wider icon slots (Motion v2):** `scla-points` accepts optional per-item
  `icons` (comma list from the ICONS set, revealed on each item's cue),
  `scla-morph` optional per-card icons, and `scla-chips` an optional
  statement-style hero `icon`. Defaults stay empty — existing builds compile
  unchanged. The "novel, not on every frame" discipline still governs use.
- **An icon name the template's own library lacks draws nothing, silently.**
  `ICONS[name]` returning undefined is a typo no browser can report, and the
  libraries are per-template copies that drift: `map` existed in
  `scla-statement` and `scla-steps` and not in `scla-points`, so scene-17 of the
  2026-07-29 criteria build shipped with a hole where row 2's icon belonged and
  every gate passed it. *(Mechanism: `render-qa/src/check_slots.py` rule
  `unknown-icon`, which reads the library it is actually calling — run by
  `preflight.py` in full AND `--static` mode. The four libraries were re-synced
  the same day.)*
- **Hide the wrapper until the draw-on cue (render-qa friction log, 2026-07-27
  B1):** every icon path is built with `stroke-linecap: round` and animated
  from `strokeDasharray "100 100"` / `strokeDashoffset 100`, which is a
  zero-*length* stroke — but a round linecap still paints it as a filled dot,
  not nothing. Any icon host (`#cd-iconwrap`, `#sm-iconwrap`, `#st-iconwrap`,
  `#cc-iconwrap`, `.mp-cicon`, `.kp-icon`) must therefore be held at
  `opacity: 0` from t=0 and only set to `opacity: 1` at the same cue
  (`drawAt`/`iconAt`) that starts the stroke-draw tween — the draw-on is the
  reveal; without the opacity hold, the dot is visible from t=0 until the cue
  fires. All six current icon hosts carry this fix; a new icon-bearing
  template must repeat it.
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
  `examine` (magnifier), `map` (folded map with a gold pin — the picture for
  "compare your options on a career map"; added 2026-07-29 after the owner
  called out a magnifying glass as the wrong image for that beat),
  `done` (check). Closed-circle ring shared by
  compass/pressure/target/question/done: `M 48 16 A 32 32 0 1 1 48 80 A 32 32 0 1 1 48 16 Z`.
- Adding an icon = a new entry in that `ICONS` map + a name here. Keep the set
  small and on-language (line-art, oval-ring family); don't open a clip-art floodgate.

## Host-root progress rail

A thin brand-gold rail that advances across the **whole runtime** — a completion
indicator (a documented watch-through lever), never scene motion. It lives at the
**host root** (`index.html`), not in any sub-composition, because it must span
every scene. Every build carries it — since 2026-07-28 it comes pre-wired in
`renders-hyperframes/_run/scaffold/index.html`, which builds clone
(`scripts/batch-prepare.sh` generates it from this section), so no build can
forget it and no builder has to copy the pattern out of another build.

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
- Assignment: the human picks, or **`render-qa/src/theme_for.py <program-slug>`**
  answers. It rotates `summit → horizon → cadence` by the program's
  **started-build** count and is the only thing that computes this — including
  the `--offset N` an orchestrator passes for the Nth video of a batch, so
  consecutive builds keep rotating instead of all reading one pre-batch count.
  This paragraph used to restate the computation (`count(*.txt in rendered/)
  mod 3`) and drifted from it silently on 2026-07-28, when that folder came to
  mean *published* — leaving mid-career-momentum at a count of 0 with 14 builds
  on disk, and every one of its next 12 videos assigned `summit`. Prose that
  restates a computation drifts from it; prose that cites a script cannot.
- A new package = a new `data-theme` override block in **all twelve** templates
  plus a row here. Never fork a template to make a look.

## Motion rotation — the sanctioned arsenal

Curated from the full HyperFrames skill pack + registry (surveyed 2026-07-09) so
every lesson can vary its motion without re-researching. Each entry names the
recipe to start from — read the rule/blueprint file (in `.claude/skills/`) before
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
| Living icon draws on as it's named | brand-native SVG line-art · `strokeDashoffset` draw-on, gold accent pops last (`back.out`) | Home is `scla-condition`; geometry set in "Living icon library" below. **Scope widened 2026-07-15** — also legal on a genuinely single-focus beat of another template (optional `icon` variable), one hero per scene, sparing and on-language. Never sprinkled |
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
