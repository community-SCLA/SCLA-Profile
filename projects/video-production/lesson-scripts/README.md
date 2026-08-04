# Lesson Scripts — organized by program, state = folder

Narration **scripts**, one folder per program. The rendered video does **not**
live here: finished MP4s stage locally in `../renders-mp4/` and are uploaded to
**Wistia**, not committed to the repo (see
[`decisions/log.md`](../../../decisions/log.md), 2026-07-08). This folder
tracks the durable source (the `.txt`); Wistia holds the build output.

## Structure — a script's location IS its state

```
lesson-scripts/
  <program-slug>/
    inbox/<stem>.txt        ← RAW — captured, not yet refined; /refine-scripts' queue
    ready/<stem>.txt        ← READY — refined + approved; /render-lessons' BUILD queue,
                              and the open human review buffer (edit/veto any time)
    published/<stem>.txt    ← PUBLISHED — live on Wistia, with a published.tsv row
```

**The folder name IS the stage name** (2026-08-04). Three folders, three
stages, same words — no folder means something other than what it is called,
and **a raw script is never left loose at the program root**: it goes in
`inbox/`. `lint-refs.sh` check 13 fails a program that breaks either rule.

There is one route now. The `avatar/` and `refined/avatar/` subfolders — the
HeyGen talking-head lane — were deleted 2026-08-04 with the rest of that lane;
every lesson here is illustrated (HyperFrames). A lesson that genuinely needs a
human face is a HeyGen web-UI job the owner does by hand, outside this tree.

Between `ready/` and `published/`, a lesson's in-flight state lives outside this
folder, in its `../renders-hyperframes/<stem>/` workspace — read it with `bash
scripts/batch-status.sh`, or open the generated `../PIPELINE-STATUS.md`, which
also carries the Wistia link for everything delivered.
[`refinement-log.md`](refinement-log.md) is a ledger (history for humans), never
a decision input.

**Live programs are whatever `ls` of this folder shows** — one subfolder per
program, no hand-maintained list (don't write down what the file tree already
says). A new program starts with all three folders, so nothing has to remember
to create them mid-flight. Add one only when it actually starts producing
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
carries no date at all** — the `inbox/` script, the `ready/` script, the build
workspace and the `published/` script all share one name, which never changes as
the file moves between state folders. That name is therefore the lesson's
identity, and `mkdir renders-hyperframes/<name>` is what stops two concurrent
build agents landing on the same lesson.

Only the delivered MP4 gains a date, the date it was rendered — a fact about an
event that happened once, frozen at publish:

```
m1_the-value-of-building-mid-career-momentum.txt          ← inbox/ ready/ published/
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

- **In:** a raw capture or draft lands in `inbox/`. `/refine-scripts`
  drains `inbox/` into `ready/` (one subagent per script + qa-facts pass);
  scripts with open human questions stay in `inbox/` with a ledger note.
- **Through:** `/render-lessons` BUILD drains `ready/` into hyperframe
  workspaces and **stops at the human hyperframe gate** — a human previews
  every hyperframe before any MP4 exists.
- **Out:** an explicit `ship <stem>` (the one human trigger after the gate)
  renders, verifies, files the MP4 in
  [`../renders-mp4/<program-slug>/`](../renders-mp4/README.md), and publishes
  to Wistia **in one uninterrupted pass** — no separate MP4-review or publish
  step (gate removed 2026-07-22, `decisions/log.md`). The Wistia URL is
  recorded in `published.tsv` and the ledger, and the `.txt` moves to
  `published/` in that same pass.

The `.txt` is plain spoken narration only (no cues, no shot list). Refinement
rules live in `/refine-scripts`; drafting prompt templates in
[`../script-templates/`](../script-templates/).
