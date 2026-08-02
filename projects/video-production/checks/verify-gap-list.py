#!/usr/bin/env python3
"""Executable check for the wistia-gap-list task.

Validates gap-list.tsv against BOTH ground truths, so a fabricated list fails:
  1. Disk: every lesson script on disk (refined/*.txt plus unrefined *.txt at
     each program root) appears exactly once, and no invented rows exist.
  2. Wistia: re-queries each program's Wistia project (GET only). Every row
     marked 'live' must cite a hashed id that really exists in that project;
     every row marked 'missing' must not obviously match a live media name.

Requires the WISTIA_API env var — run under scripts/with-secrets.sh.
Prints every failure with its reason. Copies the TSV to --export on success.
"""
import argparse
import csv
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path

REL_PREFIX = "projects/video-production/lesson-scripts"
COLUMNS = ["program", "lesson_stem", "script_path", "status", "wistia_hashed_id", "wistia_title"]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def core_stem(stem: str, program: str) -> str:
    s = re.sub(r"^m\d+_", "", stem)
    s = re.sub(r"_" + re.escape(program) + r"$", "", s)
    return norm(s)


def fetch_medias(token: str, project_id: str):
    medias, page = [], 1
    while page <= 10:
        url = (f"https://api.wistia.com/v1/medias.json"
               f"?project_id={project_id}&per_page=100&page={page}")
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.load(resp)
        medias.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return medias


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", required=True)
    ap.add_argument("--endpoints", required=True, help="path to config/endpoints.json")
    ap.add_argument("--scripts-root", required=True, help="absolute path to lesson-scripts/")
    ap.add_argument("--export", help="copy the TSV here on success")
    args = ap.parse_args()

    failures = []
    token = os.environ.get("WISTIA_API")
    if not token:
        print("FAIL: WISTIA_API is not set — run this check under scripts/with-secrets.sh")
        return 2

    endpoints = json.loads(Path(args.endpoints).read_text())
    projects = {e["program_slug"]: str(e["id"])
                for e in endpoints["wistia"]
                if e.get("type") == "project" and e.get("program_slug") and e.get("id")}
    if not projects:
        print("FAIL: no wistia projects found in endpoints registry")
        return 2

    # Ground truth 1: scripts on disk.
    root = Path(args.scripts_root)
    disk = {}  # repo-relative path -> program
    for program in projects:
        pdir = root / program
        if not pdir.is_dir():
            failures.append(f"program directory missing on disk: {pdir}")
            continue
        for f in pdir.glob("*.txt"):
            disk[f"{REL_PREFIX}/{program}/{f.name}"] = program
        for f in (pdir / "refined").glob("*.txt"):
            disk[f"{REL_PREFIX}/{program}/refined/{f.name}"] = program

    # Parse the TSV.
    tsv_path = Path(args.tsv)
    if not tsv_path.is_file():
        print(f"FAIL: {tsv_path} does not exist")
        return 2
    with open(tsv_path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        rows = list(reader)
    if not rows:
        print("FAIL: TSV is empty")
        return 2
    header = [h.strip().lower() for h in rows[0]]
    if header[: len(COLUMNS)] != COLUMNS:
        failures.append(f"TSV header must start with {COLUMNS}, got {header}")
        rows = []
    body = []
    for i, row in enumerate(rows[1:], 2):
        if not any(cell.strip() for cell in row):
            continue
        if len(row) < len(COLUMNS):
            failures.append(f"line {i}: expected {len(COLUMNS)} columns, got {len(row)}")
            continue
        body.append((i, dict(zip(COLUMNS, (c.strip() for c in row)))))

    # Disk <-> TSV set equality.
    tsv_paths = [r["script_path"] for _, r in body]
    for p in disk:
        if p not in tsv_paths:
            failures.append(f"script on disk but absent from TSV: {p}")
    seen = set()
    for i, r in body:
        p = r["script_path"]
        if p not in disk:
            failures.append(f"line {i}: script_path not found on disk (invented row?): {p}")
        elif r["program"] != disk[p]:
            failures.append(f"line {i}: program {r['program']!r} does not match path {p}")
        if p in seen:
            failures.append(f"line {i}: duplicate row for {p}")
        seen.add(p)
        if r["status"] not in ("live", "missing"):
            failures.append(f"line {i}: status must be live|missing, got {r['status']!r}")
        if r["status"] == "live" and r["wistia_hashed_id"] in ("", "NULL"):
            failures.append(f"line {i}: live row without a wistia_hashed_id")
        if r["status"] == "missing" and r["wistia_hashed_id"] != "NULL":
            failures.append(f"line {i}: missing row must carry NULL, got {r['wistia_hashed_id']!r}")

    # Ground truth 2: Wistia itself.
    counts = {}
    for program, project_id in projects.items():
        try:
            medias = fetch_medias(token, project_id)
        except Exception as exc:  # noqa: BLE001 — any API failure is a hard stop
            print(f"FAIL: Wistia API query failed for {program} (project {project_id}): {exc}")
            return 2
        hashed = {m.get("hashed_id") for m in medias}
        names = {m.get("hashed_id"): m.get("name", "") for m in medias}
        counts[program] = len(medias)
        for i, r in (x for x in body if x[1]["program"] == program):
            if r["status"] == "live" and r["wistia_hashed_id"] not in hashed:
                failures.append(
                    f"line {i}: claims live but hashed id {r['wistia_hashed_id']!r} "
                    f"is not in Wistia project {project_id} ({program})")
            if r["status"] == "missing":
                core = core_stem(r["lesson_stem"], program)
                for hid, name in names.items():
                    if core and core in norm(name):
                        failures.append(
                            f"line {i}: marked missing but Wistia media {hid!r} "
                            f"({name!r}) matches stem {r['lesson_stem']!r} — publishing would duplicate it")

    for program, n in counts.items():
        live = sum(1 for _, r in body if r["program"] == program and r["status"] == "live")
        miss = sum(1 for _, r in body if r["program"] == program and r["status"] == "missing")
        print(f"{program}: {n} media(s) on Wistia; TSV says {live} live / {miss} missing")

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        print(f"\nFAIL: {len(failures)} problem(s) in {tsv_path}")
        return 1

    if args.export:
        dest = Path(args.export)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tsv_path, dest)
        print(f"exported {tsv_path} -> {dest}")
    print(f"OK: {len(body)} rows verified against disk and Wistia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
