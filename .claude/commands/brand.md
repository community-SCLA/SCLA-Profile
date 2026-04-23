---
description: Generate the brand guide from scraped content in client/_raw/.
---

# /brand

Runs the `brand-analyst` sub-agent.

## What it does

Reads `client/_raw/web/` and `client/_raw/assets/`, then produces:

- `client/brand/brand-guide.md` — top-level index
- `client/brand/voice-and-tone.md` — with real sentence samples
- `client/brand/visual-identity.md` — colors, typography, design tokens
- `client/brand/assets/index.md` — inventory of every logo/image

## Prerequisites

- `/ingest` has run and `client/_raw/web/` is populated.

## Rules enforced

- Never invents colors, taglines, or values without source evidence.
- Confidence is stamped into frontmatter based on how much copy was available.
- Missing inputs become `TODO: needs input` rather than hallucinations.

## Re-running

This command **overwrites** `client/brand/`. Diff first if you've hand-edited anything.
