# SCLA Video Design System — brand token & asset store

The brand-owned token and asset store for SCLA lesson videos: the normative
numbers (`config/tokens.yml`), the vendored brand typeface, and the logo SVGs.
Every freeform build copies these in at claim time, and the render-qa gates
grade against them. The twelve scene templates, the demo reel and the
template-lane authoring docs retired to `_archive/` on 2026-08-05
(decisions/log.md) — this folder no longer contains renderable compositions.

**This is SCLA's illustrated-lesson pipeline territory.** Every SCLA
lesson/program video runs through the two-skill pipeline: **`/refine-scripts`**
(`inbox/` → `ready/`) and **`/render-lessons`** (ready script → freeform
hyperframe → pilot gate → MP4; **owns the build sequence and every command** —
this file does not restate them). `/produce-video` is the one-call dispatcher
over both. Start there; do not route SCLA lesson videos into generic
HyperFrames workflow skills.

## What's here

| Path | What it is |
|---|---|
| `config/tokens.yml` | **The normative numbers** — colors, type scale, min text sizes, spacing, pinned voice, program display names, retired names, chrome regions. `render-qa/src/tokens.py` LOADS this; the gates grade against it (the workspace's copied version). Changing a number here changes a gate's verdict. Never hand-copy one into code. |
| `assets/fonts/` | Self-hosted Proxima Nova woff2 (400/700/900, from SCLA's Adobe kit) + `metrics.json`, the measured font metrics `render-qa/src/textmetrics.py` reads |
| `assets/brand/` | SCLA logo SVGs (copied from `brand/assets/`) |
| `package.json` | Carries the pinned `hyperframes` version — the single pin `render-qa/src/check_layout.py` reads and every render runs at. Bump deliberately, never drop. |
| `docs/README.md` | Why this folder ignores the repo's project convention and what we gave up by doing so |
| `_archive/` | The retired template lane: twelve scene templates, demo reel, authoring-menu doc. Read-only provenance — never route here. |

## Narration voice — HeyGen starfish, live since 2026-07-22

**HeyGen "Oxana" (en-US) `442360a3e0894fbd85024ff64cc2b928` @ 1.0 speed** —
the pinned provider and voice (owner pick, 2026-07-22), declared in
`config/tokens.yml` → `voice:`.
Approved alternate: **Seema — Professional** `166aa8d7acd1495a839d34024ccb1505`.
Neither voice supports pause tags — pace narration with sentence structure.
Returns native per-word timestamps with the synthesis, so no separate
transcribe step runs on new builds (`decisions/log.md` 2026-07-22).
Fallback (kokoro, local, no credits) exists but is a manual escape hatch —
see `/render-lessons`; never audition or swap voices.

## Rules

- No FERPA/PII in any prompt or composition. Never fabricate SCLA content.
- Changing `tokens.yml` changes gate verdicts repo-wide — treat any edit as a
  gate edit: run `bash scripts/lint-refs.sh` and the render-qa suite after.
- Workspaces grade against their own COPY of `tokens.yml`; preflight's
  `composition_freshness` section fails a workspace whose copy has drifted
  from this spec.
