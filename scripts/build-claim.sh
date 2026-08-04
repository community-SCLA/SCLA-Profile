#!/usr/bin/env bash
# build-claim.sh — the ONE way a build starts.
#
# Four things have to happen together when a build begins, and until 2026-08-04
# three of them were prose in a skill file:
#
#   1. claim the workspace   — `mkdir` is the lock; atomic, succeeds exactly once
#   2. arm the write fence   — the shared machinery goes read-only for the build
#   3. open the build journal— .build-log.tsv, so an interrupted run leaves a trace
#   4. regenerate the status — PIPELINE-STATUS.md notices that a build exists
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

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"

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
  echo "== resumed workspace renders-hyperframes/$STEM"
else
  # THE LOCK. Never `mkdir -p`, never test-then-create: the whole point is that
  # exactly one of N concurrent build subagents wins the race.
  mkdir "$WS" 2>/dev/null || {
    echo "FATAL: renders-hyperframes/$STEM is already claimed by another build." >&2
    echo "       If that build is dead, resume it rather than deleting it:" >&2
    echo "         bash scripts/build-claim.sh $STEM $PROGRAM --resume" >&2
    echo "       Check what it finished: bash scripts/batch-status.sh" >&2
    exit 1
  }
  echo "== claimed workspace renders-hyperframes/$STEM"
fi

bash "$REPO/scripts/build-session.sh" arm "$STEM"

bash "$REPO/scripts/build-log.sh" "$STEM" \
  "$([ "$MODE" = "--resume" ] && echo resume || echo claim)" \
  "program=$PROGRAM"

bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true
echo "== PIPELINE-STATUS.md regenerated"
echo
echo "Journal each completed step:  bash scripts/build-log.sh $STEM <step> [detail]"
echo "Gate it:                      bash scripts/build-gate.sh $STEM"
echo "Close out:                    bash scripts/build-release.sh $STEM"
