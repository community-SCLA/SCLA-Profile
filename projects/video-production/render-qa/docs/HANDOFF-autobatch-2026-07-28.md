# HANDOFF — AUTO-BATCH, updated 2026-07-28 evening (certification complete)

> ## ⛔ SUPERSEDED — read `HANDOFF-owner-review-enforcement-2026-07-28.md` first
>
> **The owner reviewed this "certified" pilot later on 2026-07-28 and REJECTED
> it.** Everything below describes the state before that review and is kept as
> history. Three claims in it are now false:
>
> 1. **"Ready to ship pending sign-off" — no.** The pilot now FAILS preflight on
>    11 variety + 30 copy findings plus the in-scene silence gate. It needs a
>    rebuild, not a preview.
> 2. **The workspace path changed.** It is now
>    `renders-hyperframes/better-decisions-come-from-better-criteria_early-career-boost_**2026-07-28**/`
>    and the MP4 is `..._2026-07-28.mp4` — a stem carries exactly one date, and
>    it means the most recent action.
> 3. **Certification was necessary but not sufficient.** Three clean rebuilds
>    with zero vision-lane FAILs still shipped a video the owner called
>    "boring." The gates it passed did not measure variety, artwork, heading
>    case, list conjunctions, or in-scene silence. They do now.

Written for a session starting with **zero context**. Read this whole file,
then run `bash scripts/batch-status.sh`.

## 1. Where things stand

**The pilot is CERTIFIED and the batch is ready — pending one thing: the
owner's PILOT GATE sign-off.**

The certification bar (owner directive, 2026-07-28): the pilot must rebuild
from scratch **3 consecutive times with zero glitches**, each run verified on
actual pixels. Achieved — three full clean cycles, one per theme:

| Run | Theme | Scenes | Gates | Precheck vision | Verify | 3 vision lanes |
|---|---|---|---|---|---|---|
| 1 | horizon | 21 | all 0 | clean after 2 copy fixes | PASS, 0 violations | 0 FAILs |
| 2 | cadence | 20 | all 0 | **CLEAN first pass** | PASS, 0 violations | 0 FAILs |
| 3 | summit | 21 | all 0 | **CLEAN first pass** | PASS, 0 violations | 0 FAILs |

The summit cut is on disk awaiting preview:
`renders-hyperframes/better-decisions-come-from-better-criteria_early-career-boost_2026-07-06/`
(MP4 160.4s in `renders/`, `qa/VERIFIED` sha-256 marker written).

**To finish:** the owner previews
(`bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`),
then `bash scripts/batch-ship.sh <stem> early-career-boost --publish`
publishes the pilot, and approval covers the remaining 29-video queue per the
PILOT GATE rule.

## 1b. What exists on disk RIGHT NOW that you can view

Exactly **one** rendered build exists locally — the certified summit pilot:

- Live hyperframe (interactive, scrubbing):
  `bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`
- The verified MP4 itself:
  `renders-hyperframes/better-decisions-come-from-better-criteria_early-career-boost_2026-07-06/renders/*_2026-07-28_18-49-26.mp4`
- Its frame dump (3 stills per scene): that workspace's `qa/frames/`

**There are no other local renders.** The builds you previewed in earlier
sessions that then "disappeared" were casualties of the old state machine
(scripts moved to `rendered/` pre-publish, invisible to every tool); their
workspaces no longer exist. Their scripts were recovered into `refined/`, so
the batch rebuilds them fresh — under the new rules that can't lose them.
The 6 videos already live are on Wistia; their URLs are one command away:
`cat projects/video-production/lesson-scripts/published.tsv`.

## 2. The pipeline, end to end (who does what)

```
  lesson-scripts/<prog>/<stem>.txt          RAW INTAKE — you drop .txt scripts here
        │
        │  YOU: /refine-scripts   (or /produce-video, which chains everything)
        ▼
  lesson-scripts/<prog>/refined/<stem>.txt  BUILD QUEUE + your open review buffer
        │                                   (edit/veto scripts here any time)
        │  ═══ AUTO-BATCH loop — one video at a time, priority order ═══
        ▼
  [cold BUILD agent]                        clones _run/scaffold, authors index.html,
        │                                   then loops 5 commands until green:
        │                                   instance_templates → HeyGen TTS →
        │                                   compile_timeline → preflight(8 gates) → check
        ▼
  renders-hyperframes/<stem>/               THE WORKSPACE (local-only, gitignored)
        │
        │  orchestrator re-runs preflight itself (never trusts agent-reported exits)
        │  batch-precheck.sh → snapshots every scene → [vision agent] judges pixels
        ▼
  batch-ship.sh <stem> <prog>               RENDER (~7 min) + verify container/presence
        │                                   → writes qa/VERIFIED (mp4 + sha-256)
        │                                   → dumps qa/frames/ (3 stills per scene)
        ▼
  [3 vision lane agents]                    every scene's frames reviewed; 0 FAILs required
        │
        │  ┌───────────── PILOT ONLY: STOPS HERE ─────────────┐
        │  │ YOU: bash scripts/preview.sh <stem>              │
        │  │ YOU: reply "ship <stem>"  → approval covers the  │
        │  │      whole batch (PILOT GATE)                    │
        │  └──────────────────────────────────────────────────┘
        ▼
  batch-ship.sh <stem> <prog> --publish     refuses without qa/VERIFIED · re-hashes MP4 ·
        │                                   refuses already-published stems · then:
        │                                   file MP4 → Wistia upload → published.tsv row
        │                                   + ledger row → git mv script to rendered/ →
        │                                   commit → delete local MP4 → prune workspace
        ▼
  published.tsv row + rendered/<stem>.txt   = DONE (workspace stays, editable)

  ── any guard failure, any step ──►  quarantine.log row · workspace kept ·
                                      never published · batch continues with next video
```

