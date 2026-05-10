---
description: Run only the ingestion stage — scrape sources listed in scla.config.yml into scla/_raw/.
---

# /ingest

Runs the `ingestor` sub-agent against the current `scla.config.yml`.

## What it does

1. Launches `ingestor` with its full contract (see `.claude/agents/ingestor.md`).
2. Scrapes every item in `sources.websites`, `sources.docs`, `sources.repos`,
   `sources.drives`, and `sources.artifacts`.
3. Writes everything to `scla/_raw/` with an updated `MANIFEST.md`.

## When to use

- Fresh onboarding (before `/brand`, `/kb`, `/workflows`).
- Source list in `scla.config.yml` changed and you want to re-sync.
- Someone added new files to `scla/_raw/docs/inbox/` — re-run to register them.

## After it finishes

Inspect:
- `scla/_raw/MANIFEST.md` — what got captured
- `scla/_raw/INGEST_ERRORS.md` — anything that failed (auth, 403, etc.)

Then run `/brand`, `/kb`, or `/workflows` — or `/onboard` to continue the full pipeline.
