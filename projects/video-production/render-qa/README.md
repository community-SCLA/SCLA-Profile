# render-qa/ — the deterministic toolchain for illustrated lesson videos

*Owner's manual for the whole SCLA lesson-video pipeline, and the tool
reference for this folder — the single place that narrates the flow. It
explains the system; it does not govern it. The skills
(`.claude/skills/render-lessons`, `refine-scripts`, `produce-video`), the
rules (`.claude/rules/video-production.md`), and the checkers under
`render-qa/` govern — if this manual ever disagrees with them, they win and
this file needs a fix.*

**Why these tools exist:** the first at-scale builds hand-typed scene
boundaries and cue times, reconciled against the narration *after* the
fact — 26 boundary violations, mid-word cuts, 14 cue-phrase mismatches. The
inversion: **authors declare text (per-scene narration spans + cue phrases);
these tools compute every number.** Used by `/render-lessons` (BUILD gates +
SHIP verify) and `/adversarial-qa`; the authoring contract lives in
`design-system/docs/design-contract.md`.

**Folder shape:** `src/` tool code · `tests/` the suite that pins it ·
`docs/` handoffs and working notes · `logs/` the rolling snag-log and rotated
archives. Pipeline-structure decisions land in `decisions/log.md`, not here.

**Fragile point:** tool paths are derived from `__file__` positionally —
`src/` → `render-qa/` → `video-production/` is `parents[2]`, repo root is
`parents[4]`. Moving a `.py` between directory levels silently breaks every
relative lookup (design-system, lesson-scripts, the skills dir) with no
syntax error. If you move one, re-derive its `parents[n]` and run
`tests/run_tests.py`.

## 1. The pipeline, end to end

### 1.1 The idea in one paragraph

Agent judgment is confined to exactly two artifacts: the **refined script**
(what is said) and the **`scenes.json` plan** (what is shown — beats, template
per beat, on-frame copy, cue anchor phrases, icons). Everything else is
compiled or gated by machines: a compiler emits the HTML, a compiler owns every
timing number, checkers enforce your standing preferences at the moment the
plan is written, snapshots are vision-reviewed *before* a render is spent, and
a verifier hashes what actually rendered before anything is published. **State
is the folder** — a script's location *is* its stage; no database tracks it,
no hook moves it, every transition is a `git mv` performed by a named script,
and every "where is everything?" question is answered by reading the folders
back off disk. You stand at **one gate**: previewing a batch's pilot.
Everything downstream of your approval is exit codes.

### 1.2 The whole flow

