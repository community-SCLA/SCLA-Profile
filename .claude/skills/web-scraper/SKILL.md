---
name: web-scraper
description: Crawl a public website and snapshot each page to markdown under scla/_raw/web/. Use when ingesting items from sources.websites in scla.config.yml.
---

# web-scraper

Fetches a client's public web properties and writes one markdown file per page
into `scla/_raw/web/<host>/<path>.md`, preserving site structure.

## When to use

Called by the `ingestor` agent for every entry in
`scla.config.yml` → `sources.websites`.

## How it works

1. Read the website entry: `url`, `crawl_depth`, `include_paths`,
   `exclude_paths`, `include_assets`.
2. Use `WebFetch` on the root URL. Convert HTML → markdown.
3. Extract every in-domain link. Queue ones that match include/exclude rules
   and haven't been seen.
4. Recurse until `crawl_depth` is exhausted or the queue is empty.
5. For each page, write:
   ```
   scla/_raw/web/<host>/<slug>.md
   ```
   with frontmatter:
   ```yaml
   ---
   source_url: <url>
   fetched_at: <ISO timestamp>
   depth: <n>
   ingestor_skill: web-scraper
   ---
   ```
6. If `include_assets: true`, download images/PDFs linked from the page into
   `scla/_raw/assets/web/<host>/` and add a row to
   `scla/_raw/MANIFEST.md`.

## Failure modes

- **403 / 429** → log to `scla/_raw/INGEST_ERRORS.md`, continue.
- **JS-heavy SPA** → `WebFetch` may return skeleton HTML. Note this in errors
  and suggest the human export the page manually.
- **robots.txt disallow** → respect it. Log skipped paths.

## Rules

- One file per page. Never concatenate.
- Text content is **verbatim** — no summarization, no editorializing.
- Don't follow external domains.
