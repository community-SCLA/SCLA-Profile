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
    <stem>.txt              ← RAW intake, illustrated route — /refine-scripts' queue
    avatar/<stem>.txt       ← RAW intake, HeyGen-avatar route — /refine-scripts' queue
    refined/<stem>.txt      ← refined — /render-lessons' BUILD queue (illustrated)
                              and the open human review buffer (edit/veto any time)
    refined/avatar/<stem>.txt  ← refined — avatar-pipeline's queue (talking-head)
    rendered/<stem>.txt     ← published — MP4 filed in ../renders-mp4/ and on Wistia
```

**Render route is also a location.** Program root / `refined/` = illustrated
(HyperFrames); the `avatar/` and `refined/avatar/` subfolders = talking-head
(HeyGen, `../avatar-pipeline/`). The two queues never mix: `/render-lessons`
builds only the `refined/` root, `avatar-pipeline/config.json` points only into
`refined/avatar/`. `/refine-scripts` preserves the split (root → `refined/`,
`avatar/` → `refined/avatar/`).

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

Current scheme (program is now the folder, so it drops out of the filename):

```
m<#>_<title>_<date>
```

- **m<#>** — the lesson's module number: `m1`, `m2`, … (a lesson AKA "module").
- **title** — the video title, kebab-case: `the-value-of-building-mid-career-momentum`.
- **date** — for the `.txt`: capture/approval date; the stem stays unchanged as the file moves between state folders.

Underscores separate the three parts; hyphens go *inside* a part. The rendered
video reuses `m<#>`+title but **swaps the date for the render date**, so a video
rendered well after its script doesn't carry a stale date — source and
deliverable stay traceable by module+title:

```
m1_the-value-of-building-mid-career-momentum_2026-07-20.txt   ← refined/avatar/ (approved 07-20)
m1_the-value-of-building-mid-career-momentum_2026-07-22       ← MP4 stem + Wistia title (rendered 07-22)
```

Lowercase throughout. No spaces, no `+`, no capitals — keeps filenames safe
across shells, URLs, and Wistia titles.

> **Older programs** (`early-career-boost`, `career-readiness-accelerator`,
> `scla-leadership-program`) use the previous `<section>_<program>_<date>`
> scheme (section kebab-case; program = the folder slug). Their existing files
> keep it; the tooling reads both. Use `m<#>_<title>_<date>` for new programs.

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
  reads scripts from `refined/avatar/` via `config.json`, renders each lesson as
  one talking-head video, and stages the MP4 in
  [`../renders-mp4/<program-slug>/avatar/`](../renders-mp4/README.md).

The `.txt` is plain spoken narration only (no cues, no shot list). Refinement
rules live in `/refine-scripts`; drafting prompt templates in
[`../script-templates/`](../script-templates/).
