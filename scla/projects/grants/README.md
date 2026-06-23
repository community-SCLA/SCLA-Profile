# `grants/` — grant applications and funder work

Active grant applications, funder research, and award tracking.

## What belongs here

- Grant applications (drafts and final submissions)
- Funder research notes
- Award notifications and follow-up

## Key sources to reference

- `context/me.md` — org identity, mission, founding facts
- `context/goals.md` — mission and success criteria
- `scla/programs/programs-overview.md` — program names (use these exactly)
- `scla/member-support/` — FAQs and org facts

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
