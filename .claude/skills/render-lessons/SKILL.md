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

`/render-lessons AUTO-BATCH` delegates scheduling and parallel execution while
the coordinator is active. Selection and external-task reservations survive an
interruption, but there is no background daemon: a stopped agent session does
not continue TTS, reviews, merges, renders, or publishing by itself. Never ask
the user to choose, copy, or paste stems.

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

`AUTO-BATCH [PROGRAM] --cloud` records cloud source authoring through the
matching `run.sh batch ... --cloud` command, then runs `run.sh drain` once.
Drain atomically reserves each untouched `READY` lesson before submission,
records its task reference, respects authoring capacity, and is safe to rerun.
`run.sh delegate` only previews assignments. After each branch/PR is merged,
record the handoff with `run.sh dispatch-merged --stem STEM [--task-ref REF]`,
then resume narration and gates locally. `reserved`, `submitted`, and `unknown`
Cloud ownership blocks local resume. Never delegate a stem that already has a
workspace; resume it locally instead.

Return each passing lesson immediately and launch its Studio preview with
`bash scripts/review.sh STEM`; continue its siblings. Do not hand routine
commands back to the user.

Retry only after its cause changes. Only `PUBLISHED` is complete.

### Automatic dispatch loop

1. Read `run.sh resume --json`, then explicitly select the requested program or
   `--all`. Disk evidence preserves older unfinished work.
2. Give each worker one stem. Resume `STALLED`; diagnose `REJECTED`; dispatch
   untouched `READY`; render `APPROVED`; review a required encode; and publish
   `RENDERED` serially. Do not build `RAW` or `NEEDS SCRIPT`.
3. Return each clean stem through `review.sh` immediately while siblings keep
   moving. Re-read status after completions and refill slots in priority order.
4. At three clean reviewed Cloud renders, set `cloud-limit 4`. Never delete or
   silently retry; a workspace must not be redelegated.

Use available slots and enforce provider/render queues. Normal AUTO-BATCH uses
in-session workers; `--cloud` uses Cloud tasks.

Program and whole-queue work require `run.sh batch --program PROGRAM` or
`run.sh batch --all`. Never broaden a named stem.

## Prepare once

Run `bash scripts/batch-prepare.sh` once; it preserves `_run/run.json`.

Capacity is stage-specific: available authors, two narration jobs, two cloud
renders, and one publisher. Three clean renders unlock four; failure resets two.

## Four-call flow

### 1. Concept planner

Give the planner only the selected refined script, local tokens, and this task:

```text
Propose and score two distinct visual lenses for fidelity, evolution, attention,
and feasibility. Select one. Write its carrier, beat progression, milestone
frames, motion logic, and risk to CONCEPT.md; retain scores in concept.json.
```

### 2. Builder

Give one builder exactly:

- `contracts/builder.md` (or its generated `_run/BUILD-KIT.md` copy)
- the selected refined script
- `CONCEPT.md`
- the workspace-local `tokens.yml`

The builder claims one stem, authors HTML directly, runs audio and timing, and
stops at a green gate. It never renders or publishes and always releases.

### 3. Combined pre-render visual review

Use one reviewer with `contracts/visual-review.md`. It must return separate
blocking and taste verdicts. Send one consolidated revision list to the same
builder if needed; do not create parallel review debates.

Persist the verdict against the current source revision:

```bash
bash projects/video-production/run.sh visual-review STEM \
  --blocking-defect PASS|FAIL --taste ALIVE|FLAT \
  --recommendation PROCEED|REVISE [--finding "specific finding"]
```

Only `PASS` + `ALIVE` + `PROCEED` advances to owner review. Any source edit
invalidates the gate, visual verdict, and owner approval for the previous cut.

### 4. Post-render encode review

After rendering, sample the beginning, middle, transitions, and ending for
missing frames, audio damage, drift, blanks, truncation, or preview differences.
Record the verdict with `run.sh encode-review STEM --backend cloud|local
--verdict PASS|FAIL`. Retain this review through three clean reviewed Cloud
renders; deterministic MP4 verification always remains.

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

Render and verify with `run.sh ship STEM`. After any required encode review,
publish that verified rendition with `run.sh ship STEM --publish`. Never use the
publish form as a render command. The driver owns Wistia ledger updates,
cleanup, release, and one concise run record.
