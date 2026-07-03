# Plan: Wire the FAQ knowledge base into the SCLA workflow

Plug `member-support/faqs.md` (the curated source of truth, organized into 6 routes — GENERAL, MEMBERSHIP, PAYMENTS, PROGRAMS, ACCOUNT, ADMINISTRATOR — with `<!-- route: -->` tags) into four surfaces — Gmail, the website (member dashboard), Slack, and the member portal/dashboard messaging system — and feed every real exchange back into the repo so the KB grows on its own. Stack: **Google Workspace + Gemini** for the AI layer, **Apps Script** as the glue, **GitHub** as the system of record.

> **Cross-channel dedup/merge** is owned by the **case/queue layer**, not this KB plan. See `member-support/member-support-integration.md` for the unified operating model.

Decisions locked in:
- Dashboard stack: custom React/Next → embed a native widget
- AI engine: Gemini (Google Workspace native)
- Feedback loop: auto-append *both* unanswered questions *and* the staff-written answers harvested from replies

---

## Architecture at a glance

```
                ┌──────────────────────────────────────────┐
                │   SCLA-Profile repo (this repo, GitHub)  │
                │   member-support/faqs.md  (truth)   │
                └───────────────┬──────────────────────────┘
                                │ (1) publish on push
                ▼                                            ▲
        ┌───────────────┐                          ┌─────────────────┐
        │  faqs.json    │  ← built artifact         │  PR bot writes  │
        │  (Drive)      │   served to all surfaces  │  new Q&A pairs  │
        └──────┬────────┘                          └────────▲────────┘
               │                                            │ (4) harvested
   ┌───────────┼──────────────┐                             │     answers
   ▼           ▼              ▼                             │
┌──────┐   ┌────────┐   ┌──────────┐                  ┌─────┴──────┐
│Gmail │   │Website │   │  Slack   │ ─── unanswered ──▶│  capture   │
│Apps  │   │widget  │   │ /askscla │     questions     │   queue    │
│Script│   │(Gemini)│   │  (Apps   │                  │ (Sheet +   │
│      │   │        │   │  Script) │                  │  Slack)    │
└──────┘   └────────┘   └──────────┘                  └────────────┘
   │           │             │                              ▲
   └───────────┴─────────────┴── (2) answer from faqs.json  │
                                 (3) staff reply observed ──┘
```

Numbered flows:
1. On every push to `main`, GitHub Actions converts `faqs.md` → `faqs.json` and uploads to a Drive folder all three surfaces read from.
2. Each surface queries Gemini with `faqs.json` as grounded context; if Gemini's confidence is high, it auto-replies; if not, it routes to the right human (per `route_map`).
3. When a staff member replies to a routed thread, the harvester reads the staff reply and pairs it with the original question.
4. A nightly job opens a PR against `faqs.md` adding the new Q&A under the correct route, tagged with provenance. Staff review → merge → loop closes.

---

## Surface 1 — Gmail auto-reply + smart routing (Apps Script)

**What to build**
- Apps Script project bound to the shared `community@thescla.org` inbox.
- Time-driven trigger every 2 min: scans `label:unprocessed` threads.
- For each new thread: call Gemini with the message body + `faqs.json` as system context, ask for either `(answer, confidence, route)` or `(needs_human, route)`.
- If `confidence ≥ 0.8`: send draft reply (start in draft-only mode for 2 weeks, flip to auto-send once accuracy is validated), label `auto-answered`.
- Else: forward / re-label thread to the correct route owner (Yesse for membership, Kierra for tech, Amy for community) using the existing `route_map` in `faqs.md` frontmatter, label `needs-human`.

**Key files / endpoints to create**
- `integrations/gmail-apps-script/Code.gs` — main handler
- `integrations/gmail-apps-script/prompts/system.md` — grounded prompt (uses faqs.json + voice from `brand/voice-and-tone.md`)
- Populate `endpoints.md`: Gmail label IDs, Apps Script project ID, Gemini API key in Script Properties (NOT in repo, per CLAUDE.md credential rule)

