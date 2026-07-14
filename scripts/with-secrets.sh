#!/usr/bin/env bash
# Run a command with Infisical secrets injected into its environment.
#
# Infisical is the SOURCE OF TRUTH for all secrets. Secrets are injected at
# runtime via `infisical run` and are NEVER written to .env, the repo, or any
# file on disk. Do not add an `infisical export` path here.
#
# Usage:   scripts/with-secrets.sh <command> [args...]
# Example: scripts/with-secrets.sh curl -H "Authorization: Bearer $WISTIA_API_TOKEN" ...
#
# Auth: machine identity (universal-auth) via Codespaces repo secrets
#   INFISICAL_CLIENT_ID + INFISICAL_SECRET_KEY.
# Project/env IDs are registered in endpoints.md → "Infisical"; overridable via
#   INFISICAL_PROJECT_ID / INFISICAL_ENV.
set -euo pipefail

: "${INFISICAL_CLIENT_ID:?INFISICAL_CLIENT_ID not set (add it as a Codespaces repo secret)}"
: "${INFISICAL_SECRET_KEY:?INFISICAL_SECRET_KEY not set (add it as a Codespaces repo secret)}"

INFISICAL_PROJECT_ID="${INFISICAL_PROJECT_ID:-eea9b546-3f30-45d8-a9b9-a6ede93e3a71}"  # scla-projects-n-joy (endpoints.md)
INFISICAL_ENV="${INFISICAL_ENV:-dev}"

if ! command -v infisical >/dev/null 2>&1; then
  echo "infisical CLI not installed — it is provisioned by .devcontainer/devcontainer.json (postCreateCommand)." >&2
  exit 127
fi

if [ "$#" -eq 0 ]; then
  echo "usage: scripts/with-secrets.sh <command> [args...]" >&2
  exit 2
fi

# Log in with the machine identity; the token stays in this process's env only.
INFISICAL_TOKEN="$(infisical login --method=universal-auth \
  --client-id="$INFISICAL_CLIENT_ID" --client-secret="$INFISICAL_SECRET_KEY" \
  --silent --plain)"
export INFISICAL_TOKEN

exec infisical run --projectId "$INFISICAL_PROJECT_ID" --env "$INFISICAL_ENV" -- "$@"
