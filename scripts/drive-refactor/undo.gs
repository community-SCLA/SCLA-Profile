/**
 * SCLA Community Team Drive — Folder Refactor v2 ROLLBACK
 * ======================================================
 * Reverses a completed `execute()` run of community-team-folder-refactor.gs.
 *
 * The refactor script cannot undo itself: its log records
 * [Action, Item name, Destination] and never the file ID or the ORIGINAL parent
 * (see record_() in community-team-folder-refactor.gs). So the prior state is
 * reconstructed from the **Drive Activity API v2**, which records, per item, the
 * parents a move removed (`removedParents`) and the title a rename replaced
 * (`rename.oldTitle`). That API is the only faithful record of where things were.
 *
 * RUN ORDER — four functions, in this order, no skipping:
 *
 *   1. harvest()     read-only. Reads Drive Activity for the run window and
 *                    writes the "UNDO PLAN" Sheet — one row per reversal, each
 *                    with an `Apply?` cell. THE SHEET IS THE PLAN OF RECORD.
 *   2. (you) review the Sheet. Set `Apply?` to NO on anything you want kept.
 *                    Rows harvest flagged as low-confidence already default NO.
 *   3. undoDryRun()  reads the Sheet back, checks every row against live Drive,
 *                    writes predicted outcomes + conflicts to "UNDO LOG (DRY RUN)".
 *                    Changes nothing.
 *   4. undoExecute() applies the YES rows in phase order.
 *
 *   reset() clears checkpoints and resume triggers for a fresh pass.
 *
 * SAFETY INVARIANTS
 *  - Nothing is ever permanently deleted. "Delete" always means setTrashed(true).
 *  - An item whose CURRENT parent is not where the refactor put it is treated as
 *    re-filed by a human since the run: flagged CONFLICT-MOVED-SINCE, never moved.
 *  - An item modified after RUN_WINDOW_END is flagged CHANGED-SINCE and defaults
 *    to Apply?=NO — a rollback must not fling a week of live work backwards.
 *  - Untrash runs FIRST, so retired legacy containers exist again before anything
 *    is moved back into them.
 *  - Share removal and marker cleanup are opt-in flags, default OFF.
 *
 * SETUP
 *  - Add the Drive Activity scope. In the Apps Script editor: Project Settings →
 *    "Show appsscript.json" → merge the oauthScopes block from README-UNDO.md.
 *    (This file calls the REST endpoint via UrlFetchApp, so the DriveActivity
 *    advanced service does not need to be enabled.)
 *  - Run as community@thescla.org — the account that ran the refactor.
 *  - SET RUN_WINDOW_START/END below before harvesting. See README-UNDO.md §1.
 */

// ============================================================================
// CONFIG — set the window before harvesting.
// ============================================================================

/** The refactor's execute() window, ISO-8601 UTC. Widen slightly on both sides;
 *  activity outside it is ignored entirely. Read the exec run's start from the
 *  "Drive Refactor Log" Sheet creation time and its end from the last row's
 *  timestamp, then pad ~1h each way. */
var RUN_WINDOW_START = '2026-07-20T00:00:00Z';
var RUN_WINDOW_END   = '2026-07-29T23:59:59Z';

var ROOT_FOLDER_ID = '1i2Y4cx2bg2qqopCFTq-5SbP4e7SMTFWu'; // Community Team Folder

/** Legacy shared roots the refactor absorbed. Queried as activity ancestors too,
 *  so moves recorded against the old location are also picked up. */
var SOURCE_ROOTS = [
  '1lqXCKzPC5bwVfFCRu60aFgLyxRT8FEEx', // Community & Learning SCLA
  '1tLn-UcNvWtlRi0WHwJhyzS_rXQxV3-VA', // Marketing SCLA
  '1zznScJ44VDAIGyIu5WspIQ4_OjbJfClF', // Chapter Interns
  '1vPVQMY5xs1ecF0GSQQyAdYSt7liYepPv'  // Accreditation SCLA
];

/** Editors the refactor added to the CT root (shareRootWithOwners_). Removing
 *  them is OPT-IN: some may have been editors before the refactor, and the
 *  Activity API's permission records don't reliably say which. */
var UNDO_SHARES = false;
var OWNER_EMAILS = [
  'awestby@thescla.org', 'ilomax@thescla.org', 'yordonez@thescla.org',
  'jheath@thescla.org', 'mgueta@thescla.org', 'membership@thescla.org'
];

