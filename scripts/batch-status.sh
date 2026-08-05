#!/usr/bin/env bash
# batch-status.sh — reconstruct the pipeline from disk alone.
#
# This is the resume key for an interrupted AUTO-BATCH run. It reads only the
# folders, the ledger and the logs; nothing depends on a previous session's
# context surviving. A stem is PUBLISHED if and only if it has a Wistia URL in
# published.tsv — that URL is committed in the same pass that publishes it, so
# there is never a window where work exists but isn't recorded.
#
# Usage:  bash scripts/batch-status.sh [--json | --write [path]]
#
# --write regenerates the human-facing status document (default
# projects/video-production/PIPELINE-STATUS.md) from the same disk-truth read
# as the terminal report. It is called by the pipeline itself at every stage
# transition — build-claim.sh (a build starts), build-release.sh (a build
# finishes), batch-ship.sh (quarantine, publish) — so the doc cannot go stale
# the way the hand-maintained status.md/PIPELINE-MAP.md deleted 2026-07-27 did
# (decisions/log.md). It is a build artifact, not a place to hand-edit.
#
# THE VOCABULARY (2026-08-04). The folder name IS the stage name:
#
#   lesson-scripts/<program>/inbox/<base>.txt      RAW        captured, not refined
#   lesson-scripts/<program>/ready/<base>.txt      READY      waiting to build
#   lesson-scripts/<program>/published/<base>.txt  PUBLISHED  live on Wistia
#   renders-hyperframes/<base>/                    BUILDING -> NEEDS REVIEW -> RENDERED
#   renders-mp4/<program>/<base>_<date>.mp4        the delivered file
#
# Exception states are reported separately and never silently: NEEDS SCRIPT,
# STALLED, REJECTED, STRANDED, ORPHAN. Each one used to be invisible to at
# least one code path here, which is how a run could report "0 blocked" while a
# script carrying SCRIPT PENDING sat in the tree.
#
# Priority order is the drain order: highest-value programs ship first, so an
# interrupted run leaves the most important videos already live. This line is
# the ONE definition of priority in the repo — everything else cites it.
# Override with VIDEO_PRIORITY="slug-a slug-b ...".
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# The DATA root. Overridable so the state model can be graded against fixture
# trees instead of against whatever the live repo happens to hold today —
# render-qa/tests/test_pipeline_status.py builds one tree per state. The CODE
# root below is never overridden: a test must exercise the real stem.py.
VP="${VIDEO_VP_ROOT:-$REPO/projects/video-production}"
SRC="$REPO/projects/video-production/render-qa/src"

PRIORITY="${VIDEO_PRIORITY:-early-career-boost mid-career-momentum career-transitions entrepreneur-accelerator}"

MODE=text
OUTPATH="$VP/PIPELINE-STATUS.md"
case "${1:-}" in
  --json)  MODE=json ;;
  --write) MODE=write; [[ -n "${2:-}" ]] && OUTPATH="$2" ;;
esac

PRIORITY="$PRIORITY" LESSONS="$VP/lesson-scripts" SRC="$SRC" \
WS="$VP/renders-hyperframes" LEDGER="$VP/lesson-scripts/refinement-log.md" \
PUBTSV="$VP/lesson-scripts/published.tsv" QLOG="$VP/render-qa/quarantine.log" \
STALL_MINUTES="${VIDEO_STALL_MINUTES:-30}" \
MODE="$MODE" OUTPATH="$OUTPATH" python3 - <<'PY'
import json, os, re, sys, time
from pathlib import Path

lessons = Path(os.environ["LESSONS"])
ws_root = Path(os.environ["WS"])
ledger  = Path(os.environ["LEDGER"])
pubtsv  = Path(os.environ["PUBTSV"])
qlog    = Path(os.environ["QLOG"])
mode    = os.environ["MODE"]
outpath = Path(os.environ["OUTPATH"])
priority = os.environ["PRIORITY"].split()
try:
    STALL_SEC = float(os.environ["STALL_MINUTES"]) * 60
except ValueError:
    STALL_SEC = 30 * 60
NOW = time.time()

