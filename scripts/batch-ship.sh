#!/usr/bin/env bash
# batch-ship.sh — the deterministic tail of a lesson video, in one call.
#
# Everything after preflight-green is mechanical and needs no agent judgement,
# so it lives here instead of in an orchestrator's context. Two modes:
#
#   bash scripts/batch-ship.sh <stem> <program-slug>
#       RENDER phase: preflight -> render -> verify (writes qa/VERIFIED) ->
#       sample frames for review. Exits 0 with AWAITING_VISION, or 3 with
#       QUARANTINE (never publishes a video that failed a guard).
#
#   bash scripts/batch-ship.sh <stem> <program-slug> --publish
#       PUBLISH phase, run only after the sampled frames pass review: check the
#       qa/VERIFIED marker -> file exactly that MP4 -> upload to Wistia ->
#       record stem+URL in published.tsv AND refinement-log.md -> move script
#       to published/ -> commit -> prune the workspace in place (kept editable).
#       The filed MP4 is KEPT under renders-mp4/ (gitignored) as the local
#       backup of the delivered cut — owner call 2026-07-29.
#
# Fail soft, always: a guard failure quarantines THIS video and exits non-zero;
# the caller moves on to the next. One bad lesson never costs the others.
# If a quarantine happens AFTER a successful upload, the Wistia URL is written
# into the quarantine record so the video is never live-but-unrecorded.
#
# Resume contract: a stem is done iff it has a row in
# lesson-scripts/published.tsv (machine key, full stem, committed in the same
# pass that publishes it). refinement-log.md stays the human-facing ledger.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
QLOG="$VP/render-qa/quarantine.log"
PUBTSV="$VP/lesson-scripts/published.tsv"
RUN_STATE="$VP/render-qa/src/run_state.py"
REVISION_TOOL="$VP/render-qa/src/workspace_revision.py"

STEM="${1:-}"; PROGRAM="${2:-}"; MODE_ARG="${3:-}"
if [[ -z "$STEM" || -z "$PROGRAM" ]]; then
  echo "Usage: bash scripts/batch-ship.sh <stem> <program-slug> [--publish]" >&2
  exit 2
fi
case "$MODE_ARG" in
  "")          MODE="render" ;;
  --publish)   MODE="publish" ;;
  *) echo "FATAL: unknown mode '$MODE_ARG' (only --publish is accepted)" >&2; exit 2 ;;
esac

WS="$VP/renders-hyperframes/$STEM"
[[ -d "$WS" ]] || { echo "FATAL: no workspace at $WS" >&2; exit 2; }
python3 "$RUN_STATE" can-ship "$STEM" || exit $?

# Shipping is a workspace-writing session too. Refresh one idempotent lease and
# release exactly this stem on every exit; TTL remains only a hard-crash backup.
RLOCK=""
LOCK=""
# Shipping always continues an approved existing workspace. --resume permits
# stale-lease takeover at the short recovery threshold while still refusing a
# fresh live owner; failure remains closed before render/publish side effects.
bash "$REPO/scripts/build-session.sh" arm "$STEM" --resume >/dev/null \
  || { echo "FATAL: could not acquire exclusive lesson lease for $STEM" >&2; exit 2; }
cleanup_ship() {
  [[ -z "$RLOCK" ]] || rm -rf "$RLOCK" 2>/dev/null || true
  [[ -z "$LOCK" ]] || rmdir "$LOCK" 2>/dev/null || true
  bash "$REPO/scripts/build-session.sh" release "$STEM" >/dev/null 2>&1 || true
  bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true
}
trap cleanup_ship EXIT

# Stem naming has exactly one owner: render-qa/src/stem.py. A WORKING artifact
# (workspace, ready/ script, published/ script) is named `<title>_<program>`
# with no date at all, so its name is its identity and never moves. Only the
# DELIVERED MP4 gains a date, the render date, frozen at publish. `stem_base`
# is tolerant of legacy dated names, so a workspace built before 2026-07-29
# still keys correctly. (Dropped 2026-07-29, decisions/log.md: a name that
# moves cannot be a lock, and a restamping rebuild had already produced two
# workspaces for one lesson.)
STEM_PY="$VP/render-qa/src/stem.py"
stem_base()      { python3 "$STEM_PY" base "$1"; }
stem_delivered() { python3 "$STEM_PY" delivered "$1" --date "$2"; }

BASE="$(stem_base "$STEM")" || { echo "FATAL: malformed stem '$STEM'" >&2; exit 2; }

