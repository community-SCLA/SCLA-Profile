# Codex Cloud Video Production — User Guide

## Recommended: use one command

For a hands-off run, invoke:

```text
/render-lessons AUTO-BATCH
```

That is the normal user path. The coordinator reads the active run, chooses the
correct stems from their stages, fills available parallel worker slots, keeps
HeyGen and cloud renders inside their queues, publishes serially, and continues
through the remaining programs in priority order. You do not copy prompts,
select stems, or open separate cloud tasks.

To prepare source authoring as separate Codex Cloud tasks instead, invoke:

```text
/render-lessons AUTO-BATCH --cloud
```

Or limit the new cloud-authored batch to one program:

```text
/render-lessons AUTO-BATCH mid-career-momentum --cloud
```

This records cloud authoring in the run and produces one exact delegation
assignment per `READY` lesson. Submit those assignments in Codex Cloud; the
current public launcher is the Cloud interface, not a repository shell API.

To limit a new run to one program:

```text
/render-lessons AUTO-BATCH mid-career-momentum
```

The sequence first builds every selected lesson into a gate-clean HyperFrames
workspace, then pauses once for review of the complete program set. Nothing
renders or publishes before that full-set approval. Reply to the pause in the
same conversation; you do not need to restart the sequence.

## What runs where

| Stage | Where | Starting limit | Why |
| --- | --- | ---: | --- |
| Source authoring | Codex Cloud, one isolated task per stem | 6 | No HeyGen calls and no Codespace rendering load |
| Narration | Live coordinator through the shared HeyGen queue | 2 | Prevents provider bursts; a normal lesson is one request |
| Final timing and gate fixes | Live coordinator or one worker per stem | 3 local | Needs the generated timing and local QA evidence |
| Cloud render | HeyGen-hosted HyperFrames render | 2, then 4 | Starts conservatively and scales only after clean evidence |
| Publish | Live checkout | 1 | Wistia and shared ledgers must stay serial |

Generated voice, QA, render, dependency, font, and brand copies remain ignored.
The authored workspace source is tracked, so Codex Cloud can return it in a
commit or pull request.

## Do not choose stems from memory

Start with the active run and let each lesson's stage determine the action:

```bash
bash projects/video-production/run.sh resume
bash projects/video-production/run.sh status
bash projects/video-production/run.sh batch --all --cloud
bash projects/video-production/run.sh batch --program --cloud
```
Use Sol High for a full program batch.
Sol High: Best default for this pipeline. It balances creative judgment, coding, QA, and persistence.
Extra High (xhigh): Use for recovering rejected/stalled builds or solving difficult visual/technical failures. It is slower and more expensive, and usually unnecessary for every lesson.
Medium: Fine for status checks, clean reruns, and mechanical fixes—not ideal for unattended authoring.
Light/Low: Avoid for building lesson videos. It’s better suited to simple, latency-sensitive tasks.
So for Mid-Career Momentum: Sol High + /render-lessons AUTO-BATCH. Escalate individual problem lessons to Extra High if they fail gates repeatedly.

| Stage shown | What to do |
| --- | --- |
| `READY` | Generate a Codex Cloud prompt with `run.sh delegate --stem STEM` The lesson script is approved and placed in the build queue.|
| `STALLED` | Resume the existing workspace; never delegate or recreate it |
| `NEEDS REVIEW` | Review all selected workspaces; after the complete set is ready, run `run.sh approve BATCH` |
| `APPROVED` | Render it with `run.sh ship STEM` The workspace/composition has passed review and is cleared to become an MP4.|
| `RENDERED` | Publish it with `run.sh ship STEM --publish` The workspace has been converted into a finished, verified MP4, but it has not yet been published.|
| `REJECTED` | Correct the recorded cause, authorize retry if required, then ship again |
| `RAW` | Refine the script first |
| `NEEDS SCRIPT` | Stop; the owner must supply narration |
| `PUBLISHED` | Nothing; it is complete The MP4 has been uploaded to Wistia.|

Do not start another `batch --program` while the current program still has
unfinished work: selecting a new batch replaces the active scope. Delegate only
stems displayed as `READY` inside the active run. The command refuses a stem
outside that scope.

For a fresh coordinator session, paste:

