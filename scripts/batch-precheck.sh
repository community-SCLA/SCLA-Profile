#!/usr/bin/env bash
# batch-precheck.sh — look at a build BEFORE spending 7 minutes rendering it.
#
# Added 2026-07-28 after the AUTO-BATCH pilot passed every static gate and still
# produced a video whose scenes were 85% blank. Deterministic gates only catch
# the bug classes someone has already met; one cheap look at real pixels catches
# the ones nobody has met yet.
#
# Renders one snapshot per scene at its midpoint (~40s for a 21-scene lesson),
# then prints a sampled spread of frame paths for a vision subagent to review.
# Also flags low-ink frames deterministically: a scene that renders only its
# background and footer compresses far smaller than one carrying real content,
# so an outlier on PNG size is a strong blank-scene signal and costs nothing.
#
# Usage:  bash scripts/batch-precheck.sh <stem> [sample-count]
# Exit:   0 gates green, frames captured  ·  3 gate failure (quarantine)  ·  2 bad args
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
STEM="${1:-}"; SAMPLE="${2:-5}"
[[ -n "$STEM" ]] || { echo "Usage: bash scripts/batch-precheck.sh <stem> [sample-count]" >&2; exit 2; }

WS="$VP/renders-hyperframes/$STEM"
[[ -d "$WS" ]] || { echo "FATAL: no workspace at $WS" >&2; exit 2; }

PIN="$(grep -o 'hyperframes@[0-9.]*' "$VP/design-system/package.json" | head -1)"
OUT="$WS/qa/precheck"

echo "== preflight (authoritative — subagent-reported exits are not trusted)"
PREFLIGHT_OUT="$(python3 "$VP/render-qa/src/preflight.py" "$WS" 2>&1)"
rc=$?
if [[ $rc -ne 0 ]]; then
  echo "PRECHECK_FAIL $STEM preflight exit=$rc" >&2
  grep -E '^\[!!' -A4 <<<"$PREFLIGHT_OUT" | head -30 >&2
  exit 3
fi
echo "   preflight exit=0"

# One snapshot per scene, at the scene's midpoint. parse_scenes is the shared
# multi-line-safe scene parser — a per-line regex scan silently misses scene
# tags that span lines.
mapfile -t TIMES < <(WS="$WS" RQ="$VP/render-qa/src" python3 - <<'PY'
import os, pathlib, sys
sys.path.insert(0, os.environ["RQ"])
from hfp_common import parse_scenes
t = pathlib.Path(os.environ["WS"], "index.html").read_text(encoding="utf-8", errors="replace")
for sc in parse_scenes(t):
    if sc["start"] == sc["start"] and sc["duration"] == sc["duration"]:  # not NaN
        print(f"{sc['start'] + sc['duration'] / 2:.2f}")
PY
)
[[ ${#TIMES[@]} -gt 0 ]] || { echo "PRECHECK_FAIL $STEM no scene clips found" >&2; exit 3; }

rm -rf "$OUT"; mkdir -p "$OUT"
echo "== snapshotting ${#TIMES[@]} scenes at their midpoints"
# --describe false: snapshot otherwise probes for a Gemini key to auto-describe
# frames. SCLA has never had one; our vision review is a subagent, not Gemini.
( cd "$WS" && npx --yes "$PIN" snapshot . \
    --at "$(IFS=,; echo "${TIMES[*]}")" --no-end --describe false -o "$OUT" ) >/dev/null 2>&1 \
  || { echo "PRECHECK_FAIL $STEM snapshot failed" >&2; exit 3; }

# Deterministic low-ink flag: blank scenes compress far smaller than real ones.
# (Advisory, not fatal: dark statement scenes legitimately compress small — the
# vision reviewer judges the flagged frames. But the check itself must run.)
OUT="$OUT" python3 - <<'PY' || { echo "PRECHECK_FAIL $STEM low-ink check crashed" >&2; exit 3; }
import os, pathlib, statistics
out = pathlib.Path(os.environ["OUT"])
pngs = sorted(p for p in out.glob("frame-*.png"))
if len(pngs) < 3:
    raise SystemExit(0)
sizes = [p.stat().st_size for p in pngs]
med = statistics.median(sizes)
# A frame under 45% of the median is almost always background + chrome only.
flagged = [(p, s) for p, s in zip(pngs, sizes) if s < med * 0.45]
print(f"   ink: median {med//1024}KB across {len(pngs)} scenes")
for p, s in flagged:
    print(f"LOWINK {p}  ({s//1024}KB vs median {med//1024}KB) — likely blank scene")
if not flagged:
    print("   ink: no blank-scene outliers")
PY

# Sampled spread for the vision reviewer.
mapfile -t FRAMES < <(SAMPLE="$SAMPLE" OUT="$OUT" python3 - <<'PY'
import os, pathlib
out = pathlib.Path(os.environ["OUT"])
f = sorted(str(p) for p in out.glob("frame-*.png"))
n = min(int(os.environ["SAMPLE"]), len(f))
if n:
    idx = [round(i * (len(f) - 1) / (n - 1)) if n > 1 else 0 for i in range(n)]
    for i in sorted(set(idx)):
        print(f[i])
PY
)

echo
echo "AWAITING_PRECHECK_VISION $STEM"
# snapshot splits into contact-sheet-N.jpg past ~9 frames, so emit whatever exists
for cs in "$OUT"/contact-sheet*.jpg; do
  [[ -e "$cs" ]] && echo "CONTACT_SHEET $cs"
done
for f in "${FRAMES[@]}"; do echo "FRAME $f"; done
echo
echo "Review these BEFORE rendering. Every scene must carry real content —"
echo "a background + footer with no heading or body copy is the blank-scene bug."
