# Proposal: The Next Video Pipeline

*2026-08-19. Built from `ideal-pipeline.md` (outside research, written before looking at our setup) and `evidence-log.md` (every claim below cites a verified finding there by ID — C = consistency, T = throughput, R = reliability).*

---

## WHAT — where we are

We have shipped 38 lessons. The factory works: scripts go in, Wistia links come out, and a real machine gate stands in front of every render. But the record shows three things clearly:

1. **Each video is designed from scratch.** The builder invents three concepts, picks one, and hand-writes the whole composition against a 196-line list of prose rules. The brand's colors and type are in code; its *motion* and *components* are prose the builder re-creates every time (C10). The result is a look that is brand-colored but not brand-*shaped*: the five recorded owner rejections are all about structure — repeated panels, copied illustrations, overlays crossing cards, panels escaping their box (C4).

2. **The rules are discovered by trial and error, one build at a time.** 344 gate failures across 35 builds; 0 of 35 passed first try; 26 failed five or more times (T4). A build cost 50–80 minutes and a pilot burned ~80 minutes "iterating against gates" (T3). The gates are doing their job — they're just doing it *instead of* the authoring knowing the rules up front.

3. **The factory was rebuilt while it ran.** The lane that builds videos went from "opt-in, unproven" to "the only lane" in six days; a naming rule lasted a day; a write-fence locked the owner out within a day; the stagnation threshold moved three times in six days (R6). Output was 1 video by Jul 13, 6 by Jul 29, 38 by Aug 11 — with 58% shipped in the final two days under a deadline (T1). That's a burst, not a rate.

Underneath those three: checks that couldn't fail (R1), checks that passed total failures (R2), agents reporting success that hadn't happened (R3), a 5-day environment outage nobody was told about (T2), and 88 quarantine incidents in 13 days (R4).

What's *good* and must be kept: narration-first with word timings; one pinned voice; a real machine gate on every build; the blocking-defect / taste split in review; the rejection → fixture → "prove the gate fires" loop (C9, R1); retry caps and a circuit breaker in the run state; a published ledger. Those are ahead of what most teams have.

### Before — how a lesson moves today

```
  script (inbox → ready)
    agent refines · facts check · script-match gate
         │
         ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ BUILDER AGENT — one per lesson, cold start                   │
  │   invent 3 concepts ──▶ selector picks 1 ──▶ design.md       │
  │   author the whole composition by hand                       │
  │   196 lines of prose rules · tokens: palette/type in code,   │
  │   motion/components in prose · "never look at another build" │
  └──────────────────────────────┬───────────────────────────────┘
                                 ▼
                    narration (one voice) → word timings
                                 ▼
                 ┌───────────────────────────────┐
                 │ MACHINE GATE (21 sections)    │◀──┐  ~10 reds per build
                 │ red → edit HTML → re-snapshot │───┘  0 of 35 green first try
                 └───────────────┬───────────────┘
                                 ▼ green
                 visual review — defect + taste — on EVERY video
                                 ▼
                 owner approves, per lesson
                                 ▼
                 render (cloud | local) → verify → publish → ledger

  failures  → quarantine.log: 88 rows / 13 days · rows never clear
  rejection → fixture → registry → new gate   (good loop; retro step often skipped)
  shared machinery (gates, contracts, lanes) changed weekly while producing
```

---

## SO WHAT — the gap against the ideal

The research converged on one idea that we don't have: **build the look once, then assemble.** Teams that keep hundreds of videos looking like one hand (Kurzgesagt, Vox, BBC newsroom graphics, code-first shops) keep a small **kit of scene types** with fill-in slots, put the **motion rules in code** alongside the colors, and measure every new video against a **golden reference**. Freshness comes from content, order, and illustration — not from each video inventing its own grammar.

We tried templates once and the owner rejected the output as flat — "21 scenes on 5 templates," blank slots from a file collision, 12 videos about to look identical (C6, C7). So the pipeline swung to the opposite pole: total freedom per lesson. The evidence says that swing traded one failure for another:

