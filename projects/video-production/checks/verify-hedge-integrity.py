#!/usr/bin/env python3
"""Hedge-language integrity checker for SCLA lesson videos.

The refined narration script is the source of truth for qualified claims
("seems to", "it is easy to think", ...). Compares it against the on-screen
copy in the composed workspace and flags any hedge marker that appears in
the narration but was dropped from the build — a qualified claim rendered
as an unqualified one. Prints file:line and the missing marker; exits
non-zero if any marker regressed. This is a mechanical floor: it proves a
marker survived somewhere on screen, not that phrasing or tone is right.
"""
import argparse
import sys
from pathlib import Path

HEDGE_MARKERS = [
    "seems to",
    "it is easy to think",
    "the whole story of",
    "tends to",
    "may not",
    "is usually",
    "can feel like",
    "often feels",
    "in some cases",
    "not always",
    "a version of",
    "one way to",
]


def find_markers(text: str) -> set[str]:
    lowered = text.lower()
    return {marker for marker in HEDGE_MARKERS if marker in lowered}


def marker_line(text: str, marker: str) -> int | str:
    for lineno, line in enumerate(text.splitlines(), 1):
        if marker in line.lower():
            return lineno
    return "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, type=Path,
                     help="refined narration .txt (source of truth for hedges)")
    ap.add_argument("--build", required=True, type=Path,
                     help="on-screen copy file, e.g. workspace/index.html")
    args = ap.parse_args()

    if not args.script.is_file():
        print(f"FAIL: {args.script} is not a file")
        return 2
    if not args.build.is_file():
        print(f"FAIL: {args.build} is not a file")
        return 2

    script_text = args.script.read_text(encoding="utf-8", errors="replace")
    build_text = args.build.read_text(encoding="utf-8", errors="replace")

    script_markers = find_markers(script_text)
    build_markers = find_markers(build_text)
    dropped = sorted(script_markers - build_markers)

    if dropped:
        for marker in dropped:
            lineno = marker_line(script_text, marker)
            print(f"{args.script}:{lineno}: hedge marker {marker!r} present in "
                  f"narration but missing from {args.build}")
        print(f"\nFAIL: {len(dropped)} hedge marker(s) dropped between script and build")
        return 1

    print(f"OK: {len(script_markers)} hedge marker(s) in narration all present "
          f"in on-screen build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
