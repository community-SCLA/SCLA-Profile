#!/usr/bin/env python3
"""Control-v3 visual approval must be independent and evidence-backed."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))
from visual_review_receipt import validate_visual_review  # noqa: E402
from gate_contract import gate_contract_revision  # noqa: E402
from workspace_revision import workspace_revision  # noqa: E402

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label} {detail}")


build_gate = (HERE.parents[3] / "scripts" / "build-gate.sh").read_text()
snapshot_call = build_gate.find('snapshot . --at "$SNAP_TIMES"')
preflight_call = build_gate.find('python3 "$PREFLIGHT" "$WS"')
check("the authoritative gate refreshes per-beat frames before preflight",
      snapshot_call >= 0 and preflight_call > snapshot_call,
      f"snapshot={snapshot_call} preflight={preflight_call}")


tmp = Path(tempfile.mkdtemp(prefix="scla-review-evidence-"))
try:
    vp = tmp / "video-production"
    ws = vp / "renders-hyperframes" / "lesson_prog"
    (ws / "qa").mkdir(parents=True)
    (ws / "snapshots").mkdir()
    (ws / "concepts").mkdir()
    (vp / "lesson-scripts" / "prog" / "ready").mkdir(parents=True)
    (vp / "lesson-scripts" / "prog" / "ready" / "lesson_prog.txt").write_text("Lesson.")
    (ws / "index.html").write_text('<main data-duration="1"></main>')
    (ws / "concepts" / "CONCEPT-BOARD.json").write_text(
        json.dumps({"authored_by": "builder-agent"}))
    for name in ("one.png", "two.png", "three.png", "weak.png"):
        (ws / "snapshots" / name).write_bytes(("visible-" + name).encode())
    revision = workspace_revision(ws)
    (ws / "qa" / "PREFLIGHT-OK").write_text(json.dumps({
        "source_revision": revision,
        "gate_revision": gate_contract_revision(),
    }))
    run_file = vp / "renders-hyperframes" / "_run" / "run.json"
    run_file.parent.mkdir()
    run_file.write_text(json.dumps({
        "version": 4, "mode": "produce",
        "scope": {"kind": "stem", "value": "lesson_prog"},
        "items": [{"stem": "lesson_prog", "program": "prog"}]
    }))
    env = dict(os.environ, VIDEO_VP_ROOT=str(vp), VIDEO_RUN_STATE=str(run_file),
               VIDEO_RUN_STATE_LOCK=str(run_file) + ".lock")
    base = [sys.executable, str(SRC / "run_state.py"), "record-visual-review",
            "lesson_prog", "--blocking-defect", "PASS", "--taste", "ALIVE",
            "--recommendation", "PROCEED"]
    missing = subprocess.run(base, env=env, capture_output=True, text=True)
    check("every SCLA build refuses label-only approval",
          missing.returncode != 0 and
          "reviewer is missing" in missing.stderr, missing.stderr)
    same = subprocess.run(base + ["--reviewer", "builder-agent"], env=env,
                          capture_output=True, text=True)
    check("concept author cannot self-approve", same.returncode != 0 and
          "reviewer is the concept author" in same.stderr, same.stderr)
    (ws / "concepts" / "CONCEPT-BOARD.json").write_text(json.dumps({}))
    (ws / "qa" / "PREFLIGHT-OK").write_text(json.dumps({
        "source_revision": workspace_revision(ws),
        "gate_revision": gate_contract_revision(),
    }))
    missing_author = subprocess.run(
        base + ["--reviewer", "review-agent"], env=env,
        capture_output=True, text=True)
    check("review cannot proceed when independence is unverifiable",
          missing_author.returncode != 0 and
          "concept author is missing" in missing_author.stderr,
          missing_author.stderr)
    (ws / "concepts" / "CONCEPT-BOARD.json").write_text(
        json.dumps({"authored_by": "builder-agent"}))
    (ws / "qa" / "PREFLIGHT-OK").write_text(json.dumps({
        "source_revision": workspace_revision(ws),
        "gate_revision": gate_contract_revision(),
    }))
    complete = base + ["--reviewer", "review-agent", "--layout-families", "3"]
    for name in ("one.png", "two.png", "three.png"):
        complete += ["--evidence-frame", f"snapshots/{name}"]
    complete += ["--weakest-frame", "snapshots/weak.png"]
    for i in range(5):
        complete += ["--change-note", f"beat {i} materially changes the teaching mechanism"]
    passed = subprocess.run(complete, env=env, capture_output=True, text=True)
    receipt = json.loads((ws / "qa" / "VISUAL-REVIEW.json").read_text())
    check("evidence-backed independent review passes", passed.returncode == 0,
          passed.stderr)
    check("receipt binds inspected pixels by hash",
          receipt["evidence_frames"][0]["sha256"] ==
          hashlib.sha256((ws / "snapshots" / "one.png").read_bytes()).hexdigest())
    check("the shared reader accepts the complete receipt",
          not validate_visual_review(ws, receipt),
          str(validate_visual_review(ws, receipt)))
    (ws / "snapshots" / "one.png").write_bytes(b"changed-after-review")
    failures = validate_visual_review(ws, receipt)
    check("changing an inspected frame invalidates the review",
          any("bytes changed after review" in failure for failure in failures),
          str(failures))

    coverage = tmp / "coverage"
    (coverage / "snapshots").mkdir(parents=True)
    (coverage / "index.html").write_text("<main></main>")
    (coverage / "audio_request.json").write_text(json.dumps({
        "lines": [{"id": f"b{i}", "text": f"Beat {i}."} for i in range(4)]
    }))
    (coverage / "timing.json").write_text(json.dumps({
        "total": 8,
        "rows": [{"id": f"b{i}", "vis_start": i * 2, "vis_dur": 2}
                 for i in range(4)]
    }))
    rows = []
    for i, when in enumerate((1, 3, 5)):
        path = coverage / "snapshots" / f"frame-{i:02d}-at-{when}s.png"
        path.write_bytes(f"frame-{i}".encode())
        rows.append({"path": str(path.relative_to(coverage)),
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    partial = {
        "reviewer": "review-agent", "evidence_frames": rows,
        "weakest_frames": rows[:1], "layout_families": 3,
        "material_changes": [f"change {i}" for i in range(5)],
    }
    failures = validate_visual_review(coverage, partial)
    check("three cherry-picked frames cannot approve a four-beat lesson",
          any("does not cover 1/4" in failure for failure in failures),
          str(failures))
finally:
    shutil.rmtree(tmp)

print(f"{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