/** Trash the "MOVED — see Community Team Folder" markers the refactor dropped in
 *  each legacy root. Opt-in: harmless to leave, and they're useful signage if the
 *  rollback turns out to be partial. */
var UNDO_MARKERS = false;

/** Trash the folders the refactor created (the 01–09 tree), once empty. Left ON:
 *  a rollback that leaves the new tree standing is confusing. Empty-only, so a
 *  folder holding anything the rollback couldn't move survives and gets flagged. */
var UNDO_CREATED_FOLDERS = true;

/** Move an item back even if it was edited after the run. Default false — those
 *  rows harvest as Apply?=NO and you opt in per row in the Sheet instead. */
var ALLOW_CHANGED_SINCE = false;

var TIME_BUDGET_MS = 4.5 * 60 * 1000;
var PLAN_SHEET = 'UNDO PLAN';

// Phase ordering — untrash before move-back, so restore targets exist.
var PHASE = { UNTRASH: 1, MOVE_BACK: 2, RENAME_BACK: 3, TRASH_CREATED: 4, MARKER: 5, SHARE: 6 };

// ============================================================================
// ENTRY POINTS
// ============================================================================

var DRY_RUN = true;

function harvest()      { withLock_(harvest_); }
function undoDryRun()   { DRY_RUN = true;  withLock_(apply_); }
function undoExecute()  { DRY_RUN = false; withLock_(apply_); }

function reset() {
  deleteResumeTriggers_();
  var p = PropertiesService.getScriptProperties();
  var i = 0;
  while (p.getProperty('u_ckpt_' + i) !== null) p.deleteProperty('u_ckpt_' + i++);
  p.deleteProperty('u_ckpt_mode');
  Logger.log('Undo checkpoints and resume triggers cleared. (Plan Sheet kept.)');
}

function withLock_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) { Logger.log('Another undo pass is active; exiting.'); return; }
  try { fn(); } finally { lock.releaseLock(); }
}

// ============================================================================
// PHASE 0 — HARVEST. Read-only: Drive Activity → the UNDO PLAN Sheet.
// ============================================================================

var REPORT = [];
var startedAt = 0;
var props = null;

function harvest_() {
  startedAt = Date.now();
  props = PropertiesService.getScriptProperties();
  REPORT = [];
  log_('===== ROLLBACK HARVEST — window ' + RUN_WINDOW_START + ' … ' + RUN_WINDOW_END + ' =====');

  var acts = [];
  var ancestors = [ROOT_FOLDER_ID].concat(SOURCE_ROOTS);
  for (var i = 0; i < ancestors.length; i++) {
    try {
      var got = queryActivity_(ancestors[i]);
      log_('  ancestor ' + ancestors[i] + ' → ' + got.length + ' activities');
      acts = acts.concat(got);
    } catch (e) {
      log_('  ANCESTOR FAILED ' + ancestors[i] + ': ' + e);
      REPORT.push(['HARVEST-ERROR', ancestors[i], String(e).slice(0, 200)]);
    }
  }

  var rows = buildPlan_(dedupeActivities_(acts));
  rows = rows.concat(syntheticRows_());
  rows.sort(function (a, b) { return a[0] - b[0]; });

  writePlanSheet_(rows);
  log_('===== Harvest done. ' + rows.length + ' planned reversals. REVIEW THE SHEET, then undoDryRun(). =====');
}

/** Drive Activity API v2 :query, paged. consolidationStrategy=none so each
 *  action stays discrete and individually invertible. */
function queryActivity_(ancestorId) {
  var out = [], pageToken = null, guard = 0;
  do {
    if (outOfTime_()) { log_('  time budget hit mid-harvest — widen nothing, just re-run harvest()'); break; }
    var body = {
      ancestorName: 'items/' + ancestorId,
      consolidationStrategy: { none: {} },
      pageSize: 100,
      filter: 'time >= "' + RUN_WINDOW_START + '" AND time <= "' + RUN_WINDOW_END + '" ' +
              'AND detail.action_detail_case:(MOVE RENAME DELETE CREATE)'
    };
    if (pageToken) body.pageToken = pageToken;

    var res = withRetry_(function () {
      return UrlFetchApp.fetch('https://driveactivity.googleapis.com/v2/activity:query', {
        method: 'post',
        contentType: 'application/json',
        headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
        payload: JSON.stringify(body),
        muteHttpExceptions: true
      });
    });
    var code = res.getResponseCode();
    if (code !== 200) throw new Error('activity:query HTTP ' + code + ' — ' + res.getContentText().slice(0, 300));

    var json = JSON.parse(res.getContentText());
    (json.activities || []).forEach(function (a) { out.push(a); });
    pageToken = json.nextPageToken || null;
  } while (pageToken && ++guard < 200);
  return out;
}

