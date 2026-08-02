#!/usr/bin/env bash
# setup-ringer.sh — make this machine able to run Ringer swarms on Claude.
#
# Idempotent and safe to re-run: every step checks before it acts, and nothing
# here is destructive without --force. Called by .devcontainer/devcontainer.json
# on container create, and runnable by hand any time something looks missing.
#
#   bash scripts/setup-ringer.sh            # install anything absent, touch nothing else
#   bash scripts/setup-ringer.sh --force    # also overwrite an existing engine config
#
# What a Codespace rebuild destroys, and this script rebuilds:
#   ~/.config/ringer/config.toml   the engine config (plain $HOME — not persisted)
#   the global `claude` CLI        under ~/nvm (plain $HOME — not persisted)
# What it does NOT rebuild, because those survive on their own:
#   /workspaces/ringer             the clone (/workspaces persists across rebuild)
#   ~/.claude/settings.json        a symlink into /workspaces/.codespaces/.persistedshare
# A brand-new Codespace has neither, so the clone step below runs then.

set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLONE="/workspaces/ringer"
CONF_DIR="$HOME/.config/ringer"
CONF="$CONF_DIR/config.toml"
SRC="$REPO/config/ringer-engines.toml"
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

say()  { echo "  -> $*"; }
skip() { echo "  ok: $*"; }

echo "setup-ringer: preparing Claude-powered swarm delegation"

# ── 1. The Ringer clone — a sibling of this repo, never inside it ─────────────
# Nested, sync.sh's `git add -A` would stage it as a bare gitlink with no
# .gitmodules and clones would get an empty directory (decisions/log.md,
# 2026-08-02). .gitignore keeps a `ringer/` rule as a guard against that.
if [ -d "$CLONE/.git" ]; then
  skip "clone present at $CLONE"
else
  say "cloning Ringer to $CLONE"
  git clone https://github.com/NateBJones-Projects/ringer "$CLONE" || {
    echo "WARN: clone failed — run it by hand, then re-run this script"; }
fi

# ── 2. The Claude Code CLI — the worker engine ───────────────────────────────
# Auth is deliberately NOT automated: `claude` signs in through a browser OAuth
# flow tied to the user's own account. A script cannot and should not do that.
if command -v claude >/dev/null 2>&1; then
  skip "claude CLI present ($(claude --version 2>/dev/null | head -1))"
else
  say "installing the Claude Code CLI"
  npm install -g @anthropic-ai/claude-code || {
    echo "WARN: npm install failed — install by hand: npm install -g @anthropic-ai/claude-code"; }
  echo "  NOTE: run \`claude\` once and sign in before the first swarm."
fi

# ── 3. The engine config — the part a rebuild actually eats ──────────────────
mkdir -p "$CONF_DIR"
if [ -f "$CONF" ] && [ "$FORCE" -eq 0 ]; then
  if cmp -s "$SRC" "$CONF"; then
    skip "engine config already matches config/ringer-engines.toml"
  else
    echo "  ok: engine config exists and differs from the repo copy — left alone."
    echo "      Diff it:      diff $SRC $CONF"
    echo "      Repo wins:    bash scripts/setup-ringer.sh --force"
    echo "      Machine wins: cp $CONF $SRC   (then commit)"
  fi
else
  say "installing $SRC -> $CONF"
  cp "$SRC" "$CONF"
fi

# ── 4. Swarm identity — must sit at the repo ROOT ────────────────────────────
# Ringer walks UP from the worker's directory looking for .fleet-agent, so a copy
# under config/ would never be found. A deliberate exception to the closed-root
# convention, recorded in decisions/log.md (2026-08-02).
if [ -f "$REPO/.fleet-agent" ]; then
  skip "swarm identity: $(cat "$REPO/.fleet-agent")"
else
  say "writing repo-root swarm identity (.fleet-agent)"
  echo "scla-profile" > "$REPO/.fleet-agent"
fi

echo "setup-ringer: done."
echo "  Check a manifest before running it:  python3 $CLONE/ringer.py lint <manifest.json>"
