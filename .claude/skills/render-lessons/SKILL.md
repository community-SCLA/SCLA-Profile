---
name: render-lessons
description: Build, ship, and publish SCLA lesson videos from refined scripts, in three explicitly separate phases. BUILD drains lesson-scripts/<program-slug>/refined/ into HyperFrames workspaces (one cold subagent per video, ≤3 per session) and STOPS at the HYPERFRAME GATE — a human previews every hyperframe before any MP4 exists. SHIP ("ship <stem>") renders + verifies + files the MP4 locally and STOPS at MP4 REVIEW. PUBLISH ("publish <stem>") uploads the reviewed MP4 to Wistia and closes the books. No automation ever takes a script to an MP4 in one shot, and no MP4 reaches Wistia unwatched. Downstream half of the SCLA lesson pipeline (dispatcher: /produce-video; upstream: /refine-scripts).
---

# render-lessons — refined script → hyperframe → (gate) → MP4 → (review) → Wistia

**This file owns the build/ship/publish sequence and every command.** The
design contract (tokens, animacy rules, anchor/timing contract, templates,
style packages) is `projects/video-production/design-system/frame.md` — the
build subagent reads it while assembling; nothing from it is restated here.

**TWO HUMAN CHECKPOINTS, both blocking, both explicit:**

1. **HYPERFRAME GATE** — a human previews every built hyperframe before it may
   become an MP4. Hyperframe → MP4 is a manual human decision, never automated.
2. **MP4 REVIEW** — a human watches every filed MP4 before it may go to Wistia.

`refined/` is your finalize-before-build buffer — it holds only scripts not
yet built (edit or veto any of them there, any time *before* you invoke
BUILD). The moment a build is gate-clean, its script moves `refined/ →
rendered/` (B3), so `refined/` always shows exactly what's left to build and
parallel BUILD sessions see a shrinking queue; the human hyperframe gate then
reviews the built workspace, not the script. Everything else between the
checkpoints is machine work behind deterministic gates. BUILD may not render;
SHIP may not run without the human naming the stem after the preview; PUBLISH
may not run without the human naming the stem after watching the MP4. Never
self-approve. Never fabricate SCLA content; no FERPA/PII in any prompt.

**State is the folder:**

```
lesson-scripts/<program-slug>/refined/   BUILD's queue — scripts not yet built
                                         (refined/avatar/ is the HeyGen avatar
                                         queue — NOT built here; see B1)
renders-hyperframes/<stem>/              built — sitting at the HYPERFRAME GATE
lesson-scripts/<program-slug>/rendered/  its script, moved here once the build is gate-clean (B3)
renders-mp4/<program-slug>/hyperframes/<stem>.mp4   shipped — sitting at MP4 REVIEW
```

(`rendered/` means "a gate-clean build exists for this script," not
"published." Publishing to Wistia closes the books but no longer moves the
file — B3 already did.)

---

## Phase BUILD (default) — drain `refined/` into workspaces, then stop

### B0 — Environment preflight (orchestrator, once per session)

```bash
date +%Y-%m-%d                                       # render-date stems
pkill -f "hyperframes[ ]preview" 2>/dev/null || true # keep the bracket — unbracketed kills its own shell (exit 144)
grep /dev/shm /proc/mounts                           # need >=256M for headless Chrome
```

- `/dev/shm` under ~256M → `sudo mount -o remount,size=512M /dev/shm` (64M
  hangs Chrome mid-render; the devcontainer remount can fail silently).
