# Video Request Queue (Notion) — retired

> **⚠️ RETIRED AS INTAKE — 2026-07-13.** Do not work this queue as a request
> pipeline. Scripts enter as `.txt` files in
> `lesson-scripts/<program-slug>/inbox/` and flow `inbox/` → `ready/` →
> `published/` via `/refine-scripts` → `/render-lessons` (see `../CLAUDE.md` →
> Task Routing).

## What Notion is still for

One thing: it holds links to some delivered lessons, for people who live in
Notion. It is a **copy**, never a source.

The receipt lives in the repo:

- `lesson-scripts/published.tsv` — the machine key. A stem is published if and
  only if it has a row here.
- `../PIPELINE-STATUS.md` → **Delivered** — the same rows as a human-readable
  table with clickable Wistia links and local MP4 paths. Generated; never
  hand-edited.
- `lesson-scripts/refinement-log.md` — the human ledger (dates, per-script
  notes, findings).

**Database:** [SCLA Video Production Queue](https://app.notion.com/p/280a361540ab4fd6a0267c5fbea1e6bd)
(data source `collection://e99fc1e7-d9a1-4be9-9bda-b9d79ef9ae57`), a child of the
"SCLA Workspace" hub page.

## Automation — repointed 2026-07-22

The scheduled routine that used to poll this queue (claude.ai cloud, ID + URL in
`config/endpoints.json` → "Claude Code routines") is now named **"SCLA lesson
pipeline worker"**, runs hourly, and does not touch Notion at all — it runs
`/produce-video` against the `.txt` intake above. It never ships or publishes;
those stay human-triggered. See `config/endpoints.json` for the current config
and `decisions/log.md` (2026-07-22) for why.

## Why the rest of this file is gone (2026-08-04)

It used to carry the whole Notion flow: a **nine-status model** (Requested →
Script drafting → … → Delivered → Blocked), its own priority order (Rush → High
→ Normal → Low), its own style-package rotation formula, and its own
artifact-location table.

Every one of those was a second answer to a question the live pipeline already
answers, and by 2026-08-04 each had drifted from it:

| It said | The live answer |
|---|---|
| nine Notion statuses | the folder names — `inbox/` → `ready/` → `published/`, plus the workspace stages `batch-status.sh` derives |
| Rush → High → Normal → Low | `scripts/batch-status.sh:28`, the one definition of priority, overridable with `VIDEO_PRIORITY` |
| rotate by delivered `.mp4` count | `render-qa/src/theme_for.py <program-slug>` |
| approved script at `lesson-scripts/<program-slug>/<stem>.txt` | `lesson-scripts/<program-slug>/ready/<base>.txt`, no date |
| final video linked on the Notion row | `published.tsv` + the *Delivered* table |

A retired document that still describes a live process is not history, it is a
competing instruction set — and a cold subagent has no way to tell which of two
plausible models it is holding. The old flow is in git history, which is the
archive. This banner is what remains.
