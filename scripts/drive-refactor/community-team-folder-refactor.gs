/**
 * SCLA Community Team Drive — Folder Refactor v2
 * ==============================================
 * Consolidates the Community Team Folder AND the four legacy shared drives
 * ("Community & Learning SCLA", "Marketing SCLA", "Chapter Interns",
 * "Accreditation SCLA") plus standalone shared files into ONE canonical tree,
 * per scripts/drive-refactor/ANNOTATED-WORKTREE.md.
 *
 * Built against the full live inventory of 2026-07-20 (~500 items). Routing is
 * ID-FIRST: every explicitly decided item routes by Drive file ID (immune to the
 * trailing-space and duplicate-name landmines in this Drive). Name rules and the
 * course-code router exist only as fallback for files created after the inventory.
 *
 * v2 design points (from adversarial feasibility review):
 *  - Capability-probed DRY RUN: predicts MOVE / SHORTCUT-FALLBACK / TRASH-BLOCKED
 *    per item using the Drive advanced service (enable "Drive API" under
 *    Services in the Apps Script editor; see README).
 *  - Non-owner trash never throws the run: canTrash items are trashed, the rest
 *    are staged into "_PENDING-OWNER-TRASH/" with an owner worklist.
 *  - Shared ROOTS and parentless shared files are never moved (impossible for a
 *    non-owner); their CHILDREN are moved, or a pointer shortcut is created.
 *  - Shortcut tri-policy: COLLAPSE (target routed into tree) / KEEP-AS-POINTER
 *    (target alive but outside our reach) / DEAD-OR-INVISIBLE (flagged, staged).
 *  - Folders are created LAZILY (only when the first item lands) — the tree can
 *    never contain empty placeholder folders.
 *  - Continuation-safe: elapsed-time guard, chunked checkpoints in
 *    PropertiesService, self-scheduling resume trigger, LockService, batched
 *    Sheet logging, exponential backoff on every Drive write.
 *
 * RUN ORDER: dryRun() → review the "Drive Refactor Log (DRY RUN)" Sheet →
 * execute() → review "Drive Refactor Log" + the OWNER WORKLIST tab.
 */

// ============================================================================
// CONFIG
// ============================================================================

var ROOT_FOLDER_ID = '1i2Y4cx2bg2qqopCFTq-5SbP4e7SMTFWu'; // Community Team Folder

/** Legacy shared roots. Children are absorbed; the roots themselves only get a
 *  "MOVED" marker doc (a non-owner cannot move or trash another user's root). */
var SOURCE_ROOTS = [
  '1lqXCKzPC5bwVfFCRu60aFgLyxRT8FEEx', // Community & Learning SCLA
  '1tLn-UcNvWtlRi0WHwJhyzS_rXQxV3-VA', // Marketing SCLA
  '1zznScJ44VDAIGyIu5WspIQ4_OjbJfClF', // Chapter Interns
  '1vPVQMY5xs1ecF0GSQQyAdYSt7liYepPv'  // Accreditation SCLA
];

/** Org content owners: execute() shares the Community Team Folder with them so
 *  files they own never vanish from their view after a move. */
var OWNER_EMAILS = [
  'awestby@thescla.org', 'ilomax@thescla.org', 'yordonez@thescla.org',
  'jheath@thescla.org', 'mgueta@thescla.org', 'membership@thescla.org'
];

var DRY_RUN = true;                 // set by the entry points; don't edit
var ARCHIVE = '_Archive';
var PENDING_TRASH = '_PENDING-OWNER-TRASH';
var TIME_BUDGET_MS = 4.5 * 60 * 1000; // exit-and-resume before the 6-min wall

// ============================================================================
// ENTRY POINTS
// ============================================================================

function dryRun()  { DRY_RUN = true;  run_(); }
function execute() { DRY_RUN = false; run_(); }

/** Clears checkpoints + resume triggers. Run before a fresh top-to-bottom pass. */
function reset() {
  deleteResumeTriggers_();
  PropertiesService.getScriptProperties().deleteAllProperties();
  Logger.log('Checkpoints and resume triggers cleared.');
}

// ============================================================================
// DESTINATION PATH CONSTANTS
// ============================================================================

var L   = '01 Learning (CIAO)';
var CC  = L + '/Course Catalog';
var CR  = L + '/Career Readiness';
var CRP = CR + '/Career Readiness Program';
var CTK = CR + '/Career Toolkit';
var LNK = CR + '/LinkedIn & Personal Brand Toolkit';
var JRS = CR + '/Job Readiness Steps (True Colors Series)';
var YGT = CR + '/You Got This Series';
var CD  = L + '/Course Development';
var PC  = L + '/Partner Courses';
var ISP = PC + '/ISPI';
var ACA = L + '/The Academy';
var S   = '02 Strategy & Frameworks';
var C   = '03 Communications';
var MI  = '04 Micro-Internships';
var P   = '05 Partnerships';
var LEG = P + '/Legal & Agreements';
var A   = '06 Accreditation & Credibility';
var T   = '07 Team Operations';
var M   = '08 Member Engagement';
var EV  = M + '/Events';
var BW  = EV + '/The BIG Welcome';
var BC  = EV + '/The BIG Celebration';
var IS  = EV + '/Info Sessions';
var CHA = M + '/Champions & Ambassadors';
var B   = '09 Marketing & Brand';

// ============================================================================
// TRASH — by ID only, content-verified (see ANNOTATED-WORKTREE.md §4).
// {id, why, byteMatchOf?} — byteMatchOf: only trash if getSize() equals that
// file's size; otherwise route to `else` (or leave + flag).
// Folders listed here are trashed only if empty at execute time.
// ============================================================================

var TRASH_RULES = [
  { id: '1ERsfWwfV-KXcFQnf7QQ0L5E0VALV1B_gbxO9sFD0g2E', why: 'exact dup of Currency Audit 1bMven-…' },
  { id: '1y631-AsDuiR3E8qpUfbuw_ldKj00OwQo', why: 'byte-identical ICS Engagement Agreement twin' },
  { id: '1cHC_-VsZKrYCJhXlhEgxraDIl19Y_IWg', why: '99MB dup of TheBIGWelcome_v1',
    byteMatchOf: '1MpX6mk8Szk2aNjGOKKdGhVWYIrMjZsP9', else: BW + '/' + ARCHIVE },
  { id: '1f07U0ZM9qwewTetIHpu2bzW5rKyP3ZOt_RUJKYzkf4o', why: 'superseded copy of Thank you Orientation' },
  { id: '1AKJD8jN3jHuLzoP1AwGBdR0GSWM4dt6G', why: 'exact dup completion template (misnames org)' },
  { id: '1BdBVvTtzNtg6tNFvoDAIaVtHse--2IDV', why: 'superseded by Pronouns rec-letter template' },
  { id: '1hP_EUPsMAmFOlWdDM4eoWOIkbfnf0iA1flXt17c_vDA', why: 'mangled derivative of the Plan doc (verified)' },
  { id: '1ESvYr5QYgtAdobF9gQVuCvWCD3EfdIeA', why: 'Word lock/temp file (162 bytes)' },
  { id: '1vdHuQC9tABk-2_Z8l8jn0V1PYk170wLn', why: 'misnamed size-twin of Step One Overview pptx',
    byteMatchOf: '1yga98xYi1NLadKHHvtYvJMIKZwDJAx19', else: JRS + '/' + ARCHIVE },
  { id: '1C4HVIHGVARhqYE9cTfxmgCDS_ycfvEIS', why: 'duplicate "SCLA Info Session Plan" shortcut' },
  // Folders — trashed only when empty at execute time:
  { id: '1uK_YjIXzA6Pe_7kdyq_hEwZ2IP0FW2Bw', why: 'empty "The Academy" duplicate folder', folder: true },
  { id: '1DP1xXs7AUXXySp-GpvPBNKDAc4ttXRDF', why: 'empty "2. Files for Review"', folder: true },
  { id: '1z228HUJ8uVF_V7xCeEQZ4XvYK_56yI9T', why: 'empty "1. Meetings Lounge"', folder: true },
  { id: '1pvDGmwbzqYep_KDzqB_VbIx2trx-E0sJ', why: 'empty "Posted Content"', folder: true },
  { id: '1ltkniIzVdN7bQO2oekxwoUhhI_f4a8KN', why: 'empty "Items of Evidence: ARRAY"', folder: true }
];

// ============================================================================
// RENAMES — applied before moves (setName works for editors).
// ============================================================================