| Stage | Ideal | Us today | Gap |
|---|---|---|---|
| Look system | tokens **incl. motion** in code; scene kit; golden reference; sound kit | palette/type/spacing in code; motion + components as prose; no kit; two approved cuts as informal references (one rejected reference is unrecoverable); one voice, no bed (tick fix is knowledge-only) | **Large** — the root of C2, C3, C4, C5, C10 |
| Script | approved, locked, checked before anything else | refined by agents (fabrication caught by a cold reader, C8); script-match gate; owner-actionable duplicates sat for weeks (T6) | Small–medium |
| Narration | batch first, word timings, cached | yes — strength; provider quirks now clamped (R5) | Small |
| Plan | cheap artifact a human can look at | concept boards + design.md exist but are per-lesson invention, agent-judged; owner sees nothing until ~80 min later | Medium |
| Assemble | fill a kit; no new grammar | author from scratch; 85% of a build was hand-writing HTML (T3) | **Large** |
| Machine gates | 100%, catch defects | 100%, 21 sections, firing tests — strength; but used as the discovery loop (0% first pass, T4); history of gates that couldn't fail (R1) and passed empty frames (R2); two gates pull against each other (C10) | Medium — the gates are compensating for the missing kit |
| Review | defect vs taste; full on first-of-kind, sampled after | defect vs taste: yes; but taste runs per video (was meant to be pilot-only and never landed, T3); owner approves per lesson | Small–medium |
| Render | parallel, cloud, pinned, tested fallback | cloud lane exists and is pinned; 17 cloud timeouts; upload broke; now back on local; local hung 35 min on a long lesson — fallback untested (T8) | Medium |
| Post-render | machine check + sampled eyes | yes — verify + sampled encode review | Small |
| Publish | API + ledger | yes; takedowns need a human (token scope) | Small |
| Failure handling | structured record, caps, breaker, quarantine, classified | record, caps, breaker, quarantine: yes; timeouts misread as content defects; rows never clear; no watchdog (T8, T9, R4) | Medium |
| Metrics | first-pass, rework, escape tracked | none computed; all the data exists in logs (evidence log, "absent") | **Large but cheap** |
| Rejection → gate | every rejection becomes a check | yes, with firing tests — *ahead* of the ideal; retro step silently stopped running (R8); owner-calibrated MP4 thresholds live only in a memory note | Small |
| Stability | pilot, then batch, on a frozen version | factory redesigned weekly while producing (R6, T1) | **Large** |

Read the table top to bottom and the picture is simple: **we have the back half of the ideal pipeline (gates, review, render, publish, rejection loop) and are missing the front half (a look system and a kit to assemble from), and we change the machinery too often for the back half to be trusted.**

---

## NOW WHAT — the changes, in priority order

Each change: what · why (evidence) · which goal it serves · size · tradeoff and my recommendation.

### 1. Build the scene kit — the middle path between templates and freeform
**What.** A small library (8–12) of *layout skeletons with motion presets, in code* — title, statement, list-reveal, comparison, steps/process, quote, callout, diagram-with-stations, close, and so on. Each has fill-in slots for copy and illustration. The builder **chooses and fills; it does not invent grammar.** Every kit scene is pre-verified green against all 21 gate sections *and* judged ALIVE against the owner's approved reference cuts before it enters the kit. Motion and component values move out of prose in `tokens.yml` into code presets the kit uses. A new scene type is allowed — proposed by a builder, reviewed once, then it's in the kit for everyone.
**Why.** All five recorded rejections are structural, not content (C4). The fixed-skeleton trick that resolved the ink-vs-churn fight was invented by hand on one lesson and is not shared (C10). Ripples came back because re-adding motion was a two-line fix for a failing gate — a kit with no ripple removes the option (C2). 0 of 35 builds passed first try (T4): a kit scene that already passes can't fail those sections.
**Goals.** All three — this is the only change that moves all three at once.
**Size.** Largest in the plan: ~3–4 weeks to build and calibrate, then a 3-clean-run pilot.
**Tradeoff.** Template fatigue is real and the owner already lived it (C3, C6, C7). *Recommendation:* this is **not** the old template lane. Skeletons, not finished scenes; illustration and copy stay free; 8–12 layout families so "≥3 families per lesson" is met by construction; kit entry requires passing the taste references, not just the gates; freshness comes from content, scene order, and the illustration — and that's exactly the freshness the research says works. The old lane's failures were implementation bugs (file collisions, blank slots) and a 5-template kit, not the idea of reuse.

### 2. Stop moving the factory while it runs — version it, pilot each version, then batch
**What.** Freeze a pipeline version: kit + tokens + gates + contracts + renderer pin. Changes to shared machinery land only *between* batches, as a new version, with a changelog, and every new version runs the 3-clean-re-run pilot the owner already set. Blocking-defect hotfixes are the only exception.
**Why.** Rules and lanes reversed within days (R6); a month produced 6 videos while the machinery was rebuilt (T1); 38% of one wave's checks couldn't fire (R1); a fence locked out its own author (R6). The research's #1 reliability point is same-input-same-output — impossible when the input is the pipeline itself.
**Goals.** Reliability, throughput.
**Size.** Small — a rule and a version stamp in run state.
**Tradeoff.** Slower to adopt a good idea. *Recommendation:* weekly versions during calibration, then per batch. Speed of improvement matters less than knowing what produced a given video.

