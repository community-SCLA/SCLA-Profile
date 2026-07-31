#!/usr/bin/env bash
# batch-status.sh — reconstruct the remaining video queue from disk alone.
#
# This is the resume key for an interrupted AUTO-BATCH run. It reads only the
# folders and the ledger; nothing depends on a previous session's context
# surviving. A stem is DONE if and only if it has a Wistia URL in
# refinement-log.md — that URL is committed in the same pass that publishes it,
# so there is never a window where work exists but isn't recorded.
#
# Usage:  bash scripts/batch-status.sh [--json | --write [path]]
#
# --write regenerates the human-facing status document (default
# projects/video-production/PIPELINE-STATUS.md) from the same disk-truth read
# as the terminal report, and is meant to be called by the pipeline itself
# (batch-ship.sh at quarantine/publish, refine-scripts book-keeping) so the
# doc updates itself at every stage transition instead of going stale like the
# hand-maintained status.md/PIPELINE-MAP.md deleted 2026-07-27
# (decisions/log.md). It is a build artifact, not a place to hand-edit.
#
# Priority order is the drain order: highest-value programs ship first, so an
# interrupted run leaves the most important videos already live. Override with
# VIDEO_PRIORITY="slug-a slug-b ...".
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"

PRIORITY="${VIDEO_PRIORITY:-early-career-boost mid-career-momentum career-transitions entrepreneur-accelerator}"

MODE=text
OUTPATH="$VP/PIPELINE-STATUS.md"
case "${1:-}" in
  --json)  MODE=json ;;
  --write) MODE=write; [[ -n "${2:-}" ]] && OUTPATH="$2" ;;
esac

PRIORITY="$PRIORITY" LESSONS="$VP/lesson-scripts" VP="$VP" \
WS="$VP/renders-hyperframes" LEDGER="$VP/lesson-scripts/refinement-log.md" \
PUBTSV="$VP/lesson-scripts/published.tsv" QLOG="$VP/render-qa/quarantine.log" \
MODE="$MODE" OUTPATH="$OUTPATH" python3 - <<'PY'
import json, os, re, sys
from pathlib import Path

lessons = Path(os.environ["LESSONS"])
ws_root = Path(os.environ["WS"])
ledger  = Path(os.environ["LEDGER"])
pubtsv  = Path(os.environ["PUBTSV"])
qlog    = Path(os.environ["QLOG"])
mode    = os.environ["MODE"]
outpath = Path(os.environ["OUTPATH"])
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

report, totals = [], {"queued": 0, "blocked": 0, "built_unpublished": 0,
                      "composition_only": 0, "mp4_awaiting_publish": 0,
                      "quarantined": 0, "rendered_unpublished": 0, "published": 0}

