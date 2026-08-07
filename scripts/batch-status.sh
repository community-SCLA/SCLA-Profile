#!/usr/bin/env bash
# batch-status.sh — reconstruct the pipeline from disk alone.
#
# This is the resume key for an interrupted AUTO-BATCH run. It reads only the
# folders, the ledger and the logs; nothing depends on a previous session's
# context surviving. A stem is PUBLISHED if and only if it has a Wistia URL in
# published.tsv — that URL is committed in the same pass that publishes it, so
# there is never a window where work exists but isn't recorded.
#
# Usage:  bash scripts/batch-status.sh [--json | --write [path]]
#
# --write regenerates the human-facing status document (default
# projects/video-production/PIPELINE-STATUS.md) from the same disk-truth read
# as the terminal report. It is called by the pipeline itself at every stage
# transition — build-claim.sh (a build starts), build-release.sh (a build
# finishes), batch-ship.sh (quarantine, publish) — so the doc cannot go stale
# the way the hand-maintained status.md/PIPELINE-MAP.md deleted 2026-07-27 did
# (decisions/log.md). It is a build artifact, not a place to hand-edit.
#
# THE VOCABULARY (2026-08-07). Script folders identify queue lifecycle; build
# content and revision-bound receipts identify production phase. Exceptional
# conditions (stalled, rejected, stale receipt) are reported separately so an
# interruption never erases the last completed production phase:
#
#   lesson-scripts/<program>/inbox/<base>.txt      RAW        captured, not refined
#   lesson-scripts/<program>/ready/<base>.txt      READY      waiting to build
#   lesson-scripts/<program>/published/<base>.txt  PUBLISHED  live on Wistia
#   renders-hyperframes/<base>/                    authored phase + condition
#   renders-mp4/<program>/<base>_<date>.mp4        the delivered file
#
# Exception states are reported separately and never silently: NEEDS SCRIPT,
# STALLED, REJECTED, STRANDED, ORPHAN. Each one used to be invisible to at
# least one code path here, which is how a run could report "0 blocked" while a
# script carrying SCRIPT PENDING sat in the tree.
#
# Priority order is the drain order: highest-value programs ship first, so an
# interrupted run leaves the most important videos already live. This line is
# the ONE definition of priority in the repo — everything else cites it.
# Override with VIDEO_PRIORITY="slug-a slug-b ...".
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# The DATA root. Overridable so the state model can be graded against fixture
# trees instead of against whatever the live repo happens to hold today —
# render-qa/tests/test_pipeline_status.py builds one tree per state. The CODE
# root below is never overridden: a test must exercise the real stem.py.
VP="${VIDEO_VP_ROOT:-$REPO/projects/video-production}"
SRC="$REPO/projects/video-production/render-qa/src"

PRIORITY="${VIDEO_PRIORITY:-early-career-boost mid-career-momentum career-transitions entrepreneur-accelerator}"

MODE=text
OUTPATH="$VP/PIPELINE-STATUS.md"
case "${1:-}" in
  --json)  MODE=json ;;
  --write) MODE=write; [[ -n "${2:-}" ]] && OUTPATH="$2" ;;
esac

PRIORITY="$PRIORITY" LESSONS="$VP/lesson-scripts" SRC="$SRC" \
WS="$VP/renders-hyperframes" LEDGER="$VP/lesson-scripts/refinement-log.md" \
PUBTSV="$VP/lesson-scripts/published.tsv" QLOG="$VP/render-qa/quarantine.log" \
RUNSTATE="$VP/renders-hyperframes/_run/run.json" \
STALL_MINUTES="${VIDEO_STALL_MINUTES:-30}" \
MODE="$MODE" OUTPATH="$OUTPATH" python3 - <<'PY'
import hashlib, json, os, re, sys, time
from pathlib import Path

lessons = Path(os.environ["LESSONS"])
ws_root = Path(os.environ["WS"])
ledger  = Path(os.environ["LEDGER"])
pubtsv  = Path(os.environ["PUBTSV"])
qlog    = Path(os.environ["QLOG"])
runstate = Path(os.environ["RUNSTATE"])
mode    = os.environ["MODE"]
outpath = Path(os.environ["OUTPATH"])
priority = os.environ["PRIORITY"].split()
try:
    STALL_SEC = float(os.environ["STALL_MINUTES"]) * 60
except ValueError:
    STALL_SEC = 30 * 60
NOW = time.time()

try:
    active_run = json.loads(runstate.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    active_run = {}
run_items = {x.get("stem") for x in active_run.get("items", []) if x.get("stem")}

backend = active_run.get("backend", "local")
legacy_concurrency = int(active_run.get(
    "concurrency", 4 if backend == "cloud" else 3))
run_capacity = {
    "backend": backend,
    "authoring": int(active_run.get(
        "authoring_concurrency", 6 if backend == "cloud" else legacy_concurrency)),
    "tts": int(active_run.get("tts_concurrency", 2)),
    "cloud_render": int(active_run.get("cloud_render_concurrency", 2)),
    "cloud_render_max": int(active_run.get("cloud_render_max", 4)),
    "publish": int(active_run.get("publish_concurrency", 1)),
    "cloud_clean_streak": int(active_run.get("cloud_clean_streak", 0)),
}

ledger_text = ledger.read_text(encoding="utf-8", errors="replace") if ledger.exists() else ""

# Every comparison here is on BASE (title_program). Since 2026-07-29 a working
# artifact carries no date, so base_of() is usually the identity function — but
# it stays because the MP4 still carries its render date, refinement-log.md rows
# still quote legacy dated stems, and a workspace built before the change may
# survive. stem.py owns the rule; base() strips any trailing date/clock.
sys.path.insert(0, os.environ["SRC"])
from stem import base as stem_base, StemError
from workspace_revision import read_revision_marker, workspace_revision


approval_records = active_run.get("approvals") or {}
legacy_review = active_run.get("review") or {}


def approval_revision(stem: str):
    """The owner approval for this stem, bound to one source revision."""
    record = approval_records.get(stem)
    if isinstance(record, dict):
        revision = record.get("revision")
        if isinstance(revision, str):
            return revision
    elif isinstance(record, str):
        return record

    # Transitional read support for revision-aware legacy review records. Old
    # stem-only approvals intentionally do not count: they cannot prove which
    # cut the owner watched.
    if stem not in set(legacy_review.get("stems") or []):
        return None
    revisions = legacy_review.get("revisions") or {}
    revision = revisions.get(stem) if isinstance(revisions, dict) else None
    if not revision and len(legacy_review.get("stems") or []) == 1:
        revision = legacy_review.get("revision")
    return revision if isinstance(revision, str) else None

def base_of(name: str) -> str:
    try:
        return stem_base(name)
    except StemError:
        return name          # undated/legacy name: compare it as-is


def ago(seconds: float) -> str:
    m = int(seconds // 60)
    if m < 1:
        return "just now"
    if m < 90:
        return f"{m} min ago"
    h = m / 60
    if h < 48:
        return f"{h:.0f} h ago"
    return f"{h / 24:.0f} days ago"


def at_utc(epoch: float) -> str:
    """Stable timestamp for generated files; relative ages make lint flap."""
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(epoch))


# ── the ledgers ──────────────────────────────────────────────────────────────
# Primary key: published.tsv — base, written and committed by batch-ship.sh in
# the same pass that uploads. The ledger scan below is a fallback for lessons
# published before the tsv existed (rows abbreviate the stem, so that matching
# is best-effort — the tsv is the contract).
published, media_ids, published_rows = set(), set(), []
if pubtsv.exists():
    for line in pubtsv.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) >= 4:
            published.add(cols[0])
            published_rows.append({"base": cols[0], "program": cols[1],
                                    "render_date": cols[2], "wistia_url": cols[3]})
            m = re.search(r'wistia\.com/medias/(\w+)', cols[3])
            if m:
                media_ids.add(m.group(1))
