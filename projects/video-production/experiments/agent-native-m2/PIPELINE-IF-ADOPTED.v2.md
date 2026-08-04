# What the pipeline looks like if the Build Plan is fully adopted

Grounded in `render-qa/docs/BUILD-PLAN-agent-native-2026-08-04.md` and the actual code
it produced (commits `ddbc673`..`2e55fa9`), not in a description of what a checker is
supposed to do. Every claim below traces to a file, a ledger entry, or a result
observed on the real `agent-native-m2` reference build.

**Scope of "fully adopted":** Phases 1–2 are landed (ledger below). Phase 3 (one
freeform pilot) is scoped but **deliberately not started** — owner instruction,
2026-08-04. Phase 4 (retirement) requires an owner "go" that hasn't been given. This
document describes the pipeline as it stands today (Phases 1–2) and, where it differs,
what Phase 4 would still change. Anywhere below that isn't yet true is marked
**⛔ not yet**.

---

## 0. The architectural swap

The geometry question a freeform build has to answer is the same one templates
answered: *is there ink where there must not be?* Templates answered it with a static
model — parse template CSS, read real font metrics, compute where every box lands, no
browser involved. That model cannot follow arbitrary agent-authored CSS.

The answer that shipped is **pixel measurement, not a DOM model**:
`render-qa/src/check_ink.py` takes a rendered still, finds local-contrast edges (glyph
edges — a radial glow or faint grid varies smoothly, a letterform doesn't), and checks
them against keep-out bands declared in `tokens.yml` `chrome-regions`. No browser at
check-time, no CSS resolution, nothing that can be fooled by flow, flex, grid, calc(),
`%`, or a load race. It was promoted from a spike that validated clean on 21 real stills
with three planted defects, all firing and discriminating correctly (Step 1.4).

```
any HTML ──► render to stills @ N beats ──► check_ink.py (pixel contrast, no browser)
```

A DOM-rect probe was considered and explicitly rejected for this pipeline (Build Plan
ground rule 5): a prior prototype of exactly that produced 1,760 plausible findings from
a single mis-served page. A probe that can be fooled by a load race is worse than the
static model it would replace. The cost of the pixel approach is real and stated, not
hidden: it can tell you *that* ink landed somewhere wrong, never *why*. `check_fit.py`
(§2) exists to catch some of those cases earlier, in text, before a render is spent.

---

## 1. Per-module verdict

The pattern across nearly every row: a checker that keeps grading a freeform build
needs a real adapter for the freeform data shapes (`audio_request.json` /
`audio_meta.json` / `timing.json`, instead of the compiler's private
`data-narration` / `data-variable-values`), and **building that adapter surfaced a real
defect that had been shipping ungraded.** That happened often enough that it is the
actual finding of Phase 1, not a side effect of it.

| Module | Status | What it does now | Real finding surfaced |
| --- | --- | --- | --- |
| `check_copy.py` | adapted | `hfp_common.load_beats()` reads `audio_request.json` when `data-narration` is absent (Step 1.1); grades the beat manifest with the same rules as compiled narration | narration itself was clean (24/24 beats), but zero headings were declared (`data-role="heading"`) — Title Case / terminal-period rules graded 0 of 70 on-frame strings |
| `check_continuity.py` | adapted | same beat-manifest adapter as `check_copy.py` | narration clean — no finding beyond the above |
| `check_motion.py` | adapted | composition glob widened to all composition HTML (was `scla-*.html` only); the `DECORATIVE` name-matching allow-list (`ghost`/`ring`/`-bg`) is deleted, replaced by an explicit `/* motion-allow: <reason> */` declared at the tween's call site (Step 1.2) | the real agent-native build's `#bg-glow` was exempt purely by name and had declared nothing — caught immediately once name-matching was removed; a helper-routed tween must now declare at the CALL SITE, since a declaration in the helper body would exempt every caller |
| `check_layout.py` | adapted | sampling moved from per-clip to per-beat via `hfp_common.sample_units()` (Step 1.5a) | the old per-clip grid sampled 3 points on a 200s video; per-beat sampling now takes 24 |
| `verify_render.py` | adapted | same `sample_units()` grid; 3-per-unit now yields 72 stills where per-clip gave 9 (Step 1.5b) | the grid was found to silently fall back to clip-count on a build with no usable beat timing yet — exactly the coverage collapse this step exists to close. It now returns an empty, explicitly ungradeable grid in that case instead of a smaller number that reads as clean |
| `check_presence.py` | adapted | `hfp_common.load_words()` reads all three word-timestamp shapes and offsets per-clip words by `timing.json`'s `audio_start` (Step 1.5c) | this loader is the ONE loader; `check_diversity.py` calls the same one, by design |
| `check_boundaries.py` | adapted | `check_freeform()` grades the same rule IDs (`audio-tail-clipped`, `final-hold`) against `audio_request.json` + `audio_meta.json` + `timing.json` per clip, rather than one flat mixdown wav (Step 1.5d) | **the real agent-native build FAILS `audio-tail-clipped`**: its final clip holds 0.261s of real audio past the last word against a 1.5s floor. It had been shipping ungraded because this gate used to exit 2 (unreadable) on the whole build rather than fail the one clip |
| `boxmodel.py` | retired on this lane | superseded by `check_ink.py` (§0); still exists and still grades the 13 mid-career template workspaces until Phase 4 | had produced 281 findings on a build independently verified clean across 34 stills — the exact failure mode `check_ink.py` was built to close |
| `check_geometry.py` | retired on this lane | same disposition as `boxmodel.py` — its job is now split across `check_ink.py` (hard, pixel) and `check_fit.py` (advisory, plan-stage) | — |
| `check_text.py` | not touched | its freeform-lane job is covered by `check_ink.py` (blocking) + `check_fit.py` (advisory) rather than by rewriting this file | — |
| `check_capacity.py` | rehomed | `check_fit.py` keeps the one part that was load-bearing — measurement in the real vendored font via `textmetrics.py` — and drops the per-slot `maxLines` lookup, which has no freeform referent (Step 1.3c) | the question becomes "does this string fit the content area at the minimum legal type size," advisory per STD-38. First version's heading threshold (~240 chars) was a bound no real heading could reach — corrected before landing |
| `check_slots.py` | split | `placeholder-slot` (the `[[…]]`/TODO/TBD fabrication-ban half) rehomed into `check_copy.py`, now grading the BEAT MANIFEST too, not just on-frame strings (Step 1.3b). `unknown-icon` / `banned-row-icons` / `scene-index-badge` stay template-shaped, still on Phase 4's deletion list | a marker in narration is worse than one on frame — it gets spoken, and costs a re-synthesis once wavs exist. That half had never been graded on the freeform lane at all |
| `check_variety.py` | split | `one-item-list` / `one-card` rehomed into a new file, `check_forms.py`, graded on element structure (`<ul>`/`<ol>` nesting, or declared `data-role="list"`/`"compare"`) (Step 1.3a). The rest of the file (template-family counting) has no freeform referent and stays on Phase 4's deletion list | stated limit, printed every run: a build that draws lists as bare divs and declares nothing is graded on nothing there — not silently, but still nothing |
| `check_diversity.py` | unchanged | perceptual-hash of beat midpoints, `twin-beats` / `static-span`; predates this Build Plan | structurally cannot express "this list has one item" — that's why `check_forms.py` exists as a separate file rather than an extension of this one |
| `build_index.py`, `instance_templates.py` | unchanged | still compile the 13 mid-career workspaces | Phase 4 deletion list |
| `stem.py`, `preflight.py`, `tokens.py` | survive | `preflight.py` gained a `freeform` branch through nearly every section; `tokens.py` gained `chrome_regions()` | — |
| `hfp_common.py` | grew substantially | gained the entire freeform beat-manifest layer: `load_beats`, `load_words`, `onframe_strings`, `sample_units` | this is where most of the real adapter code actually lives — the reason every row above says "adapted" rather than "rewritten" |

Over what's landed: **2 modules retired on the freeform lane** (`boxmodel.py`,
`check_geometry.py`, superseded by `check_ink.py`), **1 new file**
(`check_forms.py`), **1 rehomed** (`check_capacity.py` → `check_fit.py`), **1 split**
(`check_slots.py`), **6 adapted** (copy, continuity, layout, verify_render, presence,
boundaries), and each adapter surfaced a real, previously-ungraded defect on the actual
reference build. None of those defects are hypothetical — they're sitting in
`experiments/agent-native-m2/` right now.

