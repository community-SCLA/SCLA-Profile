# Lesson Script Refinement Log

Tracks each script's lifecycle — **captured → refined → rendered** — so an agent can tell at a glance which `.txt` files in this folder are actually safe to hand to HyperFrames, without re-reading every file to check.

## How to read this

| Column | Meaning |
|---|---|
| **Created** | Date the lesson was captured from the SCLA platform (from the raw capture's `Captured:` header, or the filename's date suffix before refinement stripped the header) |
| **Refined** | Date raw-capture artifacts (`LESSON CAPTURE` metadata, `[IMAGE]`/`[VIDEO]` markers, chart-description prose, duplicated lines) were converted into clean spoken narration. **Blank = still raw — do not render.** |
| **Rendered** | Date + location if an MP4 already exists (`../renders-mp4/` or Wistia) |
| **Ready to render?** | ✅ only when Refined is filled in *and* Rendered is empty. Rendered scripts are done; raw scripts need the refinement pass first (style + process: `../script-templates/course-script-prompt.md`, worked example below). |

Update this table whenever a script is refined or rendered — it's the fast-path check so agents don't have to open every `.txt` to find out.

## early-career-boost

| Script | Created | Refined | Rendered | Ready to render? |
|---|---|---|---|---|
| `mini-syllabus_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean, no capture pass needed) | 2026-07-08 → `../renders-mp4/early-career-boost/mini-syllabus_early-career-boost_2026-07-06.mp4` | Already rendered — skip |
| `better-decisions-come-from-better-criteria_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean) | — | ✅ |
| `build-direction-before-you-build-a-plan_..._2026-07-07.txt` | 2026-07-07 | 2026-07-07 (authored clean) | — | ✅ |
| `what-makes-for-a-dream-job_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | ✅ |
| `career-building-is-a-repeatable-process_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | ✅ |
| `do-not-just-ask-what-ai-replaces_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | ✅ |
| `finding-creating-a-career-purpose-statement_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | ✅ |
| `how-to-make-strong-career-decisions_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | ✅ |
| `skills-for-the-ai-era-future_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | ✅ |
| `using-the-career-map-tool_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | ✅ |
| `early-career-boost-resources_..._2026-07-10.txt` | 2026-07-10 | — *(still a raw capture)* | — | ⛔ Not ready — see note below |
| `what-energizes-me_..._2026-07-10.txt` | 2026-07-10 | — *(still a raw capture)* | — | ⛔ Not ready |

**Open questions on the two raw files:**
- `early-career-boost-resources` — this lesson is just a pointer to an attached references PDF, not taught content. Worth confirming with a human whether it needs a video at all before spending a refinement pass on it.
- `what-energizes-me` — references an attached worksheet PDF and an AI-coach activity; refine using the same process as the seven scripts above (strip `LESSON CAPTURE` header, `[IMAGE]`/`[VIDEO]` markers, condense to ~580 words of second-person narration).

## career-readiness-accelerator

No scripts yet — program hasn't started producing videos (see `../README.md`).

## scla-leadership-program

No scripts yet — program hasn't started producing videos (see `../README.md`).
