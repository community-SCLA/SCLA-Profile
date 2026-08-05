---
name: render-lessons
description: Orchestrate SCLA lesson builds, review, render, resume, and publish through the video run driver.
argument-hint: "STATUS | BUILD <stem> | SHIP <stem> | RESUME"
disable-model-invocation: true
---

# Render Lessons

This skill orchestrates; it does not teach composition authoring. The public
control surface is `projects/video-production/run.sh`. Generated human status
documents are not agent input.

## Command map

```text
STATUS       → run.sh status --json
BUILD STEM   → run.sh produce --stem STEM, then the four-call flow below
SHIP STEM    → run.sh ship STEM [--publish]
RESUME       → run.sh resume, then continue only selected unfinished items
```

Program and whole-queue work are valid only after an explicit
`run.sh batch --program PROGRAM` or `run.sh batch --all`. Never broaden a named
stem into a queue scan.

## Prepare once

Run `bash scripts/batch-prepare.sh` once for a selected run. It creates one
cached scaffold and copies the tracked compact builder contract to
`_run/BUILD-KIT.md`. It must preserve `_run/run.json`.

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
