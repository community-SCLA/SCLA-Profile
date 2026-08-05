---
name: render-lessons
description: Build and ship SCLA lesson videos from approved scripts. AUTO-BATCH (default for a queue) builds ONE pilot video, stops for a single human preview, and on approval drains the whole queue in priority order — build → render → verify → publish to Wistia — one cold subagent per video, no batch cap, each video published and committed before the next starts so an interrupted run never strands work. BUILD and SHIP ("ship <stem>") remain for one-off work. Downstream half of the SCLA lesson pipeline (dispatcher: /produce-video; upstream: /refine-scripts).
---

# render-lessons — ready script → hyperframe → (gate) → MP4 → (review) → Wistia

**This file owns the build/ship/publish sequence and every command.** Every
build is freeform (agent-native): the HTML is the authored artifact — no
templates, no scenes.json, no compiler (the template lane retired 2026-08-05,
decisions/log.md). The gated rules live in `.claude/rules/video-production.md`
and every normative number in `design-system/config/tokens.yml`; nothing from
either is restated here.

**ONE HUMAN CHECKPOINT, blocking, explicit:**

1. **PILOT GATE** — a batch builds ONE video, stops, and a human previews it.
   Approval authorizes the entire batch; a failure stops the run. (Changed
   2026-07-28 — this replaced the per-video HYPERFRAME GATE, which required an
   approval per stem and made a 30-video queue impossible to drain. For a
   single one-off video, the pilot *is* that video, so nothing changes.)

`ready/` is your finalize-before-build buffer — it holds only scripts not
yet built (edit or veto any of them there, any time *before* you invoke
BUILD). The moment a lesson is live on Wistia, its script moves `ready/ →
published/` (B4), so `ready/` always shows exactly what's left to build and
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

A working artifact is named `<title>_<program>` — **no date**. Only the
delivered MP4 carries one, the render date, frozen at publish (2026-07-29,
`decisions/log.md`).

```
lesson-scripts/<program-slug>/inbox/<base>.txt      RAW — captured, not yet refined
lesson-scripts/<program-slug>/ready/<base>.txt      READY — BUILD's queue, refined + approved
renders-hyperframes/<base>/                         BUILDING → NEEDS REVIEW → RENDERED
lesson-scripts/<program-slug>/published/<base>.txt  PUBLISHED — live on Wistia
renders-mp4/<program-slug>/<base>_<render-date>.mp4 the delivered file
```

**The folder name IS the stage name** (2026-08-04). `published/` means
published — live at a Wistia URL — and `batch-ship.sh --publish` is the one
thing that moves a script there, in the same pass that records the URL. It is
not "a gate-clean build exists"; that state is the workspace's own, read from
`renders-hyperframes/<base>/` by `batch-status.sh`.

---

## Phase BUILD (default) — drain `ready/` into workspaces, then stop

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
  `projects/video-production/render-qa/logs/snag-log.md` (the first `## ` entry —
  use Read with a line limit; never load the whole file). Its **Open** list
  rolls forward until fixed — carry it into every build-subagent prompt and
  into your close-out.

### B1 — Queue and batch

- Queue = every `*.txt` in **`ready/`** (`ls …/ready/*.txt`, non-recursive —
  `ready/` has no subfolders; the `refined/avatar/` HeyGen lane was deleted
  2026-08-04 along with the rest of the avatar lane). A published lesson's
  script moves out to `published/` (B4), so `ready/` holds only lessons not yet
  live. The workspace check is what tells built from unbuilt:
  if a script in `ready/` already has a `renders-hyperframes/<base>/`
  workspace, it's built and waiting at the gate — skip it (never rebuild one
  without being asked; point the human at its preview instead). Since a
  workspace is named for its base and nothing restamps it, that check is exact;
  the subagent's own `mkdir` is the hard backstop for a race the check loses.
