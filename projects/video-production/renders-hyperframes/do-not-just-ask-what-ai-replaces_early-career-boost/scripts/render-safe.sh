#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
project_name="$(basename "$project_dir")"
render_fps="${SAFE_RENDER_FPS:-30}"
render_duration="${SAFE_RENDER_DURATION:-154.5}"
render_workers="${SAFE_RENDER_WORKERS:-4}"

mkdir -p "$project_dir/renders"
safe_work_dir="$(mktemp -d "$project_dir/renders/.safe-frames.XXXXXX")"
sequence_dir="$safe_work_dir/sequence"

cleanup_safe_render() {
  rm -rf -- "$safe_work_dir"
}
trap cleanup_safe_render EXIT

cd "$project_dir"
npx --yes hyperframes@0.7.79 render . \
  --fps "$render_fps" \
  --format png-sequence \
  --workers "$render_workers" \
  --no-browser-gpu \
  --output "$sequence_dir"

output_mp4="$project_dir/renders/${project_name}_$(date +%F_%H-%M-%S).mp4"
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
  "$output_mp4"

printf 'Safe PNG-sequence render complete: %s\n' "$output_mp4"