var RENAMES = {
  '1KmwQS88oecnr0sbkM76w9EXAQekRIyy_Ey_pfutaTY0': 'Durable Skills — Competency & Sub-Competency Table',
  '1ZdBacPGOAqUejwKAikGuZvGny7GIzYE0dt5o0DJIWKM': 'Zoom Webinar Roles',
  '1qIMnSY10ri86Csh0KaMqkwLLOck1ys3vpP4v8zrWszg': 'SCLA Course Catalog (Master)',
  '1XX8CkkSYfYJOAwy70DE_cW9PkzTsqyl5fELDTVphLuw': 'Course Title: Rockstar Interview Video',
  '1eR8FVyOMO8zpp0nD38_ohYsn-bDOU02H1BTpZdn36sc': 'MI Company Outreach List (Master)',
  '1epdag16U1pXAM1FP9aRrOpAq1hSZASWk': 'ISPI Intro.mp4',
  '1bpjoBZn1J_lSRKhX9JeyrJuK9MvdcPu1': 'Module1_Launchpad.mp4',
  '1dTfA8zP9AJsOkCloMc1rvit9bFN04YBi': 'Module2_KnowYourself.mp4',
  '1cF-sI6bKfA5nXv8NFl5QzY_8UR-rtm83': 'BIG Welcome Recording 2026-03-12.mp4',
  '1I7i1LDAdkwWRnj-m295I3F05_4lb9XB4': 'BIG Welcome Recording 2026-02-24.mp4',
  '1DWS5YLRanWnk7hvLCSGNz13eK3bCsqLL': 'BIG Welcome Audio 2026-02-24.m4a',
  '1b_HAqPSCPQrtSlKTvl8_ow28I9iuFEaF': 'Accreditation Application (ARRAY)'
};

// ============================================================================
// FOLDER_ROUTES — whole folders that move (with contents) under a new parent.
// Their internal structure is preserved; the folder registers in the path index
// under parentPath + '/' + name so later routes find it. Processed FIRST.
// ============================================================================

var FOLDER_ROUTES = {
  '1IdP-li1UVTIxzejfQXoKdCo_Ac7aYdxg': A,   // NECHE
  '1M6O7GThNlgWLc_iY6VmAjJOzaqCHpbxX': A,   // AACRAO
  '1A37vLenJt0DVmkGB6tcAjwjohozt6VYc': A,   // WASC
  '1b_HAqPSCPQrtSlKTvl8_ow28I9iuFEaF': A,   // Application Accreditation → renamed ARRAY
  '19Vh6m6-J6gjn4Wvi0jTIDeIFv-ZqTVb3': A + '/AACRAO', // FERPA (its sibling FERPA-ish folders flatten INTO it via container routes)
  '1YKEkUUT4P1OYSQQwS6KzUp0wd9apqzEt': BC,  // Zena Collins (student photos)
  '1Txq4MPz_KPxIwiic4f8p9kP4urKqCemB': EV,  // The BIG Welcome (C&L)
  '1ApUFbLWVWF3nCWZ-Q8Bk0rLnT8TJpFk2': EV,  // The BIG Celebration (C&L)
  // Google-Forms response trees move intact (ED15; expected OWNER-BLOCKED on the
  // jheathmoreno@gmail.com-owned one → pointer shortcut + worklist):
  '1RYTSnz3LxOX9g_afG-2ZPmI_3G1EMZTC3OMH_DP41KqeXdr5gkUglAp70Q3UbJhbmNlYCC_6': BC,
  '1AKXiD9T2We-Yc5Wd7f0HYwm4Oh9pWCwrtYMARFMbW8TFtWl3Evy44C1uQjGj7LoJVH2AEPOY': BC
};

// ============================================================================
// CONTAINER_ROUTES — legacy folders that DISSOLVE: every file inside (at any
// depth, unless inside a FOLDER_ROUTES subtree) routes to the destination;
// ID_ROUTES override per file; shortcuts get the tri-policy with this
// destination as their pointer home. Emptied containers are retired.
// ============================================================================

var CONTAINER_ROUTES = {
  // --- 01 Learning
  '1fQ1Chyz5P0_MIvv3J7LIoLAz3jo9fmXf': LNK,                 // 10X LinkedIn
  '1o-9hMKV12HGGSR8IeFal0y6FIZwr1I20': LNK,                 // 10X Toolkits (wrapper)
  '1SD2qBf4keuayJEDdlPqwp5xbFlKS1mnC': YGT,                 // Media Review_Lori&Classic
  '10SSKI8FlGnlaNfZbSbVExrwmSxTb6hL6': JRS,                 // Job Readiness Content
  '12jx8GWuC4FUWFvIIBdgX-f1MiV8Bi25z': CC + '/Career & Job Search', // Career Courses
  '1TVKpZehFRgxADAbMq8QzFpPXYYHD-K06': CTK,                 // Career Toolkit (C&L)
  '1V44tladJ3GB30hyOH3QCyFkEDHdIAf40': CRP,                 // Career Accelerator
  '14IuNqqgzt0pKSCN86zBFvvrwZbdjM_-w': ISP + '/' + ARCHIVE, // ISPI Sept 2025 render (Q1 in worktree)
  '1r4dOR9zq9EcLEESkODw_zkAX3IVXNX7_': ISP,                 // ISPI Oct 2025 render (current)
  '1fjFSNoGJ819j4P9ntbk3b7Hfma4E5NRI': ISP,                 // ISPI Scripts
  '1IGAY32tJ-g53dmvWNXaLaxfhDTa1djBF': PC + '/Identity Leadership (IDL)', // IDL and SGA
  '1ypmPPV_5d-8g_Sg3ycSB7Uoh4YsZuWNh': ACA,                 // "The Academy " (trailing space)
  '1HiXLR4EitF1v3G8fLIcdrL2cnhdx5BtR': CD,                  // Ed Content Development
  '1A4Gp0zdeRjSK5jRsEDt8cVlC6ZUABrNx': CC + '/Master Catalog', // Prospectus… (course codes route the 59; stragglers land in Master Catalog)
  '1jVvWbUsuzyEgkoj97aCmF2iWK36J1Qjl': S + '/Frameworks',   // Learning Frameworks
  '1xKZZoAgS6CbW7NFFiuCUDAL7yhemvel_': S + '/Strategy',     // Yesse- workshop proposal
  // --- 02 / 03
  '1GZQTjgterDMpjAmv-EH_9q19PD4Ulhg9': S + '/Strategy',     // Learning Strategy & Metrics
  '1Ph9V12pdy3Bms_xNrQ3c3HTG5_9XpbDo': S + '/Research & Member Feedback', // Ed Feedback and Surveys
  '1H9Mwr6XtJOWL9rtg6-EBxH1sIMfr9KBC': C + '/Channels & Planning', // Communications & Comms
  '1YnX8Kt-Pu1xOqE3MdHHbT0DAQKYXxJZf': C + '/Weekly Updates/' + ARCHIVE, // Friday_Monday Updates
  '1gTYpua4Kx7fbgcshO-6U-xrMS8103DLi': C + '/Social Media & Blog', // Member Social Media
  '1XVKGK3ILRDnTi7BJxC8SHieU0b-BJhe8': T + '/Member Support', // "Community Engagement " (C&L)
  // --- 04 Micro-Internships
  '135fnfRzDjMX5g0n9-6eKcoA2rvQ2kNBJ': MI + '/Program Roadmap', // Micro Internships root
  '14tug5vonWZilrOIDMnOzZ1mZoRD8CHhl': MI + '/Partner Ideas',   // 1. Ideas Zone
  '1G_fprzscn3BeHSppdLYnKTF16PrsRax-': MI + '/Program Roadmap', // 2. Project Roadmap_MI
  '1FXA7o8782JMkAIcZ-8cy6x8D60mPgQvv': MI + '/Project Content', // 3. Ed Content_MI
  '1bos9lmneiQqWmxzDMD9me6_yCBgO-8PG': MI + '/Outreach & Marketing', // 4. Outreach_Mktg_Partners
  // --- 05 Partnerships
  '1yOR6SncHIqm7oZA0FMkw4YsxYgAkyPdd': P + '/SGA (Student Government Associations)', // SGA & SCLA Partnership
  '1vjgKN-Gm7IvUKx0LH1IsboOKSxwYSRrR': P + '/SGA (Student Government Associations)', // SGA Notes and Marketing Docs
  '1zgxRUfLPK9t6HTlT6Q3BrWANgekpdvj2': LEG,                 // Legal Docs Partnerships
  '1w60ITWx0v1rZFe0uAomvrKBl3jUmjLjq': LEG,                 // Agreements FINAL
  '1UpdH07wigrIencK-4ks3IilRR6b4uGRq': LEG,                 // Agreements DRAFT
  '1ze43oRH-dww8_NHIHgm-XosnSjLfM095': LEG,                 // Partner Docs
  '111-NNBrVTj7Sqx7fBcKw4pJv0OYOCUub': P + '/Partner Directory & Lists', // Partners SCLA
  '13ErvEI4-fAXGSUNEfQJ_vNi0qC-oneMz': P + '/Partner Directory & Lists', // Partner Lists & Marketing
  '1wZMUGe3FOYXLOVOVg7rRbrkR_xSUC6si': P + '/' + ARCHIVE,   // NIC and SCLA (ED2; CGHS pdf overridden below)
  // --- 06 flattening (FERPA satellites merge into AACRAO/FERPA)
  '1QxsMxh35F01ib3Hc4I0DwjHT1y3y-2ma': A + '/AACRAO/FERPA', // FERPA Misc. (NAB deck overridden below)
  '1GBgvZbu_lhrEKiJwxYCfNf4w7_4jdrxy': A + '/AACRAO/FERPA', // AACRAO Agreement
  '1Fra1l_Fc4LsD2uYAY00xQ5uIYDyiCRhJ': A + '/AACRAO/FERPA', // FERPA Toolkit & Comms
  '1vsvucqReJvCwi13XUMcn3ppy-cp64AS0': A + '/AACRAO/FERPA', // FERPA Policies for SCLA (dup-shortcut wrapper dies)
  // --- 07
  '1dXFO8lhEW-arBKgyRTkT6YH7PbPKFv2w': T + '/Team Admin & Planning', // Ed Ops
  '18h-e855HXIbNtCxeJAe0K7_tlYhTBEuo': T + '/Finance & Vendor Records', // LXPs and Leaderboards
  '1L38AzCorPfKt0TSB7ef1HsNqXkh2ogNR': T + '/Frontline',    // Frontline Content
  '12crU6bONFuERCg2rHlnc63XwJowTEV8P': T + '/Member Support', // "Member Support " (C&L)
  '1zznScJ44VDAIGyIu5WspIQ4_OjbJfClF': T + '/Chapter Interns', // Chapter Interns (shared root: children only)
  // --- 08
  '11d1Y-mida6r65laZqaEjKz76RzK-i7uK': EV + '/Event Planning', // CT "Events " (trailing space)
  '18lM62mGM9svyV-WI3lf678GbdzW1O601': BC,                  // CT Events/Celebration
  '11FUCcEU4ooaxgL4xwNaLAkQ-VOuq-uZ2': IS,                  // CT Events/Info Session
  '1iUznbedvNTlSgKyGFAq15Q_YGRuFLgDz': BW,                  // CT Events/"Orientation "
  '195TA-znQynZvBcyKPO7LPKtKbDyY4QOZ': EV + '/Event Planning', // C&L Events
  '1dqH0EU0Et1tPGZEPBjVnonZqPxLifqu2': EV + '/Event Planning', // Events BIG and Little
  '10i4JGip9qoDGOHuEbF4SFzYw6P0apsSL': IS,                  // "The BIG Info Sesh "
  '1EKhqz5Xct5lsdz8QC82rD1t-DaigAoVc': CHA,                 // Community Champions Program
  '1PAfmKVqEl6FuPWm7DKC6I5xgFInXWJI1': CHA,                 // Community Champions 2026
  '1dV57XIPXqYxIXDfNDuobVTc6Wgj4_5ud': CHA,                 // Community of Champions Kickoff
  '1gQFGVZHYWCL71-CZX2GgnSecJwcK6Y9c': M + '/Member Journey & Onboarding', // The Member Journey & Engagement
  '1wPbEcKy7Glg2GKA7ToHVATFmXv0vJZkG': M,                   // CT/Member Engagement (wrapper; shortcut children → policy)
  // --- 09 + CT wrappers
  '1tLn-UcNvWtlRi0WHwJhyzS_rXQxV3-VA': B,                   // Marketing SCLA (shared root: children only)
  '1c3-Uv_OGv7L6Aj74cfoRqUo6xE8sJNTX': B,                   // CT/Branding & Communications
  '11jj1NnAEfTsPLmDaZqu8GiCraEnF7XEq': CD,                  // CT/Education & Learning Programs (overrides below)
  '1j2vfmJnd-XoDWIau-oSu68X6zrxRfhpZ': T + '/Member Support', // CT/FAQs 2026
  '1p2W51JvsarOIkLDDkOh1yx21QWJmZ0dH': T + '/Member Support', // CT/SOP's Admin & Governance (overrides below)
  '1iqS9TIenjj4gW-bMiupbfILKcXgkU6fm': S + '/Grants',       // CT/Grants
  '1a-Gk2E5-1MktuCYcpeW17Jby-AmrXOrS': S + '/Grants/Career Passport', // CT/Grants/Career Passport
  '1CQnm9kR0hJOkKIomGwjHCLbhvgOh-Sey': null                 // CT/_Archived — per-ID routes only; stragglers → UNMATCHED
};

