#!/usr/bin/env bash
KH=/tmp/claude-1000/-workspaces-SCLA-Profile/e127206f-4995-4ba3-a6bb-9f1e0e42ef97/scratchpad/kit-harvest
cd /workspaces/SCLA-Profile/projects/video-production/renders-hyperframes || exit 2
: > "$KH/capture.log"
for d in */; do
  s=${d%/}
  [ -f "$s/index.html" ] || continue
  [ -d "$KH/thumbs/$s" ] && [ "$(ls "$KH/thumbs/$s" | wc -l)" -gt 0 ] && { echo "have $s" >>"$KH/capture.log"; continue; }
  "$KH/capture_one.sh" "$s" >>"$KH/capture.log" 2>&1
done
echo "DONE $(find "$KH/thumbs" -name '*.jpg' | wc -l) frames" >>"$KH/capture.log"
