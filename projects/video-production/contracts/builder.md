# Builder Contract

Build one SCLA lesson into one gate-clean HyperFrames workspace. Read only this
file, the selected concept, the one refined script, and the workspace's
`tokens.yml`. Do not render, publish, inspect other builds, or load human docs.

## Inputs

- `STEM`: undated canonical `<title>_<program>` name
- `PROGRAM`: lesson-script program folder
- refined script: the verbatim narration source
- `concepts/CONCEPT-BOARD.json`: three visible, materially different concept
  boards plus the independent selector's scored decision
- `CONCEPT.md`: the selected visual thesis and milestone frames
- `_run/scaffold/`: pinned HyperFrames runtime, brand assets, fonts, and tokens

## Build sequence

1. Enter through exactly one claim path.

   **New build — no workspace exists:**

   ```bash
   bash scripts/build-claim.sh STEM PROGRAM
   ```

   The claim command wins the atomic directory lock first and then hydrates the
   prepared scaffold itself. If it fails, stop. Never copy the scaffold by
   hand, delete or rename a workspace, or build into another claim.

   **Resume — the canonical workspace already exists:**

   ```bash
   bash scripts/build-claim.sh STEM PROGRAM --resume
   ```

   Resume never copies the scaffold. Before returning, the claim command saves
   the existing authored source under
   `source-revisions/<content-revision>/`, including visual assets. Exact voice
   bytes are retained once in the checkpoint blob store; QA evidence, snapshots,
   and caches are excluded. Continue from the files that exist; do not recreate
   completed work. Repeating resume without a source change reuses the same
   checkpoint.

2. Before authoring the composition, create `concepts/CONCEPT-BOARD.json` and
   the three board images it names. Each option needs a different visual carrier
   and layout family plus at least five milestone frames. Variants of one card,
   dashboard, timeline, or split-screen template count as one idea. Record the
   author and a different selecting agent; score every option for clarity,
   progression, variation, and teaching value; explain why each loser lost.
   The selected option must be a highest-scoring option.

3. Write `design.md` with the chosen concept, visual carrier, beat-to-frame map,
   and motion logic. Make the lesson feel like one developing idea, not a stack
   of interchangeable cards.

4. Write `audio_request.json`. Every `lines[].text` must trace exactly to the
   refined script. Beat IDs are arbitrary but unique; never depend on an `s`
   prefix.

5. Author `index.html` directly. On-frame words live in markup. Use the local
   token values and assets; do not create a compiler or `make_*.py` helper.

6. Run static QA before paid synthesis:

   ```bash
   python3 projects/video-production/render-qa/src/preflight.py \
     projects/video-production/renders-hyperframes/STEM --static
   ```

7. Synthesize and compute timing through shared production tools:

   ```bash
   bash scripts/video-audio.sh \
     projects/video-production/renders-hyperframes/STEM
   python3 projects/video-production/render-qa/src/plan_timing.py \
     projects/video-production/renders-hyperframes/STEM
   ```

   Apply `timing.json` values to the composition without altering them.

8. Run the durable gate:

   ```bash
   bash scripts/build-gate.sh STEM
   ```

   Fix the composition until it passes. The gate, not prose, owns measurable
   requirements. Release the lease when the build session ends:

   ```bash
   bash scripts/build-release.sh STEM
   ```

## Content contract

- Do not invent SCLA facts, steps, counts, or examples. Visible copy may quote
  or compress its own beat but must not change the claim.
- Derive the program eyebrow from `tokens.yml programs:` and the title from the
  canonical stem. Both must be visible markup.
- Headings stand alone as complete phrases. Avoid fragments that depend on later
  text to become meaningful.
- Use semantic markup: headings use heading elements or `data-role="heading"`;
  lists and comparisons identify their structure.

## Visual contract

- Use one recognizable visual carrier across the lesson and evolve it as the
  argument develops.
