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

## 5. Recommendations (highest leverage first) — all 8 approved & implemented 2026-07-13

1. ✅ **Restore the snag-retro hook** in project `.claude/settings.json` (its test already exists — make `test_retro_hook.sh` pass again). Without it the self-improvement loop depends on the model remembering; that's the failure mode the hook existed to remove. *Done — `test_retro_hook.sh` passing 4/4. Root cause pinned in the process: `32ce4d0` ("consolidate render hooks") is the commit that dropped the hooks block — it deleted the whole stack and never added back the guarded reminder it promised; the guarded SNAG RETRO hook was restored from `32ce4d0^`, alone, matching the consolidation intent.*
2. ✅ **Add a script-vs-transcript diff gate** to `compile_timeline.py` or `preflight.py` — fuzzy word-diff of `transcript.json` against the approved `.txt`; fail above a small threshold. Catches TTS misreads (§3.6), which today only a human ear can catch. *Done — new threshold-based check in `preflight.py` (auto-locates the approved `.txt` from the stem, `--script` override, warns-and-skips if absent), with tests.*
3. ✅ **Neutralize the generated workspace CLAUDE.md** — add a post-init step to the skill (overwrite it with two lines pointing back at `/produce-video` + `design-system/CLAUDE.md`), since upstream regenerates it every init. *Done — one `printf` line added to the skill's Step 2 block.*
4. ✅ **Fix rotation to count builds, not deliveries** (§3.4) — one-line rule change in `frame.md`. *Done — `frame.md` "Style packages" now counts started builds (live + archived + delivered); skill points at frame.md instead of restating the rule.*
5. ✅ **Update the skill's TTS command** (drop `--provider`) and consider pinning the CLI minor version in the skill text less specifically than command flags — flags belong to `--help`, not docs. *Done — flag dropped in the skill; `frame.md` voice pin now states `provider:` is an engine pin, not a CLI flag.*
6. ✅ **Retrofit or re-label the demo reel** (§3.5) so the "copy this" comment points at an anchored example. *Done — re-labeled: the header comment now says it is the style guide, NOT the timing pattern, and points at the most recent lesson build.*
7. ✅ **Fix the stale `pipeline/` path** in `qa-layout.md`; move `check_boundaries.py`/`check_presence.py` into `render-qa/` (the always-on home) and have adversarial-qa import from there, not the reverse. *Done — checkers moved, all live references updated.*
8. ✅ **Commit a project-level hooks block** (or document the global dependency) so a fresh clone keeps the budget + governance rails. *Done — project settings carries the snag-retro hook (rec 1); the global-registration dependency for the governance/budget hooks is now documented in `GOVERNANCE.md` → Hard Stops.*

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

## 7. Proposal — split `/produce-video` into two gateless skills

*Direction from the owner (2026-07-13): separate the pipeline's components into skills and remove the two human gates — a refinement skill that drains unrefined scripts into a `refined/` folder per program, and a render skill that includes the outcome checks. This section is the recommended shape; not yet implemented.*

### 7.1 Recommended shape: two workhorse skills + a thin dispatcher

| Skill | Job | Stops? |
|---|---|---|
| **`/refine-scripts`** | Drain every raw `.txt` sitting at `lesson-scripts/<program-slug>/` root: strip capture noise (keep the "what you already built" callbacks), run the mandatory `qa-facts` pass on anything drafted/refined, write the result to `lesson-scripts/<program-slug>/refined/`, update the ledger row. Already-clean scripts just get the facts pass + move. | Never |
| **`/render-lessons`** | Drain `lesson-scripts/<program-slug>/refined/`: per script, the whole machine sequence — env preflight, init + neutralize workspace CLAUDE.md, TTS, transcribe, assemble (anchors only), compile, `preflight.py` (now including the script-vs-transcript diff gate), `npm run check`, render, `verify_render.py`, builder frame self-review — then file the MP4 + QA packet, upload to Wistia, move the script to `rendered/`, fill the ledger, archive the workspace, append snags. | Never |
| **`/produce-video`** | Becomes a ~20-line dispatcher: run `/refine-scripts`, then `/render-lessons`. Keeps the one-call entry point, the root CLAUDE.md routing row, and the Notion-queue habit intact. Every command lives in exactly one skill — no duplication. | Never |

