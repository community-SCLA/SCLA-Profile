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
  echo "usage: run.sh {status [--json]|produce --stem STEM|refine --stem STEM|batch (--program SLUG|--all) [--cloud]|delegate --stem STEM|dispatch --stem STEM|dispatch-merged --stem STEM [--task-ref REF]|drain|limits|cloud-limit (2|4)|visual-review STEM VERDICTS|encode-review STEM VERDICT|approve (STEM|BATCH)|ship STEM [--publish]|resume [--json]|retry STEM --reason TEXT|migrate-state}" >&2
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
        program="$2"
        shift 2
        authoring_backend="local"
        if [[ "${1:-}" == "--cloud" && -z "${2:-}" ]]; then
          authoring_backend="cloud"
        elif [[ -n "${1:-}" ]]; then
          usage
        fi
        python3 "$STATE" select --mode batch --scope-kind program \
          --scope-value "$program" --authoring-backend "$authoring_backend"
        refresh_human_status
        ;;
      --all)
        shift
        authoring_backend="local"
        if [[ "${1:-}" == "--cloud" && -z "${2:-}" ]]; then
          authoring_backend="cloud"
        elif [[ -n "${1:-}" ]]; then
          usage
        fi
        python3 "$STATE" select --mode batch --scope-kind all \
          --authoring-backend "$authoring_backend"
        refresh_human_status
        ;;
      *) usage ;;
    esac
    ;;
  delegate)
    stem="$(stem_arg "${1:-}" "${2:-}")"
    located="$(python3 "$STATE" delegate-info "$stem")"
    program="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("program") or "")' <<<"$located")"
    [[ -n "$program" ]] || { echo "FATAL: cannot resolve ready script for $stem" >&2; exit 2; }
    cat <<EOF
Work only on ${stem} for program ${program}.

Read projects/video-production/contracts/cloud-author.md, then follow it exactly.
Run: bash scripts/cloud-author.sh ${stem} ${program}

This is source-only authoring. Do not call HeyGen, render, publish, or modify
run.json, PIPELINE-STATUS.md, shared scripts, contracts, or another workspace.
Run bash scripts/cloud-review-ready.sh ${stem}. Do not call the task complete
unless it prints REVIEW_READY: PASS. Commit only this workspace's trackable
source, and return the commit or pull-request link with the required summary
immediately; never wait for another lesson.
EOF
    ;;
  dispatch)
    stem="$(stem_arg "${1:-}" "${2:-}")"
    shift 2
    converge=0
    if [[ "${1:-}" == "--converge" && -z "${2:-}" ]]; then
      converge=1
    elif [[ -n "${1:-}" ]]; then
      usage
    fi
    reserve_args=(reserve-dispatch "$stem")
    [[ "$converge" == "0" ]] || reserve_args+=(--allow-existing)
    reservation="$(python3 "$STATE" "${reserve_args[@]}")"
    already_owned="$(python3 -c 'import json,sys; print("1" if json.load(sys.stdin).get("already_owned") else "0")' <<<"$reservation")"
    if [[ "$already_owned" == "1" ]]; then
      echo "Cloud dispatch converged: $stem already has durable external ownership."
      exit 0
    fi
    program="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["program"])' <<<"$reservation")"
    if dispatch_output="$(CLOUD_PROGRAM="$program" bash "$REPO/scripts/cloud-dispatch.sh" "$stem" 2>&1)"; then
      printf '%s\n' "$dispatch_output"
      task_ref="$(python3 -c 'import re,sys; s=sys.stdin.read(); u=re.findall(r"https?://\S+",s); lines=[x for x in s.splitlines() if x.strip()]; print((u[-1] if u else (lines[-1] if lines else "submitted"))[:1000])' <<<"$dispatch_output")"
      python3 "$STATE" record-dispatch "$stem" --status submitted --task-ref "$task_ref" >/dev/null
    else
      rc=$?
      printf '%s\n' "$dispatch_output" >&2
      outcome="failed"
      [[ "$dispatch_output" != *"Submitting $stem to Codex Cloud..."* ]] || outcome="unknown"
      python3 "$STATE" fail-dispatch "$stem" --outcome "$outcome" \
        --error "$dispatch_output" >/dev/null 2>&1 || true
      exit "$rc"
    fi
    ;;
  dispatch-merged)
    stem="$(stem_arg "${1:-}" "${2:-}")"
    shift 2
    task_ref=""
    if [[ "${1:-}" == "--task-ref" && -n "${2:-}" && -z "${3:-}" ]]; then
      task_ref="$2"
    elif [[ -n "${1:-}" ]]; then
      usage
    fi
    merged_args=(record-dispatch "$stem" --status merged)
    [[ -z "$task_ref" ]] || merged_args+=(--task-ref "$task_ref")
    python3 "$STATE" "${merged_args[@]}"
    refresh_human_status
    ;;
  drain)
    [[ -z "${1:-}" ]] || usage
    dispatchable="$(python3 "$STATE" dispatchable)"
    mapfile -t stems < <(python3 -c 'import json,sys; sys.stdout.write("\n".join(x["stem"] for x in json.load(sys.stdin)["items"]))' <<<"$dispatchable")
    blocked="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print("; ".join("{}: {}".format(x["stem"], x["condition"]) for x in d.get("blocked", [])))' <<<"$dispatchable")"
    if [[ -n "$blocked" ]]; then
      echo "Cloud drain safety hold: $blocked"
      echo "Record a merged handoff, or use retry only after confirming no remote task is running."
    fi
    if [[ ${#stems[@]} -eq 0 ]]; then
      echo "Cloud drain: no untouched selected READY lessons are dispatchable."
      exit 0
    fi
    echo "Cloud drain: dispatching ${#stems[@]} unique lesson(s)."
    pids=()
    for stem in "${stems[@]}"; do
      ( bash "$SCRIPT_VP/run.sh" dispatch --stem "$stem" --converge ) &
      pids+=("$!")
    done
    drain_rc=0
    for pid in "${pids[@]}"; do
      wait "$pid" || drain_rc=1
    done
    exit "$drain_rc"
    ;;
  limits)
    python3 "$STATE" capacity
    ;;
  cloud-limit)
    [[ -n "${1:-}" && -z "${2:-}" ]] || usage
    python3 "$STATE" set-cloud-concurrency "$1"
    refresh_human_status
    ;;
  approve)
    [[ -n "${1:-}" ]] || usage
    python3 "$STATE" approve "$1" --approved-by owner
    refresh_human_status
    ;;
  visual-review)
    [[ -n "${1:-}" ]] || usage
    python3 "$STATE" record-visual-review "$@"
    refresh_human_status
    ;;
  encode-review)
    [[ -n "${1:-}" ]] || usage
    python3 "$STATE" record-encode-review "$@"
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
    if [[ "${1:-}" == "--json" && -z "${2:-}" ]]; then
      active_json="$(python3 "$STATE" show 2>/dev/null || true)"
      [[ -n "$active_json" ]] || active_json='{}'
      live_json="$(bash "$REPO/scripts/batch-status.sh" --json)"
      ACTIVE_RUN_JSON="$active_json" LIVE_STATUS_JSON="$live_json" python3 - <<'PY'
