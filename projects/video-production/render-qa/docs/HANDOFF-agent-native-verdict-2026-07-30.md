# HANDOFF — Agent-native rendering: the verified module verdict

**Date:** 2026-07-30 · **Branch:** `experiment/agent-native-hyperframe-m2` ·
**Status:** verification COMPLETE · archiving DEFERRED (measured blocker, §4) ·
**Audience:** a fresh session with no memory of the conversation that produced this.

Read top to bottom before touching anything. Self-contained. Every number below
was measured, not reasoned — the commands that produce them are in §6 and each
one re-runs in under two minutes.

---

## 0. What was asked, and what changed

`experiments/agent-native-m2/PIPELINE-IF-ADOPTED.md` proposes replacing the
template library + static box model with agent-authored HTML + a runtime probe.
It carries a per-module survives/dies table and this caveat on itself:

> the per-module verdicts below are reasoned from that rules file's own
> description of what each checker does plus `ls render-qa/src/`; I did not read
> all 22 modules' source. **Treat the survives/dies column as a proposal to
> verify, not a finding.**

The owner asked for the verdicts to be verified and the recommended elements
archived. **All 22 modules were read and every one was executed against the
agent-native build.** The verification changed the table in four places and
found the archive step blocked. Nothing was archived. Nothing in `render-qa/src/`
was modified — the tree is exactly as it was.

### The one-line summary

The brief's split — *"gates that encode owner preferences survive; gates that
encode template mechanics die"* — is **directionally right and wrong about which
side `check_copy.py` is on.** `check_copy.py` is called out in the brief as "the
owner-preference enforcer, and it is template-independent". It is not
template-independent. It reads `data-narration` and `data-variable-values`, both
of which `build_index.py` writes. Run against the agent-native build it prints
`COPY: PASS` having graded **zero of 24 narration beats and zero on-frame
strings**.

That is the `nothing-graded` failure mode this repo has now hit four separate
times (`check_capacity` on `scla-loop`; `check_geometry` on the orphaned
`</circle>`; `hyperframe-guard.sh` invoking a moved path; `check_text`'s floor
set at the smallest size in use). A gate that passes because it looked at nothing
is the single most expensive shape of bug in this pipeline's history, and the
adoption plan as written reintroduces it on the rule the owner has given more
often than any other.

---

## 1. The coupling nobody named

Eight checkers reach the build through one function: `hfp_common.parse_scenes()`.
It finds scenes by `data-composition-src` and reads content out of
`data-narration` + `data-variable-values`.

Those three attributes are not HyperFrames contract. `data-composition-src` is —
the other two are **`build_index.py`'s private authoring protocol**. Retire the
compiler and every consumer keeps running, keeps exiting 0, and keeps grading
nothing.

Measured, same tool, two builds:

| | template build (`m2_four-kinds…`) | agent-native (`agent-native-m2`) |
|---|---|---|
| `parse_scenes()` → scenes | 27 | **3** |
| …carrying `data-narration` | 27 | **0** |
| …carrying `data-variable-values` | 27 | **0** |
| runtime | 149s | 200.5s |
| real narration beats | 27 | 24 (`audio_request.json` → `lines`) |

Every downstream number follows from that row. This is the thing to fix first,
and it is upstream of the probe: **re-point `parse_scenes` (or give the
agent-native build a beat manifest the checkers can read) before building
anything else**, or the new pipeline ships with its copy rules disarmed.

---

## 2. The verified verdict table

Changes from the brief are in **bold**. "Evidence" is the observed behaviour, not
an argument.