```
                        THE MACHINE                                   YOU
  ┌─────────────────────────────────────────────────────┐   ┌──────────────────┐
  │                                                     │   │                  │
  │  RAW script (.txt)                                  │   │  drop scripts in │
  │  lesson-scripts/<program>/inbox/      ◄─────────────┼───┤  inbox/;         │
  │        │                                            │   │  edit any time   │
  │        ▼  /refine-scripts  (qa-facts pass — no      │   │                  │
  │        │                    fabrication survives)   │   │                  │
  │  READY script                                       │   │  open review     │
  │  lesson-scripts/<program>/ready/      ◄─────────────┼───┤  buffer: edit or │
  │        │   ── the script STAYS here through build,  │   │  veto any script │
  │        │      gate, render and verify ──            │   │  before build    │
  │        ▼  /render-lessons BUILD  (cold subagent)    │   │                  │
  │        │                                            │   │                  │
  │   ┌────┴──────────── the authoring loop ─────────┐  │   │                  │
  │   │  agent authors scenes.json   [ONLY judgment] │  │   │                  │
  │   │      │                ▲                      │  │   │                  │
  │   │      ▼                │ fix plan (seconds)   │  │   │                  │
  │   │  build_index.py ──► index.html  [COMPILED]   │  │   │                  │
  │   │  preflight --static  [GATES: variety, copy,  │  │   │                  │
  │   │      │                slots, text, geometry] │  │   │                  │
  │   └──────┼── exit 0 ──────────────────────────────┘ │   │                  │
  │          ▼                                          │   │                  │
  │   synth_narration.py    [HeyGen TTS, cached,        │   │                  │
  │          │               silence-capped]            │   │                  │
  │   compile_timeline.py   [owns EVERY number]         │   │                  │
  │   preflight.py (full)   [+ script-vs-transcript]    │   │                  │
  │   npm run check         [lint + validate]           │   │                  │
  │          │                                          │   │                  │
  │   batch-precheck.sh     [1 snapshot per scene,      │   │                  │
  │          │               blank-scene flags,         │   │                  │
  │          │               vision review of pixels    │   │                  │
  │          │               — BEFORE the render spend] │   │                  │
  │          ▼                                          │   │                  │
  │  built workspace                                    │   │ ★ PILOT GATE ★   │
  │  renders-hyperframes/<base>/  ══════════════════════╪═══╡ review.sh, then  │
  │          │      (mkdir <base> IS the build lock)    │   │ "ship <stem>"    │
  │          │  "ship <stem>" unlocks ▼                 │   │ (one approval    │
  │          ▼                                          │   │  covers the      │
  │   batch-ship.sh: render (~7 min) ─► verify_render   │   │  whole batch)    │
  │          │        [duration ±0.15s, 1920×1080,      │   │                  │
  │          │         presence check, sha-256 marker]  │   │                  │
  │          ▼        ─► encode spot-check (vision)     │   │                  │
  │   --publish: file MP4 ─► Wistia upload ─►           │   │                  │
  │   published.tsv row + ledger row ─► script moves    │   │                  │
  │   ready/ → published/ ─► commit ─► prune workspace  │   │  Wistia URL      │
  │          │        ── ALL of it in one pass ──       │   │  reported to you │
  │          ▼                                          │   │  as confirmation │
  │   next video in the queue (fail = quarantine that   │   │                  │
  │   ONE video; the batch never stops for it)          │   │                  │
  └─────────────────────────────────────────────────────┘   └──────────────────┘
```

**Only two things ever move a script, and each move renames its stage.**
`/refine-scripts` moves it `inbox/` → `ready/`. `batch-ship.sh --publish` moves
it `ready/` → `published/`, in the same commit that records the Wistia URL.
Nothing else — not building, not gating, not rendering, not verifying. (Changed
2026-07-28: a gate-clean build used to move its own script. Moving at publish is
what makes `published/` without a `published.tsv` row a *detectable* state — see
STRANDED in §1.6. The folders were renamed to match on 2026-08-04, when
`rendered/` had been meaning *published* for a week.)

### 1.3 What you invoke, and when

| You want | You say / run |
|---|---|
| A video (or many) produced end to end | `/produce-video` — refines whatever is raw, builds, stops at the pilot gate |
| Just refine raw scripts | `/refine-scripts` — drains `inbox/` into `ready/` |
| Just build from ready scripts | `/render-lessons` — BUILD is the default; a queue >1 runs AUTO-BATCH (pilot first) |
| **See what's ready to watch** | `bash scripts/review.sh` — gates every build and opens a preview only for the clean ones |
| Preview one specific build | `bash scripts/preview.sh <stem>` |
| Approve the pilot / a one-off | watch it, then reply **`ship <stem>`** |
| See what's outstanding | `bash scripts/batch-status.sh` |
| Resume an interrupted batch | `bash scripts/batch-status.sh` — then tell the agent to continue; state is on disk, no session memory needed |
| Deep-audit a suspicious cut | `/adversarial-qa` (escalation only — not part of the normal run) |
| Retire a shipped workspace to `_archive/` | your call only, `bash scripts/archive-lesson.sh <stem>` — never automated |

**Your two writing surfaces:** drop raw scripts at
`lesson-scripts/<program-slug>/` root (intake), and edit/veto anything in
`ready/` any time before it builds (the open review buffer). Nothing else in
the pipeline is hand-edited — `index.html` is a build artifact, timing numbers
are compiler-owned, and a preference you state becomes a checker, not a memo.

**Batching, plainly**

