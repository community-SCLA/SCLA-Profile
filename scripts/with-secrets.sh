#!/usr/bin/env bash
# Run a command with Infisical secrets injected into its environment.
#
# Infisical is the SOURCE OF TRUTH for all secrets. Secrets are injected at
# runtime via `infisical run` and are NEVER written to .env, the repo, or any
# file on disk. Do not add an `infisical export` path here.
#
# Usage:   scripts/with-secrets.sh <command> [args...]
# Example: scripts/with-secrets.sh curl -H "Authorization: Bearer $WISTIA_API" ...
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

# REST API injection is the ONLY path (2026-07-28). The `infisical` CLI is not
# installed in this Codespace — the devcontainer's apt install never survived —
# so the CLI branch was dead code that only ever emitted a "falling back"
# warning on stderr. In a 30-video batch that warning fired on every TTS and
# every upload, so it went too. Re-add a CLI branch only if the CLI is actually
# provisioned; REST is equivalent and equally never writes secrets to disk.
# --retry only (no --retry-all-errors: system curl is 7.68, flag needs >=7.71
# — an unknown flag makes curl exit 2 BEFORE any request, snag 2026-07-28).
_token="$(curl -sf --retry 3 --max-time 60 --connect-timeout 15 \
  -X POST https://app.infisical.com/api/v1/auth/universal-auth/login \
  -H "Content-Type: application/json" \
  -d "{\"clientId\":\"${INFISICAL_CLIENT_ID}\",\"clientSecret\":\"${INFISICAL_SECRET_KEY}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")"

# Fetch all secrets and export them into the current env.
eval "$(curl -sf --retry 3 --max-time 60 --connect-timeout 15 \
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