### 3. Measure what we have, and put the rules upstream of the gate
**What.** Compute first-pass yield, rework rate, quarantine per lesson, and escape rate (defects found after a green gate) from the build logs and quarantine log on every status run. Rank the 344 failures by gate section and fix the top three *in the kit*, not in the builder's loop. Add the static, pre-TTS checks that are still missing (the pacing lesson: "learned after 258 clips instead of during a JSON edit"). Targets: ≥70% first-pass within one month of the kit, 90% after.
**Why.** No yield, rework, or cost metric exists anywhere; everything in the evidence log had to be hand-counted (evidence log, "absent"). You can't steer throughput blind.
**Goals.** Throughput, reliability.
**Size.** Small — the data is already on disk.

### 4. Make the environment boring
**What.** Bake the TTS/ffmpeg/CLI/secrets toolchain into the dev container; automatic cache pruning *before* the disk gate; a 15-minute no-progress watchdog on builder agents (kill, log, retry once, then stop and report); scheduled runs notify once on first block and then **stop re-firing**; a backend health check before any batch (one real cloud upload; a timed local render of the longest lesson) so the fallback is tested, not assumed.
**Why.** 5 days blocked, 56 hourly no-ops, queue 13→31 before anyone knew (T2); every fresh container re-pays the install tax (T7); 9 low-disk halts and an approved lesson rejected twice within days (T7); a builder idle 41 minutes unnoticed (T9); cloud upload broke and the local path hung (T8).
**Goals.** Reliability, throughput.
**Size.** Small–medium, mostly one-time.

### 5. Triage failures by kind, not by count
**What.** Classify every failure as *infrastructure* (timeout, upload, disk, 403, install) or *content* (a gate finding). Infrastructure → bounded retry with backoff, never a content rewrite. Content → back to the builder with the gate's own finding. Quarantine rows auto-clear on publish and link to their log. The stop-the-line rule fires on two same-class failures in a row — automatically.
**Why.** A render timeout was misdiagnosed as a pacing defect and burned a full rewrite; the stop-the-line rule "should have fired instead of retrying" (T8); 88 incidents in 13 days, rows never clear (R4); four agents misdiagnosed a concurrency limit as a credential fault (T5).
**Goals.** Reliability.
**Size.** Small.

### 6. Close the known gate blind spots, and bring memory-only knowledge into the repo
**What.** Four checks the record says are missing: "nothing graded" must fail loudly; 0.00% churn is a hard fail (empty render); still count must equal beat count before any ink/pace number is trusted; discover timeline names instead of assuming one. Port the owner-calibrated MP4 thresholds (frame ink, palette floors, silence, click detection) from the memory note into the post-render check. Make the close-out retro something the driver writes from machine artifacts, not a prose hook that can silently stop.
**Why.** Empty frames passed the full gate (R2); dots walked off their path past gate + visual review (R2); stale snapshots gave good numbers three runs running (R2); the retro hook "exists nowhere except the test" and a full day of gate work produced no retro (R8); thresholds "live only in a memory note" (evidence log, "absent").
**Goals.** Reliability, consistency.
**Size.** Small each; do them together.

### 7. One golden reference; taste on pilots and a sample, defects on every video
**What.** The two approved cuts and the two rejected cuts become a permanent fixture set — the yardstick for every kit scene and every pilot. The taste critic runs on pilots and a 1-in-5 sample, not every video. The blocking-defect review stays on every video (it caught real headless frames the gates passed).
**Why.** Gate-clean videos were rejected as boring/thin three times (C3); the per-video taste lane was meant to be pilot-only and never landed (T3); the rejected reference is gitignored and unrecoverable (evidence log, "absent").
**Goals.** Consistency, throughput.
**Size.** Small.
**Tradeoff.** A flat video can ship unreviewed. *Recommendation:* accept it — flatness is now mostly structural and the kit is calibrated against the references; keep post-publish sampling and fix the Wistia token scope so a replacement is a command, not a web-UI chore.

### 8. Approve the cheap thing
**What.** Owner approval of a *kit version's pilot* authorizes the batch for that version; per-lesson owner review only for flagged or sampled lessons. For first-of-kind (a new program, a new scene type), the owner sees the plan and a preview — never waits for a finished render.
**Why.** 30 approvals for 30 videos "guaranteed it would never finish in one night"; owner clearing latency measured at 5–8 days (T6); approval cycles are the #1 bottleneck in the outside research.
**Goals.** Throughput.
**Size.** Small — `approve BATCH` already exists.

