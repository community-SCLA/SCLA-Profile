/**
 * Community Team Drive — Folder Refactor
 * ======================================
 * Restructures the SCLA "Community Team" Google Drive folder to match the
 * hierarchy in scla/projects/drive-review-brief.md:
 *   - Organize by Topic/Initiative, not by Type
 *   - Exactly one home per document (no cross-posting / shortcut duplicates)
 *   - Max 3 folder levels; superseded versions go to a sibling _Archive/
 *   - Stale items: Archive (set aside) or Trash (no future value)
 *
 * HOW TO USE
 * ----------
 *   1. Open https://script.google.com → New project → paste this file.
 *   2. Set ROOT_FOLDER_ID below to the Community Team folder's ID
 *      (the long string in its Drive URL: drive.google.com/drive/folders/<ID>).
 *   3. Run `dryRun()` first. It changes NOTHING — it only writes a plan to the
 *      execution log and to a "Drive Refactor Log" Google Sheet in your Drive.
 *   4. Read the log. Resolve anything tagged UNMATCHED or AMBIGUOUS by adding a
 *      rule in MOVE_RULES (match an exact-or-partial file name → destination).
 *   5. When the plan looks right, run `execute()` to apply it for real.
 *
 * The script is idempotent: folders are find-or-created, files already in the
 * right home are skipped, and a second run after a clean run is a no-op.
 *
 * Requires the "Drive" advanced service? No — uses built-in DriveApp + Spreadsheet.
 */

// ============================================================================
// CONFIG
// ============================================================================

/** Drive ID of the Community Team root folder. REQUIRED. */
var ROOT_FOLDER_ID = 'PASTE_COMMUNITY_TEAM_FOLDER_ID_HERE';

/**
 * Master safety switch.
 *   true  → plan only, no changes (default). Run dryRun().
 *   false → apply changes. Run execute().
 * The dryRun() / execute() entry points set this for you; you normally don't
 * edit it by hand.
 */
var DRY_RUN = true;

/** If true, files that match no rule are reported but left untouched. */
var SKIP_UNMATCHED = true;

/** Name used for per-folder archive subfolders. */
var ARCHIVE_FOLDER_NAME = '_Archive';

// ============================================================================
// ENTRY POINTS
// ============================================================================

function dryRun() {
  DRY_RUN = true;
  run_();
}

function execute() {
  DRY_RUN = false;
  run_();
}

// ============================================================================
// TARGET FOLDER HIERARCHY  (from drive-review-brief.md)
// Nested object → folders are created depth-first, find-or-create (idempotent).
// Leaf folders that hold docs are listed as {} (no children).
// ============================================================================

var FOLDER_TREE = {
  '01 Learning (CIAO)': {
    'Course Catalog': {
      'AI & Technology': {},
      'Career & Job Search': {},
      'Networking': {},
      'Communication': {},
      'Leadership': {},
      'Psychology & EQ': {},
      'Learning Skills': {},
      'Productivity': {},
      'Workplace Skills': {},
      'Thinking Skills': {},
      'Entrepreneurship': {},
      'Assessments': {},
      'Seasonal Cohorts': {},
      'Master Catalog': {}
    },
    'Career Readiness Program': {},
    'LinkedIn & Personal Brand Toolkit': {},
    'Partner Courses': {
      'Identity Leadership (IDL)': {},
      'ISPI': {}
    },
    'Wellness Center — Q3 Not Started': {},
    'Job Readiness Steps (True Colors Series)': {}
  },
  '02 Foundation': {
    'Frameworks': {},
    'Strategy': {},
    'Research & Member Feedback': {},
    '_Archive': {}
  },
  '03 Communications': {
    'Active': {},
    'Standalone Content': {},
    '_Archive': {
      'Weekly Updates 2026': {}
    }
  },
  '04 Micro-Internships': {
    'Program Roadmap': {},
    'Partner Ideas': {},
    'Project Content': {},
    'Member & Partner Assessments': {},
    'Outreach & Marketing': {}
  },
  '05 Partner Portal': {
    'SGA (Student Government Associations)': {}
  },
  '06 Accreditation & Credibility': {},
  '07 Team Operations': {
    'Member Support': {},
    'Info Sessions': {},
    'Templates & Tools': {},
    'Frontline': {}
  },
  '08 Member Engagement': {
    'Member Journey & Onboarding': {
      '_Archive': {}
    },
    'Events': {},
    'Pledge Project': {},
    'Celebrations': {}
  },
  '09 Advisor Community': {},
  '_Marketing & Brand': {}
};

