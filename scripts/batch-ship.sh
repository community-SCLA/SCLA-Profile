#!/usr/bin/env bash
# batch-ship.sh — the deterministic tail of a lesson video, in one call.
#
# Everything after preflight-green is mechanical and needs no agent judgement,
# so it lives here instead of in an orchestrator's context. Two modes:
#
#   bash scripts/batch-ship.sh <stem> <program-slug>
#       RENDER phase: preflight -> move script to rendered/ -> render -> verify
#       -> sample frames for review. Exits 0 with AWAITING_VISION, or 3 with
#       QUARANTINE (never publishes a video that failed a guard).
#
#   bash scripts/batch-ship.sh <stem> <program-slug> --publish
#       PUBLISH phase, run only after the sampled frames pass review: file the
#       MP4 -> upload to Wistia -> record the URL in refinement-log.md -> commit
#       -> delete the local MP4 -> prune the workspace in place (kept editable).
#
# Fail soft, always: a guard failure quarantines THIS video and exits non-zero;
# the caller moves on to the next. One bad lesson never costs the others.
#
# Resume contract: a stem is done iff its Wistia URL is in refinement-log.md,
# and that URL is committed in the same pass that publishes it.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
QLOG="$VP/render-qa/quarantine.log"

STEM="${1:-}"; PROGRAM="${2:-}"; MODE="${3:-render}"
if [[ -z "$STEM" || -z "$PROGRAM" ]]; then
  echo "Usage: bash scripts/batch-ship.sh <stem> <program-slug> [--publish]" >&2
  exit 2
fi
[[ "$MODE" == "--publish" ]] && MODE="publish" || MODE="render"

WS="$VP/renders-hyperframes/$STEM"
[[ -d "$WS" ]] || { echo "FATAL: no workspace at $WS" >&2; exit 2; }

quarantine() {
  local reason="$1"
  mkdir -p "$(dirname "$QLOG")"
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$STEM" "$PROGRAM" "$reason" >> "$QLOG"
  echo "QUARANTINE: $STEM — $reason" >&2
  echo "  workspace kept at renders-hyperframes/$STEM; not published." >&2
  exit 3
}

