# `grants/` — grant applications and funder work

Active grant applications, funder research, and award tracking.

## What belongs here

- Grant applications (drafts and final submissions)
- Funder research notes
- Award notifications and follow-up

## Key sources to reference

- `scla/source-of-truth/mission.md` — mission statement and success criteria
- `scla/source-of-truth/program-names.md` — canonical program names (use these exactly)
- `scla/knowledge-base/` — SCLA history, FAQs, and org facts

## Status lifecycle

`draft` → `active` (in review) → `submitted` → `awarded` or `declined`

## Starting a new grant application

Run the script from this directory — it copies the template, names the file with today's date, and pre-fills the frontmatter:

```bash
cd scla/projects/grants
./new-grant.sh <short-name>
# e.g. ./new-grant.sh niche-foundation
# → creates 2026-05-11-niche-foundation.md
```