/** Same action can surface under more than one ancestor query. */
function dedupeActivities_(acts) {
  var seen = {}, out = [];
  acts.forEach(function (a) {
    var k = JSON.stringify([a.timestamp || (a.timeRange && a.timeRange.endTime), a.targets, a.actions]);
    if (seen[k]) return;
    seen[k] = 1; out.push(a);
  });
  return out;
}

/** Turn activities into plan rows. One row per invertible action. */
function buildPlan_(acts) {
  var rows = [];
  acts.forEach(function (act) {
    var when = act.timestamp || (act.timeRange && act.timeRange.endTime) || '';
    var byUs = actorIsCurrentUser_(act);
    (act.actions || []).forEach(function (action) {
      var d = action.detail || {};
      var tgt = itemOf_(action.target) || itemOf_((act.targets || [])[0]);
      if (!tgt.id) return;
      var t = action.timestamp || when;
      var note = byUs ? '' : 'actor was NOT this account — verify before applying';
      var conf = byUs ? 'HIGH' : 'LOW';

      if (d.move) {
        var from = parentIdsOf_(d.move.addedParents);     // where the refactor put it
        var to   = parentIdsOf_(d.move.removedParents);   // where it was before
        if (!to.length) {
          rows.push(row_(PHASE.MOVE_BACK, 'MOVE-BACK', tgt.id, tgt.title, from[0] || '', '', '', t,
            'LOW', 'no removedParents recorded — original parent unknown', 'NO'));
          return;
        }
        if (to.length > 1) note = joinNote_(note, 'item had ' + to.length + ' parents; restoring the first, re-add the rest by hand');
        rows.push(row_(PHASE.MOVE_BACK, 'MOVE-BACK', tgt.id, tgt.title, from[0] || '', to[0],
          parentTitleOf_(d.move.removedParents, 0), t, conf, note, conf === 'HIGH' ? 'YES' : 'NO'));

      } else if (d.rename) {
        rows.push(row_(PHASE.RENAME_BACK, 'RENAME-BACK', tgt.id, d.rename.newTitle || tgt.title, '',
          d.rename.oldTitle || '', d.rename.oldTitle || '', t, conf,
          joinNote_(note, 'restore title: "' + (d.rename.oldTitle || '?') + '"'),
          (conf === 'HIGH' && d.rename.oldTitle) ? 'YES' : 'NO'));

      } else if (d.delete) {
        var perm = d.delete.type === 'PERMANENT_DELETE';
        rows.push(row_(PHASE.UNTRASH, 'UNTRASH', tgt.id, tgt.title, '', '', '', t,
          perm ? 'LOW' : conf,
          perm ? 'PERMANENTLY DELETED — not recoverable by script; ask a Workspace admin (~25-day window)'
               : joinNote_(note, 'restore from trash'),
          (!perm && conf === 'HIGH') ? 'YES' : 'NO'));

      } else if (d.create && UNDO_CREATED_FOLDERS) {
        var isFolder = !!(tgt.mimeType === 'application/vnd.google-apps.folder' || tgt.isFolder);
        if (!isFolder) return; // the refactor created no files except the markers, handled separately
        rows.push(row_(PHASE.TRASH_CREATED, 'TRASH-CREATED-FOLDER', tgt.id, tgt.title, '', '', '', t, conf,
          joinNote_(note, 'folder created by the refactor — trashed only if empty'),
          conf === 'HIGH' ? 'YES' : 'NO'));
      }
    });
  });
  return rows;
}

