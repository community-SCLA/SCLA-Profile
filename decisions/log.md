---
source: manual
generated_by: source-of-truth-curator
last_updated: 2026-06-11
confidence: high
---

# SCLA Decisions Log

Running log of notable team decisions. Append new entries at the top.

## 2026-06-11 — Repo restructure: one-question-one-file framework completed
**Decision:** Converged root docs into single question-owners: GUARDRAILS.md + EXPANSIONS.md merged into GOVERNANCE.md (originals archived in `_archive/` with dated names); MAP.md rewritten as an SCLA-real atlas; CLAUDE.md cut to routing only. This log moved `scla/source-of-truth/decisions-log.md` → `decisions/log.md` (framework-standard path, history preserved via `git mv`). Duplicated facts (identity, roster, goals, voice) trimmed to one canonical owner each with pointers; canonical-owner table lives in GOVERNANCE.md.
**Rationale:** The repo was a half-finished framework install — placeholder navigation, governance describing nonexistent enforcement, and 10 duplication clusters drifting independently. One canonical home per fact keeps copies from contradicting each other.
**Owner:** Kierra Woekel (executed by Claude)

## 2026-05-11 — Stage 5 source-of-truth curation completed
**Decision:** Pipeline source-of-truth-curator agent ran Stage 5: supplemented all 5 stub files with pipeline outputs, created `onboarding.md` and `HANDOFF.md`, merged `(removed — ingest scratch)` into knowledge-base and operations files.
**Rationale:** Converts pipeline-generated content into a usable starting point for the SCLA team without overwriting the manual stubs.
**Owner:** source-of-truth-curator agent (pipeline)

## 2026-04-20 — MJML email template automation path decided
**Decision:** Kierra will use Claude to build an MJML template from 3 SCLA exemplars; hand to tech team (Sean/Shawn) for implementation. Unblocks Weekly News consistent cadence.
**Owner:** Kierra Woekel, Amy Westby
**Source:** Apr 20 Community Team Monday meeting notes

## 2026-04-20 — Community Google Drive as single source of truth + Claude KB pipeline
**Decision:** All team work goes into Community Google Drive. Kierra owns ingestion into Claude KB. Team pings Kierra in Slack when a doc is dropped.
**Owner:** Kierra Woekel
**Source:** Apr 20 Community Team Monday meeting notes

## 2026-04-13 — Team Projects tracker (Canva) as single source for action items
**Decision:** Team Projects tracker built by Kierra in Canva is the canonical home for all action items. Replaces Amy's personal OG Google Sheet for team-wide visibility.
**Owner:** Kierra Woekel
**Source:** Apr 13 Community Team Monday meeting notes

## 2026-04-06 — Claude Pro upgrade authorized
**Decision:** Team upgraded to Claude Pro (~$17/month) to unlock MCP calls and greater functionality. Intended to replace the Gemini-based Slack AI bot concept.
**Owner:** Amy Westby / Kierra Woekel (billing owner TBD)
**Source:** Apr 6 Community Team Monday meeting notes

## 2026-05-10 — SCLA-Profile redesigned as SCLA-native knowledge base
**Decision:** Migrated from generic template to SCLA-native structure. Renamed all `scla/` references to `scla/`. Separated programs, members, operations, partnerships into first-class directories.
**Rationale:** Generic template naming created confusion; SCLA-specific structure makes the knowledge base faster to navigate and easier for agents to target.
**Owner:** Kierra Woekel
