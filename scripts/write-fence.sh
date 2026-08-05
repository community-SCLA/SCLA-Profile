#!/usr/bin/env bash
# write-fence.sh — PreToolUse fence around the shared pipeline machinery.
#
# THE HOLE THIS CLOSES. .claude/settings.json grants Write and Edit with no path
# restriction, and no other PreToolUse hook restricts anything
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
# WHEN IT IS ON: only while a build is running, which is announced by the
# sentinel file renders-hyperframes/.build-in-progress (written by
# scripts/build-session.sh arm, from scripts/build-claim.sh). No sentinel means
# no build, which means an owner session — and an owner is never fenced.
#
# WHY NOT A SESSION ENV FLAG. The first cut of this fence default-DENIED and
# expected template/gate work to export SCLA_SYSTEM_SESSION=1. That
# discriminator cannot work: the owner and the build subagents they dispatch
# share ONE process, so one env value has to answer for both, and it answered
# for the wrong one — it fenced the owner out of their own repo within a day of
# install and was switched off. The sentinel discriminates on what is actually
# happening (a build is in flight) rather than on which session type someone
# remembered to declare. The env flag is kept as an explicit override.
#
# The sentinel path is itself fenced, so an armed builder cannot rm its way out.
# A sentinel a dead run never cleaned up expires after VIDEO_BUILD_SESSION_TTL
# seconds (default 6h) — a stale lock file must not fence the repo forever.
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

SENTINEL_REL="projects/video-production/renders-hyperframes/.build-in-progress"
SENTINEL="$PROJECT_DIR/$SENTINEL_REL"

# A deliberately flagged system session: template/gate/orchestration work.
# Kept as an explicit override for anyone who wants the old behaviour back.
if [ "${SCLA_SYSTEM_SESSION:-0}" = "1" ]; then
  exit 0
fi

# No build in flight -> this is an owner session -> the fence is OFF entirely.
# An expired sentinel counts as absent: a run that died without disarming must
# not leave the repo read-only until someone notices.
if [ ! -f "$SENTINEL" ]; then
  exit 0
fi
TTL="${VIDEO_BUILD_SESSION_TTL:-21600}"
case "$TTL" in ''|*[!0-9]*) TTL=21600 ;; esac
if [ "$TTL" -gt 0 ]; then
  NOW="$(date +%s)"
  ARMED_AT="$(stat -c %Y "$SENTINEL" 2>/dev/null \
              || stat -f %m "$SENTINEL" 2>/dev/null \
              || printf '%s' "$NOW")"
  if [ "$((NOW - ARMED_AT))" -ge "$TTL" ]; then
    exit 0
  fi
fi