for prog in ordered:
    refined = lessons / prog / "refined"
    if not refined.is_dir():
        continue
    queued, blocked, built, stranded = [], [], [], []
    # A workspace FOLDER only proves a build was started. Until 2026-07-29 this
    # tool called any existing workspace "built", which read as "finished, just
    # not uploaded" — so a resuming session faced a republish-or-rebuild call
    # with no evidence either way, and rebuilding discards valid narration audio.
    # These probes are cheap (no browser, no gate run) and claim only what the
    # files on disk actually show; preflight remains the sole authority on
    # gate-clean. Found when 12 of 13 "built" lessons turned out to have never
    # had compile_timeline.py --apply run against them.
    #
    # Returns (stage, label, next-action). "built" was ONE word covering six
    # different situations, so the owner could not tell a folder holding a
    # half-written plan from a finished MP4 waiting on an upload, and the label
    # named the tool that failed rather than what to do about it
    # ("verify_render.py non-zero" means nothing to a human) — 2026-07-31.
    # The two questions this has to answer without a follow-up: which of these
    # are compositions still waiting to become MP4s, and which are MP4s already
    # made and waiting to be published.
    def ws_state(ws_dir):
        if ws_dir is None or not (ws_dir / "scenes.json").is_file():
            return ("no-plan", "build folder exists but holds no scene plan — nothing authored yet",
                    "restart the build: `/render-lessons` BUILD {stem}")
        if not (ws_dir / "assets" / "voice" / "narration.wav").is_file():
            return ("planned", "scene plan written; narration voice-over not yet synthesized",
                    "resume the build: `/render-lessons` BUILD {stem}")
        try:
            html = (ws_dir / "index.html").read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ("uncompiled", "narration synthesized; the composition was never compiled",
                    "resume the build: `/render-lessons` BUILD {stem}")
        if set(re.findall(r'data-start="([^"]*)"', html)) <= {"0"}:
            return ("untimed", "composition compiled, but scene timings were never applied",
                    "resume the build: `/render-lessons` BUILD {stem}")
        if (ws_dir / "qa" / "VERIFIED").is_file():
            return ("verified", "MP4 rendered and gate-verified — waiting only on the Wistia upload",
                    "publish it: `bash scripts/batch-ship.sh {stem} {program} --publish`")
        return ("composition", "HyperFrames composition ready to render; no MP4 exists yet",
                "render + verify it: `bash scripts/batch-ship.sh {stem} {program}`")
    for f in sorted(refined.glob("*.txt")):          # non-recursive: refined/avatar/ is the HeyGen queue
        stem = f.stem
        if base_of(stem) in published:
            totals["published"] += 1
            continue
        why = blocked_reason(f)
        if why:
            blocked.append((stem, why[0], why[1])); totals["blocked"] += 1
        elif base_of(stem) in ws_by_base:
            # workspace exists but no Wistia URL -> unpublished; say WHICH stage it reached.
            # Most quarantines fire while the script is still HERE (refined/, not
            # rendered/) — batch-ship.sh only moves it to rendered/ at publish — so a
            # quarantine.log hit must be surfaced on this branch too, or "stuck" never
            # shows a reason at all. quarantine.log keys on the STEM at quarantine time,
            # which for a current-format (undated) script equals its own base.
            ws_dir = ws_by_base.get(base_of(stem))
            stage, state, nxt = ws_state(ws_dir)
            q = quarantined.get(stem) or quarantined.get(base_of(stem))
            if q:
                # The log records which guard said no, never what it said. Ask the
                # guard again — batch-ship.sh keeps the workspace precisely so the
                # failure is reproducible — and point at the transcript if one was
                # captured. "verify_render.py non-zero" is a citation, not a reason.
                stage = "quarantined"
                state = f"a release gate rejected this cut ({q})"
                reason_file = ws_dir / "qa" / "quarantine-reason.txt" if ws_dir else None
                if reason_file is not None and reason_file.is_file():
                    nxt = ("read the failure in "
                           f"`renders-hyperframes/{ws_dir.name}/qa/quarantine-reason.txt`, "
                           "fix the authoring, then re-render: "
                           f"`bash scripts/batch-ship.sh {stem} {prog}`")
                else:
                    nxt = ("re-run the gate to see what it objected to: "
                           f"`python3 projects/video-production/render-qa/src/verify_render.py "
                           f"projects/video-production/renders-hyperframes/{ws_dir.name if ws_dir else stem}`")
            built.append((stem, stage, state,
                          nxt.replace("{stem}", stem).replace("{program}", prog)))
            totals["built_unpublished"] += 1
            totals[{"verified": "mp4_awaiting_publish",
                    "quarantined": "quarantined"}.get(stage, "composition_only")] += 1
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
            state = "build folder present" if ws_dir else "NO build folder — the MP4 cannot be re-made from here"
            if ws_dir and (ws_dir / "qa" / "VERIFIED").is_file():
                state += ", MP4 verified and awaiting publish"
            if stem in quarantined:
                state += f", rejected by a gate ({quarantined[stem]})"
            nxt = (f"finish the publish: `bash scripts/batch-ship.sh {stem} {prog} --publish`"
                   if ws_dir and (ws_dir / "qa" / "VERIFIED").is_file() else
                   f"re-run the tail: `bash scripts/batch-ship.sh {stem} {prog}`")
            stranded.append((stem, state, nxt)); totals["rendered_unpublished"] += 1
    report.append({"program": prog, "queued": queued,
                   "blocked": [{"stem": s, "reason": r, "detail": d} for s, r, d in blocked],
                   "built_unpublished": [{"stem": s, "stage": g, "state": st, "next": nx}
                                          for s, g, st, nx in built],
                   "rendered_unpublished": [{"stem": s, "state": st, "next": nx}
                                             for s, st, nx in stranded]})

