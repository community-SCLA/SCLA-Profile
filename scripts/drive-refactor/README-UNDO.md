# Rolling back the Drive refactor

`undo.gs` reverses a completed `execute()` run of
[`community-team-folder-refactor.gs`](./community-team-folder-refactor.gs).

**Why a second script and not an `undo()` in the first one:** the refactor logs
`[Action, Item name, Destination]` and never records the file ID or the parent an
item was moved *out of*. Its own log therefore cannot drive a reversal. The prior
state is reconstructed from the **Drive Activity API v2**, which records
`move.removedParents` and `rename.oldTitle` per item — the only faithful record of
where things were.

---

## 1. Set the run window first

`undo.gs` only inverts activity inside `RUN_WINDOW_START … RUN_WINDOW_END`.
Get the real bounds before harvesting:

1. Open the **"Drive Refactor Log"** Sheet (the exec one, not `(DRY RUN)`).
   Its **creation time** is when `execute()` first ran — File → Version history.
2. The **last row's** action is roughly when it finished (a checkpointed run may
   have resumed over several hours; take the last resume).
3. Pad ~1 hour each side and write both into the constants at the top of `undo.gs`.

A window that is too wide sweeps in unrelated activity — it will surface as extra
plan rows, which you delete in the review step. A window that is too narrow
silently misses moves. Prefer too wide.

## 2. Add the Drive Activity scope

Apps Script editor → **Project Settings** → check *"Show appsscript.json"* →
open the file and merge:

```json
{
  "timeZone": "America/New_York",
  "oauthScopes": [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.activity.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/script.scriptapp",
    "https://www.googleapis.com/auth/script.external_request"
  ],
  "exceptionLogging": "STACKDRIVER"
}
```

`undo.gs` calls the Activity REST endpoint through `UrlFetchApp`, so the
DriveActivity *advanced service* does not need to be enabled — but
`script.external_request` does need to be in scopes. Re-authorize when prompted.

Run as **community@thescla.org** — the account that ran the refactor. Activity
attributed to any other actor is harvested with `Confidence=LOW` and
`Apply?=NO`.

## 3. Run order

| # | Call | Writes to Drive? | What it does |
|---|---|---|---|
| 1 | `harvest()` | No | Reads Activity, writes the **UNDO PLAN** Sheet |
| 2 | *you* | — | Review the Sheet; set `Apply?` per row |
| 3 | `undoDryRun()` | No | Replays the plan against live Drive, predicts + flags conflicts |
| 4 | `undoExecute()` | Yes | Applies the `Apply?=YES` rows in phase order |

`reset()` clears checkpoints and the resume trigger. It leaves the plan Sheet alone.

### The plan Sheet is the gate

`harvest()` writes one row per reversal and **`undoExecute()` acts only on rows
whose `Apply?` cell reads `YES`.** Anything flagged `LOW` confidence harvests as
`NO`. Delete rows, flip cells, edit `Target` — the Sheet is the plan of record, not
the script.

| Column | Meaning |
|---|---|
| `Phase` | Execution order: 1 untrash → 2 move-back → 3 rename-back → 4 trash created folders → 5 markers → 6 shares |
| `Op` | `UNTRASH` / `MOVE-BACK` / `RENAME-BACK` / `TRASH-CREATED-FOLDER` / `TRASH-MARKER` / `REMOVE-EDITOR` |
| `RefactorParent` | Where the refactor left the item — used to detect post-run re-filing |
| `Target` | Restore destination (folder ID), or the old title for `RENAME-BACK` |
| `Confidence` | `HIGH` when the actor was this account and the source parent was recorded |
| `Apply?` | `YES`/`NO` — the only thing `undoExecute()` reads to decide |

Untrash is phase 1 on purpose: retired legacy containers must exist again before
anything can be moved back into them.

## 4. Conflict handling

A week of live work sits on top of this refactor. `undoDryRun()` and
`undoExecute()` both refuse to touch:

- **`CONFLICT-MOVED-SINCE`** — the item's current parent isn't where the refactor
  put it, so a human re-filed it. Left alone.
- **`CHANGED-SINCE`** — edited after `RUN_WINDOW_END`. Left alone unless you set
  `ALLOW_CHANGED_SINCE = true` or flip that single row to `YES` yourself.
- **`CONFLICT-RENAMED-SINCE`** — current title isn't the one the refactor set.
- **`DEST-MISSING` / `DEST-TRASHED`** — restore parent isn't there yet. Untrash it
  and re-run; the pass is idempotent.
- **`OWNER-BLOCKED`** — the item belongs to someone else. Logged for a worklist;
  the owner has to move it.

Nothing is ever permanently deleted. Every "delete" in this script is
`setTrashed(true)`.

## 5. What a rollback cannot recover

- **Permanently deleted items.** The refactor only ever called `setTrashed(true)`,
  so this should be empty — but if anyone emptied the trash since, those rows
  harvest as `LOW` with a note. A Workspace admin can restore for ~25 days after
  the trash was emptied; after that they are gone.
- **Trash auto-purge.** Items the refactor trashed self-destruct 30 days after
  trashing. If `execute()` ran on 2026-07-20, that clock runs out around
  **2026-08-19**. Phase 1 (`UNTRASH`) is the time-critical part of this rollback —
  it is worth running even if the rest waits.
- **Items outside the Activity record.** Activity is scoped to items the account
  can see. Anything living in another user's My Drive that was never shared in
  won't appear; the `OWNER-BLOCKED` rows in the original run's OWNER WORKLIST tab
  are the cross-check for that set.
- **Multi-parent items.** Drive's legacy multi-parenting: if an item had several
  parents, `undo.gs` restores the first and notes the rest. Re-add by hand.
- **Pre-existing editors.** `REMOVE-EDITOR` rows default to `Apply?=NO` because the
  Activity record does not reliably say who was an editor *before* the refactor.

## 6. Fallback if the Activity window has aged out

The repo holds an approximate pre-refactor map, good enough to rebuild most of the
tree by hand:

- **`CONTAINER_ROUTES` keys in the refactor script are the original parent folder
  IDs** for everything routed by container — the largest slice of the run.
- [`ANNOTATED-WORKTREE.md`](./ANNOTATED-WORKTREE.md) §2 annotates sources with `←`
  in prose for most per-file decisions.

Neither covers the per-file `ID_ROUTES` set completely, and both are a 2026-07-20
snapshot. Treat this as reconstruction, not reversal.
