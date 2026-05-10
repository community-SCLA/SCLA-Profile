# SCLA-Profile Redesign Spec
**Date:** 2026-05-10
**Status:** Approved — ready for implementation planning

---

## Purpose

SCLA-Profile is the comprehensive, centralized knowledge base that powers Claude for all SCLA work. It is not a one-time snapshot — it is the single source of intelligence Claude draws from to assist with grants, program development, member campaigns, content, operations, partnerships, user experience, and anything else SCLA-related.

Primary use: Claude reads this context to do SCLA work accurately without needing re-explanation each session.

---

## Terminology

- **SCLA** — replaces all prior use of "client" throughout files, directories, agents, commands, and documentation
- **Members** — the people SCLA serves; replaces any prior use of "clients" when referring to students/members

---

## Directory Structure

```
scla/
  _raw/                  ← Claude's ingestion cache; humans never edit this directly
    web/                 ← scraped thescla.org pages (markdown)
    docs/                ← Google Docs / PDFs exported from Drive
    artifacts/           ← Gemini meeting notes, stakeholder notes, Slack exports
    assets/              ← logos, brand PDFs, screenshots, image files
  brand/                 ← voice, tone, visual standards, asset index
  programs/              ← every SCLA offering in detail:
                            Career Readiness Certification, ISPI strengths assessment,
                            Career Hub (AI-powered), CEO Speaker Series,
                            skill development videos, micro-internships, Focus Modes,
                            scholarships, peer networking
  members/               ← member journey, pledge process, onboarding, engagement
  operations/            ← team structure, roles, workflows, SOPs, tools inventory
  partnerships/          ← campus partners, org partners, employer partners,
                            contacts, relationship data organized by partnership type
  knowledge-base/        ← SCLA history, FAQs, glossary
  source-of-truth/       ← human-maintained, write-locked on re-runs (see below)
    mission.md
    program-names.md
    voice-decisions.md
    decisions-log.md
    team-handbook.md
  projects/              ← active and archived project work
    grants/              ← grant applications (drafts, submitted, templates)
    campaigns/           ← member campaigns and outreach
    programs/            ← program development work
    content/             ← newsletters, social, content pieces
```

Generic `client/` directory and all `client` references are fully removed and replaced with the above SCLA-native structure.

---

## Pipeline (5 Stages)

| Stage | Agent | Reads | Writes |
|---|---|---|---|
| 1. Ingest | `ingestor` | `scla.config.yml` | `scla/_raw/**` |
| 2. Brand | `brand-analyst` | `scla/_raw/web/`, `scla/_raw/assets/`, `source-of-truth/mission.md`, `source-of-truth/voice-decisions.md` | `scla/brand/**` |
| 3. Knowledge | `knowledge-architect` | `scla/_raw/docs/`, `scla/_raw/web/`, `source-of-truth/program-names.md`, `source-of-truth/decisions-log.md` | `scla/knowledge-base/**`, `scla/programs/**`, `scla/members/**`, `scla/partnerships/**` *(knowledge-architect is explicitly granted multi-directory write — all four are knowledge outputs from the same agent)* |
| 4. Workflows | `workflow-mapper` | `scla/_raw/artifacts/`, `scla/_raw/docs/`, `source-of-truth/decisions-log.md` | `scla/operations/**` + `scla/_raw/kb-deltas.md` |
| 5. Curate | `source-of-truth-curator` | all of `scla/**` | `scla/source-of-truth/**` (merge-only) + merges `kb-deltas.md` into `knowledge-base/` |

---

## Architecture Changes (Phase 1)

### C1 — Frontmatter Enforcement

The `stamp-frontmatter.sh` hook is upgraded from placeholder-injector to validator.

**Current behavior:** Injects `source: TODO / generated_by: unknown / confidence: low` when frontmatter is missing. Agents are supposed to overwrite but nothing enforces it.

