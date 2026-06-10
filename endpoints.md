# Endpoints Registry

Frequently used IDs, URLs, and paths across all automations and sessions.
Update here first — scripts and skills should read from here, not from hardcoded values.

> **Related:** Auth methods and connection status → `connections.md`

---

## Notion

| Name | Type | ID | Used By |
|---|---|---|---|
| [Page Name] | Page | `[32-char UUID with hyphens]` | [task-name] |
| [Database Name] | Database | *(add ID)* | [task-name] |

> To find a Notion database ID: open the DB in browser → copy the 32-char string from the URL before the `?`.
> Format with hyphens: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## Google Drive

| Name | Type | ID / URL | Used By |
|---|---|---|---|
| *(add folders as you reference them regularly)* | | | |

---

## GitHub

| Name | Path | Notes |
|---|---|---|
| This repo | `[YOUR_USERNAME]/[YOUR_REPO]` | Main branch: `main` |

---

## Other Services

| Service | Name | ID / URL | Used By |
|---|---|---|---|
| [Slack] | [Channel name] | [channel ID] | [task-name] |

---

## Notes

- IDs belong here, not hardcoded in scripts — makes rotation and auditing easy.
- The weekly-ops-audit scans scripts for hardcoded UUIDs and flags any not registered here.
- Last verified: [DATE]
