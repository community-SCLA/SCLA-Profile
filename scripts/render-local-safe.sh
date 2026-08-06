#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: render-local-safe.sh WORKSPACE" >&2
  exit 2
fi

workspace="$(cd "$1" && pwd)"
project_name="$(basename "$workspace")"
render_fps="${SCLA_RENDER_FPS:-30}"
render_workers="${SCLA_RENDER_WORKERS:-4}"

mkdir -p "$workspace/renders"
safe_work_dir="$(mktemp -d "$workspace/renders/.safe-frames.XXXXXX")"
sequence_dir="$safe_work_dir/sequence"

cleanup_safe_render() {
  rm -rf -- "$safe_work_dir"
}
trap cleanup_safe_render EXIT

cd "$workspace"
npm run render -- . \
  --fps "$render_fps" \
  --format png-sequence \
  --workers "$render_workers" \
  --no-browser-gpu \
  --output "$sequence_dir"

frame_count="$(printf '%s\n' "$sequence_dir"/frame_*.png | wc -l)"
if [[ "$frame_count" -lt 1 || ! -f "$sequence_dir/frame_000001.png" ]]; then
  echo "safe local render produced no PNG frames" >&2
  exit 1
fi
render_duration="$(awk -v frames="$frame_count" -v fps="$render_fps" 'BEGIN { printf "%.6f", frames / fps }')"
encoded_mp4="$safe_work_dir/${project_name}.mp4"
output_mp4="$workspace/renders/${project_name}_$(date +%F_%H-%M-%S).mp4"

if [[ -s "$sequence_dir/audio.aac" ]]; then
  ffmpeg -hide_banner -loglevel error -y \
    -framerate "$render_fps" \
    -start_number 1 \
    -i "$sequence_dir/frame_%06d.png" \
    -i "$sequence_dir/audio.aac" \
    -c:v libx264 \
    -preset veryfast \
    -crf 17 \
    -pix_fmt yuv420p \
    -af apad \
    -c:a aac \
    -b:a 192k \
    -movflags +faststart \
    -t "$render_duration" \
    "$encoded_mp4"
else
  ffmpeg -hide_banner -loglevel error -y \
    -framerate "$render_fps" \
    -start_number 1 \
    -i "$sequence_dir/frame_%06d.png" \
    -c:v libx264 \
    -preset veryfast \
    -crf 17 \
    -pix_fmt yuv420p \
    -movflags +faststart \
    -t "$render_duration" \
    "$encoded_mp4"
fi

# Keep the delivery directory free of half-written MP4s. The run driver may
# normalize timestamped outputs as soon as they appear there, which races with
# FFmpeg's faststart second pass if encoding happens in-place.
mv "$encoded_mp4" "$output_mp4"

printf 'Safe local render complete: %s (%s frames, %ss)\n' \
  "$output_mp4" "$frame_count" "$render_duration"
