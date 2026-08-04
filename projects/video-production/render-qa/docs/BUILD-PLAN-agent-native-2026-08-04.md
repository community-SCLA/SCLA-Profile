# BUILD PLAN — agent-native adoption, execution order

**Date:** 2026-08-04 · **Status:** approved for execution through Phase 2;
Phases 3–4 have hard human stops. Phase 3 was scaled down from a 3-lesson A/B
to a single freeform pilot on 2026-08-04 — the owner is already confident in
the agent-native direction · **Audience:** a fresh session with no memory of
the conversation that produced this.

**This plan executes** `render-qa/docs/PROPOSAL-agent-native-adoption-2026-08-04.md`
(the reasoning and all measurements), plus the two surviving pieces of
`render-qa/docs/Pipeline-Build-Proposal` (its B1 write fence and AGENTS.md
purge). Evidence base: `experiments/agent-native-m2/PROVENANCE.md` and
`render-qa/docs/HANDOFF-agent-native-verdict-2026-07-30.md`. When this plan and
the proposal disagree on a detail, the proposal wins — it carries the
measurements.

---

## Ground rules for the executing session

1. **Nothing here touches the shipping path until Phase 4.** Phases 1–2 are
   strictly additive; the 13 mid-career workspaces and the template pipeline
   must keep working after every commit. If a step forces a choice between
   additive and breaking, stop and report.
