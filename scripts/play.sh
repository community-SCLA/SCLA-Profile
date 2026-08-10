#!/usr/bin/env bash
# Watch one built lesson in the lightweight HyperFrames player.
# Usage: bash scripts/play.sh <stem>
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$REPO/scripts/preview.sh" --player "$@"
