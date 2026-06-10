#!/usr/bin/env bash
# doctor.sh - Safely clean stale tool-call counters in session-turns.json
# Usage:
#   doctor.sh --show
#   doctor.sh --clear <session_id>
#   doctor.sh --clear-ended
#   doctor.sh --clear-over-limit [max_calls]
#   doctor.sh --clear-all
#
# Notes:
# - A "stale" entry means no recent tool_considered event in system-events.jsonl.
# - This script only edits ~/.claude/logs/session-turns.json.

set -euo pipefail

LOGS_DIR="$HOME/.claude/logs"
TURNS_FILE="$LOGS_DIR/session-turns.json"
EVENTS_LOG="$LOGS_DIR/system-events.jsonl"
DEFAULT_MAX=80

mkdir -p "$LOGS_DIR"

if [[ ! -f "$TURNS_FILE" ]]; then
  echo "No session counter file found at: $TURNS_FILE"
  exit 0
fi

usage() {
  cat <<'EOF'
Usage:
  doctor.sh --show
  doctor.sh --clear <session_id>
  doctor.sh --clear-ended
  doctor.sh --clear-over-limit [max_calls]
  doctor.sh --clear-all
EOF
}

show() {
  python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home()/'.claude/logs/session-turns.json'
try:
    data = json.load(open(p))
except Exception:
    data = {}
print(json.dumps(data, indent=2))
PY
}

clear_id() {
  local sid="$1"
  python3 - "$sid" <<'PY'
import json, os, sys, pathlib
sid = sys.argv[1]
p = pathlib.Path.home()/'.claude/logs/session-turns.json'
try:
    data = json.load(open(p)) if p.exists() else {}
except Exception:
    data = {}
removed = sid in data
if removed:
    data.pop(sid, None)
with open(p, 'w') as f:
    json.dump(data, f, indent=2)
print(f"removed={str(removed).lower()} session_id={sid}")
PY
}

clear_all() {
  printf '{}\n' > "$TURNS_FILE"
  echo "Cleared all session counters in $TURNS_FILE"
}

clear_ended() {
  python3 - <<'PY'
import json, pathlib
turns_path = pathlib.Path.home()/'.claude/logs/session-turns.json'
log_path = pathlib.Path.home()/'.claude/logs/system-events.jsonl'

try:
    turns = json.load(open(turns_path)) if turns_path.exists() else {}
except Exception:
    turns = {}

ended = set()
if log_path.exists():
    for line in log_path.open():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get('event') == 'session_end' and ev.get('session_id'):
            ended.add(ev['session_id'])

removed = [sid for sid in list(turns.keys()) if sid in ended]
for sid in removed:
    turns.pop(sid, None)

with open(turns_path, 'w') as f:
    json.dump(turns, f, indent=2)

print(f"removed_count={len(removed)}")
if removed:
    print("removed_sessions=")
    for sid in removed:
        print(sid)
PY
}

clear_over_limit() {
  local max_calls="${1:-$DEFAULT_MAX}"
  python3 - "$max_calls" <<'PY'
import json, pathlib, sys
limit = int(sys.argv[1])
p = pathlib.Path.home()/'.claude/logs/session-turns.json'
try:
    turns = json.load(open(p)) if p.exists() else {}
except Exception:
    turns = {}
removed = [sid for sid, count in list(turns.items()) if isinstance(count, int) and count >= limit]
for sid in removed:
    turns.pop(sid, None)
with open(p, 'w') as f:
    json.dump(turns, f, indent=2)
print(f"limit={limit} removed_count={len(removed)}")
if removed:
    print("removed_sessions=")
    for sid in removed:
        print(sid)
PY
}

case "${1:-}" in
  --show)
    show
    ;;
  --clear)
    [[ -n "${2:-}" ]] || { echo "Missing session_id for --clear"; usage; exit 1; }
    clear_id "$2"
    ;;
  --clear-ended)
    clear_ended
    ;;
  --clear-over-limit)
    clear_over_limit "${2:-$DEFAULT_MAX}"
    ;;
  --clear-all)
    clear_all
    ;;
  *)
    usage
    exit 1
    ;;
esac
