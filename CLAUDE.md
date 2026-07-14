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
| Produce a video (one call; stops at the hyperframe gate) | `/produce-video` |
| Refine raw lesson scripts (batch) | `/refine-scripts` |
| Build / ship / publish lesson videos | `/render-lessons` |
| Wistia links in Notion (intake retired 2026-07-13) | `projects/video-production/notion-queue.md` |
| Illustrated lesson video (default) | `projects/video-production/design-system/CLAUDE.md` |
| HeyGen lesson script | `projects/video-production/script-templates/heygen-lesson-script.md` |
| Render HeyGen videos (code) | `projects/video-production/avatar-pipeline/CLAUDE.md` |
| Start a new project | `/new-from-template` |
| Where a fact lives | `MAP.md` |
| Structural change (read first) | `GOVERNANCE.md` |
| Why a decision was made | `decisions/log.md` |
| Integrations, endpoint IDs | `endpoints.md` |

## Hard Rules

Full rulebook and all other rules: `GOVERNANCE.md`.
These two bind every session:

- **Never load or route to `_archive/`**

## Tool usage discipline (context budget)
- Read files with the Read tool, not `cat`/`head`/`tail`. Read specific line ranges when you know roughly where to look.
- Use plain `ls` scoped to ONE directory. No `ls -la`, no recursive/whole-tree listings.
- Use Grep/Glob for searching, not `find` or `grep` in Bash.
- Never re-read a file already read this session.
