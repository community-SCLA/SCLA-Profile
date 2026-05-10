---
description: Map current-state workflows and surface automation opportunities from artifacts.
---

# /workflows

Runs the `workflow-mapper` sub-agent.

## What it does

Reads `scla/_raw/artifacts/` (Slack exports, tickets, meeting notes, runbooks)
and produces:

- `scla/workflows/current-state.md` — one section per recurring workflow
- `scla/workflows/automation-opportunities.md` — prioritized table
- `scla/workflows/ship-fast-playbook.md` — top 5 recommendations

## Prerequisites

- `/ingest` has run and `scla/_raw/artifacts/` has at least one artifact.
- Ideally `/kb` has also run so the mapper can reference `systems-and-tools.md`.

## Heuristics it applies

- **Copy-paste between tools** → integration candidate
- **Deterministic decisions by humans** → bot/rule candidate
- **Context lost at handoff** → shared-doc candidate
- **Status-update meetings** → written-summary candidate

## Output format

Every opportunity row includes priority (P0/P1/P2) and effort (S/M/L/XL)
so SCLA's team can triage.

## Re-running

**Overwrites** `scla/workflows/`. Safe — regenerated from artifacts.
