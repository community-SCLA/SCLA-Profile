# Ingest Manifest

One row per file ingested. Append-only. Written by the `ingestor` agent.

| Date | Source | Local Path | Bytes |
|---|---|---|---|
| 2026-04-23 | https://www.thescla.org/ (search-index snapshot; direct fetch returned HTTP 403) | client/_raw/web/www.thescla.org/index.md | 7186 |

---

## Run summary — 2026-04-23

| Category | Count | Notes |
|---|---|---|
| Websites configured | 1 | https://www.thescla.org (crawl_depth: 2, include_assets: true) |
| Pages scraped (full) | 0 | Entire domain returned HTTP 403 |
| Pages snapshotted (search index) | 1 | index.md — partial content only; low confidence |
| Assets downloaded | 0 | No pages were reachable; no asset URLs resolved |
| Docs imported from inbox | 0 | Inbox exists but is empty |
| Docs imported from URL | 0 | URL field in config is blank |
| Repos ingested | 0 | sources.repos is empty |
| Drives ingested | 0 | sources.drives is empty |
| Artifacts ingested | 0 | sources.artifacts is empty |
| Errors logged | 3 | See client/_raw/INGEST_ERRORS.md |

### Files written this run

| File | Description | Bytes |
|---|---|---|
| client/_raw/web/www.thescla.org/index.md | Search-index snapshot of root URL + known sub-pages + partial content | 7186 |
| client/_raw/INGEST_ERRORS.md | Error log with remediation instructions | 4208 |
| client/_raw/MANIFEST.md | This file | — |
