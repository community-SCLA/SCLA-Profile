#!/usr/bin/env bash
# build-claim.sh — the ONE way a build starts.
#
# Five things have to happen together when a build begins. Until 2026-08-04,
# the last three were prose in a skill file; until 2026-08-07, scaffold
# hydration and resume preservation still lived outside this boundary:
#
#   1. claim the workspace   — `mkdir` is the lock; atomic, succeeds exactly once
#   2. prepare its source    — hydrate NEW; checkpoint existing source on RESUME
#   3. arm the write fence   — the shared machinery goes read-only for the build
#   4. open the build journal— .build-log.tsv, so an interrupted run leaves a trace
#   5. regenerate the status — PIPELINE-STATUS.md notices that a build exists
#
# Prose got (1) done and nothing else. That is why PIPELINE-STATUS.md never
# regenerated on a build, and why two workspaces created on 2026-08-04 held a
# scaffold and no record whatsoever of what the builder that made them had done.
#
# Usage:
#   bash scripts/build-claim.sh <stem> <program-slug>            claim a NEW workspace
#   bash scripts/build-claim.sh <stem> <program-slug> --resume   take over an existing one
#
# --resume is the answer to STALLED. The workspace IS the lock, so "restart the
# build" against a folder that already exists names a command that exits
# immediately — and deleting the folder to get around that discards narration
# audio a rebuild would have to pay for again. Resuming re-arms the fence and
# journals the takeover instead.
set -uo pipefail

SCRIPT_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${VIDEO_REPO_ROOT:-$SCRIPT_REPO}"
VP="${VIDEO_VP_ROOT:-$REPO/projects/video-production}"
SCAFFOLD="$VP/renders-hyperframes/_run/scaffold"

STEM="${1:-}"
PROGRAM="${2:-}"
MODE="${3:-}"
if [ -z "$STEM" ] || [ -z "$PROGRAM" ]; then
  echo "usage: build-claim.sh <stem> <program-slug> [--resume]" >&2
  exit 2
fi
case "$MODE" in
  ""|--resume) ;;
  *) echo "FATAL: unknown mode '$MODE' (only --resume is accepted)" >&2; exit 2 ;;
esac

# A working artifact carries NO date — that is what makes its name a lock. A
# dated workspace name is the 2026-07-29 defect (a restamping rebuild produced
# two workspaces for one lesson); stem.py owns the rule, so ask it rather than
# hand-slicing a suffix here. preflight.py check 12 fails the same thing later;
# this refuses before the workspace exists at all.
BASE="$(python3 "$VP/render-qa/src/stem.py" base "$STEM" 2>/dev/null)" || {
  echo "FATAL: '$STEM' is not a stem stem.py can read" >&2; exit 2; }
if [ "$BASE" != "$STEM" ]; then
  echo "FATAL: '$STEM' carries a date. A working artifact never does — the name" >&2
  echo "       is the lock, and a name that moves cannot be one. Claim '$BASE'." >&2
  exit 2
fi

if [ ! -d "$VP/lesson-scripts/$PROGRAM" ]; then
  echo "FATAL: no such program: lesson-scripts/$PROGRAM" >&2; exit 2
fi

WS="$VP/renders-hyperframes/$STEM"

if [ "$MODE" = "--resume" ]; then
  if [ ! -d "$WS" ]; then
    echo "FATAL: nothing to resume — $WS does not exist." >&2
    echo "       Claim it instead: bash scripts/build-claim.sh $STEM $PROGRAM" >&2
    exit 2
  fi
  # Resume is local editing too, but a Cloud-authored stem stays externally
  # owned until its result is explicitly marked merged.  Then acquire the
  # per-stem lease before reading or checkpointing any source so two resume
  # workers cannot both proceed.
  python3 "$VP/render-qa/src/run_state.py" can-resume "$STEM" \
    --program "$PROGRAM" || exit $?
  bash "$REPO/scripts/build-session.sh" arm "$STEM" --resume || exit $?
  # A resume is allowed to edit the canonical workspace only after its current
  # authored/runtime source has a content-addressed recovery point.  The
  # checkpoint retains authored media and deduplicated voice bytes while
  # excluding QA, snapshots, and caches. It is idempotent, so retrying without
  # source changes reuses the same revision directory.
  python3 "$VP/render-qa/src/source_checkpoint.py" "$WS" >/dev/null || {
    echo "FATAL: could not checkpoint renders-hyperframes/$STEM; resume refused." >&2
    bash "$REPO/scripts/build-session.sh" release "$STEM" >/dev/null 2>&1 || true
    exit 1
  }
  echo "== resumed workspace renders-hyperframes/$STEM"
else
  # Acquire one per-stem owner first.  claim-local then checks explicit scope,
  # local backend, durable Cloud ownership, and mkdirs the canonical workspace
  # in the same run-state lock used by Cloud reservation.  Therefore a local
  # build and a Cloud dispatch cannot both win, even when started together.
  bash "$REPO/scripts/build-session.sh" arm "$STEM" || exit $?
  if ! python3 "$VP/render-qa/src/run_state.py" claim-local "$STEM" \
      --program "$PROGRAM" >/dev/null; then
    bash "$REPO/scripts/build-session.sh" release "$STEM" >/dev/null 2>&1 || true
    exit 1
  fi
  # Hydrate only AFTER mkdir wins the atomic claim.  Copying before the claim
  # lets two builders prepare the same stem; leaving this copy to a caller made
  # resume indistinguishable from a fresh scaffold and allowed authored source
  # to be overwritten.
  if [ ! -d "$SCAFFOLD" ] || ! cp -a "$SCAFFOLD/." "$WS/"; then
    echo "FATAL: could not hydrate the claimed workspace from _run/scaffold." >&2
    # This invocation created and leased WS. Remove only that exact failed
    # claim, then lower its lease, so a later healthy invocation can retry.
    rm -rf -- "$WS"
    bash "$REPO/scripts/build-session.sh" release "$STEM" >/dev/null 2>&1 || true
    exit 1
  fi
  # New control-plane workspaces opt into the compact v2 build contract.
  # Legacy workspaces remain resumable without forcing destructive migration.
  : > "$WS/.scla-control-v2"
  echo "== claimed workspace renders-hyperframes/$STEM"
fi

bash "$REPO/scripts/build-log.sh" "$STEM" \
  "$([ "$MODE" = "--resume" ] && echo resume || echo claim)" \
  "program=$PROGRAM"

bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true
echo "== PIPELINE-STATUS.md regenerated"
echo
echo "Journal each completed step:  bash scripts/build-log.sh $STEM <step> [detail]"
echo "Gate it:                      bash scripts/build-gate.sh $STEM"
echo "Close out:                    bash scripts/build-release.sh $STEM"
