#!/usr/bin/env bash
# Extracts the SNAG RETRO hook command from settings.json and checks its behavior.
set -u
SETTINGS=".claude/settings.json"
HOOK=$(jq -r '.hooks.PostToolUse[].hooks[].command' "$SETTINGS" | grep 'SNAG RETRO' | head -1)
if [ -z "$HOOK" ]; then echo "FAIL: no SNAG RETRO hook found"; exit 1; fi

pass=0
# 1. render command → emits SNAG RETRO
out=$(printf '%s' '{"tool_input":{"command":"npm run render"}}' | bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && { echo "ok: render fires"; pass=$((pass+1)); } || echo "FAIL: render did not fire"
# 2. npx hyperframes render → fires
out=$(printf '%s' '{"tool_input":{"command":"npx hyperframes render"}}' | bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && { echo "ok: npx render fires"; pass=$((pass+1)); } || echo "FAIL: npx render did not fire"
# 3. word "render" in unrelated command → silent
out=$(printf '%s' '{"tool_input":{"command":"git commit -m \"render fix\""}}' | bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && echo "FAIL: false positive on word render" || { echo "ok: no false positive"; pass=$((pass+1)); }
# 4. disabled → silent even on render command
out=$(printf '%s' '{"tool_input":{"command":"npm run render"}}' | VIDEO_SNAG_RETRO_HOOK_DISABLED=1 bash -c "$HOOK")
printf '%s' "$out" | grep -q "SNAG RETRO" && echo "FAIL: fired while disabled" || { echo "ok: silent when disabled"; pass=$((pass+1)); }

echo "PASS $pass/4"
[ "$pass" -eq 4 ]
