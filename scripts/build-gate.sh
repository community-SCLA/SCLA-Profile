#!/usr/bin/env bash
# build-gate.sh — run the authoritative preflight and write down its verdict.
#
# WHY THE MARKER EXISTS. "Gate-clean, awaiting your eyes" was a state that
# existed only in the memory of the session that ran preflight. When that
# session ended, the workspace on disk was indistinguishable from one whose gate
# had never run — so batch-status.sh could not derive the visual-review stage, and
# an owner opening PIPELINE-STATUS.md saw a half-finished build where a finished
# one was actually sitting at the pilot gate.
#
# qa/PREFLIGHT-OK is that verdict, written down. It is written HERE and nowhere
# else, on exit 0 and only on exit 0, so the marker cannot be present without
# the gate having actually passed — and a non-zero run DELETES a marker left by
# an earlier pass, because a stale green is worse than no green (the failure
# class this repo quantifies as 14 defects from rules that existed but did not
# fire).
#
# This does not replace the gates; it runs the real preflight.py and reports
# exactly what it said. Nothing here can make a build pass.
#
# Usage:  bash scripts/build-gate.sh <stem> [extra preflight args...]
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="${VIDEO_VP_ROOT:-$REPO/projects/video-production}"
PREFLIGHT="$REPO/projects/video-production/render-qa/src/preflight.py"
REVISION_TOOL="$REPO/projects/video-production/render-qa/src/workspace_revision.py"
GATE_REVISION_TOOL="$REPO/projects/video-production/render-qa/src/gate_contract.py"

STEM="${1:-}"
if [ -z "$STEM" ]; then
  echo "usage: build-gate.sh <stem> [extra preflight args...]" >&2
  exit 2
fi
shift

WS="$VP/renders-hyperframes/$STEM"
[ -d "$WS" ] || { echo "FATAL: no workspace at renders-hyperframes/$STEM" >&2; exit 2; }

MARKER="$WS/qa/PREFLIGHT-OK"
mkdir -p "$WS/qa"

# Pixel and adversarial review must see THIS source, not whatever PNGs happen
# to be left in snapshots/ from an earlier edit. Freeform workspaces carry the
# canonical per-beat grid in timing.json; regenerate it before preflight so the
# geometry gate and the later hashed visual-review receipt share fresh pixels.
if [ -f "$WS/audio_request.json" ] && [ -f "$WS/timing.json" ] && [ -f "$WS/package.json" ]; then
  SNAP_TIMES="$(PYTHONPATH="$VP/render-qa/src" python3 - "$WS" <<'PY'
import sys
from pathlib import Path
from hfp_common import sample_units

units = sample_units(Path(sys.argv[1]))
print(",".join(f"{u['start'] + u['duration'] / 2:.3f}" for u in units))
PY
)"
  if [ -z "$SNAP_TIMES" ]; then
    rm -f "$MARKER"
    echo "FATAL: no per-beat snapshot grid; visual evidence cannot be refreshed" >&2
    exit 2
  fi
  SNAP_EXPECTED="$(awk -F, '{print NF}' <<<"$SNAP_TIMES")"
  SNAP_CLI="$(python3 - "$WS/package.json" <<'PY'
import re
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
matches = re.findall(r"hyperframes@([0-9][0-9.]*)", raw)
print(f"hyperframes@{matches[-1]}" if matches else "hyperframes")
PY
)"
  mkdir -p "$WS/snapshots"
  SNAP_BACKUP="$(mktemp -d)"
  shopt -s nullglob
  OLD_FRAMES=("$WS"/snapshots/frame-*-at-*.png)
  if [ "${#OLD_FRAMES[@]}" -gt 0 ]; then
    mv -- "${OLD_FRAMES[@]}" "$SNAP_BACKUP/"
  fi
  shopt -u nullglob
  set +e
  (
    cd "$WS" || exit 2
    npx --yes "$SNAP_CLI" snapshot . --at "$SNAP_TIMES" --no-end -o snapshots
  )
  SNAP_RC=$?
  set -e
  shopt -s nullglob
  NEW_FRAMES=("$WS"/snapshots/frame-*-at-*.png)
  shopt -u nullglob
  if [ "$SNAP_RC" -ne 0 ] || [ "${#NEW_FRAMES[@]}" -ne "$SNAP_EXPECTED" ]; then
    if [ "${#NEW_FRAMES[@]}" -gt 0 ]; then
      rm -f -- "${NEW_FRAMES[@]}"
    fi
    shopt -s nullglob
    BACKUP_FRAMES=("$SNAP_BACKUP"/frame-*-at-*.png)
    if [ "${#BACKUP_FRAMES[@]}" -gt 0 ]; then
      mv -- "${BACKUP_FRAMES[@]}" "$WS/snapshots/"
    fi
    shopt -u nullglob
    rm -r -- "$SNAP_BACKUP"
    rm -f "$MARKER"
    echo "FATAL: current-source snapshot refresh failed or returned " \
         "${#NEW_FRAMES[@]}/$SNAP_EXPECTED frames" >&2
    exit 2
  fi
  rm -r -- "$SNAP_BACKUP"
  echo "== refreshed $SNAP_EXPECTED per-beat review frame(s) from current source"
fi

set +e
python3 "$PREFLIGHT" "$WS" "$@"
RC=$?
set -e

if [ "$RC" -ne 0 ]; then
  # A previous pass may have left a marker. It is now a lie.
  if [ -f "$MARKER" ]; then
    rm -f "$MARKER"
    echo "== removed a stale qa/PREFLIGHT-OK — this build is no longer gate-clean"
  fi
  bash "$REPO/scripts/build-log.sh" "$STEM" preflight "exit $RC" >/dev/null 2>&1 || true
  bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true
  echo "== preflight exit $RC — NOT gate-clean" >&2
  exit "$RC"
fi

# A green marker names the exact authored/runtime inputs that passed. Remove
# any older receipt before calculating the new identity so a tooling failure
# can never leave a stale green behind.
rm -f "$MARKER"
REVISION="$(python3 "$REVISION_TOOL" "$WS")" || {
  echo "FATAL: preflight passed but the workspace revision could not be recorded" >&2
  exit 2
}
GATE_REVISION="$(python3 "$GATE_REVISION_TOOL")" || {
  echo "FATAL: preflight passed but the gate contract could not be recorded" >&2
  exit 2
}
python3 - "$MARKER" "$REVISION" "$GATE_REVISION" "$STEM" "${*:-}" <<'PY'
import datetime
import json
import os
import sys
from pathlib import Path

marker, revision, gate_revision, stem, extra = (
    Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
payload = {
    "version": 2,
    "preflight_exit": 0,
    "created_at": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"),
    "workspace": f"renders-hyperframes/{stem}",
    "command": f"python3 render-qa/src/preflight.py <workspace>{(' ' + extra) if extra else ''}",
    "source_revision": revision,
    "gate_revision": gate_revision,
}
temporary = marker.with_name(f".{marker.name}.tmp-{os.getpid()}")
temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
os.replace(temporary, marker)
PY

bash "$REPO/scripts/build-log.sh" "$STEM" preflight "exit 0 — gate-clean" >/dev/null 2>&1 || true
bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true

echo "== gate-clean: wrote qa/PREFLIGHT-OK"
echo "   This build now reads as AWAITING VISUAL REVIEW in batch-status.sh and"
echo "   PIPELINE-STATUS.md. A durable PASS/ALIVE/PROCEED receipt advances it."
