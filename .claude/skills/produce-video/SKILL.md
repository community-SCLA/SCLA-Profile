---
name: produce-video
description: Select one SCLA lesson video and run it to the existing pilot gate.
argument-hint: "<stem>"
disable-model-invocation: true
---

# Produce One SCLA Video

This is a thin command map. It never scans or drains the queue.

1. Require one explicit canonical stem.
2. Run `bash projects/video-production/run.sh produce --stem STEM`.
3. Use `/render-lessons BUILD STEM` for the selected item only.
4. Stop at the existing pilot gate unless `run.json` already records approval.

For a program or whole queue, the user must explicitly choose
`run.sh batch --program PROGRAM` or `run.sh batch --all`.

Human-facing status documents are not agent input. Read live state through
`run.sh status --json`.
