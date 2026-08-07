# SCLA Video Production — Agent Route

Human-facing overview/status files are not agent sources. Never enter `_archive/`.

## Public control

Use only `bash projects/video-production/run.sh …` from the repository root:

```text
status --json
produce --stem STEM
refine --stem STEM
batch --program PROGRAM [--cloud] | --all [--cloud]
delegate --stem STEM
dispatch --stem STEM
dispatch-merged --stem STEM [--task-ref REF]
drain
limits
cloud-limit 2 | 4
visual-review STEM --blocking-defect PASS|FAIL --taste ALIVE|FLAT --recommendation PROCEED|REVISE [--finding TEXT]
encode-review STEM --backend cloud|local --verdict PASS|FAIL [--finding TEXT]
approve STEM|BATCH
ship STEM [--publish]
resume [--json]
migrate-state
retry STEM --reason "what was fixed"
```

A stem is the default and only implicit scope. Program and whole-queue work
must be explicitly selected. The run state in `_run/run.json` owns selection
identity, revision-bound owner approvals, external-task reservations, retry
limits, backend, stage-specific capacity, and the circuit breaker. Live phase
and condition come from current workspace evidence; selection items never carry
a persisted stage label.

## Load only what the task needs

| Work | Agent source |
| --- | --- |
| Lifecycle and safety | `.claude/rules/video-production.md` |
| Build one composition | `contracts/builder.md` plus its one script and local `tokens.yml` |
| Isolated cloud source authoring | `contracts/cloud-author.md` plus its one script and local `tokens.yml` |
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
- Every mechanically and visually clean lesson is returned for rolling review
  immediately. Approval is recorded per lesson and exact source revision and
  survives sessions; siblings may remain in progress.
- A green deterministic gate advances first to combined visual review. Only a
  same-revision `PASS` + `ALIVE` + `PROCEED` receipt may reach owner review.
- Resume checkpoints the current authored source before editing and never
  re-copies the scaffold. A live owner is refused until the 30-minute stalled
  takeover age. Cloud `reserved`, `submitted`, or `unknown` ownership blocks
  resume until `dispatch-merged` records a local handoff.
- Deterministic preflight, one combined pre-render visual review, post-render
  encode review, MP4 verification, and per-video publishing remain required.
- Production voice has one provider, voice ID, and speed; there is no fallback.
