---
type: program
status: draft
owner: Kierra
created: 2026-06-24
last_updated: 2026-06-26
---

# Plan: Proposed Google Drive Folder Hierarchy for the Community Team Folder
## Overview

This is a **proposal only** — no files will be moved until approved. The goal is a clean, initiative-aligned Drive structure where every document has exactly one home and stale content is visibly separated from active content.

## Context

The current Drive is unstructured — 173 documents spread across ad-hoc folders with no consistent logic, duplicate files, and no clear active/archive split. This proposal maps a clean folder hierarchy using Notion's 9 initiative categories as the theme clusters, flags every known duplicate or contradiction, and identifies what is stale.

**Design principles:**

- **Organize by Topic/Initiative, not by Type.** Documents are filed by what they're *about* (their initiative), not by their *format*. There is no standalone "Syllabus" or "Video" folder — a syllabus lives with its course topic (e.g., a Career Readiness syllabus lives under `01 Learning (CIAO)/Career Readiness Program/`). To find something, go to the topic, not the file type.
- **Cross-posting** means putting the same document — or a copy/shortcut of it — in more than one folder so it appears in multiple places. We do **not** do this: each document has exactly one home. Duplicated copies drift out of sync (someone edits one, the other goes stale), which is the exact duplicate problem this cleanup is fixing. If a doc is relevant to two initiatives, it still lives in one folder; reference it elsewhere with a link, not a second copy.
- **Folder depth vs. version retention.** "No nesting beyond 3 levels" limits how many folders deep you click — it says nothing about saving v4 or v5 of a file. Version handling is separate: keep the current canonical version active and move clearly superseded versions to `_Archive/`.
- **Remove vs. Archive** Archive = keep but set aside. The doc is no longer active but may have reference or historical value (past weekly updates, superseded versions). Move it to the folder's `_Archive/` subfolder. Remove = remove entirely. The doc has no future reference value

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
│   │   ├── Assessments/              (ASM101–104 + PSY102 self-assessment, 5 files)
│   │   ├── Seasonal Cohorts/         (SPR101 Q2 Reset, 1 file)
│   │   └── Master Catalog/           (ed-prospectus-ed-vault-scla-2026, 1 file)
│   ├── Career Readiness Program/
│   │   ├── Career Readiness Accelerator Outline & Syllabus
│   │   ├── CRA101 – SCLA Career Readiness Accelerator
│   │   ├── CRA201 – SCLA Career Readiness Certification
│   │   ├── CRA301 – Career Readiness Accelerator Syllabus 2026  
│   │   ├── CRA302 – 18 Actionable Strategies
│   │   └── CRC101 – Career Readiness Certification Syllabus     
│   ├── LinkedIn & Personal Brand Toolkit/
│   │   └── (11 files: Define Your Personal Brand, Optimize LinkedIn Profile,
│   │         LinkedIn Profile Playbook, Sleuthing Tips, Escape Personal
│   │         Branding Workbook, 6 Ways to Grow Your Network, LinkedIn
│   │         Success Database, Activate Your Network, Supercharge Your
│   │         LinkedIn Bio, Peer Connections Templates, Sophie's Challenge)
│   │                                                             
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
│                                                                  
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
│       └── ed-update-feb2026  (superseded by Education SCLA 2026)
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
│       └── (NIC and Voyije → TRASH, not archived — see Stale section)
│
├── 06 Accreditation & Credibility/
│   └── [Reserved — no active docs yet]
│       Note: CRA/CRC certification syllabi live in 01 Learning (CIAO).
│       This folder is for platform-level credentialing docs
│       (Credly/Accredible setup, issuer agreements) once created.
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
│   │   ├── SCLA Info Session Deck
│   │   ├── SCLA Info Session (marketing version)
│   │   └── SCLA Information Deck
│   ├── Templates & Tools/
│   │   ├── Amy's Test Content (SCLA Learning Program Template)
│   ├── Info Sessions/
│   │   ├── SCLA Info Session Deck (community-learning version)  
│   │   ├── SCLA Info Session (marketing version)                
│   │   └── SCLA Information Deck (general)
│   ├── Templates & Tools/
│   │   ├── SCLA Learning Program Template (Amy's test content)
│   │   └── Community Manager Bios
│   └── Frontline/
│       └── Frontline Forward
│
├── 08 Member Engagement/
│   ├── Member Journey & Onboarding/
│   │   ├── Membership Journey Today (current state doc)
│   │   ├── The BIG Welcome — Onboarding 2026 
│   │   ├── The BIG Welcome — FINAL
│   │   ├── Membership Journey Today  (current-state reference doc)
│   │   ├── The BIG Welcome — Onboarding 2026               
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
│       Advisory board structure, recruitment process, and communications
│       all need to be created from scratch.
│
└── _Marketing & Brand/
    ├── SCLA Branding Kit v1.0
    ├── SCLA Information Deck
    └── SGA Overview (1-5-26)
```
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

---

## Implementation

This is a structural reorganization of the live Google Drive 
1. Create the top-level initiative folders 
2. Move existing files into their new homes
4. Move stale files per the dispositions above (Archive vs. remove)

---
## What Is Missing Entirely (move to TODO to be created later)

1. **Cybersecurity course** — Notion project exists; no Drive doc
2. **Microsoft courses** — Notion project exists (Anushka); no Drive doc
3. **Advisor Community content** — Notion page exists; Drive folder is empty
4. **Post-onboarding 30/60/90 day journey** — no sustained engagement content
5. **Info Session SOP** — slide materials exist but no formatted SOP doc
6. **Champions & Ambassador program** — Notion page exists; no Drive content
7. **Automation templates** — Comms PRD defines what to build but no templates yet


