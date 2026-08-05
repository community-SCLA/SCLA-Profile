#!/usr/bin/env bash
# build-session.sh — arm / disarm / report the write-fence sentinel.
#
# The sentinel is one directory containing one lease per stem:
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
# A resume refreshes the same stem file; it never appends a duplicate holder.
# Usage:
#   bash scripts/build-session.sh arm <stem>
#   bash scripts/build-session.sh release <stem>
#   bash scripts/build-session.sh status      # exit 0 armed, 1 disarmed
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SENTINEL="$REPO/projects/video-production/renders-hyperframes/.build-in-progress"
TTL="${VIDEO_BUILD_SESSION_TTL:-21600}"
case "$TTL" in ''|*[!0-9]*) TTL=21600 ;; esac

age_seconds() {
  local lease="$1" mtime now
  now="$(date +%s)"
  mtime="$(stat -c %Y "$lease" 2>/dev/null || stat -f %m "$lease" 2>/dev/null || printf '%s' "$now")"
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
    # Migrate the retired append-only file shape without discarding any live
    # holder. This branch is normally exercised only once after the upgrade.
    if [ -f "$SENTINEL" ]; then
      OLD="$SENTINEL.old.$$"
      mv "$SENTINEL" "$OLD"
      mkdir -p "$SENTINEL"
      while IFS=$'\t' read -r when old_stem; do
        [ -n "$old_stem" ] || continue
        printf '%s\t%s\n' "$when" "$old_stem" > "$SENTINEL/$old_stem"
      done < "$OLD"
      rm -f "$OLD"
    else
      mkdir -p "$SENTINEL"
    fi
    # One file per stem makes arm idempotent and parallel builds independent.
    printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$STEM" > "$SENTINEL/$STEM"
    echo "write fence ARMED for $STEM (expires after ${TTL}s if never released)"
    ;;

  disarm|release)
    STEM="${2:-}"
    if [ -z "$STEM" ]; then
      echo "build-session: release needs one stem; refusing to remove other leases" >&2
      exit 2
    fi
    if [ ! -e "$SENTINEL" ]; then
      echo "write fence already down"
      exit 0
    fi
    if [ ! -d "$SENTINEL" ]; then
      echo "build-session: legacy lease file requires an arm migration before release" >&2
      exit 2
    fi
    rm -f "$SENTINEL/$STEM"
    REMAINING=0
    for lease in "$SENTINEL"/*; do
      [ -f "$lease" ] && REMAINING=$((REMAINING + 1))
    done
    if [ "$REMAINING" -gt 0 ]; then
      echo "write fence stays ARMED — $REMAINING other build(s) still hold it"
      exit 0
    fi
    rmdir "$SENTINEL" 2>/dev/null || true
    echo "write fence DISARMED"
    ;;

  status)
    if [ ! -e "$SENTINEL" ]; then
      echo "write fence: DOWN (no build in flight — the machinery is writable)"
      exit 1
    fi
    if [ -f "$SENTINEL" ]; then
      AGE="$(age_seconds "$SENTINEL")"
      [ "$TTL" -le 0 ] || [ "$AGE" -lt "$TTL" ] || {
        echo "write fence: EXPIRED legacy sentinel (${AGE}s old) — treated as DOWN."
        exit 1
      }
      echo "write fence: ARMED by legacy sentinel"
      sed 's/^/  /' "$SENTINEL"
      exit 0
    fi
    ACTIVE=0
    for lease in "$SENTINEL"/*; do
      [ -f "$lease" ] || continue
      AGE="$(age_seconds "$lease")"
      if [ "$TTL" -gt 0 ] && [ "$AGE" -ge "$TTL" ]; then
        continue
      fi
      [ "$ACTIVE" -gt 0 ] || echo "write fence: ARMED, held by:"
      sed 's/^/  /' "$lease"
      ACTIVE=$((ACTIVE + 1))
    done
    if [ "$ACTIVE" -eq 0 ]; then
      echo "write fence: DOWN (all leases expired; TTL ${TTL}s)"
      exit 1
    fi
    exit 0
    ;;

  *)
    echo "usage: build-session.sh {arm <stem>|release <stem>|status}" >&2
    exit 2
    ;;
esac
