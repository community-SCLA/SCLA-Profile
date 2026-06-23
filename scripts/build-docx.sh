#!/bin/bash
# build-docx.sh — Convert curated scla/ Markdown into .docx for the Git→Drive mirror.
#
# Walks scla/**/*.md, strips YAML frontmatter, and runs pandoc to produce a parallel
# tree of .docx files under build/ (same relative paths). The drive-sync GitHub Action
# then rclone-syncs build/ into Google Drive, where each .docx is imported as a native
# Google Doc. See references/google-drive-api.md and .github/workflows/drive-sync.yml.
#
# Usage:  scripts/build-docx.sh [SRC_DIR] [OUT_DIR]
#   SRC_DIR  directory to scan for .md (default: scla)
#   OUT_DIR  directory to write .docx into (default: build)
#
# Requires: pandoc.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${1:-scla}"
OUT_DIR="${2:-build}"

cd "$SCRIPT_DIR"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "❌ pandoc not found — install it (apt-get install -y pandoc) before running." >&2
  exit 1
fi

count=0
# -print0 / read -d '' so paths with spaces (common in this repo) survive intact.
while IFS= read -r -d '' md; do
  rel="${md#"$SRC_DIR"/}"           # path relative to SRC_DIR
  out="$OUT_DIR/${rel%.md}.docx"    # mirror structure, swap extension
  mkdir -p "$(dirname "$out")"
  # standalone so headings/lists/tables map to real Doc structure; frontmatter is
  # parsed as metadata by pandoc's markdown reader (title only) and not rendered inline.
  pandoc "$md" --from markdown --to docx --standalone --output "$out"
  count=$((count + 1))
done < <(find "$SRC_DIR" -type f -name '*.md' -print0)

echo "✅ Converted $count Markdown file(s) from $SRC_DIR/ into $OUT_DIR/"
