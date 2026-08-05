#!/usr/bin/env python3
"""test_preflight_contract.py — preflight.py --json is a frozen wire contract.

Until 2026-08-05 this suite tested the plan-stage guard, the
PostToolUse hook that ran `preflight.py --static --json` on every scenes.json
write and extracted the verdict with jq. The guard retired with the template
lane's compiler (decisions/log.md 2026-08-05; the script is provenance under
scripts/_archive/), but the lesson it was built on did not: its jq extraction
once ran with `2>/dev/null`, so when `.output` stopped being a string the
error was eaten, the violation string came back EMPTY, and the guard reported
CLEAN on every failing plan. A machine consumer of this JSON must be able to
trust its shape — so the shape stays pinned even with no standing consumer
wired up today.

Assertions, against a workspace engineered to FAIL preflight statically:

  1. `preflight.py --static --json` runs as a real subprocess.
  2. stdout's first byte is `{` — catches any stray print() ahead of the JSON.
  3. The payload parses, carries `verdict` and `sections`, and the verdict is
     FAIL when any section fails.
  4. Every section key matches ^[a-z_]+$, every `pass` is a bool, and every
     `output` is a string — the exact drift class that went silent before.

Run:  python3 tests/test_preflight_contract.py   (exit 0 = all pass)
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]

failures = []
TMP = Path(tempfile.mkdtemp())


def check(label, cond, detail=""):
    if cond:
        print(f"  ok  {label}")
    else:
        failures.append(f"{label}  {detail}")
        print(f"  FAIL {label}  {detail}")


# A minimal freeform workspace engineered to FAIL static preflight on several
# sections at once (the realistic case): a dated (non-canonical) stem, a
# sentence-case heading with a terminal period, and no approved script for the
# beat manifest to diff against.
ws = TMP / "bad-plan_no-such-program_2026-01-01"
ws.mkdir(parents=True)
(ws / "audio_request.json").write_text(json.dumps({
    "lines": ["A first beat of narration that no approved script carries.",
              "And a second beat to give the manifest some length."]}))
(ws / "index.html").write_text(
    '<html><body><div id="root" data-composition-id="main" data-start="0" '
    'data-duration="20" data-width="1920" data-height="1080">'
    '<div class="clip" id="b1" data-start="0" data-duration="10">'
    '<h1 data-role="heading">a sentence case heading.</h1></div>'
    '<div class="clip" id="b2" data-start="10" data-duration="10">'
    '<p>Second beat copy.</p></div>'
    '</div></body></html>')

p = subprocess.run(
    [sys.executable, str(RQ / "src" / "preflight.py"), "--static", "--json", str(ws)],
    capture_output=True, text=True)

# 1 + 2. The subprocess runs, and stdout is JSON from its very first byte.
check("preflight --static --json emits JSON from the first byte "
      "(no stray print ahead of it)",
      p.stdout.lstrip() and p.stdout.lstrip()[0] == "{",
      repr(p.stdout[:120]))

payload = None
try:
    payload = json.loads(p.stdout[p.stdout.find("{"):])
except (json.JSONDecodeError, ValueError) as exc:
    check("preflight --json is parseable", False, str(exc))

# 3. Verdict discipline: a failing plan says FAIL, and the exit code agrees.
if payload:
    check("payload carries `verdict` and `sections`",
          "verdict" in payload and isinstance(payload.get("sections"), dict),
          str(payload)[:200])
    really_failed = sorted(k for k, v in payload["sections"].items()
                           if not v.get("pass"))
    check("the engineered plan actually fails section(s) — the fixture fires",
          bool(really_failed), "fixture no longer fails anything")
    check("verdict is FAIL when any section fails",
          payload["verdict"] == "FAIL", payload["verdict"])
    check("exit code agrees with the verdict", p.returncode == 1,
          str(p.returncode))

    # 4. Key and type discipline — the wire contract.
    bad_keys = [k for k in payload["sections"] if not re.fullmatch(r"[a-z_]+", k)]
    check("every section key matches ^[a-z_]+$", not bad_keys, str(bad_keys))
    bad_types = [
        k for k, v in payload["sections"].items()
        if not isinstance(v.get("pass"), bool) or not isinstance(v.get("output"), str)]
    check("sections[].pass is a bool and sections[].output is a string",
          not bad_types, str(bad_types))

shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\nFAIL ({len(failures)})")
    sys.exit(1)
print("test_preflight_contract: the --json wire contract holds")