# A guard's verdict is the diagnosis; its exit code is only the citation. Run one
# through this so the reason a video is stuck survives the session that found it —
# "verify_render.py non-zero" told the owner nothing and cost a full re-run of the
# gate to recover what the gate had already printed (2026-07-31). Output still
# streams; pipefail keeps the guard's own status, not tee's.
guarded() {
  local label="$1"; shift
  local stamp logfile
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "$WS/qa/logs"
  logfile="$WS/qa/logs/${stamp}-${label}.log"
  LAST_GUARD_LOG="$logfile"
  LAST_GUARD_COMMAND="$(printf '%q ' "$@")"
  { printf '=== %s — %s\n' "$(date -u +%FT%TZ)" "$label"; } > "$logfile"
  "$@" 2>&1 | tee -a "$logfile"
  local rc=${PIPESTATUS[0]}
  LAST_GUARD_EXIT_CODE="$rc"
  return $rc
}

quarantine() {
  local reason="$1"
  local error_class="${2:-pipeline}"
  local next_action="${3:-inspect ${LAST_GUARD_LOG:-the command output}, correct the cause, then use run.sh retry $STEM --reason \"cause corrected\"}"
  local log_path="${LAST_GUARD_LOG:-}"
  local command="${LAST_GUARD_COMMAND:-unknown}"
  local exit_code="${LAST_GUARD_EXIT_CODE:-1}"
  mkdir -p "$(dirname "$QLOG")"
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$STEM" "$PROGRAM" "$reason" >> "$QLOG"
  python3 "$RUN_STATE" record-failure \
    --workspace "$WS" --stem "$STEM" --program "$PROGRAM" \
    --error-class "$error_class" --reason "$reason" --command "$command" \
    --exit-code "$exit_code" --log "$log_path" --next-action "$next_action" \
    >/dev/null 2>&1 || true
  echo "QUARANTINE: $STEM — $reason" >&2
  [[ -z "$log_path" ]] || echo "  full output: $log_path" >&2
  echo "  workspace kept at renders-hyperframes/$STEM; not published." >&2
  bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true
  exit 3
}

# Free disk on the workspace filesystem: a render needs ~1 GB headroom and a
# full disk mid-ledger-write is the worst failure mode there is.
FREE_MB="$(df -Pm "$WS" 2>/dev/null | awk 'NR==2{print $4}')"
[[ -n "$FREE_MB" && "$FREE_MB" -ge 4096 ]] || quarantine "low disk: ${FREE_MB:-?} MB free (<4096)"

