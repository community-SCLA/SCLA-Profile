# What the pipeline looks like if every render uses this method

A design brief, not a decision. Grounded in the `agent-native-m2` build and in the gate
inventory described by `.claude/rules/video-production.md`. **Caveat on rigour:** the
per-module verdicts below are reasoned from that rules file's own description of what
each checker does plus `ls render-qa/src/`; I did not read all 22 modules' source. Treat
the survives/dies column as a proposal to verify, not a finding.

---

## 1. The one architectural swap everything else follows from

Today the geometry gate is a **static model**: `boxmodel.py` parses template CSS, reads
`metrics.json` for real Proxima advance widths and `line-height: normal`, and computes
where every box lands — with no browser. That design exists because templates are a
closed, declarable set (`data-slot`, `data-present-if`, `data-geometry-repeat`).

Agent-authored HTML has no closed set. The model cannot follow arbitrary CSS.

The replacement is a **runtime probe**: drive the composition in the browser the
preview/snapshot path already uses, seek to N sample times, and dump for every element
its `getBoundingClientRect()`, computed `font-size`, effective opacity, and text
content. Python then runs exactly the same rules against real rects.

```
today:   template CSS + metrics.json ──► boxmodel.py ──► check_geometry.py
adopted: any HTML ──► probe_geometry.(mjs) @ N seeks ──► check_geometry.py
```

This is worth building **whether or not you adopt the method**. It closes the hole
`boxmodel.py` was invented to patch — the 2026-07-29 cut where two absolutely-positioned
siblings shared pixels and three gates passed it — at the source, by measuring instead
of modelling. And it makes `check_text.py` grade *rendered* sizes rather than CSS rules,
which is the difference between a floor that can fire and one that can't.

## 2. Per-module verdict

| Module | Verdict | Note |
| --- | --- | --- |
| `verify_render.py` | **survives, unchanged** | stream duration vs `data-duration`, 1920×1080, 3 frames/scene — never knew about templates |
| `check_presence.py` | **survives, unchanged** | blank / stagnation on rendered frames |
| `check_copy.py` | **survives, unchanged** | Title Case, the conjunction rule, `part-reference` — grades narration + on-frame strings. The owner-preference enforcer, and it is template-independent |
| `check_boundaries.py` | **survives** | `audio-tail-clipped` / `final-hold` read `audio_meta.json` + root duration. Gets *easier* — the engine reports real durations |
| `stem.py` | **survives** | naming, `mkdir` build lock, `delivered` |
| `check_layout.py` | **survives** | wraps `hyperframes inspect`; `npm run check` already samples 9 points |
| `hfp_common.py` | **survives** | plumbing |
| `preflight.py` | **survives, re-sectioned** | still the orchestrator and the hard block; its section list changes |
| `tokens.py` | **survives, shrinks** | keeps the numeric floors the runtime gates read; loses `programs_problems()`? no — banner-vs-folder still applies |
| `check_geometry.py` | **rewrite** | same rules (frame-padding, safe-area, content-bottom, card-gutter, overlap), new input: probe rects |
| `check_text.py` | **rewrite** | `typography.min-size` graded on computed sizes, not CSS rules |
| `check_continuity.py` | **re-point** | `MIN_SCENE_SEC`, bare-conjunction openings, list-splitting — reads `audio_request.json` instead of `scenes.json` |
| `check_motion.py` | **rewrite, and gets stronger** | the ripple ban can't scan arbitrary JS reliably. Replace with a pixel test: sample t and t+0.12s inside a declared settled window; churn above threshold = a re-animation. `check_presence` already owns the inverse |
| `boxmodel.py` | **retire** | superseded by the probe |
| `textmetrics.py` + `metrics.json` | **demote** | no longer load-bearing for gating; keep as an *authoring* aid so a builder can pre-check copy before the browser runs |
| `check_capacity.py` | **retire** | "does this string fit that slot" is meaningless without slots; subsumed by probe overflow |
| `check_slots.py` | **retire** | `unknown-icon`, `banned-row-icons`, `scene-index-badge` are all template-shaped |
| `check_variety.py` | **retire, partially replaced** | template-family counting has no referent. Replace with `check_diversity.py`: perceptual-hash the beat midpoints and flag consecutive frames that are too similar. Catches the real defect (a monotonous video) rather than its template proxy |
| `build_index.py` | **retire** | the HTML *is* the authored artifact |
| `instance_templates.py` | **retire** | — |
| `compile_timeline.py` | **becomes `plan_timing.py`** | owns lead-in, inter-beat gaps, act-boundary gaps, `FINAL_HOLD`; input `audio_meta.json`, output `timing.json` |
| `synth_narration.py` | **thin adapter** | writes `audio_request.json` and calls the HyperFrames `audio.mjs` engine instead of owning TTS |

