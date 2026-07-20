# SCLA Community Team Drive — Annotated Worktree (Refactor Proposal v2)

**Status:** final proposal — decision-made, adversarially reviewed, ready for dry run
**Date:** 2026-07-20
**Scope:** the live **Community Team Folder** `1i2Y4cx2bg2qqopCFTq-5SbP4e7SMTFWu` **plus every folder/file shared with community@thescla.org** — the old "Community & Learning SCLA" drive, "Marketing SCLA", "Chapter Interns", "Accreditation SCLA", and 14 standalone shared files (~500 items total, fully inventoried 2026-07-20, all suspected duplicates content-verified by opening the files).

How this proposal was built: full recursive inventory of the live Drive (every level, including
shared items) → content verification inside every suspected duplicate → draft taxonomy →
three independent adversarial reviews (taxonomy, Apps Script feasibility, item-by-item
completeness) → this arbitrated final. The prior brief (`projects/drive-review-brief.md`)
described a Drive that has since drifted substantially; where this proposal overrules it,
that is stated explicitly.

---

## 1. Organizing framework (the rules that decide where anything lives)

1. **Topic/initiative, not type.** A file lives with what it is *about*, never in a
   format folder. (One consequence: the old `07 Templates & Tools` junk-drawer idea is
   dissolved; each template lives with its topic.)
2. **One home per document.** Shortcut duplicates collapse; cross-references are links.
3. **Max 3 folder levels below root**, with two explicit exemptions:
   sibling `_Archive/` folders, and Google-Forms-managed "(File responses)" subtrees,
   which must move intact or live submissions break.
4. **`_Archive/` = superseded or historical, kept for reference. Trash = zero future
   value**, 30-day recoverable, and only ever by file ID after content verification.
5. **No empty folders.** Every folder in the target tree receives content on day one.
   (This kills the reserved-but-empty "09 Advisor Community".)
6. **Names:** the script creates clean names (no trailing/double spaces) and applies an
   explicit rename list to broken file names.

## 2. Target tree — where everything goes and why

Legend: `←` source location today. **ED#** = executive decision (§3). ⚠ = expected
OWNER-BLOCKED (see §6). ↩ = shortcut kept as pointer (target lives outside our reach).