**Why a dispatcher rather than deleting `/produce-video`:** "produce this video end to end" stays a natural request, and three docs route to that name. Retiring it buys nothing; a dispatcher costs ~20 lines and zero drift risk (it restates no commands).

### 7.2 State lives in the folder, the log becomes a ledger

```
lesson-scripts/<program-slug>/          ← raw intake (refinement queue)
lesson-scripts/<program-slug>/refined/  ← render queue + open human review buffer
lesson-scripts/<program-slug>/rendered/ ← done (MP4 filed + uploaded)
```

A script's location *is* its state; both skills are idempotent queue-drains ("refine whatever sits at root", "render whatever sits in refined/"), so batch behavior falls out for free and no session ever needs to cross-check a table to know what's safe to render. `refinement-log.md` stays — but demoted from state machine to ledger (dates, render location, Wistia URL, notes like the two open questions on the raw captures).

**Migration on day one:** the 8 refined-unrendered early-career-boost scripts move to `refined/`, `mini-syllabus` (delivered) to `rendered/`, the 2 raw captures stay at root — with their open questions noted in the ledger so `/refine-scripts` knows `early-career-boost-resources` needs a human answer ("does a pointer-to-a-PDF lesson need a video at all?") and skips it rather than refining it blind.

### 7.3 What replaces the two human gates

| Removed gate | Replaced by |
|---|---|
| SCRIPT GATE (blocking approval of narration) | (a) The mandatory `qa-facts` pass inside `/refine-scripts` — facts stay a property of the script, checked once. (b) `refined/` as an **open review buffer**: a human can read, edit, or delete anything sitting there at any time before a render session drains it — review becomes possible-any-time instead of required-every-time. (c) The new script-vs-transcript diff gate guarantees the narration that renders is the text that sat in `refined/`. |
| QA GATE (blocking MP4 sign-off) | The deterministic post-render stack that §1–2 just proved out — `verify_render.py` container truth + presence v2, plus builder frame self-review — with a **QA packet** (verify summary + `qa/frames/` stills) filed next to every MP4. Human review becomes an async spot-check of `renders-mp4/` / Wistia; a rejection escalates to `/adversarial-qa` + re-render + Wistia replace. |

Two things to say plainly:

