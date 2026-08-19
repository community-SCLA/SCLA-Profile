# Video Production — Pipeline Status

**Generated file — do not hand-edit.** Overwritten by `scripts/batch-status.sh --write` at every build/quarantine/publish step; a hand edit here is lost on the next run and this file cannot go stale the way the old `status.md` did (deleted 2026-07-27, see `decisions/log.md`) because it is never the thing anyone edits — only ever the thing that gets regenerated from the folders + `published.tsv`.

## Where everything stands

- **38** — **live on Wistia.** Done; links in the *Delivered* table below.
- **0** — **ready to build.** Script approved; nothing made yet.
- **0** — **building now.** A workspace exists and is moving; each names the step it last completed.
- **0** — **awaiting visual review.** The mechanical gate matches this source; the combined visual verdict is still missing.
- **0** — **awaiting encode review.** A content-bound MP4 exists, but required playback review has not passed for those exact bytes.
- **0** — **needs revision.** The combined visual review found a blocking defect or a flat cut.
- **0** — **waiting on your eyes.** The mechanical and visual receipts match this source; no MP4 yet, and each lesson can be reviewed independently.
- **0** — **approved to render.** The exact current source has matching gate, visual-review, and owner-approval receipts.
- **0** — **rendered, not yet published.** The MP4 exists and its bytes match the current-source completion receipt; its per-render encode policy is satisfied. Only the Wistia upload is left.
- **0** — **interrupted render.** A render started but never wrote an atomic completion receipt for its current bytes; partial output will not be reused.
- **1** — **raw, not yet refined.** Sitting in `inbox/`, waiting on `/refine-scripts`.
- **1** — **NEEDS SCRIPT.** The script itself is incomplete and only you can finish it; the exact question is under each program.
- **0** — **STALLED.** An incomplete phase stopped moving; resume it in the same workspace without deleting completed work.
- **0** — **REJECTED.** A blocking review or gate failed; the completed production phase remains visible beside the condition.
- **0** — **STRANDED.** Filed as published but never recorded as published; an interrupted run left it here.
- **0** — **ORPHAN.** A build folder matching no script in any program.

### What the phases and conditions mean

Status is reconstructed from source files, workspace contents, revision-bound receipts, the run record, and the publish ledger. Each active lesson has a production **phase** (what completed) plus an optional **condition** (what blocks it now), so an interruption does not collapse progress into all-or-nothing.

| Phase or condition | Durable evidence | What it needs next |
|---|---|---|
| **RAW** | `lesson-scripts/<program>/inbox/<base>.txt` | refinement — `/refine-scripts` |
| **READY** | `lesson-scripts/<program>/ready/<base>.txt`, no build folder | an agent to author it — `/render-lessons` |
| **BUILDING** | authored files plus `.build-log.tsv` in `renders-hyperframes/<base>/` | resume the recorded phase in that workspace; do not discard completed work |
| **AWAITING VISUAL REVIEW** | matching `qa/PREFLIGHT-OK`, no matching `qa/VISUAL-REVIEW.json` | combined visual review |
| **NEEDS REVISION** | matching visual receipt says `FLAT`, `FAIL`, or `REVISE` | revise the same cut, then rerun its gates |
| **NEEDS REVIEW** | current-source `qa/PREFLIGHT-OK` plus a matching PASS / ALIVE / PROCEED `qa/VISUAL-REVIEW.json` | you — watch and approve this exact cut |
| **AWAITING VERIFICATION** | matching `qa/RENDER-START.json`, atomic render completion fields, and matching MP4 bytes; no `qa/VERIFIED` yet | resume `ship` — it verifies this MP4 without rendering again |
| *INTERRUPTED RENDER* | `qa/RENDER-START.json` exists, but no completion hash matches the current MP4 | resume `ship`; partial output is discarded and only this exact source is re-rendered |
| **AWAITING ENCODE REVIEW** | current-source `qa/VERIFIED`, but no PASS `qa/ENCODE-REVIEW.json` for the same source and MP4 hash while review is required | review the encoded beginning, middle, transitions, and ending |
| **RENDERED** | render-complete and `qa/VERIFIED` receipts match current source and actual MP4 bytes; the encode policy stamped at render start is satisfied | the Wistia upload and ledger row |
| **PUBLISHED** | `lesson-scripts/<program>/published/<base>.txt` + a row in `lesson-scripts/published.tsv` | nothing |
| *NEEDS SCRIPT* | a `TODO: needs input` / `SCRIPT PENDING` marker inside the script, in `inbox/` or `ready/` | you — the source material is missing something |
| *STALLED* | an incomplete phase with nothing written for 30+ min | resume that phase in place through `run.sh`; the workspace remains the recovery record |
| *REJECTED* | a current failed review, unresolved `qa/failure.json`, or unresolved quarantine incident | fix the listed cause, then perform the named resume or retry action |
| *STRANDED* | a script in `published/` with no `published.tsv` row | the publish step re-run; nothing is lost |
| *ORPHAN* | a build folder whose base matches no script anywhere | naming — it is either reference material or garbage |

