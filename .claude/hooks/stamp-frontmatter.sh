#!/usr/bin/env bash
# stamp-frontmatter.sh
# Ensures every markdown file in client/ has the required frontmatter block.
# Called by a PostToolUse hook in .claude/settings.json.
#
# Claude Code passes a JSON payload on stdin describing the tool call. We
# extract tool_input.file_path from it. If the file is outside client/,
# inside _raw/, not markdown, or already has frontmatter — exit silently.

set -euo pipefail

# Read the hook payload from stdin (Claude Code contract).
payload="$(cat || true)"
[[ -z "$payload" ]] && exit 0

# Prefer jq; fall back to a grep-based extractor if jq is unavailable.
file=""
if command -v jq >/dev/null 2>&1; then
  file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty')"
else
  file="$(printf '%s' "$payload" \
    | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]+"' \
    | head -n1 \
    | sed -E 's/.*"file_path"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')"
fi

[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0
[[ "$file" != *client/* ]] && exit 0
[[ "$file" != *.md ]] && exit 0
[[ "$file" == *_raw/* ]] && exit 0

# Already has frontmatter?
if head -1 "$file" | grep -q '^---$'; then
  exit 0
fi

today="$(date +%Y-%m-%d)"
tmp="$(mktemp)"
{
  echo "---"
  echo "source: TODO"
  echo "generated_by: unknown"
  echo "last_updated: ${today}"
  echo "confidence: low"
  echo "---"
  echo ""
  cat "$file"
} > "$tmp"
mv "$tmp" "$file"
