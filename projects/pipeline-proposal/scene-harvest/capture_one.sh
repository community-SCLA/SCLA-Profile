#!/usr/bin/env bash
# Capture one still per beat for one published workspace, downscale to JPEG,
# and drop the full-size PNGs. Read-only w.r.t. tracked files: snapshots/ is
# gitignored and is removed again at the end.
set -uo pipefail
VP=/workspaces/SCLA-Profile/projects/video-production
OUT=/tmp/claude-1000/-workspaces-SCLA-Profile/e127206f-4995-4ba3-a6bb-9f1e0e42ef97/scratchpad/kit-harvest/thumbs
STEM="$1"
WS="$VP/renders-hyperframes/$STEM"
cd "$WS" || exit 2

TIMES="$(PYTHONPATH="$VP/render-qa/src" python3 - "$WS" <<'PY'
import sys
from pathlib import Path
from hfp_common import sample_units
units = sample_units(Path(sys.argv[1]))
print(",".join(f"{u['start'] + u['duration']/2:.3f}" for u in units))
PY
)"
[ -z "$TIMES" ] && { echo "SKIP $STEM no-times"; exit 3; }
N=$(awk -F, '{print NF}' <<<"$TIMES")

if [ -f package.json ]; then
  PIN="$(python3 -c "import re;m=re.findall(r'hyperframes@([0-9][0-9.]*)',open('package.json').read());print('hyperframes@'+m[-1] if m else 'hyperframes@0.7.79')")"
else
  # no pinned package.json in this workspace: fall back to the design-system pin
  PIN="$(grep -o 'hyperframes@[0-9.]*' "$VP/design-system/package.json" | head -1)"
fi

rm -rf snapshots && mkdir -p snapshots
timeout 900 npx --yes "$PIN" snapshot . --at "$TIMES" --no-end -o snapshots >"/tmp/snap-$STEM.log" 2>&1
RC=$?
GOT=$(ls snapshots/frame-*.png 2>/dev/null | wc -l)

mkdir -p "$OUT/$STEM"
python3 - "$WS/snapshots" "$OUT/$STEM" <<'PY'
import sys, re
from pathlib import Path
from PIL import Image
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
frames = sorted(src.glob("frame-*.png"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.stem)][:1] or [0])
for i, f in enumerate(frames, 1):
    im = Image.open(f).convert("RGB")
    im.thumbnail((512, 512), Image.LANCZOS)
    im.save(dst / f"{i:03d}.jpg", "JPEG", quality=72, optimize=True)
PY
JPG=$(ls "$OUT/$STEM"/*.jpg 2>/dev/null | wc -l)
rm -rf snapshots
echo "$STEM rc=$RC expected=$N png=$GOT jpg=$JPG"
