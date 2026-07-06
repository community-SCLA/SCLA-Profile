# Community Team Drive — Folder Refactor (Google Apps Script)

`community-team-folder-refactor.gs` restructures the live **Community Team**
Google Drive folder to match the hierarchy in
[`projects/drive-review-brief.md`](../../projects/drive-review-brief.md).

It builds the 9 initiative folders + `_Marketing & Brand`, routes every named
document into its single home, archives superseded/`ARCHIVE`-labeled files into
the right `_Archive/` subfolder, and trashes the items marked stale (NIC, Voyije).

## Deploy & run

You don't "deploy" this as a web app — it's a script you run a couple of times
from the Apps Script editor. Pick **Option A (editor, ~5 min, recommended)** for a
one-time cleanup, or **Option B (clasp CLI)** if you'd rather keep it in this repo
and push from your terminal.

### Before you start — prerequisites

- A Google account that can **edit** the Community Team Drive folder *and* every
  file being moved. Moving a file you can view-but-not-edit will fail — run as an
  account with Manager/Content-manager access to the Shared Drive (or the folder
  owner if it's in My Drive).
- The **folder ID**. Open the Community Team folder in Drive; the URL looks like
  `https://drive.google.com/drive/folders/`**`1AbC...XyZ`** — copy the bold part.

### Option A — Apps Script editor (recommended)

1. Go to **[script.google.com](https://script.google.com)** → **New project**.
2. Rename it (top-left) to e.g. `Community Team Drive Refactor`.
3. Delete the default `function myFunction() {}` in `Code.gs`, then paste in the
   entire contents of `community-team-folder-refactor.gs`. Click **Save** (💾).
4. Near the top, set:
   ```js
   var ROOT_FOLDER_ID = '1AbC...XyZ'; // ← your folder ID from above
   ```
   Save again.
5. **Dry run first.** In the function dropdown (toolbar, next to ▶ Run) choose
   **`dryRun`** → click **Run**.
   - The first run triggers an **authorization** prompt. Click **Review
     permissions** → choose your account → on the "Google hasn't verified this
     app" screen click **Advanced** → **Go to (project name) — unsafe** →
     **Allow**. (This is expected for a personal script you wrote; the scopes it
     requests are Drive + Sheets, listed under [Authorization scopes](#authorization-scopes).)
   - `dryRun` changes **nothing**. It writes the full plan to the
     **Execution log** (View → Logs, or `Ctrl/Cmd+Enter`) *and* to a Google Sheet
     named **"Drive Refactor Log (DRY RUN)"** in your Drive.
6. **Review the plan.** Open that Sheet. Every row is one planned action
   (`CREATE FOLDER`, `MOVE`, `ARCHIVE`, `TRASH`, `SKIP`, `UNMATCHED`, `ERROR`).
   - Any **`UNMATCHED`** row is a file no rule caught. Add a line to `MOVE_RULES`
     in the script — `{ match: '<part of the file name>', dest: 'Folder/Path' }` —
     save, and run `dryRun` again. Repeat until the plan reads the way you want.
7. **Execute for real.** Switch the dropdown to **`execute`** → **Run**. It
   creates the folders, moves files into their single home, archives the
   `ARCHIVE`-labeled files, and trashes the stale ones. Results are written to a
   **"Drive Refactor Log"** Sheet.
8. **Verify.** Open the Community Team folder and spot-check a few moves. Trashed
   items sit in Drive Trash (recoverable ~30 days) if anything looks wrong.

> Tip: `execute()` is idempotent. If you add more rules and run it again, files
> already in place are reported as `SKIP (already home)` and nothing is disturbed.

### Option B — clasp CLI (keep it in this repo)

Use this if you want to edit the `.gs` in your editor and push it to Apps Script
from the terminal.

```bash
# 1. Install Google's Apps Script CLI (one time)
npm install -g @google/clasp

# 2. Log in (opens a browser for Google auth)
clasp login

# 3. From this folder, create a standalone Apps Script project
cd scripts/drive-refactor
clasp create --type standalone --title "Community Team Drive Refactor"
#   → writes .clasp.json (the script ID) and appsscript.json here.
#     Do NOT commit .clasp.json — it's gitignored below.

# 4. clasp expects a .js/.gs extension it recognizes; push the source
clasp push

# 5. Open the project in the browser to set ROOT_FOLDER_ID and run
clasp open
```

Then in the opened editor, set `ROOT_FOLDER_ID`, and run `dryRun` → review →
`execute` exactly as in Option A (steps 4–8). You can also run headless once the
folder ID is set:

```bash
clasp run dryRun     # requires enabling the Apps Script API + a GCP project
clasp run execute
```

`clasp run` needs the Apps Script API turned on
(<https://script.google.com/home/usersettings>) and a standard GCP project linked
to the script; if that's more setup than you want, just use `clasp open` and click
**Run** in the editor.

Add a gitignore entry so clasp's local credentials/IDs don't get committed:

```
# scripts/drive-refactor/.gitignore
.clasp.json
.clasprc.json
```

### Authorization scopes

The script asks for these the first time you run it:

| Scope | Why |
| --- | --- |
| `https://www.googleapis.com/auth/drive` | Create folders, move files, trash stale files |
| `https://www.googleapis.com/auth/spreadsheets` | Write the "Drive Refactor Log" report Sheet |

Apps Script infers them automatically — you don't declare them by hand. If you
want to pin them explicitly for `clasp`, add an `oauthScopes` array to
`appsscript.json`.

### Troubleshooting

| Symptom | Fix |
| --- | --- |
| `Set ROOT_FOLDER_ID ...` thrown immediately | You didn't replace the placeholder folder ID. |
| `Access denied` / `does not have permission` on a move | Run as an account with **edit** rights to that file / the Shared Drive. |
| A file landed in `UNMATCHED` | Its Drive name differs from the brief — add a `MOVE_RULES` entry and re-run `dryRun`. |
| `destination not in tree: ...` (ERROR row) | A rule's `dest` path has a typo — it must exactly match a path in `FOLDER_TREE`. |
| "Exceeded maximum execution time" (6-min limit) | Large Drives can time out. Re-run — it's idempotent and picks up where it left off; or temporarily narrow the run. |
| Want to undo `execute()` | Trashed files are in Drive Trash (~30 days). Moves can be reversed by re-running with adjusted rules, or manually. There is no automatic rollback — that's why `dryRun()` comes first. |

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