| Command | Drains | Where it stops |
|---|---|---|
| `/produce-video` | Everything: refines, then builds | At the pilot gate |
| `/refine-scripts` | Every raw script in every program | Doesn't stop — never renders, never asks |
| `/render-lessons` AUTO-BATCH | The whole queue, program by program, build → render → verify → publish | **Once**, on the pilot. Then unattended to Wistia |
| `/render-lessons` BUILD | Builds workspaces for the whole queue | Before any render — every video waits at the gate |
| `ship <stem>` | One approved video, all the way to Wistia | Doesn't stop — the approval *was* the gate |

Drain order defaults to `early-career-boost` → `mid-career-momentum` →
`career-transitions` → `entrepreneur-accelerator`, so an interrupted run leaves
the highest-value programs already live. Override with `VIDEO_PRIORITY`.
No batch cap: the queue is the batch. Up to 3 builds run concurrently
(network-bound); renders are serialised one at a time by `.render.lock`
(CPU-bound).

### 1.4 Your gates — exactly one, plus one standing right

- **★ PILOT GATE (blocking).** A batch builds ONE pilot, stops, and you
  preview it. `ship <stem>` authorizes the *entire batch* — every remaining
  video then runs build → precheck → render → verify → publish unattended,
  each protected by the mechanized guards below. A failing pilot stops the run.
  For a single one-off video, the pilot *is* that video.
- **Standing right, not a gate:** `ready/` is yours to edit or veto at any
  moment before build. After your pilot approval there is no second look —
  that's deliberate (the per-video human eye was replaced 2026-07-28 by the
  guard chain below, `decisions/log.md`).

### 1.5 What protects every video when you're not looking

Every unresolvable cue phrase, script/narration mismatch, or count mismatch is
a **fatal, named error before render time** — the same defects used to surface
as QA findings on a finished MP4 (or not at all). If `--apply` fails, nothing
is written to `index.html`. If a scene's narration text changes,
`synth_narration.py` re-synthesizes that clip only, and the deleted stale
transcript forces the re-transcribe step.

Any one of the following failing **quarantines that video** (built,
unpublished, logged in `render-qa/quarantine.log`) and the batch moves on:

1. `preflight.py` exit 0 before render — script-vs-transcript diff, coverage,
   pacing, text floors, title card, variety, copy, geometry, stem, silence caps.
2. `batch-precheck.sh` before render — re-runs preflight itself (subagent
   claims are never trusted), snapshots every scene, flags blank scenes
   deterministically, and a vision subagent reviews the real pixels.
3. `verify_render.py` after render — stream durations vs declared ±0.15s,
   exact 1920×1080, presence/stagnation check, then writes the sha-256
   `qa/VERIFIED` marker naming the exact MP4.
4. Publish refuses to run without a fresh `VERIFIED` marker, re-hashes the
   MP4 against it, and refuses any stem already in `published.tsv` — so
   re-running is always safe, and nothing ships twice.
5. Your taste, mechanized: Title Case headings, no one-item lists, "and/or"
   before final list items, max 2 consecutive same-template scenes, ≥6 content
   forms, no form >40%, artwork coverage, canvas-monotony cap, two-region
   minimum — all calibrated against your reference video
   (`what-makes-for-a-dream-job`), and the calibration itself is pinned by
   tests: **a gate that rejects the reference is a broken gate.**

### 1.6 Where things live (state IS the folder — nothing narrates it)

```
lesson-scripts/<program>/inbox/       RAW — captured, waiting to be refined
lesson-scripts/<program>/ready/       READY — YOUR review buffer, BUILD's queue
renders-hyperframes/<base>/           BUILDING → NEEDS REVIEW → RENDERED
lesson-scripts/<program>/published/   PUBLISHED — live on Wistia, moved at publish
renders-mp4/<program>/                delivered MP4s (gitignored; kept after upload)
lesson-scripts/published.tsv          THE machine truth: a stem is done iff it has a row
lesson-scripts/refinement-log.md      your human-facing ledger (Wistia URLs)
render-qa/quarantine.log              videos a guard pulled out of a batch
render-qa/logs/snag-log.md            latest entry only: session trail + your open items
```

