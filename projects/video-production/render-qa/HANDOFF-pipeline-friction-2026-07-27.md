# Handoff — pipeline friction, 2026-07-27 Motion v2 re-render

**Purpose:** hand this to a fresh session tasked with making the SCLA lesson
pipeline flow end-to-end without babysitting. It is a friction inventory, not a
status report. Status lives in the folders (`/render-lessons` → "Current Phase").

**What the session did:** re-rendered six lesson videos to Motion v2. All six
finished gate-clean and stopped at the hyperframe gate. Nothing shipped.

**Update — same day, follow-up session:** picked up items 1–3 from section D
below (B1, A1 residual, C2). All three are now fixed in the design system and
tooling — see the "FIXED (follow-up session)" notes inline in sections A/B/C
and the trimmed priority list in section D. **One consequence the next
session must act on:** the new compositions-freshness preflight check (C2)
now correctly FAILs on all six workspaces in the table above, because their
`compositions/` predates this session's B1 fix (and a pre-existing uncommitted
`scla-quote.html` edit from earlier the same day). None of the six were
rebuilt or re-previewed — do that before shipping any of them. Nothing in
this update was committed to git.

| Build | Scenes | Duration | Notes |
| --- | --- | --- | --- |
| `m1_mini-syllabus_mid-career-momentum_2026-07-25` | 14 | 102.8s | already v2, untouched |
| `m2_mid-career-mindsets-and-limiting-beliefs_mid-career-momentum_2026-07-25` | 13 | 94.5s | already v2, untouched |
| `m2_four-kinds-of-career-transition_mid-career-momentum_2026-07-25` | 29 → 30 | 196.8s | fixed in-session |
| `build-direction-before-you-build-a-plan_early-career-boost_2026-07-07` | 9 → 22 | 158.5s | full rebuild |
| `how-to-make-strong-career-decisions_early-career-boost_2026-07-10` | 11 → 21 | 182.0s | full rebuild |
| `skills-for-the-ai-era-future_early-career-boost_2026-07-10` | 9 → 25 | 191.6s | full rebuild |

Every preflight verdict below was re-run by the orchestrator, not taken from the
subagent's report.

---

## A. Fixed this session (do not re-solve)

