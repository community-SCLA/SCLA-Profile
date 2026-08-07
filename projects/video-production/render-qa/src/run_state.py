#!/usr/bin/env python3
"""Persistent control state for SCLA video runs and per-workspace failures.

Video lifecycle remains folder-owned.  This file stores only facts folders
cannot represent: explicit run scope, rolling review approval, retry counts and
the cross-video circuit breaker.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from workspace_revision import read_revision_marker, workspace_revision


SRC = Path(__file__).resolve().parent
VP = Path(os.environ.get("VIDEO_VP_ROOT", SRC.parents[1]))
REPO = Path(os.environ.get("VIDEO_REPO_ROOT", VP.parents[1]))
RUN_FILE = Path(os.environ.get(
    "VIDEO_RUN_STATE", VP / "renders-hyperframes" / "_run" / "run.json"))
RUN_LOCK = Path(os.environ.get("VIDEO_RUN_STATE_LOCK", f"{RUN_FILE}.lock"))
DEFAULT_RETRY_LIMIT = 2
DEFAULT_CIRCUIT_LIMIT = 2
DEFAULT_TTS_CONCURRENCY = 2
DEFAULT_CLOUD_RENDER_CONCURRENCY = 2
MAX_CLOUD_RENDER_CONCURRENCY = 4
ACTIVE_DISPATCH_STATES = frozenset(("reserved", "submitted", "unknown"))
TERMINAL_DISPATCH_STATES = frozenset(
    ("merged", "failed", "cancelled", "retry-authorized"))
DEFAULT_DISPATCH_RESERVATION_TTL = 900


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def load_run() -> dict:
    # Normalize in memory on every read so an old selection-time stage label is
    # never exposed as live truth.  Commands which write state persist this
    # shape; ``migrate-state`` exists for a deliberate no-op-safe disk upgrade.
    return normalize_run_state(read_json(RUN_FILE, {}))


def approval_map(state: dict) -> dict:
    """Return durable per-stem approvals, migrating the legacy review shape."""
    raw_approvals = state.get("approvals") or {}
    approvals = dict(raw_approvals) if isinstance(raw_approvals, dict) else {}
    review = state.get("review") or {}
    for stem in review.get("stems") or []:
        if stem in approvals:
            continue
        # The legacy review list named only a stem.  It did not record a source
        # digest, so binding it to whatever happens to be in the workspace now
        # would turn an old approval into approval of an unseen replacement.
        approvals[stem] = {
            "revision": None,
            "approved_at": review.get("approved_at"),
            "approved_by": review.get("approved_by") or "owner",
            "source": review.get("source") or "legacy-review-unbound",
        }
    return approvals


def sync_review_projection(state: dict) -> None:
    """Keep the old review summary readable while approvals migrate by stem."""
    approvals = approval_map(state)
    state["approvals"] = approvals
    # Only digest-bound approvals are approvals.  Unbound legacy receipts stay
    # in the durable map as audit evidence, but never appear green in the
    # compatibility projection and never authorize shipping.
    bound = {stem: receipt for stem, receipt in approvals.items()
             if isinstance(receipt, dict) and receipt.get("revision")}
    stems = sorted(bound)
    latest = max(
        (x for x in bound.values() if x.get("approved_at")),
        key=lambda x: x["approved_at"],
        default={},
    )
    state["review"] = {
        "approved_at": latest.get("approved_at"),
        "approved_by": latest.get("approved_by"),
        "stems": stems,
    }


def normalize_run_state(state: dict) -> dict:
    """Upgrade old run-state shapes without inventing lifecycle facts."""
    if not isinstance(state, dict) or not state:
        return {}
    normalized = dict(state)
    items = []
    for raw in normalized.get("items") or []:
        if not isinstance(raw, dict) or not raw.get("stem"):
            continue
        # Selection owns identity only.  Stage/phase/condition are observed
        # from disk by batch-status and must never be carried across sessions.
        items.append({"stem": raw["stem"], "program": raw.get("program")})
    normalized["items"] = items
    normalized["version"] = max(4, int(normalized.get("version") or 0))
    normalized["dispatches"] = dict(normalized.get("dispatches") or {})
    sync_review_projection(normalized)
    return normalized


def active_dispatch_count(state: dict) -> int:
    """Count machine-wide external ownership, independent of current scope."""
    return sum(
        1 for receipt in (state.get("dispatches") or {}).values()
        if isinstance(receipt, dict) and receipt.get("state") in ACTIVE_DISPATCH_STATES
    )


def seconds_since(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        stamp = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None
    return max(0, int((datetime.now(timezone.utc) - stamp).total_seconds()))


def selected_item(state: dict, stem: str) -> dict:
    item = next((x for x in state.get("items", [])
                 if x.get("stem") == stem), None)
    if not item:
        raise SystemExit(f"FATAL: {stem} is outside the active run's explicit scope")
    return item


def current_gate_revision(stem: str) -> tuple[Path, str]:
    workspace = VP / "renders-hyperframes" / stem
    if not workspace.is_dir():
        raise SystemExit(f"FATAL: no workspace found for {stem}")
    current = workspace_revision(workspace)
    preflight = read_revision_marker(workspace)
    if not preflight or preflight != current:
        raise SystemExit(
            f"FATAL: {stem} is not gate-clean at its current revision; "
            "run the build gate again")
    return workspace, current


def current_review_revision(stem: str) -> tuple[Path, str]:
    workspace, current = current_gate_revision(stem)
    visual = read_json(workspace / "qa" / "VISUAL-REVIEW.json", {})
    if (visual.get("revision") != current or
            visual.get("blocking_defect") != "PASS" or
            visual.get("taste") != "ALIVE" or
            visual.get("recommendation") != "PROCEED"):
        raise SystemExit(
            f"FATAL: {stem} has no PASS + ALIVE + PROCEED visual review "
            "for its current revision")
    return workspace, current


@contextmanager
def run_write_lock():
    """Serialize read-modify-write transactions from parallel workers."""
    RUN_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with RUN_LOCK.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def capacity_view(state: dict) -> dict:
    """Return stage-specific limits, including sane defaults for old runs."""
    backend = state.get("backend", "local")
    legacy = int(state.get("concurrency", 4 if backend == "cloud" else 3))
    return {
        "backend": backend,
        "authoring_backend": state.get("authoring_backend", "local"),
        "authoring": int(state.get(
            "authoring_concurrency", 6 if backend == "cloud" else legacy)),
        "tts": int(state.get("tts_concurrency", DEFAULT_TTS_CONCURRENCY)),
        "cloud_render": int(state.get(
            "cloud_render_concurrency", DEFAULT_CLOUD_RENDER_CONCURRENCY)),
        "cloud_render_max": int(state.get(
            "cloud_render_max", MAX_CLOUD_RENDER_CONCURRENCY)),
        "publish": int(state.get("publish_concurrency", 1)),
        "cloud_clean_streak": int(state.get("cloud_clean_streak", 0)),
    }


def save_run(state: dict) -> None:
    state["updated_at"] = now()
    atomic_write(RUN_FILE, state)


def locate(stem: str) -> dict:
    lessons = VP / "lesson-scripts"
    located = None
    for program_dir in sorted(p for p in lessons.iterdir() if p.is_dir()):
        for stage in ("inbox", "ready", "published"):
            if (program_dir / stage / f"{stem}.txt").is_file():
                located = {"stem": stem, "program": program_dir.name,
                           "source_stage": stage}
                break
        if located:
            break
    workspace = VP / "renders-hyperframes" / stem
    if workspace.is_dir():
        return {**(located or {"stem": stem, "program": None}),
                "stage": "workspace"}
    if located:
        return {**located, "stage": located["source_stage"]}
    raise SystemExit(f"FATAL: no script or workspace found for {stem}")


def queue(scope_kind: str, scope_value: str | None) -> list[dict]:
    lessons = VP / "lesson-scripts"
    programs = ([lessons / scope_value] if scope_kind == "program" else
                sorted(p for p in lessons.iterdir() if p.is_dir()))
    selected = []
    for program_dir in programs:
        if not program_dir.is_dir():
            raise SystemExit(f"FATAL: no such program: {program_dir.name}")
        for script in sorted((program_dir / "ready").glob("*.txt")):
            selected.append({"stem": script.stem, "program": program_dir.name})
    return selected


def new_run(mode: str, scope_kind: str, scope_value: str | None,
            selected: list[dict], authoring_backend: str = "local") -> dict:
    previous = load_run()
    approvals = approval_map(previous)
    backend_file = VP / "renders-hyperframes" / "_run" / "RENDER-BACKEND"
    try:
        backend = backend_file.read_text(encoding="utf-8").strip() or "local"
    except OSError:
        backend = "local"
    created = now()
    state = {
        "version": 4,
        "mode": mode,
        "scope": {"kind": scope_kind, "value": scope_value},
        "items": selected,
        # Selection changes scope only. Per-lesson approvals and dispatch
        # reservations remain durable even when a later run selects other work.
        "approvals": approvals,
        "dispatches": dict(previous.get("dispatches") or {}),
        "backend": backend,
        "authoring_backend": authoring_backend,
        # These stages consume different resources and must not share one
        # ambiguous lane count. Cloud authoring is isolated; provider calls,
        # renders and publishing use their own machine-wide queues.
        "authoring_concurrency": 6 if authoring_backend == "cloud" else 3,
        "tts_concurrency": DEFAULT_TTS_CONCURRENCY,
        "cloud_render_concurrency": DEFAULT_CLOUD_RENDER_CONCURRENCY,
        "cloud_render_max": MAX_CLOUD_RENDER_CONCURRENCY,
        "publish_concurrency": 1,
        "retry_limit": DEFAULT_RETRY_LIMIT,
        "circuit_breaker_limit": DEFAULT_CIRCUIT_LIMIT,
        "circuit_breaker": previous.get("circuit_breaker") or {
            "open": False, "error_class": None, "count": 0,
            "stems": [], "opened_at": None,
        },
        "cloud_clean_streak": int(previous.get("cloud_clean_streak", 0)),
        "cloud_clean_stems": list(previous.get("cloud_clean_stems") or []),
        "created_at": created,
        "updated_at": created,
    }
    for key in ("results", "last_closeout"):
        if key in previous:
            state[key] = previous[key]
    sync_review_projection(state)
    save_run(state)
    return state


def cmd_select(args) -> int:
    with run_write_lock():
        if args.scope_kind == "stem":
            located = locate(args.scope_value)
            selected = [{"stem": located["stem"], "program": located.get("program")}]
        else:
            selected = queue(args.scope_kind, args.scope_value)
        state = new_run(args.mode, args.scope_kind, args.scope_value, selected,
                        args.authoring_backend)
    print(json.dumps(state, indent=2))
    return 0


def cmd_approve(args) -> int:
    with run_write_lock():
        state = load_run()
        if not state:
            raise SystemExit("FATAL: no active run; select a stem or batch first")
        selected = [x.get("stem") for x in state.get("items", []) if x.get("stem")]
        if not selected:
            raise SystemExit(
                "FATAL: the active run has no selected workspaces to review")
        if args.target.upper() == "BATCH":
            if state.get("mode") != "batch":
                raise SystemExit("FATAL: BATCH approval requires an active batch")
            targets = selected
            message = f"approved batch review: {len(selected)} workspaces"
        else:
            if args.target not in selected:
                raise SystemExit(f"FATAL: {args.target} is outside the active run")
            targets = [args.target]
            message = (f"approved rolling review: {args.target}"
                       if state.get("mode") == "batch" else
                       f"approved review: {args.target}")

        revisions = {}
        failures = []
        for stem in targets:
            try:
                _workspace, revisions[stem] = current_review_revision(stem)
            except SystemExit as exc:
                failures.append(str(exc).removeprefix("FATAL: "))
        if failures:
            raise SystemExit(
                "FATAL: review is incomplete: " + "; ".join(failures))

        approved_at = now()
        approvals = approval_map(state)
        for stem, revision in revisions.items():
            approvals[stem] = {
                "revision": revision,
                "approved_at": approved_at,
                "approved_by": args.approved_by,
            }
        state["approvals"] = approvals
        sync_review_projection(state)
        save_run(state)
    print(message)
    return 0


def cmd_migrate_approval(args) -> int:
    """Retain an old owner receipt without binding it to unseen source."""
    with run_write_lock():
        state = load_run()
        if not state:
            raise SystemExit("FATAL: no active run to migrate")
        locate(args.stem)
        approvals = approval_map(state)
        approvals[args.stem] = {
            "revision": None,
            "approved_at": args.approved_at,
            "approved_by": "owner",
            "source": "legacy-approved-pilot-unbound",
        }
        state["approvals"] = approvals
        sync_review_projection(state)
        save_run(state)
    print(f"migrated unbound owner receipt: {args.stem}; fresh approval required")
    return 0


def cmd_migrate_state(_args) -> int:
    """Persist the lossless v4 identity-only state shape under the run lock."""
    with run_write_lock():
        raw = read_json(RUN_FILE, {})
        if not raw:
            raise SystemExit("FATAL: no active run to migrate")
        state = normalize_run_state(raw)
        changed = state != raw
        if changed:
            save_run(state)
    print(json.dumps({
        "version": state.get("version"),
        "items": len(state.get("items") or []),
        "changed": changed,
    }))
    return 0


def cmd_record_visual_review(args) -> int:
    with run_write_lock():
        state = load_run()
        if not state:
            raise SystemExit("FATAL: no active run; select a stem or batch first")
        selected_item(state, args.stem)
        workspace, revision = current_gate_revision(args.stem)
        proceed = (args.blocking_defect == "PASS" and args.taste == "ALIVE")
        if (args.recommendation == "PROCEED") != proceed:
            raise SystemExit(
                "FATAL: PROCEED requires BLOCKING_DEFECT=PASS and TASTE=ALIVE; "
                "every other verdict must recommend REVISE")
        receipt = {
            "revision": revision,
            "blocking_defect": args.blocking_defect,
            "taste": args.taste,
            "recommendation": args.recommendation,
            "findings": list(args.finding or []),
            "reviewed_at": now(),
        }
        atomic_write(workspace / "qa" / "VISUAL-REVIEW.json", receipt)
    print(json.dumps(receipt, indent=2))
    return 0


def cmd_show(_args) -> int:
    state = load_run()
    if not state:
        print("{}")
        return 1
    print(json.dumps(state, indent=2))
    return 0


def cmd_capacity(_args) -> int:
    state = load_run()
    if not state:
        raise SystemExit("FATAL: no active run; select a stem or batch first")
    print(json.dumps(capacity_view(state), indent=2))
    return 0


def cmd_tts_concurrency(_args) -> int:
    state = load_run()
    print(capacity_view(state).get("tts", DEFAULT_TTS_CONCURRENCY))
    return 0


def cmd_cloud_concurrency(_args) -> int:
    state = load_run()
    print(capacity_view(state).get(
        "cloud_render", DEFAULT_CLOUD_RENDER_CONCURRENCY))
    return 0


def cmd_set_cloud_concurrency(args) -> int:
    value = int(args.value)
    with run_write_lock():
        state = load_run()
        if not state:
            raise SystemExit("FATAL: no active run; select a stem or batch first")
        if value not in (2, 4):
            raise SystemExit("FATAL: cloud render capacity must be 2 or 4")
        limits = capacity_view(state)
        if value > 2 and limits["cloud_clean_streak"] < 3:
            raise SystemExit(
                "FATAL: four cloud renders require three consecutive clean cloud "
                f"renders; current streak is {limits['cloud_clean_streak']}/3")
        state["cloud_render_concurrency"] = value
        state["cloud_render_max"] = MAX_CLOUD_RENDER_CONCURRENCY
        save_run(state)
    print(f"cloud render capacity: {value}")
    return 0


def cmd_locate(args) -> int:
    print(json.dumps(locate(args.stem)))
    return 0


def cmd_delegate_info(args) -> int:
    state = load_run()
    if not state:
        raise SystemExit("FATAL: no active run; select a stem or batch first")
    item = next((x for x in state.get("items", [])
                 if x.get("stem") == args.stem), None)
    if not item:
        raise SystemExit(
            f"FATAL: {args.stem} is outside the active run's explicit scope")
    program = item.get("program")
    if not program:
        program = locate(args.stem).get("program")
    ready = VP / "lesson-scripts" / str(program) / "ready" / f"{args.stem}.txt"
    if not program or not ready.is_file():
        raise SystemExit(f"FATAL: no ready script for selected stem {args.stem}")
    workspace = VP / "renders-hyperframes" / args.stem
    if workspace.is_dir():
        raise SystemExit(
            f"FATAL: {args.stem} already has a workspace; resume it locally "
            "instead of creating a duplicate Cloud authoring task")
    print(json.dumps({"stem": args.stem, "program": program,
                      "stage": "ready"}))
    return 0


def cmd_reserve_dispatch(args) -> int:
    with run_write_lock():
        state = load_run()
        if not state:
            raise SystemExit("FATAL: no active run; select a stem or batch first")
        if state.get("authoring_backend") != "cloud":
            raise SystemExit("FATAL: Cloud dispatch requires a --cloud batch")
        item = selected_item(state, args.stem)
        program = item.get("program") or locate(args.stem).get("program")
        ready = VP / "lesson-scripts" / str(program) / "ready" / f"{args.stem}.txt"
        workspace = VP / "renders-hyperframes" / args.stem
        if workspace.is_dir():
            raise SystemExit(
                f"FATAL: {args.stem} already has a workspace; resume it locally")
        if not program or not ready.is_file():
            raise SystemExit(f"FATAL: no ready script for selected stem {args.stem}")
        dispatches = dict(state.get("dispatches") or {})
        prior = dispatches.get(args.stem) or {}
        if prior.get("state") in ACTIVE_DISPATCH_STATES and args.allow_existing:
            converged = dict(prior)
            converged["already_owned"] = True
            print(json.dumps(converged))
            return 0
        if prior.get("state") not in (None, "retry-authorized"):
            raise SystemExit(
                f"FATAL: {args.stem} already has a durable Cloud dispatch "
                f"({prior.get('state')}); refusing a duplicate task")
        active = active_dispatch_count(state)
        limit = capacity_view(state)["authoring"]
        if active >= limit:
            raise SystemExit(
                "FATAL: Cloud authoring capacity is full "
                f"({active}/{limit} durable tasks active)")
        receipt = {
            "state": "reserved",
            "program": program,
            "reserved_at": now(),
            "attempt": int(prior.get("attempt", 0)) + 1,
            "reservation_id": uuid.uuid4().hex,
        }
        dispatches[args.stem] = receipt
        state["dispatches"] = dispatches
        save_run(state)
    print(json.dumps(receipt))
    return 0


def cmd_record_dispatch(args) -> int:
    with run_write_lock():
        state = load_run()
        dispatches = dict(state.get("dispatches") or {})
        receipt = dict(dispatches.get(args.stem) or {})
        prior_state = receipt.get("state")
        if not receipt:
            raise SystemExit(f"FATAL: no active Cloud dispatch reservation for {args.stem}")
        if args.status == "submitted" and prior_state not in ("reserved", "submitted"):
            raise SystemExit(
                f"FATAL: {args.stem} dispatch is {prior_state}; refusing to "
                "move it backward to submitted")
        if args.status == "merged":
            if prior_state not in ("reserved", "submitted", "unknown", "failed",
                                   "merged"):
                raise SystemExit(
                    f"FATAL: {args.stem} dispatch is {prior_state}; no Cloud "
                    "result is eligible for a merged handoff")
            workspace = VP / "renders-hyperframes" / args.stem
            if not workspace.is_dir():
                raise SystemExit(
                    f"FATAL: merged handoff for {args.stem} requires its "
                    "workspace to exist in the local checkout")
        recorded_at = now()
        receipt.update({"state": args.status, "recorded_at": recorded_at})
        if args.status == "merged":
            receipt["merged_at"] = recorded_at
        if args.task_ref:
            receipt["task_ref"] = args.task_ref
        dispatches[args.stem] = receipt
        state["dispatches"] = dispatches
        save_run(state)
    print(json.dumps(receipt))
    return 0


def cmd_fail_dispatch(args) -> int:
    with run_write_lock():
        state = load_run()
        dispatches = dict(state.get("dispatches") or {})
        receipt = dict(dispatches.get(args.stem) or {})
        if receipt.get("state") not in ("reserved", "submitted"):
            raise SystemExit(f"FATAL: no active Cloud dispatch reservation for {args.stem}")
        receipt.update({
            # Once the CLI started submission, a transport failure cannot tell
            # us whether the remote task exists.  Keep ownership blocked until
            # the operator records a merge or explicitly authorizes a retry.
            "state": args.outcome,
            "failed_at" if args.outcome == "failed" else "outcome_unknown_at": now(),
            "error": args.error[-2000:],
        })
        dispatches[args.stem] = receipt
        state["dispatches"] = dispatches
        save_run(state)
    print(json.dumps(receipt))
    return 0


def cmd_dispatchable(_args) -> int:
    state = load_run()
    if not state:
        raise SystemExit("FATAL: no active run; select a stem or batch first")
    if state.get("authoring_backend") != "cloud":
        raise SystemExit("FATAL: active run does not use Cloud authoring")
    dispatches = state.get("dispatches") or {}
    selected = []
    blocked = []
    active = active_dispatch_count(state)
    try:
        stale_after = int(os.environ.get(
            "VIDEO_DISPATCH_RESERVATION_TTL", DEFAULT_DISPATCH_RESERVATION_TTL))
    except ValueError:
        stale_after = DEFAULT_DISPATCH_RESERVATION_TTL
    for stem, dispatch in sorted(dispatches.items()):
        if not isinstance(dispatch, dict):
            continue
        dispatch_state = dispatch.get("state")
        age = seconds_since(dispatch.get("reserved_at"))
        if dispatch_state == "unknown":
            blocked.append({
                "stem": stem,
                "state": dispatch_state,
                "condition": "remote-outcome-unknown",
                "task_ref": dispatch.get("task_ref"),
            })
        elif (dispatch_state == "reserved" and stale_after > 0 and
              (age is None or age >= stale_after)):
            blocked.append({
                "stem": stem,
                "state": dispatch_state,
                "condition": "stale-reservation",
                "age_seconds": age,
                "reservation_id": dispatch.get("reservation_id"),
            })
    for item in state.get("items", []):
        stem = item.get("stem")
        program = item.get("program")
        if not stem or not program:
            continue
        workspace = VP / "renders-hyperframes" / stem
        dispatch = dispatches.get(stem) or {}
        ready = VP / "lesson-scripts" / program / "ready" / f"{stem}.txt"
        if (ready.is_file() and not workspace.is_dir() and
                dispatch.get("state") in (None, "retry-authorized")):
            selected.append({"stem": stem, "program": program})
    available = max(0, capacity_view(state)["authoring"] - active)
    print(json.dumps({"available": available, "active": active,
                      "items": selected[:available], "blocked": blocked}))
    return 0


def cmd_can_claim(args) -> int:
    state = load_run()
    if not state:
        raise SystemExit("FATAL: no active run; select a stem or batch first")
    item = selected_item(state, args.stem)
    if state.get("authoring_backend", "local") != "local":
        raise SystemExit(
            "FATAL: local authoring requires a local run; this selection uses "
            "Cloud authoring")
    if getattr(args, "program", None) and item.get("program") != args.program:
        raise SystemExit(
            f"FATAL: {args.stem} is selected for {item.get('program')}, not "
            f"{args.program}")
    dispatch = (state.get("dispatches") or {}).get(args.stem) or {}
    if dispatch.get("state") in ACTIVE_DISPATCH_STATES:
        raise SystemExit(
            f"FATAL: {args.stem} has an external Cloud task "
            f"({dispatch.get('state')}); refusing a competing local claim")
    return 0


def cmd_claim_local(args) -> int:
    """Atomically join local ownership and canonical workspace creation."""
    with run_write_lock():
        # Run the same policy while the reservation lock is held.  Cloud
        # reserve-dispatch uses this lock too, so exactly one side can win.
        cmd_can_claim(args)
        workspace = VP / "renders-hyperframes" / args.stem
        try:
            workspace.mkdir()
        except FileExistsError:
            raise SystemExit(
                f"FATAL: renders-hyperframes/{args.stem} is already claimed")
    print(json.dumps({"stem": args.stem, "workspace": str(workspace)}))
    return 0


def cmd_can_resume(args) -> int:
    state = load_run()
    if not state:
        raise SystemExit("FATAL: no active run; select a stem or batch first")
    item = selected_item(state, args.stem)
    if getattr(args, "program", None) and item.get("program") != args.program:
        raise SystemExit(
            f"FATAL: {args.stem} is selected for {item.get('program')}, not "
            f"{args.program}")
    dispatch = (state.get("dispatches") or {}).get(args.stem) or {}
    dispatch_state = dispatch.get("state")
    resumable = (
        dispatch_state is None or
        dispatch_state in TERMINAL_DISPATCH_STATES
    )
    if not resumable:
        raise SystemExit(
            f"FATAL: {args.stem} is still externally owned ({dispatch_state}); "
            "record the merged handoff with run.sh dispatch-merged before resume")
    return 0


def cmd_can_ship(args) -> int:
    state = load_run()
    if not state:
        raise SystemExit("FATAL: no active run; select a stem or batch first")
    selected_item(state, args.stem)
    _workspace, current = current_review_revision(args.stem)
    approval = approval_map(state).get(args.stem) or {}
    if approval.get("revision") != current:
        raise SystemExit(
            f"FATAL: {args.stem} has not received review approval for its "
            f"current revision; review it, then run run.sh approve {args.stem}")
    return 0


def failure_path(workspace: Path) -> Path:
    return workspace / "qa" / "failure.json"


def load_failure(workspace: Path) -> dict:
    return read_json(failure_path(workspace), {})


def retry_limit() -> int:
    state = load_run()
    return int(state.get("retry_limit", DEFAULT_RETRY_LIMIT))


def cmd_can_attempt(args) -> int:
    state = load_run()
    circuit = state.get("circuit_breaker", {})
    if circuit.get("open"):
        print(f"CIRCUIT_OPEN: {circuit.get('error_class')} repeated across "
              f"{circuit.get('count')} videos")
        return 4
    failure = load_failure(Path(args.workspace))
    if failure.get("resolved_at"):
        return 0
    error_class = failure.get("error_class")
    attempts = int(failure.get("attempts_by_class", {}).get(error_class, 0))
    if error_class and attempts >= retry_limit():
        print(f"RETRY_EXHAUSTED: {error_class} failed {attempts} times; "
              "use run.sh retry <stem> only after a deliberate fix")
        return 3
    return 0


def update_circuit(state: dict, stem: str, error_class: str) -> None:
    circuit = state.setdefault("circuit_breaker", {})
    prior_class = circuit.get("error_class")
    stems = list(circuit.get("stems") or [])
    if circuit.get("open") and prior_class == error_class:
        return
    if prior_class == error_class:
        if not stems or stems[-1] != stem:
            stems.append(stem)
    else:
        stems = [stem]
    count = len(stems)
    limit = int(state.get("circuit_breaker_limit", DEFAULT_CIRCUIT_LIMIT))
    circuit.update({
        "error_class": error_class,
        "count": count,
        "stems": stems,
        "open": count >= limit,
        "opened_at": now() if count >= limit else None,
    })


def closeout(state: dict, stem: str, status: str, **details) -> None:
    """One concise driver-owned result record; no per-command reminder hooks."""
    record = {"status": status, "at": now(), **details}
    state.setdefault("results", {})[stem] = record
    state["last_closeout"] = {"stem": stem, **record}


def cmd_record_failure(args) -> int:
    workspace = Path(args.workspace)
    path = failure_path(workspace)
    prior = load_failure(workspace)
    attempts = dict(prior.get("attempts_by_class") or {})
    attempts[args.error_class] = int(attempts.get(args.error_class, 0)) + 1
    receipt = {
        "version": 1,
        "stem": args.stem,
        "program": args.program,
        "error_class": args.error_class,
        "reason": args.reason,
        "command": args.command,
        "exit_code": int(args.exit_code),
        "log": args.log,
        "next_action": args.next_action,
        "attempts_by_class": attempts,
        "attempt": attempts[args.error_class],
        "failed_at": now(),
        "resolved_at": None,
    }
    atomic_write(path, receipt)
    with run_write_lock():
        state = load_run()
        if state:
            update_circuit(state, args.stem, args.error_class)
            if args.error_class == "cloud-render":
                state["cloud_clean_streak"] = 0
                state["cloud_clean_stems"] = []
                state["cloud_render_concurrency"] = min(
                    capacity_view(state)["cloud_render"],
                    DEFAULT_CLOUD_RENDER_CONCURRENCY,
                )
            closeout(state, args.stem, "failed", error_class=args.error_class,
                     attempt=receipt["attempt"], recovery=args.next_action,
                     log=args.log)
            save_run(state)
            receipt["circuit_open"] = state["circuit_breaker"]["open"]
    receipt["retry_exhausted"] = receipt["attempt"] >= retry_limit()
    print(json.dumps(receipt))
    return 0


def cmd_import_legacy_failure(args) -> int:
    """Turn an old quarantine row into an enforced retry receipt."""
    workspace = Path(args.workspace)
    receipt = {
        "version": 1,
        "stem": args.stem,
        "program": args.program,
        "error_class": args.error_class,
        "reason": args.reason,
        "command": "legacy failure; command was not preserved",
        "exit_code": None,
        "log": None,
        "next_action": args.next_action,
        "attempts_by_class": {args.error_class: retry_limit()},
        "attempt": retry_limit(),
        "failed_at": args.failed_at or now(),
        "resolved_at": None,
        "legacy_import": True,
    }
    atomic_write(failure_path(workspace), receipt)
    with run_write_lock():
        state = load_run()
        if state:
            update_circuit(state, args.stem, args.error_class)
            if args.error_class == "cloud-render":
                state["cloud_clean_streak"] = 0
                state["cloud_clean_stems"] = []
                state["cloud_render_concurrency"] = min(
                    capacity_view(state)["cloud_render"],
                    DEFAULT_CLOUD_RENDER_CONCURRENCY,
                )
            closeout(state, args.stem, "failed", error_class=args.error_class,
                     attempt=receipt["attempt"], recovery=args.next_action,
                     log=None, legacy_import=True)
            save_run(state)
    print(json.dumps(receipt))
    return 0


def cmd_record_success(args) -> int:
    workspace = Path(args.workspace)
    failure = load_failure(workspace)
    if failure:
        failure["resolved_at"] = now()
        atomic_write(failure_path(workspace), failure)
    # TTS recovery is workspace-local. It must not close a render circuit or
    # mark the lesson complete before gate/render/publish have happened.
    if args.phase == "tts":
        with run_write_lock():
            state = load_run()
            if state and state.get("circuit_breaker", {}).get("error_class") == "tts":
                state["circuit_breaker"] = {
                    "open": False, "error_class": None, "count": 0,
                    "stems": [], "opened_at": None,
                }
                save_run(state)
        return 0
    with run_write_lock():
        state = load_run()
        if state:
            state["circuit_breaker"] = {
                "open": False, "error_class": None, "count": 0,
                "stems": [], "opened_at": None,
            }
            closeout(state, args.stem, "complete", phase=args.phase)
            save_run(state)
    return 0


def cmd_record_encode_review(args) -> int:
    workspace = VP / "renders-hyperframes" / args.stem
    if not workspace.is_dir():
        raise SystemExit(f"FATAL: no workspace found for {args.stem}")
    verified = read_json(workspace / "qa" / "VERIFIED", {})
    render = read_json(workspace / "qa" / "RENDER-START.json", {})
    if not isinstance(verified, dict) or not isinstance(render, dict):
        raise SystemExit(f"FATAL: {args.stem} render receipts are not JSON objects")
    current = workspace_revision(workspace)
    if (verified.get("source_revision") != current
            or render.get("source_revision") != current):
        raise SystemExit(
            f"FATAL: {args.stem} has no completed, verified MP4 for its current "
            "source revision")
    raw_mp4 = verified.get("mp4")
    if not isinstance(raw_mp4, str) or not raw_mp4:
        raise SystemExit(f"FATAL: {args.stem} VERIFIED marker has no MP4 path")
    mp4 = Path(raw_mp4)
    if not mp4.is_absolute():
        mp4 = workspace / mp4
    if not mp4.is_file():
        raise SystemExit(f"FATAL: verified MP4 is missing: {mp4}")
    raw_render_mp4 = render.get("mp4")
    render_mp4 = Path(raw_render_mp4) if isinstance(raw_render_mp4, str) else None
    if render_mp4 is not None and not render_mp4.is_absolute():
        render_mp4 = workspace / render_mp4
    if render_mp4 is None or render_mp4.resolve() != mp4.resolve():
        raise SystemExit(
            f"FATAL: {args.stem} render-start and VERIFIED identify different MP4s")
    digest = sha256_file(mp4)
    if verified.get("sha256") != digest:
        raise SystemExit(f"FATAL: verified MP4 hash changed for {args.stem}")
    if (not isinstance(render.get("completed_at"), str)
            or not render.get("completed_at")
            or render.get("completed_sha256") != digest
            or render.get("completed_bytes") != mp4.stat().st_size):
        raise SystemExit(
            f"FATAL: {args.stem} render-complete receipt does not match VERIFIED bytes")
    render_backend = render.get("backend")
    if render_backend not in {"local", "cloud"} or args.backend != render_backend:
        raise SystemExit(
            f"FATAL: {args.stem} was rendered by {render_backend or 'unknown'}, not "
            f"the requested {args.backend} backend")
    render_required = render.get("encode_review_required")
    if (not isinstance(render_required, bool)
            or verified.get("encode_review_required") is not render_required):
        raise SystemExit(
            f"FATAL: {args.stem} render receipts disagree on encode-review policy")
    render_attempt = render.get("attempt")
    if (not isinstance(render_attempt, int) or render_attempt < 1
            or verified.get("render_attempt") != render_attempt):
        raise SystemExit(
            f"FATAL: {args.stem} render receipts disagree on render attempt")
    receipt = {
        "source_revision": current,
        "mp4": str(mp4),
        "sha256": digest,
        "backend": render_backend,
        "render_attempt": render_attempt,
        "verdict": args.verdict,
        "findings": list(args.finding or []),
        "reviewed_at": now(),
    }
    atomic_write(workspace / "qa" / "ENCODE-REVIEW.json", receipt)
    with run_write_lock():
        state = load_run()
        if state and render_backend == "cloud":
            if args.verdict == "PASS":
                clean_stems = list(state.get("cloud_clean_stems") or [])
                if args.stem not in clean_stems:
                    clean_stems.append(args.stem)
                state["cloud_clean_stems"] = clean_stems[-3:]
                state["cloud_clean_streak"] = len(state["cloud_clean_stems"])
            else:
                state["cloud_clean_stems"] = []
                state["cloud_clean_streak"] = 0
                state["cloud_render_concurrency"] = min(
                    capacity_view(state)["cloud_render"],
                    DEFAULT_CLOUD_RENDER_CONCURRENCY,
                )
            closeout(state, args.stem,
                     "complete" if args.verdict == "PASS" else "failed",
                     phase="encode-review", verdict=args.verdict)
            save_run(state)
    print(json.dumps(receipt, indent=2))
    return 0


def cmd_post_review_required(_args) -> int:
    streak = int(load_run().get("cloud_clean_streak", 0))
    if streak < 3:
        print(f"post-render encode review required ({streak}/3 clean cloud renders)")
        return 0
    print(f"post-render encode review retired ({streak} consecutive clean cloud renders)")
    return 1


def cmd_retry(args) -> int:
    item = locate(args.stem)
    workspace = VP / "renders-hyperframes" / args.stem
    failure = load_failure(workspace)
    if failure:
        failure["resolved_at"] = now()
        failure["reset_reason"] = args.reason
        atomic_write(failure_path(workspace), failure)
    with run_write_lock():
        state = load_run()
        if state:
            state["circuit_breaker"] = {
                "open": False, "error_class": None, "count": 0,
                "stems": [], "opened_at": None,
            }
            dispatches = dict(state.get("dispatches") or {})
            dispatch = dict(dispatches.get(args.stem) or {})
            if dispatch.get("state") in ("failed", "reserved", "unknown"):
                dispatch.update({
                    "state": "retry-authorized",
                    "retry_authorized_at": now(),
                    "retry_reason": args.reason,
                })
                dispatches[args.stem] = dispatch
                state["dispatches"] = dispatches
            save_run(state)
    print(f"retry authorized: {item['stem']}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("select")
    s.add_argument("--mode", choices=("produce", "refine", "batch"), required=True)
    s.add_argument("--scope-kind", choices=("stem", "program", "all"), required=True)
    s.add_argument("--scope-value")
    s.add_argument("--authoring-backend", choices=("local", "cloud"),
                   default="local")
    s.set_defaults(func=cmd_select)
    s = sub.add_parser("approve")
    s.add_argument("target")
    s.add_argument("--approved-by", default="owner")
    s.set_defaults(func=cmd_approve)
    s = sub.add_parser("migrate-approval", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--approved-at", required=True)
    s.set_defaults(func=cmd_migrate_approval)
    sub.add_parser("migrate-state").set_defaults(func=cmd_migrate_state)
    s = sub.add_parser("record-visual-review")
    s.add_argument("stem")
    s.add_argument("--blocking-defect", choices=("PASS", "FAIL"), required=True)
    s.add_argument("--taste", choices=("ALIVE", "FLAT"), required=True)
    s.add_argument("--recommendation", choices=("PROCEED", "REVISE"), required=True)
    s.add_argument("--finding", action="append", default=[])
    s.set_defaults(func=cmd_record_visual_review)
    sub.add_parser("show").set_defaults(func=cmd_show)
    sub.add_parser("capacity").set_defaults(func=cmd_capacity)
    sub.add_parser("tts-concurrency").set_defaults(func=cmd_tts_concurrency)
    sub.add_parser("cloud-concurrency").set_defaults(func=cmd_cloud_concurrency)
    s = sub.add_parser("set-cloud-concurrency")
    s.add_argument("value", type=int)
    s.set_defaults(func=cmd_set_cloud_concurrency)
    s = sub.add_parser("locate")
    s.add_argument("stem")
    s.set_defaults(func=cmd_locate)
    s = sub.add_parser("delegate-info", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.set_defaults(func=cmd_delegate_info)
    s = sub.add_parser("reserve-dispatch", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--allow-existing", action="store_true")
    s.set_defaults(func=cmd_reserve_dispatch)
    s = sub.add_parser("record-dispatch", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--status", choices=("submitted", "merged"), default="submitted")
    s.add_argument("--task-ref")
    s.set_defaults(func=cmd_record_dispatch)
    s = sub.add_parser("fail-dispatch", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--error", required=True)
    s.add_argument("--outcome", choices=("failed", "unknown"), default="unknown")
    s.set_defaults(func=cmd_fail_dispatch)
    sub.add_parser("dispatchable", help=argparse.SUPPRESS).set_defaults(
        func=cmd_dispatchable)
    s = sub.add_parser("can-claim", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--program")
    s.set_defaults(func=cmd_can_claim)
    s = sub.add_parser("claim-local", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--program", required=True)
    s.set_defaults(func=cmd_claim_local)
    s = sub.add_parser("can-resume", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--program")
    s.set_defaults(func=cmd_can_resume)
    s = sub.add_parser("can-ship", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.set_defaults(func=cmd_can_ship)
    s = sub.add_parser("can-attempt")
    s.add_argument("workspace")
    s.set_defaults(func=cmd_can_attempt)
    s = sub.add_parser("record-failure")
    for name in ("workspace", "stem", "program", "error_class", "reason",
                 "command", "exit_code", "log", "next_action"):
        s.add_argument(f"--{name.replace('_', '-')}", required=True)
    s.set_defaults(func=cmd_record_failure)
    s = sub.add_parser("import-legacy-failure", help=argparse.SUPPRESS)
    for name in ("workspace", "stem", "program", "error_class", "reason",
                 "next_action"):
        s.add_argument(f"--{name.replace('_', '-')}", required=True)
    s.add_argument("--failed-at")
    s.set_defaults(func=cmd_import_legacy_failure)
    s = sub.add_parser("record-success")
    s.add_argument("--workspace", required=True)
    s.add_argument("--stem", required=True)
    s.add_argument("--phase", required=True)
    s.set_defaults(func=cmd_record_success)
    s = sub.add_parser("record-encode-review")
    s.add_argument("stem")
    s.add_argument("--backend", choices=("cloud", "local"), required=True)
    s.add_argument("--verdict", choices=("PASS", "FAIL"), required=True)
    s.add_argument("--finding", action="append", default=[])
    s.set_defaults(func=cmd_record_encode_review)
    sub.add_parser("post-review-required").set_defaults(func=cmd_post_review_required)
    s = sub.add_parser("retry")
    s.add_argument("stem")
    s.add_argument("--reason", required=True)
    s.set_defaults(func=cmd_retry)
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    raise SystemExit(args.func(args))
