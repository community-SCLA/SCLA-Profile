---
source: client/_raw/INGEST_ERRORS.md
generated_by: knowledge-architect
last_updated: 2026-04-23
confidence: high
---

# Knowledge Base TODOs

> This file lists every gap in the SCLA knowledge base and the exact source material needed to close each gap. Resolve these in priority order.

The root cause of all gaps: the ingest stage was blocked by a sandbox egress proxy. No pages from thescla.org were directly scraped. All KB content is derived from Google search-index snippets only. See [`client/_raw/INGEST_ERRORS.md`](../_raw/INGEST_ERRORS.md) for the full error log.

---

## How to fix this

**Option A (recommended):** On a machine outside this sandbox, use a browser to export each priority page below as a PDF or "Save as..." HTML file. Drop the files into `client/_raw/docs/inbox/` and re-run `/ingest` then `/kb`.

**Option B:** Run the ingestor from an environment with open egress (developer laptop, CI runner) and commit the resulting files under `client/_raw/web/` and `client/_raw/assets/`.

---

## Priority pages to export (in order)

These are the pages that will close the most gaps in the fewest exports.

| Priority | URL | What it unlocks |
|---|---|---|
| 1 | https://www.thescla.org/ | Full home page content, headline messaging, current member/campus stats |
| 2 | https://www.thescla.org/benefits | Complete benefits list; needed to verify and expand [products-services.md](./products-services.md) |
| 3 | https://www.thescla.org/mission-history | The 4 Pillars by name; full founding story; timeline beyond what snippets provide |
| 4 | https://www.thescla.org/leadership-team | Names, titles, and bios for all current leaders; needed to populate [people.md](./people.md) |
| 5 | https://www.thescla.org/faq | Verbatim member FAQ; needed to replace stub entries in [faqs.md](./faqs.md) |
| 6 | https://www.thescla.org/administrator-faq | Institution-facing FAQ; hosting cost, reporting, invitation workflow |
| 7 | https://www.thescla.org/program | Full Career Readiness Certification curriculum; ISPI full name and description |
| 8 | https://www.thescla.org/the-scla-difference | SCLA's stated competitive differentiators |
| 9 | https://www.thescla.org/membership-eligibility | Exact eligibility criteria beyond GPA minimum |
| 10 | https://www.thescla.org/start-a-chapter | Chapter start process; cost to institution; chapter officer roles |
| 11 | https://www.thescla.org/nab-apply | NAB full name confirmation; member list; application criteria |
| 12 | https://www.thescla.org/online-membership | Online membership pricing and any feature differences from on-campus |
| 13 | https://shop.thescla.org/ | Product catalog; merchandise and additional revenue lines |
| 14 | https://www.thescla.org/blog (index + posts) | Blog authorship, publishing cadence, content themes |
| 15 | https://www.thescla.org/contact-us | Official contact details; support channels; team contacts |

---

## Additional source material to request from client

Beyond the public website, the following internal materials would significantly raise KB confidence:

| Item | Why it matters |
|---|---|
| Org chart or team list | Needed to populate [people.md](./people.md) functional teams section |
| Membership onboarding flow / process doc | Would let the workflow-mapper agent (Stage 4) document the invitation-to-activation flow |
| Partnership agreement template | Would define the institution relationship and administrator role precisely |
| Pricing sheet or rate card | Would confirm $95 fee, renewal model, institutional costs |
| ISPI assessment documentation | Would let us define the ISPI acronym and describe the tool accurately |
| Career Readiness Certification accrediting body | Would identify who grants accreditation; critical for FAQ accuracy |
| AI Career Hub vendor or architecture info | Would clarify whether the tool is proprietary or third-party |

---

## Specific open questions per KB file

### glossary.md
- What does ISPI stand for?
- What are the 4 Pillars by name?
- What does the NAB (National Advisory Board) do?
- What accrediting body issued the Career Readiness Certification accreditation?
- Is "The SCLA Difference" an official internal term or just a page name?

### people.md
- Is Pat Sidhu still in an active executive role?
- Who are the co-founders (snippet implies multiple)?
- Who are all current leadership team members (names, titles, responsibilities)?
- Who chairs or staffs the NAB?
- Who is the primary contact for new institutional partnerships?

### products-services.md
- Does the $95 fee recur or is it a one-time lifetime fee?
- Who pays the $95 — the student or the institution?
- Are there membership tiers with different benefit levels?
- Does online membership cost the same as on-campus membership?
- What is the formal process for an institution to become a partner campus?
- What does the shop at shop.thescla.org sell?

### faqs.md
- All verbatim member FAQ content from https://www.thescla.org/faq
- All verbatim administrator FAQ content from https://www.thescla.org/administrator-faq

---

## Files that will be created or expanded once source material arrives

When the priority pages above are exported and re-ingested, the following additional KB pages should be created:

| File | Trigger |
|---|---|
| `customers.md` | Export of partner campus list or institutional contacts |
| `systems-and-tools.md` | Export of app.thescla.org, members.thescla.org, and any admin portals |
| `compliance.md` | Any accreditation body documentation or institutional data-sharing agreements |
