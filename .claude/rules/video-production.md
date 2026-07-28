---
description: Always-true SCLA video-pipeline constraints — load for any work in the factory
paths: projects/video-production/**
---

# Video production — standing constraints

Each rule names its enforcement mechanism, or is honestly labelled a **convention**.

- **Never fabricate SCLA course content.** Work only from provided outlines and source material. *(Mechanisms: mandatory qa-facts pass at `/refine-scripts`; script-vs-transcript diff gate in `render-qa/preflight.py`; the brand re-materialize safeguard in `.devcontainer/devcontainer.json` exists because a cold subagent once fabricated `brand/voice-and-tone.md`.)*
- **HYPERFRAME GATE is the one human checkpoint.** A human previews every built hyperframe before any MP4 exists. Hyperframe → MP4 runs only on an explicit `ship <stem>` from a human. Never self-approve the gate; no automation takes a script to an MP4 in one shot. *(Convention at the gate itself; the deterministic gates — `render-qa/preflight.py` pre-render, `render-qa/verify_render.py` post-render — are the mechanized part.)*
- **SHIP is one uninterrupted pass** — render, verify, file to `renders-mp4/<program-slug>/`, upload to Wistia. No second human review before publish (gate removed 2026-07-22, `decisions/log.md`). *(Convention.)*
- **Close the books after a render.** Any session that ran a HyperFrames render prepends a snag-log retro entry per `render-qa/snag-log.md` header rules before ending. *(Mechanism: PostToolUse hook in `.claude/settings.json`.)*
- **No FERPA/PII in any prompt sent to an AI tool.** *(Convention.)*
- **Brand facts come from `brand/visual-identity.md` and `brand/voice-and-tone.md`.** Never restate hex values in pipeline docs — they drift. *(Mechanism: `lint-refs.sh` check 6 flags stray legacy hex.)*
- **The narration voice is pinned** (Oxana, ID in `design-system/frame.md`). Do not audition, swap, or reference retired voices. *(Convention.)*
