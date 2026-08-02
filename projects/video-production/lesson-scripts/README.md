# Lesson Scripts — organized by program, state = folder

> **The pipeline this folder fed was retired 2026-08-02.** The script library is
> live and unchanged, but every skill and script named below (`/refine-scripts`,
> `/render-lessons`, `/produce-video`, the `../renders-*` staging trees) now sits
> under `../_archive/` and does not run. The raw → `refined/` → `rendered/`
> convention still describes what is on disk, so it is kept as written.

Narration **scripts**, one folder per program. The rendered video does **not**
live here: finished MP4s stage locally in `../renders-mp4/` and are uploaded to
**Wistia**, not committed to the repo (see
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
    refined/avatar/<stem>.txt  ← refined — HeyGen web UI queue (talking-head)
    rendered/<stem>.txt     ← gate-clean build exists — MP4 filed in ../renders-mp4/
                              (and on Wistia once shipped)
```

**Render route is also a location.** Program root / `refined/` = illustrated
(HyperFrames); the `avatar/` and `refined/avatar/` subfolders = talking-head
(HeyGen, rendered manually via the HeyGen web UI — the batch/resumable code
path was removed 2026-08-02). The two queues never mix: `/render-lessons`
builds only the `refined/` root. `/refine-scripts` preserves the split (root →
`refined/`, `avatar/` → `refined/avatar/`).

Between `refined/` and shipped, an illustrated lesson's in-flight state lives
outside this folder: a `../renders-hyperframes/<stem>/` workspace = built,
waiting at the human **hyperframe gate**; a Wistia URL in
[`refinement-log.md`](refinement-log.md) = published. The log is a ledger
(history for humans), never a decision input.

**Live programs are whatever `ls` of this folder shows** — one subfolder per
program, no hand-maintained list (don't write down what the file tree already
says). Create `refined/`/`rendered/` with their first file (`mkdir -p`), not
ahead of need. Add a new program folder only when it actually starts producing
videos, and log it in `decisions/log.md`.

## Naming convention

Current scheme (program is now the folder, so it drops out of the filename):

```
m<#>_<title>              working artifacts — NO date
m<#>_<title>_<date>.mp4   the delivered MP4 only — the render date
```

- **m<#>** — the lesson's module number: `m1`, `m2`, … (a lesson AKA "module").
- **title** — the video title, kebab-case: `the-value-of-building-mid-career-momentum`.

Underscores separate the parts; hyphens go *inside* a part. **A working artifact
carries no date at all** — the raw script, the `refined/` script, the build
workspace and the `rendered/` script all share one name, which never changes as
the file moves between state folders. That name is therefore the lesson's
identity, and `mkdir renders-hyperframes/<name>` is what stops two concurrent
build agents landing on the same lesson.

Only the delivered MP4 gains a date, the date it was rendered — a fact about an
event that happened once, frozen at publish:

```
m1_the-value-of-building-mid-career-momentum.txt          ← raw / refined/ / rendered/
m1_the-value-of-building-mid-career-momentum_2026-07-22.mp4  ← the delivered video
```

"When was this last acted on" is mtime; the filesystem tracks it and cannot
drift. (Changed 2026-07-29 — the old scheme restamped every artifact at every
transition, and a name that moves cannot be a lock. See `decisions/log.md`.)

Lowercase throughout. No spaces, no `+`, no capitals — keeps filenames safe
across shells, URLs, and Wistia titles.

> **Older program** `early-career-boost/` uses the previous
> `<section>_<program>` scheme (section kebab-case; program = the folder slug).
> Its existing files keep it; the tooling reads both. Use `m<#>_<title>` for new
> programs. `stem.py base` also still accepts any legacy dated name, so an
> artifact that predates 2026-07-29 keys correctly wherever one survives.

## How scripts move

- **In:** a raw capture or draft lands at the program root. `/refine-scripts`
  drains roots into `refined/` (one subagent per script + qa-facts pass);
  scripts with open human questions stay at root with a ledger note.
- **Through:** `/render-lessons` BUILD drains `refined/` into hyperframe
  workspaces and **stops at the human hyperframe gate** — a human previews
  every hyperframe before any MP4 exists.
- **Out:** an explicit `ship <stem>` (the one human trigger after the gate)
  renders, verifies, files the MP4 in
  [`../renders-mp4/<program-slug>/`](../renders-mp4/README.md), and publishes
  to Wistia **in one uninterrupted pass** — no separate MP4-review or publish
  step (gate removed 2026-07-22, `decisions/log.md`). The Wistia URL is
  recorded in the ledger and the `.txt` sits in `rendered/`.
- The avatar path reads scripts from `refined/avatar/` manually via the HeyGen
  web UI (the batch/resumable code path, `avatar-pipeline/`, was removed
  2026-08-02), rendering each lesson as one talking-head video staged in
  [`../renders-mp4/<program-slug>/avatar/`](../renders-mp4/README.md).

The `.txt` is plain spoken narration only (no cues, no shot list). Refinement
rules live in `/refine-scripts`; drafting prompt templates in
[`../script-templates/`](../script-templates/).
