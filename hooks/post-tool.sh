#!/usr/bin/env bash
# post-tool.sh — Logs tool execution result after each tool fires.
# Receives JSON on stdin: {"session_id": "...", "tool_name": "...", "tool_input": {...}, "tool_response": {...}}

LOGS_DIR="$HOME/.claude/logs"
EVENTS_LOG="$LOGS_DIR/system-events.jsonl"
TURNS_FILE="$LOGS_DIR/session-turns.json"

mkdir -p "$LOGS_DIR"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','unknown'))" 2>/dev/null || echo "unknown")
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Get current tool call count for this session
CURRENT_COUNT=0
if [ -f "$TURNS_FILE" ]; then
  CURRENT_COUNT=$(python3 -c "
import json
try:
    d = json.load(open('$TURNS_FILE'))
    print(d.get('$SESSION_ID', 0))
except:
    print(0)
" 2>/dev/null || echo "0")
fi

# Log tool_selected event
echo "{\"ts\":\"$TS\",\"session_id\":\"$SESSION_ID\",\"event\":\"tool_selected\",\"tool\":\"$TOOL_NAME\",\"tool_call\":$CURRENT_COUNT}" >> "$EVENTS_LOG"

exit 0