```
Community Team Folder/
│
├── 01 Learning (CIAO)/
│   ├── Course Catalog/                     ← C&L "Prospectus, Syllabi, Catalog, Templates" (59 course docs route by code prefix)
│   │   ├── AI & Technology/               AI101–AI306; + "Grow With Google: Foundations of Cybersecurity" ← C&L/Ed Content Development
│   │   ├── Career & Job Search/           CAR101–106; + Hidden Job Market for Graduates.pptx ← C&L/Career Courses;
│   │   │                                  + "Course Title: Brand You" + "Course Title: Rockstar Interview Video" (renamed — see §5)
│   │   ├── Networking/  Communication/  Leadership/  Psychology & EQ/  Learning Skills/
│   │   ├── Productivity/  Workplace Skills/  Thinking Skills/  Entrepreneurship/
│   │   ├── Assessments/                   ASM101–104, PSY102 self-assessment; + AI Assessment Sample ← CT/Education & Learning Programs
│   │   ├── Seasonal Cohorts/              SPR101 (Q2 Reset)
│   │   └── Master Catalog/                Ed Prospectus_Ed Vault_SCLA 2026; "SCLA Course Catalog (Master)" sheet (renamed from "Copy of…" — the ~125-course master list)
│   ├── Career Readiness/                   ── ONE umbrella for the four career doors (panel finding: 4 sibling folders all answered to "career")
│   │   ├── Career Readiness Program/      CRA/CRC syllabi (CRA301_2026 = current), "Career Readiness Accelerator Outline > Syllabus" draft,
│   │   │                                  Career_Accelerator_Framework.pptx (pdf twin → _Archive), Career Readiness & Decision-Making Tool.pdf,
│   │   │                                  Career Accelerator_Honors_PunchList → NO — lives in The Academy (ED8); ↩ CR Index Score shortcut
│   │   │                                  └── _Archive/  superseded CRA301 (undated) ← CT/_Archived; V1Design shortcuts collapse
│   │   ├── Career Toolkit/                canonical 2026 doc + distributable pdf export + workbook.pdf + "Tools as Learning Activity or Track ??";
│   │   │                                  ↩ Graduate Career Toolkit shortcut
│   │   │                                  └── _Archive/  _FULL.pdf (superseded STAR-era toolkit — verified), Currency Audit (1 of 2 — twin trashed)
│   │   ├── LinkedIn & Personal Brand Toolkit/   ← entire C&L "10X Toolkits/10X LinkedIn" + strays:
│   │   │                                  playbooks, workbooks, cheat sheets, zips, "1.3 Define your Personal Brand.docx" ← CT/_Archived,
│   │   │                                  "1.4 Optimize your LinkedIn profile.docx", Sophie's Challenge
│   │   ├── Job Readiness Steps (True Colors Series)/   ← C&L "Job Readiness Content": Step One–Four pptx, SMART Goals,
│   │   │                                  four color videos pptx, Peer/Career Connections Templates docs, Welcome/Choose-Orientation decks,
│   │   │                                  ↩ Career Hub, Tech notes, Certification Steps, Non-Public program shortcuts
│   │   │                                  └── _Archive/  "Orange: Four True Colors" size-twin (byte-checked; else stays), older Welcome-deck variant (§4 Q5)
│   │   └── You Got This Series/           ← "Media Review_Lori&Classic": the 12 course-module MP4s (this IS the course, not "media";
│   │                                      two missing .mp4 extensions fixed — §5)
│   ├── Course Development/                 ── how courses get made (was scattered across 3 old folders)
│   │                                      "The New Syllabus" (pedagogy guide — verified distinct from CRA syllabi), Video Production Samples/Process/Costs,
│   │                                      "Explaining the Learning at the SCLA", Education_Content_2026.xlsx (content tracker),
│   │                                      ↩ SCLA Learning Program Template + Certified Member template shortcuts
│   │                                      └── _Archive/  "Amy's Test Content SCLA Learning Program Template" (test data)
│   ├── Partner Courses/
│   │   ├── Identity Leadership (IDL)/     IDL Content from LXP ← C&L/Partner Courses/IDL and SGA
│   │   └── ISPI/                          scripts (3 ↩ shortcuts), "New Readiness Course Video Needs", current videos (Oct 2025 render) directly here
│   │                                      └── _Archive/  Sept 2025 render set (§4 Q1)
│   ├── The Academy/                       ← both C&L "The Academy " folders (empty twin trashed — ED8):
│   │                                      Academy v. Honors Features List, Conference Planning doc (+ ↩ pptx shortcut),
│   │                                      Academy_Career Essentials PunchList, Career Accelerator_Honors_PunchList, Scalation Road Map? → NO (02/Strategy)
│   └── Wellness Center/                   CONDITIONAL — only content is an unknown-target shortcut ("Wellness Center Framework DRAFT");
│                                          folder is created only if the target resolves, else logged RESOLVE-REVIEW (no empty folders)
│
├── 02 Strategy & Frameworks/               (renamed from "Foundation" — read as philanthropic; ED-panel)
│   ├── Frameworks/                        C2C pdf (+ png), Durable Skills doc (docx twin → _Archive),
│   │                                      "Durable Skills — Competency & Sub-Competency Table" (renamed from "Untitled document" — verified real taxonomy),
│   │                                      Competency and Sub-Competency List sheet (reconcile flag), Focus Modes, Powerful Personal Development
│   ├── Strategy/                          Education_SCLA_2026.pdf, ↩ Product Strategy & Positioning shortcut, SCLA Scalation Road Map.pdf,
│   │                                      🌟 Leader of the Future, SCLA Hi Po National Rollout Proposal.docx, "WORKSHOP  PROPOSAL" (Yesse) ⚠
│   ├── Research & Member Feedback/        OGC member survey, Focus group module suggestions, "Sharing our 🧡 Testimonials",
│   │                                      Feedback from Advisors (Tally) sheet, Compelling Parts of Member's Area sheet
│   ├── Metrics & Reporting/               Ed Metrics sheet ⚠, Education_Community_2026_SCLA sheet
│   ├── Grants/
│   │   └── Career Passport/               2 RFP Google Docs (working copies)
│   │       └── _Archive/                  the 2 raw .md source files ← CT/_Archived (provenance; Docs are the working format — overrules verifier's keeper pick)
│   └── _Archive/                          Ed Update Feb2026 slides (superseded by Education SCLA 2026)
│
├── 03 Communications/
│   ├── Weekly Updates/                    "Community Team Weekly" (live doc)
│   │   └── _Archive/                      the 4 dated updates (02.27, 03.13, 03.20, 03.27)
│   ├── Channels & Planning/               Community Communications_2026_PRD, #channels doc, SCLA_Channel_Map.xlsx,
│   │                                      "Standard Operating Procedure (SOP)" (verified: channel-taxonomy SOP), ↩ Email Deliverability Guide
│   │   └── _Archive/                      Notion's Lifecycle Engine pdf (160 MB third-party reference)
│   └── Social Media & Blog/               ← C&L "Member Social Media ": ↩ SM & Blog SOP + Calendar shortcut
│                                          (Voice and Tone doc → 09; BrandingKit (3) shortcut collapses)
│
├── 04 Micro-Internships/                   ← C&L "Micro Internships" + CT remnants
│   ├── Program Roadmap/                   Micro-Internships doc, ↩ development-context shortcut, Overview & Strategic Discussion,
│   │                                      Explaining Micro-Internships_v1.pdf, Program/Eligibility/Details doc
│   ├── Partner Ideas/                     Forage.pdf
│   ├── Project Content/                   3 UN project pdfs, Micro-Internship Samples.docx, Rubrics sheet
│   ├── Assessments/                       project_interest + project_wishlist docx
│   ├── Outreach & Marketing/              "MI Company Outreach List (Master)" (renamed — verified superset, 3,050 rows),
│   │                                      Mentors + Sponsors form, ↩ SCLA Outreach Drafts shortcuts (2, deduped)
│   │   └── _Archive/                      "MI Company List " + "Micro-Internship Companies" (verified older/partial versions of the same dataset)
│   └── Templates & Letters/               RecommendationLetterTemplatePronouns.docx (plain version trashed — superseded),
│                                          MI Completion Letter Template.docx (exact-dup twin trashed — it also misnamed the org),
│                                          Micro-Internship Project Template sheet ⚠ (personal-gmail owner)
│       └── _Archive/                      Recommendation Letter for Isabel Elimu (filled letter = PII record, not a template)
│
├── 05 Partnerships/                        (renamed from "Partner Portal" — now holds real partner ops: ED7)
│   ├── SGA (Student Government Associations)/   ← C&L "SGA & SCLA Partnership ": pitch pptx, National University Binder,
│   │                                      Stedman Graham handoff script, Amy's Notes, Agenda, SGA 4-7-25 pdf
│   ├── Legal & Agreements/                ← "Legal Docs Partnerships" flattened: CGHS indemnification (signed pdf kept; docx copies deduped),
│   │                                      ICS Engagement Agreement doc (byte-identical docx twin trashed; one docx kept), SCLA-ICS-MOU (doc; docx twin → _Archive),
│   │                                      2 MOUs, Educational Partnership LOI, Partner Types doc
│   ├── Partner Directory & Lists/         Company & Expert Directory.xlsx, SCLA_VendorsReport.xlsx, Expert Partners-All companies.csv
│   ├── Leadership Development Coaching Initiative Pilot_Draft.docx    (files directly here — 1 doc doesn't earn a folder)
│   └── _Archive/                          NIC wind-down set (Comms SCLA_NIC, NIC_Innovation pdf, 2 NIC list csvs) + Voyije Program Wrap pdf
│                                          — ED2: OVERRULES the brief's "trash NIC/Voyije"; partner history is cheap to keep, and
│                                          the NIC folder turned out to contain a SIGNED legal agreement (→ Legal & Agreements)
│
├── 06 Accreditation & Credibility/         ← the entire shared "Accreditation SCLA" folder — the reserved-empty 06 finally gets its real content (ED3)
│   ├── NECHE/                             Provider Workshop Activity doc (pdf twin → _Archive)
│   ├── AACRAO/                            Technical Overview doc (pdf twin → _Archive), signed AACRAO Agreement, AACROA letter, SCLA ppt,
│   │   └── FERPA/                         ── the four scattered FERPA folders collapse to ONE:
│   │                                      FERPA Policy_ISPI, FERPA_New.pdf, certification pdf, compliance statement pdf, NAB-to-Registrar template pdf,
│   │                                      CSU articulation sample, ↩ policy/FAQ/affidavit/MOU shortcuts (deduped — "FERPA Policies for SCLA" wrapper dies)
│   ├── NAB (National Advisory Board)/     Dec '25 NAB Meeting pptx (a board deck was buried in "FERPA Misc." — panel finding)
│   ├── WASC/                              WASC Certificate
│   └── Accreditation Application (ARRAY)/ Self-Study v1 sheet, Accred Visit QA, ↩ Constitution shortcut ("Items of Evidence" empty folder not recreated)
│
├── 07 Team Operations/
│   ├── Member Support/                    ↩ Member Support_Spec shortcut, Two-Tier Communication SOP ⚠, SCLA Engagement Flow docx,
│   │                                      SCLA_Knowledge_Base_Master_FAQ_Outline.docx ← CT/FAQs 2026, ↩ SCLA FAQ shortcut
│   │   └── _Archive/                      legacy 2015/16 admin@ "Member FAQ" + "Member Support SOP" (kept as ↩ pointers — unmovable, ED13)
│   ├── Team Admin & Planning/             Team Hour Tracker, Community Team RR_June2026, Q2 Projects sheet, Feature and Bug List,
│   │                                      Community Manager Bios, Dashboard Drive-Through recording (staff product walkthrough),
│   │                                      "Plan: Proposed Google Drive Folder Hierarchy" (kept as provenance of this refactor)
│   ├── Finance & Vendor Records/          Est_13532 Underground Sports Shop invoice ← "LXPs and Leaderboards" (folder dies; an invoice is not
│   │                                      member engagement — panel finding; first finance home in the tree)
│   ├── Chapter Interns/                   ← shared "Chapter Interns" folder: CP Weekly pdf + pptx, 4 ↩ intern shortcuts (ED6: internal program, not a partnership)
│   └── Frontline/                         Frontline Forward
│
├── 08 Member Engagement/
│   ├── Member Journey & Onboarding/       "Membership Journey Today " ⚠, Enrolling in Orientation from the Dashboard, TL;DR Highlights (both),
│   │                                      The BIG Welcome_Onboarding_2026 doc, Orientation SOP 5.28.26, Thank you Orientation (mail layout),
│   │                                      ↩ Fall Member Journey INTERNAL PLAYBOOK shortcut
│   │   └── _Archive/                      Reminder Email DRAFT, Follow Up Orientation Email DRAFT (superseded by Orientation SOP)
│   ├── Events/                             ── ED4: the FOUR competing Events folders merge here
│   │   ├── Event Planning/                Event Tracker, Event Calendar Descriptions, Event Proposal June 2026, Events_2026_PRD,
│   │   │                                  Event Operations DRAFT, Event Team 10-Hour Cadence pdf, "Zoom Webinar Roles" (renamed sheet),
│   │   │                                  Naming Ideas for BIG Events, RESET Book-Club Guide + One-Pager, ↩ Project Ops Coordinator SOP shortcut
│   │   ├── The BIG Welcome/               TheBIGWelcome FINAL(May2026).pptx (current), both Orientation Scripts (same name, two authors — §4 Q3),
│   │   │                                  "Orientation Slides ", Importance of Community.MOV, TheSCLABigWelcome.m4a,
│   │   │                                  renamed welcome recordings (§5)
│   │   │   └── _Archive/                  TheBIGWelcome_v1.pptx, Google-Slides FINAL (older of the two FINALs — §4 Q4); the 99 MB "(1)" byte-twin is trashed after byte check
│   │   ├── The BIG Celebration/           May: agenda, Celebration Comms, PPT, "MAY2026 …Script FINAL" doc (moved in — both shortcuts to it collapse),
│   │   │                                  Emails for the BIG Celebration; Aug: August agenda, ↩ August DRAFT shortcut;
│   │   │                                  Raffle + Scholarship Winner forms with their full "(File responses)" trees ⚠ (personal-gmail owner — ED15),
│   │   │                                  Zena Collins/ (student photo submissions, kept as-is)
│   │   ├── Info Sessions/                 SCLA Info Session FINAL slides ← Marketing SCLA, ↩ MAY2026 deck / script / outreach-template / plan shortcuts (deduped)
│   │   │   └── _Archive/                  ARCHIVE Info Session Slides.pptx + ARCHIVE deck shortcut (as labeled)
│   ├── Champions & Ambassadors/           ── ED5: the program finally gets a home (13+ files, no home in any prior plan)
│   │                                      ← C&L "Community Champions Program" + "Community Champions 2026" + kickoff folder:
│   │                                      Scope doc (pdf twin → _Archive), kickoff pptx + agenda/presenter docx, Application Questions sheet
│   │                                      (csv exports → _Archive), invitation/ceremony/template docx pack, Sample Ambassador Programs.pdf,
│   │                                      "Combined files.pdf" (log RENAME-REVIEW), ↩ Champions Application (Responses) shortcut,
│   │                                      "Scla Community Engagement Sop 2026.5.5.pdf" (verified: champion/stipend SOP — topic home is here, not 07)
│   ├── Pledge Project/                    "Pledge Project Outreach Scripts " ⚠ (both pointer shortcuts collapse)
│   └── SCLA_Swag_Incentive_Program_Proposal.docx ⚠   (files directly here — 1 doc doesn't earn a folder)
│
└── 09 Marketing & Brand/                   (was "_Marketing & Brand"; promoted to the number it deserves once 09 Advisor Community was cut)
    ├── SCLA Brand Guide, SCLA Visual Identity ← CT/Branding & Communications
    ├── "SCLA Voice and Tone" ← C&L/Member Social Media — ED10: content-verified NEWER canonical (three-pillar spine, 2026-04-23)
    ├── SCLA_BrandingKit_v1.0 (2).pdf, SCLA Information Deck (native slides), SGA Overview pptx,
    ├── SCLA Learning_Overview.png, ↩ Marketing & Brand Guidelines for ICS shortcut, ↩ Explaining SCLA shortcut
    └── _Archive/   older "SCLA Voice & Tone" doc, SCLA Information Deck.pptx (verified identical 20-slide format twin)
```

