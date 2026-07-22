#!/usr/bin/env bash
# wistia-upload.sh — headless upload of a filed lesson MP4 to Wistia.
#
# Proven end to end via ad-hoc curl (render-qa/snag-log.md 2026-07-15,
# 2026-07-22): the WISTIA_API token in Infisical is read+write (not delete)
# and the upload API returns 200 + hashed_id with no web-UI step. This script
# is the reusable form of that call, wired into /render-lessons SHIP.
#
# Usage:   bash scripts/wistia-upload.sh <mp4-path> <program-slug> [title]
# Example: bash scripts/wistia-upload.sh \
#            renders-mp4/early-career-boost/hyperframes/foo_2026-07-22.mp4 \
#            early-career-boost
#
# Project IDs (endpoints.md -> "Wistia"): only Early Career Boost has one
# filed today. Unmapped programs upload to the Wistia account's default
# project — add a case below once a program's project id is confirmed and
# recorded in endpoints.md.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

MP4="${1:-}"
PROGRAM_SLUG="${2:-}"
TITLE="${3:-}"

if [[ -z "$MP4" || -z "$PROGRAM_SLUG" ]]; then
  echo "Usage: bash scripts/wistia-upload.sh <mp4-path> <program-slug> [title]" >&2
  exit 2
fi

[[ -f "$MP4" ]] || { echo "No file at $MP4" >&2; exit 1; }

if [[ -z "$TITLE" ]]; then
  TITLE="$(basename "$MP4" .mp4)"
fi

PROJECT_ID=""
case "$PROGRAM_SLUG" in
  early-career-boost) PROJECT_ID="10733647" ;;
  *) echo "No Wistia project id mapped for '$PROGRAM_SLUG' — uploading to account default project. Add its id to endpoints.md and this script once known." >&2 ;;
esac

CURL_ARGS=(-sS -F "name=$TITLE" -F "file=@$MP4")
[[ -n "$PROJECT_ID" ]] && CURL_ARGS+=(-F "project_id=$PROJECT_ID")

RESPONSE="$("$REPO_ROOT/scripts/with-secrets.sh" bash -c '
  curl -sS -F "api_password=$WISTIA_API" "$@" https://upload.wistia.com/
' _ "${CURL_ARGS[@]}")"

HASHED_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("hashed_id",""))' <<<"$RESPONSE" 2>/dev/null || true)"

if [[ -z "$HASHED_ID" ]]; then
  echo "Upload failed or no hashed_id in response:" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

echo "Uploaded: $TITLE"
echo "hashed_id: $HASHED_ID"
echo "Share URL:  https://sclc.wistia.com/medias/$HASHED_ID"
echo "Embed URL:  https://fast.wistia.net/embed/iframe/$HASHED_ID"
