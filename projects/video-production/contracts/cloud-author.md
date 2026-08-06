# Isolated Cloud Author

Build the source for exactly one assigned lesson in a Codex Cloud task. The
task ends before any paid service call or render. Do not inspect or edit another
lesson workspace.

## Inputs

- `STEM`: the assigned undated lesson stem
- `PROGRAM`: its lesson-script program folder
- narration: `lesson-scripts/PROGRAM/ready/STEM.txt`
- brand/runtime scaffold: `renders-hyperframes/_run/scaffold/`

## Do this

1. From the repository root, run:

   ```bash
   bash scripts/cloud-author.sh STEM PROGRAM
   ```

2. Read only the assigned narration and the new workspace's `tokens.yml`.
3. Create `CONCEPT.md`, `concept.json`, `design.md`, `audio_request.json`,
   `index.html`, and `index.motion.json`. Every narration line must copy the
   refined script exactly.
4. Give every beat a unique ID. Author the composition directly in HTML using
   tracked local source and the pinned scaffold. The root must have a positive
   duration and the required HyperFrames attributes; every narration beat must
   be a timed clip; one paused, seekable timeline must be registered under the
   exact composition ID. A Studio-loadable static shell is not a deliverable.
5. Run the one source-only review gate:

   ```bash
   bash scripts/cloud-review-ready.sh STEM
   ```

   This restores ignored scaffold assets, runs static SCLA preflight, and runs
   the pinned HyperFrames browser/runtime check. `REVIEW_READY: PASS` is the
   only successful handoff state. Cloud task completion without that line is a
   failed authoring attempt, not review-ready work.
6. Fix every finding, rerun the gate to `REVIEW_READY: PASS`, then commit only
   the assigned workspace's trackable source files and return the commit or
   pull-request link immediately. Never wait for sibling Cloud tasks.

## Stop here

Do not call HeyGen, generate narration, render, publish, write `run.json`, update
pipeline status, or use the live build claim/release scripts. The coordinator
does those after this isolated source change is merged.

Return:

```text
workspace: <relative path>
beats: <count>
review gate: PASS|FAIL
commit or PR: <reference>
```
