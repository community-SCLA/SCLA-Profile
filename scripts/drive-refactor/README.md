# Community Team Drive — Folder Refactor (Google Apps Script)

`community-team-folder-refactor.gs` restructures the live **Community Team**
Google Drive folder to match the hierarchy in
[`scla/projects/drive-review-brief.md`](../../scla/projects/drive-review-brief.md).

It builds the 9 initiative folders + `_Marketing & Brand`, routes every named
document into its single home, archives superseded/`ARCHIVE`-labeled files into
the right `_Archive/` subfolder, and trashes the items marked stale (NIC, Voyije).

## Run it

1. Go to [script.google.com](https://script.google.com) → **New project**.
2. Paste in `community-team-folder-refactor.gs`.
3. Set `ROOT_FOLDER_ID` to the Community Team folder ID — the string after
   `/folders/` in its Drive URL.
4. Run **`dryRun()`**. Nothing is changed. It writes the full plan to the
   execution log *and* to a **"Drive Refactor Log"** Google Sheet in your Drive.
   Authorize the Drive/Sheets scopes when prompted.
5. Read the log. Anything tagged **`UNMATCHED`** is a file no rule caught —
   add a line to `MOVE_RULES` (`{ match: '<part of file name>', dest: 'Folder/Path' }`)
   and re-run `dryRun()` until the plan is clean.
6. Run **`execute()`** to apply it for real.

## How routing works

| Layer | What it does |
| --- | --- |
| `FOLDER_TREE` | The target hierarchy. Folders are find-or-created (idempotent). |
| `TRASH_RULES` | Sent to Drive trash (recoverable ~30 days). |
| `ARCHIVE_RULES` | Moved into a destination `_Archive/` subfolder. |
| `MOVE_RULES` | Explicit `name-substring/regex → destination`. First match wins. |
| `COURSE_CODE_MAP` | Fallback: files named `AI101…`, `CAR103…`, `CRA201…` route by prefix. |

`MOVE_RULES` is evaluated **before** the course-code router, so specific
overrides (e.g. `PSY102 self-assessment` → Assessments) win over the generic
`PSY → Psychology & EQ` prefix rule.

## Safety notes

- **`dryRun()` changes nothing** — always run it first and review the Sheet.
- Each file gets **exactly one home**: `file.moveTo()` detaches it from all other
  parents, which also collapses the cross-posted shortcut duplicates the brief flags.
- The script is **idempotent** — a second run after a clean run is a no-op
  (`SKIP (already home)`).
- Trash is recoverable for ~30 days; nothing is permanently deleted.
- Matching is by file **name**, so rename-drift in Drive can leave a file
  `UNMATCHED`. That's intentional — it surfaces in the log instead of being
  guessed into the wrong folder.
