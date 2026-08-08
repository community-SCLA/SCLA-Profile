# Codex Cloud Recovery Archive — 2026-08-07

This folder is a local, unapplied backup of the Codex Cloud task queue before an account switch.

## Recovery decision — 2026-08-08

The current local lesson workspaces are canonical and are farther along than
these archived alternatives. **Do not apply or merge these patches into the
live lesson folders.** Existing workspaces must be resumed in place through
`projects/video-production/run.sh`; they must not be rebuilt from this archive.

Keep this folder as recovery evidence until the current lessons are published
and the recovery commit is backed up remotely. The archive is only about 4 MB,
so deleting it does not materially reduce Codespace usage.

Permanently exclude
`diffs/task_e_6a754358b5a0832698e1cdcd420a89f5.patch`: it contains only an
obsolete generated `PIPELINE-STATUS.md` snapshot. The live status source is
`bash projects/video-production/run.sh status --json`.

`download-failures.txt` is a historical first-pass retry log, not a list of
missing work. Thirty-four listed tasks have nonempty patches; the remaining
task is the documented no-diff task.

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
