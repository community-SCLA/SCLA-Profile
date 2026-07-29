# HANDOFF — Making owner feedback stick: the enforcement rebuild

**Date:** 2026-07-29 · **Status:** plan approved for build, not yet built ·
**Audience:** a fresh session with no memory of the conversation that produced this.

Read this file top to bottom before touching anything. It is self-contained.
Every open question was decided here on purpose so you do not have to ask the
owner anything. Where a decision is genuinely the owner's, it is marked
**OWNER CALL** with a safe default already chosen and the override written down.

---

## 0. Why this exists (read this or you will rebuild the wrong thing)

The owner asked for a **self-improving / self-learning mechanism** in the video
pipeline: "everything gets put into the log but nothing reads it."

A design was proposed — typed rule IDs, a JSONL gate ledger, an escape/dead-gate/
noise analyzer, and CI teeth that block a batch on unaddressed debt. **Eight
adversarial review lanes ran against it. It was rejected.** Not softened —
rejected. Sections 1–3 record why, so nobody rebuilds it in six weeks.

Then the owner said the thing that redirected the whole effort:

> "SO many things are referencing design-contract.md when that is a prose file, it's not
> enforceable... a lot of rules in there that aren't enforced and not armed. So
> many of the points of feedback that I have given in the past have landed there
> and then just not been enforced."

That is the real problem, it is measurable, and it is fixable. This plan fixes
that instead.

### The measured problem

A trace of all 33 standing preferences the owner has given across the repo's history:

| Metric | Value |
|---|---|
| Armed as a mechanism at the moment first given, **before 2026-07-27** | **0 of 18 (0%)** |
| Buried as prose (or contradicted by a doc) | **23 of 33 (70%)** |
| **Buried preferences that later recurred as a shipped or rejected defect** | **14 of 23 (61%)** |
| Median lag, feedback → enforced (pre-2026-07-27 cohort) | **10 days** |
| Worst lag | **22 days** (`frame-padding: 120px`) |
| Preferences needing **three** gives before they held | 1 (the conjunction rule) |

And the second, less visible failure — **armed but not firing**. Five gates
existed, were correctly named, passed the repo's own STD-35 enforcement audit as
"backed claims", and never fired on the defect they were written for:

| Gate | Why it didn't fire | Cost |
|---|---|---|
| `check_copy` conjunction | graded per scene; a 7-item list split 3/2/2 never reached the ≥3 threshold | the 2026-07-29 owner rejection |
| `check_text` restatement | `chips` key unmatched; comma lists diluted the overlap ratio | echo-chips shipped |
| `check_variety.family()` | `__scene_NN` clone suffixes made every clone its own family — reported 8 findings when the truth was 13 | the rejected pilot passed certification |
| `npm run check` layout | 9 samples across the whole runtime; `content_overlap` emitted at severity `info` | **both** owner layout complaints were already visible and discarded |
| `preflight script_match` | missing-script branch is WARN-and-skip returning `pass: True` | would silently disarm the fabrication ban |

**≈38% of the mechanisms armed in the 2026-07-27/28 wave were later found not to fire.**

### The doctrine this plan encodes

> **A rule is not armed when a checker exists. It is armed when something
> automatically re-runs the owner's actual defect against that checker and fails
> if it passes.**

Everything in Section 4 follows from that one sentence.

---

## 1. What was proposed and why it was rejected

Do not rebuild any of this. Each row has the finding that killed it.

