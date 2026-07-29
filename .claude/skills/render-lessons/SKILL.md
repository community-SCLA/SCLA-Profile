---
name: render-lessons
description: Build and ship SCLA lesson videos from refined scripts. AUTO-BATCH (default for a queue) builds ONE pilot video, stops for a single human preview, and on approval drains the whole queue in priority order — build → render → verify → publish to Wistia — one cold subagent per video, no batch cap, each video published and committed before the next starts so an interrupted run never strands work. BUILD and SHIP ("ship <stem>") remain for one-off work. Downstream half of the SCLA lesson pipeline (dispatcher: /produce-video; upstream: /refine-scripts).
---

# render-lessons — refined script → hyperframe → (gate) → MP4 → (review) → Wistia

**This file owns the build/ship/publish sequence and every command.** The
design contract (tokens, animacy rules, anchor/timing contract, templates,
style packages) is `projects/video-production/design-system/frame.md` — the
build subagent reads it while assembling; nothing from it is restated here.

**ONE HUMAN CHECKPOINT, blocking, explicit:**

1. **PILOT GATE** — a batch builds ONE video, stops, and a human previews it.
   Approval authorizes the entire batch; a failure stops the run. (Changed
   2026-07-28 — this replaced the per-video HYPERFRAME GATE, which required an
   approval per stem and made a 30-video queue impossible to drain. For a
   single one-off video, the pilot *is* that video, so nothing changes.)

`refined/` is your finalize-before-build buffer — it holds only scripts not
yet built (edit or veto any of them there, any time *before* you invoke
BUILD). The moment a build is gate-clean, its script moves `refined/ →
rendered/` (B3), so `refined/` always shows exactly what's left to build and
parallel BUILD sessions see a shrinking queue; the human pilot gate then
reviews a built workspace, not the script. Everything on either side of that
gate is machine work behind deterministic gates: BUILD may not render; a batch
may not proceed past its pilot without the human approving it — but once
granted, each video runs render → verify → file → Wistia upload to completion
with no further human look (MP4 REVIEW gate removed 2026-07-22; per-video
HYPERFRAME GATE replaced by the pilot gate 2026-07-28 — both in
decisions/log.md). From there the quality bar is mechanized: `preflight.py`,
the pre-render `batch-precheck.sh` snapshot review, `verify_render.py`,
`check_presence.py`, and a sampled vision review of `qa/frames/`, any of which
failing quarantines that one video rather than stopping the batch. Never
self-approve the pilot gate.
Never fabricate SCLA content; no FERPA/PII in any prompt.

**State is the folder:**