for line in ledger_text.splitlines():
    ids = re.findall(r'wistia\.com/medias/(\w+)', line)
    if not ids:
        continue
    media_ids.update(ids)
    for m in re.finditer(r'[A-Za-z0-9][\w.-]*_\d{4}-\d{2}-\d{2}', line):
        published.add(base_of(m.group(0)))

# Quarantine: a row is an INCIDENT, never deleted — that file is the trail. A
# row is RESOLVED when its base later published, or when a later row in the log
# marks it resolved. Until 2026-08-04 quarantines were suppressed only by
# accident (the published branch happened to run first), so a rejected cut that
# never published could show up as an ordinary unbuilt lesson.
quarantined, resolved_rows = {}, set()
if qlog.exists():
    for line in qlog.read_text(encoding="utf-8", errors="replace").splitlines():
        cols = line.split("\t")
        if len(cols) < 4:
            continue
        when, stem, prog, reason = cols[0], cols[1], cols[2], cols[3]
        if reason.strip().lower().startswith("resolved"):
            resolved_rows.add(base_of(stem))
            continue
        quarantined[base_of(stem)] = {"when": when, "program": prog, "reason": reason}
for b in list(quarantined):
    if b in published or b in resolved_rows:
        del quarantined[b]

# ── the workspaces ───────────────────────────────────────────────────────────
# Workspaces are keyed by BASE, never joined on a path: a workspace can carry a
# legacy build date while its script carries a refine date.
SKIP_DIRS = {"node_modules", ".git", ".thumbnails", ".waveform-cache",
             "source-revisions"}

def newest_mtime(d: Path) -> float:
    newest = 0.0
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for name in files:
            try:
                m = os.stat(os.path.join(root, name)).st_mtime
            except OSError:
                continue
            if m > newest:
                newest = m
    return newest or d.stat().st_mtime


