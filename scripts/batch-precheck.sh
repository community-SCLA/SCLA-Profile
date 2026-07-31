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

# Snapshot times. Two grids, because two questions need different densities:
#
#   template lane — one frame per scene midpoint, as it has always been. The
#     freeze question is answered upstream and for free by preflight check 6
#     (check_pacing), from the compiled cue list.
#
#   freeform lane — check_pacing is SKIPPED there and cannot be ported (its
#     input is the compiler's private cue protocol). So the grid becomes uniform
#     and dense enough for check_diversity to measure a freeze: ~1.25s, which is
#     STAGNANT_FAIL/4. That costs ~120 stills instead of ~5 on a 150s lesson and
#     is the whole point — on 2026-07-31 a freeform cut passed this precheck on 5
#     stills, passed a human preview, and was then blocked post-render by three
#     5s frozen spans that nothing upstream had been looking for.
#
# sample_units (not parse_scenes) is the beat grid: a freeform clip is an ACT,
# so per-clip sampling starves every sampler — 26 beats collapse to 5 stills.
#
# The lane is decided ONCE, here, and read back as a flag. It was briefly
# inferred downstream from "more than 5 snapshot times", which every template
# lesson also satisfies (~27 scenes) — that would have run the dense-grid gate
# against a sparse per-scene grid and hard-failed the entire template lane on
# grid-too-sparse. A lane is a fact to be read, never a count to be guessed at.
FREEFORM="$(WS="$WS" RQ="$VP/render-qa/src" python3 - <<'PY'
import os, pathlib, sys
sys.path.insert(0, os.environ["RQ"])
from hfp_common import parse_scenes
html = pathlib.Path(os.environ["WS"], "index.html").read_text(
    encoding="utf-8", errors="replace")
print("0" if any(s["narration"] is not None for s in parse_scenes(html)) else "1")
PY
)"
[[ "$FREEFORM" == "0" || "$FREEFORM" == "1" ]] \
  || { echo "PRECHECK_FAIL $STEM could not determine lane" >&2; exit 3; }

mapfile -t TIMES < <(FREEFORM="$FREEFORM" WS="$WS" RQ="$VP/render-qa/src" python3 - <<'PY'
import os, pathlib, sys
sys.path.insert(0, os.environ["RQ"])
from hfp_common import parse_scenes, sample_units
from check_diversity import MAX_SAMPLE_GAP

ws = pathlib.Path(os.environ["WS"])
html = (ws / "index.html").read_text(encoding="utf-8", errors="replace")
units = sample_units(ws)
freeform = os.environ["FREEFORM"] == "1"

if not freeform:
    for u in units:
        print(f"{u['start'] + u['duration'] / 2:.2f}\t{u['id']}")
else:
    end = max((u["start"] + u["duration"] for u in units), default=0.0)
    # Label every sample with the beat containing it, so check_diversity's
    # twin-beats rule has a beat to group by instead of one "beat" per still.
    def beat_at(t):
        for u in units:
            if u["start"] <= t < u["start"] + u["duration"]:
                return u["id"]
        return units[-1]["id"] if units else "s00"
    # Start half an interval in, not at 0.0: t=0 is the pre-roll frame before
    # the opening beat has animated anything, so it is legitimately dim and
    # tripped the LOWINK blank-scene flag on every single freeform run. A flag
    # that always fires is a flag people learn to skip past.
    t = MAX_SAMPLE_GAP / 2.0
    while t < end:
        print(f"{t:.2f}\t{beat_at(t)}")
        t += MAX_SAMPLE_GAP
PY
)
[[ ${#TIMES[@]} -gt 0 ]] || { echo "PRECHECK_FAIL $STEM no beats found" >&2; exit 3; }
# Split the tab-separated grid into parallel arrays.
AT=(); BEAT=()
for row in "${TIMES[@]}"; do AT+=("${row%%$'\t'*}"); BEAT+=("${row##*$'\t'}"); done

rm -rf "$OUT"; mkdir -p "$OUT"
echo "== snapshotting ${#AT[@]} frame(s)"
# --describe false: snapshot otherwise probes for a Gemini key to auto-describe
# frames. SCLA has never had one; our vision review is a subagent, not Gemini.
( cd "$WS" && npx --yes "$PIN" snapshot . \
    --at "$(IFS=,; echo "${AT[*]}")" --no-end --describe false -o "$OUT" ) >/dev/null 2>&1 \
  || { echo "PRECHECK_FAIL $STEM snapshot failed" >&2; exit 3; }

# Rename to the shared evidence convention f<time>s_<beat>_<pos>.png, the same
# names verify_render.py writes. One naming scheme means one parser, and it is
# what gives check_diversity a beat to group by. The CLI emits
# frame-<n>-at-<t>s.png in --at order, so index N carries beat N.
AT="$(IFS=,; echo "${AT[*]}")" BEAT="$(IFS=,; echo "${BEAT[*]}")" OUT="$OUT" \
python3 - <<'PY' || { echo "PRECHECK_FAIL $STEM could not name frames" >&2; exit 3; }
import os, pathlib, re
out = pathlib.Path(os.environ["OUT"])
ats = os.environ["AT"].split(",")
beats = os.environ["BEAT"].split(",")
pngs = sorted(out.glob("frame-*.png"),
              key=lambda p: int(re.search(r"frame-(\d+)", p.name).group(1)))
for i, p in enumerate(pngs):
    if i >= len(ats):
        break
    p.rename(out / f"f{float(ats[i]):07.2f}s_{beats[i]}_g{i:03d}.png")
print(f"   named {min(len(pngs), len(ats))} frame(s) as shared evidence")
PY

# Deterministic low-ink flag: blank scenes compress far smaller than real ones.
# (Advisory, not fatal: dark statement scenes legitimately compress small — the
# vision reviewer judges the flagged frames. But the check itself must run.)
OUT="$OUT" python3 - <<'PY' || { echo "PRECHECK_FAIL $STEM low-ink check crashed" >&2; exit 3; }
import os, pathlib, statistics
out = pathlib.Path(os.environ["OUT"])
pngs = sorted(p for p in out.glob("*.png"))
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

# The freeze gate — the reason the freeform grid is dense. Fatal, and it runs
# BEFORE the vision handoff so a frozen build never reaches a reviewer's eyes:
# "did the picture hold perfectly still for five seconds" is a stopwatch
# measurement, and handing it to a human is what let the 2026-07-31 cut through.
# Template lane: skipped, because preflight check 6 (check_pacing) owns it from
# the compiled cue list and a second opinion here would just cost snapshots.
if [[ "$FREEFORM" == "1" ]]; then
  echo "== diversity (freeze + monotony, from real pixels)"
  DIV_OUT="$(python3 "$VP/render-qa/src/check_diversity.py" "$OUT" --ws "$WS" 2>&1)"
  rc=$?
  echo "$DIV_OUT" | sed 's/^/   /'
  if [[ $rc -ne 0 ]]; then
    echo "PRECHECK_FAIL $STEM check_diversity exit=$rc" >&2
    exit 3
  fi
fi

# Sampled spread for the vision reviewer.
mapfile -t FRAMES < <(SAMPLE="$SAMPLE" OUT="$OUT" python3 - <<'PY'
import os, pathlib
out = pathlib.Path(os.environ["OUT"])
f = sorted(str(p) for p in out.glob("f*s_*.png"))
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