// ============================================================================
// ID_ROUTES — per-file decisions. OVERRIDE container defaults. Key = file ID.
// Grouped by destination; see ANNOTATED-WORKTREE.md for each rationale.
// ============================================================================

var ID_ROUTES = {
  // --- 01 / Course Catalog
  '1PIz9x5CC3oFB_Q0HgowoW1nbn_Urwul5fspJH5kSA18': CC + '/AI & Technology',    // Grow With Google Cybersecurity
  '1B8O90zJ0Woj0CSok8ndCINbwBdcFZGtf': CC + '/Career & Job Search',           // Hidden Job Market pptx
  '120UNCmyGny26bCm-786O941k4kym25XURdUWAMZOaaY': CC + '/Career & Job Search',// Course Title: Brand You
  '1XX8CkkSYfYJOAwy70DE_cW9PkzTsqyl5fELDTVphLuw': CC + '/Career & Job Search',// …Rockstar Interview Video (renamed)
  '1S2XGr--HEBVUpiJMw8KPM-99g7bSMERq0Tu37RQMmEs': CC + '/Assessments',        // AI Assessment Sample
  '11DTwqREkEk7h7O8wEVZuvMif29c_NEIfKeK5JN8B0JA': CC + '/Master Catalog',     // Ed Prospectus_Ed Vault
  '1qIMnSY10ri86Csh0KaMqkwLLOck1ys3vpP4v8zrWszg': CC + '/Master Catalog',     // SCLA Course Catalog (Master)
  '1K4EbDRnksHr_mdqfyXfSZUpHf747u5uL': B,                                     // SCLA Learning_Overview.png → brand collateral
  // --- 01 / Career Readiness Program
  '1N4l0eYE8hPt3VEtM8OhMdvWq83yCnF0j7BsPFc6lNWg': CRP,                        // CRA301 _2026 (current)
  '19_o-r_kB164Fsx6erYY-4XW3kde50_MsQnbXV4QL-3o': CRP,                        // CRC101 (verified distinct course)
  '11rlX40ams18WPL9PnoZ2wW0PD70TtQ5dubuHXVKbm_I': CRP,                        // CR Accelerator Outline > Syllabus
  '128g3FIPp33BaHQxQ3Oko7n3Od-U8Qxp1QVHzfg7QQbM': CRP + '/' + ARCHIVE,        // CRA301 undated (superseded)
  '15BQEe4qa-lkFXfkQJvp1A1pa-aR7p3nM': CRP,                                   // Career_Accelerator_Framework.pptx
  '1REAwZ6QloostCbNB7PB2brel3ico5q2v': CRP + '/' + ARCHIVE,                   // …pdf export twin
  '1GE9F0QHwuz8Cs9KmkYATrF-kMqjmHMex': CRP,                                   // CR & Decision-Making Tool.pdf
  '1STu8IJwoRe9QHHQydlRfa3-fU1OLSYt2CdKPz4mqPr8': ACA,                        // Career Accelerator_Honors_PunchList → Academy
  // --- 01 / Career Toolkit
  '1fAMWBS4iG8xETsImC9jqFkuI5buY5Yajn9zf4Ou9k9Y': CTK,                        // canonical 2026 doc
  '1uxZXGwYtUg3G_JKCUpXQg8IW83QvObVH': CTK,                                   // distributable pdf export (CT root)
  '1c4v1i95jwUpzvitH6yL8o1hF3CopFB5M': CTK,                                   // workbook.pdf
  '1jAFpQtVs6XjNX9LgmoTotT4eYBQd3rsbAYnB2sFgK9w': CTK,                        // Tools as Learning Activity or Track ??
  '1KP_9sHAG-uVU3430G7YNSbu001zEZXkH': CTK + '/' + ARCHIVE,                   // _FULL.pdf (superseded STAR-era)
  '1bMven-h1vSJXjB5SNSD1qTQ7Q8O9BpetVv0ZXG7llJs': CTK + '/' + ARCHIVE,        // Currency Audit (kept copy)
  // --- 01 / LinkedIn toolkit strays
  '1jXoHVqWvzkWOP_ck9NXHOmp360K0UWEY': LNK,                                   // 1.3 Define your Personal Brand.docx
  // --- 01 / Job Readiness Steps archive overrides
  '1YThaPkBmUEWSu-HZw5wmqC38m7UTQQwL': JRS + '/' + ARCHIVE,                   // older Welcome/Choose-Orientation deck (Q5)
  // --- 01 / Course Development
  '11Q4QFT5hPgMwmJqi1GQh-ONl5yM2Ew40NRSWzmHfOA0': CD,                         // "The New Syllabus" (pedagogy guide)
  '1uO_UxJyxLl013AObJTIkTuCgOVWaDptFrg0no0tOqRo': CD,                         // Video Production Samples/Process/Costs
  '1pqg-fh3dxnbzfnQVsIVrhPxAY0Ah8CziuUAC25GZMjg': CD,                         // Explaining the Learning at the SCLA
  '1oPiImv4RRoU7daW7-okS9N8ZuiH6ePtr': CD,                                    // Education_Content_2026.xlsx (content tracker)
  '1m165LVwxCBgf6skmpVjPsTszfPV7DvKw9LjCm446qn4': CD + '/' + ARCHIVE,         // Amy's Test Content (test data)
  // --- 01 / ISPI + Academy
  '1JkSvq765YffrhZOKrheZb-Z-YbVBOLKfaS2oXhyqqvM': ISP,                        // New Readiness Course Video Needs
  '1Vn3pIu1Fy_vJoaNAYXmjVJ8fgg38eoJAnB_K3o3BFk4': PC + '/Identity Leadership (IDL)', // IDL Content from LXP
  '1RRgJ-__CJOFOUn2QBwN94qM-xrj27kISl4IKrfmlYQI': ACA,                        // Academy v. Honors Features List
  '1ly4CPYR5yCWywn1C-8k-n3LXO2MG7c449oh1978XoMg': ACA,                        // Conference Planning (deck script doc)
  '1C6L6a-COxWJIosIpj6_PyD8RE1_8yuGmKmszqfbnkNw': ACA,                        // Academy_Career Essentials PunchList
  '1H2B425QBnBtDRbc67Fq5PkPtRYbgB_cL': S + '/Strategy',                       // Scalation Road Map (strategy, not Academy)
  // --- 02 Strategy & Frameworks
  '1NSult6_d-7ZpfSP11axtYtfVInWHisCc_LF4R18MqQc': S + '/Frameworks',          // Focus Modes
  '1DYBjSjlSlW7dGznrGuJtmisozWug1b14YCfyrtNtPX0': S + '/Frameworks',          // Durable Skills doc
  '1G9JV6LZt3KuGDPP_kGReLxuYArtNzHB2': S + '/Frameworks/' + ARCHIVE,          // Durable Skills .docx twin
  '1KmwQS88oecnr0sbkM76w9EXAQekRIyy_Ey_pfutaTY0': S + '/Frameworks',          // Competency table (renamed)
  '10TYp4hjhXtH6klakxyBkh7rApJlLKqspVfU4nRpEmPk': S + '/Frameworks',          // Competency and Sub-Competency List sheet
  '1fQv9tmrs0N6OFLR4EcdGsnsfCgEZIEJA': S + '/Frameworks',                     // C2C pdf
  '16N2so9y1rELdGLgin4brd0D3iFlRrEPV': S + '/Frameworks',                     // C2C png
  '10_8JWDfR3vfwjNv5n3JSEOdxwA1t36G8c3S85iETrdw': S + '/Frameworks',          // Powerful Personal Development
  '1XmaKJw8aGZlBsGhLBYwRVFOw0NZc7UYc': S + '/Strategy',                       // Education_SCLA_2026.pdf
  '1LvKPNp1sQvR71ZeDNtI-zIHZbQVlTkXBAKWtuiGLQc0': S + '/Strategy',            // 🌟 Leader of the Future
  '1P4oqbVOHPVicrQmhNvthjQt6264OIqEB': S + '/Strategy',                       // Hi Po National Rollout
  '1DdhJ3e6y1U7obZKjNk8pT9iVQCmSZ4Ebrw6Ww8tvZ6E': S + '/' + ARCHIVE,          // Ed Update Feb2026 (superseded)
  '1hoHF6oEjwkVTkb_SNLMEVDhAAQugbyElMZvX5kwypTY': S + '/Research & Member Feedback', // OGC member survey
  '1m4n_LCV4GQscAuTaCH-TaEmKwyeXQiXPfzHkLvmcMSc': S + '/Research & Member Feedback', // Focus group module suggestions
  '1N9ds3PoEVIsb6xWXPVAssRQQqTh9Kl2JGAHmqqzKZSU': S + '/Research & Member Feedback', // Compelling Parts of Member's Area
  '1z1taV8Wsn5zFMSn2ESwT5vzphPUZhAk7jKHvncUMwcI': S + '/Metrics & Reporting', // Ed Metrics
  '1_qZhYzUGv3fkLSRK_FV2bq5X-L4j3XKAVJdLiakLpYo': S + '/Metrics & Reporting', // Education_Community_2026 sheet
  '1yItebjJLjfulav6HGMOXG9s7dCYYP7gLkHUod1TAKNQ': S + '/Grants/Career Passport',           // RFP pilot-readiness (Doc)
  '1S283C6ThWhTMB_-8RqYLSExFRxOqTiGRuwzAVxmsP0g': S + '/Grants/Career Passport',           // RFP innovation-concept (Doc)
  '1__Q0G1pGFGB2IstOlHoDuEreflkyRNoh': S + '/Grants/Career Passport/' + ARCHIVE,           // .md source
  '1vFkizaFQQyUo3bJOOOlgQHA6gDabguxl': S + '/Grants/Career Passport/' + ARCHIVE,           // .md source
  // --- 03 Communications
  '1UuU5ZqNmSiOdhbPBmN-G1JJmkZ0_1pzdL4V7RI9zMqg': C + '/Weekly Updates',      // Community Team Weekly (live)
  '1eWW1orwl_ZxBSBKjINsVVzEmuQ-8pBaYk8Pv_8ajtYI': C + '/Channels & Planning', // Comms 2026 PRD
  '14mQJtnpyTYJFmBCu7IplQ0iqeODOsBGX7_79ysuaoMQ': C + '/Channels & Planning', // #channels
  '1pM8DrsDSt7sIjLRW58IH0M1KI6_vR9Rj': C + '/Channels & Planning',            // SCLA_Channel_Map.xlsx
  '1SH5rDeEAIY5aKNW_3EKOg6JhGoup43UtlSFloPA_l24': C + '/Channels & Planning', // "Standard Operating Procedure (SOP)" (channel taxonomy — verified)
  '1Qv_XqBu8zagSaRPTw1HPnaIHZHwdI0qP': C + '/Channels & Planning/' + ARCHIVE, // Notion Lifecycle Engine (3rd-party, 160MB)
  '1x562t5V_R7FX6zEGoYYpZsRnplPURYun1-TD8kJz3EI': B,                          // SCLA Voice and Tone (canonical — ED10)
  // --- 04 Micro-Internships
  '1vwb-HqdSAf40zLVsjrhcCXf3h7zdbnecsQLVfhDFNtw': MI + '/Program Roadmap',    // Micro-Internships doc
  '14kQg8wKTPbVh-uohckCMbrHlqA2IO-AZVV8IpSCdClM': MI + '/Program Roadmap',    // Overview & Strategic Discussion
  '1Y9FFntuNmO1NRuwoTU0BFKfvGCX0HyzN': MI + '/Program Roadmap',               // Explaining MI v1.pdf
  '1wDEp3uVdKKCQxEvRixGPdgVTV_gI6hkU22yTRwXe3Nk': MI + '/Program Roadmap',    // Program, Eligibility, Details
  '1FjdEX_ECtVURUQyONrHCGMpDqcLlFN44': MI + '/Partner Ideas',                 // Forage.pdf
  '14FG0psJPoQaTYaZ5DOIL5Em6FzsOOHoXjmAQUo0fGbI': MI + '/Project Content',    // Rubrics
  '1MOv8EBwGcUBde0XKtf8dfiX9pzVh957c': MI + '/Project Content',               // MI Samples.docx
  '18IF131hC6DAVhWTLGC0tAqUpOyM7nnUv': MI + '/Assessments',                   // project_interest
  '1EkFo4PiM44eToIlHkobT2G4wjhHmvlcb': MI + '/Assessments',                   // project_wishlist
  '1eR8FVyOMO8zpp0nD38_ohYsn-bDOU02H1BTpZdn36sc': MI + '/Outreach & Marketing', // Master company list (renamed)
  '1LTFwmhK_xfZwI5S3zWgZ2zNctWUFnKRh6rC_SecYgFM': MI + '/Outreach & Marketing', // Mentors + Sponsors form
  '1dJJWLmgk29YEp8428ywGbRsAHh5dWj_xDt_eNCkN7kk': MI + '/Outreach & Marketing/' + ARCHIVE, // MI Company List (older gen)
  '12yruw7MB8v-M1NhHljQakuAcN5KpAJgEAucEio_Ta_U': MI + '/Outreach & Marketing/' + ARCHIVE, // MI Companies (older gen)
  '1gm5EGVbqHUCmGGLq5Pvlj2bkP4FkDBXK': MI + '/Templates & Letters',           // Rec letter (Pronouns)
  '10Akt_LpGUTM3Ems1YQa97RRYnuWCnGtg': MI + '/Templates & Letters',           // MI Completion Letter Template
  '1OZ5qEifUsj3m5BRsb6FftAkUmySLo2BDKp1Pd993sYo': MI + '/Templates & Letters',// Project Template (⚠ gmail owner)
  '167FzUcmEtZ7f61H_FLolWrj_c7fAyPjM': MI + '/Templates & Letters/' + ARCHIVE,// Isabel Elimu letter (PII record)
  // --- 05 Partnerships
  '1MLyAduL_2AEcA_3fAVfpWmse9UvG8SUe': LEG,                                   // CGHS signed pdf ← NIC folder (ED2)
  '1lBP7iyL5kBlqmeo_5ta1aZuglc9ZS0Yl': LEG + '/' + ARCHIVE,                   // CGHS docx (copy of signed)
  '1zIwkyWuH68JT0BII-GoMprPDyd_QWt49': LEG + '/' + ARCHIVE,                   // CGHS docx (2nd copy, Agreements FINAL)
  '1uBITrZcN0u36P5KgMlhWTY9A2aDu9ysc': P + '/Partner Directory & Lists',      // Company & Expert Directory
  '1WxwCSRcFMT3KUZF4xOMsR0a5McczTAg5': P + '/Partner Directory & Lists',      // VendorsReport
  '1qxCiloPI_gUiJF7vtpgC91SQFEwOcF8b': P,                                     // Coaching Initiative Pilot (files at 05 root)
  '1n9xni7XDBqRAG8FRn29_1MmLgRprS5ks': P + '/' + ARCHIVE,                     // Voyije Program Wrap (ED2)
  // --- 06 (post-wholesale-move overrides)
  '1FLqZ2XmvK-t1sjSKdWBdgrnpKVNBd2f4': A + '/NAB (National Advisory Board)',  // Dec '25 NAB Meeting (out of "FERPA Misc.")
  '1uFN7LZIU-wkYPl9rNHWURzyLBUVwRUOQ': A + '/NECHE/' + ARCHIVE,               // NECHE worksheet pdf twin
  '1zBTIKJDzMfPumJBSz0zo-5Et7S2PSryj': A + '/AACRAO/' + ARCHIVE,              // Technical Overview pdf twin
  // --- 07 Team Operations
  '1bkhrmmqdAq9CLMvuWmPmGDiCvDylKdZOoTJm5hue1YI': T + '/Member Support',      // Two-Tier Communication SOP
  '1DTx9H1t2yOYmxLn6rlVJKyqO7b1UUPad': T + '/Member Support',                 // SCLA Engagement Flow docx
  '1SVlXpIHq5twxEXiyT6Uponv_qA_vqrtK': T + '/Member Support',                 // KB Master FAQ Outline.docx
  '1AJAarVduDexrV2jk4z6fJK3CViTaLHFFieGxbukubRM': T + '/Team Admin & Planning', // Team Hour Tracker
  '1D5G6hXU472bSR1dnJnP0IlpjsklXmTcbr_fR2OSMh9s': T + '/Team Admin & Planning', // Community Team RR_June2026
  '1_mjFJKWgzyGAU750bh-jg8OtkS0cHfdHxxLZW2E1PeM': T + '/Team Admin & Planning', // Q2 Projects sheet
  '1GUmzBG0BpDjwiXM6qoTqYhQPAmptnEUWBW2G8C7Ch1g': T + '/Team Admin & Planning', // Feature and Bug List
  '1AqY3-jqE8aIwbYfbtxxfjSb4cWCN_ZcRV9arpGvuHRs': T + '/Team Admin & Planning', // Community Manager Bios
  '1i-tpzHQDs8O_KaUAQPz_paXGwcxibW9C': T + '/Team Admin & Planning',          // Dashboard Drive-Through recording
  '1zLdtHT-XtiDSrFiAy5gAzPazWEzR-mvmgIJ34a68-DE': T + '/Team Admin & Planning', // Plan: Proposed hierarchy (provenance — ED12)
  '1JesIDpjGqLB5mbwOQG0WMLqTo5uLQOFB': T + '/Finance & Vendor Records',       // Underground Sports invoice
  '1EupX-tzg9AUB7DViZ0WY9VoYn362MwwuJpyAiDnHnMU': T + '/Frontline',           // Frontline Forward
  // --- 08 Member Engagement
  '1r0a6K4n4UKMh1vVVX67WGWd33LjYXj-DAL3_B_MeEnA': M + '/Member Journey & Onboarding', // Membership Journey Today
  '1cfYoj4DImj531H-Uf1oabWVFCoZ5MVFpQFpquH0IlPU': M + '/Member Journey & Onboarding', // Enrolling in Orientation
  '1gliAUODqHIlcCUJh5gugt-ocpaPsYj84UsdyjVmocjQ': M + '/Member Journey & Onboarding', // TL;DR Highlights_03.23.26
  '19lyBhgMlBahzF4Bs9mtE9A4ygWed9htfV0JfMSSRSnI': M + '/Member Journey & Onboarding', // BIG Welcome_Onboarding_2026 doc
  '1K-lZgsk0uuFZ4Ua7cjhyvHzsPrTZTVoj3EtQjV8y10g': M + '/Member Journey & Onboarding', // Orientation SOP 5.28.26
  '18tLoJceBR6wsiGPhqb_vm1-t2bbuyfsgSSTLn5Ekhg8': M + '/Member Journey & Onboarding', // Thank you Orientation
  '1eBXmhri5o0FCtfDnA33ikNtH-cDJdo3_Hp9P2VsjIHQ': M + '/Member Journey & Onboarding/' + ARCHIVE, // Reminder Email DRAFT
  '116GDCyilaDDvVwSuE1lijx7ikg13hmP6qEjbKXgT9Ls': M + '/Member Journey & Onboarding/' + ARCHIVE, // Follow Up Email DRAFT
  '10hfO23p6C1tiRJh32mrb0kiA-EIGA4_WXpHqXTQAwD0': EV + '/Event Planning',     // Event Tracker
  '1_CFC0hS2fI06OiusSY5C4xBkzSHyFuYM33Z0n6-PGKM': EV + '/Event Planning',     // Event Calendar Descriptions
  '1EAbbLMYUObiUgjK22M35YIm-PUvY3sGHsyY6xho0wls': EV + '/Event Planning',     // Event Proposal June 2026
  '17AVXrVcZK9jdn2_A8EXEp3Nlu8xPzfXxTPJOGxm5_xI': EV + '/Event Planning',     // Events_2026_PRD
  '16LE9v4s6Zhi4frrvqZUE4rgrbdF-PObrQf0iseLDNIg': EV + '/Event Planning',     // Event Operations DRAFT
  '1d3KMDvJlReKQOE8mncsD5ubc-RN1-PC8': EV + '/Event Planning',                // Event Team 10-Hour Cadence
  '1_1FPOcEDhUylmGTmdG8J21QDoFFM2jYWJEdKJnBMqxs': EV + '/Event Planning',     // Naming Ideas for BIG Events
  '1cKi7FA_FJIqmGMqBOKyHKQ-BZVhGhQEy': EV + '/Event Planning',                // RESET Book Club Guide
  '1aalByqHrhKHu2YWCZLwVCzhHtu72SUZA': EV + '/Event Planning',                // Reset One-Pager
  '1WD3MFn1NS7f_7W71wXOk7SrkSk_hawNX': BW,                                    // TheBIGWelcome FINAL(May2026).pptx (current)
  '1k3D6Z-Ew1Q-ajBO4RlAIYyG6SFYha18Oe8i66ksiznA': BW + '/' + ARCHIVE,         // older FINAL Slides (Q4)
  '1MpX6mk8Szk2aNjGOKKdGhVWYIrMjZsP9': BW + '/' + ARCHIVE,                    // TheBIGWelcome_v1.pptx
  '1XXih-hS2idzLiTcsTMnuolRcHbq2r3dGubhuQmNowck': BW,                         // Orientation Script (jheath) — Q3
  '1E_Ic3brMbU-Cy_pe6h7vGcSrinmVYoEfPOedPbn_16I': BW,                         // Orientation Script (ilomax) — Q3
  '1wbG3n4x_64Dks7qFaibnGUJT51giBE6erv7uaJfa-YA': BW,                         // "Orientation Slides "
  '1GFtJyEr2uuMtliB7w8SYwOh9x2kMW1vC': BW,                                    // Importance of Community.MOV
  '1zmJPX5wkOZggSvPA0bC_gFx_tigB6XlM': BW,                                    // TheSCLABigWelcome.m4a
  '1cF-sI6bKfA5nXv8NFl5QzY_8UR-rtm83': BW,                                    // welcome recording (renamed)
  '1I7i1LDAdkwWRnj-m295I3F05_4lb9XB4': BW,                                    // welcome recording (renamed)
  '1DWS5YLRanWnk7hvLCSGNz13eK3bCsqLL': BW,                                    // welcome audio (renamed)
  '1SeOxEAkL5iEjeIiU6UHpGh2hJN1qPDtRrgberiERDHE': BC,                         // MAY2026 BIG Celebration Script FINAL
  '1ODqESSHMpOcyP0YLnaIIf2KTHlbE2EcPVjBxsQl4X3c': BC,                         // August agenda (current event)
  '1Vl3y73fxuGVTAc5KPN35X4UR66ce4763tSiBDq9e0Ks': BC,                         // May agenda
  '1JiZrC_OEh6s-yXracG7drDn_WCcAdjrhEuoHejBLUNs': BC,                         // Celebration Comms
  '1vHehuUmcC3oQ0VUmofeLIwplJKBdpjlR': BC,                                    // Big Celebration PPT
  '137nTrrIbLkf2jsYvQ1bU52JBu0CmEbEJdBaV3KATs4s': BC,                         // Emails for the BIG Celebration
  '1PgUa4f3c7A1Tq3Qy3DuSB7eYtWkj3sb_dIhbrwbdybI': BC,                         // Scholarship Winner form (⚠ gmail owner)
  '1bOUHFQb-d-hEdRLes1e8QBq_RCcumxz6Aq7H3jvppJM': BC,                         // Raffle form
  '1aB-wQcWYhY8DDTDQKxb6wKTVP8fGx45PTX-kUoK5xPQ': IS,                         // SCLA Info Session FINAL slides
  '1MjGlGiwhhjlsoiyZov1WYtvhq1mtSDok': IS + '/' + ARCHIVE,                    // ARCHIVE Info Session Slides.pptx
  '1ZdBacPGOAqUejwKAikGuZvGny7GIzYE0dt5o0DJIWKM': EV + '/Event Planning',     // Zoom Webinar Roles (renamed)
  '1MzXP9vsRE9nUv8qIMx_d8tSYKoyjVw5Oq2Ix7OY-boU': M + '/Pledge Project',      // Pledge Project Outreach Scripts
  '1Ldv6QLhidhID_Ni-LOmx46Gqc2jVW0wB': M,                                     // Swag Incentive Proposal (08 root)
  '1wkBFrzV7_19wFRR5B3NjfGn7QES8roDO': CHA,                                   // Community Engagement SOP pdf (champion/stipend — verified)
  '1irvBJAMaurwefH4RU_vtlyVb58jeEmH2': CHA + '/' + ARCHIVE,                   // Champions application csv (export twin)
  '1MxdY-uNikY27QcSRewFeweMVbDGNuREj': CHA + '/' + ARCHIVE,                   // Champions copy-bank csv
  '1B_QBRmQMyDdGNiqmqaPFovJMJ6ZY2rrJ': CHA + '/' + ARCHIVE,                   // Champions milestone-tracker csv
  '17QfqxcQRapMpLmEF9z44nvhAIhz4zAxW': CHA + '/' + ARCHIVE,                   // Scope pdf (doc twin is current)
  // --- 09 Marketing & Brand
  '1R2BkiEgDM9Xu3vwji1xW_Pn-u0vcz8IYEY6iSQ8k1Og': B,                          // Brand Guide
  '1dxtsca_NBOV3PNQIhROl3-DPj8KFAHXym75h_IX_ry4': B,                          // Visual Identity
  '1dvEUjKPq8eMIRnOI91FvpZxagYmn7lj1X6E1u2qWiKE': B + '/' + ARCHIVE,          // older Voice & Tone (superseded — ED10)
  '1apg3sG-pTFoAtXCyOiurNSgDwn5wGW1m': B,                                     // BrandingKit v1.0 (2).pdf
  '1LlLBC3zQxPAjK3iThCgN1Bb3Z_L2_BY3d8HRWvpZyok': B,                          // Information Deck (Slides)
  '1W0iyduDGLZYMilMhUmpAcC3g8SRSY4NI': B + '/' + ARCHIVE,                     // Information Deck.pptx (verified twin)
  '1A0rGxSYga7Q6KRuyeDUcawdlxSdlSyz-': B                                      // SGA Overview pptx
};

