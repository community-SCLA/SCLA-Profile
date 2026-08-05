# Video Production — Pipeline Status

**Generated file — do not hand-edit.** Overwritten by `scripts/batch-status.sh --write` at every build/quarantine/publish step; a hand edit here is lost on the next run and this file cannot go stale the way the old `status.md` did (deleted 2026-07-27, see `decisions/log.md`) because it is never the thing anyone edits — only ever the thing that gets regenerated from the folders + `published.tsv`.

## Where everything stands

- **5** — **live on Wistia.** Done; links in the *Delivered* table below.
- **27** — **ready to build.** Script approved; nothing made yet.
- **0** — **building now.** A workspace exists and is moving; each names the step it last completed.
- **0** — **waiting on your eyes.** Gate-clean, no MP4 yet — this is the pilot gate.
- **1** — **approved to render.** Gate-clean and covered by the active batch pilot approval.
- **2** — **rendered, not yet published.** The MP4 exists and passed every gate; only the Wistia upload is left.
- **1** — **raw, not yet refined.** Sitting in `inbox/`, waiting on `/refine-scripts`.
- **1** — **NEEDS SCRIPT.** The script itself is incomplete and only you can finish it; the exact question is under each program.
- **2** — **STALLED.** A build folder that stopped moving; the lock has to be released before it can be rebuilt.
- **2** — **REJECTED.** A finished attempt a release check refused; needs a fix and a re-render.
- **0** — **STRANDED.** Filed as published but never recorded as published; an interrupted run left it here.
- **0** — **ORPHAN.** A build folder matching no script in any program.

### What the stages mean

The pipeline has no database — the folders on disk *are* the state, and since 2026-08-04 **the folder name is the stage name**. Every lesson sits in exactly one row.

| Stage | Where it lives on disk | What it needs next |
|---|---|---|
| **RAW** | `lesson-scripts/<program>/inbox/<base>.txt` | refinement — `/refine-scripts` |
| **READY** | `lesson-scripts/<program>/ready/<base>.txt`, no build folder | an agent to author it — `/render-lessons` |
| **BUILDING** | `renders-hyperframes/<base>/`, incomplete | the build to continue; `.build-log.tsv` says which step it last finished |
| **NEEDS REVIEW** | the same folder plus `qa/PREFLIGHT-OK` | you — watch it, then `ship <stem>` |
| **RENDERED** | the same folder plus `qa/VERIFIED` and an `.mp4` | the Wistia upload and its ledger row |
| **PUBLISHED** | `lesson-scripts/<program>/published/<base>.txt` + a row in `lesson-scripts/published.tsv` | nothing |
| *NEEDS SCRIPT* | a `TODO: needs input` / `SCRIPT PENDING` marker inside the script, in `inbox/` or `ready/` | you — the source material is missing something |
| *STALLED* | a build folder with nothing written for 30+ min | the lock released, then a rebuild |
| *REJECTED* | a build folder and an unresolved row in `render-qa/quarantine.log` | a human fix to the authoring, then a re-render |
| *STRANDED* | a script in `published/` with no `published.tsv` row | the publish step re-run; nothing is lost |
| *ORPHAN* | a build folder whose base matches no script anywhere | naming — it is either reference material or garbage |

## Delivered

Every lesson that is live, and where to watch it. Generated from `lesson-scripts/published.tsv`, which `batch-ship.sh` writes in the same commit as the upload.

