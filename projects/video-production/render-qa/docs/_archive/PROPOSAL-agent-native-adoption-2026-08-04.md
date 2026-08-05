# PROPOSAL — Adopting agent-native rendering: decouple first, retire last

**Date:** 2026-08-04 · **Branch:** `experiment/agent-native-hyperframe-m2` ·
**Status:** proposal, awaiting owner decision · **Audience:** the owner, and a
fresh session with no memory of the conversation that produced this.

**Depends on two documents; read neither to understand this one, both to audit it:**

- `experiments/agent-native-m2/PROVENANCE.md` — what the template-free build
  consumed, ran, produced, and deliberately did not touch.
- `render-qa/docs/HANDOFF-agent-native-verdict-2026-07-30.md` — the verified
  per-module survives/dies table, and the measured reason nothing was archived.

Every number in this proposal is quoted from those two, not re-derived. Where
this document proposes something new it says **proposed**, and where it makes a
claim it names where the claim was measured.

---

## 1. The decision being asked for

**Adopt the agent-native authoring method. Retire nothing yet. Spend the next
unit of work decoupling the gates from the compiler, because that work pays for
itself on the pipeline shipping videos today whether or not agent-native is ever
adopted.**

That third sentence is the whole proposal. Everything below is the reasoning for
it and the order of operations it implies.

---

## 2. The finding that reframes the question

The experiment was run to test whether templates were making videos come out
badly. The answer is yes — but the verification found something more useful, and
it changes what "removing the templates" costs.

**The gates are welded to the compiler, not to the templates.**

Eight checkers reach a build through one function, `hfp_common.parse_scenes()`.
It finds scenes by `data-composition-src` — which is HyperFrames contract — and
then reads their content out of `data-narration` and `data-variable-values`,
which are **not**. Those two attributes are `build_index.py`'s private authoring
protocol. Retire the compiler and every consumer keeps running, keeps exiting 0,
and keeps grading nothing.

Measured, same tool, two builds (HANDOFF §1):

| | template build | agent-native build |
|---|---|---|
| `parse_scenes()` → scenes | 27 | **3** |
| …carrying `data-narration` | 27 | **0** |
| …carrying `data-variable-values` | 27 | **0** |

`check_copy.py` — the enforcer for the standing owner preferences, the rules
given more often than any other — printed `COPY: PASS` having graded **zero of
24 narration beats and zero on-frame strings**.

This is the `nothing-graded` failure mode the repo has now hit four separate
times (`check_capacity` on `scla-loop`; `check_geometry` on the orphaned
`</circle>`; `hyperframe-guard.sh` invoking a moved path; `check_text`'s floor
set at the smallest size in use). A gate that passes because it looked at nothing
is the most expensive shape of bug in this pipeline's history.

**Why this reframes the decision:** the coupling is a latent defect in the
*current* pipeline, not a cost of the new one. Any future change that touches the
authoring format — a template refactor, a schema change, a second compiler —
walks into the same trap. Fixing it is not a bet on agent-native. It is
maintenance that agent-native happened to expose.

---

## 3. Why the method is worth adopting

From `PROVENANCE.md` §7, the four reasons the build came out different, with the
two that speak directly to "forced into a template":

1. **One concept carried the whole runtime.** The 2×2 map is built once and never
   left, across 3:20. A per-scene template library cannot express this, because
   each scene there is an independent card. This is not a polish difference; it
   is a class of video the current system cannot make.
2. **The layout was designed for this content**, so copy was never squeezed into
   a slot that pre-existed it. The template path inverts this: the slot is fixed
   and the sentence bends.
3. Real HeyGen word timestamps drove the reveals — every arrival pinned to the
   syllable that earns it, rather than to a scene boundary.
4. Motion doctrine over motion inventory — sequential reveal timed to the VO, one
   ambient breath on the background, nothing settled re-animating.

**And the honest cost, stated by the experiment itself:** none of the
deterministic gates ran. Correctness rested on `npx hyperframes check` plus 34
hand-reviewed stills — weaker coverage than `preflight.py` + `verify_render.py`
provide. The experiment named this as the main thing to weigh, and this proposal
treats it as the thing to fix rather than the thing to accept.

---

## 4. Why "retire nothing yet" is a measurement, not caution

The archive step was tested, not reasoned about. The six candidate modules
(`boxmodel`, `check_capacity`, `check_slots`, `check_variety`, `build_index`,
`instance_templates`) were moved out of `src/`, CI was run, and they were moved
back (HANDOFF §4):

| Gate | Baseline | Six archived |
|---|---|---|
| `lint-refs.sh` check 10 (`check-enforcement.py`) | exit 0 | **exit 1 — 13 broken claims** |
| `lint-refs.sh` check 11 (`run_tests.py`) | exit 0 | **exit 1 — 10 of 15 test files break** |
| `preflight.py --static` on a live workspace | PASS | **FAIL — 4 sections can't open file** |

