# Oversight Brief — First End-to-End Run After the Pipeline Refactor

**Date:** 2026-07-13 · **Video:** `finding-creating-a-career-purpose-statement_early-career-boost_2026-07-10`
**Style package:** horizon · **Overseer:** Claude (Fable 5), with one Explore subagent for pipeline inventory
**Verdict up front:** the refactored pipeline ran end to end with **zero manual timing work, zero gate failures, and one real snag** (a CLI flag that no longer exists). The deterministic core — anchors → compiler → preflight → render → verify — behaved exactly as designed. The problems found are all at the *edges*: stale docs, a missing hook, and two ambiguities that will bite an unsupervised session.

---

## 1. What happened, in plain terms

1. **Preflight** caught two known environment traps before they could bite: `/dev/shm` was 64M (would hang Chrome mid-render) → remounted to 512M; and the TTS Python issue from the snag-log → `HYPERFRAMES_PYTHON` set preemptively. The snag-log memory loop did its job.
2. **Script gate** was skipped legitimately: the refinement log showed the script as Refined 2026-07-12 / not yet rendered → pre-approved fast path, exactly as the skill specifies.
3. **TTS hit the run's one real snag** — the runbook command `npx hyperframes tts --provider kokoro` failed: hyperframes 0.7.56 **removed the `--provider` flag** (kokoro is now the only built-in engine). Dropping the flag fixed it. This is doc drift between the skill and the upstream CLI, now logged in the snag-log.
4. **Narration + transcript** generated cleanly (113.4s, 362 words).
5. **Assembly**: 10 scenes from 6 of the 9 templates, all timing declared as verbatim transcript anchor phrases, every number a placeholder. The demo reel turned out to be the *wrong* pattern to copy (see §3.5) — the previous lesson build was the correct reference.
6. **Compile → preflight → check: all green on the first pass.** The compiler resolved all 10 boundaries + 17 cues, inserted boundary silence (audio 113.4s → 119.5s), set root duration 120.56s. Preflight: PASS, 0 violations. `npm run check`: 0 errors (one pre-existing cosmetic contrast warning on the `scla-steps` ghost numeral — decorative by design).
7. **Render #1 + verify: the new deterministic gate earned its keep.** The first render came back clean on container truth, but `verify_render.py`'s presence check **failed the build**: the outro sat pixel-static for 5.5s while narration was still speaking (plus two 3–3.5s gray-zone stagnations). Exactly the defect class the refactor moved from "four QA agents might notice" to "a script fails the exit code". Fix was per the animacy rule: split the two over-long scenes and add a fourth cued step — 10 scenes became 12.
8. **Rebuild loop hit snag #2** — recompile refused two cue phrases because whisper emits em-dash-joined compound tokens (`buzzwords—just` is one token; the phrase "no buzzwords" can't match inside it). The compiler's error named the scene and the exact transcript window, so the fix took one edit. Doc'd in the snag-log as a new phrase-authoring rule.
9. **Render #2 + verify** — see §2.
10. **QA gate** — presented to the human; outcome pending sign-off.

Two subagents were used: an **Explore agent** inventoried the whole pipeline in parallel with the build (its findings are folded into §3) and the render ran as a background task while this brief was drafted. **Neither went off track**; no intervention was needed.

## 2. Render + verify result

**Render #2 verified clean: PASS, 0 violations.** Container truth: 122.03s video / 122.05s audio / root 122.02s, 1920×1080. Presence: 245 frames sampled, no blank/default/dead frames; two gray-zone stagnation warnings (3.0s and 4.5s, both under the 5s deterministic trip) judged acceptable in self-review — one sits between two step reveals, the other is a statement card whose reading ripple falls below the pixel-diff threshold. Frame review of all 12 scenes: horizon package consistent, reveals land on their spoken cues, no clipping, outro holds ≥1s past the last word.

