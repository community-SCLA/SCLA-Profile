#!/usr/bin/env bash
# SCLA video control plane. Agents and humans enter the pipeline here; the
# existing scripts remain implementation details during the compatibility window.
set -euo pipefail

SCRIPT_VP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VP="${VIDEO_VP_ROOT:-$SCRIPT_VP}"
REPO="${VIDEO_REPO_ROOT:-$(cd "$SCRIPT_VP/../.." && pwd)}"
STATE="${VIDEO_RUN_STATE_TOOL:-$SCRIPT_VP/render-qa/src/run_state.py}"

refresh_human_status() {
  bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true
}

usage() {
  echo "usage: run.sh {status [--json]|produce --stem STEM|refine --stem STEM|batch (--program SLUG|--all)|approve STEM|ship STEM [--publish]|resume|retry STEM --reason TEXT}" >&2
  exit 2
}

stem_arg() {
  [[ "${1:-}" == "--stem" && -n "${2:-}" ]] || usage
  printf '%s' "$2"
}

command="${1:-}"
shift || true
case "$command" in
  status)
    if [[ "${1:-}" == "--json" ]]; then
      bash "$REPO/scripts/batch-status.sh" --json
    else
      bash "$REPO/scripts/batch-status.sh"
    fi
    ;;
  produce|refine)
    stem="$(stem_arg "${1:-}" "${2:-}")"
    python3 "$STATE" select --mode "$command" --scope-kind stem --scope-value "$stem"
    refresh_human_status
    echo
    echo "Selected only $stem. No unrelated inbox or queue item is in scope."
    ;;
  batch)
    case "${1:-}" in
      --program)
        [[ -n "${2:-}" ]] || usage
        python3 "$STATE" select --mode batch --scope-kind program --scope-value "$2"
        refresh_human_status
        ;;
      --all)
        python3 "$STATE" select --mode batch --scope-kind all
        refresh_human_status
        ;;
      *) usage ;;
    esac
    ;;
  approve)
    [[ -n "${1:-}" ]] || usage
    python3 "$STATE" approve "$1" --approved-by owner
    refresh_human_status
    ;;
  ship)
    [[ -n "${1:-}" ]] || usage
    stem="$1"; mode="${2:-}"
    located="$(python3 "$STATE" locate "$stem")"
    program="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("program") or "")' <<<"$located")"
    [[ -n "$program" ]] || { echo "FATAL: cannot resolve program for $stem" >&2; exit 2; }
    if [[ "$mode" == "--publish" ]]; then
      bash "$REPO/scripts/batch-ship.sh" "$stem" "$program" --publish
    elif [[ -z "$mode" ]]; then
      bash "$REPO/scripts/batch-ship.sh" "$stem" "$program"
    else
      usage
    fi
    ;;
  resume)
    echo "== active run"
    python3 "$STATE" show || true
    echo "== live status"
    bash "$REPO/scripts/batch-status.sh" --json
    ;;
  retry)
    [[ -n "${1:-}" && "${2:-}" == "--reason" && -n "${3:-}" ]] || usage
    python3 "$STATE" retry "$1" --reason "$3"
    refresh_human_status
    ;;
  *) usage ;;
esac
