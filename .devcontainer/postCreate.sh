#!/usr/bin/env bash
# postCreate.sh — runs once when the Codespace is created or rebuilt.
set -euo pipefail

echo "→ Installing ffmpeg..."
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg

echo "→ Installing Infisical CLI..."
curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo bash
sudo apt-get install -y -qq infisical

echo "→ Installing HyperFrames..."
npm install -g hyperframes

echo "→ Running repo setup (hooks + Claude settings)..."
bash scripts/setup.sh || true   # non-interactive; hooks/settings may already be wired

# brand/ must be on disk: cold refine/QA subagents read brand/voice-and-tone.md by
# relative path. When it was sparse-excluded they silently fabricated its contents
# (snag-log 2026-07-22). Only acts on an already-sparse clone; a full clone is untouched.
if [ "$(git config --get core.sparseCheckout 2>/dev/null)" = "true" ]; then
  echo "→ Ensuring brand/ is materialized in the sparse checkout..."
  git sparse-checkout add brand || true
fi

echo "✓ Devcontainer ready."
