---
source: manual
generated_by: source-of-truth-curator
last_updated: 2026-06-12
---

# SCLA Decisions Log

Running log of notable team decisions. Append new entries at the top.

## 2026-06-17 — Archive consolidation: docs/ removed, source-dumps moved to _archive/
**Decision:** Eliminated the `docs/` root folder entirely. `docs/` existed solely as a wrapper around `docs/_archive/source-dumps/` — it had no other purpose and created a confusing second archive location alongside the already-approved root `_archive/`. Moved `source-dumps/` directly into `_archive/source-dumps/`. Updated all references in CLAUDE.md, MAP.md, GOVERNANCE.md, and `hooks/governance-check.sh`. Removed `docs` from the approved root layout in both GOVERNANCE.md and the governance hook. Note: the 2026-06-16 decisions log entry references the old path `docs/_archive/source-dumps/community-learning/member-support/...`; the canonical path is now `_archive/source-dumps/community-learning/member-support/...`.
**Rationale:** One archive location (`_archive/`) with a clear subfolder (`source-dumps/`) is less confusing than two archive paths with different names. Raw exports now live at `_archive/source-dumps/` and are covered by the existing "never load by default" rule in CLAUDE.md.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-17 — /scla restructure: knowledge-base → member-support, source-of-truth archived
**Decision:** (1) Renamed `scla/knowledge-base/` to `scla/member-support/` — the new name better reflects the folder's actual purpose (member-facing support content, not a generic KB). (2) Moved `scla/projects/kb-integration-plan.md` and `scla/projects/member-support-integration.md` into `scla/member-support/` so the integration planning docs live beside the content they govern. (3) Moved `scla/source-of-truth/` (charter.md, mission.md, onboarding.md, program-names.md, rituals.md, team-handbook.md, voice-decisions.md) to `_archive/source-of-truth/` — canonical org facts are now maintained in `context/me.md` and `context/goals.md`; the source-of-truth folder is retained as read-only provenance. Updated CLAUDE.md, MAP.md, and GOVERNANCE.md to reflect new paths.
**Rationale:** `knowledge-base` was an ambiguous label; `member-support` is unambiguous and routes correctly. The source-of-truth folder was increasingly duplicating context files — archiving removes the drift risk while preserving history.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-17 — Governance hooks added: structural enforcement for new files and folders
**Decision:** Created `hooks/governance-check.sh` and registered all hooks in `.claude/settings.json`. The governance hook fires as a PreToolUse check on Write and Bash tool calls and enforces six rules from GOVERNANCE.md: (1) banned directory names (`notes/`, `misc/`, `tmp/`, `inbox/`); (2) new root-level items must be in the approved layout; (3) no parallel decisions log files; (4) CLAUDE.md only at root or under `scla/projects/`; (5) future-home placeholders (`scheduled-tasks/`, `sops/`) require real content; (6) `_archive` not `archive` naming. Also wired the previously-orphaned `pre-tool.sh`, `post-tool.sh`, `stop.sh`, and `skill-eval.sh` hooks into `settings.json` — they were documented in GOVERNANCE.md as hard stops but were not registered.
**Rationale:** The governance rules existed in GOVERNANCE.md but nothing enforced them at the moment of creation. Now structural violations are blocked before they land in the repo rather than caught in a manual lint-refs run.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-16 — Member Support System: unified operating spec adopted
**Decision:** Reconciled the independently-authored Member Support Spec with the FAQ knowledge-base system into a single unified operating flow. Adopted a five-stage model — Intake, Triage, Answer, Resolve, Learn — documented in `scla/projects/member-support-integration.md`. Three explicit decisions made: (1) answer content canon stays in `faqs.md` in GitHub, not GDrive; (2) one AI router selected at implementation time, not two competing routers; (3) dashboard/platform messaging added as a fourth intake channel with cross-channel dedup/merge owned by the case layer. Settled open questions: canonical support email = `membership@thescla.org`; SLA = 24 business hours; Tier 1 = non-member/pre-payment, Tier 2 = active member/portal; system-of-record split = case state (case tool) / answer content (GitHub). Original spec archived at `docs/_archive/source-dumps/community-learning/member-support/member-support-plan-spec.md`.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-12 — Structure audit: routing fixes + `references/` created
**Decision:** Ran `/kb-audit` (scored 85/100, Stage 2; saved to `audits/audit-2026-06-12.md`) and fixed the routing/health defects it surfaced. Archived the stale `_inbox/INGEST_MANIFEST.md` (generated 2026-06-10, pre-restructure) to `_archive/INGEST_MANIFEST-pre-2026-06-11.md` so `/ingest` can't auto-fire on an already-organized repo. Repaired `scripts/lint-refs.sh` to exit 0 honestly: added `.remember/` to skip-paths, excluded `decisions/log.md` from the stale-path check (its migration entry legitimately cites the old path), and excluded `.svg` art files from the legacy-hex check. Corrected bare-filename backticks in GOVERNANCE.md to full paths, fixed a stale spec path in the kb-audit skill, removed a duplicate logo (`scla/brand/SCLA-Logo.svg`; identical copy kept in `assets/`), and listed `knowledge-base/TODOS.md` in MAP.md. Created the `references/` directory with `references/notion-api.md` as the first connected-tool reference; added it to the approved root layout and routing tables.
**Rationale:** The framework was structurally sound but its own linter was failing and the ingest trigger was primed to re-fire — both erode the "routes effectively" guarantee. `references/` was the highest-leverage audit gap (six MCP tools wired, zero references).
**Owner:** Kierra Woekel (executed by Claude)


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