# ---------------------------------------------------------------- RENDER phase
if [[ "$MODE" == "render" ]]; then
  python3 "$RUN_STATE" can-attempt "$WS" || exit $?
  # Render backend: `local` (default) or `cloud`, chosen by the one-line file
  # renders-hyperframes/_run/RENDER-BACKEND. A file, not an env flag — owner
  # and subagents must read the same state (the write-fence lesson,
  # decisions/log.md 2026-08-04). `cloud` renders on HeyGen's own
  # Chromium/FFmpeg via `hyperframes cloud render`: only the zip upload and
  # the MP4 download touch this box, so cloud renders run in PARALLEL and the
  # CPU lock below is skipped. (Added 2026-08-05, the overnight drain.)
  BACKEND_FILE="$VP/renders-hyperframes/_run/RENDER-BACKEND"
  RENDER_BACKEND="local"
  [[ -f "$BACKEND_FILE" ]] && RENDER_BACKEND="$(tr -d '[:space:]' < "$BACKEND_FILE")"
  case "$RENDER_BACKEND" in
    local|cloud) ;;
    *) quarantine "unknown RENDER-BACKEND '$RENDER_BACKEND' (only local|cloud)" ;;
  esac

  if [[ "$RENDER_BACKEND" == "local" ]]; then
    # ONE local render at a time, machine-wide. Builds run N-wide (authoring +
    # network TTS), but a local render is CPU-bound and two of them on a
    # 4-core box thrash and cost more than they save. Until 2026-07-29 this
    # was a sentence in the SKILL asking the orchestrator not to — and a
    # session running 4 concurrent builds was one gate-pass away from
    # disproving it. mkdir is atomic, so the lock is the mechanism (STD-35);
    # the publish phase below has had the same shape all along. Held for the
    # render, released on any exit.
    RLOCK="$VP/renders-hyperframes/.render.lock"
    if ! mkdir "$RLOCK" 2>/dev/null; then
      HOLDER="$(cat "$RLOCK/stem" 2>/dev/null || echo "unknown")"
      echo "FATAL: another render is in flight ($HOLDER). Renders are serialised;" >&2
      echo "       retry when it finishes, or remove $RLOCK if it is stale." >&2
      exit 2
    fi
    echo "$STEM" > "$RLOCK/stem" 2>/dev/null || true
  fi

  # Previews contaminate renders (they hold the same ports and GPU/shm state).
  pkill -f "hyperframes[ ]preview" 2>/dev/null || true

  echo "== preflight: $STEM"
  guarded "preflight" python3 "$VP/render-qa/src/preflight.py" "$WS" \
    || quarantine "preflight rejected the plan (preflight.py)" "preflight" \
      "inspect $LAST_GUARD_LOG, fix the authoring, then run the build gate"

  RENDER_REVISION="$(python3 "$REVISION_TOOL" "$WS")" \
    || quarantine "could not compute source revision at render start"
  REUSE_RENDER=0
  mapfile -t REUSE_META < <(python3 - "$WS" "$RENDER_REVISION" <<'PY' 2>/dev/null
import hashlib
import json
import sys
from pathlib import Path

workspace = Path(sys.argv[1])
current = sys.argv[2]
try:
    receipt = json.loads((workspace / "qa/RENDER-START.json").read_text())
except (OSError, json.JSONDecodeError, TypeError):
    raise SystemExit(0)
encode = {}
failure = {}
try:
    encode = json.loads((workspace / "qa/ENCODE-REVIEW.json").read_text())
except (OSError, json.JSONDecodeError, TypeError):
    pass
try:
    failure = json.loads((workspace / "qa/failure.json").read_text())
except (OSError, json.JSONDecodeError, TypeError):
    pass
raw_mp4 = receipt.get("mp4") if isinstance(receipt, dict) else None
mp4 = Path(raw_mp4) if isinstance(raw_mp4, str) and raw_mp4 else None
if mp4 is not None and not mp4.is_absolute():
    mp4 = workspace / mp4
required = receipt.get("encode_review_required") if isinstance(receipt, dict) else None
backend = receipt.get("backend") if isinstance(receipt, dict) else None
completed_sha = receipt.get("completed_sha256") if isinstance(receipt, dict) else None
completed_bytes = receipt.get("completed_bytes") if isinstance(receipt, dict) else None
attempt = receipt.get("attempt") if isinstance(receipt, dict) else None
actual_sha = None
if mp4 is not None and mp4.is_file():
    digest = hashlib.sha256()
    with mp4.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_sha = digest.hexdigest()
if (receipt.get("source_revision") == current
        and isinstance(required, bool)
        and isinstance(attempt, int) and attempt >= 1
        and backend in {"local", "cloud"}
        and isinstance(receipt.get("completed_at"), str)
        and receipt.get("completed_at")
        and isinstance(completed_bytes, int)
        and mp4 is not None and mp4.is_file()
        and mp4.stat().st_size == completed_bytes
        and actual_sha == completed_sha):
    encode_failed = (
        isinstance(encode, dict)
        and encode.get("source_revision") == current
        and encode.get("sha256") == completed_sha
        and encode.get("render_attempt") == attempt
        and str(encode.get("verdict", "")).strip().upper() == "FAIL"
    )
    verify_retry = (
        isinstance(failure, dict)
        and failure.get("error_class") == "verify-render"
        and isinstance(failure.get("resolved_at"), str)
        and failure.get("resolved_at")
        and str(failure.get("failed_at") or "") >= str(receipt.get("completed_at") or "")
    )
    if encode_failed or verify_retry:
        raise SystemExit(0)
    for value in (receipt.get("render_date") or "", backend,
                  receipt.get("task_key") or "", str(mp4),
                  "true" if required else "false", str(attempt)):
        print(value)
PY
)
  if [[ ${#REUSE_META[@]} -eq 6 ]]; then
    REUSE_RENDER=1
    RENDER_DATE="${REUSE_META[0]}"
    RENDER_BACKEND="${REUSE_META[1]}"
    RENDER_TASK_KEY="${REUSE_META[2]}"
    OUT_MP4="${REUSE_META[3]}"
    ENCODE_REVIEW_REQUIRED="${REUSE_META[4]}"
    RENDER_ATTEMPT="${REUSE_META[5]}"
    echo "== resume verification: reusing current-source MP4 $(basename "$OUT_MP4")"
  else
    # A pruned workspace has no node_modules; reinstall only when a new render
    # is actually needed. An interrupted verify reuses its existing MP4.
    if [[ ! -d "$WS/node_modules" ]]; then
      echo "== npm install (workspace was pruned)"
      guarded "npm-install" bash -c 'cd "$1" && npm install --no-audit --no-fund' _ "$WS" \
        || quarantine "npm install failed" "dependency-install" \
          "inspect $LAST_GUARD_LOG and restore package access before retrying"
    fi

    # Only a new render clears older output. A matching RENDER-START receipt
    # plus MP4 is durable resume state and must survive an interrupted verify.
    rm -f "$WS/renders/"*.mp4 2>/dev/null
    rm -f "$WS/qa/VERIFIED" 2>/dev/null
    RENDER_DATE="$(date +%F)"
    OUT_MP4="$WS/renders/$(stem_delivered "$STEM" "$RENDER_DATE").mp4"
    PREVIOUS_RENDER_ATTEMPT="$(python3 - "$WS/qa/RENDER-START.json" <<'PY'
import json
import sys
try:
    value = json.load(open(sys.argv[1], encoding="utf-8")).get("attempt", 0)
    print(value if isinstance(value, int) and value >= 0 else 0)
except (OSError, json.JSONDecodeError, AttributeError, TypeError):
    print(0)
PY
)"
    RENDER_ATTEMPT=$((PREVIOUS_RENDER_ATTEMPT + 1))
    RENDER_TASK_KEY="scla-${STEM}-${RENDER_DATE}-${RENDER_REVISION}-a${RENDER_ATTEMPT}"
    ENCODE_REVIEW_REQUIRED="true"
    if [[ "$RENDER_BACKEND" == "cloud" ]]; then
      if python3 "$RUN_STATE" post-review-required >/dev/null 2>&1; then
        POST_REVIEW_RC=0
      else
        POST_REVIEW_RC=$?
      fi
      case "$POST_REVIEW_RC" in
        0) ENCODE_REVIEW_REQUIRED="true" ;;
        1) ENCODE_REVIEW_REQUIRED="false" ;;
        *) quarantine "could not determine encode-review policy at render start" ;;
      esac
    fi
    mkdir -p "$WS/qa" "$WS/renders"
    RENDER_RECEIPT_TMP="$WS/qa/.RENDER-START.json.tmp.$$"
    STEM="$STEM" RENDER_BACKEND="$RENDER_BACKEND" RENDER_DATE="$RENDER_DATE" \
    RENDER_REVISION="$RENDER_REVISION" RENDER_TASK_KEY="$RENDER_TASK_KEY" \
    RENDER_MP4="$OUT_MP4" RENDER_ATTEMPT="$RENDER_ATTEMPT" \
    ENCODE_REVIEW_REQUIRED="$ENCODE_REVIEW_REQUIRED" \
    python3 - "$RENDER_RECEIPT_TMP" "$WS/qa/RENDER-START.json" <<'PY' \
      || quarantine "could not persist render-start receipt"
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

