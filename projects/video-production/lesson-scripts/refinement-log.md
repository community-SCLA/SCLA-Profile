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
| `mini-syllabus_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean) | 2026-07-22 → `../renders-mp4/early-career-boost/mini-syllabus_early-career-boost_2026-07-22.mp4` · Wistia https://sclc.wistia.com/medias/nj4n0073vn | in `rendered/`; **published 2026-07-22** to Wistia "Early Career Boost" project (id 10733647), hashedId `nj4n0073vn`, 86.4s. Now **fully re-branded** — both the on-screen header AND the spoken narration say "Career Accelerator" (owner directed the audio re-voice 2026-07-22; MP4-review gate waived). Rebuilt on the current per-scene pipeline (data-narration + cue anchors; synth/compile/preflight all PASS). ⚠ **verify_render presence FAILs on false positives** (6 stagnant/near-blank flags) — every flagged frame pixel-verified correct + on-brand; the legacy 2026-07-06 compositions have low-amplitude ambient + light-theme frames that under-register at QA sampling (same class as the 2026-07-15 depth-drift note). Ambient bumped toward the fix; a full re-animation of these bespoke comps is a separate future pass. **Owner action:** archive the superseded audio-wrong copy `2ilh1o6c4g` on Wistia (still in folder; token can't delete) |
| `better-decisions-come-from-better-criteria_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean) | — | in `refined/`; build workspace live. **Facts provenance blocker:** lesson body/outline never filed as source — needs owner input before ship |
| `build-direction-before-you-build-a-plan_..._2026-07-07.txt` | 2026-07-07 | 2026-07-07 (authored clean) | — | in `refined/`; build workspace live |
| `what-makes-for-a-dream-job_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-21 → `../renders-mp4/early-career-boost/what-makes-for-a-dream-job_early-career-boost_2026-07-17.mp4` · Wistia https://sclc.wistia.com/medias/gryylc7qns | in `rendered/`; **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `gryylc7qns`, 187.5s, theme summit. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `6g95getfl2` (old header) moved to Wistia archive by owner 2026-07-21 |
| `career-building-is-a-repeatable-process_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-21 → `../renders-mp4/early-career-boost/career-building-is-a-repeatable-process_early-career-boost_2026-07-17.mp4` · Wistia https://sclc.wistia.com/medias/6413m7yywi | **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `6413m7yywi`, 168.7s, theme horizon, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `lsgkfzu60w` (old header) moved to Wistia archive by owner 2026-07-21. Earlier disputed cut `zyr1fq35t7` already 404 / gone |
| `do-not-just-ask-what-ai-replaces_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-21 → `../renders-mp4/early-career-boost/do-not-just-ask-what-ai-replaces_early-career-boost_2026-07-17.mp4` · Wistia https://sclc.wistia.com/medias/8ry7t1ma6x | **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `8ry7t1ma6x`, 148.6s, theme cadence, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `n18la37w3o` (old header) moved to Wistia archive by owner 2026-07-21 |
| `finding-creating-a-career-purpose-statement_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-21 → `../renders-mp4/early-career-boost/finding-creating-a-career-purpose-statement_early-career-boost_2026-07-17.mp4` · Wistia https://sclc.wistia.com/medias/euxv2h3c20 | **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `euxv2h3c20`, 127.3s, theme horizon, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `cnmkchs5dt` (old header) moved to Wistia archive by owner 2026-07-21 |
| `how-to-make-strong-career-decisions_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `skills-for-the-ai-era-future_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `using-the-career-map-tool_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | — | in `refined/` |
| `early-career-boost-resources_..._2026-07-10.txt` | 2026-07-10 | — | **RETIRED 2026-07-14** — no video | Owner decided (2026-07-14) the lesson is a pointer to an attached references PDF and needs no video; moved to `early-career-boost/_archive/`. Closes the prior open question. |
| `what-energizes-me_..._2026-07-10.txt` | 2026-07-10 | 2026-07-14 | 2026-07-21 → `../renders-mp4/early-career-boost/what-energizes-me_early-career-boost_2026-07-17.mp4` · Wistia https://sclc.wistia.com/medias/yr8c7ajrjw | in `rendered/`; **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `yr8c7ajrjw`, 163.7s, theme summit, 18 scenes, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `of5caanz21` (old header) moved to Wistia archive by owner 2026-07-21. Refine notes (unchanged): 647→447 words; qa-facts **PASS**. NOTE: opening "the five conditions" traces cross-lesson to `what-makes-for-a-dream-job` / "Five Criteria of Engaging Work" — defensible, no change |

## career-readiness-accelerator

No scripts yet — program hasn't started producing videos (see `../README.md`).

## scla-leadership-program

No scripts yet — program hasn't started producing videos (see `../README.md`).
