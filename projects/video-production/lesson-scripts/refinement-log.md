# Lesson Script Ledger

**Ledger, not state machine (since 2026-07-13).** A script's *state* is the
folder it sits in — `inbox/` = raw, `ready/` = render-ready, `published/` =
live on Wistia, with in-flight builds visible as `../renders-hyperframes/<stem>/`
workspaces and filed MP4s in `../renders-mp4/` (see `README.md`). **Never read
this table to decide what to refine, build, ship, or publish.** It is the
human-facing history: dates, locations, Wistia URLs, and notes (including
open questions that make `/refine-scripts` skip a raw script).

⚠ **Rows written before 2026-08-04 use the retired folder vocabulary.** Read
`refined/` as today's `ready/` and `rendered/` as today's `published/`; program
root became `inbox/`. Those folders no longer exist on disk — an "in `refined/`"
note is a historical statement, not a current location. The live answer is
always `bash scripts/batch-status.sh`.

| Column | Meaning |
|---|---|
| **Created** | Date the lesson was captured from the SCLA platform |
| **Refined** | Date the refinement pass produced the `ready/` copy |
| **Rendered** | Render date + MP4/Wistia location once shipped/published |
| **Notes** | Open questions, blockers, anything a human should know |

Skills append/update rows at their close-out (`/refine-scripts`,
`/render-lessons` SHIP + PUBLISH); staleness here can't break the pipeline.

## early-career-boost

