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
python3 "$VP/render-qa/preflight.py" "$WS" >/dev/null 2>&1
rc=$?
if [[ $rc -ne 0 ]]; then
  echo "PRECHECK_FAIL $STEM preflight exit=$rc" >&2
  python3 "$VP/render-qa/preflight.py" "$WS" 2>&1 | grep -E '^\[!!' -A4 | head -30 >&2
  exit 3
fi
echo "   preflight exit=0"

# One snapshot per scene, at the scene's midpoint.
mapfile -t TIMES < <(WS="$WS" python3 - <<'PY'
import os, re, pathlib
t = pathlib.Path(os.environ["WS"], "index.html").read_text(encoding="utf-8", errors="replace")
for line in t.splitlines():
    if 'class="clip"' not in line or 'data-composition-src' not in line:
        continue
    s = re.search(r'data-start="([0-9.]+)"', line)
    d = re.search(r'data-duration="([0-9.]+)"', line)
    if s and d:
        print(f"{float(s.group(1)) + float(d.group(1)) / 2:.2f}")
PY
)
[[ ${#TIMES[@]} -gt 0 ]] || { echo "PRECHECK_FAIL $STEM no scene clips found" >&2; exit 3; }

rm -rf "$OUT"; mkdir -p "$OUT"
echo "== snapshotting ${#TIMES[@]} scenes at their midpoints"
( cd "$WS" && npx --yes "$PIN" snapshot . \
    --at "$(IFS=,; echo "${TIMES[*]}")" --no-end -o "$OUT" ) >/dev/null 2>&1 \
  || { echo "PRECHECK_FAIL $STEM snapshot failed" >&2; exit 3; }

# Deterministic low-ink flag: blank scenes compress far smaller than real ones.
OUT="$OUT" python3 - <<'PY'
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
