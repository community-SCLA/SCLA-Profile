# Video Production — Pipeline Status

**Generated file — do not hand-edit.** Overwritten by `scripts/batch-status.sh --write` at every build/quarantine/publish step; a hand edit here is lost on the next run and this file cannot go stale the way the old `status.md` did (deleted 2026-07-27, see `decisions/log.md`) because it is never the thing anyone edits — only ever the thing that gets regenerated from the folders + `published.tsv`.

## Where everything stands

- **23** — **queued to build.** Script approved; nothing made yet.
- **12** — **built as compositions, no MP4 yet.** The animated lesson exists as HyperFrames HTML + narration audio; it still has to be rendered to video.
- **0** — **MP4 rendered and verified, not yet published.** The video file exists and passed the gates; only the Wistia upload is left.
- **0** — **rejected by a gate.** A finished attempt a release check refused; needs a fix and a re-render.
- **0** — **stranded mid-pipeline.** Filed as rendered but never recorded as published; an interrupted run left it here.
- **0** — **blocked, needs owner input.** The script itself is incomplete; see the exact question under each program below.
- **3** — **live on Wistia.** Done.

### What the stages mean

The pipeline has no database — the folders on disk *are* the state, and this table says which folder means what. Every lesson sits in exactly one row.

| Stage | What exists on disk | What it needs next |
|---|---|---|
| **Queued to build** | a refined script in `lesson-scripts/<program>/refined/` and no build folder | an agent to author it — `/render-lessons` |
| **Built — composition, no MP4** | `renders-hyperframes/<lesson>/` with a scene plan, narration `.wav` and a timed `index.html` | render + verify — this is what turns it into an MP4 (~15-20 min each) |
| **MP4 awaiting publish** | the same folder, plus a `qa/VERIFIED` marker and an `.mp4` under `renders/` | the Wistia upload and its ledger row |
| **Quarantined** | a build folder and a row in `render-qa/quarantine.log` | a human fix to the authoring, then a re-render — it will never publish itself |
| **Stranded** | a script in `rendered/` with no row in `published.tsv` | the publish step re-run; nothing is lost |
| **Blocked** | a `TODO: needs input` marker inside the refined script | you — the source material is missing something the lesson needs |
| **Published** | a row in `lesson-scripts/published.tsv` with a Wistia URL | nothing |

Partly-authored build folders (plan written but no narration yet, and so on) are counted under *built as compositions* and name their own half-finished stage in the per-program list.

## Published — live on Wistia

| Lesson | Program | Render date | Wistia URL |
|---|---|---|---|
| what-makes-for-a-dream-job_early-career-boost | early-career-boost | 2026-07-17 | https://sclc.wistia.com/medias/gryylc7qns |
| better-decisions-come-from-better-criteria_early-career-boost | early-career-boost | 2026-07-29 | https://sclc.wistia.com/medias/t6cathsymi |
| build-direction-before-you-build-a-plan_early-career-boost | early-career-boost | 2026-08-04 | https://sclc.wistia.com/medias/v2gnkvdcbc |

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

## mid-career-momentum

**Queued to build:**

9. m2_mid-career-mindsets-and-limiting-beliefs
10. m2_the-value-of-building-mid-career-momentum
11. m3_discover-experiences-that-support-your-next-move

**Built — composition only, no MP4 yet:**

*Authored as HyperFrames HTML with narration audio. Each still has to be rendered and verified before it can be published.*

- m1_mini-syllabus
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m1_mini-syllabus mid-career-momentum`
- m2_four-kinds-of-career-transition_mid-career-momentum
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m2_four-kinds-of-career-transition_mid-career-momentum mid-career-momentum`
- m3_building-your-future-you-resume-pt1
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m3_building-your-future-you-resume-pt1 mid-career-momentum`
- m3_from-history-to-signal
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m3_from-history-to-signal mid-career-momentum`
- m3_how-to-reposition-your-career
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m3_how-to-reposition-your-career mid-career-momentum`
- m3_rewrite-your-linkedin-for-future-you
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m3_rewrite-your-linkedin-for-future-you mid-career-momentum`
- m3_using-the-resume-builder-tool-pt2
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m3_using-the-resume-builder-tool-pt2 mid-career-momentum`
- m4_finding-new-peers-sponsors-and-opportunity-holders
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m4_finding-new-peers-sponsors-and-opportunity-holders mid-career-momentum`
- m4_visibility-actions
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m4_visibility-actions mid-career-momentum`
- m4_who-will-walk-this-next-chapter-with-you
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m4_who-will-walk-this-next-chapter-with-you mid-career-momentum`
- m5_skills-for-the-ai-era
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m5_skills-for-the-ai-era mid-career-momentum`
- m6_youve-built-momentum
  - state: HyperFrames composition ready to render; no MP4 exists yet
  - next: render + verify it: `bash scripts/batch-ship.sh m6_youve-built-momentum mid-career-momentum`

## career-transitions

**Queued to build:**

12. m2_four-kinds-of-career-transition_career-transitions
13. m2_welcome-and-using-career-transitions-as-leaps-ahead
14. m3_the-identity-audit
15. m3_the-two-sided-work
16. m4_building-your-carry-forward-inventory
17. m5_testing-your-next-chapter
18. m5_the-story-that-makes-the-change-legible
19. m7_your-reinvention-roadmap

## entrepreneur-accelerator

**Queued to build:**

20. m1_reframing-entrepreneurship-and-going-solo
21. m3_choosing-your-solo-model
22. m4_building-visibility-on-your-own
23. m5_making-solo-work-sustainable

---
Resume: `/render-lessons` AUTO-BATCH starts at the top of the queued list above. Full state model: `bash scripts/batch-status.sh` (terminal) or `bash scripts/batch-status.sh --json` (machine).
