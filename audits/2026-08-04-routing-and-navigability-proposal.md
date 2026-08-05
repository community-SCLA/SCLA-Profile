# PROPOSAL — Routing cleanup and workspace navigability

**Date:** 2026-08-04 · **Status:** EXECUTED 2026-08-04 — see §6 · **Audience:**
a fresh session with no memory of the conversation that produced this.

This document is a handoff, not a fix. Every finding below was independently
re-verified against live `HEAD` on 2026-08-04 — not inherited from any prior
audit. Fix items are additive and low-risk (doc/comment corrections, one
editor-only settings change); nothing here touches pipeline scripts, gates, or
tests. None of it is blocked on `render-qa/docs/PROPOSAL-agent-native-adoption-2026-08-04.md`
(the separate, still-open template-retirement proposal) — that document is
linked, not restated, in §3.

**Session-type note:** fixing §1 and §2 below edits `scripts/*.sh` comments
and (possibly) `audits/*` and `lesson-scripts/refinement-log.md`. None of
these are write-fenced outside an active build, but if
`renders-hyperframes/.build-in-progress` exists when you start, either wait
for it to clear or export `SCLA_SYSTEM_SESSION=1` per the standing write-fence
rule (`.claude/rules/video-production.md`).

---

## 1. Confirmed broken routing (verified live, 2026-08-04)

| Issue | Evidence | Fix |
|---|---|---|
| `lesson-scripts/refinement-log.md` still describes the retired `refined/`/`rendered/` folder model as current | Header `:3-9` and row `:34` (a 2026-08-04 entry) both say `refined/`/`rendered/`, but those folders don't exist anywhere on disk — the pipeline moved to `inbox/`/`ready/`/`published/` on 2026-08-04, and `lesson-scripts/README.md` already reflects that | Update the header block and any surviving `refined/`/`rendered/` prose in row text to `ready/`/`published/`, or mark old rows explicitly historical |
| Two live scripts cite the pre-2026-07-31-rename snag-log path in comments | `scripts/wistia-upload.sh:4` and `scripts/preview.sh:72` both say `render-qa/snag-log.md`, which does not exist; the real path is `render-qa/logs/snag-log.md` (already correct in all 3 skills and in `.claude/rules/video-production.md`) | One-line comment fix in each script |
| `projects/README.md` hub links to two files at the wrong path | `projects/README.md:19-20` cites `drive-review-brief.md` and `kb-integration-plan.md` as living directly under `projects/` — neither does; actual locations are `audits/drive-review-brief.md` and `member-support/kb-integration-plan.md` | Fix both links |
| `member-support/README.md` hub links `kb-integration-plan.md` at the wrong path | `member-support/README.md:16` links `../projects/kb-integration-plan.md`; the actual file is `member-support/kb-integration-plan.md` (same directory) | Fix the link |
| `PIPELINE-STATUS.md` currently drifted from live state | The committed file says 1 building / 13 STALLED; a live read-only `bash scripts/batch-status.sh` run returns 0 building / 14 STALLED right now; `git status` already shows the file modified/uncommitted | Structural, not just a one-off: only `batch-ship.sh` and `/refine-scripts` currently trigger `--write`. Decide whether to widen the regeneration trigger (e.g. also on stall-detection) rather than just re-running `--write` once |

Everything checked and found clean (root `CLAUDE.md` and
`projects/video-production/CLAUDE.md` routing tables, `docs/notion-queue.md`,
`config/endpoints.json`, the three lesson-pipeline `SKILL.md` files, the
avatar-lane deletion, `renders-hyperframes/README.md`) is **not** repeated
here — only what's actually broken is listed.

---

## 2. A stale artifact needs a disposition decision, not silent deletion

`audits/2026-08-03-video-pipeline-audit` is **untracked** (never committed).
Its central findings — `batch-status.sh` blind to the freeform lane, no stall
detector, competing status narratives across `PIPELINE-STATUS.md` /
`refinement-log.md` / `quarantine.log` / the retired Notion doc — appear to
already be implemented by the two most recent commits: `2e2cff0`
("sentinel-gated write fence; inbox/ready/published; avatar lane deleted")
and `c4d688e` ("one honest status, resumable builds, a real receipt"). Live
evidence: a current `batch-status.sh` run already reports freeform-lane
states (`career-building-is-a-repeatable-process_early-career-boost (freeform
lane) — state: freeform design written; narration not yet synthesized`) and
stall detection (`left off after **preflight**, 56 min ago`) — neither of
which the audit's own description of the tool says it could do.

