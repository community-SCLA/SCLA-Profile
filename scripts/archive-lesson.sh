#!/usr/bin/env bash
# archive-lesson.sh — retire a delivered lesson build workspace.
#
# Moves projects/video-production/lessons/<stem>/ to lessons/_archive/<stem>/
# and prunes regenerable bulk (node_modules, caches, snapshots, renders, logs),
# leaving a re-renderable source tree (HTML + frame.md + assets + configs).
#
# Usage:  bash scripts/archive-lesson.sh <script-stem>
# Run AFTER the final MP4 is verified and filed in videos/<program-slug>/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LESSONS="$REPO_ROOT/projects/video-production/lessons"
VIDEOS="$REPO_ROOT/projects/video-production/videos"

STEM="${1:-}"
if [[ -z "$STEM" ]]; then
  echo "Usage: bash scripts/archive-lesson.sh <script-stem>" >&2
  echo "Active workspaces:" >&2
  find "$LESSONS" -mindepth 1 -maxdepth 1 -type d ! -name '_archive' -printf '  %f\n' >&2
  exit 1
fi

SRC="$LESSONS/$STEM"
DEST="$LESSONS/_archive/$STEM"

[[ -d "$SRC" ]] || { echo "No active workspace at $SRC" >&2; exit 1; }
[[ -e "$DEST" ]] && { echo "$DEST already exists — refusing to overwrite an archived build" >&2; exit 1; }

# Safety: the deliverable must be filed before its workspace is retired.
if ! find "$VIDEOS" -mindepth 2 -name "$STEM.mp4" | grep -q .; then
  echo "No $STEM.mp4 found under videos/<program-slug>/ — file the final render first." >&2
  exit 1
fi

# Prune regenerable bulk (all rebuildable via npm install / hyperframes).
for junk in node_modules .thumbnails .waveform-cache .hyperframes snapshots renders output; do
  rm -rf "$SRC/$junk"
done
find "$SRC" -maxdepth 1 -name '*.log' -delete

mkdir -p "$LESSONS/_archive"
mv "$SRC" "$DEST"

echo "Archived: lessons/_archive/$STEM ($(du -sh "$DEST" | cut -f1))"
echo "To re-render later: cd into it, npm install, npm run render."