temporary, destination = map(Path, sys.argv[1:3])
receipt = {
    "source_revision": os.environ["RENDER_REVISION"],
    "backend": os.environ["RENDER_BACKEND"],
    "render_date": os.environ["RENDER_DATE"],
    "task_key": os.environ["RENDER_TASK_KEY"],
    "attempt": int(os.environ["RENDER_ATTEMPT"]),
    "mp4": os.environ["RENDER_MP4"],
    "encode_review_required": os.environ["ENCODE_REVIEW_REQUIRED"] == "true",
    "stem": os.environ["STEM"],
    "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
temporary.replace(destination)
PY

    if [[ "$RENDER_BACKEND" == "cloud" ]]; then
    # Output straight to the delivered name — the normalise loop below then
    # no-ops. npx resolves the workspace's own pinned hyperframes install
    # (node_modules guaranteed by the install block above). with-secrets.sh
    # injects HEYGEN_API_KEY, the credential cloud render authenticates with.
    CLOUD_LIMIT="$(python3 "$RUN_STATE" cloud-concurrency 2>/dev/null || echo 2)"
    echo "== cloud render: $STEM  (HeyGen-hosted; capacity $CLOUD_LIMIT; hard cap 60 min)"
    guarded "cloud-render" bash "$REPO/scripts/with-capacity.sh" \
      cloud-render "$CLOUD_LIMIT" -- bash -c \
      'cd "$1" && timeout -k 30 3600 bash "$2" npx hyperframes cloud render . --quality high --output "$3" --idempotency-key "$4"' \
      _ "$WS" "$REPO/scripts/with-secrets.sh" "$OUT_MP4" "$RENDER_TASK_KEY" \
      || quarantine "cloud render failed or timed out (hyperframes cloud render)" \
        "cloud-render" "inspect $LAST_GUARD_LOG and the cloud credential/backend before retrying"
    [[ -s "$OUT_MP4" ]] || quarantine "cloud render exited 0 but no MP4 landed in renders/"
    else
      local_render_timeout="${SCLA_LOCAL_RENDER_TIMEOUT:-1500}"
      echo "== render: $STEM  (~7 min; hard cap $((local_render_timeout / 60)) min)"
      guarded "local-render" timeout -k 30 "$local_render_timeout" bash "$REPO/scripts/render-local-safe.sh" "$WS" \
        || quarantine "safe local render failed or timed out" "local-render" \
          "inspect $LAST_GUARD_LOG before retrying"
    fi
  fi

  # The HyperFrames CLI names its LOCAL output `<workspace-dir>_<date>_<clock>.mp4`,
  # so the renderer's own output violates the one-date rule by construction.
  # Normalise it here, BEFORE verify_render.py records the path and sha in
  # qa/VERIFIED — otherwise the marker pins the malformed name and publish
  # would upload it. The date used is the render date, which is what the name
  # is supposed to mean. (A cloud MP4 is already delivered-named; the loop
  # no-ops on it.)
  if [[ "$REUSE_RENDER" -eq 0 ]]; then
    shopt -s nullglob
    for raw in "$WS/renders/"*.mp4; do
      want="$(stem_delivered "$(basename "$raw")" "$RENDER_DATE").mp4"
      [[ "$(basename "$raw")" == "$want" ]] && continue
      mv -f "$raw" "$WS/renders/$want" || quarantine "could not normalise render filename"
      echo "   render name normalised -> $want"
    done
    shopt -u nullglob
  fi
  [[ -s "$OUT_MP4" ]] \
    || quarantine "render receipt MP4 is missing after render: $OUT_MP4"
  if [[ "$REUSE_RENDER" -eq 0 ]]; then
    RENDER_COMPLETE_TMP="$WS/qa/.RENDER-START.complete.tmp.$$"
    python3 - "$WS/qa/RENDER-START.json" "$OUT_MP4" "$RENDER_COMPLETE_TMP" <<'PY' \
      || quarantine "could not persist atomic render-complete receipt"
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

receipt_path, mp4, temporary = map(Path, sys.argv[1:4])
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
digest = hashlib.sha256()
with mp4.open("rb") as source:
    for chunk in iter(lambda: source.read(1024 * 1024), b""):
        digest.update(chunk)
receipt["completed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
receipt["completed_sha256"] = digest.hexdigest()
receipt["completed_bytes"] = mp4.stat().st_size
temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
temporary.replace(receipt_path)
PY
  fi

  echo "== verify_render"
  rm -f "$WS/qa/VERIFIED" 2>/dev/null
  guarded "verify-render" python3 "$VP/render-qa/src/verify_render.py" "$WS" "$OUT_MP4" \
    || quarantine "the rendered MP4 failed post-render verification (verify_render.py)" \
      "verify-render" "inspect $LAST_GUARD_LOG, fix the named defect, then re-render"
  [[ -f "$WS/qa/VERIFIED" ]] || quarantine "verify passed but wrote no qa/VERIFIED marker"
  python3 "$RUN_STATE" record-success --workspace "$WS" --stem "$STEM" \
    --phase "$([[ "$RENDER_BACKEND" == "cloud" ]] && echo cloud-render || echo local-render)" \
    >/dev/null 2>&1 || true

  case "$ENCODE_REVIEW_REQUIRED" in
    true) ;;
    false)
      echo
      echo "READY_TO_PUBLISH $STEM — deterministic verification passed; " \
           "this render was stamped after encode review retired"
      exit 0
      ;;
    *) quarantine "render receipt has no valid encode-review policy" ;;
  esac

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
# One publisher at a time: publish touches git and the shared ledgers.
LOCK="$VP/renders-hyperframes/.publish.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "FATAL: another publish is in flight ($LOCK exists). Retry when it finishes." >&2
  exit 2
