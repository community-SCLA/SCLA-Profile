# HANDOFF — deterministic plan-first rewire, 2026-07-28 (night)

> **PICKED UP 2026-07-28 (later session).** §6 ran green; agents A–C had all
> landed (A's missing pinning test added as `tests/test_build_index.py`, 26
> checks). Landing fix: `check_variety.family()` now strips any `__` instance
> suffix — the rejected pilot's `__scene_NN` clone names had let every
> run/cap/canvas rule undercount (8 → 13 findings once fixed). Broken
> enforcement claim in `.claude/rules/video-production.md` reworded (0 broken).
> Decisions entry written. §7.4 pilot rebuild dispatched through the new flow.
> Remaining open when this banner was written: commit decision (§7.5), research
> adoption (§7.6), icon vocabulary (§7.7), the 31 unbacked rules (§7.8).

Written for a session starting with **zero context**, mid-flight: this session
was interrupted at its limit with THREE implementation subagents still running.
Read this whole file, then §6 (verify agent landings) before anything else.
Companion: `HANDOFF-owner-review-enforcement-2026-07-28.md` (same day, earlier
session — root-cause analysis, gate calibration, the Repo Structure Playbook
v1.1 embedded at its bottom). This file supersedes nothing; it continues that
one.

---

## 1. The owner's directive (this session's mandate — verbatim in substance)

The owner is furious and the queue is past due. Their words, condensed:

- "Everything is unenforceable… the solution of the last session was simply to
  add gates but then it just sends it back after it's already rendered over and
  over. **This should be deterministic — from the jump, a formula that can just
  be cranked out.** Too much is left up to agents and these stupid prose files."
- "Do not assume the conventions we have put in place are the most efficient or
  effective. Look big picture and connect the dots on what's going to make this
  process ship end to end quickly, seamlessly, with a consistent polished and
  engaging output."
- The reference for "great": https://sclc.wistia.com/s/u99h9iia509hd7y
  (= `what-makes-for-a-dream-job_early-career-boost`, Wistia `gryylc7qns`) —
  already measured and pinned into the gates by the earlier session.
- Mid-session addition: "look into how others are streamlining video creation
  for HeyGen HyperFrames / review the HyperFrames docs for ideas" → done, §5.
- "Review the best practices playbook I'm going to attach" → it is embedded at
  the bottom of `HANDOFF-owner-review-enforcement-2026-07-28.md` (STD-1..43).

**Mandate: implement, don't re-plan.** This session moved from review into
implementation on that basis.

---

## 2. The core finding (the whole assessment in one paragraph)

The architecture was backwards: a cold agent freehand-authored a 21-scene
`index.html` from 6,139 words of prose (`design-contract.md`), and quality was determined
afterwards by gates — so every failure cost a full re-author, and every owner
rejection cost a render. Meanwhile **the deterministic compiler the owner is
asking for already existed and was orphaned**: `render-qa/src/build_index.py`
compiles an ~8-line-per-scene `scenes.json` manifest into the complete
`index.html` (head/tail boilerplate, rail, audio host, per-slot template
clones, `--extract` reverses it) — and neither SKILL nor BUILD-KIT ever
mentioned it. Same story for `scripts/batch-precheck.sh` (pre-render per-scene
snapshots + low-ink blank-scene detection — the vision review BEFORE the 7-min
render), built earlier that day, wired into nothing. A real `index.html` is 85
lines with ZERO bespoke markup/CSS/JS; everything downstream of the scene plan
is already mechanical (`compile_timeline.py` owns every number from HeyGen word
timestamps). The genuinely creative residue is small and identifiable: beat
segmentation, template choice per beat, on-frame copy, cue anchor phrases, icon
assignment — i.e. exactly the contents of `scenes.json`. So the fix: **the
builder authors only the plan; gates run on the plan in milliseconds; the
compiler emits the HTML; vision looks at snapshots before any render.**
"Boring" was also diagnosed: NOT slowness (rejected build changes visual state
*more* often than the reference — 4.2s vs 5.1s) but sameness + thin vocabulary:
artwork = 11 inline SVG icons in `scla-condition.html`'s ICONS map (mirrored
into statement/steps), and the reference's praised devices (bar chart, strike-
throughs, card demotion) mostly live in the less-used templates the variety
gate now forces builders to spend.

## 2b. New flow (target state)