/** Rows that don't come from activity: markers and share removal. */
function syntheticRows_() {
  var rows = [];
  if (UNDO_MARKERS) {
    SOURCE_ROOTS.forEach(function (rid) {
      try {
        var it = DriveApp.getFolderById(rid).getFilesByName('MOVED — see Community Team Folder');
        while (it.hasNext()) {
          var f = it.next();
          rows.push(row_(PHASE.MARKER, 'TRASH-MARKER', f.getId(), f.getName(), rid, '', '', '', 'HIGH',
            'signage the refactor left in ' + rid, 'YES'));
        }
      } catch (e) { REPORT.push(['HARVEST-ERROR', 'marker scan ' + rid, String(e).slice(0, 200)]); }
    });
  }
  if (UNDO_SHARES) {
    OWNER_EMAILS.forEach(function (email) {
      rows.push(row_(PHASE.SHARE, 'REMOVE-EDITOR', ROOT_FOLDER_ID, email, '', email, email, '', 'LOW',
        'may have been an editor BEFORE the refactor — confirm before applying', 'NO'));
    });
  }
  return rows;
}

function row_(phase, op, id, name, fromParent, target, targetName, when, conf, note, apply) {
  return [phase, op, id, name, fromParent, target, targetName, when, conf, note || '', apply];
}

function joinNote_(a, b) { return a ? a + '; ' + b : b; }