fi

# Idempotency: a lesson with a published.tsv row is done — never re-upload.
# Keyed on BASE, not the full stem: the date is a state stamp that moves with
# every action, so a full-stem key would miss the row the moment a rebuild
# restamped it and would happily publish the same lesson twice.
if [[ -f "$PUBTSV" ]]; then
  PREV_URL="$(awk -F'\t' -v b="$BASE" '$1==b{print $4; exit}' "$PUBTSV")"
  if [[ -n "$PREV_URL" ]]; then
    echo "ALREADY PUBLISHED: $BASE  ($PREV_URL)"
    exit 0
  fi
fi

# Publish exactly what verify verified — path and hash from the marker.
MARKER="$WS/qa/VERIFIED"
[[ -f "$MARKER" ]] || quarantine "no qa/VERIFIED marker — render+verify have not passed on the current MP4"
CURRENT_REVISION="$(python3 "$REVISION_TOOL" "$WS")" \
  || quarantine "could not compute current source revision"
RENDER_MARKER="$WS/qa/RENDER-START.json"
[[ -f "$RENDER_MARKER" ]] \
  || quarantine "no qa/RENDER-START.json — the MP4 is not bound to a source revision"
if PUBLISH_META_RAW="$(python3 - "$WS" "$CURRENT_REVISION" "$MARKER" "$RENDER_MARKER" <<'PY'
import json
import sys
from pathlib import Path

