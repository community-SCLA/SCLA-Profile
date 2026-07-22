# Renders (MP4) — organized by program, split by render path

Local staging for finished lesson-video MP4s — **both render paths file here**,
one folder per program, mirroring [`lesson-scripts/`](../lesson-scripts/README.md).
This is where a video lives after it's rendered and QA-passed, so it's viewable
locally before — and during — the Wistia upload. Gitignored: nothing here is
committed.

## Structure

```
renders-mp4/
  <program-slug>/
    hyperframes/   ← illustrated (HyperFrames) renders — /render-lessons SHIP
    avatar/        ← talking-head (HeyGen) renders — avatar-pipeline
      <stem>.mp4   ← local only, not committed
```

One subfolder per program (slug matches its folder in
[`../lesson-scripts/`](../lesson-scripts/README.md) and
[`programs/`](../../../programs/)); inside it, `hyperframes/` and `avatar/`
separate the two render paths so a program's two kinds of video never collide.
Subfolders are created with their first real render, not ahead of need (the
governance hook rejects empty placeholder dirs).

## Naming — universal `m<#>_<title>_<render-date>`

A render's filename is the **script stem with the date swapped to the date it
was rendered** — source and deliverable stay traceable, and a video rendered
well after its script doesn't carry a stale date. The stem is also the Wistia
title. The current scheme is `m<#>_<title-slug>_<render-date>`:

```
lesson-scripts/mid-career-momentum/refined/avatar/m1_the-value-of-building-mid-career-momentum_2026-07-20.txt   ← script, approved 07-20
renders-mp4/mid-career-momentum/avatar/m1_the-value-of-building-mid-career-momentum_2026-07-22.mp4              ← same video, rendered 07-22
```

- **m<#>** — the lesson's module number (`m1`, `m2`, …).
- **title-slug** — the video title, kebab-case (hyphens inside, no spaces/`+`/capitals).
- **render-date** — ISO `YYYY-MM-DD`, the date rendered.

Underscores separate the three parts; hyphens go *inside* a part. Lowercase
throughout — safe across shells, URLs, and Wistia titles. Older programs
(e.g. `early-career-boost`) keep their `<section>_<program>_<render-date>`
files as-is; the tooling handles both.

## Lifecycle

**Illustrated (HyperFrames):**
1. HyperFrames renders to `../renders-hyperframes/<script-stem>/renders/*.mp4`.
2. Once `verify_render.py` passes, the file is renamed (date → render date) and
   moved to `hyperframes/`.
3. Upload to Wistia (title = the filename's stem); record the URL in the ledger.
4. `scripts/archive-lesson.sh` checks a matching file exists here (by stem
   prefix, any render date) before it will archive the build workspace.

**Avatar (HeyGen):**
1. `avatar-pipeline/generate_videos.py` renders each lesson (concatenating its
   HeyGen chunks into one video) straight into `avatar/` under this program.
2. Human MP4 review, then upload to Wistia; record the URL in the ledger.

Files can stay here after upload — a free local backup of the delivered cut.
