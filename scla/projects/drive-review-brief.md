---
type: program
status: draft
owner: Kierra
created: 2026-06-24
last_updated: 2026-06-26
---

# Plan: Proposed Google Drive Folder Hierarchy

## Overview

This is a **proposal only** — no files will be moved until approved. The goal is a clean, initiative-aligned Drive structure where every document has exactly one home and stale content is visibly separated from active content.

## Context

SCLA's Q2 2026 goal #3 is "Community Google Drive as single source of truth" (Drive cleanup priority owned by Kierra). The current Drive is unstructured — 173 documents spread across ad-hoc folders with no consistent logic, duplicate files, and no clear active/archive split. This proposal maps a clean folder hierarchy using Notion's 9 initiative categories as the theme clusters, flags every known duplicate or contradiction, and identifies what is stale.

**Design principles:**

- One document → one folder. No cross-posting (see *Definitions* below).
- Notion initiative = top-level folder. The team already navigates by initiative in Notion; Drive should mirror that.
- Every folder has an `_Archive/` subfolder. Active docs and historical records never mix.
- Flat within sub-folders. No folder *nesting* deeper than 3 levels (this is about folder depth, not how many file versions we keep — see *Definitions*).

---

## Definitions & Clarifications

> Added in response to review comments (2026-06-24) to clarify the design principles above.

- **Organize by Topic/Initiative, not by Type.** Documents are filed by what they're *about* (their initiative), not by their *format*. There is no standalone "Syllabus" or "Video" folder — a syllabus lives with its course topic (e.g., a Career Readiness syllabus lives under `01 Learning (CIAO)/Career Readiness Program/`). To find something, go to the topic, not the file type.
- **Cross-posting** means putting the same document — or a copy/shortcut of it — in more than one folder so it appears in multiple places. We do **not** do this: each document has exactly one home. Duplicated copies drift out of sync (someone edits one, the other goes stale), which is the exact duplicate problem this cleanup is fixing. If a doc is relevant to two initiatives, it still lives in one folder; reference it elsewhere with a link, not a second copy.
- **Folder depth vs. version retention.** "No nesting beyond 3 levels" limits how many folders deep you click — it says nothing about saving v4 or v5 of a file. Version handling is separate: keep the current canonical version active and move clearly superseded versions to `_Archive/`.
- **Trash vs. Archive** (see guideline below).

### Trash vs. Archive guideline

> Added in response to a review question about when to trash vs. archive.

- **Archive** = keep but set aside. The doc is no longer active but may have reference or historical value (past weekly updates, superseded versions). Move it to the folder's `_Archive/` subfolder.
- **Trash** = remove entirely. The doc has no future reference value (a wound-down partnership, a completed program wrap-up).
- **Rule of thumb:** when in doubt, archive. Only trash when you're sure there's no historical or cross-team value — and **never trash a document owned or shared by another team**, since trashing from a shared Drive removes it for them too.

---

## Proposed Folder Hierarchy

