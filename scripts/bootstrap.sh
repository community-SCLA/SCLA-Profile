#!/usr/bin/env bash
# bootstrap.sh
# Clone this template into a fresh per-client repo.
#
# Usage:
#   ./scripts/bootstrap.sh <client-slug>           # creates ../<client-slug>-onboarding/
#   ./scripts/bootstrap.sh <client-slug> <target>  # creates at <target>/

set -euo pipefail

slug="${1:-}"
if [[ -z "$slug" ]]; then
  cat <<EOF
Usage: $0 <client-slug> [target-dir]

Example:
  $0 acme-corp
    → creates ../acme-corp-onboarding/
EOF
  exit 1
fi

target="${2:-../${slug}-onboarding}"

if [[ -e "$target" ]]; then
  echo "❌ $target already exists — refusing to overwrite." >&2
  exit 1
fi

template_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "📦 Cloning template to $target ..."
mkdir -p "$target"

# Copy everything except .git, node_modules, and any previously generated client/ content
# we want to start empty.
rsync -a \
  --exclude '.git' \
  --exclude 'node_modules' \
  --exclude 'client/_raw/web/*' \
  --exclude 'client/_raw/docs/inbox/_processed/*' \
  --exclude 'client/_raw/artifacts/inbox/_processed/*' \
  --exclude 'client/brand/brand-guide.md' \
  --exclude 'client/brand/voice-and-tone.md' \
  --exclude 'client/brand/visual-identity.md' \
  --exclude 'client/knowledge-base/*.md' \
  --exclude 'client/workflows/*.md' \
  --exclude 'client/source-of-truth/*.md' \
  --exclude 'client/source-of-truth/.source-of-truth-generated' \
  "${template_root}/" "${target}/"

# Re-stamp client.config.yml with the slug so the human only needs to fill in the rest.
cfg="${target}/client.config.yml"
if [[ -f "$cfg" ]]; then
  # Portable sed -i across GNU/BSD
  if sed --version >/dev/null 2>&1; then
    sed -i "s/<client-slug>/${slug}/g" "$cfg"
  else
    sed -i '' "s/<client-slug>/${slug}/g" "$cfg"
  fi
fi

# Initialize fresh git repo
( cd "$target" && git init -q && git add -A && git commit -q -m "chore: bootstrap ${slug} from client-onboarding-template" )

cat <<EOF

✅ Bootstrapped $target

Next steps:
  cd $target
  \$EDITOR client.config.yml     # fill in client.name, sources, team…
  # then open Claude Code here and run:
  /onboard
EOF
