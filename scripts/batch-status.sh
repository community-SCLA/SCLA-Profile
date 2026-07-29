#!/usr/bin/env bash
# batch-status.sh — reconstruct the remaining video queue from disk alone.
#
# This is the resume key for an interrupted AUTO-BATCH run. It reads only the
# folders and the ledger; nothing depends on a previous session's context
# surviving. A stem is DONE if and only if it has a Wistia URL in
# refinement-log.md — that URL is committed in the same pass that publishes it,
# so there is never a window where work exists but isn't recorded.
#
# Usage:  bash scripts/batch-status.sh [--json]
#
# Priority order is the drain order: highest-value programs ship first, so an
# interrupted run leaves the most important videos already live. Override with
# VIDEO_PRIORITY="slug-a slug-b ...".
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"

PRIORITY="${VIDEO_PRIORITY:-early-career-boost mid-career-momentum career-transitions entrepreneur-accelerator}"

JSON=0
[[ "${1:-}" == "--json" ]] && JSON=1

PRIORITY="$PRIORITY" LESSONS="$VP/lesson-scripts" VP="$VP" \
WS="$VP/renders-hyperframes" LEDGER="$VP/lesson-scripts/refinement-log.md" \
PUBTSV="$VP/lesson-scripts/published.tsv" QLOG="$VP/render-qa/quarantine.log" \
JSON="$JSON" python3 - <<'PY'
import json, os, re, sys
from pathlib import Path

lessons = Path(os.environ["LESSONS"])
ws_root = Path(os.environ["WS"])
ledger  = Path(os.environ["LEDGER"])
pubtsv  = Path(os.environ["PUBTSV"])
qlog    = Path(os.environ["QLOG"])
as_json = os.environ["JSON"] == "1"
priority = os.environ["PRIORITY"].split()

ledger_text = ledger.read_text(encoding="utf-8", errors="replace") if ledger.exists() else ""

# Every comparison here is on BASE (title_program). Since 2026-07-29 a working
# artifact carries no date, so base_of() is usually the identity function — but
# it stays because the MP4 still carries its render date, refinement-log.md rows
# still quote legacy dated stems, and a workspace built before the change may
# survive. stem.py owns the rule; base() strips any trailing date/clock.
sys.path.insert(0, str(Path(os.environ["VP"]) / "render-qa" / "src"))
from stem import base as stem_base, StemError

def base_of(name: str) -> str:
    try:
        return stem_base(name)
    except StemError:
        return name          # undated/legacy name: compare it as-is

# Primary key: published.tsv — base, written and committed by batch-ship.sh in
# the same pass that uploads. The ledger scan below is a fallback for lessons
# published before the tsv existed (rows abbreviate the stem, so that matching
# is best-effort — the tsv is the contract).
published, media_ids = set(), set()
if pubtsv.exists():
    for line in pubtsv.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) >= 4:
            published.add(cols[0])
            m = re.search(r'wistia\.com/medias/(\w+)', cols[3])
            if m:
                media_ids.add(m.group(1))
for line in ledger_text.splitlines():
    ids = re.findall(r'wistia\.com/medias/(\w+)', line)
    if not ids:
        continue
    media_ids.update(ids)
    for m in re.finditer(r'[A-Za-z0-9][\w.-]*_\d{4}-\d{2}-\d{2}', line):
        published.add(base_of(m.group(0)))

# Workspaces are named with the BUILD date, refined scripts with the REFINE
# date, so a workspace can never be found by joining the script's stem to the
# path. Index them by base instead.
ws_by_base = {}
if ws_root.is_dir():
    for d in ws_root.iterdir():
        if d.is_dir() and not d.name.startswith((".", "_")):
            ws_by_base[base_of(d.name)] = d

# Latest quarantine reason per stem, to annotate stuck videos.
quarantined = {}
if qlog.exists():
    for line in qlog.read_text(encoding="utf-8", errors="replace").splitlines():
        cols = line.split("\t")
        if len(cols) >= 4:
            quarantined[cols[1]] = cols[3]