# Distinct Wistia media = videos actually live, independent of folder state.
totals["published"] = len(media_ids)

if mode == "json":
    print(json.dumps({"priority": ordered, "totals": totals, "programs": report,
                       "published": published_rows}, indent=2))
    sys.exit(0)

if mode == "write":
    stuck = [(r["program"], x) for r in report
             for x in r["built_unpublished"] if x["stage"] == "quarantined"]
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
    a(f"- **{totals['queued']}** — **queued to build.** Script approved; nothing made yet.")
    a(f"- **{totals['composition_only']}** — **built as compositions, no MP4 yet.** "
      "The animated lesson exists as HyperFrames HTML + narration audio; it still has to "
      "be rendered to video.")
    a(f"- **{totals['mp4_awaiting_publish']}** — **MP4 rendered and verified, not yet "
      "published.** The video file exists and passed the gates; only the Wistia upload is left.")
    a(f"- **{totals['quarantined']}** — **rejected by a gate.** A finished attempt a "
      "release check refused; needs a fix and a re-render.")
    a(f"- **{totals['rendered_unpublished']}** — **stranded mid-pipeline.** Filed as "
      "rendered but never recorded as published; an interrupted run left it here.")
    a(f"- **{totals['blocked']}** — **blocked, needs owner input.** The script itself is "
      "incomplete; see the exact question under each program below.")
    a(f"- **{totals['published']}** — **live on Wistia.** Done.")
    a("")
    a("### What the stages mean")
    a("")
    a("The pipeline has no database — the folders on disk *are* the state, and this table "
      "says which folder means what. Every lesson sits in exactly one row.")
    a("")
    a("| Stage | What exists on disk | What it needs next |")
    a("|---|---|---|")
    a("| **Queued to build** | a refined script in `lesson-scripts/<program>/refined/` "
      "and no build folder | an agent to author it — `/render-lessons` |")
    a("| **Built — composition, no MP4** | `renders-hyperframes/<lesson>/` with a scene "
      "plan, narration `.wav` and a timed `index.html` | render + verify — this is what "
      "turns it into an MP4 (~15-20 min each) |")
    a("| **MP4 awaiting publish** | the same folder, plus a `qa/VERIFIED` marker and an "
      "`.mp4` under `renders/` | the Wistia upload and its ledger row |")
    a("| **Quarantined** | a build folder and a row in `render-qa/quarantine.log` | a "
      "human fix to the authoring, then a re-render — it will never publish itself |")
    a("| **Stranded** | a script in `rendered/` with no row in `published.tsv` | the "
      "publish step re-run; nothing is lost |")
    a("| **Blocked** | a `TODO: needs input` marker inside the refined script | you — the "
      "source material is missing something the lesson needs |")
    a("| **Published** | a row in `lesson-scripts/published.tsv` with a Wistia URL | "
      "nothing |")
    a("")
    a("Partly-authored build folders (plan written but no narration yet, and so on) are "
      "counted under *built as compositions* and name their own half-finished stage in the "
      "per-program list.")
    a("")
    if stuck:
        a("## Stuck right now")
        a("")
        for prog, x in stuck:
            a(f"- **{x['stem']}** ({prog}) — {x['state']}")
            a(f"  - **To clear it:** {x['next']}")
        a("")
    if published_rows:
        a("## Published — live on Wistia")
        a("")
        a("| Lesson | Program | Render date | Wistia URL |")
        a("|---|---|---|---|")
        for row in published_rows:
            a(f"| {row['base']} | {row['program']} | {row['render_date']} | {row['wistia_url']} |")
        a("")
    n = 0
    for r in report:
        if not (r["queued"] or r["blocked"] or r["built_unpublished"]
                or r["rendered_unpublished"]):
            continue
        a(f"## {r['program']}")
        a("")
        if r["queued"]:
            a("**Queued to build:**")
            a("")
            for s in r["queued"]:
                n += 1
                a(f"{n}. {s}")
            a("")
        # One heading per real situation. A single "Built, unpublished" list put a
        # finished MP4 and a folder with a half-written plan on adjacent lines.
        for stages, heading, blurb in (
            (("verified",), "Rendered — MP4 verified, waiting on publish",
             "The video file exists and passed every gate. Nothing left but the upload."),
            (("composition", "no-plan", "planned", "uncompiled", "untimed"),
             "Built — composition only, no MP4 yet",
             "Authored as HyperFrames HTML with narration audio. Each still has to be "
             "rendered and verified before it can be published."),
            (("quarantined",), "Quarantined — a gate rejected this cut",
             "Built and rendered, then refused by a release check. It will not publish "
             "until a human fixes the cause and re-renders."),
        ):
            group = [x for x in r["built_unpublished"] if x["stage"] in stages]
            if not group:
                continue
            a(f"**{heading}:**")
            a("")
            a(f"*{blurb}*")
            a("")
            for x in group:
                a(f"- {x['stem']}")
                a(f"  - state: {x['state']}")
                a(f"  - next: {x['next']}")
            a("")
        if r["rendered_unpublished"]:
            a("**Stranded mid-pipeline:**")
            a("")
            a("*Filed as rendered but never recorded as published — a run was interrupted "
              "between the two. Nothing is lost; the publish step just has to finish.*")
            a("")
            for x in r["rendered_unpublished"]:
                a(f"- {x['stem']}")
                a(f"  - state: {x['state']}")
                a(f"  - next: {x['next']}")
            a("")
        if r["blocked"]:
            a("**Blocked — needs owner input:**")
            a("")
            a("*The refined script carries an unanswered question. Answer it in the script "
              "and delete the marker line; the lesson rejoins the build queue on the next "
              "status run, with no other bookkeeping.*")
            a("")
            for b in r["blocked"]:
                a(f"- {b['stem']}")
                a(f"  - marker: `{b['reason']}` in "
                  f"`lesson-scripts/{r['program']}/refined/{b['stem']}.txt`")
                a(f"  - **what's needed:** {b['detail'] or '(the marker gives no detail — open the script)'}")
            a("")
    a("---")
    a("Resume: `/render-lessons` AUTO-BATCH starts at the top of the queued list above. "
      "Full state model: `bash scripts/batch-status.sh` (terminal) or "
      "`bash scripts/batch-status.sh --json` (machine).")
    a("")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {outpath}")
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
    for x in r["built_unpublished"]:
        tag = {"verified": "\033[32mMP4 ready to publish" + O,
               "quarantined": "\033[31mQUARANTINED" + O}.get(x["stage"],
                              f"{D}composition, no MP4 yet{O}")
        print(f"       {tag} — {x['stem']}  ({x['state']})")
        print(f"         {D}next: {x['next']}{O}")
    for x in r["rendered_unpublished"]:
        print(f"       \033[33mSTRANDED mid-pipeline{O} — {x['stem']}  ({x['state']})")
        print(f"         {D}next: {x['next']}{O}")
    for b in r["blocked"]:
        print(f"       {D}blocked ({b['reason']}){O} — {b['stem']}")
        if b["detail"]:
            print(f"         {D}needs: {b['detail']}{O}")
    print()

t = totals
print(f"{B}{t['queued']} to build{O} · {t['composition_only']} composition-only · "
      f"{t['mp4_awaiting_publish']} MP4 ready to publish · {t['quarantined']} quarantined · "
      f"{t['rendered_unpublished']} stranded · "
      f"{t['blocked']} blocked · {t['published']} already on Wistia\n")
if t["queued"]:
    print(f"{D}Resume: /render-lessons AUTO-BATCH — it starts at the top of this list.{O}\n")
PY
