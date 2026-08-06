---
name: render-lessons
description: Orchestrate SCLA lesson builds, review, render, resume, and publish through the video run driver. Use AUTO-BATCH whenever the user wants a hands-off run, asks to continue the factory, does not want to choose stems, or wants safe parallel delegation from one slash command.
argument-hint: "AUTO-BATCH [PROGRAM|--all] | STATUS | BUILD <stem> | SHIP <stem> | RESUME"
disable-model-invocation: true
---

# Render Lessons

Use `projects/video-production/run.sh`; generated human status documents are not
agent input.

## AUTO-BATCH is the default hands-off path

`/render-lessons AUTO-BATCH` means the user has delegated scheduling and safe
parallel execution to the coordinator. Never ask the user to choose, copy, or
paste stems. Never require them to open separate Codex Cloud tasks.

It authorizes the coordinator to:

- resume and drain an unfinished active run;
- when that run is complete, select the remaining queue with `run.sh batch
  --all` and drain programs in the status priority order;
- launch parallel in-session subagents for different stems, up to the available
  agent slots and the recorded stage capacity;
- run normal build, queued TTS, gate, cloud-render, verification, and serial
  publish commands inside the selected scope.

`AUTO-BATCH PROGRAM` limits new selection to that program. If another run is
unfinished, finish it before replacing its scope.

Pause only for the one pilot approval or a genuine external blocker. Do not hand
routine commands back to the user.

AUTO-BATCH authorizes an evidence-based `run.sh retry` after the agent verifies
that the recorded cause changed; it does not authorize blind retry loops. A run
is complete only when every selected stem is `PUBLISHED`, never when
`run.json results.status` merely says a render completed.

### Automatic dispatch loop

1. Run `run.sh resume` and read the persisted selection plus live JSON status.
2. Intersect work with the active run's selected items. The broader status
   backlog is context, not permission to choose unrelated stems.
3. If a batch has no approved pilot, build and gate the first selected stem,
   present its preview, and pause once for owner approval. Do not render or
   publish any selected stem until `run.json` records that approval.
4. Drain stages without asking for stems:
   - `RENDERED`: publish serially.
   - `APPROVED`: render through the cloud/local queue, verify, then publish.
   - `STALLED`: resume the existing workspace at its recorded next action;
     preserve narration and completed work.
   - `REJECTED`: diagnose the recorded failure. Retry only after evidence that
     its cause changed; respect retry exhaustion and the circuit breaker.
   - selected `READY`: assign the highest-priority stems to parallel workers.
   - `RAW` or `NEEDS SCRIPT`: do not build; surface only if it blocks scope.
5. Give every worker one unique stem. A worker owns concept, direct HTML
   authoring, queued narration, computed timing, gate fixes, and lease release.
   The coordinator owns stage selection, pilot state, renders, and publishing.
6. Re-read live status after every completion and refill open worker slots.
   Use `status.priority` for program order and each program's displayed queue
   order for stems. At a 3/3 clean cloud streak, run `run.sh cloud-limit 4`
   automatically. Continue until selected work is published or truly blocked.
7. After an unfinished run is fully published, select a requested program with
   `run.sh batch --program PROGRAM`; otherwise AUTO-BATCH uses `run.sh batch
   --all` for the remaining backlog.

Use available in-session worker slots without promising a fixed number.
Provider/render queues remain enforced. Separate Codex Cloud tasks are an
optional advanced handoff, not part of AUTO-BATCH.

## Command map

```text
STATUS       → run.sh status --json
BUILD STEM   → run.sh produce --stem STEM, then the four-call flow below
SHIP STEM    → run.sh ship STEM [--publish]
RESUME       → run.sh resume, then continue only selected unfinished items
AUTO-BATCH   → resume, select, parallelize, render, and publish automatically
```

Program and whole-queue work are valid only after an explicit
`run.sh batch --program PROGRAM` or `run.sh batch --all`. Never broaden a named
stem into a queue scan.

## Prepare once

Run `bash scripts/batch-prepare.sh` once for a selected run. It creates one
cached scaffold and copies the tracked compact builder contract to
`_run/BUILD-KIT.md`. It must preserve `_run/run.json`.

Capacity is stage-specific: use available authoring workers, two queued
narration jobs, two cloud renders initially, and one publisher. Four cloud
renders unlock after three verified clean renders; a failure returns to two.

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

This replaces two pitchers and a judge. The two lenses must differ in visual
logic, not merely palette.

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

After the driver renders and verifies the MP4, sample beginning, middle,
transitions, and ending. Check encode-only failures: missing frames, corrupted
audio, sync drift, black/blank frames, truncation, or render differences from
the approved preview. This review remains until `run.json` records three
consecutive clean cloud renders. Deterministic MP4 verification always remains.

## Pilot and continuation

An explicit batch has one pilot. Record approval with:

```bash
bash projects/video-production/run.sh approve PILOT
```

Approval persists in `run.json`; never request it again on resume. After the
pilot, continue selected lessons without extra human checkpoints. A named
single-video run has no hidden queue continuation.

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
