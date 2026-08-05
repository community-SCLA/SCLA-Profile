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

# Shipping is a workspace-writing session too. Refresh one idempotent lease and
# release exactly this stem on every exit; TTL remains only a hard-crash backup.
RLOCK=""
LOCK=""
bash "$REPO/scripts/build-session.sh" arm "$STEM" >/dev/null
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

  # A pruned workspace (post-publish revisit, or the 3x stability loop) has no
  # node_modules; reinstall instead of false-quarantining "render failed".
  if [[ ! -d "$WS/node_modules" ]]; then
    echo "== npm install (workspace was pruned)"
    guarded "npm-install" bash -c 'cd "$1" && npm install --no-audit --no-fund' _ "$WS" \
      || quarantine "npm install failed" "dependency-install" \
        "inspect $LAST_GUARD_LOG and restore package access before retrying"
  fi

  # Stale MP4s from earlier renders must not survive into this run: publish
  # uploads via qa/VERIFIED, but a clean renders/ makes every state legible.
  rm -f "$WS/renders/"*.mp4 2>/dev/null
  rm -f "$WS/qa/VERIFIED" 2>/dev/null

  RENDER_DATE="$(date +%F)"
  if [[ "$RENDER_BACKEND" == "cloud" ]]; then
    # Output straight to the delivered name — the normalise loop below then
    # no-ops. npx resolves the workspace's own pinned hyperframes install
    # (node_modules guaranteed by the install block above). with-secrets.sh
    # injects HEYGEN_API_KEY, the credential cloud render authenticates with.
    OUT_MP4="$WS/renders/$(stem_delivered "$STEM" "$RENDER_DATE").mp4"
    mkdir -p "$WS/renders"
    echo "== cloud render: $STEM  (HeyGen-hosted; hard cap 60 min)"
    guarded "cloud-render" bash -c \
      'cd "$1" && timeout -k 30 3600 bash "$2" npx hyperframes cloud render . --quality high --output "$3" --idempotency-key "$4"' \
      _ "$WS" "$REPO/scripts/with-secrets.sh" "$OUT_MP4" "scla-${STEM}-${RENDER_DATE}" \
      || quarantine "cloud render failed or timed out (hyperframes cloud render)" \
        "cloud-render" "inspect $LAST_GUARD_LOG and the cloud credential/backend before retrying"
    [[ -s "$OUT_MP4" ]] || quarantine "cloud render exited 0 but no MP4 landed in renders/"
  else
    echo "== render: $STEM  (~7 min; hard cap 25)"
    guarded "local-render" bash -c 'cd "$1" && timeout -k 30 1500 npm run render' _ "$WS" \
      || quarantine "npm run render failed or timed out" "local-render" \
        "inspect $LAST_GUARD_LOG before retrying"
  fi

  # The HyperFrames CLI names its LOCAL output `<workspace-dir>_<date>_<clock>.mp4`,
  # so the renderer's own output violates the one-date rule by construction.
  # Normalise it here, BEFORE verify_render.py records the path and sha in
  # qa/VERIFIED — otherwise the marker pins the malformed name and publish
  # would upload it. The date used is the render date, which is what the name
  # is supposed to mean. (A cloud MP4 is already delivered-named; the loop
  # no-ops on it.)
  shopt -s nullglob
  for raw in "$WS/renders/"*.mp4; do
    want="$(stem_delivered "$(basename "$raw")" "$RENDER_DATE").mp4"
    [[ "$(basename "$raw")" == "$want" ]] && continue
    mv -f "$raw" "$WS/renders/$want" || quarantine "could not normalise render filename"
    echo "   render name normalised -> $want"
  done
  shopt -u nullglob

  echo "== verify_render"
  guarded "verify-render" python3 "$VP/render-qa/src/verify_render.py" "$WS" \
    || quarantine "the rendered MP4 failed post-render verification (verify_render.py)" \
      "verify-render" "inspect $LAST_GUARD_LOG, fix the named defect, then re-render"
  [[ -f "$WS/qa/VERIFIED" ]] || quarantine "verify passed but wrote no qa/VERIFIED marker"
  python3 "$RUN_STATE" record-success --workspace "$WS" --stem "$STEM" \
    --phase "$([[ "$RENDER_BACKEND" == "cloud" ]] && echo cloud-render || echo local-render)" \
    >/dev/null 2>&1 || true

  if ! python3 "$RUN_STATE" post-review-required >/dev/null 2>&1; then
    echo
    echo "READY_TO_PUBLISH $STEM — deterministic verification passed; " \
         "post-render encode review retired after three clean cloud renders"
    exit 0
  fi

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
MP4_SRC="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["mp4"])' "$MARKER")"
WANT_SHA="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sha256"])' "$MARKER")"
[[ -f "$MP4_SRC" ]] || quarantine "verified MP4 missing: $MP4_SRC"
GOT_SHA="$(sha256sum "$MP4_SRC" | cut -d' ' -f1)"
[[ "$GOT_SHA" == "$WANT_SHA" ]] || quarantine "MP4 changed since verify (sha mismatch) — re-run render phase"

# Filed name = the ONE place a date is still added. A delivered MP4 records
# the date it was rendered — a fact about an event that happened once, frozen
# here and never restamped. stem.py owns it; never hand-slice the suffix.
RENDER_DATE="$(date +%F)"
SHIP_STEM="$(stem_delivered "$STEM" "$RENDER_DATE")" \
  || quarantine "could not build delivered name for '$STEM'"
FILED="${SHIP_STEM}.mp4"
DEST_DIR="$VP/renders-mp4/$PROGRAM"
mkdir -p "$DEST_DIR"
[[ ! -f "$DEST_DIR/$FILED" ]] || quarantine "filed MP4 already exists: $FILED (same-day re-publish?)"
cp "$MP4_SRC" "$DEST_DIR/$FILED" || quarantine "could not file MP4"
echo "== filed: renders-mp4/$PROGRAM/$FILED"

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
