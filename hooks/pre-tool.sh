#!/usr/bin/env bash
# pre-tool.sh — Logs tool consideration and checks turn budget before any tool fires.
# Receives JSON on stdin: {"session_id": "...", "tool_name": "...", "tool_input": {...}}
# Exit 0: allow | Exit 2 + stdout message: block with reason shown to user.

LOGS_DIR="$HOME/.claude/logs"
EVENTS_LOG="$LOGS_DIR/system-events.jsonl"
TURNS_FILE="$LOGS_DIR/session-turns.json"
BUDGET_FILE="$HOME/.claude/budget.json"

mkdir -p "$LOGS_DIR"

# Parse stdin
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','unknown'))" 2>/dev/null || echo "unknown")
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Skip budget tracking for hook/doctor scripts to avoid noise
if [[ "$TOOL_NAME" == "Bash" ]]; then
  CMD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")
  if [[ "$CMD" == *"pre-tool.sh"* || "$CMD" == *"post-tool.sh"* || "$CMD" == *"stop.sh"* || "$CMD" == *"doctor.sh"* ]]; then
    exit 0
  fi
fi

# Get or initialize tool call counter for this session
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
CURRENT_COUNT=$((CURRENT_COUNT + 1))

# Persist updated count
python3 -c "
import json, os
f = '$TURNS_FILE'
try:
    d = json.load(open(f)) if os.path.exists(f) else {}
except:
    d = {}
d['$SESSION_ID'] = $CURRENT_COUNT
json.dump(d, open(f, 'w'), indent=2)
" 2>/dev/null

# Read budget thresholds
MAX_CALLS=$(python3 -c "import json; d=json.load(open('$BUDGET_FILE')); print(d['session']['max_tool_calls'])" 2>/dev/null || echo "80")
WARN_CALLS=$(python3 -c "import json; d=json.load(open('$BUDGET_FILE')); print(d['session']['warn_at_tool_calls'])" 2>/dev/null || echo "60")

# Hard limit: block and log
if [ "$CURRENT_COUNT" -ge "$MAX_CALLS" ]; then
  echo "{\"ts\":\"$TS\",\"session_id\":\"$SESSION_ID\",\"event\":\"budget_halt\",\"tool\":\"$TOOL_NAME\",\"tool_call\":$CURRENT_COUNT,\"limit\":$MAX_CALLS}" >> "$EVENTS_LOG"
  echo "Tool call limit reached ($CURRENT_COUNT/$MAX_CALLS). Stop reason: max_budget_reached. Wrap up and save progress — start a new session to continue."
  exit 2
fi

# Soft limit: log warning but allow tool to fire
if [ "$CURRENT_COUNT" -ge "$WARN_CALLS" ]; then
  echo "{\"ts\":\"$TS\",\"session_id\":\"$SESSION_ID\",\"event\":\"budget_warning\",\"tool\":\"$TOOL_NAME\",\"tool_call\":$CURRENT_COUNT,\"limit\":$MAX_CALLS}" >> "$EVENTS_LOG"
fi

# Log tool_considered event
echo "{\"ts\":\"$TS\",\"session_id\":\"$SESSION_ID\",\"event\":\"tool_considered\",\"tool\":\"$TOOL_NAME\",\"tool_call\":$CURRENT_COUNT}" >> "$EVENTS_LOG"

exit 0
