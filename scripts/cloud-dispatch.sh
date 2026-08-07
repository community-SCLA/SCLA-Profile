#!/usr/bin/env bash
# Submit one selected, untouched READY lesson to the configured Codex Cloud environment.
set -euo pipefail

SCRIPT_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${VIDEO_REPO_ROOT:-$SCRIPT_REPO}"
VP="${VIDEO_VP_ROOT:-$REPO/projects/video-production}"
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

CURRENT_BRANCH="$(git -C "$REPO" branch --show-current)"
BRANCH="${CODEX_CLOUD_BRANCH:-$CURRENT_BRANCH}"
[[ -n "$BRANCH" ]] || { echo "FATAL: dispatch requires a named git branch" >&2; exit 2; }
[[ "$BRANCH" == "$CURRENT_BRANCH" ]] || {
  echo "FATAL: Cloud branch $BRANCH is not the checked-out branch $CURRENT_BRANCH" >&2
  exit 2
}
if [[ "${CODEX_CLOUD_ALLOW_DIRTY:-0}" != "1" ]]; then
  PROGRAM="${CLOUD_PROGRAM:-}"
  [[ -n "$PROGRAM" ]] || {
    echo "FATAL: Cloud dispatch did not receive the selected lesson program" >&2; exit 2;
  }
  REL_VP="${VP#"$REPO"/}"
  cloud_inputs=(
    "AGENTS.md"
    ".claude/rules/video-production.md"
    "$REL_VP/CLAUDE.md"
    "$REL_VP/contracts/cloud-author.md"
    "$REL_VP/lesson-scripts/$PROGRAM/ready/$STEM.txt"
    "$REL_VP/renders-hyperframes/_run/scaffold"
    "$REL_VP/render-qa/src"
    ":(exclude)$REL_VP/render-qa/src/run_state.py"
    ":(exclude)$REL_VP/render-qa/src/workspace_revision.py"
    ":(exclude)$REL_VP/render-qa/src/source_checkpoint.py"
    ":(exclude)$REL_VP/render-qa/src/verify_render.py"
    "scripts/cloud-author.sh"
    "scripts/cloud-review-ready.sh"
  )
  [[ -z "$(git -C "$REPO" status --porcelain -- "${cloud_inputs[@]}")" ]] || {
    echo "FATAL: commit and push this lesson's Cloud inputs before dispatch" >&2
    echo "       Unrelated dirty lesson workspaces do not block dispatch." >&2
    exit 2
  }
fi

# Cloud reads the upstream commit, not this working tree.  Merely having no
# unpushed commits is insufficient: a checkout behind upstream would dispatch
# stale instructions and lesson source.  Dirty-input checks may be explicitly
# bypassed for controlled tests, but commit identity never is.
git -C "$REPO" rev-parse --verify '@{upstream}' >/dev/null 2>&1 || {
  echo "FATAL: branch $BRANCH has no upstream; push it before Cloud dispatch" >&2; exit 2;
}
LOCAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
UPSTREAM_HEAD="$(git -C "$REPO" rev-parse '@{upstream}')"
[[ "$LOCAL_HEAD" == "$UPSTREAM_HEAD" ]] || {
  echo "FATAL: local HEAD must exactly match upstream before Cloud dispatch" >&2
  echo "       local=$LOCAL_HEAD upstream=$UPSTREAM_HEAD" >&2
  exit 2
}

PROMPT="$(bash "$RUN" delegate --stem "$STEM")"
echo "Submitting $STEM to Codex Cloud..." >&2
# The Codex Cloud CLI writes error.log in its current directory. Keep that
# diagnostic side effect outside the tracked worktree so parallel dispatches
# cannot make one another fail the clean-worktree preflight.
CLI_WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/scla-codex-cloud.XXXXXX")"
trap 'rm -rf -- "$CLI_WORKDIR"' EXIT
(
  cd "$CLI_WORKDIR"
  "${CODEX_CLOUD_BIN:-codex}" cloud exec --env "$ENV_ID" --branch "$BRANCH" "$PROMPT"
)
