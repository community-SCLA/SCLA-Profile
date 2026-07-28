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

PRIORITY="$PRIORITY" LESSONS="$VP/lesson-scripts" \
WS="$VP/renders-hyperframes" LEDGER="$VP/lesson-scripts/refinement-log.md" \
JSON="$JSON" python3 - <<'PY'
import json, os, re, sys
from pathlib import Path

lessons = Path(os.environ["LESSONS"])
ws_root = Path(os.environ["WS"])
ledger  = Path(os.environ["LEDGER"])
as_json = os.environ["JSON"] == "1"
priority = os.environ["PRIORITY"].split()

ledger_text = ledger.read_text(encoding="utf-8", errors="replace") if ledger.exists() else ""

# A stem is published iff its name appears on a ledger line that also carries a
# Wistia media URL. Checked per line so one stem's URL can't vouch for another.
# A row names the script stem AND the filed MP4 (same base, render date swapped),
# so collect both spellings for exclusion but count distinct media IDs for the
# published tally — otherwise every video counts twice.
published, media_ids = set(), set()
for line in ledger_text.splitlines():
    ids = re.findall(r'wistia\.com/medias/(\w+)', line)
    if not ids:
        continue
    media_ids.update(ids)
    for m in re.finditer(r'[A-Za-z0-9][\w.-]*_\d{4}-\d{2}-\d{2}', line):
        published.add(m.group(0))

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

report, totals = [], {"queued": 0, "blocked": 0, "built_unpublished": 0, "published": 0}

for prog in ordered:
    refined = lessons / prog / "refined"
    if not refined.is_dir():
        continue
    queued, blocked, built = [], [], []
    for f in sorted(refined.glob("*.txt")):          # non-recursive: refined/avatar/ is the HeyGen queue
        stem = f.stem
        if stem in published:
            totals["published"] += 1
            continue
        why = blocked_reason(f)
        if why:
            blocked.append((stem, why)); totals["blocked"] += 1
        elif (ws_root / stem).is_dir():
            # workspace exists but no Wistia URL -> built, unpublished (quarantine or in flight)
            built.append(stem); totals["built_unpublished"] += 1
        else:
            queued.append(stem); totals["queued"] += 1
    report.append({"program": prog, "queued": queued,
                   "blocked": [{"stem": s, "reason": r} for s, r in blocked],
                   "built_unpublished": built})

# Distinct Wistia media = videos actually live, independent of folder state.
totals["published"] = len(media_ids)

if as_json:
    print(json.dumps({"priority": ordered, "totals": totals, "programs": report}, indent=2))
    sys.exit(0)

B, D, O = "\033[1m", "\033[2m", "\033[0m"
print(f"\n{B}Remaining video queue{O} {D}(priority order — drain top to bottom){O}\n")
n = 0
for r in report:
    if not (r["queued"] or r["blocked"] or r["built_unpublished"]):
        continue
    print(f"{B}{r['program']}{O}")
    for s in r["queued"]:
        n += 1
        print(f"  {n:3d}. {s}")
    for s in r["built_unpublished"]:
        print(f"       {D}built, NOT published{O} — {s}   <- verify before re-running")
    for b in r["blocked"]:
        print(f"       {D}blocked ({b['reason']}){O} — {b['stem']}")
    print()

t = totals
print(f"{B}{t['queued']} to build{O} · {t['built_unpublished']} built-unpublished · "
      f"{t['blocked']} blocked · {t['published']} already on Wistia\n")
if t["queued"]:
    print(f"{D}Resume: /render-lessons AUTO-BATCH — it starts at the top of this list.{O}\n")
PY