---

## 2. The build loop, as it actually runs today

```
 1  stem.py claims  renders-hyperframes/<stem>/
 2  hyperframes init --example=blank
 3  copy brand kit: fonts/ + brand-truth.md + tokens.yml
 4  BUILDER writes audio_request.json          — the beat plan, freeform's scenes.json
       hook ▸ check_copy.py (beat-manifest mode, via hfp_common.load_beats)
             + check_continuity.py + check_slots.placeholder_problems (spoken half)
 5  audio.mjs --provider heygen --voice <Oxana>   →  audio_meta.json
 6  plan_timing.py (compile_timeline.py's freeform successor)  →  timing.json
 7  BUILDER writes design.md, index.html, compositions/*.html
       — must declare data-role="heading" on every heading (Step 1.1 finding)
       — every ambient/decorative tween declares /* motion-allow: <reason> */
         AT THE CALL SITE, never inside a shared helper body (Step 1.2 finding)
       hook ▸ hyperframes lint + check_copy.py (on-frame strings) + check_motion.py
 8  npm run check          lint · runtime · layout · motion · WCAG AA contrast
 9  preflight.py --static  freeform branch: script_match, title_card, brand,
                            check_fit.py (advisory), check_forms.py — all before
                            any render is spent
10  render → per-beat stills (sample_units grid, not per-clip)
11  preflight.py (full)   + check_ink.py over the beat stills + check_boundaries
                            check_freeform() (audio-tail-clipped, final-hold)
12  batch-precheck.sh snapshot + vision pass
13  render final → verify_render.py (per-beat stills) → check_presence.py
                 → file → Wistia → published.tsv
```