workspace = Path(sys.argv[1])
current = sys.argv[2]
try:
    verified = json.load(open(sys.argv[3], encoding="utf-8"))
    render = json.load(open(sys.argv[4], encoding="utf-8"))
except (OSError, json.JSONDecodeError, TypeError) as exc:
    print(f"receipt is unreadable ({exc})")
    raise SystemExit(1)
if not isinstance(verified, dict) or not isinstance(render, dict):
    print("render receipts are not JSON objects")
    raise SystemExit(1)
if verified.get("source_revision") != current or render.get("source_revision") != current:
    print("render task or verification belongs to different source")
    raise SystemExit(1)
required = render.get("encode_review_required")
if not isinstance(required, bool) or verified.get("encode_review_required") is not required:
    print("render receipts disagree on the immutable encode-review policy")
    raise SystemExit(1)
attempt = render.get("attempt")
if (not isinstance(attempt, int) or attempt < 1
        or verified.get("render_attempt") != attempt):
    print("render receipts disagree on render attempt")
    raise SystemExit(1)

def resolve_mp4(value):
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else workspace / path

render_mp4 = resolve_mp4(render.get("mp4"))
verified_mp4 = resolve_mp4(verified.get("mp4"))
if (render_mp4 is None or verified_mp4 is None
        or render_mp4.resolve() != verified_mp4.resolve()):
    print("render receipts do not identify the same MP4")
    raise SystemExit(1)
digest = verified.get("sha256")
if not isinstance(digest, str) or not digest:
    print("VERIFIED has no MP4 hash")
    raise SystemExit(1)
if (not isinstance(render.get("completed_at"), str)
        or not render.get("completed_at")
        or not isinstance(render.get("completed_bytes"), int)
        or render.get("completed_sha256") != digest):
    print("render-complete receipt does not match VERIFIED")
    raise SystemExit(1)
print(verified_mp4)
print(digest)
print("true" if required else "false")
PY
)"; then
  mapfile -t PUBLISH_META <<< "$PUBLISH_META_RAW"
else
  quarantine "publish receipts are invalid — ${PUBLISH_META_RAW:-unknown receipt error}"
