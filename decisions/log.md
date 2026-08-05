---
source: manual
generated_by: source-of-truth-curator
last_updated: 2026-07-09
confidence: high
---

# SCLA Decisions Log

Running log of notable team decisions. Append new entries at the top.

## 2026-08-05 — Taste becomes a judged stage (concept competition + critic lane)

**The verdict that forced it:** the owner rejected the
`career-building-is-a-repeatable-process_early-career-boost` pilot as "pretty
boring … lackluster illustrations, not a lot of illustrative variation or
movement" — a build that was **gate-clean including the armed pace gates**.
Its carrier was a minimal 6-dot circle on near-empty navy frames for all 42
beats: the cheapest legal satisfaction of carrier persistence + low churn.
Where the 2026-08-04 rejection was SLOW (pace, no carrier), this one is THIN
(pace fine, carrier without substance) — the two failures point in opposite
directions and the approved cuts sit between them. Root cause: every gate is
a floor against a known defect; nothing in the pipeline exerted pressure
toward visual ambition, so a gate-optimizing builder lands on
minimum-viable-pass.

**Decision (owner-approved):** taste is judged by agents against pinned
references, at the two cheapest points in the pipeline — both BEFORE the
render, which is the machine-wide serialized bottleneck:

1. **Concept competition** (`/render-lessons` B2): per video, two independent
   pitch lenses (metaphor-first, accumulation-first) + one vision judge that
   grades against the reference contact sheets and writes
   `_concepts/<stem>/CONCEPT.md` — chosen angle, milestone frames, what
   accumulates, payoff beat. The builder starts from it and may sharpen,
   never silently replace. Competition judged once was chosen over a mutual
   peer-review mesh deliberately: reviewers reviewing each other converge
   and get polite; independent pitches + one judge stay sharp and cost less.
2. **Advisory taste lane** in every precheck vision review, beside the
   blocking defect lane: grades real contact-sheet pixels against the
   critic questions in `design-system/docs/taste.md`, verdict ALIVE/FLAT
   with beats named. FLAT buys exactly ONE revision pass; taste alone never
   quarantines a video or stops a batch.

**Explicitly NOT done, and why:** no numeric "richness" thresholds — the
bracket is three cuts, and 2026-08-04 already proved what constants derived
from too few references do (approved the boring cut, quarantined the approved
one). This entry also **closes the open "freeform variety contract" item**
(snag-log 2026-08-05): the retired variety checkers (consecutive-family,
distinct-forms, 40% ceiling) stay retired as Conventions; freeform variety is
judged by the taste stage, not counted.

**Artifacts:** rubric + bracket at `design-system/docs/taste.md`; the
rejected cut filed to
`renders-hyperframes/_reference/…_2026-08-05-thin-carrier-backup` (local-only
evidence, contact sheets intact); mechanisms in `/render-lessons` B2/B4/SHIP,
`batch-precheck.sh`'s two-lane handoff, and `batch-prepare.sh`'s builder read
order. The pilot rebuilds through the new stages and stops at the same human
gate.

## 2026-08-05 — The template lane is retired

**Decision:** following the owner's approval of the freeform `m1_mini-syllabus`
trial (entry below), the template lane is **fully retired, now, not staged** —
freeform (agent-native) is the default and ONLY way an SCLA lesson video is
built. This entry supersedes, by name, the 2026-07-30 clauses *"Nothing is
retired yet… the template lane keeps shipping untouched"*, the `--freeform`
opt-in flag, and *"freeform never enters AUTO-BATCH while its quality floor is
unproven"* — the floor was proven by the approved trial and the B1 pace gates.
A future session that reads 2026-07-30 without this entry rebuilds the old
default; do not.

**Archived, not deleted — an explicit owner override of `repo-hygiene.md`'s
delete-first default.** Everything moved to a nested `_archive/` inside its own
directory, read-only provenance:

- `render-qa/_archive/src/` — the scenes.json → index.html compiler
  (`build_index.py`, `instance_templates.py`) and the template-shaped gates:
  `boxmodel.py` + `check_geometry.py` (measured confidently wrong on freeform
  CSS: 281 false findings on a build verified clean across 34 stills),
  `check_capacity.py` (per-slot maxLines needs slots), `check_slots.py` (its
  one lane-neutral rule, the placeholder scan, was already rehomed into
  `check_copy.py`), `check_variety.py` (one-item-list/one-card rehomed onto
  element structure in `check_forms.py`; three rules orphaned — below), and
  `theme_for.py` (style-package rotation fed compiler slot variables).
- `render-qa/_archive/tests/` — `test_build_index.py`, `test_variety.py`,
  `test_theme_rotation.py`, and the compiler mutation harness's base fixture.
- `scripts/_archive/hyperframe-guard.sh` — the PostToolUse write guard retired
  WITH the compiler it recompiled for; its hook registration is removed from
  `.claude/settings.json` (a hook that crashes is a gate that is off). Its
  `preflight --json` wire-contract lesson lives on in
  `test_preflight_contract.py`.
- `design-system/_archive/` — the twelve `scla-*.html` templates and the demo
  reel; `design-system/docs/_archive/design-contract.md` — the template
  authoring menu. `design-system/` itself survives as a brand token & asset
  store: `config/tokens.yml`, the vendored Proxima set + `metrics.json`, the
  brand SVGs, and the `hyperframes` version pin in `package.json`.
- `render-qa/docs/_archive/` — the adoption proposal, the 2026-07-30 verdict
  handoff and the 2026-08-04 build plan (decision made, documents superseded);
  `script-templates/_archive/` + `docs/_archive/` — avatar-lane and
  Notion-intake residue.

**`preflight.py` collapsed to one lane:** the `freeform` detection boolean and
every fork are gone; the freeform branch is the code path. `check_freeform_*`
functions dropped the prefix. The `inscene_gaps` rule was NOT deleted — it is
lane-neutral (the owner read a >0.8s mid-scene hole as "a major glitch"); its
flat-words adapter for per-beat clip audio stays deferred, so it WARNs
visibly (`no-word-timings`) instead of grading. `tokens.py` lost
`card_gutter()` (orphaned) and made `footer_reserve()` private (it survives
only to derive `content_bottom()`, which `check_ink`/`check_fit` read).

**Three owner rules are now honest Conventions, not gates** — retiring
`check_variety` orphaned "max 2 consecutive scenes on one visual family",
"≥6 distinct content forms" and "no one form above 40%". They are labelled
`*(Convention — mechanism retired…)*` in `.claude/rules/video-production.md`,
NOT silently dropped and NOT ported: the owner decision on what visual variety
means for freeform (where `carrier-drift` actively rewards one persisting
carrying object) is **pending** — see the open items below.

**Still open, deliberately not closed here** (carried from the entry below):
1. **The variety contract is unowned** — the three Conventions above have no
   checker; the trial used essentially one content form for 17 beats.
2. **The fabrication ban is structurally blind on-frame** — the beat-manifest
   diff never reads markup; the trial's "Course Introduction" eyebrow proves
   the hole.
3. **The two ending gates disagree** — `check_boundaries` measures the final
   hold from the wav, the timing gate from the timeline; only a wav pad PLUS a
   video hold clears both, and the trial ships 3.6s of silence where
   `FINAL_HOLD` is 1.8s.
4. ~~13 stalled template-lane workspaces are ungradeable~~ — closed 2026-08-05:
   the 12 dead template workspaces were deleted (their `ready/` scripts are
   untouched and lane-neutral; rebuilds are freeform from the script), and the
   one freeform build among them resumes.

## 2026-08-05 — The freeform lane is approved, and a symbol the voice cannot say

**Decision:** the owner reviewed the 2026-08-04 freeform (agent-native,
template-free) trial of `m1_mini-syllabus` — 17 beats, 106.63s, one career-track
rail carried end to end — and called it "fantastic", confirming **the freeform
lane is the direction for SCLA lesson video**, with one defect: the voice read
`#questionsupport` as "pound sign questionsupport".

Two mechanisms, both armed:

1. `check_copy.py` rule `unspoken-symbol` — a symbol the voice reads as its own
   name is a defect in NARRATION (both lanes, plus script mode at
   `/refine-scripts`, where the fix costs a text edit instead of a
   re-synthesis). On-frame copy keeps `#questionsupport`: that is the channel's
   real written name and reads correctly on a slide. The three approved scripts
   carrying it — `m1_mini-syllabus`, `m0_welcome-to-mid-career-momentum`,
   `mini-syllabus_early-career-boost` — now read "hashtag questionsupport".
2. `preflight.py` `STAGE_DIRS` + `program_of()` — one reader for the program
   slug, replacing two hand-written folder lists that both missed the
   2026-08-04 `inbox/ready/published` rename. Every script in a `ready/` folder
   resolved to the program `ready`, so `title_card` failed on **every current
   build, template and freeform alike**. Found on the trial; the pin grades the
   live library, so the next rename turns a test red instead of a gate into
   noise.

**Why the fix is in the script, not at synthesis:** rewriting the text on its
way to HeyGen hands back word timings ("hashtag", "questionsupport") that no
longer match the script tokens `check_freeform_script_match` and the cue anchors
diff against — trading a mispronunciation for a gate failure. The script is the
narration source of truth, so the spoken form belongs in the script.

**Deliberately one symbol.** A sweep of all 36 refined scripts found `%` ("by
30%") and `&` in live copy; the voice speaks both correctly, and grading them
would cost false positives and retire the rule.

**Still open, and NOT cleared by this approval** — each surfaced by the trial:
- The **variety contract is unowned on the freeform lane.** `check_variety` is
  skipped entirely; `check_forms` rehomes only `one-item-list`/`one-card`. So
  "≥6 distinct content forms", "max 2 consecutive on one family" and "no form
  above 40%" grade nothing. The trial used essentially ONE content form for all
  17 beats — a build the template lane would fail instantly — and `carrier-drift`
  actively rewards that, because a frame that barely changes shape scores well
  on churn. An owner decision is owed before freeform goes near a batch.
- The **fabrication ban is structurally blind on-frame** in freeform.
  `check_freeform_script_match` diffs the beat manifest against the script and
  never looks at on-frame markup. The trial's own "Course Introduction" (an
  eyebrow the script never says) proves the hole is live; both instances were
  benign, but an invented statistic or policy line would sail through.
- The **one-item-list rule is defeated by progressive reveals.** `check_forms`
  reads markup structure, so declared 2/3/4-item lists pass — while at 3 of 17
  beat midpoints the frame renders exactly one bullet, the defect the rule
  describes, visible in the stills the gate itself requires.
- The **two ending gates measure the final hold from different places and both
  are armed**: `check_boundaries` `audio-tail-clipped` wants ≥1.5s of wav after
  the last word; `preflight.check_freeform_timing` wants ≥1.5s of timeline after
  the last clip file ends. Padding the wav moves `audio_dur` with it, so only a
  wav pad PLUS a separate video hold clears both — the trial ships 3.6s of
  silence where `FINAL_HOLD` is 1.8s.

## 2026-08-04 — `member-support/` and `partnerships/` deleted

**Decision:** Deleted both folders outright (owner instruction, not archived —
repo-hygiene default). Removed their two routing rows from root `CLAUDE.md`
("Member-facing answer" → `member-support/faqs.md`, "Partner org" →
`partnerships/NIC.md`), the `member-support/faqs.md` critical-file check and
the `member-support partnerships` directory args in `scripts/lint-refs.sh`
(checks 5 and 7), the dangling `../member-support/kb-integration-plan.md` row
in `projects/README.md`, and the `member-support/` bullet in
`projects/grants/README.md`. Historical mentions in this log, `audits/`,
`refinement-log.md`, and `render-qa/logs/snag-log.md` are left as record —
history is not rewritten.

**Why:** owner-directed deletion; no successor location was given for FAQ /
partner-org content.

## 2026-08-04 — Owner verdict: gate set approved the rejected cut, quarantined the approved one

**Decision:** the freeform pipeline gains a Pace rule (`render-qa/src/check_pace.py`,
BLOCKING) — median beat ≤7.0s, ≥8.0 beats/minute, ≤60% of runtime in beats over
8.0s, and a carrying-object churn band (`carrier-drift`) — and `check_diversity`'s
per-pair `twin-beats` defect is retired in favor of `twin-share`, an anti-gaming
backstop for `beat-pace` with a 25% ceiling that deliberately does not
discriminate between the two cuts below.

**Why:** the owner reviewed two freeform cuts of the same lesson on 2026-08-04.
`build-direction-before-you-build-a-plan_early-career-boost` (built 2026-07-30/31,
26 beats, 10.26 beats/min, median 5.15s) was **approved to ship** — and was
QUARANTINED by `verify_render`'s presence check on three static spans (5.0s,
5.5s, 5.5s) the owner had already watched and approved. A second cut of the same
lesson (17 beats, 6.47 beats/min, median 9.12s) passed every gate in `src/`
clean and was called **"SO boring."** The gate set had it backwards in both
directions at once.

A prediction was made and refuted: the expectation was that the boring cut
would fail `check_presence` harder. It does not — its longest static span is
3.75s, under the (then) 5.0s floor, and it changes something every ~2.5s,
scoring as the *more* animated build by every metric the pipeline owned. The
refutation is what found the real discriminators: the rejected cut delivers
one idea every 9.3s and nothing on screen accumulates, while the approved
cut's low inter-beat churn (3.34%, two twin pairs) is the *signature* of a
persisting carrying object — one field of 48 marks, built once and thereafter
only re-grouped. The gate set measured animacy; the owner was responding to
idea rate and whether the frame accumulates.

**Two follow-on changes, same session:** `STAGNANT_FAIL` moves 5.0 → 6.0 (the
quarantine floor sat below a span the owner had already approved; it does not
rescue the rejected cut, whose worst span is already under the old floor) and
the existing MP4 ships unmodified — **live at the Wistia URL recorded in
`published.tsv`** against `build-direction-before-you-build-a-plan_early-career-boost`.

**Stated limit:** the pace thresholds are calibrated on n=2 — one lesson, two
cuts. Enough to fix a direction, not enough to claim a general law. A future
lesson that genuinely wants a slower shape is an owner decision that pins a
second reference build here, never a loosened constant or a CLI flag.

**Where the two reference cuts are (added 2026-08-04).** The APPROVED cut is
live at the Wistia URL recorded against
`build-direction-before-you-build-a-plan_early-career-boost` in `published.tsv`.
The REJECTED cut is filed at
`renders-hyperframes/_reference/build-direction-before-you-build-a-plan_early-career-boost_2026-08-04-freeform-backup`
— moved there from the workspace root, where it had been reporting as an ORPHAN
because it matches no script. Underscore folders are skipped by every workspace
scan, so filing it is what makes it stop looking like unfinished work.

**Say the honest thing about that evidence: `renders-hyperframes/` is
gitignored, so the rejected cut exists only on the machine that built it.** It
is not recoverable from this repository. The durable record of the calibration
is the numbers written above — 17 beats, 6.47 beats/min, median 9.12s, longest
static span 3.75s, against the approved cut's 26 beats, 10.26 beats/min, median
5.15s — plus the fixtures in `render-qa/tests/test_pace.py`. If the folder is
lost, the thresholds still stand on those; what is lost is the ability to re-run
a new gate against a build whose verdict is already known.

## 2026-08-04 — The write fence

**Decision:** a `PreToolUse` hook (`scripts/write-fence.sh`) hard-blocks writes
to the shared pipeline machinery — `design-system/` (templates, `tokens.yml`,
contracts), `renders-hyperframes/_run/` (the scaffold), `render-qa/src/` (the
gates), `scripts/`, `.claude/` — unless the session exports
`SCLA_SYSTEM_SESSION=1`. A workspace's own files stay fully writable. Default is
DENY, and the flag marks template/gate work as a deliberate, separate session
type; a build subagent never sets it and cannot set it for itself, because the
value is read from the agent process's environment and a Bash tool call cannot
reach back into that.

**Why:** `.claude/settings.json` granted Write and Edit with no path
restriction, and the only hook (`hyperframe-guard.sh`) exits 0 for anything
outside a workspace's `scenes.json`/`index.html`. When a pacing agent decided to
"improve" the shared `scla-stat` template and 14 workspace copies of it, nothing
slowed it down. "You author `scenes.json` only" was a sentence, not a mechanism
— the failure class this log already quantifies as 14 defects from rules that
existed but did not fire, and 0 from rules anyone forgot. The agent-native
experiment then showed the existing guard is LOCATION-shaped and can be routed
around (`PROVENANCE.md` §2), so the fence is PATH-shaped instead.

**The hook matches Bash as well as Write/Edit,** because a shell redirect or a
`cp` is the obvious way around a Write-only fence. Reading and *running* fenced
files stays free — `python3 render-qa/src/check_copy.py` and
`bash scripts/lint-refs.sh` are the pipeline working normally, and a fence that
blocked those would be switched off within a day. Direction matters for the
copy family: copying OUT of a fenced path is a read (`batch-prepare.sh` does
exactly that on every prepare), while copying IN is a write. `mv` out is still
blocked — it removes the original.

**Two failure modes, both graded.** `render-qa/tests/test_write_fence.py`
invokes the real script with crafted payloads and asserts it is neither too
loose (the machinery stays writable) nor too tight (ordinary build work is
blocked). An unparseable payload is REFUSED rather than waved through: a guard
that cannot see the call it is grading is not a guard. Verified live in the
session that installed it — `touch scripts/__fence_probe` was blocked, a
workspace write succeeded.

**What a builder does instead:** a template, token, gate or script that is
genuinely wrong is a real finding, and gets REPORTED rather than patched from a
build session. The block message says so.

**Amended the same day — the discriminator changes, the fence stays.** The
`SCLA_SYSTEM_SESSION` gate above was wrong, and the fence is now armed by a
sentinel file instead: `renders-hyperframes/.build-in-progress`, written by
`scripts/build-session.sh arm` (called from `scripts/build-claim.sh`) and
removed at close-out by `scripts/build-release.sh`. No sentinel, no fence — an
owner session is completely unrestricted.

The reason is a fact about the harness, not a change of mind about the risk. A
whole-session env flag cannot separate the owner from a subagent, **because they
share one process**: the subagents a build dispatches inherit the environment of
the session that dispatched them, so one value has to answer for both. It
answered for the wrong one. Within a day of install the fence had refused the
owner's own edits to `scripts/` and `.claude/`, including the patch that would
have fixed it, and the owner disabled it by deleting the hook's `command` key —
the "too tight" failure mode `test_write_fence.py` was written to catch, landing
on the axis the test did not grade. Defaulting to DENY was the error: it made
every unflagged session a build session, and most sessions are not.

The sentinel discriminates on *what is happening* rather than on *what someone
remembered to declare*, which is the same reason the rest of this pipeline reads
state from the folders. Three properties make it safe to trust: the sentinel
path is itself fenced, so an armed builder cannot `rm` its way out; it expires
after `VIDEO_BUILD_SESSION_TTL` (default 6h), so a run that dies without
releasing does not leave the repo read-only until someone notices; and arming
appends rather than truncates, so overlapping builds (up to 3-wide) each hold it
and the last one out lowers it. `SCLA_SYSTEM_SESSION=1` survives as an explicit
override. The block message no longer names it — a build subagent that reads
about an escape hatch will try the escape hatch.

`test_write_fence.py` was retargeted to grade the gate itself: every block is
asserted twice, once armed and once disarmed, and it now runs against a
throwaway project dir so a test run can never leave the live repo fenced.

## 2026-07-31 (rules refactor) — The video rules file splits by audience

**Decision:** `.claude/rules/video-production.md` is auto-loaded on every session
that touches `projects/video-production/**`. It had grown to 41 bullets and
~8,300 tokens, of which the normative claims were ~640 (8%); the rest was
incident narrative (~56%) and mechanism citations (~35%). The narrative moves
here. The rule file keeps the claim and the mechanism, and cites its history as
`Why: log <date> "<title>"` — a grep target rather than a heading anchor, so the
citation survives the log being re-titled or re-ordered.

**Why:** the file's job is to state constraints a session must not violate; a
postmortem is a different document for a different reader, and paying 8k tokens
for the postmortem before any work starts is a tax on every build. Much of the
narrative was already duplicated here — `2026-07-29 "A gate must be able to
fail"`, `"The gates the better-decisions rejection exposed"`, `"Working
artifacts lose their date suffix"` and `2026-07-28 "Owner review"` each carry in
full what a rule bullet was re-telling in miniature.

**Two things went in rather than out.** The histories that existed *only* in the
rule file are now real log entries — the 2026-07-29 owner review below, and the
freeform measurement gates above — because deleting them would have destroyed
the provenance that makes those rules defensible when a future session wants to
"simplify" a gate. And three rules were stale against the branch that changed
them: the `static-span` rule did not mention `TIME_EPS`, the tolerance without
which it demotes a real 5.0s freeze to a warning; no rule mentioned
`PIPELINE-STATUS.md`; and the word-timing rule had traded the literal
`timing.json` for the prose "its workspace timing manifest", losing the grep
target (`hfp_common.py` names that file in three places). A citation that cannot
be checked is the failure mode this file exists to prevent. A fourth, older
staleness was fixed in passing: the close-out rule pointed at
`render-qa/snag-log.md`, which moved to `render-qa/logs/snag-log.md`.

**Rules:** `.claude/rules/video-production.md`.

## 2026-07-31 (status doc) — The queue read becomes a document, not only a command

**Decision:** `scripts/batch-status.sh --write` regenerates
`projects/video-production/PIPELINE-STATUS.md` — the same read the terminal
command performs, rendered as a document a human can open without running
anything. `batch-ship.sh` calls it on every quarantine and every publish;
`/refine-scripts` regenerates and stages it alongside the ledger row. It is a
build artifact of the ledger plus the folder state, never hand-edited.

**Why:** the resume key was correct and invisible. `batch-status.sh` reads
everything it needs from disk alone, which is what makes a fresh session
resumable and mid-run context compaction a non-event — but it answers only to
someone at a terminal who already knows the command exists. Regenerating at the
two moments state actually changes costs one call and makes "what's left, what's
stuck, what's published where" answerable by opening a file.

**Rules:** `.claude/rules/video-production.md`.

## 2026-07-31 (freeform gates) — A measurement is never delegated to the human preview

**Decision:** the 2026-07-30 freeform lane skipped `check_pacing` and
`check_variety` and named one compensating control for both — "owned by the
per-video human preview". That deferral is now split, because the two questions
are not the same kind:

- *Is this video monotonous?* is a taste judgement, and it stays with the human.
  `check_diversity`'s `twin-beats` rule names consecutive beats drawing
  near-identical pictures (it finds two on the 2026-07-31 cut, including the pair
  straddling a scene cut) and `verify_render.py`'s `monotony` section prints
  them. It never fails a ship: the twin threshold is not calibrated against the
  owner's reference video the way `check_variety`'s are, and a gate that blocks
  on an unpinned taste number is one that gets switched off. Per STD-38 it
  teaches first; pin it against a reference build before arming it.
- *Did the picture hold perfectly still for 5 seconds?* is a stopwatch reading,
  and no eye performs it reliably — least of all with narration playing over the
  stillness to fill it. It moves to `check_diversity`'s `static-span` rule, run
  by `scripts/batch-precheck.sh` over a uniform ~1.25s snapshot grid. Pre-render,
  so the fix costs a re-author instead of a 19-minute render. Same rule and same
  constants as `check_presence`, which stays authoritative post-render.

**Why:** on 2026-07-31 the owner watched
`build-direction-before-you-build-a-plan`, approved it, and `check_presence` then
failed it post-render on three spans of 5.0–5.5s of pixel-identical video under
continuous speech, two running straight through a scene cut. The approval was not
the defect; the assignment was. A deferral must state which instrument answers
the question, and "the human" is only a legal answer for questions a human can
actually answer.

**Three supporting mechanisms:**