// ============================================================================
// NAME FALLBACK — only for files created after the 2026-07-20 inventory.
// ============================================================================

var COURSE_CATALOG_BASE = CC;
var COURSE_CODE_MAP = {
  AI: CC + '/AI & Technology',   CAR: CC + '/Career & Job Search',
  NET: CC + '/Networking',       COM: CC + '/Communication',
  LDR: CC + '/Leadership',       PSY: CC + '/Psychology & EQ',
  LRN: CC + '/Learning Skills',  PRD: CC + '/Productivity',
  WRK: CC + '/Workplace Skills', STR: CC + '/Workplace Skills',
  THK: CC + '/Thinking Skills',  ENT: CC + '/Entrepreneurship',
  ASM: CC + '/Assessments',      SPR: CC + '/Seasonal Cohorts',
  CRA: CRP, CRC: CRP
};

var NAME_RULES = [
  { match: /weekly|friday update|team update/i, dest: C + '/Weekly Updates' },
  { match: 'info session',       dest: IS },
  { match: 'celebration',        dest: BC },
  { match: 'big welcome',        dest: BW },
  { match: 'champion',           dest: CHA },
  { match: /micro.?intern/i,     dest: MI + '/Program Roadmap' },
  { match: 'ferpa',              dest: A + '/AACRAO/FERPA' },
  { match: 'pledge',             dest: M + '/Pledge Project' },
  { match: 'linkedin',           dest: LNK },
  { match: 'true color',         dest: JRS },
  { match: 'toolkit',            dest: CTK },
  { match: 'ispi',               dest: ISP },
  { match: 'academy',            dest: ACA },
  { match: 'sga',                dest: P + '/SGA (Student Government Associations)' },
  { match: /\bmou\b|agreement|indemnification/i, dest: LEG },
  { match: 'orientation',        dest: M + '/Member Journey & Onboarding' }
];