**Cut from the old plans:** `09 Advisor Community` (would be empty on day one — advisor
material actually lives in 02/Research and 06/NAB; recreate when advisor programming
produces files). `03/Standalone Content` (phantom — its two planned files don't exist in
the live Drive). `Templates & Tools`, `Incentives & Recognition`, `Coaching Initiative
Pilot`, `Celebrations` as folders (each held ≤1 real item; contents filed by topic).

**Sources that end up empty and are then retired:** CT: `Branding & Communications`,
`Education & Learning Programs`, `Events `, `FAQs 2026`, `Member Engagement`, `SOP's
Admin & Governance`, `_Archived`, `Grants` (shell after move); C&L: all 25 subfolders +
the 2 already-empty ones; `Marketing SCLA`, `Chapter Interns`, `Accreditation SCLA`
(owner-permitting — each old root gets a `MOVED — see Community Team Folder` marker doc,
since the roots themselves cannot be moved or trashed by community@).

---

## 3. Executive decisions (where I made the call)

| # | Decision | Why |
|---|----------|-----|
| ED1 | One canonical tree = Community Team Folder; the 4 shared drives are absorbed (children moved in; roots marked & retired) | community@ owns it; the 01/02/03 skeleton was already started there; every alternative multiplies owner-blocked moves |
| ED2 | **NIC/Voyije: archive, not trash** — overrules the brief | The "trash" folder contained a signed CGHS indemnification agreement; signed legal docs are never trash. Partner history costs nothing in `_Archive` |
| ED3 | Entire Accreditation SCLA tree → 06 (child-by-child, not root move) | Fills the reserved-empty 06 with its real content; root itself is unmovable by a non-owner |
| ED4 | Four Events folders merge into `08/Events` with per-event subfolders | The #1 findability failure in the live Drive |
| ED5 | Champions & Ambassadors → `08` | Member-facing program, 13+ live files, no home in any prior plan |
| ED6 | Chapter Interns → `07` | Internal team program, not a partnership |
| ED7 | `05 Partner Portal` → **`05 Partnerships`** + Legal & Agreements + Directory | The live content is partner *operations* (MOUs, signed agreements, directories) — "Portal" described nothing that exists |
| ED8 | The Academy → `01 Learning/The Academy`; empty duplicate folder trashed | Learning-product initiative; punch lists + conference planning + Academy-v-Honors cohere by topic |
| ED9 | Course media lives with its course (ISPI videos in ISPI; "You Got This" MP4s are a course folder, not "media") | Topic-not-type; Oct-2025 ISPI render kept current, Sept render archived (§4 Q1) |
| ED10 | Canonical Voice & Tone flips to the C&L copy | Content-verified newer (three-pillar spine, verified 2026-04-23). Repo `brand/voice-and-tone.md` may need re-sync — flagged |
| ED11 | MI company-list master = the "Copy of… Outreach List" superset; other two sheets archived | Content-verified: 3,050 rows + form responses vs 2,293 and 775 subsets |
| ED12 | Keep "Plan: Proposed Google Drive Folder Hierarchy" (provenance); trash "Community Team Drive_Proposed Refractor" | Verified: the latter is a mangled, self-contradicting derivative of the former |
| ED13 | Legacy 2015/16 admin@ Member FAQ/SOP → pointer shortcuts in `07/Member Support/_Archive` | Owner unreachable; content historically valuable; originals cannot be moved |
| ED14 | All 10 loose CT-root shortcuts + C&L root shortcuts collapse after their targets are routed | One-home rule |
| ED15 | Forms + "(File responses)" trees move intact with The BIG Celebration | Forms bind by ID, not path — moving is safe; restructuring the response tree is not |
| ED16 | 02 renamed **Strategy & Frameworks**; Grants stays inside it | "Foundation" misreads as philanthropic; grants are a strategy function here |
| ED17 | Trash is **ID-only, content-verified, capability-gated**; anything a non-owner can't trash goes to `_PENDING-OWNER-TRASH/` with an owner worklist | Non-owners cannot trash My-Drive files; silent exception storms would corrupt the run |