---

## Surface 2 — Website support chat (custom-built dashboard)

**What to build**
- A small React component `<SclaSupportChat />` mounted on the member dashboard and the AMA channel page.
- Backend: a single serverless endpoint (Cloud Function on the existing Google project) that:
  - Loads `faqs.json` from Drive (cached 5 min)
  - Calls Gemini with the user message + faqs.json + the member's identity from the dashboard's auth context
  - Streams the reply back
  - If `needs_human` → opens a ticket in the capture queue and tells the member "I've sent this to a staff member, expect a reply by EOD."
- Logs every exchange (question, AI answer, member feedback thumbs up/down) to the capture queue.

**Key files to create**
- `dashboard/components/SclaSupportChat.tsx` (in the dashboard repo — referenced here for completeness)
- `integrations/chat-backend/index.js` (Cloud Function) lives in *this* repo so it ships with the KB

---

## Surface 3 — Slack `/askscla` slash command (internal)

**What to build**
- Slack app with one slash command `/askscla <question>` available in every channel including `#community-team`.
- Backed by the same Cloud Function from Surface 2 (one backend, three surfaces).
- Returns answer in-thread with a "Was this right? 👍 / 👎 / 📝 add note" message-action.
- 👎 / 📝 routes the exchange straight into the capture queue with the staff member's correction attached.

**Bonus: passive Slack listening (optional, gate behind a flag)**
- Monitor a designated `#member-questions-inbox` channel (where the team forwards member emails).
- For each message: post a thread reply with a Gemini-drafted answer + "Reply '/approve' to send to member, or edit and reply '/approve' to send your version."
- The captured staff edit is the gold-standard answer that feeds back to the KB.

---

## The feedback loop — keeping `faqs.md` growing

**Capture queue** (Google Sheet, lives in the Community Drive — single sheet across all three surfaces):

| ts | source | route | question | ai_answer | confidence | staff_answer | status |

- Gmail Apps Script appends a row whenever a thread is routed to a human; once the human replies, a second trigger reads `getLatestReplyFromStaff()` and fills `staff_answer` + sets status to `harvested`.
- Website chat backend appends rows for every exchange; thumbs-down + staff ticket resolution fills `staff_answer`.
- Slack `/askscla` 👎 or `/approve <edit>` fills `staff_answer` directly.

**Nightly harvester** (GitHub Action in this repo, runs at 06:00 UTC):
- Reads the Sheet (service-account creds stored as GitHub secret, never in repo)
- For each row with `status=harvested` and not yet promoted:
  - Appends the Q&A under the right `<!-- route: X -->` block in `faqs.md`
  - Tags with `<!-- source: gmail|chat|slack, captured: YYYY-MM-DD -->` for provenance
  - Opens a PR titled `kb: harvest N new Q&As from <surfaces>`, labeled `kb-harvest`, assigned to Amy/Kierra
- Staff reviews the PR. Merging it = the new Q&A is canonical and immediately republished to all three surfaces (closes the loop).

This honors the **"Never fabricate SCLA facts"** rule from `CLAUDE.md`: nothing reaches `faqs.md` without a human merge.

**Unanswered questions** (when no staff reply ever comes) get appended to `member-support/pending-answers.md` weekly.

---

## Files this plan will create/modify

**New, in this repo:**
- `integrations/README.md` — overview of the three surfaces
- `integrations/gmail-apps-script/` — Apps Script source, README, deploy notes
- `integrations/chat-backend/` — Cloud Function source (Node.js), README
- `integrations/slack-app/` — Slack app manifest + handler glue
- `scripts/build-faqs-json.js` — converts `faqs.md` → `faqs.json` artifact
- `scripts/harvest-from-sheet.js` — nightly harvester that opens KB PRs
- `.github/workflows/publish-faqs.yml` — runs build + Drive upload on push to main
- `.github/workflows/harvest-faqs.yml` — nightly harvester
- `member-support/pending-answers.md` — overflow file for unanswered questions