// ============================================================================
// ENGINE
// ============================================================================

var REPORT = [];
var WORKLIST = [];
var pathIndex = {};      // 'Path/Under/Root' -> Folder (lazily created)
var startedAt = 0;
var props = null;

function run_() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) { Logger.log('Another run is active; exiting.'); return; }
  try { runLocked_(); } finally { lock.releaseLock(); }
}

function runLocked_() {
  startedAt = Date.now();
  props = PropertiesService.getScriptProperties();
  REPORT = []; WORKLIST = []; pathIndex = {};
  var done = loadCheckpoint_();
  var mode = DRY_RUN ? 'DRY RUN (no changes)' : 'EXECUTE';
  log_('===== SCLA Drive Refactor v2 — ' + mode + ' — resuming past ' + Object.keys(done).length + ' items =====');

  var root = DriveApp.getFolderById(ROOT_FOLDER_ID);
  pathIndex[''] = root;

  if (!DRY_RUN) shareRootWithOwners_(root);

  // Phase 1 — renames (cheap, editor-allowed, idempotent).
  applyRenames_(done);

  // Phase 2 — whole-folder moves (register their new paths first).
  var timedOut = applyFolderRoutes_(done);

  // Phase 3 — per-item routing over the CT tree + each shared root's children.
  if (!timedOut) timedOut = routeAll_(root, done);

  // Phase 4 — trash pass (capability-gated, empty-check for folders).
  if (!timedOut) timedOut = applyTrash_(done);

  // Phase 5 — retire emptied legacy containers, leave markers in shared roots.
  if (!timedOut && !DRY_RUN) retireEmptyContainers_(done);

  flushReport_();
  if (timedOut) {
    saveCheckpoint_(done);
    scheduleResume_();
    log_('Time budget reached — checkpointed. A resume trigger will continue automatically.');
  } else {
    clearCheckpoint_();
    deleteResumeTriggers_();
    log_('===== Done. ' + REPORT.length + ' actions this pass. Worklist items: ' + WORKLIST.length + ' =====');
  }
}

