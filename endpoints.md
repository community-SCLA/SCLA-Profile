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
| Lesson videos project/folder | Project | filed per-program; **Early Career Boost** = id `10733647` / hashedId `miuwd520zj` | where uploaded lessons are filed in Wistia (one Wistia project per program) |
| Upload API token | — | in **Infisical** (project `scla-projects-n-joy`, env `dev`, secret name `WISTIA_API` — see the Infisical section below); never in `.env`, this file, or the repo | injected at `/render-lessons` PUBLISH via `scripts/with-secrets.sh` |

> Video title = the filed MP4 stem `<section>_<program-slug>_<render-date>`.
> The Wistia URL of a published lesson is recorded in
> `projects/video-production/lesson-scripts/refinement-log.md` (ledger row).

> **Token scope — verified 2026-07-15:** the `WISTIA_API` token in Infisical is
> **read+write but NOT delete**. Probed live: `GET /account.json` → 200,
> `GET /medias/zyr1fq35t7.json` → 200, but **every `DELETE /medias/*.json` → 401**
> (reproduced via `api_password` query param *and* `Authorization: Bearer`, even
> against a bogus id — so it is a permission-scope rejection, not an auth-method or
> resource issue; Wistia returns 401 for an operation above the token's permission
> tier). Uploads/publishes work; **media deletion does not.** To delete media
> (e.g. the owner-approved take-down of `zyr1fq35t7`) the `WISTIA_API` secret must
> be rotated to a token minted with **read-write-delete-all-data** permission in
> the Wistia account settings — an owner action (needs Wistia admin).

---

## HeyGen

| Name | Type | ID / URL | Used By |
|---|---|---|---|
| API key | — | in **Infisical** (project `scla-projects-n-joy`, env `dev`, secret name `HEYGEN_API_KEY`) — never in `.env`, this file, or the repo | `avatar-pipeline/` renders, HeyGen TTS path in `hyperframes-media` |

> **Status — verified live 2026-07-21:** key rotated (previous key returned 403
> "Ask your Space Admin" on every endpoint — see `decisions/log.md` 2026-07-15,
> `projects/video-production/status.md` blockers). Injected via
> `scripts/with-secrets.sh` and probed against `GET /v2/user/remaining_quota`
> with header `X-Api-Key` → **200**, `remaining_quota: 15000` (`api: 15000, seat: 1,
> plan_credit: 1000`). Note: that endpoint is HeyGen's **legacy v2** API, sunsetting
> 2026-10-31 per its own response — new integration work should target
> `GET /v3/users/me` instead (https://developers.heygen.com/reference).
> `avatar-pipeline/` renders and the HeyGen TTS path are unblocked.

---

## Infisical (secrets manager — source of truth for ALL secrets)

Secrets live **only** in Infisical and are injected at runtime by the CLI —
**never written to `.env`, this file, or the repo.** No `infisical export` path.

| Name | ID / value | Notes |
|---|---|---|
| Project | `scla-projects-n-joy` · `eea9b546-3f30-45d8-a9b9-a6ede93e3a71` | the SCLA secrets project |
| Environment | `dev` | default env for injection |
| Machine-identity auth | Codespaces repo secrets `INFISICAL_CLIENT_ID` + `INFISICAL_SECRET_KEY` | universal-auth; the CLI logs in with these — the values are never in the repo. Identity **`SCLA-PROJECTS`** (`identityId 12f0b20a-2ac1-44f6-902c-cb8ef121d210`, client-id `9f0c3057-aed5-4e16-8606-08e24aed92f6`) — this is the identity the video pipeline authenticates as. |

**Injection:** `scripts/with-secrets.sh <command> [args…]` logs in with the
machine identity and runs the command under `infisical run`, so every secret in
the project/env is present as an env var for that process only. Override the
project/env with `INFISICAL_PROJECT_ID` / `INFISICAL_ENV`. CLI is provisioned by
`.devcontainer/devcontainer.json` (`postCreateCommand`).

> **Verified 2026-07-15:** Infisical is healthy — the reported HTTP 401 is **not**
> Infisical's. Identity `SCLA-PROJECTS` logs in (universal-auth, exit 0) and
> `scripts/with-secrets.sh` injects project secrets on `scla-projects-n-joy` /
> `dev`; the injection line "Injecting N Infisical secrets" is success, not
> failure. The 401 the owner hit comes from **Wistia** rejecting a `DELETE` — see
> the Wistia section. The right machine identity is being called and it is
> authorized.
> (Earlier states for the record: 2026-07-14 endpoints note "read access";
> decision-log 2026-07-14 "authenticates but reads 403, blocked pending owner
> assigning the identity to the project" — that block is now cleared.)
>
> **2026-07-21:** now injecting 3 secrets: `WISTIA_API`, `HEYGEN_API_KEY`, and a
> third named plain `HEYGEN`. The third is **intentionally unused** (owner call,
> 2026-07-22) — not a blocker, ignore it. `HEYGEN_API_KEY` is the pipeline key;
> see "HeyGen" section above for its live-verified status.

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
- Last verified: 2026-07-15 (Infisical machine identity + Wistia token scope)
