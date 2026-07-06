# Video Library — organized by program

Finished lesson videos and the approved scripts that produced them, filed one folder per program. This is the curated library — the durable home for a video once it's rendered and approved, whether it came from the [code pipeline](../heygen-pipeline/CLAUDE.md) or the HeyGen web UI.

## Structure

```
videos/
  <program-slug>/
    <section>_<program>_<date>.txt    ← approved narration script
    <section>_<program>_<date>.mp4    ← rendered video
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

Underscores separate the three parts; hyphens go *inside* a part. A video and its script share the same stem, differing only by extension — so they sort next to each other:

```
smart-goals_scla-leadership-program_2026-07-06.txt
smart-goals_scla-leadership-program_2026-07-06.mp4
```

Lowercase throughout. No spaces, no `+`, no capitals — keeps filenames safe across shells, URLs, and hosting platforms.

## How videos land here

- **From the code pipeline** — [`heygen-pipeline/`](../heygen-pipeline/CLAUDE.md) renders to its own `output/videos/lesson-*.mp4` staging area. Once a render is approved, rename it to the convention above and move it (with its `.txt`) into the matching program folder.
- **From the HeyGen web UI** — download the MP4 and save it here directly under the right program folder, alongside the approved script.

The approved `.txt` here is the plain spoken narration (no cues, no shot list) — the same text the avatar read. See [`templates/heygen-narration-prompt.md`](../templates/heygen-narration-prompt.md) for producing it.