```
refined/*.txt ─▶ builder authors scenes.json          [AGENT — the only judgment]
                   ▲       │
                   │       ▼ (seconds per loop)
                   │  build_index.py → index.html      [DETERMINISTIC]
                   │  preflight.py --static            [GATES: variety, copy,
                   └──fix plan on failure──┘            slots, text, stem]
                 synth_narration.py (HeyGen TTS)       [DETERMINISTIC, cached]
                 compile_timeline.py --apply           [DETERMINISTIC]
                 preflight.py (full) + npm run check   [GATES]
                 batch-precheck.sh                     [snapshots + vision,
                                                        PRE-render quarantine]
                 PILOT GATE (human, once per batch)    [HUMAN]
                 batch-ship.sh render→verify→publish   [DETERMINISTIC]
```

---

## 3. COMPLETED this session (all uncommitted, on top of the earlier session's
~27 also-uncommitted files — `git status` is the union; nothing was committed
or reverted; the commit-vs-revert call is still open and this session's work
builds on the earlier session's, which effectively endorses commit)

1. **`.claude/skills/render-lessons/SKILL.md`** — rewritten to plan-first:
   - BUILD-KIT:BEGIN marker MOVED UP so the "Author `scenes.json` FIRST —
     never `index.html`" paragraph is INSIDE the extracted kit (verified:
     `awk '/BUILD-KIT:BEGIN/,/BUILD-KIT:END/'` = 102 lines, includes it).
   - Landmines updated: rail bullet deleted (compiler owns rail); new
     "`index.html` is a build artifact — never hand-edit" bullet with the
     cheap loop (`build_index.py .` → `preflight.py . --static`); variety
     bullet now lists all rules incl. artwork coverage + single-canvas cap and
     says "plan the whole scene list against these BEFORE filling copy".
   - Build-sequence command block: `build_index.py .` + `preflight.py .
     --static` inserted BEFORE synth/compile/preflight/check, with "iterate on
     scenes.json until --static exits 0, only then spend TTS".
   - B2 subagent prompt: authors scenes.json only.
   - Phase SHIP: `batch-precheck.sh <stem>` before `batch-ship.sh`.
   - A3 renamed "three tool calls per video": build → **precheck + vision
     (pre-render, quarantines before the 7-min spend)** → ship (post-render
     vision demoted to encode-defect spot-check).
   - Intro guard list + A2 pilot line mention precheck.
2. **`scripts/batch-prepare.sh`** (generated BUILD-KIT header/footer):
   "Assemble index.html FIRST" section deleted; scaffold text now says you
   never touch its index.html; FTR §1 rewritten — build_index owns template
   cloning (instance_templates no longer a manual step), six-command loop with
   plan-gate iteration; §2 wording → scenes.json; report fields gain
   `static=<exit>`.
3. **`.claude/rules/video-production.md`** — guards bullet adds
   `batch-precheck.sh` (exit 3 = pre-render quarantine); standing-preferences
   bullet now states plan-stage enforcement (`preflight --static`, guard on
   scenes.json, index.html compiler-generated).
