# SCLA Video Production — Agent Route

Human-facing overview/status files are not agent sources. Never enter `_archive/`.

## Public control

Use only `bash projects/video-production/run.sh …` from the repository root:

```text
status --json
produce --stem STEM
refine --stem STEM
batch --program PROGRAM | --all
approve PILOT
ship STEM [--publish]
resume
retry STEM --reason "what was fixed"
```

A stem is the default and only implicit scope. Program and whole-queue work
must be explicitly selected. The run state in `_run/run.json` owns selection,
pilot approval, retry limits, backend, concurrency, and the circuit breaker.

## Load only what the task needs

| Work | Agent source |
| --- | --- |
| Lifecycle and safety | `.claude/rules/video-production.md` |
| Build one composition | `contracts/builder.md` plus its one script and local `tokens.yml` |
| Combined visual review | `contracts/visual-review.md` |
| Script folder semantics | `contracts/script-state.md` |
| Deterministic QA | `render-qa/AGENTS.md` |
| Design-system contract | `design-system/CONTRACT.md` |

Do not load the full brand guide for a build. The builder consumes the copied
`tokens.yml`; the gates enforce those same tokens.

## Invariants

- Script lifecycle remains `inbox → ready → workspace → published`.
- Every new workspace starts through `scripts/build-claim.sh` and ends through
  `scripts/build-release.sh`.
- One human pilot approval is recorded once and survives sessions.
- Deterministic preflight, one combined pre-render visual review, post-render
  encode review, MP4 verification, and per-video publishing remain required.
- Production voice has one provider, voice ID, and speed; there is no fallback.