## 2b. What YOU invoke, and when

**Right now (one-time):**
1. `bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`
   — watch the pilot. Check: title card says CAREER ACCELERATOR / correct
   lesson title; copy matches the script; pacing feels right.
2. If good: tell the session **`ship better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`**.
   That single reply publishes the pilot AND authorizes the 29-video batch to
   run unattended. If not good: say what's wrong instead — a failing pilot
   stops everything by rule.

**Routine operation (any later session):**
- Add lessons: drop `.txt` scripts at `lesson-scripts/<program-slug>/`, then
  invoke `/produce-video` (it refines, builds, and stops at the pilot gate).
- See where everything is: `bash scripts/batch-status.sh` — the only status
  command; reads disk only, safe always.
- Watch any built-but-unshipped video: `bash scripts/preview.sh <stem>`
  (or open its `qa/frames/` stills without launching anything).
- Approve a one-off build: reply `ship <stem>` — same contract as the pilot
  but covers only that stem.
- After a batch: read the close-out report; anything quarantined is listed
  with its reason and is sitting intact in its workspace for a human look.

**You never invoke:** batch-ship.sh --publish directly (sessions do, behind
the VERIFIED guard), archive-lesson.sh without --in-place (moving a workspace
to `_archive/` is your call but do it knowingly), or any `hyperframes` CLI
command — the pipeline wraps them all.

## 2c. Every log, and what it answers

| Question | File (repo-relative) |
|---|---|
| What is live on Wistia? (machine truth, resume key) | `projects/video-production/lesson-scripts/published.tsv` |
| Human-readable history per lesson (dates, URLs, notes) | `projects/video-production/lesson-scripts/refinement-log.md` |
| Which videos failed a guard, when, why? | `projects/video-production/render-qa/quarantine.log` |
| What went wrong/right last session? (newest entry = full current state) | `projects/video-production/render-qa/logs/snag-log.md` |
| Why is the pipeline built this way? | `decisions/log.md` |
| Where is video X in its journey right now? | not a file — `bash scripts/batch-status.sh` (disk is the truth; §3b maps every state + recovery) |
| What did any agent change? | `git log` (every publish and every pipeline fix is a commit) |

## 2d. What changed this session (all committed)

The morning handoff's pipeline had **5 state-machine blockers** and a live
fabrication vector. Everything below is now mechanism, not convention:

1. **Resume key**: `lesson-scripts/published.tsv` (full stem + Wistia URL,
   committed in the publish pass). `batch-status.sh` reads it and flags
   anything in `rendered/` without a row as **STRANDED** — interrupted runs
   can no longer silently strand videos. Ledger rows alone never matched real
   stems (abbreviated cells) and would have caused double-publishes.
2. **Publish contract**: `verify_render.py` writes `qa/VERIFIED` (mp4 path +
   sha-256) only on PASS; `--publish` refuses without it, re-hashes, refuses
   already-published stems, holds a lock, and a git failure quarantines WITH
   the live URL instead of masking. Script moves `refined/ → rendered/` at
   publish (not preflight), so folder state stays truthful.