**New behavior:** On every write to `scla/` (excluding `_raw/`), the hook checks that `source`, `generated_by`, and `confidence` are present and not `TODO` or `unknown`. If any field is unfilled, the hook emits a loud warning and blocks the commit.

**Why:** The frontmatter is the trust signal Claude uses to weight knowledge. `TODO` placeholders silently degrade output quality.

---

### C2 — Source-of-Truth Write Protection

`source-of-truth/` is human-maintained and must never be overwritten by a pipeline re-run.

**New behavior:** The source-of-truth-curator, on any run after initial generation, diffs its proposed output against the existing files. Instead of writing directly, it produces `scla/source-of-truth/PROPOSED_CHANGES.md` listing what changed and why, for human review. A human applies or rejects changes manually.

**Why:** Without this, any scheduled cron re-run silently destroys human edits — org decisions, canonical program names, handbook updates.

---

### C3 — Curator Feedback Loop (Efficient)

Agents read from `source-of-truth/` to ensure canonical facts propagate into every generated output — but only the specific files relevant to each agent's task.

**Agent → source-of-truth file mapping:**
- `brand-analyst` reads: `mission.md`, `voice-decisions.md`
- `knowledge-architect` reads: `program-names.md`, `decisions-log.md`
- `workflow-mapper` reads: `decisions-log.md`
- `source-of-truth-curator` reads: all files in `source-of-truth/`

**source-of-truth/ is structured as small, targeted files** (not one large document) so agents can load only what they need. No agent reads the full directory.

**Why:** Without this, re-runs overwrite canonical facts with re-scraped guesses. With it, decisions made once (program naming, voice, org structure) persist and propagate automatically without context bloat.

---

### C5 — KB-Delta Merge

`workflow-mapper` cannot write to `knowledge-base/` directly (one agent, one directory rule). Currently it writes `kb-deltas.md` listing gaps — which has never been automatically applied.

**New behavior:** The source-of-truth-curator, as part of Stage 5, reads `scla/_raw/kb-deltas.md`, merges the entries into the appropriate `knowledge-base/` files, then deletes `kb-deltas.md`.

**Why:** KB gaps identified by workflow analysis actually get filled. The delta file stops being a permanent unactioned TODO.

---

### C4 — Pipeline State Tracking (Deferred)

`pipeline.state.json` tracking completed stages, timestamps, and confidence per stage — enabling safe `/onboard --resume`. Deferred to the cron/hybrid-update milestone.

---

## Update Model

| Content type | How it stays current |
|---|---|
| Stable facts (mission, canonical names, decisions) | Manual edits to `source-of-truth/` by Kierra or Amy |
| Website content | Scheduled cron re-ingest *(deferred to next milestone)* |
| Google Drive docs | Scheduled cron re-ingest *(deferred to next milestone)* |
| Meeting notes, stakeholder docs | File-drop into `scla/_raw/artifacts/inbox/` triggers ingestion via hook *(deferred to next milestone)* |

---

## Migration Scope

This is a full structural migration, not an additive change. The following work happens in Phase 1:

1. **Merge `onboard-flow` branch** — preserves all real data (meeting notes, web scrape, brand drafts, workflows, knowledge base scaffolding) accumulated since April 2026
2. **Global rename** — `client/` → `scla/`, "client" → "SCLA", people served → "members" across all files, agent definitions, commands, templates, hooks, config, and documentation
3. **Restructure directories** — map existing pipeline output into new SCLA-native structure; discard generic template skeleton
4. **Implement C1, C2, C3, C5** — architectural changes as specified above
5. **Run Stage 5** — execute source-of-truth-curator on the new structure to produce the initial `source-of-truth/` content

---

## Out of Scope (This Phase)

- Hybrid update triggers (cron + inbox hook)
- Pipeline state tracking (C4)
- New raw ingestion runs (website re-scrape, Drive import)
- `projects/` content population (directories created, not filled)
