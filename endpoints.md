# Endpoints Registry

Frequently used IDs, URLs, and paths across all automations and sessions.
Update here first — scripts and skills should read from here, not from hardcoded values.

> **Do not invent IDs — unknown values stay `TODO: needs input` until confirmed.**

> **Related:** Auth methods and connection status → `connections.md`

---

## GitHub

| Name | Path | Notes |
|---|---|---|
| This repo | `community-SCLA/SCLA-Profile` | Main branch: `main` |

---

## Notes

- IDs belong here, not hardcoded in scripts — makes rotation and auditing easy.
- No IDs registered yet for Notion, Google Drive, Slack, Gmail, Canva, or Figma —
  add a section per service when its first real ID lands (DB IDs: 32-char string
  from the URL before the `?`, hyphenated `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
- Last verified: 2026-07-03
