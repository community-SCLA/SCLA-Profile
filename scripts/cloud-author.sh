#!/usr/bin/env bash
# Create one source-only workspace inside an isolated Codex Cloud task.
# This deliberately does not touch the live run, leases, status, TTS or renders.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
STEM="${1:-}"
PROGRAM="${2:-}"

if [[ -z "$STEM" || -z "$PROGRAM" ]]; then
  echo "usage: cloud-author.sh <stem> <program-slug>" >&2
  exit 2
fi

BASE="$(python3 "$VP/render-qa/src/stem.py" base "$STEM" 2>/dev/null)" || {
  echo "FATAL: malformed stem: $STEM" >&2
  exit 2
}
[[ "$BASE" == "$STEM" ]] || {
  echo "FATAL: cloud authoring requires an undated working stem: $BASE" >&2
  exit 2
}

SCRIPT="$VP/lesson-scripts/$PROGRAM/ready/$STEM.txt"
SCAFFOLD="$VP/renders-hyperframes/_run/scaffold"
WS="$VP/renders-hyperframes/$STEM"
[[ -f "$SCRIPT" ]] || { echo "FATAL: ready script not found: $SCRIPT" >&2; exit 2; }
[[ -d "$SCAFFOLD" ]] || { echo "FATAL: tracked scaffold not found: $SCAFFOLD" >&2; exit 2; }

# mkdir is the task-local duplicate-stem guard. The live coordinator claims the
# merged workspace later with build-claim.sh --resume.
mkdir "$WS" 2>/dev/null || {
  echo "FATAL: workspace already exists: $WS" >&2
  exit 1
}
cp -a "$SCAFFOLD/." "$WS/"
: > "$WS/.scla-control-v2"

echo "cloud authoring workspace: $WS"
echo "refined narration: $SCRIPT"
echo "next: create CONCEPT.md, concept.json, design.md, audio_request.json and index.html"
echo "stop after static preflight; do not call TTS, render, publish or shared run-state scripts"