`lint-refs.sh` runs on every push, so that is a red branch, not a warning. And
the referent is still live: **13 workspaces under `renders-hyperframes/` plus the
entire `design-system/` template set are on the template path today.** Archiving
now disarms the pipeline that is actually shipping videos, in exchange for a
freeform path that does not yet exist.

The brief's own Phase 4 already said this — *"a checker with no referent is worse
than no checker."* The verification confirmed it with exit codes.

---

## 5. The proposal — seven steps, in this order

Each step states the reasoning, what it costs, and what makes it done. Steps 1–4
are additive: they do not touch the template path and cannot break a shipping
build. Steps 5–7 are the actual migration.

### Step 1 — Give the copy gates a beat source that is not the compiler

**Do:** teach `hfp_common` to read an alternate beat manifest —
`audio_request.json` → `lines` is the obvious candidate, since it already exists
in the agent-native build and is the engine's own input contract. Re-point
`check_copy.py` and `check_continuity.py` to consume it when
`data-narration` is absent.

**Why first:** it is the stated blocker for everything downstream (HANDOFF Test
B, and Test C is explicitly blocked on it). It is also the step with the
strongest independent justification — the conjunction rule already *wants* to
live upstream of synthesis, where a violation costs a text edit rather than a
re-synthesis and a re-render. The rules file already concedes this: the
script-mode grading exists precisely because "a render-stage gate can only report
it after a video exists."

**Done when:** a firing test asserts both checkers **FAIL** on the agent-native
build's real narration. Per this repo's `test_firing_coverage` discipline, a gate
that has never been *seen* to fire is not armed — and re-pointing a gate that
currently grades nothing is exactly the case where a PASS proves nothing.

**Record the outcome either way:** does `check_copy` find anything in the
agent-native narration? It has never been graded. A clean result is a finding; so
is a dirty one.

### Step 2 — The one-line `check_motion` fix

**Do:** widen `compositions()` past its `scla-*.html` glob. Measured: copy the
three agent-native comps to `scla-*.html` names and the checker grades **26
tweens and correctly passes** — the build has zero `repeat`/`yoyo`. The
capability is intact; only the file-discovery pattern is template-shaped.

**Also decide:** what replaces the `DECORATIVE` substring allow-list, which
encodes SCLA template naming conventions (`ghost`, `ring`, `-bg`, …) that
agent-authored HTML will not follow. Left alone, it either over-blocks legitimate
ambient motion or silently exempts nothing.

**Why now:** it is nearly free, and the in-place keep-alive motion ban is
recorded as the repo's most-violated rule. Leaving its enforcer blind on the new
path re-opens the rule that has cost the most to close.

**Done when:** a hand-planted `repeat: -1` tween in a copy of `map.html` makes it
FAIL.

### Step 3 — Rehome the three orphaned owner rules

Three rules currently have a mechanism and would have none after the retirement.
**Do not retire the owning file until the rule has somewhere to live** (HANDOFF
§3):

1. **`one-item-list` / `one-card`** (`check_variety` rules 1, 1b). `check_diversity`
   is a perceptual hash of beat midpoints — it structurally cannot express "a list
   slot with exactly one item is a defect."
2. **`placeholder-slot`** (`check_slots`). A string scan for `[[…]]`, `…`, TODO,
   TBD, xxx. This is a **fabrication-ban guard**, not template mechanics, and it
   dies silently with the file it happens to live in. It re-points trivially.
3. **Plan-stage fit** (`check_capacity`). Today's cheapest gate: it fails a
   too-long string while the fix is still a JSON edit. The runtime probe replaces
   it with a browser pass, which by definition cannot run before the HTML exists.

**Why this is non-negotiable:** the operating principle here is that a preference
isn't real until it's a checker — prose rules have failed repeatedly in this
repo, which is why `check-enforcement.py` exists at all. A retirement that drops
a rule to prose is a regression even when the video quality improves.

### Step 4 — Land the ink-band gate properly

**Do:** promote `experiments/agent-native-m2/spikes/ink_bands.py` into
`render-qa/src/`, move its brandline chrome region into `tokens.yml` (not a
command-line flag), put its fixture in `render-qa/tests/`, and call it from
`preflight.py`.

**Why it's ready:** it is already built and validated against this repo's own
discipline — clean passes, planted defects fire, and the two rules genuinely
discriminate rather than one shadowing the other (HANDOFF §5 A3):

| Frame | safe | pad | footer | Verdict |
|---|---|---|---|---|
| 21 real stills, agent-native | 0 | 0 | 0 | **PASS** |
| text planted at y=1000 (below content-bottom 960) | 9047 | — | 9658 | **FAIL** ✔ |
| text planted at x=20 (inside the 72px keep-out) | 663 | 1280 | 0 | **FAIL** ✔ |
| text planted at x=80 (between safe-area and padding) | **0** | 387 | 0 | **FAIL** ✔ |

