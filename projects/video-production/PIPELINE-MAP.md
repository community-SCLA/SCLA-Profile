# SCLA Lesson-Video Pipeline — Live Map (human reference)

**What this is:** the one visual map of how a lesson video goes from a raw script
to a published Wistia video — the skills, the folders, the two human checkpoints.
**Who it's for:** humans. Agents don't route here; it's not loaded into any session.
**Keep it live:** whenever the pipeline flow, a skill, a folder, or a gate changes,
update this file in the same change. Last updated **2026-07-14**.

> Deep history (build sessions, run reports, the original proposal) lives in
> `render-qa/BUILD-LOG.md` — that's a dated journal and some of its diagrams are
> pre-v3. **This file is the current-state map.**

---

## The three skills (one entry point, two workhorses)

```
  /produce-video          thin dispatcher — "make an SCLA lesson video end to end"
      │                   runs /refine-scripts, then /render-lessons BUILD, and
      │                   STOPS at the hyperframe gate. ~20 lines, restates nothing.
      ├──────────────►  /refine-scripts     raw script  → refined/
      └──────────────►  /render-lessons     refined/    → hyperframe → MP4 → Wistia
                                             (3 phases: BUILD · SHIP · PUBLISH)
```

You can call either workhorse directly. `ship <stem>` and `publish <stem>` are
always explicit calls into `/render-lessons`.

---

## The flow (state = the folder, not the session)

A script's **location is its status.** Every phase is a cold, resumable
queue-drain: you can review in one session and run the next phase in a brand-new
session days later — no context carries over, nothing bloats.

```
 ┌─ RAW ────────────────────────────────────────────────────────────────────────┐
 │  lesson-scripts/<program>/*.txt          raw capture, dropped in at the root   │
 └───────────────────────────────┬───────────────────────────────────────────────┘
                                 │   /refine-scripts   (one cold subagent per script)
                                 │   • strip capture noise, keep "what you built" callbacks
                                 │   • mandatory qa-facts pass (no fabricated SCLA content)
                                 │   • a script with an open question is SKIPPED → asks you
                                 ▼
 ┌─ REFINED ─────────────────────────────────────────────────────────────────────┐
 │  lesson-scripts/<program>/refined/*.txt                                         │
 │  ░ ASYNC REVIEW BUFFER — you may read / edit / delete anything here, any time. ░│
 │  ░ Nothing blocks or waits on you. This replaces the old blocking script gate. ░│
 └───────────────────────────────┬───────────────────────────────────────────────┘
                                 │   /render-lessons  BUILD   (≤3 per session, one cold
                                 │   subagent each; strong model for illustration-heavy)
                                 │   • init workspace + copy design-system (frame.md, 9 templates)
                                 │   • assemble index.html: per-scene data-narration (verbatim
                                 │     script spans) + CUE PHRASES — never a typed timing number
                                 │   • synth_narration.py: one kokoro clip PER SCENE, concatenated
                                 │     with real boundary silence (sample-exact manifest; replaced
                                 │     the single-take + inserted-silence flow 2026-07-14)
                                 │   • transcribe (whisper, cues only) → compile_timeline.py owns
                                 │     every number (boundaries from the manifest)
                                 │   • preflight.py (incl. script-vs-transcript diff) + npm run check
                                 │   • NO RENDER in this phase
                                 ▼
 ┌─ BUILT ───────────────────────────────────────────────────────────────────────┐
 │  renders-hyperframes/<stem>/             the HyperFrames workspace, gate-clean  │
 │                                                                                 │
 │   ██ HUMAN CHECKPOINT 1 — HYPERFRAME GATE ███████████████████████████████████   │
 │   You preview the hyperframe in the browser BEFORE any MP4 exists.              │
 │   Preview:  scripts/preview.sh <stem>    (Studio on :3002 — auto-forwards & opens)│
 │   Approve:  say  ship <stem>       (covers only that stem)                      │
 │   No automation ever turns a script into an MP4 in one shot.                    │
 └───────────────────────────────┬───────────────────────────────────────────────┘
                                 │   /render-lessons  SHIP   ( trigger: "ship <stem>" )
                                 │   • npm run render  (~7 min)
                                 │   • verify_render.py — container truth + presence v2 + qa/frames
                                 │   • builder self-review of qa/frames/
                                 │   • file the MP4 + QA packet
                                 ▼
 ┌─ SHIPPED ─────────────────────────────────────────────────────────────────────┐
 │  renders-mp4/<program>/hyperframes/m<#>_<title>_<render-date>.mp4  (local, gitignored)│
 │                                                                                 │
 │   ██ HUMAN CHECKPOINT 2 — MP4 REVIEW █████████████████████████████████████████  │
 │   You WATCH the filed MP4 before it can reach Wistia.                           │
 │   Approve:  say  publish <stem>                                                 │
 │   Reject → fix → re-render → re-verify (not a rebuild from scratch).            │
 └───────────────────────────────┬───────────────────────────────────────────────┘
                                 │   /render-lessons  PUBLISH   ( trigger: "publish <stem>" )
                                 │   • upload MP4 → Wistia (via scripts/with-secrets.sh once the
                                 │     Infisical token is wired; manual web-UI upload until then)
                                 │   • record Wistia URL in refinement-log.md
                                 │   • git mv script  refined/ → rendered/
                                 │   • archive-lesson.sh <stem>  (refuses if MP4 not filed)
                                 ▼
 ┌─ PUBLISHED ───────────────────────────────────────────────────────────────────┐
 │  lesson-scripts/<program>/rendered/*.txt     books closed; video lives on Wistia │
 └───────────────────────────────────────────────────────────────────────────────┘

 Legend:  ██ = a blocking HUMAN checkpoint (the only two)   ░ = async, non-blocking
          everything between the checkpoints is machine work behind deterministic gates
```

