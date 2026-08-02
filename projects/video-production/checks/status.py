#!/usr/bin/env python3
"""The board — where every SCLA lesson video stands, read at call time.

A reader, not a gate: it never fails and never writes. It globs
`lessons/<program>/<stem>/status.yml` and prints

  1. lessons blocked on the owner, with the reason and how long they have waited
  2. one table per program — stem, stage, next action
  3. a tally by stage

Because it reads the records themselves, it cannot go stale and there is no
generated file to refresh. Grading the records is a different job:
`verify-status-records.py`, wired into `scripts/lint-refs.sh`.

Usage:  python3 projects/video-production/checks/status.py
Exit:   always 0.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

VP = Path(__file__).resolve().parent.parent
LESSONS = VP / "lessons"

STAGE_ORDER = ["scripted", "narrated", "composed", "rendered", "published", "blocked"]
# Order the owner asked for the programs to be produced in (brief.md).
PROGRAM_ORDER = ["early-career-boost", "mid-career-momentum",
                 "career-transitions", "entrepreneur-accelerator"]

try:
    import yaml
except ImportError:
    print("PyYAML is not installed — cannot read the board.")
    sys.exit(0)


def load() -> list[dict]:
    if not LESSONS.is_dir():
        return []
    out = []
    for record in sorted(LESSONS.glob("*/*/status.yml")):
        try:
            data = yaml.safe_load(record.read_text(encoding="utf-8"))
        except Exception as exc:
            data = {"stage": "?unreadable", "next_action": f"fix this file: {exc}"}
        if not isinstance(data, dict):
            data = {"stage": "?unreadable", "next_action": "not a YAML mapping"}
        data.setdefault("program", record.parent.parent.name)
        data.setdefault("stem", record.parent.name)
        data["_path"] = record
        out.append(data)
    return out


def blocked_on(blocked: dict):
    """`on:` is spelled bare in the record; YAML 1.1 resolves it to True."""
    return blocked["on"] if "on" in blocked else blocked.get(True)


def age_days(since) -> str:
    if not since:
        return "age unknown"
    try:
        if isinstance(since, datetime.date):
            d = since
        else:
            d = datetime.date.fromisoformat(str(since).strip())
    except ValueError:
        return f"since {since}"
    n = (datetime.date.today() - d).days
    if n < 0:
        return f"since {d.isoformat()}"
    return f"{n} day{'' if n == 1 else 's'} (since {d.isoformat()})"


def truncate(s: str, width: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= width else s[: width - 1] + "…"


def program_sort_key(name: str):
    return (PROGRAM_ORDER.index(name) if name in PROGRAM_ORDER else 99, name)


def main() -> int:
    records = load()
    print("SCLA lesson videos — the board")
    print(f"read {datetime.date.today().isoformat()} from "
          f"{LESSONS.relative_to(VP.parent.parent)}/<program>/<stem>/status.yml")
    print()

    if not records:
        print("No lesson records yet. A lesson begins when an agent creates")
        print("lessons/<program>/<stem>/status.yml — see PROCESS.md.")
        return 0

    # ── 1. blocked on the owner ────────────────────────────────────────────
    owner_queue = [r for r in records
                   if r.get("stage") == "blocked"
                   and isinstance(r.get("blocked"), dict)
                   and blocked_on(r["blocked"]) == "owner"]
    print(f"BLOCKED ON OWNER ({len(owner_queue)})")
    print("-" * 78)
    if not owner_queue:
        print("  nothing waiting on you.")
    for r in owner_queue:
        b = r["blocked"]
        print(f"  {r['stem']}  [{r['program']}]")
        print(f"      why : {truncate(b.get('reason', '(no reason recorded)'), 66)}")
        print(f"      held: {age_days(b.get('since'))}")
        print(f"      next: {truncate(r.get('next_action') or '(none)', 66)}")
    print()

    # ── 2. one table per program ───────────────────────────────────────────
    programs = sorted({r.get("program", "?") for r in records}, key=program_sort_key)
    for program in programs:
        rows = sorted((r for r in records if r.get("program") == program),
                      key=lambda r: str(r.get("stem", "")))
        print(f"{program.upper()}  ({len(rows)} lesson{'' if len(rows) == 1 else 's'})")
        print("-" * 78)
        print(f"  {'STEM':<46} {'STAGE':<10} NEXT ACTION")
        for r in rows:
            stage = str(r.get("stage", "?"))
            if stage == "published":
                nxt = f"live: {r.get('wistia_hashed_id') or '(no id recorded)'}"
            else:
                nxt = r.get("next_action") or "(none recorded)"
            print(f"  {truncate(r.get('stem', '?'), 46):<46} "
                  f"{truncate(stage, 10):<10} {truncate(nxt, 60)}")
        print()

    # ── 3. tally ───────────────────────────────────────────────────────────
    print(f"TALLY ({len(records)} lessons)")
    print("-" * 78)
    seen = [str(r.get("stage", "?")) for r in records]
    known = [s for s in STAGE_ORDER if s in seen]
    other = sorted({s for s in seen if s not in STAGE_ORDER})
    for stage in known + other:
        n = seen.count(stage)
        print(f"  {stage:<12} {n:>3}  {'#' * n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
