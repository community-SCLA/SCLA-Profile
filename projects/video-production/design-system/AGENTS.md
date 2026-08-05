# SCLA Video Design System — HyperFrames project

The brand-owned illustrated-video system for SCLA lesson videos. Twelve reusable
scene templates + design tokens + a pinned narration voice give every lesson a
brand-true starting point — but the templates are the **structural floor, not a
ceiling**: the frame must stay alive and *illustrate what's being said*
(`docs/design-contract.md` → "Every scene earns its seconds" + "Illustration over text").
Decision record: repo-root `decisions/log.md` (2026-07-07, revamped 2026-07-08).

## Skills — USE THESE FIRST

**Always invoke the relevant skill before writing or modifying compositions.**
Skills encode framework-specific patterns (e.g., `window.__timelines`
registration, `data-*` attribute semantics, shader-compatible CSS rules) that
are NOT in generic web docs. Skipping them produces broken compositions.

**This is SCLA's illustrated-lesson design-system project.** Every SCLA
lesson/program video runs through the two-skill pipeline: **`/refine-scripts`**
(`inbox/` → `ready/`) and **`/render-lessons`** (ready script → hyperframe
→ human preview gate → MP4; **owns the build sequence and every command** —
this file does not restate them). `/produce-video` is the one-call dispatcher
over both. Start there; do not route SCLA lesson videos into generic
HyperFrames workflow skills.

- **Design contract — read `docs/design-contract.md` first**: the house visual
  language, the anchor/timing syntax, the twelve scene templates, the icon set,
  the style packages, and the motion rotation. Read it while assembling any
  composition. It is a menu, not a rulebook — the gated rules are in
  `.claude/rules/video-production.md` and the numbers in `config/tokens.yml`.
- **Authoring & rendering mechanics:** `/hyperframes-core` (the composition
  contract), `/hyperframes-animation`, `/hyperframes-creative`, `/hyperframes-cli`,
  `/hyperframes-media`, `/hyperframes-registry`.
- **Deep QA:** `/adversarial-qa` — on-demand escalation only; see "QA model" below.

> **Tailwind v4 projects** (`hyperframes init --tailwind`): see `/hyperframes-core` → `references/tailwind.md`.

> **HyperFrames domain skills not available or need updating?** Run `npx skills add heygen-com/hyperframes`
> and restart the agent session so the new skills load.

## What's here

| Path | What it is |
|---|---|
| `config/tokens.yml` | **The normative numbers** — colors, type scale, min text sizes, spacing, pinned voice, program display names. `render-qa/src/tokens.py` LOADS this; the gates grade against it. Changing a number here changes a gate's verdict. Never hand-copy one into code. |
| `docs/design-contract.md` | **The authoring menu** — house visual language, the twelve templates, the icon set, style packages, motion recipes, and the `data-*` syntax you can't guess. Copied into every build scaffold; it is what the builder reads. It deliberately restates no gated rule — those live in `.claude/rules/video-production.md`, with the numbers in `tokens.yml`. |
| `docs/README.md` | Why this folder ignores the repo's project convention (HyperFrames dictates the layout) and what we gave up by doing so. |
| `compositions/scla-*.html` | The twelve scene templates (sub-compositions with variables, referenced via `data-composition-src`) — see table in `docs/design-contract.md` |
| `index.html` | Demo reel: all twelve templates with real approved-lesson content. Living style guide — render it after any template change. |
| `assets/brand/` | SCLA logo SVGs (copied from `brand/assets/`) |
| `assets/fonts/` | Self-hosted Proxima Nova woff2 (400/700/900, from SCLA's Adobe kit) |
| `meta.json` | Project metadata (id, name) |

## Commands (this folder only)

```bash
npm run dev      # preview server (long-running — background it)
npm run check    # lint + validate + inspect — ALWAYS run after edits
npm run render   # re-render the demo reel after template changes
npm run publish  # publish and get a shareable link
npx hyperframes lint --verbose  # include info-level findings
npx hyperframes lint --json     # machine-readable output for CI
npx hyperframes docs <topic>    # local reference docs — topics: data-attributes,
                                # gsap, compositions, rendering, examples, troubleshooting
```

> **`npm run dev` is a long-running server, not a one-shot command.** It blocks
> until stopped — always run it in the background, never in the foreground (it
> will time out and the server will die, breaking the browser preview).

After creating or editing any `.html` composition, **always** run `npm run check`
and fix all errors before considering the task complete. Review inspect warnings
before rendering.

Environment landmines (pkill bracket, /dev/shm size, CLI pin 0.7.79+/#2064,
HYPERFRAMES_PYTHON) are documented once, in `/render-lessons` Phase BUILD Step B0.

**Full documentation:** discover pages via the machine-readable index — do NOT
guess URLs: `https://hyperframes.heygen.com/llms.txt`

## Template & composition rules

- Templates are instantiated with variables (`data-composition-src` +
  `data-variable-values`), never forked. A recurring new need = a new
  `scla-*.html` template here, added to `docs/design-contract.md`'s table.
- Every template carries the three style packages (`theme`:
  `summit`/`horizon`/`cadence`) as CSS-only `data-theme` override blocks —
  timelines stay identical across packages (spec: `docs/design-contract.md` → "Style packages").
- Every timed element needs `data-start`, `data-duration`, `data-track-index`,
  and **`class="clip"`** — the framework uses the class for visibility control.
- One paused GSAP timeline per composition, registered on `window.__timelines`:
  ```js
  window.__timelines = window.__timelines || {};
  window.__timelines["composition-id"] = gsap.timeline({ paused: true });
  ```
- Deterministic only — no clocks (`Date.now()`), no `Math.random()`, no
  `repeat: -1`, no network fetches.
- `<video>`/`<audio>` live at the host root, never inside a sub-comp; videos
  use `muted` with a separate `<audio>` element for the audio track.
- Fonts: the `@font-face` block must be **inside** each sub-comp's `<template>`
  (the composited render discards everything outside it).
- No FERPA/PII in any prompt or composition. Never fabricate SCLA course content.

## Narration voice — HeyGen starfish, live since 2026-07-22

**HeyGen "Oxana" (en-US) `442360a3e0894fbd85024ff64cc2b928` @ 1.0 speed** —
`render-qa/src/synth_narration.py`'s default provider and voice (owner pick,
2026-07-22).
Approved alternate: **Seema — Professional** `166aa8d7acd1495a839d34024ccb1505`,
via `--voice`. Neither voice supports pause tags — pace narration with sentence
structure. Returns native per-word timestamps with the
synthesis, so the Whisper transcribe step no longer runs on new builds (see
`config/tokens.yml` → `voice:` + `docs/design-contract.md` → "Authoring contract", and
`decisions/log.md` 2026-07-22). Superseded 2026-07-07's Kokoro `af_heart`
decision once the 2026-07-21 HeyGen key rotation cleared the 403 that had
blocked this path.

**Manual fallback:** `synth_narration.py <ws> --provider kokoro` still works
(local engine, no credits/API key) — it has no
native word timestamps, so chain `npx hyperframes transcribe` after it (writes
`transcript.json`), same as the pre-2026-07-22 flow.

## QA model (2026-07-13)

Quality is enforced by the deterministic gates
(`../render-qa/{compile_timeline,preflight,verify_render}.py`), the builder's
frame review, and the one human checkpoint — the hyperframe preview gate
before any MP4 (the MP4-review gate was removed 2026-07-22; SHIP publishes in
one uninterrupted pass) — see `/render-lessons`. `/adversarial-qa` (four cold-context reviewer
lanes) is an on-demand escalation, not a standing per-render gauntlet.
