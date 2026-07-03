#!/usr/bin/env bash
# Usage: ./new-grant.sh <short-name>
# Example: ./new-grant.sh niche-foundation
#
# Creates a dated grant application file from the project template.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEMPLATE="$REPO_ROOT/templates/project-grant.md"
GRANTS_DIR="$SCRIPT_DIR"

if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: $0 <short-name>" >&2
  echo "  Example: $0 niche-foundation" >&2
  exit 1
fi

NAME="$1"
TODAY="$(date +%Y-%m-%d)"
OUTPUT="$GRANTS_DIR/${TODAY}-${NAME}.md"

if [[ -f "$OUTPUT" ]]; then
  echo "File already exists: $OUTPUT" >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "Template not found: $TEMPLATE" >&2
  exit 1
fi

cp "$TEMPLATE" "$OUTPUT"

# Fill in frontmatter dates and reset status
sed -i '' \
  -e "s/created: YYYY-MM-DD/created: $TODAY/" \
  -e "s/last_updated: YYYY-MM-DD/last_updated: $TODAY/" \
  "$OUTPUT"

echo "Created: $OUTPUT"
