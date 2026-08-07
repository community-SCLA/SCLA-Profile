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
python3 - "$MARKER" "$REVISION" "$STEM" "${*:-}" <<'PY'
import datetime
import json
import os
import sys
from pathlib import Path

marker, revision, stem, extra = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
payload = {
    "version": 1,
    "preflight_exit": 0,
    "created_at": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"),
    "workspace": f"renders-hyperframes/{stem}",
    "command": f"python3 render-qa/src/preflight.py <workspace>{(' ' + extra) if extra else ''}",
    "source_revision": revision,
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
