---
generated_by: ingestor
last_updated: 2026-04-23
---

# Ingest Errors

One entry per failure. Written by the `ingestor` agent. Append-only.

---

## ERROR-001 — HTTP 403: www.thescla.org (entire domain)

| Field | Value |
|---|---|
| Date | 2026-04-23 |
| Source | https://www.thescla.org/ |
| Error | HTTP 403 Forbidden |
| Scope | All paths tested on www.thescla.org |

### URLs attempted

All of the following returned HTTP 403:

- https://www.thescla.org/
- https://thescla.org/
- https://www.thescla.org/about
- https://www.thescla.org/membership
- https://www.thescla.org/benefits
- https://www.thescla.org/the-scla-difference
- https://www.thescla.org/start-a-chapter
- https://www.thescla.org/nab-apply
- https://www.thescla.org/online_membership
- https://www.thescla.org/program
- https://www.thescla.org/mission-history
- https://www.thescla.org/faq
- https://www.thescla.org/blog/what-is-the-scla
- https://www.thescla.org/membership-eligibility
- https://www.thescla.org/contact-us
- https://www.thescla.org/leadership-team

### Subdomains attempted

- https://students.thescla.org/ — HTTP 403
- https://info.thescla.org/mission-history — HTTP 403
- https://info.thescla.org/contact-us — HTTP 403
- https://shop.thescla.org/ — HTTP 403
- https://app.thescla.org/ — HTTP 403
- https://members.thescla.org/users/sign_in — Auth-gated (sign-in wall, not applicable to ingestor)

### Likely cause

The 403 is returned by the **sandbox egress proxy**, not by thescla.org.
The response body is literally `"Host not in allowlist"` (21 bytes), and
the same 403 is returned by `curl`, `WebFetch`, and headless browsers
regardless of User-Agent. Tested on 2026-04-23: github.com and
api.anthropic.com pass through; thescla.org, web.archive.org, archive.org,
and googlecache.com are all blocked. No automated fetch from this
environment can reach the target. Changing the User-Agent, using
Playwright, or asking SCLA to whitelist our IP will NOT help — the block
is on our side.

### What a human needs to do

Option A (recommended, only reliable path): Use a browser on a machine
outside this sandbox to export each key page as PDF or "Save as..." HTML,
then drop the files into `scla/_raw/docs/inbox/` and re-run `/ingest`.
Priority pages to export:

1. https://www.thescla.org/ (home)
2. https://www.thescla.org/benefits
3. https://www.thescla.org/the-scla-difference
4. https://www.thescla.org/mission-history
5. https://www.thescla.org/program
6. https://www.thescla.org/faq
7. https://www.thescla.org/membership-eligibility
8. https://www.thescla.org/start-a-chapter
9. https://www.thescla.org/contact-us
10. https://www.thescla.org/leadership-team
11. https://www.thescla.org/administrator-faq
12. https://www.thescla.org/online-membership
13. https://www.thescla.org/blog (index + individual posts)

Option B: Run the ingestor from an environment *outside* this sandbox
(a developer laptop, a CI runner with open egress) and commit the
resulting files under `scla/_raw/web/` and `scla/_raw/assets/`.

Option C (NOT viable from this sandbox): headless browser. Playwright
can render JS and pass bot checks, but the sandbox proxy still returns
403 before the request reaches thescla.org.

### Partial data saved

A search-index snapshot (partial content from Google's indexed snippets) was
saved to:
`scla/_raw/web/www.thescla.org/index.md`

This is NOT a full scrape. It captures only what Google's search index exposed
in snippet form. Downstream agents should treat this file as low-confidence
until replaced by a real scrape.

---

## ERROR-002 — Empty docs inbox

| Field | Value |
|---|---|
| Date | 2026-04-23 |
| Source | scla/_raw/docs/inbox/ |
| Error | Directory exists but contains no documents (only .gitkeep) |

### What a human needs to do

Drop any client-supplied documents (PDFs, DOCX, Google Doc exports, Notion
exports) into `scla/_raw/docs/inbox/` and re-run `/ingest`. The
doc-ingester will pick them up automatically.

---

## ERROR-003 — Empty URL in sources.docs

| Field | Value |
|---|---|
| Date | 2026-04-23 |
| Source | client.config.yml → sources.docs[1].url |
| Error | URL field is empty string ("") |

### What a human needs to do

If there is a public Google Doc, Notion page, or PDF URL you want ingested,
add it to the `url:` field under `sources.docs` in `client.config.yml` and
re-run `/ingest`.

---

## SKIPPED — sources.repos (empty)

`sources.repos` is an empty list in `client.config.yml`. No action taken.

---

## SKIPPED — sources.drives (empty)

`sources.drives` is an empty list in `client.config.yml`. No action taken.

---

## SKIPPED — sources.artifacts (empty)

`sources.artifacts` is an empty list in `client.config.yml`. No action taken.
