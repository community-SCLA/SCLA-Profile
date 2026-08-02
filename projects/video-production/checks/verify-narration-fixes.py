#!/usr/bin/env python3
"""Narration-hazard scanner for SCLA lesson scripts.

Scans the .txt files directly inside --dir (non-recursive) for constructions a
TTS voice stumbles on. Prints file:line and the reason for every hit; exits
non-zero if any remain. This is the executable floor for the narration-polish
fix lanes — it cannot judge flow, only mechanical hazards.
"""
import argparse
import re
import sys
from pathlib import Path

HAZARDS = [
    (re.compile(r"&"), "ampersand — write 'and'"),
    (re.compile(r"\be\.g\.", re.I), "'e.g.' — say 'for example'"),
    (re.compile(r"\bi\.e\.", re.I), "'i.e.' — say 'that is'"),
    (re.compile(r"\betc\b", re.I), "'etc' — finish the list or drop it"),
    (re.compile(r"\bvs\b\.?", re.I), "'vs' — say 'versus'"),
    (re.compile(r"https?://|\bwww\.", re.I), "URL — a voice cannot read a URL"),
    (re.compile(r"[A-Za-z]{2,}/[A-Za-z]{2,}"), "word/word slash — pick one or say 'or'"),
    (re.compile(r"%"), "percent sign — write 'percent'"),
    (re.compile(r"\$\d"), "dollar-digit — spell out the amount"),
    (re.compile(r"\((?!k\))", re.I), "parenthetical aside — fold it into the sentence"),
    (re.compile(r"^\s*#"), "markdown heading — narration is plain prose"),
    (re.compile(r"\*\*|`"), "markdown markup in narration"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="directory whose top-level .txt files are scanned")
    args = ap.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"FAIL: {root} is not a directory")
        return 2
    files = sorted(p for p in root.iterdir() if p.is_file() and p.suffix == ".txt")
    if not files:
        print(f"FAIL: no .txt files directly inside {root}")
        return 2

    hits = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            print(f"{path}: file is empty")
            hits += 1
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, reason in HAZARDS:
                m = pattern.search(line)
                if m:
                    print(f"{path}:{lineno}: {reason} (matched {m.group(0)!r})")
                    hits += 1

    if hits:
        print(f"\nFAIL: {hits} narration hazard(s) across {len(files)} file(s)")
        return 1
    print(f"OK: {len(files)} script(s) clean of mechanical narration hazards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