## Delivered

Every lesson that is live, and where to watch it. Generated from `lesson-scripts/published.tsv`, which `batch-ship.sh` writes in the same commit as the upload.

| Lesson | Program | Rendered | Watch | Local MP4 |
|---|---|---|---|---|
| m5_making-solo-work-sustainable | entrepreneur-accelerator | 2026-08-11 | [uphndr7qnn](https://sclc.wistia.com/medias/uphndr7qnn) | `renders-mp4/entrepreneur-accelerator/m5_making-solo-work-sustainable_2026-08-11.mp4` |
| m2_the-value-of-building-mid-career-momentum | mid-career-momentum | 2026-08-11 | [xg6mxd0vcr](https://sclc.wistia.com/medias/xg6mxd0vcr) | `renders-mp4/mid-career-momentum/m2_the-value-of-building-mid-career-momentum_2026-08-11.mp4` |
| m3_building-your-future-you-resume-pt1 | mid-career-momentum | 2026-08-11 | [vgcigi2ilp](https://sclc.wistia.com/medias/vgcigi2ilp) | `renders-mp4/mid-career-momentum/m3_building-your-future-you-resume-pt1_2026-08-11.mp4` |
| m3_discover-experiences-that-support-your-next-move | mid-career-momentum | 2026-08-11 | [w5lzzvgdl1](https://sclc.wistia.com/medias/w5lzzvgdl1) | `renders-mp4/mid-career-momentum/m3_discover-experiences-that-support-your-next-move_2026-08-11.mp4` |
| m3_from-history-to-signal | mid-career-momentum | 2026-08-11 | [itg5iy0xay](https://sclc.wistia.com/medias/itg5iy0xay) | `renders-mp4/mid-career-momentum/m3_from-history-to-signal_2026-08-11.mp4` |
| m3_how-to-reposition-your-career | mid-career-momentum | 2026-08-11 | [9cmgpehr0o](https://sclc.wistia.com/medias/9cmgpehr0o) | `renders-mp4/mid-career-momentum/m3_how-to-reposition-your-career_2026-08-11.mp4` |
| m4_visibility-actions | mid-career-momentum | 2026-08-11 | [blkukx9a7p](https://sclc.wistia.com/medias/blkukx9a7p) | `renders-mp4/mid-career-momentum/m4_visibility-actions_2026-08-11.mp4` |
| m5_skills-for-the-ai-era | mid-career-momentum | 2026-08-11 | [7pdoss94gj](https://sclc.wistia.com/medias/7pdoss94gj) | `renders-mp4/mid-career-momentum/m5_skills-for-the-ai-era_2026-08-11.mp4` |
| m3_the-two-sided-work | career-transitions | 2026-08-11 | [pwpwvz6zm9](https://sclc.wistia.com/medias/pwpwvz6zm9) | `renders-mp4/career-transitions/m3_the-two-sided-work_2026-08-11.mp4` |
| m3_choosing-your-solo-model | entrepreneur-accelerator | 2026-08-10 | [6lvtga2yzt](https://sclc.wistia.com/medias/6lvtga2yzt) | `renders-mp4/entrepreneur-accelerator/m3_choosing-your-solo-model_2026-08-10.mp4` |
| m5_the-story-that-makes-the-change-legible | career-transitions | 2026-08-10 | [9739fjclol](https://sclc.wistia.com/medias/9739fjclol) | `renders-mp4/career-transitions/m5_the-story-that-makes-the-change-legible_2026-08-10.mp4` |
| m5_testing-your-next-chapter | career-transitions | 2026-08-10 | [1csb5yue4s](https://sclc.wistia.com/medias/1csb5yue4s) | `renders-mp4/career-transitions/m5_testing-your-next-chapter_2026-08-10.mp4` |
| m4_finding-new-peers-sponsors-and-opportunity-holders | mid-career-momentum | 2026-08-10 | [tklv0cr5xx](https://sclc.wistia.com/medias/tklv0cr5xx) | `renders-mp4/mid-career-momentum/m4_finding-new-peers-sponsors-and-opportunity-holders_2026-08-10.mp4` |
| m4_who-will-walk-this-next-chapter-with-you | mid-career-momentum | 2026-08-10 | [lph5w2gcn8](https://sclc.wistia.com/medias/lph5w2gcn8) | `renders-mp4/mid-career-momentum/m4_who-will-walk-this-next-chapter-with-you_2026-08-10.mp4` |
| m2_four-kinds-of-career-transition_career-transitions | career-transitions | 2026-08-10 | [8my18zw4fb](https://sclc.wistia.com/medias/8my18zw4fb) | `renders-mp4/career-transitions/m2_four-kinds-of-career-transition_career-transitions_2026-08-10.mp4` |
| m2_mid-career-mindsets-and-limiting-beliefs | mid-career-momentum | 2026-08-10 | [bw01arzcic](https://sclc.wistia.com/medias/bw01arzcic) | `renders-mp4/mid-career-momentum/m2_mid-career-mindsets-and-limiting-beliefs_2026-08-10.mp4` |
| m2_four-kinds-of-career-transition_mid-career-momentum | mid-career-momentum | 2026-08-10 | [02cu6ojupk](https://sclc.wistia.com/medias/02cu6ojupk) | `renders-mp4/mid-career-momentum/m2_four-kinds-of-career-transition_mid-career-momentum_2026-08-10.mp4` |
| m3_using-the-resume-builder-tool-pt2 | mid-career-momentum | 2026-08-10 | [uw60kvq8dx](https://sclc.wistia.com/medias/uw60kvq8dx) | `renders-mp4/mid-career-momentum/m3_using-the-resume-builder-tool-pt2_2026-08-10.mp4` |
| m4_building-your-carry-forward-inventory | career-transitions | 2026-08-10 | [dw676qxzpy](https://sclc.wistia.com/medias/dw676qxzpy) | `renders-mp4/career-transitions/m4_building-your-carry-forward-inventory_2026-08-10.mp4` |
| m7_your-reinvention-roadmap | career-transitions | 2026-08-10 | [ir9qak9ay5](https://sclc.wistia.com/medias/ir9qak9ay5) | `renders-mp4/career-transitions/m7_your-reinvention-roadmap_2026-08-10.mp4` |
| m1_reframing-entrepreneurship-and-going-solo | entrepreneur-accelerator | 2026-08-10 | [vpu39a7qe9](https://sclc.wistia.com/medias/vpu39a7qe9) | `renders-mp4/entrepreneur-accelerator/m1_reframing-entrepreneurship-and-going-solo_2026-08-10.mp4` |
| m4_building-visibility-on-your-own | entrepreneur-accelerator | 2026-08-10 | [pvv6ceudsg](https://sclc.wistia.com/medias/pvv6ceudsg) | `renders-mp4/entrepreneur-accelerator/m4_building-visibility-on-your-own_2026-08-10.mp4` |
| m3_rewrite-your-linkedin-for-future-you | mid-career-momentum | 2026-08-08 | [n3tl8aczyl](https://sclc.wistia.com/medias/n3tl8aczyl) | `renders-mp4/mid-career-momentum/m3_rewrite-your-linkedin-for-future-you_2026-08-08.mp4` |
| m1_mini-syllabus | mid-career-momentum | 2026-08-07 | [ix0uy4jjmg](https://sclc.wistia.com/medias/ix0uy4jjmg) | `renders-mp4/mid-career-momentum/m1_mini-syllabus_2026-08-07.mp4` |
| m3_the-identity-audit | career-transitions | 2026-08-07 | [7kcc5t69fk](https://sclc.wistia.com/medias/7kcc5t69fk) | `renders-mp4/career-transitions/m3_the-identity-audit_2026-08-07.mp4` |
| m2_welcome-and-using-career-transitions-as-leaps-ahead | career-transitions | 2026-08-07 | [izkgx5kdba](https://sclc.wistia.com/medias/izkgx5kdba) | `renders-mp4/career-transitions/m2_welcome-and-using-career-transitions-as-leaps-ahead_2026-08-07.mp4` |
| m6_youve-built-momentum | mid-career-momentum | 2026-08-07 | [6fsnr8zwt2](https://sclc.wistia.com/medias/6fsnr8zwt2) | `renders-mp4/mid-career-momentum/m6_youve-built-momentum_2026-08-07.mp4` |
| mini-syllabus_early-career-boost | early-career-boost | 2026-08-06 | [ays7di6sti](https://sclc.wistia.com/medias/ays7di6sti) | `renders-mp4/early-career-boost/mini-syllabus_early-career-boost_2026-08-06.mp4` |
| do-not-just-ask-what-ai-replaces_early-career-boost | early-career-boost | 2026-08-06 | [uhnqbjt0x7](https://sclc.wistia.com/medias/uhnqbjt0x7) | `renders-mp4/early-career-boost/do-not-just-ask-what-ai-replaces_early-career-boost_2026-08-06.mp4` |
| career-building-is-a-repeatable-process_early-career-boost | early-career-boost | 2026-08-05 | [cnj1463xuw](https://sclc.wistia.com/medias/cnj1463xuw) | `renders-mp4/early-career-boost/career-building-is-a-repeatable-process_early-career-boost_2026-08-05.mp4` |
| finding-creating-a-career-purpose-statement_early-career-boost | early-career-boost | 2026-08-05 | [0szz79g9m7](https://sclc.wistia.com/medias/0szz79g9m7) | `renders-mp4/early-career-boost/finding-creating-a-career-purpose-statement_early-career-boost_2026-08-05.mp4` |
| how-to-make-strong-career-decisions_early-career-boost | early-career-boost | 2026-08-05 | [u54hifguqf](https://sclc.wistia.com/medias/u54hifguqf) | `renders-mp4/early-career-boost/how-to-make-strong-career-decisions_early-career-boost_2026-08-05.mp4` |
| what-energizes-me_early-career-boost | early-career-boost | 2026-08-05 | [0lbi1p8due](https://sclc.wistia.com/medias/0lbi1p8due) | `renders-mp4/early-career-boost/what-energizes-me_early-career-boost_2026-08-05.mp4` |
| skills-for-the-ai-era-future_early-career-boost | early-career-boost | 2026-08-05 | [r21mwmy2tn](https://sclc.wistia.com/medias/r21mwmy2tn) | `renders-mp4/early-career-boost/skills-for-the-ai-era-future_early-career-boost_2026-08-05.mp4` |
| using-the-career-map-tool_early-career-boost | early-career-boost | 2026-08-05 | [599zwe5ii9](https://sclc.wistia.com/medias/599zwe5ii9) | `renders-mp4/early-career-boost/using-the-career-map-tool_early-career-boost_2026-08-05.mp4` |
| build-direction-before-you-build-a-plan_early-career-boost | early-career-boost | 2026-08-04 | [v2gnkvdcbc](https://sclc.wistia.com/medias/v2gnkvdcbc) | `renders-mp4/early-career-boost/build-direction-before-you-build-a-plan_early-career-boost_2026-08-04.mp4` |
| better-decisions-come-from-better-criteria_early-career-boost | early-career-boost | 2026-07-29 | [t6cathsymi](https://sclc.wistia.com/medias/t6cathsymi) | `renders-mp4/early-career-boost/better-decisions-come-from-better-criteria_early-career-boost_2026-07-29.mp4` |
| what-makes-for-a-dream-job_early-career-boost | early-career-boost | 2026-07-17 | [gryylc7qns](https://sclc.wistia.com/medias/gryylc7qns) | `renders-mp4/early-career-boost/what-makes-for-a-dream-job_early-career-boost_2026-07-17.mp4` |

## Your review queue

- **m4_visibility-actions-what-they-are-and-how-to-practice-them** (mid-career-momentum) — source material is missing
  - **What's needed:** do not refine or build. Re-confirmed 2026-07-24 (auto drain): body is byte-identical (post-normalization) to m4_who-will-walk-this-next-life-chapter-experience-with-you; never defines or demonstrates a "visibility action" despite the title. See refinement-log.md 2026-07-22 row. Owner-actionable: supply real visibility-actions narration.

## mid-career-momentum

**NEEDS SCRIPT — only you can finish these:**

*The script carries an unanswered question. Answer it in the script and delete the marker line; the lesson rejoins the queue on the next status run, with no other bookkeeping.*

- m4_visibility-actions-what-they-are-and-how-to-practice-them
  - marker: `SCRIPT PENDING` in `lesson-scripts/mid-career-momentum/inbox/m4_visibility-actions-what-they-are-and-how-to-practice-them.txt`
  - **what's needed:** do not refine or build. Re-confirmed 2026-07-24 (auto drain): body is byte-identical (post-normalization) to m4_who-will-walk-this-next-life-chapter-experience-with-you; never defines or demonstrates a "visibility action" despite the title. See refinement-log.md 2026-07-22 row. Owner-actionable: supply real visibility-actions narration.

## entrepreneur-accelerator

**RAW — waiting on refinement:**

- m2_why-build-your-own-path — `/refine-scripts`

---
Resume: `/render-lessons` AUTO-BATCH starts at the top of the READY list above. Full state model: `bash scripts/batch-status.sh` (terminal) or `bash scripts/batch-status.sh --json` (machine).
