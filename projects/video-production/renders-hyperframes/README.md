# HyperFrames Render Workspaces

Per-video HyperFrames build workspaces for the illustrated-video path: a workspace is
scaffolding — HTML scene files, TTS audio, caches — and the durable outputs it
produces are filed elsewhere (see "What lives where" below).

## Lifecycle

```
renders-hyperframes/
  <script-stem>/            ← ACTIVE build (one folder per video, named after its script)
  _archive/
    <script-stem>/          ← DELIVERED builds, pruned of caches, kept for re-edits
```

1. **Active:** `design-system/CLAUDE.md` → "Building a lesson video" scaffolds
   `renders-hyperframes/<script-stem>/` (stem = the approved script's filename in
   `../lesson-scripts/<program-slug>/`).
2. **Delivered:** the workspace **stays put after publish**. Archiving is a
   human-only call — no skill, hook, or agent step retires a build on its own.
   When you want the disk back, run from the repo root:

   ```bash
   bash scripts/archive-lesson.sh <script-stem>
   ```

   This moves the workspace to `renders-hyperframes/_archive/<script-stem>/` and deletes the
   regenerable bulk (`node_modules/`, `.thumbnails/`, `.waveform-cache/`,
   `.hyperframes/`, `snapshots/`, `renders/`, logs). What remains — `index.html`,
   `compositions/`, `design.md`, `tokens.yml`, `assets/`, configs — is a complete,
   re-renderable source: `npm install && npm run render` brings it back.

`renders-hyperframes/` contains this README, workspaces (in production *and*
delivered), `_run/` (the scaffold every workspace is copied from), `_reference/`
(builds kept as measurement evidence) and `_archive/`. Underscore folders are
skipped by every workspace scan, which is what keeps them out of the queue.
Delivered folders lingering at the root are expected — they are only cleared
when a human runs `archive-lesson.sh`.

## What lives where (durable vs. scaffolding)

| Artifact | Home | In git? |
|---|---|---|
| Approved narration script `.txt` | `../lesson-scripts/<program-slug>/ready/` → `published/` at publish | Yes |
| Final `.mp4` | `../renders-mp4/<program-slug>/<stem>_<render-date>.mp4` | No — gitignored; the Wistia upload is the durable copy |
| The Wistia URL | `../lesson-scripts/published.tsv` (machine) + the *Delivered* table in `../PIPELINE-STATUS.md` (human) | Yes |
| QA frames / snapshots | `renders-hyperframes/<stem>/qa/`, pruned in place after publish | No (local) |
| Build journal | `renders-hyperframes/<stem>/.build-log.tsv` — one row per completed step | No (local) |
| Scene HTML + build sources | `renders-hyperframes/<stem>/`; retiring one to `_archive/<stem>/` is a human-only call | No (local) |
| Scene *templates* (reusable) | `../design-system/compositions/` | Yes |

*(Corrected 2026-08-04: this table used to file the final MP4 under
`lesson-scripts/<program-slug>/` — which holds only `.txt` — and route QA
snapshots to Notion, which was retired as intake on 2026-07-13.)*

**Note:** because workspaces are local-only, they exist on the machine that built
them. That's acceptable — the approved script (tracked) plus the design-system
templates (tracked) can reproduce any video; the archive just saves the
re-assembly work.

This `_archive/` is the video project's local build archive — it is not the
repo-root `_archive/` (read-only provenance) and is never a routing target.