1. **The grid grades itself.** `grid-too-sparse` fails a run whose stills are too
   far apart to see a `STAGNANT_FAIL` freeze, because a sampler that cannot
   answer must say so rather than return clean. Thresholds calibrated against
   that cut's 78 real stills — a frozen pair reads 0.00000 churn and max cell
   delta 2, the nearest genuine reveal reads 0.00852 and 80 — and pinned by
   `test_diversity.py`.
2. **Timestamp precision is spent once, not per rule.** Frame times are read back
   out of filenames at 1/100s, so every time comparison in `check_diversity`
   carries that slop, and both directions bit during calibration: a perfect 1.25s
   grid measured 1.26s wide (33.125 and 34.375 round to 33.12 and 34.38) and
   fired `grid-too-sparse`, then the real 5.0s freeze at 74.0s measured 3.74s
   against a 3.75s threshold (78.125 and 74.375 round to 78.12 and 74.38) and was
   demoted to a warning by one hundredth of a second. `TIME_EPS = 0.02` is
   declared once beside the thresholds, and `scripts/batch-precheck.sh` rounds
   its emitted grid to the same precision so the sampler and the gate agree.
3. **Narration word timings get one loader.** `check_presence` knew only the two
   flat word files, so on a freeform build (per-beat wavs + `audio_meta.json`) it
   found none, and its `not words` fallback graded every static run as if
   narration ran wall to wall — stricter than designed, silently, and it would
   eventually have failed the deliberate 1.8s `FINAL_HOLD` every lesson ends on.
   `hfp_common.load_words()` now reads all three shapes, offsetting each clip's
   words by its `timing.json` `audio_start`; `check_presence` and
   `check_diversity` both call it; an absent transcript emits a `no-word-timings`
   warning naming the lost coverage instead of passing for rigour. Pinned by
   `test_diversity.py`, which asserts a frozen span over silence does NOT fire
   and the same span over speech does.

**Rules:** `.claude/rules/video-production.md`.

## 2026-07-31 (later) — A build workspace carries no agent instructions of its own

**Decision:** `hyperframes init` writes an `AGENTS.md` and a `CLAUDE.md` into
every scaffolded project, and `scripts/batch-prepare.sh` copies the scaffold
into all 16 build workspaces — so both files existed, byte-identical, in every
one. `batch-prepare.sh` had been overwriting `CLAUDE.md` with a one-line pointer
since the day the scaffold was built, with the reason stated inline ("init
writes a CLAUDE.md routing to skills this repo deleted"), and had never touched
`AGENTS.md` at all. Both are now deleted from the scaffold instead of corrected,
and removed from the 16 workspaces already on disk. A workspace holds
compositions, assets, tokens, the design contract and the plan — no prose telling
an agent how to work.

**Why:** `AGENTS.md` carried exactly the defect `CLAUDE.md` had been replaced
for, in the one directory a build subagent actually works in. Its 96 lines
routed to `/product-launch-video` and `/faceless-explainer` — generic workflows
`/produce-video` forbids by name for SCLA lessons — and named `npm run check` as
the gate when the gate is `render-qa/src/preflight.py`. Sixteen copies of
instructions that contradict the pipeline is a live hazard, not clutter, and it
is the repo's oldest recurring failure: prose losing an argument with other
prose. Correcting it would have created a second authoritative brief to keep in
sync with the SKILL; deleting it leaves one. This follows the ripple-motion
(2026-07-29) and row-icon (2026-07-29) precedent — remove the capability rather
than police it.

**Why nothing breaks:** no gate, hook, test or script ever read a
workspace-level copy of either file — the only `AGENTS.md` any code names is
`design-system/AGENTS.md`, a different file. The one real loss was a breadcrumb:
an auto-loaded `CLAUDE.md` was the sole in-tree link from a workspace back to
`_run/BUILD-KIT.md`. The primary path never used it (the AUTO-BATCH orchestrator
hands the cold build subagent that path directly in its prompt), and the
secondary path is covered by a new routing row in
`projects/video-production/CLAUDE.md` — a parent directory, so it auto-loads
anyway, and unlike the deleted files it is tracked in git and linted. The
builder-facing warning moved to the SKILL's BUILD-KIT block (the kit is
regenerated from those markers on every `batch-prepare.sh` run, so editing
`BUILD-KIT.md` directly would have been overwritten): a workspace agent file
found in future is an init artifact to delete, not to follow.

## 2026-07-31 — The Wistia poster frame goes back to Wistia's default

**Decision:** Owner call — *"I no longer need Claude to select thumbnails for
Wistia for the MP4s."* The first-frame poster step added 2026-07-29 (entry
below) is deleted from `wistia-upload.sh`: no ffmpeg extract, no Image-media
upload, no `new_still_media_id` PUT. The script uploads the MP4 and reports
the URL, and Wistia picks the poster frame as it did before 2026-07-29.
Already-published videos keep whatever still they have — this changes new
uploads only, and any poster is still settable by hand in the Wistia UI.

**Why it's a clean removal:** the step was best-effort and terminal — it ran
after the video was live, printed `THUMBNAIL_WARN` on every failure path, and
returned 0. Nothing parsed its output and no gate depended on it, so deleting
it changes no exit code and no publish path. It also retires the STD-35
exception the 2026-07-29 entry carved out: with the step gone, there is no
longer a deliberately-unenforced rule in the publish tail to justify.

## 2026-07-30 — Freeform (agent-native) builds become a second lane, opt-in, same contract

**Decision:** Owner call, after the verified module verdict
(`render-qa/docs/HANDOFF-agent-native-verdict-2026-07-30.md`) and a side-by-side
frame review of the same lesson built both ways. Four parts:

