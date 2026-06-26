---
source: Community Team Mondays notes Apr 2026 (archived externally); stakeholder notes (archived externally)
---

# SCLA — Automation Opportunities

Derived from Community Team Mondays (Apr 6, 13, 20, 2026) plus the stakeholder tooling inventory.

Tools in play (proposals stick to these): Slack, Gmail, Google Drive, Zoom, Claude Pro (MCP), Canva (trackers + design), Google Sheets (Amy's "OG" tracker + Chuck tracker), Notebook LM, Perplexity, Figma, Heygen/Synthesia. No Notion, Jira, or Airtable.

---

## P0 — The team has already committed to these

### 1. Claude-generated MJML email templates from Canva designs

| Field | Value |
|---|---|
| **Workflow** | [Weekly News email production](./current-state.md#weekly-news-email-production) |
| **Type** | rule/bot + context-passing-doc |
| **Tools involved** | Canva → Claude Pro → MJML → tech team handoff |
| **Est. time saved** | Unblocks a weekly cadence currently stalled; removes "Sean" as single point of failure |
| **Effort** | S–M (day to week) |
| **Priority** | P0 (blocking weekly cadence) |
| **Dependencies** | 3 sample MJML source files from Amy; Claude Pro access; Canva export of current design |

**Status:** decided (Apr 20). Kierra builds an MJML template from three sample files and hands it to the tech team for implementation, routing around Sean/Shawn's MJML conversion bottleneck.

**Proposed shape**

Amy sends Kierra 3 MJML exemplars. Kierra feeds them + the current Canva
design to a Claude project with MJML/email-rendering context. Claude
emits a parameterized MJML template (tokens, colors, brand rules). The
output is handed to Sean/Shawn for implementation rather than requiring
Sean to author from scratch. On later cycles, the same project converts
new Canva designs directly.

**Success metric**

Weekly announcements ship on a consistent cadence for 4 consecutive
weeks without Sean being on the critical path for authoring.

---

### 2. Community Google Drive → Claude knowledge base → dashboard

| Field | Value |
|---|---|
| **Workflow** | [Member journey / onboarding documentation](./current-state.md#member-journey-funnel) + cross-team institutional knowledge |
| **Type** | integration + context-passing-doc |
| **Tools involved** | Google Drive ↔ Claude Pro ↔ dashboard surface |
| **Est. time saved** | Compounding — eliminates "where does this doc live?" and enables every future agent to cite SCLA context |
| **Effort** | M (week) for v1; ongoing |
| **Priority** | P0 (already decided + teammate waiting) |
| **Dependencies** | Everyone actually dropping work into the community Drive; Kierra ingestion workflow |

**Status:** decided (Apr 20). Team members drop work into the community Google Drive; Kierra feeds it to a Claude Pro account that scrapes it, builds a knowledge base, and surfaces it on the dashboard — also preserving institutional knowledge.

**Proposed shape**

A single Claude project (or MCP-backed workspace) pointed at the
community Google Drive. Drop folder-level conventions: `/journey`,
`/sops`, `/campaigns`, `/courses`, `/advisor-subcommittees`. Kierra owns
ingestion cadence. A weekly cron feeds new/changed docs into the Claude
project. Team members ask Claude (via Slack or a web surface) "what's
the latest on X?" and get grounded answers with source-doc citations.

**Success metric**

Jenna can get a first-draft SOP template from Claude within 48h of
asking; team stops re-asking Amy where documents live.

---

### 3. Google Apps Script email triage (Gmail + Google Groups workaround)

| Field | Value |
|---|---|
| **Workflow** | [Inbound email triage](./current-state.md#inbound-email-triage) |
| **Type** | integration / rule-bot |
| **Tools involved** | Gmail → Apps Script → keyword/partner routing |
| **Est. time saved** | Small per-message × high volume; removes ongoing manual access grants |
| **Effort** | M (week) |
| **Priority** | P1 (team already sketching offline) |
| **Dependencies** | Gmail admin access; partner keyword list |

**Status:** in progress offline (Kierra, Amy, Yesse). Apps Script to reroute incoming email by keyword/partner, replacing manual access grants used to work around a Google Groups glitch.

**Proposed shape**

Apps Script trigger on incoming Gmail: classify by (a) partner domain,
(b) subject keyword patterns, (c) Claude-backed intent classification
for edge cases. Route labels → appropriate team member's inbox. Falls
back to a human-review queue for unclassifiable mail.

**Success metric**

Team stops manually granting Google Groups access as a workaround;
inbound mail routes in under 2 minutes without human intervention for
the top 80% of patterns.

---

## P1 — High leverage, implied but not yet explicitly assigned

### 4. Slack AI agent: thread summaries, weekly digest, action-item extraction

| Field | Value |
|---|---|
| **Workflow** | Weekly team sync + Slack as the de facto status ledger |
| **Type** | rule/bot |
| **Tools involved** | Slack ↔ Claude Pro |
| **Est. time saved** | ~1–2 hours/week for Amy (leadership update compilation) + ambient relief across team |
| **Effort** | M (week) |
| **Priority** | P1 |
| **Dependencies** | Slack app install; Claude Pro (done) |

**Status:** Kierra prototyped a Gemini-based Slack agent (thread summaries, action items, weekly summaries, resource lookup); the team upgraded to Claude Pro (~$17/mo, MCP) as the path forward.

**Proposed shape**

Slack → Claude bot with three commands: `/digest [#channel]` (weekly
rollup), `/actions [#channel]` (extract owned action items from last N
days), `/find [query]` (grounded search over the Drive KB from
opportunity #2). Weekly digest cron posts to `#community-team` Sunday
evening so Monday meetings start from a shared baseline.

**Success metric**

Amy's pre-Monday prep time drops below 15 minutes; team arrives at
Community Team Mondays already aligned on the previous week.

---

### 5. AI Resume Builder content upgrade (Claude-backed conversational)

| Field | Value |
|---|---|
| **Workflow** | Member support — resume feedback loop |
| **Type** | rule/bot / product feature |
| **Tools involved** | Platform resume builder ↔ Claude Pro |
| **Est. time saved** | Reduces inbound support for resume help; directly improves core product |
| **Effort** | L (month) — needs PRD + tech team buy-in |
| **Priority** | P1 |
| **Dependencies** | PRD (Amy flagged as needed); tech team capacity; Sean/Chuck prioritization |

**Status:** proposed (Apr 20). A conversational AI agent that takes a student's duties + target job description and outputs transferable skills as outcome-driven language. Addresses a content problem (students struggle to identify transferable skills and word them), not just UI.

**Proposed shape**

Conversational agent wraps the existing resume builder. Prompts extract
duties + target job description, outputs transferable-skills mapping +
outcome-driven bullet drafts. Gate behind the "newbie to career" focus
mode (launching Aug 1).

**Success metric**

Opt-in usage > 30% among new members in the "newbie" focus mode; Zeketra
sees resume quality improve in review samples.

---

## P2 — Nice to have, flagged but lower urgency

### 6. Meeting notes → Team Projects tracker auto-sync

| Field | Value |
|---|---|
| **Workflow** | Weekly project status |
| **Tools involved** | Zoom/Gemini meeting notes ↔ Team Projects tracker (Canva canvas) |
| **Effort** | M (week) |
| **Priority** | P2 |

Gemini already produces structured "Next steps" sections per meeting
(visible in all three Apr notes). Parse, match owners, append to the
centralized Team Projects tracker so the "Suggested next steps" list
stops evaporating into meeting-notes history.

---

### 7. Change log / feature request backlog tool

Need flagged Apr 20: a tool to manage the change log, future requests, and backlog, so Sean, the team, and Chuck can prioritize rollouts from documented field input.

**Proposed shape:** a structured Google Doc (or Claude-curated one) with
columns {source, category, severity, proposed-fix, status}. Weekly
Claude digest highlights unprocessed items before the Monday meeting.

---

### 8. Google Analytics → member journey drop-off dashboard

Analyze Google Analytics to find where members drop off in the journey (flagged Apr 20). Scale: 15,000 onboarded since Dec 1; 30,000 members since Jul 1; 317 refunds (~1%). Data exists but isn't being mined.

---

### 9. Course production pipeline (Heygen + Synthesia + Claude script drafting)

Only 2 of 61–62 courses exist; hiring an additional course-builder was raised Apr 13. Heygen and Synthesia are already in use (Annie). Claude can draft lesson scripts, quiz items, and syllabus outlines from the course catalog (Mayeth's work) — the "first 70%" before Annie's videography step.

---

### 10. Community-wide benefit promotion (SCCLA benefit hub)

Apr 20: Amy saved $90/night on a hotel using the benefit hub and
suggested the team promote it. No one owns this today — low-effort
automation: pin a weekly benefit highlight in a dedicated Slack channel
via scheduled message.

---

## Open questions needing human input

- Who owns the ongoing Claude Pro admin (account, billing, MCP access)?
  Apr 20 next-steps list both Amy and Kierra as "Acquire Claude" — clarify
  single owner.
- Is "Sean" and "Shawn" the same person? Apr 6 writes "Sean"; Apr 20 writes
  "Shawn." Treating as same person until corrected.
- What is the "dashboard" that Kierra keeps referring to? Context suggests
  a custom internal surface, but confirm whether it's the Figma focus-modes
  mockup, the Team Projects tracker, or a separate artifact.
- What's the canonical Drive folder structure for the community Drive? The
  Claude KB ingestion design (opp #2) depends on this. Mentioned as
  existing but not named in the notes.