```
Community Team Drive/
│
├── 01 Learning (CIAO)/
│   ├── Course Catalog/
│   │   ├── AI & Technology/          (AI101–AI306, 9 files)
│   │   ├── Career & Job Search/      (CAR101–106, Hidden Job Market, Interview Video, 8 files)
│   │   ├── Networking/               (NET101, NET201–202, 3 files)
│   │   ├── Communication/            (COM101–102, 2 files)
│   │   ├── Leadership/               (LDR101, 102, 201–203, 5 files)
│   │   ├── Psychology & EQ/          (PSY101–109, 9 files)
│   │   ├── Learning Skills/          (LRN101–104, 4 files)
│   │   ├── Productivity/             (PRD101–104, 4 files)
│   │   ├── Workplace Skills/         (WRK101–103, STR101, 4 files)
│   │   ├── Thinking Skills/          (THK101–102, 2 files)
│   │   ├── Entrepreneurship/         (ENT101–102, 2 files)
│   │   ├── Assessments/              (ASM101–104, PSY102 self-assessment, 5 files)
│   │   ├── Seasonal Cohorts/         (SPR101 Q2 Reset, 1 file)
│   │   └── Master Catalog/           (ed-prospectus-ed-vault-scla-2026.md, 1 file)
│   ├── Career Readiness Program/
│   │   ├── Career Readiness Accelerator Outline Syllabus
│   │   ├── CRA101 – SCLA Career Readiness Accelerator
│   │   ├── CRA201 – SCLA Career Readiness Certification
│   │   ├── CRA301 – Career Readiness Accelerator Syllabus 2026  ⚠️ DUPLICATE (see below)
│   │   ├── CRA302 – 18 Actionable Strategies
│   │   └── CRC101 – Career Readiness Certification Syllabus     ⚠️ OVERLAP (see below)
│   ├── LinkedIn & Personal Brand Toolkit/
│   │   └── (11 files: define brand, optimize profile, playbook, sleuthing tips,
│   │         escape workbook, 6 ways to grow network, LinkedIn success database,
│   │         activate network, supercharge bio, peer connections, Sophie's challenge)
│   ├── Partner Courses/
│   │   ├── Identity Leadership (IDL)/   (idl-content-from-lxp.md)
│   │   └── ISPI/                        (script-three-archetypes-of-innovation.md,
│   │                                     new-readiness-course-video-needs.md)
│   ├── Wellness Center (Q3 — Not Started)/
│   │   └── wellness-center-framework-draft.md
│   └── Job Readiness Steps (True Colors Series)/
│       └── (step-one through step-four, 4 True Colors video scripts,
│             welcome videos, SMART Goals, peer-connections, career-connections,
│             SCLA Career Hub, SCLA Leadership Program Tech Notes — 16 files)
│           ⚠️ peer-connections-templates.md appears here AND in LinkedIn Toolkit (see below)
│
├── 02 Foundation/
│   ├── Frameworks/
│   │   ├── Durable Skills Framework & Sub-Competency Map 2026
│   │   ├── SCLA C2C Framework 2026
│   │   └── Focus Modes Framework
│   ├── Strategy/
│   │   ├── Education SCLA 2026
│   │   ├── SCLA Product Strategy & Positioning Framework
│   │   ├── Academy v. Honors Features List
│   │   ├── SCLA Scalation Road Map
│   │   └── Leader of the Future
│   ├── Research & Member Feedback/
│   │   ├── OGC Member Survey (Feb 2026)
│   │   └── Focus Group Module Suggestions (ranked by member input)
│   └── _Archive/
│       └── ed-update-feb2026.md  (superseded by Education SCLA 2026)
│
├── 03 Communications/
│   ├── Active/
│   │   ├── Community Communications 2026 PRD
│   │   └── Channels Documentation
│   ├── Standalone Content/
│   │   ├── The Case for Doing Less for Your Community  (newsletter-ready)
│   │   └── What Kind of Learner Are You Right Now      (newsletter-ready)
│   └── _Archive/
│       └── Weekly Updates 2026/
│           ├── Friday Update 02-27-26
│           ├── LT Community & Learning Team Update 03-13-2026
│           ├── Weekly Sync 03-20-2026
│           ├── Weekly Sync 03-27-2026
│           └── Team Update 05-04-2026
│
├── 04 Micro-Internships/
│   ├── Program Roadmap/
│   │   └── micro-internships.md
│   ├── Partner Ideas/
│   │   └── forage.md (Forage partnership)
│   ├── Project Content/
│   │   ├── Digital Access in Nigeria (UN)
│   │   ├── Tech Truck (UN)
│   │   ├── Upskilling Women (UN)
│   │   └── Micro-Internship Samples
│   ├── Member & Partner Assessments/
│   │   ├── Project Interest Assessment
│   │   └── Project Wishlist Assessment
│   └── Outreach & Marketing/
│       └── SCLA Outreach Drafts
│
├── 05 Partner Portal/
│   ├── SGA (Student Government Associations)/
│   │   ├── SGA Pitch to Chapters
│   │   ├── Amy's Notes (SCLA-SGA)
│   │   ├── National University Binder v2
│   │   ├── SGA Presentation (4-7-25)
│   │   └── Stedman Graham Live Handoff Script
│   ├── Leadership Development Coaching Initiative Pilot (DRAFT)
│   └── _Archive/
│       └── (NIC and Voyije → TRASH, not archived — see Stale section)
│
├── 06 Accreditation & Credibility/
│   └── [Reserved — no active docs yet]
│       Note: CRA/CRC certification syllabi live in 01 Learning (CIAO).
│       This folder is for platform-level credentialing docs
│       (Credly/Accredible setup, issuer agreements) once created.
│
├── 07 Team Operations/
│   ├── Member Support/
│   │   ├── Member Support Plan Spec (June 2026)
│   │   └── Membership Team Two-Tier Communication SOP
│   ├── Info Sessions/                               ⚠️ DUPLICATE (see below)
│   │   ├── SCLA Info Session Deck
│   │   ├── SCLA Info Session (marketing version)
│   │   └── SCLA Information Deck
│   ├── Templates & Tools/
│   │   ├── Amy's Test Content (SCLA Learning Program Template)
│   │   └── Community Manager Bios
│   └── Frontline/
│       └── Frontline Forward
│
├── 08 Member Engagement/
│   ├── Member Journey & Onboarding/
│   │   ├── Membership Journey Today (current state doc)
│   │   ├── The BIG Welcome — Onboarding 2026  ⚠️ CANONICAL AMBIGUITY (see below)
│   │   ├── The BIG Welcome — FINAL
│   │   ├── SCLA Orientation Script
│   │   ├── TL;DR Highlights (03-23-26)
│   │   └── _Archive/
│   │       ├── The BIG Welcome v1
│   │       └── The BIG Welcome v1-1
│   ├── Events/
│   │   ├── Events 2026 PRD
│   │   ├── Reset Book Club Guide
│   │   ├── Reset One-Pager
│   │   └── Naming Ideas for the BIG Events
│   ├── Pledge Project/
│   │   └── Pledge Project Outreach Scripts
│   └── Celebrations/
│       └── Emails for the BIG Celebration
│
├── 09 Advisor Community/
│   └── [Empty — no Drive content exists for this initiative]
│       Note: Advisory board structure, recruitment process, and
│       communications all need to be created from scratch.
│
└── _Marketing & Brand/
    ├── SCLA Branding Kit v1.0
    ├── SCLA Information Deck
    └── SGA Overview (1-5-26)
```