fi
[[ ${#PUBLISH_META[@]} -eq 3 ]] || quarantine "publish receipt metadata is incomplete"
MP4_SRC="${PUBLISH_META[0]}"
WANT_SHA="${PUBLISH_META[1]}"
ENCODE_REVIEW_REQUIRED="${PUBLISH_META[2]}"
[[ -f "$MP4_SRC" ]] || quarantine "verified MP4 missing: $MP4_SRC"
GOT_SHA="$(sha256sum "$MP4_SRC" | cut -d' ' -f1)"
[[ "$GOT_SHA" == "$WANT_SHA" ]] || quarantine "MP4 changed since verify (sha mismatch) — re-run render phase"

# The encode-review decision was frozen when this render started. A later
# global streak cannot retroactively bless older/local bytes. When required,
# the actual file hash above closes the chain: source -> render task ->
# VERIFIED -> ENCODE-REVIEW -> bytes uploaded below.
case "$ENCODE_REVIEW_REQUIRED" in
  true)
    ENCODE_MARKER="$WS/qa/ENCODE-REVIEW.json"
    [[ -f "$ENCODE_MARKER" ]] \
      || quarantine "post-render encode review is still required — no qa/ENCODE-REVIEW.json"
    ENCODE_PROBLEM="$(python3 - "$MARKER" "$ENCODE_MARKER" <<'PY'
import json
import sys

try:
    verified = json.load(open(sys.argv[1], encoding="utf-8"))
    review = json.load(open(sys.argv[2], encoding="utf-8"))
except (OSError, json.JSONDecodeError, TypeError) as exc:
    print(f"encode-review receipt is unreadable ({exc})")
    raise SystemExit(1)
if not isinstance(verified, dict) or not isinstance(review, dict):
    print("encode-review receipt is not a JSON object")
    raise SystemExit(1)
if review.get("source_revision") != verified.get("source_revision"):
    print("encode review belongs to different source")
    raise SystemExit(1)
if review.get("sha256") != verified.get("sha256"):
    print("encode review belongs to different MP4 bytes")
    raise SystemExit(1)
if review.get("render_attempt") != verified.get("render_attempt"):
    print("encode review belongs to different render attempt")
    raise SystemExit(1)
if str(review.get("verdict", "")).strip().upper() != "PASS":
    findings = review.get("findings") or []
    detail = "; ".join(str(item) for item in findings if str(item).strip())
    print("encode review did not pass" + (f": {detail}" if detail else ""))
    raise SystemExit(1)
PY
)"
    ENCODE_RC=$?
    [[ "$ENCODE_RC" -eq 0 ]] \
      || quarantine "post-render encode review is not publishable — ${ENCODE_PROBLEM:-invalid receipt}" \
        "encode-review" "correct the named encode defect, re-render, and review the new MP4"
    ;;
  false) ;;
  *) quarantine "render receipt has no valid encode-review policy" ;;
esac

# Filed name = the ONE place a date is still added. A delivered MP4 records
# the date it was rendered — a fact about an event that happened once, frozen
# here and never restamped. stem.py owns it; never hand-slice the suffix.
RENDER_DATE="$(date +%F)"
SHIP_STEM="$(stem_delivered "$STEM" "$RENDER_DATE")" \
  || quarantine "could not build delivered name for '$STEM'"
FILED="${SHIP_STEM}.mp4"
DEST_DIR="$VP/renders-mp4/$PROGRAM"
mkdir -p "$DEST_DIR"
if [[ -f "$DEST_DIR/$FILED" ]]; then
  # A failed upload deliberately leaves its filed MP4 behind. On an authorized
  # retry, resume from it only when it is byte-for-byte the artifact that the
  # current VERIFIED marker approved; never overwrite a conflicting delivery.
  FILED_SHA="$(sha256sum "$DEST_DIR/$FILED" | awk '{print $1}')"
  [[ "$FILED_SHA" == "$WANT_SHA" ]] \
    || quarantine "filed MP4 conflicts with the current verified artifact: $FILED"
  echo "== reusing verified filed MP4: renders-mp4/$PROGRAM/$FILED"
else
  cp "$MP4_SRC" "$DEST_DIR/$FILED" || quarantine "could not file MP4"
  echo "== filed: renders-mp4/$PROGRAM/$FILED"
fi

echo "== wistia upload"
guarded "wistia-upload" bash "$REPO/scripts/wistia-upload.sh" "$DEST_DIR/$FILED" "$PROGRAM" \
  || quarantine "wistia-upload.sh failed" "wistia-upload" \
    "inspect $LAST_GUARD_LOG and correct Wistia credentials/access before retrying"
UPLOAD_OUT="$(cat "$LAST_GUARD_LOG")"
WURL="$(grep -o 'https://[a-z0-9.-]*wistia\.com/medias/[A-Za-z0-9]*' <<<"$UPLOAD_OUT" | head -1)"
[[ -n "$WURL" ]] || quarantine "no Wistia URL returned"

# From here on the video is LIVE: any failure must carry the URL into the
# quarantine record, keep the filed MP4, and skip the prune.
publish_quarantine() { quarantine "$1 — video IS live at $WURL (record by hand)"; }

# Machine ledger first: tab-separated, greppable. This is the resume key
# batch-status.sh reads. Column 1 is the BASE (title_program), not a dated
# stem — the date is a mutable state stamp and lives in its own column, so a
# dated key would silently stop matching after any restamp.
{
  [[ -f "$PUBTSV" ]] || printf '# base\tprogram\trender_date\twistia_url\n'
  printf '%s\t%s\t%s\t%s\n' "$BASE" "$PROGRAM" "$RENDER_DATE" "$WURL"
} >> "$PUBTSV" || publish_quarantine "could not write published.tsv"

