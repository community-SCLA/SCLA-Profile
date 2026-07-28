---
description: Always-true SCLA video-pipeline constraints — load for any work in the factory
paths: projects/video-production/**
---

# Video production — standing constraints

Each rule names its enforcement mechanism, or is honestly labelled a **convention**.

- **Never fabricate SCLA course content.** Work only from provided outlines and source material. *(Mechanisms: mandatory qa-facts pass at `/refine-scripts`; script-vs-transcript diff gate in `render-qa/preflight.py`; the brand re-materialize safeguard in `.devcontainer/devcontainer.json` exists because a cold subagent once fabricated `brand/voice-and-tone.md`.)*
- **PILOT GATE — one human approval per batch, not per video.** A batch run builds ONE pilot video, stops, and a human previews it. Only on explicit approval do the remaining videos run build → render → verify → publish unattended. A batch may never start without a passing pilot, and a failing pilot stops the run. *(Convention at the pilot itself. Superseded the per-video HYPERFRAME GATE 2026-07-28, `decisions/log.md` — the per-video human eye is replaced by three mechanized guards, below.)*
- **The guards that replace the per-video human eye** — every video, no exceptions: `render-qa/preflight.py` exit 0 before render; `render-qa/verify_render.py` exit 0 after (stream durations vs `#root data-duration` ±0.15s, exact 1920×1080, 3 frames/scene); `render-qa/check_presence.py` blank/stagnation detection; and a sampled vision review of `qa/frames/`. Any one failing **quarantines that video** — built, unpublished, logged — and the batch continues. *(Mechanism: `scripts/batch-ship.sh`, which fails soft per video and never publishes a video that failed a guard.)*
- **SHIP is one uninterrupted pass** — render, verify, file to `renders-mp4/<program-slug>/`, upload to Wistia. No second human review before publish (gate removed 2026-07-22, `decisions/log.md`). *(Convention.)*
- **A published video is recorded before the next one starts.** The full stem + Wistia URL land in `lesson-scripts/published.tsv` (the machine resume key) and the human-facing `refinement-log.md` row, committed in the same pass — a commit failure quarantines the video with its URL and keeps the MP4. A stem is done if and only if it has a `published.tsv` row; anything in `rendered/` without one is flagged **STRANDED** by the status tool, so an interrupted run never silently strands work. Publish runs only against `qa/VERIFIED` (the sha-256 marker `verify_render.py` writes) and refuses stems already published. *(Mechanisms: `scripts/batch-ship.sh` guards, 2026-07-28; read the remaining queue with `scripts/batch-status.sh`.)*
- **Never archive automatically.** Retiring a workspace to `renders-hyperframes/_archive/` is a human-only call. A shipped video's workspace is pruned in place (`scripts/archive-lesson.sh <stem> --in-place`) and stays put, editable. *(Convention, stated in `projects/video-production/CLAUDE.md`.)*
- **Close the books after a render.** Any session that ran a HyperFrames render prepends a snag-log retro entry per `render-qa/snag-log.md` header rules before ending. *(Mechanism: PostToolUse hook in `.claude/settings.json`.)*
- **No FERPA/PII in any prompt sent to an AI tool.** *(Convention.)*
- **Brand facts come from `brand/visual-identity.md` and `brand/voice-and-tone.md`.** Never restate hex values in pipeline docs — they drift. *(Mechanism: `lint-refs.sh` check 6 flags stray legacy hex.)*
- **The narration voice is pinned** (Oxana, ID in `design-system/frame.md`). Do not audition, swap, or reference retired voices. *(Convention.)*
