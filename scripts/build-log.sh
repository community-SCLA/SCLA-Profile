#!/usr/bin/env bash
# build-log.sh — append one row to a workspace's build journal.
#
#   renders-hyperframes/<stem>/.build-log.tsv
#   <timestamp>\t<step>\t<detail>
#
# APPEND-ONLY, and one row per COMPLETED step. This is evidence, not a status
# field: nothing ever rewrites a row, so it cannot lie the way a "status:
# building" line in a frontmatter block can — that line is only true until the
# process holding it dies, which is exactly when it gets read.
#
# batch-status.sh reads the LAST row and prints "left off after **voice**, 41
# min ago". Before this existed (2026-08-04), an interrupted build left no trace
# of what it had finished, and a resuming session faced a rebuild-or-resume call
# with no evidence either way — where rebuilding discards valid narration.
#
# Write a row only for work that is DONE. A row saying `voice` means the voice
# step finished; if the process dies mid-synthesis there is no row, which is the
# correct reading.
#
# Usage:  bash scripts/build-log.sh <stem> <step> [detail...]
#
# Conventional steps: claim · resume · design · plan · voice · timing · compile
#                     preflight · precheck · render · verify · publish · release
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_ROOT="${VIDEO_VP_ROOT:-$REPO/projects/video-production}/renders-hyperframes"

STEM="${1:-}"
STEP="${2:-}"
shift 2 2>/dev/null || true
DETAIL="${*:-}"

if [ -z "$STEM" ] || [ -z "$STEP" ]; then
  echo "usage: build-log.sh <stem> <step> [detail...]" >&2
  exit 2
fi

WS="$WS_ROOT/$STEM"
if [ ! -d "$WS" ]; then
  echo "build-log: no workspace at renders-hyperframes/$STEM — claim it first:" >&2
  echo "  bash scripts/build-claim.sh $STEM <program-slug>" >&2
  exit 2
fi

# Tabs are the field separator, so they can never appear inside a field.
STEP="${STEP//$'\t'/ }"
DETAIL="${DETAIL//$'\t'/ }"
DETAIL="${DETAIL//$'\n'/ }"

printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$STEP" "$DETAIL" \
  >> "$WS/.build-log.tsv"
echo "journal: $STEM — $STEP${DETAIL:+ ($DETAIL)}"
