---
source: client/_raw/INGEST_ERRORS.md | client/_raw/artifacts/inbox/Copy of Community Team Mondays - 2026_04_06 15_56 CDT - Notes by Gemini.md | client/_raw/artifacts/inbox/Copy of Community Team Mondays - 2026_04_13 15_55 CDT - Notes by Gemini.md | client/_raw/artifacts/inbox/Community Team Mondays - 2026_04_20 16_00 CDT - Notes by Gemini.md | client/_raw/artifacts/inbox/stakeholder-notes.md | client/brand/TODOS.md | client/knowledge-base/TODOS.md | client/workflows/automation-opportunities.md | client/workflows/pain-points.md
generated_by: source-of-truth-curator
last_updated: 2026-04-25
confidence: high
---

> This page is the team's — edit it freely. Generated on first pass from the onboarding pipeline; no longer auto-regenerated.

# Handoff — Pipeline Completion Summary

This document records what the onboarding pipeline produced, what is still incomplete, and the exact next actions required from the SCLA team to make this workspace production-ready.

---

## What is complete

### Stage 1 — Ingest

**Status: Partial — blocked by sandbox egress proxy**

The ingestor ran successfully but was blocked from reaching any `thescla.org` domain by the execution environment's egress proxy. The proxy returns `"Host not in allowlist"` for all SCLA URLs regardless of approach (HTTP, headless browser, etc.). This is a sandbox-side constraint, not a SCLA-side issue.

What was successfully ingested:
- Google search-index snippets for thescla.org (low-confidence partial content)
- Three Community Team Monday meeting notes (Apr 6, 13, 20, 2026) — high-quality source material
- Stakeholder tooling inventory (provided directly by the client)

What was not ingested (and why):
- Full website content for all thescla.org pages — blocked (see `client/_raw/INGEST_ERRORS.md`)
- Google Drive documents — Drive URL was not provided in `client.config.yml`
- Any PDF or doc files from `client/_raw/docs/inbox/` — directory was empty

**Confidence: low** for anything derived from the website; **high** for anything derived from the meeting notes.

---

### Stage 2 — Brand

**Status: Scaffold complete; confidence low — needs website content**

Produced:
- `client/brand/brand-guide.md` — organizational identity, at-a-glance data, known copy inconsistencies
- `client/brand/voice-and-tone.md` — voice axis analysis from available snippets; confirmed copy samples
- `client/brand/TODOS.md` — prioritized list of what to provide to raise confidence

All visual identity fields (primary color, fonts, logo files, brand PDF) are `TODO: needs input`. The voice analysis is based on approximately 7 KB of search-index snippet text — insufficient for high-confidence characterization.

**Confidence: low**

---

### Stage 3 — Knowledge Base

**Status: Scaffold complete; confidence low — needs website content**

Produced:
- `client/knowledge-base/glossary.md` — 12 terms defined; most with `TODO: needs input` for full definitions
- `client/knowledge-base/people.md` — Pat Sidhu as founder (confirmed); leadership team page not scraped; functional teams not documented
- `client/knowledge-base/products-services.md` — full benefits list from search snippets; pricing confirmed ($95); deeper product details missing
- `client/knowledge-base/faqs.md` — inferred from snippets; not verbatim from actual FAQ pages
- `client/knowledge-base/TODOS.md` — 15 priority pages to export; additional internal documents requested

Notable gap: the community team members (Amy, Kierra, Zeketra, etc.) are not yet documented in `people.md`. The workflow-mapper captured them in `client/workflows/kb-deltas.md` — a human or re-run of Stage 3 should merge that data.

**Confidence: low**

---

### Stage 4 — Workflows

**Status: Complete and high-quality — sourced from meeting notes**

Produced:
- `client/workflows/current-state.md` — 10 workflows documented with steps, owners, and pain points
- `client/workflows/pain-points.md` — 11 pain points prioritized P0 through P2
- `client/workflows/automation-opportunities.md` — 10 automation opportunities; 3 already committed by the team (P0/P1)
- `client/workflows/kb-deltas.md` — list of people, programs, tools, and terms to add to the knowledge base

The meetings provided rich evidence. Confidence is medium (not high) because the meeting notes are AI-generated (Gemini) and cover only a 3-week window.

**Confidence: medium**

---

### Stage 5 — Source of Truth (this stage)

**Status: Complete**

Produced:
- `client/source-of-truth/README.md` — front door with Ship Faster section and team quick-reference
- `client/source-of-truth/charter.md` — mission, vision, values, Q2 success definition
- `client/source-of-truth/decisions-log.md` — 8 decisions logged from Apr 6–20 meetings; template for future entries
- `client/source-of-truth/team-handbook.md` — meeting cadence, communication norms, tool ownership
- `client/source-of-truth/rituals.md` — 7 rituals documented with owners and cadence
- `client/source-of-truth/onboarding.md` — first-week checklist for new hires
- `client/source-of-truth/HANDOFF.md` — this file

