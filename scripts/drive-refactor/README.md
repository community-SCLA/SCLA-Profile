# Community Team Drive — Folder Refactor v2 (Google Apps Script)

`community-team-folder-refactor.gs` consolidates the live **Community Team
Folder** *and* the four legacy shared drives ("Community & Learning SCLA",
"Marketing SCLA", "Chapter Interns", "Accreditation SCLA") plus the standalone
shared files into one canonical tree.

**The map of where everything goes — and why — is
[`ANNOTATED-WORKTREE.md`](./ANNOTATED-WORKTREE.md).** Read it first; it is the
authority this script implements. It was built from a complete live inventory
(2026-07-20, ~500 items), content-verification of every suspected duplicate,
and three adversarial reviews (taxonomy, feasibility, completeness).

## What's different from v1

| | v1 | v2 |
|---|---|---|
| Scope | Community Team folder only | + 4 shared drives + standalone shared files |
| Routing | name substrings | **file-ID first** (names here have trailing spaces & twins); name rules only for post-inventory files |
| Trash | name-match, throws for non-owned files | ID-only, content-verified, capability-gated; blocked items staged in `_PENDING-OWNER-TRASH/` + owner worklist |
| Shortcuts | ignored | tri-policy: collapse (target routed) / keep-as-pointer (target unreachable but alive) / dead-flag (never silently deleted) |
| Ownership | assumed movable | dry run **predicts** MOVE vs OWNER-BLOCKED per item via the Drive API; move failures fall back to a pointer shortcut; CT folder is shared with all content owners first |
| Folders | pre-created tree | **lazy creation** — a folder exists only once something lands in it (no empty placeholders) |
| 6-min limit | re-run manually | checkpoints (chunked in Script Properties), self-scheduling resume trigger, LockService, batched Sheet logging, backoff retries |

## Setup (Apps Script editor)

1. [script.google.com](https://script.google.com) → **New project**, name it
   `Community Team Drive Refactor`, paste the whole `.gs` file.
2. **Enable the Drive advanced service**: left sidebar → **Services (+)** →
   **Drive API** → Add. (Without it the script still runs, but the dry run
   can't predict owner-blocked items — it assumes optimistically.)
3. The folder/file IDs are already baked in from the 2026-07-20 inventory —
   `ROOT_FOLDER_ID` is the Community Team Folder. Nothing to paste.
4. Run **as community@thescla.org** (owner of the Community Team Folder).

## Run order

1. **`dryRun()`** — changes nothing. First run triggers the auth prompt
   (Drive + Sheets + Triggers scopes; "unverified app" → Advanced → Allow).
   Writes **"Drive Refactor Log (DRY RUN)"** Sheet: one row per item with the
   *predicted* outcome — `MOVE`, `MOVE FOLDER`, `KEEP-AS-POINTER`,
   `COLLAPSE-SHORTCUT`, `OWNER-BLOCKED (predicted)`, `TRASH (predicted)`,
   `TRASH-BLOCKED (predicted)`, `RENAME`, `ARCHIVE`, `DEAD-OR-INVISIBLE`,
   `UNMATCHED`, `SKIP (already home)`.
2. **Review the Sheet.** `UNMATCHED` rows = files created after the inventory —
   add an `ID_ROUTES` entry (or let a NAME_RULE catch it) and re-`dryRun()`.
   Check the **OWNER WORKLIST** tab for expected blocks.
3. **`execute()`** — applies the plan. Long runs checkpoint at ~4.5 min and
   resume themselves via a one-minute trigger; just let it finish (watch the
   "Drive Refactor Log" Sheet grow). Idempotent — a re-run after a clean run
   is all `SKIP (already home)`.
4. **Work the OWNER WORKLIST** tab: `MOVE-BLOCKED` / `TRASH-BLOCKED` rows list
   what each owner (awestby@, ilomax@, jheath@, yordonez@…) must move, trash,
   or transfer. Items owned by **personal gmail accounts** cannot be
   transferred into the org — recreate/copy those (noted in the worktree §6).
5. **`reset()`** — clears checkpoints + resume triggers for a fresh full pass.

## Safety

- `dryRun()` never writes to Drive. Trash is 30-day recoverable and only ever
  by explicit, content-verified file ID — two entries additionally require a
  byte-size match with their twin before trashing (else they archive).
- Non-owner trash never throws: blocked items are staged into
  `_PENDING-OWNER-TRASH/` for the owner to empty.
- Shortcuts with unreachable targets are **flagged, never deleted** — a throw
  can't distinguish "target deleted" from "target not shared with us".
- Shared drive roots and standalone shared files are never moved (impossible
  for a non-owner) — they get organized pointer shortcuts; each emptied legacy
  drive gets a `MOVED — see Community Team Folder` marker.
- Google-Forms "(File responses)" trees move **intact** — forms bind by ID, so
  submissions keep flowing regardless of folder location.

## clasp (optional)

Same as v1: `clasp create --type standalone` in this folder, `clasp push`,
`clasp open`. Don't commit `.clasp.json` / `.clasprc.json`. If you use clasp,
also commit an `appsscript.json` with the Drive advanced service enabled:

```json
{
  "timeZone": "America/New_York",
  "dependencies": {
    "enabledAdvancedServices": [
      { "userSymbol": "Drive", "serviceId": "drive", "version": "v2" }
    ]
  },
  "exceptionLogging": "STACKDRIVER"
}
```
