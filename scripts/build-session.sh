#!/usr/bin/env bash
# build-session.sh — arm / disarm / report the write-fence sentinel.
#
# The sentinel is one file:
#   projects/video-production/renders-hyperframes/.build-in-progress
#
# Its presence is the ONLY thing that turns scripts/write-fence.sh on. Absent,
# the fence exits 0 for everything and an owner session is completely
# unrestricted; present, the shared machinery (design-system/, _run/,
# render-qa/src/, scripts/, .claude/) is read-only for the duration.
#
# The discriminator has to be "is a build running", not "which session type is
# this", because the owner and the build subagents they dispatch share one
# process — see decisions/log.md 2026-08-04 "The write fence".
#
# Normally called by scripts/build-claim.sh (arm) and scripts/build-release.sh
# (disarm), not by hand. Both are ordinary script invocations, which the fence
# allows even while armed: the hook grades the tool call, and `bash
# scripts/build-release.sh <stem>` writes nothing itself.
#
# Usage:
#   bash scripts/build-session.sh arm <stem>
#   bash scripts/build-session.sh disarm
#   bash scripts/build-session.sh status      # exit 0 armed, 1 disarmed
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SENTINEL="$REPO/projects/video-production/renders-hyperframes/.build-in-progress"
TTL="${VIDEO_BUILD_SESSION_TTL:-21600}"
case "$TTL" in ''|*[!0-9]*) TTL=21600 ;; esac

age_seconds() {
  local mtime now
  now="$(date +%s)"
  mtime="$(stat -c %Y "$SENTINEL" 2>/dev/null || stat -f %m "$SENTINEL" 2>/dev/null || printf '%s' "$now")"
  printf '%s' "$((now - mtime))"
}

case "${1:-status}" in
  arm)
    STEM="${2:-}"
    if [ -z "$STEM" ]; then
      echo "build-session: arm needs the stem it is arming for — the sentinel" \
           "records WHICH build holds the fence, so a stale one can be" \
           "diagnosed instead of guessed at." >&2
      exit 2
    fi
    mkdir -p "$(dirname "$SENTINEL")"
    # Append, never truncate: two builds can legitimately overlap (builds run up
    # to 3-wide), and the fence must stay armed until the LAST one releases.
    printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$STEM" >> "$SENTINEL"
    echo "write fence ARMED for $STEM (expires after ${TTL}s if never released)"
    ;;

  disarm)
    STEM="${2:-}"
    if [ ! -f "$SENTINEL" ]; then
      echo "write fence already down"
      exit 0
    fi
    if [ -n "$STEM" ]; then
      REMAINING="$(grep -v -F "	$STEM" "$SENTINEL" 2>/dev/null)"
      if [ -n "$REMAINING" ]; then
        printf '%s\n' "$REMAINING" > "$SENTINEL"
        echo "write fence stays ARMED — $(printf '%s\n' "$REMAINING" | wc -l | tr -d ' ') other build(s) still hold it"
        exit 0
      fi
    fi
    rm -f "$SENTINEL"
    echo "write fence DISARMED"
    ;;

  status)
    if [ ! -f "$SENTINEL" ]; then
      echo "write fence: DOWN (no build in flight — the machinery is writable)"
      exit 1
    fi
    AGE="$(age_seconds)"
    if [ "$TTL" -gt 0 ] && [ "$AGE" -ge "$TTL" ]; then
      echo "write fence: EXPIRED (${AGE}s old, TTL ${TTL}s) — treated as DOWN."
      echo "A run died without releasing it. Clear it: bash scripts/build-session.sh disarm"
      exit 1
    fi
    echo "write fence: ARMED (${AGE}s), held by:"
    sed 's/^/  /' "$SENTINEL"
    exit 0
    ;;

  *)
    echo "usage: build-session.sh {arm <stem>|disarm [stem]|status}" >&2
    exit 2
    ;;
esac