| Module | Brief | **Verified** | Evidence |
|---|---|---|---|
| `hfp_common.py` | survives (plumbing) | **survives — and is the hidden coupling** | `parse_scenes()` is the single point through which 8 checkers silently grade nothing (§1) |
| `check_copy.py` | survives, unchanged | **RE-POINT — currently grades 0** | `COPY: PASS` on 24 beats / ~40 on-frame strings. Reads `data-narration` + `data-variable-values` |
| `check_continuity.py` | re-point | re-point ✔ | `CONTINUITY: PASS`, vacuous — every rule needs `narration`, which is `None` |
| `check_motion.py` | rewrite, gets stronger | **RE-POINT — one-line glob fix, not a rewrite** | `compositions()` globs `scla-*.html` only → "no compositions, nothing to grade", exit 2. Copy the 3 comps to `scla-*.html` and it grades **26 tweens and correctly PASSES** (build has zero `repeat`/`yoyo`) |
| `check_text.py` | rewrite | **SPLIT: size survives, restate retires** | size half fired and found a **real** defect — `map.html .plate-name` at 38px vs the 40px floor. restate half graded 0 lines |
| `check_geometry.py` | rewrite | rewrite ✔ **— more urgent than stated** | **281 findings** (279 `text-collision`) on a build verified clean across 34 stills. Not "cannot grade" — *confidently wrong* |
| `boxmodel.py` | retire | retire ✔ **— sharper root cause** | Not merely "arbitrary CSS": `is_present()` is driven **only** by `data-present-if`, and boxmodel has **no concept of time**. The agent-native build reveals content by animating `opacity` on absolutely-positioned overlays stacked at identical coordinates, so it grades three time-multiplexed panels as simultaneously visible |
| `check_capacity.py` | retire | retire ✔ | `CAPACITY: PASS`, vacuous — bind map empty (no `data-slot`, no `maxLines` schema). **Cost: this is the only plan-stage fit check; the probe needs a browser** |
| `check_slots.py` | retire | **retire, but ONE rule must be rehomed** | Vacuous PASS. `placeholder-slot` (`[[…]]`, `…`, TODO, TBD, xxx) is a **fabrication guard**, not template mechanics, and dies silently with the file |
| `check_variety.py` | retire, replaced by `check_diversity` | **retire — but rules 1 and 1b are left UNOWNED** | `FAIL (6)`, all meaningless (0% artwork, 71% one "form"). A perceptual-hash diversity gate has no opinion about `one-item-list` or `one-card`, which are standing owner preferences, not template proxies |
| `build_index.py` | retire | retire ✔ **— takes the authoring-time guard with it** | `scripts/hyperframe-guard.sh` exists to compile `scenes.json` → `index.html` and re-grade on every write. The whole plan-stage loop is template-shaped |
| `instance_templates.py` | retire | retire ✔ | Sole purpose is one-template-file-per-slot |
| `textmetrics.py` + `metrics.json` | demote | demote ✔ | Keep the file **and** `test_variety.py`'s `lineHeight` assertion — nothing else pins it |
| `check_layout.py` | survives | **survives, coverage COLLAPSES** | `scene_times()` samples one point per composition clip: **27 → 3** samples for a *longer* video. Worse than the 9-point `npm run check` it was built to replace. Must sample per **beat** (`timing.json`), not per clip |
| `verify_render.py` | survives, unchanged | **survives, coverage COLLAPSES** | 3 frames/scene: **81 → 9** stills for 200s (one per 22s). Container truth + `qa/VERIFIED` marker unaffected |
| `check_presence.py` | survives, unchanged | **survives, stricter AND blind** | `words_from()` finds no `narration.words.json` → `words = []` → `not words` makes **every** ≥3s static run gradeable regardless of speech. Needs an `audio_meta.json` adapter |
| `check_boundaries.py` | survives, gets easier | **survives only with an adapter** | exit 2. Wants `narration.wav` + a flat words file; agent-native has 24 clip wavs + `audio_meta.json` |
| `preflight.py` | survives, re-sectioned | survives, re-sectioned ✔ | — |
| `tokens.py` | survives, shrinks | **survives, barely shrinks** | `programs_problems()`, `retired_names()`, `min_size()` and all four spacing tokens still have consumers. `test_tokens_coverage.py` fails if any accessor loses its last non-test consumer, so retiring a consumer forces a `tokens.py` edit **in the same commit** |
| `stem.py` | survives | survives ✔ | No template coupling. Note `is_canonical("agent-native-m2") == True`, so the experiment's own name would pass check 12 — but it sits outside `renders-hyperframes/`, so the `mkdir` build lock never applied. **Open: does a freeform build take a stem?** |
| `compile_timeline.py` → `plan_timing.py` | transform | transform ✔ | Output shape already proven — `timing.json` exists and was computed once from `audio_meta.json` |
| `synth_narration.py` → thin adapter | transform | transform ✔ | Already demonstrated: the experiment called `audio.mjs` directly. **`FINAL_HOLD = 1.8` must move into the adapter** or the ending floor the owner rejected twice goes unenforced |

**Net, corrected:** 6 retire · 1 demote · 1 rewrite · 1 split · 3 re-point ·
2 transform · 8 survive.
Brief said 6 / — / 4 / — / 1 / 2 / 10. Retire and transform held exactly. The
"10 survive" is the wrong number: **3 of them need real work and 4 more silently
lose coverage.**

