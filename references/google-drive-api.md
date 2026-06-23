---
source: Google Drive integration (MCP read + rclone write-back via GitHub Action)
generated_by: drive-sync setup
last_updated: 2026-06-23
confidence: high
---

# Google Drive — Integration Reference

Researched-once reference for the Google Drive connection registered in `connections.md`
(domain 4 Knowledge/Files). Concrete folder IDs live in `endpoints.md`, never hardcoded here.

Drive is used two ways, both pointed at the same account:

| Direction | Mechanism | Purpose |
|---|---|---|
| Drive → Claude (read) | `mcp` | Read shared team docs / trace source material |
| Git → Drive (write-back) | `script` (GitHub Action + rclone) | Publish curated `scla/` pages into Drive as Google Docs |

## Git → Drive mirror (the write-back path)

One-way mirror, **Git is the source of truth**. On every push to `main` touching `scla/`,
`.github/workflows/drive-sync.yml` runs:

1. `scripts/build-docx.sh` converts `scla/**/*.md` → parallel `.docx` tree under `build/`
   (pandoc; YAML frontmatter parsed as metadata, not rendered).
2. `rclone sync build/ <GDRIVE_TARGET>/ --drive-import-formats docx --drive-use-trash
   --create-empty-src-dirs` uploads each `.docx`; Drive imports it as a native Google Doc.

Properties to remember:
- **Edits made in the Drive Docs are overwritten** on the next sync — edit the repo, not Drive.
- A `.md` removed/renamed in Git is **trashed/renamed** in Drive on the next sync
  (`--drive-use-trash` keeps it recoverable).
- rclone updates Docs **in place** by path, so re-syncs do not create duplicates.

## Configuration

| Field | Value |
|---|---|
| rclone remote | name set in the rclone config (e.g. `gdrive`); target folder in `vars.GDRIVE_TARGET`, form `gdrive:SCLA-Profile` |
| Auth secret | GitHub repo secret `RCLONE_CONF_BASE64` — base64 of an `rclone.conf` authorized as `community@thescla.org` (OAuth refresh token) |
| Target folder | human-readable name + ID in `endpoints.md` → Google Drive section |
| Trigger | `push` to `main`, `paths: scla/**`; plus `workflow_dispatch` (with `dry_run`) |

### Regenerating the auth secret
1. Locally: `rclone config` → new remote, type `drive`, scope `drive`, authorize as
   `community@thescla.org`. This writes a refresh token into `~/.config/rclone/rclone.conf`.
2. `base64 -w0 ~/.config/rclone/rclone.conf` → paste as repo secret `RCLONE_CONF_BASE64`.
3. Set repo variable `GDRIVE_TARGET` to `<remote>:<folder>` (e.g. `gdrive:SCLA-Profile`).

**Alternative auth (org-robust):** a Google service account added as a member of a Google
**Shared Drive**, JSON key stored as the secret instead. Avoids a personal-account token but
requires a Shared Drive (service accounts have no My Drive storage quota).

## Read path (MCP tools)

| Tool | Purpose |
|---|---|
| `search_files` | Find a file/folder by name or query |
| `get_file_metadata` / `get_file_permissions` | Inspect a file and its sharing |
| `read_file_content` / `download_file_content` | Read or download a file's contents |
| `list_recent_files` | Browse recently touched files |
| `create_file` / `copy_file` | Create or duplicate a file |

> Note: the MCP toolset has **no in-place overwrite/update** — that's why the write-back
> mirror uses rclone, not MCP, so re-syncs update Docs instead of duplicating them.

## IDs

Drive folder IDs are registered in `endpoints.md` under **Google Drive**. Unknown IDs stay
`TODO: needs input` until confirmed — do not invent them. To find a folder ID: open the
folder in the browser → copy the string after `/folders/` in the URL.