---

## Why the phases are separate sessions (the thing that saves context)

Because **state is the folder**, you are never forced to keep a session open:

- **Session A** — run BUILD, then close it. Review the hyperframes whenever you like.
- **Session B (fresh)** — `ship <stem>`; it reads the workspace off disk and renders.
- **Session C (fresh)** — after watching the MP4, `publish <stem>`.

None of B or C inherits A's context. Reviewing hyperframes can take a while; that
review no longer costs you a bloated render session.

---

## The two things that guard quality without a blocking gate

- **Deterministic gates** (`render-qa/`): `compile_timeline.py` (owns all timing),
  `preflight.py` (pre-render, incl. script-vs-transcript diff), `verify_render.py`
  (post-render container + presence checks). Green exit codes, not vibes.
- **Facts, once, at the script stage:** `qa-facts` runs inside `/refine-scripts`.
  Facts are a property of the script, so re-renders never re-check them.
- On-demand only: `/adversarial-qa` (four cold reviewer lanes) — run it when a cut
  resists diagnosis or you say "try to break it," not on every render.

---

## The self-improvement loop (ask-model, 2026-07-14)

Every build/render session ends by writing an entry to `render-qa/snag-log.md`:

- **Anything the agent can fix, it fixes in-session** — never rolled forward.
- **An item that rolls over is owner-actionable by definition** (needs your
  decision, a credential, or access). At close-out the session **asks you
  directly** about each one — you never have to open the log.

---

## Design + hosting facts

- **Look & feel:** `design-system/frame.md` (the design contract), nine `scla-*`
  scene templates, three style packages (**summit → horizon → cadence**, rotated
  by the program's *started-build* count).
- **Voice:** kokoro TTS, pinned in `frame.md`.
- **Hosting:** Wistia (`sclc.wistia.com`). The upload API token lives in
  **Infisical** and is injected at PUBLISH via `scripts/with-secrets.sh` — never
  in `.env` or the repo. IDs + status: root `endpoints.md`.

The illustrated (HyperFrames) path above is the default for lesson videos. The
avatar path (`avatar-pipeline/`, HeyGen) is a separate tool for
translations / talking-head / true human-presence moments. It reads from the
program's `refined/avatar/` queue (route = location: root/`refined/` →
illustrated, `avatar/`/`refined/avatar/` → HeyGen), assembles one talking-head
MP4 per lesson, and files it to `renders-mp4/<program>/avatar/` under the same
`m<#>_<title>_<render-date>` naming — then the same MP4 REVIEW → Wistia steps.
Hybrid (avatar + on-screen overlays) is a future build: `hybrid-avatar-overlay-brief.md`.
