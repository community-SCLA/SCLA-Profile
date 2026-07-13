# Endpoints Registry

Frequently used IDs, URLs, and paths across all automations and sessions.
Update here first — scripts and skills should read from here, not from hardcoded values.

> **Do not invent IDs — unknown values stay `TODO: needs input` until confirmed.**

> **Related:** Auth methods and connection status → `connections.md`

---

## Google Drive

| Name | Type | ID / URL | Used By |
|---|---|---|---|
| Git→Drive mirror target | Folder | `TODO: needs input` | `.github/workflows/drive-sync.yml` (Git→Drive sync) |

> **Git→Drive mirror config** (see `references/google-drive-api.md`):
> - GitHub **variable** `GDRIVE_TARGET` = `<rclone-remote>:<folder>`, e.g. `gdrive:SCLA-Profile`.
> - GitHub **secret** `RCLONE_CONF_BASE64` = base64 of an `rclone.conf` authorized as `community@thescla.org`.
> - Folder ID above: open the target folder in Drive → copy the string after `/folders/` in the URL. Stays `TODO: needs input` until confirmed.

---

## Wistia

| Name | Type | ID / URL | Used By |
|---|---|---|---|
| SCLA Wistia account | Account | https://sclc.wistia.com | lesson-video hosting + analytics — `/render-lessons` PUBLISH, `avatar-pipeline/` delivery |
| Lesson videos project/folder | Project | `TODO: needs input` | where uploaded lessons are filed in Wistia |
| Upload API token | — | `TODO: needs input` (goes in `.env` as `WISTIA_API_TOKEN`, never here) | not wired — until then, uploads are manual via the web UI (`connections.md`: not connected) |

> Video title = the filed MP4 stem `<section>_<program-slug>_<render-date>`.
> The Wistia URL of a published lesson is recorded in
> `projects/video-production/lesson-scripts/refinement-log.md` (ledger row).

---

## GitHub

| Name | Path | Notes |
|---|---|---|
| This repo | `community-SCLA/SCLA-Profile` | Main branch: `main` |

---

## Notion

| Name | Type | ID / URL | Used By |
|---|---|---|---|
| SCLA Video Production Queue | Database | `280a3615-40ab-4fd6-a026-7c5fbea1e6bd` · https://app.notion.com/p/280a361540ab4fd6a0267c5fbea1e6bd | `projects/video-production/notion-queue.md` |
| SCLA Video Production Queue | Data source | `collection://e99fc1e7-d9a1-4be9-9bda-b9d79ef9ae57` | queue queries (`notion-query-data-sources`) |
| How to Request a Video | Page | https://app.notion.com/p/3968dcf30bdb81bbb0ddecc352b23e22 | team instructions for the queue |
| SCLA Workspace (team hub) | Page | `3668dcf3-0bdb-808e-9891-f99ec02f73dd` | parent of the queue + how-to page |

---

## Claude Code routines (claude.ai cloud)

| Name | Type | ID / URL | Used By |
|---|---|---|---|
| SCLA video queue worker | Scheduled routine | `trig_01MLz82FGHA6T6NJ3SgWVqv6` · https://claude.ai/code/routines/trig_01MLz82FGHA6T6NJ3SgWVqv6 | polls the video queue weekdays 9:13 + 15:13 UTC (`projects/video-production/notion-queue.md` → "Automation") |

---

## Notes

- IDs belong here, not hardcoded in scripts — makes rotation and auditing easy.
- No IDs registered yet for Slack, Gmail, Canva, or Figma —
  add a section per service when its first real ID lands (DB IDs: 32-char string
  from the URL before the `?`, hyphenated `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
- Google Drive: mirror target folder ID pending (see section above).
- Last verified: 2026-07-08
