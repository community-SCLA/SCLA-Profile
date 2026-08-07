# Builder Contract

Build one SCLA lesson into one gate-clean HyperFrames workspace. Read only this
file, the selected concept, the one refined script, and the workspace's
`tokens.yml`. Do not render, publish, inspect other builds, or load human docs.

## Inputs

- `STEM`: undated canonical `<title>_<program>` name
- `PROGRAM`: lesson-script program folder
- refined script: the verbatim narration source
- `CONCEPT.md`: selected visual thesis and milestone frames
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

2. Write `design.md` with the chosen concept, visual carrier, beat-to-frame map,
   and motion logic. Make the lesson feel like one developing idea, not a stack
   of interchangeable cards.

3. Write `audio_request.json`. Every `lines[].text` must trace exactly to the
   refined script. Beat IDs are arbitrary but unique; never depend on an `s`
   prefix.

4. Author `index.html` directly. On-frame words live in markup. Use the local
   token values and assets; do not create a compiler or `make_*.py` helper.

5. Run static QA before paid synthesis:

   ```bash
   python3 projects/video-production/render-qa/src/preflight.py \
     projects/video-production/renders-hyperframes/STEM --static
   ```

6. Synthesize and compute timing through shared production tools:

   ```bash
   bash scripts/video-audio.sh \
     projects/video-production/renders-hyperframes/STEM
   python3 projects/video-production/render-qa/src/plan_timing.py \
     projects/video-production/renders-hyperframes/STEM
   ```

   Apply `timing.json` values to the composition without altering them.

7. Run the durable gate:

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
- Stage motion around meaning: establish, transform, settle. Content must be
  readable at its settled state and seek-safe at arbitrary frames.
- Keep text concise, large, and within token-defined safe regions. Use only the
  token palette and brand typefaces.
- Prefer designed typography, diagrams, paths, and simple data forms. Decorative
  detail must clarify hierarchy or progression.

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