**Audio verified correct.** The §3.6 suspicion resolved in the pipeline's favor: re-transcribing the suspect segment with whisper `base.en` produced *"specific enough to guide a real decision"* — the script line as written. `small.en` had simply misheard it. The narration is right; the finding stands only as evidence that a script-vs-transcript diff gate would flag false positives at ~1 word per 360 with `small.en`, so it should gate on a threshold, not exact match.

**Cost of the full run:** 2 renders, 1 rebuild loop, ~35 minutes wall clock, well inside the tool-call budget.

## 3. Snags, confusion, and bugs found

Ordered by how much they'd hurt a future unsupervised session.

### 3.1 The snag-retro hook is gone (regression from the refactor)
Commit `32c1356` added an on-by-default "SNAG RETRO" PostToolUse reminder on render, and `render-qa/tests/test_retro_hook.sh` still asserts it exists in project `.claude/settings.json`. But after the settings refactor, **project settings has no `hooks` block at all** — the string "SNAG RETRO" exists nowhere except the test. The test fails; the snag-log update at close-out is now purely voluntary. The self-improvement loop's enforcement half silently disappeared. *(Found by the Explore subagent; confirmed against `.claude/settings.json` + its `.bak`.)*

### 3.2 The workspace's own CLAUDE.md routes to deleted skills
`hyperframes init` generates a CLAUDE.md inside every build workspace that tells the agent to route requests through `/faceless-explainer`, `/general-video`, `/motion-graphics`, etc. — the 12 generic skills that were just deleted from this repo. A future session that opens a workspace and reads its CLAUDE.md (which it will — it's auto-loaded context) gets pointed at workflows that no longer exist, directly contradicting the repo's routing contract ("produce-video owns orchestration"). This is upstream boilerplate, so it will regenerate on every `init`.

### 3.3 CLI doc drift: `tts --provider` no longer exists
The skill's Step 2 command block and `frame.md`'s voice pin both say `--provider kokoro`; hyperframes 0.7.56 rejects the flag. Cost this run ~3 minutes; would confuse an unsupervised session longer. Fix: drop `--provider` from the SKILL.md command (voice/speed flags still work).

### 3.4 Style-package rotation doesn't see in-flight builds
The rule rotates summit → horizon → cadence by the program's **delivered** count (mod 3). Delivered = 1 → this run correctly computed **horizon**. But `career-building-is-a-repeatable-process` (built, unrendered-in-log, still in `renders-hyperframes/`) already used horizon — so two consecutive lesson videos will ship in the same look, which is what the rotation exists to prevent. The rule needs to count *builds started*, not videos delivered — or read the themes actually used in `renders-hyperframes/` + `renders-mp4/`.

### 3.5 The demo reel is a stale "pattern to copy"
`design-system/index.html`'s header comment calls itself "the instantiation pattern to copy for lesson builds", but it predates the anchor contract: numeric cues, no `data-anchor-end`, no `data-cue-anchors`, no `<audio>` at root. An unsupervised session that obeys that comment would hand-type timing numbers — the exact defect class the compiler was built to eliminate. The real pattern lives in the previous lesson build's `index.html`. Either retrofit the demo reel with anchors or fix its comment to point at a canonical anchored example.

### 3.6 Transcript mishears go undetected (resolved for this run, gap remains)
Whisper `small.en` heard *"**I am honest** enough to guide a real decision"* where the script says *"**Specific** enough…"* (~28s, scene 04). A `base.en` cross-check of the extracted segment confirmed **the audio is correct** — the transcription model misheard, kokoro didn't misread. No harm this run, but the gap is real: the pipeline never compares the transcript back to the approved script, so an *actual* TTS misread would sail through every gate and reach the human ear only. A fuzzy script-vs-transcript word-diff in preflight (threshold-based, since small.en mishears ~1 word in 360) closes it.

### 3.7 Em-dash compound tokens break cue-phrase matching
Whisper tokenizes speech across em-dashes as single words (`artifact—a`, `buzzwords—just`). The compiler's phrase matcher strips punctuation per token but never splits a token, so an anchor phrase that ends or starts *inside* a compound ("no buzzwords") silently fails to resolve. Workaround: quote the compound verbatim from the transcript ("no buzzwords—just"). Real fix: normalize em-dashes to token boundaries in `hfp_common.py`'s matcher. The failure message is good (names scene + window); the *rule* just isn't written anywhere an author would read first.

### 3.8 Smaller findings (from the Explore inventory)
- `qa-layout.md` line 26 references `pipeline/verify_render.py` — the `pipeline/` directory no longer exists (real path: `render-qa/`).
- All governance/budget hooks live only in **global** `~/.claude/settings.json`; a fresh clone gets no tool budget, no governance checks. Not portable.
- `check_boundaries.py` / `check_presence.py` physically live under `.claude/skills/adversarial-qa/scripts/` but the *always-on* gates import them — the "on-demand" skill dir is load-bearing for every render. Works, but the coupling is easy to break by "cleaning up" adversarial-qa.
- Permission-list drift between project and global settings (`Bash(mkdir *)` vs `Bash(mkdir:*)` forms; legacy `cat/head/tail` entries).

## 4. Annotated pipeline map (as it runs today)

```
                       ┌────────────────────────────────────────────────────────────┐
                       │  /produce-video  (SKILL.md — owns sequence + every command) │
                       └────────────────────────────────────────────────────────────┘

  STEP 0 · PREFLIGHT           STEP 1 · SCRIPT                 GATE 1 ██ SCRIPT GATE ██
 ┌─────────────────────┐      ┌──────────────────────┐        (human approves narration)
 │ date · pkill preview│      │ refinement-log.md    │              │
 │ /dev/shm ≥256M ⚠64M!│ ───► │ fast path:           │──[refined+un-│rendered = skip gate]──┐
 │ CLI pin ≥0.7.45     │      │ draft/refine + facts │              ▼                       │
 │ snag-log Known list │      │ (qa-facts agent)     │───► gate stops here otherwise        │
 └─────────────────────┘      └──────────────────────┘                                      │
                                                                                            ▼
  STEPS 2–5 · MACHINE BUILD (no human stops) ───────────────────────────────────────────────┐
 │                                                                                          │
 │  init workspace ──► copy design-system (frame.md, 9 scla-* templates, fonts, logos)      │
 │        │                                                                                 │
 │  tts (kokoro af_heart ⚠ --provider flag removed in 0.7.56)                               │
 │        │            └── HYPERFRAMES_PYTHON must point at kokoro_onnx interpreter         │
 │  transcribe (whisper small.en) ──► transcript.json  ⚠ no script-vs-transcript diff gate  │
 │        │                                                                                 │
 │  assemble index.html — anchors ONLY, numbers are placeholders                            │
 │        │               (pattern: previous build, NOT the stale demo reel)                │
 │        ▼                                                                                 │
 │  compile_timeline.py --apply   ◄── owns ALL numbers: boundaries, cues, silence padding,  │
 │        │                            sceneDuration, audio + root duration                 │
 │  preflight.py  (4 checks: drift · boundaries · coverage · variables)  ── exit 0 or loop  │
 │  npm run check (lint · runtime · layout · motion · contrast)          ── exit 0 or loop  │
 └────────┬─────────────────────────────────────────────────────────────────────────────────┘
          ▼
  STEP 6 · RENDER + VERIFY
 ┌──────────────────────────────┐     ┌──────────────────────────────────────────┐
 │ npm run render ──► MP4       │ ──► │ verify_render.py (3 jobs: container truth │
 │ (⚠ SNAG RETRO hook missing — │     │  · presence v2 · qa/frames/ dump 3/scene) │
 │  refactor regression)        │     └──────────────────────────────────────────┘
 └──────────────────────────────┘                      │
          builder self-review of qa/frames/ ◄──────────┘
          (replaces old 4-agent gauntlet; /adversarial-qa = escalation only)
          ▼
  GATE 2 ██ QA GATE ██  (human watches MP4, qa-checklist.md)
          ▼
  STEP 7 · CLOSE OUT
  file MP4 → renders-mp4/<program>/ ──► Wistia upload ──► refinement-log Rendered date
  archive-lesson.sh <stem> → _archive/ (refuses if MP4 not filed)
  snag-log.md append (⚠ voluntary — enforcement hook gone, §3.1)
```

Legend: `██` = the only two human stops · `⚠` = issue found this run (see §3).

## 5. Recommendations (highest leverage first)

1. **Restore the snag-retro hook** in project `.claude/settings.json` (its test already exists — make `test_retro_hook.sh` pass again). Without it the self-improvement loop depends on the model remembering; that's the failure mode the hook existed to remove.
2. **Add a script-vs-transcript diff gate** to `compile_timeline.py` or `preflight.py` — fuzzy word-diff of `transcript.json` against the approved `.txt`; fail above a small threshold. Catches TTS misreads (§3.6), which today only a human ear can catch.
3. **Neutralize the generated workspace CLAUDE.md** — add a post-init step to the skill (overwrite it with two lines pointing back at `/produce-video` + `design-system/CLAUDE.md`), since upstream regenerates it every init.
4. **Fix rotation to count builds, not deliveries** (§3.4) — one-line rule change in `frame.md`.
5. **Update the skill's TTS command** (drop `--provider`) and consider pinning the CLI minor version in the skill text less specifically than command flags — flags belong to `--help`, not docs.
6. **Retrofit or re-label the demo reel** (§3.5) so the "copy this" comment points at an anchored example.
7. **Fix the stale `pipeline/` path** in `qa-layout.md`; move `check_boundaries.py`/`check_presence.py` into `render-qa/` (the always-on home) and have adversarial-qa import from there, not the reverse.
8. **Commit a project-level hooks block** (or document the global dependency) so a fresh clone keeps the budget + governance rails.

## 6. Model fit per pipeline step

The pipeline is mostly deterministic scripts; model intelligence only matters at the judgment points. Fastest cheap model that clears each bar:

| Pipeline step | Nature of the work | Recommended model | Why |
|---|---|---|---|
| Step 0 preflight, compile/preflight/check loop, render, verify, archive | Running scripts, reading exit codes | **Haiku 4.5** | Deterministic tooling; the scripts are the intelligence. Any model that follows a runbook works. |
| Step 1 script drafting/refinement | Brand voice, curriculum fidelity, judgment about what to cut | **Fable 5** (or Opus 4.8) | Highest-stakes creative text; errors here survive to every render. The "never cut callbacks" class of rule needs strong instruction-holding. |
| Step 1 facts check (qa-facts lane) | Claim-by-claim source comparison | **Sonnet 5** | Careful reading, low creativity; cold context is the point, not raw power. |
| Steps 2–5 scene assembly | Mapping narration beats → templates, picking anchor phrases, animacy rules | **Fable 5 / Opus 4.8** | The one genuinely hard step: design judgment + a long normative spec (frame.md) + exact verbatim anchor discipline. This run's zero-retry compile came from careful phrase selection. |
| Step 6 frame self-review (`qa/frames/`) | Visual judgment against transcript | **Opus 4.8 or Sonnet 5** (vision) | Needs image reading + taste; Sonnet 5 is fine when the deterministic gates are green, Opus when escalating. |
| /adversarial-qa lanes (on-demand) | Four independent break-it audits | **Sonnet 5** | Parallel cold-context reviewers; volume over depth. Escalate a stubborn lane to Opus 4.8. |
| Orchestration of the whole run | Sequencing, snag handling, gate discipline | **Sonnet 5** for routine runs; **Fable 5** when observing/changing the pipeline itself | Once the runbook is stable, the orchestrator mostly follows it; first runs after a refactor (like this one) warrant the frontier model. |

**Practical default:** run `/produce-video` on Sonnet 5, with the scene-assembly step being the reason to upgrade a given run to Opus/Fable (e.g., a lesson needing many bespoke illustrated scenes rather than template instantiation).

---
*Written during the run; render/verify section finalized at completion. Snag §3.3 appended to `snag-log.md` per Step 7.*
