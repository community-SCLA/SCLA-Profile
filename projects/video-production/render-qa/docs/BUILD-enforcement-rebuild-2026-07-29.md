# BUILD — enforcement rebuild

**Status: BUILT — all six phases landed 2026-07-29.** Kept as the record of what
was specified and why; the outcome, including the two things this plan got wrong
about itself, is in `decisions/log.md` (2026-07-29, telemetry-rejection entry).
The acceptance checklist at the bottom is ticked with how each was verified.
· **Audience:** a fresh build session.
Background and the rejected alternatives live in
`HANDOFF-self-improving-gates-2026-07-29.md` — you do not need them to build.

## What you are building

Every `render-qa/check_*.py` must be **proven to fire** by an automated test, on a
realistic input, forever. Then close the specific holes where the checkers are
armed but inert. Six phases, strictly ordered, each independently revertable.

## Rules of engagement

- Run `python3 projects/video-production/render-qa/tests/run_tests.py` after every
  phase. It must stay green.
- **Where code and doc disagree, the code is authoritative.** Every drift below is
  a doc that went stale after a deliberate recalibration.
- **Nothing you build may block a batch or require the owner to clear it.** The
  worst failure mode at every step is a red test with an agent-fixable remedy.
- Verify line numbers before editing — several of these files are uncommitted and
  moving.
- Do not build a gate ledger, escape metric, dead-gate check, or CI teeth. That
  design was reviewed and rejected; see the handoff §1 and §7 if tempted.

---

## Phase 0 — Commit the truth, repair the lies

1. **`git add` the untracked gate files**: `check_capacity.py`,
   `check_continuity.py`, `check_layout.py`, `check_geometry.py`, `boxmodel.py`,
   `textmetrics.py`, `tokens.py`, `tests/test_gates.py`, and
   `design-system/assets/fonts/metrics.json`.
   `textmetrics.py` reads `metrics.json` unguarded, and `check_capacity.py` +
   `test_gates.py` both depend on it — on a fresh clone, capacity checking
   currently crashes or silently does not exist. Confirm `run_tests.py` passes
   from a clean checkout afterwards.

2. **Fix three doc/code drifts** (`design-system/docs/design-contract.md`):
   | design-contract.md says | Change to | Also fix |
   |---|---|---|
   | pacing gap FAIL > 4.5s, WARN > 3.5s | **4.0 / 3.0** (`preflight.py` values) | `preflight.py`'s own docstring is stale too |
   | "no stagnant frame beyond ~2s" | **3.0 WARN / 5.0 FAIL** (`check_presence`) | — |
   | "no form above 40% **of the content scenes**" | "of content **seconds**" | `check_variety` grades in seconds |

3. **Fix four self-contradictions:**
   - Delete the sentence-case `title` description. **Title Case wins** — owner's
     stated preference and what `check_copy` enforces.
   - Reconcile depth-drift amplitude to the **85–120px** figure (delete the
     "16–30px amplitude" line that the same doc later calls a defect).
   - Delete the superseded condition-only living-icon scope in the motion table
     (the 2026-07-15 widening is current).
   - `.claude/rules/video-production.md`: "≥5 distinct content forms" → **6**.

4. **The false CANVAS claim.** `check_variety.py` and `tests/test_variety.py` both
   claim the test greps every template's first `background:` against the `CANVAS`
   map. No such code exists. *Recommended: implement it* (~10 lines in
   `test_variety.py`) — it is a genuine template-drift guard. Otherwise delete
   the claim from both files.

5. **Correct two false enforcement claims** — the `# LOADED` comment above
   `design-contract.md`'s frontmatter `spacing` block, and the matching sentence in
   `.claude/rules/video-production.md`. Reality today: `tokens.py` exposes
   `frame_padding()`, `safe_area()`, `footer_reserve()`, `content_bottom()`, and
   the **only** checker consumer is `check_text.py` calling `min_size()`. Until
   Phase 2 lands, both must say min-size is loaded and the four spacing tokens are
   **not yet consumed by a gate**.

