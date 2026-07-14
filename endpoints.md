# Endpoints Registry

Frequently used IDs, URLs, and paths across all automations and sessions.
Update here first — scripts and skills should read from here, not from hardcoded values.

> **Do not invent IDs — unknown values stay `TODO: needs input` until confirmed.**

> Each integration's connection status (reachable? auth?) is noted inline in its
> section below — `endpoints.md` is the single integration registry.

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
| Upload API token | — | in **Infisical** (project `scla-projects-n-joy`, env `dev` — see the Infisical section below); never in `.env`, this file, or the repo | injected at `/render-lessons` PUBLISH via `scripts/with-secrets.sh`; exact secret name confirmed once the machine identity has project access |

> Video title = the filed MP4 stem `<section>_<program-slug>_<render-date>`.
> The Wistia URL of a published lesson is recorded in
> `projects/video-production/lesson-scripts/refinement-log.md` (ledger row).

---

## Infisical (secrets manager — source of truth for ALL secrets)

Secrets live **only** in Infisical and are injected at runtime by the CLI —
**never written to `.env`, this file, or the repo.** No `infisical export` path.

| Name | ID / value | Notes |
|---|---|---|
| Project | `scla-projects-n-joy` · `eea9b546-3f30-45d8-a9b9-a6ede93e3a71` | the SCLA secrets project |
| Environment | `dev` | default env for injection |
| Machine-identity auth | Codespaces repo secrets `INFISICAL_CLIENT_ID` + `INFISICAL_SECRET_KEY` | universal-auth; the CLI logs in with these — the values are never in the repo |

**Injection:** `scripts/with-secrets.sh <command> [args…]` logs in with the
machine identity and runs the command under `infisical run`, so every secret in
the project/env is present as an env var for that process only. Override the
project/env with `INFISICAL_PROJECT_ID` / `INFISICAL_ENV`. CLI is provisioned by
`.devcontainer/devcontainer.json` (`postCreateCommand`).

> **Access pending (owner action):** the machine identity must be assigned to
> the `scla-projects-n-joy` project with read on `dev` — until then the CLI
> authenticates but every read returns `403 Forbidden`.

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
