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
3. Create `CONCEPT.md`, `concept.json`, `design.md`, `audio_request.json`, and
   `index.html`. Every narration line must copy the refined script exactly.
4. Give every beat a unique ID. Author the composition directly in HTML using
   tracked local source and the pinned scaffold.
5. Run the source-only check:

   ```bash
   python3 projects/video-production/render-qa/src/preflight.py \
     projects/video-production/renders-hyperframes/STEM --static
   ```

6. Fix source findings, then commit only the assigned workspace's trackable
   source files and return the commit or pull-request link.

## Stop here

Do not call HeyGen, generate narration, render, publish, write `run.json`, update
pipeline status, or use the live build claim/release scripts. The coordinator
does those after this isolated source change is merged.

Return:

```text
workspace: <relative path>
beats: <count>
static preflight: PASS|FAIL
commit or PR: <reference>
```
