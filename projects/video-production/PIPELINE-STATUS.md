# Video Production — Pipeline Status

**Generated file — do not hand-edit.** Overwritten by `scripts/batch-status.sh --write` at every build/quarantine/publish step; a hand edit here is lost on the next run and this file cannot go stale the way the old `status.md` did (deleted 2026-07-27, see `decisions/log.md`) because it is never the thing anyone edits — only ever the thing that gets regenerated from the folders + `published.tsv`.

- **20** queued to build
- **14** built, not yet published
- **0** stranded mid-pipeline
- **2** blocked — needs owner input
- **2** live on Wistia

## Stuck right now

- **build-direction-before-you-build-a-plan_early-career-boost** (early-career-boost) — QUARANTINED: verify_render.py non-zero

## Published — live on Wistia

| Lesson | Program | Render date | Wistia URL |
|---|---|---|---|
| what-makes-for-a-dream-job_early-career-boost | early-career-boost | 2026-07-17 | https://sclc.wistia.com/medias/gryylc7qns |
| better-decisions-come-from-better-criteria_early-career-boost | early-career-boost | 2026-07-29 | https://sclc.wistia.com/medias/t6cathsymi |

## early-career-boost

**Queued to build:**

1. career-building-is-a-repeatable-process_early-career-boost
2. do-not-just-ask-what-ai-replaces_early-career-boost
3. finding-creating-a-career-purpose-statement_early-career-boost
4. how-to-make-strong-career-decisions_early-career-boost
5. mini-syllabus_early-career-boost
6. skills-for-the-ai-era-future_early-career-boost
7. using-the-career-map-tool_early-career-boost
8. what-energizes-me_early-career-boost

**Built, unpublished:**

- build-direction-before-you-build-a-plan_early-career-boost — QUARANTINED: verify_render.py non-zero

## mid-career-momentum

**Built, unpublished:**

- m1_mini-syllabus — compiled — run preflight to confirm gate-clean
- m2_four-kinds-of-career-transition_mid-career-momentum — compiled — run preflight to confirm gate-clean
- m2_mid-career-mindsets-and-limiting-beliefs — compiled — run preflight to confirm gate-clean
- m3_building-your-future-you-resume-pt1 — compiled — run preflight to confirm gate-clean
- m3_from-history-to-signal — compiled — run preflight to confirm gate-clean
- m3_how-to-reposition-your-career — compiled — run preflight to confirm gate-clean
- m3_rewrite-your-linkedin-for-future-you — compiled — run preflight to confirm gate-clean
- m3_using-the-resume-builder-tool-pt2 — compiled — run preflight to confirm gate-clean
- m4_finding-new-peers-sponsors-and-opportunity-holders — compiled — run preflight to confirm gate-clean
- m4_visibility-actions — compiled — run preflight to confirm gate-clean
- m4_who-will-walk-this-next-chapter-with-you — compiled — run preflight to confirm gate-clean
- m5_skills-for-the-ai-era — compiled — run preflight to confirm gate-clean
- m6_youve-built-momentum — compiled — run preflight to confirm gate-clean

**Blocked — needs owner input:**

- m2_the-value-of-building-mid-career-momentum — TODO: needs input
- m3_discover-experiences-that-support-your-next-move — TODO: needs input

## career-transitions

**Queued to build:**

9. m2_four-kinds-of-career-transition_career-transitions
10. m2_welcome-and-using-career-transitions-as-leaps-ahead
11. m3_the-identity-audit
12. m3_the-two-sided-work
13. m4_building-your-carry-forward-inventory
14. m5_testing-your-next-chapter
15. m5_the-story-that-makes-the-change-legible
16. m7_your-reinvention-roadmap

## entrepreneur-accelerator

**Queued to build:**

17. m1_reframing-entrepreneurship-and-going-solo
18. m3_choosing-your-solo-model
19. m4_building-visibility-on-your-own
20. m5_making-solo-work-sustainable

---
Resume: `/render-lessons` AUTO-BATCH starts at the top of the queued list above. Full state model: `bash scripts/batch-status.sh` (terminal) or `bash scripts/batch-status.sh --json` (machine).