// ============================================================================
// COURSE-CODE ROUTER
// Course syllabi are named "<PREFIX><NNN> ...". Route by alpha prefix into the
// Course Catalog. Runs only on names matching /^[A-Z]{2,4}\s?\d{3}/.
// Specific overrides (e.g. PSY102 self-assessment) are handled in MOVE_RULES,
// which is evaluated FIRST, so generic prefixes never clobber them.
// ============================================================================

var COURSE_CATALOG_BASE = '01 Learning (CIAO)/Course Catalog';

var COURSE_CODE_MAP = {
  AI:  COURSE_CATALOG_BASE + '/AI & Technology',
  CAR: COURSE_CATALOG_BASE + '/Career & Job Search',
  NET: COURSE_CATALOG_BASE + '/Networking',
  COM: COURSE_CATALOG_BASE + '/Communication',
  LDR: COURSE_CATALOG_BASE + '/Leadership',
  PSY: COURSE_CATALOG_BASE + '/Psychology & EQ',
  LRN: COURSE_CATALOG_BASE + '/Learning Skills',
  PRD: COURSE_CATALOG_BASE + '/Productivity',
  WRK: COURSE_CATALOG_BASE + '/Workplace Skills',
  STR: COURSE_CATALOG_BASE + '/Workplace Skills',      // STR101 → Workplace Skills
  THK: COURSE_CATALOG_BASE + '/Thinking Skills',
  ENT: COURSE_CATALOG_BASE + '/Entrepreneurship',
  ASM: COURSE_CATALOG_BASE + '/Assessments',
  SPR: COURSE_CATALOG_BASE + '/Seasonal Cohorts',
  // Career Readiness Program (not Course Catalog):
  CRA: '01 Learning (CIAO)/Career Readiness Program',
  CRC: '01 Learning (CIAO)/Career Readiness Program'
};

// ============================================================================
// EXPLICIT MOVE RULES  (evaluated before the course-code router)
// {match: 'substring or /regex/', dest: 'Folder/Path', exact?: true}
// Matching is case-insensitive. `exact:true` requires the whole name to match.
// First matching rule wins, so order specific rules before broad ones.
// ============================================================================