| Rejected | Why |
|---|---|
| **Gate ledger (JSONL of every finding)** | The pipeline's dominant failure is **miscalibrated presence**, not absence. Overlap at `info`, `instance_templates` at warning, `family()` returning 8 of 13 — in every case a finding *existed*. An escape join ("no gate flagged this") returns **"not an escape"** on the three worst defects in repo history, and a dead-gate report returns **"alive and healthy."** The detector is defined inversely to the actual failure mode. |
| **`self_audit.py` escapes / dead gates / noise / margin collapse** | No sample size, and none is coming. `published.tsv` = **6 videos lifetime**; **7 of 9 checkers postdate all six publishes**, so zero approved videos have ever been seen by the current gate stack. Owner rejections in repo history: **2, both of the same lesson**. AUTO-BATCH is *designed* so one pilot approval authorizes a whole batch — verdicts accrue **per batch, not per video**, so N grows at single digits per year. The metrics need ~30. |
| **"Dead gate fails CI"** | "Never fired" is also the definition of success. The rules that fire zero times on a healthy batch are the *good* ones — fabrication ban, `audio-tail-clipped`, blank-scene detection. P(≥1 rule fires zero times in 29 builds) ≈ 1.0, so the check fails always and the only ways to clear it are **loosen the gate** or **mark it expected-rare until vacuous**. Worse: `lint-refs.sh` funnels everything through one `WARNINGS` counter, so a permanently-red dead-gate finding **masks a real `test_variety` regression** — a net loss of enforcement. |
| **"An escape with no new rule blocks the next batch"** | Strict dichotomy, no safe branch: an agent can write the release field → theater; only the owner can → deadlock. **The deadlock already happened.** On 2026-07-29 the session correctly declined to hard-block the script-stage conjunction check (16/32 scripts flag it; a minority are rhetoric). Under this rule that judgment is illegal and all 29 queued videos freeze. Measured owner clearing latency on this repo: **5–8 days**; one recommendation went unacted-on across 25 consecutive routine firings. Estimated probability of ≥1 multi-day stall in month 1: **80–85%**. |
| **Shadow-mode auto-promotion by measured precision** | Same missing sample size, ×100. |
| **Typed rule IDs as a cross-checker refactor** | See §4.3 — a *narrow* version survives. The broad version does not: `preflight.py --json`'s shape is consumed by `hyperframe-guard.sh`, and breaking it **degrades silently to "always clean"** (§2.6). |
| **Freeze approved+rejected plans as a golden corpus ("approved must PASS, rejected must FAIL")** | Disproved by experiment. A reviewer deleted the 4.5s blip rule — the gate built for the owner's first-named defect — and the rejected build **still failed**, because two sibling rules in the same checker fired. The assertion stays green while the rule you care about is gone. Separately, a one-line template edit (`width: 360px → 300px` on `scla-career-map`) flipped the *approved* fixture from `CAPACITY: PASS` to `FAIL (2)`. Golden corpora rot against routine template edits. **Superseded by §4.4 (mutation), which is differential and immune to this.** |

### Two corrections to the record

1. The claim "the conjunction rule was dead for months and no telemetry noticed"
   is **false**. `check_copy.py` was created 2026-07-28, ~one day before the
   rejection. For the months in question the rule was **prose in `design-contract.md`,
   written as the soft word "prefer"**. A ledger of firings cannot notice a rule
   that was never code. This is the owner's point, not an argument for telemetry.
2. `tests/test_variety.py` was cited as "the pattern that works." Its own
   docstring says the reference video's workspace was pruned, so the fixture is a
   **hand reconstruction that documents its own divergence from the real video
   (43% vs ~35% measured)**. The REJECTED fixture is a synthetic
   `for _i in range(8)` loop. Treat it as a *synthetic* pin — which is fine and
   valuable — never as evidence about a real video.

---

## 2. Live defects found during review — fix these regardless of the plan

These are real, they exist right now, and most are independent of everything else.
**Verify every line number before editing — many of these files are uncommitted and moving.**

### 2.1 BLOCKING — the spacing tokens are still enforced by nothing

`config/tokens.yml` contains this comment above the `spacing` block:

> `# These four are LOADED, not quoted: render-qa/src/tokens.py parses this block and`
> `# every checker imports from it. Changing a number here changes the gate.`

**False.** `tokens.py` exposes `frame_padding()`, `safe_area()`, `footer_reserve()`,
`content_bottom()`. The only checker consumer of `tokens` is
`check_text.py`, which calls `min_size()` **only**. `tests/test_gates.py` asserts
the four spacing values equal hard-coded literals (`72`, `120`, …) — which is the
hand-copy `tokens.py` was written to abolish, and which fails only if *design-contract.md*
changes, never if a *video* violates the number.

