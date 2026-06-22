# Google Drive Restructure Proposal — June 2026

**Status:** Proposal only — no files have been moved. Kierra to review and approve before any reorganization.
**Prepared:** 2026-06-22
**Source:** 173 Google Drive exports in `_archive/source-dumps/` + live Notion workspace scan

---

## Design Principles

- **One document → one folder.** No cross-posting.
- **Notion initiative = top-level folder.** The team navigates by initiative in Notion; Drive mirrors that.
- **Every folder has an `_Archive/` subfolder.** Active docs and historical records never mix.
- **Flat within sub-folders.** No nesting beyond 3 levels.

---

## Proposed Folder Hierarchy

```
Community Team Drive/
│
├── 01 Learning (CIAO)/
│   ├── Course Catalog/
│   │   ├── AI & Technology/          (AI101–AI306, 9 files)
│   │   ├── Career & Job Search/      (CAR101–106 + Hidden Job Market, Interview Video — 8 files)
│   │   ├── Networking/               (NET101, NET201–202, 3 files)
│   │   ├── Communication/            (COM101–102, 2 files)
│   │   ├── Leadership/               (LDR101–102, LDR201–203, 5 files)
│   │   ├── Psychology & EQ/          (PSY101–109, 9 files)
│   │   ├── Learning Skills/          (LRN101–104, 4 files)
│   │   ├── Productivity/             (PRD101–104, 4 files)
│   │   ├── Workplace Skills/         (WRK101–103, STR101, 4 files)
│   │   ├── Thinking Skills/          (THK101–102, 2 files)
│   │   ├── Entrepreneurship/         (ENT101–102, 2 files)
│   │   ├── Assessments/              (ASM101–104 + PSY102 self-assessment, 5 files)
│   │   ├── Seasonal Cohorts/         (SPR101 Q2 Reset, 1 file)
│   │   └── Master Catalog/           (ed-prospectus-ed-vault-scla-2026, 1 file)
│   ├── Career Readiness Program/
│   │   ├── Career Readiness Accelerator Outline & Syllabus
│   │   ├── CRA101 – SCLA Career Readiness Accelerator
│   │   ├── CRA201 – SCLA Career Readiness Certification
│   │   ├── CRA301 – Career Readiness Accelerator Syllabus 2026   ⚠️ FLAG #1
│   │   ├── CRA302 – 18 Actionable Strategies
│   │   └── CRC101 – Career Readiness Certification Syllabus      ⚠️ FLAG #2
│   ├── LinkedIn & Personal Brand Toolkit/
│   │   └── (11 files: Define Your Personal Brand, Optimize LinkedIn Profile,
│   │         LinkedIn Profile Playbook, Sleuthing Tips, Escape Personal
│   │         Branding Workbook, 6 Ways to Grow Your Network, LinkedIn
│   │         Success Database, Activate Your Network, Supercharge Your
│   │         LinkedIn Bio, Peer Connections Templates, Sophie's Challenge)
│   │                                                              ⚠️ FLAG #5 (Peer Connections duplicate)
│   ├── Partner Courses/
│   │   ├── Identity Leadership (IDL)/   (idl-content-from-lxp)
│   │   └── ISPI/                        (Three Archetypes of Innovation script,
│   │                                     New Readiness Course Video Needs)
│   ├── Wellness Center — Q3 Not Started/
│   │   └── Wellness Center Framework DRAFT
│   └── Job Readiness Steps (True Colors Series)/
│       └── (Step One–Four True Colors video scripts, welcome videos,
│             SMART Goals, peer-connections, career-connections,
│             SCLA Career Hub, SCLA Leadership Program Tech Notes — 16 files)
│                                                                  ⚠️ FLAG #6 & #7 (see below)
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
│       └── ed-update-feb2026  (superseded by Education SCLA 2026)
│
├── 03 Communications/
│   ├── Active/
│   │   ├── Community Communications 2026 PRD
│   │   └── Channels Documentation
│   ├── Standalone Content/
│   │   ├── The Case for Doing Less for Your Community   (newsletter-ready)
│   │   └── What Kind of Learner Are You Right Now       (newsletter-ready)
│   └── _Archive/
│       └── Weekly Updates 2026/
│           ├── Friday Update 02-27-26
│           ├── LT Community & Learning Team Update 03-13-26
│           ├── Weekly Sync 03-20-26
│           ├── Weekly Sync 03-27-26
│           └── Team Update 05-04-26
│
├── 04 Micro-Internships/
│   ├── Program Roadmap/
│   │   └── Micro-Internships Overview & Roadmap
│   ├── Partner Ideas/
│   │   └── Forage Partnership
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
│       ├── NIC/
│       │   ├── Comms SCLA-NIC
│       │   └── NIC Innovation PDF
│       └── Voyije Program Wrap 2026
│
├── 06 Accreditation & Credibility/
│   └── [Reserved — no active docs yet]
│       CRA/CRC syllabi live in 01 Learning (CIAO) > Career Readiness Program.
│       This folder is for platform credentialing docs (Credly/Accredible
│       setup, issuer agreements) once that work begins.
│
├── 07 Team Operations/
│   ├── Member Support/
│   │   ├── Member Support Plan Spec (June 2026)
│   │   └── Membership Team Two-Tier Communication SOP
│   ├── Info Sessions/
│   │   ├── SCLA Info Session Deck (community-learning version)  ⚠️ FLAG #4
│   │   ├── SCLA Info Session (marketing version)                ⚠️ FLAG #4
│   │   └── SCLA Information Deck (general)
│   ├── Templates & Tools/
│   │   ├── SCLA Learning Program Template (Amy's test content)
│   │   └── Community Manager Bios
│   └── Frontline/
│       └── Frontline Forward
│
├── 08 Member Engagement/
│   ├── Member Journey & Onboarding/
│   │   ├── Membership Journey Today  (current-state reference doc)
│   │   ├── The BIG Welcome — Onboarding 2026               ⚠️ FLAG #3
│   │   ├── The BIG Welcome — FINAL                         ⚠️ FLAG #3
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
│       Advisory board structure, recruitment process, and communications
│       all need to be created from scratch.
│
└── _Marketing & Brand/
    ├── SCLA Branding Kit v1.0
    ├── SCLA Information Deck
    └── SGA Overview (1-5-26)
```

