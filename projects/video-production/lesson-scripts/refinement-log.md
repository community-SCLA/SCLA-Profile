# Lesson Script Ledger

**Ledger, not state machine (since 2026-07-13).** A script's *state* is the
folder it sits in — root = raw, `refined/` = render-ready, `rendered/` =
published, with in-flight builds visible as `../renders-hyperframes/<stem>/`
workspaces and filed MP4s in `../renders-mp4/` (see `README.md`). **Never read
this table to decide what to refine, build, ship, or publish.** It is the
human-facing history: dates, locations, Wistia URLs, and notes (including
open questions that make `/refine-scripts` skip a raw script).

| Column | Meaning |
|---|---|
| **Created** | Date the lesson was captured from the SCLA platform |
| **Refined** | Date the refinement pass produced the `refined/` copy |
| **Rendered** | Render date + MP4/Wistia location once shipped/published |
| **Notes** | Open questions, blockers, anything a human should know |

Skills append/update rows at their close-out (`/refine-scripts`,
`/render-lessons` SHIP + PUBLISH); staleness here can't break the pipeline.

## early-career-boost

| Script | Created | Refined | Rendered | Notes |
|---|---|---|---|---|
| `mini-syllabus_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean) | 2026-07-08 → `../renders-mp4/early-career-boost/mini-syllabus_early-career-boost_2026-07-06.mp4` | in `rendered/`; Wistia URL `TODO: needs input` (upload was pending at migration) |
| `better-decisions-come-from-better-criteria_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean) | — | in `refined/`; build workspace live. **Facts provenance blocker:** lesson body/outline never filed as source — needs owner input before ship |
| `build-direction-before-you-build-a-plan_..._2026-07-07.txt` | 2026-07-07 | 2026-07-07 (authored clean) | — | in `refined/`; build workspace live |
| `what-makes-for-a-dream-job_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-15 → `../renders-mp4/early-career-boost/what-makes-for-a-dream-job_early-career-boost_2026-07-10.mp4` · Wistia https://sclc.wistia.com/medias/6g95getfl2 | in `rendered/`; **published** (theme summit, 187.5s, verify PASS). Owner waived the MP4-review gate for this one; filed to Wistia account default project (Lesson-videos project id still `TODO` in endpoints.md) |
| `career-building-is-a-repeatable-process_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-15 → `../renders-mp4/early-career-boost/career-building-is-a-repeatable-process_early-career-boost_2026-07-15.mp4` · Wistia https://sclc.wistia.com/medias/lsgkfzu60w | **published 2026-07-15** to Wistia "Early Career Boost" project (id 10733647). Theme horizon, 166.9s, verify PASS. Owner directed the upload in this session ("just need to be uploaded to wistia") and waived the MP4-review gate. Supersedes the earlier disputed cut `zyr1fq35t7`, which is now **404 / gone** from Wistia — no duplicate remains |
| `do-not-just-ask-what-ai-replaces_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-15 → `../renders-mp4/early-career-boost/do-not-just-ask-what-ai-replaces_early-career-boost_2026-07-15.mp4` · Wistia https://sclc.wistia.com/medias/n18la37w3o | **published 2026-07-15** to Wistia "Early Career Boost" project (id 10733647). Theme cadence, 149.5s, verify PASS, 0 warnings. Owner directed the upload in this session and waived the MP4-review gate |
| `finding-creating-a-career-purpose-statement_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-15 → `../renders-mp4/early-career-boost/finding-creating-a-career-purpose-statement_early-career-boost_2026-07-15.mp4` · Wistia https://sclc.wistia.com/medias/cnmkchs5dt | **published 2026-07-15** to Wistia "Early Career Boost" project (id 10733647). Theme horizon, 127.2s, verify PASS, 1 gray-zone warning. Owner directed the upload in this session and waived the MP4-review gate |
| `how-to-make-strong-career-decisions_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `skills-for-the-ai-era-future_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `using-the-career-map-tool_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `early-career-boost-resources_..._2026-07-10.txt` | 2026-07-10 | — | **RETIRED 2026-07-14** — no video | Owner decided (2026-07-14) the lesson is a pointer to an attached references PDF and needs no video; moved to `early-career-boost/_archive/`. Closes the prior open question. |
| `what-energizes-me_..._2026-07-10.txt` | 2026-07-10 | 2026-07-14 | — | in `refined/` (647→447 words; source thin on narration, faithful over padded). qa-facts **PASS**. NOTE: opening "the five conditions" traces cross-lesson to `what-makes-for-a-dream-job` / "Five Criteria of Engaging Work" (not stated in this lesson's own raw) — defensible, no change; revisit if the criteria lesson is recut to a different count |

## career-readiness-accelerator

No scripts yet — program hasn't started producing videos (see `../README.md`).

## scla-leadership-program

No scripts yet — program hasn't started producing videos (see `../README.md`).
