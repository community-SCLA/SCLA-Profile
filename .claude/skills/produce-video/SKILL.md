---
name: produce-video
description: One-call dispatcher for the SCLA illustrated-lesson pipeline — THE entry point for "produce/make an SCLA lesson video". Runs /refine-scripts (raw scripts → refined/), then /render-lessons BUILD (refined/ → HyperFrames workspaces), and stops at the HYPERFRAME GATE — a human previews every hyperframe before any MP4 exists. The one later step is an explicit /render-lessons "ship <stem>" after the preview — SHIP then renders, verifies, files, and publishes to Wistia in one uninterrupted pass (no separate "publish" call, no second review; MP4 REVIEW gate removed 2026-07-22). Never route SCLA lesson videos into generic hyperframes workflow skills.
---

# produce-video — thin dispatcher

Every command lives in exactly one place; this file restates none of them.

1. **Refine** — run `/refine-scripts`: drain every raw `.txt` at
   `lesson-scripts/<program-slug>/` root into `refined/` (one cold subagent
   per script + qa-facts pass). Skip if the request names a script already in
   `refined/`.
2. **Build** — run `/render-lessons` Phase BUILD: drain `refined/` into
   HyperFrames workspaces (one cold subagent per video, ≤3 per session),
   deterministic gates green, **no MP4**.
3. **Stop at the HYPERFRAME GATE.** Hand the human the preview instructions
   per built video and end the turn. Never run `/render-lessons` SHIP from this
   dispatcher — SHIP happens only when the human, having watched the preview,
   says `ship <stem>`. Once granted, SHIP renders, verifies, files, and
   publishes to Wistia in one uninterrupted pass — there is no separate
   `publish` call (MP4 REVIEW gate removed 2026-07-22, `decisions/log.md`).

State is the folder (`refined/` → workspace at gate → `rendered/`); if the
request is only one piece ("just refine", "just build", "ship X"), call
`/refine-scripts` or `/render-lessons` directly.
