#!/usr/bin/env python3
"""Persistent control state for SCLA video runs and per-workspace failures.

Video lifecycle remains folder-owned.  This file stores only facts folders
cannot represent: explicit run scope, batch review approval, retry counts and the
cross-video circuit breaker.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


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


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


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
    return read_json(RUN_FILE, {})


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
    for program_dir in sorted(p for p in lessons.iterdir() if p.is_dir()):
        for stage in ("inbox", "ready", "published"):
            if (program_dir / stage / f"{stem}.txt").is_file():
                return {"stem": stem, "program": program_dir.name, "stage": stage}
    workspace = VP / "renders-hyperframes" / stem
    if workspace.is_dir():
        return {"stem": stem, "program": None, "stage": "workspace"}
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
            selected.append({"stem": script.stem, "program": program_dir.name,
                             "stage": "ready"})
    return selected


def new_run(mode: str, scope_kind: str, scope_value: str | None,
            selected: list[dict]) -> dict:
    backend_file = VP / "renders-hyperframes" / "_run" / "RENDER-BACKEND"
    try:
        backend = backend_file.read_text(encoding="utf-8").strip() or "local"
    except OSError:
        backend = "local"
    created = now()
    state = {
        "version": 3,
        "mode": mode,
        "scope": {"kind": scope_kind, "value": scope_value},
        "items": selected,
        "review": {"approved_at": None, "approved_by": None, "stems": []},
        "backend": backend,
        # These stages consume different resources and must not share one
        # ambiguous lane count. Cloud authoring is isolated; provider calls,
        # renders and publishing use their own machine-wide queues.
        "authoring_concurrency": 6 if backend == "cloud" else 3,
        "tts_concurrency": DEFAULT_TTS_CONCURRENCY,
        "cloud_render_concurrency": DEFAULT_CLOUD_RENDER_CONCURRENCY,
        "cloud_render_max": MAX_CLOUD_RENDER_CONCURRENCY,
        "publish_concurrency": 1,
        "retry_limit": DEFAULT_RETRY_LIMIT,
        "circuit_breaker_limit": DEFAULT_CIRCUIT_LIMIT,
        "circuit_breaker": {
            "open": False, "error_class": None, "count": 0,
            "stems": [], "opened_at": None,
        },
        "cloud_clean_streak": 0,
        "cloud_clean_stems": [],
        "created_at": created,
        "updated_at": created,
    }
    save_run(state)
    return state


def cmd_select(args) -> int:
    with run_write_lock():
        if args.scope_kind == "stem":
            selected = [locate(args.scope_value)]
        else:
            selected = queue(args.scope_kind, args.scope_value)
        state = new_run(args.mode, args.scope_kind, args.scope_value, selected)
    print(json.dumps(state, indent=2))
    return 0


def cmd_approve(args) -> int:
    with run_write_lock():
        state = load_run()
        if not state:
            raise SystemExit("FATAL: no active run; select a stem or batch first")
        selected = [x.get("stem") for x in state.get("items", []) if x.get("stem")]
        if state.get("mode") == "batch":
            if not selected:
                raise SystemExit(
                    "FATAL: the active batch has no selected workspaces to review")
            if args.target.upper() != "BATCH":
                raise SystemExit(
                    "FATAL: batch review approval covers the complete selected set; "
                    "use run.sh approve BATCH after reviewing every workspace")
            missing = [stem for stem in selected if not (
                VP / "renders-hyperframes" / stem / "qa" / "PREFLIGHT-OK").is_file()]
            if missing:
                raise SystemExit(
                    "FATAL: batch review is incomplete; these selected workspaces are "
                    "not gate-clean: " + ", ".join(missing))
            state["review"] = {"approved_at": now(),
                               "approved_by": args.approved_by,
                               "stems": selected}
            message = f"approved batch review: {len(selected)} workspaces"
        else:
            if args.target not in selected:
                raise SystemExit(f"FATAL: {args.target} is outside the active run")
            workspace = VP / "renders-hyperframes" / args.target
            if not (workspace / "qa" / "PREFLIGHT-OK").is_file():
                raise SystemExit(
                    f"FATAL: {args.target} is not gate-clean "
                    "(qa/PREFLIGHT-OK missing)")
            state["review"] = {"approved_at": now(),
                               "approved_by": args.approved_by,
                               "stems": [args.target]}
            message = f"approved review: {args.target}"
        save_run(state)
    print(message)
    return 0


def cmd_migrate_approval(args) -> int:
    """Import an approval that predates run.json without asking again."""
    with run_write_lock():
        state = load_run()
        if not state:
            raise SystemExit("FATAL: no active run to migrate")
        locate(args.stem)
        state["review"] = {"stems": [args.stem],
                           "approved_at": args.approved_at,
                           "approved_by": "owner", "source": "legacy-approved-pilot"}
        save_run(state)
    print(f"migrated approved pilot: {args.stem}")
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
        if value > 2 and state.get("mode") == "batch":
            selected = {
                x.get("stem") for x in state.get("items", []) if x.get("stem")
            }
            review = state.get("review") or {}
            reviewed = set(review.get("stems") or [])
            if (not selected or not review.get("approved_at") or
                    not selected.issubset(reviewed)):
                raise SystemExit(
                    "FATAL: four cloud renders require approval of the complete "
                    "batch review set")
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
    print(json.dumps({"stem": args.stem, "program": program,
                      "stage": "ready"}))
    return 0


def cmd_can_ship(args) -> int:
    state = load_run()
    if not state:
        raise SystemExit("FATAL: no active run; select a stem or batch first")
    selected = {x.get("stem") for x in state.get("items", [])}
    if args.stem not in selected:
        raise SystemExit(f"FATAL: {args.stem} is outside the active run")
    if state.get("mode") == "batch":
        review = state.get("review") or {}
        approved = set(review.get("stems") or [])
        if not review.get("approved_at") or not selected.issubset(approved):
            raise SystemExit(
                "FATAL: batch review is not approved; build and review every "
                "selected workspace, then record approval with run.sh approve BATCH")
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
            if args.phase == "cloud-render":
                clean_stems = list(state.get("cloud_clean_stems") or [])
                if args.stem not in clean_stems:
                    clean_stems.append(args.stem)
                state["cloud_clean_stems"] = clean_stems[-3:]
                state["cloud_clean_streak"] = len(state["cloud_clean_stems"])
            closeout(state, args.stem, "complete", phase=args.phase)
            save_run(state)
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
    s.set_defaults(func=cmd_select)
    s = sub.add_parser("approve")
    s.add_argument("target")
    s.add_argument("--approved-by", default="owner")
    s.set_defaults(func=cmd_approve)
    s = sub.add_parser("migrate-approval", help=argparse.SUPPRESS)
    s.add_argument("stem")
    s.add_argument("--approved-at", required=True)
    s.set_defaults(func=cmd_migrate_approval)
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
    sub.add_parser("post-review-required").set_defaults(func=cmd_post_review_required)
    s = sub.add_parser("retry")
    s.add_argument("stem")
    s.add_argument("--reason", required=True)
    s.set_defaults(func=cmd_retry)
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    raise SystemExit(args.func(args))
