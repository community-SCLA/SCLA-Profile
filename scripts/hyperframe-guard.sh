#!/usr/bin/env bash
# hyperframe-guard.sh — enforce the frame contract AT AUTHORING TIME.
#
# STD-35: a written rule is a request; only a mechanism is a guarantee. The
# static gates were already mechanisms — but they only fired at preflight,
# i.e. AFTER a cold subagent had authored an entire 21-scene video.
# Discovering "8 of your scenes are the same template" at that point means
# rebuilding from scratch, so in practice the builder learned the rule late or
# not at all (owner, 2026-07-28: "I want them to be enforceable from the very
# beginning when the hyperframes are actually being rendered").
#
# The builder authors scenes.json (the plan); render-qa/build_index.py
# compiles it to index.html deterministically. This hook fires on every write
# to either file: on a scenes.json write it recompiles index.html first, then
# runs `preflight.py --static` — the SAME sections the hard gate runs, minus
# the ones that need voice assets. One source of truth, thousands of tokens
# earlier.
#
# Usage:
#   bash scripts/hyperframe-guard.sh <workspace|index.html|scenes.json>  # human/CI
#   bash scripts/hyperframe-guard.sh --hook                              # PostToolUse hook
#
# Fail-soft by design: a half-written scenes.json during authoring is normal
# (malformed JSON reports nothing), so this NEVER blocks the write (always
# exit 0 in --hook mode). It reports. The hard block stays at preflight, which
# is the last point where a rebuild is still cheap.

set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RQ="$REPO/projects/video-production/render-qa"

resolve_ws() {
  # Accept a workspace dir or any path inside one; return the workspace root.
  local p="${1:-}"
  [ -n "$p" ] || return 1
  case "$p" in */index.html|*/scenes.json) p="$(dirname "$p")" ;; esac
  # Walk up until we find the workspace marker.
  while [ "$p" != "/" ] && [ -n "$p" ]; do
    if { [ -f "$p/index.html" ] || [ -f "$p/scenes.json" ]; } && [ -d "$p/compositions" ]; then
      printf '%s' "$p"; return 0
    fi
    p="$(dirname "$p")"
  done
  return 1
}

run_gates() {
  # Static preflight — the same code path as the hard gate (one source of
  # truth). Emits only the actionable lines: each failing section's name and
  # output; nothing when the plan is clean.
  local ws="$1" out viol
  out="$(python3 "$RQ/preflight.py" --static --json "$ws" 2>&1)"
  viol="$(printf '%s' "$out" | jq -r '
    .sections | to_entries[] | select(.value.pass | not)
    | "!! [" + .key + "]\n"
      + (.value.output | split("\n") | map("   " + .) | join("\n"))' 2>/dev/null)"
  if [ -z "$viol" ] && ! printf '%s' "$out" | jq -e '.verdict' >/dev/null 2>&1; then
    # preflight crashed instead of grading — that is itself actionable.
    viol="!! [preflight] preflight.py --static produced no verdict:
$(printf '%s\n' "$out" | head -15)"
  fi
  printf '%s' "$viol"
}

check_workspace() {
  # $1 = workspace, $2 = kind (scenes|index|cli). Prints violations (if any).
  local ws="$1" kind="$2" co
  if [ "$kind" = "scenes" ] || { [ "$kind" = "cli" ] && [ -f "$ws/scenes.json" ]; }; then
    # Malformed JSON mid-edit is normal authoring — report nothing.
    python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$ws/scenes.json" \
      >/dev/null 2>&1 || return 0
    # The plan parses: recompile index.html so the gates grade THIS plan.
    if ! co="$(python3 "$RQ/build_index.py" "$ws" 2>&1)"; then
      printf '!! [build_index] scenes.json parses but did not compile:\n%s\n' \
        "$(printf '%s\n' "$co" | head -15)"
      return 0
    fi
  fi
  [ -f "$ws/index.html" ] || return 0
  run_gates "$ws"
}

if [ "${1:-}" = "--hook" ]; then
  INPUT="$(cat)"
  FP="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null)"
  case "$FP" in
    *renders-hyperframes*index.html) KIND=index ;;
    *renders-hyperframes*scenes.json) KIND=scenes ;;
    *) exit 0 ;;
  esac
  WS="$(resolve_ws "$FP")" || exit 0
  VIOL="$(check_workspace "$WS" "$KIND")" || true
  [ -n "$VIOL" ] || exit 0
  MSG="FRAME CONTRACT (automated guard, fired on your ${KIND/scenes/scenes.json} write; graded by preflight.py --static — the same sections the hard gate runs). These are HARD GATES that preflight will fail on — fix them NOW, while the scene plan is still a cheap JSON edit, not after the build is finished:

${VIOL}
Fix the plan in scenes.json and let build_index.py recompile — NEVER edit index.html by hand; it is compiled output and your edit will be overwritten. Contract: design-system/frame.md -> \"Variety contract\" and \"Type rules\". Do not proceed to narration synthesis or render with these outstanding."
  jq -cn --arg m "$MSG" \
    '{hookSpecificOutput:{hookEventName:"PostToolUse", additionalContext:$m}}'
  exit 0
fi

WS="$(resolve_ws "${1:-}")" || {
  echo "usage: bash scripts/hyperframe-guard.sh <workspace|index.html|scenes.json>" >&2
  exit 2; }
VIOL="$(check_workspace "$WS" cli)" || true
if [ -n "$VIOL" ]; then
  echo "FRAME CONTRACT violations in $(basename "$WS"):"
  printf '%s\n' "$VIOL"
else
  echo "FRAME CONTRACT: clean — $(basename "$WS")"
fi
exit 0
