# BUILD PLAN — agent-native adoption, execution order

**Date:** 2026-08-04 · **Status:** Phases 1–2 landed. **Phase 3's pilot was
REJECTED by the owner on 2026-08-04 ("SO boring"), and a different, earlier
freeform cut was approved instead — see Phase 3R, which is now the live work.**
Phase 4's precondition was rewritten 2026-08-04 (it referenced a pilot that no
longer exists) and it still needs an explicit owner go-ahead ·
**Audience:** a fresh session with no memory of the conversation that produced
this.

> **Read Phase 3R before Phase 1.** The owner verdict reversed the direction of
> a gate that Phases 1–2 spent their whole effort tightening, and it re-scopes a
> rule the snag-log has been queued to arm. Executing Phase 1's ledger forward
> without Phase 3R will rebuild the boring cut.

> **Phase 3R is TWO independent tracks and they were previously tangled.**
> **Track A ships the video the owner already approved** and needs exactly one
> code change plus a credential. **Track B stops the next build being boring**
> and is the larger job. Track A does not depend on Track B. Do Track A first —
> it delivers a finished lesson, and it is four hours of work behind a
> one-line constant. *(Split 2026-08-04 by the advising session; the previous
> revision listed the shipping blocker as ledger item 3R.6, last, behind five
> gate edits it does not depend on.)*

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

## Phase 3R — Re-evaluation after the owner verdict ⛔ needs a flagged session

**This supersedes Phase 3's remaining boxes.** Phase 3 delivered a gate-clean
pilot and the owner rejected it. A second cut of the same lesson, built
2026-07-30/31 and sitting QUARANTINED at
`renders-hyperframes/build-direction-before-you-build-a-plan_early-career-boost`,
was approved to ship. Full measurements, thresholds and the exact edits:
**`render-qa/docs/PENDING-pace-gates.md`**, with the working checker beside it
at `render-qa/docs/check_pace.py`.

**The verdict in one line:** the gate set approved the cut the owner rejected
and quarantined the cut the owner approved.

**Why nothing in `src/` could have caught it.** Phase 1 assumed the freeform
risk was *coverage* — gates grading zero elements. That was real and is closed.
The rejected pilot exposes a second failure the plan did not model: **the
surviving gates all measure animacy, and the owner was responding to
structure.** Measured on the rejected cut — 22 stills on a 1.25s grid across its
two longest beats — it changes something every ~2.5s, its longest static span is
**3.75s** (under `STAGNANT_FAIL`), it draws a new picture every beat, and it has
**zero** twin pairs. By every metric this pipeline owns it is the *healthier*
build. It is boring because each idea takes 9.3s to arrive and nothing on screen
accumulates.

A prediction was made here and refuted: the expectation was that the boring cut
would fail `check_presence` harder. It does not. The refutation is what
identified the real discriminators.

| | approved | rejected |
| --- | ---: | ---: |
| beats per minute | **10.26** | **6.47** |
| median beat | **5.15s** | **9.12s** |
| runtime in >8s beats | **45%** | **79%** |
| mean inter-beat churn | **3.34%** | **10.07%** |
| twin pairs / longest static span | 2 / 5.5s | 0 / 3.75s |

The last row is inverted, and it is load-bearing: **low inter-beat churn is the
signature of the carrying object**, not a defect. The approved cut's field of 48
marks arrives once and is thereafter only re-grouped.

---

### TRACK A — ship the cut the owner approved

Independent of Track B. Two blockers, one of them not code.

**A1. `STAGNANT_FAIL` 5.0 → 6.0** *(fenced — needs `SCLA_SYSTEM_SESSION=1`)*

The quarantine fired on exactly three spans: **5.0s, 5.5s, 5.5s** (re-read from
`qa/quarantine-reason.txt` 2026-08-04, not recalled). **The owner watched those
three spans and approved the cut**, so a hard floor at 5.0 sits below the owner's
line. 6.0 clears the worst with 0.5s of margin and still fails the 7s+ dead hold
nothing defends. Every other `verify_render` section on that build is already
`ok` — container, frames, and monotony-as-advisory — so this one constant is the
whole quarantine.