Net: **6 retire · 4 rewrite · 2 transform · 10 survive.** The gates that encode owner
*preferences* almost all survive. The gates that encode *template mechanics* almost all
die. That split is the real finding.

## 3. The build loop, concretely

```
1  stem.py claims  renders-hyperframes/<stem>/            (unchanged)
2  hyperframes init --example=blank
3  copy brand kit: fonts/ + brand-truth.md + tokens.yml
4  BUILDER writes audio_request.json          ← the new scenes.json: the beat plan
      hook ▸ check_copy.py (script mode) + check_continuity.py
5  audio.mjs  --provider heygen --voice <Oxana>   →  audio_meta.json
6  plan_timing.py                                 →  timing.json
7  BUILDER writes design.md, index.html, compositions/*.html
      hook ▸ hyperframes lint + check_copy.py (frame strings) + check_motion.py
8  npm run check          lint · runtime · layout · motion · WCAG AA contrast
9  probe_geometry → preflight.py: geometry · text-floor · overlap · safe-area · diversity
10 snapshot at every beat midpoint + vision pass          (batch-precheck.sh)
11 render → verify_render.py → check_presence.py → file → Wistia → published.tsv
```

Two structural consequences:

- **The beat plan moves upstream of the audio, and the HTML moves downstream of it.**
  Today a `scenes.json` edit can change narration, so a late geometry failure costs a
  re-synthesis *and* a re-render. Here narration is frozen at step 5 and the visual is
  authored against fixed timings — so a step-9 geometry failure costs an HTML edit and
  nothing else. The expensive-failure profile improves.
- **The geometry gate can no longer fire at plan stage.** That is a genuine regression
  from today's `preflight.py --static`, and the honest mitigation is the point above:
  its failures got cheaper, so firing later hurts less.

## 4. What replaces the template library as the authoring input

Templates were doing two jobs. Separate them:

| Job templates did | Replacement |
| --- | --- |
| Encode brand truth (palette, type scale, frame padding, safe area) | **`brand-truth.md`** — one shared file the builder reads, plus `tokens.yml` for the numbers the gates read. Roughly the durable half of this project's `design.md` |
| Guarantee a quality floor | **A reference build.** Pin `agent-native-m2` as the house reference the way `check_variety` thresholds are pinned to the owner's reference video: a gate that rejects the reference is a broken gate |

Per video the builder still writes a `design.md`, but only the part templates could never
supply — the **concept angle**. One sentence naming what this lesson's single carrying
idea is. That is the thing that made this video different, and it is the one thing in
the whole pipeline no checker can grade.

## 5. Costs, honestly

| | Today | Adopted |
| --- | --- | --- |
| Builder output per video | ~30-line `scenes.json` | ~600 lines of HTML/CSS/JS across 3–4 files |
| Token cost per video | baseline | **~3–5×** |
| Wall clock per build | baseline | up: more authoring + a browser probe pass |
| Quality floor | high and flat — templates guarantee it | **variable.** Some builds will be worse than template output |
| Quality ceiling | capped by the template set | uncapped |
| New code to write | — | `probe_geometry`, `plan_timing`, `check_diversity`, 4 rewrites |

The variance line is the one that matters for AUTO-BATCH. Draining a 20-video queue
unattended is safe today partly *because* templates cannot produce a surprising layout.
Remove them and the pilot gate stops being a formality — it becomes the only thing
standing between a bad concept angle and 20 published videos. Either the pilot gate
tightens, or `check_diversity` + the vision pass have to get good enough to quarantine a
weak build on their own.

## 6. Staged adoption

- **Phase 1 — build the probe.** `probe_geometry` + re-point `check_geometry` /
  `check_text`. Do this regardless of the rest; it strengthens today's pipeline and is
  the prerequisite for everything below.
- **Phase 2 — hoist brand truth.** Extract `brand-truth.md` from
  `design-contract.md` + `tokens.yml`. Harmless on its own; templates keep working.
- **Phase 3 — `/render-lessons --freeform`.** A second BUILD mode beside the template
  path. Run 3 lessons both ways, same scripts, and compare on the pilot gate.
- **Phase 4 — flip the default** only after freeform wins N consecutive pilots. Retire
  the six template-shaped checkers in the same pass that retires the templates, never
  before — a checker with no referent is worse than no checker.

Nothing in phases 1–3 is reversible-only-with-pain, and phase 3 leaves both paths alive.
