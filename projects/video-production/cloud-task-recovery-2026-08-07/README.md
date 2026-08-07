# Codex Cloud Recovery Archive — 2026-08-07

This folder is a local, unapplied backup of the Codex Cloud task queue before an account switch.

## Contents

- `manifest.json` — all 60 task records captured from Codex Cloud.
- `pages/` — the three original task-list responses.
- `diffs/<task-id>.patch` — the unified diff for each task that produced one.
- `export-summary.json` — the recovery result.

## Recovery result

- 59 tasks were listed as `ready`; 58 supplied a downloadable patch.
- One `ready` task, `task_e_6a754373106c83268fece1f77a7d9b30` ("Send career-transitions lesson scripts to Codex Cloud"), reports `no diff`; its metadata is preserved in `manifest.json`.
- One task ended in `error` with zero changed files; its metadata is preserved in `manifest.json`.

## Important

These patches have **not** been applied to this workspace. Several task diffs overlap with one another and with existing local changes. Inspect a patch before applying it, and apply only a selected task to a clean, dedicated recovery branch or worktree.