**Exit test:** `python3 scripts/check-enforcement.py` → 0 broken claims;
`run_tests.py` green from a fresh clone.

---

## Phase 1 — The firing mandate 

**Every `render-qa/check_*.py` must be covered by at least one test asserting a
POSITIVE finding.** A checker that cannot be shown to fire is not a gate.

Today: 11 `check_*.py` modules, 4 firing fixtures. `check_layout`, `check_slots`,
`check_boundaries`, `check_presence`, `check_geometry` have none. `check_text` has
only a token-import assertion. Title Case is armed in `check_copy.titlecase()`
with zero fixture proving it fires.

1. **`tests/test_firing_coverage.py`** — globs `render-qa/check_*.py`, globs the
   tests, fails if any checker has no test asserting a positive finding. Declare
   the association **explicitly** (module-level `COVERS = ["check_copy", ...]`),
   never inferred from imports — inference is how `check-enforcement.py`'s
   `invokers()` got its false negatives.

2. **Write the missing firing tests.** Each asserts the checker **returns a
   finding** on a minimal crafted input — not merely that it passes on a good one.
   Order: Title Case first, then `check_slots`, `check_text` size + restatement,
   `check_boundaries`, `check_geometry`.

3. `check_layout` and `check_presence` need a browser / rendered MP4. Register
   them in the coverage map as `tier: slow` so they are **tracked as uncovered
   rather than silently skipped** — silent skipping is how `run_tests.py` lost
   five suites.

**Exit test:** deliberately break `check_copy.titlecase()` → suite goes red.
Delete any firing assertion → suite goes red.

---

## Phase 2 — Arm the orphaned spacing tokens 

`render-qa/src/check_geometry.py` + its engine `boxmodel.py` exist, are untracked, and
are **invoked by nothing**. It is the gate that consumes the orphaned spacing
tokens (`safe_area()`, `content_bottom()`, `footer_reserve()`, `canvas()`).

1. **Resolve the 32px question first. Do not wire the gate in until it is
   explained** — a gate that falsely rejects the reference is a broken gate.

   Run against the pilot awaiting sign-off, `check_geometry` exits 1 with:
   ```
   !! scene-05 (scla-points.html)      [safe-area-breach] #kp-rail-label crosses the 72px keep-out (right x=1876)
   !! scene-17 (scla-points__i2.html)  [safe-area-breach] #kp__i2-rail-label crosses the 72px keep-out (right x=1876)
   ```
   Facts already gathered: only `scla-points.html` has a `#kp-rail-label`; its CSS
   is `position:absolute; right:76px; font-size:20px; letter-spacing:0.22em;
   writing-mode:vertical-rl`. `right:76px` on 1920 puts the right edge at **1844**,
   inside the 1848 limit — the gate measured **1876**, a 32px discrepancy.
   `boxmodel.py` does detect `writing-mode` (sets `vertical: True`), so this is
   either a real offset or a vertical-metrics bug.

   **Method:** run `npx hyperframes inspect` (the pinned CLI `check_layout.py`
   already uses) against the pilot and compare the browser's geometry for
   `#kp-rail-label` to `boxmodel.py`'s. **The browser is the oracle.**
   - `boxmodel` wrong → fix its vertical-writing-mode metrics, re-run, confirm the
     pilot is clean.
   - Breach real → template defect in `scla-points.html`. Fix the template; note in
     the decisions-log entry that this proves the gate's value. (See OWNER CALL 2.)

   Also settle the chrome asymmetry: `_is_footer_chrome()` exempts chrome from the
   **bottom** bounds only, not left/right/top. **Recommended: exempt chrome on all
   four edges** — grading chrome against the content keep-out on some axes and not
   others is incoherent, and may itself be the bug.

2. **Wire `check_geometry.py` into `preflight.py`** as a new section, `--static`-safe
   (it needs no render). Follow the existing `run_tool` **exit-code** pattern
   exactly — do not parse its JSON (see Phase 3).