It does **not** rescue the rejected cut (worst span 3.75s, already under the old
floor), so it cannot be mistaken for a general loosening. Track B's pace gates
are what replace the pressure.

`check_diversity` derives `MAX_SAMPLE_GAP = STAGNANT_FAIL / 4.0`, so its grid
relaxes 1.25s → 1.5s automatically; its calibration comment (lines 76–99) is
written against `FAIL = 5.0` and must be re-stated in the same commit or it
becomes a lie about the current constant. `test_diversity.py` pins the derived
gap — expect it to move.

**A2. `WISTIA_API_TOKEN` is absent and publish will fail without it**
*(owner/infra action, not code)*

Probed 2026-08-04 against the live vault: `scripts/with-secrets.sh` resolves
`HEYGEN_API_KEY` and **nothing else** — `WISTIA_API_TOKEN` and
`ELEVENLABS_API_KEY` do not appear in the `dev` environment, which is the only
one the wrapper reads by default. This is now a measured fact, not the previous
revision's "UNVERIFIED, probe was refused". SHIP's last step is
`scripts/wistia-upload.sh`, so Track A completes to a filed, verified MP4 and
then stops. Either add the token to `dev` or point the wrapper at the
environment that holds it.

**A3. s07 script fidelity — RESOLVED 2026-08-04, no longer a blocker.**
See the ledger entry for what was done and why; `script_match` reads
**386 vs 386 words, 0.00%**, and full `preflight --static` on that workspace is
**PASS**.

**Track A done when:** `verify_render` exits 0 on the existing
`..._2026-07-31.mp4`, the quarantine marker is cleared, `qa/VERIFIED` is written,
the MP4 is filed to `renders-mp4/early-career-boost/`, and — once A2 lands — the
Wistia URL is in `published.tsv` + `refinement-log.md` in the same commit.
**Do not re-render.** The approved artifact is the file on disk; a re-render
changes what the owner approved.

---

### TRACK B — stop the next build being boring

**B1. `check_pace.py` into `src/`** — `beat-pace`, `long-beat-share`,
`carrier-drift`; thresholds pinned in the gap between the two cuts with margin on
both sides. Re-proven 2026-08-04 by the advising session against both live
workspaces, not carried over as a claim: approved → `PACE: PASS` exit 0;
rejected → `PACE: FAIL (4)` exit 1 with `--stills`, `FAIL (3)` without. Wire into
`preflight.py`'s freeform branch — timing rules in `--static` (where the fix is
re-splitting the beat manifest and is free), `carrier-drift` in the full gate
over the existing `snapshots/` grid.

**Blocking, not advisory.** The boring cut passed everything advisory and reached
the owner clean. The usual objection to a blocking taste number — "it gets
switched off within a day" — is answered by *where* it fires: the timing rules
run at plan stage, so a false stop costs a beat re-split before any audio exists,
not a re-render.

**Stated limit, and it must be written into the module docstring:** these
thresholds are calibrated on **n=2, and both cuts are the same lesson**. That is
enough to fix a direction and not enough to claim a general law. A future lesson
that genuinely wants a slower shape is an **owner decision that pins a second
reference build**, recorded in `decisions/log.md` — never a CLI flag, never a
loosened constant. Same posture as the ink gate's declared keep-out region.

**B2. `twin-beats` — re-scope, do not simply delete** *(changed 2026-08-04 by the
advising session; the previous revision said "retire it on this lane", full
stop)*

The retirement half is right and the reasoning holds: `logs/snag-log.md`
2026-07-31 has the rule waiting on "one approved freeform cut nominated as the
reference", that cut now exists, and it scores **worse** on the per-pair rule
(2 twins) than the rejected one (0). Arming it as a per-pair defect drives every
future build toward the boring cut. **So the per-pair defect dies.**

But deleting it outright leaves a hole that B1 itself opens. **`beat-pace` reads
the audio manifest, not the pixels.** Split one 12s beat into two 6s beats with
the same picture on screen and `beat-pace` goes green while nothing changed for
the viewer. `carrier-drift`'s `FROZEN_MEAN_CHURN = 0.004` floor only catches a
build that is nearly a still image; a build sitting at 1–2% churn passes
everything. That is a live gaming vector, and it is the *cheapest* way to satisfy
the new gate.

