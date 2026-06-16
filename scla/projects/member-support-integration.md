---
source:
  - scla/projects/kb-integration-plan.md
  - docs/_archive/source-dumps/community-learning/member-support/scla-membership-team-two-tier-communication-sop.md
last_updated: 2026-06-16
version: 1.0
---

# SCLA Member Support System — Proposal Brief

**Date:** June 16, 2026 · **Status:** Proposed · **Owner:** SCLA Community Team

---

## The idea in one line

Every member question — from any channel — lands in **one queue**, gets answered
from **one knowledge base** within **one business day**, and feeds back to make the
next answer faster.

---

## The flow

```
  INTAKE  ──▶  TRIAGE  ──▶  ANSWER  ──▶  RESOLVE  ──▶  LEARN
    ①            ②           ③            ④            ⑤
```

**① Intake** — Email, member dashboard, website chat, and Slack all converge into a
single queue. Each message becomes a case with an SLA clock. If the same person
reaches out twice on different channels, the cases merge into one.

**② Triage** — Every case is tagged two ways:
- **Route** — `general · membership · payments · programs · account · administrator`
- **Tier** — Tier 1 (non-member / pre-payment) or Tier 2 (active member)

Route + Tier decide which team handles it and which templates apply. Cases route to a
**function, not a named person**, so coverage holds as the team changes.

**③ Answer** — Replies come from the knowledge base (`faqs.md`), not improvised. If an
answer isn't in the KB, it's flagged as a gap — never guessed.

**④ Resolve** — Most cases close from the KB. Specialist cases escalate by route
(account → technical, payments → finance, programs → community, membership → membership).
The 24-business-hour SLA runs until the issue is resolved.

**⑤ Learn** — Recurring questions with no good answer, plus staff replies, are
harvested nightly into draft KB updates. A person reviews and approves before anything
goes live. The KB grows itself from real member data.

---

## What lives where

| | System of record |
|---|---|
| **Answer content** | `faqs.md` (version-controlled, reviewed) |
| **Case state** (owner, status, SLA) | The case / queue tool |

---

## Principles

- **One queue** — nothing lives in a private inbox
- **24-business-hour SLA** — every case, both tiers
- **Route-based ownership** — survives staffing changes
- **Grounded answers only** — not in the KB means it's a flagged gap, not a guess
- **Human-in-the-loop learning** — the system drafts, people approve

---

## Open items for the team

| Item | Decision needed |
|---|---|
| Queue tooling | Which platform hosts the unified queue |
| AI routing | One automated router (not several competing ones) |
| Dashboard channel | When the member portal goes live as an intake source |
