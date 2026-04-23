#!/usr/bin/env bash
# stamp-frontmatter.sh
# Ensures every markdown file in client/ has the required frontmatter block.
# Called by a PostToolUse hook in .claude/settings.json.
#
# If the file is outside client/ or already has frontmatter, exit silently.

set -euo pipefail

file="${1:-}"
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
