#!/usr/bin/env bash
# Production TTS wrapper: pin provider/voice/speed, then invoke the shared engine.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
WS="${1:-}"
[[ -n "$WS" ]] || { echo "usage: video-audio.sh <workspace>" >&2; exit 2; }
[[ "$WS" = /* ]] || WS="$REPO/$WS"
[[ -f "$WS/audio_request.json" ]] || { echo "FATAL: no audio_request.json in $WS" >&2; exit 2; }

python3 "$VP/render-qa/src/prepare_audio.py" "$WS"
bash "$REPO/scripts/with-secrets.sh" node \
  "$REPO/.claude/skills/hyperframes-media/scripts/audio.mjs" \
  --request "$WS/audio_request.json" --hyperframes "$WS" --out "$WS/audio_meta.json"
python3 "$VP/render-qa/src/prepare_audio.py" "$WS" --stamp-meta
python3 "$VP/render-qa/src/prepare_audio.py" "$WS" --check