var MOVE_RULES = [
  // --- 01 Learning: Career Readiness Program specific docs ---
  { match: 'Career Readiness Accelerator Outline', dest: '01 Learning (CIAO)/Career Readiness Program' },
  { match: '18 Actionable Strategies',             dest: '01 Learning (CIAO)/Career Readiness Program' },

  // --- 01 Learning: overrides that would otherwise hit the course router ---
  { match: 'PSY102 self-assessment', dest: COURSE_CATALOG_BASE + '/Assessments' },

  // --- 01 Learning: Course Catalog named (non-coded) items ---
  { match: 'Hidden Job Market',                 dest: COURSE_CATALOG_BASE + '/Career & Job Search' },
  { match: 'Interview Video',                   dest: COURSE_CATALOG_BASE + '/Career & Job Search' },
  { match: 'Ed Prospectus',                     dest: COURSE_CATALOG_BASE + '/Master Catalog' },
  { match: 'Ed Vault SCLA 2026',                dest: COURSE_CATALOG_BASE + '/Master Catalog' },
  { match: 'Q2 Reset',                          dest: COURSE_CATALOG_BASE + '/Seasonal Cohorts' },

  // --- 01 Learning: LinkedIn & Personal Brand Toolkit ---
  { match: 'Define Your Personal Brand',        dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'Optimize LinkedIn Profile',         dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'LinkedIn Profile Playbook',         dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'Sleuthing Tips',                    dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'Escape Personal Branding Workbook', dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: '6 Ways to Grow Your Network',       dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'LinkedIn Success Database',         dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'Activate Your Network',             dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'Supercharge Your LinkedIn Bio',     dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: 'Peer Connections Templates',        dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },
  { match: "Sophie's Challenge",                dest: '01 Learning (CIAO)/LinkedIn & Personal Brand Toolkit' },

  // --- 01 Learning: Partner Courses ---
  { match: 'IDL Content',                       dest: '01 Learning (CIAO)/Partner Courses/Identity Leadership (IDL)' },
  { match: 'Three Archetypes of Innovation',    dest: '01 Learning (CIAO)/Partner Courses/ISPI' },
  { match: 'New Readiness Course Video Needs',  dest: '01 Learning (CIAO)/Partner Courses/ISPI' },

  // --- 01 Learning: Wellness ---
  { match: 'Wellness Center Framework',         dest: '01 Learning (CIAO)/Wellness Center — Q3 Not Started' },

  // --- 01 Learning: Job Readiness Steps (True Colors Series) ---
  { match: /step-(one|two|three|four)/i,        dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },
  { match: 'True Colors',                       dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },
  { match: 'welcome video',                     dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },
  { match: 'SMART Goals',                       dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },
  { match: 'peer-connections',                  dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },
  { match: 'career-connections',                dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },
  { match: 'SCLA Career Hub',                   dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },
  { match: 'SCLA Leadership Program Tech Notes',dest: '01 Learning (CIAO)/Job Readiness Steps (True Colors Series)' },

  // --- 02 Foundation: Frameworks ---
  { match: 'Durable Skills Framework',          dest: '02 Foundation/Frameworks' },
  { match: 'C2C Framework',                     dest: '02 Foundation/Frameworks' },
  { match: 'Focus Modes',                       dest: '02 Foundation/Frameworks' },
  // --- 02 Foundation: Strategy ---
  { match: 'Education SCLA 2026',               dest: '02 Foundation/Strategy' },
  { match: 'Product Strategy & Positioning',    dest: '02 Foundation/Strategy' },
  { match: 'Academy v. Honors',                 dest: '02 Foundation/Strategy' },
  { match: 'Scalation Road Map',                dest: '02 Foundation/Strategy' },
  { match: 'Leader of the Future',              dest: '02 Foundation/Strategy' },
  { match: 'Workshop Proposal',                 dest: '02 Foundation/Strategy' },
  // --- 02 Foundation: Research & Member Feedback ---
  { match: 'OGC Member Survey',                 dest: '02 Foundation/Research & Member Feedback' },
  { match: 'Focus Group Module Suggestions',    dest: '02 Foundation/Research & Member Feedback' },
  // --- 02 Foundation: _Archive ---
  { match: 'Ed Update Feb 2026',                dest: '02 Foundation/_Archive' },

  // --- 03 Communications ---
  { match: 'Community Communications 2026 PRD', dest: '03 Communications/Active' },
  { match: 'Channels Documentation',            dest: '03 Communications/Active' },
  { match: 'The Case for Doing Less',           dest: '03 Communications/Standalone Content' },
  { match: 'What Kind of Learner Are You',      dest: '03 Communications/Standalone Content' },
  { match: 'What kind of learner are you',      dest: '03 Communications/Standalone Content' },
  // Weekly updates → archive
  { match: 'Friday Update 02-27-26',            dest: '03 Communications/_Archive/Weekly Updates 2026' },
  { match: 'Community & Learning Team Update 03-13-26', dest: '03 Communications/_Archive/Weekly Updates 2026' },
  { match: 'Weekly Sync 03-20-26',              dest: '03 Communications/_Archive/Weekly Updates 2026' },
  { match: 'Weekly Sync 03-27-26',              dest: '03 Communications/_Archive/Weekly Updates 2026' },
  { match: 'Team Update 05-04-26',              dest: '03 Communications/_Archive/Weekly Updates 2026' },

  // --- 04 Micro-Internships ---
  { match: 'Micro-Internships Overview',        dest: '04 Micro-Internships/Program Roadmap' },
  { match: 'Forage Partnership',                dest: '04 Micro-Internships/Partner Ideas' },
  { match: 'Digital Access in Nigeria',         dest: '04 Micro-Internships/Project Content' },
  { match: 'Tech Truck',                        dest: '04 Micro-Internships/Project Content' },
  { match: 'Upskilling Women',                  dest: '04 Micro-Internships/Project Content' },
  { match: 'Micro-Internship Samples',          dest: '04 Micro-Internships/Project Content' },
  { match: 'Project Interest Assessment',       dest: '04 Micro-Internships/Member & Partner Assessments' },
  { match: 'Project Wishlist Assessment',       dest: '04 Micro-Internships/Member & Partner Assessments' },
  { match: 'SCLA Outreach Drafts',              dest: '04 Micro-Internships/Outreach & Marketing' },

  // --- 05 Partner Portal: SGA ---
  { match: 'SGA Pitch to Chapters',             dest: '05 Partner Portal/SGA (Student Government Associations)' },
  { match: "Amy's Notes",                       dest: '05 Partner Portal/SGA (Student Government Associations)' },
  { match: 'National University Binder',        dest: '05 Partner Portal/SGA (Student Government Associations)' },
  { match: 'SGA Presentation',                  dest: '05 Partner Portal/SGA (Student Government Associations)' },
  { match: 'Stedman Graham Live Handoff',       dest: '05 Partner Portal/SGA (Student Government Associations)' },
  { match: 'Leadership Development Coaching Initiative Pilot', dest: '05 Partner Portal' },

  // --- 07 Team Operations ---
  { match: 'Member Support Plan Spec',          dest: '07 Team Operations/Member Support' },
  { match: 'Two-Tier Communication SOP',        dest: '07 Team Operations/Member Support' },
  { match: 'Info Session Deck',                 dest: '07 Team Operations/Info Sessions' },
  { match: 'Info Session (marketing',           dest: '07 Team Operations/Info Sessions' },
  { match: 'Learning Program Template',         dest: '07 Team Operations/Templates & Tools' },
  { match: 'Community Manager Bios',            dest: '07 Team Operations/Templates & Tools' },
  { match: 'Frontline Forward',                 dest: '07 Team Operations/Frontline' },

  // --- 08 Member Engagement ---
  { match: 'Membership Journey Today',          dest: '08 Member Engagement/Member Journey & Onboarding' },
  { match: 'The BIG Welcome — FINAL',           dest: '08 Member Engagement/Member Journey & Onboarding' },
  { match: 'The BIG Welcome — Onboarding 2026', dest: '08 Member Engagement/Member Journey & Onboarding' },
  { match: 'Orientation Script',                dest: '08 Member Engagement/Member Journey & Onboarding' },
  { match: 'TL;DR Highlights',                  dest: '08 Member Engagement/Member Journey & Onboarding' },
  { match: 'The BIG Welcome v1',                dest: '08 Member Engagement/Member Journey & Onboarding/_Archive' },
  { match: 'Events 2026 PRD',                   dest: '08 Member Engagement/Events' },
  { match: 'Reset Book Club Guide',             dest: '08 Member Engagement/Events' },
  { match: 'Reset One-Pager',                   dest: '08 Member Engagement/Events' },
  { match: 'Naming Ideas for the BIG Events',   dest: '08 Member Engagement/Events' },
  { match: 'Pledge Project Outreach',           dest: '08 Member Engagement/Pledge Project' },
  { match: 'Emails for the BIG Celebration',    dest: '08 Member Engagement/Celebrations' },

  // --- _Marketing & Brand ---
  { match: 'SCLA Branding Kit',                 dest: '_Marketing & Brand' },
  { match: 'SCLA Information Deck',             dest: '_Marketing & Brand' },
  { match: 'SGA Overview',                      dest: '_Marketing & Brand' }
];