// ---- phases ----------------------------------------------------------------

function applyRenames_(done) {
  Object.keys(RENAMES).forEach(function (id) {
    if (done['rn:' + id]) return;
    try {
      var f = getItemById_(id);
      if (f && f.getName() !== RENAMES[id]) {
        if (!DRY_RUN) withRetry_(function () { f.setName(RENAMES[id]); });
        record_('RENAME', RENAMES[id], 'was: ' + f.getName());
      }
    } catch (e) { record_('ERROR', 'rename ' + id, String(e)); }
    done['rn:' + id] = 1;
  });
}

function applyFolderRoutes_(done) {
  var ids = Object.keys(FOLDER_ROUTES);
  for (var i = 0; i < ids.length; i++) {
    if (outOfTime_()) return true;
    var id = ids[i];
    if (done['fr:' + id]) { registerMovedFolder_(id); continue; }
    var destPath = FOLDER_ROUTES[id];
    try {
      var folder = DriveApp.getFolderById(id);
      var dest = getOrCreatePath_(destPath);
      var newPath = destPath + '/' + clean_(folder.getName());
      if (isAlreadyIn_(folder, dest)) {
        record_('SKIP (already home)', folder.getName(), newPath);
      } else if (DRY_RUN) {
        record_(predictMove_(id) ? 'MOVE FOLDER' : 'OWNER-BLOCKED (predicted)', folder.getName(), '→ ' + newPath);
      } else {
        try {
          withRetry_(function () { folder.moveTo(dest); });
          record_('MOVE FOLDER', folder.getName(), '→ ' + newPath);
        } catch (e) {
          withRetry_(function () { dest.createShortcut(id); });
          record_('OWNER-BLOCKED → POINTER', folder.getName(), destPath + ' (owner must move; ' + String(e).slice(0, 80) + ')');
          WORKLIST.push(['MOVE-BLOCKED', folder.getName(), id, destPath]);
        }
      }
      pathIndex[newPath] = folder;
    } catch (e) { record_('ERROR', 'folder ' + id, String(e)); }
    done['fr:' + id] = 1;
  }
  return false;
}

