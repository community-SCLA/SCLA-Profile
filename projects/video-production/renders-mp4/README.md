# Renders (MP4) — organized by program

Local staging for finished **HyperFrames-rendered MP4s**, filed one folder per
program, mirroring [`lesson-scripts/`](../lesson-scripts/README.md). This is where a
video lives after it's rendered and QA-passed, so it's viewable locally before — and
during — the Wistia upload. Gitignored: nothing here is committed.

For avatar-rendered (HeyGen) videos, see `avatar-pipeline/output/videos/` instead —
this folder is for the illustrated/HyperFrames path only.

## Structure

```
renders-mp4/
  <program-slug>/
    <section>_<program>_<render-date>.mp4   ← local only, not committed
```

One subfolder per program; the slug matches its folder in
[`../lesson-scripts/`](../lesson-scripts/README.md) and [`programs/`](../../../programs/).

## Naming — render date, not script date

The script that seeds a video is named `<section>_<program>_<script-date>.txt` (the
date it was approved). The MP4 filed here reuses the section and program but swaps in
**the date it was rendered**, not the script's date — the two can differ when a video
is rendered well after its script was approved.

```
lesson-scripts/scla-leadership-program/smart-goals_scla-leadership-program_2026-07-06.txt   ← script, approved 07-06
renders-mp4/scla-leadership-program/smart-goals_scla-leadership-program_2026-07-11.mp4       ← same video, rendered 07-11
```

The MP4's stem is also its Wistia title.

## Lifecycle

1. HyperFrames renders to `../renders-hyperframes/<script-stem>/renders/*.mp4` (the
   build workspace).
2. Once `verify_render.py` and the `/adversarial-qa` gauntlet pass, the file is renamed
   to `<section>_<program>_<render-date>` and moved here.
3. Upload to Wistia (title = the filename's stem); paste the Wistia URL into the
   Notion row's **Final video** field.
4. `scripts/archive-lesson.sh` checks a matching file exists here (by section+program,
   any render date) before it will archive the build workspace.

The file can stay here after upload too — it's a free local backup of the delivered
cut, same as `../renders-hyperframes/_archive/` keeps the source workspace.
