---
name: produce-video
description: One-call dispatcher for the SCLA illustrated-lesson pipeline — THE entry point for "produce/make an SCLA lesson video". Runs /refine-scripts (raw scripts → refined/), then /render-lessons BUILD (refined/ → HyperFrames workspaces), and stops at the HYPERFRAME GATE — a human previews every hyperframe before any MP4 exists. The later steps are always separate explicit calls: /render-lessons "ship <stem>" after the preview, "publish <stem>" after the human watches the filed MP4. Never route SCLA lesson videos into generic hyperframes workflow skills.
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
   per built video and end the turn. Never run `/render-lessons` SHIP or
   PUBLISH from this dispatcher — SHIP happens only when the human, having
   watched the preview, says `ship <stem>`; PUBLISH only when they've watched
   the filed MP4 and say `publish <stem>`.

State is the folder (`refined/` → workspace at gate → MP4 at review →
`rendered/`); if the request is only one piece ("just refine", "just build",
"ship X", "publish X"), call `/refine-scripts` or `/render-lessons` directly.