**A1 — `scla-morph.html` could not be namespaced; blocked every build using it.**
`build_index.py` gives each slot its own template file by cloning and prefixing
element ids. It requires one shared id prefix. `scla-morph.html` shipped with 8
of 16 ids unprefixed (`cardA`, `cardB`, `cnA`, `cnB`, `csA`, `csB`, `ctA`,
`ctB`), so it died with `ids do not share one prefix (8/16 use 'mp-') —
namespace by hand`. **Any** build using morph was hard-blocked.
*Fixed:* ids namespaced in `design-system/compositions/scla-morph.html`
(attribute values, `getElementById` strings, CSS selectors; JS local variable
names deliberately untouched).
*Residual risk:* the other eight templates were never audited for the same
defect. **Worth a sweep** — the failure is silent until a second slot uses the
template.
*Audit run (follow-up session) — clean, no other offenders.* Ran
`instance_templates.clone()`'s exact prefix-share check (`prefixes[prefix] <
len(ids) - 1`) against every `id="..."` in all 12 composition files. All 11
non-morph templates pass with every id sharing one dominant prefix (0
non-conforming ids each) — `scla-morph` was the only one with the defect, and
it's already fixed. No code change needed; closing this as verified rather
than open.

**A2 — Motion v2 duration caps deadlock against the sentence-end boundary rule.**
Hit on 3 of the 4 rebuilt videos. A scene cap (12.5s standard, `scla-title`
6.5s, `scla-outro` 8.5s) cannot be met when the scene's narration is ONE
sentence longer than the cap, because boundaries may only land on sentence
ends. No `scenes.json` re-authoring can clear it; the build stalls.
*Fixed structurally, three levels:*
- `design-system/frame.md` — new normative bullet: an over-cap sentence is a
  **script** defect, and the sanctioned repair is word-preserving
  re-punctuation (em dash / colon / semicolon joining two independent clauses
  becomes a period). `script_match` must still read 0.00% after.
- `.claude/agents/script-refiner.md` — the ~14-word *average* was promoted to a
  hard per-sentence rule; opening and closing lines called out, since they
  inherit the tightest caps and are habitually one long summarizing sentence.
- `.claude/agents/lesson-builder.md` — builders are now authorized to make the
  repair themselves and re-run gates, with bounds, instead of stalling.
Decision recorded in `decisions/log.md` (2026-07-27).
*Scripts edited (punctuation only, zero words changed):*
`m2_four-kinds-of-career-transition_2026-07-23.txt`,
`build-direction-before-you-build-a-plan_early-career-boost_2026-07-07.txt`,
`skills-for-the-ai-era-future_early-career-boost_2026-07-10.txt`.

**A3 — HeyGen rejects the 5-wide TTS pool.**
`synth_narration.py`'s `TTS_WORKERS = 5` (added earlier the same day to cut a
14-scene pass from ~100s to ~25s) got ~5 clips through and then failed the
remaining **16 of 21** with `request/transcode error`. Sequential always
worked. One builder routed around it with a scratch wrapper — correct call, but
it left the trap armed.
*Fixed:* pool default 5 → 3 and `TTS_WORKERS` env-overridable; bounded retry
with exponential backoff (2s/4s/8s) per clip; the final attempt re-raises so a
genuinely bad clip still fails loudly. `tests/run_tests.py` → 36 passed, 0
failed. Retry behaviour smoke-tested both ways (transient recovers, permanent
raises).

**A4 — `brand/voice-and-tone.md` reads removed from two agents** (owner
directive, not a defect): `script-refiner.md` and `qa-facts.md`. Note the
refiner's removed block also carried the "don't pad with invented lines"
warning; the anti-invention guarantee now rests on the agent's own contract and
the mandatory qa-facts pass.

---

## B. Open — real defects, not yet fixed

**B1 — `iconCue` leaves a visible dot from t=0 until the cue fires.** *(highest
viewer-visible impact)* — **FIXED (follow-up session), central this time.**
The Motion v2 icon path holds strokes at `strokeDasharray "100 100" /
strokeDashoffset 100` from timeline start, but round line-caps still paint a
~4px navy dot. On light canvases this is clearly visible — worst case measured
**5.7s** of a stray dot before the icon draws. Affected `scla-condition`,
`scla-statement`, `scla-steps`, `scla-chips`, `scla-morph` — **plus
`scla-points`**, a sixth occurrence found while fixing the other five (same
ICONS-library pattern, not previously flagged; the per-item icon there
cascades through its row's own opacity fade instead of sitting in a static
wrapper, but the same round-linecap dot is visible either way).
*Fix applied:* the icon host is held at `opacity: 0` from t=0 and set to
`opacity: 1` at the same cue that starts the stroke-draw tween (`drawAt` /
`iconAt`) — the draw-on tween is the reveal, the opacity flip just keeps the
dot hidden until then. Six hosts, six call sites:
`#cd-iconwrap` (scla-condition), `#sm-iconwrap` (scla-statement),
`#st-iconwrap` (scla-steps), `#cc-iconwrap` (scla-chips), `.mp-cicon`
(scla-morph, per-card — `buildIcon()`/`drawIcon()` now carry `wrap` through),
`.kp-icon` (scla-points, per-item — `iconSets[i].wrap`).
Documented as a normative rule in `design-system/frame.md` → "Living icon
library" so a future icon-bearing template repeats it.
*Consequence:* the six workspaces at the hyperframe gate (table above) still
hold **pre-fix** copies of these templates in their own `compositions/` —
this fix does not retroactively reach them. Rebuild or manually refresh
`compositions/` before shipping any of the six (see C2's new preflight check,
which now catches exactly this and will FAIL on all six until refreshed).

