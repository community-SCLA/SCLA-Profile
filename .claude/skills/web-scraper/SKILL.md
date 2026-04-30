---
name: web-scraper
description: Crawl a public website and snapshot each page to markdown under client/_raw/web/. Use when ingesting items from sources.websites in client.config.yml.
---

# web-scraper

Fetches a client's public web properties and writes one markdown file per page
into `client/_raw/web/<host>/<path>.md`, preserving site structure.

## When to use

Called by the `ingestor` agent for every entry in
`client.config.yml` → `sources.websites`.

## How it works

1. Read the website entry: `url`, `crawl_depth`, `include_paths`,
   `exclude_paths`, `include_assets`.
2. Use `WebFetch` on the root URL. Convert HTML → markdown.
3. Extract every in-domain link. Queue ones that match include/exclude rules
   and haven't been seen.
4. Recurse until `crawl_depth` is exhausted or the queue is empty.
5. For each page, write:
   ```
   client/_raw/web/<host>/<slug>.md
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
   `client/_raw/assets/web/<host>/` and add a row to
   `client/_raw/MANIFEST.md`.

## Failure modes

- **403 / 429** → log to `client/_raw/INGEST_ERRORS.md`, continue.
- **JS-heavy SPA** → `WebFetch` may return skeleton HTML. Note this in errors
  and suggest the human export the page manually.
- **robots.txt disallow** → respect it. Log skipped paths.

## Egress-blocked environments

Claude's sandbox blocks most external domains via an egress proxy that returns
HTTP 403 with body `"Host not in allowlist"`. This is a sandbox-side constraint
— changing the User-Agent, using Playwright, or whitelisting the client's IP
will not help.

**Preferred path (Option B):** Run the web-scraper from a machine outside the
sandbox (developer laptop, CI runner with open egress). Commit the resulting
`client/_raw/web/` files and re-run downstream stages from within the sandbox.

**Fallback (Option A — slow):** Export priority pages manually via browser
("Save as..." HTML or PDF), drop into `client/_raw/docs/inbox/`, re-run
`/ingest`. Use only when Option B is not available.

**Fallback of last resort:** If both options are unavailable, attempt a Google
search index snapshot. Use `WebSearch` to collect snippet text for priority
pages. Write results to `client/_raw/web/<host>/index.md` with frontmatter:
```yaml
fetch_status: 403_BLOCKED
note: "Content sourced from Google search snippets only. Low confidence."
```
Downstream agents must treat this file as `confidence: low`.

## Rules

- One file per page. Never concatenate.
- Text content is **verbatim** — no summarization, no editorializing.
- Don't follow external domains.