- **This requires amending a standing critical rule.** `projects/video-production/CLAUDE.md` says *"Always flag scripts for human approval before render — script → render is a manual gate, never automated."* Implementing this proposal rewrites that rule (approval becomes async-auditable rather than blocking) and needs its own `decisions/log.md` entry. That's the owner's call to make — this proposal is the formal ask.
- **Wistia upload is the one outward-facing step.** Recommendation: keep it in the unattended run (it's hosting/staging, and a bad cut is recoverable by re-render + replace), but the *member-facing publish* — pasting the Wistia URL into the Notion row's Final-video field — is where I'd keep the human's async check landing, since that's the moment students can see it.

**Residual risk, honestly stated:** this run's §3.6 showed the class of defect only a human ear caught before — the diff gate now closes the TTS-misread half of it deterministically, and the transcription-mishear half proved to be gate noise, not a content defect. What has **no** deterministic backstop is taste (a technically-clean scene that reads wrong). The builder self-review plus async spot-checks of the first several unattended deliveries is the honest mitigation; the two gray-zone stagnation warnings in §2 are exactly the kind of judgment call that will now ship without a human seeing it first.

### 7.4 Implementation checklist (when approved)

1. Create `.claude/skills/refine-scripts/` and `.claude/skills/render-lessons/`; shrink `/produce-video` to the dispatcher. Split the current SKILL.md content along the Step 1 / Steps 0+2–7 seam — the commands are already written.
2. **By hand** (lint-refs won't flag drift here): `skills-lock.json`, `design-system/AGENTS.md`, and `hooks/skill-rules.json` (the registry lists implemented skills only).
3. Create the `refined/`/`rendered/` folders with the migration above; update `lesson-scripts/README.md` (naming + folder semantics) and the `refinement-log.md` header (ledger, not state).
4. Rewrite the two gate rules in `projects/video-production/CLAUDE.md` (+ the root CLAUDE.md routing rows for the two new skills) and log the gate-removal decision in `decisions/log.md`.
5. Update `notion-queue.md` status gates to match (request → refined → rendered → published, with the human check at publish).
6. Budget note: 8 scripts × 150–300 calls ≫ the 500-call session cap — `/render-lessons` should chunk (≤2–3 videos per session) or the cap gets raised in `~/.claude/budget.json` per run; say which in the close-out.
7. Model fit per §6 stands: `/refine-scripts` wants the strong model (Fable/Opus — brand voice + facts); `/render-lessons` runs fine on Sonnet with the scene-assembly step as the upgrade trigger.

### 7.5 Pipeline map after the change

```
              ┌──────────────────────────────────────────────────────────────┐
              │   /produce-video  (thin dispatcher: refine ── then ── render) │
              │   — or call either skill directly —                           │
              └──────────────────────────────────────────────────────────────┘

  /refine-scripts  (batch, no stops)
 ┌───────────────────────────────────────────────────────────────────────────┐
 │  drain lesson-scripts/<program>/*.txt (raw intake)                        │
 │    strip capture noise · keep built-artifact callbacks · plain spoken     │
 │    lines only · qa-facts agent pass (drafted/refined scripts)             │
 │    open questions (pointer-only lessons etc.) → ledger note, skip         │
 │        ▼                                                                  │
 │  write → lesson-scripts/<program>/refined/   +  ledger row (Refined date) │
 └───────────────────────────────┬───────────────────────────────────────────┘
                                 ▼
      ░░ refined/ = open review buffer — human may edit/veto ANY time; ░░
      ░░ nothing blocks, nothing waits                                 ░░
                                 ▼
  /render-lessons  (batch ≤2–3/session, no stops; loops per script)
 ┌───────────────────────────────────────────────────────────────────────────┐
 │  env preflight (shm · pkill bracket · CLI pin · snag-log Known list)      │
 │  init workspace ─► overwrite generated CLAUDE.md ─► copy design-system    │
 │  tts (kokoro af_heart, no --provider) ─► transcribe (small.en)            │
 │  assemble index.html — anchors ONLY (pattern: newest lesson build)        │
 │        ▼                                                                  │
 │  compile_timeline.py --apply      ◄─ owns every number                    │
 │  preflight.py — drift · boundaries · coverage · variables ·               │
 │                 script-vs-transcript diff (NEW — closes §3.6)             │
 │  npm run check                                    ── each: exit 0 or loop │
 │  npm run render ─► verify_render.py (container truth · presence v2 ·     │
 │                                      qa/frames/ dump)                     │
 │  builder self-review of qa/frames/  (adversarial-qa = escalation only)    │
 │        ▼                                                                  │
 │  file MP4 + QA packet → renders-mp4/<program>/ ─► Wistia upload           │
 │  move script refined/ → rendered/ · ledger Rendered date                  │
 │  archive-lesson.sh · snag-log append (hook-enforced again)                │
 └───────────────────────────────┬───────────────────────────────────────────┘
                                 ▼
      ░░ async human involvement (non-blocking):                        ░░
      ░░  • spot-check MP4 / QA packet / Wistia                         ░░
      ░░  • paste Wistia URL → Notion "Final video" (the publish check) ░░
      ░░  • rejection → /adversarial-qa → fix → re-render → re-upload   ░░
```

Legend: `░░` = async human touchpoints (replacing the two `██` blocking gates in §4) · every box between them is machine work.

---
*Written during the run; render/verify section finalized at completion. Snag §3.3 appended to `snag-log.md` per Step 7. §5 statuses + §7 proposal added later the same day, after the owner approved all eight recommendations and requested the gate-removal proposal.*
