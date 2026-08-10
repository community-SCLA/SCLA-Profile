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


tmp = Path(tempfile.mkdtemp(prefix="scla-review-evidence-"))
try:
    vp = tmp / "video-production"
    ws = vp / "renders-hyperframes" / "lesson_prog"
    (ws / "qa").mkdir(parents=True)
    (ws / "snapshots").mkdir()
    (ws / "concepts").mkdir()
    (vp / "lesson-scripts" / "prog" / "ready").mkdir(parents=True)
    (vp / "lesson-scripts" / "prog" / "ready" / "lesson_prog.txt").write_text("Lesson.")
    (ws / ".scla-control-v3").touch()
    (ws / "index.html").write_text('<main data-duration="1"></main>')
    (ws / "concepts" / "CONCEPT-BOARD.json").write_text(
        json.dumps({"authored_by": "builder-agent"}))
    for name in ("one.png", "two.png", "three.png", "weak.png"):
        (ws / "snapshots" / name).write_bytes(("visible-" + name).encode())
    revision = workspace_revision(ws)
    (ws / "qa" / "PREFLIGHT-OK").write_text(json.dumps({"source_revision": revision}))
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
    check("v3 refuses label-only approval", missing.returncode != 0 and
          "requires --reviewer" in missing.stderr, missing.stderr)
    same = subprocess.run(base + ["--reviewer", "builder-agent"], env=env,
                          capture_output=True, text=True)
    check("concept author cannot self-approve", same.returncode != 0 and
          "different from the concept author" in same.stderr, same.stderr)
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
finally:
    shutil.rmtree(tmp)

print(f"{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
