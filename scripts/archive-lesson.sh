#!/usr/bin/env bash
# archive-lesson.sh — retire a delivered lesson build workspace.
#
# Moves projects/video-production/renders-hyperframes/<stem>/ to
# renders-hyperframes/_archive/<stem>/ and prunes regenerable bulk
# (node_modules, caches, snapshots, renders, logs, source checkpoints), leaving a
# re-renderable source tree (HTML + design-contract.md + assets + configs).
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
PUBLISHED="$REPO_ROOT/projects/video-production/lesson-scripts/published.tsv"

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

# Safety: cleanup is allowed only after delivery is proved by either a filed
# local MP4 or an exact published.tsv row carrying a Wistia URL. The ledger path
# matters because local MP4s are disposable after a verified upload.
HAS_LOCAL=0
HAS_WISTIA=0
if find "$VIDEOS" -mindepth 2 -type f -name "${STEM}_*.mp4" -print -quit | grep -q .; then
  HAS_LOCAL=1
fi
if [[ -f "$PUBLISHED" ]] && awk -F '\t' -v stem="$STEM" '
  $1 == stem && $4 ~ /^https:\/\/[^[:space:]]+$/ { found=1 }
  END { exit(found ? 0 : 1) }
' "$PUBLISHED"; then
  HAS_WISTIA=1
fi
if [[ "$HAS_LOCAL" -eq 0 && "$HAS_WISTIA" -eq 0 ]]; then
  echo "No filed ${STEM}_*.mp4 or exact Wistia publication row — refusing cleanup." >&2
  exit 1
fi
# A ledger row may describe an older published cut while the same canonical
# workspace is being revised. With no newly filed MP4 as proof, consult live
# pipeline state and refuse every agent- or owner-queue stem.
if [[ "$HAS_LOCAL" -eq 0 && "$HAS_WISTIA" -eq 1 ]]; then
  STATUS_JSON="$(bash "$REPO_ROOT/projects/video-production/run.sh" status --json)" || {
    echo "Could not verify live pipeline state — refusing ledger-only cleanup." >&2
    exit 1
  }
  if printf '%s' "$STATUS_JSON" | python3 -c '
import json, sys
stem = sys.argv[1]
status = json.load(sys.stdin)
live = {
    item.get("stem")
    for queue in ("agent_queue", "owner_queue")
    for item in status.get(queue, [])
    if isinstance(item, dict)
}
raise SystemExit(0 if stem in live else 1)
' "$STEM"; then
    echo "$STEM is active in live pipeline state — refusing ledger-only cleanup." >&2
    exit 1
  fi
fi

# Retention policy: active and review-stage workspaces keep every immutable
# source checkpoint and review still. Delivery is the lifecycle boundary. Once
# the guard above proves delivery, the canonical authored source + current
# assets remain re-renderable, while historical checkpoints and review/render
# byproducts become regenerable bulk and are removed.
# qa/ + verify/ are the render-verification frame dumps — the biggest byproduct
# by far (qa/ alone ran ~70M in the 2026-07-24 cleanup) and fully regenerable by
# re-running verify_render.py; the MP4's QA packet already ships to renders-mp4/.
for junk in node_modules .thumbnails .waveform-cache .hyperframes renders output qa verify source-revisions; do
  rm -rf "$SRC/$junk"
done
# Review passes may preserve named generations such as snapshots-stale-* or
# snapshots-before-*. They share the same delivered-only retention boundary.
find "$SRC" -mindepth 1 -maxdepth 1 -type d -name 'snapshots*' -exec rm -rf -- {} +
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
