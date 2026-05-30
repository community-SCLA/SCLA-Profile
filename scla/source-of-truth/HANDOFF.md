---
source: scla/source-of-truth-curator
generated_by: source-of-truth-curator
last_updated: 2026-05-11
confidence: medium
---

# Stage 5 Handoff — Source-of-Truth Curator

Run date: 2026-05-11. This file summarizes what was done, what still needs human input, and what to do next.

---

## What's Complete

### Stub files supplemented (`scla/source-of-truth/`)

| File | What was added |
|---|---|
| `mission.md` | Org-at-a-glance facts from web snippets (scale, founder, address, tagline hypothesis); mission/vision/values TODOs preserved |
| `program-names.md` | 10 new programs added from April meeting notes (Member Journey, Champions Ambassador, Focus Modes, Micro-Internships, etc.); table expanded with Source column |
| `voice-decisions.md` | All 5 voice-axis ratings from `scla/brand/voice-and-tone.md`; 4 confirmed verbatim copy samples; brand inconsistencies flagged (SCLA vs. The SCLA, honor society capitalization) |
| `decisions-log.md` | 4 new entries: MJML automation decided, Community Drive pipeline decided, Team Projects tracker decided, Claude Pro upgrade |
| `team-handbook.md` | Full community team roster (10 people + emails + roles); adjacent staff table; expanded tools table with Figma/Heygen/NotebookLM/etc.; reporting chain added |

### New files created (`scla/source-of-truth/`)

- `onboarding.md` — First-week checklist for new Community Team members (Day 1–5 + 30-day ongoing)
- `HANDOFF.md` — this file

### KB-delta merge — what went where

| Delta category | Destination file |
|---|---|
| Community team (10 people + emails + roles) | `scla/operations/team-roster.md` |
| Adjacent staff (Chuck, Sean/Shawn, Aman, Annie, Nollie, Joshua Todd, Boris, Victor, Brian) | `scla/operations/team-roster.md` |
| Programs (Member Journey, Conversion Program, Champions Ambassador, Honors/Academy tiers, Advisor Subcommittees, Prospectus, Nonprofit grant, Resume Builder, Interview Tool, SCCLA Benefit Hub, Course Catalog) | `scla/programs/programs-overview.md` |
| Tools (Team Projects tracker, weekly sync canvas, OG tracker, Notebook LM, Perplexity, Figma, Manis, Heygen/Synthesia, Google Analytics, Google Groups, LinkedIn) | `scla/operations/team-roster.md` tools section (see also `scla/source-of-truth/team-handbook.md`) |
| Terminology/jargon (canvas, tech team, community team, Focus Modes, the grand project, OG tracker, flying the plane while building it) | `scla/knowledge-base/glossary.md` |

**Note:** `(removed — ingest scratch)` deletion was attempted but the pipeline agent does not have `rm` permission in this environment. The file should be manually deleted or the user can run: `(removed — ingest scratch)` from the terminal.

---

## What Still Says `TODO: needs input`

These TODOs require human input — the pipeline cannot fill them from available source material.

### `mission.md`
- Official mission statement (verbatim)
- Official vision statement
- Confirmed core values
- 4 Pillars names (https://www.thescla.org/mission-history not yet scraped)

### `program-names.md`
- Confirm canonical capitalization: "SCA Academy" vs. "SCLA Academy"
- Confirm whether "Honors Community" and "SCA Academy" are official tier names or working labels

### `voice-decisions.md`
- Human confirmation of 5 voice-axis ratings (currently low-confidence hypotheses)
- 3–5 confirmed "we always/never do this" rules from Amy or Kierra
- Confirmed "Write this, not that" table rows
- Resolution of "SCLA" vs. "The SCLA" for running prose
- Resolution of "Honor Society" capitalization (title case vs. lowercase)

### `team-handbook.md`
- Correct spelling of Sean vs. Shawn
- Chuck's last name and full title
- Brian (CFO) last name
- Formal org chart

### `scla/operations/team-roster.md`
- Pat Sidhu's current title and day-to-day role
- Co-founders (snippets say "Founders, led by Pat Sidhu")
- Full leadership team (https://www.thescla.org/leadership-team not yet scraped)
- NAB membership, remit, and chair
- Joshua Todd identity/purpose (flagged by Amy in Slack)

### `scla/knowledge-base/glossary.md`
- ISPI full name (not available in snippets)
- "Dashboard" product definition — is it the Figma Focus Modes mockup, the Team Projects tracker, or a separate artifact?

### `scla/programs/programs-overview.md`
- Chapter program: process and cost for institutions
- Membership fee structure: lifetime vs. annual
- AI Career Hub: proprietary vs. third-party
- Resume Builder PRD owner
- Interview tool official name
- Nonprofit grant entity name and structure
- Course catalog: publishing timeline

---

## Ship Faster — Top 3 P0/P1 Automation Opportunities

From `scla/operations/automation-opportunities.md`:

### P0-1: Claude-generated MJML email templates from Canva designs
**Unblocks:** Weekly News consistent cadence (currently stalled on Sean/Shawn bottleneck)
**How:** Amy sends Kierra 3 MJML exemplars → Kierra feeds them + current Canva design to Claude → parameterized MJML template handed to tech team
**Effort:** S–M (day to week). Already decided. Just needs execution.
**Success metric:** 4 consecutive weeks of Weekly News without Sean on the critical path

### P0-2: Community Google Drive → Claude knowledge base → dashboard
**Unblocks:** Institutional knowledge preservation; ends "where does this doc live?" questions
**How:** Drop folder conventions (`/journey`, `/sops`, `/campaigns`, etc.); Kierra ingests weekly; Claude answers "what's the latest on X?" with citations
**Effort:** M (week for v1; ongoing after). Already decided.
**Success metric:** Jenna gets a first-draft SOP template from Claude within 48h of asking

### P1-3: Google Apps Script email triage (Gmail + Google Groups workaround)
**Unblocks:** Manual Google Groups access grants; inbound email routing chaos
**How:** Apps Script trigger on Gmail → classify by partner domain + subject keywords → route labels to right team member → fallback to human queue
**Effort:** M (week). Team already sketching this offline.
**Success metric:** Top 80% of inbound mail routes automatically in under 2 minutes

---

## Suggested First 3 Edits (for the SCLA team)

These are the highest-value human edits to make these files truly yours:

1. **`mission.md` — Write the official mission and vision statements** (even a draft). The pipeline left placeholders; your actual words go here. Once filled in, all agents will use them as source of truth.

2. **`voice-decisions.md` — Add 3 confirmed voice rules** in the "Confirmed decisions" section. Format: "We always [X]. We never [Y]." This unlocks accurate AI-generated copy across all future pipeline runs.

3. **`team-handbook.md` — Confirm Sean vs. Shawn spelling and add Chuck's full name**. These appear in meeting notes constantly and the ambiguity will keep surfacing as a TODO in every pipeline run until resolved.
