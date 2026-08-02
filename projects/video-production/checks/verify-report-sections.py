#!/usr/bin/env python3
"""Structural check for a worker-written report.

Verifies the report exists, meets a size floor, and contains every required
section heading (case-insensitive substring — tolerant on format, strict on
presence). Prints exactly what is missing. On success optionally copies the
report to --export so it survives a doomed worktree.
"""
import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--require", nargs="+", required=True, help="section names that must appear")
    ap.add_argument("--min-bytes", type=int, default=1500)
    ap.add_argument("--export", help="copy the report here on success")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"FAIL: {path} does not exist")
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    failures = []
    if len(text.encode()) < args.min_bytes:
        failures.append(f"report is {len(text.encode())} bytes; floor is {args.min_bytes} — too thin to be real work")
    lowered = text.lower()
    for section in args.require:
        if section.lower() not in lowered:
            failures.append(f"required section not found: {section!r}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    if args.export:
        dest = Path(args.export)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        print(f"exported {path} -> {dest}")
    print(f"OK: {path} has all {len(args.require)} required sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
