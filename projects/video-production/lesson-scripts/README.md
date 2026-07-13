# Lesson Scripts — organized by program, state = folder

Narration **scripts**, one folder per program. The rendered video does **not**
live here: finished MP4s are uploaded to **Wistia** (account + auth status:
repo-root `endpoints.md` → "Wistia") and are not committed to the repo (see
[`decisions/log.md`](../../../decisions/log.md), 2026-07-08). This folder
tracks the durable source (the `.txt`); Wistia holds the build output.

## Structure — a script's location IS its state

```
lesson-scripts/
  <program-slug>/
    <stem>.txt            ← RAW intake — /refine-scripts' queue; do not render
    refined/<stem>.txt    ← refined + facts-checked — /render-lessons' BUILD queue
                            and the open human review buffer (edit/veto any time)
    rendered/<stem>.txt   ← published — MP4 filed in ../renders-mp4/ and on Wistia
```

Between `refined/` and `rendered/` a lesson's in-flight state lives outside
this folder: a `../renders-hyperframes/<stem>/` workspace = built, waiting at
the human **hyperframe gate**; an MP4 in `../renders-mp4/<program-slug>/` =
shipped, waiting at human **MP4 review**. No table needs consulting —
[`refinement-log.md`](refinement-log.md) is a ledger (history for humans),
never a decision input.

Create `refined/`/`rendered/` with their first file (`mkdir -p`), not ahead of
need. One subfolder per program; the slug matches its folder in
[`programs/`](../../../programs/). Live programs:

| Folder | Program |
|---|---|
| `early-career-boost/` | Early Career Boost |
| `career-readiness-accelerator/` | Career Readiness Accelerator |
| `scla-leadership-program/` | SCLA Leadership Program |

Add a new program folder only when it actually starts producing videos —
match the `programs/` slug and log it in `decisions/log.md` per
[GOVERNANCE.md](../../../GOVERNANCE.md).

## Naming convention

```
<section>_<program>_<date>
```

- **section** — the course section the video teaches, kebab-case: `brand-you-intro`, `smart-goals`, `hidden-job-market-1`.
- **program** — the program slug, matching the folder name: `early-career-boost`.
- **date** — for the `.txt`: capture/approval date; the stem stays unchanged as the file moves between state folders.

Underscores separate the three parts; hyphens go *inside* a part. The rendered
video reuses section+program but **swaps the date for the render date**, so a
video rendered well after its script doesn't carry a stale date — source and
deliverable stay traceable by section+program:

```
smart-goals_scla-leadership-program_2026-07-06.txt   ← refined/ (approved 07-06)
smart-goals_scla-leadership-program_2026-07-11        ← MP4 stem + Wistia title (rendered 07-11)
```

Lowercase throughout. No spaces, no `+`, no capitals — keeps filenames safe across shells, URLs, and Wistia titles.

## How scripts move

- **In:** a raw capture or draft lands at the program root. `/refine-scripts`
  drains roots into `refined/` (one subagent per script + qa-facts pass);
  scripts with open human questions stay at root with a ledger note.
- **Through:** `/render-lessons` BUILD drains `refined/` into hyperframe
  workspaces and stops at the human hyperframe gate; SHIP (per stem, on human
  go) renders + files the MP4 into [`../renders-mp4/`](../renders-mp4/README.md)
  for human MP4 review.
- **Out:** PUBLISH (per stem, on human go) uploads to Wistia, records the URL
  in the ledger, and `git mv`s the `.txt` to `rendered/`.
- The avatar path ([`../avatar-pipeline/`](../avatar-pipeline/CLAUDE.md))
  reads scripts from `refined/` via `config.json` and stages its MP4s in
  `avatar-pipeline/output/videos/`.

The `.txt` is plain spoken narration only (no cues, no shot list). Refinement
rules live in `/refine-scripts`; drafting prompt templates in
[`../script-templates/`](../script-templates/).