Narration freezes at step 5, before the HTML is authored against it — so a geometry
failure at step 11 costs an HTML edit, not a re-synthesis. The geometry gate can no
longer fire at plan stage the way the template path's static model could; `check_fit.py`
at step 9 is the honest mitigation, catching what it can in text before render.

---

## 3. What's still gated, not yet true (⛔)

**Phase 3 — the pilot — has not run.** Scoped in the ledger (queue-top lesson
identified, stem lock claimed and released, credentials checked) but explicitly halted
on owner instruction 2026-08-04, and separately blocked on a live defect:

**The write fence (Step 2.1) currently blocks the pipeline's own credential path.**
`scripts/with-secrets.sh` — the mandatory Infisical entry point for every HeyGen/Wistia
call — is itself a fenced token by name. An ordinary build command like
`bash scripts/with-secrets.sh node audio.mjs > .../audio_meta.json` gets blocked: the
fence scans the raw command string for mutator syntax near a fenced path, and treats the
literal text `scripts/with-secrets.sh` in an allowed, non-mutating position as if it
were a write target. TTS synthesis (step 5 above) and publish both cross that script. A
fix is written and proven against 24 cases
(`render-qa/docs/PENDING-write-fence-fix.md` + `verify_fence_fix.py`) but not applied —
applying it means editing `scripts/`, which the fence itself blocks from an unflagged
session. It needs a session that exports `SCLA_SYSTEM_SESSION=1` before Phase 3 can
synthesize audio at all.

**Phase 4 — retirement — requires an explicit owner "go" on retirement, separately from
approving the pilot's output**, plus the 13 mid-career workspaces (template path) fully
drained per `batch-status.sh` / `published.tsv`. Neither has happened. If it does, one
commit retires: `boxmodel.py`, `check_capacity.py` *(functionally superseded already by
`check_fit.py` — this is deleting dead code, not losing a rule)*, `check_slots.py`
*(minus `placeholder-slot`, already migrated out)*, `check_variety.py` *(minus
`one-item-list`/`one-card`, already migrated to `check_forms.py`)*, `build_index.py`,
`instance_templates.py`, the `design-system/` template set, plus 13 enforcement-claim
lines in `.claude/rules/video-production.md` and 10 test files.

---

## 4. Costs, measured against a real build

Phase 1 ran the re-pointed gates against the actual `agent-native-m2` reference build,
so this is what was found rather than what might be found:

| | Result |
| --- | --- |
| Narration quality | clean — 24/24 beats pass conjunction, retired-name, part-reference rules |
| Heading declaration | **0 of 70 on-frame strings were gradeable** for Title Case / terminal-period, because zero headings were marked `data-role="heading"`. Not a gate failure — a build omission the gate can now see and name, where it used to print a bare PASS |
| Motion discipline | one real exemption-by-name caught (`#bg-glow`) the moment name-matching was removed |
| Ending / final hold | **fails today**: 0.261s of real trailing audio against a 1.5s floor (owner wants 1.8s). This is the ending the owner has rejected twice, now confirmed to have been shipping ungraded rather than merely under-tested |
| Sampling coverage | was silently 3 samples on a 200s video (27→3 collapse); now 24–72 depending on gate, and a build with no beat timing yet returns *ungradeable* rather than a smaller number that reads as clean |

The reference build the whole proposal is built on **currently fails two of its own
gates** (`no-headings-declared`, `audio-tail-clipped`). Phase 3's pilot has to clear
both before it reaches the owner gate.

---

## 5. Staged adoption — current status

| Stage | Status |
| --- | --- |
| 1. Build the geometry answer for freeform HTML | done — `check_ink.py`, pixel-based, not a browser probe (§0) |
| 2. Hoist brand truth | not part of this Build Plan; `brand-truth.md` exists inside `experiments/agent-native-m2/` but has not been extracted as a shared file |
| 3. One freeform pilot | scoped, **not started** — blocked on the write-fence credential-path defect (§3); no template twin, since the direction is already decided and this phase exists to put real pixels in front of the owner before Phase 4 deletes code |
| 4. Retirement | **requires an explicit owner go-ahead on retirement specifically**, separate from approving the pilot's video, plus the mid-career queue drained. Scope is enumerated exactly (§1, §3), not estimated |

The gates that encode owner *preferences* survive; the gates that encode *template
mechanics* die. What the adapting work in Phase 1 added to that picture: the survivors
don't survive unchanged, and building their adapters is what found the two live defects
sitting in the reference build today.
