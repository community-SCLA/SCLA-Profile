#!/usr/bin/env python3
"""Regression guard for Cloud tasks that return a stagnant Studio frame."""

import json
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from preflight import check_hyperframes_source

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


with tempfile.TemporaryDirectory(prefix="scla-cloud-gate-") as tmp:
    ws = Path(tmp) / "lesson-a"
    ws.mkdir()
    (ws / "audio_request.json").write_text(json.dumps({
        "lines": [
            {"id": "welcome", "text": "Welcome."},
            {"id": "commitment", "text": "Commit."},
        ]
    }))

    stagnant = """<!doctype html><html><body>
    <main data-composition="lesson-a" data-width="1920" data-height="1080">
      <section class="clip" data-beat-id="welcome" data-duration="2">Welcome</section>
      <section class="clip" data-beat-id="commitment" data-duration="2">Commit</section>
    </main></body></html>"""
    result = check_hyperframes_source(ws, stagnant)
    check("stagnant Cloud shell fails source gate", not result["pass"], result["output"])
    check("zero-duration failure is explicit",
          "composition root" in result["output"] and
          "timeline" in result["output"] and
          "index.motion.json" in result["output"], result["output"])

    (ws / "index.motion.json").write_text(json.dumps({
        "duration": 4,
        "assertions": [
            {"kind": "appearsBy", "selector": "#welcome-title", "bySec": 0.5},
            {"kind": "appearsBy", "selector": "#commit-title", "bySec": 2.5},
            {"kind": "keepsMoving", "withinSelector": "#root"},
        ]
    }))
    valid = """<!doctype html><html><body>
    <main id="root" data-composition-id="lesson-a" data-start="0"
          data-width="1920" data-height="1080" data-duration="4">
      <section id="welcome" class="clip" data-beat-id="welcome"
               data-start="0" data-duration="2" data-track-index="1">
        <h1 id="welcome-title">Welcome</h1>
      </section>
      <section id="commitment" class="clip" data-beat-id="commitment"
               data-start="2" data-duration="2" data-track-index="1">
        <h1 id="commit-title">Commit</h1>
      </section>
    </main>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#welcome-title", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0);
      tl.fromTo("#commit-title", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 2);
      window.__timelines["lesson-a"] = tl;
    </script></body></html>"""
    result = check_hyperframes_source(ws, valid)
    check("timed animated source passes source gate", result["pass"], result["output"])

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
