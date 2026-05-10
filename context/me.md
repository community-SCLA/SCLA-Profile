## What This Project Is

scla-profile is a **client knowledge base pipeline**. It ingests raw inputs (website pages, documents, Slack exports, brand assets) and produces five structured outputs:

1. **Raw inputs** — scraped and imported source material (never edited, audit trail)
2. **Brand guide** — colors, typography, voice, design tokens extracted from SCLA's web presence
3. **Knowledge base** — structured wiki of SCLA's programs, history, team, and operations
4. **Workflow map** — current operational workflows + automation opportunities
5. **Source of truth** — SCLA's charter, decisions log, team handbook, and onboarding guide (client-owned, never auto-overwritten)

## Pipeline Architecture

Five specialized Claude agents run in sequence, each writing to `client/`:

```
/ingest    → Crawls thescla.org, imports docs → client/_raw/
/brand     → Extracts brand identity           → client/brand/
/kb        → Structures the knowledge base     → client/knowledge-base/
/workflows → Maps team workflows               → client/workflows/
/onboard   → Synthesizes source of truth       → client/source-of-truth/
```

Run all five at once with `/onboard`.

## Current Configuration

- **Client:** The Society for Collegiate Leadership & Achievement (SCLA)
- **Primary source:** https://www.thescla.org (2-level crawl)
- **Doc inbox:** `client/_raw/docs/inbox/` (drop PDFs, Google Docs exports here)
- **Status:** Pipeline built, not yet run — `client/` directories exist but contain only READMEs

## This Is a Template

The pipeline is designed to be cloned per client. `scripts/bootstrap.sh` creates a new repo from this template. The `.claude/` directory (agents, commands, skills, hooks) is the engine — don't edit it unless upgrading the engine itself.
