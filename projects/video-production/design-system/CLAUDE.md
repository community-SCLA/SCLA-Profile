# SCLA Video Design System — HyperFrames project

The brand-owned illustrated-video system for SCLA lesson videos. Nine reusable
scene templates + design tokens + a pinned narration voice give every lesson a
brand-true starting point — but the templates are the **structural floor, not a
ceiling**: the frame must stay alive and *illustrate what's being said*, not park
static text (`frame.md` → "Every scene earns its seconds" + "Illustration over
text"). Decision record: `decisions/log.md` (2026-07-07, revamped 2026-07-08).

**Read `frame.md` first** — it is the design spec (normative tokens + frame rules).
For HyperFrames authoring mechanics, start at the `/hyperframes` skill and let it
route; the composition contract lives in `/hyperframes-core`.

## What's here

| Path | What it is |
|---|---|
| `frame.md` | Design spec — SCLA tokens adapted to the video frame. Brand truth stays in `brand/`. |
| `compositions/scla-*.html` | The nine scene templates (sub-compositions with variables) — see table in `frame.md` |
| `index.html` | Demo reel: all nine templates with real approved-lesson content. Living style guide. |
| `assets/brand/` | SCLA logo SVGs (copied from `brand/assets/`) |
| `assets/fonts/` | Self-hosted Proxima Nova woff2 (400/700/900, from SCLA's Adobe kit) |
| `voice-auditions/` | Kokoro voice samples generated from approved script lines — listen and re-decide anytime |

## Commands

```bash
npm run dev      # preview server (long-running — background it)
npm run check    # lint + validate + inspect — ALWAYS run after edits
npx hyperframes snapshot --at <t1,t2,...>   # frame stills for eyeball review
npm run render   # MP4 — only after the human QA gate
```

If `validate`/`render` fails, hangs, or dies with an odd exit code (e.g. 144):
check `grep /dev/shm /proc/mounts` first — the codespace mounts `/dev/shm` at
64 MB and headless Chrome needs ≥256 MB. The devcontainer's `postStartCommand`
remounts it to 512 MB but can fail silently; fix with
`sudo mount -o remount,size=512M /dev/shm`. Pinned CLI is **0.7.45**
(`package.json`); copy that pin into new lesson workspaces. Never pin below
0.7.45 — earlier versions silently render every sub-comp scene as its template
defaults (upstream heygen-com/hyperframes#2064, fixed in 0.7.45; probe-verified
2026-07-09).

## Building a lesson video (the scale recipe)

1. **Approved script first** — the existing gate is unchanged: narration `.txt`
   approved and saved to `../lesson-scripts/<program-slug>/` before anything renders.
2. **New project per video:** `HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <script-stem> --example=blank --non-interactive`
   inside `projects/video-production/renders-hyperframes/`, then copy in `frame.md`,
   `compositions/`, `assets/` from this project.
3. **Narration** (voice is pinned in `frame.md` → `voice:`):
   ```bash
   npx hyperframes tts "$(cat ../../lesson-scripts/<program>/<stem>.txt)" \
     --provider kokoro --voice af_heart --speed 0.95 -o assets/voice/narration.wav
   npx hyperframes transcribe assets/voice/narration.wav --model small.en   # word timings
   ```
4. **Assemble** `index.html`: one slot per beat using the scene templates with
   `data-variable-values` (copy the pattern from this project's demo reel);
   `<audio>` for narration sits at the host root. Set the video's **style
   package** on every scene (`"theme":"summit|horizon|cadence"`) — one package
   per video, assignment rule in `frame.md` → "Style packages". Bespoke scenes
   are welcome — follow `frame.md`, don't fork the templates.

   **Never type a timing number.** Author the *anchors* and let the compiler
   own the numbers (`frame.md` → "Scene boundaries, padding & endings"):
   - every scene slot: `data-anchor-end="<its last spoken phrase>"` (verbatim
     transcript words);
   - every cue variable: `data-cue-anchors='{"chipCues":["phrase",…], …}'` —
     one transcript phrase per item, in spoken order;
   - placeholders are fine for `data-start`/`data-duration`/numeric cues —
     the compiler overwrites them.

   **Make every scene move (the animacy rules — `frame.md`).** Graded at QA:
   - **No stagnant frame beyond ~2s.** If a beat runs long with nothing left to
     reveal, split it into more scenes rather than parking static text. Title
     cards hold only for the opening line. (Templates carry a built-in
     late-phase resolve, but it supplements cue reveals, never replaces them.)
   - **Illustrate what's said.** Text is the floor; draw the thing (a path/map,
     a thinking figure, a comparison, per-item icons entering on cue). Author
     bespoke illustrated scenes for any narration that describes something
     concrete — and give them the same anchor attributes.
   - **Vary reveals.** Rotate list forms (`scla-chips` pop/slide, `scla-points`,
     grid cascade — `frame.md` → "Motion rotation"); the opening enumeration
     gets its own `scla-chips` scene right after the title; `scla-steps`
     overview only when the narration enumerates the steps. `scla-statement`
     has no per-word emphasis — its built-in reading ripple + late-phase
     resolve keeps long holds alive without per-scene authoring.
   - **Statement vs. quote.** A program/SCLA thesis is `scla-statement` (bold,
     unattributed). `scla-quote` is only for a **named person's** words.
   - **Numerals & index.** Scene index stays small in the lower-right. A hero
     numeral is only a real stat (`scla-stat`) or the spoken step (`scla-steps`).
5. **Compile + gate (one command each, from the workspace):**
   ```bash
   python3 ../../render-qa/compile_timeline.py . --apply   # pads silence, sets every boundary/cue from the transcript
   python3 ../../render-qa/preflight.py .                  # compiler drift + boundary rules + coverage + theme — exit 0 or fix
   npm run check                                          # lint + validate + inspect
   npx hyperframes snapshot --at <scene-midpoints>        # stills for eyeball review
   ```
   `--apply` is idempotent; re-run it after any script/beat change. If an
   anchor fails to resolve, the compiler names the scene and the transcript
   window — fix the phrase, never the numbers.

   > History: on CLI ≤0.7.44 render ignored sub-comp `data-variable-values`
   > (heygen-com/hyperframes#2064), which forced a manual "bake defaults" step and
   > per-instance template copies. **Fixed in 0.7.45** (probe-verified 2026-07-09:
   > injection, multi-mount, and per-mount seeking all correct). No baking needed —
   > `data-variable-values` in `index.html` is the single source of scene content,
   > and one template file can be mounted many times.
6. **Human QA gate** — `../script-templates/qa-checklist.md` (illustrated section). Never skip.
7. **Render + verify + file:** kill any stale preview servers first — use exactly
   `pkill -f "hyperframes[ ]preview" || true` (the bracket keeps the pattern from
   matching your own shell's command line; the unbracketed form **kills the shell
   that runs it**, exit 144, before the render starts). Then:
   ```bash
   npm run render
   python3 ../../render-qa/verify_render.py .   # container truth + presence v2 + per-scene frame dump → qa/frames/
   ```
   `verify_render.py` must exit 0 before anything else sees the cut; it also
   writes the shared frame evidence (`qa/frames/`, 3 stills per scene) that the
   `/adversarial-qa` lanes and the human gate review — nobody re-extracts
   frames. Eyeball a few frames yourself, rename the MP4 to the script's stem,
   move it next to its script in `../lesson-scripts/<program-slug>/`.
8. **Archive the workspace:** once the MP4 is filed (and, for queue videos, the
   Notion row is Delivered), run `bash scripts/archive-lesson.sh <script-stem>`
   from the repo root. It moves `renders-hyperframes/<stem>/` to `renders-hyperframes/_archive/<stem>/`
   pruned of caches — re-renderable later, invisible to git (all of `renders-hyperframes/`
   is gitignored; see `../renders-hyperframes/README.md`).

Edits later cost one scene, not a full re-render: change the sub-comp or its
variables, re-check, re-render.

## Narration voice — decided 2026-07-07

**Kokoro `af_heart` @ 0.95 speed** (local engine, no credits, no API key).
Chosen against `af_nova`, `af_sky`, `am_adam` — samples in `voice-auditions/`.
Warm American female read; keeps voice continuity with the HeyGen avatar
presenter ("Ann") used by `../avatar-pipeline/`.

**Upgrade path:** the HeyGen API key currently returns 403 on every endpoint
(no API permission on the space — also blocks `../avatar-pipeline/`). Once fixed
(`npx hyperframes auth login`, or a key with API access), audition HeyGen
starfish voices (`node .claude/skills/hyperframes-media/scripts/heygen-tts.mjs --list`)
and update `frame.md` → `voice:` in one place. HeyGen TTS also returns native
word timestamps, which removes the transcribe step above.

## Rules

- **The frame never sits still.** No stagnant slide beyond ~2s; enumerations reveal
  on the spoken cue; illustrate what's said, don't just label it; statements aren't
  quotes; the scene index stays small in the lower-right. Full spec + the failures
  that motivated these: `frame.md` → "Every scene earns its seconds", "Illustration
  over text", "Scene index & numerals".
- **Cuts follow the transcript.** Sentence-aligned boundaries, ≥0.5s of air after
  the last word, questions keep their inflection, and the video ends on a populated
  final scene that outlives the audio — never a bare frame. Spec: `frame.md` →
  "Scene boundaries, padding & endings".
- **Motion comes from the rotation.** Before building any bespoke effect, pick
  recipes from `frame.md` → "Motion rotation" (named rules/blueprints in
  `.agents/skills/` + registry blocks) and vary reveal forms between consecutive
  list scenes. A twice-used bespoke scene becomes a template here.
- **The builder never grades its own cut.** `/adversarial-qa` runs four
  independent reviewer lanes (Timing, Layout, Facts, Presence) — plan audit
  before render, full gauntlet on every MP4. All four must PASS before the
  human QA gate; any fix + re-render voids all clears.
- Templates are instantiated with variables, never forked. A recurring new need
  = a new `scla-*.html` template here, added to `frame.md`'s table.
- Every template carries the three style packages (`theme` variable:
  `summit`/`horizon`/`cadence`) as CSS-only `data-theme` override blocks —
  timelines stay identical across packages. Full spec: `frame.md` → "Style packages".
- Every timed element: `data-start`, `data-duration`, `data-track-index`,
  `class="clip"`. One paused GSAP timeline per composition on `window.__timelines`.
- Deterministic only — no clocks, no `Math.random`, no `repeat: -1`, no network fetches.
- `<video>`/`<audio>` live at the host root, never inside a sub-comp template.
- Fonts: the `@font-face` block must be **inside** each sub-comp's `<template>`.
- No FERPA/PII in any prompt or composition. Never fabricate SCLA course content.