| Script | Created | Refined | Rendered | Notes |
|---|---|---|---|---|
| `what-makes-for-a-dream-job_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-07-21 → `../renders-mp4/early-career-boost/what-makes-for-a-dream-job_early-career-boost_2026-07-17.mp4` · Wistia https://sclc.wistia.com/medias/gryylc7qns | in `rendered/`; **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `gryylc7qns`, 187.5s, theme summit. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `6g95getfl2` (old header) moved to Wistia archive by owner 2026-07-21 |
| `career-building-is-a-repeatable-process_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-08-05 → `../renders-mp4/early-career-boost/career-building-is-a-repeatable-process_early-career-boost_2026-08-05.mp4` · Wistia https://sclc.wistia.com/medias/cnj1463xuw | **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `6413m7yywi`, 168.7s, theme horizon, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `lsgkfzu60w` (old header) moved to Wistia archive by owner 2026-07-21. Earlier disputed cut `zyr1fq35t7` already 404 / gone. **UNPUBLISHED 2026-07-29** — owner archived `6413m7yywi` on Wistia: banner read "Career Accelerator", not "Early Career Boost". Script returned to `refined/`, `published.tsv` row removed; requeued for rebuild · published 2026-08-05 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `do-not-just-ask-what-ai-replaces_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-08-06 → `../renders-mp4/early-career-boost/do-not-just-ask-what-ai-replaces_early-career-boost_2026-08-06.mp4` · Wistia https://sclc.wistia.com/medias/uhnqbjt0x7 | **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `8ry7t1ma6x`, 148.6s, theme cadence, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `n18la37w3o` (old header) moved to Wistia archive by owner 2026-07-21. **UNPUBLISHED 2026-07-29** — owner archived `8ry7t1ma6x` on Wistia: banner read "Career Accelerator", not "Early Career Boost". Script returned to `refined/`, `published.tsv` row removed; requeued for rebuild · published 2026-08-06 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `finding-creating-a-career-purpose-statement_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-08-05 → `../renders-mp4/early-career-boost/finding-creating-a-career-purpose-statement_early-career-boost_2026-08-05.mp4` · Wistia https://sclc.wistia.com/medias/0szz79g9m7 | **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `euxv2h3c20`, 127.3s, theme horizon, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `cnmkchs5dt` (old header) moved to Wistia archive by owner 2026-07-21. **UNPUBLISHED 2026-07-29** — owner archived `euxv2h3c20` on Wistia: banner read "Career Accelerator", not "Early Career Boost". Script returned to `refined/`, `published.tsv` row removed; requeued for rebuild · published 2026-08-05 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `how-to-make-strong-career-decisions_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-08-05 → `../renders-mp4/early-career-boost/how-to-make-strong-career-decisions_early-career-boost_2026-08-05.mp4` · Wistia https://sclc.wistia.com/medias/u54hifguqf | in `refined/` · published 2026-08-05 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `skills-for-the-ai-era-future_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-08-05 → `../renders-mp4/early-career-boost/skills-for-the-ai-era-future_early-career-boost_2026-08-05.mp4` · Wistia https://sclc.wistia.com/medias/r21mwmy2tn | in `refined/` · published 2026-08-05 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `using-the-career-map-tool_..._2026-07-10.txt` | 2026-07-10 | 2026-07-12 | 2026-08-05 → `../renders-mp4/early-career-boost/using-the-career-map-tool_early-career-boost_2026-08-05.mp4` · Wistia https://sclc.wistia.com/medias/599zwe5ii9 | in `refined/` · published 2026-08-05 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `early-career-boost-resources_..._2026-07-10.txt` | 2026-07-10 | — | **RETIRED 2026-07-14** — no video | Owner decided (2026-07-14) the lesson is a pointer to an attached references PDF and needs no video; moved to `early-career-boost/_archive/`. Closes the prior open question. |
| `what-energizes-me_..._2026-07-10.txt` | 2026-07-10 | 2026-07-14 | 2026-08-05 → `../renders-mp4/early-career-boost/what-energizes-me_early-career-boost_2026-08-05.mp4` · Wistia https://sclc.wistia.com/medias/0lbi1p8due | in `rendered/`; **re-published 2026-07-21** to Wistia "Early Career Boost" project (id 10733647), hashedId `yr8c7ajrjw`, 163.7s, theme summit, 18 scenes, verify PASS. On-screen program label re-branded **"Early Career Boost" → "Career Accelerator"** (owner-directed bulk fix, MP4-review gate waived). Superseded copy `of5caanz21` (old header) moved to Wistia archive by owner 2026-07-21. Refine notes (unchanged): 647→447 words; qa-facts **PASS**. NOTE: opening "the five conditions" traces cross-lesson to `what-makes-for-a-dream-job` / "Five Criteria of Engaging Work" — defensible, no change. **UNPUBLISHED 2026-07-29** — owner archived `yr8c7ajrjw` on Wistia: banner read "Career Accelerator", not "Early Career Boost". Script returned to `refined/`, `published.tsv` row removed; requeued for rebuild · published 2026-08-05 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `build-direction-before-you-build-a-plan_..._2026-07-07.txt` | 2026-07-07 | 2026-07-07 (authored clean) | 2026-08-04 → `../renders-mp4/early-career-boost/hyperframes/build-direction-before-you-build-a-plan_early-career-boost_2026-08-04.mp4` · Wistia https://sclc.wistia.com/medias/v2gnkvdcbc | in `published/`; published 2026-08-04 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `mini-syllabus_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean) | 2026-08-06 → `../renders-mp4/early-career-boost/mini-syllabus_early-career-boost_2026-08-06.mp4` · Wistia https://sclc.wistia.com/medias/ays7di6sti | in `rendered/`; **published 2026-07-22** to Wistia "Early Career Boost" project (id 10733647), hashedId `nj4n0073vn`, 86.4s. Now **fully re-branded** — both the on-screen header AND the spoken narration say "Career Accelerator" (owner directed the audio re-voice 2026-07-22; MP4-review gate waived). Rebuilt on the current per-scene pipeline (data-narration + cue anchors; synth/compile/preflight all PASS). ⚠ **verify_render presence FAILs on false positives** (6 stagnant/near-blank flags) — every flagged frame pixel-verified correct + on-brand; the legacy 2026-07-06 compositions have low-amplitude ambient + light-theme frames that under-register at QA sampling (same class as the 2026-07-15 depth-drift note). Ambient bumped toward the fix; a full re-animation of these bespoke comps is a separate future pass. **Owner action:** archive the superseded audio-wrong copy `2ilh1o6c4g` on Wistia (still in folder; token can't delete). **UNPUBLISHED 2026-07-29** — owner archived `nj4n0073vn` on Wistia: banner read "Career Accelerator", not "Early Career Boost". Script returned to `refined/`, `published.tsv` row removed; requeued for rebuild. ⚠ The 2026-07-22 re-voice put "Career Accelerator" in the **spoken** line 1 as well; both instances reverted to "Early Career Boost" in the refined script, so this rebuild needs a fresh TTS pass, not just a new banner · published 2026-08-06 (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable |
| `better-decisions-come-from-better-criteria_..._2026-07-06.txt` | 2026-07-06 | 2026-07-06 (authored clean) | 2026-07-29 → `../renders-mp4/early-career-boost/hyperframes/better-decisions-come-from-better-criteria_early-career-boost_2026-07-29.mp4` · Wistia https://sclc.wistia.com/medias/t6cathsymi | in `refined/`; facts provenance blocker resolved 2026-07-25 (owner confirmed ready to ship) · published 2026-07-29 (AUTO-BATCH); local MP4 deleted after upload, workspace pruned in place and still editable |