**Replace the per-pair defect with a share ceiling — `twin-share`.** Fraction of
consecutive beat pairs that are twins: approved reads **2/25 = 8%**, rejected
**0/16 = 0%**. Ceiling at **25%**. Being honest about what this is: it does
**not** discriminate between the two cuts — both pass — so it is not a quality
rule and must not be described as one. It is a backstop that exists only because
B1 created something worth gaming. **It therefore has no naturally-occurring
failing build, which by this repo's own discipline means it lands with a
planted-defect firing test in `test_pace.py` or it does not land at all.**

**B3. `.claude/skills/render-lessons/SKILL.md`, freeform sequence** — steps 2, 3
and 7. Both builders followed this sequence faithfully; its only quality
instruction is an ungraded one-sentence "concept angle", and the rejected cut's
`design.md` states plainly that its carrying object "hands off". The carrying
object must now declare the beat range it persists across (≥60% of runtime), and
step 3 states the pace target (~10 beats/min — a ~150s lesson is ~25 beats, not
~17). Add step 3's `check_pace.py --static` call beside the existing
`preflight --static` advice: that is the step where the fix is free.

**B4. `.claude/rules/video-production.md`** — a Pace rule with `check_pace.py`
as its mechanism; update the stagnation number to 6.0 and rewrite the monotony
bullet to describe `twin-share` rather than a rule awaiting a pin.
`lint-refs.sh` check 10 audits these claims, so this lands in the same commit.

