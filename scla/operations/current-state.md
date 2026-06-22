---
source: Community Team Mondays notes Apr 2026 (archived externally); stakeholder notes (archived externally)
generated_by: workflow-mapper
last_updated: 2026-04-24
---

# SCLA — Current-State Workflows

Ten workflows observed across three consecutive Community Team Monday
meetings (Apr 6, 13, 20). Claims are cited to meeting notes; thin
evidence is marked `TODO: needs input`.

**Scope note — stakeholder-inventory correction:** the stakeholder
inventory captured the client's self-description as "no project/task
tracking." The meeting notes show a different picture. The team uses a
**Team Projects tracker** (a Canva canvas, built by Kierra Woekel),
plus a **Community weekly sync canvas** and two Google Sheets ("OG
tracker" + a simpler Chuck tracker). As of Apr 13, the team
**decided** the Canva Team Projects tracker is the single source of
truth for action items. This is recorded here because the workflow
exists even though the client didn't name it as a tool.

---

## 1. Community Team Mondays (weekly sync) {#weekly-sync}

**Trigger:** Standing Monday 4pm CDT meeting.
**Owner:** Amy Westby (agenda), Gemini (notes).
**Occurs:** Weekly, 60 min.
**Avg cycle time:** Same-day notes via Gemini; action items extracted automatically.

### Steps

1. Attendees join Zoom — tool: `Zoom` — actor: `Community team (10)`
2. Gemini auto-takes notes — tool: `Gemini / Google Meet notes`
3. Notes auto-posted, action items captured in "Suggested next steps" section — tool: `Gemini`
4. Manual upload of notes to repo `(removed — ingest scratch)` — tool: `git`, `GitHub` — actor: `Kierra Woekel`
5. Action items to be propagated to Team Projects tracker — currently manual — tool: `Canva canvas` — actor: `individual owners`

### Pain points

> "Amy Westby stated that the primary goal of the meeting was to discuss projects and bring order to the current workflow, which has been chaotic but productive."
> *source: Apr 13 notes (archived externally — not in repo)*

### Related automation opportunities

- [Meeting notes → Team Projects tracker auto-sync](./automation-opportunities.md)

---

## 2. Weekly leadership update (Amy → Chuck / Shawn / leadership) {#leadership-update}

**Trigger:** Monday meeting wraps; Amy compiles a rollup.
**Owner:** Amy Westby.
**Occurs:** Weekly.
**Avg cycle time:** Same week; manual compile.

### Steps

1. Team drops quick wrap-ups + blockers into community weekly sync canvas — tool: `Canva canvas`
2. Amy reviews and summarizes — tool: manual
3. Amy sends written update to Chuck, Shawn (Sean), leadership — tool: `Gmail` / `Slack` (`TODO: needs input — which channel`)

### Pain points

> "These notes would then be used by Amy Westby to update Chuck, Shawn, and the leadership team weekly on project progress, allowing for better coordination with other integrated teams."
> *source: Apr 13 notes (archived externally — not in repo)*

Amy wants this more visual — screenshot-driven.

### Related automation opportunities

- [Slack AI agent / weekly digest](./automation-opportunities.md)

---

## 3. Weekly News email production {#weekly-news-email-production}

**Trigger:** Weekly publishing cadence (currently stalled).
**Owner:** Zeketra Grandy (content), Kierra Woekel (technical), Sean/Shawn (MJML + send).
**Occurs:** Weekly (intended); actual cadence interrupted.
**Avg cycle time:** Stalled — days to weeks due to MJML bottleneck.

### Steps

1. Team submits content for announcements — actor: `the group` → `Zeketra`
2. Zeketra builds layout in Canva — tool: `Canva` — actor: `Zeketra Grandy`
3. Previously: handoff to Sean/Shawn for MJML conversion → stall
4. Apr 6 workaround: Kierra scraped the Canva design with Manis to generate HTML — tool: `Manis`, `Perplexity`
5. Apr 20 forward-path: Amy sends 3 MJML samples → Kierra feeds Claude → Claude drafts template → tech team implements — tool: `Claude Pro`

### Handoffs

- Zeketra → Sean/Shawn: Canva design for MJML conversion (current blocker)
- Kierra → Amy: scraped HTML versions for review
- Amy → Kierra: MJML sample files (committed Apr 20)

### Pain points

> "Kierra Woekel's provided HTML code for the news required additional revision in Perplexity because it did not work immediately due to CSS code issues that can arise depending on the rendering location."
> *source: Apr 13 notes (archived externally — not in repo)*

> "configuration barriers, particularly with email communications, due to Shawn's specific requirements for the MJML code used for email templates."
> *source: Apr 20 notes (archived externally — not in repo)*

### Related automation opportunities

- [Claude-generated MJML templates from Canva designs](./automation-opportunities.md)

---

## 4. Member Journey funnel (Pledge → Info session → Orientation → Onboarding → Support) {#member-journey-funnel}

**Trigger:** Prospective member engages (pledge project / info session).
**Owner:** Distributed. Amy coordinates. Jenna Heath + Iman Lomax + Aman own info session; Zeketra Grandy + Alyssa Phillips own onboarding; Yesse Ordonez catches member support edge cases.
**Occurs:** Ongoing per member.
**Scale:** "onboarded nearly 15,000 students since December 1st"; 30,000 members since July 1; 317 refunds (~1%).

### Steps

1. Pledge / outreach emails — actor: `Iman`, `Jenna`, `Aman`
2. Big info session — tool: `Zoom` — actor: `Jenna Heath`, `Iman Lomax`, `Aman`
3. Orientation — `TODO: needs input — process details`
4. Onboarding experience (30-day process, 60-day playbook) — actor: `Zeketra Grandy`, `Alyssa Phillips`
5. Member Support catchall — actor: `Yesse Ordonez`

### Handoffs

- Jenna/Iman/Aman → Zeketra/Alyssa: pledged members post-info-session
- Zeketra/Alyssa → Yesse: members needing extra support
- Zeketra/Alyssa → Kierra: onboarding docs for SOP consolidation

### Pain points

> "Zeketra Grandy explained that they are holding off on publishing the documents until they merge their work with Alyssa's to avoid conflicting documents, and they plan to seek Kierra Woekel's guidance on where the completed version should reside."
> *source: Apr 20 notes (archived externally — not in repo)*

> "Jenna Heath mentioned they did not have access to the community Google Drive and requested access. Kierra Woekel provided a troubleshooting tip, noting that if the browser is signed into a non-SCA Google account, access will be blocked, and suggested creating separate Chrome profiles as a hack."
> *source: Apr 20 notes (archived externally — not in repo)*

### Related automation opportunities

- [Google Drive → Claude knowledge base → dashboard](./automation-opportunities.md)

---

## 5. Inbound email triage {#inbound-email-triage}

**Trigger:** Incoming email to shared / group addresses.
**Owner:** Kierra Woekel, Amy Westby, Yesse Ordonez (offline working group).
**Occurs:** Continuous.
**Avg cycle time:** Currently manual per-message.

### Steps

1. Email arrives to shared address — tool: `Gmail`
2. Currently: manual access grant (workaround for broken Google Groups) — actor: team
3. Planned: Google Apps Script classifies by keyword / partner — tool: `Google Apps Script`
4. Route to appropriate inbox — tool: `Gmail`

### Pain points

> "the Google group issue with Sean is ongoing due to a known Google error message."
> *source: Apr 6 notes (archived externally — not in repo)*

### Related automation opportunities

- [Google Apps Script email triage](./automation-opportunities.md)

---

## 6. Course content production {#course-production}

**Trigger:** Platform gap — 61–62 courses planned, ~2 complete (Google, Microsoft).
**Owner:** Amy Westby (strategy), Mayeth Gueta (catalog), Nollie (design finalization), Annie (videography).
**Occurs:** Per-course; backlog heavy.
**Avg cycle time:** `TODO: needs input`

### Steps

1. Topic selection — `TODO: needs input`
2. Syllabus + coding — actor: `Mayeth Gueta`
3. Design finalization — actor: `Nollie`
4. Video production — tool: `Heygen`, `Synthesia` — actor: `Annie`
5. Platform coding / database entry — actor: `TODO: needs input`

### Pain points

> "the organization has 61 or 62 courses, all of which require syllabi and coding, and stressed the need for further work on the database to manage the content."
> *source: Apr 6 notes (archived externally — not in repo)*

> "they may need to hire an additional person to focus on building the courses due to the amount of work involved"
> *source: Apr 13 notes (archived externally — not in repo)*

### Related automation opportunities

- [Course production pipeline — Claude script drafting](./automation-opportunities.md)

---

## 7. Project tracking / status {#project-tracking}

**Trigger:** Work in flight.
**Owner:** Kierra Woekel + Alyssa Phillips (tracker maintenance), Amy Westby (reporting).
**Occurs:** Continuous; rolled up weekly.

### Steps (post Apr 13 decision)

1. Individuals populate Team Projects tracker — tool: `Canva canvas`
2. Weekly updates dropped into community weekly sync canvas — tool: `Canva canvas`
3. Amy screenshots tracker for leadership updates — tool: manual
4. Kierra investigating Excel sync — tool: `Canva` ↔ `Google Sheets` (exploratory)

### Pain points

> "Kierra Woekel raised the issue of having multiple locations for tracking tasks and advocated for a single, centralized workflow to avoid spreading effort across different canvases and documents."
> *source: Apr 13 notes (archived externally — not in repo)*

> "Amy Westby confirmed they use two main Google Sheets, their personal 'OG' tracker and a simpler one for Chuck, in addition to the project tracker canvas."

---

## 8. Ad-hoc tech support & backlog management {#tech-support}

**Trigger:** Bug report or feature request from the field.
**Owner:** Tech team (3 people, including Sean/Shawn) — Yesse Ordonez catches from the community team side.
**Occurs:** Continuous.

### Steps

1. Bug surfaces (e.g., "500 error when students publish credentials to LinkedIn") — reporter: team / members
2. Documented (or not) — team documents extensively; Sean/Shawn "zero documentation"
3. Passed to tech team — `TODO: needs input — via what channel?`
4. Prioritization — informal; Amy flagged need for change-log tool

### Pain points

> "the tech team is a small startup crew of three people focused on building sustainable long-term solutions, not just one-off fixes."
> *source: Apr 20 notes (archived externally — not in repo)*

> "Amy Westby emphasized the need for a better process or tool for managing the change log, future requests, and backlog"
> *source: Apr 20 notes (archived externally — not in repo)*

### Related automation opportunities

- [Change log / feature request backlog tool](./automation-opportunities.md)

---

## 9. Event planning (partner-scale) {#events}

**Trigger:** Partner event scheduled (e.g., University of Phoenix May 26/27, ~500 attendees).
**Owner:** Jenna Heath + Aman.
**Occurs:** Periodic.

### Steps

1. Event scheduled with partner
2. Capacity/licensing check — tool: `Zoom` (license capacity for 500+)
3. Promotion — `TODO: needs input — channel, copy, audience`
4. Hosting — tool: `Zoom`

### Pain points

> "a potentially larger event on May 26th/27th with the University of Phoenix could draw over 500 attendees, necessitating a discussion about acquiring a larger Zoom license."
> *source: Apr 13 notes (archived externally — not in repo)*

`TODO: needs input — confirm Zoom license upgrade status before May 26.`

---

## 10. Micro-internship partnership sourcing {#micro-internships}

**Trigger:** New partner company interest OR revenue need ($39/each after first free).
**Owner:** Cindy Rariza (current focus).
**Occurs:** Ongoing.

### Steps

1. Partner outreach — `TODO: needs input — channel`
2. Contract + sample handoff — artifact: contract templates, samples
3. Project assignment to members — async relationship
4. Mediation + grading — actor: organization

### Pain points

> "they currently have many asynchronous relationships where the company provides a project and the organization handles all mediation and grading. The goal is to establish deeper, more formal partnerships where companies might run channels, be guest speakers, or collaborate on 'behind-the-scenes' tours."
> *source: Apr 6 notes (archived externally — not in repo)*

---

## What's missing from this map

- **Chapter operations** — nothing in the meeting notes about NAB reviews,
  chapter approvals, or campus administrator onboarding. KB references
  these but `(removed — ingest scratch)` has no evidence. Targeted Drive search required.
- **Shop / fulfillment** (`shop.thescla.org`) — not mentioned in any meeting.
- **CEO Speaker Series** — not mentioned.
- **Member renewals** — contracts expire June; Zeketra surfaced maintenance
  concerns but no renewal workflow documented.
- **CRM / advisor tools** — mentioned as "in the tech team's build" (Apr 20)
  but no current-state workflow.

These gaps are the core reason for the [Drive search queries](../../_archive/drive-search-queries-pre-2026-06-11.md).