ledger_text = ledger.read_text(encoding="utf-8", errors="replace") if ledger.exists() else ""

# Every comparison here is on BASE (title_program). Since 2026-07-29 a working
# artifact carries no date, so base_of() is usually the identity function — but
# it stays because the MP4 still carries its render date, refinement-log.md rows
# still quote legacy dated stems, and a workspace built before the change may
# survive. stem.py owns the rule; base() strips any trailing date/clock.
sys.path.insert(0, os.environ["SRC"])
from stem import base as stem_base, StemError

def base_of(name: str) -> str:
    try:
        return stem_base(name)
    except StemError:
        return name          # undated/legacy name: compare it as-is


def ago(seconds: float) -> str:
    m = int(seconds // 60)
    if m < 1:
        return "just now"
    if m < 90:
        return f"{m} min ago"
    h = m / 60
    if h < 48:
        return f"{h:.0f} h ago"
    return f"{h / 24:.0f} days ago"


# ── the ledgers ──────────────────────────────────────────────────────────────
# Primary key: published.tsv — base, written and committed by batch-ship.sh in
# the same pass that uploads. The ledger scan below is a fallback for lessons
# published before the tsv existed (rows abbreviate the stem, so that matching
# is best-effort — the tsv is the contract).
published, media_ids, published_rows = set(), set(), []
if pubtsv.exists():
    for line in pubtsv.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) >= 4:
            published.add(cols[0])
            published_rows.append({"base": cols[0], "program": cols[1],
                                    "render_date": cols[2], "wistia_url": cols[3]})
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

# Quarantine: a row is an INCIDENT, never deleted — that file is the trail. A
# row is RESOLVED when its base later published, or when a later row in the log
# marks it resolved. Until 2026-08-04 quarantines were suppressed only by
# accident (the published branch happened to run first), so a rejected cut that
# never published could show up as an ordinary unbuilt lesson.
quarantined, resolved_rows = {}, set()
if qlog.exists():
    for line in qlog.read_text(encoding="utf-8", errors="replace").splitlines():
        cols = line.split("\t")
        if len(cols) < 4:
            continue
        when, stem, prog, reason = cols[0], cols[1], cols[2], cols[3]
        if reason.strip().lower().startswith("resolved"):
            resolved_rows.add(base_of(stem))
            continue
        quarantined[base_of(stem)] = {"when": when, "program": prog, "reason": reason}
for b in list(quarantined):
    if b in published or b in resolved_rows:
        del quarantined[b]

# ── the workspaces ───────────────────────────────────────────────────────────
# Workspaces are keyed by BASE, never joined on a path: a workspace can carry a
# legacy build date while its script carries a refine date.
SKIP_DIRS = {"node_modules", ".git", ".thumbnails", ".waveform-cache"}

def newest_mtime(d: Path) -> float:
    newest = 0.0
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for name in files:
            try:
                m = os.stat(os.path.join(root, name)).st_mtime
            except OSError:
                continue
            if m > newest:
                newest = m
    return newest or d.stat().st_mtime


