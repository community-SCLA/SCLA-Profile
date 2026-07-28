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
# Project/env IDs come from config/endpoints.json (the registry); overridable via
#   INFISICAL_PROJECT_ID / INFISICAL_ENV.
set -euo pipefail

: "${INFISICAL_CLIENT_ID:?INFISICAL_CLIENT_ID not set (add it as a Codespaces repo secret)}"
: "${INFISICAL_SECRET_KEY:?INFISICAL_SECRET_KEY not set (add it as a Codespaces repo secret)}"

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -z "${INFISICAL_PROJECT_ID:-}" ]; then
  INFISICAL_PROJECT_ID="$(python3 -c "
import json
d = json.load(open('${_SCRIPT_DIR}/../config/endpoints.json'))
print(next(e['id'] for e in d['infisical'] if e['type'] == 'project'))
")"
fi
INFISICAL_ENV="${INFISICAL_ENV:-dev}"

if [ "$#" -eq 0 ]; then
  echo "usage: scripts/with-secrets.sh <command> [args...]" >&2
  exit 2
fi

if command -v infisical >/dev/null 2>&1; then
  # Preferred path: CLI available — log in and exec via infisical run.
  INFISICAL_TOKEN="$(infisical login --method=universal-auth \
    --client-id="$INFISICAL_CLIENT_ID" --client-secret="$INFISICAL_SECRET_KEY" \
    --silent --plain)"
  export INFISICAL_TOKEN
  exec infisical run --projectId "$INFISICAL_PROJECT_ID" --env "$INFISICAL_ENV" -- "$@"
fi

# Fallback: CLI not installed (devcontainer postCreateCommand may not have run).
# Fetch secrets via Infisical REST API and inject them as env vars before exec.
echo "infisical CLI not found — falling back to REST API injection." >&2

_token="$(curl -sf -X POST https://app.infisical.com/api/v1/auth/universal-auth/login \
  -H "Content-Type: application/json" \
  -d "{\"clientId\":\"${INFISICAL_CLIENT_ID}\",\"clientSecret\":\"${INFISICAL_SECRET_KEY}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")"

# Fetch all secrets and export them into the current env.
eval "$(curl -sf \
  "https://app.infisical.com/api/v3/secrets/raw?workspaceId=${INFISICAL_PROJECT_ID}&environment=${INFISICAL_ENV}" \
  -H "Authorization: Bearer ${_token}" \
  | python3 -c "
import sys, json, shlex
secrets = json.load(sys.stdin).get('secrets', [])
for s in secrets:
    k, v = s.get('secretKey',''), s.get('secretValue','')
    if k:
        print('export {}={}'.format(k, shlex.quote(v)))
")"

unset _token
exec "$@"
