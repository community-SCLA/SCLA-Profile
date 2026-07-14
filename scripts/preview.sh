#!/usr/bin/env bash
# Preview a built HyperFrames lesson workspace in HeyGen Studio, on a fixed,
# auto-forwarded port. Removes the "cd into the workspace and run it by hand
# every time" friction — run it from the repo root with just the stem.
#
# Usage:  scripts/preview.sh <stem>
# In a Codespace, port 3002 auto-forwards and opens the browser (see
# .devcontainer/devcontainer.json → forwardPorts / portsAttributes).
set -euo pipefail

STEM="${1:-}"
if [ -z "$STEM" ]; then
  echo "usage: scripts/preview.sh <stem>" >&2
  exit 2
fi

WS="projects/video-production/renders-hyperframes/$STEM"
if [ ! -d "$WS" ]; then
  echo "No workspace at $WS — run /render-lessons BUILD for '$STEM' first." >&2
  exit 1
fi

PORT="${HF_PREVIEW_PORT:-3002}"

# A stale preview server contaminates renders; clear a prior preview only.
# Bracketed pattern so we never kill this shell (see render-qa/snag-log.md).
pkill -f "hyperframes[ ]preview" 2>/dev/null || true

echo "HyperFrames Studio → http://localhost:$PORT/#project/$STEM"
echo "(port $PORT auto-forwards in the Codespace; Ctrl-C to stop)"
cd "$WS"
exec npm run dev -- --port "$PORT"