- Make each beat materially different in composition or state while preserving
  continuity. Avoid repeated centered title-plus-card layouts.
- Treat narration clips as audio units, not automatic scene boundaries. Keep one
  visual scene on screen through a complete sentence or tightly connected idea,
  even when that thought spans several clips. Never trigger a whole-scene exit,
  entrance, or transition mid-sentence; evolve meaning-bearing elements inside
  the persistent scene instead. A new scene requires both a completed sentence
  and a material change in idea or visual carrier. Repeated copies of unchanged
  graphics with generic exit/re-entry motion do not count as distinct scenes.
- Stage motion around meaning: establish, transform, settle. Content must be
  readable at its settled state and seek-safe at arbitrary frames.
- Never add a playback progress bar, rail, scrubber, signal trace, or sliding
  completion line anywhere in the frame. This includes a line that grows for
  one scene's duration as well as one that grows for the whole lesson. Temporal
  progress movement is forbidden and earns no motion credit; every beat must
  develop the lesson's visual idea on its own.
- Do not display module/scene numbers as persistent chrome or current/total
  counters such as `03 / 24`. Those are authoring and deck conventions, not
  useful information in a rendered MP4.
- Keep text concise, large, and within token-defined safe regions. Use only the
  token palette and brand typefaces.
- Prefer designed typography, diagrams, paths, and simple data forms. Every
  illustration beyond ordinary text structure must explain a mechanism,
  relationship, sequence, comparison, or change. If it adds visual activity but
  no understanding, simplify it or remove it.
- Arrows and directional marks must connect named states or show an actual
  relationship. Never use an arrow as a false button, navigation cue, or
  decorative promise that a video viewer could click.
- Use the available frame intentionally. Do not shrink the entire lesson into a
  small panel with a large unused side field; scale and balance the main visual
  mass for the full 16:9 canvas unless the negative space itself explains the
  idea.
- When several beats discuss one list, keep one list on screen and highlight or
  transform the active item. Do not exit and repopulate the same blocks beside
  headings that restate them; either focus on one point or make the persistent
  list carry the progression.
- Compose and inspect each beat at its most crowded settled frame. Maintain a
  clearly readable breathing zone between unrelated text blocks, illustrations,
  paths, and labels; use layout gaps and padding rather than narrowly avoiding a
  collision. Related elements may group tightly only when the grouping remains
  visually calm and unambiguous.
- Size the message for the whole video frame, not for a web card. Across the
  lesson, most sampled frames must carry meaningful foreground detail through at
  least five of the nine equal content zones measured by `check_ink.py`. In a
  split frame, neither the copy nor the teaching graphic may read as a small
  island beside a much larger partner. Preserve the safe padding while enlarging
  both sides as one balanced composition.
- When narration lists or compares points, reveal or visibly emphasize the
  specific item being spoken. Populating every item at once, applying one quick
  style sweep to the whole group, or rebuilding the same carrier in every scene
  is a blocking defect, even when those entrances satisfy a motion counter.
- Keep text-bearing elements stable after they settle. Do not make text or text
  boxes bounce, blink, flicker, ripple, or repeatedly pulse for attention.
  Motion must establish, reveal, connect, transform, or resolve meaning.
- When geometry communicates structure, construct it accurately: concentric
  shapes share one center, circles stay circular, and relationship lines terminate
  cleanly without crossing labels or unrelated illustrations.

## Infrastructure contract

- Production voice has no fallback. Do not call TTS directly.
- `audio_meta.json` owns real durations and clip paths. `plan_timing.py` owns
  silence hygiene, gaps, final padding, and `timing.json`.
- Never run a render or Wistia upload. The driver owns shipping and failure
  receipts.
- Never modify shared scripts, tokens, gates, contracts, or another workspace
  while a build lease is active.

## Return

```text
workspace: <path>
beats: <count>
concept: <one line>
gate: PASS|FAIL
status: <one line>
```