**B5. One new freeform pilot, built under the pace gates, to the owner.**
*(Added 2026-08-04 by the advising session — the plan had no step that tests
whether B1's numbers produce a good video rather than merely a passing one.)*
B1–B4 are calibrated on a single rejected build. The only way to know they aim at
the right thing is to build one lesson under them and put the pixels in front of
the owner. Same stop as Phase 3: **ends at the hyperframe gate, no Phase 4 in the
same session.** This is also what restores Phase 4's precondition, which the
rejection invalidated.

**Blocked on:** every path in A1 and B1–B4 is inside the Step 2.1 write fence
(`render-qa/src/`, `.claude/`). Needs a session exporting
`SCLA_SYSTEM_SESSION=1`. This is the fence working as designed, not a defect.
**Fix `PENDING-write-fence-fix.md` in that same session before anything else** —
its false positives block redirecting any gate's own output anywhere, which is
friction every step below will hit.

---

## Phase 4 — Retirement ⛔ requires explicit owner go-ahead

**Preconditions** *(first one rewritten 2026-08-04 — it named the Phase 3 pilot,
which the owner REJECTED, so as written this phase was permanently unreachable)*:

1. **The Track B pilot (3R.B5) cleared the owner gate** — a freeform build
   produced under the pace gates and approved on its pixels. The Jul 30–31 cut
   does not satisfy this: it was approved, but it was built *before* the gates
   and is the reference they are calibrated against, so passing them is
   circular. Retirement needs one build that the new rules *steered*.
2. Owner has said "go" on retirement specifically.
3. The mid-career batch has drained — no live workspace still depends on the
   template path (check `batch-status.sh` and `published.tsv`).

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

      ⚠ **ESCALATED 2026-08-04 (later session), then CORRECTED 2026-08-04 by
      the session that actually ran the pilot. The escalation was WRONG: this
      is friction, not a shipping-path block.** The escalation rested on a
      command form the procedure does not use. The documented TTS invocation
      passes its output path as a FLAG, not a shell redirect —
      `audio.mjs --request … --hyperframes . --out ./audio_meta.json`
      (`hyperframes-media/SKILL.md`; the same form the reference build records
      in `PROVENANCE.md` §4). With no `>` in the command there is no token scan,
      so the fence returns **exit 0**. Verified twice, not argued: the crafted
      payload was graded by the live `write-fence.sh` (exit 0), and then the
      real call ran — 17 clips synthesized through `scripts/with-secrets.sh`
      with `HEYGEN_API_KEY` from Infisical. **The fence has never blocked the
      credential path.** Wistia publish is untested only because Phase 3 stops
      before publish.

      The underlying defect is still REAL and still worth fixing — it just
      costs a re-phrasing, not the pipeline. Two FRESH false positives were
      observed live this session, both on **read-only** commands:
      · `ls .claude/skills/hyperframes-media/ 2>/dev/null` — BLOCKED. The
        `2>/dev/null` widened the scan and `.claude/…` was an argument.
      · `python3 render-qa/src/preflight.py <ws> > <scratchpad>/pf.txt` —
        BLOCKED. The redirect targets a NON-fenced scratch path; the refusal is
        entirely because `preflight.py` appears as a read argument. **So the
        fence currently refuses to let you redirect any gate's own output
        anywhere.** That is the sharpest case yet for the fix and belongs in
        the harness beside FP4/FP5.
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
- [x] 3 freeform pilot BUILT (1 lesson) — **gates: a clean sweep.**
      `preflight.py` exit 0 (boundaries, script-match, brand, text, title,
      forms, copy, continuity, ink, motion, per-beat layout) and the framework's
      `npm run check` 0/0/0/0 with 20/20 contrast AA. Nothing was loosened to
      get there. Stem
      `build-direction-before-you-build-a-plan_early-career-boost`, 17 beats,
      **157.545s**, HeyGen/Oxana. Stops at the hyperframe gate: **not rendered**,
      per the standing owner instruction and the freeform sequence's own step 8.

      The three pre-set conditions from Phase 1 were all met, and each was
      earned rather than assumed:
      · **Headings declared** — every heading is an `<h1>`/`<h2>`, so Title Case
        graded real strings instead of reporting `no-headings-declared`. It
        immediately caught two: `Built From Repeated Clues` ("from" is a minor
        word) and one below.
      · **Ambient motion declared** — the single `#bg-lift` breath carries
        `/* motion-allow: … */` with a finite `repeat: 19`. **Placement matters
        and is not obvious:** the declaration must sit INSIDE the tween call,
        because `check_motion` reads `ALLOW.search(m.group(0))` over the tween
        match. A block comment immediately ABOVE the call is not seen — the
        `PostToolUse` guard caught exactly that and the gate said
        `keep-alive-motion`.
      · **FINAL_HOLD synthesized** — the engine tail-trims, so `s17` came back
        holding **0.215s** past its last word, the reference build's exact
        failure. The wav was padded to a true **1.800s** and `audio_meta.json`
        corrected, so the release is IN THE FILE.

      **Finding worth carrying — there are TWO different "final hold"
      measurements and satisfying one does not satisfy the other:**
      · `check_boundaries` `audio-tail-clipped`: `wav_duration - last_word_end`
      · `preflight` `compile_check` "final hold": `total - (audio_start +
        audio_dur)` — i.e. the VIDEO must also outlive the last wav.
      Padding the wav alone left compile_check reporting `final hold 0.00s`.
      Both floors are 1.5s; this build gives 1.8s to each (3.6s of visual hold
      after the last spoken word). Any freeform build will hit this.

      **New gate defect, reported not patched (`render-qa/src/` is fenced):**
      `check_copy.titlecase()` mangles a dotted initialism. `WORD_RX` matches
      only the leading `A` of `A.I.`, and since `"a"` is in `MINOR`, a heading
      containing `A.I.` anywhere but first or last position is graded against
      the expected form `a.I.` — unsatisfiable. Reproduce: heading
      `Reflection and A.I. Support`. Worked around by wording the heading
      `A.I. Supports Your Reflection`, where first position forces the cap.
      Suggested fix: treat a dotted initialism as one carrier token.

      **Script edit, before synthesis (the only point where it is a text edit
      rather than a re-synthesis):** `check_copy` in script mode flagged the
      four-question run in paragraph 2. Per the rules file the fix is to join
      the list into one sentence, so
      "Where did you feel engaged? / capable? / useful? / proud of the
      outcome?" became "Where did you feel engaged, capable, useful, or proud
      of the outcome?" Script-vs-beats then diffed 375 vs 375 words, 0.00%.
      **Owner: this is the one wording change to the approved script — say the
      word and it reverts.** Related gate observation: the run the checker
      named ended one item early, because the true final item (8 words) exceeds
      the 5-word cap and drops out of the run, so the finding is attributed to
      the wrong item even though the defect it points at is real.

      **Credentials (correcting the previous session's note):** `HEYGEN_API_KEY`
      is present AND working — it synthesized this pilot. `WISTIA_API_TOKEN` and
      `ELEVENLABS_API_KEY` are absent from the `dev` environment, which is the
      only one `with-secrets.sh` reads by default. Whether they live in another
      Infisical environment or folder is UNVERIFIED: the probe was refused by
      the session's permission classifier, not by Infisical. Check the console
      before any SHIP.
- [x] 3 ⛔ hyperframe gate — owner previewed the pilot 2026-08-04.
- [x] 3 ⛔ **owner verdict: REJECTED — "SO boring."** The owner instead approved
      the earlier freeform cut at
      `renders-hyperframes/build-direction-before-you-build-a-plan_early-career-boost`
      (built 2026-07-30/31, rendered, and QUARANTINED by `verify_render`), and
      directed that the pipeline follow the path that produced it. The gate set
      approved the rejected cut and blocked the approved one. **Phase 3 is
      closed; Phase 3R is the live work.** Per the certification protocol this
      verdict becomes checkers, not a remembered preference — the checker is
      written and proven (`docs/check_pace.py`), and blocked on the write fence.
**Ledger re-ordered 2026-08-04 by the advising session** to follow the Track
A / Track B split above. Track A ships a finished lesson and does not wait on
Track B.

*TRACK A — ship the approved cut*

- [x] **A3 s07 script fidelity — RESOLVED, and the owner delegated the call.**
      The choice was framed as "revert to the July wording" vs "re-synthesize and
      re-render". **Both framings were wrong, because the July SCRIPT and the
      approved AUDIO were never the same string** — the July build satisfied the
      conjunction rule with a one-word edit in its own beat manifest
      (`Where` → `or`) and never back-ported it, which is the snag-log's
      "needs back-porting (or veto)" entry from 2026-07-30. Reverting the script
      to its pre-`ab3c19d` text would therefore have left `script_match` failing
      anyway.
      **What was done instead: the script was set to what the approved video
      actually says** — "Where did you feel engaged? Where did you feel capable?
      Where did you feel useful, or did you feel proud of the outcome?"
      Verified, not assumed: `script_match` went 375 vs 386 words / 2.93% /
      longest miss run 4 → **386 vs 386 / 0.00% / run 0**, and full
      `preflight --static` on that workspace is **PASS** including `COPY` — the
      `or` satisfies the conjunction rule, so nothing was traded away to get
      here. The MP4 is untouched and still the artifact the owner approved.
- [ ] A1 ⛔ `STAGNANT_FAIL` 5.0 → 6.0 (+ `check_diversity` gap & comment) —
      clears the quarantine; the only code change Track A needs
- [ ] A2 ⛔ `WISTIA_API_TOKEN` into the `dev` environment (owner/infra) — measured
      absent 2026-08-04; SHIP's publish step cannot run without it
- [ ] A4 ⛔ `verify_render` exit 0 → `qa/VERIFIED` → file the MP4 → publish +
      `published.tsv` row. **No re-render.**

*TRACK B — stop the next build being boring*

- [ ] B1 ⛔ `check_pace.py` → `src/` + `preflight` wiring + firing test + the
      n=2 calibration limit stated in the module docstring
- [ ] B2 ⛔ `twin-beats` per-pair defect retired, replaced by `twin-share` (25%
      ceiling) as the anti-gaming backstop for `beat-pace` — lands with a
      planted-defect firing test or does not land
- [ ] B3 ⛔ `render-lessons` freeform sequence — steps 2, 3, 7
- [ ] B4 ⛔ `.claude/rules/video-production.md` mechanism lines
- [ ] B5 ⛔ one new freeform pilot built UNDER the pace gates → owner verdict.
      Restores Phase 4's precondition.

*Prerequisite for both tracks*

- [ ] W ⛔ apply `PENDING-write-fence-fix.md` first in the flagged session — its
      false positives block redirecting any gate's output anywhere

- [ ] 4 ⛔ retirement commit (owner-approved, queue drained, B5 pilot approved)