**Modified:**
- `endpoints.md` — fill in Gmail label IDs, Slack channel/app IDs, Drive folder ID, Cloud Function URL, Sheet ID (all TODO today)
- `connections.md` — flip Gmail/Slack/Drive entries from "MCP only" to "MCP + Apps Script", add Gemini row
- `operations/automation-opportunities.md` — mark items #3 (email triage) and #4 (Slack agent) as in-progress with links to the new dirs

**Outside this repo (referenced, not built here):**
- `<dashboard repo>/components/SclaSupportChat.tsx` — a follow-up PR there

---

## Reuse already in place — don't rebuild

- `faqs.md` frontmatter `route_map` — feed it straight to Gemini as routing rules; no hand-coded routing logic needed
- `brand/voice-and-tone.md` — drop into the system prompt so all three surfaces sound like SCLA
- `member-support/glossary.md` — include as context so the AI knows internal acronyms
- `sync.sh` — the publish workflow follows the same "main branch only, push, update workspace" pattern
- Existing MCP connections (Gmail, Slack, Drive) — used for local dev & manual ops; production traffic goes through Apps Script + Cloud Function with service-account auth

---

## Rollout phases (each ships independently)

**Phase A — Publish + capture (week 1)**
- `build-faqs-json.js` + GitHub Action → `faqs.json` in Drive
- Capture-queue Sheet created, schema defined
- No user-facing surface yet; pure plumbing

**Phase B — Slack `/askscla` (week 2)**
- Lowest blast radius (internal only), fastest harvesting velocity
- Two weeks of internal use validates Gemini answers before any member sees them

**Phase C — Gmail draft-only mode (weeks 3–4)**
- Apps Script generates *drafts* for staff to review and send. Zero risk of bad auto-reply.
- After 2 weeks of high accuracy → flip the "auto-send if confidence ≥ 0.8" switch

**Phase D — Website chat widget (weeks 5–6)**
- Ship to dashboard once B and C have validated answer quality
- Start as opt-in beta on the AMA channel page only, expand after a week

**Phase E — Nightly harvester PRs (continuous, starts week 2)**
- Runs from the moment capture queue has data; staff merges weekly

---

## Verification (per phase)

- **Phase A:** push a trivial edit to `faqs.md`, confirm `faqs.json` appears in Drive within 2 min, schema validates.
- **Phase B:** in `#community-team`, run `/askscla what's the cost of membership?` — confirm answer is from the Membership route. Thumbs-down → row appears in Sheet within 1 min.
- **Phase C:** send test email to `community@thescla.org`, confirm draft appears with correct routing label within 3 min. Staff reply → 24h later, row in Sheet has `staff_answer` filled.
- **Phase D:** open dashboard, ask 3 known questions + 1 unknown — answers correct, unknown opens a ticket. DevTools confirm POST to Cloud Function logs the exchange.
- **Phase E:** after 1 week, confirm a `kb: harvest N new Q&As` PR exists; diff is sensible; merging republishes to Drive within 5 min.

**End-to-end smoke:** a brand-new question asked in Gmail → routed to staff → answered → 24h later it answers correctly via `/askscla` and the website chat without anyone touching `faqs.md`.

---

## Open questions to resolve before implementation

1. **Drive folder for `faqs.json`** — create a new `SCLA/member-support/published/` folder, or drop into an existing one?
2. **Capture queue Sheet** — new Sheet titled `KB Capture Queue` in Community Drive, or extend an existing tracker?
3. **Gemini project** — does the team have an existing Google AI Studio / Vertex project, or does one need to be created?
4. **Who owns `kb-harvest` PR review?** — proposed: Amy default, Kierra backup.
5. **Confidence threshold for Gmail auto-send** — proposed 0.8; tune after first 50 drafts in Phase C.
6. **AMA channel as a fourth surface** — lean: just the chat widget on that page for now; revisit after launch.
