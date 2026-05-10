---
description: Generate the brand guide from scraped content in scla/_raw/.
---

# /brand

Runs the `brand-analyst` sub-agent.

## What it does

Reads `scla/_raw/web/` and `scla/_raw/assets/`, then produces:

- `scla/brand/brand-guide.md` — top-level index
- `scla/brand/voice-and-tone.md` — with real sentence samples
- `scla/brand/visual-identity.md` — colors, typography, design tokens
- `scla/brand/assets/index.md` — inventory of every logo/image

## Prerequisites

- `/ingest` has run and `scla/_raw/web/` is populated.

## Rules enforced

- Never invents colors, taglines, or values without source evidence.
- Confidence is stamped into frontmatter based on how much copy was available.
- Missing inputs become `TODO: needs input` rather than hallucinations.

## Re-running

This command **overwrites** `scla/brand/`. Diff first if you've hand-edited anything.