def journal(ws_dir: Path):
    """The last COMPLETED step, from the workspace's own append-only journal.

    .build-log.tsv is evidence, not a status field: build-claim.sh opens it and
    each step appends one `timestamp \\t step \\t detail` row. Nothing ever
    rewrites a row, so it cannot lie the way a frontmatter status field would —
    and an interrupted build stops leaving no trace of where it got to, which
    is the whole reason this exists (2026-08-04)."""
    f = ws_dir / ".build-log.tsv"
    if not f.is_file():
        return None
    rows = [ln.split("\t") for ln in
            f.read_text(encoding="utf-8", errors="replace").splitlines()
            if ln.strip() and not ln.startswith("#")]
    if not rows:
        return None
    last = rows[-1]
    when = 0.0
    try:
        when = time.mktime(time.strptime(last[0], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    except (ValueError, IndexError):
        when = f.stat().st_mtime
    return {"step": last[1] if len(last) > 1 else "?",
            "detail": last[2] if len(last) > 2 else "",
            "when": when, "rows": len(rows)}


def ws_lane(ws_dir: Path) -> str:
    """Which authoring lane this workspace is on — detected, never assumed.

    Until 2026-08-04 every probe below assumed the TEMPLATE lane, so a freeform
    workspace (no scenes.json by design — the HTML is the authored artifact)
    reported as "build folder exists but holds no scene plan — nothing authored
    yet", with a next-action of *restart the build*. That advice collides with
    the mkdir build lock and, taken literally, discards finished narration."""
    if (ws_dir / "scenes.json").is_file():
        return "template"
    if (ws_dir / "design.md").is_file() or (ws_dir / "audio_request.json").is_file():
        return "freeform"
    return "scaffold"


def timed_html(ws_dir: Path) -> bool:
    try:
        html = (ws_dir / "index.html").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(set(re.findall(r'data-start="([^"]*)"', html)) - {"0"})


def ws_state(ws_dir):
    """(stage, label, next-action). Cheap file probes only — no browser, no gate
    run — claiming exactly what the files show and nothing more. preflight
    remains the sole authority on gate-clean; qa/PREFLIGHT-OK is that verdict
    written down so it survives the session that produced it.

    "built" was ONE word covering six situations, so the owner could not tell a
    folder holding a half-written plan from a finished MP4 waiting on an upload
    (2026-07-31). Every branch names what to DO, not which tool exited non-zero.
    """
    # RESUME, never restart. `/render-lessons BUILD` claims a workspace with
    # mkdir, so telling a human to "restart the build" against a folder that
    # already exists names a command that exits immediately — the lesson never
    # moves. Only a scaffold-only workspace is safe to delete; every later stage
    # holds narration audio or a plan that a rebuild would throw away, so those
    # reclaim the lock instead (2026-08-04).
    DISCARD = ("nothing authored yet, so nothing is lost — discard and rebuild: "
               "`rm -rf projects/video-production/renders-hyperframes/{ws} && "
               "/render-lessons BUILD {stem}`")
    # Always build-gate.sh, never a bare preflight.py: the marker it writes is
    # what carries "gate-clean" past the end of this session, so advice that runs
    # the gate WITHOUT writing it leaves the state exactly where it was.
    GATE = ("run the gate: `bash scripts/build-gate.sh {stem}` — it runs preflight "
            "and writes qa/PREFLIGHT-OK on exit 0, which is what makes this read "
            "as NEEDS REVIEW tomorrow")
    RESUME = ("reclaim the lock, then resume: `bash scripts/build-claim.sh {stem} "
              "{program} --resume` → `/render-lessons` BUILD {stem}. Do NOT delete "
              "the workspace — it holds work a rebuild would discard")
    if ws_dir is None:
        return ("scaffolded", "no build folder", "start the build: `/render-lessons` BUILD {stem}")
    if (ws_dir / "qa" / "VERIFIED").is_file():
        return ("rendered", "MP4 rendered and gate-verified — waiting only on the Wistia upload",
                "publish it: `bash scripts/batch-ship.sh {stem} {program} --publish`")
    if (ws_dir / "qa" / "PREFLIGHT-OK").is_file():
        return ("needs-review", "gate-clean and waiting on your eyes — no MP4 yet",
                "watch it, then ship: `bash scripts/preview.sh {stem}` → `ship {stem}`")

    lane = ws_lane(ws_dir)
    if lane == "scaffold":
        return ("scaffolded",
                "workspace claimed from the scaffold; no plan and no design authored yet",
                DISCARD)
    if lane == "freeform":
        # design.md -> per-beat wavs -> timing.json -> timed index.html
        if not list((ws_dir / "assets" / "voice").glob("s*.wav")):
            return ("planned", "freeform design written; narration not yet synthesized",
                    RESUME)
        if not (ws_dir / "timing.json").is_file():
            return ("untimed", "freeform narration synthesized; clip timings not yet computed",
                    RESUME)
        if not timed_html(ws_dir):
            return ("untimed", "freeform timings computed but never applied to the composition",
                    RESUME)
        return ("composed", "freeform composition timed and ready — the gate has not run yet",
                GATE)
    # template lane
    if not (ws_dir / "assets" / "voice" / "narration.wav").is_file():
        return ("planned", "scene plan written; narration voice-over not yet synthesized",
                RESUME)
    if not (ws_dir / "index.html").is_file():
        return ("uncompiled", "narration synthesized; the composition was never compiled",
                RESUME)
    if not timed_html(ws_dir):
        return ("untimed", "composition compiled, but scene timings were never applied",
                RESUME)
    return ("composed", "HyperFrames composition ready — the gate has not run yet",
            GATE)


DONE_STAGES = {"rendered", "needs-review"}

ws_by_base = {}
if ws_root.is_dir():
    for d in sorted(ws_root.iterdir()):
        if d.is_dir() and not d.name.startswith((".", "_")):
            ws_by_base[base_of(d.name)] = d

# ── blocked scripts ──────────────────────────────────────────────────────────
# Detected from content, not a hand-list, so a fixed script re-enters the queue
# automatically with no bookkeeping. Scanned in BOTH inbox/ and ready/: the
# scan used to cover the render queue only, so a raw script carrying SCRIPT
# PENDING was reported as nothing at all.
BLOCK_PATTERNS = [
    (re.compile(r'TODO:\s*needs input', re.I),          "TODO: needs input"),
    (re.compile(r'SCRIPT PENDING',      re.I),          "SCRIPT PENDING"),
]

def blocked_reason(p: Path):
    """(label, detail) — the marker AND the paragraph it sits in.

    The script always states what it needs ("the RAW names the four parts of the
    bullet formula but never defines what each one means"); echoing only the
    marker word threw that away and left the owner a status doc that said
    "needs input" without ever saying which input (2026-07-31).
    """
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for rx, label in BLOCK_PATTERNS:
        for i, line in enumerate(lines):
            if not rx.search(line):
                continue
            para = [line.strip()]
            for nxt in lines[i + 1:]:          # the marker's own paragraph
                if not nxt.strip():
                    break
                para.append(nxt.strip())
            detail = re.sub(r'^\W*(TODO:\s*needs input|SCRIPT PENDING)\W*', '',
                            " ".join(para), flags=re.I).strip()
            return (label, detail)
    return None


programs = sorted([d.name for d in lessons.iterdir() if d.is_dir()])
ordered  = [p for p in priority if p in programs] + [p for p in programs if p not in priority]

report = []
totals = {"raw": 0, "needs_script": 0, "queued": 0, "building": 0, "stalled": 0,
          "needs_review": 0, "rendered": 0, "rejected": 0, "stranded": 0,
          "published": 0, "orphan": 0}
known_bases = set()

for prog in ordered:
    pdir = lessons / prog
    raw, needs_script, queued, in_flight, stranded = [], [], [], [], []

    for stage_dir in ("inbox", "ready"):
        d = pdir / stage_dir
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.txt")):
            stem = f.stem
            known_bases.add(base_of(stem))
            if base_of(stem) in published:
                continue
            why = blocked_reason(f)
            if why:
                needs_script.append({"stem": stem, "folder": stage_dir,
                                     "marker": why[0], "detail": why[1]})
                totals["needs_script"] += 1
                continue
            if stage_dir == "inbox":
                raw.append(stem)
                totals["raw"] += 1
                continue
            # ready/: built or not?
            ws_dir = ws_by_base.get(base_of(stem))
            if ws_dir is None:
                queued.append(stem)
                totals["queued"] += 1
                continue
            stage, state, nxt = ws_state(ws_dir)
            findings, jrn = [], journal(ws_dir)
            q = quarantined.get(base_of(stem))
            if q:
                # The log records which guard said no, never what it said. Ask
                # the guard again — batch-ship.sh keeps the workspace precisely
                # so the failure is reproducible. "verify_render.py non-zero" is
                # a citation, not a reason.
                stage = "rejected"
                state = f"a release gate rejected this cut — {q['reason']}"
                reason_file = ws_dir / "qa" / "quarantine-reason.txt"
                if reason_file.is_file():
                    txt = reason_file.read_text(encoding="utf-8", errors="replace")
                    findings = [re.sub(r'^-\s*', '', ln.strip()) for ln in txt.splitlines()
                                if re.match(r'\s+-\s+\[', ln)][:4]
                    nxt = ("read the full failure in "
                           f"`renders-hyperframes/{ws_dir.name}/qa/quarantine-reason.txt`, "
                           "fix the authoring, then re-render: "
                           f"`bash scripts/batch-ship.sh {stem} {prog}`")
                else:
                    nxt = ("re-run the gate to see what it objected to: "
                           f"`python3 projects/video-production/render-qa/src/verify_render.py "
                           f"projects/video-production/renders-hyperframes/{ws_dir.name}`")
                totals["rejected"] += 1
            elif stage in DONE_STAGES:
                totals["needs_review" if stage == "needs-review" else "rendered"] += 1
            else:
                # Incomplete. STALLED is report-only and never kills anything —
                # but its next-action must RELEASE THE LOCK. "restart the build"
                # collides with the mkdir lock: the folder is already there, so
                # a fresh BUILD exits immediately and the lesson never moves.
                idle = NOW - newest_mtime(ws_dir)
                if idle > STALL_SEC:
                    # STALLED is a statement about TIME, not a different job: the
                    # action stays whatever the stage needs, because deleting a
                    # workspace that holds narration is not a resume.
                    stage = "stalled"
                    totals["stalled"] += 1
                else:
                    totals["building"] += 1
            in_flight.append({
                "stem": stem, "stage": stage, "lane": ws_lane(ws_dir),
                "workspace": ws_dir.name, "state": state, "findings": findings,
                "idle": ago(NOW - newest_mtime(ws_dir)),
                "journal": (f"left off after **{jrn['step']}**, {ago(NOW - jrn['when'])}"
                            if jrn else None),
                "next": nxt.replace("{stem}", stem).replace("{program}", prog)
                           .replace("{ws}", ws_dir.name)})

    # published/ without a published.tsv row = STRANDED mid-pipeline (upload or
    # commit did not complete). This bucket is what makes an interrupted batch
    # resumable rather than merely restartable.
    pub = pdir / "published"
    if pub.is_dir():
        for f in sorted(pub.glob("*.txt")):
            stem = f.stem
            known_bases.add(base_of(stem))
            if base_of(stem) in published:
                continue
            ws_dir = ws_by_base.get(base_of(stem))
            verified = bool(ws_dir and (ws_dir / "qa" / "VERIFIED").is_file())
            state = ("build folder present" if ws_dir else
                     "NO build folder — the MP4 cannot be re-made from here")
            if verified:
                state += ", MP4 verified and awaiting publish"
            if base_of(stem) in quarantined:
                state += f", rejected by a gate ({quarantined[base_of(stem)]['reason']})"
            nxt = (f"finish the publish: `bash scripts/batch-ship.sh {stem} {prog} --publish`"
                   if verified else
                   f"re-run the tail: `bash scripts/batch-ship.sh {stem} {prog}`")
            stranded.append({"stem": stem, "state": state, "next": nxt})
            totals["stranded"] += 1

    report.append({"program": prog, "raw": raw, "needs_script": needs_script,
                   "queued": queued, "in_flight": in_flight, "stranded": stranded})

# ORPHAN — a workspace whose base matches no script in any program. Before
# 2026-08-04 these were invisible to every code path here: the scan only ever
# looked up workspaces BY script, so a workspace with no script was never
# looked up at all.
orphans = []
for base, d in sorted(ws_by_base.items()):
    if base in known_bases or base in published:
        continue
    stage, state, _ = ws_state(d)
    orphans.append({"workspace": d.name, "stage": stage, "state": state,
                    "idle": ago(NOW - newest_mtime(d))})
    totals["orphan"] += 1

# Distinct Wistia media = videos actually live, independent of folder state.
totals["published"] = len(media_ids)

if mode == "json":
    print(json.dumps({"priority": ordered, "totals": totals, "programs": report,
                       "orphans": orphans, "published": published_rows}, indent=2))
    sys.exit(0)

# ─────────────────────────────────────────────────────────────────────────────
if mode == "write":
    lines = []
    a = lines.append
    a("# Video Production — Pipeline Status")
    a("")
    a("**Generated file — do not hand-edit.** Overwritten by `scripts/batch-status.sh "
      "--write` at every build/quarantine/publish step; a hand edit here is lost on the "
      "next run and this file cannot go stale the way the old `status.md` did (deleted "
      "2026-07-27, see `decisions/log.md`) because it is never the thing anyone edits — "
      "only ever the thing that gets regenerated from the folders + `published.tsv`.")
    a("")
    a("## Where everything stands")
    a("")
    a(f"- **{totals['published']}** — **live on Wistia.** Done; links in the "
      "*Delivered* table below.")
    a(f"- **{totals['queued']}** — **ready to build.** Script approved; nothing made yet.")
    a(f"- **{totals['building']}** — **building now.** A workspace exists and is "
      "moving; each names the step it last completed.")
    a(f"- **{totals['needs_review']}** — **waiting on your eyes.** Gate-clean, no MP4 "
      "yet — this is the pilot gate.")
    a(f"- **{totals['rendered']}** — **rendered, not yet published.** The MP4 exists "
      "and passed every gate; only the Wistia upload is left.")
    a(f"- **{totals['raw']}** — **raw, not yet refined.** Sitting in `inbox/`, waiting "
      "on `/refine-scripts`.")
    a(f"- **{totals['needs_script']}** — **NEEDS SCRIPT.** The script itself is "
      "incomplete and only you can finish it; the exact question is under each program.")
    a(f"- **{totals['stalled']}** — **STALLED.** A build folder that stopped moving; "
      "the lock has to be released before it can be rebuilt.")
    a(f"- **{totals['rejected']}** — **REJECTED.** A finished attempt a release check "
      "refused; needs a fix and a re-render.")
    a(f"- **{totals['stranded']}** — **STRANDED.** Filed as published but never "
      "recorded as published; an interrupted run left it here.")
    a(f"- **{totals['orphan']}** — **ORPHAN.** A build folder matching no script in "
      "any program.")
    a("")
    a("### What the stages mean")
    a("")
    a("The pipeline has no database — the folders on disk *are* the state, and since "
      "2026-08-04 **the folder name is the stage name**. Every lesson sits in exactly "
      "one row.")
    a("")
    a("| Stage | Where it lives on disk | What it needs next |")
    a("|---|---|---|")
    a("| **RAW** | `lesson-scripts/<program>/inbox/<base>.txt` | refinement — "
      "`/refine-scripts` |")
    a("| **READY** | `lesson-scripts/<program>/ready/<base>.txt`, no build folder | "
      "an agent to author it — `/render-lessons` |")
    a("| **BUILDING** | `renders-hyperframes/<base>/`, incomplete | the build to "
      "continue; `.build-log.tsv` says which step it last finished |")
    a("| **NEEDS REVIEW** | the same folder plus `qa/PREFLIGHT-OK` | you — watch it, "
      "then `ship <stem>` |")
    a("| **RENDERED** | the same folder plus `qa/VERIFIED` and an `.mp4` | the Wistia "
      "upload and its ledger row |")
    a("| **PUBLISHED** | `lesson-scripts/<program>/published/<base>.txt` + a row in "
      "`lesson-scripts/published.tsv` | nothing |")
    a("| *NEEDS SCRIPT* | a `TODO: needs input` / `SCRIPT PENDING` marker inside the "
      "script, in `inbox/` or `ready/` | you — the source material is missing something |")
    a("| *STALLED* | a build folder with nothing written for "
      f"{int(STALL_SEC // 60)}+ min | the lock released, then a rebuild |")
    a("| *REJECTED* | a build folder and an unresolved row in "
      "`render-qa/quarantine.log` | a human fix to the authoring, then a re-render |")
    a("| *STRANDED* | a script in `published/` with no `published.tsv` row | the "
      "publish step re-run; nothing is lost |")
    a("| *ORPHAN* | a build folder whose base matches no script anywhere | naming — "
      "it is either reference material or garbage |")
    a("")
    if published_rows:
        a("## Delivered")
        a("")
        a("Every lesson that is live, and where to watch it. Generated from "
          "`lesson-scripts/published.tsv`, which `batch-ship.sh` writes in the same "
          "commit as the upload.")
        a("")
        a("| Lesson | Program | Rendered | Watch | Local MP4 |")
        a("|---|---|---|---|---|")
        for row in sorted(published_rows, key=lambda r: r["render_date"], reverse=True):
            mp4 = (f"`renders-mp4/{row['program']}/{row['base']}_"
                   f"{row['render_date']}.mp4`")
            a(f"| {row['base']} | {row['program']} | {row['render_date']} | "
              f"[{row['wistia_url'].rsplit('/', 1)[-1]}]({row['wistia_url']}) | {mp4} |")
        a("")
    attention = [(r["program"], x) for r in report for x in r["in_flight"]
                 if x["stage"] in ("rejected", "stalled")]
    if attention or orphans:
        a("## Needs a human right now")
        a("")
        for prog, x in attention:
            a(f"- **{x['stem']}** ({prog}) — {x['stage'].upper()}: {x['state']}")
            for fdg in x["findings"]:
                a(f"  - {fdg}")
            if x["journal"]:
                a(f"  - {x['journal']}")
            a(f"  - **To clear it:** {x['next']}")
        for o in orphans:
            a(f"- **{o['workspace']}** — ORPHAN: a build folder matching no script in "
              f"any program ({o['state']}; last touched {o['idle']})")
            a("  - **To clear it:** name what it is. Reference material belongs in "
              "`renders-hyperframes/_reference/` (underscore folders are skipped by "
              "this scan); anything else can be deleted.")
        a("")
    n = 0
    for r in report:
        if not (r["raw"] or r["needs_script"] or r["queued"] or r["in_flight"]
                or r["stranded"]):
            continue
        a(f"## {r['program']}")
        a("")
        if r["queued"]:
            a("**READY — queued to build:**")
            a("")
            for s in r["queued"]:
                n += 1
                a(f"{n}. {s}")
            a("")
        for stages, heading, blurb in (
            (("rendered",), "RENDERED — MP4 verified, waiting on publish",
             "The video file exists and passed every gate. Nothing left but the upload."),
            (("needs-review",), "NEEDS REVIEW — gate-clean, waiting on your eyes",
             "The pilot gate. Watch it, then reply `ship <stem>`."),
            (("scaffolded", "planned", "uncompiled", "untimed", "composed"),
             "BUILDING — in flight, no MP4 yet",
             "A workspace exists and is part-way through. Each names the last step it "
             "actually completed, so a resuming session picks up rather than restarts."),
            (("stalled",), "STALLED — the build folder stopped moving",
             "Report-only: nothing here is killed automatically. The folder is still "
             "the `mkdir` lock, so it has to be released before a rebuild can claim it."),
            (("rejected",), "REJECTED — a gate refused this cut",
             "Built and rendered, then refused by a release check. It will not publish "
             "until a human fixes the cause and re-renders."),
        ):
            group = [x for x in r["in_flight"] if x["stage"] in stages]
            if not group:
                continue
            a(f"**{heading}:**")
            a("")
            a(f"*{blurb}*")
            a("")
            for x in group:
                a(f"- {x['stem']}")
                a(f"  - state: {x['state']}")
                if x["journal"]:
                    a(f"  - {x['journal']}")
                else:
                    a(f"  - last written to: {x['idle']} (no `.build-log.tsv` — this "
                      "workspace predates the build journal)")
                for fdg in x["findings"]:
                    a(f"  - gate said: {fdg}")
                a(f"  - next: {x['next']}")
            a("")
        if r["stranded"]:
            a("**STRANDED mid-pipeline:**")
            a("")
            a("*Filed in `published/` but never recorded in `published.tsv` — a run was "
              "interrupted between the two. Nothing is lost; the publish step just has "
              "to finish.*")
            a("")
            for x in r["stranded"]:
                a(f"- {x['stem']}")
                a(f"  - state: {x['state']}")
                a(f"  - next: {x['next']}")
            a("")
        if r["needs_script"]:
            a("**NEEDS SCRIPT — only you can finish these:**")
            a("")
            a("*The script carries an unanswered question. Answer it in the script and "
              "delete the marker line; the lesson rejoins the queue on the next status "
              "run, with no other bookkeeping.*")
            a("")
            for b in r["needs_script"]:
                a(f"- {b['stem']}")
                a(f"  - marker: `{b['marker']}` in "
                  f"`lesson-scripts/{r['program']}/{b['folder']}/{b['stem']}.txt`")
                a(f"  - **what's needed:** {b['detail'] or '(the marker gives no detail — open the script)'}")
            a("")
        if r["raw"]:
            a("**RAW — waiting on refinement:**")
            a("")
            for s in r["raw"]:
                a(f"- {s} — `/refine-scripts`")
            a("")
    a("---")
    a("Resume: `/render-lessons` AUTO-BATCH starts at the top of the READY list above. "
      "Full state model: `bash scripts/batch-status.sh` (terminal) or "
      "`bash scripts/batch-status.sh --json` (machine).")
    a("")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {outpath}")
    sys.exit(0)

# ─────────────────────────────────────────────────────────────────────────────
B, D, O = "\033[1m", "\033[2m", "\033[0m"
RED, YEL, GRN, CYN = "\033[31m", "\033[33m", "\033[32m", "\033[36m"
print(f"\n{B}Pipeline{O} {D}(priority order — drain top to bottom){O}\n")
n = 0
for r in report:
    if not (r["raw"] or r["needs_script"] or r["queued"] or r["in_flight"]
            or r["stranded"]):
        continue
    print(f"{B}{r['program']}{O}")
    for s in r["queued"]:
        n += 1
        print(f"  {n:3d}. READY  {s}")
    for x in r["in_flight"]:
        tag = {"rendered":     f"{GRN}RENDERED — ready to publish{O}",
               "needs-review": f"{CYN}NEEDS REVIEW — your eyes{O}",
               "rejected":     f"{RED}REJECTED{O}",
               "stalled":      f"{YEL}STALLED{O}"}.get(x["stage"],
                              f"{D}BUILDING ({x['stage']}){O}")
        print(f"       {tag} — {x['stem']}  ({x['state']})")
        if x["journal"]:
            print(f"         {D}{x['journal'].replace('**', '')}{O}")
        for fdg in x["findings"]:
            print(f"         {D}{fdg}{O}")
        print(f"         {D}next: {x['next']}{O}")
    for x in r["stranded"]:
        print(f"       {YEL}STRANDED mid-pipeline{O} — {x['stem']}  ({x['state']})")
        print(f"         {D}next: {x['next']}{O}")
    for b in r["needs_script"]:
        print(f"       {YEL}NEEDS SCRIPT{O} ({b['marker']} in {b['folder']}/) — {b['stem']}")
        if b["detail"]:
            print(f"         {D}needs: {b['detail']}{O}")
    for s in r["raw"]:
        print(f"       {D}RAW — awaiting /refine-scripts{O} — {s}")
    print()

if orphans:
    print(f"{B}unattached build folders{O}")
    for o in orphans:
        print(f"       {YEL}ORPHAN{O} — {o['workspace']}  ({o['state']}; {o['idle']})")
        print(f"         {D}next: name it — move reference material to "
              f"renders-hyperframes/_reference/, delete the rest{O}")
    print()

t = totals
print(f"{B}{t['published']} live{O} · {t['queued']} ready · {t['building']} building · "
      f"{t['needs_review']} needs review · {t['rendered']} rendered · "
      f"{t['raw']} raw · {t['needs_script']} NEEDS SCRIPT · {t['stalled']} STALLED · "
      f"{t['rejected']} REJECTED · {t['stranded']} STRANDED · {t['orphan']} ORPHAN\n")
if t["queued"]:
    print(f"{D}Resume: /render-lessons AUTO-BATCH — it starts at the top of this list.{O}\n")
PY