# Blocked: scripts that must not be built. Detected from content, not a hand-list,
# so a fixed script re-enters the queue automatically with no bookkeeping.
BLOCK_PATTERNS = [
    (re.compile(r'TODO:\s*needs input', re.I),          "TODO: needs input"),
    (re.compile(r'SCRIPT PENDING',      re.I),          "SCRIPT PENDING"),
]

def blocked_reason(p: Path):
    try:
        head = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for rx, label in BLOCK_PATTERNS:
        if rx.search(head):
            return label
    return None

programs = sorted([d.name for d in lessons.iterdir() if d.is_dir()])
ordered  = [p for p in priority if p in programs] + [p for p in programs if p not in priority]

report, totals = [], {"queued": 0, "blocked": 0, "built_unpublished": 0,
                      "rendered_unpublished": 0, "published": 0}

for prog in ordered:
    refined = lessons / prog / "refined"
    if not refined.is_dir():
        continue
    queued, blocked, built, stranded = [], [], [], []
    for f in sorted(refined.glob("*.txt")):          # non-recursive: refined/avatar/ is the HeyGen queue
        stem = f.stem
        if base_of(stem) in published:
            totals["published"] += 1
            continue
        why = blocked_reason(f)
        if why:
            blocked.append((stem, why)); totals["blocked"] += 1
        elif base_of(stem) in ws_by_base:
            # workspace exists but no Wistia URL -> built, unpublished (quarantine or in flight)
            built.append(stem); totals["built_unpublished"] += 1
        else:
            queued.append(stem); totals["queued"] += 1
    # rendered/ without a published record = stranded mid-pipeline (render,
    # verify, vision, upload or commit did not complete). Invisible before
    # 2026-07-28; this bucket is what makes an interrupted batch resumable.
    rendered = lessons / prog / "rendered"
    if rendered.is_dir():
        for f in sorted(rendered.glob("*.txt")):
            stem = f.stem
            if base_of(stem) in published:
                continue
            ws_dir = ws_by_base.get(base_of(stem))
            state = "workspace present" if ws_dir else "NO workspace"
            if ws_dir and (ws_dir / "qa" / "VERIFIED").is_file():
                state += ", verified MP4 awaiting publish"
            if stem in quarantined:
                state += f", quarantined: {quarantined[stem]}"
            stranded.append((stem, state)); totals["rendered_unpublished"] += 1
    report.append({"program": prog, "queued": queued,
                   "blocked": [{"stem": s, "reason": r} for s, r in blocked],
                   "built_unpublished": built,
                   "rendered_unpublished": [{"stem": s, "state": st} for s, st in stranded]})

# Distinct Wistia media = videos actually live, independent of folder state.
totals["published"] = len(media_ids)

if as_json:
    print(json.dumps({"priority": ordered, "totals": totals, "programs": report}, indent=2))
    sys.exit(0)

B, D, O = "\033[1m", "\033[2m", "\033[0m"
print(f"\n{B}Remaining video queue{O} {D}(priority order — drain top to bottom){O}\n")
n = 0
for r in report:
    if not (r["queued"] or r["blocked"] or r["built_unpublished"]
            or r["rendered_unpublished"]):
        continue
    print(f"{B}{r['program']}{O}")
    for s in r["queued"]:
        n += 1
        print(f"  {n:3d}. {s}")
    for s in r["built_unpublished"]:
        print(f"       {D}built, NOT published{O} — {s}   <- verify before re-running")
    for x in r["rendered_unpublished"]:
        print(f"       \033[33mSTRANDED mid-pipeline{O} — {x['stem']}  ({x['state']})")
    for b in r["blocked"]:
        print(f"       {D}blocked ({b['reason']}){O} — {b['stem']}")
    print()

t = totals
print(f"{B}{t['queued']} to build{O} · {t['built_unpublished']} built-unpublished · "
      f"{t['rendered_unpublished']} stranded · "
      f"{t['blocked']} blocked · {t['published']} already on Wistia\n")
if t["queued"]:
    print(f"{D}Resume: /render-lessons AUTO-BATCH — it starts at the top of this list.{O}\n")
PY
