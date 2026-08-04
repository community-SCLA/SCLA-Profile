#!/usr/bin/env bash
# write-fence.sh — PreToolUse fence around the shared pipeline machinery.
#
# THE HOLE THIS CLOSES. .claude/settings.json grants Write and Edit with no path
# restriction, and the only hook (hyperframe-guard.sh) exits 0 for anything
# outside a workspace's scenes.json / index.html. So when a build agent decided
# to "improve" the shared scla-stat template and 14 workspace copies of it,
# nothing even slowed it down. "You author scenes.json only" was a sentence, not
# a mechanism — the failure class this repo's own log quantifies as 14 defects
# from rules that existed but did not fire, and 0 from rules anyone forgot.
#
# The agent-native experiment then demonstrated the guard is LOCATION-shaped and
# can be routed around (PROVENANCE §2). This fence is PATH-shaped instead.
#
# WHAT IS FENCED (shared machinery — one edit corrupts every future build):
#   projects/video-production/design-system/         templates, tokens.yml, contracts
#   projects/video-production/renders-hyperframes/_run/   the scaffold every workspace is copied from
#   projects/video-production/render-qa/src/         the gates themselves
#   scripts/                                         the orchestration
#   .claude/                                         rules, agents, settings, hooks
#
# WHAT IS NOT: a workspace's own files. renders-hyperframes/<stem>/ stays fully
# writable — that is where building happens, and fencing it would fence the job.
#
# DEFAULT DENY. Template and gate work is a DELIBERATE, SEPARATE session type,
# marked by exporting SCLA_SYSTEM_SESSION=1 in the shell that launches Claude
# Code. A build subagent never sets it and cannot set it for itself: the value
# is read from the agent process's own environment, which a Bash tool call
# cannot reach back into. Defaulting the other way would mean the fence is off
# in exactly the sessions nobody remembered to think about.
#
# Exit 0 = allow. Exit 2 = block, with stderr fed back to the model as the
# reason (the documented PreToolUse blocking contract).
#
# Tested by render-qa/tests/test_write_fence.py, which runs THIS script as a
# subprocess with crafted hook payloads — per test_guard_contract.py's rule that
# a guard is verified by invoking it, never by reading it. A hook that crashes
# is a gate that is off; one that blocks everything is worse.

set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"

# A deliberately flagged system session: template/gate/orchestration work.
if [ "${SCLA_SYSTEM_SESSION:-0}" = "1" ]; then
  exit 0
fi

FENCED_PREFIXES=(
  "projects/video-production/design-system/"
  "projects/video-production/renders-hyperframes/_run/"
  "projects/video-production/render-qa/src/"
  "scripts/"
  ".claude/"
)

PAYLOAD="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  echo "write-fence: jq is not available, so this fence cannot read the tool" \
       "call it is supposed to be grading. Refusing rather than passing —" \
       "a guard that cannot see is not a guard." >&2
  exit 2
fi

TOOL="$(printf '%s' "$PAYLOAD" | jq -r '.tool_name // ""' 2>/dev/null)"
if [ -z "$TOOL" ]; then
  echo "write-fence: could not parse the PreToolUse payload. Refusing rather" \
       "than passing — an unreadable call is not a safe one." >&2
  exit 2
fi

# Repo-relative, with the project dir and any ./ prefix stripped.
relativize() {
  local p="$1"
  p="${p#"$PROJECT_DIR"/}"
  p="${p#./}"
  printf '%s' "$p"
}

is_fenced() {
  local rel
  rel="$(relativize "$1")"
  for prefix in "${FENCED_PREFIXES[@]}"; do
    case "$rel" in
      "$prefix"*) printf '%s' "$prefix"; return 0 ;;
    esac
  done
  return 1
}

deny() {
  cat >&2 <<EOF
BLOCKED by scripts/write-fence.sh — $1 is shared pipeline machinery.

  target: $2
  fenced: $3

One edit here changes every future build, so this is not a build-session
action. Nothing about your current task requires it:

  - Authoring a video?  Write inside your own workspace
    (renders-hyperframes/<stem>/) — that is fully writable.
  - Hit a template, token, gate or script that is genuinely WRONG?  That is a
    real finding and it should be REPORTED, not patched from here. Say what is
    wrong and what you would change; a flagged system session
    (SCLA_SYSTEM_SESSION=1) makes the change deliberately, with the gates and
    tests that go with it.

Do not attempt to route around this with another path form, a shell redirect,
or a copy — the fence matches on the resolved path, and working around a guard
is itself the defect it exists to catch.
EOF
  exit 2
}

case "$TOOL" in
  Write|Edit|NotebookEdit)
    TARGET="$(printf '%s' "$PAYLOAD" \
      | jq -r '.tool_input.file_path // .tool_input.notebook_path // ""')"
    [ -z "$TARGET" ] && exit 0
    if PREFIX="$(is_fenced "$TARGET")"; then
      deny "$TOOL to this path" "$TARGET" "$PREFIX"
    fi
    ;;
  Bash)
    CMD="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // ""')"
    [ -z "$CMD" ] && exit 0
    # Only commands that can actually MUTATE are candidates. Reading, running
    # and grepping fenced files stay free — `python3 render-qa/src/check_copy.py`
    # and `bash scripts/lint-refs.sh` are the pipeline working normally, and a
    # fence that blocked them would be removed within a day.
    # Destructive: the fenced path is damaged wherever it appears, including as
    # a SOURCE (`mv fenced/x /tmp` removes it just as surely as rm does).
    DESTRUCTIVE='(^|[[:space:];&|(])(rm|mv|tee|touch|truncate|dd|patch|shred|chmod|chown)([[:space:]]|$)'
    REDIRECT='>[[:space:]]*[^|&[:space:]]'
    SED_INPLACE='(^|[[:space:];&|(])(sed|perl)([[:space:]]+[^;&|]*)?[[:space:]]-[a-zA-Z]*i'
    GIT_MUTATE='(^|[[:space:];&|(])git[[:space:]]+(checkout|restore|rm|mv|apply|clean|reset)([[:space:]]|$)'
    # Copy-family: only the DESTINATION is written. Copying OUT of a fenced
    # path is a read — and it is what batch-prepare.sh does on every prepare
    # (`cp design-system/config/tokens.yml <scaffold>/`). A fence that blocked
    # that would block the pipeline doing its job correctly, which is how a
    # guard gets switched off inside a day.
    COPY_FAMILY='(^|[[:space:];&|(])(cp|install|ln|rsync)([[:space:]]|$)'

    tokens_of() {
      printf '%s' "$1" | tr '"'"'"'`=(){}[]<>|&;,' ' '
    }

    if printf '%s' "$CMD" | grep -Eq "$DESTRUCTIVE|$REDIRECT|$SED_INPLACE|$GIT_MUTATE"; then
      for tok in $(tokens_of "$CMD"); do
        case "$tok" in -*) continue ;; esac
        if PREFIX="$(is_fenced "$tok")"; then
          deny "a Bash-mediated write touching this path" "$tok" "$PREFIX"
        fi
      done
    elif printf '%s' "$CMD" | grep -Eq "$COPY_FAMILY"; then
      # Destination only: the last non-flag token.
      DEST=""
      for tok in $(tokens_of "$CMD"); do
        case "$tok" in -*) continue ;; esac
        DEST="$tok"
      done
      if [ -n "$DEST" ] && PREFIX="$(is_fenced "$DEST")"; then
        deny "a Bash-mediated copy INTO this path" "$DEST" "$PREFIX"
      fi
    fi
    ;;
esac

exit 0
