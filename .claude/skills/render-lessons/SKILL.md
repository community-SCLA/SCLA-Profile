---
name: render-lessons
description: Orchestrate SCLA lesson builds, review, render, resume, and publish through the video run driver. Use AUTO-BATCH whenever the user wants a hands-off run, asks to continue the factory, does not want to choose stems, or wants safe parallel delegation from one slash command.
argument-hint: "AUTO-BATCH [PROGRAM|--all] [--cloud] | STATUS | BUILD <stem> | SHIP <stem> | RESUME"
disable-model-invocation: true
---

# Render Lessons

Use `projects/video-production/run.sh`; generated human status documents are not
agent input.

## AUTO-BATCH is the default hands-off path

`/render-lessons AUTO-BATCH` delegates scheduling and parallel execution.
Never ask the user to choose, copy, or paste stems.

It authorizes the coordinator to:

- preserve unfinished work in its workspace and failure receipt while
  selecting the requested batch; stalled or rejected lessons do not block
  fresh READY authoring;
- select the remaining queue with `run.sh batch --all` and drain programs in
  status priority order;
- launch parallel in-session subagents for different stems, up to the available
  agent slots and the recorded stage capacity;
- run normal build, queued TTS, gate, cloud-render, verification, and serial
  publish commands inside the selected scope.

`AUTO-BATCH PROGRAM` limits new selection to that program. Existing unfinished
work remains durable and recoverable when the batch selection replaces scope.

`AUTO-BATCH [PROGRAM] --cloud` records cloud source authoring through the
matching `run.sh batch ... --cloud` command. Print one `run.sh delegate` prompt
per selected untouched `READY` lesson instead of building locally. Submission
remains in the chosen Cloud task UI. After each branch/PR is merged, resume narration
and gates locally. Never delegate a stem that already has a workspace; resume
it locally instead.

Return each passing lesson immediately and launch its Studio preview with
`bash scripts/review.sh STEM`; continue other work. Pause that stem
for review without pausing its siblings. Do not hand routine commands
back to the user.

Retry only after the recorded cause changes. A stem is complete only when it is
`PUBLISHED`; unresolved siblings stay visible without withholding completed work.

### Automatic dispatch loop

1. Run `run.sh resume` and read persisted selection plus live JSON status.
2. For AUTO-BATCH, select the explicitly requested program or `--all` even when
   earlier work is unfinished. Folder state and `qa/failure.json` preserve it;
   never delete or silently retry it.
3. Advance each selected stem independently. As soon as one becomes gate-clean,
   run `bash scripts/review.sh STEM`, return its Studio URL, and await approval
   for that stem while continuing every other unblocked stem.
4. Drain stages without asking for stems:
   - `RENDERED`: publish serially.
   - `APPROVED`: render, verify, then publish without waiting for siblings.
   - `STALLED`: resume locally at its recorded next action; preserve completed work.
   - `REJECTED`: diagnose independently. Retry only after its cause changed;
     do not block unrelated authoring, review, rendering, or publishing.
   - selected untouched `READY`: assign workers, or generate Cloud assignments
     when `authoring_backend` is `cloud`. A READY stem with an existing
     workspace resumes locally and must not be redelegated.
   - `RAW` or `NEEDS SCRIPT`: do not build; surface only if it blocks scope.
5. Give every worker one unique stem. A worker owns concept, direct HTML
   authoring, queued narration, computed timing, gate fixes, and lease release.
   The coordinator owns stage selection, review state, renders, and publishing.
6. Re-read live status after every completion and refill open worker slots.
   Use `status.priority` for program order and each program's displayed queue
   order for stems. At a 3/3 clean cloud streak, run `run.sh cloud-limit 4`
   automatically. Continue authoring while individual lessons await review.
7. AUTO-BATCH selects a requested program with `run.sh batch --program PROGRAM`;
   otherwise it uses `run.sh batch --all`. Durable failures remain recoverable
   after the new selection is recorded.

Use available slots and enforce provider/render queues. Normal AUTO-BATCH uses
in-session workers; `--cloud` uses Cloud tasks.

## Command map

```text
STATUS       → run.sh status --json
BUILD STEM   → run.sh produce --stem STEM, then the four-call flow below
SHIP STEM    → run.sh ship STEM [--publish]
RESUME       → run.sh resume, then continue only selected unfinished items
AUTO-BATCH   → resume, select, parallelize, render, and publish automatically
AUTO-BATCH --cloud → select cloud authoring and prepare one Cloud task per READY stem
```

Program and whole-queue work require `run.sh batch --program PROGRAM` or
`run.sh batch --all`. Never broaden a named stem.

## Prepare once

Run `bash scripts/batch-prepare.sh` once. It caches the scaffold and builder
contract while preserving `_run/run.json`.

Capacity is stage-specific: available authors, two narration jobs, two cloud
renders, and one publisher. Three clean renders unlock four; failure resets two.

## Four-call flow

### 1. Concept planner

Give the planner only the selected refined script, local tokens, and this task:

```text
Propose two meaningfully different visual lenses for this lesson.
For each: name the visual thesis, recurring carrier, beat progression,
three milestone frames, motion logic, and primary risk.
Score each 1–5 for claim fidelity, visual evolution, attention, and feasibility.
Select the stronger lens and explain the choice in no more than 80 words.
Write only the selected plan to CONCEPT.md; retain the scores in concept.json.
```

### 2. Builder

Give one builder exactly:

- `contracts/builder.md` (or its generated `_run/BUILD-KIT.md` copy)
- the selected refined script
- `CONCEPT.md`
- the workspace-local `tokens.yml`

The builder claims one stem, authors HTML directly, uses `video-audio.sh` and
`plan_timing.py`, and stops at a green deterministic gate. It never renders or
publishes. A build session releases its own lease even when it exits early.

### 3. Combined pre-render visual review

Use one reviewer with `contracts/visual-review.md`. It must return separate
blocking and taste verdicts. Send one consolidated revision list to the same
builder if needed; do not create parallel review debates.

### 4. Post-render encode review

After rendering, sample the beginning, middle, transitions, and ending for
missing frames, audio damage, drift, blanks, truncation, or preview differences.
Retain this review through three clean cloud renders; MP4 verification remains.

## Rolling review and continuation

Each lesson is handed back as soon as it is gate-clean. Launch its detached
Studio server and print the live URL:

```bash
bash scripts/review.sh STEM
```

After the owner reviews that lesson, record only its approval:

```bash
bash projects/video-production/run.sh approve STEM
```

Approval persists in `run.json`. Render, verify, and publish that stem without
waiting for the rest. `approve BATCH` remains an optional convenience only when
the owner has actually reviewed every selected gate-clean workspace.

## Failure policy

The driver records every failed external command in `qa/failure.json` and a
full log. It refuses a third same-stem attempt and opens the circuit after two
consecutive distinct stems fail with the same class. Do not loop around either
stop. After the underlying cause changes, the owner or operator explicitly
authorizes:

```bash
bash projects/video-production/run.sh retry STEM --reason "what changed"
```

Resume from the recorded recovery action. Do not delete workspaces or rebuild
cached narration.

## Close-out

Publish per workspace through `run.sh ship STEM --publish`. The driver owns
verification, Wistia ledger updates, cleanup, release, and one concise run
record. Do not inject per-command cleanup reminders.
