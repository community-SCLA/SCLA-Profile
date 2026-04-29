#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/SCLA"

# ── Sync scla-profile ─────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"
git pull origin main
git add -A
git diff --cached --quiet || git commit -m "local sync $(date '+%Y-%m-%d %H:%M')"
git push origin main

# ── Update scla-workspace submodule pointer ───────────────────────────────────
cd "$WORKSPACE_DIR"
git add projects/scla-profile
git diff --cached --quiet || git commit -m "chore: update scla-profile submodule pointer $(date '+%Y-%m-%d %H:%M')"
git push origin main
