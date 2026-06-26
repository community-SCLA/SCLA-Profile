---
source: Community Team Mondays notes Apr 2026 (archived externally)
---

# SCLA — Pain Points

Prioritized by frequency across the three Apr 2026 meetings, whether a fix is within the community team's control, and rough hours-saved/risk-avoided.

---

## P0 — Appeared in all three meetings

### 1. Sean/Shawn is a single point of failure for email templates

Three weeks, three mentions. The only path for weekly announcements to
actually ship requires Sean/Shawn's MJML conversion.

> "the team is waiting for Sean to convert them into MJML email templates for use in campaigns, preventing a consistent rhythm from starting."
> *— Apr 6, source (archived externally — not in repo)*

> "Kierra Woekel's provided HTML code for the news required additional revision in Perplexity because it did not work immediately due to CSS code issues"
> *— Apr 13, source (archived externally — not in repo)*

> "configuration barriers, particularly with email communications, due to Shawn's specific requirements for the MJML code used for email templates."
> *— Apr 20, source (archived externally — not in repo)*

**Fixable?** Yes — the team has already committed to routing around via
Claude-generated MJML templates (automation opp #1).

**Hours saved:** unquantified, but the weekly cadence is currently
*stopped* — value is qualitative + strategic.

---

### 2. Documents scattered across multiple locations

> "Kierra Woekel raised the issue of having multiple locations for tracking tasks and advocated for a single, centralized workflow to avoid spreading effort across different canvases and documents. Amy Westby confirmed they use two main Google Sheets, their personal 'OG' tracker and a simpler one for Chuck, in addition to the project tracker canvas."
> *— Apr 13, source (archived externally — not in repo)*

> "Zeketra Grandy explained that they are holding off on publishing the documents until they merge their work with Alyssa's to avoid conflicting documents, and they plan to seek Kierra Woekel's guidance on where the completed version should reside."
> *— Apr 20, source (archived externally — not in repo)*

**Fixable?** Partially. Apr 13 decision to centralize on the Team
Projects tracker (Canva) + community Google Drive is in progress.
Execution is the remaining work.

**Risk:** Without a single source of truth, onboarding new hires (or
recovering from turnover after June contracts) becomes a re-archaeology
project. See pain point #7.

---

### 3. Tech team backlog unmanaged; no change-log tool

> "Amy Westby emphasized the need for a better process or tool for managing the change log, future requests, and backlog, which would allow the team to document input from the field."
> *— Apr 20, source (archived externally — not in repo)*

> "the tech team is a small startup crew of three people focused on building sustainable long-term solutions, not just one-off fixes."

Asymmetric documentation culture:

> "Sean's zero documentation and the team's extensive documentation"

**Fixable?** Yes — a structured change-log doc (even just a Google
Doc/Sheet) would reduce the information gap. Harder question: getting
Sean to engage with it.

---

## P1 — Appeared in two meetings

### 4. Google Drive access is flaky; Google Groups workaround is broken

> "Jenna Heath mentioned they did not have access to the community Google Drive and requested access. Kierra Woekel provided a troubleshooting tip, noting that if the browser is signed into a non-SCA Google account, access will be blocked, and suggested creating separate Chrome profiles as a hack."
> *— Apr 20, source (archived externally — not in repo)*

> "the Google group issue with Sean is ongoing due to a known Google error message."
> *— Apr 6, source (archived externally — not in repo)*

**Fixable?** Partially — the Google error is external. Workarounds
(Apps Script triage, Chrome-profile hack) are known and in progress.

---

### 5. Course production pace vs. ambition

Only 2 of 61–62 courses complete.

> "Amy Westby suggested that they may need to hire an additional person to focus on building the courses due to the amount of work involved, even with tools like Hey Gen and Synthesia for videography help from Annie."
> *— Apr 13, source (archived externally — not in repo)*

**Fixable?** Partially — AI-drafted syllabi + Claude lesson outlines
could accelerate the "first 70%", but someone still has to own finishing
and reviewing. Hiring remains on the table.

---

### 6. Configuration barriers + underused Kierra capacity

> "Zeketra Grandy voiced frustration regarding configuration barriers and the lack of movement on their team's deliverables, suggesting that Kierra Woekel's talent is underutilized to move their projects forward."
> *— Apr 20, source (archived externally — not in repo)*

Amy's response acknowledged the tension — tech team is building
sustainable infra, not one-off fixes. No resolution beyond that.

**Fixable?** Structural. The Claude-based routing (automation opps #1,
#2) is the concrete path Kierra can unblock work without waiting on the
tech team.

---

## P1 — Strategic / one-meeting but high-stakes

### 7. Team contract expiration in June → member-support continuity risk

> "Zeketra Grandy raised concerns that the current four-month contracts, two months of which have passed, could lead to a lack of maintenance and support for community members if the contracts are not renewed, resulting in no one responding to questions or handling orientation."
> *— Apr 20, source (archived externally — not in repo)*

> "Amy Westby clarified that the four-month contract period was intended as a momentary barometer or milestone and not as a set time for people to leave [...] Amy Westby reassured the team that they do not want to hire a new team and are committed to keeping the current team for the long haul"

**Fixable?** Above the community team's pay grade — Chuck/leadership
decision. But the risk is real: 15,000 students onboarded in 4 months
(Dec 1 → Apr 20) depend on a team that doesn't have contracted
continuity.

**Mitigation within team's control:** Automation opp #2 (Drive → Claude
KB) preserves institutional knowledge regardless of turnover — Kierra
explicitly flagged this.

---

### 8. AI Resume Builder: content + tech both broken

> "Amy Westby highlighted the need to define whether improvements require a technical upgrade or a content/teaching solution, which is where the two teams intersect."
> *— Apr 20, source (archived externally — not in repo)*

> "many students struggle with the content itself, specifically identifying transferable skills and knowing what words to write."

**Fixable?** Yes — needs a PRD (Amy's action item) and Claude-backed
content agent (automation opp #5).

---

## P2 — Low frequency / narrow scope

### 9. LinkedIn credential publish error (500)

> "some students were experiencing a 500 error when attempting to publish their credentials to LinkedIn. Yesse Ordonez offered to be notified if any transcripts are returned."
> *— Apr 6, source (archived externally — not in repo)*

Tech-team bug. Noted, no recurrence in later meetings — status unclear.

### 10. No SOP template exists

> "Jenna Heath asked if Kierra Woekel could provide a template so that they and Aman could simply plug in their existing information. Kierra Woekel responded that they do not have a template but explained that Amy Westby and they are planning to use a Claude Pro account to scrape all information, create a knowledge base, and then automate the creation of a suitable structure."
> *— Apr 20, source (archived externally — not in repo)*

**Fixable?** Blocked on automation opp #2 landing.

### 11. Tool utilization varies per member

Example member wanted only the async component, not the resume builder or interview tool — a signal that focus-modes gating (Aug 1 launch) is the right product direction.
