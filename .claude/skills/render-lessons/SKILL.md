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

`refined/` is an open review buffer (a human may edit or veto any script
there, any time — nothing waits on them); everything else between the
checkpoints is machine work behind deterministic gates. BUILD may not render;
SHIP may not run without the human naming the stem after the preview; PUBLISH
may not run without the human naming the stem after watching the MP4. Never
self-approve. Never fabricate SCLA content; no FERPA/PII in any prompt.

**State is the folder:**

```
lesson-scripts/<program-slug>/refined/   BUILD's queue
renders-hyperframes/<stem>/              built — sitting at the HYPERFRAME GATE
renders-mp4/<program-slug>/<stem>.mp4    shipped — sitting at MP4 REVIEW
lesson-scripts/<program-slug>/rendered/  published (MP4 on Wistia, books closed)
```

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

- Queue = every `*.txt` in each `lesson-scripts/<program-slug>/refined/`
  **minus** stems that already have a `renders-hyperframes/<stem>/` workspace
  (those are already built and waiting at the gate — never rebuild one without
  being asked; point the human at its preview instead).
- **Batch cap: ≤3 builds per session.** One build costs ~150–300 tool calls in
  its subagent; the per-session budget is 500 (`hooks/pre-tool.sh`). Each
  subagent carries its own context and budget — that's why builds are
  delegated, not run inline. More queued than 3 → say so and leave the rest
  for the next run.
- Style package: the human's pick if given; otherwise rotate
  summit → horizon → cadence by the program's **started-build** count (rule +
  count definition: `frame.md` → "Style packages"). The orchestrator computes
  the theme per queued video (consecutive builds in one batch keep rotating)
  and passes it to the subagent. Say which was picked.

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
npx hyperframes tts "$(cat ../../lesson-scripts/<program-slug>/refined/<stem>.txt)" \
  --voice af_heart --speed 0.95 -o assets/voice/narration.wav   # no --provider (removed in 0.7.56)
npx hyperframes transcribe assets/voice/narration.wav --model small.en
```

**Assemble `index.html`** — one scene slot per beat from the nine templates
(pattern: the **newest lesson build**, not the demo reel — its header comment
says so), `<audio>` at the host root. Follow `frame.md`'s animacy +
illustration rules. Standing landmines:

- **Never type a timing number.** `data-anchor-end="<last spoken phrase>"` on
  every scene slot, `data-cue-anchors='{"chipCues":[…],…}'` with **verbatim
  transcript phrases**; placeholder numbers everywhere — the compiler owns them.
- Whisper emits em-dash compounds as ONE token (`buzzwords—just`): an anchor
  phrase can't start or end *inside* one — quote the compound verbatim from
  the transcript or pick a phrase that clears it.
- Idle pulses: translate-only (the y-nudge pattern). Animating `scale` + SVG
  `opacity` together ghosts in the streaming encode.

**Compile + gates** (from the workspace — loop until all three green):

```bash
python3 ../../render-qa/compile_timeline.py . --apply  # owns ALL numbers
python3 ../../render-qa/preflight.py .                 # incl. script-vs-transcript diff — exit 0 or fix
npm run check                                          # lint + validate + inspect
```

An unresolvable anchor error names the scene and transcript window — fix the
phrase, never the numbers. **Stop here. No render in this phase.**

### B3 — Verify + present the gate (orchestrator)

For each returned workspace, independently re-run the deterministic gate —
trust exit codes you produced, not subagent prose:

```bash
python3 projects/video-production/render-qa/preflight.py projects/video-production/renders-hyperframes/<stem>
```

Then **stop and hand the human the gate**, per video: stem, theme, scene
count, and how to watch it —

```bash
cd projects/video-production/renders-hyperframes/<stem> && npm run dev   # background it; long-running
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

**File it, then stop:** rename the MP4 to `<section>_<program-slug>_<render-date>`
and move it to `../renders-mp4/<program-slug>/` with its QA packet (verify
summary + `qa/frames/`); fill the ledger row's Rendered date + location.
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
3. `git mv` the script `refined/` → `rendered/` — the lesson is now done.
4. `cd <repo-root> && bash scripts/archive-lesson.sh <stem>` (refuses if the
   MP4 isn't filed).

## Close-out — the self-improvement loop (every session, both phases)

Append a **new entry at the top** of `render-qa/snag-log.md` following the
rules in its header: new snags tagged `[env]/[tooling]/[authoring]/[upstream]/[defect]`
with resolution + time cost, **Open items carried forward verbatim from the
previous entry until actually fixed**, and durable lessons promoted into the
owning doc (this SKILL, `frame.md`, or preflight/verify checks) in the same
session — the doc is the memory, the log is the trail. **If the new entry's
Open list is non-empty, the close-out report must lead with it** — the human
gets notified every session until each item is fixed. File any new HyperFrames
bug upstream before ending (hyperframes#2064 is the model repro). Report per
video: stem, theme, phase reached, gate outcomes, Wistia URL (or pending).