It answers "is there ink where there must not be" from rendered pixels — no CSS
model, no font metrics, no framework internals — which is why it works on
freeform HTML where `boxmodel.py` does not.

**Check first:** whether `test_firing_coverage.py` requires every checker in
`src/` to have a firing test. If so the fixture lands in the same commit or CI
goes red.

**Stated limit, not hidden:** a pixel gate cannot tell label-class chrome from
body content. The brandline sits 8px inside the keep-out, which the design
contract grants it by name — so that region must be **declared**, never tolerated
by a loosened threshold.

### Step 5 — Fix the four silent coverage collapses

These are the ones the original brief scored as "survives, unchanged" and the
verification found lose coverage without saying so:

| Module | What collapses | Fix |
|---|---|---|
| `check_layout.py` | `scene_times()` samples one point per composition clip: **27 → 3** samples for a *longer* video — worse than the 9-point `npm run check` it replaced | sample per **beat** (`timing.json`), not per clip |
| `verify_render.py` | 3 frames/scene → **81 → 9** stills for 200s, one per 22s | frames per beat; container truth and the `qa/VERIFIED` marker are unaffected |
| `check_presence.py` | no `narration.words.json` → `words = []` → **every** ≥3s static run becomes gradeable regardless of speech: stricter *and* blind | an `audio_meta.json` adapter |
| `check_boundaries.py` | exits 2 — wants `narration.wav` + a flat words file; agent-native has 24 clip wavs | an adapter; **`FINAL_HOLD = 1.8` must move with it** or the ending floor the owner rejected twice goes unenforced |

**Why before the A/B:** without these, a comparison between the two paths
measures the gates rather than the method. That is the wrong experiment.

### Step 6 — The A/B (the brief's Phase 3)

Three lessons, both paths, same refined scripts, compared at the pilot gate.
Blocked on steps 1–5 for the reason above. Geometry is no longer a blocker:
`hyperframes check`/`inspect` sampled per beat plus the ink-band gate together
cover it for a freeform build.

### Step 7 — The archive commit

Only after 6. One commit, containing all of it or CI goes red — HANDOFF §5 Test D
is the checklist. Note `repo-hygiene.md` makes **deletion, not `_archive/`**, the
default disposition: git history is the archive.

---

## 6. What this proposal deliberately does not propose

- **A DOM-rect probe.** The brief's "build one runtime probe" is blocked:
  `bundleProjectHtml` is internal to `dist/cli.js` and unexported, and the studio
  serves compositions only through one API route. It is also **not needed** —
  `inspect` answers "does text land on text" and ink-bands answers "does ink
  cross a keep-out band."
  **Keep the trap on record:** the probe as built reported **1760 findings**, all
  artifacts of a harness serving unstyled HTML. It produced a plausible, precise,
  enormous finding list *from a page that was not the page*, and was caught only
  by checking a computed font-size against the CSS. Any future probe needs that
  assertion as a self-test before its output is believed.
- **Retiring `boxmodel.py` early.** Its retirement is now supported by
  measurement rather than argument — 281 findings (279 `text-collision`) against
  the inspector's 0 at the same instants, on a build verified clean across 34
  stills. It is confidently wrong, not merely blind. But it is still load-bearing
  for 13 live workspaces, so it goes in step 7 with the rest.
- **Making freeform the default.** See §7.

---

## 7. Owner calls

Both carry a safe default, already chosen in the handoff. **Proposed: take both
defaults unless overridden in writing.**

1. **Does a freeform build take a stem?** *Default: yes* — freeform builds live
   under `renders-hyperframes/<base>` and keep the `mkdir` build lock. The lock
   prevents two builders colliding on one lesson; it has nothing to do with
   templates. The experiment sat in `experiments/` and therefore never took it.
2. **Does the pilot gate tighten?** *Default: freeform stays opt-in
   (`--freeform`) and never becomes the AUTO-BATCH default* until
   `check_diversity` plus the vision pass can quarantine a weak build on their
   own. Removing templates removes the flat quality floor that makes unattended
   batching safe — the pilot gate stops being a formality on the freeform path.

---

## 8. The main risk, named

**Agent-authored HTML has no floor.** The template library's real function was
never quality — it was *variance suppression*. Every card was mediocre and no
card was broken. Freeform authoring raises the ceiling (§3) and removes the
floor at the same time, and the deterministic gates that would have caught the
floor falling out are exactly the ones this migration re-points or retires.

That is why the order matters more than the destination: steps 1–5 rebuild the
floor on measurable ground *before* step 7 removes the old one, and step 6 is the
evidence that the new floor holds. Reordering — retiring first and re-arming
after — is the failure mode, and it is the one the archive test in §4 already
demonstrated in miniature.

---

## 9. Recommended next action

**Step 1.** It is self-contained, additive, does not touch the shipping path, is
the stated blocker for every later step, and its value survives even if the
answer to agent-native adoption turns out to be no.