// ============================================================================
// STALE DISPOSITIONS  (from "What Is Clearly Stale" + Additional Findings)
// ============================================================================

/** TRASH — no future reference value. Sent to Drive trash (recoverable 30 days). */
var TRASH_RULES = [
  { match: 'Comms SCLA-NIC' },             // NIC wind-down
  { match: 'NIC Innovation' },             // NIC wind-down
  { match: 'Voyije Program Wrap' }         // program completed
];

/**
 * ARCHIVE — keep but set aside. Moved to the destination's _Archive subfolder.
 * Used for ARCHIVE-labeled files found loose in active folders (Finding #4).
 */
var ARCHIVE_RULES = [
  { match: 'ARCHIVE SCLA Info Session Deck',  dest: '07 Team Operations/Info Sessions/_Archive' },
  { match: 'ARCHIVE Info Session Slides',     dest: '07 Team Operations/Info Sessions/_Archive' }
];

// ============================================================================
// ENGINE  (you should not need to edit below this line)
// ============================================================================

var REPORT = []; // {action, item, detail}

function run_() {
  if (ROOT_FOLDER_ID === 'PASTE_COMMUNITY_TEAM_FOLDER_ID_HERE') {
    throw new Error('Set ROOT_FOLDER_ID to the Community Team folder ID before running.');
  }
  REPORT = [];
  var mode = DRY_RUN ? 'DRY RUN (no changes)' : 'EXECUTE (applying changes)';
  log_('===== Community Team Drive Refactor — ' + mode + ' =====');

  var root = DriveApp.getFolderById(ROOT_FOLDER_ID);
  log_('Root: ' + root.getName());

  // 1. Build the target folder skeleton.
  var folderIndex = {}; // 'Path/To/Folder' -> Folder
  buildTree_(root, FOLDER_TREE, '', folderIndex);

  // 2. Snapshot all files up front (so moves don't disturb iteration).
  var files = collectFiles_(root, folderIndex);
  log_('Found ' + files.length + ' files under root.');

  // 3. Apply trash, archive, then move rules.
  files.forEach(function (f) { routeFile_(f, root, folderIndex); });

  // 4. Persist the report to a Google Sheet for review.
  writeReport_();
  log_('===== Done. ' + REPORT.length + ' planned/applied actions. =====');
}

