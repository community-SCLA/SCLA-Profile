# Renders (MP4) — organized by program

Local staging for finished lesson-video MP4s — one folder per program, mirroring [`lesson-scripts/`](../lesson-scripts/README.md).
This is where a video lives after it's rendered and QA-passed, so it's viewable
locally before — and during — the Wistia upload. Gitignored: nothing here is
committed.

## Structure

```
renders-mp4/
  <program-slug>/
    <stem>_<render-date>.mp4   ← local only, not committed
```

One folder per program (slug matches its folder in
[`../lesson-scripts/`](../lesson-scripts/README.md) and
[`programs/`](../../../programs/)), and the MP4s sit directly in it. The
per-lane `hyperframes/` and `avatar/` subfolders were flattened away on
2026-08-04: they existed only to keep two render paths apart, and the avatar
lane was deleted. Program folders are created with their first real render, not
ahead of need.

## Naming — universal `m<#>_<title>_<render-date>`

A render's filename is the **script stem with the date swapped to the date it
was rendered** — source and deliverable stay traceable, and a video rendered
well after its script doesn't carry a stale date. The stem is also the Wistia
title. The current scheme is `m<#>_<title-slug>_<render-date>`:

```
lesson-scripts/mid-career-momentum/ready/m1_the-value-of-building-mid-career-momentum.txt          ← the script — no date, ever
renders-mp4/mid-career-momentum/m1_the-value-of-building-mid-career-momentum_2026-07-22.mp4        ← the delivered video, rendered 07-22
```

- **m<#>** — the lesson's module number (`m1`, `m2`, …).
- **title-slug** — the video title, kebab-case (hyphens inside, no spaces/`+`/capitals).
- **render-date** — ISO `YYYY-MM-DD`, the date rendered.

Underscores separate the three parts; hyphens go *inside* a part. Lowercase
throughout — safe across shells, URLs, and Wistia titles. Older programs
(e.g. `early-career-boost`) keep their `<section>_<program>_<render-date>`
files as-is; the tooling handles both.

## Lifecycle

1. HyperFrames renders to `../renders-hyperframes/<script-stem>/renders/*.mp4`.
2. Once `verify_render.py` passes, `batch-ship.sh --publish` copies exactly that
   verified file here, adding the render date to its name.
3. Upload to Wistia (title = the filename's stem); the URL is recorded in
   `published.tsv` and the ledger in the same commit.
4. `scripts/archive-lesson.sh` checks a matching file exists here (by stem
   prefix, any render date) before it will prune or archive the build
   workspace.

Files can stay here after upload — a free local backup of the delivered cut.
