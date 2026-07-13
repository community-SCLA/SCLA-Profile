# HyperFrames Composition Project

## Skills — USE THESE FIRST

**Always invoke the relevant skill before writing or modifying compositions.** Skills encode framework-specific patterns (e.g., `window.__timelines` registration, `data-*` attribute semantics, shader-compatible CSS rules) that are NOT in generic web docs. Skipping them produces broken compositions.

**This is SCLA's illustrated-lesson design-system project.** Every SCLA
lesson/program video is produced by **`/produce-video`** — the one-call pipeline
that owns the build sequence and every command (script → build → render → verify →
file). Start there; do not route SCLA lesson videos into generic HyperFrames
workflow skills.

- **Design contract:** `frame.md` in this folder — normative tokens, frame/animacy
  rules, the anchor/timing contract, the nine scene templates, and the style
  packages. Read it while assembling any composition.
- **Authoring & rendering mechanics:** `/hyperframes-core` (the composition
  contract), `/hyperframes-animation`, `/hyperframes-creative`, `/hyperframes-cli`,
  `/hyperframes-media`, `/hyperframes-registry`.
- **Deep QA:** `/adversarial-qa` — on-demand adversarial audit (four cold-context
  reviewer lanes), an escalation only; the deterministic gates + human QA gate in
  `/produce-video` are the standing quality bar.

> **Tailwind v4 projects** (`hyperframes init --tailwind`): see `/hyperframes-core` → `references/tailwind.md`.

> **HyperFrames domain skills not available or need updating?** Run `npx skills add heygen-com/hyperframes`
> and restart the agent session so the new skills load.

## Commands

```bash
npm run dev          # start the preview server (long-running — keep it alive in background)
npm run check        # lint + validate + inspect
npm run render       # render to MP4
npm run publish      # publish and get a shareable link
npx hyperframes lint --verbose  # include info-level findings
npx hyperframes lint --json     # machine-readable output for CI
npx hyperframes docs <topic> # reference docs in terminal
```

> **`npm run dev` is a long-running server, not a one-shot command.** It blocks until stopped.
> In Claude Code, always run it with `run_in_background: true`. Never run it as a foreground
> command — it will time out and the server will die, breaking the browser preview.

## Documentation

**For quick reference**, use the local CLI docs command (no network required):

```bash
npx hyperframes docs <topic>
```

Topics: `data-attributes`, `gsap`, `compositions`, `rendering`, `examples`, `troubleshooting`

**For full documentation**, discover pages via the machine-readable index — do NOT guess URLs:

```
https://hyperframes.heygen.com/llms.txt
```

## Project Structure

- `index.html` — main composition (root timeline)
- `compositions/` — sub-compositions referenced via `data-composition-src`
- `meta.json` — project metadata (id, name)
- `transcript.json` — whisper word-level transcript (if generated)

## Linting — ALWAYS RUN AFTER CHANGES

After creating or editing any `.html` composition, **always** run the full check before considering the task complete:

```bash
npm run check
```

Fix all errors before presenting the result. Inspect warnings should be reviewed before rendering.

## Key Rules

1. Every timed element needs `data-start`, `data-duration`, and `data-track-index`
2. Elements with timing **MUST** have `class="clip"` — the framework uses this for visibility control
3. Timelines must be paused and registered on `window.__timelines`:
   ```js
   window.__timelines = window.__timelines || {};
   window.__timelines["composition-id"] = gsap.timeline({ paused: true });
   ```
4. Videos use `muted` with a separate `<audio>` element for the audio track
5. Sub-compositions use `data-composition-src="compositions/file.html"` to reference other HTML files
6. Only deterministic logic — no `Date.now()`, no `Math.random()`, no network fetches