/** Depth-first find-or-create of the folder tree. Records paths in index. */
function buildTree_(parentFolder, node, prefix, index) {
  Object.keys(node).forEach(function (name) {
    var path = prefix ? prefix + '/' + name : name;
    var folder = findOrCreateFolder_(parentFolder, name);
    index[path] = folder;
    buildTree_(folder, node[name], path, index);
  });
}

function findOrCreateFolder_(parent, name) {
  var it = parent.getFoldersByName(name);
  if (it.hasNext()) return it.next();
  if (DRY_RUN) {
    record_('CREATE FOLDER', name, 'under ' + parent.getName());
    // Return a lightweight stand-in so dry-run path lookups still resolve.
    return { __virtual: true, getName: function () { return name; },
             getFoldersByName: function () { return { hasNext: function () { return false; } }; } };
  }
  record_('CREATE FOLDER', name, 'under ' + parent.getName());
  return parent.createFolder(name);
}

/** Recursively gather files, skipping the folders we just created as targets. */
function collectFiles_(root, folderIndex) {
  var out = [];
  var stack = [root];
  while (stack.length) {
    var folder = stack.pop();
    var files = folder.getFiles();
    while (files.hasNext()) out.push(files.next());
    var subs = folder.getFolders();
    while (subs.hasNext()) stack.push(subs.next());
  }
  return out;
}

