# SCLA Video Design System — HyperFrames project

The brand-owned illustrated-video system for SCLA lesson videos. Nine reusable
scene templates + design tokens + a pinned narration voice give every lesson a
brand-true starting point — but the templates are the **structural floor, not a
ceiling**: the frame must stay alive and *illustrate what's being said*
(`frame.md` → "Every scene earns its seconds" + "Illustration over text").
Decision record: repo-root `decisions/log.md` (2026-07-07, revamped 2026-07-08).

**Read `frame.md` first** — it is the design spec (normative tokens + frame
rules + the anchor/timing contract + templates + style packages + motion
rotation). **The build sequence and every command are owned by `/render-lessons`**
(`/produce-video` is the one-call dispatcher over it and `/refine-scripts`) —
this file does not restate them. For HyperFrames authoring mechanics, the
composition contract lives in `/hyperframes-core`.

## What's here

| Path | What it is |
|---|---|
| `frame.md` | Design spec — SCLA tokens adapted to the video frame. Brand truth stays in `brand/`. |
| `compositions/scla-*.html` | The nine scene templates (sub-compositions with variables) — see table in `frame.md` |
| `index.html` | Demo reel: all nine templates with real approved-lesson content. Living style guide — render it after any template change. |
| `assets/brand/` | SCLA logo SVGs (copied from `brand/assets/`) |
| `assets/fonts/` | Self-hosted Proxima Nova woff2 (400/700/900, from SCLA's Adobe kit) |
| `voice-auditions/` | Kokoro voice samples generated from approved script lines — listen and re-decide anytime |

## Commands (this folder only)

```bash
npm run dev      # preview server (long-running — background it)
npm run check    # lint + validate + inspect — ALWAYS run after edits
npm run render   # re-render the demo reel after template changes
```

Environment landmines (pkill bracket, /dev/shm size, CLI pin 0.7.45+/#2064,
HYPERFRAMES_PYTHON) are documented once, in `/render-lessons` Phase BUILD Step B0.

## Template rules

- Templates are instantiated with variables (`data-composition-src` +
  `data-variable-values`), never forked. A recurring new need = a new
  `scla-*.html` template here, added to `frame.md`'s table.
- Every template carries the three style packages (`theme`:
  `summit`/`horizon`/`cadence`) as CSS-only `data-theme` override blocks —
  timelines stay identical across packages (spec: `frame.md` → "Style packages").
- Every timed element: `data-start`, `data-duration`, `data-track-index`,
  `class="clip"`. One paused GSAP timeline per composition on `window.__timelines`.
- Deterministic only — no clocks, no `Math.random`, no `repeat: -1`, no network
  fetches. `<video>`/`<audio>` live at the host root, never inside a sub-comp.
- Fonts: the `@font-face` block must be **inside** each sub-comp's `<template>`
  (the composited render discards everything outside it).
- No FERPA/PII in any prompt or composition. Never fabricate SCLA course content.

## Narration voice — decided 2026-07-07

**Kokoro `af_heart` @ 0.95 speed** (local engine, no credits, no API key).
Chosen against `af_nova`, `af_sky`, `am_adam` — samples in `voice-auditions/`.
Warm American female read; keeps voice continuity with the HeyGen avatar
presenter ("Ann") used by `../avatar-pipeline/`.

**Upgrade path:** the HeyGen API key currently returns 403 on every endpoint
(no API permission on the space — also blocks `../avatar-pipeline/`). Once fixed
(`npx hyperframes auth login`, or a key with API access), audition HeyGen
starfish voices (`node .claude/skills/hyperframes-media/scripts/heygen-tts.mjs --list`)
and update `frame.md` → `voice:` in one place. HeyGen TTS also returns native
word timestamps, which removes the transcribe step.

## QA model (2026-07-13)

Quality is enforced by the deterministic gates
(`../render-qa/{compile_timeline,preflight,verify_render}.py`), the builder's
frame review, and the two human checkpoints — the hyperframe preview gate
before any MP4, and MP4 review before Wistia — see `/render-lessons`. `/adversarial-qa` (four cold-context reviewer
lanes) is an on-demand escalation, not a standing per-render gauntlet.