function itemOf_(t) {
  if (!t || !t.driveItem) return { id: '', title: '' };
  return {
    id: String(t.driveItem.name || '').replace(/^items\//, ''),
    title: t.driveItem.title || '',
    mimeType: t.driveItem.mimeType || '',
    isFolder: !!t.driveItem.driveFolder
  };
}

function parentIdsOf_(list) {
  return (list || []).map(function (p) {
    if (p.driveItem) return String(p.driveItem.name || '').replace(/^items\//, '');
    if (p.drive)     return String(p.drive.name || '').replace(/^drives\//, '');
    return '';
  }).filter(function (x) { return !!x; });
}

function parentTitleOf_(list, i) {
  var p = (list || [])[i];
  if (!p) return '';
  return (p.driveItem && p.driveItem.title) || (p.drive && p.drive.title) || '';
}

function actorIsCurrentUser_(act) {
  var actors = act.actors || [];
  for (var i = 0; i < actors.length; i++) {
    var u = actors[i].user;
    if (u && u.knownUser && u.knownUser.isCurrentUser) return true;
  }
  return false;
}

// ============================================================================
// PHASES 1–6 — APPLY. Reads the (human-edited) plan Sheet back.
// ============================================================================

function apply_() {
  startedAt = Date.now();
  props = PropertiesService.getScriptProperties();
  REPORT = [];
  var done = loadCheckpoint_();
  log_('===== ROLLBACK ' + (DRY_RUN ? 'DRY RUN (no changes)' : 'EXECUTE') +
       ' — resuming past ' + Object.keys(done).length + ' rows =====');

  var plan = readPlanSheet_();
  if (!plan.length) { log_('No UNDO PLAN sheet or no rows. Run harvest() first.'); return; }

  plan.sort(function (a, b) { return Number(a[0]) - Number(b[0]); });

  var timedOut = false;
  for (var i = 0; i < plan.length; i++) {
    if (outOfTime_()) { timedOut = true; break; }
    var r = plan[i];
    var key = r[1] + ':' + r[2] + ':' + i;
    if (done[key]) continue;
    if (String(r[10]).toUpperCase() !== 'YES') { record_('SKIP (Apply?=NO)', r[3], r[1]); done[key] = 1; continue; }
    try { applyRow_(r); } catch (e) { record_('ERROR', r[3], r[1] + ' — ' + String(e).slice(0, 160)); }
    done[key] = 1;
  }

  flushReport_();
  if (timedOut) {
    saveCheckpoint_(done); scheduleResume_();
    log_('Time budget reached — checkpointed. A resume trigger continues automatically.');
  } else {
    clearCheckpoint_(); deleteResumeTriggers_();
    log_('===== Rollback pass done. ' + REPORT.length + ' actions. =====');
  }
}

function applyRow_(r) {
  var op = r[1], id = String(r[2]), name = r[3], fromParent = String(r[4] || ''), target = String(r[5] || '');

  if (op === 'REMOVE-EDITOR') {
    if (DRY_RUN) { record_('REMOVE-EDITOR (predicted)', target, ROOT_FOLDER_ID); return; }
    withRetry_(function () { DriveApp.getFolderById(ROOT_FOLDER_ID).removeEditor(target); });
    record_('REMOVE-EDITOR', target, 'CT root'); return;
  }

  var item = getItemById_(id);
  if (!item) { record_('GONE', name, id + ' — not found or not accessible'); return; }

  if (op === 'UNTRASH') {
    if (!item.isTrashed()) { record_('SKIP (not trashed)', name, id); return; }
    if (DRY_RUN) { record_('UNTRASH (predicted)', name, id); return; }
    withRetry_(function () { item.setTrashed(false); });
    record_('UNTRASH', name, 'restored to its pre-trash parent'); return;
  }

  if (op === 'RENAME-BACK') {
    if (!target) { record_('SKIP (no old title)', name, id); return; }
    if (item.getName() === target) { record_('SKIP (already named)', target, id); return; }
    if (item.getName() !== name) {
      record_('CONFLICT-RENAMED-SINCE', item.getName(), 'expected "' + name + '" — left alone'); return;
    }
    if (DRY_RUN) { record_('RENAME-BACK (predicted)', item.getName(), '→ ' + target); return; }
    withRetry_(function () { item.setName(target); });
    record_('RENAME-BACK', name, '→ ' + target); return;
  }

  if (op === 'MOVE-BACK') {
    if (!target) { record_('SKIP (no restore target)', name, id); return; }
    if (!ALLOW_CHANGED_SINCE && changedSinceRun_(item)) {
      record_('CHANGED-SINCE', name, 'edited after the run — set ALLOW_CHANGED_SINCE or flip the row by hand'); return;
    }
    var cur = currentParentId_(item);
    if (cur === target) { record_('SKIP (already home)', name, target); return; }
    if (fromParent && cur && cur !== fromParent) {
      record_('CONFLICT-MOVED-SINCE', name, 'now in ' + cur + ', refactor left it in ' + fromParent + ' — left alone'); return;
    }
    var dest = getFolderOrNull_(target);
    if (!dest) { record_('DEST-MISSING', name, 'restore parent ' + target + ' not found — untrash it first'); return; }
    if (dest.isTrashed()) { record_('DEST-TRASHED', name, 'restore parent ' + target + ' is in the trash — untrash it first'); return; }
    if (DRY_RUN) { record_('MOVE-BACK (predicted)', name, '→ ' + dest.getName()); return; }
    try {
      withRetry_(function () { item.moveTo(dest); });
      record_('MOVE-BACK', name, '→ ' + dest.getName());
    } catch (e) {
      record_('OWNER-BLOCKED', name, 'cannot move (not owner) → ' + dest.getName() + ': ' + String(e).slice(0, 100));
    }
    return;
  }

  if (op === 'TRASH-CREATED-FOLDER' || op === 'TRASH-MARKER') {
    if (item.isTrashed()) { record_('SKIP (already trashed)', name, id); return; }
    if (op === 'TRASH-CREATED-FOLDER' && !isFolderEmpty_(item)) {
      record_('TRASH-SKIPPED (not empty)', name, 'still holds items the rollback could not move — inspect'); return;
    }
    if (DRY_RUN) { record_(op + ' (predicted)', name, id); return; }
    withRetry_(function () { item.setTrashed(true); });
    record_(op, name, 'reversible from trash'); return;
  }

  record_('UNKNOWN-OP', name, op);
}

// ============================================================================
// PLAN SHEET I/O
// ============================================================================

var PLAN_HEADERS = ['Phase', 'Op', 'ItemID', 'Name', 'RefactorParent', 'Target',
                    'TargetName', 'ActivityTime', 'Confidence', 'Note', 'Apply?'];

function writePlanSheet_(rows) {
  var ss = SpreadsheetApp.create('Drive Refactor — UNDO PLAN ' + RUN_WINDOW_START.slice(0, 10));
  props.setProperty('undo_plan_id', ss.getId());
  var sh = ss.getSheets()[0];
  sh.setName(PLAN_SHEET);
  sh.appendRow(PLAN_HEADERS);
  if (rows.length) sh.getRange(2, 1, rows.length, PLAN_HEADERS.length).setValues(rows);
  sh.setFrozenRows(1);
  sh.autoResizeColumns(1, PLAN_HEADERS.length);
  if (REPORT.length) {
    var errs = ss.insertSheet('HARVEST NOTES');
    errs.appendRow(['Kind', 'Subject', 'Detail']);
    errs.getRange(2, 1, REPORT.length, 3).setValues(REPORT);
  }
  REPORT = [];
  log_('UNDO PLAN: ' + ss.getUrl());
}

function readPlanSheet_() {
  var id = props.getProperty('undo_plan_id');
  if (!id) return [];
  var sh;
  try { sh = SpreadsheetApp.openById(id).getSheetByName(PLAN_SHEET); } catch (e) { return []; }
  if (!sh || sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, PLAN_HEADERS.length).getValues();
}

// ============================================================================
// HELPERS
// ============================================================================

function getItemById_(id) {
  try { return DriveApp.getFileById(id); }
  catch (e) { try { return DriveApp.getFolderById(id); } catch (e2) { return null; } }
}

function getFolderOrNull_(id) {
  try { return DriveApp.getFolderById(id); } catch (e) { return null; }
}

function currentParentId_(item) {
  try {
    var p = item.getParents();
    return p.hasNext() ? p.next().getId() : '';
  } catch (e) { return ''; }
}

function changedSinceRun_(item) {
  try { return item.getLastUpdated().getTime() > new Date(RUN_WINDOW_END).getTime(); }
  catch (e) { return false; }
}

function isFolderEmpty_(folder) {
  try { return !folder.getFiles().hasNext() && !folder.getFolders().hasNext(); }
  catch (e) { return false; }
}

function withRetry_(fn) {
  var delay = 500;
  for (var i = 0; i < 5; i++) {
    try { return fn(); }
    catch (e) {
      if (i === 4 || !/rate|quota|timed? ?out|internal|503|500/i.test(String(e))) throw e;
      Utilities.sleep(delay); delay *= 2;
    }
  }
}

function outOfTime_() { return Date.now() - startedAt > TIME_BUDGET_MS; }

// ---- checkpoint / resume ---------------------------------------------------

function loadCheckpoint_() {
  var done = {}, i = 0, chunk;
  while ((chunk = props.getProperty('u_ckpt_' + i++)) !== null)
    chunk.split(',').forEach(function (k) { if (k) done[k] = 1; });
  return done;
}

function saveCheckpoint_(done) {
  var keys = Object.keys(done), CHUNK = 200, n = 0;
  for (var i = 0; i < keys.length; i += CHUNK)
    props.setProperty('u_ckpt_' + n++, keys.slice(i, i + CHUNK).join(','));
  props.setProperty('u_ckpt_mode', DRY_RUN ? 'dry' : 'exec');
}

function clearCheckpoint_() {
  var i = 0;
  while (props.getProperty('u_ckpt_' + i) !== null) props.deleteProperty('u_ckpt_' + i++);
  props.deleteProperty('u_ckpt_mode');
}

function scheduleResume_() {
  deleteResumeTriggers_();
  ScriptApp.newTrigger('undoResume_').timeBased().after(60 * 1000).create();
}

function undoResume_() {
  var mode = PropertiesService.getScriptProperties().getProperty('u_ckpt_mode');
  if (mode === 'exec') undoExecute(); else if (mode === 'dry') undoDryRun();
}

function deleteResumeTriggers_() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'undoResume_') ScriptApp.deleteTrigger(t);
  });
}

// ---- reporting -------------------------------------------------------------

function record_(action, item, detail) {
  REPORT.push([action, item, detail || '']);
  log_('[' + action + '] ' + item + (detail ? '  ' + detail : ''));
}

function log_(msg) { Logger.log(msg); }

function flushReport_() {
  var name = DRY_RUN ? 'UNDO LOG (DRY RUN)' : 'UNDO LOG';
  var key = 'undo_report_' + (DRY_RUN ? 'dry' : 'exec');
  var ssId = props.getProperty(key), ss;
  try { ss = ssId ? SpreadsheetApp.openById(ssId) : SpreadsheetApp.create(name); }
  catch (e) { ss = SpreadsheetApp.create(name); }
  props.setProperty(key, ss.getId());

  var sh = ss.getSheets()[0];
  if (sh.getLastRow() === 0) sh.appendRow(['Action', 'Item', 'Detail']);
  if (REPORT.length) sh.getRange(sh.getLastRow() + 1, 1, REPORT.length, 3).setValues(REPORT);
  log_('Report: ' + ss.getUrl());
}
