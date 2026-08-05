#!/usr/bin/env bash
# Run one command while holding one slot in a named machine-wide queue.
# flock releases the slot automatically if the command exits or the session dies.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE="${1:-}"
LIMIT="${2:-}"
shift 2 2>/dev/null || true
[[ "${1:-}" == "--" ]] && shift

[[ "$QUEUE" =~ ^[a-z0-9-]+$ ]] || {
  echo "usage: with-capacity.sh <queue> <positive-limit> -- <command...>" >&2
  exit 2
}
[[ "$LIMIT" =~ ^[1-9][0-9]*$ && "$#" -gt 0 ]] || {
  echo "usage: with-capacity.sh <queue> <positive-limit> -- <command...>" >&2
  exit 2
}
command -v flock >/dev/null 2>&1 || {
  echo "FATAL: with-capacity.sh requires flock" >&2
  exit 2
}

ROOT="${VIDEO_CAPACITY_ROOT:-$REPO/projects/video-production/renders-hyperframes/_run/capacity}"
POLL="${VIDEO_CAPACITY_POLL_SECONDS:-2}"
WAIT="${VIDEO_CAPACITY_WAIT_SECONDS:-3600}"
mkdir -p "$ROOT"
START="$(date +%s)"
ANNOUNCED=0

while true; do
  for ((slot = 1; slot <= LIMIT; slot++)); do
    LOCK="$ROOT/${QUEUE}-${slot}.lock"
    exec {LOCK_FD}>"$LOCK"
    if flock -n "$LOCK_FD"; then
      echo "== capacity: $QUEUE slot $slot/$LIMIT"
      "$@"
      exit $?
    fi
    exec {LOCK_FD}>&-
  done
  NOW="$(date +%s)"
  if (( NOW - START >= WAIT )); then
    echo "FATAL: timed out waiting ${WAIT}s for $QUEUE capacity ($LIMIT slot(s))" >&2
    exit 75
  fi
  if (( ANNOUNCED == 0 )); then
    echo "== capacity: waiting for $QUEUE ($LIMIT slot(s) busy)"
    ANNOUNCED=1
  fi
  sleep "$POLL"
done