import json, os

run = json.loads(os.environ["ACTIVE_RUN_JSON"])
live = json.loads(os.environ["LIVE_STATUS_JSON"])
observed = {}
for program in live.get("programs", []):
    slug = program.get("program")
    for stem in program.get("queued", []):
        observed[stem] = {"stage": "ready", "program": slug}
    for row in program.get("needs_script", []):
        observed[row["stem"]] = {"stage": "needs-script", "program": slug, **row}
    for stem in program.get("raw", []):
        observed[stem] = {"stage": "raw", "program": slug}
    for row in program.get("in_flight", []):
        observed[row["stem"]] = {"program": slug, **row}
    for row in program.get("stranded", []):
        observed[row["stem"]] = {"stage": "stranded", "program": slug, **row}

approvals = run.get("approvals") or {}
dispatches = run.get("dispatches") or {}
selection = []
for item in run.get("items", []):
    stem = item.get("stem")
    selection.append({
        "stem": stem,
        "program": item.get("program"),
        "observed": observed.get(stem, {"stage": "unknown"}),
        "approval": approvals.get(stem),
        "dispatch": dispatches.get(stem),
    })
print(json.dumps({
    "scope": run.get("scope"),
    "mode": run.get("mode"),
    "authoring_backend": run.get("authoring_backend", "local"),
    "capacity": live.get("run", {}),
    "selection": selection,
}, indent=2))
PY
    elif [[ -z "${1:-}" ]]; then
      echo "== active run"
      python3 "$STATE" show || true
      echo "== live status"
      bash "$REPO/scripts/batch-status.sh" --json
    else
      usage
    fi
    ;;
  retry)
    [[ -n "${1:-}" && "${2:-}" == "--reason" && -n "${3:-}" ]] || usage
    python3 "$STATE" retry "$1" --reason "$3"
    refresh_human_status
    ;;
  migrate-state)
    [[ -z "${1:-}" ]] || usage
    python3 "$STATE" migrate-state
    refresh_human_status
    ;;
  *) usage ;;
esac