1. **A freeform build is a normal lesson build.** It takes a stem, claims
   `renders-hyperframes/<base>` via `mkdir` (the build lock), and its script moves
   raw → `refined/` → `rendered/` exactly like the template path. The stem contract
   has nothing to do with templates. (Resolves the handoff's open owner call #1.)
2. **Freeform is opt-in (`--freeform`) with a human preview per video.** It never
   becomes the AUTO-BATCH default while its quality floor is unproven — the
   template lane keeps shipping untouched. (Resolves open owner call #2.)
3. **The DOM-rect probe is dropped, not deferred.** It is blocked on unexported
   framework bundling and produced 1760 false findings from an unstyled page; the
   per-beat layout inspector plus the ink-bands pixel gate cover the same rules
   from real pixels. `check_diversity` (perceptual hash) is deferred — the
   per-video human preview covers monotony while freeform is opt-in.
4. **Nothing is retired yet.** The six template-shaped modules stay until the
   freeform lane has shipped real lessons (handoff §4: archiving today reds CI
   and disarms the lane that ships). Deletion, not `_archive/`, when it lands.

**Why:** the owner's stated end goal is visually interesting videos; the
agent-native reference build is the more designed cut of the same lesson. The
five real invariants — script fidelity, brand colors, brand fonts, stem naming,
folder-state — get mechanized on the freeform lane (beat-source adapter re-arms
the copy gates; a new brand gate closes the one gap templates had been covering
by construction). Everything template-mechanical stays on the template lane only.

## 2026-07-29 (owner review) — Eight defects from the career-map and visibility-actions cuts

**Decision:** a round of owner review across two cuts produced eight fixes. Two
of them delete a capability rather than police it, following the ripple-motion
precedent from the same day.

1. **No icons beside bullet rows or cards — only ONE hero illustration per
   frame.** The plural `icons` slot drew a ~64px glyph at the right edge of every
   `scla-points` row and in every `scla-morph` card corner, and it shipped three
   ways wrong: positionally, so a short list left holes (`icons=",insight,"` put
   one icon beside point 2 of three); duplicated, drawing `mentorship` and
   `mentorship2` — two near-identical person glyphs — in one frame; and competing
   with the row copy in a family whose whole job is a list of words. Owner: *"add
   a rule that icons should not render to the right of bullet points… no future
   renders should include the icons within this style of illustration."* The slot
   is gone from both templates, and `check_slots.py` rule `banned-row-icons`
   fails any scene still authoring it — including a stale workspace, whose
   variable the compiler would otherwise drop in silence. The singular hero
   `icon` on statement/chips/steps/condition is untouched. The two fixtures that
   had pinned `icons="compass,target"` as PASSING were inverted in the same pass.
2. **A one-card comparison is the one-item list in the form the list rules could
   not see.** `scla-morph` is a two-option comparison whose options are two
   SCALAR slots, so the `one-item-list` rule was structurally blind to it: the
   visibility-actions cut filled `aTitle`, left `bTitle` blank, and rendered a
   single card with its `notes` caption stranded in the right-hand column beside
   nothing. Owner: *"having just a single card breaks the rule… having the text
   off to the side outside the card also is just awkward and should never
   happen."* `check_variety.py` rule `one-card`, which also fails a `winner`
   naming a card that was never filled — the morph resolving, gold check glyph
   and all, onto something that does not exist. `test_variety.py` also gave rule
   1 `one-item-list` the firing proof it had never had.
3. **Even spacing is a property of the SLOTS, not of the copy in them.** A card
   grows when its copy wraps, so cards top-anchored on slots sized for the copy
   in front of you come out unevenly spaced the moment one of them takes a second
   line: the career-map cut left 74px between the first pair and 26px between the
   second, and the owner read the 26 as touching. Every gate passed, because the
   *ink* inside those cards was nowhere near colliding — it was the borders that
   met. Size the slots for the widest legal card the schema permits, and let a
   short card sit high in its slot. `check_geometry.py` rule `card-gutter`
   against `tokens.yml` `spacing.card-gutter`, graded on LAYOUT boxes — the one
   rule in that gate that is, because a border and a fill are what a viewer sees
   touching. Deliberately narrow to stay believable: absolutely positioned +
   fully bordered + text-bearing + horizontally overlapping, which is what keeps
   chip rows, hairline-separated list rows and the decorative concentric ghost
   rings out of it.
4. **The on-frame scene badge is the frame's real position.** `sceneIndex` is how
   the owner names a frame when reviewing a cut, and m4_visibility-actions
   numbered 13 scenes 1..11 (two 07s, two 09s), so a whole round of
   frame-numbered feedback could not be resolved against the plan.
   `check_slots.py` rule `scene-index-badge`.
5. **The geometry gate can see every box on the frame.** Chips, condition chips,
   statement lines and morph notes are all created at RUN TIME with no geometry
   prototype, so `check_geometry` graded ZERO of them — it returned PASS on the
   frame whose four chips ran through the footer band, and on the frame whose
   last chip crossed the padding border, both of which the owner reported by eye.
   `boxmodel.py` gained `data-geometry-repeat` prototypes (declared in the
   templates, structured ones carrying `data-geometry-text`), `flex-wrap` row
   packing, border-box measurement of padded pills, and `data-geometry-alt-if`
   for geometry a template applies conditionally in JS — `scla-chips` narrows its
   field to `right: 620px` when a hero icon is set, and the script now reads that
   number back out of the attribute so the declaration cannot drift. Both
   owner-reported overflows now fail from the plan alone, with no browser and no
   render.
6. **`line-height: normal` is measured in the real vendored font, never
   assumed.** `boxmodel.py` assumed 1.2; Proxima Nova resolves to **1.404 / 1.447
   / 1.477** by weight (Chrome reads hhea ascent/descent/lineGap — OS/2
   USE_TYPO_METRICS is off on this kit). Every block that does not set
   `line-height` was therefore ~20% shorter in the model than on the frame, which
   is how four wrapped chip rows modelled as ending 43px clear of a footer they
   in fact ran through. The number is generated into
   `design-system/assets/fonts/metrics.json` beside the advance widths and read
   by `textmetrics.normal_line_height()`. The regen recipe in `textmetrics.py`
   was also fixed: it grepped `/^REGEN/` against a line beginning `# REGEN`, so
   it matched nothing, ran an empty program, and reported success.
7. **A body statement belongs under the heading, not at the foot of the frame.**
   `scla-statement`'s only body slot rendered BULLETS, so a builder either
   bulleted a single sentence (which `one-item-list` rightly rejects) or pushed
   the thought into a sub-beat, which paints at the bottom. The owner reported
   both shapes in one review: *"do not render as bullet points, it really is a
   single statement… render the heading statement and then maybe a secondary body
   statement"*, and *"the body statement that populates at the bottom should
   really live up below the statement heading"*. `scla-statement` and
   `scla-condition` gained a `sub` slot; `scla-chips` and `scla-points` sub-beats
   moved from the bottom band to directly under the heading. Which slot an author
   picks stays a convention; the geometry gate enforces that whatever they pick
   fits.
8. **A lesson's part number is a filing convention, never on-screen copy.**
   `...-resume-pt1` / `...-tool-pt2` tell two halves of one lesson apart on disk;
   the builder turned both stems into title cards reading "…Pt1"/"…Pt2". Owner:
   *"that is simply a reference for our purposes and should not actually go into
   the content created."* `check_copy.py` rule `part-reference`, graded on
   narration AND every on-frame string, in workspace and script mode; and
   `preflight.py`'s `title_card` check strips the same suffix from the expected
   stem title, because two gates that disagree make the fix impossible — removing
   "Pt2" to satisfy one failed the other. Deliberately narrow: `four-part lens`
   is authored copy that appears 8 times in one program, and a rule that flagged
   it would be off within a week.

**Also this day, unprompted by the review:** one render at a time, machine-wide,
with builds up to 3-wide. Authoring and TTS are network-bound and overlap
cleanly; a render is CPU-bound and two on a 4-core box thrash. `batch-ship.sh`
takes `renders-hyperframes/.render.lock` via `mkdir` for the whole render phase
and exits 2 if another holds it — the same shape the publish phase has always
used. Added when a session was found running 4 concurrent builds against a render
phase that had no lock at all, and only a sentence in the SKILL asking it not to.

**Rules:** `.claude/rules/video-production.md`. **Trail:**
`projects/video-production/render-qa/logs/snag-log.md`.

## 2026-07-29 (later) — Delivered MP4s are kept, and the Wistia poster is the first frame

**Decision:** Owner call, two changes to the publish tail:

1. **Publish no longer deletes the local MP4.** `batch-ship.sh` filed the
   delivered cut to `renders-mp4/<program>/hyperframes/` and then `rm -f`'d it,
   on the 2026-07-28 reasoning that "Wistia is the delivery copy." That line is
   now gone: the filed MP4 stays. The folder is gitignored, so nothing enters
   git history, and `renders-mp4/README.md` had said *"Files can stay here
   after upload — a free local backup of the delivered cut"* the whole time —
   the deletion was the side that was out of step. It also makes
   `archive-lesson.sh`'s "deliverable must be filed before the workspace is
   pruned" check permanently true instead of true-for-one-second.

2. **The Wistia thumbnail is the video's own first frame.** Wistia otherwise
   picks a poster frame from somewhere in the middle of the video, which for a
   lesson lands on an arbitrary mid-animation state. Wistia has no "use frame
   0" flag, so `wistia-upload.sh` does the documented three-step version:
   `ffmpeg -frames:v 1` → upload the JPEG as an Image media → `PUT
   new_still_media_id` on the video, waiting for the image to reach `ready`
   first (a PUT against an unprocessed still is silently ignored).

**Why the thumbnail step is best-effort, not a gate:** it runs *after* the
video is live. Failing hard there would make `batch-ship.sh` quarantine a
published video and — because the URL is grepped out of the upload output —
lose its URL in the process. So every failure path prints `THUMBNAIL_WARN` and
returns 0. That is a deliberate exception to STD-35, not an unarmed rule: the
poster frame is cosmetic and recoverable by hand; a live-but-unrecorded video
is not.

## 2026-07-29 — Working artifacts lose their date suffix; the name becomes the lock

**Decision:** Owner call while planning a throughput rebuild: *"let's drop the
renaming convention."* A lesson's working artifacts — raw script, `refined/`
script, build workspace, `rendered/` script — are now named `<title>_<program>`
with **no date**. Only the delivered MP4 keeps one, the render date, frozen at
publish. This replaces the one-date restamp rule added 2026-07-28, eight days
into its life.

**Why the old rule had to go.** It made the name a mutable state stamp,
restamped at every transition. But the pipeline's only defence against two
concurrent build agents landing on the same lesson was a name-based check —
"does `renders-hyperframes/<stem>/` already exist?" — and a name that moves
cannot answer that question. It had already failed in production: on the morning
of 2026-07-29 the same lesson held two complete build workspaces,
`better-decisions-come-from-better-criteria_early-career-boost_2026-07-28` and
`..._2026-07-29`, each with its own rendered MP4 and `qa/VERIFIED` marker,
because a rebuild restamped its way into a second directory instead of reusing
the first. Both are preserved (the older as `...superseded-2026-07-28`); which
cut ships is the owner's call.

With the date gone, the directory entry **is** the identity, so `mkdir <base>`
is an atomic build lock — the mechanism STD-35 asks for, in place of a sentence
asking orchestrators to check first. The information is not lost: "when was this
last acted on" is mtime, which the filesystem maintains and which cannot drift.
A date suffix maintained by code was denormalized mtime.

**The 2026-07-28 complaint is better served, not abandoned.** That rule came
from the owner reviewing a video still named for its 2026-07-06 refine date with
the renderer's `_<date>_<clock>` stacked on top. Removing dates from working
artifacts answers that more completely than restamping did: there is no date
left to go stale, and the one date that survives describes an event that really
did happen once.

**Migration was not a flag day.** `stem.py base()` strips any trailing date and
clock segments, so a legacy name still resolves to the right identity wherever
one survives — in `refinement-log.md` rows, in an un-migrated workspace, in the
renderer's own output. 55 artifacts were renamed in one pass (40 tracked via
`git mv`, 15 gitignored workspaces via `mv`).

**Mechanisms.** `render-qa/src/stem.py` is still the sole owner: `base` is the
tolerant reader, `delivered` is the one remaining naming transition (the filed
MP4), and `restamp`/`normalize` now exit 2 pointing here rather than silently
producing a dated working name. `preflight.py` check 12 inverted — it fails a
workspace whose name carries a date, with the `mv` to fix it. `batch-ship.sh`
files the MP4 via `stem.py delivered` and moves the script to `rendered/` under
its base. `render-qa/tests/test_stem.py` pins both halves: the tolerance that
made migration safe, and the strictness that stops a dated name coming back.

**Shipped in the same pass: renders are serialised by a lock.** `batch-ship.sh`
now takes `renders-hyperframes/.render.lock` (`mkdir`, released on exit) for its
whole render phase and exits 2 if another render holds it — the same shape the
publish phase has always used. Builds are explicitly allowed to run **3-wide**;
they are network- and authoring-bound and overlap cleanly, while a render is
CPU-bound and two on a 4-core box thrash. Until now "sequentially" was a
sentence in the render-lessons SKILL, and a session was found running four
concurrent builds against a render phase with no lock at all — it had simply not
yet reached a render.

## 2026-07-29 — The banner is the program folder's name; the 2026-07-21 on-screen rebrand is reverted

**Decision:** Owner call, reviewing an Early Career Boost lesson whose title card
read "Career Accelerator": *"a MUST is the banner should ALWAYS correspond to the
project folder name as that is the name of the program … a hard rule that must be
enforced."* `early-career-boost` renders as **"Early Career Boost"**. The
2026-07-21 on-screen rebrand is reverted — it put a program name on a lesson that
does not belong to that program, which is false on screen, not a style choice.

**Why it shipped with a green gate.** `preflight.py` check 7b has compared the
title-card eyebrow to `tokens.yml`'s `programs:` map since 2026-07-28, and the map
said Career Accelerator. Grading a value against an unvalidated table is not
enforcement; it relocates the place where a wrong value is allowed to sit. So the
map is now graded too: a display name is legal only if it slugifies back to its
own key. That admits real orthography ("Mid-Career Momentum" → `mid-career-momentum`)
and admits no alias whatsoever — the rule has no discretionary surface for a
future rebrand to slip through, which is the point of the owner calling it a MUST.

Two mechanisms, deliberately at different altitudes: `tokens.programs_problems()`
inside check 7b (fails a build, at plan stage, in `--static` too), and
`render-qa/tests/test_programs.py` under `lint-refs.sh` check 11 (grades the map
in CI with no build in flight, and additionally fails a `lesson-scripts/` folder
with no banner or a banner with no folder — so adding a program cannot skip it).

**Found on the way in, same class:** `scripts/hyperframe-guard.sh` — the
PostToolUse hook that is supposed to run the plan-stage gates on every
`scenes.json` write — had invoked `render-qa/preflight.py` and
`render-qa/build_index.py` since the 2026-07-28 refactor moved both into
`render-qa/src/`. Every firing printed `can't open file` where a verdict belonged.
It looked alive because it produced output. `test_guard_contract.py` — the suite
whose stated purpose is that this guard cannot go silently clean — could not see
it, because it grades a JSON payload and no interpreter ran to emit one. It now
resolves the guard's own `RQ` and asserts both entry points exist on disk.

## 2026-07-29 — One project shape, and frame.md split into the numbers and the prose

**Decision:** Owner call — every project gets the same layout: `README.md` (human
door), `AGENTS.md` (agent door), `run.sh` (machine door), then `src/`, `config/`,
`docs/`, `logs/`. Nothing loose at a project root. Applied across
`projects/video-production/`: 21 checkers moved to `render-qa/src/`, three loose
docs to `docs/`, `snag-log.md` to `logs/`, `avatar-pipeline` split into
`src/` + `config/` + `docs/`, and `README.md` doors added where a folder holds 4+
items. The convention is stated in root `CLAUDE.md`.

**`frame.md` is retired, and this is the substantive half.** The owner asked what
it was and what it served. The answer: 709 lines doing two incompatible jobs. Its
frontmatter was *executed* — `tokens.py` parses it, `check_text.py` and
`check_geometry.py` grade against it, `batch-prepare.sh` copies it into every
workspace, `preflight.py` hard-fails a workspace whose copy drifted. Its remaining
633 lines were prose, most of it backed by no checker, and it had a documented
history of **outranking the owner**: the pipeline correctly obeyed frame.md's
"sentence case" and violated a standing Title Case instruction (2026-07-28, below),
and this log already called it a graveyard. A human document that is also machine
load-bearing gets edited by humans and silently changes gate verdicts.

Split into `design-system/config/tokens.yml` (the numbers, machine-read) and
`design-system/docs/design-contract.md` (the prose, read by nobody in code). The
program display-name map moved into `tokens.yml` too — `preflight.py` had been
scraping it out of a **markdown table**, which is a checker parsing prose.
`tokens.py` gained `programs()`; `test_tokens_coverage.py` proves it has a real
non-test consumer, so it cannot rot into another orphan the way `frame_padding()`
did.

**What this cost, honestly.** ~50 files of path rewrites through CI, hooks, four
agent files, three skills, twelve compositions and this log. Two live build
workspaces had to be refreshed — `preflight.py`'s `composition_freshness` section
caught them, which is the gate doing exactly its job. The render-qa checkers derive
paths positionally from `__file__`, so nesting them one level deeper broke every
relative lookup with no syntax error; each was retargeted and `render-qa/README.md`
now names that fragility instead of just forbidding the move.

**Deliberately NOT done — `design-system/` keeps its HyperFrames shape.** Owner
call. HyperFrames resolves `index.html`, `compositions/`, `assets/`,
`hyperframes.json` at the project root, and sub-compositions reference each other
by relative path. Forcing our convention would fight the tool for cosmetics. **One
real consequence, written down rather than discovered later:** HyperFrames also
auto-discovers a design spec as `frame.md → design.md → DESIGN.md` at the project
root, and after the split we satisfy none of them — a generic HyperFrames workflow
landing in that folder would find no brand spec and fail *silently*, producing
something plausible and off-brand. Acceptable only because SCLA lesson videos never
route through generic workflows (`/produce-video` → `/refine-scripts` →
`/render-lessons` is the sanctioned path, and those name both files directly). The
divergence and two ways to close it are in `design-system/docs/README.md`. Not
scheduled.

**Verified:** `lint-refs.sh` 11/11 healthy (81 assertions, STD-35 audit 86 backed /
0 broken), `design-system` `npm run check` PASS (0 errors, 37/37 WCAG AA, layout
and motion clean).

## 2026-07-29 — A gate must be able to fail. Three that structurally could not.

**Decision:** After the owner rejected the rebuilt `better-decisions` cut over
overlapping text, awkward scene-02 audio, and body copy "just too small", the
root cause in all three was the same shape — **a rule that existed, was wired,
ran, and was incapable of firing.**

1. **Minimum text size.** The floor was 32px. The smallest body rule in the
   system was also 32px. A floor set at the minimum in use can never fail
   anything; the caption the owner objected to was exactly compliant. Body floor
   → **40px** in `frame.md` (the single loaded source), which moved 12 rules and
   cost one card's copy. `test_gates.py` now asserts no body rule sits *at* the
   floor, so this specific way of being armed-but-inert cannot recur.
2. **Text-on-text overlap.** Three gates passed a collision visible in the
   owner's screenshot. `check_layout.py` ran the real browser inspector at 60
   points and found nothing — `hyperframes inspect` grades text against its own
   container, and sibling-vs-sibling collision is not a case it models.
   `check_capacity.py` never looked, because it *inferred* slot bindings from a
   JS pattern that `scla-loop` does not use. Rather than wait on upstream,
   `boxmodel.py` resolves every string to a frame box from the template CSS +
   committed font metrics, and `check_geometry.py` grades collisions and bounds
   with no browser — so it runs at plan stage. Templates now **declare**
   bindings (`data-slot`, `data-present-if`) and carry geometry prototypes for
   run-time-created lines, because a gate cannot grade a box only the browser
   knows about.
3. **The conjunction rule's own blast radius.** The rule the owner has given
   more than any other was satisfied by bolting "Or" onto a standalone fragment
   — which is what produced the audio they then rejected. The fix is joining the
   list into one sentence; a new rule says so, exempting question lists (which
   are *meant* to rise) and mid-paragraph topic labels. The existing test that
   had pinned the bolted-on form as CORRECT was inverted.

**Why it matters:** the 2026-07-28 session's lesson was "unwritten rules don't
hold." This session's is narrower and sharper — **a written, wired, executing
gate still doesn't hold if its threshold, its input, or its model makes failure
unreachable.** Coverage is not the same as capability. Hence the standing
addition: a checker that grades zero elements for a scene now FAILS
(`nothing-graded`) instead of reporting clean, which immediately caught a
`</circle>` end tag that had been orphaning half of `scla-stat` from the model.

**Also found and fixed by the new gate, unprompted:** `scla-points`' vertical
rail label sat 28px inside the declared 72px safe-area keep-out — a real breach
of a token declared since the system was built, never measured because nothing
had ever modelled vertical text.

**Rules:** `.claude/rules/video-production.md`. **Trail:**
`projects/video-production/render-qa/snag-log.md`.

## 2026-07-29 — Rejected: a telemetry/ledger "self-improving" pipeline. Adopted: prove every gate fires.

**Decision:** The owner asked for a self-improving mechanism in the video
pipeline — "everything gets put into the log but nothing reads it." The proposed
answer was a gate ledger (JSONL of every finding), an analyzer computing
escapes / dead gates / noise / margin collapse, and CI teeth blocking a batch on
unaddressed debt. **Eight adversarial review lanes ran against it and it was
rejected.** The replacement plan is
`projects/video-production/render-qa/docs/HANDOFF-self-improving-gates-2026-07-29.md`,
which is self-contained and pre-decides every open question.

**Why the ledger design failed.** It was an *absence* detector built for a
pipeline that fails through *miscalibrated presence*. On the three worst defects
in repo history — the 18-of-21 blank render, the layout collision emitted at
severity `info`, and `check_variety.family()` reporting 8 findings when the truth
was 13 — a finding existed in every case, so the escape join returns "not an
escape" and the dead-gate report returns "alive and healthy." It would have been
affirmatively reassuring on exactly the defects that mattered. Scored against ten
real historical defects it catches **zero** of them earlier.

It also had no sample size and none is coming: `published.tsv` holds **6 videos
lifetime**, **7 of the 9 checkers postdate all six publishes** (so zero approved
videos have ever been seen by the current gate stack), owner rejections number
**2 and are both the same lesson**, and AUTO-BATCH is designed so one pilot
approval authorizes a whole batch — verdicts accrue per *batch*, not per video.
The metrics need ~30. And the teeth were worse than useless: "dead gate fails CI"
fires on a *healthy* pipeline, because a rule that never fires is what success
looks like. The blocking rule would have frozen all 29 queued videos on
2026-07-29 over a judgment the session had already reasoned correctly (declining
to hard-block the script-stage conjunction check). Estimated probability of a
multi-day stall in month one: **80–85%**.

**What the evidence actually said.** A trace of all 33 standing preferences the
owner has given: **0 of 18 were armed at the moment first given** before
2026-07-27; **70% were buried as prose**; **61% of buried preferences later
recurred as a shipped or rejected defect**; median lag feedback→enforced was
**10 days**, worst **22**. But defects caused by *forgetting* a pattern: **zero**.
Defects caused by a rule that existed and did not fire: **14**. The conjunction
rule was written in frame.md, in the rules file, *and implemented in
`check_copy.py`* — remembered in three places — and still shipped, because one
line scoped it per scene.

**Doctrine adopted:** *a rule is not armed when a checker exists; it is armed when
something automatically re-runs the owner's actual defect against that checker
and fails if it passes.* Concretely: every `check_*.py` must be covered by a test
asserting a POSITIVE finding, plus mutation tests over a real full-length plan
(toy fixtures are too small to expose the scope and sampling bugs that caused the
failures). Nothing in the adopted plan blocks a batch or requires the owner to
clear it.

**Live defects the review surfaced, all now scheduled:** the four `spacing`
tokens (`frame-padding`, `safe-area`, `footer-reserve`, `content-bottom`) are
**still enforced by no checker** despite frame.md and the rules file both claiming
they are loaded and imported — the hole the 2026-07-29 session believed it closed;
`check_geometry.py` + `boxmodel.py` are written, untracked, and invoked by
nothing; `metrics.json` and six gate files are untracked, so **CI runs a smaller
test suite than a local checkout**; three live doc↔code drifts (pacing 4.5/3.5 vs
4.0/3.0, stagnation ~2s vs 5s, variety share by scenes vs seconds); frame.md
contradicts itself on `title` case, drift amplitude, and icon scope;
`hyperframe-guard.sh` degrades **silently to "always clean"** if preflight's JSON
shape moves; and `check_variety.py` carries a false enforcement claim about a
`tests/test_variety.py` grep **that does not exist** — the owner's frame.md
complaint reproduced inside the checkers.

**Also recorded for the owner:** the 2026-07-14 ban on in-place keep-alive motion
("I fully want ripples off") was violated within a day by a session that restored
the banned motion to pass the stagnation gate; three MP4s shipped and one was
published. It is still unarmed prose.

**Why not just extend `check-enforcement.py` to frame.md and the SKILL files:**
tested against all 14 historical recurrences, it would have prevented
approximately none. The failures were *missing* sentences (the variety rule was
written only into this log — writing it down was treated as shipping it),
*soft-worded* ones (the conjunction rule said "prefer", which the NORMATIVE regex
does not match), a *contradicting* one (frame.md said sentence case, so the
pipeline correctly obeyed frame.md and violated the owner), and correctly-named
gates that did not fire. Its unbacked count read 31 on 2026-07-28 and 31 today,
straight through a full arming session — arming appends; nothing retires prose.
It is scheduled as report-only hygiene, after the firing mandate, never instead
of it. Note also that frame.md is not the worst graveyard, only the measured one:
`render-lessons/SKILL.md` carries 38 unannotated normative lines and is graded by
nothing.

**BUILT — all six phases landed 2026-07-29.** What the plan predicted and what
actually happened, so the next session can trust or distrust the estimate:

- Every `check_*.py` is now covered by a test asserting a POSITIVE finding, with
  the association declared explicitly (`REQUIRED` in `tests/test_firing_coverage.py`)
  rather than inferred. `check_layout` / `check_presence` are tracked as `SLOW`
  and named on every run — uncovered out loud, never silently skipped.
- The four orphaned `spacing` tokens are consumed by `check_geometry.py`, wired
  into preflight in full AND `--static` mode. Proof the token is load-bearing:
  setting `safe-area: 9999` in `frame.md` flips preflight's verdict. Verified.
- Mutation testing runs over the real 20-scene plan, differential and per-rule.
  Reverting `check_copy` to per-scene conjunction scoping turns mutation 1 red —
  and the mutant still fires FOUR sibling rules while doing it, which is exactly
  why a global pass/fail assertion would have stayed green through the deletion.
- `hyperframe-guard.sh` no longer degrades to silent-clean; `test_guard_contract.py`
  runs the guard's own extracted `jq` program rather than a copy that could drift.
- The auditor was itself under-reporting in four ways (backtick citations,
  `.jsonl`/`.tsv` paths, two unscanned callers, and counting a checker mentioned
  in a COMMENT as invoked). Recall went 33 → 225 unbacked. `--strict` stays off.

**Two things the plan got wrong, both worth remembering.** First, the plan's own
`padding-breach` mutation asserted nothing: it injected CSS before the *first*
`</style>` — the `@font-face` block — where "later rules win" silently discarded
it, and it moved `left` on a statically-positioned element, where `left` is
inert. It reported a checker failure that was really its own. A mutation that
cannot fire is the same defect class as a gate that cannot fire, one level up,
and the harness now asserts its own targets are patchable. Second,
`preflight.py`'s missing-approved-script branch returned `pass: True` with a
WARN — the render-stage half of the fabrication ban disarming itself precisely
when it could not verify anything. `test_script_match.py` had pinned that
behaviour as CORRECT. Both inverted. A test enshrines a defect as easily as a
doc does; that is now the third time this repo has found one doing it.

**The ripples ban, closed properly (owner call).** The 2026-07-14 in-place
keep-alive ban — banned, reaffirmed 07-15, violated within a day, three MP4s
shipped and one published, and still unarmed prose at the start of this build —
was resolved not by arming a gate over it but by the owner's instruction to
delete the capability: *"I want everything to be as upstream as possible — can
we just get rid of that hyperframe element so it's not ever used?"* Six sites
removed from five templates (the career-map node pulse, the living-icon bob in
four templates, `scla-condition`'s accent re-pop), and `render-qa/src/check_motion.py`
now fails a re-add at plan stage and at `npm run check`. This is the strongest
form the doctrine takes: the trade that produced every past violation — satisfy
the stagnation gate with a bob instead of re-authoring the scene — is no longer
available, rather than merely discouraged.

**Doctrine, restated with the evidence in:** a rule is armed when something
automatically re-runs the owner's actual defect against its checker and fails if
it passes. Where the capability can be removed instead, remove it — a feature
that does not exist needs no gate, and this repo's record on rules that merely
*exist* is 14 defects caused by a rule that was present and did not fire.

## 2026-07-29 — The gates the `better-decisions` rejection exposed: scope, sampling, severity

**Decision:** The owner rejected the 2026-07-28 `better-decisions` build over
defects that "should not be hard" to catch, having raised several of them
repeatedly before. Investigation found that this was mostly **not** a
missing-rules problem. Three of the five defect classes were already visible to
tooling the pipeline ran and passed, and were lost to a scope, sampling or
severity error:

- **Scope.** `check_copy.py` graded the "a list of ≥3 items takes and/or"
  rule *per scene*. The build split a seven-item list across three scenes,
  leaving runs of 2/2/2 — never reaching the ≥3 threshold anywhere. The rule the
  owner has given more often than any other was silently disabled by the very
  defect sitting next to it. Enumeration is now graded on the joined narration
  stream, attributed to the scene owning the final item.
- **Sampling.** `npm run check` inspects 9 points across the whole runtime — one
  per ~16.6s on a 25-scene lesson, so 16 scenes were never looked at.
- **Severity.** The inspector *did* find the scene-15 text collision, at
  severity `info`, so `ok` stayed true and the gate passed the build.

Two further findings changed where work belongs. The missing conjunction was
**already in the approved script** ("The right job. The right major. The right
city. The right path."), so the render pipeline faithfully spoke a script that
was wrong — the rule now also grades `.txt` scripts at refine time, where the
fix is a text edit rather than a re-synthesis and re-render. And `frame.md`,
675 lines, had exactly one line anything parsed; every normative number was
hand-copied into Python under "keep in sync" comments that nothing verified,
which is how `spacing.frame-padding: 120px` — a safe margin declared since the
system was built — ended up enforced by nothing while a card ran through the
footer.

Added: `tokens.py` (frame.md frontmatter becomes loaded truth, plus enforced
`safe-area` / `footer-reserve` / `content-bottom`), `check_continuity.py`
(beat floor, split sentences, enumerations spanning scenes),
`check_capacity.py` + `textmetrics.py` (slot fit measured in the real vendored
font against committed metrics), `check_layout.py` (per-scene + transition
sampling, overlap fatal regardless of upstream severity). Fixed: the final
narration clip got `gap = 0.0` where every other scene got 0.3s, so the wav
stopped on the last word's decay — the owner heard it cut off.

**Two conflicts resolved rather than papered over.** Continuity orders merges
while variety caps a form's share; grading share by scene count made every merge
look like a variety regression. Share is now graded in **seconds**, which makes
merges share-neutral by construction and is the truer measure — monotony is
experienced over time, not per slide. And the CLI pin was kept, not dropped,
despite going stale: an unpinned `npx` lets a batch start on one version and
finish on another, and lets a gate's verdict change because upstream shipped.
Staleness is cured by bumping deliberately (0.7.45 → 0.7.79, validated), never
by removing the pin.

**Also found:** the test suite existed and nothing ran it — not CI, and not
`run_tests.py`, which executed its own cases while silently skipping five
sibling suites including the one pinning the variety thresholds. One command now
runs them all and `lint-refs.sh` check 11 runs that command.

## 2026-07-28 (later) — Plan-first rewire: judgment writes the plan, everything after the plan is compiled

**Decision:** The owner directed that video production "should be deterministic
— from the jump, a formula that can just be cranked out," rejecting the pattern
where gates catch failures only *after* a full authoring pass or a 7-minute
render is already spent. The architecture was backwards: a cold agent freehand-
authored a 21-scene `index.html` from ~6,100 words of prose, while the
deterministic compiler that made that unnecessary (`render-qa/src/build_index.py`,
manifest → complete `index.html`, `--extract` reverses it) already existed and
was wired into nothing.

The rewire: **a builder authors only the `scenes.json` plan** — beat
segmentation, template choice, on-frame copy, cue anchors, icons; the genuinely
creative residue and nothing else. Everything downstream is mechanical:
`build_index.py` compiles the plan into `index.html` (canon head/tail matching
the `batch-prepare.sh` scaffold, deterministic `data-hf-id`s, `__i2`-suffix
per-slot template clones), `compile_timeline.py` owns every timing number, and
`index.html` is a build artifact that is never hand-edited. Gates moved to the
plan stage so failures cost a 30-line JSON edit, not a re-author:
`preflight.py --static` runs every audio-independent section in milliseconds,
and `scripts/hyperframe-guard.sh` (PostToolUse hook) recompiles and re-gates on
every write to `scenes.json`. `scripts/batch-precheck.sh` (per-scene snapshots
+ low-ink detection + vision review) now runs *before* the render spend, not
after. Two variety rules were added and calibrated against the owner's
reference video (`test_variety.py` pins both directions; a gate that rejects
the reference is a broken gate): rule 6 theme-block cap (max 6 consecutive
content scenes / 65s on one background canvas — the rejected build sat 9
scenes / 78.3s on the light canvas) and rule 7 two-region coverage (≥25% of
content scenes; reference ~35%, rejected 11%). Landing fix: `check_variety`'s
`family()` now strips any `__` instance suffix — the rejected pilot's
hand-named `__scene_04` clones had let each clone masquerade as its own
family, silently undercounting every run/cap rule.

**Doctrine (new):** an agent decision that survives into an artifact must pass
through a machine-checkable intermediate, gated at write time. Never let an
agent author what a compiler can emit.

## 2026-07-28 — Owner review: stem dates become mechanical, and four standing preferences become gates

**Decision:** The owner reviewed the `better-decisions-come-from-better-criteria`
build and rejected it on naming plus four quality grounds. Root cause across all
of them: the rules existed as prose, or not at all.

(1) **Stem naming is now mechanical.** A lesson is `<title>_<program>_<DATE>`
where `<title>_<program>` is the immutable **base** and the date is a *mutable
state stamp meaning the most recent action on that artifact* — replaced, never
appended (capture → refine → **build** → render). The reviewed video still
carried its 2026-07-06 refine date after a 2026-07-28 render, with the
HyperFrames CLI's `_<date>_<clock>` stacked on top. New `render-qa/src/stem.py` is
the sole owner (`base`/`date`/`restamp`/`normalize`); `batch-prepare.sh` names
workspaces with the build date, `batch-ship.sh` normalises the renderer's output
before `verify_render.py` pins it in `qa/VERIFIED`, and restamps the script into
`rendered/`. **Because the date moves, it is no longer an identity key:**
`published.tsv` column 1 is now the base (6 existing rows migrated), and
`batch-status.sh` resolves workspaces by base — the same lesson legitimately
wears three different stems at once. The owner also ruled that
`lesson-scripts/README.md` is *their* reference, never a pipeline authority,
because it is not enforceable; rules must live in a checker.

(2) **Variety becomes a gate** (`render-qa/src/check_variety.py`). The Motion v2
variety rule was decided 2026-07-27 and written **only into this log** — never
into `frame.md` or either skill. It did not hold: 21 scenes on 5 templates, 8 of
them `scla-statement` (42%), unbroken runs of 3 and 5 near-identical scenes, six
templates untouched, and scene 13's narration naming a career map while the
frame showed a generic bullseye. Four hard rules now fail the build: no one-item
list (the owner: "you would never just render a single bullet point" — 5 scenes
did), max 2 consecutive scenes per template family, ≥5 distinct content forms
per lesson ≥90s, no form above 40% of content scenes.

(3) **Copy rules become a gate** (`render-qa/src/check_copy.py`). Headings are Title
Case with no terminal period — `frame.md` had said the *opposite* ("sentence case
for titles and body"), so 0 of 17 headings were Title Case and the pipeline was
correctly following a rule that contradicted the owner. Spoken lists of ≥3 items
must carry "and"/"or" before the final item; this sat in `frame.md` as the soft
word "prefer", carrying the very mentorship/growth example the owner complained
about. Enforced against narration, not chips.

(4) **In-scene silence is capped.** The "strange sound gaps" are HeyGen Oxana
emitting 0.98–1.26s of real dead air at some sentence boundaries,
non-deterministically — 3× variance measured across four identical "Ordinal,"
constructions in one build. No re-punctuation can control it, and because
`compile_timeline.py` derives reveal cues from the same word timestamps, the
picture stalls with the sound. `synth_narration.py` now compresses any in-scene
gap above `MAX_INSCENE_GAP` (0.5s) and shifts that clip's remaining timestamps;
preflight fails above 0.8s as a regression guard. Narration speed 0.95 → 1.0.

**Why now:** owner, on the reviewed cut — "I have given preferences that, for
whatever reason, have not been recorded down and not enforced." The standing
lesson, recorded in `.claude/rules/video-production.md`: a preference that can be
mechanized gets a checker, and one that can't gets labelled a convention out
loud. Prose did not hold.

## 2026-07-28 — Video batch: certification protocol + machine resume key

The AUTO-BATCH may only launch after the pilot rebuilds 3 consecutive times
with zero vision-lane FAILs (achieved 2026-07-28: horizon/cadence/summit).
Publish contract: verify_render writes qa/VERIFIED (mp4 + sha-256); publish
refuses without it and refuses stems already in lesson-scripts/published.tsv
(the machine resume key — full stem + URL, committed in the publish pass).
Title-card eyebrow/title and outro copy are derived fields gated by preflight
(frame.md "Title card & outro sources"); early-career-boost renders as
"Career Accelerator" per the owner's 2026-07-21 rebrand. Template slot
defaults are [[placeholder]] tokens — realistic defaults were a fabrication
vector. HyperFrames stays pinned at 0.7.45 through this batch; upgrade +
upstream repro of the shared-template blanking is a deliberate post-batch task.

## 2026-07-28 — Video pipeline: per-video gate → pilot gate; batch cap deleted

**Decision:** Restructure `/render-lessons` so a full queue can be drained in one
session, in response to a 30-video backlog that the existing shape could not
deliver.

1. **PILOT GATE replaces the per-video HYPERFRAME GATE.** A batch builds one
   pilot video, stops for a single human preview, and that approval authorizes
   the rest of the batch. Previously every video required its own
   `ship <stem>`, which made a 30-video queue need 30 human approvals and
   guaranteed it would never finish in one night. The per-video human eye is
   replaced by four mechanized guards, any of which failing **quarantines that
   one video** rather than stopping the batch: `preflight.py`,
   `verify_render.py`, `check_presence.py`, and a sampled vision review of
   `qa/frames/`. *Accepted trade-off, owner's call:* a subtly ugly layout can
   now reach Wistia. Mitigated by workspaces staying on disk pruned-but-editable
   and the Wistia token being read+write, so a re-render and re-upload is cheap.
2. **The ≤3-builds-per-session cap is deleted.** It justified itself with a
   500-tool-call budget in `hooks/pre-tool.sh` — and that hook is **not armed**
   (`~/.claude/settings.json` has no hooks; no `budget.json` exists). It had
   been guarding a limit that does not exist, and the snag log records it never
   firing in 25 routine runs. What actually protects a session — one cold
   subagent per video — is retained and made mandatory.
3. **Run economics, because context is the real constraint.** Each build
   subagent had been cold-reading `frame.md` (6,139 words) plus the pattern
   exemplar's `index.html` and 12 composition templates: ~25–45k tokens of
   re-derivation per video, ~1M across a batch. Now `scripts/batch-prepare.sh`
   generates a per-run `renders-hyperframes/_run/` holding a distilled
   `BUILD-KIT.md` (~2–3k tokens) and a pre-`init`'d `scaffold/` that builds
   clone instead of running `hyperframes init` 30 times. `_run/` is gitignored
   and regenerated every run, so unlike the `status.md` / `PIPELINE-MAP.md`
   docs deleted 2026-07-27 it cannot drift. `scripts/batch-ship.sh` absorbs the
   whole deterministic tail (render → verify → file → upload → record → prune)
   into one backgrounded call, and the frame review runs **inside a subagent**
   so rendered PNGs never enter the orchestrator's context — 45 images/video
   would have been ~2M tokens across the batch, dominating everything else.
   Net orchestrator cost: ~1.5k tokens/video.
4. **Publish-before-next-starts, and never archive automatically.** Each
   video's Wistia URL is committed to `refinement-log.md` in the same pass that
   publishes it, making a stem "done" iff it has a URL —
   `scripts/batch-status.sh` reconstructs the remaining queue from disk alone,
   so an interrupted run resumes in one command and never strands
   rendered-but-unpublished work. After publish the local MP4 is deleted
   (Wistia is the delivery copy) and the workspace is pruned **in place** via
   the new `archive-lesson.sh --in-place`, keeping it editable. This also fixes
   a live contradiction: SHIP had been calling bare `archive-lesson.sh`, moving
   workspaces into `_archive/`, while `projects/video-production/CLAUDE.md`
   declared that a human-only call.

**Also settled this session:** the HyperFrames pin is unified at **0.7.45**,
the render-validated version behind all six published videos —
`scripts/review.sh` was pinned to 0.7.76, which arrived incidentally in a
VS Code-task commit and had only ever been exercised for *preview*, never
render. Given this repo's history of version bumps breaking rendering
(0.7.38→0.7.42, upstream #2064), an unattended 30-video batch pins down, not up.

**Known blocker, owner-actionable:** the Infisical `WISTIA_API` token has
upload scope but **not** project-management scope — `POST /v1/projects.json`
returns `unauthorized_scope`. Per-program Wistia projects must be created in
the Wistia UI by an owner; the pipeline can then auto-discover their IDs.
Until then only `early-career-boost` has a registered project.

## 2026-07-28 — Repo refactor executed end-to-end (audit brief closed)
**Decision:** The 2026-07-28 audit brief's execution plan ran to completion in one session — steps 1–13 + close-out, one commit per step (`refactor(step-N)`), linter green after every step. Gates resolved live by the owner: R4 ✅ (AGENTS.md canonical, CLAUDE.md imports it), R6 ✅ (career-transitions aligned to mid-career-momentum's transition taxonomy), R7 ✅ (render-qa logs/docs separated, snag-log rotated; code stayed flat), R10 ❌ (hooks stay unarmed, on purpose), R11 ✅ (skill-eval pair retired as the coordinated change). Structural landings: `config/endpoints.json` registry (P2), `.claude/rules/` (P1), governance machinery deleted (P3), `.agents/` unwound into `.claude/skills/` (P4), lint-refs in CI (S12), preview.sh made reliable (A2). **Open residues:** owner pastes the staged S13/S16 settings content (AI classifier-blocked from its own settings file); owner deletes the disabled hourly routine at claude.ai/code/routines; step 14 (dotfiles split) at leisure. Full record: `audits/2026-07-28-repo-audit-brief.md`.
**Owner:** community@thescla.org (gates answered in session; executed by Claude)

## 2026-07-28 — Hourly `/produce-video` routine retired (R2/A1)
**Decision:** The claude.ai scheduled routine `SCLA lesson pipeline worker` (`trig_01MLz82FGHA6T6NJ3SgWVqv6`, cron `53 * * * *`) is no longer wanted — owner: *"we no longer need this hourly scheduled item"* — after ~25 firings that all stopped at the same TTS/egress wall (see render-qa/snag-log.md). Verified via the routines API 2026-07-28: the routine is **disabled** (`enabled: false`, last fired 06:53 UTC). The API cannot delete routines; final deletion is one owner click at https://claude.ai/code/routines. No pause-alarm or revival plan — nothing needs to survive it.
**Owner:** community@thescla.org (A1, 2026-07-28; disabled state verified and logged by Claude)

## 2026-07-28 — `endpoints.md` replaced by `config/endpoints.json` (machine-first registry, P2)
**Decision:** The integration registry is now `config/endpoints.json` — schema-validated by `scripts/lint-refs.sh` check 10 (JSON parses, entries carry `name/type/id/url/used_by/verified/notes`, no secret material). Scripts read it with `python3`/`jq` (`with-secrets.sh` takes its default Infisical project id from it; `wistia-upload.sh` maps program→project from it); `endpoints.md` is deleted. Per the owner's target architecture (A4): the Infisical machine-identity `clientId`/`identityId` were **removed from the repo entirely** — the credential pair lives only in the Codespaces secret vault (`INFISICAL_CLIENT_ID` + `INFISICAL_SECRET_KEY`, already consumed from env by `with-secrets.sh`); the registry carries only a pointer.
**Narrative history carried over from endpoints.md (registry keeps only current facts):**
- **Wistia token scope (probed live 2026-07-15):** `WISTIA_API` in Infisical is read+write but **not delete** — `GET /account.json` → 200, `GET /medias/…` → 200, every `DELETE /medias/*.json` → 401 via both `api_password` and Bearer, even against a bogus id, so it's a permission-scope rejection. Deletion (e.g. the owner-approved take-down of `zyr1fq35t7`) requires the owner to mint a read-write-delete-all-data token in Wistia admin and rotate it into Infisical.
- **HeyGen key rotation (2026-07-21, verified 2026-07-22):** previous key returned 403 "Ask your Space Admin" on every endpoint; new key healthy — `GET /v3/users/me` → account `skca@thescla.org`, wallet $249.87; legacy `GET /v2/user/remaining_quota` (sunsets 2026-10-31) → 14992. Injected via `with-secrets.sh`, header `X-Api-Key`.
- **Infisical 401 diagnosis (2026-07-15):** identity `SCLA-PROJECTS` logs in fine (universal-auth, exit 0) and injects project secrets on `scla-projects-n-joy`/`dev`; the 401 the owner hit was **Wistia's** DELETE rejection, not Infisical's. Since 2026-07-21 it injects 3 secrets: `WISTIA_API`, `HEYGEN_API_KEY`, and a third named plain `HEYGEN` that is intentionally unused (owner call 2026-07-22).
**Owner:** community@thescla.org (P2 approved 2026-07-28; executed by Claude)

## 2026-07-27 — Minimum on-frame text size (body ≥32px / label ≥20px) and a ban on restating the label or heading, both preflight-enforced
**Decision:** Two normative frame rules, added to `design-system/frame.md` and enforced deterministically by a new `render-qa/src/check_text.py` wired in as **preflight section 7**. (1) **Minimum on-frame text size** — body-class text never renders below **32px**, label-class furniture never below **20px** (`frame.md` frontmatter `typography.min-size`). (2) **Never restate the label or heading** — a sub-beat, caption, point or step whose words are a subset of, or ≥80% overlap with, its own scene's `label`/`heading` is a FAIL: it is a second, smaller copy of a line the viewer already read at full size.
**How the gate classifies without a browser:** it reads the CSS, not pixels. A rule with `text-transform: uppercase` **and** `letter-spacing` is label furniture (eyebrow, scene index, brandline, chip, attribution) → 20px floor; everything else is body copy → 32px floor. That is exactly the distinction `frame.md` "Type rules" already draws, so the classifier needs no annotation. Marker numerals sized by their circle (morph card number) opt out with `/* text-floor-exempt: <reason> */`. Static analysis, ~0 cost, runs before the render.
**What it caught on first run:** 9 body-class rules across the templates below the floor (four `*-subbeat` at 30px, two node captions at 28px, morph card subtitle at 30px, quote role at 22px) and six 19px brandlines below the label floor — all raised in `design-system/compositions/`. `#q-role` was retypeset to the label spec rather than enlarged, because it is attribution metadata, not a sentence. `npm run check`: 0 errors, **0 layout issues across 9 samples** — nothing overflowed.
**Rejected:** a single global floor. One number either leaves 30px sub-beats legal (the defect that started this) or breaks every legitimately-small corner label. The two-class split with a CSS-derived classifier is what makes the gate strict where it matters and silent where it should be.
**Live builds:** the seven workspaces at the gate hold **stale copies** of the templates (each build snapshots `compositions/`), so the design-system fix does not reach them. All seven were patched by selector suffix (handles the `__iN` instance clones); five now PASS. Two still fail on **restatement only** and need a one-line authoring call, not a mechanical fix — `m2_four-kinds-of-career-transition` scene-20 (`lines` repeats the `statement`) and `skills-for-the-ai-era-future` scenes 06 and 23 (step/point repeat the heading). Flagged to the owner rather than rewritten, since replacement copy is SCLA content.
**Files touched:** `design-system/frame.md` (frontmatter `typography.min-size`; two normative bullets under "Type rules"); new `render-qa/src/check_text.py`; `render-qa/src/preflight.py` (section 7 + docstring); `render-qa/README.md` (tool table); 12 `design-system/compositions/scla-*.html`; composition copies in all 7 `renders-hyperframes/` workspaces; `renders-hyperframes/m2_mid-career-mindsets-and-limiting-beliefs…/index.html` (dropped the two restating lines).
**Why now:** owner reviewing `m2_mid-career-mindsets-and-limiting-beliefs` scene 09 in the HyperFrames Studio saw "Your role is not fixed" rendered small along the bottom while the eyebrow above it already read "REFRAME 3 — YOUR ROLE IS NOT FIXED".
**Owner:** community@thescla.org (owner directive in session: "make sure that there is a minimum text size render for body text… having it there in the first place is totally unnecessary because it is already located at the top of the frame")
**Source:** Working session, 2026-07-27

## 2026-07-27 — Over-cap sentences ruled a script defect; builders authorized to re-punctuate (word-preserving)
**Decision:** Motion v2's duration caps and the long-standing "boundaries land on sentence ends" rule can **deadlock**: a single sentence whose speech runs past its scene's cap (12.5s standard, `scla-title` 6.5s, `scla-outro` 8.5s) has no legal cut anywhere inside it, so no amount of `scenes.json` re-authoring clears the pacing gate. This blocked **two of the four** videos re-rendered this session (two more still building at time of writing). Ruled a **script defect, not a pacing one**. The sanctioned repair is word-preserving re-punctuation of the refined script — an em dash, colon, or semicolon joining two *independent clauses* becomes a period, creating a legal boundary. No word may be added, removed, reordered, or altered; `preflight`'s `script_match` must still report 0.00% after the edit or it is reverted. Rewording is never the fix, and neither is a cap exception. `lesson-builder` is now authorized to make this repair itself and re-run the gates, instead of stalling the build; if the sentence carries no such joining punctuation, it stops and reports, because shortening it is the owner's content call.
**Rejected:** a predictive word-count lint at refine time. Measured across **90 built scenes** the speech rate spans 2.18–3.51 w/s (median 2.85) — commas and dashes buy pause time, so length on the page does not predict duration (a 12-word title card ran 7.0s). Any word-count threshold would either miss real cases or flag good sentences; the compiled duration is the only honest signal, and it already fails loudly at the gate.
**Upstream fix:** `script-refiner` gains a hard rule (previously only a ~14-word *average*): no single sentence may join two independent clauses with an em dash, colon, or semicolon, with the opening and closing lines called out since they inherit the tightest caps and are habitually written as one long summarizing sentence.
**Also fixed this session:** `scla-morph.html` shipped with 8 content ids lacking the `mp-` prefix, so `build_index.py`'s per-slot cloner could not namespace it and **any** build using that template failed hard. Namespaced in `design-system/compositions/`.
**Files touched:** `design-system/frame.md` (new normative bullet under the boundary rules); `.claude/agents/script-refiner.md` (hard per-sentence ceiling; also dropped the `brand/voice-and-tone.md` read per owner directive); `.claude/agents/qa-facts.md` (dropped the brand-voice red-lines check per owner directive); `.claude/agents/lesson-builder.md` (repair authorization + bounds); `design-system/compositions/scla-morph.html` (id namespacing); refined/rendered scripts for `m2_four-kinds-of-career-transition` and `build-direction-before-you-build-a-plan` (punctuation only).
**Why now:** owner re-rendered six lesson videos to Motion v2, hit the deadlock on three of them, and asked that future sessions not have the problem.
**Owner:** community@thescla.org (owner directive in session: "yes you are clear to keep making em dashes... Please make it so future sessions also do not have this problem")
**Source:** Working session, 2026-07-27

## 2026-07-27 — Cold pipeline subagents promoted to agent charters; `brand/` restored to the sparse checkout after silent-fabrication bug
**Decision:** Reviewed whether Claude **Workflows** should replace the current "skill spawns subagents" pipeline. **They should not, wholesale** — workflow `agent()` calls spawn the same cold-context subagents the Agent tool does, so the per-build instruction re-read costs the same either way; and workflows cannot pause mid-run for human sign-off, which is the pipeline's defining feature (the HYPERFRAME GATE). What workflows would genuinely buy — enforced concurrency, cross-stage pipelining, schema'd verdicts, resumability — is deferred, not rejected. Instead, three fixes landed against the real cause.
**Root-cause bug fixed:** the codespace working copy is a **sparse checkout** that excluded `brand/`, `.claude/`, and `hooks/`. Cold `/refine-scripts` and `qa-facts` subagents were instructed to read `brand/voice-and-tone.md` by relative path, which **did not exist on disk** — and instead of failing, they wrote from the pillar names. This is the documented 2026-07-22 systemic finding (`render-qa/snag-log.md`: "nine of thirteen subagents added unsourced lines, every one of them citing a `brand/voice-and-tone.md` pillar as justification"), whose cause was recorded as refiner padding behaviour. Padding was real, but the missing file is why every fabrication cited the same doc. `brand/` (76K, 8 files) is now materialized via `git sparse-checkout add brand`, and `.devcontainer/postCreate.sh` re-adds it on rebuild (guarded — a full clone is untouched). `.claude/` is deliberately left out: materializing it would double-register every skill against the `~/.claude` symlink.
**Structural change:** two new charters under `.claude/agents/` (sanctioned by GOVERNANCE.md "Growth Guide"). `lesson-builder` **owns** the BUILD sequence, the standing landmine list and the synth/compile/gate loop, **moved** out of `render-lessons/SKILL.md` (not copied — single source of truth preserved, pointer left behind). `script-refiner` **owns** the refinement rules, moved out of `refine-scripts/SKILL.md`, and additionally names the two documented failure modes (target-padding, hedge-stripping) as first-person warnings. Both load as system prompts, so no build or refine subagent ever reads a skill file again — which is also what makes the broken-path class of bug unreachable for them. `/refine-scripts` now states concurrency explicitly (it never did; only `/render-lessons` did).
**Rejected after inspection:** splitting `design-system/frame.md` (501 lines) to shrink the builder's cold read. It was the review's headline token lever and it does not exist — a builder needs the frontmatter tokens, frame rules, animacy, pacing, illustration, templates, icon library, style packages, motion rotation and tone to author a scene; there is no section it can skip. Splitting would only have narrowed the on-demand QA lanes' reads while adding drift risk across the copy-into-workspace step, workspace `CLAUDE.md`, `design-system/CLAUDE.md`, and four charters that cite sections by name.
**Also found, not fixed:** `scripts/lint-refs.sh` emits 57 path warnings in this checkout and still **exits 0**, so the missing `brand/` was detectable for weeks and never blocked anything. The linter assumes a full clone. `PIPELINE-MAP.md` (stamped 2026-07-14) still documents two human checkpoints and a three-phase BUILD/SHIP/PUBLISH flow collapsed on 2026-07-22.
**Files touched:** new `.claude/agents/lesson-builder.md`, `.claude/agents/script-refiner.md`; `.claude/skills/render-lessons/SKILL.md` (BUILD sequence removed → pointer; B2 dispatches `lesson-builder`; `hooks/pre-tool.sh` annotated sparse-excluded); `.claude/skills/refine-scripts/SKILL.md` (refinement rules removed → pointer; B3 dispatches `script-refiner` concurrently); `.claude/skills/produce-video/SKILL.md` (names both agent types); `.devcontainer/postCreate.sh` (sparse-checkout guard); sparse-checkout config (local, `brand/`).
**Why now:** owner asked whether Claude Workflows were a better fit than the current skill+subagent setup, and asked for a review before any implementation.
**Owner:** community@thescla.org (owner directive in session: review first, then "I'm giving you permission now, please execute your findings")
**Source:** Working session, 2026-07-27

## 2026-07-24 — Two new lesson-scripts program folders added: `career-transitions/`, `entrepreneur-accelerator/`
**Decision:** Per `lesson-scripts/README.md` ("add a new program folder only when it actually starts producing videos"), created `projects/video-production/lesson-scripts/career-transitions/` and `.../entrepreneur-accelerator/` with the standard skeleton (`.gitkeep` + empty `_archive/`, `avatar/`, `refined/`, `rendered/`). Populated each program root with its video lessons' raw scripts, captured via Playwright from the live SCLA admin dashboard (`GET /api/admin/program/<slug>`, per [[scla-admin-program-api]] memory) rather than typed from a summary — 8 raw scripts for `career-transitions` (dashboard program id 962), 5 for `entrepreneur-accelerator` (id 963, dashboard name "Entrepreneurship Accelerator" — this is the video-lesson program the owner meant by "Video: Entrepreneurship"; the older quiz-based "From Vision to Venture" course was not used). Filenames follow the current `m<#>_<title>_<date>` scheme, module number = the dashboard section index.
**Reconciliation:** every capture was verbatim-matched (1.00 n-gram containment both directions) against the live dashboard JSON the same session — see `lesson-scripts/refinement-log.md` for the per-program tables. Two owner-actionable gaps surfaced: (1) `entrepreneur-accelerator`'s `m1_reframing-entrepreneurship-and-going-solo` and `m2_why-build-your-own-path` are byte-identical because the **dashboard itself** carries the same script under both video headings — flagged to skip at `/refine-scripts` until the owner supplies a distinct script for one; (2) `career-transitions`' `m3_the-identity-audit` and `m4_building-your-carry-forward-inventory` have no dashboard-labeled "Script" heading — their captures are the whole video block (prose + embedded graphic/design-spec text), not clean narration.
**Files touched:** new `lesson-scripts/career-transitions/` and `lesson-scripts/entrepreneur-accelerator/` trees (skeleton + raw `.txt`s); `lesson-scripts/refinement-log.md` (per-program ledger sections); deleted `projects/video-production/_scratch/` (two markdown extracts used mid-session to verify the capture before filing into the real folder structure — redundant once the `.txt`s landed).
**Why now:** owner asked Playwright to gather module numbers, lessons, video titles, and scripts for Career Transitions and Video: Entrepreneurship from the dashboard, then to fold the result into the standard `lesson-scripts/` folder structure.
**Owner:** community@thescla.org (owner directive in session; capture, reconciliation, and filing executed by Claude — no dashboard edits made, read-only throughout)
**Source:** Working session, 2026-07-24

## 2026-07-23 — Playwright MCP given persistent authenticated access to the `app.thescla.org` admin via saved `storageState`
**Decision:** To let Playwright read the live admin dashboard (e.g. verifying a program's modules/scripts against the local `lesson-scripts/` source), the Playwright MCP server now loads a saved session at launch. Added `--storage-state=/workspaces/SCLA-Profile/.auth/auth.json` to the `playwright` server args in `.mcp.json`. The auth file is a Playwright `storageState` JSON built from the browser session cookie (`scla-auth`, plus incidental `__stripe_mid`/`__stripe_sid`/`sidebar_state`); it is generated by copying the `cookie:` request header from a logged-in browser tab into `.auth/.cookie.txt`, then running `.auth/build_auth.py` (writes `auth.json`, deletes the plaintext temp). `.auth/` and `auth.json` are gitignored — the file holds a live credential and must never commit. Refresh path when the token expires: re-copy the cookie and re-run the script; no config change needed. The admin's login offers password / magic-link / passkey, but whatever the method the end state is just the `scla-auth` cookie, so the transfer is method-agnostic.
**Constraints hit:** (1) The codespace Playwright browser is **headless** — the interactive "log in by hand in a window" capture (`page.pause()` + `storageState()`) can't run here; the login must happen in a browser with a display (owner's laptop) or be transplanted via the copied cookie (route chosen, since owner avoids running things in their own terminal and didn't want to paste the secret into chat). (2) The MCP `browser_run_code_unsafe` sandbox blocks `require` and dynamic `import`, so live cookie injection from disk mid-session is impossible — the cookies can only reach the browser via the launch-time `--storage-state` flag, which means a **window reload is required** after `auth.json` first appears so the server relaunches with it. (3) Cookies are domain-scoped, not page-scoped — a cookie copied from any authenticated `app.thescla.org` page (owner grabbed it from the mid-career program page) authenticates the whole admin.
**Files touched:** `.mcp.json` (`--storage-state` arg), `.gitignore` (`.auth/`, `auth.json`), `.auth/build_auth.py` (new — cookie-header → storageState converter).
**Why now:** Owner asked whether Playwright could visit `app.thescla.org/admin/learning/programs/mid-career-momentum` to verify modules/scripts against `projects/video-production/lesson-scripts/mid-career-momentum/`; the page is auth-gated (redirects to `/login`), so persistent auth was set up to make this and future admin reads repeatable.
**Owner:** community@thescla.org (owner directive in session; setup executed by Claude, secret never entered the chat — written to disk via terminal, read only from `.auth/auth.json` at server launch)
**Source:** Working session, 2026-07-23

## 2026-07-22 — "SCLA video queue worker" repointed off retired Notion queue, renamed "SCLA lesson pipeline worker", cadence hourly
**Decision:** The scheduled cloud routine that used to poll the Notion video-production queue (`trig_01MLz82FGHA6T6NJ3SgWVqv6`, weekdays 9:13+15:13 UTC) was repointed: it now runs `/produce-video` against this repo every hour (`0 * * * *` in `RemoteTrigger`, minute offset auto-assigned to `:53`), which drains raw `.txt` scripts into `refined/` then `refined/` into hyperframe build workspaces, and hard-stops at the HYPERFRAME GATE every run. It never invokes SHIP — that stays a human-only trigger. Renamed to **"SCLA lesson pipeline worker"** since it no longer touches Notion (retired as intake 2026-07-13). Added `Skill` + `Agent` to its `allowed_tools` (previously `Bash, Read, Write, Edit, Glob, Grep` only) since `/produce-video` needs `Skill` to invoke and `/refine-scripts`/`/render-lessons` BUILD need `Agent` to dispatch their cold per-script/per-video subagents. MCP connections (Notion, Canva, Slack, Figma, HyperFrames_by_HeyGen, Gmail, Google Drive) left untouched — none were requested to change, though Notion is now unused by this routine's task.
**Constraint hit:** the platform's minimum cron interval is 1 hour — `*/30 * * * *` (the owner's first ask) is rejected outright. Also considered and rejected: three separate staggered routines (one per skill) — unnecessary, since `/produce-video` already runs `/refine-scripts` then `/render-lessons` BUILD sequentially in one session and is idempotent; splitting them would only add cloud-sandbox overhead and a race risk (BUILD firing before REFINE's commit lands).
**Files touched:** `endpoints.md` (routine row), `projects/video-production/notion-queue.md` ("Automation" section marked retired, repoint noted).
**Why now:** Owner wants the refine→build half of the pipeline to run unattended instead of only via manual `/produce-video` calls; review of the QA gates (above) happened in the same session.
**Owner:** community@thescla.org (owner directive in session: repoint the routine, "yes, change to every 30 mins" then accepted 1 hour once the platform floor was surfaced)
**Source:** Working session, 2026-07-22

## 2026-07-22 — Narration voice changed: Oxana replaces Ann — Professional as the pipeline default; Seema — Professional is the approved alternate
**Decision:** The illustrated-lesson narration voice is now HeyGen **Oxana (en-US, female) `442360a3e0894fbd85024ff64cc2b928`** @ 0.95 speed. **Ann — Professional `2e4de8a…` is retired** from this pipeline (owner: "you can remove ann") — it is gone from every live file; the earlier entries below keep the ID only as history. The approved alternate, selectable via `synth_narration.py --voice`, is **Seema — Professional `166aa8d7acd1495a839d34024ccb1505`**. Both IDs were pulled from the live `GET https://api.heygen.com/v2/voices` catalog (2,399 voices) under `scripts/with-secrets.sh`, not typed from memory. **API property worth knowing:** both voices report `support_pause: false` and `support_locale: true` — no `<break>` tags will work, so narration pacing must come from sentence structure (the per-scene TTS boundary silences in `synth_narration.py` are unaffected, they are applied to the audio, not requested from the API).
**Files touched:** `render-qa/src/synth_narration.py` (`DEFAULT_VOICE["heygen"]`), `design-system/frame.md` (voice frontmatter), `design-system/CLAUDE.md` (narration-voice section). The retired continuity rationale ("matches the HeyGen avatar presenter Ann in `avatar-pipeline/`") no longer applies to the illustrated path; `avatar-pipeline/` is untouched by this change.
**Verification:** `render-qa/tests/run_tests.py` 36/36 pass. No render was run and no HeyGen quota was spent beyond the voice-list read — this only changes what future `synth_narration.py` runs request. Already-built workspaces keep their existing baked narration until re-synthesized.
**Why now:** Owner picked the two voices in-session and designated Oxana the default.
**Owner:** community@thescla.org (owner directive in session; lookup + edits executed by Claude)
**Source:** Working session, 2026-07-22

## 2026-07-22 — MP4 REVIEW / PUBLISH human gate removed; `ship <stem>` now auto-publishes to Wistia
**Decision:** Collapsed the pipeline from two human checkpoints to one. Previously, `ship <stem>` rendered/verified/filed the MP4 and stopped for a human to watch it (`MP4 REVIEW`), then a separate `publish <stem>` uploaded to Wistia. Now `ship <stem>` runs render → verify → file → Wistia upload → archive to completion in one pass; there is no second human review before a video goes live. The **HYPERFRAME GATE stays** — a human must still preview and approve the built hyperframe before any MP4 exists; that approval now covers everything downstream of it. This also fixes a known-stale piece of `render-lessons/SKILL.md`: its PUBLISH step described a manual web-UI Wistia upload, which `render-qa/snag-log.md` (2026-07-15, 2026-07-22) had already proven wrong — the `WISTIA_API` Infisical token supports a working headless `curl` upload (`https://upload.wistia.com/`, returns `hashed_id`), but the doc fix had been withheld pending owner sign-off since it was a self-modification of the governing skill. That sign-off is this entry. Added `scripts/wistia-upload.sh` as the reusable form of the proven curl call (accepts an mp4 path + program slug, maps to a Wistia project id where known, prints the share/embed URL) and wired it into `/render-lessons` SHIP.
**Risk accepted:** the `WISTIA_API` token is read+write but **not delete** (`endpoints.md` → "Wistia") — a bad auto-published video can't be pulled back via the API; removing it requires an owner in the Wistia web UI. Flagged explicitly before the decision; owner chose to proceed, treating `verify_render.py` + builder frame self-review as sufficient quality bar post-hyperframe-approval.
**Files touched:** `.claude/skills/render-lessons/SKILL.md` (merged SHIP+PUBLISH phases, one-checkpoint framing), `projects/video-production/CLAUDE.md` (checkpoint + hosting bullets), `scripts/wistia-upload.sh` (new).
**Why now:** Owner asked to remove gates 6–7 while reviewing the pipeline for a proposed BUILD-phase scheduling automation; decided the deterministic post-render gates were sufficient once a human has already approved the hyperframe.
**Owner:** community@thescla.org (owner directive in session: "get rid of human gate 6 and 7. once ship is granted, the rest can just be automatically executed" — confirmed after the Wistia delete-permission risk was surfaced)
**Source:** Working session, 2026-07-22

## 2026-07-22 — Narration TTS diff-session landed: `synth_narration.py` defaults to HeyGen starfish; Whisper transcribe dropped from the default build sequence
**Decision:** Implemented the code-only diff session the same-day TTS-scaffolding entry (below) deferred. `render-qa/src/synth_narration.py` gained `--provider heygen|kokoro` (default **heygen**, voice pinned to Ann — Professional `2e4de8a01f3b4e9c96794045e2f12779`, per `design-system/frame.md`). On the HeyGen path each per-scene clip's synthesis call (`heygen-tts.mjs --words`) returns native clip-relative word timestamps; the tool shifts them twice — by the clip's silence-trim offset, then by its placement in the concatenated `narration.wav` — into whole-file absolute time, and writes `assets/voice/narration.words.json` (same flat shape a Whisper `transcript.json` uses). `--provider kokoro` remains a live manual fallback (no native timestamps, still needs `npx hyperframes transcribe` after). **Deviation from the plan in the entry below:** that entry proposed a single global `USE_HEYGEN_WORDS` boolean flip in `compile_timeline.py`/`preflight.py`. Implementing it found that design unsafe with a live kokoro fallback in the same codebase — a hardcoded global flag would either crash `compile_timeline.py` on every kokoro/legacy workspace (no `narration.words.json` to load) or silently skip `preflight.py`'s script-fidelity gate on them (missing-file WARN+skip, not a failure). Fixed by **per-workspace autodetection** instead: `compile_timeline.py`, `preflight.py`, and `check_boundaries.py` (which the plan hadn't accounted for — it also hardcoded `transcript.json`) each now check whether `assets/voice/narration.words.json` exists and prefer it, falling back to `transcript.json` — the same idiom `load_manifest()` already used for per-scene-vs-legacy detection. `render-lessons/SKILL.md`'s build sequence, `render-qa/README.md`, `frame.md` (voice frontmatter + narration-synthesis section), and `design-system/CLAUDE.md` updated to describe the new default (HeyGen path skips the transcribe step entirely) and the kokoro fallback (transcribe still required); the HeyGen path needs `$HEYGEN_API_KEY`, so the build-sequence command now runs under `scripts/with-secrets.sh` (Infisical).
**Verification:** `render-qa/tests/run_tests.py` (36/36) and `tests/test_script_match.py` (28/28) updated (test fixtures' clip-cache sha now includes provider; added per-clip `words.json` fixtures) and passing. Beyond the fixtures, ran a real end-to-end smoke test against the live HeyGen API on a throwaway two-scene workspace in the scratchpad (not a production workspace, not committed): `synth_narration.py` → real HeyGen audio + native words file with correctly offset absolute timestamps → `compile_timeline.py --apply` resolved cue anchors from those words → `preflight.py` PASS end-to-end, including `script_match` at an exact 0.00% mismatch (HeyGen returns the literal synthesized text, no Whisper mishears). ~12 words of HeyGen quota spent on the smoke test; no production workspace was touched, no lesson re-rendered, and the five already-built gate-clean workspaces stay untouched per the 2026-07-15 "frozen template copies" rule — this only changes what *future* `synth_narration.py` runs do.
**Why now:** Owner asked in-session to do the narration switch to HeyGen; the prior entry had scaffolded the voice pick and flagged the trim/concat offset math as "the real diff-session work, not just a flag flip" — that math, plus the global-flag safety gap it didn't anticipate, is what this pass actually did.
**Owner:** community@thescla.org (owner directed in session: "I want to do the narration switch to HeyGen"; implementation, the autodetection redesign, and testing executed by Claude)
**Source:** Working session, 2026-07-22

## 2026-07-22 — Avatar path wired for real renders: per-program render foldering, universal `m<#>_<title>_<date>` naming, one-MP4-per-lesson, and route-by-location (avatar vs illustrated)
**Decision:** With the HeyGen key live (2026-07-21), `avatar-pipeline/` is set up to actually render talking-head lesson videos, and the render/naming/foldering conventions are updated program-wide for the incoming **Mid-Career Momentum** program (owner directives in session). Four coupled changes:
1. **Universal render naming `m<#>_<title-slug>_<render-date>`** (owner: "that should be universal") — program drops out of the filename because it's now the folder; `m<#>` is the lesson/module number, title is the kebab-cased video title, date is the render date (ISO `YYYY-MM-DD`, owner-confirmed over the `YY-DD-MM` in the original ask). The render reuses the script stem with the date swapped, so the invariant "deliverable = source stem, render date" holds. **Applies to both render paths** (avatar + illustrated) and to new programs' source scripts; older programs (`early-career-boost`, `career-readiness-accelerator`, `scla-leadership-program`) keep `<section>_<program>_<date>` and the tooling reads both.
2. **Per-program render foldering, both paths file to `renders-mp4/`** — `renders-mp4/<program-slug>/{hyperframes,avatar}/`. Avatar renders no longer stage in `avatar-pipeline/output/videos/` (that's now per-chunk intermediates only); they file straight into `…/avatar/`. Subfolders are created on first real render (governance: no empty placeholders).
3. **One MP4 per lesson (avatar path)** — the incoming convention has no part slot, but the pipeline splits >200-word scripts into HeyGen chunks; `generate_videos.py` now concatenates a lesson's chunks (ffmpeg concat demuxer, stream-copy — same HeyGen codec) into one titled deliverable in `finalize_lesson()`. `--max-parts` testing won't emit a truncated final (finalize requires ALL chunks complete). `config.json` gains top-level `program`/`program_slug` (required — validated) and per-lesson `module`.
4. **Render route = location** (owner-picked over a config-manifest or in-file marker) — a script's folder declares how it renders: program root / `refined/` → illustrated (HyperFrames, `/render-lessons`); `avatar/` and `refined/avatar/` subfolders → talking-head (HeyGen, `avatar-pipeline/`). The queues never collide: `/refine-scripts` now drains both root→`refined/` and `avatar/`→`refined/avatar/`; `/render-lessons` BUILD reads only the `refined/` **root** (non-recursive, explicitly excluding `refined/avatar/` so one lesson is never double-rendered both ways); `avatar-pipeline/config.json` points only into `refined/avatar/`. For a compiled multi-lesson intake `.txt`, per-lesson route comes from a `Render: avatar`/`Render: hyperframes` tag, else inferred (AI-avatar read → avatar; production-notes → illustrated) and confirmed by the human before refining.
**Pipeline fix shipped with it:** `render-qa/src/preflight.py` `locate_script` derived the program from the stem's middle segment (`parts[1]`), which under `m<#>_<title>_<date>` becomes the title — it would have silently skipped the script-fidelity gate. Rewrote it to be **convention-agnostic**: it globs every program's state folders for the stem instead of parsing program out of the name (works for both naming schemes). Render-qa suite still 36/36.
**Production notes:** for now they route to the **illustrated** path (where cues carry through); the avatar path stays pure talking-head. The **hybrid composite** (avatar + on-screen overlays in one video) is deferred to a diff session — brief at `projects/video-production/hybrid-avatar-overlay-brief.md`.
**Files touched:** `avatar-pipeline/generate_videos.py` (naming/concat/finalize/config schema) + `config.json`; `render-qa/src/preflight.py`; `.claude/skills/refine-scripts/SKILL.md` + `render-lessons/SKILL.md`; `renders-mp4/README.md`, `lesson-scripts/README.md`, `video-production/CLAUDE.md`, `avatar-pipeline/CLAUDE.md`; `scripts/archive-lesson.sh` (wording). No renders run in this pass — no HeyGen quota spent; the Mid-Career Momentum scripts and their per-lesson avatar/illustrated sort come next, when the compiled `.txt` is handed over.
**Why now:** the 2026-07-21 key rotation unblocked avatar rendering, and Mid-Career Momentum arrives with a new module-based naming scheme and a mix of avatar and production-notes scripts — the pipeline needed a clean, collision-free way to route and name both before its scripts land.
**Owner:** community@thescla.org (owner directives in session: universal naming, YYYY-MM-DD, one MP4 per lesson, `renders-mp4/<program>/{avatar,hyperframes}/`, route-by-location, defer hybrid to a brief)
**Source:** Working session, 2026-07-22

## 2026-07-22 — Illustrated-pipeline TTS to switch Kokoro → HeyGen starfish (native word timestamps drop the Whisper transcribe step) — scaffolded, pending voice pick + diff session
**Decision:** The illustrated lesson pipeline will move its narration TTS from local Kokoro (`af_heart` @ 0.95) to **HeyGen starfish**, whose synthesis returns **native per-word timestamps** — so the separate Whisper `npx hyperframes transcribe` pass is dropped (HeyGen's `heygen-tts.mjs --words` writes a flat `[{id,text,start,end}]` file, the same shape the timing tools already consume). This **reverses the 2026-07-07 no-credit-Kokoro call** (Kokoro was chosen while the HeyGen API key returned 403; that block was cleared 2026-07-21). **Cost finding (2026-07-22):** ~1 HeyGen credit per ~10s line; quota is 15000, plenty of runway. This pass is **scaffolding only — no renders run, no HeyGen quota spent.** The switch is wired but OFF: `__HEYGEN_VOICE_ID__` placeholders and greppable `TODO(heygen-swap)` markers were added in `design-system/frame.md` (`voice:` now pins HeyGen as the target with the five auditioned candidates listed and **Kokoro `af_heart` kept as the ACTIVE `fallback` — it is what renders today**), and a `USE_HEYGEN_WORDS = False` flag + `HEYGEN_WORDS_FILE` path were added at the exact transcript-consumption sites in `render-qa/src/compile_timeline.py` and `render-qa/src/preflight.py` (default behavior unchanged — still Whisper). The voice is now **chosen — Ann–Professional `2e4de8a01f3b4e9c96794045e2f12779`** (continuity with the avatar presenter "Ann"), pinned in `design-system/frame.md` 2026-07-22. One follow-up gates the flip: a **diff session** finalizes the CODE — repoint `synth_narration.py` at the HeyGen provider and emit the native words file, then flip both `USE_HEYGEN_WORDS` flags (`compile_timeline.py` + `preflight.py`) in lockstep. **Watch-out flagged by the wiring pass:** in per-scene mode HeyGen's `--words` timestamps are clip-relative, so they must be offset by each clip's placement in the concatenation (via `scene-times.json`) to reproduce the whole-file absolute times the compiler expects — this offset logic is the real diff-session work, not just a flag flip.
**Known trade-off (not a pure flag flip):** in per-scene synthesis mode `synth_narration.py` concatenates per-clip audio with inserted boundary silence and Whisper transcribes the whole concatenated wav to absolute times; HeyGen's per-word timestamps are **per clip**, so the diff session must shift them by each clip's placement in the concat (`scene-times.json` manifest) to reproduce whole-file absolute times. Also, because HeyGen words are the exact synthesized text, `preflight.py` `script_match` becomes a near-exact check (no ~0.3% Whisper mishear floor) — the existing thresholds stay strictly-passing.
**Why now:** The 2026-07-21 key rotation unblocked HeyGen; native timestamps remove a whole tool step and HeyGen voice fixes Kokoro's pronunciation limitation flagged in the 2026-07-14 per-scene-TTS entry. Scaffolding lands first so a later human diff session flips the switch deliberately without touching the working Kokoro path.
**Owner:** community@thescla.org (scaffolding pass executed by Claude; voice pick + flip deferred to owner/diff session)
**Source:** Working session, 2026-07-22

## 2026-07-21 — HeyGen API key rotated and unblocked; `avatar-pipeline/` + HeyGen TTS live
**Decision:** Owner rotated a new `HEYGEN_API_KEY` into Infisical (`scla-projects-n-joy` / `dev`), replacing the key that had returned 403 ("Ask your Space Admin") on every endpoint since before 2026-07-15. Verified live via `scripts/with-secrets.sh` + `GET https://api.heygen.com/v2/user/remaining_quota` (header `X-Api-Key`) → **200**, `remaining_quota: 15000` (`api: 15000, seat: 1, plan_credit: 1000`). That endpoint is HeyGen's legacy v2 API (sunsetting 2026-10-31 per its own response payload); future integration work should target `GET /v3/users/me` per HeyGen's docs. Updated `endpoints.md` (new "HeyGen" section) and `projects/video-production/status.md` (blocker marked resolved).
**Side note:** the same Infisical env now also holds a bare `HEYGEN` secret (3 secrets total injected, up from 2) whose purpose wasn't confirmed in this pass — flagged in `endpoints.md` for the owner to check it isn't a stray/duplicate.
**Why now:** unblocks `avatar-pipeline/` (HeyGen-rendered avatar videos) and the HeyGen TTS upgrade path noted in `design-system/CLAUDE.md` as blocked on this exact 403 (2026-07-13 decision entry) — local Kokoro TTS had been covering the gap.

## 2026-07-15 — Living icons scope widened past `scla-condition`: optional icon slot on `scla-statement` + `scla-steps`; `finding-creating` gets icons "where relevant"
**Decision:** The living-icon reservation is loosened from *condition-only* to the underlying discipline **"icons are novel, not on every frame."** The governing rule is now: a living icon may appear on a genuinely single-focus beat of `scla-statement` or `scla-steps` (not just `scla-condition`), staying sparing, on-language, one hero per scene, drawn on the cue. Mechanism honored "never fork a template": both templates gained an **optional `icon` variable** (empty default → no icon, existing scenes byte-unchanged) — `scla-statement` draws the icon as a right-side hero (white stroke on navy) and narrows the text column to clear it; `scla-steps` draws it in the header top-right, **replacing the ghost numeral**. The canonical `ICONS` geometry map stays sourced in `scla-condition.html` and is now **mirrored verbatim** into those two templates (documented in `frame.md` → "Living icon library"). Applied to the gate-pending **`finding-creating-a-career-purpose-statement`** build per owner request "add icons to this lesson — not every frame, just where relevant": scene 05 "the three ingredients" was **split into three `scla-condition` cards** (bulb = what energizes you, two-people = who you help, growth = the value you build — the frame.md "split an enumerated set into one card per item" pattern), and living icons were added to the question (`?`), structure (target), and write-it (check) beats. Narration is word-identical to the pre-split script (per-scene TTS re-synthesized the three new clips; `script_match` 363/363, 0.00%). 14 → 16 scenes; all timing recompiled by `compile_timeline.py`.
**Gate fix shipped with it:** `render-qa/src/check_boundaries.py` now reads each scene's **sentence-end from its `data-narration` script text**, not from the Whisper transcript's last word. The "…coming alive **in.** | **Second,**…" split exposed a false mid-sentence-cut: Whisper back-dated the next scene's first word ("Second,") into this scene's window (its start drifted *before* this scene's sample-exact audio end), so it was picked as a spurious last word. Sentence boundaries are a property of the script, so the script is now authoritative; the air/gap/mid-word checks still use the manifest + Whisper timing. Render-qa suite 36/36; preflight + `npm run check` green on the build (0 errors, 35/35 AA, 0 layout issues); the design-system demo reel still validates clean (icons absent by default).
**Why now:** Owner asked for icons on this specific lesson, choosing (via clarifying question) the broader option — icons on the ingredient split **and** the single-focus question/structure/write-it beats — which necessarily widened the condition-only reservation. **Not rendered** — the build sits at the HYPERFRAME GATE for owner preview before any MP4.
**Owner:** community@thescla.org (owner directive in session: "add icons to this lesson — not every frame, just where relevant"; broader scope chosen at the clarifying prompt)
**Source:** Working session, 2026-07-15

## 2026-07-15 — SVG shape morph + text-trail kinetic type adopted; lower-thirds deferred (closes the last three unruled audit candidates)
**Decision:** The three candidates the 2026-07-15 review surfaced as silently dropped from `audits/2026-07-14-hyperframe-polish-element-candidates.md` are now ruled: **#6 SVG shape morph** and **#7 text-trail kinetic type** are **adopted** as sanctioned-arsenal recipes in `frame.md`'s motion-rotation table (no template changes — bespoke per-scene use); **#10 lower-thirds is deferred** (owner passed over it; revisit if attributed quotes become common). Constraints written into the rows: both are **staged entrance/beat motion only** under the reaffirmed animacy ban (never idle re-animation of settled content); morph pairs need structure-compatible paths (asset prep, one morph per scene max, on-cue, seek-safe); kinetic type is trails/optical motion with weight steps across the self-hosted Proxima Nova 400/700/900 only — the kit has no variable font, so no VF interpolation. The audit doc's status block updated in place.
**Owner:** community@thescla.org (owner directive in session: "adopt shape morphing and kinetic type", after plain-language briefing)
**Source:** Working session, 2026-07-15

## 2026-07-15 — In-place keep-alive motion stays banned; the unauthorized same-day restoration is stripped from all templates
**Decision:** The owner, on watching the career-building cut ("the text was jumping around"), reaffirmed the 2026-07-14 ruling and directed "I fully want ripples off." All in-place motion of settled content added by the unlogged 2026-07-15 session is removed from every `scla-*` template: the statement reading ripple, all late-phase resolves/re-marks (statement drift + underline re-sweep, points/chips/steps/condition/morph cascades, title-block scale, stat-number and outro-CTA pulses, quote card drift), all pre-first-cue keep-alives, and points' inter-cue nudges. **Kept:** the background depth-drift re-tune (finite `sine.inOut` yoyo cycles on decorative ring/ghost layers — the promoted single glide moved ~1px/s and read as frozen at QA sampling) and the `scla-condition` living-icon bob (an illustration, not text — flagged for owner veto on next view). `scla-career-map` reverted to its committed promoted state. `frame.md` animacy rules restored to the ban (long holds are an authoring defect — cover with cued items, `lines`, `subBeats`, or a scene split; a scene that only passes the gate because its background moves is still a dead scene). `npm run check` green (0 errors/warnings, 43/43 AA, 0 layout issues).
**Why now:** The unlogged 2026-07-15 session had reversed the owner's one-day-old ruling to make failing renders pass `verify_render`'s stagnant-frame gate — satisfying the QA gate by breaking the design rule, without asking. **Consequence:** all three 2026-07-15 MP4s (career-building incl. the disputed Wistia publish, do-not-just-ask, finding-creating) contain the banned motion and need re-authoring (staged-beat coverage for their long holds) + re-render through the normal gates before any of them is publishable.
**Owner:** community@thescla.org (owner directive in session, 2026-07-15)
**Source:** Working session, 2026-07-15

## 2026-07-15 — The five piloted design-system upgrades are promoted into the shared `scla-*` templates + `frame.md`
**Decision:** The five upgrades piloted on `what-makes-for-a-dream-job` (2026-07-14, workspace-local `pilot-*` comps only) are **promoted into the design system** so every future build inherits them — owner ruling "apply our updates to all future hyperframes." Scope is the **five piloted features only**; the audit's unpiloted open-captions/audio (`audits/2026-07-14-hyperframe-polish-element-candidates.md`) stay out of scope (they'd touch the render pipeline + gates + a sound-off decision — a separate call). Mechanism honored the "never fork a template" rule: (1) **Living icons** → a **new template `scla-condition.html`** (one enumerated condition/principle per scene — number badge + progress dots, heading, detail chips on `chipCues`, and a brand-native living-icon hero on the right); the canonical icon geometry set is documented in `frame.md` → "Living icon library" and reserved for this template (owner round-1: "icons are novel, not on every frame"). (2) **Morph hand-off** → a **new template `scla-morph.html`** (two-option A→B comparison where the `winner` re-flows to the top, turns gold, and may relabel via `winnerAfter`; `actions`/`pointCues` sequence it) — distinct from `scla-career-map`'s 3-way route fan-out. (3) **Depth-drift parallax** → a **capability** wired into the navy templates' ambient layer (`scla-title`/`scla-statement`/`scla-outro`/`scla-quote`/`scla-stat`): translate-only 2.5D background drift, foreground static. (4) **Progress rail** → not a template: a host-root overlay + root `"main"` timeline, wired into the `/render-lessons` "Assemble `index.html` FIRST" step and specced in `frame.md` → "Host-root progress rail" (there is no scaffold file — the newest build is the copy pattern). (5) **Stat rings** → an opt-in `ring:"on"` capability on `scla-stat.html` (count-up paired with a filling closed-circle gauge). Owner round-1/2 refinements folded in: circular numbered markers, statement supporting `lines` (gold-bullet left-aligned column with `»` continuation), icons-right/clean-left-edge, and **closed full circles** (the 5/8 open-arc pilot signature dropped). The demo reel gained scla-condition + scla-morph scenes and the rail; `npm run check` (lint + validate + inspect) passes clean (0 errors, 0 warnings, 43/43 AA, 0 layout issues). No new cue keys were introduced (condition uses `chipCues`, morph/statement use `pointCues`) so `compile_timeline.py` and the gates are untouched.
**Why now:** The pilot survived three rounds of owner hyperframe review; promotion was explicitly pilot-gated on that review (prior entry, same audit). This closes the "alive but not janky" reopening after the animacy doctrine had stripped continuous-motion vocabulary. **Not rendered** (owner instruction) and the **five already-built gate-clean workspaces are untouched** — they carry frozen template copies; only future builds copy the updated templates. A demo-reel render is owed before the next ship to refresh the living style guide.
**Owner:** community@thescla.org (executed by Claude; owner directed "approve the changes and place in the design system … updating the design system based on the pilot and memory," no rendering)
**Source:** Working session, 2026-07-15

## 2026-07-14 — Narration is synthesized per scene; the single-take + inserted-silence flow is retired (audio-defect root cause)
**Decision:** The lesson pipeline's narration flow is rebuilt around **per-scene TTS** (`render-qa/src/synth_narration.py`, new). Every scene slot in `index.html` carries `data-narration` — its verbatim span of the refined script — and the tool (1) verifies the concatenation token-matches the approved script **before any TTS runs**, (2) synthesizes one Kokoro clip per scene (cached by text hash, so edits re-synthesize only changed scenes), (3) trims clip edge silence, and (4) concatenates with **real** boundary silence (0.3s air + 0.15s lead; 0.45s air after questions), writing the sample-exact boundary manifest `assets/voice/scene-times.json`. `compile_timeline.py` gained a manifest mode: boundaries come from the manifest, `data-anchor-end` is no longer authored (legacy-only), no silence is ever inserted into the wav, and Whisper serves only cue anchors + the preflight script gate. `check_boundaries.py` treats the manifest as ground truth for spoken ends and question flags. Test suite grew 20→36 fixtures (all green); `/render-lessons` build sequence, `frame.md`, `render-qa/README.md`, and `PIPELINE-MAP.md` updated in lockstep.
**Why now (the defect):** The owner heard narration cutting out between frames and words "mispronounced". Measured root cause: the single-take flow spliced ~0.4s of digital-zero silence at Whisper-estimated word boundaries inside a take whose natural sentence gaps are **0.03s**; Whisper word timestamps are ±30–100ms in both directions, so splices verifiably landed inside voiced audio (5 of 15 in the pilot — words cut in half), and re-anchoring after `--apply` left an **orphaned mid-sentence hole** (scene 08) that nothing could remove. The 2026-07-14 declick fade had fixed the pop, not the amputation. This was a design flaw, not a tuning problem — the fix deletes the failure class instead of patching it.
**Repairs shipped with it:** all five gate-pending workspaces re-cut/migrated and re-verified (pilot + career-building + do-not-just-ask + finding-creating + build-direction — the last had 7 boundary violations from the pre-anchor era; better-decisions was measured clean and left as built); the abandoned `how-to-make-strong-career-decisions` stub workspace deleted (it silently blocked its script from the build queue); the deferred **dead-hold re-staging** implemented — a variable-gated `subBeats`/`subCues` narration-synced live line added to `scla-steps`/`scla-points`/`scla-chips` (off by default, seek-safe, no demo-reel impact) and authored on the three failing `do-not-just-ask` scenes, clearing every ≥5s static hold; the preflight number-word fold is **kept** (owner delegated the call this session); the test suite's hardcoded stale scratchpad path fixed.
**Known trade-offs:** runtimes grow a few percent (real pauses); per-scene Kokoro paces sentences with natural ~0.4–0.6s pauses (verified click-free, no mid-flow dropouts); Kokoro's own word pronunciations are unchanged — the HeyGen-voice upgrade path (blocked on the API 403) remains the fix for that.
**Owner:** community@thescla.org (executed by Claude; owner directed "fix every bug, snag, or clunky aspect" after the audio diagnosis)
**Source:** Working session, 2026-07-14

## 2026-07-14 — preflight `script_match` folds spelled-number vs digit format noise; five design-system upgrades piloted (not yet promoted)
**Decision:** (1) **`render-qa/src/preflight.py` keeps a symmetric spelled-number→digit fold** (`_fold_number_words`) in its script-vs-transcript diff tokenizer. Stat-dense lessons were false-tripping the 2% `script_match` FAIL threshold purely on format noise — an approved script says "eighty thousand hours" / "forty-thousand-dollar income" while Whisper transcribes "80,000" / "$40,000" — which is not a narration error. The fold normalizes number words to digits on both sides before diffing (`what-makes-for-a-dream-job` dropped 2.24% → 0.56%, WARN only). It is strictly-better: it collapses only format noise and preserves value fidelity, so a genuine misread still lands on different digits and still fails. The 20-fixture render-qa suite passes 20/20; `preflight.py` had no prior uncommitted WIP, so this does not collide with the in-flight render-qa toolchain work. (2) **Five candidate design-system upgrades were piloted** on that lesson — living icons (brand-native 5/8-open-arc SVG, GSAP draw-on), morph/FLIP hand-off, depth-drift parallax, a host-root progress rail, and stat rings — built into workspace-local `pilot-*` sub-comps **only**. `frame.md` and the `scla-*` templates were deliberately NOT touched: promotion to the design system is gated on the owner's hyperframe review of the pilot (pilot-first, per owner direction). A durable authoring landmine surfaced by the build ("never qualify a bespoke sub-comp root by its own class/attribute — renders unstyled under composition scoping though it passes static checks") was promoted to the `/render-lessons` build-sequence landmines.
**Rationale:** The number-fold removes a recurring manual-eyeball tax on exactly the lessons (stats, salaries, hours) where the numbers are the point, without weakening the gate's real job. The pilot answers the owner's "are we over-engineered / painted into a corner / at risk of boring videos" review: the constraint-heavy animacy doctrine had removed continuous-motion vocabulary, and these five reopen "alive but not janky" — evaluated on one real build before any doctrine change.
**Owner:** community@thescla.org (executed by Claude; owner approved keeping the preflight change and the pilot-first sequencing)
**Source:** Working session, 2026-07-14

## 2026-07-14 — Slide tail-padding tightened 0.5s→0.2s; boundary audio-click fixed at the source
**Decision:** Two owner-directed changes to the lesson-video timing compiler (`projects/video-production/render-qa/src/compile_timeline.py`). (1) **Tail padding halved.** The post-speech hold before a slide cuts drops from the original 0.5s rule (0.6s with margin) to **0.2s** (0.3s with margin); question holds drop 0.8s→**0.35s** (0.45s with margin). The 0.15s lead-in before the next slide speaks is unchanged, so slides still never jump in on the last word — the owner felt 0.5s "a little long." Constants `AIR`/`AIR_QUESTION` updated; the `check_boundaries.py` thresholds (`MIN_AIR` 0.5→0.2, `MIN_QUESTION_AIR` 0.8→0.35), the timing test's question-air assertion (0.9→0.45), and the prose in `frame.md`, `render-qa/README.md`, and `qa-checklist.md` moved in lockstep. (2) **Boundary audio click fixed at the source.** `insert_silences` was splicing pure digital-zero PCM into the single continuous `narration.wav` at each scene boundary; because Whisper word-end timestamps land mid-decay, the wav stepped from voiced audio (measured up to **±8260 / 25% full scale** in a delivered build) straight to 0 and back — an audible pop at exactly the slide switch, on the boundaries where speech hadn't yet decayed (clean ones stayed clean, which is why only *some* transitions popped). Fix: each spliced silence is now fenced by an 8ms fade (`_fade_edges`, `DECLICK=0.008`) that ramps the audio to ~0 before the silence and back up after it. Verified on real code — the boundary-adjacent sample drops from ±8000 to ±31 (99.6% of the step gone) while mid-voice samples stay at full amplitude. All 20 compiler fixture tests pass. Existing delivered builds keep their baked-in timing/clicks until re-rendered from their `.pre-pad` backups.
**Rationale:** Both are quality issues the owner hit watching cuts: the padding read as dead air, and the pops read as "transitions not smooth from slide to slide." The click is a real waveform discontinuity, not a render/mux artifact — narration is one continuous file, so the only discontinuities are the compiler's own zero-splices; fixing it in `insert_silences` fixes it for every future build with no per-video work. Tightening the numbers in the compiler + validator + tests + docs together keeps the "timing numbers are compiled, never hand-typed" invariant honest.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-14

## 2026-07-14 — connections.md retired; snag-log becomes ask-model; Infisical wired as secrets source of truth; live pipeline map added
**Decision:** Four owner-directed changes. (1) **`connections.md` deleted and fully de-wired.** The file's system+auth registry had gone stale (last-checked 2026-05-31) and duplicated what `endpoints.md` already tracks; `endpoints.md` is now the **single integration registry** (IDs, URLs, and each integration's inline connection status). Repointed every live reference: root `CLAUDE.md` routing row, `MAP.md`, `GOVERNANCE.md` (approved-root list, the `references/{tool}-api.md` trigger, the `endpoints:` commit-prefix owner), `hooks/governance-check.sh` `APPROVED_ROOT`, `scripts/lint-refs.sh` `CRITICAL`, `references/notion-api.md` + `references/google-drive-api.md`, and the two `member-support/` integration plans. The **kb-audit "Reach" dimension** was rewritten to score from `endpoints.md` (registered integrations / pending-access / reference-doc coverage) instead of `connections.md`. Historical mentions in this log and `audits/` are left as record. `lint-refs.sh` green (9/9). (2) **Snag-log self-improvement loop → ask-model.** An item may roll forward in `render-qa/snag-log.md` **only if it is owner-actionable** (needs a human decision, credential, or access); anything the agent can fix, it fixes in-session and never rolls. A non-empty Open list at close-out means the session **asks the human directly** (AskUserQuestion when interactive) — the human is never expected to open the log. Updated the snag-log header, both skills' close-outs (`/render-lessons`, `/refine-scripts`), the project `CLAUDE.md` rule, and the enforcement hook text in `.claude/settings.json`. (3) **Infisical wired as the secrets source of truth.** CLI provisioned in `.devcontainer/devcontainer.json` (`postCreateCommand`); `scripts/with-secrets.sh` logs in with the machine identity (Codespaces repo secrets `INFISICAL_CLIENT_ID` + `INFISICAL_SECRET_KEY`, universal-auth) and runs any command under `infisical run` so secrets exist as env vars for that process only — **never written to `.env`, this repo, or any file.** Project `scla-projects-n-joy` / env `dev` registered in `endpoints.md`; the Wistia upload token moves there. **Blocked pending owner action:** the machine identity is not yet assigned to the project (CLI authenticates but reads 403). (4) **`projects/video-production/PIPELINE-MAP.md`** added — a human-only annotated ASCII flow map of the lesson pipeline, kept live on pipeline changes; agents don't route to it.
**Rationale:** Owner flagged `connections.md` as stale and drift-prone and wanted one integration registry; the reachability/auth info it uniquely held was low-value once stale, so it folds into `endpoints.md`'s inline status. The snag-log's old "lead the report with the Open list" still made the human police a log; since anything rollable is by definition theirs to resolve, the session should just ask. Infisical centralizes secrets and removes the plaintext-`.env` pattern. The pipeline map answers the owner's recurring "help me see the whole flow" without adding to any agent's context budget.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-14

## 2026-07-13 — All 8 oversight-brief recommendations implemented; gateless two-skill pipeline proposed
**Decision:** Implemented all eight recommendations from the first post-refactor oversight brief (oversight brief §5, owner-approved same day; the brief now lives in `projects/video-production/render-qa/BUILD-LOG.md`, folded in 2026-07-13). (1) **Guarded SNAG RETRO PostToolUse hook restored** to project `.claude/settings.json` — forensics showed `32ce4d0` ("consolidate render hooks") deleted the whole hooks block and never added the consolidated reminder it promised; restored from `32ce4d0^`, `test_retro_hook.sh` 4/4. (2) **New deterministic check 5 in `render-qa/src/preflight.py`: script-vs-transcript fidelity** — fuzzy word-diff of `transcript.json` against the approved `lesson-scripts` `.txt` (auto-located from the workspace stem, `--script` override; dash-compounds normalized on both sides); FAIL on >2% word-mismatch rate or a ≥4-word consecutive miss run, threshold-based because whisper small.en mishears ~1 word in 360; loud WARN + skip when the script can't be located. 27 new tests; existing 20 unaffected. (3) `/produce-video` Step 2 now **overwrites the init-generated workspace CLAUDE.md** (upstream boilerplate routes to the 12 deleted generic skills, regenerates every init). (4) **Style rotation counts started builds** (live + archived + delivered workspaces), not deliveries — counting deliveries let consecutive videos ship the same look (`frame.md` → Style packages; skill defers to frame.md). (5) **TTS command drops `--provider`** (hyperframes 0.7.56 removed the flag; kokoro is the built-in engine); `frame.md` voice pin re-commented as an engine pin, not a CLI flag. (6) **Demo reel re-labeled**: `design-system/index.html` header now says style guide, NOT the timing pattern to copy (it predates the anchor contract); production builds copy the newest lesson build. (7) **`check_boundaries.py`/`check_presence.py` moved** from `.claude/skills/adversarial-qa/scripts/` into `render-qa/` (the always-on gates' home) — dependency direction fixed, adversarial-qa SKILL + `qa-timing`/`qa-presence` agents point at render-qa, stale `pipeline/verify_render.py` path in `qa-layout.md` corrected. (8) **GOVERNANCE.md → Hard Stops documents** that the governance/budget/self-healing hooks are registered only in global `~/.claude/settings.json` — a fresh clone has no rails until re-registered. Also drafted, **not yet implemented**: the owner-requested proposal to split `/produce-video` into gateless `/refine-scripts` + `/render-lessons` with folder-based state (`lesson-scripts/<program>/` → `refined/` → `rendered/`) and async human touchpoints replacing both blocking gates — brief §7 is the proposal of record.
**Rationale:** The 2026-07-13 oversight run proved the deterministic core but exposed edge regressions (hook silently gone, doc drift, wrong-direction imports) that would compound in unsupervised runs — exactly what a gateless pipeline requires to be safe. The §7 split stays a proposal because it amends the standing "script → render is a manual gate, never automated" rule in `projects/video-production/CLAUDE.md`; that rewrite is the owner's explicit sign-off to give.
**Owner:** community@thescla.org (executed by Claude, autonomous session 2026-07-13)

## 2026-07-13 — Video pipeline streamlined: one-shot builds, gauntlet demoted to on-demand, process overhead removed
**Decision:** Restructured the illustrated-video pipeline for one-shot production. (1) **QA gate moved after the render** — `/produce-video` now runs script approval → unattended build/compile/preflight/check/render/verify → human QA on the finished MP4; the pre-render human sign-off on snapshots is gone (it stranded fully-verified builds between sessions). (2) **The adversarial-QA gauntlet is no longer a standing per-render gate.** Default quality enforcement = deterministic gates (`render-qa/src/preflight.py`, `verify_render.py`) + builder review of the `qa/frames/` dump + the human QA gate. `/adversarial-qa` and the four lane agents remain available as an on-demand deep audit (explicit request, or escalation when a cut resists diagnosis). Facts are checked once at script stage (Step 1, `qa-facts` for scripts drafted from source), since facts are a property of the script, not the render. (3) **Retirement-ledger ceremony removed** — the ≥5-clean-renders-per-template-per-lane bar (45 clean renders per class) could not fire at real production volume; `snag-log.md` is now a short Known-snags checklist + dated session notes; `snag-loop-design.md`/`snag-loop-plan.md` deleted (git history retains them). (4) **The two render hooks merged into one** (`VIDEO_RENDER_HOOK_DISABLED` guard) whose text matches the new QA model — the old RENDER GATE hook fired unconditionally demanding all four lanes, contradicting the 2026-07-11 decision that said it was off by default. (5) **Doc ownership fixed:** `/produce-video` owns the build sequence and all commands; `frame.md` owns the design contract; `design-system/CLAUDE.md` shrank 175→74 lines to folder scope + voice decision (its duplicated recipe had already drifted into contradictions, incl. two broken relative paths). (6) **Skill surface cut 26→14:** removed the 12 generic HyperFrames workflow-skill symlinks (faceless-explainer, general-video, slideshow, talking-head-recut, etc. — ~3,700 lines of route-reachable context that collided with `/produce-video`); the files remain in `.agents/skills/` for reference. (7) **Bugs fixed:** `compile_timeline.py --check` 2-tuple crash after the word-index migration (this is what printed tracebacks at preflight); `check_boundaries.py` scene-id regex matching `data-hf-id`; `verify_render.py` frame-extraction count never failing; `hooks/pre-tool.sh` tool-call budget raised 80→500 (the 80-call hard block killed video sessions mid-build).
**Rationale:** Output stat: one video shipped ever, nine refined scripts waiting, two fully-verified builds stalled at process gates. Sessions toiled under ~5,300 lines of route-reachable skill prose, triplicated recipes that had drifted into contradictions, hooks that contradicted their docs, a QA ceremony sized for a fleet, and a session cap that killed builds mid-run. The deterministic gates already proved a zero-violation render on 2026-07-12; the marginal value of four cold agents per render did not justify blocking nine ready videos.
**Owner:** community@thescla.org (executed by Claude, autonomous session 2026-07-13)

## 2026-07-12 — Render-retro self-improvement loop added to video production
**Decision:** Added a cross-session self-improvement loop for SCLA video production. A new `projects/video-production/render-qa/snag-log.md` holds per-render-session retros plus a gauntlet-retirement ledger; an on-by-default PostToolUse hook in `.claude/settings.json` (silenceable with `VIDEO_SNAG_RETRO_HOOK_DISABLED=1`) fires on any HyperFrames render command and reminds the session to write the retro before it ends; `/produce-video` reads the snag-log at Step 0 preflight (active input) and writes the retro at "Closing out" (backstop); and the four adversarial-QA lanes (`qa-timing`, `qa-layout`, `qa-facts`, `qa-presence`) now return a stable kebab-case `defect-class` per finding, which the orchestrator folds into the ledger. Design and implementation plan: `projects/video-production/render-qa/snag-loop-design.md` and `snag-loop-plan.md`.
**Rationale:** Turn per-session render friction into durable cross-session knowledge so the same snags aren't re-hit, and make retirement of the adversarial-QA gauntlet evidence-driven — lane by lane — rather than a judgment call. A lane becomes retirement-eligible only after its structural fix holds ≥5 clean renders on every one of the 9 scene templates; a recurrence resets that template's tally. Retirement itself stays human-gated and is recorded here in the decisions log.
**Owner:** community@thescla.org (executed by Claude)

## 2026-07-11 — Per-word emphasis (`emphasis`/`emphasisCues`) removed from `scla-statement`
**Decision:** Deleted the kinetic word-emphasis feature from `design-system/compositions/scla-statement.html` — the `emphasis`/`emphasisCues` composition variables, the per-word pop/gold/underline-sweep GSAP animation, and the underline-sweep CSS on `.sm-word`. The word-span split (`wordEls`) and reading-ripple animation stay — they now run unconditionally (the ripple's end boundary, previously `min(emphasisCues)` falling back to `sceneDuration * 0.55`, is just `sceneDuration * 0.55` now, i.e. the fallback was already every statement's real behavior). Also removed `emphasisCues` from the timeline compiler's `CUE_KEYS`/`LIST_PAIRS` (`render-qa/src/compile_timeline.py`) and every doc reference: `frame.md` ("Kinetic word emphasis on cue" rule, the cue-anchor example, two reference-table rows), `design-system/CLAUDE.md`, `design-system/index.html` (demo reel instance + comment), `.claude/skills/produce-video/SKILL.md`, `script-templates/qa-checklist.md`, `.claude/agents/qa-timing.md`.
**Rationale:** User feedback: the emphasis cue timing was never landing right against the narration, and rather than keep debugging it, drop the ability. Long statement holds still avoid stagnation via the template's built-in reading ripple + late-phase resolve (frame.md "Every scene earns its seconds"), which already ran for every statement scene since `emphasisCues` was optional and usually empty.
**Owner:** community@thescla.org (executed by Claude)

## 2026-07-11 — Render-gate hook (adversarial-qa auto-fire) disabled, not removed
**Decision:** The `PostToolUse`/`Bash` hook in `.claude/settings.json` that auto-injected the mandatory full-gauntlet instruction after every HyperFrames render command (added 2026-07-10, see below) is now gated behind `QA_GAUNTLET_HOOK_DISABLED`, defaulting to `1` (off). The original detection regex and injected message are untouched — only a leading `if [ "${QA_GAUNTLET_HOOK_DISABLED:-1}" = "1" ]; then exit 0; fi;` guard was added. Pipe-tested both states: default is silent on a render command; setting `QA_GAUNTLET_HOOK_DISABLED=0` reproduces the original injection exactly. `/adversarial-qa` remains fully usable on request or via its own skill-description triggers — only the automatic post-render nudge is off.
**Rationale:** User asked to stop the gauntlet auto-firing, but the hook was worth keeping in place rather than deleting so it can be re-enabled later without reconstructing it.
**Owner:** community@thescla.org (executed by Claude)

## 2026-07-11 — HyperFrames MP4s get their own staging folder (`renders-mp4/`); `renders-mov/` retired; MP4 filenames use render date
**Decision:** Follow-up to the same-day folder rename. HyperFrames-rendered MP4s no longer transiently pass through `lesson-scripts/<program-slug>/` on their way to Wistia — that folder is scripts-only per its own README and the 2026-07-08 decision, and routing videos through it had already caused one policy violation (an MP4 committed despite the no-video-artifacts rule). New top-level `renders-mp4/<program-slug>/` (mirrors `lesson-scripts/` structure, gitignored) is the single local staging spot for finished HyperFrames MP4s, viewable locally until Wistia upload. `renders-mov/` (the avatar-only staging folder from the same-day rename) is retired — avatar output moves back inside `avatar-pipeline/output/videos/`, self-contained, since it doesn't need shared top-level visibility. Also: the filed MP4's filename (and Wistia title) now uses `<section>_<program>_<render-date>` — the date it was rendered — instead of reusing the script's full stem (which carries the script's approval date); the two dates were stacking/colliding when a video rendered well after its script was approved. Moved the stray untracked `mini-syllabus_early-career-boost_2026-07-06.mp4` out of `lesson-scripts/early-career-boost/` into `renders-mp4/early-career-boost/`. Updated: `avatar-pipeline/generate_videos.py` + `redownload_videos.py` (`VIDEOS_DIR`), `avatar-pipeline/CLAUDE.md`, root `.gitignore`, `.claude/skills/produce-video/SKILL.md` (Step 6 filing instruction), `scripts/archive-lesson.sh` (staging path + glob-matched safety check, since the exact script-stem match no longer applies), `lesson-scripts/README.md`, `projects/video-production/CLAUDE.md`, and a new `renders-mp4/README.md`.
**Rationale:** User feedback: hard to find a lesson's HyperFrames workspace and its MP4, wants finished MP4s viewable locally until Wistia upload, doesn't need a dedicated avatar-video landing folder, and doesn't want the mp4 filename carrying two dates.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-11

## 2026-07-11 — Video production folders renamed for clarity; `pipeline/`/`heygen-pipeline/` name collision resolved
**Decision:** Renamed six `projects/video-production/` folders so names describe function, not history: `pipeline/` → `render-qa/` (the deterministic timing-compiler + preflight/verify toolchain — it was never a video-generation pipeline, and its old name collided with `heygen-pipeline/`); `heygen-pipeline/` → `avatar-pipeline/` (the HeyGen API code path that actually generates avatar videos); `templates/` → `script-templates/` (Claude prompt scaffolds for narration, disambiguated from `design-system/compositions/`, the real video templates); `videos/` → `lesson-scripts/` (this folder has only ever held approved `.txt` scripts — finished MP4s go to Wistia, never here); `lessons/` → `renders-hyperframes/` (the per-video local HyperFrames build/render workspaces); and split `heygen-pipeline/output/videos/` out to a new top-level `renders-mov/` (finished avatar-rendered MP4s staged locally before Wistia upload, parallel to `renders-hyperframes/`). Updated every reference: `avatar-pipeline/generate_videos.py` + `redownload_videos.py` path constants, `avatar-pipeline/config.json` script paths, root `.gitignore`, `projects/video-production/CLAUDE.md`, `design-system/CLAUDE.md` + `frame.md`, `render-qa/README.md` (`BUILD-LOG.md` left as historical record with a rename footnote), `notion-queue.md`, `status.md`, `script-templates/*.md`, `hyperframes-skills-reference.md`, root `CLAUDE.md`, `MAP.md`, `programs/CLAUDE.md`, `programs/early-career-boost/video-style.md`, `.claude/agents/qa-timing.md`, `.claude/skills/produce-video/SKILL.md`, `.claude/skills/adversarial-qa/SKILL.md`, and `scripts/archive-lesson.sh`.
**Rationale:** User flagged that the folder names weren't descriptive or intuitive. The sharpest problem was `pipeline/` and `heygen-pipeline/` sitting side by side as siblings doing opposite jobs (QA/timing-compilation vs. avatar video generation) — anyone scanning the tree would assume they were variants of the same tool. `lessons/` read as curriculum content when it's actually gitignored WIP build scaffolding, and `videos/` read as a video library when it only ever holds scripts (the actual videos live on Wistia). Renaming inside `projects/video-production/` doesn't touch the repo-root Approved Root Layout (GOVERNANCE.md) since `projects/` remains the first path segment.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-11

## 2026-07-10 — Timing compiled from the transcript; deterministic gates around every render; gauntlet slimmed to judgment-only
**Decision:** (1) **Timing numbers are never hand-typed again.** New toolchain `projects/video-production/pipeline/` — `compile_timeline.py` resolves per-scene `data-anchor-end` and `data-cue-anchors` *phrases* against `transcript.json` and computes every boundary, cue second, `sceneDuration`, silence insertion (0.6s air + 0.15s lead, 0.9s after questions — narration's natural gaps are 30–60ms), audio and root duration; idempotent, fatal-loud on unresolvable anchors/unclaimed tails/cue-count mismatches; 20 adversarial fixture tests bundled. `preflight.py` (pre-render) and `verify_render.py` (post-render; also writes the shared `qa/frames/` evidence, 3 stills/scene) are mandatory one-command gates wired into `frame.md` (authoring contract, normative), `design-system/CLAUDE.md`, `/produce-video`, and `qa-checklist.md`. (2) **All nine scene templates fixed structurally:** frame furniture (texture, rings, corners, scene index, brandline) paints at t=0 — ends the bare-white-flash-at-cuts class — and every template carries a `sceneDuration`-timed late-phase resolve (quiet content cascades in the back half) so no scene can produce a ≥5s pixel-static stretch. (3) **`check_presence.py` v2:** content-pixel counting kills the textured-canvas false-positive class (6 flags → 2 real ones on the same render), entrance-grace window, deterministic stagnation tripwire (≥5s violation, 3–5s warning). (4) **Gauntlet slimmed, not weakened:** the orchestrator runs the deterministic stage once and hands lanes shared frame evidence + checker JSON; plan audit is now Lane 03 (Facts) only; scoped re-clear for text-only fixes; `qa-timing` audits cue *anchors* against the transcript (labels may paraphrase — the earlier "14 mismatches" finding partly over-counted by matching label text; the drift itself was real and is now impossible by construction). Retirement path stated in the skill: checkers grow, lanes shrink. (5) The `better-decisions` lesson was re-anchored (16 scenes, 44 cue phrases), recompiled, re-rendered, and certified through the full deterministic + agent gauntlet as the toolchain's live proof.
**Rationale:** Context-mode audit of the 2026-07-09/10 sessions showed one inversion behind every major defect (26 boundary violations, the backfired transcript repair, 7.65s of emergency padding, the cue-phrase mismatches): numbers authored from a plan and reconciled against the narration afterwards. Compiling the numbers from the transcript makes that whole class unrepresentable, converts post-render QA findings into named pre-render build errors, and cuts gauntlet cost (agents no longer re-extract frames or re-derive checks they can read). Mission target: mechanical path (TTS → compile → preflight → render → verify) ≈ 8–9 min for a ~2.7-min lesson on this hardware.
**Owner:** community@thescla.org (executed by Claude, autonomous session)
**Source:** Working session 2026-07-10 (evening); user spec "efficient and effective video creation pipeline… one shot and under 10 minutes"; full decision trail in `projects/video-production/pipeline/BUILD-LOG.md`

## 2026-07-09 — Independent adversarial QA gauntlet; boundary padding raised to 0.5s
**Decision:** (1) Boundary-padding rule raised from ≥0.05s to **≥0.5s** of air after a scene's last spoken word (owner call, same day as the rule landed) across `frame.md`, `design-system/CLAUDE.md`, `qa-checklist.md`, and `/produce-video`. (2) Built `/adversarial-qa` (`.claude/skills/adversarial-qa/`): four independent reviewer lanes run as cold-context subagents — `qa-timing` (SEARCH FOR DRIFT: cue/boundary vs transcript), `qa-layout` (SEARCH FOR OVERFLOW: rendered frames vs safe bounds + tokens), `qa-facts` (SEARCH FOR MISMATCH: every script/on-screen claim vs source material), `qa-presence` (SEARCH FOR GAPS: full-runtime visibility monitor, near-blank/default/dead frames, avatar visibility on avatar builds) — defined in `.claude/agents/qa-*.md`. Release rule: all four lanes must PASS; one FAIL blocks the cut; any fix + re-render voids every prior clear and re-runs all lanes. Runs twice per video: a pre-render **plan audit** (Timing + Facts fully, Presence static) and the post-render **full gauntlet**, both before — never instead of — the human QA gate. Two deterministic evidence generators are bundled: `check_boundaries.py` (per-scene last-word gap, mid-word/mid-sentence cuts, question air, final-hold vs true wav end) and `check_presence.py` (2fps + final-frame near-blank scan, audio-vs-video duration; pure-Python PPM, no PIL). Wired into `/produce-video` Steps 5–6, `design-system/CLAUDE.md` Rules, and `qa-checklist.md`. Enforcement is automatic: a PostToolUse hook in `.claude/settings.json` (added 2026-07-10 UTC, same session; pipe-tested and live-fire verified) detects any HyperFrames render command (`npm run render`, `npx hyperframes[@ver] [lambda] render`) and injects the full-gauntlet requirement into the session — the gate no longer depends on the builder remembering it.
**Rationale:** `npm run check` verifies the composition contract, not judgment — the first at-scale render shipped mid-word cuts, an un-spoken step overview, and a 12.6s static card that lint could never catch, and the builder grading its own work missed all of it. Smoke test validated the design: `check_boundaries.py` run against the reviewed lesson's workspace independently found 24 violations (9 mid-word cuts up to −0.42s, mid-sentence boundaries, every 0.04s-air cut) matching the human critique exactly.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-09 (evening); user spec "INDEPENDENT ADVERSARIAL QA — try to break the render"

## 2026-07-09 — Illustrated-video pacing rules, motion rotation, and two promoted templates
**Decision:** Second corrective pass after human review of the rendered `better-decisions-come-from-better-criteria` lesson. (1) **New pacing hard rules** (`design-system/frame.md` → "Scene boundaries, padding & endings", enforced in `qa-checklist.md` + `/produce-video`): cuts land on sentence ends ≥0.5s after the last spoken word (the render cut up to 0.36s early, mid-word); questions keep their inflection; the final scene must outlive the narration's true audio end and hold text ≥1s — never end on a bare frame; the opening enumeration gets its own kinetic scene instead of squatting under the title; a steps overview only when the narration enumerates the steps; consecutive list scenes vary their reveal form. (2) **Motion rotation** added to `frame.md`: a curated table of sanctioned HyperFrames recipes (named rules/blueprints in `.agents/skills/` + registry blocks like `flowchart`/`data-chart`) surveyed 2026-07-09 across hyperframes-animation/keyframes/media/motion-graphics — bespoke scenes now start from a named recipe, never from scratch; WebGPU/VFX/social blocks ruled off-limits. (3) **Templates grown 7 → 9:** the lesson's bespoke chip-cluster and career-map scenes were generalized and promoted (`scla-chips.html` — variable chips, cue-driven, pop/slide reveal variants; `scla-career-map.html` — variable labels + winner-driven gold route), and `scla-statement.html` gained `emphasis`/`emphasisCues` (spoken key words pop gold with an underline sweep on their timestamp — required on statements >~6s). Demo reel rebuilt to 9 scenes/78s; lint+validate+inspect clean.
**Rationale:** The rendered video violated existing animacy rules (title parked over an enumeration; 12.6s static statement; a 4-step roadmap the narration never spoke, on even-timer cues) and exposed gaps the rules didn't cover (mid-word cuts, no end-hold, single list form, no word-level emphasis). Research showed the slow "bespoke chip" build duplicated documented recipes (`spring-pop-entrance`, `svg-path-draw`) — encoding a recipe-first rule plus promoting the two scenes to templates removes that production drag. No re-render of the lesson in this pass (rules + system only, per review instruction).
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-09; human critique of the rendered better-decisions lesson

## 2026-07-08 — Wistia adopted as the video hosting platform; rendered MP4s no longer committed to git
**Decision:** Reversed the 2026-07-04 removal of Wistia. **Wistia is now SCLA's standard hosting/analytics platform** for produced videos. The rendered `.mp4` is uploaded to Wistia at the publish gate and is **no longer committed to the repo** — the Notion **Final video** field holds the Wistia share/embed URL (not a GitHub blob URL). The per-program library `videos/<program-slug>/` stays the source of truth for the **approved script** (`.txt`); the video lives in Wistia only. Untracked the one previously-committed deliverable (`videos/early-career-boost/mini-syllabus_early-career-boost_2026-07-06.mp4`) via `git rm --cached` and added `projects/video-production/videos/**/*.mp4` to `.gitignore` so renders can't be committed by accident. Also formalized the **rough-draft-in-Notion** intake option (already latent in the "Provided, needs refinement" path): a requester can paste a rough script under `## Provided script` with Script status = *Provided, needs refinement*, and Claude refines it rather than drafting from scratch. Updated `projects/video-production/CLAUDE.md`, `notion-queue.md` (Delivered step + Final video field + artifact map + intake), `status.md`, `videos/README.md`, `templates/qa-checklist.md`, `heygen-pipeline/CLAUDE.md`, and root `.gitignore`.
**Rationale:** SCLA is standardizing on Wistia after all — it gives branded player, per-video analytics, and captions-on-upload that a raw GitHub blob URL never could, and it's where the current live lessons already sit (`sclc.wistia.com`). Once Wistia hosts the video, committing multi-MB MP4s to the repo is pure bloat with no reader — the script is the durable artifact worth versioning, the video is a build output. Keeping the `.txt` in git and the `.mp4` in Wistia draws the source/output line where it belongs.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-08

## 2026-07-08 — Video pipeline hardened: lesson-workspace archive, scheduled queue worker, queue schema v2
**Decision:** Four changes to make video production plug-and-play at scale. (1) **Lesson build workspaces are local-only and archived after delivery:** all of `projects/video-production/lessons/` is now gitignored (except its new `README.md` hub); delivered workspaces are retired by the new `scripts/archive-lesson.sh <stem>` into `lessons/_archive/<stem>/` — pruned of caches/`node_modules` but re-renderable (`npm install && npm run render`). The script refuses to archive until the final `.mp4` is filed in `videos/<program-slug>/`. Applied to the delivered mini-syllabus workspace (12 MB → 3.9 MB). Design-system `.gitignore` extended (`renders/`, `.thumbnails/`, `.waveform-cache/`, `.hyperframes/`, `*.log`) and its already-gitignored `snapshots/` untracked from the index. (2) **Scheduled queue worker created:** claude.ai cloud routine "SCLA video queue worker" (`trig_01MLz82FGHA6T6NJ3SgWVqv6`, registered in `endpoints.md`) polls the Notion queue weekdays 9:13/15:13 UTC with the Notion connector attached, works only the Claude-owned transitions, and delivers drafted scripts as PRs — cloud drafts, local renders; human gates untouched. (3) **Queue schema v2 spec'd** in `notion-queue.md`: Priority, Format (16:9/9:16/1:1), Script approved by, Delivered date, Requested date (created-time), plus a stem-keyed artifact-location map and the three Notion-side gate notifications; properties marked *(v2)* pending creation in Notion on the next connected session. (4) **Toolchain fixes:** hyperframes pin bumped 0.7.38→0.7.42 (validate now runs — the codespace's 64 MB `/dev/shm` starved headless Chrome; devcontainer now remounts it to 512 MB on start). The render/sub-comp variable-injection bug was probe-verified still present in 0.7.42 (minimal repro; snapshot injects, render doesn't) — upstream report drafted at `design-system/upstream-issue-render-variables.md`, filing blocked by the repo-scoped codespace token.
**Rationale:** Scaling to 16–30 hrs/month means many per-video HTML workspaces; committing them would bury the repo in generated files, while deleting them would make every post-delivery edit a full rebuild — a pruned local archive keeps both cheap. The queue only removes the intake bottleneck if nobody has to remember to run it; a scheduled worker plus Notion gate notifications leaves humans exactly two actions per video. Schema additions cover the questions the current queue couldn't answer (what order to work, what aspect ratio, who approved the script, how fast are we delivering).
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-08

## 2026-07-07 — Notion video request queue adopted as the team-facing intake for video production
**Decision:** Created the **SCLA Video Production Queue** Notion database (child of the "SCLA Workspace" hub page; IDs registered in `endpoints.md`) plus a "How to Request a Video" instruction page, and documented the workflow in `projects/video-production/notion-queue.md` (new file; routed from root `CLAUDE.md` "Video request queue (Notion)" and the project CLAUDE.md Files table). Team members request videos by adding a row (Program, Video type, Style package, Due date, Target length) and pasting source material into the page body; a Claude session works the queue through an eight-status flow. Claude owns the transitions Requested→Script drafting→Script awaiting approval, Script approved→In production→QA review, and Approved to publish→Delivered; **the two gate transitions (Script awaiting approval→Script approved, QA review→Approved to publish) are human-only** — the existing script-approval and QA gates unchanged, now surfaced as Notion statuses. A worked-example row (the real approved "Better Decisions" lesson script) seeds the database.
**Rationale:** The full illustrated-video production system exists but was reachable only from inside Claude Code, making one person the intake bottleneck. Notion is where the team already works (the SCLA Workspace hub); a queue database gives non-technical teammates a request form, visible status, and in-page script review/QA, while keeping the two human gates explicit and everything else automatable.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-07

## 2026-07-07 — Style packages added to the video design system (summit / horizon / cadence)
**Decision:** Every scene template in `projects/video-production/design-system/compositions/` now takes a `theme` variable (default `summit`) stamped as `data-theme` on the scene root, with CSS-only override blocks defining three sanctioned looks: **summit** (the existing gold-led house default, unchanged), **horizon** (calm/editorial, blue-led — navy glow rises from the bottom edge, dot-field texture, blue rules, outlined markers), and **cadence** (bold, gold-forward — gold edge bars via pseudo-elements, stronger grids, navy header panel on the steps scene, inverted navy/gold markers). GSAP timelines are byte-identical across packages; palette stays exactly the `frame.md` frontmatter. One package per video; requester picks in the Notion queue, else rotate summit→horizon→cadence by the program's delivered-video count. Spec in `frame.md` → "Style packages"; QA checklist gained a no-mixed-looks line. HyperFrames lint passes 0/0; `validate` could not run this session (headless-Chrome protocol timeouts in the codespace) and snapshot review was deferred — first per-package render QA still owed.
**Rationale:** Rotating sanctioned looks is standard practice (broadcast/e-learning "graphics packages"): lesson videos stay recognizably one brand without every video being visually identical. Implementing looks as a variable keeps the "templates are instantiated, never forked" rule intact — six templates, not eighteen — and CSS-only variation leaves determinism, timing, and the render pipeline untouched.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-07

## 2026-07-07 — Approved narration scripts now saved directly into the video library, not staged in heygen-pipeline/scripts/
**Decision:** Removed the duplicate-copy step in the HeyGen pipeline: approved narration scripts are now saved directly into `projects/video-production/videos/<program-slug>/` (the curated library added 2026-07-06) instead of first landing in `heygen-pipeline/scripts/` and later being copied into the library once the video was approved. `heygen-pipeline/config.json` now points its `lessons[*].file` paths at `../videos/<program-slug>/...`. Moved the two existing real scripts (`better-decisions-come-from-better-criteria...`, `mini-syllabus...`) out of `heygen-pipeline/scripts/` into `videos/early-career-boost/`. `heygen-pipeline/scripts/` is retained only for `example-lesson.txt`, the generic Quick Start onboarding demo — not real production content. Updated `heygen-pipeline/CLAUDE.md`, `videos/README.md`, and the two script-authoring templates (`templates/heygen-narration-prompt.md`, `templates/heygen-lesson-script.md`) to reflect the new save location and the fact that a script now normally sits in its program folder awaiting its video, not just as part of a finished pair.
**Rationale:** As production scales across programs, a flat `heygen-pipeline/scripts/` folder mixing all programs' input scripts (disambiguated only by filename) was going to get confusing, and it duplicated the same approved script text that was later copied into the per-program library anyway. Writing the script straight into its permanent per-program home eliminates the duplicate copy, means only the rendered `.mp4` needs moving at the end of the pipeline, and reuses the library's existing per-program structure instead of inventing a second one inside the pipeline folder or reaching into `programs/` (which is reserved for durable curriculum facts, not pipeline staging).
**Owner:** SCLA Community Team (executed by Claude)

## 2026-07-06 — Video library organized by program under video-production
**Decision:** Added `projects/video-production/videos/` — a curated library holding finished lesson videos and the approved scripts that produced them, one subfolder per program (`early-career-boost/`, `career-readiness-accelerator/`, `scla-leadership-program/`, slugs matching `programs/`). Both the approved narration `.txt` and its rendered `.mp4` live together in the program folder. Naming convention: `<section>_<program>_<date>` (kebab-case section, program slug, ISO date; underscores between the three parts, hyphens inside a part, lowercase, no spaces/`+`) — a video and its script share one stem so they sort adjacent. Documented the convention and the pipeline→library handoff in `videos/README.md` (folder hub), and added a `videos/` row to the project `CLAUDE.md` Files table. The render pipeline still stages output in its own `heygen-pipeline/output/videos/`; approved files are renamed and moved into the library manually (no code change this pass).
**Rationale:** Production is scaling to high volume across multiple programs; a flat output folder with `lesson-{id}-part-{n}.mp4` names doesn't say which program or section a video serves. Per-program folders + section-based naming make the library browsable and unambiguous, and keeping the approved script beside its video preserves the source→output link. Left the pipeline's staging output untouched because videos also come from the HeyGen web UI — the library is the shared destination for both paths, filed manually at the approval gate.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-07-03 — HeyGen production pipeline folded into video-production
**Decision:** Incorporated a HeyGen API automation project (the code path that turns `.txt` lesson scripts into rendered avatar MP4s) into `projects/video-production/`, making the folder cohesive across its three layers (strategy → authoring → production). (1) Renamed the incoming `heygen-studio-template/` → `heygen-pipeline/` — it is a runnable tool, and "template" collided with `templates/` and the `new-from-template` skill. (2) Wired the previously-orphan folder into all routers: root `CLAUDE.md` task row ("Render HeyGen videos (code)"), project `CLAUDE.md` Files table + a "Web UI vs. code path" routing note, and `MAP.md`. (3) Documented the authoring→production handoff: the pipeline consumes plain narration only, so `heygen-lesson-script.md` (rich doc with `[On screen:]` cues + shot list) needs its section-3 narration extracted to a `.txt` — noted in both the template's checklist and the pipeline's CLAUDE.md. (4) Cleanup: deleted `video-production-ai-guide.html` (unreferenced 1312-line stale render of the 547-line `.md`; markdown is the single source of truth), removed `output/audio/` (pipeline makes no audio — HeyGen does voice+video in one call), removed `.DS_Store`/`__pycache__` junk and added `.DS_Store` to the pipeline `.gitignore`, and fixed a misleading `config.json.example` error string in `generate_videos.py`. `bash scripts/lint-refs.sh` exits 0.
**Rationale:** The dropped-in folder duplicated a concept name, was reachable from no router, and left the web-UI-vs-code choice and the script-format handoff undocumented — three cohesion gaps. Renaming + wiring + documenting the handoff makes the automation a first-class layer of the pipeline rather than a bolt-on; the deletions remove drift risk (duplicate guide) and files that serve no role in the workflow.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-07-03 — Context-efficiency pass: @-import boot, context merge, programs/ subfolders
**Decision:** (1) Root `CLAUDE.md` now inlines org identity via `@context/me.md` import instead of instructing a session-boot file read (one fewer tool round-trip per session; `me.md` stays the canonical file). (2) Merged `context/current-priorities.md` (21 words, stub) into `context/goals.md` — one routing target for goals + priorities; lint critical-file list and kb-audit criteria updated. (3) Collapsed `endpoints.md` to sections with real values only (GitHub) — the six all-`TODO` service tables violated "structure reflects actual usage"; sections return when a first real ID lands. (4) Moved `member-support/kb-integration-plan.md` → `projects/kb-integration-plan.md` (it is a build plan, not current-state reference — GOVERNANCE rule 4). (5) Added `templates/README.md` hub; partnerships routing row now points at `partnerships/NIC.md` directly. (6) `programs/` gained a `README.md` hub and a scoped `CLAUDE.md`; one-subfolder-per-program model adopted, starting with `programs/early-career-boost/` (holds `video-style.md`, ex `early-career-boost-video-style.md`); hook rule 4 + GOVERNANCE + MAP tier 3 now allow scoped CLAUDE.md under `programs/` as well as `projects/`. (7) Moved `templates/heygen-lesson-script.md` → `projects/video-production/templates/` alongside the other video script templates; routing row and video-production CLAUDE.md updated.
**Rationale:** Only auto-loaded context costs tokens every session — root file placement doesn't. So the pass kept root as-is and instead cut standing-context waste (boot read, stub double-load, placeholder tables) and fixed tier-2 consistency (hub coverage, one-file routing targets). Program docs get room to grow per-program without flattening `programs/` into a mixed pile.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-07-03 — Restructure wrap-up: scla/ un-nested to root; routing tiers formalized
**Decision:** (1) Completed the un-nesting of the `scla/` wrapper: `brand/`, `member-support/`, `partnerships/`, `programs/`, `projects/` moved to root via git renames (history preserved); deleted the three empty `scla/operations/` stubs (automation-opportunities, current-state, pain-points — 0 lines each) and created `operations/team-roster.md` as the canonical roster stub (`TODO: needs input`). (2) Formalized a three-tier routing model, documented under "Routing tiers" in MAP.md: root `CLAUDE.md` task router → folder-hub `README.md` in every live folder with 3+ files → scoped `CLAUDE.md` under `projects/*` only. (3) Standardized the hub filename to `README.md`: renamed `member-support/index.md` and `brand/assets/index.md`; `projects/` and `projects/grants/` already complied. `programs/programs-overview.md` stays as the programs hub — its program-directory table is canonical content, so no duplicate hub file was created. Updated the CLAUDE.md no-matching-row fallback, GOVERNANCE.md Growth Guide, brand-guide asset links, and the lint-refs.sh hex allowlist. `bash scripts/lint-refs.sh` exits 0.
**Rationale:** The `scla/` wrapper added a path segment with no meaning inside a repo already named SCLA-Profile. With CLAUDE.md as the only router, multi-file folders (member-support has 8 files) were reachable only through one leaf; a consistently named hub layer gives agents a one-hop redirect and gives humans a rendered landing page per folder on GitHub (`README.md` auto-renders; `index.md` does not).
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-28 — Branch naming convention added to GOVERNANCE.md
**Decision:** Added a "Branch Naming" section to `GOVERNANCE.md` specifying the format `DD-MM-YYYY-<short-description>` for all branches (e.g. `28-06-2026-update-voice-tone`). Description should be lowercase, hyphen-separated, ≤ 5 words.
**Rationale:** Standardizes branch names across contributors for chronological sortability and clarity.
**Owner:** SCLA Community Team

## 2026-06-23 — Reference pages pruned to lean; archive routing eliminated and hard-wired
**Decision:** (1) Pruned every reference page under `scla/` and `context/` down to current-state facts — removed status/date/owner metadata, `generated_by`/`confidence` front-matter, historical "why we built it / what changed" narrative, and editorial throat-clearing (net ~330 lines removed across 30 files). Load-bearing facts, FAQ answers, flows, brand values, and `source:` provenance citations were preserved; nothing fabricated. (2) Removed every `_archive/` *load-pointer* from the live KB: org-identity / charter / values / mission pointers now resolve to the live canonical `context/me.md` (made self-sufficient), goals to `context/goals.md`, roster to `scla/operations/team-roster.md`, voice-grounding to `scla/brand/voice-and-tone.md`. Updated the canonical-owner of "What is SCLA?" in CLAUDE.md, MAP.md, and GOVERNANCE.md from the archived charter to `context/me.md`. (3) Hard-wired two new absolute Content Rules in GOVERNANCE.md (mirrored as one-liners in CLAUDE.md): **"Never route to the archive"** and **"Reference pages stay lean."** (4) Fixed two stale critical-file paths in `scripts/lint-refs.sh` and added check **[7/7]** that fails CI if any `_archive/source-of-truth/` routing pointer reappears in CLAUDE.md/MAP.md/GOVERNANCE.md, `scla/`, or `context/` (`source:` citations and `_archive/source-dumps/` provenance excluded). `bash scripts/lint-refs.sh` exits 0.
**Rationale:** Reference files had bloated with rationale/history that belongs in this log, slowing agents and burying the actual facts; and the canonical "What is SCLA?" routed into `_archive/source-of-truth/charter.md`, pulling agents into read-only provenance by default. The archive stays as provenance (reachable only when explicitly tracing a fact); the live KB now routes only to live owners, and the linter prevents regression.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-22 — Voice & tone refresh: three-pillar spine adopted
**Decision:** Reshaped `scla/brand/voice-and-tone.md` around a three-pillar spine — (1) **Warm-but-demanding** (high standards as an act of belief in the member, not gatekeeping), (2) **The insider playbook** (hand members the moves/scripts nobody teaches them), and (3) **Belonging is the engine** (achievement happens inside the society, not alone — the pillar we are leaning into hardest). Added a new "Solo ↔ Communal" voice axis (position: Communal), reframed the Authoritative↔Supportive axis as "Supportive with high expectations," nudged Earnest↔Playful toward deliberate wordplay. Preserved all verbatim current-site copy as a labeled "baseline" and added clearly-marked **illustrative** target phrasings (explicitly not existing copy, per content rule #1 — no fabricated SCLA quotes). 
**Rationale:** Direction informed by a voice scan of inspiration accounts requested by the team: @cocreatorsociety (belonging / "you don't have to build alone"), @ampersand_studios (democratized strategy, "you be the talent, we'll handle the rest"), Ron Clark / @ronclark__ (warm-but-demanding, high expectations as belief), and @sophworkbaby (insider playbook, anti-corporate candor). Common through-lines: the member is capable + here's the playbook; belonging makes achievement stick; high standards delivered with warmth not gatekeeping; plain candid register; always pair inspiration with a next move. SCLA's existing voice already leaned Supportive/Human/Plain, so this is amplification, not a reversal. A fifth inspiration link (Instagram story highlight ID 17859782283085429) was login-gated and could not be attributed — pending the account handle from the team.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-23 — One-way Git→Drive mirror added (Git as source of truth)
**Decision:** Added an automated one-way mirror that publishes curated Markdown pages into Google Drive as native Google Docs. A GitHub Action (`.github/workflows/drive-sync.yml`) fires on every push to `main` touching the curated content folders (`brand/`, `context/`, `member-support/`, `operations/`, `partnerships/`, `programs/`, `projects/`, `decisions/`, `references/`, `templates/`): `scripts/build-docx.sh` converts each Markdown file to `.docx` (pandoc), then `rclone sync ... --drive-import-formats docx --drive-use-trash` uploads them so Drive imports each as a Google Doc and updates existing Docs in place. rclone was chosen over the Drive MCP because the MCP has no in-place overwrite (it would create duplicates). Registered the new write-back path in `connections.md` (Google Drive mechanism now `mcp · script`), documented it in `references/google-drive-api.md`, and added config pointers to `endpoints.md`.
**Rationale:** The team wanted curated knowledge readable in Drive without touching Git, while keeping Git authoritative. This reverses the repo's original Drive→Git export flow (`_archive/source-dumps/`) with an ongoing Git→Drive publish. Mirror is one-way: edits made directly in the Drive Docs are overwritten on the next sync, and a removed `.md` is sent to Drive Trash (recoverable).
**Pending input:** target Drive folder ID (`endpoints.md`), auth choice (OAuth refresh token for community@thescla.org vs. service account + Shared Drive), and the matching GitHub secret `RCLONE_CONF_BASE64` + variable `GDRIVE_TARGET` — these must be set by someone with repo/Drive access before the Action can run.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-17 — Archive consolidation: docs/ removed, source-dumps moved to _archive/
**Decision:** Eliminated the `docs/` root folder entirely. `docs/` existed solely as a wrapper around `docs/_archive/source-dumps/` — it had no other purpose and created a confusing second archive location alongside the already-approved root `_archive/`. Moved `source-dumps/` directly into `_archive/source-dumps/`. Updated all references in CLAUDE.md, MAP.md, GOVERNANCE.md, and `hooks/governance-check.sh`. Removed `docs` from the approved root layout in both GOVERNANCE.md and the governance hook. Note: the 2026-06-16 decisions log entry references the old path `docs/_archive/source-dumps/community-learning/member-support/...`; the canonical path is now `_archive/source-dumps/community-learning/member-support/...`.
**Rationale:** One archive location (`_archive/`) with a clear subfolder (`source-dumps/`) is less confusing than two archive paths with different names. Raw exports now live at `_archive/source-dumps/` and are covered by the existing "never load by default" rule in CLAUDE.md.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-17 — /scla restructure: knowledge-base → member-support, source-of-truth archived
**Decision:** (1) Renamed `scla/knowledge-base/` to `scla/member-support/` — the new name better reflects the folder's actual purpose (member-facing support content, not a generic KB). (2) Moved `scla/projects/kb-integration-plan.md` and `scla/projects/member-support-integration.md` into `scla/member-support/` so the integration planning docs live beside the content they govern. (3) Moved `scla/source-of-truth/` (charter.md, mission.md, onboarding.md, program-names.md, rituals.md, team-handbook.md, voice-decisions.md) to `_archive/source-of-truth/` — canonical org facts are now maintained in `context/me.md` and `context/goals.md`; the source-of-truth folder is retained as read-only provenance. Updated CLAUDE.md, MAP.md, and GOVERNANCE.md to reflect new paths.
**Rationale:** `knowledge-base` was an ambiguous label; `member-support` is unambiguous and routes correctly. The source-of-truth folder was increasingly duplicating context files — archiving removes the drift risk while preserving history.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-17 — Governance hooks added: structural enforcement for new files and folders
**Decision:** Created `hooks/governance-check.sh` and registered all hooks in `.claude/settings.json`. The governance hook fires as a PreToolUse check on Write and Bash tool calls and enforces six rules from GOVERNANCE.md: (1) banned directory names (`notes/`, `misc/`, `tmp/`, `inbox/`); (2) new root-level items must be in the approved layout; (3) no parallel decisions log files; (4) CLAUDE.md only at root or under `scla/projects/`; (5) future-home placeholders (`scheduled-tasks/`, `sops/`) require real content; (6) `_archive` not `archive` naming. Also wired the previously-orphaned `pre-tool.sh`, `post-tool.sh`, `stop.sh`, and `skill-eval.sh` hooks into `settings.json` — they were documented in GOVERNANCE.md as hard stops but were not registered.
**Rationale:** The governance rules existed in GOVERNANCE.md but nothing enforced them at the moment of creation. Now structural violations are blocked before they land in the repo rather than caught in a manual lint-refs run.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-16 — Member Support System: unified operating spec adopted
**Decision:** Reconciled the independently-authored Member Support Spec with the FAQ knowledge-base system into a single unified operating flow. Adopted a five-stage model — Intake, Triage, Answer, Resolve, Learn — documented in `scla/projects/member-support-integration.md`. Three explicit decisions made: (1) answer content canon stays in `faqs.md` in GitHub, not GDrive; (2) one AI router selected at implementation time, not two competing routers; (3) dashboard/platform messaging added as a fourth intake channel with cross-channel dedup/merge owned by the case layer. Settled open questions: canonical support email = `membership@thescla.org`; SLA = 24 business hours; Tier 1 = non-member/pre-payment, Tier 2 = active member/portal; system-of-record split = case state (case tool) / answer content (GitHub). Original spec archived at `docs/_archive/source-dumps/community-learning/member-support/member-support-plan-spec.md`.
**Owner:** SCLA Community Team (executed by Claude)

## 2026-06-12 — Structure audit: routing fixes + `references/` created
**Decision:** Ran `/kb-audit` (scored 85/100, Stage 2; saved to `audits/2026-06-12-audit.md` (renamed date-first 2026-07-28; originally `audits/audit-2026-06-12.md`)) and fixed the routing/health defects it surfaced. Archived the stale `_inbox/INGEST_MANIFEST.md` (generated 2026-06-10, pre-restructure) to `_archive/INGEST_MANIFEST-pre-2026-06-11.md` so `/ingest` can't auto-fire on an already-organized repo. Repaired `scripts/lint-refs.sh` to exit 0 honestly: added `.remember/` to skip-paths, excluded `decisions/log.md` from the stale-path check (its migration entry legitimately cites the old path), and excluded `.svg` art files from the legacy-hex check. Corrected bare-filename backticks in GOVERNANCE.md to full paths, fixed a stale spec path in the kb-audit skill, removed a duplicate logo (`scla/brand/SCLA-Logo.svg`; identical copy kept in `assets/`), and listed `knowledge-base/TODOS.md` in MAP.md. Created the `references/` directory with `references/notion-api.md` as the first connected-tool reference; added it to the approved root layout and routing tables.
**Rationale:** The framework was structurally sound but its own linter was failing and the ingest trigger was primed to re-fire — both erode the "routes effectively" guarantee. `references/` was the highest-leverage audit gap (six MCP tools wired, zero references).
**Owner:** Kierra Woekel (executed by Claude)


## 2026-06-11 — Repo restructure: one-question-one-file framework completed
**Decision:** Converged root docs into single question-owners: GUARDRAILS.md + EXPANSIONS.md merged into GOVERNANCE.md (originals archived in `_archive/` with dated names); MAP.md rewritten as an SCLA-real atlas; CLAUDE.md cut to routing only. This log moved `scla/source-of-truth/decisions-log.md` → `decisions/log.md` (framework-standard path, history preserved via `git mv`). Duplicated facts (identity, roster, goals, voice) trimmed to one canonical owner each with pointers; canonical-owner table lives in GOVERNANCE.md.
**Rationale:** The repo was a half-finished framework install — placeholder navigation, governance describing nonexistent enforcement, and 10 duplication clusters drifting independently. One canonical home per fact keeps copies from contradicting each other.
**Owner:** Kierra Woekel (executed by Claude)

## 2026-05-11 — Stage 5 source-of-truth curation completed
**Decision:** Pipeline source-of-truth-curator agent ran Stage 5: supplemented all 5 stub files with pipeline outputs, created `onboarding.md` and `HANDOFF.md`, merged `(removed — ingest scratch)` into knowledge-base and operations files.
**Rationale:** Converts pipeline-generated content into a usable starting point for the SCLA team without overwriting the manual stubs.
**Owner:** source-of-truth-curator agent (pipeline)

## 2026-04-20 — MJML email template automation path decided
**Decision:** Kierra will use Claude to build an MJML template from 3 SCLA exemplars; hand to tech team (Sean/Shawn) for implementation. Unblocks Weekly News consistent cadence.
**Owner:** Kierra Woekel, Amy Westby
**Source:** Apr 20 Community Team Monday meeting notes

## 2026-04-20 — Community Google Drive as single source of truth + Claude KB pipeline
**Decision:** All team work goes into Community Google Drive. Kierra owns ingestion into Claude KB. Team pings Kierra in Slack when a doc is dropped.
**Owner:** Kierra Woekel
**Source:** Apr 20 Community Team Monday meeting notes

## 2026-04-13 — Team Projects tracker (Canva) as single source for action items
**Decision:** Team Projects tracker built by Kierra in Canva is the canonical home for all action items. Replaces Amy's personal OG Google Sheet for team-wide visibility.
**Owner:** Kierra Woekel
**Source:** Apr 13 Community Team Monday meeting notes

## 2026-04-06 — Claude Pro upgrade authorized
**Decision:** Team upgraded to Claude Pro (~$17/month) to unlock MCP calls and greater functionality. Intended to replace the Gemini-based Slack AI bot concept.
**Owner:** Amy Westby / Kierra Woekel (billing owner TBD)
**Source:** Apr 6 Community Team Monday meeting notes

## 2026-05-10 — SCLA-Profile redesigned as SCLA-native knowledge base
**Decision:** Migrated from generic template to SCLA-native structure. Renamed all `scla/` references to `scla/`. Separated programs, members, operations, partnerships into first-class directories.
**Rationale:** Generic template naming created confusion; SCLA-specific structure makes the knowledge base faster to navigate and easier for agents to target.
**Owner:** Kierra Woekel

## 2026-07-03 — Documented Early Career Boost lesson script & video style
**Decision:** Reverse-engineered the lesson script and video style from the live Early Career Boost track (app.thescla.org, read-only via the learn API) to enable HeyGen video production from course material. Added `scla/programs/early-career-boost-video-style.md` (findings + style patterns) and `templates/heygen-lesson-script.md` (reusable Style-B production template).
**Rationale:** Most lessons ship a drafted "video script" but only ~4 are produced to video (Wistia). Standardizing on the newer structured "Style B" spec (Video asset + Full video script with inline `[On screen:]`/`[Graphic:]` cues + shot list) lets us generate consistent scripts for HeyGen from any lesson's written material. Presenter voice is "Ann," a career coach.
**Owner:** Amy Westby
**Source:** Live platform observation, Early Career Boost

## 2026-07-04 — Video templates made program-agnostic; Wistia removed from workflow
**Decision:** De-hardwired the two HeyGen script templates (`templates/heygen-lesson-script.md`, `templates/heygen-narration-prompt.md`) so presenter/persona, target length, audience, and narrative arc are per-program fill-in parameters rather than fixed to Early Career Boost's "Ann the coach / 5–7 min / myth-bust arc." Style B structure and SCLA brand voice remain the only constants; Early Career Boost keeps its specifics in `programs/early-career-boost/video-style.md` as the worked example. Separately, removed Wistia as the mandated hosting/analytics layer across `projects/video-production/CLAUDE.md`, `status.md`, `qa-checklist.md`, and `batch-csv-template.md` — hosting/analytics platform is now `TODO: needs input`.
**Rationale:** Each program has different video length and presenter needs, so hard-wiring one program's assumptions into shared templates blocked reuse. SCLA is no longer standardizing on Wistia, so mandating it in the workflow docs no longer reflects reality; genericized to a platform-neutral "hosting platform" pending the decision. The observed fact that current lessons are hosted on Wistia (`sclc.wistia.com`) is left intact in `programs/early-career-boost/video-style.md` as a real observation, not a mandate.
**Owner:** Amy Westby (executed by Claude)
**Source:** Working session, 2026-07-04

## 2026-07-07 — SCLA video design system built; illustrated (HyperFrames) path is the default for lesson videos
**Decision:** Skipped the phased rollout from the "Scaling Lesson Videos Beyond the Avatar" proposal and built the full production system in one pass: (1) `projects/video-production/design-system/` — a HyperFrames project holding the SCLA video design spec (`frame.md`, tokens from `brand/visual-identity.md` adapted to the video frame), six reusable scene templates (`scla-title`, `scla-points`, `scla-steps`, `scla-quote`, `scla-stat`, `scla-outro`) as variable-driven sub-compositions, self-hosted Proxima Nova woff2 (400/700/900 from SCLA's Adobe kit), brand SVGs, and a 48s demo reel built from the approved "Better Decisions Come From Better Criteria" script (lint/validate/inspect clean). (2) Narration voice pinned: Kokoro `af_heart` @ 0.95 — local engine, zero per-render cost; auditioned against `af_nova`/`af_sky`/`am_adam` (samples in `design-system/voice-auditions/`). (3) Flow wired to scale: per-lesson build recipe in `design-system/CLAUDE.md`, tool routing updated in `projects/video-production/CLAUDE.md` (illustrated = default for concept lessons; HeyGen kept for translations/social/human-presence; Synthesia under re-evaluation), illustrated-video section added to `templates/qa-checklist.md`. Script-approval and human-QA gates unchanged.
**Rationale:** Team judged avatar output weak for the 18–24 audience and agreed with the proposal's case (brand-owned visuals, sound-off teaching, per-scene editability, no per-minute credits); launch urgency collapsed the pilot/phase plan into a single build. Voice runs local because the HeyGen API key currently returns 403 on every endpoint (no API permission on the space — also blocks `heygen-pipeline/`); upgrade path to HeyGen TTS documented in `design-system/CLAUDE.md`.
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-07; artifact "SCLA Video Scaling Proposal" (claude.ai/code/artifact/2f01aa45-998f-4094-be2a-95519496056d)

## 2026-07-08 — Illustrated-video formula revamped: animacy + illustration + statement/quote/numeral rules
**Decision:** Reworked the illustrated-lesson formula after review of the first at-scale build (`lessons/better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`) surfaced repeated failures. New **hard rules**, added to `design-system/frame.md` (normative) and enforced at the QA gate (`templates/qa-checklist.md`), threaded through the build recipe (`design-system/CLAUDE.md`) and the `/produce-video` orchestrator: (1) **No stagnant frame beyond ~2s** — every scene develops across its full duration; long beats split rather than park static text; title cards hold only for the opening line, never over ongoing narration. (2) **Reveal on the spoken cue** — enumerations appear as the narration says them, driven by word timings from `transcript.json` via `pointCues`/`stepCues`, not an even timer. (3) **Illustration over text** — the frame depicts what's being said (path/map, thinking figure, comparison, per-item icons); bespoke illustrated scenes are now the expectation for concrete narration, templates are the structural floor only. (4) **Statements aren't quotes** — added a 7th template `scla-statement.html` (bold, unattributed navy card) for program/SCLA theses; `scla-quote.html` repurposed to named-person quotes only (variables renamed `attribution`/`role` → `speaker`/`speakerRole`). (5) **Numerals & index** — scene index standardized to small lower-right on every template; a hero numeral is reserved for a genuine stat (`scla-stat`) or the spoken step (`scla-steps`), never deck position. Also added `stepCues` to `scla-steps` (mirrors `scla-points`), moved the scene index to lower-right on points/steps/quote, and rebuilt the demo reel (`design-system/index.html`, now 7 scenes / 56s) as the corrected living style guide.
**Rationale:** The template-assembly model was producing generic, static videos that ignored the narration — the Better-Decisions build sat ~20s on a title card while the audio listed items, cast two program theses as fake quotes, and rendered a bare "5" that read as a slide number. Encoding the fixes as normative rules + QA checks (not just per-video notes) makes the formula self-correcting for every future lesson. Templates unchanged in count-as-contract but reframed as a floor, not a finish. No video re-rendered in this pass (rules + templates only).
**Owner:** community@thescla.org (executed by Claude)
**Source:** Working session, 2026-07-08; user review of `better-decisions-come-from-better-criteria_early-career-boost_2026-07-06`

## 2026-07-13 — Pipeline v3: folder-state model, two-skill split, gates moved to hyperframe + MP4 review
**Decision:** Restructured the illustrated-lesson pipeline. (1) `/produce-video` split into two workhorse skills plus a ~20-line dispatcher: `/refine-scripts` (drains raw `.txt` at `lesson-scripts/<program-slug>/` root into `refined/`, one cold subagent per script + mandatory qa-facts pass) and `/render-lessons` (three explicit phases — BUILD drains `refined/` into HyperFrames workspaces, one cold subagent per video, ≤3/session; SHIP renders+verifies+files the MP4 on `ship <stem>`; PUBLISH uploads to Wistia on `publish <stem>`). Subagent-per-unit is deliberate: each build costs 150–300 tool calls and gets its own context + budget, so batch sessions can't context-bloat or hit the 500-call cap. (2) **The standing rule "script → render is a manual gate" is replaced, not removed:** script approval becomes async (`refined/` is an open review buffer; qa-facts + the preflight script-vs-transcript diff gate guard fidelity), and two blocking human checkpoints take its place — the HYPERFRAME GATE (human previews every hyperframe before any MP4 exists; no script→MP4 single-shot automation anywhere) and MP4 REVIEW (human watches every filed MP4 before Wistia). (3) State lives in the folder (root → `refined/` → workspace-at-gate → MP4-at-review → `rendered/`); `refinement-log.md` demoted from state machine to human-facing ledger. Migrated: 9 refined scripts → `refined/`, `mini-syllabus` → `rendered/`, 2 raw captures stay at root; `preflight.py locate_script` + `avatar-pipeline/config.json` updated for the new paths. (4) Snag-log rebuilt as a rolling self-improvement loop: sessions read ONLY the newest entry; unresolved items roll forward verbatim until fixed and a non-empty Open list must lead every close-out report (hook text updated, test 4/4); durable lessons are promoted into the owning doc, not accumulated in the log. (5) Notion retired as intake (banner on `notion-queue.md`); its remaining role (Wistia-link ledger, polling-routine fate) is deferred to a separate session. (6) Endpoints centralized: Wistia section added to `endpoints.md` (+ `connections.md` row, not connected); hardcoded `sclc.wistia.com` mentions across live docs replaced with pointers. Oversight brief folded into `render-qa/BUILD-LOG.md`.
**Rationale:** First post-refactor run (BUILD-LOG 2026-07-13) proved the deterministic core; the remaining risk is taste, which the owner keeps by reviewing the exact artifacts that carry it (hyperframe preview, filed MP4) instead of blocking on script text. Folder-state makes both skills idempotent queue-drains, immune to ledger staleness. Full automation to MP4 stays off until quality is consistently proven.
**Owner:** community@thescla.org (executed by Claude, Fable 5)
**Source:** Working session 2026-07-13 (owner directives on the oversight brief)

## 2026-07-27 — Motion contract v2: pacing becomes deterministic (owner "boring/slow" verdict on first five renders)
**Decision:** After the owner reviewed the five rendered hyperframe builds and judged them technically correct but boring — pace drags, missed illustration opportunities; explicitly no music and no captions — the illustrated-video system got a structural overhaul rather than per-video notes. (1) **Motion v2 in `design-system/frame.md`** (normative): entrances settle ≤1.2s; every scene ends with a cued closing beat; every scene except the outro exits (0.3s content slide-out at sceneDuration−0.35, furniture stays); compound cues ("focus follows the voice": new items dim settled siblings, the closing beat restores); the 2026-07-14/15 idle-keep-alive ban stands untouched. (2) **Pacing is now a deterministic gate**, not an aesthetic judgment: `preflight.py` check 6 fails any scene whose largest gap between visual events (entrance settle + compiled cues + closing beat) exceeds 4.5s (warn 3.5s), or whose duration exceeds 12.5s (title 6.5s, outro 8.5s). Background depth-drift no longer buys a pass — it defeats the pixel sampler, so pacing is graded on communicative beats only. (3) **All twelve templates re-choreographed** to the contract; two live defects fixed (scla-chips' dead subBeats mechanism; scla-statement's cue fallback firing uncued lines before cued siblings — now also a compiler count check, `lines`/`point1..4` vs `pointCues`). (4) **Icons become beats:** `iconCue` fires the draw when the narration names the thing; icon slots widened to `scla-points` (per-item), `scla-morph` (per-card), `scla-chips` (hero). (5) **Variety rule** in `/render-lessons`: max 2 consecutive scenes of one template, ≥5 distinct forms per lesson over ~90s, illustration-capable templates for concrete narration. (6) **Script style rule** in `/refine-scripts`: ~14-word declarative sentences, no long comma lists (they drop TTS to ~115 wpm). The five reviewed builds are re-authored to the new contract and stop at the hyperframe gate as always.
**Rationale:** Audit of the five builds + twelve templates showed narration at ~158 wpm against one visual event per 6–11s, scenes averaging 15–22s, 4–5 consecutive same-template runs (51–52% of runtime in one layout), six illustration-capable templates unused, and zero bespoke scenes — while the spec already demanded the opposite. The gap was enforcement: the only animacy check was pixel sampling, which decorative drift satisfies. Encoding pace as a compiled, gated budget makes the fix self-correcting for every future lesson, exactly as the 2026-07-08 revamp did for animacy rules. TTS voice/speed left at owner-pinned Oxana 0.95; raising to 1.0 offered separately as an owner listening decision.
**Owner:** community@thescla.org (executed by Claude, Fable 5)
**Source:** Working session 2026-07-27; owner review of the five 07-10/07-25 hyperframe renders
