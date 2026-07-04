# SCLA Profile — Company Knowledge Base

**Session boot:** match the task below, load the ONE file it names, stop.
No matching row? Open that folder's README.md hub (every multi-file folder has one) — never the whole folder.

## Task Routing

| Task | Load |
| --- | --- |
| SCLA facts — identity, scale, mission | `context/me.md` |
| Goals, priorities | `context/goals.md` |
| Brand colors, logo, type | `brand/visual-identity.md` |
| Voice & tone | `brand/voice-and-tone.md` |
| Naming, tagline | `brand/brand-guide.md` |
| Team member or role | `operations/team-roster.md` |
| Member-facing answer | `member-support/faqs.md` |
| Look up a program | `programs/programs-overview.md` |
| Develop a program | `programs/README.md` |
| Partner org | `partnerships/NIC.md` |
| Grant work | `projects/grants/` |
| Video production | `projects/video-production/CLAUDE.md` |
| HeyGen lesson script | `projects/video-production/templates/heygen-lesson-script.md` |
| Render HeyGen videos (code) | `projects/video-production/heygen-pipeline/CLAUDE.md` |
| Start a new project | `/new-from-template` |
| Where a fact lives | `MAP.md` |
| Structural change (read first) | `GOVERNANCE.md` |
| Why a decision was made | `decisions/log.md` |
| Integrations, endpoint IDs | `connections.md` · `endpoints.md` |

## Hard Rules

Full rulebook and all other rules: `GOVERNANCE.md`.
These two bind every session:
- **Never fabricate SCLA facts** — if it's not in the files, mark it `TODO: needs input`.
- **Never load or route to `_archive/`**

## Sync

```bash
./sync.sh   # main branch only; commits, pushes, updates workspace submodule
```
