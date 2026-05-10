---
description: Run the full 5-stage onboarding pipeline with human gates between stages.
argument-hint: "[--resume]"
---

# /onboard

Orchestrates the full onboarding pipeline for SCLA defined in
`scla.config.yml`. Pauses between stages so you can review.

## Flow

```
 ingest → brand → kb → workflows → source-of-truth
    │        │      │       │              │
    └── gate ┴─ gate ┴─ gate ┴──── gate ────┘
```

## Steps

1. **Pre-flight**: read `scla.config.yml`. Confirm `scla.name` and
   `scla.slug` are filled in. If not, ask the user to fill them and stop.

2. **Stage 1 — Ingest.**
   - Invoke the `ingestor` sub-agent.
   - When it returns, show the user `scla/_raw/MANIFEST.md` and any
     `INGEST_ERRORS.md`.
   - **GATE**: ask "Proceed to brand + knowledge extraction? (y/n)". Stop if n.

3. **Stage 2 + 3 — Brand & Knowledge (parallel).**
   - Launch `brand-analyst` and `knowledge-architect` in parallel.
   - Summarize their outputs and confidence levels.
   - **GATE**: ask "Proceed to workflow mapping? (y/n)".

4. **Stage 4 — Workflows.**
   - Invoke `workflow-mapper`.
   - Show the top 5 automation opportunities by priority.
   - **GATE**: ask "Generate source-of-truth? (y/n)".

5. **Stage 5 — Source of truth.**
   - Check for `scla/source-of-truth/.source-of-truth-generated`.
     If present, warn: "Source of truth already exists. Regenerating will
     NOT overwrite — it will only fill in missing files." Confirm.
   - Invoke `source-of-truth-curator`.

6. **Wrap-up.** Print:
   - Location of `scla/source-of-truth/README.md`
   - Count of `TODO: needs input` markers across `scla/`
   - Suggested next steps from `HANDOFF.md`

## `--resume` flag

If `$ARGUMENTS` contains `--resume`, run `/status` first and skip any stage
marked ✅ complete.

## Rules

- Never skip a gate. Human review between stages is the whole point.
- If any stage fails, stop the pipeline and report — don't cascade failures.