---

## Duplicate & Contradiction Flags

> Resolutions updated 2026-06-24 to reflect decisions made in review comments. ✅ = resolved/approved; ❓ = still open pending confirmation.

| # | Files | Issue | Resolution (per review) |
|---|---|---|---|
| ✅ 1 | `cra301-career-readiness-accelerator-syllabus-2026.md` vs `cra301-scla-career-readiness-certification-ispi.md` | Same course code (CRA301), two different versions — one standard, one ISPI-branded | **Keep only the branded (ISPI) version; archive the standard one.** |
| ✅ 2 | `crc101-career-readiness-certification-syllabus.md` vs `cra201-scla-career-readiness-certification.md` | Both appear to be career readiness certification syllabi — unclear if same credential under different codes | **Keep both for now.** Revisit later to confirm whether CRC101 and CRA201 are the same credential; consolidate then if so. |
| ❓ 3 | `the-big-welcome/thebigwelcome-final.md` vs `the-big-welcome/the-big-welcome-onboarding-2026.md` | Both claim to be the current BIG Welcome; "final" was presumably the last version before the 2026 update | **Confirm with Iman and Jenna which one is the most current; archive the other.** |
| ❓ 4 | `community-learning/scla-info-session-deck.md` (in community-learning/) vs `marketing/scla-info-session.md` (in marketing/) | Two info session documents — note one may belong to another team (Sales) | **This may be a Sales-team document.** Do not trash. Confirm ownership with Sales first; default to archive/link rather than trash. If same deck, keep one in `07 Team Operations/Info Sessions/` only with Sales' agreement. |
| ✅ 5 | `peer-connections-templates.md` in `career-courses/job-readiness/` AND `ed-content/10x-toolkits/10x-linkedin/` | Same filename in two directories — likely the same file duplicated | **Keep one canonical copy in `01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit/`; remove the job-readiness copy.** (Approved.) |
| ✅ 6 | `step-one-orientation-true-colors.md` vs `step-one-overview-and-intro-to-four-colors.md` | Both are Step 1 of the job readiness program with overlapping content | **Archive both.** |
| ✅ 7 | `career-connections-templates.md` (job-readiness) vs `peer-connections-templates.md` (LinkedIn toolkit) | May overlap significantly — career connections vs peer connections could be near-identical | **Approved approach:** read both; if content overlaps >50%, merge into one; otherwise keep distinct. |

---

## What Is Clearly Current (keep as active)

- All 60+ course syllabi in `prospectus-syllabi/` — these are the content production backlog
- `community-communications-2026-prd.md` — automation spec
- `events/events-2026-prd.md` — event planning source of truth
- `micro-internships/` all 9 files — active program
- `member-support/member-support-plan-spec.md` — just uploaded June 16
- `learning-frameworks/` all files — active frameworks
- `learning-strategy/focus-modes.md` — active for Aug 1 launch
- SGA partner folder (5 files) — active partnership

