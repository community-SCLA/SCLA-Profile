#!/usr/bin/env bash
# Source-only acceptance gate for one isolated Codex Cloud lesson workspace.
# It restores ignored scaffold assets, runs the SCLA static gate, then runs the
# pinned HyperFrames browser/runtime check. It never calls TTS or renders.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
STEM="${1:-}"

if [[ -z "$STEM" || -n "${2:-}" ]]; then
  echo "usage: cloud-review-ready.sh <stem>" >&2
  exit 2
fi

BASE="$(python3 "$VP/render-qa/src/stem.py" base "$STEM" 2>/dev/null)" || {
  echo "FATAL: malformed stem: $STEM" >&2
  exit 2
}
[[ "$BASE" == "$STEM" ]] || {
  echo "FATAL: review gate requires an undated working stem: $BASE" >&2
  exit 2
}

WS="$VP/renders-hyperframes/$STEM"
SCAFFOLD="$VP/renders-hyperframes/_run/scaffold"
[[ -d "$WS" ]] || { echo "FATAL: workspace not found: $WS" >&2; exit 2; }
[[ -f "$WS/index.html" ]] || { echo "FATAL: index.html missing: $WS" >&2; exit 2; }
[[ -f "$WS/package.json" ]] || { echo "FATAL: package.json missing: $WS" >&2; exit 2; }
[[ -f "$WS/.pin" ]] || { echo "FATAL: HyperFrames .pin missing: $WS" >&2; exit 2; }

PINNED="$(tr -d '[:space:]' < "$WS/.pin")"
[[ "$PINNED" =~ ^hyperframes@[0-9]+\.[0-9]+\.[0-9]+([_-][A-Za-z0-9.-]+)?$ ]] || {
  echo "FATAL: invalid HyperFrames pin: $PINNED" >&2
  exit 2
}

# Fonts and brand assets are deliberately ignored in lesson workspaces to
# avoid duplicating binaries in every commit. Rehydrate them from the tracked
# scaffold before the browser check, including after a Cloud diff is applied.
for shared in fonts brand; do
  if [[ -d "$SCAFFOLD/assets/$shared" ]]; then
    mkdir -p "$WS/assets/$shared"
    cp -a "$SCAFFOLD/assets/$shared/." "$WS/assets/$shared/"
  fi
done

python3 "$VP/render-qa/src/preflight.py" "$WS" --static
(
  cd "$WS"
  # Invoke the validated pin directly. The authored package.json cannot turn
  # the acceptance gate into an echo/no-op script.
  npx --yes "$PINNED" check --json
)

echo "REVIEW_READY: PASS — $STEM"
