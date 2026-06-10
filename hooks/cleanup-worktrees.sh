#!/usr/bin/env bash
# Remove .claude/worktrees/ entries whose branches are already merged into main.
# Runs as a Stop hook — fires at the end of every Claude session.

GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
WORKTREES_DIR="$GIT_ROOT/.claude/worktrees"

[[ -d "$WORKTREES_DIR" ]] || exit 0

# Branches reachable from main (i.e. already merged)
MERGED=$(git branch --merged main 2>/dev/null || git branch --merged master 2>/dev/null || echo "")

while IFS= read -r line; do
  wt_path=$(echo "$line" | awk '{print $1}')
  wt_branch=$(echo "$line" | sed -n 's/.*\[\(.*\)\].*/\1/p')

  [[ "$wt_path" == "$WORKTREES_DIR"/* ]] || continue
  [[ -n "$wt_branch" ]] || continue

  if echo "$MERGED" | grep -qF "$wt_branch"; then
    git worktree remove --force "$wt_path" 2>/dev/null || true
    git branch -d "$wt_branch" 2>/dev/null || true
  fi
done < <(git worktree list 2>/dev/null)
