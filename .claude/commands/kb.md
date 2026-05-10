---
description: Build SCLA's internal knowledge base (glossary, people, products, FAQs) from scraped docs.
---

# /kb

Runs the `knowledge-architect` sub-agent.

## What it does

Reads `scla/_raw/docs/` and `scla/_raw/web/` and produces a structured wiki
in `scla/knowledge-base/`:

| File | Contents |
|---|---|
| `index.md` | Entry point + "start here" for new readers |
| `glossary.md` | Acronyms, code-names, internal terms |
| `people-and-teams.md` | Who does what, contact info |
| `products-and-services.md` | What the company sells |
| `systems-and-tools.md` | Software stack + ownership |
| `faqs.md` | Recurring questions from `_raw/artifacts/` |

## Prerequisites

- `/ingest` has run.

## Rules enforced

- Quotes over paraphrases; every claim links back to `_raw/`.
- One entity → one canonical name (with variants noted).
- Cross-links between people ↔ teams ↔ products ↔ tools.
- Gaps marked `TODO: needs input`, never filled in by guessing.

## Re-running

**Overwrites** `scla/knowledge-base/`. Safe because everything is regenerated
from `_raw/`.