---

## 3. Three gaps the brief's replacement plan does not cover

Each is an owner preference that currently has a mechanism and would have none.
Do not retire the owning file until the rule has somewhere to live.

1. **`one-item-list` / `one-card`** (`check_variety` rules 1, 1b). "A list slot
   with exactly one item is a defect — never render a single bullet."
   `check_diversity` (perceptual hash of beat midpoints) cannot express this.
2. **`placeholder-slot`** (`check_slots`). Placeholder text reaching the frame is
   a fabrication-ban violation. It is a string scan over on-frame copy and
   survives re-pointing trivially — it just has to be moved, not dropped.
3. **Plan-stage fit** (`check_capacity`). Today's cheapest gate: it fails a
   too-long string while the fix is a JSON edit. The probe replaces it with a
   browser pass, which cannot run before the HTML exists. The brief acknowledges
   this for geometry; it applies to capacity identically.

---

## 4. Why nothing was archived — measured, not argued

The brief's own Phase 4 says: *"Retire the six template-shaped checkers in the
same pass that retires the templates, never before — a checker with no referent
is worse than no checker."*

That was tested. The six candidates (`boxmodel`, `check_capacity`,
`check_slots`, `check_variety`, `build_index`, `instance_templates`) were moved
out of `src/`, CI was run, and they were moved back. Result:

| Gate | Baseline | Six archived |
|---|---|---|
| `lint-refs.sh` check 10 (`check-enforcement.py`) | exit 0 | **exit 1 — 13 broken claims** |
| `lint-refs.sh` check 11 (`run_tests.py`) | exit 0, all pass | **exit 1 — 10 of 15 test files break** |
| `preflight.py --static` on a live workspace | PASS | **FAIL — 4 sections print `can't open file`** |

`lint-refs.sh` runs on every push (`.github/workflows/lint-refs.yml`), so this
is a red branch, not a warning.

**The 13 broken claims** — docs that would be promising a mechanism that no
longer exists:

```
.claude/rules/video-production.md:17,39            check_variety.py
.claude/rules/video-production.md:21               check_capacity.py
.claude/rules/video-production.md:22,40            boxmodel.py
.claude/rules/video-production.md:30,37,40         check_slots.py
design-system/docs/design-contract.md:311,318,320,323,340   check_variety.py
```

**The 10 breaking test files:** `test_build_index`, `test_enforcement_audit`,
`test_firing_coverage`, `test_gates`, `test_guard_contract`, `test_motion`,
`test_mutations`, `test_script_match`, `test_typed_findings`, `test_variety`.

**The 4 disarmed preflight sections:** `instance_templates`, `slots`, `variety`,
`capacity` — plus `geometry`, which fails on the `boxmodel` import.

And the referent is still live: **13 workspaces under `renders-hyperframes/`
plus the whole `design-system/` template set are on the template path today.**
Archiving now disarms the pipeline that is actually shipping videos in exchange
for a freeform path that does not exist yet.

**Verdict: the archive step is correctly gated behind Phase 3, exactly as the
brief says. It is one commit, and §5 Test D is its checklist.** Note also that
`.claude/rules/repo-hygiene.md` makes deletion — not `_archive/` — the default
disposition when that commit lands: git history is the archive.

---

## 5. Test A was run. Results, and what they changed.

Spikes live in `experiments/agent-native-m2/spikes/`. They are **not** wired into
`preflight.py` and no doc claims they are.

### A1 — the browser inspector, sampled per BEAT (the decisive number)

```
npx hyperframes@0.7.79 inspect . --json --at <24 beat midpoints>
  →  ok: true, issueCount: 0, errorCount: 0
check_geometry.py experiments/agent-native-m2
  →  FAIL (281)   — 279 text-collision, 1 safe-area, 1 padding
```

**0 against 281, same build, same moment.** Reading the CSS confirms the cause on
both counts: `.pnl-line + .pnl-line { margin-top: 34px }` is flow-stacked and
`.step-text` is `flex: 1 1 auto; max-width: 1420px`, so boxmodel put three lines
at one origin and computed a right edge of x=2122 on a 1920px canvas. The static
model does not just fail to grade — it is confidently wrong at scale.

### A2 — the DOM probe as the brief specifies it: BLOCKED, and it lied first

