---
source: user conversation, 2026-04-24
generated_by: human (captured by claude)
last_updated: 2026-04-24
confidence: high
---

# SCLA Tooling Inventory (stakeholder-provided)

Captured directly from the client during the Stage 4 inventory gate.
This file is a primary input for the `workflow-mapper` agent — it
describes the tool landscape any workflow evidence should be
interpreted against.

## Tools used day-to-day

| Category | Tool | Notes |
|---|---|---|
| Team chat | Slack | Primary channel for internal comms |
| Email | Gmail | — |
| Docs & files | Google Drive | Likely home of meeting notes, SOPs, playbooks |
| Meetings | Zoom | — |
| AI assistance | Claude Pro | **Just acquired** — signals appetite for AI-enabled workflow changes |

## Tools explicitly NOT in use

- **Project / task tracking:** none. No Asana, Notion tasks, Jira, Linear,
  Trello, or equivalent. Work is coordinated ad-hoc via Slack + Gmail.
- **Ticketing / help desk:** not mentioned — treat as absent until
  confirmed.
- **CRM:** not mentioned — treat as absent until confirmed. (There is
  almost certainly a member database behind `app.thescla.org` /
  `members.thescla.org`, but the user did not flag it as a daily tool for
  the core team.)

## Automation-opportunity signals (for workflow-mapper)

The workflow-mapper should treat the following as high-value signals when
it reads the meeting notes and any other artifacts that arrive:

1. **No task tracker means work status lives in Slack threads and email.**
   Expect repeated "what's the status of X?" questions. Candidate pattern
   for lightweight status automation or a minimal Notion/Airtable board.
2. **Claude Pro is new.** Any recurring drafting, summarization, or
   reformatting work surfaced in meeting notes is a direct candidate for
   Claude automation. Flag these explicitly in
   `client/workflows/automation-opportunities.md`.
3. **Google Drive is the docs hub.** Shared folders and naming
   conventions observed in meeting notes are the closest thing SCLA has
   to an information architecture — worth mapping.
4. **Zoom + no note-taking tool mentioned.** If meeting notes are
   hand-written into a Google Doc after each call, that handoff is itself
   a candidate workflow (Zoom → auto-transcript → Claude summary → Drive).

## Open questions for next check-in

- Is there a member database or CRM behind `members.thescla.org`? Who
  maintains it?
- Is `shop.thescla.org` Shopify, or custom? Who handles fulfillment?
- How many people are on the core team, and who does what?
- Which Slack channels contain recurring process discussions (vs.
  one-off chatter)?