**B2 — `scla-chips` with `reveal:"slide"` trips the layout auditor.**
`inspect` reports `text_occluded #cc-field inside div.cc-bg` ~0.11s into the
scene. Diagnosis: `slide`'s from-state translates chips `x: ±90 / y: -70` at
opacity 0, so a hit-test at `#cc-field`'s centre falls through to the
full-bleed `.cc-bg`. `pop` keeps chips near their layout position, so it does
not fire. The snapshot at that instant shows furniture painted and content not
yet entered — **a transient-entrance false positive, not a reading defect.**
*Current state:* worked around by switching two chips scenes to `pop` on
`how-to-make-strong-career-decisions` — i.e. a motion-design change made to
satisfy a buggy check. *Correct fix is in sampling, not the template:* the
modern CLI exposes `--at`, `--samples`, `--at-transitions`; the audit should
skip or tolerate the entrance window (content settles by 1.2s per `frame.md`).

**B3 — `invalid_variable_values_json` lint fires falsely, once per scene.**
`preflight.py` and the `hyperframes` CLI rewrite `data-variable-values` from
single-quoted JSON to the HTML-escaped form; `hyperframes@0.7.76`'s lint then
parses the attribute **without unescaping** and errors. Reproduced on the
untouched, already-shipped `m1_mini-syllabus` build — **14 errors, one per
scene** — so it is environmental, not authoring. Rendering provably unaffected.
This makes `npm run check` untrustworthy as a gate: a real error can hide in a
wall of false ones.

**B4 — CLI version drift.** Every workspace `package.json` pins
`hyperframes@0.7.45` and runs the **deprecated** `lint && validate && inspect`
chain; the installed/global CLI is `0.7.76`, where those are aliases for
`check`. The 0.7.45 pin is deliberate (documented landmine, `#2064`), but the
consequence — builds audited by an old command whose successor has the
sampling flags that would fix B2 — is not.

---

## C. Process friction (no code defect, still cost time)

**C1 — Subagents die with the parent process.** Two of three builders were
killed mid-run when the process exited. Their `scenes.json` survived and matched
their generated `index.html`, so both were resumable from disk via
`SendMessage` — but nothing detects or auto-resumes this. A fresh session
should check for orphaned workspaces before dispatching new builds.

