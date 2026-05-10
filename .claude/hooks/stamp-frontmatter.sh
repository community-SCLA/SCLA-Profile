#!/usr/bin/env bash
# stamp-frontmatter.sh
# C1: Validates that every markdown file written to scla/ (excluding _raw/)
# has fully-filled frontmatter. Injects stubs if missing; warns loudly if
# required fields contain placeholder values.
#
# Claude Code passes a JSON payload on stdin describing the tool call.

set -euo pipefail

payload="$(cat || true)"
[[ -z "$payload" ]] && exit 0

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
[[ "$file" != *scla/* ]] && exit 0
[[ "$file" != *.md ]] && exit 0
[[ "$file" == *_raw/* ]] && exit 0
[[ "$file" == *source-of-truth/PROPOSED_CHANGES* ]] && exit 0

today="$(date +%Y-%m-%d)"

# If no frontmatter at all — inject stubs
if ! head -1 "$file" | grep -q '^---$'; then
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
  echo "⚠️  FRONTMATTER: Injected stub frontmatter into ${file}. Fill in source, generated_by, and confidence before committing." >&2
  exit 0
fi

# Frontmatter exists — validate required fields are not placeholders
has_todo_source=false
has_unknown_generated_by=false

if grep -q '^source: TODO' "$file"; then
  has_todo_source=true
fi
if grep -q '^generated_by: unknown' "$file"; then
  has_unknown_generated_by=true
fi

if $has_todo_source || $has_unknown_generated_by; then
  echo "" >&2
  echo "🚫 FRONTMATTER VALIDATION FAILED: ${file}" >&2
  echo "   The following required fields are still placeholders:" >&2
  $has_todo_source && echo "   - source: TODO  →  replace with the source URL or _raw/ path" >&2
  $has_unknown_generated_by && echo "   - generated_by: unknown  →  replace with the agent name (e.g. brand-analyst)" >&2
  echo "   Fix these before committing." >&2
  echo "" >&2
fi
