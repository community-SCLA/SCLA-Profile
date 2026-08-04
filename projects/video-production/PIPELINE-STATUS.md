# Video Production — Pipeline Status

**Generated file — do not hand-edit.** Overwritten by `scripts/batch-status.sh --write` at every build/quarantine/publish step; a hand edit here is lost on the next run and this file cannot go stale the way the old `status.md` did (deleted 2026-07-27, see `decisions/log.md`) because it is never the thing anyone edits — only ever the thing that gets regenerated from the folders + `published.tsv`.

## Where everything stands

- **3** — **live on Wistia.** Done; links in the *Delivered* table below.
- **22** — **ready to build.** Script approved; nothing made yet.
- **1** — **building now.** A workspace exists and is moving; each names the step it last completed.
- **0** — **waiting on your eyes.** Gate-clean, no MP4 yet — this is the pilot gate.
- **0** — **rendered, not yet published.** The MP4 exists and passed every gate; only the Wistia upload is left.
- **1** — **raw, not yet refined.** Sitting in `inbox/`, waiting on `/refine-scripts`.
- **1** — **NEEDS SCRIPT.** The script itself is incomplete and only you can finish it; the exact question is under each program.
- **13** — **STALLED.** A build folder that stopped moving; the lock has to be released before it can be rebuilt.
- **0** — **REJECTED.** A finished attempt a release check refused; needs a fix and a re-render.
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
| build-direction-before-you-build-a-plan_early-career-boost | early-career-boost | 2026-08-04 | [v2gnkvdcbc](https://sclc.wistia.com/medias/v2gnkvdcbc) | `renders-mp4/early-career-boost/build-direction-before-you-build-a-plan_early-career-boost_2026-08-04.mp4` |
| better-decisions-come-from-better-criteria_early-career-boost | early-career-boost | 2026-07-29 | [t6cathsymi](https://sclc.wistia.com/medias/t6cathsymi) | `renders-mp4/early-career-boost/better-decisions-come-from-better-criteria_early-career-boost_2026-07-29.mp4` |
| what-makes-for-a-dream-job_early-career-boost | early-career-boost | 2026-07-17 | [gryylc7qns](https://sclc.wistia.com/medias/gryylc7qns) | `renders-mp4/early-career-boost/what-makes-for-a-dream-job_early-career-boost_2026-07-17.mp4` |

## Needs a human right now

- **career-building-is-a-repeatable-process_early-career-boost** (early-career-boost) — STALLED: freeform design written; narration not yet synthesized
  - **To clear it:** reclaim the lock, then resume: `bash scripts/build-claim.sh career-building-is-a-repeatable-process_early-career-boost early-career-boost --resume` → `/render-lessons` BUILD career-building-is-a-repeatable-process_early-career-boost. Do NOT delete the workspace — it holds work a rebuild would discard
- **do-not-just-ask-what-ai-replaces_early-career-boost** (early-career-boost) — STALLED: workspace claimed from the scaffold; no plan and no design authored yet
  - **To clear it:** nothing authored yet, so nothing is lost — discard and rebuild: `rm -rf projects/video-production/renders-hyperframes/do-not-just-ask-what-ai-replaces_early-career-boost && /render-lessons BUILD do-not-just-ask-what-ai-replaces_early-career-boost`
- **m2_four-kinds-of-career-transition_mid-career-momentum** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m2_four-kinds-of-career-transition_mid-career-momentum` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m3_building-your-future-you-resume-pt1** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m3_building-your-future-you-resume-pt1` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m3_from-history-to-signal** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - left off after **preflight**, 56 min ago
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m3_from-history-to-signal` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m3_how-to-reposition-your-career** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m3_how-to-reposition-your-career` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m3_rewrite-your-linkedin-for-future-you** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m3_rewrite-your-linkedin-for-future-you` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m3_using-the-resume-builder-tool-pt2** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m3_using-the-resume-builder-tool-pt2` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m4_finding-new-peers-sponsors-and-opportunity-holders** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m4_finding-new-peers-sponsors-and-opportunity-holders` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m4_visibility-actions** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m4_visibility-actions` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m4_who-will-walk-this-next-chapter-with-you** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m4_who-will-walk-this-next-chapter-with-you` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m5_skills-for-the-ai-era** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m5_skills-for-the-ai-era` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- **m6_youve-built-momentum** (mid-career-momentum) — STALLED: HyperFrames composition ready — the gate has not run yet
  - **To clear it:** run the gate: `bash scripts/build-gate.sh m6_youve-built-momentum` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow

## early-career-boost

**READY — queued to build:**

1. finding-creating-a-career-purpose-statement_early-career-boost
2. how-to-make-strong-career-decisions_early-career-boost
3. mini-syllabus_early-career-boost
4. skills-for-the-ai-era-future_early-career-boost
5. using-the-career-map-tool_early-career-boost
6. what-energizes-me_early-career-boost

**STALLED — the build folder stopped moving:**

*Report-only: nothing here is killed automatically. The folder is still the `mkdir` lock, so it has to be released before a rebuild can claim it.*

- career-building-is-a-repeatable-process_early-career-boost  (freeform lane)
  - state: freeform design written; narration not yet synthesized
  - last written to: 4 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: reclaim the lock, then resume: `bash scripts/build-claim.sh career-building-is-a-repeatable-process_early-career-boost early-career-boost --resume` → `/render-lessons` BUILD career-building-is-a-repeatable-process_early-career-boost. Do NOT delete the workspace — it holds work a rebuild would discard
- do-not-just-ask-what-ai-replaces_early-career-boost  (scaffold lane)
  - state: workspace claimed from the scaffold; no plan and no design authored yet
  - last written to: 4 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: nothing authored yet, so nothing is lost — discard and rebuild: `rm -rf projects/video-production/renders-hyperframes/do-not-just-ask-what-ai-replaces_early-career-boost && /render-lessons BUILD do-not-just-ask-what-ai-replaces_early-career-boost`

## mid-career-momentum

**READY — queued to build:**

7. m0_welcome-to-mid-career-momentum
8. m2_mid-career-mindsets-and-limiting-beliefs
9. m2_the-value-of-building-mid-career-momentum
10. m3_discover-experiences-that-support-your-next-move

**BUILDING — in flight, no MP4 yet:**

*A workspace exists and is part-way through. Each names the last step it actually completed, so a resuming session picks up rather than restarts.*

- m1_mini-syllabus  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - left off after **preflight**, just now
  - next: run the gate: `bash scripts/build-gate.sh m1_mini-syllabus` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow

**STALLED — the build folder stopped moving:**

*Report-only: nothing here is killed automatically. The folder is still the `mkdir` lock, so it has to be released before a rebuild can claim it.*

- m2_four-kinds-of-career-transition_mid-career-momentum  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m2_four-kinds-of-career-transition_mid-career-momentum` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m3_building-your-future-you-resume-pt1  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m3_building-your-future-you-resume-pt1` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m3_from-history-to-signal  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - left off after **preflight**, 56 min ago
  - next: run the gate: `bash scripts/build-gate.sh m3_from-history-to-signal` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m3_how-to-reposition-your-career  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m3_how-to-reposition-your-career` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m3_rewrite-your-linkedin-for-future-you  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m3_rewrite-your-linkedin-for-future-you` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m3_using-the-resume-builder-tool-pt2  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m3_using-the-resume-builder-tool-pt2` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m4_finding-new-peers-sponsors-and-opportunity-holders  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m4_finding-new-peers-sponsors-and-opportunity-holders` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m4_visibility-actions  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m4_visibility-actions` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m4_who-will-walk-this-next-chapter-with-you  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m4_who-will-walk-this-next-chapter-with-you` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m5_skills-for-the-ai-era  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m5_skills-for-the-ai-era` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow
- m6_youve-built-momentum  (template lane)
  - state: HyperFrames composition ready — the gate has not run yet
  - last written to: 18 h ago (no `.build-log.tsv` — this workspace predates the build journal)
  - next: run the gate: `bash scripts/build-gate.sh m6_youve-built-momentum` — it runs preflight and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read as NEEDS REVIEW tomorrow

**NEEDS SCRIPT — only you can finish these:**

*The script carries an unanswered question. Answer it in the script and delete the marker line; the lesson rejoins the queue on the next status run, with no other bookkeeping.*

- m4_visibility-actions-what-they-are-and-how-to-practice-them
  - marker: `SCRIPT PENDING` in `lesson-scripts/mid-career-momentum/inbox/m4_visibility-actions-what-they-are-and-how-to-practice-them.txt`
  - **what's needed:** do not refine or build. Re-confirmed 2026-07-24 (auto drain): body is byte-identical (post-normalization) to m4_who-will-walk-this-next-life-chapter-experience-with-you; never defines or demonstrates a "visibility action" despite the title. See refinement-log.md 2026-07-22 row. Owner-actionable: supply real visibility-actions narration.

## career-transitions

**READY — queued to build:**

11. m2_four-kinds-of-career-transition_career-transitions
12. m2_welcome-and-using-career-transitions-as-leaps-ahead
13. m3_the-identity-audit
14. m3_the-two-sided-work
15. m4_building-your-carry-forward-inventory
16. m5_testing-your-next-chapter
17. m5_the-story-that-makes-the-change-legible
18. m7_your-reinvention-roadmap

## entrepreneur-accelerator

**READY — queued to build:**

19. m1_reframing-entrepreneurship-and-going-solo
20. m3_choosing-your-solo-model
21. m4_building-visibility-on-your-own
22. m5_making-solo-work-sustainable

**RAW — waiting on refinement:**

- m2_why-build-your-own-path — `/refine-scripts`

---
Resume: `/render-lessons` AUTO-BATCH starts at the top of the READY list above. Full state model: `bash scripts/batch-status.sh` (terminal) or `bash scripts/batch-status.sh --json` (machine).
