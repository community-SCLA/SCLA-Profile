---
source:
  - docs/_archive/source-dumps/community-learning/member-support/member-support-plan-spec.md
  - scla/projects/kb-integration-plan.md
  - docs/_archive/source-dumps/community-learning/member-support/scla-membership-team-two-tier-communication-sop.md
last_updated: 2026-06-16
version: 1.0
---

# SCLA Member Support System
## Specification & Operating Flow

**Version:** 1.0 · **Date:** June 16, 2026 · **Status:** Proposed
**Owner:** SCLA Community Team

---

## 1. Purpose

Every member question — no matter where it comes from — should land in one place,
get answered correctly within one business day, and make the next answer faster.

This document specifies that system end to end: how a message arrives, how it is
routed, how it is answered, how it escalates, and how the system learns.

---

## 2. The System at a Glance

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                     SCLA MEMBER SUPPORT FLOW                         │
  │                                                                       │
  │   INTAKE  ──▶  TRIAGE  ──▶  ANSWER  ──▶  RESOLVE  ──▶  LEARN        │
  │     ①             ②           ③            ④            ⑤           │
  └─────────────────────────────────────────────────────────────────────┘
```

The five stages are described in order below.

---

## 3. Stage ① — Intake

All inbound member messages converge into a **single queue** regardless of channel.
One place to look. One SLA clock. No message lost between inboxes.

```
  CHANNEL                            QUEUE
  ──────────────────────────         ───────────────────────────────
  Email  (membership@thescla)  ┐
  Dashboard / platform msgs    ├──▶  Unified queue
  Website support chat         │     · case record created
  Slack  /askscla              ┘     · SLA timer starts
                                     · source channel tagged
```

| Channel | Notes |
|---|---|
| Email | `membership@thescla.org` — canonical member-facing address |
| Dashboard / platform | Messages sent from inside the member portal |
| Website support chat | Live chat widget on thescla.org |
| Slack | `/askscla` for internal and staff-surfaced questions |

**Identity resolution & dedup.** On arrival each message is matched to a member
record. If the same person contacts support on two channels about the same issue,
the system merges them into one case — not two open tickets.

---

## 4. Stage ② — Triage

Every case is classified along two axes. This classification is the shared language
of the entire system — routing, answer lookup, templates, and reporting all use it.

**Axis 1 — Route** *(what is this about?)*

| Route | Covers |
|---|---|
| `general` | What is SCLA, how to contact, general information |
| `membership` | Joining, eligibility, invitations |
| `payments` | Dues, billing, refunds |
| `programs` | Courses, certifications, credit |
| `account` | Login, portal, technical access |
| `administrator` | Campus administrator inquiries |

**Axis 2 — Tier** *(who is asking?)*

| Tier | Who | SLA |
|---|---|---|
| Tier 1 | Non-member or pre-payment contact | 24 business hours |
| Tier 2 | Active member / portal user | 24 business hours |

Route + Tier together determine which team handles the case and which response
templates apply. Cases route to a **function, not a named person** — coverage holds
as the team changes.

---

## 5. Stage ③ — Answer

Answers are drawn from a single, versioned **Knowledge Base** — not improvised.

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                          KNOWLEDGE BASE                               │
  │                                                                       │
  │   faqs.md       ──build──▶   faqs.json    ──▶   suggested reply       │
  │   (version-controlled          (published          shown to           │
  │    source of truth)             artifact)          support agent)     │
  │                                                                       │
  │   · One source of truth for all answer content                        │
  │   · Every published answer is reviewed and traceable                  │
  │   · If an answer is not in the KB, it is flagged as a gap — not guessed│
  └──────────────────────────────────────────────────────────────────────┘
```

When a case is triaged, the system surfaces the grounded answer for the route + tier.
The agent reviews, personalizes if needed, and sends. Updating one answer in the KB
updates it across every channel and template automatically.

---

## 6. Stage ④ — Resolve & Escalate

Most cases are answered from the KB and closed. When a case needs specialist
attention it escalates by **route** — never to a random inbox.

```
  ESCALATION PATHS  (by route)
  ──────────────────────────────
  account     ──▶  Technical support
  payments    ──▶  Finance / billing
  programs    ──▶  Community / programs team
  membership  ──▶  Membership team
  general     ──▶  Membership team  (default)
```

The SLA timer runs for the life of the case and stops when the issue is resolved
or the case is formally closed.

---

## 7. Stage ⑤ — Learn

The system improves itself. Two signals feed back into the KB:

1. **Staff replies** to routed cases — harvested nightly.
2. **Recurring questions with no adequate answer** — gaps surfaced by reporting.

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                        THE LEARNING LOOP                              │
  │                                                                       │
  │   live cases  ──▶  recurring gap detected  ──▶  Harvester             │
  │                                                       │               │
  │                                                       ▼               │
  │                                           draft update to faqs.md     │
  │                                                       │               │
  │                                                       ▼               │
  │                                       human reviews and approves      │
  │                                                       │               │
  │                                                       ▼               │
  │                                   KB grows; next identical question   │
  │                                   answered instantly from canon       │
  └──────────────────────────────────────────────────────────────────────┘
```

Nothing reaches members without human review. The harvester proposes; a person
approves. Over time the KB covers more ground, faster, from real member data.

---

## 8. Systems of Record

| Domain | System of record | Why |
|---|---|---|
| **Answer content** | `faqs.md` in GitHub | Version-controlled, reviewed, traceable |
| **Case state** (owner, status, SLA) | Case / queue tool | Live operational state |

`faqs.json` on Drive is a published copy the surfaces read from — never edited
directly. All answer changes go into `faqs.md` and propagate outward on next build.

---

## 9. Operating Principles

- **One queue.** Every channel converges. Nothing lives in a private inbox.
- **24-business-hour SLA** on every case, both tiers.
- **Route-based ownership.** Cases route to a function — coverage survives staffing changes.
- **Grounded answers only.** If it is not in the KB, it is not sent — it becomes a flagged gap.
- **Human-in-the-loop learning.** The system drafts KB updates; people approve them.

---

## 10. Open Items

| Item | Needs |
|---|---|
| Case / queue tooling | Which platform hosts the unified queue |
| AI routing | Single automated router selected (not multiple competing) |
| Dashboard channel rollout | Sequencing the portal as an active intake source |

Items not yet decided are tracked here and marked `TODO: needs input` in the KB —
never assumed.
