# HyperFrames Render Workspaces — local only, not in git

Per-video HyperFrames build workspaces for the illustrated-video path. Everything
here except this README is **gitignored** (root `.gitignore`): a workspace is
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
2. **Delivered:** once the final MP4 is verified and filed in
   `../lesson-scripts/<program-slug>/`, run from the repo root:

   ```bash
   bash scripts/archive-lesson.sh <script-stem>
   ```

   This moves the workspace to `renders-hyperframes/_archive/<script-stem>/` and deletes the
   regenerable bulk (`node_modules/`, `.thumbnails/`, `.waveform-cache/`,
   `.hyperframes/`, `snapshots/`, `renders/`, logs). What remains — `index.html`,
   `compositions/`, `frame.md`, `assets/`, configs — is a complete, re-renderable
   source: `npm install && npm run render` brings it back.

`renders-hyperframes/` should only ever contain this README, workspaces currently in
production, and `_archive/`. If a folder sits here for a video that's already
delivered, archive it.

## What lives where (durable vs. scaffolding)

| Artifact | Home | In git? |
|---|---|---|
| Approved narration script `.txt` | `../lesson-scripts/<program-slug>/` | Yes |
| Final `.mp4` | `../lesson-scripts/<program-slug>/` (+ linked on the Notion row) | No — gitignored; the Wistia upload is the durable copy |
| QA snapshots / progress | Posted to the video's Notion page | No (Notion) |
| Scene HTML + build sources | `renders-hyperframes/<stem>/` → `renders-hyperframes/_archive/<stem>/` after delivery | No (local) |
| Scene *templates* (reusable) | `../design-system/compositions/` | Yes |

**Note:** because workspaces are local-only, they exist on the machine that built
them. That's acceptable — the approved script (tracked) plus the design-system
templates (tracked) can reproduce any video; the archive just saves the
re-assembly work.

This `_archive/` is the video project's local build archive — it is not the
repo-root `_archive/` (read-only provenance) and is never a routing target.