## 4. Duplicates

**Auto-resolved (content-verified, no action needed from you):**

| Files | Verdict | Action |
|---|---|---|
| 2 × `SCLA_Career_Toolkit_2026_Currency_Audit.md` | exact duplicate | keep one, trash twin |
| 2 × `ICS_SCLA_Engagement Agreement…docx` | byte-identical (85,755 B) | trash one |
| `TheBIGWelcome_v1.pptx` vs `(1)` copy | 99 MB twins | byte-check → trash copy (else archive) |
| 2 × completion-letter templates | exact dup (one misnames the org) | keep "MI Completion Letter Template", trash twin |
| Rec-letter plain vs Pronouns | version | keep Pronouns, trash plain |
| RFP doc vs .md pairs (×2) | format twins | Docs stay working copies; .md → Grants/_Archive |
| Information Deck slides vs .pptx | identical 20 slides | keep Slides, archive pptx |
| Technical Overview / Durable Skills / NECHE Worksheet / Career_Accelerator_Framework doc-vs-pdf(/docx) | format twins | keep native doc, archive export |
| CRA301 undated vs `_2026` | version | `_2026` current, other archived |
| **CRC101 vs CRA201** | **NOT duplicates** (1.0-cr certification vs 3.0-cr accelerator) — the old brief was wrong | both kept |
| May vs August Celebration agendas | different events | both kept |
| Champions application CSV vs Sheet | export twins | keep Sheet, archive CSVs |
| "Copy of Course Title: Brand You" | misnamed, different course | renamed, both kept |
| 3 MI company lists | one dataset, three generations | master renamed, two archived (ED11) |
| Voice & Tone pair | version | C&L copy canonical (ED10) |
| Engagement "SOP" pdf vs "Standard Operating Procedure (SOP)" doc | **different documents** (champion/stipend vs channel taxonomy) | routed separately (08 / 03) |