/** Decide what happens to one file: trash → archive → move-rule → course code. */
function routeFile_(file, root, folderIndex) {
  var name = file.getName();

  // Trash
  for (var i = 0; i < TRASH_RULES.length; i++) {
    if (nameMatches_(name, TRASH_RULES[i].match)) {
      doTrash_(file);
      return;
    }
  }
  // Archive (explicit)
  for (var a = 0; a < ARCHIVE_RULES.length; a++) {
    if (nameMatches_(name, ARCHIVE_RULES[a].match)) {
      doMove_(file, ARCHIVE_RULES[a].dest, folderIndex, 'ARCHIVE');
      return;
    }
  }
  // Explicit move rules
  for (var m = 0; m < MOVE_RULES.length; m++) {
    if (nameMatches_(name, MOVE_RULES[m].match, MOVE_RULES[m].exact)) {
      doMove_(file, MOVE_RULES[m].dest, folderIndex, 'MOVE');
      return;
    }
  }
  // Course-code router
  var dest = routeByCourseCode_(name);
  if (dest) {
    doMove_(file, dest, folderIndex, 'MOVE (course code)');
    return;
  }
  // Unmatched
  if (SKIP_UNMATCHED) {
    record_('UNMATCHED', name, 'left in place — add a MOVE_RULE to route it');
  }
}

function routeByCourseCode_(name) {
  var m = name.trim().match(/^([A-Z]{2,4})\s?\d{3}/i);
  if (!m) return null;
  var prefix = m[1].toUpperCase();
  return COURSE_CODE_MAP[prefix] || null;
}

function nameMatches_(name, matcher, exact) {
  if (matcher instanceof RegExp) return matcher.test(name);
  var hay = name.toLowerCase();
  var needle = String(matcher).toLowerCase();
  return exact ? hay === needle : hay.indexOf(needle) !== -1;
}

function doMove_(file, destPath, folderIndex, label) {
  var target = folderIndex[destPath];
  if (!target) {
    record_('ERROR', file.getName(), 'destination not in tree: ' + destPath);
    return;
  }
  // Already home? (single-parent check)
  var parents = file.getParents();
  if (parents.hasNext()) {
    var p = parents.next();
    if (!parents.hasNext() && p.getName() === target.getName()) {
      record_('SKIP (already home)', file.getName(), destPath);
      return;
    }
  }
  if (DRY_RUN || target.__virtual) {
    record_(label, file.getName(), '→ ' + destPath);
    return;
  }
  file.moveTo(target); // detaches from all other parents (single home)
  record_(label, file.getName(), '→ ' + destPath);
}

function doTrash_(file) {
  if (!DRY_RUN) file.setTrashed(true);
  record_('TRASH', file.getName(), 'no future reference value');
}

// ---- reporting -------------------------------------------------------------

function record_(action, item, detail) {
  REPORT.push({ action: action, item: item, detail: detail || '' });
  log_('[' + action + '] ' + item + (detail ? '  ' + detail : ''));
}

function log_(msg) { Logger.log(msg); }

function writeReport_() {
  var sheetName = 'Drive Refactor Log';
  var ss;
  var files = DriveApp.getFilesByName(sheetName);
  if (files.hasNext()) {
    ss = SpreadsheetApp.open(files.next());
  } else if (!DRY_RUN) {
    ss = SpreadsheetApp.create(sheetName);
  } else {
    // Dry run with no existing sheet: still create one so reviewers can read it.
    ss = SpreadsheetApp.create(sheetName + ' (DRY RUN)');
  }
  var sheet = ss.getSheets()[0];
  sheet.clearContents();
  sheet.appendRow(['Timestamp', new Date().toISOString(), DRY_RUN ? 'DRY RUN' : 'EXECUTED']);
  sheet.appendRow(['Action', 'Item', 'Detail']);
  REPORT.forEach(function (r) { sheet.appendRow([r.action, r.item, r.detail]); });
  log_('Report written to: ' + ss.getUrl());
}
