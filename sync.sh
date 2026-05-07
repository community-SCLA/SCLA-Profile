#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/SCLA"
SYNC_BRANCH="${SYNC_BRANCH:-main}"

# ── Sync scla-profile ─────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"
current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" != "$SYNC_BRANCH" ]]; then
  echo "❌ sync.sh expects branch '$SYNC_BRANCH' but you're on '$current_branch'." >&2
  echo "   Switch branches or override with SYNC_BRANCH=<branch> ./sync.sh" >&2
  exit 1
fi

git pull origin "$SYNC_BRANCH"
git add -A
git diff --cached --quiet || git commit -m "local sync $(date '+%Y-%m-%d %H:%M')"
git push origin "$SYNC_BRANCH"

# ── Update scla-workspace submodule pointer ───────────────────────────────────
if [[ -d "$WORKSPACE_DIR/.git" ]]; then
  cd "$WORKSPACE_DIR"
  git add projects/scla-profile
  git diff --cached --quiet || git commit -m "chore: update scla-profile submodule pointer $(date '+%Y-%m-%d %H:%M')"
  git push origin "$SYNC_BRANCH"
else
  echo "ℹ️  Skipping workspace submodule update — $WORKSPACE_DIR not found."
fi