## What Is Clearly Stale

> Dispositions updated per review: NIC and Voyije are **TRASH**; the rest are **Archive**.

**Trash** (no future reference value):

- NIC folder (2 files) — wind-down complete
- `voyije-program-wrap-2026-2.md` — program completed

**Archive** (move to `_Archive/`):

- 5 weekly updates (Feb–May 2026) — historical meeting records
- `thebigwelcome-v1.md` and `thebigwelcome-v1-1.md` — superseded
- `ed-update-feb2026.md` — superseded by education-scla-2026

---

## What Is Missing Entirely (gaps to create)

> Note: Kierra, Yesse, and Alyssa can supply source content for several of these. Gather inputs from the three of them before creating placeholders.

1. **Cybersecurity course** — Notion project exists; no Drive doc
2. **Microsoft courses** — Notion project exists (Anushka); no Drive doc
3. **Advisor Community content** — Notion page exists; Drive folder is empty
4. **Post-onboarding 30/60/90 day journey** — no sustained engagement content
5. **Info Session SOP** — slide materials exist but no formatted SOP doc
6. **Champions & Ambassador program** — Notion page exists; no Drive content
7. **Automation templates** — Comms PRD defines what to build but no templates yet

---

## Implementation (when approved)

This is a structural reorganization of the live Google Drive — NOT a task for Claude. Kierra (Drive cleanup owner) should:

1. Create the top-level initiative folders (01–09 + _Marketing & Brand)
2. Move existing files into their new homes
3. Resolve the remaining open flags (#3, #4) before moving; the rest (#1, #2, #5, #6, #7) are decided above
4. Move stale files per the dispositions above (Archive vs. Trash)
5. Create placeholder docs for the 7 gaps above (gather source content from Kierra, Yesse, Alyssa)

No files should be deleted until the team has confirmed the archive copies are accurate, and no other team's shared documents should be trashed.

**Backup owner:** designate a secondary owner with Drive access and training who can pick up the cleanup/maintenance responsibility if Kierra is unavailable.

---

## Appendix: Responses to Review Comments (2026-06-24)

> The Drive integration cannot post replies into the Google Doc comment threads, so the answers are recorded here. Decisions from these comments are already reflected in the sections above.

**On the design principles**

- *"Should set up a back-up plan for who also has access and training."* — Agreed; added a **Backup owner** note under Implementation.
- *"Please explain cross-posting — and why no cross-posting."* — See *Definitions*: cross-posting = the same doc in more than one folder; we avoid it because duplicate copies drift out of sync.
- *"When can someone trash a document? How to know when to trash vs. archive?"* — See the new **Trash vs. Archive guideline**. Short version: archive when in doubt; only trash when there's no reference/cross-team value; never trash another team's shared doc.
- *"Does this mean we don't save v4 or v5?"* — No. The "3 levels" rule is about folder depth, not version retention. Keep the current version active; archive superseded ones.
- *"Do we document by Topic vs. Type? Do we remove the Syllabus folder?"* — Yes, by Topic/Initiative. No standalone Syllabus folder — each syllabus lives under its course topic. (That's separate from cross-posting.)

**On the duplicate/contradiction flags**

- Flag 1 (CRA301): "Keep only the branded one" → keep ISPI version, archive standard. ✅
- Flag 2 (CRC101 / CRA201): "Keep both for now." ✅
- Flag 3 (BIG Welcome): "Confirm with Iman and Jenna; archive the other." ❓ open
- Flag 4 (Info Session): "Another team's (Sales) doc — keep/archive/trash?" → Don't trash a shared doc; confirm with Sales; default to archive/link. ❓ open
- Flag 5 (peer-connections): "Agree" → keep one canonical copy in LinkedIn Toolkit, remove the job-readiness copy. ✅
- Flag 6 (Step 1 versions): "Archive both." ✅
- Flag 7 (career vs peer connections): "Agree" → read both, merge if >50% overlap, else keep distinct. ✅

**On stale content**

- *"Trash NIC, Voyije. The others can be archived."* → NIC and Voyije moved to **Trash**; weekly updates and superseded versions remain **Archive**. ✅

**On gaps**

- *"I can provide some of this to populate. Yesse has some, Alyssa has some, too."* → Noted in the gaps section so source content is gathered from Kierra, Yesse, and Alyssa.

**General**

- *"GREAT work!!"* — Thank you! 🙏