3. **`tests/test_tokens_coverage.py`** — every scalar in `design-contract.md`'s frontmatter
   must have a `tokens.py` accessor **and at least one non-test consumer**. This is
   what makes the orphaned-token failure non-recurring: a token nobody reads
   becomes a red test.

4. **Delete the hard-coded literals in `tests/test_gates.py:190-195`** asserting
   `safe_area() == 72` etc. They are the hand-copy `tokens.py` exists to abolish,
   and they fail only if *design-contract.md* changes, never if a *video* violates the number.
   Replace with the coverage assertion from step 3.

5. Only now, restore the `# LOADED` comment in `design-contract.md` — it will finally be true.

**Exit test:** set `safe-area: 9999` in `design-contract.md`, confirm `preflight.py`'s verdict
changes. That is the proof the token is load-bearing. Revert.

---

## Phase 3 — Narrow typed findings 

Needed so Phase 4's assertions key on something stable instead of brittle
substrings. **Scope is strictly limited.**

**DO:** add a stable `rule_id` and `severity` to each checker's own `--json` output.
Nothing in the repo calls `check_*.py --json` — those nine blocks are dead code
today, so the blast radius is zero.

**DO NOT:**
- Touch `preflight.py --json`. It is a **frozen wire contract**: `sections[].pass`
  stays a bool, `sections[].output` stays a string, keys stay `^[a-z_]+$`
  (`scripts/review.sh` and `batch-precheck.sh` scrape them). Add typed data only
  under a new sibling key.
- Rewire `preflight.py` to consume checker JSON instead of exit codes. Five
  checkers have no `pass` key at all (`check_layout`, `check_slots`, `check_text`,
  `check_boundaries`, `check_presence` emit `fatal`/`findings`/`verdict`/
  `violations`), so `json.loads(out).get("pass", True)` **silently passes four
  gates**. Exit codes are the one part of this pipeline that has never lied.
- Print anything to preflight's stdout before the JSON.

**Harden the guard.** `scripts/hyperframe-guard.sh` is the only machine consumer of
`preflight.py --json`, and it fails silently: if `.output` stops being a string,
`jq` errors, `2>/dev/null` eats it, `viol` is empty, and the crash-fallback does not
fire because `.verdict` still parses — **the plan-stage guard exits 0 and reports
clean on every failing plan.** Remove the `2>/dev/null`, or add an explicit shape
assertion.

**Exit test — mandatory.** `tests/test_guard_contract.py`, for a workspace
engineered to FAIL each preflight section in turn:
1. Run `python3 preflight.py --static --json <ws>` as a real subprocess capturing
   `2>&1`, exactly as the guard does.
2. Assert stdout's **first byte is `{`** → catches any stray `print()`.
3. Run the guard's **actual** `jq` program (extract it from `hyperframe-guard.sh`;
   do not paste a copy or the two will drift) and assert it emits a **non-empty**
   string naming that section → catches the silent-clean failure.
4. Assert the same pipeline on a **clean** workspace emits the empty string →
   catches the inverse (renaming `pass` makes every clean section look violated).
5. Assert every section key matches `^[a-z_]+$`.

---

## Phase 4 — Mutation testing over a real full-length plan (~1 day)

This is what catches "a checker stopped being a checker." A toy fixture does not:
the natural fixture for the conjunction rule is one scene with three items and no
"or", which fires fine even under the broken per-scene scoping. Scope and sampling
bugs only manifest at real length.

**Base fixture.** Commit `tests/fixtures/base/scenes.json` — the 20-scene
2026-07-29 `better-decisions` plan, the only real full-length gate-clean plan that
exists. Label it in the fixture manifest as **`gate-clean, pending owner sign-off`
— never "approved."** No owner-approved plan exists; all six published videos
predate `build_index.py`.

**Store `scenes.json` only; rebuild against live `design-system/`.** Verified
end-to-end (`build_index.py` → `preflight.py --static`). A frozen *workspace*
hard-fails `composition_freshness` within 24h; a frozen *plan* tracks live
templates by construction.