**Confidence: medium** (limited by the same gaps as stages 1–3)

---

## What still says `TODO: needs input` across the workspace

The following are the highest-impact gaps. Resolving these would raise pipeline confidence from low/medium to high.

### Critical — blocks other work

| File | What is missing | Why it matters |
|---|---|---|
| `client/brand/TODOS.md` (Priority 1) | Full website page exports (13 URLs listed) | Unblocks voice/tone, visual identity, and the full knowledge base |
| `client/brand/TODOS.md` (Priority 2) | Logo files (SVG and PNG) | Required for any design work |
| `client/brand/TODOS.md` (Priority 3) | Brand guidelines PDF or style guide | Required for color palette, typography, design tokens |
| `client/knowledge-base/people.md` | All 10 community team members + adjacent people | Critical for onboarding and institutional knowledge |
| `client/source-of-truth/charter.md` | Chuck's full name and title | Team needs to know who their leadership contact is |
| `client/source-of-truth/team-handbook.md` | Sean/Shawn's correct full name | Causes confusion in external communications |
| `client/source-of-truth/team-handbook.md` | Slack workspace admin; channel list for new hires | Required to complete the onboarding checklist |

### Important — degrades usability

| File | What is missing |
|---|---|
| `client/knowledge-base/glossary.md` | ISPI full name; 4 Pillars by name; NAB full name and purpose |
| `client/knowledge-base/products-services.md` | Is the $95 fee paid by the student or institution? Is it renewable? |
| `client/workflows/current-state.md` | Channel for submitting tech team requests; Zoom license upgrade status for May 26 event |
| `client/source-of-truth/onboarding.md` | Slack channel list; Google Drive folder map; platform access provisioning process |
| `client/workflows/automation-opportunities.md` | Who is the single owner of the Claude Pro account? |

### Nice to have

| File | What is missing |
|---|---|
| `client/brand/TODOS.md` (Priority 4) | Tagline confirmation ("From Campus to Career") |
| `client/brand/TODOS.md` (Priority 5) | Name style confirmation ("SCLA" vs. "The SCLA"; "Honor Society" capitalization) |
| `client/source-of-truth/rituals.md` | Spotify team playlist link once created |
| `client/workflows/current-state.md` | Chapter operations workflow; Shop/fulfillment workflow; CEO Speaker Series cadence |

---

## Suggested first 3 edits for the SCLA team

These are the highest-leverage changes the team can make right now, without any additional pipeline runs:

**1. Export 5 website pages and re-run `/ingest` then `/brand` and `/kb`**

This single action removes the root cause of all `confidence: low` ratings. Priority order: homepage, /benefits, /mission-history, /leadership-team, /faq. Use a browser on any machine outside this sandbox. Save as PDF or HTML. Drop into `client/_raw/docs/inbox/`. Re-run the pipeline.

See `client/_raw/INGEST_ERRORS.md` for the full instructions and the complete list of 13 priority pages.

**2. Add the 10 community team members to `client/knowledge-base/people.md`**

The workflow-mapper captured all names, emails, and roles in `client/workflows/kb-deltas.md`. Copy that table into `people.md` and expand each person with their actual responsibilities, Slack handle, and a short bio. This makes the knowledge base immediately useful for onboarding and for the Claude knowledge-base ingestion that Kierra is building.

**3. Fill in the `TODO: needs input` fields in `client/source-of-truth/team-handbook.md`**

Specifically: (a) confirm Sean/Shawn's full name; (b) add Chuck's full name and title; (c) list the Slack channels every new hire should join; (d) add the channel or process for submitting tech team requests. These four items make the handbook usable for the next person who joins the team.

---

## Re-running the pipeline

The `source-of-truth/` directory is protected by the `.source-of-truth-generated` marker file. Re-running the full pipeline will regenerate stages 1–4 but will not overwrite stage 5. To regenerate stage 5, delete the marker file first and confirm with the pipeline operator.

Stages 1–4 are idempotent: re-running them from new `_raw/` inputs will regenerate their outputs from scratch. This is the intended update path once the website exports and additional documents are provided.

---

## Key dates to track

| Date | Event |
|---|---|
| May 26–27, 2026 | University of Phoenix event (500+ attendees) — Jenna Heath confirming Zoom license |
| June 2026 | Community team contract milestone — Amy has confirmed team is staying |
| August 1, 2026 | Focus Modes launch — Anushka Gupta owns content build |