**A workspace folder only proves a build was *started*.** `batch-status.sh`
probes the files inside it and reports which of five stages it actually
reached — cheap probes, no browser, no gate run:

| Stage key | Reported state | What it means |
|---|---|---|
| `no-plan` | build folder exists but holds no scene plan | Folder claimed, nothing authored yet |
| `planned` | scene plan written; narration not yet synthesized | `scenes.json` exists, no narration audio |
| `uncompiled` / `untimed` | never compiled / timings never applied | Audio exists, the composition is not renderable |
| `composition` | HyperFrames composition ready to render; no MP4 exists yet | Ready for preflight — this is what "at the gate" looks like |
| `verified` | MP4 rendered and gate-verified — waiting only on the Wistia upload | Only the upload is left |
| `quarantined` | a release gate rejected this cut | A guard said no; the workspace keeps `qa/quarantine-reason.txt`, the guard's own transcript |

The stage key is what `--json` emits and what the generated `PIPELINE-STATUS.md`
groups its headings by, so the two questions a human actually asks — *which of
these are compositions still waiting to become MP4s, and which are MP4s waiting
to be published* — are answered by the heading, not by decoding a state string
(2026-07-31).

(Added 2026-07-29, after 12 of 13 lessons the tool was calling "built" turned
out to have never had `compile_timeline.py --apply` run against them. Rebuilding
one of those discards valid narration audio, so the distinction is worth money.)

**"What's outstanding?" = `bash scripts/batch-status.sh`.** It rebuilds the
queue in priority order from the folders + tsv + quarantine log alone, into five
buckets:

- **to build** — in `ready/`, no workspace yet
- **built-unpublished** — workspace exists, annotated with the stage above
- **STRANDED** — in `published/` with no `published.tsv` row: upload or
  commit did not complete. This bucket is the whole reason the script moves at
  publish rather than at build.
- **blocked** — the script body still contains `TODO: needs input` or
  `SCRIPT PENDING`. Read from the text, not a hand-kept list, so fixing the
  script re-enters it in the queue with no bookkeeping. The marker's whole
  paragraph is reported, because the script always says *which* input it needs
  and echoing the marker word alone threw that away (2026-07-31).
- **already on Wistia** — has a `published.tsv` row. Done, by definition.

**"What do I need to watch?" = `bash scripts/review.sh`.** It runs the
deterministic gate over every build in `renders-hyperframes/` (~0.4s each),
starts a preview server for each gate-clean one with a clickable link, and
lists everything else as "not ready" so you know to skip it. Anything needing
*your* eyes on a decision instead lives in the snag log's latest **Open** list,
and the session is required to ask you about those directly at close-out —
you should never have to go dig.

**Naming: a working artifact carries no date.** A lesson's identity is
`<title>_<program>` — the **base** — and that one name is the `inbox/` script,
the `ready/` script, the build workspace, and the `published/` script. The only artifact
that gains a date is the delivered MP4 (`<base>_<render-date>.mp4`), frozen at
publish because it records an event that happened once. "When was this last
acted on" is mtime, which the filesystem tracks natively and cannot drift.
`render-qa/src/stem.py` owns the rule; nothing hand-slices a suffix.

This replaced the restamp rule on 2026-07-29, and the reason is mechanical
rather than cosmetic: **a moving name cannot be a lock.** `mkdir
renders-hyperframes/<base>` succeeds exactly once, which is what stops two
concurrent build subagents colliding on one lesson — but only while the name
holds still. Under the old rule a rebuild restamped its way into a *second*
workspace, leaving one lesson holding both `..._2026-07-28` and
`..._2026-07-29`.

### 1.7 Two lanes through the same folders

Same stems, same locks, same state model — different authoring method and a
different gate policy.

| Lane | How it's authored | Gate policy |
|---|---|---|
| **Illustrated · template** (default) | Author `scenes.json`; `build_index.py` compiles the HTML and the compiler owns every timing | Eligible for AUTO-BATCH — one pilot approval covers the queue |
| **Illustrated · freeform** (`--freeform`, opt-in) | No templates, no `scenes.json`, no compiler — the HTML is the authored artifact. Narration-first: audio is frozen before a pixel is placed | **Never enters AUTO-BATCH.** Every video stops for its own preview while the quality floor is unproven |