`.claude/rules/video-production.md` repeats the false claim ("...and imported by
the checkers"). **Three of those four are imported by no checker.**

So `frame-padding: 120px` — the number whose absence let a card run through the
footer on 2026-07-28 — is *still* unenforced. The 2026-07-29 session believed it
closed this hole. It did not.

### 2.2 BLOCKING — `check_geometry.py` is a written gate that nothing invokes

`render-qa/src/check_geometry.py` (+ its engine `render-qa/src/boxmodel.py`) exist, are
**untracked in git**, and are **invoked by nothing** — not `preflight.py`, not any
script. It is the gate that would consume the orphaned spacing tokens: it calls
`tokens.safe_area()`, `content_bottom()`, `footer_reserve()`, `canvas()`.

Run against the pilot currently awaiting owner sign-off it **exits 1** with two findings:

```
[geometry] 128 painted text box(es) across 20 scene(s); 2 element(s) unplaced
  !! scene-05 (scla-points.html)      [safe-area-breach] #kp-rail-label crosses the 72px keep-out (right x=1876)
  !! scene-17 (scla-points__i2.html)  [safe-area-breach] #kp__i2-rail-label crosses the 72px keep-out (right x=1876)
```

**Whether these are true defects or a measurement error is UNRESOLVED, and
resolving it is task 1 of the build.** Facts gathered:

- Only `scla-points.html` has a `#kp-rail-label`; every other template's chrome passes.
- Its CSS is `position: absolute; right: 76px; font-size: 20px; letter-spacing: 0.22em; writing-mode: vertical-rl`.
- `right: 76px` on a 1920 canvas puts the right edge at **1844**, inside the 1848 limit. The gate measured **1876** — a **32px discrepancy**.
- `boxmodel.py` *does* detect `writing-mode` (sets `vertical: True`), so this is not a blind spot — it is either a real offset or a vertical-metrics bug.
- `_is_footer_chrome()` exempts chrome from the **bottom** bounds checks only; the left/right/top safe-area checks are not chrome-exempt. That asymmetry may itself be the bug.

**Do not wire this gate in until that 32px is explained.** Wiring a gate that
falsely rejects the pilot is the exact failure the repo's own doctrine names
("a gate that rejects the reference is a broken gate").

### 2.3 SERIOUS — CI is running a smaller test suite than your laptop

These files are **untracked**: `check_capacity.py`, `check_continuity.py`,
`check_layout.py`, `check_geometry.py`, `boxmodel.py`, `textmetrics.py`,
`tokens.py`, `tests/test_gates.py`, and
`design-system/assets/fonts/metrics.json`.

`textmetrics.py` reads `metrics.json` unguarded (`json.loads(METRICS.read_text())`),
and `check_capacity.py` + `tests/test_gates.py` both depend on it. On a fresh clone
or in CI, capacity checking either crashes or silently does not exist.
**Commit all of these.**

### 2.4 SERIOUS — three live drifts between design-contract.md and the code

| design-contract.md says | Code enforces | Provenance |
|---|---|---|
| pacing gap **FAIL > 4.5s, WARN > 3.5s** | `preflight.py` `GAP_FAIL = 4.0`, `GAP_WARN = 3.0` | snag-log 2026-07-28 records the recalibration; design-contract.md was never updated. `preflight.py`'s **own docstring is also stale** — the file contradicts itself. |
| "no stagnant frame beyond **~2s**" | `check_presence` `STAGNANT_WARN=3.0`, `STAGNANT_FAIL=5.0` | **2.5× looser than the doc every builder reads.** |
| "no form above 40% **of the content scenes**" | `check_variety` grades share in **seconds** (since 2026-07-29) | threshold matches, unit does not — a builder counting scenes computes a different number than the gate. |

Consequence of row 1: **every builder authoring to the spec targets a pacing
budget the gate rejects.**

### 2.5 SERIOUS — design-contract.md contradicts itself, including on Title Case

| A | B | Nature |
|---|---|---|
| heading slots (`heading`/`statement`/**`title`**) are **Title Case**, no terminal period | `title` = the lesson title "…in **sentence case** ('Better decisions come from better criteria')" | **Direct contradiction on the same slot.** This is the owner's most-cited grievance, half-fixed. `check_copy` grades `title` as Title Case; `preflight.check_title_card` compares case-**insensitively**, so it doesn't crash — it just misinstructs every builder. |
| depth-drift "**16–30px** amplitude" | "~85–120px — small **16–30px** moves read static" | The document prescribes an amplitude and then calls that amplitude a defect, 478 lines later. Neither is gated. |
| icon discipline "novel, not on every frame" (widened 2026-07-15) | living icon "**reserved for the condition/principle hero**" | The motion table preserves the superseded 2026-07-14 scope. |
| `.claude/rules/video-production.md`: "**≥5** distinct content forms" | design-contract.md and code both say **6** | A third copy, also drifted. |

### 2.6 SERIOUS — `hyperframe-guard.sh` fails silently and wears a blindfold

`scripts/hyperframe-guard.sh` is the **only** machine consumer of `preflight.py --json`:

```bash
viol="$(printf '%s' "$out" | jq -r '
  .sections | to_entries[] | select(.value.pass | not)
  | "!! [" + .key + "]\n" + (.value.output | split("\n") | map("   " + .) | join("\n"))' 2>/dev/null)"
```

Verified by experiment: if `.output` ever stops being a **string**, `jq` errors,
`2>/dev/null` eats it, `viol` is empty, and the crash-fallback does **not** fire
because `.verdict` still parses. **The plan-stage guard exits 0 and reports clean
on every failing plan.** Also: any stray `print()` to preflight's stdout breaks
`jq -e '.verdict'` and makes the guard scream on *every* write.

Fixes: drop the `2>/dev/null` (or add an explicit shape assertion), and treat
`preflight.py --json` as a **frozen wire contract** (§4.3).

### 2.7 SERIOUS — a false enforcement claim inside a checker

`check_variety.py` claims in a comment:

> "Freshness: `tests/test_variety.py` greps every template's first `background:`
> declaration against this map, so a template edit that flips a canvas breaks the
> test loudly."

**No such code exists.** `tests/test_variety.py` repeats the claim in its own
docstring. The `CANVAS` map happens to be correct today; nothing keeps it correct.
Found independently by two reviewers. `check-enforcement.py` cannot see it because
it grades six markdown files, not Python comments.

**This is the owner's design-contract.md complaint reproduced inside the checkers.** Either
write the grep or delete the claim.

### 2.8 The `check-enforcement.py` auditor has false negatives

- **`LINTCHECK` regex is dead in practice.** It requires whitespace after the filename, but every real citation is backticked (`` `scripts/lint-refs.sh` check 11 ``). It matches **1 of 6** citations across both rules files.
- **`lint-refs.sh` labels only `[1/10]`…`[10/10]`**; the test-suite check is real but **unnumbered**, so both "check 11" claims are literally unverifiable.
- **`PATHISH` does not match `.jsonl`.**
- **`invokers()` scans a fixed six-file list** that excludes `hyperframe-guard.sh` and `batch-precheck.sh` — a `check_*.py` invoked only by those audits as "invoked by nothing."
- **`invokers()` matches a filename anywhere in a caller, including comments** — a checker named-but-never-executed audits as armed.
- It **never parses YAML frontmatter** (so §2.1's false claim is invisible) and **only grades lines starting with `-`, `*`, or `|`** (so every normative *paragraph* is skipped). Measured recall against design-contract.md: **~17%**.
- **The unbacked count read 31 on 2026-07-28 and 31 today**, straight through a full arming session. Arming *appends* new annotated rules; nothing retires the prose already buried.

### 2.9 OWNER-VISIBLE — a standing directive was violated and published

On 2026-07-14 the owner banned in-place keep-alive motion ("I fully want ripples
off"), reaffirmed 2026-07-15. It was violated **within a day**: a session
*restored* the banned motion so renders would pass the stagnation gate. **Three
MP4s shipped; one was published.** It remains unarmed prose in `design-contract.md` today.

Surface this to the owner. Do not silently re-arm or silently drop it —
see §5, OWNER CALL 3.

### 2.10 Provenance gap in the rejected artifact

The on-disk 2026-07-28 rejected workspace **passes `check_variety`** (7 families,
26% peak share). But `check_variety.py` and `preflight.py` both describe that build
as "21 scenes on 5 templates, 8 × scla-statement, 42% share." Either the artifact
was edited after rejection or the calibration notes are wrong, and **nothing in the
repo can tell you which**, because no record links artifact → verdict.

Do not treat that workspace as authoritative evidence of anything. §4.4's
mutations are authored deliberately, not scraped from it.

---

## 3. The one-paragraph summary of what to build

Stop trying to detect *forgetting* — the review found **zero** defects in repo
history caused by a forgotten pattern, and **14** caused by a rule that existed
and did not fire. Build the thing that catches a rule which stopped being a rule:
**every checker must be proven to FIRE, by an automated test, on a realistic
input, forever.** Then close the specific holes where owner feedback is
demonstrably dying. Nothing new blocks a batch. Nothing new needs the owner.

---

## 4. The build plan

Six phases. **Strictly ordered — each phase is independently valuable and
independently revertable.** Nothing here can stall the video queue: the worst
failure at every step is a red test with an agent-fixable remedy.

Run `python3 projects/video-production/render-qa/tests/run_tests.py` after every
phase. It must stay green.

### Phase 0 — Commit the truth, repair the lies (do this first, ~1h)

Nothing downstream is trustworthy until the repo and the spec agree.

1. **`git add` the untracked gate files and `metrics.json`** (§2.3). Confirm
   `run_tests.py` passes from a clean checkout afterwards.
2. **Fix the three drifts (§2.4)** — the code is right, the doc is stale.
   Update `design-contract.md` to 4.0/3.0; update `preflight.py`'s own stale docstring;
   update the stagnation line to 3.0 WARN / 5.0 FAIL; change the variety wording
   from "of the content scenes" to "of content seconds."
3. **Fix the contradictions (§2.5)** — delete the sentence-case `title`
   description (Title Case wins; it is the owner's stated preference and what
   `check_copy` enforces); reconcile the depth-drift amplitude to the 85–120px
   figure; delete the superseded condition-only icon scope; change
   `video-production.md` "≥5 distinct content forms" to **6**.
4. **Delete or implement the false CANVAS claim (§2.7).** *Recommended: implement
   it* — it is ~10 lines in `tests/test_variety.py` and it is a genuine
   template-drift guard.
5. **Correct the two false enforcement claims** — the `# LOADED` comment in
   design-contract.md's frontmatter and the matching sentence in
   `.claude/rules/video-production.md`. Until Phase 2 lands they must say
   `min-size` is loaded and the four spacing tokens are **not yet consumed by a
   gate**. Do not leave a claim standing that Phase 2 has not yet made true.

**Exit test:** `python3 scripts/check-enforcement.py` reports **0 broken claims**;
`run_tests.py` green from a fresh clone.

### Phase 1 — The firing mandate (the core of this plan, ~half a day)

**Every `render-qa/check_*.py` must be covered by at least one test that asserts a
POSITIVE finding.** A checker that cannot be shown to fire is not a gate.

Today: **11 `check_*.py` modules, 4 firing fixtures.** `check_layout`,
`check_slots`, `check_boundaries`, `check_presence`, `check_geometry` have **no
firing test at all**. `check_text` has only a token-import assertion. And **Title
Case — the preference the owner named as "given before and never applied" — is
armed in `check_copy.titlecase()` with zero fixture proving it fires.** That is
precisely the state the conjunction rule was in on 2026-07-28, one day before it
failed him.

Build:

1. `tests/test_firing_coverage.py` — globs `render-qa/check_*.py`, globs the
   tests, and **fails if any checker has no test asserting a positive finding.**
   Mark the test-side association explicitly (e.g. a module-level
   `COVERS = ["check_copy", ...]`) rather than inferring it from imports —
   inference is how `invokers()` got its false negative (§2.8).
2. Write the missing firing tests. Each asserts the checker **returns a finding**
   on a minimal crafted input — not merely that it passes on a good one. Start
   with **Title Case**, then `check_slots`, `check_text` size + restatement,
   `check_boundaries`, `check_geometry`.
3. `check_layout` and `check_presence` need a browser / a rendered MP4 and cannot
   run in the fast tier — see Phase 4 for their tier. Register them in the
   coverage map as `tier: slow` so they are **tracked as uncovered rather than
   silently skipped**. Silent skipping is how `run_tests.py` lost five suites.

**Exit test:** `run_tests.py` fails if you delete any firing assertion; passes
otherwise. Deliberately break `check_copy.titlecase()` and confirm the suite goes red.

### Phase 2 — Arm the orphaned spacing tokens (~half a day)

Closes §2.1 and §2.2 — the hole the repo already believes it closed.

1. **Resolve the 32px question (§2.2) before anything else.** Method: run
   `npx hyperframes inspect` (the pinned CLI `check_layout.py` already uses) against
   the pilot and compare the real browser's geometry for `#kp-rail-label` to
   `boxmodel.py`'s. The browser is the oracle.
   - If `boxmodel` is wrong → fix `boxmodel.py`'s vertical-writing-mode metrics,
     re-run, confirm the pilot is clean.
   - If the breach is real → it is a **template** defect in `scla-points.html`.
     Fix the template, and note that this proves the gate's value in the
     decisions-log entry.
   - Either way, also decide the chrome asymmetry: `_is_footer_chrome` exempts
     bottom bounds but not left/right/top. **Recommended: exempt chrome on all
     four edges** — grading chrome against the *content* keep-out on some axes and
     not others is incoherent.
2. **Wire `check_geometry.py` into `preflight.py`** as a new section, `--static`-safe
   (it needs no render). Follow the existing `run_tool` exit-code pattern exactly —
   do **not** parse its JSON (§4.3).
3. **Add `tests/test_tokens_coverage.py`:** every scalar in design-contract.md's frontmatter
   must have a `tokens.py` accessor **and at least one non-test consumer**. This is
   the mechanism that makes §2.1 non-recurring — a token nobody reads becomes a red test.
4. **Delete the hard-coded literals in `tests/test_gates.py:190-195`** that assert
   `safe_area() == 72`. They are the hand-copy `tokens.py` exists to abolish.
   Replace with the coverage assertion from step 3.
5. Only now, restore the `# LOADED` comment in design-contract.md — it will finally be true.

**Exit test:** change `safe-area` in design-contract.md to `9999`, confirm `preflight.py`'s
verdict changes. That is the proof the token is load-bearing. Revert.

### Phase 3 — Narrow typed findings (enabling only; ~2h)

Needed so Phase 4's mutation assertions key on something stable instead of
brittle substrings. **Scope is strictly limited.**

- **DO:** add a stable `rule_id` (and `severity`) to each checker's own `--json`
  output. Verified safe: **nothing in the repo calls `check_*.py --json`** — those
  nine blocks are dead code today, so changing them has zero blast radius.
- **DO NOT** touch `preflight.py --json`. `sections[].pass` stays a **bool**,
  `sections[].output` stays a **string**, section keys stay `^[a-z_]+$`
  (`scripts/review.sh` and `batch-precheck.sh` scrape them). Add typed data only
  under a *new* sibling key if needed.
- **DO NOT** rewire `preflight.py` to consume checker JSON instead of exit codes.
  Five checkers have no `pass` key at all (`check_layout`, `check_slots`,
  `check_text`, `check_boundaries`, `check_presence` emit `fatal`/`findings`/
  `verdict`/`violations`), so the obvious `json.loads(out).get("pass", True)`
  **silently passes four gates**. Exit codes are the one part of this pipeline that
  has never lied. Leave them alone.
- **DO NOT** print anything to preflight's stdout before the JSON (§2.6).
- **Harden the guard:** remove the `2>/dev/null` on the `jq` call in
  `hyperframe-guard.sh`, or add an explicit shape assertion.

**Exit test — this is mandatory, not optional.** Add `tests/test_guard_contract.py`:

```
For a workspace engineered to FAIL each preflight section in turn:
  1. run  python3 preflight.py --static --json <ws>  as a real subprocess, capturing 2>&1
     exactly as the guard does
  2. assert stdout's FIRST byte is '{'                   -> catches any stray print
  3. run the guard's ACTUAL jq program (extract it from hyperframe-guard.sh; do not
     paste a copy, or the two will drift) and assert it emits a NON-EMPTY string
     naming that section
  4. assert the same pipeline on a CLEAN workspace emits the EMPTY string
  5. assert every section key matches ^[a-z_]+$
```

Step 3 catches the silent-clean failure; step 4 catches the inverse (renaming
`pass` makes *every* clean section look like a violation).

### Phase 4 — Mutation testing over a real full-length plan (~1 day)

This is what actually catches "a checker stopped being a checker." A toy fixture
does **not** — the natural fixture for the conjunction rule is one scene with three
items and no "or", which **fires fine under per-scene scoping**. Scope and sampling
bugs only manifest at real length: a 9-point sampler is harmless on 3 scenes and
misses 16 of 25 on a real video.

**Base fixture.** Commit `tests/fixtures/base/scenes.json` — the **20-scene
2026-07-29 `better-decisions` plan**, the only real full-length gate-clean plan
that exists. **Label it honestly in the fixture manifest: `gate-clean, pending
owner sign-off` — NOT "approved."** No owner-approved plan exists anywhere; all
six published videos predate `build_index.py`.

**Store `scenes.json` only. Rebuild against live `design-system/`.** Verified to
work end-to-end (`build_index.py` → `preflight.py --static`). This is what kills
the rot: a frozen *workspace* hard-fails `composition_freshness` within 24 hours,
and a frozen plan tracks live templates by construction.

**Harness rules — each one is load-bearing:**

1. **Assertions are DIFFERENTIAL and per-rule**: rule R **fires on the mutant**
   AND **does not fire on the baseline**. Never assert global pass/fail — that is
   what let the deleted blip rule go unnoticed, and it is what makes a golden
   corpus rot on unrelated template edits.
2. **The harness must copy `compositions/` into the temp workspace.** Verified:
   without templates, `check_slots` **prints a clean PASS on zero templates**, and
   `check_capacity` / `check_text`-size silently no-op. A corpus that proves
   nothing while going green is worse than none.
3. **Pass `static=True`** to `check_continuity` on uncompiled plans. Without it,
   the placeholder `data-duration="1"` makes it report **18 findings** on a
   gate-clean plan — 100% false positives.
4. Use `tempfile.mkdtemp()`, never the fixed `/tmp` paths `run_tests.py` and
   `test_gates.py` use — those collide under parallel runs.
5. Call checkers **in-process** where possible (~2s added to a 2.2s suite);
   shelling out to `preflight.py` costs 0.65s × N.

**The mutation set — start with the eight that reproduce real history:**

| Mutation | Must fire | Reproduces |
|---|---|---|
| split an enumeration across three scenes (3/2/2) | `check_copy` conjunction | the 2026-07-29 rejection |
| inject a text collision at **scene 15** | `check_layout` / `check_geometry` | the 9-point sampler **and** the `info`-severity discard |
| rename two scenes to `__scene_NN` clones of one family | `check_variety` | the `family()` undercount |
| add a chip restating its heading | `check_text` | echo-chips shipped |
| point two scenes at one shared template | `instance_templates` wiring | 18-of-21 blank render |
| push a card past `frame-padding` | `check_geometry` | the footer breach |
| lowercase a heading | `check_copy` Title Case | the owner's most-repeated grievance |
| blank a declared slot | `check_slots` | template-default fabrication |
| point a `script_match` at a missing script | must **FAIL**, not WARN-and-pass | the silently-disarmed fabrication ban |

**Exit test:** revert `check_copy` to per-scene conjunction scoping and confirm
mutation 1 goes red. That single check is the whole point of the phase.

### Phase 5 — Close the graveyards (report-only; ~half a day)

**Calibrate your expectations: this phase would have prevented approximately
ZERO of the 14 historical recurrences.** It is hygiene, not the fix. Build it
after Phases 1–4, never instead of them.

Why it scores so low: the failures were not unbacked sentences. They were
*missing* sentences (the variety rule was written only into `decisions/log.md` —
"writing it down was treated as shipping it"), *soft-worded* ones (the conjunction
rule said **"prefer"**, which the `NORMATIVE` regex does not match — that is
exactly why it survived), a *contradicting* one (design-contract.md said sentence case, so
the pipeline correctly obeyed design-contract.md and violated the owner), and gates that
were named correctly and did not fire.

Also note: **design-contract.md is not the worst graveyard, it is the only one measured.**
After discounting duplicates it holds ~9 genuinely unarmed statements.
`.claude/skills/render-lessons/SKILL.md` holds **38 normative lines with zero
mechanism annotations and is graded by nothing** — and it is read into every build
subagent's instructions. `decisions/log.md` and `refine-scripts/SKILL.md` hosted
the two most expensive burials on record. Neither is graded.

Build, all **report-only** per STD-38:

1. Add `render-lessons/SKILL.md`, `refine-scripts/SKILL.md`, and `decisions/log.md`
   to `check-enforcement.py`'s `GRADED` list.
2. Fix the auditor's own false negatives (§2.8): the `LINTCHECK` backtick regex
   (one character: `[\s\`]+`), the `.jsonl` gap in `PATHISH`, the six-file
   `invokers()` list (add `hyperframe-guard.sh`, `batch-precheck.sh`), and make
   `invokers()` ignore comment lines.
3. Number the test-suite check in `lint-refs.sh` so the two "check 11" citations
   become verifiable.
4. Widen the line filter beyond `-`/`*`/`|` to any prose line, and parse YAML
   frontmatter comments. Raises recall from ~17% toward ~90%.

**Do NOT flip `--strict`.** It would hard-fail CI on ~115 design-contract.md items on day
one, and the cheapest response is relabelling them `Convention`, which changes
nothing physical. The repo's own doctrine (STD-38) says a drift check starts
non-blocking so it teaches.

**Do NOT attempt the full design-contract.md split** (machine spec + rationale doc) in this
pass. It touches ~20 files that route agents to "read design-contract.md first" — including
a hook string in `.claude/settings.json` — and `preflight.check_title_card`
regex-scrapes the program display-name table out of design-contract.md's **body**, which the
split would move. It is a legitimate follow-up, not part of this build.

---

## 5. Decisions already made — do not re-ask the owner

| # | Decision | Rationale |
|---|---|---|
| 1 | **No JSONL ledger, no escape metric, no dead-gate check, no CI teeth, ever at this N.** | §1. If a future session wants these, it must first show ≥30 owner verdict events exist. Today: 2. |
| 2 | **Nothing in this plan blocks a batch or needs the owner to clear it.** | The queue is 29 videos; measured owner latency 5–8 days; the 25-firing wall is precedent. Every new failure mode is a red test with an agent-fixable remedy. |
| 3 | **Base fixture is labelled `gate-clean, pending sign-off`, never `approved`.** | No approved plan exists. Overclaiming provenance is how `test_variety.py`'s fixture ended up pinning a fabricated 43%. |
| 4 | **Title Case wins over design-contract.md's sentence-case `title` line.** | It is the owner's stated preference and what `check_copy` already enforces. |
| 5 | **design-contract.md is corrected, not deleted or split, in this pass.** | The split is real work with a 20-file blast radius and a live parser dependency. Sequencing it after the firing mandate costs nothing. |
| 6 | **Where code and doc disagree, the CODE is authoritative** (Phase 0). | Every drift found was the doc going stale after a deliberate recalibration. |

**OWNER CALL 1 — the pilot still needs sign-off.** `bash scripts/preview.sh
better-decisions-come-from-better-criteria_early-career-boost_2026-07-29`. This has
rolled forward unresolved across four snag-log entries. Phase 4 uses that plan as
its base fixture regardless; sign-off is not a prerequisite for the build.

**OWNER CALL 2 — if Phase 2 step 1 finds the rail-label breach is real**, it is a
template fix to `scla-points.html`, which changes the pilot's pixels and may
warrant a re-preview. Default: fix the template, re-run gates, flag it at the next
preview rather than blocking.

**OWNER CALL 3 — the ripples/in-place-motion ban (§2.9) is still unarmed and was
violated in published work.** It is a *motion* rule, and the honest options are
(a) arm it as a real check in `check_presence`'s neighbourhood, (b) route it to the
`/adversarial-qa` vision lanes as an explicit rubric item, or (c) mark it
`Convention` out loud so it stops reading as an enforced rule. Default if the owner
is unreachable: **(c) plus a tracked follow-up** — labelling it honestly is strictly
better than leaving a violated rule wearing an enforcement costume. Do not silently
drop it.

---

## 6. Verification checklist — the build is done when all of these pass

- [ ] `run_tests.py` green **from a fresh clone** (proves §2.3 is fixed)
- [ ] `python3 scripts/check-enforcement.py` → **0 broken claims**
- [ ] Deleting any firing assertion turns `run_tests.py` red (Phase 1)
- [ ] Breaking `check_copy.titlecase()` turns the suite red (Phase 1)
- [ ] Setting design-contract.md `safe-area: 9999` changes `preflight.py`'s verdict (Phase 2)
- [ ] Reverting `check_copy` to per-scene conjunction scoping turns mutation 1 red (Phase 4)
- [ ] `hyperframe-guard.sh` still reports violations on a failing plan **and** stays silent on a clean one, asserted by `test_guard_contract.py` running the guard's real `jq` program (Phase 3)
- [ ] `preflight.py --json` shape unchanged: `sections[].pass` bool, `sections[].output` string, keys `^[a-z_]+$`
- [ ] The 2026-07-29 pilot still passes every gate end to end (no new false blocks)
- [ ] `decisions/log.md` entry written: why the telemetry design was rejected, what replaced it, and the doctrine in §0

---

## 7. If you are tempted to build the ledger anyway

Read §1 again, then answer these three questions with evidence from the repo:

1. How many owner verdict events exist? (Answer today: **2**, both the same lesson.)
2. How many approved videos has the current gate stack ever seen? (Answer: **0**.)
3. What does your escape metric return for the 18-of-21 blank render, the
   `info`-severity layout collision, and the `family()` undercount? (Answer:
   **"not an escape — a gate saw it"** on all three, and **"alive and healthy"**
   from the dead-gate report.)

If those answers have changed, revisit. If they have not, the answer is still no.