4. Swept for stale "author index.html" instructions elsewhere: none found
   (design-system/AGENTS.md's index.html row is its own demo reel — fine).
5. Pilot workspace note: I ran `build_index.py --extract` on
   `renders-hyperframes/better-decisions-come-from-better-criteria_early-career-boost_2026-07-28`,
   so a **`scenes.json` now sits in that workspace** (useful exemplar). Its
   `index.html` was overwritten once by a compile and **restored byte-identical**
   from scratchpad — verify with `git status` irrelevance (workspace is
   gitignored) and the fact that full preflight still fails only 9/10/11.

## 4. IN FLIGHT — three background subagents, state unknown at cutoff

Their edits may be complete, partial, or absent. **First job of the next
session: run §6 and inspect `git status` + the files below.** If an agent's
work is missing or half-landed, its full spec is reproduced here — re-run it.

### Agent A — `render-qa/src/build_index.py` canon refresh
Spec: update HEAD/TAIL constants to the current approved canon = the pilot's
hand-authored `index.html` (Motion v2 + follow-ons: rail CSS `bottom: 48px`,
track opacity .28, `background: #000`, Inter/JetBrains Mono rules, current
rail script); keep the generated-file banner; investigate `data-hf-id`
(canon divs carry `hf-xxxx`, compiler omits — decide via render-qa greps +
hyperframes lint behavior; if needed generate DETERMINISTICALLY, e.g. hash of
scene id); acceptance = extract→build→`compile_timeline --apply` round-trip on
a scratch copy of the pilot, semantically identical (head/tail identical
modulo banner; scene attrs identical modulo documented timing placeholders);
add a pinning test in `render-qa/tests/`. Last heard (relayed): "Extract
matches the pilot manifest exactly. Now build and compare head/tail against
canon" — i.e. mid-step, HEAD/TAIL edits possibly not yet written.
**Known drift it was fixing (measured this session):** compiled head had
`background: #000`→`#0d2437` discrepancy inverted, rail at `bottom: 0` vs
canon `bottom: 48px`, missing font rules, missing `data-hf-id`, and scene divs
compiled with placeholder `data-start="0" data-duration="1"
data-track-index="0"` (the last three are BY DESIGN — compile_timeline owns
them; do not "fix" those).

### Agent B — `preflight.py --static` + guard extension
Spec: `--static` flag runs ONLY audio/transcript-independent sections
(≈ compositions-freshness 2c, one-theme 4, text 7, title-card 7b, slots 8,
variety 10, copy 11, stem 12 — agent to confirm from code), skips the rest
with "(static mode)" notes, exit semantics unchanged, full mode byte-for-byte
unchanged. `scripts/hyperframe-guard.sh`: fire on BOTH
`*renders-hyperframes*/scenes.json` AND `.../index.html`; on scenes.json write
→ if JSON parses, recompile via build_index then run `--static`, report
actionable lines; malformed JSON mid-edit → silent exit 0; keep ALWAYS-exit-0
fail-soft hook contract + additionalContext JSON shape; message text now says
"edit scenes.json, not index.html"; non-hook CLI still works.
`.claude/settings.json` untouched if matcher already routes all Write|Edit.
Tests in `render-qa/tests/` incl.: --static on the pilot fails 10/11, doesn't
attempt 9; full mode unchanged (fails 9/10/11).

### Agent C — variety rules 6 + 7
Spec: in `check_variety.py`: **Rule 6 theme-block cap** — >6 consecutive
content scenes OR >65s continuous on one background canvas (light vs navy)
fails; template→canvas map as ONE explicit dict + freshness test grepping each
`design-system/compositions/scla-*.html` background so template edits break
loudly; seconds-half skips gracefully when durations are placeholders (plan
stage), scene-count half always enforced. Calibration: rejected pilot runs 9
consecutive light scenes / 78.3s → must FAIL; reference must PASS. **Rule 7
composition (two-region) coverage** — ≥25% of content scenes two-region
(reference ~35%, rejected 0%); classify from template + filled slots by
reading actual template layout; **if not calibratable against BOTH fixtures it
ships REPORT-ONLY** (a gate that rejects the owner's reference is a broken
gate). Extend `test_variety.py` pinning both rules to both videos; full suite
must pass; preflight §10 picks the rules up automatically (agent forbidden
from editing preflight.py — Agent B owns it).

### Agent D — research (COMPLETE, results in §5)

---

## 5. Research results — HyperFrames streamlining (agent complete)

Public material thin; the local skill pack is deeper than anything public.
Ranked, with adoption cost:

1. **Registry transitions + branded caption styles** (S per item, M to brand):
   `hyperframes add` — 13 transition categories (push/dissolve/blur/radial/
   grid…), 13 caption styles, 11 lower-thirds, grain/vignette/light-leak
   overlays, installable as sub-compositions. Directly attacks "boring" without
   new templates. **Do first.**
2. **Word-timed karaoke captions** (S–M): registry caption-highlight /
   caption-pill-karaoke / caption-weight-shift consume exactly the HeyGen
   native word timestamps we already hold. **Do first.**
3. **`npx hyperframes benchmark` + `--workers` + `--gpu`** (S): find fastest
   render config; NVENC/VAAPI. Cheapest speed lever for 29×~7min ≈ 3.4h serial.
4. **`*.motion.json` sidecars** (S–M): `inspect` auto-checks appearsBy/before/
   staysInFrame/keepsMoving against the seeked timeline — a machine proxy for
   "watching" the video; generate sidecars from compile_timeline's own data.
   Fits owner doctrine (preferences→gates).
5. **AWS Lambda parallel rendering** (M): `hyperframes lambda deploy/render`,
   16 parallel chunks — batch render in minutes of wall-clock. Zero-ops alt:
   HeyGen hosted Cloud Rendering API (per-minute billing).
6. **`hyperframes publish`** (S): stable public preview URL per composition —
   owner could review pilots from a phone. Caveat: publicly accessible.
7. **`render --batch rows.json`** (M): documented at
   hyperframes.heygen.com/guides/pipeline but absent from the local skill copy
   — verify `npx hyperframes render --help` before relying on it.
8. **Audio-reactive polish** (S, lowest priority for narration lessons).

---

## 6. Verification checklist for the next session (run in order)

```bash
cd /workspaces/SCLA-Profile
git status                                              # union of both sessions' edits; expect possibly-partial agent edits
git diff projects/video-production/render-qa/src/build_index.py   # Agent A landed?
git diff projects/video-production/render-qa/src/preflight.py scripts/hyperframe-guard.sh  # Agent B?
git diff projects/video-production/render-qa/src/check_variety.py projects/video-production/render-qa/tests/test_variety.py  # Agent C?
python3 projects/video-production/render-qa/tests/run_tests.py          # was 65 passed pre-session
python3 projects/video-production/render-qa/tests/test_variety.py       # reference PASSES, rejected FAILS — non-negotiable
bash scripts/lint-refs.sh                                # check 10 = 0 broken claims (rules file was edited — claims must hold)
python3 scripts/check-enforcement.py                     # was 40 backed / 0 broken / 31 unbacked
WS=projects/video-production/renders-hyperframes/better-decisions-come-from-better-criteria_early-career-boost_2026-07-28
python3 projects/video-production/render-qa/src/preflight.py $WS            # must STILL fail exactly 9/10/11 (+6/7 if Agent C landed & counts pilot's canvas run)
python3 projects/video-production/render-qa/src/preflight.py $WS --static   # if Agent B landed: fails 10/11, never attempts 9
python3 projects/video-production/render-qa/src/build_index.py $WS && git -C . status  # compile from the workspace scenes.json; then RESTORE if comparing (workspace gitignored)
bash scripts/batch-prepare.sh && head -40 projects/video-production/renders-hyperframes/_run/BUILD-KIT.md  # kit opens with "Author scenes.json FIRST"; leak-check passes
```

Mind the leak-check in batch-prepare (`grep -qE 'Phase (SHIP|AUTO-BATCH)|batch-ship'`
over the kit body): if anyone adds batch-ship references inside the BUILD-KIT
markers, prepare FATALs — that's intended.

## 7. NOT done — the queue to ship (in order)

1. **Land/finish agents A–C** (§4) and run §6 green.
2. **Decisions log entry** (append at TOP of `decisions/log.md`, style of the
   2026-07-28 entry): the plan-first rewire — builder authors scenes.json;
   build_index.py compiles (was orphaned); gates moved to plan stage
   (`--static` + guard on scenes.json); batch-precheck wired pre-render;
   rules 6/7 added; cite the owner's "deterministic from the jump" directive.
3. **Snag-log retro** — this session edited pipeline but ran no render; the
   PostToolUse retro hook was not tripped by this session's work; still,
   close-out convention says prepend an entry when touching the factory.
4. **Rebuild the pilot THROUGH THE NEW FLOW** — the proof. Cold builder gets
   BUILD-KIT (regenerate via batch-prepare), authors scenes.json for
   `better-decisions-come-from-better-criteria`, loops --static, synths,
   compiles, full preflight, precheck — STOP at pilot gate for the owner.
   The old build fails 11 variety + 30 copy + in-scene-gap findings; the new
   contract (Title Case, conjunctions in scenes 2+10, ≥2-item lists, more
   forms/artwork, 0.5s gap cap, speed 1.0) is all gated now.
5. **Commit** (owner has not explicitly said commit — ASK, or point at this
   file's §3 preamble; recommendation: COMMIT both sessions' work as granular
   commits — the gates are calibrated, tested, and the owner's direction is
   unambiguous).
6. **Adopt research items 1–3** (§5): brand-wrap 2–3 registry transition
   blocks + karaoke captions into design-system; run benchmark for render
   config. Then 4 (motion sidecars) as the next preferences→gates increment.
7. **Icon vocabulary expansion** — ICONS map is 11 inline SVGs duplicated
   verbatim across three templates (STD-20/21 violation AND the artwork
   bottleneck: the artwork gate needs ≥5 distinct per video from a pool of
   11). Owner explicitly asked for "an arrow pointing from one statement to
   another" style devices. Needs visual QA — do it with snapshot verification,
   not blind.
8. **The 31 unbacked rules** (`check-enforcement.py --json`) — mechanise or
   label Convention. Backlog, not blocking.
9. **Open from previous handoff, still true:** `HANDOFF-autobatch-2026-07-28.md`
   is stale (banner added); `decisions/log.md` 2026-07-13 silence numbers
   wrong (0.6/0.9 vs real 0.3/0.15/0.45) — historical, don't trust.

## 8. Doctrine (carry forward, verbatim from the owner's two sessions)

- **A preference is not real until it is a checker.** Mechanise or label
  Convention. Never prose alone. (Memory:
  `owner-preferences-must-become-gates.md`.)
- **A gate calibrated without a reference is a guess** — every threshold pins
  to the reference video via test_variety.py; a gate that rejects the
  reference is a broken gate.
- **NEW this session: judgment writes the plan; everything after the plan is
  compiled.** An agent decision that survives into an artifact must pass
  through a machine-checkable intermediate (scenes.json), gated at write time.
  Never let an agent author what a compiler can emit.
- One date per stem, most recent action, `stem.py` owns it, key on base.
