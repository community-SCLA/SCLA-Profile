# SCLA Video Design System — HyperFrames project

The brand-owned illustrated-video system for SCLA lesson videos. Six reusable
scene templates + design tokens + a pinned narration voice, so every lesson video
is assembly, not invention. Decision record: `decisions/log.md` (2026-07-07).

**Read `frame.md` first** — it is the design spec (normative tokens + frame rules).
For HyperFrames authoring mechanics, start at the `/hyperframes` skill and let it
route; the composition contract lives in `/hyperframes-core`.

## What's here

| Path | What it is |
|---|---|
| `frame.md` | Design spec — SCLA tokens adapted to the video frame. Brand truth stays in `brand/`. |
| `compositions/scla-*.html` | The six scene templates (sub-compositions with variables) — see table in `frame.md` |
| `index.html` | Demo reel: all six templates with real approved-lesson content. Living style guide. |
| `assets/brand/` | SCLA logo SVGs (copied from `brand/assets/`) |
| `assets/fonts/` | Self-hosted Proxima Nova woff2 (400/700/900, from SCLA's Adobe kit) |
| `voice-auditions/` | Kokoro voice samples generated from approved script lines — listen and re-decide anytime |

## Commands

```bash
npm run dev      # preview server (long-running — background it)
npm run check    # lint + validate + inspect — ALWAYS run after edits
npx hyperframes snapshot --at <t1,t2,...>   # frame stills for eyeball review
npm run render   # MP4 — only after the human QA gate
```

## Building a lesson video (the scale recipe)

1. **Approved script first** — the existing gate is unchanged: narration `.txt`
   approved and saved to `../videos/<program-slug>/` before anything renders.
2. **New project per video:** `HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <script-stem> --example=blank --non-interactive`
   inside `projects/video-production/lessons/`, then copy in `frame.md`,
   `compositions/`, `assets/` from this project.
3. **Narration** (voice is pinned in `frame.md` → `voice:`):
   ```bash
   npx hyperframes tts "$(cat ../../videos/<program>/<stem>.txt)" \
     --provider kokoro --voice af_heart --speed 0.95 -o assets/voice/narration.wav
   npx hyperframes transcribe assets/voice/narration.wav --model small.en   # word timings
   ```
4. **Assemble** `index.html`: one slot per beat using the scene templates with
   `data-variable-values` (copy the pattern from this project's demo reel), sized
   to the narration's word timings; `<audio>` for narration sits at the host root.
   Bespoke scenes are welcome — follow `frame.md`, don't fork the templates.
5. **Check + eyeball:** `npm run check`, then `snapshot` at each scene midpoint.
6. **Human QA gate** — `../templates/qa-checklist.md` (illustrated section). Never skip.
7. **Render + file:** `npm run render`, rename the MP4 to the script's stem, move
   it next to its script in `../videos/<program-slug>/`.

Edits later cost one scene, not a full re-render: change the sub-comp or its
variables, re-check, re-render.

## Narration voice — decided 2026-07-07

**Kokoro `af_heart` @ 0.95 speed** (local engine, no credits, no API key).
Chosen against `af_nova`, `af_sky`, `am_adam` — samples in `voice-auditions/`.
Warm American female read; keeps voice continuity with the HeyGen avatar
presenter ("Ann") used by `../heygen-pipeline/`.

**Upgrade path:** the HeyGen API key currently returns 403 on every endpoint
(no API permission on the space — also blocks `../heygen-pipeline/`). Once fixed
(`npx hyperframes auth login`, or a key with API access), audition HeyGen
starfish voices (`node .claude/skills/hyperframes-media/scripts/heygen-tts.mjs --list`)
and update `frame.md` → `voice:` in one place. HeyGen TTS also returns native
word timestamps, which removes the transcribe step above.

## Rules

- Templates are instantiated with variables, never forked. A recurring new need
  = a new `scla-*.html` template here, added to `frame.md`'s table.
- Every timed element: `data-start`, `data-duration`, `data-track-index`,
  `class="clip"`. One paused GSAP timeline per composition on `window.__timelines`.
- Deterministic only — no clocks, no `Math.random`, no `repeat: -1`, no network fetches.
- `<video>`/`<audio>` live at the host root, never inside a sub-comp template.
- Fonts: the `@font-face` block must be **inside** each sub-comp's `<template>`.
- No FERPA/PII in any prompt or composition. Never fabricate SCLA course content.