| Lesson | Program | Rendered | Watch | Local MP4 |
|---|---|---|---|---|
| career-building-is-a-repeatable-process_early-career-boost | early-career-boost | 2026-08-05 | [cnj1463xuw](https://sclc.wistia.com/medias/cnj1463xuw) | `renders-mp4/early-career-boost/career-building-is-a-repeatable-process_early-career-boost_2026-08-05.mp4` |
| finding-creating-a-career-purpose-statement_early-career-boost | early-career-boost | 2026-08-05 | [0szz79g9m7](https://sclc.wistia.com/medias/0szz79g9m7) | `renders-mp4/early-career-boost/finding-creating-a-career-purpose-statement_early-career-boost_2026-08-05.mp4` |
| build-direction-before-you-build-a-plan_early-career-boost | early-career-boost | 2026-08-04 | [v2gnkvdcbc](https://sclc.wistia.com/medias/v2gnkvdcbc) | `renders-mp4/early-career-boost/build-direction-before-you-build-a-plan_early-career-boost_2026-08-04.mp4` |
| better-decisions-come-from-better-criteria_early-career-boost | early-career-boost | 2026-07-29 | [t6cathsymi](https://sclc.wistia.com/medias/t6cathsymi) | `renders-mp4/early-career-boost/better-decisions-come-from-better-criteria_early-career-boost_2026-07-29.mp4` |
| what-makes-for-a-dream-job_early-career-boost | early-career-boost | 2026-07-17 | [gryylc7qns](https://sclc.wistia.com/medias/gryylc7qns) | `renders-mp4/early-career-boost/what-makes-for-a-dream-job_early-career-boost_2026-07-17.mp4` |

## Needs a human right now

- **do-not-just-ask-what-ai-replaces_early-career-boost** (early-career-boost) — REJECTED: a release gate rejected this cut — cloud render failed or timed out
  - last completed **gate** at 2026-08-05 08:08 UTC
  - **To clear it:** inspect cloud credentials/backend, then use run.sh retry after the path is corrected
- **mini-syllabus_early-career-boost** (early-career-boost) — REJECTED: a release gate rejected this cut — cloud render failed or timed out
  - last completed **preflight** at 2026-08-05 16:41 UTC
  - **To clear it:** inspect cloud credentials/backend, then use run.sh retry after the path is corrected
- **using-the-career-map-tool_early-career-boost** (early-career-boost) — STALLED: freeform composition timed and ready — the gate has not run yet
  - last completed **release** at 2026-08-05 20:31 UTC
  - **To clear it:** resume through the control plane: `bash projects/video-production/run.sh resume`; continue only using-the-career-map-tool_early-career-boost. Do not delete the workspace
- **m0_welcome-to-mid-career-momentum** (mid-career-momentum) — STALLED: workspace claimed from the scaffold; no plan and no design authored yet
  - last completed **release** at 2026-08-05 20:31 UTC
  - **To clear it:** select only this lesson: `bash projects/video-production/run.sh produce --stem m0_welcome-to-mid-career-momentum`; then continue `/render-lessons BUILD m0_welcome-to-mid-career-momentum`

## early-career-boost

**RENDERED — MP4 verified, waiting on publish:**

*The video file exists and passed every gate. Nothing left but the upload.*

- how-to-make-strong-career-decisions_early-career-boost
  - state: MP4 rendered and gate-verified — waiting only on the Wistia upload
  - last completed **release** at 2026-08-05 20:31 UTC
  - next: publish it: `bash projects/video-production/run.sh ship how-to-make-strong-career-decisions_early-career-boost --publish`
- what-energizes-me_early-career-boost
  - state: MP4 rendered and gate-verified — waiting only on the Wistia upload
  - last completed **release** at 2026-08-05 16:40 UTC
  - next: publish it: `bash projects/video-production/run.sh ship what-energizes-me_early-career-boost --publish`

**APPROVED — gate-clean, ready to render:**

*The active batch pilot approval already covers this video.*

- skills-for-the-ai-era-future_early-career-boost
  - state: gate-clean; the active batch pilot is approved
  - last completed **release** at 2026-08-05 20:31 UTC
  - next: render it: `bash projects/video-production/run.sh ship skills-for-the-ai-era-future_early-career-boost`

**STALLED — the build folder stopped moving:**

*Report-only: nothing here is killed automatically. The folder is still the `mkdir` lock, so it has to be released before a rebuild can claim it.*

- using-the-career-map-tool_early-career-boost
  - state: freeform composition timed and ready — the gate has not run yet
  - last completed **release** at 2026-08-05 20:31 UTC
  - next: resume through the control plane: `bash projects/video-production/run.sh resume`; continue only using-the-career-map-tool_early-career-boost. Do not delete the workspace

**REJECTED — a gate refused this cut:**

*Built and rendered, then refused by a release check. It will not publish until a human fixes the cause and re-renders.*

- do-not-just-ask-what-ai-replaces_early-career-boost
  - state: a release gate rejected this cut — cloud render failed or timed out
  - last completed **gate** at 2026-08-05 08:08 UTC
  - next: inspect cloud credentials/backend, then use run.sh retry after the path is corrected
- mini-syllabus_early-career-boost
  - state: a release gate rejected this cut — cloud render failed or timed out
  - last completed **preflight** at 2026-08-05 16:41 UTC
  - next: inspect cloud credentials/backend, then use run.sh retry after the path is corrected

## mid-career-momentum

**READY — queued to build:**

1. m1_mini-syllabus
2. m2_four-kinds-of-career-transition_mid-career-momentum
3. m2_mid-career-mindsets-and-limiting-beliefs
4. m2_the-value-of-building-mid-career-momentum
5. m3_building-your-future-you-resume-pt1
6. m3_discover-experiences-that-support-your-next-move
7. m3_from-history-to-signal
8. m3_how-to-reposition-your-career
9. m3_rewrite-your-linkedin-for-future-you
10. m3_using-the-resume-builder-tool-pt2
11. m4_finding-new-peers-sponsors-and-opportunity-holders
12. m4_visibility-actions
13. m4_who-will-walk-this-next-chapter-with-you
14. m5_skills-for-the-ai-era
15. m6_youve-built-momentum

**STALLED — the build folder stopped moving:**

*Report-only: nothing here is killed automatically. The folder is still the `mkdir` lock, so it has to be released before a rebuild can claim it.*

- m0_welcome-to-mid-career-momentum
  - state: workspace claimed from the scaffold; no plan and no design authored yet
  - last completed **release** at 2026-08-05 20:31 UTC
  - next: select only this lesson: `bash projects/video-production/run.sh produce --stem m0_welcome-to-mid-career-momentum`; then continue `/render-lessons BUILD m0_welcome-to-mid-career-momentum`

**NEEDS SCRIPT — only you can finish these:**

*The script carries an unanswered question. Answer it in the script and delete the marker line; the lesson rejoins the queue on the next status run, with no other bookkeeping.*

- m4_visibility-actions-what-they-are-and-how-to-practice-them
  - marker: `SCRIPT PENDING` in `lesson-scripts/mid-career-momentum/inbox/m4_visibility-actions-what-they-are-and-how-to-practice-them.txt`
  - **what's needed:** do not refine or build. Re-confirmed 2026-07-24 (auto drain): body is byte-identical (post-normalization) to m4_who-will-walk-this-next-life-chapter-experience-with-you; never defines or demonstrates a "visibility action" despite the title. See refinement-log.md 2026-07-22 row. Owner-actionable: supply real visibility-actions narration.

## career-transitions

**READY — queued to build:**

16. m2_four-kinds-of-career-transition_career-transitions
17. m2_welcome-and-using-career-transitions-as-leaps-ahead
18. m3_the-identity-audit
19. m3_the-two-sided-work
20. m4_building-your-carry-forward-inventory
21. m5_testing-your-next-chapter
22. m5_the-story-that-makes-the-change-legible
23. m7_your-reinvention-roadmap

## entrepreneur-accelerator

**READY — queued to build:**

24. m1_reframing-entrepreneurship-and-going-solo
25. m3_choosing-your-solo-model
26. m4_building-visibility-on-your-own
27. m5_making-solo-work-sustainable

**RAW — waiting on refinement:**

- m2_why-build-your-own-path — `/refine-scripts`

---
Resume: `/render-lessons` AUTO-BATCH starts at the top of the READY list above. Full state model: `bash scripts/batch-status.sh` (terminal) or `bash scripts/batch-status.sh --json` (machine).