# Human ledger row.
STEM="$SHIP_STEM" BASE="$BASE" PROGRAM="$PROGRAM" WURL="$WURL" FILED="$FILED" RENDER_DATE="$RENDER_DATE" \
LEDGER="$VP/lesson-scripts/refinement-log.md" python3 - <<'PY' || publish_quarantine "ledger update failed"
import os, re
from pathlib import Path

led = Path(os.environ["LEDGER"]); stem = os.environ["STEM"]
prog = os.environ["PROGRAM"]; url = os.environ["WURL"]
filed = os.environ["FILED"]; rdate = os.environ["RENDER_DATE"]
text = led.read_text(encoding="utf-8"); lines = text.splitlines()

# Match on the title prefix ALONE. The row was written when the script was
# refined and still carries the refine date, while `stem` now carries the
# render date — so matching on date too (as this did until 2026-07-28) would
# never hit after a restamp and would append a duplicate row every publish.
rest = os.environ["BASE"].split("_")
if rest and rest[-1] == prog:
    rest = rest[:-1]
prefix = "_".join(rest)

rendered_cell = f"{rdate} → `../renders-mp4/{prog}/{filed}` · Wistia {url}"
note = f"published {rdate} (AUTO-BATCH); local MP4 kept in renders-mp4/, workspace pruned in place and still editable"

# Rows abbreviate the stem (`title_..._DATE.txt`), so match on prefix.
hit = None
for i, ln in enumerate(lines):
    if not ln.startswith("|") or "`" not in ln:
        continue
    cell = ln.split("|")[1] if len(ln.split("|")) > 1 else ""
    if prefix and prefix in cell:
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

# The script leaves the queue only now, when the video is actually live. It
# keeps its name: published/ is a working folder, and a working artifact is
# named for its base alone. The render date is recorded in published.tsv's own
# column and on the filed MP4, which is where a date belongs. (Destination is
# BASE rather than STEM so a legacy dated script migrates on its way through.)
SRC_SCRIPT="$VP/lesson-scripts/$PROGRAM/ready/$STEM.txt"
DST_SCRIPT="$VP/lesson-scripts/$PROGRAM/published/$BASE.txt"
if [[ -f "$SRC_SCRIPT" ]]; then
  mkdir -p "$(dirname "$DST_SCRIPT")"
  git -C "$REPO" mv "$SRC_SCRIPT" "$DST_SCRIPT" 2>/dev/null || mv "$SRC_SCRIPT" "$DST_SCRIPT"
  echo "   script -> published/"
fi

# Regenerate the human-facing status doc in the same pass that publishes —
# it's a build artifact of published.tsv + ready/ + published/, never hand-edited,
# so it rides in this commit alongside the ledger rows it's derived from. This is
# one of four triggers; build-claim.sh, build-gate.sh and build-release.sh cover
# the build side, which had none until 2026-08-04 (which is why the doc could sit
# at 23/12 while disk said 21/14).
bash "$REPO/scripts/batch-status.sh" --write >/dev/null 2>&1 || true

# Commit is part of the publish contract — a failure here is a quarantine
# (with the URL), not a shrug, and the local MP4 must survive it.
guarded "git-add-publish" git -C "$REPO" add -A "$VP/lesson-scripts" "$VP/PIPELINE-STATUS.md" \
  || publish_quarantine "git add failed"
if git -C "$REPO" diff --cached --quiet; then
  publish_quarantine "nothing staged after publish — ledger writes did not land"
fi
guarded "git-commit-publish" git -C "$REPO" commit -q -m "ship($PROGRAM): $STEM → Wistia

$WURL

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" \
  || publish_quarantine "git commit failed"
echo "   committed"

# Prune the workspace (regenerable bulk only). archive-lesson.sh refuses to
# prune a workspace whose deliverable isn't filed — a check that now holds for
# good, since the filed MP4 is never removed.
bash "$REPO/scripts/archive-lesson.sh" "$STEM" --in-place || echo "   (prune skipped)"
echo "   local MP4 kept: renders-mp4/$PROGRAM/$FILED (gitignored backup)"
python3 "$RUN_STATE" record-success --workspace "$WS" --stem "$STEM" --phase publish \
  >/dev/null 2>&1 || true

echo
echo "PUBLISHED $STEM $WURL"