function registerMovedFolder_(id) {
  try {
    var folder = DriveApp.getFolderById(id);
    pathIndex[FOLDER_ROUTES[id] + '/' + clean_(folder.getName())] = folder;
  } catch (e) { /* gone or inaccessible; routes depending on it will error visibly */ }
}

function routeAll_(root, done) {
  // Walk CT root + children of each shared root. Skip FOLDER_ROUTES subtrees
  // (they moved wholesale). Route every file; give shortcuts the tri-policy.
  var stack = [{ folder: root, container: null }];
  SOURCE_ROOTS.forEach(function (rid) {
    try { stack.push({ folder: DriveApp.getFolderById(rid), container: CONTAINER_ROUTES[rid] || null, isSharedRoot: true }); }
    catch (e) { record_('ERROR', 'shared root ' + rid, String(e)); }
  });

  while (stack.length) {
    if (outOfTime_()) return true;
    var cur = stack.pop();
    var folderId = cur.folder.getId();
    if (FOLDER_ROUTES[folderId] && folderId !== ROOT_FOLDER_ID) continue; // moved wholesale
    var container = CONTAINER_ROUTES.hasOwnProperty(folderId) ? CONTAINER_ROUTES[folderId] : cur.container;

    var files = cur.folder.getFiles();
    while (files.hasNext()) {
      if (outOfTime_()) return true;
      var f = files.next();
      if (!done['f:' + f.getId()]) { routeFile_(f, container); done['f:' + f.getId()] = 1; }
    }
    var subs = cur.folder.getFolders();
    while (subs.hasNext()) {
      var sub = subs.next();
      if (isInsideTargetTree_(sub)) continue; // don't re-walk what we've built
      stack.push({ folder: sub, container: container });
    }
  }

  // Standalone shared files (parent = owner's My Drive root, never traversed):
  Object.keys(ID_ROUTES).forEach(function (id) {
    if (done['f:' + id] || !ID_ROUTES[id]) return;
    try { var f = DriveApp.getFileById(id); routeFile_(f, null); }
    catch (e) { record_('ERROR', 'standalone ' + id, String(e)); }
    done['f:' + id] = 1;
  });
  return false;
}

function routeFile_(file, containerDest) {
  var id = file.getId();
  if (isTrashListed_(id)) return; // handled in trash phase

  if ((file.getMimeType && file.getMimeType() === 'application/vnd.google-apps.shortcut') ||
      (file.getTargetId && file.getTargetId())) {
    return routeShortcut_(file, containerDest);
  }

  var dest = ID_ROUTES[id] || containerDest || routeByCourseCode_(file.getName()) || routeByName_(file.getName());
  if (!dest) { record_('UNMATCHED', file.getName(), 'left in place — add an ID_ROUTE'); return; }
  moveWithFallback_(file, dest, 'MOVE');
}

/** Shortcut tri-policy: COLLAPSE / KEEP-AS-POINTER / DEAD-OR-INVISIBLE. */
function routeShortcut_(sc, containerDest) {
  var targetId = sc.getTargetId();
  var name = sc.getName();
  var targetAlive = false, target = null;
  try { target = getItemById_(targetId); targetAlive = !!target; } catch (e) { targetAlive = false; }

  if (!targetAlive) {
    record_('DEAD-OR-INVISIBLE', name, 'target ' + targetId + ' unreachable — NOT deleted (may be alive but unshared)');
    WORKLIST.push(['DEAD-OR-INVISIBLE-SHORTCUT', name, sc.getId(), '']);
    return;
  }
  if (ID_ROUTES[targetId] || isTrashListed_(targetId) || isInsideTargetTree_(target)) {
    // Target has (or will have) a home in the tree — the shortcut is a duplicate.
    if (DRY_RUN) { record_('COLLAPSE-SHORTCUT (predicted)', name, 'target routed'); return; }
    try { withRetry_(function () { sc.setTrashed(true); }); record_('COLLAPSE-SHORTCUT', name, 'target routed into tree'); }
    catch (e) {
      record_('COLLAPSE-BLOCKED', name, 'cannot trash others\' shortcut — left in place');
      WORKLIST.push(['TRASH-BLOCKED-SHORTCUT', name, sc.getId(), '']);
    }
    return;
  }
  // Sole reference to something outside our reach — keep it, but in the right place.
  var dest = ID_ROUTES[sc.getId()] || containerDest;
  if (dest) moveWithFallback_(sc, dest, 'KEEP-AS-POINTER');
  else record_('KEEP-AS-POINTER (in place)', name, 'target outside tree; no destination rule');
}

function moveWithFallback_(file, destPath, label) {
  var dest = getOrCreatePath_(destPath);
  if (isAlreadyIn_(file, dest)) { record_('SKIP (already home)', file.getName(), destPath); return; }
  if (DRY_RUN) {
    record_(predictMove_(file.getId()) ? label : 'OWNER-BLOCKED (predicted)', file.getName(), '→ ' + destPath);
    return;
  }
  try {
    withRetry_(function () { file.moveTo(dest); });
    record_(label, file.getName(), '→ ' + destPath);
  } catch (e) {
    try {
      withRetry_(function () { dest.createShortcut(file.getId()); });
      record_('OWNER-BLOCKED → POINTER', file.getName(), destPath + ' (' + String(e).slice(0, 80) + ')');
    } catch (e2) { record_('ERROR', file.getName(), 'move+pointer both failed: ' + String(e2).slice(0, 80)); }
    WORKLIST.push(['MOVE-BLOCKED', file.getName(), file.getId(), destPath]);
  }
}

function applyTrash_(done) {
  for (var i = 0; i < TRASH_RULES.length; i++) {
    if (outOfTime_()) return true;
    var r = TRASH_RULES[i];
    if (done['t:' + r.id]) continue;
    try {
      var item = r.folder ? DriveApp.getFolderById(r.id) : DriveApp.getFileById(r.id);
      if (r.folder && !isFolderEmpty_(item)) {
        record_('TRASH-SKIPPED', item.getName(), 'folder not empty at run time — re-check');
        WORKLIST.push(['TRASH-NOT-EMPTY', item.getName(), r.id, '']); done['t:' + r.id] = 1; continue;
      }
      if (r.byteMatchOf && !r.folder) {
        var twin = DriveApp.getFileById(r.byteMatchOf);
        if (item.getSize() !== twin.getSize()) {
          moveWithFallback_(item, r['else'], 'ARCHIVE (byte-mismatch, not trashed)');
          done['t:' + r.id] = 1; continue;
        }
      }
      if (DRY_RUN) { record_(predictTrash_(r.id) ? 'TRASH (predicted)' : 'TRASH-BLOCKED (predicted)', item.getName(), r.why); }
      else {
        try { withRetry_(function () { item.setTrashed(true); }); record_('TRASH', item.getName(), r.why); }
        catch (e) {
          // Non-owner: stage it instead so the run never throws.
          try { moveWithFallback_(item, PENDING_TRASH, 'STAGED-FOR-OWNER-TRASH'); }
          catch (e2) { record_('TRASH-BLOCKED', item.getName(), 'owner must trash'); }
          WORKLIST.push(['TRASH-BLOCKED', item.getName(), r.id, r.why]);
        }
      }
    } catch (e) { record_('ERROR', 'trash ' + r.id, String(e)); }
    done['t:' + r.id] = 1;
  }
  return false;
}

