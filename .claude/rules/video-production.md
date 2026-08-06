# Video Production Invariants

These rules apply to SCLA lesson-video work. They are the safety and lifecycle
contract, not an operating manual. Commands and machine gates own procedure.

## Scope and sources

- `projects/video-production/run.sh` is the only public control surface.
- A named stem is the default scope. A program or the whole queue requires an
  explicit `batch --program …` or `batch --all` command.
- Human-facing overview/status documents are not agent input. Obtain live state
  from `run.sh status --json`.
- Never load, route to, search, move, or modify `_archive/`.
- Never inspect another build for inspiration. A builder gets one script, one
  selected concept, the compact builder contract, and its local `tokens.yml`.

## Script and build lifecycle

- Preserve `inbox/ → ready/ → workspace → published/`. Do not skip or invent a
  lifecycle folder.
- A working workspace is the undated canonical stem. The dated name belongs to
  the delivered MP4.
- Start or resume only with `scripts/build-claim.sh`. End every claimed session
  with `scripts/build-release.sh`; the driver also releases its lease on exit.
- A lease is one file per stem. Never delete another stem's lease or workspace.
  TTL recovery is for hard crashes, not normal cleanup.
- Preserve usable narration, snapshots, and verified renders on resume. Never
  delete an active or stalled workspace merely to reacquire a lock.
- The workspace must not contain `make_*.py` or other bespoke infrastructure.
  Use tracked shared audio and timing commands; author the HTML directly.

## Content and design

- Narration and on-screen claims come only from the approved lesson script.
  Compression is allowed; new facts, counts, steps, quotations, or promises are
  not.
- No student records, FERPA data, or personal information may be sent to an AI
  or media provider.
- The program banner is derived from `tokens.yml programs:`. The lesson title is
  derived from the canonical stem. Neither is improvised.
- The workspace copy of `tokens.yml` owns palette, type, layout floors, timing,
  program names, and voice settings. Do not load the full visual-identity file.
- On-frame copy is markup, not hidden JavaScript strings. Required semantic
  roles and any narrow exceptions are declared where they occur.

## Audio and timing

- Production audio uses the configured provider, voice ID, and speed. There is
  no automatic fallback and no unpinned direct provider call.
- Invoke production TTS through `scripts/video-audio.sh`; it injects secrets,
  pins the request, and records the effective metadata.
- Generate timing only with `render-qa/src/plan_timing.py`. Never hand-tune a
  timestamp or create a workspace timing generator.
- `audio_meta.json` is the authority for synthesized clips. Clip IDs may use any
  prefix; all declared paths must exist.

## Quality and approval

- A deterministic gate must be green before visual review or rendering.
- The one pre-render reviewer reports two independent verdicts:
  `BLOCKING_DEFECT: PASS|FAIL` and `TASTE: ALIVE|FLAT`. A taste concern does not
  disguise a blocking defect, and a clean implementation does not imply taste.
- For an explicit program batch, author and gate every selected lesson before
  rendering any of them. The owner reviews the complete set of gate-clean
  HyperFrames workspaces, then records one batch-review approval in `run.json`.
  Reuse that approval across sessions; do not render or publish a selected lesson
  before the complete set is ready and approved.
- Retain sampled post-render encode review until run state records three
  consecutive clean cloud renders. Deterministic verification always remains.
- A failed external command writes its command, exit code, error class, attempt,
  full log path, and correct recovery action to `qa/failure.json`.
- Refuse a third attempt for the same stem and error class. Stop a batch after
  two consecutive distinct stems fail with the same error class. Only an
  explicit `run.sh retry … --reason …` may reopen work after the cause changes.
- Publish and clean up through the run driver. MP4 naming and Wistia ledger
  semantics remain unchanged.
