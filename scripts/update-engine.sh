#!/usr/bin/env bash
# update-engine.sh
# Pull the latest onboarding "engine" (.claude/, templates/, scripts/) from
# the template repo, WITHOUT touching client data.
#
# Run this inside a client repo whenever the template gets improvements
# you want to adopt.
#
# Configuration:
#   UPSTREAM_TEMPLATE_URL   HTTPS or SSH URL to the template repo
#                           (default: https://github.com/community-scla/scla-profile)
#   UPSTREAM_BRANCH         Branch to pull from (default: main)
#
# Safety:
#   - Never touches client/** or client.config.yml
#   - Leaves your working tree dirty for you to review + commit

set -euo pipefail

UPSTREAM="${UPSTREAM_TEMPLATE_URL:-https://github.com/community-scla/scla-profile}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-main}"

# Engine paths we sync (everything else — including client/ — is left alone)
ENGINE_DIRS=( ".claude" "templates" "scripts" "docs" )
ENGINE_FILES=( "CLAUDE.md" "TEMPLATE.md" ".gitignore" )

# ───────────────────────────────────────────────────────────────────────────
# Sanity checks
# ───────────────────────────────────────────────────────────────────────────
if ! command -v git >/dev/null; then
  echo "❌ git is required" >&2; exit 1
fi
if ! command -v rsync >/dev/null; then
  echo "❌ rsync is required" >&2; exit 1
fi
if [[ ! -d .git ]]; then
  echo "❌ Run this from the root of a client repo (.git not found)" >&2; exit 1
fi

# Refuse to run if this IS the template repo (avoid self-sync)
if [[ -f TEMPLATE.md ]] && grep -q "This is the Template Repo" TEMPLATE.md 2>/dev/null; then
  remote_url="$(git config --get remote.origin.url 2>/dev/null || true)"
  if [[ "$remote_url" == *"scla-profile"* || "$remote_url" == *"client-onboarding"* ]]; then
    echo "⚠️  This appears to be the template repo itself. Nothing to do." >&2
    exit 0
  fi
fi

echo "🔄 Updating engine from: $UPSTREAM ($UPSTREAM_BRANCH)"
echo ""

# ───────────────────────────────────────────────────────────────────────────
# Clone upstream shallow to a temp dir
# ───────────────────────────────────────────────────────────────────────────
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git clone --depth 1 --branch "$UPSTREAM_BRANCH" "$UPSTREAM" "$tmp/upstream" 2>&1 \
  | sed 's/^/  /'

# ───────────────────────────────────────────────────────────────────────────
# Sync engine directories
# ───────────────────────────────────────────────────────────────────────────
for dir in "${ENGINE_DIRS[@]}"; do
  if [[ -d "$tmp/upstream/$dir" ]]; then
    echo "  📁 $dir/"
    mkdir -p "$dir"
    rsync -a --delete "$tmp/upstream/$dir/" "./$dir/"
  fi
done

# ───────────────────────────────────────────────────────────────────────────
# Sync engine files (README.md is deliberately NOT synced — clients may
# customize their top-level README.)
# ───────────────────────────────────────────────────────────────────────────
for file in "${ENGINE_FILES[@]}"; do
  if [[ -f "$tmp/upstream/$file" ]]; then
    echo "  📄 $file"
    cp "$tmp/upstream/$file" "./$file"
  fi
done

# ───────────────────────────────────────────────────────────────────────────
# Summary
# ───────────────────────────────────────────────────────────────────────────
echo ""
echo "✅ Engine sync complete."
echo ""

if git diff --quiet && git diff --cached --quiet; then
  echo "   No changes — you're already up to date."
else
  echo "   Review changes:"
  echo "     git status"
  echo "     git diff"
  echo ""
  echo "   Commit when ready:"
  echo "     git add .claude templates scripts docs CLAUDE.md TEMPLATE.md .gitignore"
  echo "     git commit -m 'chore: sync onboarding engine from upstream template'"
fi