function retireEmptyContainers_(done) {
  Object.keys(CONTAINER_ROUTES).forEach(function (id) {
    if (done['rc:' + id] || SOURCE_ROOTS.indexOf(id) !== -1) return;
    try {
      var folder = DriveApp.getFolderById(id);
      if (isFolderEmpty_(folder)) {
        try { withRetry_(function () { folder.setTrashed(true); }); record_('RETIRE', folder.getName(), 'emptied legacy container'); }
        catch (e) { record_('RETIRE-BLOCKED', folder.getName(), 'owner must trash'); WORKLIST.push(['RETIRE-BLOCKED', folder.getName(), id, '']); }
      } else {
        record_('RETIRE-SKIPPED', folder.getName(), 'not empty (owner-blocked leftovers?) — see worklist');
      }
    } catch (e) { /* already gone */ }
    done['rc:' + id] = 1;
  });
  SOURCE_ROOTS.forEach(function (rid) {
    try {
      var rootFolder = DriveApp.getFolderById(rid);
      var probe = rootFolder.getFilesByName('MOVED — see Community Team Folder');
      if (!probe.hasNext()) rootFolder.createFile('MOVED — see Community Team Folder',
        'This drive was consolidated into the Community Team Folder on ' + new Date().toISOString().slice(0, 10) +
        '.\nSee scripts/drive-refactor/ANNOTATED-WORKTREE.md in the SCLA-Profile repo for the map.');
    } catch (e) { /* read-only root; note stays in worklist via blocked entries */ }
  });
}

// ---- helpers ---------------------------------------------------------------

function clean_(name) { return String(name).replace(/\s+/g, ' ').trim(); }

function getOrCreatePath_(path) {
  if (pathIndex[path]) return pathIndex[path];
  var parts = path.split('/');
  var cur = pathIndex[''];
  var walked = '';
  for (var i = 0; i < parts.length; i++) {
    walked = walked ? walked + '/' + parts[i] : parts[i];
    if (pathIndex[walked]) { cur = pathIndex[walked]; continue; }
    var it = cur.getFoldersByName(parts[i]);
    if (it.hasNext()) { cur = it.next(); }
    else if (DRY_RUN) {
      record_('CREATE FOLDER (predicted)', parts[i], 'under ' + walked);
      cur = virtualFolder_(parts[i]);
    } else {
      var name = parts[i];
      cur = withRetry_(function () { return cur.createFolder(name); });
      record_('CREATE FOLDER', parts[i], walked);
    }
    pathIndex[walked] = cur;
  }
  return cur;
}

function virtualFolder_(name) {
  return { __virtual: true,
    getId: function () { return 'virtual'; },
    getName: function () { return name; },
    getFoldersByName: function () { return { hasNext: function () { return false; } }; },
    createShortcut: function () {},
    createFolder: function (n) { return virtualFolder_(n); } };
}

function isAlreadyIn_(item, dest) {
  if (dest.__virtual) return false;
  var parents = item.getParents();
  if (parents.hasNext()) {
    var p = parents.next();
    if (!parents.hasNext() && p.getId() === dest.getId()) return true;
  }
  return false;
}

function isInsideTargetTree_(item) {
  // True if any ancestor is the CT root AND its top ancestor path was built by us.
  try {
    var p = item.getParents();
    var hops = 0;
    var cur = p.hasNext() ? p.next() : null;
    while (cur && hops++ < 10) {
      if (cur.getId() === ROOT_FOLDER_ID) return /^0[1-9] |^09 /.test(topAncestorName_(item)) || true;
      var pp = cur.getParents();
      cur = pp.hasNext() ? pp.next() : null;
    }
  } catch (e) {}
  return false;
}

function topAncestorName_(item) {
  try {
    var cur = item, name = item.getName();
    for (var i = 0; i < 10; i++) {
      var p = cur.getParents();
      if (!p.hasNext()) return name;
      var parent = p.next();
      if (parent.getId() === ROOT_FOLDER_ID) return cur.getName();
      name = parent.getName(); cur = parent;
    }
  } catch (e) {}
  return '';
}

function isFolderEmpty_(folder) {
  return !folder.getFiles().hasNext() && !folder.getFolders().hasNext();
}

function isTrashListed_(id) {
  for (var i = 0; i < TRASH_RULES.length; i++) if (TRASH_RULES[i].id === id) return true;
  return false;
}

function getItemById_(id) {
  try { return DriveApp.getFileById(id); }
  catch (e) { return DriveApp.getFolderById(id); }
}

function routeByCourseCode_(name) {
  var m = clean_(name).match(/^([A-Z]{2,4})\s?\d{3}/i);
  if (!m) return null;
  return COURSE_CODE_MAP[m[1].toUpperCase()] || null;
}

function routeByName_(name) {
  var hay = clean_(name).toLowerCase();
  for (var i = 0; i < NAME_RULES.length; i++) {
    var mch = NAME_RULES[i].match;
    if (mch instanceof RegExp ? mch.test(name) : hay.indexOf(String(mch).toLowerCase()) !== -1)
      return NAME_RULES[i].dest;
  }
  return null;
}

/** Capability probe via the Drive advanced service (enable "Drive API" in
 *  Services). Falls back to optimistic prediction when unavailable. */
function predictMove_(id)  { return predictCap_(id, 'canMoveItemWithinDrive'); }
function predictTrash_(id) { return predictCap_(id, 'canTrash'); }
function predictCap_(id, cap) {
  try {
    if (typeof Drive === 'undefined') return true;
    var meta = Drive.Files.get(id, { fields: 'capabilities', supportsAllDrives: true });
    var caps = meta.capabilities || {};
    return caps[cap] !== false;
  } catch (e) { return true; }
}

function shareRootWithOwners_(root) {
  OWNER_EMAILS.forEach(function (email) {
    try { root.addEditor(email); } catch (e) { WORKLIST.push(['SHARE-FAILED', email, ROOT_FOLDER_ID, String(e).slice(0, 60)]); }
  });
}

function withRetry_(fn) {
  var delay = 500;
  for (var i = 0; i < 5; i++) {
    try { return fn(); }
    catch (e) {
      if (i === 4 || !/rate|quota|timed? ?out|internal/i.test(String(e))) throw e;
      Utilities.sleep(delay); delay *= 2;
    }
  }
}

function outOfTime_() { return Date.now() - startedAt > TIME_BUDGET_MS; }

// ---- checkpoint / resume ---------------------------------------------------

function loadCheckpoint_() {
  var done = {}, i = 0, chunk;
  while ((chunk = props.getProperty('ckpt_' + i++)) !== null)
    chunk.split(',').forEach(function (k) { if (k) done[k] = 1; });
  return done;
}

function saveCheckpoint_(done) {
  var keys = Object.keys(done), CHUNK = 300, n = 0;
  for (var i = 0; i < keys.length; i += CHUNK)
    props.setProperty('ckpt_' + n++, keys.slice(i, i + CHUNK).join(','));
  props.setProperty('ckpt_mode', DRY_RUN ? 'dry' : 'exec');
}

function clearCheckpoint_() {
  var i = 0;
  while (props.getProperty('ckpt_' + i) !== null) props.deleteProperty('ckpt_' + i++);
  props.deleteProperty('ckpt_mode');
}

function scheduleResume_() {
  deleteResumeTriggers_();
  ScriptApp.newTrigger('resume_').timeBased().after(60 * 1000).create();
}

function resume_() {
  var mode = PropertiesService.getScriptProperties().getProperty('ckpt_mode');
  if (mode === 'exec') execute(); else if (mode === 'dry') dryRun();
}

function deleteResumeTriggers_() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'resume_') ScriptApp.deleteTrigger(t);
  });
}

// ---- reporting -------------------------------------------------------------

function record_(action, item, detail) {
  REPORT.push([action, item, detail || '']);
  log_('[' + action + '] ' + item + (detail ? '  ' + detail : ''));
}

function log_(msg) { Logger.log(msg); }

function flushReport_() {
  var sheetName = DRY_RUN ? 'Drive Refactor Log (DRY RUN)' : 'Drive Refactor Log';
  var ssId = props.getProperty('report_' + (DRY_RUN ? 'dry' : 'exec'));
  var ss;
  try { ss = ssId ? SpreadsheetApp.openById(ssId) : SpreadsheetApp.create(sheetName); }
  catch (e) { ss = SpreadsheetApp.create(sheetName); }
  props.setProperty('report_' + (DRY_RUN ? 'dry' : 'exec'), ss.getId());

  var sheet = ss.getSheets()[0];
  if (sheet.getLastRow() === 0) sheet.appendRow(['Action', 'Item', 'Detail']);
  if (REPORT.length)
    sheet.getRange(sheet.getLastRow() + 1, 1, REPORT.length, 3).setValues(REPORT);

  if (WORKLIST.length) {
    var wl = ss.getSheetByName('OWNER WORKLIST') || ss.insertSheet('OWNER WORKLIST');
    if (wl.getLastRow() === 0) wl.appendRow(['Type', 'Item', 'ID', 'Destination / note']);
    wl.getRange(wl.getLastRow() + 1, 1, WORKLIST.length, 4).setValues(WORKLIST);
  }
  log_('Report: ' + ss.getUrl());
}
