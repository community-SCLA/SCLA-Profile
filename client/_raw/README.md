# `_raw/` — scraped source material

**Do not edit files in this directory.** Everything here is a dated,
attributed snapshot of what the client gave us to work with. Downstream
agents read from it; they never write here.

## Subfolders

| Folder | Populated by | Contents |
|---|---|---|
| `web/` | `web-scraper` skill | One markdown file per scraped page |
| `docs/` | `doc-ingester` skill | Normalized documents (pdf/docx/etc → md) |
| `assets/` | `web-scraper` + human drops | Logos, images, PDFs |
| `artifacts/` | human drops + `doc-ingester` | Slack exports, tickets, meeting notes |

## Inbox

Humans drop unprocessed files here:

```
client/_raw/docs/inbox/
client/_raw/artifacts/inbox/
```

`/ingest` moves processed files to `inbox/_processed/` so re-runs are idempotent.

## Files

- `MANIFEST.md` — one row per ingested source (date, source, local path, size).
  Generated/updated by the `ingestor` agent.
- `INGEST_ERRORS.md` — any source that failed to ingest, with what the human
  needs to do to resolve it.
