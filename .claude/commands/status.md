---
description: Report onboarding progress — which stages are complete, confidence per stage, open TODOs.
---

# /status

Reports a dashboard of onboarding progress.

## What to check and report

1. **Config**: is `client.config.yml` filled in? (`client.name`, `client.slug`
   non-empty, at least one source listed).

2. **Stage completion** — for each stage, check if its target files exist
   and have non-TODO frontmatter confidence:

   | Stage | File(s) that must exist | Indicator |
   |---|---|---|
   | Ingest | `client/_raw/MANIFEST.md` with ≥1 entry | ✅ / ⚠️ / ❌ |
   | Brand | `client/brand/brand-guide.md` | ✅ / ⚠️ / ❌ |
   | KB | `client/knowledge-base/index.md` | ✅ / ⚠️ / ❌ |
   | Workflows | `client/workflows/current-state.md` | ✅ / ⚠️ / ❌ |
   | Source of Truth | `client/source-of-truth/README.md` | ✅ / ⚠️ / ❌ |

   - ✅ = file exists, `confidence: medium|high`
   - ⚠️ = file exists, `confidence: low` OR has TODOs
   - ❌ = file missing

3. **Confidence gates**: compare each stage's frontmatter `confidence:` to
   the minimum set in `client.config.yml` → `gates.*`. Flag any that fail.

4. **Open TODOs**: grep `client/` for `TODO: needs input` and count per file.
   Print top 10 files with counts.

5. **Next action**: suggest what to run next (e.g. "Run `/brand` — ingest is
   done but brand stage hasn't started").

## Output format

```
📊 Onboarding status — <client.name>

  Ingest          ✅  (12 files, 0 errors)
  Brand           ⚠️  (confidence: low — only homepage ingested)
  Knowledge Base  ✅  (confidence: medium)
  Workflows       ❌  (no artifacts in _raw/artifacts/)
  Source of Truth ❌  (not generated yet)

  Open TODOs: 14
    client/knowledge-base/people-and-teams.md  (6)
    client/brand/voice-and-tone.md             (4)
    ...

  👉 Suggested next: /workflows (after adding Slack export to _raw/artifacts/)
```

## Rules

- Read-only — this command never modifies files.
- Runs fast. No LLM reasoning; pure file-system + grep.
