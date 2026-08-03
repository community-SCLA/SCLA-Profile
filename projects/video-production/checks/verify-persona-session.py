#!/usr/bin/env python3
"""Verify one screening-panel persona session.

SCLA-owned replacement for the generic focus-group template checker. Keeps
the substance — a reaction, graded evaluator notes, and an EXECUTED session
validator — and drops the exact-title regexes and the 1500-word cap that
failed honest persona work on formatting.

A persona session proves three things: the persona watched the actual video,
reacted in character, and graded it against named criteria. Exit 0 only when
all three hold.
"""
import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

REACTION_SECTIONS = ("What Landed", "What Felt Wrong", "Would I Continue")
NOTES_SECTIONS = ("Criteria Grades", "Evidence")
GRADE = re.compile(r"\b(PASS|FAIL|MIXED)\b", re.IGNORECASE)

fails = []


def fail(name, detail):
    fails.append(f"FAIL [{name}]: {detail}")


def read(path, label):
    if not path.is_file():
        fail(f"missing_{label}", f"{path} does not exist")
        return ""
    if path.stat().st_size == 0:
        fail(f"empty_{label}", f"{path} is empty")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require_sections(text, sections, label):
    lowered = text.lower()
    for heading in sections:
        if heading.lower() not in lowered:
            fail(f"{label}_missing_section", f"{label} has no '{heading}' section")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-dir", required=True, type=Path)
    ap.add_argument("--reaction", required=True, type=Path)
    ap.add_argument("--notes", required=True, type=Path)
    ap.add_argument("--session-validator", required=True,
                    help="command proving the persona saw the real artifact; "
                         "{session_dir} is substituted")
    args = ap.parse_args()

    if not args.session_dir.is_dir():
        fail("missing_session_dir", f"{args.session_dir} does not exist")

    reaction = read(args.reaction, "reaction")
    notes = read(args.notes, "notes")

    if reaction:
        require_sections(reaction, REACTION_SECTIONS, "reaction")
    if notes:
        require_sections(notes, NOTES_SECTIONS, "notes")
        if not GRADE.search(notes):
            fail("notes_missing_grade",
                 "evaluator notes must grade each criterion PASS, FAIL, or MIXED")

    command = args.session_validator.strip()
    if not command or command.lower() == "none" or "{{" in command:
        fail("validator_missing",
             "--session-validator must run a real check that the persona saw the artifact")
    else:
        resolved = command.replace("{session_dir}", shlex.quote(str(args.session_dir)))
        result = subprocess.run(resolved, shell=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            fail("session_validator_failed",
                 f"exited {result.returncode}: {resolved}\n{(result.stdout or '').strip()[-3000:]}")

    if fails:
        for item in fails:
            print(item)
        return 1
    print(f"PASS [persona_contract]: {args.session_dir} — in-character reaction, "
          "graded criteria, and a validated session")
    return 0


if __name__ == "__main__":
    sys.exit(main())