**Harness rules — each is load-bearing:**

1. **Assertions are DIFFERENTIAL and per-rule:** rule R **fires on the mutant** AND
   **does not fire on the baseline**. Never assert global pass/fail — a global
   assertion stays green while the rule you care about is deleted, because sibling
   rules in the same checker fire.
2. **Copy `compositions/` into the temp workspace.** Verified: without templates,
   `check_slots` prints a clean PASS on zero templates, and `check_capacity` /
   `check_text`-size silently no-op. A corpus that proves nothing while going green
   is worse than none.
3. **Pass `static=True` to `check_continuity`** on uncompiled plans. Without it the
   placeholder `data-duration="1"` yields 18 findings on a gate-clean plan — 100%
   false positives.
4. Use `tempfile.mkdtemp()`, never the fixed `/tmp` paths `run_tests.py` and
   `test_gates.py` use — those collide under parallel runs.
5. Call checkers **in-process** where possible (~2s added to a 2.2s suite);
   shelling out to `preflight.py` costs 0.65s × N.

**Mutation set — the nine that reproduce real defects:**

| Mutation | Must fire |
|---|---|
| Split an enumeration across three scenes (3/2/2) | `check_copy` conjunction |
| Inject a text collision at **scene 15** | `check_layout` / `check_geometry` |
| Rename two scenes to `__scene_NN` clones of one family | `check_variety` |
| Add a chip restating its heading | `check_text` |
| Point two scenes at one shared template | `instance_templates` wiring |
| Push a card past `frame-padding` | `check_geometry` |
| Lowercase a heading | `check_copy` Title Case |
| Blank a declared slot | `check_slots` |
| Point `script_match` at a missing script | must **FAIL**, not WARN-and-pass |

The last one is a live bug: `preflight`'s missing-script branch is WARN-and-skip
returning `pass: True`, which silently disarms the fabrication ban.

**Exit test:** revert `check_copy` to per-scene conjunction scoping → mutation 1
goes red. That single check is the whole point of the phase.

---

## Phase 5 — Close the graveyards (report-only)

Hygiene, not the fix. Build it **after** Phases 1–4, never instead of them.

All changes **report-only** per STD-38:

