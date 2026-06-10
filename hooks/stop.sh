#!/usr/bin/env bash
# stop.sh — Logs session end with total tool call count and stop reason.
# Receives JSON on stdin: {"session_id": "...", "stop_reason": "...", "usage": {...}}

LOGS_DIR="$HOME/.claude/logs"
EVENTS_LOG="$LOGS_DIR/system-events.jsonl"
TURNS_FILE="$LOGS_DIR/session-turns.json"

mkdir -p "$LOGS_DIR"

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','unknown'))" 2>/dev/null || echo "unknown")
STOP_REASON=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('stop_reason','unknown'))" 2>/dev/null || echo "unknown")
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Get final tool call count
TOTAL_CALLS=0
if [ -f "$TURNS_FILE" ]; then
  TOTAL_CALLS=$(python3 -c "
import json
try:
    d = json.load(open('$TURNS_FILE'))
    print(d.get('$SESSION_ID', 0))
except:
    print(0)
" 2>/dev/null || echo "0")
fi

echo "{\"ts\":\"$TS\",\"session_id\":\"$SESSION_ID\",\"event\":\"session_end\",\"stop_reason\":\"$STOP_REASON\",\"total_tool_calls\":$TOTAL_CALLS}" >> "$EVENTS_LOG"

# Clear the finished session from the counter file so resumed sessions do not inherit stale counts.
python3 -c "
import json, os
f = '$TURNS_FILE'
if os.path.exists(f):
  try:
    d = json.load(open(f))
  except:
    d = {}
  d.pop('$SESSION_ID', None)
  json.dump(d, open(f, 'w'), indent=2)
" 2>/dev/null

exit 0
