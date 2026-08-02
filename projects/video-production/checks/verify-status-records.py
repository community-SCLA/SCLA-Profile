#!/usr/bin/env python3
"""Status-record gate for the SCLA lesson-video pipeline.

Every lesson has exactly one record on disk saying where it stands, and a
record that lies is worse than no record: a resuming session reads `stage` and
`next_action` and acts on them without re-deriving anything. This grades the
records themselves — not the work they describe.

Enforced:
  1. every `lesson-scripts/<program>/refined/<stem>.txt` has a matching
     `lessons/<program>/<stem>/status.yml`
  2. every status.yml parses as a YAML mapping
  3. `stage` is one of scripted|narrated|composed|rendered|published|blocked
  4. `next_action` is a non-empty string unless stage == published
  5. `blocked` is non-null with `on` in owner|vendor|upstream iff stage ==
     blocked
  6. `wistia_hashed_id` is null unless stage == published (never invented)

Prints file-and-reason for every violation. Exit 0 = clean, 1 = violations,
2 = the tree is not where it is expected to be.
"""
from __future__ import annotations

import sys
from pathlib import Path

VP = Path(__file__).resolve().parent.parent
LESSON_SCRIPTS = VP / "lesson-scripts"
LESSONS = VP / "lessons"

STAGES = ("scripted", "narrated", "composed", "rendered", "published", "blocked")
BLOCKED_ON = ("owner", "vendor", "upstream")

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a data problem
    print("FAIL: PyYAML is not installed; cannot grade status records")
    sys.exit(2)


def blocked_on(blocked: dict):
    """The `on:` key, which YAML 1.1 parses as the boolean True.

    The schema in PROCESS.md writes `on: owner` unquoted because that is what
    a human writes and what the report specified. PyYAML resolves a bare `on`
    key to True, so a naive .get("on") reports every well-formed blocked
    record as missing its owner — a false failure on the one record type that
    exists to be read by a person.
    """
    if "on" in blocked:
        return blocked["on"]
    return blocked.get(True)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(VP.parent.parent))
    except ValueError:
        return str(p)


def main() -> int:
    if not LESSON_SCRIPTS.is_dir():
        print(f"FAIL: {rel(LESSON_SCRIPTS)} is not a directory")
        return 2

    problems: list[str] = []
    n_scripts = 0
    n_records = 0

    # ── 1. every refined script has a record ───────────────────────────────
    for program_dir in sorted(p for p in LESSON_SCRIPTS.iterdir() if p.is_dir()):
        refined = program_dir / "refined"
        if not refined.is_dir():
            continue
        for txt in sorted(refined.glob("*.txt")):
            n_scripts += 1
            record = LESSONS / program_dir.name / txt.stem / "status.yml"
            if not record.is_file():
                problems.append(
                    f"{rel(txt)}: no status record — expected {rel(record)} "
                    f"(mkdir of the lesson dir is the build lock; every refined "
                    f"script needs one)")

    if not n_scripts:
        print(f"FAIL: no refined scripts found under {rel(LESSON_SCRIPTS)}")
        return 2

    # ── 2-6. every record on disk is well-formed ───────────────────────────
    for record in sorted(LESSONS.glob("*/*/status.yml")) if LESSONS.is_dir() else []:
        n_records += 1
        where = rel(record)
        try:
            data = yaml.safe_load(record.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(f"{where}: does not parse as YAML — {exc}")
            continue
        if not isinstance(data, dict):
            problems.append(
                f"{where}: top level is {type(data).__name__}, must be a mapping")
            continue

        stage = data.get("stage")
        if stage not in STAGES:
            problems.append(
                f"{where}: stage {stage!r} is not one of {'|'.join(STAGES)}")
            # every remaining rule keys off stage; nothing more to say here
            continue

        next_action = data.get("next_action")
        if stage != "published":
            if not isinstance(next_action, str) or not next_action.strip():
                problems.append(
                    f"{where}: stage '{stage}' needs a non-empty next_action — a "
                    f"resuming session reads this field to know what to do")

        blocked = data.get("blocked")
        if stage == "blocked":
            if not isinstance(blocked, dict):
                problems.append(
                    f"{where}: stage 'blocked' requires a blocked: mapping naming "
                    f"who it waits on, got {blocked!r}")
            else:
                on = blocked_on(blocked)
                if on not in BLOCKED_ON:
                    problems.append(
                        f"{where}: blocked.on {on!r} is not one of "
                        f"{'|'.join(BLOCKED_ON)} — the board groups by who is "
                        f"holding it up")
                reason = blocked.get("reason")
                if not isinstance(reason, str) or not reason.strip():
                    problems.append(
                        f"{where}: blocked records need a reason a reader can act on")
        elif blocked is not None:
            problems.append(
                f"{where}: blocked must be null unless stage == blocked "
                f"(stage is '{stage}')")

        hashed = data.get("wistia_hashed_id")
        if stage != "published" and hashed is not None:
            problems.append(
                f"{where}: wistia_hashed_id {hashed!r} is set but stage is "
                f"'{stage}' — an ID only exists once the media is live; never "
                f"invent one")
        if stage == "published" and (not isinstance(hashed, str) or not hashed.strip()):
            problems.append(
                f"{where}: stage 'published' must record the real "
                f"wistia_hashed_id, got {hashed!r}")

    if problems:
        print(f"FAIL: {len(problems)} status-record problem(s) across "
              f"{n_records} record(s) / {n_scripts} refined script(s)\n")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"OK: {n_records} status record(s) valid; every one of {n_scripts} "
          f"refined script(s) has one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
