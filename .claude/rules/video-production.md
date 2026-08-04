---
description: Always-true SCLA video-pipeline constraints — load for any work in the factory
paths: projects/video-production/**
---

# Video production — standing constraints

Each rule states the constraint and names the **mechanism** that enforces it, or
is honestly labelled a **convention** (a request, not a guarantee — see
`decisions/log.md` on why prose governance was deleted).

**Why a rule exists is not here.** It lives in `decisions/log.md`, cited as
`Why: log <date> "<title>"` — a grep target, not a heading anchor, so the
citation survives the log being re-titled or re-ordered. This file is auto-loaded
on every session that touches the factory, so it stays a checklist: claim,
mechanism, pointer. Incident narrative, calibration numbers and superseded
designs belong in the log entry. *(Split by audience 2026-07-31; `Why: log
2026-07-31 (rules refactor) "The video rules file splits by audience"`.)*

## Content fidelity

- **Never fabricate SCLA course content.** Work only from provided outlines and
  source material. *(Mechanisms: mandatory qa-facts pass at `/refine-scripts`;
  script-vs-transcript diff in `render-qa/src/preflight.py`; the brand
  re-materialize safeguard in `.devcontainer/devcontainer.json`. Why: log
  2026-07-27 "Cold pipeline subagents promoted to agent charters".)*
- **The banner is the program folder's name — always, no aliases.** A lesson's
  title-card `eyebrow` names the `lesson-scripts/<slug>/` folder its script lives
  in. A display name is legal only if it slugifies back to its own key.
  *(Mechanisms: `render-qa/src/tokens.py` `programs_problems()` → `preflight.py`
  check 7b in full AND `--static` mode; `render-qa/tests/test_programs.py` via
  `lint-refs.sh` check 11. Why: log 2026-07-29 "The banner is the program
  folder's name".)*
- **A lesson's part number is a filing convention, never on-screen copy.**
  `-pt1`/`-pt2` tell two halves of one lesson apart on disk and never reach the
  frame or the narration. *(Mechanisms: `check_copy.py` rule `part-reference`,
  graded on narration AND every on-frame string, workspace and script mode;
  `preflight.py`'s `title_card` strips the same suffix. Why: log 2026-07-29
  (owner review) "Eight defects from the career-map and visibility-actions
  cuts".)*
- **No FERPA/PII in any prompt sent to an AI tool.** *(Convention.)*
- **Brand facts come from `brand/visual-identity.md` and
  `brand/voice-and-tone.md`.** Never restate hex values in pipeline docs — they
  drift. *(Mechanism: `lint-refs.sh` check 6 flags stray legacy hex.)*
- **The narration voice is pinned** (Oxana, ID in
  `design-system/config/tokens.yml`). Do not audition, swap, or reference retired
  voices. *(Convention.)*

## The batch — gates, locks, resume

- **PILOT GATE — one human approval per batch, not per video.** A batch builds
  ONE pilot, stops for a human preview, and only on explicit approval do the rest
  run build → render → verify → publish unattended. A batch may never start
  without a passing pilot; a failing pilot stops the run. *(Convention at the
  pilot itself. Why: log 2026-07-28 "Video pipeline: per-video gate → pilot gate;
  batch cap deleted".)*
- **The guards that replace the per-video human eye** — every video, no
  exceptions: `preflight.py` exit 0 before render; `scripts/batch-precheck.sh`
  before render (authoritative preflight re-run, one snapshot per scene,
  deterministic low-ink flags, vision review of real pixels); `verify_render.py`
  exit 0 after (stream durations vs `#root data-duration` ±0.15s, exact
  1920×1080, 3 frames/scene); `check_presence.py` blank/stagnation detection; and
  a sampled vision review of `qa/frames/`. Any one failing **quarantines that
  video** — built, unpublished, logged — and the batch continues. *(Mechanisms:
  `scripts/batch-ship.sh` fails soft per video and never publishes a video that
  failed a guard; `batch-precheck.sh` exits 3 to quarantine pre-render. Why: log
  2026-07-28 "Video pipeline: per-video gate → pilot gate".)*
- **SHIP is one uninterrupted pass** — render, verify, file to
  `renders-mp4/<program-slug>/`, upload to Wistia. No second human review before
  publish. *(Convention. Why: log 2026-07-22 "MP4 REVIEW / PUBLISH human gate
  removed".)*
- **A published video is recorded before the next one starts.** The full stem +
  Wistia URL land in `lesson-scripts/published.tsv` (the machine resume key) and
  the human-facing `refinement-log.md` row, committed in the same pass — a commit
  failure quarantines the video with its URL and keeps the MP4. A stem is done if
  and only if it has a `published.tsv` row; anything in `rendered/` without one
  is flagged **STRANDED**. Publish runs only against `qa/VERIFIED` and refuses
  stems already published. *(Mechanisms: `scripts/batch-ship.sh` guards. Read the
  queue with `scripts/batch-status.sh`, or open the generated
  `projects/video-production/PIPELINE-STATUS.md`, regenerated on every quarantine
  and publish. Why: log 2026-07-28 "Video batch: certification protocol + machine
  resume key"; log 2026-07-31 (status doc) "The queue read becomes a document".)*
- **One render at a time, machine-wide; builds run up to 3-wide.** Authoring and
  TTS are network-bound and overlap cleanly; a render is CPU-bound and two on a
  4-core box thrash. *(Mechanism: `batch-ship.sh` takes
  `renders-hyperframes/.render.lock` via `mkdir` for the whole render phase and
  exits 2 if another holds it. Why: log 2026-07-29 (owner review) "Eight
  defects…", closing section.)*

## Naming and filing

- **A working artifact carries NO date; only a delivered MP4 does.** A lesson's
  identity is `<title>_<program>` — the **base** — and that names the raw script,
  the `refined/` script, the build workspace and the `rendered/` script. It never
  changes, which is what makes it a lock: `mkdir renders-hyperframes/<base>`
  succeeds exactly once, so concurrent build subagents cannot collide. Only the
  delivered MP4 gains a date (`<base>_<render-date>.mp4`). "When was this last
  acted on" is mtime. *(Mechanisms: `render-qa/src/stem.py` is the sole owner;
  `preflight.py` check 12 fails a dated workspace name; `batch-ship.sh` files the
  MP4 via `stem.py delivered`. Pinned by `render-qa/tests/test_stem.py`. Why: log
  2026-07-29 "Working artifacts lose their date suffix; the name becomes the
  lock".)*
- **Never archive automatically.** Retiring a workspace to
  `renders-hyperframes/_archive/` is a human-only call. A shipped video's
  workspace is pruned in place (`scripts/archive-lesson.sh <stem> --in-place`)
  and stays put, editable. *(Convention, stated in
  `projects/video-production/CLAUDE.md`.)*

## Copy and narration

- **Standing owner preferences are gated, not remembered.** Headings
  (`heading`/`statement`/`title`) are **Title Case with no terminal period**;
  body copy stays sentence case. Every spoken list of ≥3 items takes **"and"/"or"
  before the final item**. A list slot with **exactly one item is a defect**. Max
  **2 consecutive** scenes on one template family, **≥6 distinct content forms**
  per lesson ≥90s (≥7 at ≥150s), **no form above 40%** of content seconds.
  Enforced at authoring time: a builder authors only `scenes.json`;
  `build_index.py` compiles `index.html`. On the freeform lane the two rules
  that are about content FORM rather than templates — **one-item-list** and
  **one-card** — are graded on element structure instead of template slots, so
  they survive the compiler's retirement. *(Mechanisms: `check_copy.py` +
  `check_variety.py` via `preflight.py` (hard block), `preflight.py --static`
  (plan stage), and `scripts/hyperframe-guard.sh` (`PostToolUse` hook on
  scenes.json / index.html writes); `render-qa/src/check_forms.py` for
  one-item-list / one-card on the freeform lane, run by `preflight.py`.
  Thresholds pinned by `render-qa/tests/test_variety.py`, freeform forms by
  `render-qa/tests/test_freeform.py`. Why: log 2026-07-28 "Owner review: stem
  dates become mechanical, and four standing preferences become gates".)*
- **One thought per scene; no thought split across scenes.** A content scene
  carries at least `MIN_SCENE_SEC` (4.5s). A scene opening with a bare
  coordinating conjunction is the back half of the previous sentence and must be
  merged. A spoken list lives on ONE scene. *(Mechanism:
  `render-qa/src/check_continuity.py`, run by `preflight.py` and `--static`;
  pinned by `render-qa/tests/test_gates.py`. Why: log 2026-07-28 "Owner
  review…".)*
- **The conjunction rule is graded on the WHOLE narration, not per scene.**
  Scoping it per scene silently disables it — a seven-item list split 3/2/2
  leaves no run reaching the ≥3 threshold. *(Mechanism: `check_copy.py`,
  joined-stream enumeration. Why: log 2026-07-29 "The gates the
  `better-decisions` rejection exposed: scope, sampling, severity".)*
- **The conjunction rule is graded on the SCRIPT too, at refine time.** A
  render-stage gate can only report it after a video exists, when the fix costs a
  re-synthesis and a re-render. **Reports, does not block** — a library sweep
  found 16/32 refined scripts flagged and a minority are rhetoric or definitions,
  not lists. *(Mechanism: `check_copy.py` script mode — pass a `.txt` instead of
  a workspace. Per STD-38: non-blocking at first, so it teaches instead of nags.
  Why: log 2026-07-29 "The gates the `better-decisions` rejection exposed".)*
- **A conjunction is added by joining the list, never by bolting the word onto a
  fragment.** "The right job. The right major. Or the right path." satisfies the
  rule and sounds wrong. The fix is one sentence. Question lists are exempt —
  they are *meant* to rise — so the terminal mark is the discriminator, and only
  the LAST fragment of a run can dangle. *(Mechanism: `check_copy.py` rule (c),
  run by `preflight.py` and in script mode at `/refine-scripts`. Why: log
  2026-07-29 "A gate must be able to fail. Three that structurally could not.")*
- **The narration wav carries its own trailing hold.** Every scene gets real
  silence after it, including the last; video outliving audio proves nothing, the
  release has to be in the file. A lesson's ending needs longer to land than a
  scene boundary does — `FINAL_HOLD` is **1.8s**. *(Mechanisms:
  `synth_narration.py` (final clip is not tail-trimmed and gets `FINAL_HOLD`);
  `check_boundaries.py` rules `audio-tail-clipped` + `final-hold` against
  `MIN_FINAL_HOLD`; `test_gates.py` asserts the producer clears its own floor.
  Why: log 2026-07-29 "The gates the `better-decisions` rejection exposed".)*

## Layout and geometry

- **Copy must fit the box the template gives it.** Slot capacity is measured in
  the real vendored font, not estimated. A template declares each constrained
  slot's `maxLines` in its own variable schema, beside the CSS that creates the
  constraint. *(Mechanisms: `check_capacity.py` + `textmetrics.py` against
  committed `design-system/assets/fonts/metrics.json`. Why: log 2026-07-29 "The
  gates the `better-decisions` rejection exposed".)*
- **No text may land on other text, and the gate does not depend on a browser to
  know it.** *Given the wrapped line count, does this box intersect anything?* is
  answerable from template CSS plus real font metrics, with no browser. Two
  corollaries: a template **declares** which slot each element renders
  (`data-slot`) and which slot it disappears with (`data-present-if`) rather than
  the gate guessing from JS; and a run-time-created line carries an **empty
  geometry prototype** in the HTML. *(Mechanisms: `boxmodel.py` +
  `check_geometry.py` via `preflight.py` (full AND `--static`); a scene where the
  model resolves nothing fails as `nothing-graded`. Pinned by `test_gates.py`.
  Why: log 2026-07-29 "A gate must be able to fail".)*
- **The geometry gate can see every box on the frame.** Chips, condition chips,
  statement lines and morph notes are created at run time and need declared
  prototypes, or the gate grades zero of them and returns PASS. *(Mechanisms:
  `boxmodel.py` `data-geometry-repeat` prototypes — structured ones carrying
  `data-geometry-text` — plus `flex-wrap` row packing, border-box measurement of
  padded pills, and `data-geometry-alt-if` for geometry a template applies
  conditionally in JS. Why: log 2026-07-29 (owner review) "Eight defects…".)*
- **The minimum text size is a real floor, not the smallest size in use.** Body
  floor is **40px** (~1/27 of frame height, which is what survives phone
  viewing). `design-system/config/tokens.yml` is the single source, so the number
  moves in one place. *(Mechanisms: `tokens.yml` `typography.min-size` →
  `render-qa/src/tokens.py` → `check_text.py`; `test_gates.py` asserts no body
  rule sits *at* the floor. Why: log 2026-07-29 "A gate must be able to fail";
  originally log 2026-07-27 "Minimum on-frame text size".)*
- **Even spacing is a property of the SLOTS, not of the copy in them.** Size
  slots for the widest legal card the schema permits and let a short card sit
  high in its slot. *(Mechanism: `check_geometry.py` rule `card-gutter` against
  `tokens.yml` `spacing.card-gutter`, graded on LAYOUT boxes — the one rule in
  that gate that is. Deliberately narrow: absolutely positioned + fully bordered
  + text-bearing + horizontally overlapping. Fixture: `test_gates.py`. Why: log
  2026-07-29 (owner review) "Eight defects…".)*
- **No icons beside bullet rows or cards — only ONE hero illustration per
  frame.** The plural `icons` slot is deleted, not policed. The singular hero
  `icon` on statement/chips/steps/condition is untouched. *(Mechanisms: the slot
  is gone from both templates; `check_slots.py` rule `banned-row-icons` fails any
  scene still authoring it, including a stale workspace whose variable the
  compiler would otherwise drop in silence. Fixture: `test_gates.py`. Why: log
  2026-07-29 (owner review) "Eight defects…".)*
- **An icon name the template does not have draws nothing, and says nothing.**
  `ICONS[name]` returning undefined is a typo the browser cannot report, and the
  per-template libraries drift. *(Mechanism: `check_slots.py` rule
  `unknown-icon`, reading the library it is actually calling, run by
  `preflight.py` in full and `--static` mode.)*
- **A one-card comparison is the one-item list in the form the list rules could
  not see.** `scla-morph`'s two options are SCALAR slots, so `one-item-list` is
  structurally blind to it. *(Mechanism: `check_variety.py` rule `one-card`,
  which also fails a `winner` naming a card that was never filled. Fixtures:
  `test_variety.py`. Why: log 2026-07-29 (owner review) "Eight defects…".)*
- **The on-frame scene badge is the frame's real position.** `sceneIndex` is how
  the owner names a frame when reviewing a cut, so a duplicated number makes a
  whole round of feedback unresolvable against the plan. *(Mechanism:
  `check_slots.py` rule `scene-index-badge`. Why: log 2026-07-29 (owner review)
  "Eight defects…".)*
- **`line-height: normal` is measured in the real vendored font, never assumed.**
  Proxima Nova resolves to **1.404 / 1.447 / 1.477** by weight; assuming 1.2
  models every unset block ~20% short. *(Mechanisms:
  `textmetrics.normal_line_height()` → `boxmodel.typeface()`, generated into
  `design-system/assets/fonts/metrics.json`; pinned by `test_variety.py`, which
  fails if the key is regenerated away. Why: log 2026-07-29 (owner review) "Eight
  defects…".)*
- **A body statement belongs under the heading, not at the foot of the frame.**
  `scla-statement` and `scla-condition` have a `sub` slot; `scla-chips` and
  `scla-points` sub-beats sit directly under the heading. *(Convention on WHICH
  slot an author picks; the geometry gate enforces that whatever they pick fits.
  Why: log 2026-07-29 (owner review) "Eight defects…".)*
- **The layout inspector runs at every scene, and its verdict is not discarded.**
  Overlap is fatal whatever severity upstream assigns it; transition seams are
  sampled because static sampling misses collisions that only appear there.
  *(Mechanism: `check_layout.py`, run by `preflight.py`. Why: log 2026-07-29 "The
  gates the `better-decisions` rejection exposed".)*

## Motion

- **Settled content never re-animates in place, and the motion no longer exists
  to be chosen.** No wobble, drift, ripple, pulse or re-mark of text, chips,
  rows, nodes, numbers, CTAs or the living-icon hero once it has entered. The
  capability was removed rather than policed. A pixel-static hold is an AUTHORING
  defect with exactly one fix: re-author the scene. Deliberate exceptions are
  declared inline with `/* motion-allow: <reason> */`. *(Mechanism:
  `render-qa/src/check_motion.py` via `preflight.py` (full AND `--static`) and
  `design-system/`'s `npm run check` over the demo reel; it follows a selector
  through a helper's call sites. Fixtures: `render-qa/tests/test_motion.py`,
  `render-qa/tests/test_mutations.py`. Why: log 2026-07-15 "In-place keep-alive
  motion stays banned" — the repo's most-violated rule.)*

## How a gate must behave

- **A measurement is never delegated to the human preview.** A deferral must name
  the instrument that answers the question, and "the human" is only a legal
  answer for questions a human can actually answer. *(Mechanism:
  `render-qa/src/check_diversity.py` rule `static-span`, run pre-render by
  `scripts/batch-precheck.sh` over a uniform ~1.25s snapshot grid; same rule and
  constants as `check_presence`, which stays authoritative post-render.
  `grid-too-sparse` fails a grid too coarse to see a `STAGNANT_FAIL` freeze.
  `TIME_EPS = 0.02` absorbs the 1/100s filename-timestamp slop, and
  `batch-precheck.sh` rounds its emitted grid to match. Pinned by
  `render-qa/tests/test_diversity.py`. Why: log 2026-07-31 (freeform gates) "A
  measurement is never delegated to the human preview".)*
- **Monotony stays with the human, and is reported rather than blocked on.** The
  twin threshold is not calibrated against the owner's reference video, and a
  gate that blocks on an unpinned taste number is one that gets switched off. Per
  STD-38 it teaches first; pin it against a reference build before arming it.
  *(Mechanism: `check_diversity.py` rule `twin-beats`, advisory, printed by
  `verify_render.py`'s `monotony` section; `test_diversity.py` asserts it fires
  AND that it stays out of the blocking list. Why: log 2026-07-31 (freeform
  gates).)*
- **Narration word timings have one loader, and a gate that cannot see them says
  so.** *(Mechanisms: `hfp_common.load_words()` reads all three shapes — the two
  flat word files and the freeform per-beat one (`audio_meta.json`), offsetting
  each clip's words by its `timing.json` `audio_start`; `check_presence` and
  `check_diversity` both call it; an absent transcript emits a `no-word-timings`
  warning instead of passing for rigour. Pinned by `test_diversity.py`. Why: log
  2026-07-31 (freeform gates).)*
- **tokens.yml is LOADED, not quoted, and a number nobody reads is a red test.**
  Normative numbers (type floors, frame-padding, safe-area, footer-reserve,
  content-bottom) are parsed from the spec and read by a gate — never hand-copied
  into Python under a "keep in sync" comment. *(Mechanisms:
  `render-qa/src/tokens.py` → `check_text.py` (`min_size`) and
  `check_geometry.py` (all four spacing tokens, full AND `--static`);
  `render-qa/tests/test_tokens_coverage.py` fails if any accessor loses its
  non-test consumer. Why: log 2026-07-29 "One project shape, and frame.md split
  into the numbers and the prose".)*
- **A workspace's copied `tokens.yml` is graded against the spec, because the
  gates read the COPY.** Raising a token in `design-system/config/tokens.yml`
  does not reach workspaces already on disk. *(Mechanism: `preflight.py`'s
  `composition_freshness` section diffs the workspace's normative tokens against
  the spec and hard-fails on drift. Why: log 2026-07-29 "One project shape…".)*
- **Template defects are caught at the template, once — not once per video.**
  `npm run check` in `design-system/` runs the framework's own pass PLUS
  `check_text.py` and `check_layout.py` over the demo reel, which carries one
  scene per template. Intentional layering is *stated*
  (`data-layout-allow-overlap`), never tolerated by a loosened gate. *(Mechanism:
  `design-system/package.json` `check` script, required after any composition
  edit. Why: log 2026-07-29 "A gate must be able to fail".)*
- **A hook that crashes is a gate that is off.** A guard that still produces
  output reads as alive while grading nothing. *(Mechanism:
  `render-qa/tests/test_guard_contract.py` resolves the guard's own `RQ` path and
  asserts both entry points exist on disk, so a move breaks a test instead of a
  build. Why: log 2026-07-29 "Rejected: a telemetry/ledger … Adopted: prove
  every gate fires".)*
- **The render CLI is pinned, and the pin is checked.** An unpinned `npx
  hyperframes` lets a batch start on one version and finish on another, and lets
  a gate's verdict change because upstream shipped. Staleness is cured by bumping
  deliberately and validating, never by dropping the pin. *(Mechanism: single pin
  in `design-system/package.json`, read by `check_layout.py`. Why: log 2026-07-29
  "The gates the `better-decisions` rejection exposed".)*
- **The test suite runs in CI.** `run_tests.py` executes its own cases AND every
  sibling `test_*.py`. *(Mechanism: `scripts/lint-refs.sh` check 11. Why: log
  2026-07-29 "The gates the `better-decisions` rejection exposed".)*

## Close-out

- **Close the books after a render.** Any session that ran a HyperFrames render
  prepends a snag-log retro entry per `render-qa/logs/snag-log.md` header rules
  before ending. *(Mechanism: PostToolUse hook in `.claude/settings.json`.)*
