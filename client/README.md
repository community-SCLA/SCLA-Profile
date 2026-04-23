# `client/` — everything the onboarding produces

This directory is the **output** of the pipeline. Agents fill it; you edit it
(eventually — see per-subdirectory rules).

```
client/
├── _raw/                ← untouched scraped source material (audit trail)
├── knowledge-base/      ← structured wiki (glossary, people, products, tools)
├── brand/               ← brand guide, voice, visual identity, design tokens
├── workflows/           ← current-state workflows + automation opportunities
└── source-of-truth/     ← the team's daily-driver: charter, decisions, handbook
```

## Ownership

| Directory | Regenerated on re-run? | Who edits it? |
|---|---|---|
| `_raw/` | Yes, by `ingestor` | Nobody — it's source material |
| `knowledge-base/` | Yes, by `knowledge-architect` | Agent writes; humans correct |
| `brand/` | Yes, by `brand-analyst` | Agent writes; humans refine |
| `workflows/` | Yes, by `workflow-mapper` | Agent writes; humans prioritize |
| `source-of-truth/` | **No**, after first generation | The client's team, forever |

## Frontmatter contract

Every non-raw markdown file starts with:

```yaml
---
source: <path into _raw/ or URL>
generated_by: <agent name>
last_updated: YYYY-MM-DD
confidence: low | medium | high
---
```

Grep for `confidence: low` and `TODO: needs input` to find what still needs
human attention.