def journal(ws_dir: Path):
    """The last COMPLETED step, from the workspace's own append-only journal.

    .build-log.tsv is evidence, not a status field: build-claim.sh opens it and
    each step appends one `timestamp \\t step \\t detail` row. Nothing ever
    rewrites a row, so it cannot lie the way a frontmatter status field would —
    and an interrupted build stops leaving no trace of where it got to, which
    is the whole reason this exists (2026-08-04)."""
    f = ws_dir / ".build-log.tsv"
    if not f.is_file():
        return None
    rows = [ln.split("\t") for ln in
            f.read_text(encoding="utf-8", errors="replace").splitlines()
            if ln.strip() and not ln.startswith("#")]
    if not rows:
        return None
    # claim/resume/release are control events, not completed production work.
    # Reporting "release" hid the useful answer (for example, "gate") after
    # every clean handoff.
    meaningful = [row for row in rows
                  if len(row) > 1 and row[1].strip().lower()
                  not in {"claim", "resume", "release"}]
    if not meaningful:
        return None
    last = meaningful[-1]
    when = 0.0
    try:
        when = time.mktime(time.strptime(last[0], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    except (ValueError, IndexError):
        when = f.stat().st_mtime
    return {"step": last[1] if len(last) > 1 else "?",
            "detail": last[2] if len(last) > 2 else "",
            "when": when, "rows": len(rows)}


def ws_lane(ws_dir: Path) -> str:
    """Which authoring lane this workspace is on — detected, never assumed.

    Until 2026-08-04 every probe below assumed the TEMPLATE lane, so a freeform
    workspace (no scenes.json by design — the HTML is the authored artifact)
    reported as "build folder exists but holds no scene plan — nothing authored
    yet", with a next-action of *restart the build*. That advice collides with
    the mkdir build lock and, taken literally, discards finished narration."""
    if (ws_dir / "scenes.json").is_file():
        return "template"
    if (ws_dir / "design.md").is_file() or (ws_dir / "audio_request.json").is_file():
        return "freeform"
    return "scaffold"


def timed_html(ws_dir: Path) -> bool:
    try:
        html = (ws_dir / "index.html").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(set(re.findall(r'data-start="([^"]*)"', html)) - {"0"})


def audio_ready(ws_dir: Path) -> bool:
    """Trust the audio manifest, not a builder-chosen beat-id prefix."""
    try:
        meta = json.loads((ws_dir / "audio_meta.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    voices = meta.get("voices")
    if not isinstance(voices, list) or not voices:
        return False
    return all(isinstance(v, dict) and v.get("path") and
               (ws_dir / v["path"]).is_file() for v in voices)


def read_json_object(path: Path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def verdict(value, *keys):
    for key in keys:
        answer = value.get(key)
        if isinstance(answer, str):
            return answer.strip().upper()
    return None


def receipt_mp4(ws_dir: Path, value):
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else ws_dir / path


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def state_record(phase, state, nxt, revision, *, condition=None,
                 gate_revision=None, visual_revision=None, render_revision=None,
                 render_mp4=None, render_completed_at=None,
                 render_completed_sha=None, render_attempt=None,
                 verified_sha=None,
                 encode_required=None,
                 encode_revision=None, encode_sha=None, findings=None,
                 stage=None):
    return {
        "phase": phase,
        "condition": condition,
        "stage": stage or phase,
        "state": state,
        "next": nxt,
        "revision": revision,
        "gate_revision": gate_revision,
        "visual_review_revision": visual_revision,
        "render_revision": render_revision,
        "render_mp4": render_mp4,
        "render_completed_at": render_completed_at,
        "render_completed_sha256": render_completed_sha,
        "render_attempt": render_attempt,
        "verified_sha256": verified_sha,
        "encode_review_required": encode_required,
        "encode_review_revision": encode_revision,
        "encode_review_sha256": encode_sha,
        "findings": list(findings or []),
    }


def ws_state(ws_dir, stem=None):
    """Content-bound phase plus an independent exceptional condition."""
    # Scope and recovery both enter through run.sh. Never delete a workspace to
    # get around its lock; cached plans and narration are resume state.
    START = ("select only this lesson: `bash projects/video-production/run.sh "
             "produce --stem {stem}`; then continue `/render-lessons BUILD {stem}`")
    RESUME = ("resume this existing workspace in place through the control plane: "
              "`bash projects/video-production/run.sh resume`; continue only {stem}. "
              "Do not delete or rebuild completed work")
    SELECT_RESUME = ("put this existing lesson in scope with `bash projects/video-production/"
                     "run.sh produce --stem {stem}`, then resume its current workspace in "
                     "place; do not delete or rebuild completed work")
    CONTINUE = RESUME if stem in run_items else SELECT_RESUME
    if ws_dir is None:
        return state_record("scaffolded", "no build folder", START, None)

    try:
        revision = workspace_revision(ws_dir)
    except (OSError, ValueError) as exc:
        finding = str(exc)
        return state_record(
            "needs-revision",
            f"the current source cannot be given a stable revision — {finding}",
            "fix the render-affecting input named in the finding, then rerun the gate",
            None,
            condition="invalid-source",
            findings=[finding],
        )

    render_start_path = ws_dir / "qa" / "RENDER-START.json"
    render_start = read_json_object(render_start_path) if render_start_path.is_file() else None
    render_revision = (render_start or {}).get("source_revision")
    render_mp4 = receipt_mp4(ws_dir, (render_start or {}).get("mp4"))
    render_completed_at = (render_start or {}).get("completed_at")
    render_completed_sha = (render_start or {}).get("completed_sha256")
    render_completed_bytes = (render_start or {}).get("completed_bytes")
    render_attempt = (render_start or {}).get("attempt")
    encode_required = (render_start or {}).get("encode_review_required")
    verified_path = ws_dir / "qa" / "VERIFIED"
    if verified_path.is_file():
        verified = read_json_object(verified_path) or {}
        verified_revision = verified.get("source_revision")
        verified_mp4 = receipt_mp4(ws_dir, verified.get("mp4"))
        verified_sha = verified.get("sha256")
        verified_required = verified.get("encode_review_required")
        verified_attempt = verified.get("render_attempt")
        if (not revision or verified_revision != revision
                or render_revision != revision):
            return state_record(
                "composed",
                "the render belongs to different source — the current cut is not rendered",
                "rerun the current-source gate, visual review, approval, and render",
                revision,
                condition="stale-render",
                gate_revision=read_revision_marker(ws_dir),
                render_revision=render_revision,
                render_mp4=str(render_mp4) if render_mp4 else None,
                render_completed_at=render_completed_at,
                render_completed_sha=render_completed_sha,
                render_attempt=render_attempt,
                verified_sha=verified_sha,
                encode_required=(encode_required
                                 if isinstance(encode_required, bool) else None),
            )
        receipt_chain_ok = (
            isinstance(encode_required, bool)
            and verified_required is encode_required
            and isinstance(render_attempt, int)
            and render_attempt >= 1
            and verified_attempt == render_attempt
            and isinstance(render_completed_at, str)
            and bool(render_completed_at)
            and isinstance(render_completed_bytes, int)
            and render_completed_sha == verified_sha
            and render_mp4 is not None
            and verified_mp4 is not None
            and render_mp4.resolve() == verified_mp4.resolve()
        )
        if not receipt_chain_ok:
            return state_record(
                "awaiting-verification",
                "the render-start and verification receipts do not bind one exact cut",
                "resume the current workspace; re-render only if the recorded MP4 is gone",
                revision,
                condition="stale-render",
                gate_revision=read_revision_marker(ws_dir),
                render_revision=render_revision,
                render_mp4=str(render_mp4) if render_mp4 else None,
                render_completed_at=render_completed_at,
                render_completed_sha=render_completed_sha,
                render_attempt=render_attempt,
                verified_sha=verified_sha,
                encode_required=(encode_required
                                 if isinstance(encode_required, bool) else None),
            )
        if not verified_mp4.is_file():
            return state_record(
                "awaiting-verification",
                "the verified MP4 is missing from disk",
                "resume this workspace in place and re-render the missing artifact",
                revision,
                condition="invalid-render",
                gate_revision=read_revision_marker(ws_dir),
                render_revision=render_revision,
                render_mp4=str(verified_mp4),
                render_completed_at=render_completed_at,
                render_completed_sha=render_completed_sha,
                render_attempt=render_attempt,
                verified_sha=verified_sha,
                encode_required=encode_required,
            )
        try:
            actual_sha = sha256_file(verified_mp4)
            actual_bytes = verified_mp4.stat().st_size
        except OSError:
            actual_sha = None
            actual_bytes = None
        if (not isinstance(verified_sha, str) or actual_sha != verified_sha
                or actual_sha != render_completed_sha
                or actual_bytes != render_completed_bytes):
            return state_record(
                "awaiting-verification",
                "the MP4 bytes changed after verification",
                "re-render and verify the current source before review or publish",
                revision,
                condition="invalid-render",
                gate_revision=read_revision_marker(ws_dir),
                render_revision=render_revision,
                render_mp4=str(verified_mp4),
                render_completed_at=render_completed_at,
                render_completed_sha=render_completed_sha,
                render_attempt=render_attempt,
                verified_sha=verified_sha,
                encode_required=encode_required,
            )
        if encode_required:
            encode_path = ws_dir / "qa" / "ENCODE-REVIEW.json"
            if not encode_path.is_file():
                return state_record(
                    "awaiting-encode-review",
                    "this exact verified MP4 still requires post-render review",
                    "review the encoded video, then record `bash projects/video-production/"
                    "run.sh encode-review {stem} PASS` (or FAIL with findings)",
                    revision,
                    gate_revision=read_revision_marker(ws_dir),
                    render_revision=render_revision,
                    render_mp4=str(verified_mp4),
                    render_attempt=render_attempt,
                    verified_sha=verified_sha,
                    encode_required=True,
                )
            encode = read_json_object(encode_path)
            if encode is None:
                return state_record(
                    "awaiting-encode-review",
                    "the post-render review receipt is unreadable",
                    "repeat the encode review for this verified MP4",
                    revision,
                    condition="invalid-encode-review",
                    gate_revision=read_revision_marker(ws_dir),
                    render_revision=render_revision,
                    render_mp4=str(verified_mp4),
                    render_attempt=render_attempt,
                    verified_sha=verified_sha,
                    encode_required=True,
                )
            encode_revision = encode.get("source_revision")
            encode_sha = encode.get("sha256")
            encode_attempt = encode.get("render_attempt")
            encode_findings = [x for x in (encode.get("findings") or [])
                               if isinstance(x, str) and x.strip()]
            if (encode_revision != revision or encode_sha != verified_sha
                    or encode_attempt != render_attempt):
                return state_record(
                    "awaiting-encode-review",
                    "the post-render review belongs to different source or MP4 bytes",
                    "repeat the encode review for the current verified MP4",
                    revision,
                    condition="stale-encode-review",
                    gate_revision=read_revision_marker(ws_dir),
                    render_revision=render_revision,
                    render_mp4=str(verified_mp4),
                    render_attempt=render_attempt,
                    verified_sha=verified_sha,
                    encode_required=True,
                    encode_revision=encode_revision,
                    encode_sha=encode_sha,
                )
            encode_verdict = verdict(encode, "verdict", "VERDICT")
            if encode_verdict == "FAIL":
                return state_record(
                    "awaiting-encode-review",
                    "post-render encode review rejected this verified MP4",
                    "correct the listed encode defect, re-render, and review the new MP4",
                    revision,
                    condition="rejected",
                    gate_revision=read_revision_marker(ws_dir),
                    render_revision=render_revision,
                    render_mp4=str(verified_mp4),
                    render_attempt=render_attempt,
                    verified_sha=verified_sha,
                    encode_required=True,
                    encode_revision=encode_revision,
                    encode_sha=encode_sha,
                    findings=encode_findings or ["encode review returned FAIL"],
                    stage="rejected",
                )
            if encode_verdict != "PASS":
                return state_record(
                    "awaiting-encode-review",
                    "the post-render review receipt has no PASS/FAIL verdict",
                    "repeat the encode review for the current verified MP4",
                    revision,
                    condition="invalid-encode-review",
                    gate_revision=read_revision_marker(ws_dir),
                    render_revision=render_revision,
                    render_mp4=str(verified_mp4),
                    render_attempt=render_attempt,
                    verified_sha=verified_sha,
                    encode_required=True,
                    encode_revision=encode_revision,
                    encode_sha=encode_sha,
                )
        return state_record(
            "rendered",
            ("the current source and MP4 bytes are verified; required encode review passed"
             if encode_required else
             "the current source and MP4 bytes are verified; this render was stamped "
             "after encode review retired"),
            "publish it: `bash projects/video-production/run.sh ship {stem} --publish`",
            revision,
            gate_revision=read_revision_marker(ws_dir),
            render_revision=render_revision,
            render_mp4=str(verified_mp4),
            render_completed_at=render_completed_at,
            render_completed_sha=render_completed_sha,
            render_attempt=render_attempt,
            verified_sha=verified_sha,
            encode_required=encode_required,
            encode_revision=(encode.get("source_revision") if encode_required else None),
            encode_sha=(encode.get("sha256") if encode_required else None),
        )

    if render_start_path.is_file():
        if (not render_start or render_revision != revision
                or not isinstance(encode_required, bool)
                or not isinstance(render_attempt, int) or render_attempt < 1):
            return state_record(
                "composed",
                "the render-start receipt is unreadable or belongs to different source",
                "rerun the content-bound gates before starting a new render",
                revision,
                condition="stale-render",
                gate_revision=read_revision_marker(ws_dir),
                render_revision=render_revision,
                render_mp4=str(render_mp4) if render_mp4 else None,
            )
        render_actual_sha = None
        render_actual_bytes = None
        if render_mp4 and render_mp4.is_file():
            try:
                render_actual_sha = sha256_file(render_mp4)
                render_actual_bytes = render_mp4.stat().st_size
            except OSError:
                pass
        render_complete = (
            isinstance(render_completed_at, str)
            and bool(render_completed_at)
            and isinstance(render_completed_bytes, int)
            and render_actual_sha == render_completed_sha
            and render_actual_bytes == render_completed_bytes
        )
        if render_complete:
            return state_record(
                "awaiting-verification",
                "the renderer completed a current-source MP4; verification was interrupted",
                "resume `bash projects/video-production/run.sh ship {stem}`; it will verify "
                "this MP4 in place without rendering it again",
                revision,
                gate_revision=read_revision_marker(ws_dir),
                render_revision=render_revision,
                render_mp4=str(render_mp4),
                render_completed_at=render_completed_at,
                render_completed_sha=render_completed_sha,
                render_attempt=render_attempt,
                encode_required=encode_required,
            )
        return state_record(
            "interrupted-render",
            "render started, but no atomic completion receipt matches the current MP4 bytes",
            "resume `bash projects/video-production/run.sh ship {stem}`; it will discard "
            "partial output and render this exact source again",
            revision,
            condition="incomplete-render",
            gate_revision=read_revision_marker(ws_dir),
            render_revision=render_revision,
            render_mp4=str(render_mp4) if render_mp4 else None,
            render_completed_at=render_completed_at,
            render_completed_sha=render_completed_sha,
            render_attempt=render_attempt,
            encode_required=encode_required,
        )

    marker_path = ws_dir / "qa" / "PREFLIGHT-OK"
    if marker_path.is_file():
        gate_revision = read_revision_marker(ws_dir)
        if not revision or gate_revision != revision:
            return state_record(
                "composed",
                "the gate receipt is legacy or belongs to different source",
                "rerun `bash scripts/build-gate.sh {stem}` on the current composition",
                revision,
                condition="stale-gate",
                gate_revision=gate_revision,
            )

        visual_path = ws_dir / "qa" / "VISUAL-REVIEW.json"
        if not visual_path.is_file():
            return state_record(
                "awaiting-visual-review",
                "gate-clean for this source; combined visual review has not been recorded",
                "run the combined visual review and save `qa/VISUAL-REVIEW.json`",
                revision,
                gate_revision=gate_revision,
            )

        visual = read_json_object(visual_path)
        if visual is None:
            return state_record(
                "awaiting-visual-review",
                "the visual-review receipt is unreadable",
                "repeat the combined visual review for the current source",
                revision,
                condition="invalid-visual-review",
                gate_revision=gate_revision,
            )
        visual_revision = visual.get("source_revision") or visual.get("revision")
        if visual_revision != revision:
            return state_record(
                "awaiting-visual-review",
                "the visual review belongs to different source",
                "repeat the combined visual review for the current source",
                revision,
                condition="stale-visual-review",
                gate_revision=gate_revision,
                visual_revision=visual_revision,
            )

        blocking = verdict(visual, "blocking_defect", "BLOCKING_DEFECT")
        taste = verdict(visual, "taste", "TASTE")
        recommendation = verdict(visual, "recommendation", "RECOMMENDATION")
        if blocking == "PASS" and taste == "ALIVE" and recommendation == "PROCEED":
            if approval_revision(stem) == revision:
                return state_record(
                    "approved",
                    "this exact cut passed visual review and has owner approval",
                    "render it: `bash projects/video-production/run.sh ship {stem}`",
                    revision,
                    gate_revision=gate_revision,
                    visual_revision=visual_revision,
                )
            return state_record(
                "needs-review",
                "mechanical and visual reviews passed; ready for your review — no MP4 yet",
                "watch this cut, then approve it independently with "
                "`bash projects/video-production/run.sh approve {stem}`",
                revision,
                gate_revision=gate_revision,
                visual_revision=visual_revision,
            )
        if blocking == "FAIL" or taste == "FLAT" or recommendation == "REVISE":
            return state_record(
                "needs-revision",
                f"visual review requires revision ({blocking or '?'}/"
                f"{taste or '?'}/{recommendation or '?'})",
                "revise this workspace, then rerun the gate and combined visual review",
                revision,
                gate_revision=gate_revision,
                visual_revision=visual_revision,
            )
        return state_record(
            "awaiting-visual-review",
            "the visual-review receipt does not contain a complete verdict",
            "repeat the combined visual review for the current source",
            revision,
            condition="invalid-visual-review",
            gate_revision=gate_revision,
            visual_revision=visual_revision,
        )

    lane = ws_lane(ws_dir)
    if lane == "scaffold":
        return state_record(
            "scaffolded",
            "workspace claimed from the scaffold; no plan and no design authored yet",
            START,
            revision,
        )
    if lane == "freeform":
        # design.md -> per-beat wavs -> timing.json -> timed index.html
        if not audio_ready(ws_dir):
            return state_record(
                "planned", "freeform design written; narration not yet synthesized",
                CONTINUE, revision)
        if not (ws_dir / "timing.json").is_file():
            return state_record(
                "untimed", "freeform narration synthesized; clip timings not yet computed",
                CONTINUE, revision)
        if not timed_html(ws_dir):
            return state_record(
                "untimed", "freeform timings computed but never applied to the composition",
                CONTINUE, revision)
        return state_record(
            "composed", "freeform composition timed and ready — the gate has not run yet",
            CONTINUE, revision)
    # template lane
    if not (ws_dir / "assets" / "voice" / "narration.wav").is_file():
        return state_record(
            "planned", "scene plan written; narration voice-over not yet synthesized",
            CONTINUE, revision)
    if not (ws_dir / "index.html").is_file():
        return state_record(
            "uncompiled", "narration synthesized; the composition was never compiled",
            CONTINUE, revision)
    if not timed_html(ws_dir):
        return state_record(
            "untimed", "composition compiled, but scene timings were never applied",
            CONTINUE, revision)
    return state_record(
        "composed", "HyperFrames composition ready — the gate has not run yet",
        CONTINUE, revision)


HUMAN_PHASES = {"rendered", "awaiting-encode-review",
                "awaiting-visual-review", "needs-revision", "needs-review",
                "approved"}

ws_by_base = {}
if ws_root.is_dir():
    for d in sorted(ws_root.iterdir()):
        if d.is_dir() and not d.name.startswith((".", "_")):
            ws_by_base[base_of(d.name)] = d

# ── blocked scripts ──────────────────────────────────────────────────────────
# Detected from content, not a hand-list, so a fixed script re-enters the queue
# automatically with no bookkeeping. Scanned in BOTH inbox/ and ready/: the
# scan used to cover the render queue only, so a raw script carrying SCRIPT
# PENDING was reported as nothing at all.
BLOCK_PATTERNS = [
    (re.compile(r'TODO:\s*needs input', re.I),          "TODO: needs input"),
    (re.compile(r'SCRIPT PENDING',      re.I),          "SCRIPT PENDING"),
]

def blocked_reason(p: Path):
    """(label, detail) — the marker AND the paragraph it sits in.

    The script always states what it needs ("the RAW names the four parts of the
    bullet formula but never defines what each one means"); echoing only the
    marker word threw that away and left the owner a status doc that said
    "needs input" without ever saying which input (2026-07-31).
    """
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for rx, label in BLOCK_PATTERNS:
        for i, line in enumerate(lines):
            if not rx.search(line):
                continue
            para = [line.strip()]
            for nxt in lines[i + 1:]:          # the marker's own paragraph
                if not nxt.strip():
                    break
                para.append(nxt.strip())
            detail = re.sub(r'^\W*(TODO:\s*needs input|SCRIPT PENDING)\W*', '',
                            " ".join(para), flags=re.I).strip()
            return (label, detail)
    return None


programs = sorted([d.name for d in lessons.iterdir() if d.is_dir()])
ordered  = [p for p in priority if p in programs] + [p for p in programs if p not in priority]

report = []
totals = {"raw": 0, "needs_script": 0, "queued": 0, "building": 0, "stalled": 0,
          "awaiting_visual_review": 0, "awaiting_encode_review": 0,
          "needs_revision": 0,
          "needs_review": 0, "approved": 0, "rendered": 0, "rejected": 0,
          "stale_gate": 0, "stale_render": 0, "invalid_render": 0,
          "incomplete_render": 0,
          "stale_visual_review": 0,
          "stale_encode_review": 0,
          "stranded": 0, "published": 0, "orphan": 0}
known_bases = set()


def failure_status(ws_dir: Path):
    """Return (unresolved failure, resolved timestamp) from durable evidence."""
    path = ws_dir / "qa" / "failure.json"
    if not path.is_file():
        return None, None
    failure = read_json_object(path)
    if not failure:
        return None, None
    resolved_at = failure.get("resolved_at")
    if isinstance(resolved_at, str) and resolved_at:
        return None, resolved_at
    return failure, None

for prog in ordered:
    pdir = lessons / prog
    raw, needs_script, queued, in_flight, stranded = [], [], [], [], []

    for stage_dir in ("inbox", "ready"):
        d = pdir / stage_dir
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.txt")):
            stem = f.stem
            known_bases.add(base_of(stem))
            if base_of(stem) in published:
                continue
            why = blocked_reason(f)
            if why:
                needs_script.append({"stem": stem, "folder": stage_dir,
                                     "marker": why[0], "detail": why[1]})
                totals["needs_script"] += 1
                continue
            if stage_dir == "inbox":
                raw.append(stem)
                totals["raw"] += 1
                continue
            # ready/: built or not?
            ws_dir = ws_by_base.get(base_of(stem))
            if ws_dir is None:
                queued.append(stem)
                totals["queued"] += 1
                continue
            status = ws_state(ws_dir, stem)
            phase = status["phase"]
            condition = status["condition"]
            stage = status["stage"]
            state = status["state"]
            nxt = status["next"]
            findings, jrn = list(status["findings"]), journal(ws_dir)
            q = quarantined.get(base_of(stem))
            failure, failure_resolved_at = failure_status(ws_dir)
            # run.sh retry resolves failure.json but deliberately leaves the
            # append-only qlog incident. A resolution suppresses only an older
            # incident; a later quarantine remains actionable.
            if (q and failure_resolved_at
                    and isinstance(q.get("when"), str)
                    and q["when"] <= failure_resolved_at):
                q = None
            if q or failure or condition == "rejected":
                # The log records which guard said no, never what it said. Ask
                # the guard again — batch-ship.sh keeps the workspace precisely
                # so the failure is reproducible. "verify_render.py non-zero" is
                # a citation, not a reason.
                condition = "rejected"
                stage = "rejected"
                if q or failure:
                    incident_reason = ((failure or {}).get("reason")
                                       or (failure or {}).get("error_class")
                                       or (q or {}).get("reason")
                                       or "an unresolved build failure")
                    state = f"a build or release gate rejected this cut — {incident_reason}"
                    reason_file = ws_dir / "qa" / "quarantine-reason.txt"
                    if failure:
                        log = failure.get("log")
                        findings = ([f"full command output: {log}"] if log else [])
                        nxt = failure.get("next_action") or (
                            f"authorize a deliberate retry: `bash projects/video-production/run.sh "
                            f"retry {stem} --reason \"failure corrected\"`")
                    elif reason_file.is_file():
                        txt = reason_file.read_text(encoding="utf-8", errors="replace")
                        findings = [re.sub(r'^-\s*', '', ln.strip()) for ln in txt.splitlines()
                                    if re.match(r'\s+-\s+\[', ln)][:4]
                        nxt = ("read the full failure in "
                               f"`renders-hyperframes/{ws_dir.name}/qa/quarantine-reason.txt`, "
                               "fix the named cause in this workspace, then resume in place")
                    elif "cloud render" in q["reason"].lower():
                        nxt = ("inspect the cloud credential/backend, then authorize one "
                               f"deliberate retry: `bash projects/video-production/run.sh retry "
                               f"{stem} --reason \"cloud path corrected\"`")
                    else:
                        nxt = ("inspect and correct the recorded cause, then authorize one "
                               f"deliberate retry: `bash projects/video-production/run.sh retry "
                               f"{stem} --reason \"cause corrected\"`")
                totals["rejected"] += 1
            elif phase in HUMAN_PHASES:
                key = {"awaiting-encode-review": "awaiting_encode_review",
                       "awaiting-visual-review": "awaiting_visual_review",
                       "needs-revision": "needs_revision",
                       "needs-review": "needs_review", "approved": "approved",
                       "rendered": "rendered"}[phase]
                totals[key] += 1
                if condition == "stale-visual-review":
                    totals["stale_visual_review"] += 1
                if condition == "stale-encode-review":
                    totals["stale_encode_review"] += 1
            else:
                # Incomplete. STALLED is report-only and never kills anything.
                # Its next action resumes the recorded phase in the existing
                # workspace; replacing it would discard the recovery evidence.
                idle = NOW - newest_mtime(ws_dir)
                if condition in {"stale-gate", "stale-render", "invalid-render",
                                 "incomplete-render"}:
                    totals[condition.replace("-", "_")] += 1
                    totals["building"] += 1
                elif idle > STALL_SEC:
                    # STALLED is a statement about TIME, not a different job: the
                    # action stays whatever the stage needs, because deleting a
                    # workspace that holds narration is not a resume.
                    condition = "stalled"
                    stage = "stalled"
                    totals["stalled"] += 1
                else:
                    totals["building"] += 1
            touched = newest_mtime(ws_dir)
            in_flight.append({
                "stem": stem, "stage": stage, "phase": phase,
                "condition": condition, "revision": status["revision"],
                "gate_revision": status["gate_revision"],
                "visual_review_revision": status["visual_review_revision"],
                "render_revision": status["render_revision"],
                "render_mp4": status["render_mp4"],
                "render_completed_at": status["render_completed_at"],
                "render_completed_sha256": status["render_completed_sha256"],
                "render_attempt": status["render_attempt"],
                "verified_sha256": status["verified_sha256"],
                "encode_review_required": status["encode_review_required"],
                "encode_review_revision": status["encode_review_revision"],
                "encode_review_sha256": status["encode_review_sha256"],
                "lane": ws_lane(ws_dir),
                "workspace": ws_dir.name, "state": state, "findings": findings,
                "idle": ago(NOW - touched), "last_touched": at_utc(touched),
                "last_completed_phase": jrn["step"] if jrn else None,
                "journal": (f"last completed **{jrn['step']}** at {at_utc(jrn['when'])}"
                            if jrn else None),
                "next": nxt.replace("{stem}", stem).replace("{program}", prog)
                           .replace("{ws}", ws_dir.name)})

    # published/ without a published.tsv row = STRANDED mid-pipeline (upload or
    # commit did not complete). This bucket is what makes an interrupted batch
    # resumable rather than merely restartable.
    pub = pdir / "published"
    if pub.is_dir():
        for f in sorted(pub.glob("*.txt")):
            stem = f.stem
            known_bases.add(base_of(stem))
            if base_of(stem) in published:
                continue
            ws_dir = ws_by_base.get(base_of(stem))
            workspace_status = ws_state(ws_dir, stem) if ws_dir else None
            verified = bool(workspace_status and workspace_status["phase"] == "rendered"
                            and not workspace_status["condition"])
            state = ("build folder present" if ws_dir else
                     "NO build folder — the MP4 cannot be re-made from here")
            if verified:
                state += ", MP4 verified and awaiting publish"
            if base_of(stem) in quarantined:
                state += f", rejected by a gate ({quarantined[base_of(stem)]['reason']})"
            nxt = (f"finish the publish: `bash projects/video-production/run.sh ship {stem} --publish`"
                   if verified else
                   f"re-run the tail: `bash projects/video-production/run.sh ship {stem}`")
            stranded.append({"stem": stem, "state": state, "next": nxt})
            totals["stranded"] += 1

    report.append({"program": prog, "raw": raw, "needs_script": needs_script,
                   "queued": queued, "in_flight": in_flight, "stranded": stranded})

# ORPHAN — a workspace whose base matches no script in any program. Before
# 2026-08-04 these were invisible to every code path here: the scan only ever
# looked up workspaces BY script, so a workspace with no script was never
# looked up at all.
orphans = []
for base, d in sorted(ws_by_base.items()):
    if base in known_bases or base in published:
        continue
    status = ws_state(d, d.name)
    touched = newest_mtime(d)
    orphans.append({"workspace": d.name, "stage": status["stage"],
                    "phase": status["phase"], "condition": status["condition"],
                    "revision": status["revision"], "state": status["state"],
                    "idle": ago(NOW - touched), "last_touched": at_utc(touched)})
    totals["orphan"] += 1

# Distinct Wistia media = videos actually live, independent of folder state.
totals["published"] = len(media_ids)

if mode == "json":
    print(json.dumps({"run": run_capacity, "priority": ordered,
                       "totals": totals, "programs": report,
                       "orphans": orphans, "published": published_rows}, indent=2))
    sys.exit(0)

# ─────────────────────────────────────────────────────────────────────────────
if mode == "write":
    lines = []
    a = lines.append
    a("# Video Production — Pipeline Status")
    a("")
    a("**Generated file — do not hand-edit.** Overwritten by `scripts/batch-status.sh "
      "--write` at every build/quarantine/publish step; a hand edit here is lost on the "
      "next run and this file cannot go stale the way the old `status.md` did (deleted "
      "2026-07-27, see `decisions/log.md`) because it is never the thing anyone edits — "
      "only ever the thing that gets regenerated from the folders + `published.tsv`.")
    a("")
    a("## Where everything stands")
    a("")
    a(f"- **{totals['published']}** — **live on Wistia.** Done; links in the "
      "*Delivered* table below.")
    a(f"- **{totals['queued']}** — **ready to build.** Script approved; nothing made yet.")
    a(f"- **{totals['building']}** — **building now.** A workspace exists and is "
      "moving; each names the step it last completed.")
    a(f"- **{totals['awaiting_visual_review']}** — **awaiting visual review.** The "
      "mechanical gate matches this source; the combined visual verdict is still missing.")
    a(f"- **{totals['awaiting_encode_review']}** — **awaiting encode review.** A "
      "content-bound MP4 exists, but required playback review has not passed for those "
      "exact bytes.")
    a(f"- **{totals['needs_revision']}** — **needs revision.** The combined visual "
      "review found a blocking defect or a flat cut.")
    a(f"- **{totals['needs_review']}** — **waiting on your eyes.** The mechanical and "
      "visual receipts match this source; no MP4 yet, and each lesson can be reviewed "
      "independently.")
    a(f"- **{totals['approved']}** — **approved to render.** The exact current source "
      "has matching gate, visual-review, and owner-approval receipts.")
    a(f"- **{totals['rendered']}** — **rendered, not yet published.** The MP4 exists "
      "and its bytes match the current-source completion receipt; its per-render encode "
      "policy is satisfied. Only the Wistia upload is left.")
    a(f"- **{totals['incomplete_render']}** — **interrupted render.** A render started "
      "but never wrote an atomic completion receipt for its current bytes; partial output "
      "will not be reused.")
    a(f"- **{totals['raw']}** — **raw, not yet refined.** Sitting in `inbox/`, waiting "
      "on `/refine-scripts`.")
    a(f"- **{totals['needs_script']}** — **NEEDS SCRIPT.** The script itself is "
      "incomplete and only you can finish it; the exact question is under each program.")
    a(f"- **{totals['stalled']}** — **STALLED.** An incomplete phase stopped moving; "
      "resume it in the same workspace without deleting completed work.")
    a(f"- **{totals['rejected']}** — **REJECTED.** A blocking review or gate failed; "
      "the completed production phase remains visible beside the condition.")
    a(f"- **{totals['stranded']}** — **STRANDED.** Filed as published but never "
      "recorded as published; an interrupted run left it here.")
    a(f"- **{totals['orphan']}** — **ORPHAN.** A build folder matching no script in "
      "any program.")
    a("")
    a("### What the phases and conditions mean")
    a("")
    a("Status is reconstructed from source files, workspace contents, revision-bound "
      "receipts, the run record, and the publish ledger. Each active lesson has a "
      "production **phase** (what completed) plus an optional **condition** (what blocks "
      "it now), so an interruption does not collapse progress into all-or-nothing.")
    a("")
    a("| Phase or condition | Durable evidence | What it needs next |")
    a("|---|---|---|")
    a("| **RAW** | `lesson-scripts/<program>/inbox/<base>.txt` | refinement — "
      "`/refine-scripts` |")
    a("| **READY** | `lesson-scripts/<program>/ready/<base>.txt`, no build folder | "
      "an agent to author it — `/render-lessons` |")
    a("| **BUILDING** | authored files plus `.build-log.tsv` in "
      "`renders-hyperframes/<base>/` | resume the recorded phase in that workspace; "
      "do not discard completed work |")
    a("| **AWAITING VISUAL REVIEW** | matching `qa/PREFLIGHT-OK`, no matching "
      "`qa/VISUAL-REVIEW.json` | combined visual review |")
    a("| **NEEDS REVISION** | matching visual receipt says `FLAT`, `FAIL`, or "
      "`REVISE` | revise the same cut, then rerun its gates |")
    a("| **NEEDS REVIEW** | current-source `qa/PREFLIGHT-OK` plus a matching PASS / "
      "ALIVE / PROCEED `qa/VISUAL-REVIEW.json` | you — watch and approve this exact cut |")
    a("| **AWAITING VERIFICATION** | matching `qa/RENDER-START.json`, atomic render "
      "completion fields, and matching MP4 bytes; no `qa/VERIFIED` yet | resume `ship` — "
      "it verifies this MP4 without rendering again |")
    a("| *INTERRUPTED RENDER* | `qa/RENDER-START.json` exists, but no completion hash "
      "matches the current MP4 | resume `ship`; partial output is discarded and only "
      "this exact source is re-rendered |")
    a("| **AWAITING ENCODE REVIEW** | current-source `qa/VERIFIED`, but no PASS "
      "`qa/ENCODE-REVIEW.json` for the same source and MP4 hash while review is required "
      "| review the encoded beginning, middle, transitions, and ending |")
    a("| **RENDERED** | render-complete and `qa/VERIFIED` receipts match current source "
      "and actual MP4 bytes; the encode policy stamped at render start is satisfied | the "
      "Wistia upload and ledger row |")
    a("| **PUBLISHED** | `lesson-scripts/<program>/published/<base>.txt` + a row in "
      "`lesson-scripts/published.tsv` | nothing |")
    a("| *NEEDS SCRIPT* | a `TODO: needs input` / `SCRIPT PENDING` marker inside the "
      "script, in `inbox/` or `ready/` | you — the source material is missing something |")
    a("| *STALLED* | an incomplete phase with nothing written for "
      f"{int(STALL_SEC // 60)}+ min | resume that phase in place through `run.sh`; the "
      "workspace remains the recovery record |")
    a("| *REJECTED* | a current failed review, unresolved `qa/failure.json`, or "
      "unresolved quarantine incident | fix the listed cause, then perform the named "
      "resume or retry action |")
    a("| *STRANDED* | a script in `published/` with no `published.tsv` row | the "
      "publish step re-run; nothing is lost |")
    a("| *ORPHAN* | a build folder whose base matches no script anywhere | naming — "
      "it is either reference material or garbage |")
    a("")
    if published_rows:
        a("## Delivered")
        a("")
        a("Every lesson that is live, and where to watch it. Generated from "
          "`lesson-scripts/published.tsv`, which `batch-ship.sh` writes in the same "
          "commit as the upload.")
        a("")
        a("| Lesson | Program | Rendered | Watch | Local MP4 |")
        a("|---|---|---|---|---|")
        for row in sorted(published_rows, key=lambda r: r["render_date"], reverse=True):
            mp4 = (f"`renders-mp4/{row['program']}/{row['base']}_"
                   f"{row['render_date']}.mp4`")
            a(f"| {row['base']} | {row['program']} | {row['render_date']} | "
              f"[{row['wistia_url'].rsplit('/', 1)[-1]}]({row['wistia_url']}) | {mp4} |")
        a("")
    attention = [(r["program"], x) for r in report for x in r["in_flight"]
                 if x["stage"] in ("rejected", "stalled", "needs-revision")]
    if attention or orphans:
        a("## Needs a human right now")
        a("")
        for prog, x in attention:
            a(f"- **{x['stem']}** ({prog}) — {x['stage'].upper()}: {x['state']}")
            for fdg in x["findings"]:
                a(f"  - {fdg}")
            if x["journal"]:
                a(f"  - {x['journal']}")
            a(f"  - **To clear it:** {x['next']}")
        for o in orphans:
            a(f"- **{o['workspace']}** — ORPHAN: a build folder matching no script in "
              f"any program ({o['state']}; last touched {o['last_touched']})")
            a("  - **To clear it:** name what it is. Reference material belongs in "
              "`renders-hyperframes/_reference/` (underscore folders are skipped by "
              "this scan); anything else can be deleted.")
        a("")
    n = 0
    for r in report:
        if not (r["raw"] or r["needs_script"] or r["queued"] or r["in_flight"]
                or r["stranded"]):
            continue
        a(f"## {r['program']}")
        a("")
        if r["queued"]:
            a("**READY — queued to build:**")
            a("")
            for s in r["queued"]:
                n += 1
                a(f"{n}. {s}")
            a("")
        for stages, heading, blurb in (
            (("rendered",), "RENDERED — MP4 verified, waiting on publish",
             "The verified MP4 is bound to the current source and passed any required "
             "same-hash encode review. Nothing remains but the upload."),
            (("awaiting-verification",), "AWAITING VERIFICATION — MP4 preserved",
             "The renderer atomically completed this current-source MP4. Resume the tail "
             "to verify it in place; no re-render is needed."),
            (("interrupted-render",), "INTERRUPTED RENDER — partial output not reusable",
             "The render never recorded atomic completion for these bytes. Resume the "
             "tail; it will discard partial output and re-render this exact source."),
            (("awaiting-encode-review",), "AWAITING ENCODE REVIEW",
             "A verified MP4 exists for this source; its required post-render playback "
             "review has not passed for these exact bytes."),
            (("awaiting-visual-review",), "AWAITING VISUAL REVIEW",
             "The mechanical gate matches this exact source; it still needs the combined "
             "correctness and taste review."),
            (("needs-revision",), "NEEDS REVISION — visual review stopped this cut",
             "Revise the same workspace, then rerun the content-bound gate and review."),
            (("needs-review",), "NEEDS REVIEW — gate-clean, waiting on your eyes",
             "The gate and visual receipt match this exact source. Review and approve "
             "this lesson now; unfinished siblings do not block it."),
            (("approved",), "APPROVED — gate-clean, ready to render",
             "This lesson has its own persisted approval."),
            (("scaffolded", "planned", "uncompiled", "untimed", "composed"),
             "BUILDING — in flight, no MP4 yet",
             "A workspace exists and is part-way through. Each names the last step it "
             "actually completed, so a resuming session picks up rather than restarts."),
            (("stalled",), "STALLED — the build folder stopped moving",
             "Report-only: nothing here is killed automatically. Resume the named phase "
             "in the same workspace; its files and journal preserve completed work."),
            (("rejected",), "REJECTED — a gate refused this cut",
             "A review or gate blocked this lesson. Its production phase is retained; "
             "follow the listed correction and retry action."),
        ):
            group = [x for x in r["in_flight"] if x["stage"] in stages]
            if not group:
                continue
            a(f"**{heading}:**")
            a("")
            a(f"*{blurb}*")
            a("")
            for x in group:
                a(f"- {x['stem']}")
                a(f"  - state: {x['state']}")
                if x["journal"]:
                    a(f"  - {x['journal']}")
                else:
                    a(f"  - last written to: {x['last_touched']} (no `.build-log.tsv` — this "
                      "workspace predates the build journal)")
                for fdg in x["findings"]:
                    a(f"  - gate said: {fdg}")
                a(f"  - next: {x['next']}")
            a("")
        if r["stranded"]:
            a("**STRANDED mid-pipeline:**")
            a("")
            a("*Filed in `published/` but never recorded in `published.tsv` — a run was "
              "interrupted between the two. Nothing is lost; the publish step just has "
              "to finish.*")
            a("")
            for x in r["stranded"]:
                a(f"- {x['stem']}")
                a(f"  - state: {x['state']}")
                a(f"  - next: {x['next']}")
            a("")
        if r["needs_script"]:
            a("**NEEDS SCRIPT — only you can finish these:**")
            a("")
            a("*The script carries an unanswered question. Answer it in the script and "
              "delete the marker line; the lesson rejoins the queue on the next status "
              "run, with no other bookkeeping.*")
            a("")
            for b in r["needs_script"]:
                a(f"- {b['stem']}")
                a(f"  - marker: `{b['marker']}` in "
                  f"`lesson-scripts/{r['program']}/{b['folder']}/{b['stem']}.txt`")
                a(f"  - **what's needed:** {b['detail'] or '(the marker gives no detail — open the script)'}")
            a("")
        if r["raw"]:
            a("**RAW — waiting on refinement:**")
            a("")
            for s in r["raw"]:
                a(f"- {s} — `/refine-scripts`")
            a("")
    a("---")
    a("Resume: `/render-lessons` AUTO-BATCH starts at the top of the READY list above. "
      "Full state model: `bash scripts/batch-status.sh` (terminal) or "
      "`bash scripts/batch-status.sh --json` (machine).")
    a("")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {outpath}")
    sys.exit(0)

# ─────────────────────────────────────────────────────────────────────────────
B, D, O = "\033[1m", "\033[2m", "\033[0m"
RED, YEL, GRN, CYN = "\033[31m", "\033[33m", "\033[32m", "\033[36m"
print(f"\n{B}Pipeline{O} {D}(priority order — drain top to bottom){O}\n")
n = 0
for r in report:
    if not (r["raw"] or r["needs_script"] or r["queued"] or r["in_flight"]
            or r["stranded"]):
        continue
    print(f"{B}{r['program']}{O}")
    for s in r["queued"]:
        n += 1
        print(f"  {n:3d}. READY  {s}")
    for x in r["in_flight"]:
        tag = {"rendered":     f"{GRN}RENDERED — ready to publish{O}",
               "awaiting-verification": f"{CYN}AWAITING VERIFICATION{O}",
               "interrupted-render": f"{YEL}INTERRUPTED RENDER{O}",
               "awaiting-encode-review": f"{CYN}AWAITING ENCODE REVIEW{O}",
               "awaiting-visual-review": f"{CYN}AWAITING VISUAL REVIEW{O}",
               "needs-revision": f"{YEL}NEEDS REVISION{O}",
               "needs-review": f"{CYN}NEEDS REVIEW — your eyes{O}",
               "approved":     f"{GRN}APPROVED — ready to render{O}",
               "rejected":     f"{RED}REJECTED{O}",
               "stalled":      f"{YEL}STALLED{O}"}.get(x["stage"],
                              f"{D}BUILDING ({x['stage']}){O}")
        print(f"       {tag} — {x['stem']}  ({x['state']})")
        if x["journal"]:
            print(f"         {D}{x['journal'].replace('**', '')}{O}")
        for fdg in x["findings"]:
            print(f"         {D}{fdg}{O}")
        print(f"         {D}next: {x['next']}{O}")
    for x in r["stranded"]:
        print(f"       {YEL}STRANDED mid-pipeline{O} — {x['stem']}  ({x['state']})")
        print(f"         {D}next: {x['next']}{O}")
    for b in r["needs_script"]:
        print(f"       {YEL}NEEDS SCRIPT{O} ({b['marker']} in {b['folder']}/) — {b['stem']}")
        if b["detail"]:
            print(f"         {D}needs: {b['detail']}{O}")
    for s in r["raw"]:
        print(f"       {D}RAW — awaiting /refine-scripts{O} — {s}")
    print()

if orphans:
    print(f"{B}unattached build folders{O}")
    for o in orphans:
        print(f"       {YEL}ORPHAN{O} — {o['workspace']}  ({o['state']}; {o['idle']})")
        print(f"         {D}next: name it — move reference material to "
              f"renders-hyperframes/_reference/, delete the rest{O}")
    print()

t = totals
print(f"{B}{t['published']} live{O} · {t['queued']} ready · {t['building']} building · "
      f"{t['awaiting_visual_review']} awaiting visual · {t['needs_revision']} needs revision · "
      f"{t['awaiting_encode_review']} awaiting encode · "
      f"{t['incomplete_render']} interrupted render · "
      f"{t['needs_review']} needs review · {t['approved']} approved · {t['rendered']} rendered · "
      f"{t['raw']} raw · {t['needs_script']} NEEDS SCRIPT · {t['stalled']} STALLED · "
      f"{t['rejected']} REJECTED · {t['stranded']} STRANDED · {t['orphan']} ORPHAN\n")
if t["queued"]:
    print(f"{D}Resume: /render-lessons AUTO-BATCH — it starts at the top of this list.{O}\n")
PY