The talking-head lane that used to be a third row here — `avatar/` and
`refined/avatar/`, rendered by hand through the HeyGen web UI — was **deleted
2026-08-04**. It had one script in it, which was requeued as illustrated. Every
lesson in this tree is illustrated now, which is why `ready/` has no subfolders
and there is no render route to infer from a location.

Freeform's reference build — a visual bar plus a working example of every
artifact — is `experiments/agent-native-m2/`; read its `design.md` and
`PROVENANCE.md`, never copy its compositions. The measured per-module verdict on
adopting it more widely is `render-qa/docs/HANDOFF-agent-native-verdict-2026-07-30.md`.

### 1.8 Capabilities and costs, plainly

- **Batch scale:** yes — invoke on a whole queue (`/produce-video` or
  `/render-lessons`). AUTO-BATCH drains program by program in priority order,
  one pilot approval total, each video published and committed before the next
  starts, so an interruption strands nothing. No batch cap.
- **Cheap failure:** a variety/copy mistake now costs a 30-line JSON edit
  caught in milliseconds — not a re-authored video (minutes), a re-synth
  (TTS credits), or a re-render (7 minutes). Gates fire on every save of
  `scenes.json` via a hook; the agent literally cannot write a bad plan
  without being told immediately.
- **TTS spend** happens once per changed scene (per-scene cache); the voice is
  pinned (Oxana) with no fallback — a credential failure stops loudly rather
  than shipping a wrong voice.
- **Render spend** is ~7 min/video, only after pixels were already reviewed.
- **Changing the system:** state a preference once and it must land as a
  checker (or be honestly labeled a Convention) — that's enforced by CI
  (`check-enforcement.py`): a doc cannot *claim* a mechanism that doesn't
  exist. Prose can't guard your pipeline; it also can't lie about guarding it.

### 1.9 Known drift (open, 2026-07-30)

Found while tracing the flow for the 2026-07-30 rewrite. The mechanisms are
correct; two pieces of prose around them are not.

**Both were fixed on 2026-08-04, and both fixes were mechanisms rather than
corrected prose.** Kept here because the *shape* of these two defects is worth
recognizing again.

1. **A folder whose name lied.** `render-lessons/SKILL.md` said in one place
   that a gate-clean build moves its own script to `rendered/`, and in another
   that publish does — because `rendered/` had silently come to mean
   *published* on 2026-07-28. One stale name produced four disagreeing status
   narratives. Fixed by renaming the folders to the stage names they actually
   carry: `inbox/` → `ready/` → `published/`.
2. **A count read from the wrong folder.** Style packages rotated summit →
   horizon → cadence on `count(*.txt in rendered/) mod 3`, described in the text
   as the *started-build* count. Once the move went to publish-time, that folder
   held only published scripts — mid-career-momentum's 14 built videos counted
   as zero, and every fresh batch there restarted at `summit`. Fixed by moving
   the rule out of prose entirely: `render-qa/src/theme_for.py <program>` is now
   the only thing that answers it, counting the union of `published.tsv` rows
   and live workspaces. Prose that restates a computation will drift from it;
   prose that cites a script cannot.

### 1.10 Last known state (as of 2026-07-31)

From `bash scripts/batch-status.sh`. Re-run that command for the live count, or
read the generated `projects/video-production/PIPELINE-STATUS.md`, which every
quarantine and every publish rewrites — this table is a snapshot, not a tracked
value.

| Bucket | Count |
|---|---|
| To build | 20 |
| Built — composition only, no MP4 yet | 13 (all `mid-career-momentum`) |
| MP4 rendered and verified, awaiting publish | 0 |
| Quarantined | 1 (`build-direction-before-you-build-a-plan`, three static spans) |
| Stranded | 0 |
| Blocked | 2 (mid-career-momentum scripts carrying `TODO: needs input`) |
| Live on Wistia | 2 |

