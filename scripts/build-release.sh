#!/usr/bin/env bash
# build-release.sh — close a build out.
#
# The mirror of build-claim.sh, and the other half of the reason the write fence
# can be armed automatically: something has to lower it. Three things:
#
#   1. final journal row     — the last thing this build actually finished
#   2. disarm the fence      — for THIS stem only; overlapping builds keep theirs
#   3. regenerate the status — PIPELINE-STATUS.md sees the build end
#
# The workspace is NOT deleted and NOT archived. Retiring one is a human-only
# call (`archive-lesson.sh`), and a released build usually still has a human
# gate ahead of it.
#
# Releasing is safe to run twice: a second call finds no sentinel row of its own
# and says so rather than failing.
#
# Usage:  bash scripts/build-release.sh <stem> [note...]
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="${VIDEO_VP_ROOT:-$REPO/projects/video-production}"

STEM="${1:-}"
shift 2>/dev/null || true
NOTE="${*:-}"
if [ -z "$STEM" ]; then
  echo "usage: build-release.sh <stem> [note...]" >&2
  exit 2
fi

WS="$VP/renders-hyperframes/$STEM"
if [ -d "$WS" ]; then
  bash "$REPO/scripts/build-log.sh" "$STEM" release "${NOTE:-build session ended}"
else
  echo "build-release: no workspace at renders-hyperframes/$STEM — releasing the" \
       "fence anyway, since a missing workspace is exactly the case where a" \
       "sentinel would otherwise be left armed."
fi

bash "$REPO/scripts/build-session.sh" disarm "$STEM"
bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true
echo "== PIPELINE-STATUS.md regenerated"
