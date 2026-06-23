# Endpoints Registry

Frequently used IDs, URLs, and paths across all automations and sessions.
Update here first — scripts and skills should read from here, not from hardcoded values.

> **Do not invent IDs — unknown values stay `TODO: needs input` until confirmed.**

> **Related:** Auth methods and connection status → `connections.md`

---

## Notion

| Name | Type | ID | Used By |
|---|---|---|---|
| TODO: needs input | Page | `TODO: needs input` | TODO: needs input |
| TODO: needs input | Database | `TODO: needs input` | TODO: needs input |

> To find a Notion database ID: open the DB in browser → copy the 32-char string from the URL before the `?`.
> Format with hyphens: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

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

## GitHub

| Name | Path | Notes |
|---|---|---|
| This repo | `community-SCLA/SCLA-Profile` | Main branch: `main` |

---

## Slack

| Name | Type | ID | Used By |
|---|---|---|---|
| TODO: needs input | Channel | `TODO: needs input` | TODO: needs input |

---

## Gmail

| Name | Type | ID / Address | Used By |
|---|---|---|---|
| TODO: needs input | Label / Filter | `TODO: needs input` | TODO: needs input |

---

## Canva

| Name | Type | ID | Used By |
|---|---|---|---|
| TODO: needs input | Team / Folder | `TODO: needs input` | TODO: needs input |

---

## Figma

| Name | Type | ID | Used By |
|---|---|---|---|
| TODO: needs input | File / Project | `TODO: needs input` | TODO: needs input |

---

## Notes

- IDs belong here, not hardcoded in scripts — makes rotation and auditing easy.
- Last verified: TODO: needs input