---

## Duplicate & Contradiction Flags

Resolve these before moving anything. Each flag is a decision that needs a human call.

| # | Files in conflict | Issue | Recommended resolution |
|---|---|---|---|
| ⚠️ 1 | `CRA301 – Career Readiness Accelerator Syllabus 2026` vs `CRA301 – SCLA Career Readiness Certification (ISPI)` | Same course code, two versions — one standard, one ISPI-branded | Confirm with Amy/Anushka which is current. If both are valid for different audiences, rename to remove ambiguity (e.g., CRA301-Standard / CRA301-ISPI). Archive the inactive one. |
| ⚠️ 2 | `CRC101 – Career Readiness Certification Syllabus` vs `CRA201 – SCLA Career Readiness Certification` | Both appear to be career readiness certification syllabi. Unclear if same credential under different codes or two distinct programs. | Confirm with Anushka. If same program, consolidate into one canonical doc. |
| ⚠️ 3 | `The BIG Welcome — Onboarding 2026` vs `The BIG Welcome — FINAL` | Both claim to be the current BIG Welcome. "Final" was presumably the last version before the 2026 update was added. | Confirm which is the single canonical onboarding doc. Archive the other. (v1 and v1-1 are already clearly superseded.) |
| ⚠️ 4 | `SCLA Info Session Deck` (in community-learning) vs `SCLA Info Session` (in marketing) | Two info session documents in different locations — unclear if same deck duplicated or two different presentations for different audiences. | Review both. If same, keep one copy in `07 Team Operations/Info Sessions/` and delete the duplicate. If different, clarify the distinction in the filename (e.g., "for members" vs "for partners"). |
| ⚠️ 5 | `Peer Connections Templates` in Job Readiness Steps vs `Peer Connections Templates` in LinkedIn Toolkit | Same filename in two locations — almost certainly the same file duplicated. | Keep one canonical copy in `01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit/`. Remove the job-readiness copy. |
| ⚠️ 6 | `Step One – Orientation True Colors` vs `Step One – Overview and Intro to Four Colors` | Both are Step 1 of the job readiness program with overlapping content. | Review whether these are alternate versions of the same module or serve different purposes. If redundant, merge or archive one. |
| ⚠️ 7 | `Career Connections Templates` (job-readiness) vs `Peer Connections Templates` (LinkedIn toolkit) | May overlap significantly — the distinction between "career" and "peer" connections is unclear from filenames alone. | Read both and confirm they're distinct. If content overlaps >50%, merge into one. |

---

## What Is Clearly Current (keep as active)

| Content | Folder | Notes |
|---|---|---|
| 60+ course syllabi in prospectus-syllabi/ | 01 Learning (CIAO)/Course Catalog | Content production backlog for video pipeline |
| Community Communications 2026 PRD | 03 Communications/Active | Automation spec for Weekly News |
| Events 2026 PRD | 08 Member Engagement/Events | Event planning source of truth |
| All 9 micro-internships files | 04 Micro-Internships | Active program |
| Member Support Plan Spec (June 2026) | 07 Team Operations/Member Support | Just uploaded June 16 |
| Durable Skills Framework, C2C Framework, Focus Modes Framework | 02 Foundation/Frameworks | Active for Aug 1 launch |
| SGA partner folder (5 files) | 05 Partner Portal/SGA | Active partnership |
| LinkedIn & Personal Brand Toolkit (11 files) | 01 Learning (CIAO)/LinkedIn Toolkit | Ready-to-use member content |

---

## What Is Clearly Stale (move to `_Archive/`)

| Content | Reason |
|---|---|
| 5 weekly updates (Feb–May 2026) | Historical meeting records; operational value has passed |
| The BIG Welcome v1 and v1-1 | Superseded by newer versions |
| NIC folder (2 files) | Wind-down complete; SCLA is continuation partner only |
| Voyije Program Wrap 2026 | Program completed |
| ed-update-feb2026 | Superseded by Education SCLA 2026 strategy doc |

---

## Content Gaps — What Is Missing Entirely

These exist as Notion projects with no corresponding Drive document. Someone needs to create them.

| Gap | Notion initiative | Owner (from Notion) |
|---|---|---|
| Cybersecurity course content | Learning (CIAO) | TODO |
| Microsoft courses | Learning (CIAO) | Anushka |
| Advisor Community content (any of it) | Advisor Community | TODO |
| Info Session SOP (formatted procedure, not just slides) | Team Operations | Jenna + Iman |
| Champions & Ambassador program content | Member Engagement | TODO |
| Post-onboarding 30/60/90 day journey | Member Engagement | TODO |
| Email automation templates (for Comms PRD) | Communications | Kierra / Sean |

---

## How to Execute (when approved)

This is a manual reorganization task for the Drive owner — **not a Claude task**.

1. Resolve the 7 flags above first (each requires a human decision)
2. Create the top-level initiative folders (01–09 + `_Marketing & Brand`)
3. Create `_Archive/` subfolders within 01, 02, 03, 05, and 08
4. Move stale files to `_Archive/` — do not delete anything yet
5. Move all remaining files to their new homes per the hierarchy above
6. Create placeholder docs (blank or stub) for the 7 content gaps so the team knows they're missing