**Needs your eyes (the only questions I'm asking):**

1. **ISPI renders** — Sept 2025 set (`ISPI New_Videos`) vs Oct 2025 set (`New_ISPI_New_Andrew`): same lessons, two different cuts. I archive Sept and keep Oct as current. Confirm, or tell me Sept is the aired version.
2. **"Orange: Four True Colors Video.pptx"** is byte-size-identical to "Step One Overview and Intro to Four Colors.pptx". Script trashes it only on byte match; otherwise archives. OK?
3. **Two docs both named "SCLA Orientation Script"** (jheath 2026-04-20 vs ilomax 2026-04-06): same name, two authors, no verdict on which is current. Both move to `The BIG Welcome/`; which one is canonical?
4. **Two BIG Welcome "FINAL" decks** — Google Slides FINAL (May 5) vs `FINAL(May2026).pptx` (Jun 1). I keep the pptx as current and archive the Slides. Confirm?
5. **Welcome/Choose-Orientation pptx pair** ("Welcome to the SCLA Program & Choosing your Orientation Learning Option" vs "Welcome to the Program & Choose Orientation Video") — near-duplicates by name, not content-verified. I archive the older (May 23). Confirm?
6. **Engagement SOP "final"** — the shortcut `Scla Community Engagement Sop (final).docx` may target a NEWER version of the 2026.5.5 pdf I routed. The script resolves it at run time and logs RESOLVE-REVIEW if the target differs.

## 5. Renames the script applies

| From | To |
|---|---|
| "Untitled document" (Learning Frameworks) | Durable Skills — Competency & Sub-Competency Table |
| Copy of Zoom Webinar Roles | Zoom Webinar Roles |
| Copy of SCLA Course Catalog | SCLA Course Catalog (Master) |
| Copy of Course Title: Brand You | Course Title: Rockstar Interview Video |
| Copy of Micro Internship Company Outreach List | MI Company Outreach List (Master) |
| ISPS Intro.mp4 | ISPI Intro.mp4 |
| Module1_Launchpad / Module2_KnowYourself | + ".mp4" |
| video1210672546.mp4 / video2594629446.mp4 / audio2594629446.m4a | BIG Welcome Recording 2026-03-12.mp4 / …2026-02-24.mp4 / BIG Welcome Audio 2026-02-24.m4a |

(Plus: every folder the script creates uses clean names — no trailing/double spaces.)

## 6. Ownership reality (what the script can and cannot do)

- Most old-drive content is owned by **awestby@ / ilomax@ / yordonez@ / jheath@** (org
  accounts). Editors *can usually move and rename* those files; they **cannot trash** them.
  The script probes per-file capabilities in the dry run and reports the *predicted*
  outcome for every item (MOVE / SHORTCUT-FALLBACK / TRASH-BLOCKED) instead of guessing.
- **Unmovable by design:** the 4 shared roots and the 14 standalone shared files (their
  parent is the owner's My Drive root). They get organized **pointer shortcuts** in their
  topical home + an ownership-transfer worklist.
- **Personal-gmail owners** (jheathmoreno@gmail.com scholarship form tree;
  sureka.anushka23@gmail.com MI template): consumer→Workspace ownership transfer is
  blocked by Google. Remedy is copy-and-retire (noted in worklist), never automated.
- Before execute, the script **shares the Community Team Folder with all org content
  owners** so moved files never vanish from their owners' view.

## 7. What the script produces

Dry run writes a Google Sheet where every row is one item with: current path → destination,
predicted outcome, and reason tag (`ROUTE-ID`, `ROUTE-COURSE`, `ROUTE-NAME`, `COLLAPSE-SHORTCUT`,
`KEEP-AS-POINTER`, `TRASH-VERIFIED`, `ARCHIVE`, `RENAME`, `OWNER-BLOCKED`, `RESOLVE-REVIEW`,
`UNMATCHED`). Execute applies it with checkpoint/resume, and ends with the owner worklist
(transfers + pending trash + review flags).