The 13 composition-only builds are waiting at the gate — `bash
scripts/review.sh` will preflight them and open the clean ones.

## 2. The render-qa/ toolchain, in detail

**2026-07-14 — per-scene synthesis replaced the single-take + inserted-silence
flow.** The old flow synthesized the whole script as one Kokoro take (natural
sentence gaps ~0.03s) and spliced digital-zero silence at Whisper-estimated
boundaries; Whisper word timestamps are ±30–100ms (both directions — they also
drift into silence), so splices measurably landed inside voiced audio, cutting
words in half, and re-anchoring after `--apply` left orphaned silences in the
wav. `synth_narration.py` deletes the whole failure class: boundaries are real
silence, known sample-exactly. The legacy path in `compile_timeline.py`
remains only for pre-manifest workspaces.

**2026-07-22 — default TTS provider moved Kokoro → HeyGen starfish.** HeyGen
returns native per-word timestamps with the synthesis, so
`synth_narration.py` writes `assets/voice/narration.words.json` (whole-file
absolute time, already shifted for trim + concat placement) and the separate
`npx hyperframes transcribe` pass is skipped on new builds.
`compile_timeline.py`, `preflight.py`, and `check_boundaries.py` each detect
this file per-workspace and prefer it over `transcript.json` when present —
`--provider kokoro` (manual fallback, no native timestamps) still produces
`transcript.json` via Whisper and is read the old way.