```text
Resume the active SCLA video run. Do not ask me to choose a stem and do not
start a new batch. Read the live status, stay inside its recorded scope, and
continue the highest-priority safe next action. Tell me when owner approval or
an external fix is actually required.
```

## Start a new batch

From the live repository:

```bash
bash projects/video-production/run.sh batch --program PROGRAM --cloud
bash scripts/batch-prepare.sh
bash projects/video-production/run.sh limits
bash projects/video-production/run.sh status --json
```

Replace `PROGRAM` with the lesson program slug. The limits command should show
authoring `6`, TTS `2`, cloud render `2`, and publish `1` for a cloud run.

`batch-prepare.sh` refreshes the shared scaffold once; do not initialize each
lesson separately. Commit and push the pipeline and scaffold source changes
before opening cloud tasks. Codex Cloud works from the pushed repository state,
not uncommitted files in the Codespace.

## Optional advanced mode: separate Codex Cloud tasks

This mode is optional. Use it only when you specifically want separate isolated
pull requests instead of the one-command in-session coordinator. For each ready
stem, generate its exact task prompt:

```bash
bash projects/video-production/run.sh delegate --stem STEM
```

Copy the entire output into a fresh Codex Cloud task. Open one task per stem,
up to six at once. Every task must use a different stem.

The cloud task will:

1. Create a source-only HyperFrames workspace.
2. Write the concept, design, narration request, and composition.
3. Run static preflight.
4. Return a commit or pull request.

It will not call HeyGen, render, publish, or change shared run state.

Review and merge each task separately. Do not merge generated voice, QA,
`node_modules`, or MP4 files even if a worker created them.

## Finish each merged workspace in the live checkout

In a fresh live Codex or Claude session, paste this prompt after replacing the
two placeholders:

```text
Finish the existing SCLA lesson workspace STEM for PROGRAM. Read AGENTS.md,
projects/video-production/CLAUDE.md, and the builder contract they route to.
Resume the existing workspace; do not recreate it. Generate narration only
through scripts/video-audio.sh, compute timing through plan_timing.py, apply
timing.json without changing its values, run the build gate, fix only this
workspace, and release the build lease. Stop before render or publish and give
me the gate result.
```

The mechanical commands behind that handoff are:

```bash
bash scripts/build-claim.sh STEM PROGRAM --resume
bash scripts/video-audio.sh projects/video-production/renders-hyperframes/STEM
python3 projects/video-production/render-qa/src/plan_timing.py \
  projects/video-production/renders-hyperframes/STEM
bash scripts/build-gate.sh STEM
bash scripts/build-release.sh STEM
```

Narration is centrally queued at two videos at a time. The wrapper combines the
lesson into one HeyGen request when it fits below 4,800 characters, then splits
the returned audio and word timing into the same beat files the rest of the
pipeline expects. Longer lessons become the minimum number of whole-beat
chunks. Do not add a ten-minute stagger; the queue is the throttle.

## Render at two, then scale to four

Start cloud rendering with the default limit of two:

```bash
bash projects/video-production/run.sh limits
bash projects/video-production/run.sh ship STEM
```

Separate coordinator workers may issue `ship` for different approved stems.
The shared queue admits only two cloud renders at once; extra jobs wait.

After the complete batch review is approved and three consecutive cloud renders
pass verification, raise the limit:

```bash
bash projects/video-production/run.sh cloud-limit 4
bash projects/video-production/run.sh limits
```

The command refuses to raise the limit before both the full-set approval and the
3/3 clean streak. A later cloud-render failure resets the clean streak and
automatically returns the limit to two. To lower it manually at any time:

```bash
bash projects/video-production/run.sh cloud-limit 2
```

## Publish

After the required review and approval:

```bash
bash projects/video-production/run.sh ship STEM --publish
```

Publishing remains one at a time. This protects the Wistia upload record,
`published.tsv`, the refinement log, and the script move from conflicting
writes.

## Resume after an interruption

Start every fresh coordinator session with:

```bash
bash projects/video-production/run.sh resume
bash projects/video-production/run.sh limits
```

Then follow each item's `next` action in the JSON status. Never assign the same
stem to two cloud tasks and never bypass the TTS or cloud-render capacity queue.