**What to do:** walk that file's numbered recommendations one by one against
what's actually shipped now. For each, confirm DONE or leave OPEN. When
finished, either:
- delete the file (repo-hygiene default: deletion, not archiving — git
  history isn't even a concern here since it was never committed), or
- commit it with a one-line "superseded — see `decisions/log.md` 2026-08-04
  entries" header, if there's a reason to keep the narrative.

This document does not make that call — it's flagged for whoever executes,
because the file may still contain open items this proposal didn't have
reason to check line-by-line.

---

## 3. Explicitly out of scope

`render-qa/docs/PROPOSAL-agent-native-adoption-2026-08-04.md` — retiring the
template lane and the six candidate gate modules (`boxmodel.py`,
`check_capacity.py`, `check_slots.py`, `check_variety.py`, `build_index.py`,
`instance_templates.py`). That's a separate, already-written, still-open
proposal with its own recommended next action (its Step 1: give the copy
gates a non-compiler beat source). This document links to it and does not
duplicate or re-litigate it.

---

## 4. Workspace-folder navigability (the Explorer chaos)

Every `renders-hyperframes/<stem>/` workspace dumps 8–13 flat files at its top
level, mixing real content with pure bookkeeping:

- **Template lane** (e.g. `m1_mini-syllabus/`): `index.html`, `scenes.json` —
  content; `.build-log.tsv`, `.pin`, `hyperframes.json`, `meta.json`,
  `package.json`, `tokens.yml`, `design-contract.md` — bookkeeping, never
  hand-edited.
- **Freeform lane** (e.g.
  `build-direction-before-you-build-a-plan_early-career-boost/`): `index.html`,
  `design.md` — content; `hyperframes.json`, `meta.json`, `package.json`,
  `package-lock.json`, `tokens.yml`, `audio_request.json`, `audio_meta.json`,
  `timing.json`, `compute_timing.py` — bookkeeping.

16 of these sit as flat, unsorted-by-status siblings under one directory, with
no visual grouping by pipeline stage — which is what actually produced the
"absolute chaos" the owner hit browsing the Explorer.

**Proposed fix — editor view only, nothing on disk moves:**

```jsonc
// .vscode/settings.json — add:
"explorer.fileNesting.enabled": true,
"explorer.fileNesting.expand": false,
"explorer.fileNesting.patterns": {
  "index.html": "scenes.json, design.md, compute_timing.py, hyperframes.json, meta.json, package.json, package-lock.json, tokens.yml, design-contract.md, .pin, .build-log.tsv, audio_request.json, audio_meta.json, timing.json"
},
"files.exclude": {
  "**/__pycache__": true,
  "**/node_modules": true
}
```

This nests the bookkeeping files under `index.html`, collapsing each workspace
from ~13 visible rows to ~4 (`index.html` [expandable], `assets/`,
`compositions/`, `qa/`).

**Why folders must NOT be reorganized or renamed by status, even though that
would also declutter the tree:** the stem *is* the folder name, and `mkdir
renders-hyperframes/<stem>` is the actual build-concurrency lock
(`decisions/log.md` 2026-07-29 "Working artifacts lose their date suffix";
pinned by `render-qa/tests/test_stem.py`). Grouping by status has to stay in
the reader tools that already do it correctly —
`bash scripts/batch-status.sh`, `bash scripts/review.sh`, the generated
`PIPELINE-STATUS.md` — never in physical layout. The tree's only job is to be
low-noise once you already know which workspace you're opening; deciding
*which* workspace is a `batch-status.sh`/`review.sh` question, not an Explorer
question.

---

## 5. Recommended order + verification

Mostly independent — order barely matters, with one dependency: resolve §2's
disposition call before touching `refinement-log.md`'s vocabulary in §1,
since the stale audit also names that file.

1. §1 fixes (5 small, independent edits)
2. §2 disposition call on the stale audit file
3. §4 `.vscode/settings.json` addition

**Verification, per item:**
- §1/§2: `grep -rn` the corrected string across the repo returns zero stale
  hits; `bash scripts/lint-refs.sh` still exits 0; corrected links resolve
  with `test -e <path>`.
- §4: open a template-lane and a freeform-lane workspace in the Explorer and
  confirm both collapse to ~4 top-level rows; confirm `__pycache__` and
  `node_modules` no longer appear anywhere in the tree; confirm no pipeline
  script, gate, or test was touched (`git status` shows only
  `.vscode/settings.json` changed for this item).

---

## 6. Execution record — 2026-08-04

Executed in one pass. No build was in flight, so nothing was write-fenced.
`lint-refs.sh` ran before and after: **same 3 warnings both times, no new
failure introduced** (the 3 are pre-existing — see "Found while executing").

### §1 — done

| Item | Outcome |
|---|---|
| `refinement-log.md` folder vocabulary | Header now marks pre-2026-08-04 rows historical; the three rows *dated* 2026-08-04 that the header's disclaimer did not cover were corrected to real disk state — `build-direction…` → `published/` (confirmed in `published.tsv`), `m2_the-value-…` and `m3_discover-experiences-…` → `ready/`. Remaining `refined/`/`rendered/` text is all in pre-2026-08-04 rows, which the header covers |
| snag-log path in `wistia-upload.sh` / `preview.sh` | Fixed to `render-qa/logs/snag-log.md`. `grep` over `scripts/`, `.claude/skills/`, `.claude/rules/` returns zero stale hits |
| `projects/README.md` broken links | Fixed |
| `member-support/README.md` broken link | **Moot** — the owner deleted `member-support/` wholesale in `50c579a` mid-execution |
| `PIPELINE-STATUS.md` drift | Regenerated with `--write`. The structural question is answered below — the answer is *not* "widen the trigger" |

Also fixed, same class: `render-lessons/SKILL.md` cited priority order as
`scripts/batch-status.sh:28`; the assignment is at line 47. Replaced the line
number with the `PRIORITY=` symbol so it cannot drift again.

### §1 item 5 — the structural decision, with evidence

**Do not widen the `--write` trigger. It cannot fix this.** Regenerating the
doc and immediately re-running `lint-refs.sh` check 14 still fails:

```
95c95
<   - last written to: 8 min ago …
>   - last written to: 9 min ago …
```

`PIPELINE-STATUS.md` embeds *relative ages* ("56 min ago", "2 h ago") and the
STALLED/building split is derived from mtime age, so the generated doc drifts
from a fresh regeneration **by the passage of time alone, with zero repo
activity**. Check 14 is therefore red in CI permanently, on a clock, and no
regeneration trigger — on build start, stall detection, or publish — changes
that.

**Recommended fix (NOT applied — it edits a gate, which this proposal put out
of scope):** make the comparison clock-insensitive rather than the doc
timeless. Normalize the volatile fields (relative-age strings, and the
building↔STALLED counts that follow from them) on both sides before diffing in
check 14, and pin it with a test that regenerates, advances the clock, and
asserts the check still passes. Per the house rule, this needs a firing test —
so it is an owner decision, not a silent edit.

### §2 — disposition: kept in `audits/`, not archived

A prior session had staged the file into a **new** `audits/_archive/` folder.
Two things had changed since this proposal was written: the file is no longer
untracked (it was committed in `7135748`), and `.claude/rules/repo-hygiene.md`
forbids creating new `_archive/` folders. Both cut against archiving.

Resolved to this document's option (b): the file lives at
`audits/2026-08-03-video-pipeline-audit.md`, alongside its dated peers (none of
which are archived), carrying a **verified walk of all 16 recommendations** —
each checked against live `HEAD`, not read off the commit messages. 13 DONE,
**3 OPEN**, which is why deletion was wrong:

1. `render-qa/quarantine.log` never clears — still 2 rows, both naming lessons
   that later published.
2. No build-subagent watchdog — no idle-kill/retry rule in `render-lessons/SKILL.md`.
3. Owner call — `m4_visibility-actions`: a full workspace exists for a script
   whose raw is still marked `SCRIPT PENDING`. Build it or scrap it?

### §4 — done, with one gap the proposal's own acceptance test caught

The settings were already in `.vscode/settings.json`. Checking them against the
stated criterion ("both lanes collapse to ~4 top-level rows") found the
freeform lane still showing 5: `.thumbnails/` and `.waveform-cache/` are
generated caches, gitignored, in neither the nesting pattern nor `files.exclude`.
Added both to `files.exclude`. Template lane verified at exactly 4 rows
(`index.html`, `assets/`, `compositions/`, `qa/`).

⚠ **`.vscode/settings.json` is gitignored** (`.gitignore:19-20` shares only
`tasks.json`). This fix is machine-local and a Codespace rebuild wipes it.

### Found while executing — not in this proposal, not fixed

- **`design-contract.md` was archived with live callers still pointing at it.**
  Commit `7135748` moved `design-system/docs/design-contract.md` to
  `docs/_archive/`, but `scripts/batch-prepare.sh:59` still runs
  `cp "$DS/docs/design-contract.md" …` when it rebuilds the scaffold — that
  `cp` now fails, and `batch-prepare.sh:41`'s freshness signature reads the
  same missing path. `scripts/check-enforcement.py`'s `GRADED` list also still
  names it, which is the single broken claim failing lint checks 10 **and** 12
  (`FAIL the live repo has 0 broken claims`). Roughly 20 more live references
  in the three skills, four agent charters and `design-system/AGENTS.md`.
  **Left alone deliberately:** un-archiving vs. finishing the retirement is
  exactly the call in `render-qa/docs/PROPOSAL-agent-native-adoption-2026-08-04.md`,
  which §3 declares out of scope. But the template lane is broken until it is
  answered.
- Two dated handoff docs still cite the old `render-qa/snag-log.md` path
  (`HANDOFF-autobatch-2026-07-28.md:147,244`). Left as dated snapshots.
- **A concurrent writer was committing to this repo during execution**
  (`50c579a`, `4bcc57b`), deleting `member-support/` and `partnerships/` and
  rewriting root `CLAUDE.md`. Anything below §5 that references those paths is
  stale for that reason, not this one.