FENCED_PREFIXES=(
  "projects/video-production/design-system/"
  "projects/video-production/renders-hyperframes/_run/"
  "projects/video-production/render-qa/src/"
  "scripts/"
  ".claude/"
  # The sentinel itself: an armed builder must not be able to disarm the fence
  # it is standing inside. build-session.sh does the rm, and the hook grades
  # tool calls, not what a script does after it starts.
  "$SENTINEL_REL"
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
  local rel bare
  rel="$(relativize "$1")"
  rel="${rel%/}"
  for prefix in "${FENCED_PREFIXES[@]}"; do
    bare="${prefix%/}"
    # Both the DIRECTORY and anything under it. Matching the prefix alone left
    # the fenced directory itself unfenced — `rm -rf render-qa/src` names no
    # trailing slash, so the one command that would destroy every gate at once
    # was the one command this fence let through (found 2026-08-04 by a test
    # written for a different bug).
    case "$rel" in
      "$bare"|"$bare"/*) printf '%s' "$prefix"; return 0 ;;
    esac
  done
  return 1
}

deny() {
  cat >&2 <<EOF
BLOCKED by scripts/write-fence.sh — $1 is shared pipeline machinery.

  target: $2
  fenced: $3

A build is in flight (renders-hyperframes/.build-in-progress is armed), and one
edit here changes every future build. Nothing about building a video requires
it:

  - Authoring a video?  Write inside your own workspace
    (renders-hyperframes/<stem>/) — that is fully writable.
  - Hit a template, token, gate or script that is genuinely WRONG?  That is a
    real finding, and the right move is to REPORT it: say what is wrong, what
    you would change, and carry on with the build. The owner makes machinery
    changes outside a build, when the fence is down, with the gates and tests
    that go with them.

There is no flag for you to set. The fence is armed by the build you are part
of, and it comes down at close-out (scripts/build-release.sh).

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

    # ---------------------------------------------------------------------
    # DATA IS NOT COMMAND (fix 2026-08-04, the day this fence shipped).
    #
    # Heredoc bodies and -m/-F message arguments are payload text. A commit
    # whose MESSAGE merely mentions a mutator word near a fenced path writes
    # nothing fenced, and refusing it is the "too tight" failure mode that gets
    # a guard switched off within a day. This fence was bitten by exactly that
    # within minutes of install: the commit describing its own probe was
    # refused, and so was the patch that would have fixed it.
    # ---------------------------------------------------------------------
    SCAN="$(printf '%s' "$CMD" | awk '
      BEGIN { skip = 0 }
      {
        if (skip) { if ($0 == term) skip = 0; next }
        if (match($0, /<<-?[ ]*.?[A-Za-z_][A-Za-z0-9_]*.?[ ]*$/)) {
          t = substr($0, RSTART, RLENGTH)
          gsub(/^<<-?[ ]*/, "", t); gsub(/[^A-Za-z0-9_]/, "", t)
          term = t; skip = 1
        }
        print
      }')"
    SCAN="$(printf '%s' "$SCAN" | sed -E \
      's/(^|[[:space:]])(-m|-F|--message)[[:space:]]+("[^"]*"|'"'"'[^'"'"']*'"'"'|[^[:space:]]+)/\1\2 MSG/g')"

    # ---------------------------------------------------------------------
    # A redirect is graded by WHAT IT WRITES TO, never by merely existing.
    # `2>/dev/null` writes nothing fenced. Treating any ">" as a fence-wide
    # alarm refused ordinary read-only commands that happened to name a fenced
    # path — three times on install day, including one where the ">" was inside
    # a quoted sed replacement and was not a redirect at all.
    # ---------------------------------------------------------------------
    for tgt in $(printf '%s' "$SCAN" \
      | grep -oE '[0-9]*>>?[[:space:]]*[^[:space:];&|<>]+' \
      | sed -E 's/^[0-9]*>>?[[:space:]]*//'); do
      if PREFIX="$(is_fenced "$tgt")"; then
        deny "a shell redirect writing into this path" "$tgt" "$PREFIX"
      fi
    done

    # Destructive: the fenced path is damaged wherever it appears, including as
    # a SOURCE (`mv fenced/x /tmp` removes it just as surely as rm does).
    DESTRUCTIVE='(^|[[:space:];&|(])(rm|mv|tee|touch|truncate|dd|patch|shred|chmod|chown)([[:space:]]|$)'
    SED_INPLACE='(^|[[:space:];&|(])(sed|perl)([[:space:]]+[^;&|]*)?[[:space:]]-[a-zA-Z]*i'
    GIT_MUTATE='(^|[[:space:];&|(])git[[:space:]]+(checkout|restore|rm|mv|apply|clean|reset)([[:space:]]|$)'
    # Copy-family: only the DESTINATION is written. Copying OUT of a fenced
    # path is a read — and it is what batch-prepare.sh does on every prepare
    # (`cp design-system/config/tokens.yml <scaffold>/`). A fence that blocked
    # that would block the pipeline doing its job correctly.
    COPY_FAMILY='(^|[[:space:];&|(])(cp|install|ln|rsync)([[:space:]]|$)'

    tokens_of() {
      printf '%s' "$1" | tr '"'"'"'`=(){}[]<>|&;,' ' '
    }

    # ---------------------------------------------------------------------
    # A MUTATOR TAINTS ITS OWN SUB-COMMAND, NOT THE WHOLE LINE (fix
    # 2026-08-04, observed live within minutes of the sentinel rebuild).
    #
    #   find <workspace> -exec touch {} + ; bash scripts/batch-status.sh
    #
    # was refused: `touch` is destructive, and the whole-line token scan then
    # matched `scripts/batch-status.sh` — an argument to `bash` in a DIFFERENT
    # sub-command, which the touch never goes near. Reading and running fenced
    # files is supposed to stay free, and a guard that refuses a read because
    # something else on the line was a write is the "too tight" failure mode
    # that gets guards switched off.
    #
    # Grading each segment on its own keeps the verb and its arguments
    # together, which is the only pairing that ever mattered.
    # ---------------------------------------------------------------------
    SEGMENTS="$(printf '%s' "$SCAN" | sed -E 's/(\|\||&&|[;|&])/\n/g')"

    while IFS= read -r seg; do
      [ -z "${seg// /}" ] && continue
      if printf '%s' "$seg" | grep -Eq "$DESTRUCTIVE|$SED_INPLACE|$GIT_MUTATE"; then
        for tok in $(tokens_of "$seg"); do
          case "$tok" in -*) continue ;; esac
          if PREFIX="$(is_fenced "$tok")"; then
            deny "a Bash-mediated write touching this path" "$tok" "$PREFIX"
          fi
        done
      elif printf '%s' "$seg" | grep -Eq "$COPY_FAMILY"; then
        # Destination only: the last non-flag token of THIS sub-command.
        DEST=""
        for tok in $(tokens_of "$seg"); do
          case "$tok" in -*) continue ;; esac
          DEST="$tok"
        done
        if [ -n "$DEST" ] && PREFIX="$(is_fenced "$DEST")"; then
          deny "a Bash-mediated copy INTO this path" "$DEST" "$PREFIX"
        fi
      fi
    done <<EOF
$SEGMENTS
EOF
    ;;
esac

exit 0
