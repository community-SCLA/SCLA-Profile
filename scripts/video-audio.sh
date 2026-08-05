#!/usr/bin/env bash
# Production TTS wrapper: pin provider/voice/speed, batch narration into one
# normal provider request, meter paid calls globally, then restore beat clips.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
WS="${1:-}"
[[ -n "$WS" ]] || { echo "usage: video-audio.sh <workspace>" >&2; exit 2; }
[[ "$WS" = /* ]] || WS="$REPO/$WS"
[[ -f "$WS/audio_request.json" ]] || { echo "FATAL: no audio_request.json in $WS" >&2; exit 2; }

python3 "$VP/render-qa/src/prepare_audio.py" "$WS"
STATE="$VP/render-qa/src/run_state.py"
CONTINUOUS="$VP/render-qa/src/continuous_audio.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PROVIDER_REQUEST="$TMP/audio_request.json"
PROVIDER_META="$TMP/audio_meta.json"
MAX_CHARS="${VIDEO_TTS_MAX_CHARS:-4800}"
TTS_LIMIT="${VIDEO_TTS_CONCURRENCY:-$(python3 "$STATE" tts-concurrency 2>/dev/null || echo 2)}"
RETRIES="${VIDEO_TTS_RETRIES:-3}"
BACKOFF="${VIDEO_TTS_BACKOFF_SECONDS:-3}"

python3 "$CONTINUOUS" prepare "$WS" "$PROVIDER_REQUEST" --max-chars "$MAX_CHARS"

SUCCESS=0
for ((attempt = 1; attempt <= RETRIES; attempt++)); do
  rm -f "$PROVIDER_META"
  echo "== production TTS attempt $attempt/$RETRIES (global capacity $TTS_LIMIT)"
  if HYPERFRAMES_TTS_CONCURRENCY=1 \
    bash "$REPO/scripts/with-capacity.sh" tts "$TTS_LIMIT" -- \
    bash "$REPO/scripts/with-secrets.sh" node \
      "$REPO/.claude/skills/hyperframes-media/scripts/audio.mjs" \
      --request "$PROVIDER_REQUEST" --hyperframes "$WS" --out "$PROVIDER_META" \
      --only tts,bgm \
    && python3 "$CONTINUOUS" split "$WS" "$PROVIDER_META" --max-chars "$MAX_CHARS"; then
    SUCCESS=1
    break
  fi
  if (( attempt < RETRIES )); then
    DELAY=$((BACKOFF * (2 ** (attempt - 1))))
    echo "   transient TTS failure; retrying in ${DELAY}s" >&2
    sleep "$DELAY"
  fi
done
[[ "$SUCCESS" == "1" ]] || { echo "FATAL: production TTS failed after $RETRIES attempts" >&2; exit 1; }

python3 "$VP/render-qa/src/prepare_audio.py" "$WS" --stamp-meta
python3 "$VP/render-qa/src/prepare_audio.py" "$WS" --check
