#!/usr/bin/env python3
"""Run a fix task's real verifier and harvest its work out of the worktree.

SCLA-owned replacement for the generic fix-swarm template checker. What it
keeps from that template is the part that mattered: it EXECUTES the task's
verify command (that is the actual gate), enforces file ownership, and
exports the patch before Ringer deletes the passing worktree.

What it drops: the '# Fix Summary' title regex, the four exact '## ' heading
regexes, and the 700-word cap — format rules that failed honest fixes.
Sections are matched as case-insensitive substrings instead.

What it ADDS (the 2026-08-03 round-3 build failure): `git add -A` cannot
stage gitignored paths, and in this repo `lessons/**/render/` and
`lessons/**/audio/` ARE gitignored — so a worker's re-rendered MP4 was never
in the exported patch and died with its worktree. --export-dir copies those
paths out explicitly and fails if they are missing.

Exit 0 only when the verifier passed, the patch exported, and every declared
export landed.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_SECTIONS = ("Summary", "Files Changed", "Verification")

fails = []


def fail(name, detail):
    fails.append(f"FAIL [{name}]: {detail}")


def tail(text, limit=4000):
    text = (text or "").strip()
    return text if len(text) <= limit else text[-limit:]


def git(*args):
    return subprocess.run(["git", *args], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def parse_list(raw):
    items = []
    for line in re.split(r"[;,\n]", raw or ""):
        item = line.strip().strip("'\"")
        if item:
            items.append(item[2:] if item.startswith("./") else item.rstrip("/"))
    return items


def owned(path, owned_files):
    if "*" in owned_files:
        return True
    clean = path[2:] if path.startswith("./") else path
    return any(clean == item or clean.startswith(item.rstrip("/") + "/")
               for item in owned_files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-command", required=True,
                    help="the real gate — its exit code decides the task")
    ap.add_argument("--patch", required=True, type=Path)
    ap.add_argument("--summary", required=True, type=Path)
    ap.add_argument("--exported-summary", required=True, type=Path)
    ap.add_argument("--owned-files", required=True)
    ap.add_argument("--require", nargs="+", default=list(DEFAULT_SECTIONS))
    ap.add_argument("--export-dir", action="append", default=[], metavar="SRC:DEST",
                    help="copy a gitignored path out of the worktree (repeatable); "
                         "missing SRC is a hard failure")
    args = ap.parse_args()

    for name, value in (("verify_command", args.verify_command),
                        ("patch", str(args.patch)),
                        ("owned_files", args.owned_files)):
        if "{{" in value or "}}" in value:
            fail("placeholder_unfilled", f"{name} still contains an unfilled placeholder")

    owned_files = parse_list(args.owned_files)
    if not owned_files:
        fail("missing_owned_files", "--owned-files is empty; every fix task must declare its ownership")

    # --- the summary: present, substantial, and carrying its sections ---
    if not args.summary.is_file():
        fail("missing_summary", f"{args.summary} does not exist")
    elif args.summary.stat().st_size == 0:
        fail("empty_summary", f"{args.summary} is empty")
    else:
        text = args.summary.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        for heading in args.require:
            if heading.lower() not in lowered:
                fail("missing_summary_section", f"fix summary has no '{heading}' section")
        args.exported_summary.parent.mkdir(parents=True, exist_ok=True)
        args.exported_summary.write_text(text, encoding="utf-8")

    # --- the real gate ---
    verify = subprocess.run(args.verify_command, shell=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if verify.returncode != 0:
        fail("verify_command_failed",
             f"exited {verify.returncode}: {args.verify_command}\n{tail(verify.stdout)}")
    else:
        print(f"PASS [verify_command]: {args.verify_command}")

    # --- harvest: patch for tracked files ---
    add = git("add", "-A")
    if add.returncode != 0:
        fail("git_add_failed", tail(add.stdout))
    if not args.summary.is_absolute() and args.summary.exists():
        git("reset", "--quiet", "--", str(args.summary))

    names = git("diff", "--cached", "--name-only", "-z")
    changed = [item for item in names.stdout.split("\0") if item]
    if names.returncode != 0:
        fail("git_diff_names_failed", tail(names.stdout))
    elif not changed:
        fail("empty_patch", "no staged changes — the worker produced no tracked edits")
    else:
        for path in changed:
            if not owned(path, owned_files):
                fail("outside_owned_files", f"{path} is outside this task's declared ownership")

    diff = git("diff", "--cached", "--binary")
    if diff.returncode != 0:
        fail("git_diff_failed", tail(diff.stdout))
    elif diff.stdout.strip():
        args.patch.parent.mkdir(parents=True, exist_ok=True)
        args.patch.write_text(diff.stdout, encoding="utf-8")
    if not args.patch.is_file() or args.patch.stat().st_size == 0:
        fail("patch_not_written", f"{args.patch} was not written or is empty")

    # --- harvest: gitignored outputs the patch cannot carry ---
    for spec in args.export_dir:
        src_raw, _, dest_raw = spec.partition(":")
        src, dest = Path(src_raw), Path(dest_raw)
        if not dest_raw:
            fail("bad_export_dir", f"--export-dir {spec!r} must be SRC:DEST")
            continue
        if not src.exists():
            fail("export_source_missing",
                 f"{src} does not exist — a gitignored deliverable the patch cannot carry is absent")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copyfile(src, dest)
        print(f"exported {src} -> {dest}")

    if fails:
        for item in fails:
            print(item)
        return 1
    print(f"PASS [fix_contract]: verifier passed; exported {args.patch} with {len(changed)} changed file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