```
lesson-scripts/<program-slug>/refined/   BUILD's queue — scripts not yet built
                                         (refined/avatar/ is the HeyGen avatar
                                         queue — NOT built here; see B1)
renders-hyperframes/<stem>/              built — sitting at the HYPERFRAME GATE
lesson-scripts/<program-slug>/rendered/  its script, moved here once the build is gate-clean (B3)
renders-mp4/<program-slug>/hyperframes/<stem>.mp4   shipped — filed locally, then published to Wistia in the same pass
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
- CLI pin: `design-system/package.json` pins hyperframes **0.7.79+** — never
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
- **No batch cap — the queue is the batch.** (Removed 2026-07-28: the old
  ≤3-per-session cap justified itself with a 500-tool-call budget in
  `hooks/pre-tool.sh`, and that hook is not armed — `~/.claude/settings.json`
  has no hooks and there is no `budget.json`. It was guarding a limit that
  doesn't exist.) What actually protects the session is **one cold subagent per
  video** — that keeps script bodies and `index.html` out of the orchestrator's
  context — plus the Phase AUTO-BATCH economics below. Both are mandatory; the
  number is not.
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
  `.claude/skills/render-lessons/SKILL.md` exactly. You author `scenes.json`
  only — `index.html` is compiled, never hand-written. Read `frame.md` before
  planning scenes. Loop `build_index.py` + `preflight.py --static` until the
  plan is clean, then synth + compile and loop until full preflight and check
  are green. Do NOT run `npm run render`. Report: workspace path, scene count,
  theme, anchor summary, gate outputs."

### Build sequence (the subagent reads this section)

The workspace is named for the date it is **built**, not the date the script was
refined — one date suffix, always the most recent action (`.claude/rules/
video-production.md`). `render-qa/stem.py` owns the rule; never hand-slice it.

```bash
cd projects/video-production/renders-hyperframes
WS="$(python3 ../render-qa/stem.py restamp <script-stem>)"   # -> title_program_<today>
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init "$WS" --example=blank --non-interactive
# copy frame.md, compositions/, assets/ in from ../design-system/
cd "$WS"
# init regenerates a CLAUDE.md routing to skills this repo deleted — replace it:
printf '# Build workspace. Sequence + commands: /render-lessons. Design contract: ../../design-system/frame.md\n' > CLAUDE.md
```

<!-- BUILD-KIT:BEGIN — scripts/batch-prepare.sh extracts everything between
     these two markers verbatim into _run/BUILD-KIT.md for cold build
     subagents. Keep ONLY builder-facing content here: no orchestrator
     phases, no ship/publish steps, and never any quotable example copy
     (a builder once pasted a cautionary example's heading into a video). -->

**Author `scenes.json` FIRST — never `index.html`.** The plan is the only
thing you write; `render-qa/build_index.py` compiles it into `index.html`
deterministically (host boilerplate, progress rail, `<audio>` host, per-slot
template clones and instance repointing are all compiler-owned — the generated
file's banner comment says so). One scene entry per beat: `template` (a
design-system composition), `narration` (its verbatim span of the refined
script), every slot filled or explicitly `""`, cue **anchor phrases** never
numbers. Learn the shape from any newer dated build's `scenes.json`, or
regenerate one from an existing build with `build_index.py --extract <ws>`.
**Never pattern-match the demo reel or the init-generated workspace
`CLAUDE.md`** — both are legacy. Follow `frame.md`'s animacy + illustration
rules when choosing templates and copy. Standing landmines:

- **Vary the form, or the gate fails you** (`frame.md` → "Variety contract";
  gate: `render-qa/check_variety.py`). The hard rules: **never a one-item
  list** (a list slot with exactly one entry draws the bullet/pill illustration
  around a single fact — give it ≥2 items or use a form that states one idea);
  **max 2 consecutive** scenes on one template family; **≥5 distinct content
  forms** for a lesson ≥90s; **no single form above 40%** of content scenes;
  **artwork on most scenes** (≥60% coverage, ≥5 distinct assets, none reused
  more than twice, never 3 bare scenes in a row); **no long single-canvas
  block** (cap on consecutive scenes/seconds on one background). Plan the whole
  scene list against these BEFORE filling copy — variety is a property of the
  plan, not of any one scene.
  Before you settle the scene list, read the template table and deliberately
  spend the less-used forms — `scla-career-map`, `scla-steps`, `scla-morph`,
  `scla-loop`, `scla-quote`, `scla-stat` exist and go untouched build after
  build. When the narration names a thing ("a tool like a career map becomes
  helpful", "First… Second… Third…"), the template that depicts that thing is
  the one to use. Rotate the connective device too: an arrow drawn between two
  statements, a comparison scale, a split frame — not a fourth pill row.
- **Headings are Title Case, no terminal period** (gate:
  `render-qa/check_copy.py`). Body copy stays sentence case.
- **`index.html` is a build artifact — never hand-edit it.** Every fix goes in
  `scenes.json` (or the bespoke composition file under `compositions/`, for a
  bespoke scene) and gets recompiled. The authoring loop is seconds, not
  minutes: edit `scenes.json` → `build_index.py .` → `preflight.py . --static`
  — the same checkers the hard gate runs, before any TTS or render exists. The
  guard hook fires that same suite on every `scenes.json` write.
- **Never type a timing number.** Each scene's `narration` is its verbatim
  span of the refined script (split only at sentence ends); reveals are cue
  **anchor phrases** in the plan; the compiler owns every number
  (`data-start`/`data-duration`/cue seconds are placeholders until
  `compile_timeline.py --apply`). `data-anchor-end` is legacy-only — never
  author it.
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
refined script BEFORE any TTS, synthesizes one clip per scene (cached —
edits only re-synthesize changed scenes), and concatenates with REAL boundary
silence; never hand-run single-take `hyperframes tts` for a lesson (the
old insert-silence flow spliced words — decisions/log.md 2026-07-14). Default
provider is **HeyGen starfish** (2026-07-22 — needs a live `HEYGEN_API_KEY`,
which **only `scripts/with-secrets.sh` supplies**; the ambient shell
`HEYGEN_API_KEY` is stale and fails, so never call `synth_narration.py` bare) —
it returns native word
timestamps with the synthesis, so the Whisper transcribe step is **skipped**:

```bash
python3 ../../render-qa/build_index.py .               # scenes.json -> index.html; compiler-owned, never hand-edited
python3 ../../render-qa/preflight.py . --static        # plan-stage gates (variety, copy, slots, text, stem) — exit 0 BEFORE any TTS is spent
../../../../scripts/with-secrets.sh python3 ../../render-qa/synth_narration.py .   # per-scene HeyGen TTS -> narration.wav + scene-times.json + narration.words.json
python3 ../../render-qa/compile_timeline.py . --apply  # owns ALL numbers (boundaries + cues from the manifest + HeyGen words)
python3 ../../render-qa/preflight.py .                 # full gate incl. script-vs-transcript diff — exit 0 or fix
npm run check                                          # lint + validate + inspect
```

The first two commands are the cheap loop — iterate on `scenes.json` until
`--static` exits 0 (a variety or copy failure discovered here costs seconds; the
same failure after TTS costs a re-synth, and after a render costs 7 minutes).
Only then spend TTS.

**There is no fallback voice.** The narration voice is pinned
(`.claude/rules/video-production.md`) and kokoro is not provisioned here. If
HeyGen fails: STOP, capture the exact command + full error output, and report
— never switch providers, never `pip install` a TTS, never work around a
credential failure (a 2026-07-28 builder did all three; the actual fault was a
broken flag in `with-secrets.sh`, which only the orchestrator could see).

Edited a scene's narration or reordered scenes? Re-run the same four commands
in order — synth re-does only the changed clips, and a stale transcript fails
loudly instead of misaligning.

An unresolvable anchor error names the scene and transcript window — fix the
phrase, never the numbers. **Stop here. No render in this phase.**

<!-- BUILD-KIT:END -->

### B3 — Verify + present the gate (orchestrator)

For each returned workspace, independently re-run the deterministic gate —
trust exit codes you produced, not subagent prose:

```bash
python3 projects/video-production/render-qa/preflight.py projects/video-production/renders-hyperframes/<stem>
```

**Once your independent preflight exits 0**, the build is gate-clean. The
script STAYS in `refined/` until publish — `batch-ship.sh --publish` moves it
to `rendered/` in the same pass that records the Wistia URL (changed
2026-07-28: `rendered/` now means published-or-publishing, so
`batch-status.sh` can flag anything stranded between render and publish).

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
("ship X", "approved, render X"). Once granted, SHIP runs to completion —
render, verify, file, publish to Wistia — with no second human checkpoint
(MP4 REVIEW / PUBLISH gate removed 2026-07-22, decisions/log.md; this used to
be a separate phase gated on its own "publish <stem>" trigger).

**Scope of an approval (changed 2026-07-28):** approving a stem no longer
covers only that stem. Approving the **pilot** of a batch authorizes the whole
batch — see Phase AUTO-BATCH. Use this single-stem phase for one-off work;
use AUTO-BATCH to drain a queue.

SHIP is `batch-ship.sh`, same as the batch — one-off work gets the same guard
chain (2026-07-28; the hand-run step list this section used to carry had none
of the guards). Look at real pixels before spending the render:

```bash
bash scripts/batch-precheck.sh <stem>                       # preflight + per-scene snapshots + low-ink flags (~40s) — vision subagent reviews the printed spread
bash scripts/batch-ship.sh <stem> <program-slug>            # render phase — BACKGROUND it (~7 min)
```

That runs preflight → `npm install` if the workspace was pruned → clean
`renders/` → render (25-min cap) → `verify_render.py` (writes the
`qa/VERIFIED` marker naming the exact MP4 + sha256) → prints `AWAITING_VISION`
with a sampled frame spread. **Frame review:** delegate to one vision-capable
subagent (paths only: the printed frames + `transcript.json`) — reveals land
on their words, every frame depicts its sentence, nothing clipped or
off-brand. Escalation only: `/adversarial-qa` when a cut resists diagnosis.

On a clean review:

```bash
bash scripts/batch-ship.sh <stem> <program-slug> --publish
```

Publish refuses to run without a fresh `qa/VERIFIED` marker (and re-hashes the
MP4 against it), refuses a stem already in `published.tsv`, then: file the MP4
→ Wistia upload (retried, time-capped) → append `lesson-scripts/published.tsv`
(the machine resume key: full stem + URL) → update the `refinement-log.md` row
→ move the script `refined/ → rendered/` → commit (a commit failure
quarantines WITH the URL and keeps the MP4) → delete the local MP4 → prune the
workspace in place (`archive-lesson.sh --in-place`; moving a workspace into
`_archive/` stays a human-only call).

Report the Wistia URL to the human as confirmation of what happened, not as a
request for permission — approving the hyperframe already authorized this.

---

## Phase AUTO-BATCH — drain a whole queue in one session

Default when more than one script is queued. Two things make it survivable:
**a pilot** (one human approval for the batch) and **run economics** (below).

### A0 — Prepare the run, once

```bash
export VIDEO_SNAG_RETRO_HOOK_DISABLED=1 VIDEO_PURGE_REMINDER_HOOK_DISABLED=1
sudo mount -o remount,size=2G /dev/shm
bash scripts/batch-prepare.sh          # builds renders-hyperframes/_run/
```

`batch-prepare.sh` regenerates `_run/` from source every run — it is a build
artifact, gitignored, never committed, so it **cannot drift** the way a
hand-maintained doc would:

- `_run/BUILD-KIT.md` — the authoring contract distilled from `frame.md`
  (6,139 words) + the Build sequence + the standing landmines, down to ~2–3k
  tokens. A build subagent reads **this one file**, not thirty.
- `_run/scaffold/` — a workspace already `hyperframes init`'d at the pinned
  version with `compositions/`, `assets/`, the host-root progress rail and the
  `<audio>` host in place. Each build does `cp -a _run/scaffold <stem>` instead
  of a network install.

The hooks are silenced because they fire on *every* `npm run render` and
*every* `wistia-upload.sh` — 60 context injections across a 30-video batch,
all reminding you to do things `batch-ship.sh` already does. The snag-log retro
still happens, once, at close-out.

### A1 — Priority order

Drain **program by program**, highest value first, not alphabetically. Each
video is published and committed before the next starts, so if the session
dies the top-priority programs are already live. Priority is the human's call;
absent one, use `refinement-log.md`'s published counts (a program already
shipping is the one with an audience waiting).

### A2 — Pilot

Build ONE video — prefer a program with prior successful renders. Take it all
the way through the A3 loop (precheck included) and hand the human a preview
link plus the resulting Wistia URL. **If the pilot fails, stop and report; do not start the
batch.** The pilot exists to prove the credential path, the version pin, local
rendering, and the upload *before* 29 more run unattended — and to prove the
run economics on video 1 rather than at 3am.

### A3 — The loop, three tool calls per video

1. **Cold build subagent** — prompt carries *paths only*: the stem, its refined
   script, `_run/BUILD-KIT.md`, the assigned theme, and the verbatim snag Open
   block. It clones the scaffold, authors `scenes.json`, loops
   `build_index.py` + `preflight.py --static` until the plan is clean, then
   synth → compile → full preflight → check until green. It returns **five
   fields, no prose**: `workspace · scenes · theme · gate exits · one-line
   status`. Run on a fast model; escalate to a strong model only on a retry
   after a gate failure.
2. **`bash scripts/batch-precheck.sh <stem>`** — look before the render is
   spent: authoritative preflight re-run, one midpoint snapshot per scene
   (~40s), deterministic low-ink (blank-scene) flags, then a printed frame
   spread. A vision subagent reviews it (paths only): every scene carries real
   content, frames depict their sentences, nothing clipped or off-brand. FAIL
   → quarantine here, before the 7-minute render.
3. **`bash scripts/batch-ship.sh <stem> <program-slug>`** — the deterministic
   tail, **backgrounded**. Render phase: re-verify preflight → render (25-min
   cap) → `verify_render.py` (writes `qa/VERIFIED`) → prints `AWAITING_VISION`
   + a sampled frame spread. With a passed precheck this post-render vision
   pass is a spot-check for encode-level defects (ghosting, banding) — one
   subagent, sampled frames only. On PASS,
   `batch-ship.sh <stem> <program-slug> --publish`: marker + sha guard →
   file MP4 → Wistia upload → `published.tsv` + ledger row → `git mv` script
   to `rendered/` → commit → delete local MP4 → prune in place. Publish
   refuses a stem already in `published.tsv`, so re-running is safe.

**Pipelining:** because the driver is backgrounded, video N+1 *builds*
(network- and authoring-bound) while video N *renders* (CPU-bound). Different
resources, so they overlap cleanly. Do **not** run two renders at once — on a
4-core box that thrashes and costs more than it saves.

**Backgrounding is also what avoids the 10-minute tool-call ceiling** — a ~7
min render in a foreground call sits far too close to it.

### A4 — Orchestrator context discipline (non-negotiable)

The batch survives only if the orchestrator stays small. Never read a script
body, an `index.html`, or `frame.md` yourself — those are subagent territory.
**Never let rendered frames into your own context:** `verify_render.py` dumps 3
PNGs per scene, so a 15-scene video is 45 images ≈ 65k tokens and 30 videos
would be ~2M — more than everything else combined. The frame review runs inside
a subagent that samples ~6 frames and returns one line.

Budget: ~1.5k tokens per video, under ~80k for a 30-video batch.

### A5 — Fail soft, always

A failure at preflight, verify, or frame review **quarantines that video** —
built, unpublished, logged — and the batch moves on. One bad lesson never costs
the others. Report the quarantine list at close-out.

### A6 — Resuming

A stem is done **if and only if it has a row in
`lesson-scripts/published.tsv`** (full stem + Wistia URL, appended and
committed in the same pass that publishes — `refinement-log.md` stays the
human-facing ledger but its rows abbreviate stems and are not machine-matched).
`bash scripts/batch-status.sh` reconstructs the remaining queue in priority
order from the folders, the tsv and `render-qa/quarantine.log` alone — and
flags any script in `rendered/` without a published row as **STRANDED**, the
bucket that catches every state between render and commit. A fresh session
resumes with that one command; nothing depends on the previous session's
context surviving, which also makes mid-run context compaction a non-event.

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