# ---------------------------------------------------------------- RENDER phase
if [[ "$MODE" == "render" ]]; then
  # Previews contaminate renders (they hold the same ports and GPU/shm state).
  pkill -f "hyperframes[ ]preview" 2>/dev/null || true

  echo "== preflight: $STEM"
  python3 "$VP/render-qa/preflight.py" "$WS" || quarantine "preflight.py non-zero"

  # Move the script out of the build queue only once its build is gate-clean.
  SRC_SCRIPT="$VP/lesson-scripts/$PROGRAM/refined/$STEM.txt"
  DST_SCRIPT="$VP/lesson-scripts/$PROGRAM/rendered/$STEM.txt"
  if [[ -f "$SRC_SCRIPT" ]]; then
    mkdir -p "$(dirname "$DST_SCRIPT")"
    git -C "$REPO" mv "$SRC_SCRIPT" "$DST_SCRIPT" 2>/dev/null || mv "$SRC_SCRIPT" "$DST_SCRIPT"
    echo "   script -> rendered/"
  fi

  echo "== render: $STEM  (~7 min)"
  ( cd "$WS" && npm run render ) || quarantine "npm run render failed"

  echo "== verify_render"
  python3 "$VP/render-qa/verify_render.py" "$WS" || quarantine "verify_render.py non-zero"

  # Sample frames for the vision guard. verify_render dumps 3 per scene; a
  # 15-scene video is 45 images (~65k tokens) and a 30-video batch would be ~2M
  # — so review a spread, not the dump. check_presence.py (inside
  # verify_render) already covers blank/stagnation deterministically; this is a
  # spot-check for layout and brand, not the primary guard.
  mapfile -t FRAMES < <(
    find "$WS/qa/frames" -name '*_mid.png' 2>/dev/null | sort |
    python3 -c '
import sys
f=[l.strip() for l in sys.stdin if l.strip()]
if not f: sys.exit(0)
n=min(6,len(f))
idx=[round(i*(len(f)-1)/(n-1)) if n>1 else 0 for i in range(n)]
seen=set()
for i in idx:
    if i not in seen:
        seen.add(i); print(f[i])
')
  [[ ${#FRAMES[@]} -gt 0 ]] || quarantine "no qa/frames/ produced"

  echo
  echo "AWAITING_VISION $STEM"
  echo "TRANSCRIPT $WS/transcript.json"
  for f in "${FRAMES[@]}"; do echo "FRAME $f"; done
  exit 0
fi

# --------------------------------------------------------------- PUBLISH phase
MP4_SRC="$(find "$WS/renders" -name '*.mp4' -newer "$WS" 2>/dev/null | head -1)"
[[ -n "$MP4_SRC" ]] || MP4_SRC="$(find "$WS/renders" -name '*.mp4' 2>/dev/null | head -1)"
[[ -n "$MP4_SRC" ]] || quarantine "no MP4 in $WS/renders/"

# Filed name = script stem with the date swapped to the render date.
RENDER_DATE="$(date +%F)"
BASE="${STEM%_*}"
FILED="${BASE}_${RENDER_DATE}.mp4"
DEST_DIR="$VP/renders-mp4/$PROGRAM/hyperframes"
mkdir -p "$DEST_DIR"
cp "$MP4_SRC" "$DEST_DIR/$FILED" || quarantine "could not file MP4"
echo "== filed: renders-mp4/$PROGRAM/hyperframes/$FILED"

echo "== wistia upload"
UPLOAD_OUT="$(bash "$REPO/scripts/wistia-upload.sh" "$DEST_DIR/$FILED" "$PROGRAM" 2>&1)" || {
  echo "$UPLOAD_OUT" >&2; quarantine "wistia-upload.sh failed"; }
echo "$UPLOAD_OUT"
WURL="$(grep -o 'https://[a-z0-9.-]*wistia\.com/medias/[A-Za-z0-9]*' <<<"$UPLOAD_OUT" | head -1)"
[[ -n "$WURL" ]] || quarantine "no Wistia URL returned"

# Record the URL in the ledger — same pass, so an interrupted batch can never
# leave a published video unrecorded.
STEM="$STEM" PROGRAM="$PROGRAM" WURL="$WURL" FILED="$FILED" RENDER_DATE="$RENDER_DATE" \
LEDGER="$VP/lesson-scripts/refinement-log.md" python3 - <<'PY'
import os, re
from pathlib import Path

led = Path(os.environ["LEDGER"]); stem = os.environ["STEM"]
prog = os.environ["PROGRAM"]; url = os.environ["WURL"]
filed = os.environ["FILED"]; rdate = os.environ["RENDER_DATE"]
text = led.read_text(encoding="utf-8"); lines = text.splitlines()

parts = stem.split("_"); date = parts[-1]; rest = parts[:-1]
if rest and rest[-1] == prog:
    rest = rest[:-1]
prefix = "_".join(rest)

rendered_cell = f"{rdate} → `../renders-mp4/{prog}/hyperframes/{filed}` · Wistia {url}"
note = f"published {rdate} (AUTO-BATCH); local MP4 deleted after upload, workspace pruned in place and still editable"

# Rows abbreviate the stem (`title_..._DATE.txt`), so match on prefix + date.
hit = None
for i, ln in enumerate(lines):
    if not ln.startswith("|") or "`" not in ln:
        continue
    cell = ln.split("|")[1] if len(ln.split("|")) > 1 else ""
    if prefix and prefix in cell and date in cell:
        hit = i
        break

if hit is not None:
    cols = lines[hit].split("|")
    if len(cols) >= 6:          # | Script | Created | Refined | Rendered | Notes |
        cols[4] = f" {rendered_cell} "
        cols[5] = f" {cols[5].strip()} · {note} " if cols[5].strip() else f" {note} "
        lines[hit] = "|".join(cols)
    else:
        lines[hit] = lines[hit].rstrip() + f" · Wistia {url}"
else:
    # No existing row: append one under the program's table rather than fail.
    hdr = None
    for i, ln in enumerate(lines):
        if ln.strip() == f"## {prog}":
            hdr = i
            break
    row = f"| `{stem}.txt` | | | {rendered_cell} | {note} |"
    if hdr is not None:
        j = hdr
        while j < len(lines) and not lines[j].startswith("|---"):
            j += 1
        k = j + 1
        while k < len(lines) and lines[k].startswith("|"):
            k += 1
        lines.insert(k, row)
    else:
        lines.append(row)

led.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"   ledger row updated ({'in place' if hit is not None else 'appended'})")
PY
[[ $? -eq 0 ]] || quarantine "ledger update failed"

git -C "$REPO" add -A "$VP/lesson-scripts" >/dev/null 2>&1
git -C "$REPO" commit -q -m "ship($PROGRAM): $STEM → Wistia

$WURL

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>" >/dev/null 2>&1 \
  && echo "   committed" || echo "   (nothing to commit)"

# Prune BEFORE deleting the MP4 — archive-lesson.sh refuses to prune a
# workspace whose deliverable isn't filed, and that safety check is worth keeping.
bash "$REPO/scripts/archive-lesson.sh" "$STEM" --in-place || echo "   (prune skipped)"
rm -f "$DEST_DIR/$FILED"
echo "   local MP4 deleted — Wistia is the delivery copy"

echo
echo "PUBLISHED $STEM $WURL"
