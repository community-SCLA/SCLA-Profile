#!/bin/bash
# setup.sh — optional one-command tool installer for kwoekel-ops-template
# Run once after /onboard if you want Claude Code hooks and settings wired up.
# Safe to re-run.
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setting up ops repo — please wait...   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Copy hook scripts to ~/.claude/hooks/ ──────────────────────────────────
echo "→ Installing Claude Code hooks..."
mkdir -p "$HOME/.claude/hooks"
EXISTING=$(ls "$HOME/.claude/hooks/" 2>/dev/null | wc -l | tr -d ' ')
TEMPLATE_HOOKS=$(ls "$REPO_DIR/hooks/" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$EXISTING" -gt 0 ]]; then
  echo "  ⚠️  ~/.claude/hooks/ already has $EXISTING file(s). This will overwrite any with matching names."
  read -r -p "  Continue? [y/N] " _confirm
  if [[ "$_confirm" != "y" && "$_confirm" != "Y" ]]; then
    echo "  Skipped hook installation. Copy manually from $REPO_DIR/hooks/ if needed."
    SKIP_HOOKS=1
  fi
fi
if [[ -z "$SKIP_HOOKS" ]]; then
  cp -f "$REPO_DIR/hooks/"* "$HOME/.claude/hooks/" 2>/dev/null || true
  echo "  ✅ Hooks copied to ~/.claude/hooks/ ($TEMPLATE_HOOKS files)"
fi
# Restore real $HOME path in any hooks that use the __HOME_DIR__ placeholder
find "$HOME/.claude/hooks" -type f -exec \
  sed -i "" "s|__HOME_DIR__|$HOME|g" {} \; 2>/dev/null || \
  find "$HOME/.claude/hooks" -type f -exec \
    sed -i "s|__HOME_DIR__|$HOME|g" {} \; 2>/dev/null || true

# ── 2. Register hooks + safety rules in ~/.claude/settings.json ───────────────
echo "→ Updating global Claude settings..."
python3 "$REPO_DIR/scripts/merge-settings.py"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setup complete!                        ║"
echo "╠══════════════════════════════════════════╣"
echo "║  Hooks and settings are wired up.       ║"
echo "║  Next step — run /onboard in Claude     ║"
echo "║  Code to personalize your repo.         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
