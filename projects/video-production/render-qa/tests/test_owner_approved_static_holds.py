#!/usr/bin/env python3
"""Firing tests for the owner-approved static-hold verification policy."""

import json
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from verify_render import (  # noqa: E402
    apply_owner_static_hold_policy,
    current_owner_approval,
)

PASS = FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def report(*rules):
    return {
        "violations": [
            {"rule": rule, "rule_id": rule, "severity": "error",
             "detail": f"fixture {rule}"}
            for rule in rules
        ],
        "warnings": [],
        "verdict": "FAIL" if rules else "PASS",
    }


approval = {
    "revision": "revision-a",
    "approved_at": "2026-08-10T00:00:00Z",
    "approved_by": "owner",
}

strict = apply_owner_static_hold_policy(report("stagnant-frame"), None)
check("unapproved long static hold still fails",
      strict["verdict"] == "FAIL"
      and strict["violations"][0]["rule"] == "stagnant-frame", strict)

allowed = apply_owner_static_hold_policy(report("stagnant-frame"), approval)
check("exact owner approval makes only the static hold non-blocking",
      allowed["verdict"] == "PASS" and not allowed["violations"], allowed)
check("approved hold remains visible as an auditable warning",
      allowed["warnings"][0]["rule"] == "owner-approved-static-hold"
      and allowed["warnings"][0]["original_rule"] == "stagnant-frame"
      and allowed["warnings"][0]["approval_revision"] == "revision-a", allowed)

mixed = apply_owner_static_hold_policy(
    report("stagnant-frame", "near-blank-frame"), approval)
check("owner approval does not excuse another presence defect",
      mixed["verdict"] == "FAIL"
      and [x["rule"] for x in mixed["violations"]] == ["near-blank-frame"]
      and mixed["warnings"][0]["rule"] == "owner-approved-static-hold", mixed)

with tempfile.TemporaryDirectory(prefix="approved-static-hold-") as tmp:
    root = Path(tmp)
    ws = root / "renders-hyperframes" / "lesson-a"
    run = ws.parent / "_run" / "run.json"
    run.parent.mkdir(parents=True)
    ws.mkdir()

    def write_receipt(receipt):
        run.write_text(json.dumps({"approvals": {"lesson-a": receipt}}))

    write_receipt(approval)
    check("durable exact-revision owner approval is recognized",
          current_owner_approval(ws, "revision-a") == approval)
    check("stale approval is rejected",
          current_owner_approval(ws, "revision-b") is None)

    write_receipt({**approval, "approved_by": "agent"})
    check("non-owner approval is rejected",
          current_owner_approval(ws, "revision-a") is None)

    write_receipt({k: v for k, v in approval.items() if k != "approved_at"})
    check("incomplete approval receipt is rejected",
          current_owner_approval(ws, "revision-a") is None)

    alternate = root / "alternate-run.json"
    alternate.write_text(json.dumps({"approvals": {"lesson-a": approval}}))
    old = os.environ.get("VIDEO_RUN_STATE")
    os.environ["VIDEO_RUN_STATE"] = str(alternate)
    try:
        check("configured canonical run-state path is honored",
              current_owner_approval(ws, "revision-a") == approval)
    finally:
        if old is None:
            os.environ.pop("VIDEO_RUN_STATE", None)
        else:
            os.environ["VIDEO_RUN_STATE"] = old

with tempfile.TemporaryDirectory(prefix="approved-static-hold-e2e-") as tmp:
    root = Path(tmp)
    ws = root / "renders-hyperframes" / "lesson-e2e"
    voice = ws / "assets" / "voice"
    renders = ws / "renders"
    qa = ws / "qa"
    voice.mkdir(parents=True)
    renders.mkdir()
    qa.mkdir()
    (voice / "transcript.json").write_text(json.dumps([
        {"text": "Narration", "start": 0.0, "end": 7.0},
    ]))
    (ws / "index.html").write_text("""<!doctype html><html><body>
<div id="root" data-duration="7" data-width="1920" data-height="1080">
  <div id="scene-1" class="clip" data-composition-id="fixture"
       data-composition-src="compositions/fixture.html"
       data-start="0" data-duration="7" data-track-index="1"></div>
</div></body></html>""")
    mp4 = renders / "lesson-e2e.mp4"
    made = subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=#f5f0e6:s=1920x1080:r=30:d=7",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=7",
        "-vf", "drawbox=x=200:y=180:w=700:h=420:color=#1b2a4a:t=fill",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-shortest", str(mp4),
    ], capture_output=True, text=True)
    check("static integration fixture renders", made.returncode == 0, made.stderr)
    if made.returncode == 0:
        from workspace_revision import workspace_revision
        revision = workspace_revision(ws)
        payload = mp4.read_bytes()
        (qa / "RENDER-START.json").write_text(json.dumps({
            "source_revision": revision,
            "encode_review_required": False,
            "attempt": 1,
            "mp4": str(mp4),
            "completed_at": "2026-08-10T00:00:00Z",
            "completed_sha256": hashlib.sha256(payload).hexdigest(),
            "completed_bytes": len(payload),
        }))
        run = ws.parent / "_run" / "run.json"
        run.parent.mkdir()
        run.write_text(json.dumps({"approvals": {"lesson-e2e": {
            **approval, "revision": "stale-revision",
        }}}))
        verify = SRC / "verify_render.py"
        stale = subprocess.run(
            [sys.executable, str(verify), str(ws), str(mp4), "--json"],
            capture_output=True, text=True)
        check("full verifier still blocks a static hold with stale approval",
              stale.returncode == 1
              and "stagnant-frame" in stale.stdout, stale.stdout + stale.stderr)

        run.write_text(json.dumps({"approvals": {"lesson-e2e": {
            **approval, "revision": revision,
        }}}))
        exact = subprocess.run(
            [sys.executable, str(verify), str(ws), str(mp4), "--json"],
            capture_output=True, text=True)
        check("full verifier passes the same bytes after exact owner approval",
              exact.returncode == 0
              and "owner-approved-static-hold" in exact.stdout,
              exact.stdout + exact.stderr)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
