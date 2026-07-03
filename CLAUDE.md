# SCLA Profile — Company Knowledge Base

Living knowledge base for **The Society for Collegiate Leadership & Achievement (SCLA)**: brand, workflows, and source-of-truth documentation. This file routes tasks — find the row, load that one file, stop.

**Org identity (auto-inlined below):**

@context/me.md

**Session boot:** identify the task, load ONE target from the table.

## Task Routing

| I need to... | Load this |
| --- | --- |
| Know what SCLA is / org facts | `context/me.md` |
| Check goals or current priorities | `context/goals.md` |
| Look up brand colors, logo, type | `brand/visual-identity.md` |
| Write in SCLA's voice | `brand/voice-and-tone.md` |
| Check brand naming / tagline facts | `brand/brand-guide.md` |
| Find a team member or role | `operations/team-roster.md` |
| Answer a member-facing question | `member-support/faqs.md` |
| Look up a program | `programs/programs-overview.md` |
| Work on program development | `programs/README.md` (one subfolder per program) |
| Work with a partner org | `partnerships/NIC.md` |
| Work on a grant | `projects/grants/` (one folder per grant + RFP briefs) |
| Work on video production | `projects/video-production/CLAUDE.md` |
| Write a HeyGen lesson video script | `projects/video-production/templates/heygen-lesson-script.md` |
| Start a new project | `templates/README.md` + `/new-from-template` |
| Find where anything lives, and why | `MAP.md` |
| Make a structural change | `GOVERNANCE.md` — read it first |
| Review why a decision was made | `decisions/log.md` |
| Debug an integration | `connections.md` |
| Look up an endpoint ID / URL | `endpoints.md` |
| Trace a fact to its raw source | `_archive/source-dumps/README.md` (index only) |

No matching row? Every multi-file folder carries a README.md hub listing its contents — load that, not the whole folder.

## Hard Rules

Full rulebook and all other rules: `GOVERNANCE.md`. These two bind every session:

- **Never fabricate SCLA facts** — if it's not in the files, mark it `TODO: needs input`.
- **Never load or route to `_archive/`** — read-only provenance, reached only when explicitly tracing a `source:` citation.

## Sync

```bash
./sync.sh   # main branch only; commits, pushes, updates workspace submodule
```
