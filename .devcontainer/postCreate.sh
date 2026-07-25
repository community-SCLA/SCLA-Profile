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

echo "✓ Devcontainer ready."
