---
name: produce-video
description: One-call dispatcher for the SCLA illustrated-lesson pipeline — THE entry point for "produce/make an SCLA lesson video". Runs /refine-scripts (inbox/ → ready/), then hands off to /render-lessons. One video → BUILD, stopping for the human preview. A queue → Phase AUTO-BATCH, which builds one pilot, stops for a single human approval, then drains the whole queue in priority order to Wistia unattended. Never route SCLA lesson videos into generic hyperframes workflow skills.
---

# produce-video — thin dispatcher

Every command lives in exactly one place; this file restates none of them.

1. **Refine** — run `/refine-scripts`: drain every raw `.txt` in
   `lesson-scripts/<program-slug>/inbox/` into `ready/` (one cold subagent
   per script + qa-facts pass). Skip if the request names a script already in
   `ready/`.
2. **Build** — hand off to `/render-lessons`, picking the phase by queue size:
   - **One video** → Phase BUILD: one cold subagent, deterministic gates
     green, **no MP4**.
   - **A queue (more than one)** → Phase AUTO-BATCH: no batch cap, priority
     order, one video published and committed before the next starts.
3. **Stop at the human gate — exactly once.** Hand over the preview and end the
   turn. BUILD stops per video; AUTO-BATCH stops after its **pilot**, and the
   human's approval there authorizes the rest of the batch (changed
   2026-07-28 — the old per-video gate made a large queue undrainable;
   `decisions/log.md`). Never self-approve. Once granted, rendering →
   verify → file → Wistia runs in one uninterrupted pass; there is no separate
   `publish` call (MP4 REVIEW gate removed 2026-07-22).

State is the folder, and the folder name is the stage name (`inbox/` →
`ready/` → workspace at the gate → `published/` + a `published.tsv` row); if the request is only one piece ("just
refine", "just build", "ship X"), call `/refine-scripts` or `/render-lessons`
directly. Resuming an interrupted batch: `bash scripts/batch-status.sh`.
