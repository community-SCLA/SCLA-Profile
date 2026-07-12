# Lesson Scripts — organized by program

Approved narration **scripts**, filed one folder per program. This is the curated library and single source of truth for scripts — a script lands here as soon as it's approved. The rendered video does **not** live here: finished MP4s are uploaded to **Wistia** (`sclc.wistia.com`) and are not committed to the repo (see [`decisions/log.md`](../../../decisions/log.md), 2026-07-08). The Wistia link is recorded on the video's Notion queue row (**Final video** field). This folder tracks the durable source (the `.txt`); Wistia holds the build output.

**Before rendering a script, check [`refinement-log.md`](refinement-log.md)** — it tracks each script's created/refined/rendered dates so agents can tell which `.txt` files are actually render-ready vs. still raw platform captures.

## Structure

```
lesson-scripts/
  <program-slug>/
    <section>_<program>_<date>.txt    ← approved narration script (tracked)
                                       ← video → Wistia (not in git); link on the Notion row
```

One subfolder per program; the slug matches its folder in [`programs/`](../../../programs/). Live programs:

| Folder | Program |
|---|---|
| `early-career-boost/` | Early Career Boost |
| `career-readiness-accelerator/` | Career Readiness Accelerator |
| `scla-leadership-program/` | SCLA Leadership Program |

Add a new folder only when a program actually starts producing videos — match the `programs/` slug, and log it in [`decisions/log.md`](../../../decisions/log.md) per [GOVERNANCE.md](../../../GOVERNANCE.md).

## Naming convention

```
<section>_<program>_<date>
```

- **section** — the course section the video teaches, kebab-case: `brand-you-intro`, `smart-goals`, `hidden-job-market-1`.
- **program** — the program slug, matching the folder name: `early-career-boost`.
- **date** — production/render date, ISO `YYYY-MM-DD`.

Underscores separate the three parts; hyphens go *inside* a part. The rendered video reuses the script's section and program, but **swaps the date for
the render date** — not the script's approval date — so a video rendered well after
its script was approved doesn't carry a stale date. Source and deliverable stay
traceable by section+program even when the dates differ:

```
smart-goals_scla-leadership-program_2026-07-06.txt   ← here, in git (approved 07-06)
smart-goals_scla-leadership-program_2026-07-11        ← Wistia video title (rendered 07-11)
```

Lowercase throughout. No spaces, no `+`, no capitals — keeps filenames safe across shells, URLs, and Wistia titles.

## How scripts and videos land here

- **The script comes first.** Once narration is approved (script → render is a manual gate — see `../CLAUDE.md`), save it directly here as `<section>_<program>_<date>.txt` — this is its permanent home. `avatar-pipeline/config.json` points at the file here to render it.
- **The rendered video goes to Wistia, not here — it never lands in this folder.** Both build paths produce an MP4 locally in their own staging spot first: the [avatar pipeline](../avatar-pipeline/CLAUDE.md) downloads to `avatar-pipeline/output/videos/`; HyperFrames renders file to [`../renders-mp4/<program-slug>/`](../renders-mp4/README.md) (named with the render date, not the script's date — see that folder's README). At the publish gate, upload from there to Wistia (title = the filed MP4's stem) and paste the Wistia URL into the Notion row's **Final video** field. `.gitignore` also blocks `lesson-scripts/**/*.mp4` as a backstop.

The `.txt` here is the plain spoken narration (no cues, no shot list) — the same text the avatar read. See [`script-templates/heygen-narration-prompt.md`](../script-templates/heygen-narration-prompt.md) for producing it.