**C2 — Workspace `compositions/` go stale silently.** They are copied at init
and never refreshed. Two builds were on pre-Motion-v2 templates and needed a
manual refresh from `design-system/compositions/`. Nothing warns. **This is the
same class as A1/B1: the design system and the workspaces drift, and only a
human notices.** A version stamp or a preflight freshness check would close it.
*Fixed (follow-up session):* `preflight.py` gained a `composition_freshness`
check (section "2c", wired into `main()` right after `instance_templates`).
For each non-instanced file in `<ws>/compositions/*.html`, it hashes just the
`<style>`/`<script>` inner text and compares against
`design-system/compositions/<same name>.html`. **Why not a whole-file diff:**
HyperFrames re-serializes composition HTML on catalog/build (quote style,
self-closing tags, injected `data-hf-id` attrs), so every already-initialized
workspace fails a byte-for-byte comparison even when fully fresh — confirmed
against a real workspace (`m1_mini-syllabus`'s `scla-title.html`: whole-file
diff is large, `<style>`/`<script>` content is byte-identical). RAWTEXT
`<style>`/`<script>` blocks pass through that re-serialization unchanged and
are where every real template edit lives, so hashing just those blocks gives
a true-positive/true-negative signal — verified both directions against real
workspaces (correctly silent on files I hadn't touched, correctly flagged
stale on the six files this session's B1 fix touched).
*Known gap, by design:* instanced clones (`basename__suffix.html`, e.g.
`scla-chips__scene_06_tools.html`) are skipped, not compared — their ids are
deliberately renamed per-slot by `instance_templates.py`'s `clone()`, and
diffing them against the un-namespaced source would require re-running that
rename transform. A workspace with only instanced clones for a given template
(no bare `scla-<name>.html` slot) gets **zero** freshness coverage on it —
next session, worth deciding whether that's acceptable or whether the check
should reconstruct the expected clone content via `clone()` and compare that.
*Also:* no accompanying test was added to `tests/run_tests.py` — the suite
still reports "36 passed, 0 failed" (unchanged) and this check has only been
verified by manual script, not a fixture. Worth adding one.

**C3 — `preflight.py --script` auto-locate fails for every `m<N>_` build.**
Known and documented, still a footgun: when the workspace stem carries a
program segment the script filename lacks, the fidelity check silently WARNs
and **skips**. Passing `--script` explicitly is mandatory, and a skipped
fidelity gate looks identical to a passed one at a glance.

**C4 — The snag log was actively misleading.** Its latest entry described
`m2_four-kinds` as half-authored (28 scenes vs 9-scene narration, 33 boundary
violations, 20 colliding slots). The live gate disagreed on every count — the
build had been repaired after that entry was written. Running the gate cost
seconds; trusting the log would have cost a needless rebuild. **Treat the
snag-log Open list as a lead, never as state.** State is the folder plus the
gate.

**C5 — Stale preview servers.** Five servers were found running on ports
3002–3006 from earlier work, serving unknown workspaces, with no way to tell
what each was showing. Only 3002–3004 are declared in
`.devcontainer/devcontainer.json`, though higher ports forward fine on bind.
`scripts/preview.sh` serves one workspace per port and auto-picks the lowest
free one, which makes a stale server easy to mistake for a fresh build.

**C6 — Wistia re-ship needs a manual takedown.** The `WISTIA_API` token cannot
delete. Three of these six are **already live on Wistia** with the
template-collision defect, so re-shipping means a new upload plus a manual
removal in the Wistia UI — a window where both cuts are public. Blocks any
notion of a fully unattended publish path.

**C7 — Build cost.** With the `scenes.json` manifest flow the builders used
~158k / ~216k / ~249k tokens and roughly 5 / 11 / 16 minutes each. The manifest
change (made earlier the same day) already removed the dominant cost — hand-
writing `index.html` was ~85% of wall clock. Remaining cost is iteration
against the gates.

---

## D. What a fresh session should probably do first

Ordered by expected payoff, not effort. **Items 1–3 done as of the follow-up
session** (see the "FIXED (follow-up session)" notes in A1/B1/C2 above) —
left here struck through so the ordering/reasoning stays legible, not as
open work.

~~1. **B1** — the only item in this document a viewer can see. Fix centrally
   in the five templates, then decide whether to refresh + rebuild the six
   existing workspaces (they hold their own copies).~~ **Done** — fixed
   centrally in six templates (five plus scla-points, found in the process).
   The "decide whether to refresh + rebuild the six workspaces" half is
   **still open** — do that next, now forced by C2's new preflight check.
~~2. **A1 residual** — audit the other eight templates for unprefixed ids
   before the next build discovers one.~~ **Done** — audited all 11
   non-morph templates; clean, no other offenders.
~~3. **C2** — a freshness check on workspace `compositions/`. This silently
   produced two pre-v2 builds this session and will do it again.~~ **Done**
   — `preflight.py` now hard-fails on stale `compositions/` (see C2 above for
   the one known gap: instanced-clone-only templates get no coverage).

Remaining, in the original order:

4. **B3 + B4 together** — decide whether `npm run check` is a gate or advisory.
   Right now it is neither, reliably.
5. **B2** — fix the audit sampling so entrance windows stop forcing
   motion-design workarounds.
6. **C1** — orphan detection before dispatch.
7. **New, from this session:** refresh + rebuild (or re-verify) the six
   workspaces in the table at the top of this document against the fixed
   templates — `preflight.py` will refuse all six until that happens.

## E. What worked and should not be disturbed

- The **manifest-first flow** (`build_index.py --extract` → edit `scenes.json`
  → regenerate) is what made a 9→22-scene re-author cheap. Never hand-edit
  `index.html`.
- **Deterministic gates caught every real defect**, including two the
  orchestrator introduced (a mid-sentence cut, a template collision). The
  builders' self-reports were accurate every time they were spot-checked — but
  they were spot-checked, and that is the right posture.
- **Word-preserving punctuation repair** cleared three deadlocks at zero
  fidelity cost (0.00% mismatch on all three).
- **Per-scene TTS caching** meant re-splitting scenes re-synthesized only the
  changed clips.
