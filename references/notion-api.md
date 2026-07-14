---
source: Notion MCP integration (claude.ai account-level)
generated_by: kb-audit reference scaffold
last_updated: 2026-06-12
---

# Notion — Integration Reference

Researched-once reference for the Notion integration registered in `endpoints.md`
(Knowledge/Files + Task & Project Tracking — one MCP, two use cases).
Concrete page/database IDs live in `endpoints.md`, never hardcoded here.

## Connection

| Field | Value |
|---|---|
| Mechanism | `mcp` (configured at the claude.ai account level, not in local `.mcp.json`) |
| Auth state | `active` (MCP, configured at the claude.ai account level) |
| Writable | Yes — MCP tools can create and update pages, databases, and comments |

## Available operations (MCP tools)

| Tool | Purpose |
|---|---|
| `notion-search` | Find pages/databases by keyword across the workspace |
| `notion-fetch` | Read a page or database by ID or URL |
| `notion-create-pages` | Create one or more pages (optionally inside a parent DB) |
| `notion-update-page` | Edit page properties or content |
| `notion-move-pages` | Re-parent pages |
| `notion-duplicate-page` | Copy a page |
| `notion-create-database` / `notion-update-data-source` | Create or update a database schema |
| `notion-create-view` / `notion-update-view` | Manage database views |
| `notion-get-comments` / `notion-create-comment` | Read and post comments |
| `notion-get-users` / `notion-get-teams` | Resolve people and teamspaces |

## Common queries

- **Locate a database:** `notion-search` with the DB name, then record its ID in `endpoints.md`.
- **Read tracked work:** `notion-fetch` against the Task & Project Tracking database ID.
- **Add an item:** `notion-create-pages` with the parent DB ID and the item's properties.

## IDs

All workspace-specific IDs (page IDs, database IDs) are registered in `endpoints.md`
under the **Notion** section. Unknown IDs stay `TODO: needs input` until confirmed —
do not invent them.

> To find a Notion database ID: open the DB in browser → copy the 32-char string from
> the URL before the `?`; format with hyphens `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.