### 9. Script stage: keep the lock, put a clock on owner-actionable items
**What.** Keep script-match and the cold-reader facts check (they work: C8). Owner-actionable script problems (duplicate lessons, missing narration) get a visible age in status and a nudge after 7 days.
**Why.** Two duplicate scripts sat unresolved for weeks across dozens of sessions (T6).
**Goals.** Throughput.
**Size.** Tiny.

### 10. One source per fact
**What.** Retire the README's `scenes.json` description and any other doc that describes a retired lane; keep the pipeline's operating facts in the machine files only; add a "stale doc" check to the linter where one is cheap.
**Why.** Three contradictory priority definitions at once; a stale skill copy loaded 176 lines behind; the README still describes the retired lane (R7).
**Goals.** Reliability.
**Size.** Tiny.

### After — how a lesson would move

```
  BUILT ONCE, VERSIONED  (kit v1 · tokens v1 · gates v1 · renderer pin)
  ┌──────────────────────────────────────────────────────────────────┐
  │ SCENE KIT   8–12 layout skeletons + motion presets, IN CODE      │
  │             each pre-verified green on every gate                │
  │             each judged ALIVE against the owner's approved refs  │
  │ TOKENS      palette · type · spacing · MOTION · components       │
  │ GOLDEN REF  2 approved + 2 rejected cuts as permanent fixtures   │
  │ SOUND       one voice · tick gate · quiet bed                    │
  └───────────────────────────────┬──────────────────────────────────┘
                                  ▼  every build draws from this, never reinvents it
  script (locked) ─▶ narration + word timings ─▶ PLAN: pick kit scenes, fill slots
                                                  static pace/ink/fit check BEFORE TTS
                                  ▼
                     ASSEMBLE — copy + illustration free, no new grammar
                                  ▼
                     MACHINE GATE — target ≥70% green first try, then 90%
                                  ▼
                     defect review: every video  ·  taste review: pilots + 1-in-5
                                  ▼
                     owner approves the PILOT of a kit version → batch flows
                                  ▼
                     render (health-checked backend, tested fallback) → verify → publish

  failure   → classified infra | content → right action → row auto-clears on publish
  rejection → fixture → gate → AND back into the kit (fix once, everywhere)
  metrics   → first-pass · rework · quarantine · escapes, computed every status run
  machinery → changes only between batches, as a new version, after a 3-run pilot
```

---

## Where the three goals pull against each other

| Tension | My recommendation |
|---|---|
| Kit (consistency, speed) vs. freshness | Kit of skeletons, not scenes; content and illustration free; entry to the kit requires passing the owner's taste references. Add scene types deliberately and rarely. |
| Machine gates (reliability) vs. visual ambition | Gates are floors and stay; ambition comes from the kit being calibrated against approved cuts, not from new numeric thresholds ("do not arm richness constants off n=1"). |
| Sampled taste review (throughput) vs. a flat video shipping | Sample after the pilot; keep the defect review per video; make replacement on Wistia a one-command fix. |
| Cloud render (throughput) vs. provider dependence | Cloud by default, behind a pre-batch health check, with a *timed* local fallback; cap lesson length per backend if local can't finish the long ones. |
| Frozen versions (reliability) vs. fast improvement | Weekly versions while calibrating, per batch afterwards; hotfix only for blocking defects. |

## Sequencing

- **Weeks 1–2 — stabilize and measure, no design risk:** changes 3, 4, 5, 6, 9, 10. Cheap, mechanical, each closes an incident class in the log.
- **Weeks 2–5 — build the kit:** change 1, calibrated against the references, ending in the 3-clean-run pilot; change 2's first frozen version is "kit v1."
- **From week 5 — the new rhythm:** changes 2, 7, 8 as the standing way batches run. Watch first-pass yield; if it isn't climbing toward 70% the kit is wrong, not the builders.

## What this proposal does not claim

- I could not put hours or dollars on any of this; the record doesn't hold them. The 0% first-pass figure partly reflects the gate being used as a development loop — it overstates waste but not the *location* of the rules.
- The "70% / 90%" targets are borrowed from manufacturing quality practice; video-specific benchmarks don't exist publicly.
- Nothing here says the current owner-approved references are the final look. They are the best calibration we have; the kit should be built to them and revised when the owner revises them.
