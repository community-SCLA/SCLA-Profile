# HANDOFF — AUTO-BATCH, updated 2026-07-28 evening (certification complete)

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

## 2. What changed this session (all committed)

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
   frame.md ("Title card & outro sources" + program display-name table:
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
