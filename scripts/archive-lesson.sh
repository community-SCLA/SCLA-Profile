#!/usr/bin/env bash
# archive-lesson.sh — retire a delivered lesson build workspace.
#
# Moves projects/video-production/renders-hyperframes/<stem>/ to
# renders-hyperframes/_archive/<stem>/ and prunes regenerable bulk
# (node_modules, caches, snapshots, renders, logs), leaving a
# re-renderable source tree (HTML + frame.md + assets + configs).
#
# Usage:  bash scripts/archive-lesson.sh <script-stem> [--in-place]
#
#   (no flag)    prune, then MOVE the workspace to _archive/<stem>/.
#                Retiring a build is a HUMAN-ONLY call, never a pipeline step
#                (projects/video-production/CLAUDE.md) — pipelines pass --in-place.
#   --in-place   prune the same regenerable bulk but LEAVE the workspace where
#                it is, so it stays routable and editable. This is what
#                batch-ship.sh calls after a successful publish: the source tree
#                (index.html, compositions/, assets/ incl. synthesized
#                narration, scenes.json) survives, so revisiting a shipped
#                lesson is `npm install` away and costs no new HeyGen credits.
#
# Run AFTER the final MP4 is verified and filed in renders-mp4/<program-slug>/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LESSONS="$REPO_ROOT/projects/video-production/renders-hyperframes"
VIDEOS="$REPO_ROOT/projects/video-production/renders-mp4"

STEM=""; IN_PLACE=0
for arg in "$@"; do
  case "$arg" in
    --in-place) IN_PLACE=1 ;;
    -*) echo "Unknown flag: $arg" >&2; exit 2 ;;
    *)  STEM="$arg" ;;
  esac
done

if [[ -z "$STEM" ]]; then
  echo "Usage: bash scripts/archive-lesson.sh <script-stem> [--in-place]" >&2
  echo "Active workspaces:" >&2
  find "$LESSONS" -mindepth 1 -maxdepth 1 -type d ! -name '_archive' ! -name '_run' -printf '  %f\n' >&2
  exit 1
fi

SRC="$LESSONS/$STEM"
DEST="$LESSONS/_archive/$STEM"

[[ -d "$SRC" ]] || { echo "No active workspace at $SRC" >&2; exit 1; }
if [[ "$IN_PLACE" -eq 0 && -e "$DEST" ]]; then
  echo "$DEST already exists — refusing to overwrite an archived build" >&2; exit 1
fi

# Safety: the deliverable must be filed before its workspace is retired.
# The filed MP4 reuses the script stem but swaps in the render date, so match by
# the stem-minus-date prefix rather than the exact script stem (which carries the
# script's own date). The recursive find matches inside the program's
# hyperframes/ (or avatar/) subfolder too.
BASE="${STEM%_*}"
if ! find "$VIDEOS" -mindepth 2 -name "${BASE}_*.mp4" | grep -q .; then
  echo "No ${BASE}_*.mp4 found under renders-mp4/<program-slug>/{hyperframes,avatar}/ — file the final render first." >&2
  exit 1
fi

# Prune regenerable bulk (all rebuildable via npm install / hyperframes).
# qa/ + verify/ are the render-verification frame dumps — the biggest byproduct
# by far (qa/ alone ran ~70M in the 2026-07-24 cleanup) and fully regenerable by
# re-running verify_render.py; the MP4's QA packet already ships to renders-mp4/.
for junk in node_modules .thumbnails .waveform-cache .hyperframes snapshots renders output qa verify; do
  rm -rf "$SRC/$junk"
done
find "$SRC" -name '*.log' -delete   # includes assets/voice/tts.log, transcribe.log

if [[ "$IN_PLACE" -eq 1 ]]; then
  echo "Pruned in place: renders-hyperframes/$STEM ($(du -sh "$SRC" | cut -f1)) — workspace kept, still editable."
  echo "To revisit later: cd into it, npm install, edit, npm run render."
  exit 0
fi

mkdir -p "$LESSONS/_archive"
mv "$SRC" "$DEST"

echo "Archived: renders-hyperframes/_archive/$STEM ($(du -sh "$DEST" | cut -f1))"
echo "To re-render later: cd into it, npm install, npm run render."
