#!/usr/bin/env bash
# Submit one selected, untouched READY lesson to the configured Codex Cloud environment.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN="$REPO/projects/video-production/run.sh"
STEM="${1:-}"
[[ -n "$STEM" && -z "${2:-}" ]] || { echo "usage: cloud-dispatch.sh <stem>" >&2; exit 2; }

ENV_ID="${CODEX_CLOUD_ENV_ID:-$(python3 - "$REPO/config/endpoints.json" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1], encoding="utf-8")).get("codex_cloud") or []
print(next((str(x.get("id")) for x in rows if x.get("type") == "environment" and x.get("id")), ""))
PY
)}"
[[ -n "$ENV_ID" ]] || { echo "FATAL: Codex Cloud environment ID is not configured" >&2; exit 2; }

BRANCH="${CODEX_CLOUD_BRANCH:-$(git -C "$REPO" branch --show-current)}"
[[ -n "$BRANCH" ]] || { echo "FATAL: dispatch requires a named git branch" >&2; exit 2; }
if [[ "${CODEX_CLOUD_ALLOW_DIRTY:-0}" != "1" ]]; then
  [[ -z "$(git -C "$REPO" status --porcelain)" ]] || {
    echo "FATAL: commit and push local changes before Cloud dispatch" >&2; exit 2;
  }
  git -C "$REPO" rev-parse --verify '@{upstream}' >/dev/null 2>&1 || {
    echo "FATAL: branch $BRANCH has no upstream; push it before Cloud dispatch" >&2; exit 2;
  }
  [[ "$(git -C "$REPO" rev-list --count '@{upstream}..HEAD')" == "0" ]] || {
    echo "FATAL: branch $BRANCH has unpushed commits" >&2; exit 2;
  }
fi

PROMPT="$(bash "$RUN" delegate --stem "$STEM")"
echo "Submitting $STEM to Codex Cloud..." >&2
"${CODEX_CLOUD_BIN:-codex}" cloud exec --env "$ENV_ID" --branch "$BRANCH" "$PROMPT"