`probe_geometry.mjs` (puppeteer-core + the pinned Chrome + the runtime IIFE) runs
and dumps rects, ink boxes from `Range.getClientRects()`, effective opacity and
computed type. Graded, it reported **1760 findings — worse than boxmodel.**

Every one was an artifact of the harness. `#op-line1` reported `font-size: 16`,
the UA default: a hand-rolled static server serves the files but skips the CLI's
`bundleProjectHtml()` step, so sub-composition `<style>` blocks inside
`<template>` were never scoped and adopted. The page measured was unstyled.

**`bundleProjectHtml` is internal to `dist/cli.js` and is not exported** — the
package has no `main` and no `exports`. The studio serves the composition only
through `/api/projects/<id>/preview/`; every plain route falls through to the SPA
shell. So a DOM-rect probe must either re-implement framework bundling (fragile,
and it would have to track upstream) or wait for an upstream geometry dump.

Recorded because it is the trap: **the probe produced a plausible, precise,
enormous finding list from a page that was not the page.** It was caught only by
checking a computed font-size against the CSS. Any future probe needs that
assertion as a self-test before its findings are believed.

### A3 — the bounds rules, from real pixels: BUILT AND VALIDATED

Pivot that works today: the three bounds rules (safe-area, frame-padding,
content-bottom) ask "is there ink where there must not be", which is answerable
from the rendered frame with no CSS model, no font metrics and no framework
internals. `spikes/ink_bands.py` detects ink as **local contrast** (a glow or a
faint grid varies smoothly; glyph edges do not), applies `check_geometry`'s own
`TOLERANCE = 6`, and reads its bands from `tokens.py`.

Firing fixture, this repo's own discipline — clean must pass, planted defects must fire:

| Frame | safe | pad | footer | Verdict |
|---|---|---|---|---|
| 21 real stills, agent-native | 0 | 0 | 0 | **PASS** |
| text planted at y=1000 (below content-bottom 960) | 9047 | — | 9658 | **FAIL** ✔ |
| text planted at x=20 (inside the 72px keep-out) | 663 | 1280 | 0 | **FAIL** ✔ |
| text planted at x=80 (between safe-area and padding) | **0** | 387 | 0 | **FAIL** ✔ |

The last row is the one that matters: it fires `padding-breach` and **not**
`safe-area-breach`, so the two rules genuinely discriminate rather than one
shadowing the other.

**Known limit, stated not hidden:** a pixel gate cannot tell label-class chrome
from body content. The brandline sits at y≈64, 8px inside the 72px keep-out,
which the design contract grants it by name — so the region has to be *declared*
(`--allow-region 110,55,560,105`), never tolerated by a loosened threshold. Before
this lands, that region belongs in `tokens.yml`, not on a command line.

### What A changed about the plan

The brief's "build one runtime probe" is **two gates, and one of them already exists**:

| Question | Replacement | Status |
|---|---|---|
| does text land on text? | `hyperframes check`/`inspect`, sampled per **beat** | exists — `check_layout.py` already wraps it; the fix is sampling per beat instead of per clip (27 → 3 on a *longer* video, §2) |
| does ink cross a keep-out band? | `spikes/ink_bands.py` on snapshot stills | built, validated, needs the chrome region tokenised |
| where is every box? | DOM-rect probe | **blocked** on unexported framework bundling — and not needed for either rule above |

`boxmodel.py`'s retirement is now supported by measurement rather than argument.
It is still gated behind §4.

### Test B — firing proof for the three re-points

Cheap, and follows this repo's own `test_firing_coverage` discipline: a gate
that has never been *seen* to fire is not armed.

- `check_motion.py`: widen `compositions()` past the `scla-*.html` glob. Then
  hand-add a `repeat: -1` tween to a copy of `map.html` and assert it FAILS.
  Also decide what replaces the `DECORATIVE` substring allow-list, which encodes
  SCLA template naming (`ghost`, `ring`, `-bg`, …) that agent HTML will not follow.
- `check_copy.py` + `check_continuity.py`: give them a beat source that is not
  `data-narration` — `audio_request.json` → `lines` is the obvious one, and it is
  upstream of synthesis, which is where the conjunction rule already wants to be.
  Assert both FAIL on the agent-native build's real narration.

Expected outcome to record: does `check_copy` find anything in the agent-native
narration? It was never graded.

### Test C — the A/B (the brief's Phase 3)

