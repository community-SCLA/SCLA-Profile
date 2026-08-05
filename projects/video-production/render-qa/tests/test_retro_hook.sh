#!/usr/bin/env bash
# The driver owns one concise close-out record; command hooks must stay silent.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
SETTINGS="$REPO/.claude/settings.json"
STATE="$REPO/projects/video-production/render-qa/src/run_state.py"

jq -e '((.hooks.PostToolUse // []) | length) == 0' "$SETTINGS" >/dev/null
grep -q 'def closeout' "$STATE"
grep -q 'last_closeout' "$STATE"

echo "3 passed, 0 failed"
