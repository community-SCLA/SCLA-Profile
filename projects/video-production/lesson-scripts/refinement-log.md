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
| `what-makes-for-a-dream-job_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `career-building-is-a-repeatable-process_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/`; build workspace live (horizon) |
| `do-not-just-ask-what-ai-replaces_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `finding-creating-a-career-purpose-statement_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/`; build workspace live (horizon), two verified MP4 renders in the workspace awaiting the new gate flow |
| `how-to-make-strong-career-decisions_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `skills-for-the-ai-era-future_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `using-the-career-map-tool_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `early-career-boost-resources_..._2026-07-10.txt` | 2026-07-10 | — | — | raw, at root. **Open question — skip in /refine-scripts:** lesson is just a pointer to an attached references PDF; does it need a video at all? |
| `what-energizes-me_..._2026-07-10.txt` | 2026-07-10 | 2026-07-14 | — | in `refined/` (647→447 words; source thin on narration, faithful over padded). qa-facts **PASS**. NOTE: opening "the five conditions" traces cross-lesson to `what-makes-for-a-dream-job` / "Five Criteria of Engaging Work" (not stated in this lesson's own raw) — defensible, no change; revisit if the criteria lesson is recut to a different count |

## career-readiness-accelerator

No scripts yet — program hasn't started producing videos (see `../README.md`).

## scla-leadership-program

No scripts yet — program hasn't started producing videos (see `../README.md`).
