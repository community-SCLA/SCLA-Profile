---
source:
  - docs/_archive/source-dumps/community-learning/member-support/scla-membership-team-two-tier-communication-sop.md
last_updated: 2026-06-16
version: 2.0
---

# SCLA Member Support System — Integration Spec

**Date:** June 16, 2026 · **Status:** Proposed · **Owner:** SCLA Community Team

---

## Context

`scla/member-support/faqs.md` is the curated source of truth for member-facing answers, organized across six routes with explicit `<!-- route: -->` tags. Today, member support is manual and siloed: email triage happens by hand, Google Groups workarounds are unreliable, and questions arriving on different channels are handled inconsistently — sometimes by the wrong person, sometimes after too long a delay. The result is unpredictable response times, duplicated effort, and institutional knowledge that lives in inboxes rather than a shared base.

This spec defines the full member support system: a unified queue that consolidates every inbound channel, an AI-assisted triage and answering layer grounded in `faqs.md`, and a feedback loop that continuously grows the knowledge base from real member interactions. It covers the operating model (who owns what and how SLAs work) and the technical surfaces (Gmail, website/dashboard chat, Slack, and the future member portal).

Current team pain points this directly addresses:
- Email triage is manual (`scla/operations/current-state.md`)
- Google Groups workarounds are broken (`scla/operations/pain-points.md`)
- A "Slack AI agent" and "Apps Script email triage" are already on the automation wish list (`scla/operations/automation-opportunities.md`, items #3 and #4)

Stack: **Google Workspace + Gemini** for the AI layer, **Apps Script** as the glue for email and Slack, a **Cloud Function** for the chat backend, **GitHub** as the system of record for all answer content.

---

## Architecture at a glance

```
  INTAKE SURFACES                QUEUE LAYER             KNOWLEDGE BASE
  ─────────────────────         ─────────────          ────────────────────────
                                                        SCLA-Profile repo
  Gmail ───────────────┐                              scla/member-support/
  Website chat ────────┼──▶  unified case queue  ◀─── faqs.md  (source of truth)
  Slack /askscla ──────┤     (route + tier tags)            │
  Member portal ───────┘            │                       │ (1) push → build
         ↑                          │                       ▼
         │               ┌──────────┴──────────┐      faqs.json (Drive)
         │               │   AI ANSWER LAYER   │      served to all surfaces
         │               │  Gemini + faqs.json │◀─────────────────────────────
         │               │  confidence ≥ 0.8   │
         │               │  → auto-reply draft  │
         │               │  confidence < 0.8   │
         │               │  → route to human    │
         │               └──────────┬──────────┘
         │                          │
         │               ┌──────────┴──────────┐
         │               │   CAPTURE QUEUE     │   (3) staff reply observed
         │               │  (Google Sheet)     │◀───── by channel harvester
         │               │  ts · source · route│
         │               │  question · answer  │
         │               │  staff_answer · status│
         │               └──────────┬──────────┘
         │                          │ (4) nightly harvester
         │                          ▼
         │               PR bot opens PR against faqs.md
         │               Staff reviews → merges → loop closes
         └────────────── faqs.json republished to all surfaces
```

Numbered flows:
1. On every push to `main`, GitHub Actions converts `faqs.md` → `faqs.json` and uploads to Drive. All surfaces read from this single artifact.
2. Each surface sends member queries to Gemini with `faqs.json` as grounded context. High-confidence answers reply automatically (draft-only mode until validated per surface). Low-confidence routes to the correct human.
3. When a staff member replies, the channel's harvester captures the thread and records the Q&A pair in the capture queue Sheet.
4. A nightly GitHub Action opens a PR appending new Q&A pairs to `faqs.md` under the correct route. Staff review → merge → next publish cycle makes the new answer canonical on all surfaces.

---

## The five-stage flow

```
  INTAKE ──▶ TRIAGE ──▶ ANSWER ──▶ RESOLVE ──▶ LEARN
    ①           ②           ③          ④           ⑤
```

### ① Intake

Gmail (`community@thescla.org`), the website chat widget, Slack, and the member portal all converge into a single unified queue. Each inbound message becomes a **case** with a case ID, a timestamp, a source label, and an SLA clock. If the same person contacts support on two different channels about the same issue within a 48-hour window, the queue platform merges those into one case — the member sees one coherent thread; the team works one ticket.

### ② Triage

Every case is tagged along two dimensions before any human looks at it:

**Route** — which functional area owns the answer:

| Route | Covers |
|---|---|
| `general` | Catch-all for orientation and navigation questions |
| `membership` | Joining, renewing, membership benefits |
| `payments` | Billing, invoices, refunds |
| `programs` | Academic competitions, conferences, honors programs |
| `account` | Login, dashboard access, profile |
| `administrator` | Chapter- and institution-level admin questions |

**Tier** — which communication mode applies:
- **Tier 1** — non-member or pre-payment contact (prospective or lapsed member)
- **Tier 2** — active paying member

Route + Tier together determine which template set applies and which team handles escalation. Cases route to a **function, not a named person**, so the system survives staffing changes without reconfiguration. Routing is handled automatically by the AI layer using the `route_map` in `faqs.md`'s frontmatter — no hand-coded routing logic.

### ③ Answer

The AI layer queries Gemini with the member's question plus `faqs.json` as system context. Gemini returns `(answer, confidence, route)` or `(needs_human, route)`:

- **Confidence ≥ 0.8:** a reply draft is generated from the KB. During the validation period (first two weeks per surface), this stays as a staff-reviewed draft before sending. After validation, auto-send is enabled for that route.
- **Confidence < 0.8:** the case is routed to the correct human with the question, the route tag, and any partial KB context Gemini found.

All answers are grounded in `faqs.md`. If no KB answer exists, the case is flagged as a `gap` — the team is never put in the position of guessing.

### ④ Resolve

The 24-business-hour SLA clock runs from the moment a case is created until it is marked resolved. Escalation paths by route:

| Route | Escalation owner |
|---|---|
| `account` | Technical team (Kierra) |
| `payments` | Finance / Amy |
| `programs` | Community team |
| `membership` | Membership team (Yesse) |
| `general` | Any available staff |
| `administrator` | Community lead |

At 18 business hours, unresolved cases surface in `#community-team` Slack as an automated reminder. At 24 hours, the case status flips to `escalated` and the route's escalation owner receives a direct Slack message.

### ⑤ Learn

Every resolved case — and every staff-written reply — is harvested into the capture queue. A nightly job opens a PR adding new Q&A pairs to `faqs.md`. Staff review and merge. The moment the PR merges, the publish workflow fires: `faqs.json` is rebuilt and propagated to all surfaces. The next identical question gets answered from the KB automatically — without anyone touching a file.

---

## Surface 1 — Gmail (`community@thescla.org`)

The majority of inbound member contact arrives by email today. This surface is also the highest-risk for auto-reply errors, so it ships in draft-only mode first and advances to auto-send route by route.

**What to build:**
- Apps Script project bound to the `community@thescla.org` inbox.
- Time-driven trigger every 2 minutes: scans `label:unprocessed` threads.
- For each new thread: calls Gemini with the message body + `faqs.json` as system context.
- If `confidence ≥ 0.8`: creates a draft reply labeled `auto-answered`, logs to capture queue.
- If `confidence < 0.8`: re-labels the thread to the correct route label (`route/membership`, `route/payments`, etc.), logs to capture queue as `needs-human`.
- When a staff member sends a reply on a `needs-human` thread, a second trigger reads `getLatestReplyFromStaff()` and writes `staff_answer` + `status: harvested` to the capture queue row.

**Validation gate:** run draft-only for two weeks. Once accuracy on a given route reaches > 90% staff-approval-unchanged, flip `AUTO_SEND_ENABLED = true` in Script Properties for that route. Routes validate independently.

**Key files to create:**

| Path | Purpose |
|---|---|
| `integrations/gmail-apps-script/Code.gs` | Main handler, trigger registration, Gemini call, label management |
| `integrations/gmail-apps-script/prompts/system.md` | Grounded prompt (uses `faqs.json` + voice from `_archive/source-of-truth/voice-decisions.md`) |
| `integrations/gmail-apps-script/README.md` | Deploy instructions, Script Property key names |

Update `endpoints.md`: Gmail label IDs, Apps Script project ID. Gemini API key goes in Script Properties — never in the repo.

---

## Surface 2 — Website / Member Dashboard chat

The member dashboard and the AMA channel page are where active members go first. A native chat widget answers questions without requiring the member to open an email thread.

**What to build:**
- React component `<SclaSupportChat />` mounted on the member dashboard and the AMA channel page.
- Backend: a single Cloud Function (on the existing Google project) that:
  - Loads `faqs.json` from Drive (cached 5 minutes)
  - Calls Gemini with the member message + `faqs.json` + member identity from the dashboard's auth context (determines Tier 1 vs. Tier 2 automatically)
  - Streams the reply back to the widget
  - If `needs_human`: opens a case in the capture queue, returns to the member: "I've sent this to a staff member — expect a reply within one business day"
  - Logs every exchange (question, AI answer, thumbs up/down feedback) to the capture queue Sheet

**Why native widget over a third-party (Intercom, Drift):** the dashboard is custom code we control, there are no per-seat SaaS costs, and every transcript stays inside Google Workspace where the harvester can read it.

**Key files to create:**

| Path | Purpose |
|---|---|
| `integrations/chat-backend/index.js` | Cloud Function (Node.js), lives in this repo so it ships with the KB |
| `integrations/chat-backend/README.md` | Deploy instructions, env var names |
| `<dashboard repo>/components/SclaSupportChat.tsx` | Follow-up PR in the dashboard repo (referenced here for completeness) |

---

## Surface 3 — Slack (internal)

Two modes, shipping in order:

**Active: `/askscla` slash command**
- Slack app with one slash command `/askscla <question>` available in every channel.
- Backed by the same Cloud Function from Surface 2 — one backend, multiple surfaces.
- Returns the answer in-thread with message actions: `👍 correct` / `👎 wrong` / `📝 add correction`.
- `👎` or `📝` routes the exchange directly into the capture queue with the staff correction attached. Because staff already know the right answer when they thumbs-down, this is the fastest path to growing the KB.

**Passive: `#member-questions-inbox` monitoring (ships behind a feature flag)**
- The team already forwards member emails to a Slack channel for visibility.
- With this flag on: the Slack app posts a threaded Gemini draft in response to each forwarded message.
- Staff reply `/approve` to send the draft as-is, or edit and reply `/approve` to send their version.
- The staff edit becomes a gold-standard `staff_answer` row in the capture queue.

Slack ships before Gmail auto-reply and the public chat widget because blast radius is internal only — two weeks of `/askscla` usage validates Gemini answer quality route by route before any member sees it.

**Key files to create:**

| Path | Purpose |
|---|---|
| `integrations/slack-app/manifest.json` | Slack app manifest, slash command definition |
| `integrations/slack-app/handler.js` | Event routing, message-action handler, capture-queue writes |
| `integrations/slack-app/README.md` | Install instructions, credential locations |

---

## Surface 4 — Member Portal (future intake)

The member portal is a planned channel, not yet live. When it launches, support requests from the portal become a fourth intake surface using the same Cloud Function backend as the website chat widget. The portal's auth context (member ID, tier, account status) is passed as additional grounding to Gemini, enabling more precise answers.

**Pre-work needed before portal goes live:**
- Confirm portal auth token format so the Cloud Function can parse member identity
- Add a `portal` source label to the capture queue schema
- Define `route/account` case-creation behavior for the portal's UI

No additional infrastructure is needed — the capture queue, harvester, and publish pipeline already support a new `source` value.

---

## Case & queue layer

The queue layer is the routing and SLA backbone beneath all four surfaces. It is a configured support queue platform, not a custom build. The platform choice is an open decision (see Open Questions), but the data model and behavior are defined here.

**Data model per case:**

| Field | Value |
|---|---|
| `case_id` | UUID assigned at intake |
| `source` | `gmail \| chat \| slack \| portal` |
| `created_at` | Timestamp (intake moment) |
| `sla_due_at` | `created_at` + 24 business hours |
| `route` | One of the 6 routes above |
| `tier` | `1` or `2` |
| `status` | `open → in-progress → escalated → resolved` |
| `owner` | Functional role (not a named person) |
| `ai_answer` | Gemini draft, if generated |
| `confidence` | Gemini confidence score |
| `resolution_source` | `kb-auto \| staff-reply \| escalated` |

**Cross-channel dedup:** when the same email address opens cases via two different channels within 48 hours on a similar topic, the queue platform merges them. The member sees one reply thread; the capture queue gets one row; the SLA clock does not reset on merge.

**SLA enforcement:** at 18 business hours, unresolved cases surface in `#community-team` Slack via the Slack app. At 24 hours, the case status flips to `escalated` and the route escalation owner receives a direct Slack message.

---

## The feedback loop — keeping `faqs.md` growing

**Capture queue** (Google Sheet in the Community Drive — single sheet across all surfaces):

| ts | source | route | case_id | question | ai_answer | confidence | staff_answer | status |
|---|---|---|---|---|---|---|---|---|

How each surface writes to it:
- **Gmail:** Apps Script appends a row on every new case; fills `staff_answer` when staff reply is detected.
- **Website chat:** Cloud Function appends on every exchange; thumbs-down + staff ticket resolution fills `staff_answer`.
- **Slack:** `👎` or `/approve <edit>` fills `staff_answer` directly — fastest path.
- **Portal (future):** same Cloud Function, new `source=portal` rows.

**Nightly harvester** (GitHub Action in this repo, runs 06:00 UTC):
- Reads the Sheet (service-account credentials stored as a GitHub secret — never in the repo)
- For each row with `status=harvested` not yet promoted:
  - Appends the Q&A pair under the correct `<!-- route: X -->` block in `faqs.md`
  - Tags with `<!-- source: gmail|chat|slack, captured: YYYY-MM-DD -->` for provenance
  - Opens a PR titled `kb: harvest N new Q&As from <sources>`, labeled `kb-harvest`, assigned to Amy (backup: Kierra)
- Staff reviews the PR diff. Merging = canonical. The publish workflow fires on merge, rebuilding `faqs.json` and propagating to all surfaces within 5 minutes.

**Unanswered questions** — cases where no staff reply ever arrives — are appended weekly to `scla/member-support/pending-answers.md` so they surface as explicit knowledge gaps, not silent failures.

This honors the **"Never fabricate SCLA facts"** rule in `CLAUDE.md`: nothing reaches `faqs.md` without a human merge decision.

---

## Files this plan will create / modify

**New, in this repo:**

| Path | Purpose |
|---|---|
| `integrations/README.md` | Overview of all surfaces, dependencies, credential locations |
| `integrations/gmail-apps-script/Code.gs` | Gmail triage handler |
| `integrations/gmail-apps-script/prompts/system.md` | Grounded prompt for email |
| `integrations/gmail-apps-script/README.md` | Deploy + credential notes |
| `integrations/chat-backend/index.js` | Cloud Function (serves website chat and portal) |
| `integrations/chat-backend/README.md` | Deploy notes, env var names |
| `integrations/slack-app/manifest.json` | Slack app definition |
| `integrations/slack-app/handler.js` | Slash command + passive listener |
| `integrations/slack-app/README.md` | Install + credential notes |
| `scripts/build-faqs-json.js` | Converts `faqs.md` → `faqs.json` artifact |
| `scripts/harvest-from-sheet.js` | Reads capture queue, opens KB PRs |
| `.github/workflows/publish-faqs.yml` | Runs build + Drive upload on push to `main` |
| `.github/workflows/harvest-faqs.yml` | Nightly harvester (06:00 UTC) |
| `scla/member-support/pending-answers.md` | Unanswered-question overflow file |

**Modified:**

| Path | Change |
|---|---|
| `endpoints.md` | Fill: Gmail label IDs, Slack channel/app IDs, Drive folder ID, Cloud Function URL, Sheet ID, Gemini project ID |
| `connections.md` | Flip Gmail/Slack/Drive from "MCP only" to "MCP + Apps Script"; add Gemini row; add Cloud Function row |
| `scla/operations/automation-opportunities.md` | Mark items #3 (email triage) and #4 (Slack agent) in-progress with links to new dirs |

**Outside this repo (referenced, not built here):**

| Path | Repo |
|---|---|
| `components/SclaSupportChat.tsx` | Dashboard repo — follow-up PR after Phase D |

---

## Reuse already in place — don't rebuild

| Asset | How it's reused |
|---|---|
| `faqs.md` frontmatter `route_map` | Fed directly to Gemini as routing rules; no hand-coded routing logic needed |
| `_archive/source-of-truth/voice-decisions.md` | Dropped into the system prompt so all surfaces sound like SCLA |
| `scla/member-support/glossary.md` | Included as Gemini context so the AI knows internal acronyms |
| Existing MCP connections (Gmail, Slack, Drive) | Used for local dev and manual ops; production traffic goes through Apps Script + Cloud Function with service-account auth |
| `sync.sh` pattern | The publish workflow follows the same "main branch only, push, update workspace submodule" convention |

---

## Rollout phases

Each phase ships independently and can be paused without breaking prior phases.

**Phase A — Publish + capture infrastructure (Week 1)**
- `build-faqs-json.js` + GitHub Action → `faqs.json` in Drive
- Capture-queue Sheet created, schema locked
- No member-facing surface yet — pure plumbing. Goal: confirm the build pipeline works end-to-end before any surface goes live.

**Phase B — Slack `/askscla` (Week 2)**
- Internal-only blast radius; staff test answer quality before any member sees AI replies
- Two weeks of `/askscla` usage validates Gemini answer accuracy route by route
- `👎` feedback from staff starts populating the capture queue and seeding the KB immediately

**Phase C — Gmail draft-only mode (Weeks 3–4)**
- Apps Script generates drafts; staff review and send each one manually
- Zero risk of a bad auto-reply reaching a member
- After 2 weeks: if staff approve > 90% of drafts unchanged per route, flip `AUTO_SEND_ENABLED` for that route
- Full harvest loop live: staff replies populate the capture queue, nightly harvester opens KB PRs

**Phase D — Website chat widget (Weeks 5–6)**
- Launch as opt-in beta on the AMA channel page only
- Expand to the full member dashboard after one week of clean operation
- Backed by the same Cloud Function already validated in Phase B

**Phase E — Nightly harvester PRs (continuous from Week 2)**
- Runs from the moment the capture queue has data
- Proposed: one weekly staff slot (Monday morning) to review `kb-harvest` PRs
- Merging a PR closes the loop: new answers are live on all surfaces within 5 minutes

---

## Verification

**Phase A:** push a trivial edit to `faqs.md`. Confirm `faqs.json` appears in Drive within 2 minutes. Validate JSON schema matches the expected shape.

**Phase B:** in `#community-team`, run `/askscla what's the cost of membership?`. Confirm the answer comes from the Membership route. Hit 👎 → confirm a new row appears in the capture Sheet within 1 minute.

**Phase C:** send a test email to `community@thescla.org`. Confirm a draft reply appears with the correct route label within 3 minutes. Staff reply → 24 hours later, confirm the Sheet row has `staff_answer` filled and `status: harvested`.

**Phase D:** open the dashboard chat widget. Ask 3 known questions + 1 unknown. Confirm correct answers for the known ones; confirm the unknown creates a case and returns the right holding message. Check DevTools: POST to the Cloud Function logs the exchange, capture queue gets a new row.

**Phase E:** after one week of capture queue activity, confirm a `kb: harvest N new Q&As` PR exists. Review the diff — Q&A pairs should land under the correct route blocks with provenance tags. Merge → confirm `faqs.json` in Drive updates within 5 minutes.

**End-to-end smoke test:** send a brand-new question to `community@thescla.org`. Staff answers it. 24 hours later, ask the same question via `/askscla` and the website chat — both should answer correctly from the KB without anyone having manually edited `faqs.md`.

---

## Open questions to resolve before implementation

| # | Question | Proposed default |
|---|---|---|
| 1 | **Queue platform** — which tool hosts the unified case queue (Help Scout, Front, Zendesk, or a custom Sheet-based tracker)? | Decide before Phase A |
| 2 | **Drive folder for `faqs.json`** — new `SCLA/member-support/published/` folder, or drop into an existing one? | Create new folder |
| 3 | **Capture queue Sheet** — new Sheet titled `KB Capture Queue` in Community Drive, or extend an existing tracker? | Create new Sheet |
| 4 | **Gemini project** — does the team have an existing Google AI Studio / Vertex project, or does one need to be created? | Confirm before Phase A |
| 5 | **`kb-harvest` PR reviewer** — Amy as default, Kierra as backup | Confirm with team |
| 6 | **Gmail confidence threshold** — proposed 0.8 for auto-send; tune after first 50 drafts in Phase C | Start at 0.8 |
| 7 | **Portal auth token format** — needed before Surface 4 can be wired up | Defer until portal timeline is known |