- **No batch cap — the queue is the batch.** (Removed 2026-07-28: the old
  ≤3-per-session cap justified itself with a 500-tool-call budget in
  `hooks/pre-tool.sh`, and that hook is not armed — `~/.claude/settings.json`
  has no hooks and there is no `budget.json`. It was guarding a limit that
  doesn't exist.) What actually protects the session is **one cold subagent per
  video** — that keeps script bodies and `index.html` out of the orchestrator's
  context — plus the Phase AUTO-BATCH economics below. Both are mandatory; the
  number is not.
- **Builds run concurrently; renders do not.** Authoring and TTS are
  network-bound and overlap cleanly, so dispatch build subagents **up to 3 at a
  time**. Rendering is CPU-bound and is serialised by a lock inside
  `batch-ship.sh` (`renders-hyperframes/.render.lock`) — a second render exits 2
  rather than thrashing a 4-core box. You do not have to remember either rule:
  `mkdir <base>` is the build lock and `.render.lock` is the render lock, both
  atomic. (2026-07-29 — before this, "sequentially" was a sentence in this file
  and a session was already running 4 concurrent builds against no render lock
  at all.)
### B2 — Concept competition (orchestrator, per video, before the builder)

The gates are floors against defects; nothing mechanical rewards visual
ambition, and a gate-optimizing builder lands on minimum-viable-pass — the
2026-08-05 thin-carrier rejection passed every gate including pace
(`decisions/log.md` 2026-08-05 "Taste becomes a judged stage"). Taste is
therefore a judged stage: independent pitches compete, one judge picks.

Three cheap subagent calls, the first two in parallel, before each build
dispatch:

1. **Two concept pitchers** (parallel, text-only; prompt carries paths: the
   `ready/` script and `design-system/docs/taste.md`). Each pitches ONE
   concept from its assigned lens and returns: the carrying object (named,
   concrete), frame descriptions at 25/50/75/100% of runtime, what
   accumulates, and the payoff beat.
   - **Lens A, metaphor-first:** what single concrete object or scene could
     carry this entire lesson and visibly accumulate as it advances?
   - **Lens B, accumulation-first:** what should the frame have GAINED by
     30/60/90/120s — design the build-up first, then name the object it
     builds.
2. **One judge** (needs vision — it reads the reference contact sheets named
   in `taste.md` plus both pitches). It scores both against the concept-judge
   questions in `taste.md`, picks a winner, grafts the loser's best idea, and
   writes `renders-hyperframes/_concepts/<stem>/CONCEPT.md`: the chosen
   angle (one sentence), the milestone frames, what accumulates, the payoff
   beat. Mutual peer-review between pitchers is deliberately NOT used —
   competition judged once stays sharp; review meshes converge.

The judge's CONCEPT.md rides into the builder prompt as a path. It is the
builder's starting contract, not a cage: the builder may sharpen it against
the real timings, never silently replace it.

### B3 — One cold build subagent per video

Dispatch a general-purpose subagent per script, **up to 3 concurrently** (they
share the toolchain and `/dev/shm`, but builds are network- and authoring-bound;
the CPU-bound render is serialised separately by `.render.lock`). Each claims
its workspace with `mkdir`, so two subagents cannot collide on one lesson.
Every freeform build is bespoke authoring — run builders on a strong model. The prompt carries
**paths + facts, never file bodies** (except the snag block):

- the stem, the `ready/` script path, and the workspace parent
  `projects/video-production/renders-hyperframes/`;
- the path to the judge-written `_concepts/<stem>/CONCEPT.md` from B2;
- the **Open + rules block from the latest snag-log entry**, pasted verbatim;
- "Follow the **Build sequence** section of
  `.claude/skills/render-lessons/SKILL.md` exactly. The HTML is the authored
  artifact; narration first, then computed timings, then visuals. Run
  `preflight.py --static` early and often — it is free. Do NOT run
  `npm run render`. Report: workspace path, beat count, concept angle,
  gate outputs."

### Build sequence (the subagent reads this section)

The workspace is named `<title>_<program>` — no date (`.claude/rules/
video-production.md`). `render-qa/src/stem.py` owns the rule; never hand-slice a
suffix.

**`build-claim.sh` starts every build. There is no other way in.** It does the
four things that have to happen together and that prose only ever got one of:
takes the `mkdir` lock (atomic — exactly one of N concurrent subagents wins),
arms the write fence, opens the build journal, and regenerates
`PIPELINE-STATUS.md`. Never `mkdir` by hand, never `mkdir -p`, never
test-then-create.

```bash
bash scripts/build-claim.sh <base> <program-slug>     # exits non-zero if claimed
cd projects/video-production/renders-hyperframes/<base>
# batch runs: cp -a ../_run/scaffold/. .   (see BUILD-KIT). One-off without a kit:
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init . --example=blank --non-interactive
cp ../../design-system/config/tokens.yml tokens.yml
cp -a ../../design-system/assets assets     # vendored Proxima + brand SVGs
# init regenerates AGENTS.md/CLAUDE.md routing to skills this repo deleted — delete them:
rm -f AGENTS.md CLAUDE.md
```

**Journal every step you finish**, as you finish it — one row, append-only:

```bash
bash scripts/build-log.sh <base> voice "26 beats synthesized"
```

That row is the only reason an interrupted build can be resumed rather than
restarted. `batch-status.sh` reads the last one and prints *left off after
**voice**, 41 min ago*; without it a dead session leaves a folder and no
evidence, and the next session's only option is a rebuild that throws away
finished narration.

**A workspace that already exists is RESUMED, never re-claimed and never
deleted:** `bash scripts/build-claim.sh <base> <program-slug> --resume`.

<!-- BUILD-KIT:BEGIN — scripts/batch-prepare.sh extracts everything between
     these two markers verbatim into _run/BUILD-KIT.md for cold build
     subagents. Keep ONLY builder-facing content here: no orchestrator
     phases, no ship/publish steps, and never any quotable example copy
     (a builder once pasted a cautionary example's heading into a video). -->

**The HTML is the authored artifact.** No templates, no scenes.json, no
compiler — you author `index.html` + `compositions/*.html` directly against
computed timings. Reference build (visual bar + working example of every
artifact): `projects/video-production/experiments/m1-mini-syllabus-freeform-trial/`
(the owner-approved 2026-08-05 cut) — read its `design.md`, never copy its
compositions. Build order is narration-first (a late visual fix then costs an
HTML edit, never a re-synthesis):

1. **`design.md`** — brand truth for THIS video plus the one thing no checker
   can grade: the **concept angle**, one sentence naming the single carrying
   visual idea (the reference's: "four transitions are four positions on ONE
   map, built once, never left") **and the beat range it persists across —
   this must cover ≥60% of the runtime.** ("Laid down, read twice, then hands
   off" is a rejected cut's own honest description of itself and is not a
   concept angle; see `decisions/log.md` 2026-08-04 "Owner verdict".) State the
   rule out loud and hold to it: *if an element cannot be justified as
   another way of reading the same object, it does not exist.* **A batch
   build receives a judge-selected `CONCEPT.md` (path in your prompt):
   design.md's concept angle starts from it — sharpen it against the real
   timings if needed, never silently replace it — and its milestone frames
   are your accumulation contract: the frame at each milestone must be a
   genuinely different picture, because the object has gained, lost, or
   re-arranged something.** A carrier that persists without accumulating is
   the 2026-08-05 thin-carrier rejection (`design-system/docs/taste.md`).
   Palette and face come from `tokens.yml` / `brand/visual-identity.md`;
   hierarchy by weight/size/color, headings Title Case without terminal
   periods.
2. **`audio_request.json`** — the beat manifest: `lines: [{id, text}]`, the
   ready script **verbatim** (TTS normalizations only), split into
   narration beats. **Pace target: ~10 beats per minute** — a ~150s lesson is
   ~25 beats, not ~17; a beat manifest that undershoots this by a wide margin
   is what the owner rejected as "SO boring" (`decisions/log.md` 2026-08-04
   "Owner verdict"; the numbers are gated by `render-qa/src/check_pace.py`).
   This file is the gates' narration source (`preflight --static` diffs it
   against the approved script — run it now, it is free).
3. **Synthesize** via the HyperFrames audio engine (`audio.mjs` from the
   `hyperframes-media` skill), pinned voice from `tokens.yml`, through
   `scripts/with-secrets.sh` — never a bare env. Output: `audio_meta.json`
   + one wav per beat.
4. **`timing.json`** — `{total, rows:[{id, audio_start, audio_dur, vis_start,
   vis_dur}]}` COMPUTED from `audio_meta.json` durations (a script computes
   it; never hand-tune a number). The tail after the last word ≥ **1.8s**
   (`FINAL_HOLD` — the gate floor is 1.5s and the owner rejected 1.1s twice).
   **Run `python3 projects/video-production/render-qa/src/check_pace.py
   projects/video-production/renders-hyperframes/<stem> --static` here** —
   this is the step where a pace fix is still free (re-splitting
   `audio_request.json` and re-synthesizing), not after HTML is authored
   against these timings. `beat-pace` / `long-beat-share` are BLOCKING in the
   real gate (`preflight --static`); catch them here first, where the fix
   costs nothing.
5. **Author** `index.html` + `compositions/*.html` against the frozen
   timings, word-timestamp-driven reveals. The freeform contract the gates
   read: on-frame copy lives in **markup, never JS strings**; headings carry
   **`data-role="heading"`** (or are `<h1>`–`<h3>`); the program display name
   and the lesson title appear on the title card in markup; deliberate
   exceptions are declared where they live (`/* motion-allow: … */`,
   `/* brand-allow: … */`). Colors are `tokens.yml colors:` at any alpha;
   every `font-family` leads with the brand face; body text ≥ 40px.
6. **Snapshot every beat midpoint** with the pinned CLI:
   `npx hyperframes@<pin> snapshot . --at <beat midpoints from timing.json>
   --no-end -o snapshots` — this grid is not ink-only: the pixel bounds gate
   (`check_ink`) grades it, and so does `check_pace.py --stills`
   (`carrier-drift` + `twin-share`, run automatically inside the full
   `preflight.py`). Fewer stills than beats is a preflight FAIL either way.
   Review them yourself before presenting the gate — against the
   critic-lane questions in `design-system/docs/taste.md`: if the frames at
   25/50/75/100% could be shuffled without anyone noticing, re-author the
   flat beats now, before the gate ever sees them.
7. **Gates:** `bash scripts/build-gate.sh <stem>` (runs `preflight.py`:
   timing contract, script-vs-beats, copy, continuity, forms, brand, text,
   title, ink, motion, pace, per-beat layout) exit 0, then `npm run check`.
   **Stop here. No render in this phase.**

Standing landmines:

- **Headings are Title Case, no terminal period** (gate:
  `render-qa/src/check_copy.py`). Body copy stays sentence case.
- **Never a one-item list, never a one-card comparison** (gate:
  `render-qa/src/check_forms.py` on element structure) — a list with one
  entry draws the bullet/pill illustration around a single fact; give it ≥2
  items or state the idea in a form that is not a list.
- **Vary the form.** The old numeric variety thresholds retired with the
  template lane and stay retired — the owner resolved 2026-08-05 that
  variety is JUDGED (concept judge + taste critic against
  `design-system/docs/taste.md`), not counted. The taste they encoded is
  unchanged: rotate the connective device (an arrow between two statements,
  a comparison scale, a split frame), not a fourth pill row — and every form
  must still read as another way of reading the ONE carrying object.
- **Settled content never re-animates in place** (gate:
  `render-qa/src/check_motion.py`) — idle pulses are banned; deliberate
  exceptions are declared inline with `/* motion-allow: <reason> */`.
- Idle drift on decoration: translate-only (the y-nudge pattern). Animating
  `scale` + SVG `opacity` together ghosts in the streaming encode.
- Never qualify a bespoke sub-comp root by its own class/attribute (e.g. a
  `#root.navy` selector): it renders unstyled under composition scoping even
  though it passes every static check. Style bespoke roots with a plain
  `#root` block or a child wrapper. (Promoted 2026-07-14; landed 2026-07-15.)

**There is no fallback voice.** The narration voice is pinned
(`.claude/rules/video-production.md`) and kokoro is not provisioned here. If
HeyGen fails: STOP, capture the exact command + full error output, and report
— never switch providers, never `pip install` a TTS, never work around a
credential failure (a 2026-07-28 builder did all three; the actual fault was a
broken flag in `with-secrets.sh`, which only the orchestrator could see).

Edited a beat's narration or re-split the manifest? Re-synthesize (the audio
engine re-does only changed clips), recompute `timing.json`, re-snapshot, and
re-run the gates — a stale manifest fails loudly instead of misaligning.

<!-- BUILD-KIT:END -->

### B4 — Verify + present the gate (orchestrator)

For each returned workspace, independently re-run the deterministic gate —
trust exit codes you produced, not subagent prose:

```bash
bash scripts/build-gate.sh <stem>
```

On exit 0, look at real pixels before a human does: run
`bash scripts/batch-precheck.sh <stem>` and hand its printed spread to the
**two vision lanes** (defect + advisory taste — see Phase SHIP; both are
subagents, paths only). A FLAT taste verdict buys exactly one revision pass
(re-author the named beats, re-snapshot, re-gate, re-precheck) before the
gate is presented; it never blocks the presentation after that pass.

That runs the real `preflight.py` and, **on exit 0 and only on exit 0**, writes
`qa/PREFLIGHT-OK` — the marker that makes NEEDS REVIEW readable from disk after
this session ends. Without it "gate-clean, awaiting your eyes" lives only in
your context, and the next session sees a half-finished build. A non-zero run
deletes any marker an earlier pass left: a stale green is worse than no green.

The script STAYS in `ready/` until publish — `batch-ship.sh --publish` moves it
to `published/` in the same pass that records the Wistia URL, so
`batch-status.sh` can flag anything stranded between render and publish.

Then close the build out, which lowers the write fence and regenerates the
status doc:

```bash
bash scripts/build-release.sh <stem> "gate-clean, at the preview gate"
```

Then **stop and hand the human the gate**, per video: stem, theme, scene
count, and how to watch it. **Never print `<stem>` as a placeholder** — give
the literal, copy-pasteable command with that video's actual stem filled in,
one fenced command per video built this session (even when there's only one):

```bash
bash scripts/preview.sh career-building-is-a-repeatable-process_early-career-boost
```

```bash
bash scripts/preview.sh what-makes-for-a-dream-job_early-career-boost
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
bash scripts/batch-precheck.sh <stem>                       # preflight + per-beat snapshots + low-ink flags (~40s) — TWO vision lanes review the printed spread
bash scripts/batch-ship.sh <stem> <program-slug>            # render phase — BACKGROUND it (~7 min)
```

The precheck spread goes to **two vision lanes**, dispatched in parallel,
each a cold subagent given paths only (the printed contact sheets + frames):

1. **Defect lane** (blocking): every beat carries real content, frames depict
   their sentences, nothing clipped or off-brand — a FAIL quarantines before
   the render is spent.
2. **Taste lane** (advisory): grades the sheets against the critic-lane
   questions in `design-system/docs/taste.md` (shuffle test, carrier earning
   its frame, gain-in-detail, where a viewer checks out) and returns
   `ALIVE`/`FLAT` with beats named. FLAT buys exactly ONE revision pass —
   re-author the named beats, re-snapshot, re-gate, re-precheck — then the
   build proceeds either way; taste alone never quarantines.

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
→ move the script `ready/ → published/` → commit (a commit failure
quarantines WITH the URL and keeps the MP4) → prune the workspace in place
(`archive-lesson.sh --in-place`; moving a workspace into `_archive/` stays a
human-only call). The filed MP4 stays in `renders-mp4/<program>/`
as a local backup — gitignored, never deleted.

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

- `_run/BUILD-KIT.md` — the Build sequence + the standing landmines,
  extracted verbatim from this SKILL. A build subagent reads **this one
  file**, not thirty.
- `_run/scaffold/` — a workspace already `hyperframes init`'d at the pinned
  version with `tokens.yml`, the vendored Proxima set and the brand SVGs in
  place. Each build copies the scaffold contents instead of a network install.

The hooks are silenced because they fire on *every* `npm run render` and
*every* `wistia-upload.sh` — 60 context injections across a 30-video batch,
all reminding you to do things `batch-ship.sh` already does. The snag-log retro
still happens, once, at close-out.

### A1 — Priority order

Drain **program by program**, highest value first, not alphabetically. Each
video is published and committed before the next starts, so if the session
dies the top-priority programs are already live. **Priority has one
definition**: the `PRIORITY=` default in `scripts/batch-status.sh`, override
with `VIDEO_PRIORITY="slug-a slug-b …"`. `batch-status.sh` already emits the
queue in that order, so drain it top to bottom rather than re-deriving it.

### A2 — Pilot

Build ONE video — prefer a program with prior successful renders. Take it all
the way through the A3 loop (precheck included) and hand the human a preview
link plus the resulting Wistia URL. **If the pilot fails, stop and report; do not start the
batch.** The pilot exists to prove the credential path, the version pin, local
rendering, and the upload *before* 29 more run unattended — and to prove the
run economics on video 1 rather than at 3am.

### A3 — The loop, per video

0. **Concept competition** (B2, ~3 cheap calls): two pitch lanes in
   parallel, one vision judge → `_concepts/<stem>/CONCEPT.md`. Runs while
   the previous video renders, so it costs no wall-clock on the batch.
1. **Cold build subagent** — prompt carries *paths only*: the stem, its
   `ready/` script, `_run/BUILD-KIT.md`, its `CONCEPT.md`, and the verbatim
   snag Open block. It
   claims with `build-claim.sh`, copies the scaffold, then runs the Build
   sequence: design.md → beat manifest (+ `preflight.py --static`, free) →
   synth → computed timing.json (+ `check_pace.py --static`) → author HTML →
   per-beat snapshots → `build-gate.sh` → check until green, journalling each
   finished step with `build-log.sh`. It returns **five fields, no prose**:
   `workspace · beats · concept · gate exits · one-line status`. Freeform
   authoring is bespoke — run builders on a strong model.
2. **`bash scripts/batch-precheck.sh <stem>`** — look before the render is
   spent: authoritative preflight re-run, one midpoint snapshot per beat
   (~40s), deterministic low-ink (blank-frame) flags, then a printed frame
   spread. **Two vision lanes** review it in parallel (paths only; full lane
   contract in Phase SHIP): the defect lane (real content, frames depict
   their sentences, nothing clipped/off-brand — FAIL → quarantine here,
   before the 7-minute render) and the advisory taste lane
   (`design-system/docs/taste.md`; FLAT → one revision pass, then proceed —
   in a batch this lane is the only taste check a post-pilot video gets).
3. **`bash scripts/batch-ship.sh <stem> <program-slug>`** — the deterministic
   tail, **backgrounded**. Render phase: re-verify preflight → render (25-min
   cap) → `verify_render.py` (writes `qa/VERIFIED`) → prints `AWAITING_VISION`
   + a sampled frame spread. With a passed precheck this post-render vision
   pass is a spot-check for encode-level defects (ghosting, banding) — one
   subagent, sampled frames only. On PASS,
   `batch-ship.sh <stem> <program-slug> --publish`: marker + sha guard →
   file MP4 → Wistia upload → `published.tsv` +
   ledger row → `git mv` script to `published/` → commit → prune in place
   (the filed MP4 is kept as a local backup). Publish
   refuses a stem already in `published.tsv`, so re-running is safe.

Each video ends with `bash scripts/build-release.sh <stem>` — the final
journal row, the write fence lowered, `PIPELINE-STATUS.md` regenerated. A build
that never releases leaves the fence armed until its 6h TTL expires, which is a
nuisance rather than a disaster, but the status doc then lies about what is in
flight.

**Pipelining:** because the driver is backgrounded, videos N+1..N+3 *build*
(network- and authoring-bound) while video N *renders* (CPU-bound). Different
resources, so they overlap cleanly — keep up to **3 builds in flight** so the
render lane never sits idle waiting for a plan. Two renders at once would
thrash a 4-core box, so `batch-ship.sh` refuses: the second exits 2 on
`.render.lock`. You do not have to sequence renders by hand, but do not treat a
lock failure as a retry-in-a-loop — wait for the render in flight to finish.

**Backgrounding is also what avoids the 10-minute tool-call ceiling** — a ~7
min render in a foreground call sits far too close to it.

### A4 — Orchestrator context discipline (non-negotiable)

The batch survives only if the orchestrator stays small. Never read a script
body or an `index.html` yourself — those are subagent territory.
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
flags any script in `published/` without a `published.tsv` row as
**STRANDED**, the
bucket that catches every state between render and commit. A fresh session
resumes with that one command; nothing depends on the previous session's
context surviving, which also makes mid-run context compaction a non-event.
Four things regenerate `projects/video-production/PIPELINE-STATUS.md`, so a
build can no longer happen without the status doc noticing: `build-claim.sh`
(a build starts), `build-gate.sh` (it passes or fails the gate),
`build-release.sh` (it ends) and `batch-ship.sh` (quarantine, publish). It is
the same read as this command, rendered as a document a human can open without
running anything — and `lint-refs.sh` check 14 fails if it has drifted from a
fresh regeneration.

## Close-out — the self-improvement loop (every session, both phases)

Append a **new entry at the top** of `render-qa/logs/snag-log.md` following the
rules in its header: new snags tagged `[env]/[tooling]/[authoring]/[upstream]/[defect]`
with resolution + time cost, **Open items carried forward verbatim from the
previous entry until actually fixed**, and durable lessons promoted into the
owning doc (this SKILL, `.claude/rules/video-production.md` + its checker, or
preflight/verify checks) in the same session — the doc is the memory, the log is the trail. **Open items are
owner-actionable by definition** — anything you could fix yourself (code,
config, a retry, filing an upstream bug), fix this session; never roll
agent-fixable work forward. **If the new entry's Open list is non-empty, ASK
the human directly at close-out to resolve each item** (AskUserQuestion when
the session is interactive) — do not just file them in the log for the human to
find. File any new HyperFrames bug upstream before ending (hyperframes#2064 is
the model repro). Report per
video: stem, theme, phase reached, gate outcomes, Wistia URL (or pending).