2. **One step = one commit, CI-green.** After every step run
   `bash scripts/lint-refs.sh` (the repo's only lint entry) and
   `python3 projects/video-production/render-qa/tests/run_tests.py`. Commit
   before starting the next step so an interrupted session strands nothing.
3. **A gate change is not done until it has been seen to FAIL.** Every step's
   done-condition is a firing test (a planted defect that turns the gate red),
   per the repo's `test_firing_coverage` discipline. A PASS on a re-pointed
   gate proves nothing — that is the `nothing-graded` failure mode this whole
   plan exists to close.
4. **Keep `check-enforcement.py` green.** `.claude/rules/video-production.md`
   states a mechanism for every rule and `lint-refs.sh` check 10 audits those
   claims. When a step moves or re-points a mechanism, update the rule's
   mechanism line in the same commit.
5. **Do not build:** the stress reel, the deterministic scene planner
   (`plan_scenes.py`), the cue-resolution gate, or any DOM-rect runtime probe.
   The first three double down on the template path this plan retires. The
   probe is blocked and unnecessary — and its prototype once produced 1,760
   plausible findings from a mis-served page (proposal §6); do not resurrect it
   without that self-test.
6. **Tick the ledger** at the bottom of this file as each step lands (edit this
   file, include it in the step's commit). That is the resume key for the next
   session.

---

## Phase 1 — Make the gates see template-free builds (additive)

### Step 1.1 — Copy gates get a beat source that is not the compiler

**Problem:** eight checkers reach a build through `hfp_common.parse_scenes()`,
which reads `data-narration` / `data-variable-values` — private attributes of
`build_index.py`. On the agent-native build they find 0 narration beats, and
`check_copy.py` prints PASS having graded nothing (proposal §2).

**Do:**
- Teach `render-qa/src/hfp_common.py` to read an alternate beat manifest when
  `data-narration` is absent: `audio_request.json` → `lines` (already the audio
  engine's input contract; see `experiments/agent-native-m2/audio_request.json`
  for the live shape), with per-beat timing from `timing.json`.
- Re-point `check_copy.py` and `check_continuity.py` to consume it.

**Done when:** a firing test in `render-qa/tests/` plants violations (a
missing "and" before a list's final item, a heading with a terminal period, a
split thought) in an agent-native-shaped fixture and asserts both checkers
**FAIL**. Then run the re-pointed `check_copy` once on the real
`experiments/agent-native-m2/` build and **record the result in the ledger
below either way** — that narration has never been graded; a clean result is a
finding and so is a dirty one.

### Step 1.2 — `check_motion` discovery fix

**Problem:** `compositions()` globs `scla-*.html`, so agent-authored files are
invisible to the most-violated rule's enforcer. Measured: renamed copies grade
26 tweens correctly (HANDOFF, quoted in proposal §5 step 2).

**Do:** widen the glob to all composition HTML. Then replace the `DECORATIVE`
substring allow-list (it encodes template naming — `ghost`, `ring`, `-bg`)
with the mechanism the motion rules already prefer: an explicit inline
`/* motion-allow: <reason> */` declaration, never name-matching.

**Done when:** a hand-planted `repeat: -1` tween in a copy of the agent-native
`map.html` makes the checker FAIL, and an existing template build still passes.

### Step 1.3 — Rehome the three orphaned owner rules

These rules have a mechanism today that dies with the template modules
(proposal §5 step 3). Each must have a template-independent home **before**
Phase 4 may run:

1. **`one-item-list` / `one-card`** (now in `check_variety.py`) — "a list slot
   with exactly one item is a defect." Re-express against the Step 1.1 beat
   manifest / composition DOM rather than template slots.
2. **`placeholder-slot`** (now in `check_slots.py`) — the `[[…]]` / `…` / TODO
   / TBD / xxx scan. This is a fabrication-ban guard, not template mechanics;
   re-point it at composition HTML + the beat manifest.
3. **Plan-stage fit** (now in `check_capacity.py`) — fail a too-long string
   while the fix is still a text edit. Template font-metrics don't apply to
   freeform HTML; implement as a conservative character/line budget on the
   beat manifest, advisory-first per STD-38, and note the runtime ink-band gate
   (Step 1.4) as the hard backstop.

**Done when:** each rule has a firing test on an agent-native-shaped fixture,
and the rules file's mechanism lines are updated.

### Step 1.4 — Land the ink-band gate

The pixel-truth geometry gate for freeform HTML: "is there ink where there
must not be." Already built and validated (proposal §5 step 4 — clean passes
on 21 real stills, three planted defects all fire, rules discriminate).

**Do:**
- Promote `experiments/agent-native-m2/spikes/ink_bands.py` →
  `render-qa/src/ink_bands.py`.
- Move the brandline chrome keep-out region into
  `design-system/config/tokens.yml` as a **declared** region loaded via
  `render-qa/src/tokens.py` — never a CLI flag, never a loosened threshold.
- Fixture into `render-qa/tests/`; wire the call into `preflight.py`.
- Check whether `test_firing_coverage.py` requires every `src/` checker to
  have a firing test — if so, same commit.

**Done when:** the 21 clean stills pass; planted ink at y=1000, x=20, and x=80
each FAIL (the three cases from the validation table); `lint-refs.sh` green.

### Step 1.5 — Fix the four silent coverage collapses

All four "survive" the migration but quietly inspect far less on a freeform
build (proposal §5 step 5):

| Module | Collapse | Fix |
|---|---|---|
| `check_layout.py` | `scene_times()` samples per composition clip: 27 → 3 samples on a longer video | sample per **beat** from `timing.json` |
| `verify_render.py` | 3 frames/scene → 81 → 9 stills for 200s | frames per beat; leave container-truth checks and the `qa/VERIFIED` marker untouched |
| `check_presence.py` | no `narration.words.json` → `words = []` → every ≥3s static run gradeable regardless of speech | adapter for `audio_meta.json` word timestamps (note: `hfp_common.load_words()` may already read the per-beat shape — check before writing a second loader; one loader only) |
| `check_boundaries.py` | exits 2 wanting one flat `narration.wav`; agent-native has 24 clip wavs | per-clip adapter; **`FINAL_HOLD = 1.8` moves with it** or the ending floor the owner rejected twice goes unenforced |

**Done when:** each has a firing test at freeform-shaped input, and the
template path's behavior is unchanged (existing tests still green).

---

## Phase 2 — The two guardrails kept from the 07-31 proposal

### Step 2.1 — The write fence

**Problem:** `.claude/settings.json` grants Write/Edit with no path
restriction; the only hook exits 0 for anything outside a workspace — and the
agent-native experiment demonstrated the guard is location-shaped and can be
routed around (PROVENANCE §2).

**Do:** a `PreToolUse` hook that hard-blocks any Write/Edit/Bash-mediated
write to `design-system/`, `renders-hyperframes/_run/`, `render-qa/src/`,
`scripts/`, `.claude/`, and `design-system/config/tokens.yml` during build
sessions. Template/system work happens in a deliberately flagged session (an
explicit env var the orchestrator sets; a build subagent never sets it).
Include hook tests per `test_guard_contract.py`'s discipline — a hook that
crashes is a gate that is off.

**Done when:** in an unflagged session a write to `design-system/` is blocked
(observed, not assumed), a write to a workspace's own `scenes.json` /
composition files still succeeds, and the flagged session type passes.

### Step 2.2 — AGENTS.md purge

**Do:** `batch-prepare.sh` deletes the vendor `AGENTS.md` in the same pass
that already neutralizes the vendor CLAUDE.md; `git rm` the committed copies
in existing workspaces; add a `lint-refs.sh`-visible assertion (or preflight
section) that no workspace contains an `AGENTS.md`.

**Done when:** zero `AGENTS.md` under `renders-hyperframes/` in the index, and
a freshly prepared workspace has none.

---

## Phase 3 — One freeform pilot ⛔ ends at a human gate

**Precondition:** every Phase 1 + 2 ledger box ticked.

**Scope note:** this was a 3-lesson A/B against the template path. Cut to a
single build on the owner's call (2026-08-04) — the direction is already
decided, so this phase exists only to put real pixels in front of the owner
before Phase 4 deletes code, not to re-litigate the choice. No template twin:
the template path's output is already shipping and known.

**Do:** take 1 lesson from the queue top (`bash scripts/batch-status.sh`) and
build it agent-native from its refined script. Freeform builds follow the two
locked defaults (proposal §7): they live under `renders-hyperframes/<base>`
and take the `mkdir` build lock (freeform is invoked explicitly — `--freeform`
— and is never the AUTO-BATCH default); the stem contract from `stem.py`
applies unchanged. Run the re-pointed gates on it and record any that FAIL in
the ledger — a clean sweep needs one line, not a per-gate table.

**Stop:** present the MP4 at the pilot gate. **Do not proceed to Phase 4 in the
same session or without an explicit written owner verdict.** Per the
certification protocol, every owner note on the build becomes a new checker
rule or is consciously declined — never a verbal preference.

---

## Phase 4 — Retirement ⛔ requires explicit owner go-ahead

**Preconditions:** the Phase 3 pilot cleared the owner gate; owner has said "go"
on retirement specifically; the mid-career batch has drained (no live
workspace still depends on the template path — check `batch-status.sh` and
`published.tsv`).

**Do:** one commit, all of it or CI goes red — the checklist is HANDOFF §5
Test D. Scope measured in proposal §4: `boxmodel.py`, `check_capacity.py`,
`check_slots.py`, `check_variety.py`, `build_index.py`,
`instance_templates.py`, the `design-system/` template set, plus the 13
enforcement-claim updates and the 10 affected test files. Disposition is
**deletion, not `_archive/`** — git history is the archive
(`.claude/rules/repo-hygiene.md`). Update `.claude/rules/video-production.md`
mechanism lines and `projects/video-production/CLAUDE.md` routing in the same
commit.

---

## Ledger — tick as landed, one commit each

- [x] 1.1 beat-source adapter + copy/continuity re-point + firing test
      — `check_copy` verdict on the real agent-native narration: **24 beats
      graded (was 0) and 70 on-frame strings extracted. The narration itself is
      CLEAN** — conjunction, retired-name and part-reference all pass on the
      real 24-beat manifest, so the owner-preference rules had nothing to catch
      there. **One finding, and it is a real one: `no-headings-declared`.** The
      experiment authored zero `<h1>`–`<h3>` and zero `data-role="heading"`, so
      Title Case and heading-terminal-period graded 0 of 70 strings —
      "Mid-Career Momentum" is plainly a heading and the gate could not know it.
      The coverage hole is in the BUILD, not the gate, and the gate now says so
      instead of printing PASS. Phase 3's pilot must declare its headings.
- [x] 1.2 `check_motion` glob + `motion-allow` replaces `DECORATIVE` list
      — glob widened in `d3fab3c`; the nine-substring allow-list is now DELETED.
      33 decorative tweens across 11 templates were exempt by NAME and now
      declare themselves; `design-system` still passes (200 tweens graded).
      **Finding:** removing name-matching immediately caught one real case —
      the agent-native reference build's `#bg-glow` was exempt purely because
      its id contains `bg-`, and had declared nothing. Left unfixed on purpose:
      `experiments/` is evidence, and Phase 3's pilot must declare its own
      ambient motion. New rule: a helper-routed tween declares at the CALL
      SITE, because an allow in the helper body exempts every caller — the
      `drift()` laundering vector wearing a different hat.
- [x] 1.3a `one-item-list` / `one-card` rehomed — new `src/check_forms.py`,
      graded on ELEMENT STRUCTURE (`<ul>`/`<ol>` nesting, plus declared
      `data-role="list"` / `"compare"` for shapes HTML has no tag for). Not
      folded into `check_variety.py`: that file is on Phase 4's deletion list,
      so a rule rehomed there would die with it. Wired into `preflight.py` as
      its own `forms` section — the freeform `variety` skip previously handed
      these to the human preview, which is the deferral the rules file forbids.
      **Stated limit, printed on every run:** a build that draws lists as bare
      divs and declares nothing is graded on nothing. The real agent-native
      build is exactly that case, and says so instead of printing a bare PASS.
- [x] 1.3b `placeholder-slot` rehomed — the on-frame half landed in `d3fab3c`
      (`check_copy.placeholder_problems` over `onframe_strings`); this step
      added the half the plan also asked for and that was still missing, the
      BEAT MANIFEST. A marker in narration is worse than one on frame — it gets
      spoken, and costs a re-synthesis once the wavs exist. `check_slots.py`
      only ever saw compiled template slots, so the spoken half was ungraded on
      this lane entirely. An ellipsis is punctuation in speech and deliberately
      does NOT transfer from the on-frame rule, where a slot whose whole value
      is "…" is a defect.
- [x] 1.3c plan-stage fit rehomed (advisory) — new `src/check_fit.py`.
      **Deviation from the plan's wording, stated:** the plan said "a
      conservative character/line budget on the beat manifest". Narration never
      lands in a box, so a fit budget on it would grade the wrong artifact; the
      copy that must fit is the on-frame string set, available at the same
      moment (`preflight --static`, before render). The proposal's own wording —
      "fail a too-long string" — is what is implemented, and the proposal wins
      on details. Also kept the half of `check_capacity` that was actually
      valuable: measurement in the REAL vendored font via `textmetrics.py`
      (not on Phase 4's deletion list), rather than a character estimate. The
      budget is the content area at the MINIMUM legal type size, so a finding
      is a geometric fact — every legal size is larger. Advisory per STD-38 and
      genuinely not OR-ed into preflight's `failed`; the hard backstop is the
      ink gate. First heading threshold (3 lines at the floor, ~240 chars) was
      a bound no real heading could reach — a rule that could not fire dressed
      as a rule — and was corrected to "cannot be one line at any legal size".
- [x] 1.4 ink-band gate in `src/` + tokens region + fixtures + preflight wiring
      — landed whole in `d3fab3c` and verified against this step's own
      done-condition rather than assumed: promoted to `src/check_ink.py`, the
      brandline keep-out DECLARED in `tokens.yml` `chrome-regions` and loaded
      via `tokens.chrome_regions()` (never a CLI flag, never a loosened
      threshold), fixtures in `tests/test_ink.py`, and wired into `preflight.py`
      as `check_freeform_ink` over one snapshot still per beat. All three
      planted defects fire and DISCRIMINATE (x=80 fires padding and NOT
      safe-area); `test_firing_coverage` carries the three rules. The gate
      FAILS on missing/thin snapshots rather than passing — nothing-graded is
      never a pass. The "21 clean stills" half of the done-condition is
      historical evidence (HANDOFF §5 A3): renders are gitignored, so the
      stills are not in the repo and Phase 3's pilot is what re-exercises it on
      fresh pixels.
- [x] 1.5a `check_layout` per-beat sampling — code landed in `d3fab3c` via the
      shared `hfp_common.sample_units` grid; this step added the fixtures it
      had none of. Both consumers are declared SLOW in `test_firing_coverage`
      (browser / rendered MP4), which is precisely why the grid they delegate
      to has to be pinned in-process. 24 beats over 3 act-clips now samples 24
      midpoints, each inside its own beat; the template path still samples per
      clip.
- [x] 1.5b `verify_render` per-beat stills — same grid; 3-per-unit now yields
      72 stills where per-clip gave 9. **Defect found while writing the test:**
      `sample_units` fell back to the CLIPS when a freeform build had no usable
      beat timing — which is the 27 → 3 collapse restored silently, on exactly
      the builds not yet timed. It now returns an EMPTY grid there, and both
      callers already treat empty as ungradeable (`check_layout` exits 2,
      `verify_render` fails on `not units`). A build with no beat manifest at
      all still keeps the clips: nothing there claims to be freeform.
- [x] 1.5c `check_presence` word-timestamp adapter — landed in `d3fab3c` and
      already pinned: `hfp_common.load_words()` is the ONE loader (the plan
      warned against writing a second), reading all three shapes and offsetting
      each freeform clip's words by its `timing.json` `audio_start`.
      `test_diversity.py` pins the per-beat offset case; `check_presence` and
      `check_diversity` both call it.
- [x] 1.5d `check_boundaries` per-clip adapter + `FINAL_HOLD` —
      `check_freeform()` grades the same rules with the same rule ids from
      `audio_request.json` + `audio_meta.json` + `timing.json`, and preflight no
      longer skips boundaries on this lane (still skipped under `--static`,
      where the wavs do not exist yet). **Finding, and it is the one the plan
      predicted:** the agent-native reference build FAILS `audio-tail-clipped`.
      Its final clip's wav holds **0.261s** of real audio past the last word
      against a 1.5s floor (the producer gives 1.8s). The video does hold 2.06s,
      which is exactly the defence the rules file already rejects — "video
      outliving audio proves nothing, the release has to be in the file." That
      is the ending the owner rejected twice, and it was shipping ungraded
      because this gate exited 2 on the whole build. Also caught: `s06` gets
      0.34s after a question against the 0.35s floor. Phase 3's pilot must
      synthesize its final clip with `FINAL_HOLD`.
- [x] 2.1 write fence + hook tests — `scripts/write-fence.sh`, a `PreToolUse`
      hook on Write/Edit/NotebookEdit/**Bash** (Bash included: a shell redirect
      or a copy is the obvious way around a Write-only fence). Default DENY;
      `SCLA_SYSTEM_SESSION=1` marks the deliberate system session, and a build
      subagent cannot set it for itself because the value is read from the agent
      process's environment. **Observed live, not assumed**, in the session that
      installed it: a probe write under `scripts/` was BLOCKED with its reason
      printed, and a workspace write succeeded. 42 assertions in
      `render-qa/tests/test_write_fence.py` invoke the real script with crafted
      payloads and grade BOTH failure modes — too loose, and too tight (a fence
      that blocks ordinary build work gets switched off within a day).
      **Design point worth keeping:** direction matters for the copy family.
      Copying OUT of a fenced path is a READ — `batch-prepare.sh` does exactly
      that on every prepare — while copying IN is a write; a move out is still
      blocked because it removes the original. The first cut fenced the source
      too and would have broken `batch-prepare.sh`. Decision recorded at
      `decisions/log.md` 2026-08-04 "The write fence".

      ⚠ **OPEN DEFECT — the fence is too tight on Bash, found by being bitten
      by it.** It scans the RAW command string, so a `git commit` whose MESSAGE
      merely mentions a mutator word near a fenced path is blocked, even though
      the command writes nothing fenced. It first fired on a commit message
      containing the words "…probe under scripts/…". Heredoc bodies and `-m`
      message text are DATA, not commands, and must be stripped before the
      token scan. **Fix:** in `write-fence.sh`, before the `DESTRUCTIVE` /
      `COPY_FAMILY` matching, delete heredoc bodies (`<<'WORD'` … up to a line
      equal to `WORD`) and the argument of `-m`/`--message`. Then add fixtures
      to `test_write_fence.py` asserting a commit whose message names a fenced
      path is ALLOWED, while a real redirect into that path is still blocked.
      **This could not be fixed in the installing session:** the fence covers
      `scripts/`, so repairing it requires a flagged session
      (`SCLA_SYSTEM_SESSION=1`) — which is the fence behaving exactly as
      designed, and is why it is reported here rather than patched.
      **The fix is WRITTEN and PROVEN, just not applied** — see
      `render-qa/docs/PENDING-write-fence-fix.md`. `verify_fence_fix.py` runs 24
      cases against the live fence and the fixed one side by side: the 5 false
      positives become ALLOW and every safety case still BLOCKs. Two narrowing
      changes only — strip heredoc/`-m` bodies before matching, and grade a
      redirect by WHAT IT WRITES TO rather than by a `>` existing at all. The
      fenced set, the default-deny posture and the opt-out are unchanged.

      ⚠ **ESCALATED 2026-08-04 (later session): this is a shipping-path block,
      not friction.** `scripts/with-secrets.sh` is the mandatory Infisical entry
      point for every HeyGen and Wistia call AND is a fenced token, so an
      ordinary credentialed build command whose redirect targets the build's
      OWN workspace is refused — `bash scripts/with-secrets.sh node audio.mjs
      > …/renders-hyperframes/<stem>/audio_meta.json`, and the same with a plain
      `2>/dev/null`. TTS synthesis and publish both cross that script, so a
      BUILD session — the very session type the fence exists to constrain —
      cannot reliably run the pipeline. Found by being bitten by it while
      claiming the Phase 3 pilot stem; pinned as FP4/FP5 in the proof harness.
      **Apply the fix before any further build work on either lane.**
- [x] 2.2 AGENTS.md purge + assertion — `batch-prepare.sh` already deleted
      `scaffold/AGENTS.md` beside CLAUDE.md, and zero workspaces carried one, so
      the purge itself was done; the missing half was the ASSERTION, now
      `lint-refs.sh` check 11 (11 -> 12 checks). It fails on a stray workspace
      `AGENTS.md` AND on `batch-prepare.sh` losing its delete line — the
      mechanism, not just today's result. One vendor copy remained and was
      `git rm`'d: `experiments/agent-native-m2/AGENTS.md`, the vendor's generic
      95-line router. **Out of scope, deliberately:**
      `design-system/AGENTS.md` is a hand-written SCLA project doc that
      `design-contract.md` cites by name — not vendor litter, and deleting it
      would break a live reference. **Bug found by running the failure case:**
      `grep -c` prints 0 AND exits 1, so `|| echo 0` produced "00" and the
      mechanism half died with "integer expression expected" — i.e. it would
      never have evaluated. Fixed and re-proven.
- [ ] 3 freeform pilot built (1 lesson) — gate failures, if any: _(record here)_
      **NOT STARTED — deliberately halted 2026-08-04, owner instruction "do not
      render the pilot yet."** Scoping done and recorded so the next session
      does not redo it:
      · **Lesson:** queue top is
      `build-direction-before-you-build-a-plan_early-career-boost` (7-paragraph
      refined script, present and readable).
      · **Stem lock:** claimed, verified canonical via `stem.py check`, then
      **released** (`rmdir`, dir was empty) — an empty locked workspace would
      read as a stalled build to `batch-status.sh`. The next session re-claims it.
      · **Credentials:** `HEYGEN_API_KEY` present via Infisical (the pinned
      Oxana voice's provider). `WISTIA_API_TOKEN` and `ELEVENLABS_API_KEY` are
      **MISSING** — irrelevant to Phase 3, which stops before publish, but
      Wistia must be restored before any SHIP.
      · **Procedure:** already written — `.claude/skills/render-lessons/SKILL.md`
      "Freeform build sequence", 8 steps, narration-first. No new plumbing
      needed; `preflight.py` auto-detects the lane.
      · **Blocker:** the 2.1 escalation above. The freeform sequence's step 4 is
      a `with-secrets.sh` TTS call, which the live fence refuses.
- [ ] 3 ⛔ owner verdict: _(record here)_
- [ ] 4 ⛔ retirement commit (owner-approved, queue drained)