1. Add `.claude/skills/render-lessons/SKILL.md`, `.claude/skills/refine-scripts/SKILL.md`,
   and `decisions/log.md` to `check-enforcement.py`'s `GRADED` list.
   (`render-lessons/SKILL.md` alone holds 38 normative lines with zero mechanism
   annotations and is read into every build subagent's instructions.)
2. Fix the auditor's own false negatives:
   - `LINTCHECK` regex requires whitespace after the filename, but every real
     citation is backticked — matches 1 of 6. One character: `[\s\`]+`.
   - `PATHISH` does not match `.jsonl`.
   - `invokers()` scans a fixed six-file list excluding `hyperframe-guard.sh` and
     `batch-precheck.sh` — add both.
   - `invokers()` matches a filename anywhere in a caller, **including comments** —
     make it ignore comment lines.
3. Number the test-suite check in `lint-refs.sh` (labels run `[1/10]`…`[10/10]`, so
   both "check 11" citations are literally unverifiable today).
4. Widen the line filter beyond `-`/`*`/`|` to any prose line, and parse YAML
   frontmatter comments. Raises recall from ~17% toward ~90%.

**Do NOT flip `--strict`.** It hard-fails CI on ~115 design-contract.md items on day one, and
the cheapest response is relabelling them `Convention` — which changes nothing
physical.

**Do NOT attempt the design-contract.md split** (machine spec + rationale doc). It touches
~20 files that route agents to "read design-contract.md first", including a hook string in
`.claude/settings.json`, and `preflight.check_title_card` regex-scrapes the program
display-name table out of design-contract.md's **body**. Legitimate follow-up, not this build.

---

## Owner calls

1. **The pilot still needs sign-off** —
   `bash scripts/preview.sh better-decisions-come-from-better-criteria_early-career-boost_2026-07-29`.
   Phase 4 uses that plan as its base fixture regardless; sign-off is **not** a
   prerequisite for the build.
2. **If Phase 2 finds the rail-label breach is real**, the template fix changes the
   pilot's pixels and may warrant a re-preview. Default: fix the template, re-run
   gates, flag it at the next preview rather than blocking.
3. **The ripples / in-place keep-alive motion ban is unarmed and was violated in
   published work.** Banned 2026-07-14, reaffirmed 07-15, violated within a day (a
   session restored the banned motion so renders would pass the stagnation gate;
   three MP4s shipped, one published). It is still unarmed prose in `design-contract.md`.
   Options: (a) arm it as a real check near `check_presence`, (b) route it to
   `/adversarial-qa` as an explicit rubric item, or (c) mark it `Convention` out
   loud. **Default if the owner is unreachable: (c) plus a tracked follow-up.**
   Do not silently re-arm and do not silently drop it.

---

## Done when all of these pass

- [x] `run_tests.py` green **from a fresh clone** — verified by cloning to a temp
      dir and running the suite there; clean tree, exit 0.
- [x] `python3 scripts/check-enforcement.py` → **0 broken claims** (86 backed,
      226 unbacked report-only).
- [x] Deleting any firing assertion turns `run_tests.py` red — deleted
      `check_slots:unfilled`; suite went red with `NO FIRING PROOF`. Reverted.
- [x] Breaking `check_copy.titlecase()` turns the suite red — made it the
      identity function; four assertions went red across three suites. Reverted.
- [x] `design-contract.md safe-area: 9999` changes `preflight.py`'s verdict — PASS → FAIL
      with `safe-area-breach`; reverting restores PASS.
- [x] Reverting `check_copy` to per-scene conjunction scoping turns mutation 1 red
      — and the mutant still fired four sibling rules, which is why the assertion
      had to be differential and per-rule. Reverted.
- [x] `hyperframe-guard.sh` reports violations on a failing plan **and** stays silent
      on a clean one, asserted by `test_guard_contract.py` running the guard's real
      `jq` program. **Caveat:** its clean-plan half points at the on-disk pilot
      workspace, which is gitignored — on a fresh clone that half self-skips with a
      `~~` note. Tracked, not silent, but it does mean CI never runs the inverse
      assertion. Worth replacing with a synthetic clean fixture.
- [x] `preflight.py --json` shape unchanged: `pass` bool, `output` string, keys
      `^[a-z_]+$`, no per-section key added. (Note: `sections` is a dict keyed by
      name, not a list — the `sections[].x` notation above is loose.)
- [x] The 2026-07-29 pilot still passes every gate end to end — `--static` PASS on
      all sections. **Full mode cannot run on it as it sits:** its `index.html` was
      regenerated at 05:42 (≈3h after the MP4), so it carries plan-stage
      `data-duration="1"` placeholders and the timing/render gates legitimately
      fail. `scenes.json` predates the render, so no content drift. Every gate this
      build touched passes in BOTH modes.
- [x] `decisions/log.md` entry written: why the telemetry design was rejected, what
      replaced it, and the doctrine — *a rule is armed when something automatically
      re-runs the owner's actual defect against its checker and fails if it passes*
- [x] **Added beyond the plan, on owner instruction:** the ripples / keep-alive ban
      (OWNER CALL 3) was closed by deleting the capability rather than labelling it
      `Convention`. Six sites removed from five templates; `check_motion.py` fails a
      re-add at plan stage and at `npm run check`.

## One caution

Do not treat the on-disk 2026-07-28 rejected workspace as evidence of anything. It
**passes** `check_variety` (7 families, 26% peak share) while `check_variety.py` and
`preflight.py` both describe it as "21 scenes, 5 templates, 8 × scla-statement, 42%
share." Nothing in the repo links artifact → verdict, so the disagreement is
unresolvable. Phase 4's mutations are authored deliberately, not scraped from it.