3. **Fabrication class killed**: all template slot defaults are `[[slot]]`
   placeholders (the old defaults were this pilot's real copy); `check_slots`
   is multi-line-safe and fails any placeholder that would render; the
   BUILD-KIT generator is marker-bounded (`<!-- BUILD-KIT:BEGIN/END -->` in
   the SKILL) after its awk bug dumped the whole SKILL — including a verbatim
   fabricated heading a builder then copied on screen.
4. **Derived fields**: title-card eyebrow/title and outro copy come from
   design-contract.md ("Title card & outro sources" + program display-name table:
   early-career-boost → **"Career Accelerator"**, per the owner's 2026-07-21
   rebrand) and the stem; `preflight.py` check 7b gates them.
5. **Text gate**: `check_text` grades each chip as its own line (the `chips`
   key was previously invisible to the restatement gate).
6. **Pacing**: gate at 4.0s FAIL / 3.0s WARN + BUILD-KIT dead-air rule.
   Known accepted characteristic: 3.0–3.5s content-bearing holds appear as
   gray-zone WARNs; reviewers consistently judged them acceptable. Remedy if
   the owner disagrees: subBeats/scene-split (BUILD-KIT rule 4).
7. **Environment**: system curl is 7.68 — `--retry-all-errors` (needs 7.71)
   is banned from scripts; kokoro is uninstalled and there is **no fallback
   TTS voice** (pinned-voice rule) — TTS failure stops and reports.
8. **Renderer**: HyperFrames stays pinned at 0.7.45 for this batch.
   `instance_templates.py` stays (works around a real framework bug at the
   pin — repeated sub-composition mounts render blank; upstream fixed
   adjacent bugs after our pin). Post-batch task: file the minimal repro
   upstream, then upgrade deliberately (0.7.77+ has `check` consolidation,
   worker fixes, capture self-verification, Lambda batch rendering).

## 3. Running the batch (after pilot approval)

Per video, in `batch-status.sh` order:
1. Cold build subagent (sonnet), paths only: stem, refined script,
   `_run/BUILD-KIT.md`, theme (rotate summit → horizon → cadence), snag Open
   block. Regenerate `_run/` first with `bash scripts/batch-prepare.sh`
   (auto-rebuilds scaffold when the pin or design system changed).
2. `bash scripts/batch-precheck.sh <stem>` + one vision subagent on the
   midpoint snapshots. Blocks bad builds before the 7-min render.
3. `bash scripts/batch-ship.sh <stem> <program-slug>` — **backgrounded**.
4. Vision lanes on `qa/frames/` (≈7 scenes per lane) → on zero FAILs,
   `bash scripts/batch-ship.sh <stem> <program-slug> --publish`.

Orchestrator discipline: re-run gates yourself and trust only process exit
codes (builders have twice misreported exits); never read script bodies or
frame dumps into your own context; one render at a time; set
`VIDEO_SNAG_RETRO_HOOK_DISABLED=1 VIDEO_PURGE_REMINDER_HOOK_DISABLED=1` for
the run and do one snag retro at close-out.

## 3b. The state map — where any video is, from disk alone

Any session (or human) answers "where is video X?" with one command:
`bash scripts/batch-status.sh`. It reads only these on-disk facts — no
session memory, no narration files:

| State | On-disk truth | Status tool shows |
|---|---|---|
| raw intake | `lesson-scripts/<prog>/<stem>.txt` (program root) | (not queued yet — run /refine-scripts) |
| queued to build | `refined/<stem>.txt`, no workspace | numbered queue entry |
| built, awaiting render/vision | `refined/<stem>.txt` + `renders-hyperframes/<stem>/` | `built, NOT published` |
| rendered + verified, awaiting publish | workspace has `qa/VERIFIED` (sha-256 of the exact MP4) | `STRANDED … verified MP4 awaiting publish` |
| failed a guard | row in `render-qa/quarantine.log` (workspace kept, never published) | `STRANDED … quarantined: <reason>` |
| published | row in `lesson-scripts/published.tsv` (full stem + URL); script in `rendered/` | counted in `already on Wistia` |
| blocked | script contains `TODO: needs input` / `SCRIPT PENDING` | `blocked (<reason>)` |

Recovery rules for a fresh session picking up after a crash/timeout:
- `STRANDED, workspace present, no qa/VERIFIED` → re-run
  `batch-ship.sh <stem> <prog>` (render phase is safe to repeat: it cleans
  stale MP4s and reinstalls node_modules if pruned).
- `STRANDED, verified MP4 awaiting publish` → vision-review `qa/frames/`,
  then `batch-ship.sh <stem> <prog> --publish` (idempotent: refuses if a
  published.tsv row already exists, refuses if the MP4 changed since verify).
- `quarantined` → read the reason in `quarantine.log`; if the reason says
  "video IS live at <url>", the upload succeeded and only bookkeeping failed —
  record the URL, do not re-upload.
- `built, NOT published` → re-run preflight yourself; if green, continue at
  precheck. If the workspace is half-authored garbage, delete it — the script
  still in `refined/` re-queues it automatically.

Logging homes (each has one job): `published.tsv` = machine record of what
is live (the resume key) · `refinement-log.md` = human-facing ledger prose ·
`quarantine.log` = per-video guard failures · `render-qa/logs/snag-log.md` =
per-session retro (newest entry is the complete current state) ·
`decisions/log.md` = why the pipeline is shaped this way · git history = the
audit trail of every pipeline change.

## 4. Queue

`bash scripts/batch-status.sh` is authoritative: **29 to build**, 2 blocked
(TODO markers), 6 published (now all matchable via published.tsv). The pilot
shows STRANDED-with-workspace until its publish — that is correct.

## 5. Open items needing the owner

1. Pilot preview + sign-off (above) — approval launches the batch.
2. Confirm "Career Accelerator" as the on-screen program label for
   early-career-boost (it is on the pilot's title card).
3. Two mid-career scripts with `TODO: needs input` markers.
4. `mini-syllabus` superseded Wistia copy `2ilh1o6c4g` — archive in UI.