| Tool | When | What it does |
| --- | --- | --- |
| `synth_narration.py <ws> [--provider heygen\|kokoro]` | after assembling `index.html` | Per-scene TTS: verifies every scene's `data-narration` against the approved script (exact token match, BEFORE any TTS), synthesizes one clip per scene (cached by a hash of provider+voice+speed+text — edits re-synthesize only changed scenes; default provider **heygen**, needs `$HEYGEN_API_KEY` — run under `scripts/with-secrets.sh`), trims clip edge silence, **caps IN-SCENE silence at 0.5s** (`--max-gap`; HeyGen's Oxana pauses 0.98–1.26s mid-scene at sentence/clause boundaries, non-deterministically — audio and picture both die there because the cues derive from the same word timestamps, so the excess samples are excised, faded, and subtracted from that clip's later word times; 2026-07-28), concatenates with REAL boundary gaps (0.3s air + 0.15s lead; 0.45s air after questions), writes `narration.wav` + the sample-exact boundary manifest `assets/voice/scene-times.json` + (heygen path) `assets/voice/narration.words.json`, and deletes stale `transcript.json`/a stale words file from a different provider so a forgotten re-transcribe or a leftover words file fails loudly. |
| `compile_timeline.py <ws> --apply` | after synth (+ transcribe on the kokoro path) | Manifest mode (default for new builds): scene boundaries come from `scene-times.json`; cue phrases in `data-cue-anchors` resolve against `narration.words.json` (HeyGen) or the whisper transcript (kokoro), whichever exists, inside each scene's manifest window; writes every `data-start`/`data-duration`, numeric cue, `sceneDuration`, audio + root duration. No silence is ever inserted. Legacy mode (no manifest): `data-anchor-end` anchoring + boundary-silence insertion, kept for old workspaces. Idempotent. `--check` = drift detector (exit 1 on any). |
| `preflight.py <ws> [--script <path>]` | before every render | One-command pre-render gate: compiler drift check + `check_boundaries.py` (independent pacing rules; manifest = ground truth for spoken ends and question flags — transcript word ends can drift into silence) + one-template-file-per-slot (`instance_templates.py --check`) + **compositions/ freshness** (workspace `compositions/*.html` is copied once at init and never refreshed — compares each non-instanced file's `<style>`/`<script>` content against the current `design-system/compositions/` source; a full-file diff would false-positive on every scene because HyperFrames re-serializes HTML on catalog/build, so this hashes just the RAWTEXT blocks that pass through unchanged; instanced clones (`basename__suffix.html`) are skipped — added 2026-07-27, C2) + clip coverage (tile 0→root, no gaps/overlaps) + one-theme-per-video + script fidelity (approved `lesson-scripts/` `.txt` vs `narration.words.json`/whisper transcript, word-level diff — threshold-based because whisper small.en mishears ~1/360 (HeyGen's exact-text words pass well inside the same thresholds): isolated misses PASS with warnings, mismatch rate >2% or ≥4 consecutive missed words FAILs; spelled numbers fold to digits on both sides; script auto-located from the workspace stem or passed via `--script`; missing script = WARN + skip) + **in-scene silence** (no inter-word hole INSIDE a scene above 0.8s; scene-boundary air is excluded via `scene-times.json`, and it reads the whole-file `narration.words.json`, never the per-scene files — those keep the provider's uncompressed pauses. Regression guard for `synth_narration.py`'s 0.5s cap, 2026-07-28). Exit 0 = cleared to render. |
| `check_text.py <ws>` | inside `preflight.py` (section 7); standalone against `design-system/` to grade the templates | Static on-frame TEXT gate. **size:** every `font-size` rule in `<ws>/compositions/*.html` graded against `design-contract.md`'s `typography.min-size` floors — body ≥32px, label ≥20px — with the class read off the typesetting (`text-transform: uppercase` **and** `letter-spacing` = label furniture, everything else = body copy). Opt a rule out with `/* text-floor-exempt: <reason> */` above it (marker numerals sized by their circle). **restate:** FAILs any `subBeats`/point/step/caption/line whose words are a subset of, or ≥80% overlap with, that scene's own `label`/`heading`/`kicker`/`statement` — a second, smaller copy of a line already on the frame at full size. Both owner calls, 2026-07-27. |
| `verify_render.py <ws> [mp4]` | after every render | Container truth (streams/duration/resolution) + presence v2 (blank frames by stddev **and** content pixels, ≥5s stagnation tripwire, audio-vs-video) + writes the shared QA frame evidence: `<ws>/qa/frames/` — 3 full-res stills per scene for the gauntlet lanes and the human gate. Exit 0 before anyone reviews the cut. |
| `hfp_common.py` | library | Transcript loading, normalized duplicate-safe phrase matching (forward pointer, positional), scene-slot parse/rewrite (incl. `data-narration`), apostrophe-safe attribute JSON. |
| `tests/run_tests.py` | after editing any tool | 36 adversarial fixtures: duplicate words, missing/unresolvable anchors, cue-count mismatches, unclaimed transcript tails, question air, legacy padding idempotency, `data-hf-id` parsing trap, apostrophe injection, per-scene synth (clip cache, trim, real-silence gaps, stale-artifact hygiene), manifest-mode compile (boundaries, cue windows, idempotency, count mismatch). Must print `36 passed, 0 failed`. |
| `tests/test_script_match.py` | after editing `preflight.py` | Synthetic fixtures for the script-fidelity gate: clean match, noise-floor mishear (passes with warning), dropped/misread sentence (fails), >2% mismatch rate (fails), dash-compound tokenization, stem-based script location, missing script warn+skip. |

## 3. The authoring contract (normative copy: `design-system/docs/design-contract.md`)

```html
<div … data-narration="Ask where you are hiding somewhere. …"
      data-cue-anchors='{"chipCues":["right job","right major","right city","right path"]}'
      data-start="0" data-duration="1" …>
```

- `data-narration` — the scene's verbatim span of the ready script (split at
  sentence ends; HTML-escape inner double quotes as `&quot;`). The
  concatenation across scenes must equal the script — `synth_narration.py`
  enforces this exactly, before any TTS.
- `data-cue-anchors` — one transcript phrase per cue item, in spoken order.
  On-screen labels may paraphrase; anchors may not. (`subCues` pairs with the
  pipe-separated `subBeats` variable; other cue lists pair comma-separated.)
- `data-anchor-end` — legacy only (pre-manifest workspaces). Never author it
  on a new build.
- Numbers in `data-start`/`data-duration`/cue variables are compiler-owned.
  Hand-editing them is a defect: re-run `--apply`.