Three lessons, both paths, same refined scripts, compared at the pilot gate.
Blocked on B — without it the freeform arm has no working copy gate, so the
comparison would measure the gates, not the method. A is no longer a blocker:
A1 and A3 together cover geometry for a freeform build.

Before C, land A3 properly: `spikes/ink_bands.py` → `render-qa/src/`, its chrome
region into `tokens.yml`, its fixture into `render-qa/tests/`, and a call from
`preflight.py`. Check first whether `test_firing_coverage.py` requires every
checker in `src/` to have a firing test — if so, the fixture lands in the same
commit or CI goes red.

### Test D — the archive commit (blocked on C)

One commit, and it must contain all of this or CI goes red:

- [ ] `git rm` the six (deletion, not `_archive/` — repo-hygiene)
- [ ] Rehome the three §3 rules first
- [ ] Rewrite the 8 rule annotations in `.claude/rules/video-production.md` and
      the 5 in `design-contract.md` to name a mechanism that exists, or say
      `Convention` out loud
- [ ] Delete or re-point the 10 test files
- [ ] Re-section `preflight.py`; retire `scripts/hyperframe-guard.sh` or
      re-point it at the new plan artifact
- [ ] `scripts/batch-prepare.sh` references `build_index` / `check_slots`
- [ ] Fix `tokens.py` accessors that lose their last consumer
      (`test_tokens_coverage.py` will name them)
- [ ] `bash scripts/lint-refs.sh` green before push

---

## 6. Reproducing every number above

```bash
cd projects/video-production

# §1 — the coupling
python3 -c "
import sys; sys.path.insert(0,'render-qa/src')
from hfp_common import parse_scenes
for w in ['renders-hyperframes/m2_four-kinds-of-career-transition_mid-career-momentum',
          'experiments/agent-native-m2']:
    sc = parse_scenes(open(w+'/index.html').read())
    print(len(sc), sum(1 for s in sc if s['narration']), sum(1 for s in sc if s['variables']))"

# §2 — every checker against the agent-native build
for m in check_copy check_continuity check_variety check_slots check_capacity \
         check_geometry check_motion check_text check_boundaries; do
  echo "== $m"; python3 render-qa/src/$m.py experiments/agent-native-m2 2>&1 | tail -3
done

# §2 — check_motion is a GLOB problem, not a capability problem
T=$(mktemp -d); mkdir -p $T/compositions
for f in experiments/agent-native-m2/compositions/*.html; do
  cp "$f" "$T/compositions/scla-$(basename $f)"; done
python3 render-qa/src/check_motion.py $T          # 26 tweens, PASS

# §2 — geometry findings by rule
python3 render-qa/src/check_geometry.py experiments/agent-native-m2 --json \
 | python3 -c "
import json,sys,collections
d=json.load(sys.stdin)
print(collections.Counter(f['rule_id'] for f in d['findings']))
print('graded', d['report']['graded'], 'unplaced', d['report']['unplaced'])"

# §4 — the archive breakage (moves files OUT, then puts them BACK)
cd render-qa/src && H=$(mktemp -d)
for m in boxmodel check_capacity check_slots check_variety build_index \
         instance_templates; do mv $m.py $H/; done
rm -rf __pycache__; cd /workspaces/SCLA-Profile
python3 scripts/check-enforcement.py --json | python3 -c "
import json,sys; [print(b['file'],b['line'],b['problem'])
                 for b in json.load(sys.stdin)['broken_claims']]"
python3 projects/video-production/render-qa/tests/run_tests.py; echo "exit=$?"
for m in boxmodel check_capacity check_slots check_variety build_index \
         instance_templates; do
  mv $H/$m.py projects/video-production/render-qa/src/; done
```

---

## 7. Open owner calls

Both have a safe default already chosen; override in writing.

1. **Does a freeform build take a stem?** The experiment is `agent-native-m2` in
   `experiments/`, so it never took the `mkdir` build lock that keeps concurrent
   builders off one lesson. *Default: yes — freeform builds live under
   `renders-hyperframes/<base>` and keep the lock. The lock has nothing to do
   with templates.*
2. **Does the pilot gate tighten?** The brief is explicit that removing templates
   removes the flat quality floor that makes unattended AUTO-BATCH safe, and that
   the pilot gate stops being a formality. *Default: freeform stays opt-in
   (`--freeform`) and never becomes the AUTO-BATCH default until `check_diversity`
   plus the vision pass can quarantine a weak build alone.*
