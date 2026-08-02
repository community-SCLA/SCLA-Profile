# `projects/` — active project work

Human-managed work in progress. **No pipeline writes here** — files are never overwritten by agents.

## Subdirectories

**Live subdirectories are whatever `ls` of this folder shows** — don't write down what the file tree already says. As of 2026-08-02:

| Directory | What goes here |
|---|---|
| `grants/` | Grant applications, funder research, award tracking (`new-grant.sh` scaffolds one) |
| `video-production/` | Lesson script library + the four design-system essentials. The illustrated-lesson pipeline retired 2026-08-02 — see root `CLAUDE.md` |

New project types get a new subdirectory here rather than a new folder at the repo root.

## File naming

```
YYYY-MM-DD-short-name.md
```

Example: `2026-05-11-niche-grant-application.md`

## Frontmatter

Every file in `projects/` uses human-managed frontmatter (not pipeline frontmatter):

```yaml
---
type: grant | campaign | content | program
status: draft | active | submitted | complete | archived
owner: <name>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
---
```

## Templates

Use the matching template from `../templates/`:

| Project type | Template |
|---|---|
| Grant application | `templates/project-grant.md` |
| Campaign | `templates/project-campaign.md` |
| Content project | `templates/project-content.md` |
| Program development | `templates/project-program.md` |

## Routing via Claude

Run `/new-from-template` in Claude Code to create a new project file routed to the right subdirectory.