- CLI pin: `design-system/package.json` pins hyperframes **0.7.45+** — never
  older (≤0.7.44 silently renders template defaults, upstream #2064).
- If `npx hyperframes tts` fails on a missing `kokoro_onnx`, set
  `HYPERFRAMES_PYTHON` to an interpreter that has it (`findPython()` respects it).
- **Snag memory: read ONLY the latest entry** of
  `projects/video-production/render-qa/snag-log.md` (the first `## ` entry —
  use Read with a line limit; never load the whole file). Its **Open** list
  rolls forward until fixed — carry it into every build-subagent prompt and
  into your close-out.

### B1 — Queue and batch

- Queue = every `*.txt` at the **`refined/` root only** — NOT the
  `refined/avatar/` subfolder, which is the HeyGen avatar-render queue
  (`avatar-pipeline/`) and must never become a HyperFrames build (that would
  double-render one lesson two ways). Use a non-recursive list (`ls
  …/refined/*.txt`), not a recursive `find`. A
  gate-clean build moves its script out to `rendered/` (B3), so `refined/`
  already holds only un-built scripts. The workspace check stays as a guard:
  if a stem still in `refined/` somehow already has a
  `renders-hyperframes/<stem>/` workspace, it's built and waiting at the gate —
  skip it (never rebuild one without being asked; point the human at its
  preview instead). This is also what makes parallel BUILD sessions safe —
  neither rebuilds a stem that already has a workspace.
- **Batch cap: ≤3 builds per session.** One build costs ~150–300 tool calls in
  its subagent; the per-session budget is 500 (`hooks/pre-tool.sh`). Each
  subagent carries its own context and budget — that's why builds are
  delegated, not run inline. More queued than 3 → say so and leave the rest
  for the next run.
- Style package: the human's pick if given; otherwise rotate
  summit → horizon → cadence by the program's **started-build** count —
  `count(*.txt in lesson-scripts/<program-slug>/rendered/) mod 3` (rule:
  `frame.md` → "Style packages"). Never scan `_archive/` for this — `rendered/`
  already holds every gate-clean build's script, so it covers delivered +
  at-gate builds. The orchestrator computes the theme per queued video
  (consecutive builds in one batch keep rotating) and passes it to the subagent.
  Say which was picked.

### B2 — One cold build subagent per video

Dispatch a general-purpose subagent per script (sequentially — they share the
toolchain and `/dev/shm`). Strong model for bespoke/illustration-heavy lessons;
a routine template instantiation runs fine one tier down. The prompt carries
**paths + facts, never file bodies** (except the snag block):

- the stem, the refined script path, the workspace parent
  `projects/video-production/renders-hyperframes/`, and the assigned theme;
- the **Open + rules block from the latest snag-log entry**, pasted verbatim;
- "Follow the **Build sequence** section of
  `.claude/skills/render-lessons/SKILL.md` exactly. Read `frame.md` before
  assembling. Loop until compile, preflight, and check are all green. Do NOT
  run `npm run render`. Report: workspace path, scene count, theme, anchor
  summary, gate outputs."

### Build sequence (the subagent reads this section)

```bash
cd projects/video-production/renders-hyperframes
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <stem> --example=blank --non-interactive
# copy frame.md, compositions/, assets/ in from ../design-system/
cd <stem>
# init regenerates a CLAUDE.md routing to skills this repo deleted — replace it:
printf '# Build workspace. Sequence + commands: /render-lessons. Design contract: ../../design-system/frame.md\n' > CLAUDE.md
```

**Assemble `index.html` FIRST** — one scene slot per beat from the design-system
templates (pattern: the **newest lesson build**, not the demo reel — its
header comment says so), `<audio>` at the host root. Follow `frame.md`'s
animacy + illustration rules. Standing landmines:

- **Add the host-root progress rail to every build** (`frame.md` → "Host-root
  progress rail"). Inside `#root`, after the scene clips and before the `<audio>`,
  add `#hf-rail-track` + `#hf-rail-fill`; drive it from the root `"main"` timeline
  (`scaleX 0→1`, `duration` = the compiler-owned `#root data-duration`, `ease:"none"`).
  It is not a scene clip, so it stays out of scene coverage and the gates ignore it.
- **Never type a timing number.** Every scene slot carries
  `data-narration="<its verbatim span of the refined script>"` (HTML-escape
  inner double quotes as `&quot;`; split only at sentence ends) and, where it
  has reveals, `data-cue-anchors='{"chipCues":[…],…}'`; placeholder numbers
  everywhere — the compiler owns them. `data-anchor-end` is legacy-only: the
  per-scene manifest owns boundaries now; do not author it on new builds.
- Whisper emits em-dash compounds as ONE token (`buzzwords—just`): a CUE
  phrase can't start or end *inside* one — quote the compound verbatim from
  the transcript or pick a phrase that clears it.
- Idle pulses: translate-only (the y-nudge pattern). Animating `scale` + SVG
  `opacity` together ghosts in the streaming encode.
- Never qualify a bespoke sub-comp root by its own class/attribute (e.g. a
  `#root.navy` selector): it renders unstyled under composition scoping even
  though it passes every static check. Style bespoke roots with a plain
  `#root` block or a child wrapper. (Promoted 2026-07-14; landed 2026-07-15.)

**Synthesize per scene, then compile + gates** (from the workspace — loop
until all green). `synth_narration.py` verifies data-narration against the
refined script BEFORE any TTS, synthesizes one Kokoro clip per scene (cached —
edits only re-synthesize changed scenes), and concatenates with REAL boundary
silence; never hand-run single-take `hyperframes tts` for a lesson (the
old insert-silence flow spliced words — decisions/log.md 2026-07-14):

```bash
python3 ../../render-qa/synth_narration.py .           # per-scene TTS -> narration.wav + scene-times.json
npx hyperframes transcribe assets/voice/narration.wav --model small.en  # cues + script gate still read Whisper
python3 ../../render-qa/compile_timeline.py . --apply  # owns ALL numbers (boundaries from the manifest)
python3 ../../render-qa/preflight.py .                 # incl. script-vs-transcript diff — exit 0 or fix
npm run check                                          # lint + validate + inspect
```

Edited a scene's narration or reordered scenes? Re-run the same four commands
in order — synth re-does only the changed clips, and a stale transcript fails
loudly instead of misaligning.

An unresolvable anchor error names the scene and transcript window — fix the
phrase, never the numbers. **Stop here. No render in this phase.**

### B3 — Verify + present the gate (orchestrator)

For each returned workspace, independently re-run the deterministic gate —
trust exit codes you produced, not subagent prose:

```bash
python3 projects/video-production/render-qa/preflight.py projects/video-production/renders-hyperframes/<stem>
```

**Once your independent preflight exits 0**, the build is gate-clean and the
script has done its job in the queue — move it out so `refined/` shows only
what's left to build (do this only after exit 0; a failed build leaves the
script in `refined/`):

```bash
git mv projects/video-production/lesson-scripts/<program-slug>/refined/<stem>.txt \
       projects/video-production/lesson-scripts/<program-slug>/rendered/<stem>.txt
```

Then **stop and hand the human the gate**, per video: stem, theme, scene
count, and how to watch it. **Never print `<stem>` as a placeholder** — give
the literal, copy-pasteable command with that video's actual stem filled in,
one fenced command per video built this session (even when there's only one):

```bash
bash scripts/preview.sh career-building-is-a-repeatable-process_early-career-boost_2026-07-10
```

```bash
bash scripts/preview.sh what-makes-for-a-dream-job_early-career-boost_2026-07-10
```

State plainly: "Built and gate-clean. Nothing renders until you approve —
reply `ship <stem>` (or ask for changes)." Session may end here; the
workspace *is* the pending state.

---

## Phase SHIP — only after the human approves a previewed hyperframe

Trigger: the human explicitly names the stem after reviewing the preview
("ship X", "approved, render X"). Approval of one stem covers only that stem.

```bash
pkill -f "hyperframes[ ]preview" 2>/dev/null || true   # previews contaminate renders
cd projects/video-production/renders-hyperframes/<stem>
npm run render                                          # ~7 min — background it
python3 ../../render-qa/verify_render.py .              # container truth + presence v2 + qa/frames/ dump — exit 0 or fix + re-render
```

**Frame self-review:** inspect `qa/frames/` (3 per scene) against the
transcript — reveals land on their words, every frame depicts its sentence,
nothing clipped or off-brand. If your context is already heavy, delegate this
to one vision-capable subagent (paths only: `qa/frames/`, `transcript.json`).
Escalation only: `/adversarial-qa` when a cut resists diagnosis or the human
asks to break it.

**File it, then stop:** rename the MP4 to the **script stem with the date
swapped to the render date** — convention-agnostic, so `m1_<title>_<render-date>`
for the newer scheme or `<section>_<program-slug>_<render-date>` for the older —
and move it to `../renders-mp4/<program-slug>/hyperframes/` (the illustrated
subfolder; the avatar path files to `…/<program-slug>/avatar/`) with its QA
packet (verify summary + `qa/frames/`); fill the ledger row's Rendered date + location.
**→ MP4 REVIEW:** hand the human the MP4 path, a few key frames, and the
verify summary (`script-templates/qa-checklist.md`, illustrated section, is
the watch guide). The workspace stays live until PUBLISH — a rejection here
means fix → re-render → re-verify, not a rebuild from scratch.

## Phase PUBLISH — only after the human has watched the filed MP4

Trigger: the human explicitly names the stem after MP4 review ("publish X").

1. Upload the MP4 to Wistia — account, upload mechanics, and auth status live
   in root `endpoints.md` → "Wistia" (title = the filed stem; the `.mp4` is
   never committed). While Wistia has no wired API token, the upload itself is
   the human's move in the web UI — stage everything, then ask for the URL back.
2. Record the Wistia URL in the ledger row (`refinement-log.md`). (Where the
   URL additionally lands in Notion is an open decision, 2026-07-13 — until
   settled, the ledger row is the link's home.)
3. The script already moved `refined/ → rendered/` at the hyperframe gate (B3),
   so no move here — just confirm it's in `rendered/`. The lesson is now done.
4. `cd <repo-root> && bash scripts/archive-lesson.sh <stem>` (refuses if the
   MP4 isn't filed).

## Close-out — the self-improvement loop (every session, both phases)

Append a **new entry at the top** of `render-qa/snag-log.md` following the
rules in its header: new snags tagged `[env]/[tooling]/[authoring]/[upstream]/[defect]`
with resolution + time cost, **Open items carried forward verbatim from the
previous entry until actually fixed**, and durable lessons promoted into the
owning doc (this SKILL, `frame.md`, or preflight/verify checks) in the same
session — the doc is the memory, the log is the trail. **Open items are
owner-actionable by definition** — anything you could fix yourself (code,
config, a retry, filing an upstream bug), fix this session; never roll
agent-fixable work forward. **If the new entry's Open list is non-empty, ASK
the human directly at close-out to resolve each item** (AskUserQuestion when
the session is interactive) — do not just file them in the log for the human to
find. File any new HyperFrames bug upstream before ending (hyperframes#2064 is
the model repro). Report per
video: stem, theme, phase reached, gate outcomes, Wistia URL (or pending).
