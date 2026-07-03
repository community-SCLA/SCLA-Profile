# `projects/` — active project work

Human-managed work in progress. **The pipeline does not touch this directory** — files here are never overwritten by agents.

## Subdirectories

| Directory | What goes here |
|---|---|
| `grants/` | Grant applications, funder research, award tracking |
| `campaigns/` | Outreach, recruitment, and marketing campaigns |
| `content/` | Newsletters, social posts, blog drafts, and content series |
| `programs/` | Active program development (**not** the KB reference at `../programs/`) |
| `video-production/` | AI video pipeline (scoped `CLAUDE.md`, script templates, status) |

## Standalone briefs

| File | What it is |
|---|---|
| `drive-review-brief.md` | Google Drive review brief |
| `kb-integration-plan.md` | Plan: wire `member-support/faqs.md` into Gmail / website / Slack / portal |

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

Type `/project` in Claude Code to create a new project file routed to the right subdirectory.
