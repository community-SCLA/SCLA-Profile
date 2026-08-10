# Video workspace retention

The workspace lifecycle, rather than file age, decides what can be removed.

## Before publication

Keep all `source-revisions/` checkpoints and all `snapshots*` review evidence.
An active, stalled, rejected, or owner-review lesson may need those files for
safe recovery or comparison. No time-based cleanup applies before delivery.

## After publication

A newly filed local MP4 proves delivery during publishing. For later cleanup,
an exact `lesson-scripts/published.tsv` row with a Wistia URL is sufficient only
when live pipeline state also confirms the lesson is absent from both the agent
and owner queues. This prevents an older publication record from pruning a new
revision in progress. `scripts/archive-lesson.sh --in-place` then retains the
canonical authored source and current assets, but removes regenerable bulk:

- immutable `source-revisions/` history and its blob store;
- every `snapshots*` review generation;
- render frames, QA/verification dumps, caches, logs, and dependencies.

This leaves a lesson editable and re-renderable without retaining every
intermediate attempt. Local MP4s may be deleted after their Wistia publication
is recorded; the publication ledger remains sufficient for workspace cleanup.

## Enforcement

Publishing invokes `scripts/archive-lesson.sh STEM --in-place`. The script
refuses cleanup unless delivery evidence exists and ledger-only cleanup is not
active, so unfinished work never ages into deletion eligibility.