## mid-career-momentum

**Re-captured & re-drained 2026-07-23.** The owner re-captured the whole program
from the SCLA admin dashboard under a renumbered/retitled scheme (M1–M6, 15
lessons), superseding the 2026-07-22 organization (whose `refined/` batch was
removed in the same re-capture). All 15 raw captures were drained the same day:
**15 refined, 0 skipped** — the old `m4_visibility-actions` skip is resolved (see
that row). Raw originals preserved in commit `dfdb91b` (committed before removal)
— facts findings cite raw line numbers. **No curriculum source is filed for this
program** (`programs/` has no `mid-career-momentum/`); each raw (dashboard status:
Draft) is its own self-attesting source of record. Every facts pass flagged this:
the program has no independent fact floor — all verdicts are faithful-to-raw only.

| Script | Created | Refined | Rendered | Notes |
|---|---|---|---|---|
| `m1_mini-syllabus_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 253 spoken source→262 words. qa-facts **PASS**. Short syllabus/opener (~2.5 min) by design — not padded. Names Career Accelerator, #questionsupport, the 90-day commitment |
| `m2_the-value-of-building-mid-career-momentum_...` | 2026-07-23 | 2026-08-04 | — | in `ready/`; ~146 spoken source→~330 words. qa-facts **PASS** (re-run 2026-08-04). **Unblocked 2026-08-04:** the `TODO: needs input` (value/"why now" section absent from source) is resolved by deriving the value section from the program's own modules, none invented — m6 L3 (two arrival feelings, noise vs. paper), m0/m1 L3 (pause/reassess/deliberately choose vs. drift), m0/m1 L9 (next realistic move, 6–12 months, small consistent steps), m6 L21 (momentum decays), m6 L27 (small/consistent/compounding), m0/m1 L11 (90-day anchor). Same source-derivation method as the m6 recap fix (2026-07-22). check_copy script mode PASS |
| `m2_mid-career-mindsets-and-limiting-beliefs_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; ~290 spoken source→227 words. qa-facts **PASS**. Short but complete — three named limiting beliefs, three reframes (leverage point / career experiments / re-design thinking), one task |
| `m2_four-kinds-of-career-transition_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 558 corrected-spoken source→530 words. qa-facts **PASS**. The raw now carries an owner-directed 2026-07-23 correction supplying a consistent four-path script (Pivot / Reinvention / Rebuild / Forced Reinvention); refinement kept the corrected section and dropped the superseded three-path original — internally consistent (title, enumeration, choosing-instruction all agree on four). ⚠ **Owner-actionable (metadata):** raw dashboard slug still reads `three-paths-for-your-next-move` — confirm the slug. See cross-lesson taxonomy note below |
| `m3_building-your-future-you-resume-pt1_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 1036→624 words. qa-facts **PASS**. Next Move Statement + four-part lens + Resume Builder Tool handoff to pt2 all intact. Sample-bullet figures (30% time-to-productivity, 20% satisfaction) kept as example copy — ⚠ stat-card framing risk at the hyperframe gate if rendered standalone |
| `m3_discover-experiences-that-support-your-next-move_...` | 2026-07-23 | 2026-08-04 | — | in `ready/`; ~285 spoken source→~330 words. qa-facts **PASS** (re-run 2026-08-04). **Unblocked 2026-08-04:** the `TODO: needs input` (formula parts named but undefined) is resolved with the four definitions taken near-verbatim from this program's own `m3_using-the-resume-builder-tool-pt2` L5 (Responsibility—expected to do / Action—actually did / Measurable outcome—what changed / Scope—how big, who involved). check_copy script mode PASS |
| `m3_from-history-to-signal_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; ~262 spoken source→373 words. qa-facts **PASS** with two NOTE-level "just" minimizers the refine introduced (L5 "scanning for just a few things"; L9 "the other just lists duties") — trivially fixable in the review buffer. "reduced onboarding time by 30%" kept as sample resume copy — ⚠ stat-card risk if rendered standalone |
| `m3_how-to-reposition-your-career_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 1255→527 words. qa-facts **PASS**. Alex/Jordan/Priya personas (fictional, no PII); 25%/30% kept as sample bullet copy; Clarify→Curate→Translate→Update framework + "60-second career story" callback intact. Names 3-path set — see cross-lesson taxonomy note below |
| `m3_rewrite-your-linkedin-for-future-you_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; ~232 spoken source→329 words. qa-facts **PASS**. Quantifier "Many" and recruiter hedge "often see" preserved (not escalated). NOTE: one soft framing sentence added at L3 ("That's your first impression…") — non-contradictory, human-gate discretion |
| `m3_using-the-resume-builder-tool-pt2_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 1156→670 words (slightly over target — load-bearing enumerations kept complete). qa-facts **PASS**. AI-rewrite example figures (18% / 25% / 30–40 / quarterly) kept explicitly framed as illustrative tool output, with the raw's own accuracy caveat retained — ⚠ stat-card risk at the hyperframe gate. Names 3-path set — see cross-lesson taxonomy note below |
| `m4_finding-new-peers-sponsors-and-opportunity-holders_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; ~510 spoken source→487 words. qa-facts **PASS**. Three relationship types + three "how to find" lists + Next Move Statement callback + 20-min learning conversation + 3–5 activity all intact |
| `m4_visibility-actions_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; ~310 spoken source→281 words. qa-facts **PASS**. ✅ **Old skip resolved:** this is a NEW, distinct capture that genuinely defines & demonstrates visibility actions (definition + five examples + design-3/test-1-in-30-days activity) — machine-verified distinct from `m4_who-will-walk` (different md5). Refine stripped an unsourced "research on professional visibility shows…" stat tangent; facts confirms no residue |
| `m4_who-will-walk-this-next-chapter-with-you_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 602 spoken source→561 words. qa-facts **PASS**. Four relationship-type labels (peer/sponsor/opportunity holder/mentor) anchored in raw body prose; NOTE: their descriptor tails were promoted from an on-screen card cue into narration — supported by the raw, human-gate discretion |
| `m5_skills-for-the-ai-era_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 523 spoken source (dashboard script + companion article)→523 words. qa-facts **PASS**, no Early Career Boost ancestor leak, six-link "Additional Resources" list dropped with no citation leak. Full-length now (the raw carried a companion article). ⚠ **Owner-actionable (asset):** raw production note still says the backing video is an open dashboard slot ("insert your existing lesson video here") — narration is complete, the clip is not chosen |
| `m6_youve-built-momentum_...` | 2026-07-23 | 2026-07-23 | — | in `refined/`; 720 raw→420 words. qa-facts **PASS**. Recap traces to the raw's owner-directed correction (modules renumbered 2→6, outreach verb "drafted" not "sent", Module 5 AI content real not the old fabricated "confidence gauge"); emphatic "just" preserved. **Two owner-actionable items remain in the script verbatim** (both present in the corrected raw, carried through per the no-fabrication rule, not numbering errors): (1) a reusable four-category framework "Outcome / Visibility / Relationships / Results" that is **taught nowhere** in the program (and collides with the real four-part lens); (2) umbrella name "**The Career Accelerator** … more tracks, more tools, and a member community" — correctness unconfirmed (KB program of record is *Career Readiness Accelerator*; community is the separate theCOMMUNITY.com) |
| `m0_welcome-to-mid-career-momentum` | 2026-07-22 | 2026-07-23 | — | **Requeued as illustrated 2026-08-04** when the HeyGen avatar lane was deleted (it was the lane's only script). Date dropped from the stem on the way — a working artifact carries none. Refined 280→276 words. qa-facts **FAIL**, both defects inherited verbatim from the raw: (1) the "broader Career Accelerator journey" program-name defect is **fixed** in the body; (2) the `#questionsupport channel` **is still open** — no channel of that name exists in `member-support/community-platform.md` (all help channels use a `help-*` prefix). **Closed 2026-08-04:** the owner confirmed `#questionsupport` is a real, newly added channel on the SCLA dashboard — the narration was right and the source directory was stale. Fixed at the source: the channel is now a row in `member-support/community-platform.md`'s help-channel table, so qa-facts stops re-raising it here and in the two other `ready/` scripts that name it (`m1_mini-syllabus`, `mini-syllabus_early-career-boost`). Marker deleted; the lesson is READY |

**Cross-lesson taxonomy (program-wide, owner-actionable):** `m2_four-kinds-of-career-transition` teaches a **four-kind** model (Pivot / Reinvention / Rebuild / Forced Reinvention), while `m2_the-value…`, `m3_how-to-reposition`, and `m3_using-the-resume-builder-tool-pt2` all name a **three-path** set (promotion / lateral move / role redesign). Each script is faithful to its own raw, so this is not a facts defect in any one script — but a learner moving across the program meets two different transition taxonomies. Owner should confirm whether this is intentional or the lessons should be aligned.

**Dashboard reconciliation 2026-07-23 (post-drain):** all 15 refined scripts
trace 1:1 to the 15 `▶ VIDEO` blocks in the live `/api/admin/program/mid-career-momentum`
JSON (every dashboard script is ≥92% n-gram-contained in its preserved raw;
`m5_skills-for-the-ai-era` sources from the whole lesson body incl. companion
article, as its ledger row already records). **Nothing left behind.** Four
dashboard lesson components carry **no video block at all** — M2 "AI Feedback:
What Energizes You Mid-Career?", M2 "Discussion Prompt: What's Shaping Your
Next Move?", M2 "Creating Your Next Move Statement", M7 "Resources" — so no
script exists to capture for them; owner should confirm whether they're meant
to get videos (the "every lesson has a video" expectation fails only in the
dashboard itself, not in the capture).

## career-transitions

**Captured from the SCLA admin dashboard 2026-07-23**; reconciled against the
live `/api/admin/program/career-transitions` JSON 2026-07-23 (**all 8 captures
verbatim, n-gram containment 1.00 both directions, no dashboard video block
lacks a capture**). Dashboard is Draft; program has 8 modules. Dashboard
components with no video block: M1 Mini-Syllabus (unlike the other track
programs, it has none), M8 Resources. M6 "Reinventing with AI" is an explicit
reuse slot ("Use the same video from Early Career Boost") — no script to
capture, mirrors mid-career-momentum M5.

**Drained 2026-07-24 (`/refine-scripts`): all 8 refined, 0 skipped.** No
independent curriculum is filed under `programs/` for this program, so each raw
capture is its own faithful source of record — qa-facts verdicts are
faithful-to-raw only (no independent fact floor). NOTE: the `refined/` copies
were found already drafted+committed by a prior partial run that never ran the
facts pass or the bookkeeping; this drain supplied the mandatory qa-facts pass
on all 8, applied one fix, and completed the raw removal. Raw originals removed
from root (preserved in git history) — facts findings cite raw line numbers.

| Script | Created | Refined | Rendered | Notes |
|---|---|---|---|---|
| `m2_welcome-and-using-career-transitions-as-leaps-ahead_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **PASS**. Cue-strip + trivial rewordings only; Feiler/Ibarra, 3–5 transitions/~5 yrs, Tracks 1/2/3, 5-modules/3-things all trace to raw |
| `m2_four-kinds-of-career-transition_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **PASS** (2 NOTE: hedge "often" dropped in 3 spots; tricolon "more complexity" omitted — stylistic, no overclaim). ⚠ Same lesson title as mid-career-momentum's m2 but a **different taxonomy** (Growth Pivot / Reinvention / Redirect / Rebuild on a chosen-vs-forced × adjacent-vs-dramatic 2×2) — the CT program's own model, faithful to source, not a capture error |
| `m3_the-two-sided-work_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **PASS** (2 NOTE pov-drift: "Let me"→"Let's", "I see"→"we see" — cosmetic). Bridges/Ibarra/Dorie Clark refs + carry-forward 4-item set all trace to raw |
| `m3_the-identity-audit_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **FAIL→fixed**. Refine had dropped the raw's "(Forbes, 2026)" citation while keeping the empirical "evidence-based practices" claim as bare fact; **fixed 2026-07-24** by restoring spoken attribution ("As Forbes reported in twenty twenty-six…") — faithful to raw. Five identity layers + three audit questions intact; concentric-circles design spec correctly stripped |
| `m4_building-your-carry-forward-inventory_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **PASS** (2 NOTE added-gloss: two interpretive tails answer prompts the raw only poses — non-contradicting). Graphic-heavy source (no labeled Script): all four categories (Skills/Values/Relationships/Insights) with defs+prompts voiced complete; 1600×700px design spec stripped. Earlier "owner may need to supply narration" flag resolved — the block carried enough sourced content to refine faithfully |
| `m5_testing-your-next-chapter_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **PASS**. Ibarra/Harvard/INSEAD, design-three-experiments, 25-min / 10-20-30-hr / "saved you a year" figures all trace to raw |
| `m5_the-story-that-makes-the-change-legible_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **PASS**. Ibarra & Barbulescu, 3-part pivot story, 3 failure modes, module deliverables all trace to raw; "Harvard" attribution dropped (safe subtraction). Dashboard M5 "Your Pivot Story and Positioning" |
| `m7_your-reinvention-roadmap_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; qa-facts **PASS**. Completion/recap lesson; Ibarra ref, 18-months, four roadmap elements, 90-day rationale all trace to raw; no recap line references a module/activity absent from the program. Dashboard M7 "Completion & Your Reinvention Roadmap" |

## entrepreneur-accelerator

**Captured from the SCLA admin dashboard 2026-07-23** (dashboard program name
"Entrepreneurship Accelerator", slug `entrepreneur-accelerator`, Draft, 6
modules). Reconciled against the live program JSON 2026-07-23: **all 5 captures
verbatim (containment 1.00), no dashboard video block lacks a capture** — but
see the m1/m2 duplication below. Dashboard components with no video block:
M2 "Going Solo - What Should I Do?", M6 "Launching Your Solo Adventure",
M6 "Resources".

**Drained 2026-07-24 (`/refine-scripts`): 4 refined, 1 skipped** (`m2` — the
m1-duplicate, see its row). No independent curriculum is filed under `programs/`
for this program, so each raw capture is its own faithful source of record —
qa-facts verdicts are faithful-to-raw only. Raw originals of the 4 refined
scripts removed from root (preserved in git history); `m2` stays raw at root.

| Script | Created | Refined | Rendered | Notes |
|---|---|---|---|---|
| `m1_reframing-entrepreneurship-and-going-solo_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; 332→267 words. qa-facts **PASS**. Program opener; 5-item module roadmap (experiment / freelance-consulting-fractional / package offer / draft outreach / 30–90 day plan) complete and unaltered. Dashboard M1 Mini-Syllabus video |
| `m2_why-build-your-own-path_2026-07-23.txt` | 2026-07-23 | — | — | **SKIPPED at /refine-scripts 2026-07-24 (re-confirmed).** ⚠ Byte-identical (md5 `226e875…`) to `m1_reframing…`, faithfully so — the dashboard carries the SAME script under both M1 "Reframing Entrepreneurship & Going Solo" and M2 "Why Build Your Own Path". Not a capture error; a dashboard authoring gap. Stays raw at root. **Owner-actionable: supply a distinct script for one of the two videos** — refining both as-is produces two videos with identical narration |
| `m3_choosing-your-solo-model_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; 267→~290 words. qa-facts **FAIL→fixed**. Refine had escalated the raw's hedges/comparatives into absolutes; **fixed 2026-07-24** by restoring raw framing ("often paid", "more on clarity…than", "part-time leader or owner", "more embedded…more accountable"). Three solo models (Freelance/Consulting/Fractional) + example roles intact |
| `m4_building-visibility-on-your-own_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; 766→595 words. qa-facts **PASS**. Six enumerated sets (3 first-client sources / 4 building blocks / 3-part story / 5 touchpoints / 5 AI uses / 4-item deliverable) all complete + correctly ordered; example offer statements kept as examples, not SCLA facts. Content was real narration with on-screen cues — usable as-is |
| `m5_making-solo-work-sustainable_2026-07-23.txt` | 2026-07-23 | 2026-07-24 | — | in `refined/`; 236→218 words. qa-facts **PASS**. Five-piece solo system (tracking / intake / templates / weekly review / boundaries) complete; short by design (source carried ~217 spoken words — not padded). Dashboard M5 "Building a Solo System" |


## career-readiness-accelerator

No scripts yet — program hasn't started producing videos (see `../README.md`).

## scla-leadership-program

No scripts yet — program hasn't started producing videos (see `../README.md`).
