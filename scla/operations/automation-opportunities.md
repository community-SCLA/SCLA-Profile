---
source: Community Team Mondays notes Apr 2026 (archived externally); stakeholder notes (archived externally)
generated_by: workflow-mapper
last_updated: 2026-04-24
confidence: medium
---

# SCLA — Automation Opportunities

Derived from three consecutive Community Team Mondays (Apr 6, 13, 20, 2026)
plus the stakeholder tooling inventory. Priorities reflect what the team
has already *said out loud* that they want, plus inferred high-leverage
patterns. **Several of these are not speculative — the team has already
decided to do them.** The job is execution, not persuasion.

Tool lens: Slack, Gmail, Google Drive, Zoom, Claude Pro (just acquired,
appetite for MCP). The team also uses Canva heavily (trackers + design),
Google Sheets (Amy's personal "OG" tracker + Chuck tracker), Notebook LM,
Perplexity, Figma, Heygen/Synthesia. No Notion, no Jira, no Airtable —
proposals stick to tools already in play.

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

**Why this matters**

Sean/Shawn has been a bottleneck across every meeting read. Apr 6:

> "Zeketra Grandy has successfully created the content in Canva for weekly announcements, but the team is waiting for Sean to convert them into MJML email templates for use in campaigns, preventing a consistent rhythm from starting."
> *source: Apr 6 notes (archived externally — not in repo)*

Apr 20 recorded the decided path:

> "Kierra Woekel offered to use Claude to build an MJML template based on three desirable samples, which would then be provided to the tech team for implementation. Amy Westby agreed to work with Kierra Woekel offline to execute this plan."
> *source: Apr 20 notes (archived externally — not in repo)*

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

**Why this matters**

Apr 20 established the decided pipeline:

> "Kierra Woekel reiterated the request for team members to drop their work into the community Google Drive and ping them so they can feed it to Claude for the dashboard."

And on SOPs:

> "Kierra Woekel responded that they do not have a template but explained that Amy Westby and they are planning to use a Claude Pro account to scrape all information, create a knowledge base, and then automate the creation of a suitable structure."
> *source: Apr 20 notes (archived externally — not in repo)*

Stability angle (Apr 20):

> "Kierra Woekel also noted the importance of preserving institutional knowledge of the work that has been completed."

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

**Why this matters**

Apr 6:

> "Kierra Woekel, Amy Westby, and Yesse Ordonez are continuing to work offline on developing a system to triage incoming emails, which could involve creating an app script in Google to automate rerouting based on keywords or partners. Kierra Woekel confirmed that the Google Groups issue is a glitch, and while granting access manually is possible, they are looking for the permanent solution that the groups feature would provide."
> *source: Apr 6 notes (archived externally — not in repo)*

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

**Why this matters**

Apr 6:

> "Kierra Woekel has been developing a free Gemini-based AI agent to host in Slack that can summarize threads, pull action items, autogenerate weekly summaries, and help locate resources."
> *source: Apr 6 notes (archived externally — not in repo)*

Apr 6 decision:

> "Kierra Woekel suggested that the best investment would be to upgrade their Claude account to a paid Claude Pro level for approximately $17 a month, as this would open up MCP calls and allow for greater functionality, potentially serving as a replacement for the requested native Slack AI bot."

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

**Why this matters**

Apr 20:

> "Kierra Woekel offered the idea of an AI agent that could translate a student's duties into outcome-driven language, similar to a skills file they developed for another organization. Zeketra Grandy agreed, suggesting students should input their duties and target job description to ask the AI to determine transferable skills and help communicate them effectively. Kierra Woekel proposed using Claude's user-friendly interface to create a pop-up guiding the student through a back-and-forth conversation to extract information, rather than just filling out boxes."
> *source: Apr 20 notes (archived externally — not in repo)*

Zeketra confirmed the content problem (not just UI):

> "many students struggle with the content itself, specifically identifying transferable skills and knowing what words to write."

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

Apr 20:

> "Amy Westby emphasized the need for a better process or tool for managing the change log, future requests, and backlog, which would allow the team to document input from the field. They suggested that Sean, the team, and Chuck could prioritize the rollout of changes based on this documentation, noting the communication differences between Sean's zero documentation and the team's extensive documentation."

**Proposed shape:** a structured Google Doc (or Claude-curated one) with
columns {source, category, severity, proposed-fix, status}. Weekly
Claude digest highlights unprocessed items before the Monday meeting.

---

### 8. Google Analytics → member journey drop-off dashboard

Apr 20:

> "Kierra Woekel suggested analyzing Google Analytics data to identify where members are dropping off in the current client journey."

Context for scale: 15,000 onboarded since Dec 1; 30,000 members since
Jul 1; 317 refunds (~1%). Data exists — it just isn't being mined.

---

### 9. Course production pipeline (Heygen + Synthesia + Claude script drafting)

Apr 13:

> "they may need to hire an additional person to focus on building the courses due to the amount of work involved, even with tools like Hey Gen and Synthesia for videography help from Annie."

Only 2 of 61–62 courses exist. Heygen and Synthesia are already in use.
Claude can draft lesson scripts, quiz items, and syllabus outlines from
the course catalog (Mayeth's work). Ask Claude to do the "first 70%"
before Annie's videography step.

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
