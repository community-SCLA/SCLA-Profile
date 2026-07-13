# Connections

Registry of every system SCLA runs on. Two views in one document:
- **Team view:** What systems does SCLA operate?
- **AI view:** Which can Claude reach as of the last check date, and how?

Update this file whenever a new tool is wired. When adding a reachable tool, also save `references/{tool}-api.md` (endpoints, auth flow, common queries — researched once, referenced forever). `/kb-audit` checks for this.

| Domain # | Domain | System | Purpose | Claude can reach? | Mechanism | Auth state | Last checked |
|---|---|---|---|---|---|---|---|
| 1 | Community Platform | SCLA website (custom channels) | Member-facing community hub | No | not connected | — | — |
| 2 | Communication | Slack | Internal team comms | Yes | mcp | active | 2026-05-31 |
| 2 | Communication | Gmail | External email + member messaging | Yes | mcp | active | 2026-05-31 |
| 3 | Content & Design | Canva | Design assets, team projects tracker | Yes | mcp | active | 2026-05-31 |
| 3 | Content & Design | Figma | UI and visual design mockups | Yes | mcp | active | 2026-05-31 |
| 4 | Knowledge / Files | Google Drive | Shared team docs, source material | Yes | mcp · script | active | 2026-06-23 |
| 4 | Knowledge / Files | Notion | Knowledge base, project documentation | Yes | mcp | active | 2026-05-31 |
| 5 | Task & Project Tracking | Notion | Work tracking and ownership | Yes | mcp | active | 2026-05-31 |
| 6 | Email & Member Outreach | Gmail | Broadcast email, member comms | Yes | mcp | active | 2026-05-31 |
| 3 | Content & Design | Wistia | Lesson-video hosting + analytics (`endpoints.md` → "Wistia") | No | not connected — uploads manual via web UI | — | 2026-07-13 |
| 6 | Email & Member Outreach | MJML dashboard (SCLA) | Custom email template system | No | not connected | — | — |
| 7 | Membership Tracking | (TBD) | Member sign-ups, engagement, quarterly/annual goals | No | not connected | — | — |

**Mechanism values:** `mcp` · `script` · `export` · `key+ref` · `not connected`
**Auth state values:** `active` · `needs-auth` · `expired` · `—`

## Notes
- Notion appears in both Knowledge/Files (domain 4) and Task & Project Tracking (domain 5) — one MCP, two use cases.
- Gmail appears in both Communication (domain 2) and Email & Member Outreach (domain 6) — one MCP, two use cases.
- MCP connections are configured at the claude.ai account level, not in local `.mcp.json`.
- Membership Tracking system is TBD — update this row when the tracking system is identified.
- When a tool moves from `not connected` to connected, create `references/{tool}-api.md`.
- Google Drive has two paths on one account: `mcp` for read, plus a `script` write-back — a one-way Git→Drive mirror that publishes curated content-folder pages as Google Docs on every push to `main` (Git is source of truth; Drive edits are overwritten). See `references/google-drive-api.md` and `.github/workflows/drive-sync.yml`.
