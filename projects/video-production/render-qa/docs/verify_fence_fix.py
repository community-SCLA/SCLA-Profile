#!/usr/bin/env python3
"""Prove the write-fence fix: same cases against the LIVE fence and the FIXED one.

Two things must both hold:
  1. every case the live fence gets RIGHT stays right (no safety regression);
  2. the three false positives observed on install day become ALLOWED.
"""
import json
import os
import subprocess
import sys

REPO = "/workspaces/SCLA-Profile"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
LIVE = f"{REPO}/scripts/write-fence.sh"
FIXED = f"{SCRATCH}/write-fence.fixed.sh"

DS = "projects/video-production/design-system"
SRC = "projects/video-production/render-qa/src"


def run(script, tool, inp):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=REPO)
    env.pop("SCLA_SYSTEM_SESSION", None)
    p = subprocess.run(["bash", script],
                       input=json.dumps({"tool_name": tool,
                                         "tool_input": inp}),
                       capture_output=True, text=True, env=env)
    return p.returncode


# (label, tool, input, expected_after_fix)   BLOCK=2 ALLOW=0
CASES = [
    # --- the three false positives observed on install day -----------------
    ("FP1 commit whose MESSAGE names a fenced path + 'touch'", "Bash",
     {"command": "git add -A && git commit -q -F - <<'MSG'\n"
                 "feat: a probe write under scripts/ was blocked\n"
                 "we ran touch scripts/__fence_probe to verify\n"
                 "MSG"}, 0),
    ("FP2 quoted sed '>' that is not a redirect, near a fenced path", "Bash",
     {"command": "env | sed 's/=.*/=<set>/' ; head -20 scripts/with-secrets.sh"},
     0),
    ("FP3 read-only grep with 2>/dev/null naming a fenced path", "Bash",
     {"command": "ls x 2>/dev/null | head -12; grep -rn freeform scripts/*.sh"},
     0),

    # --- safety must not regress -------------------------------------------
    ("real redirect INTO a fenced path", "Bash",
     {"command": "echo x > scripts/batch-ship.sh"}, 2),
    ("real append INTO a fenced path", "Bash",
     {"command": f"cat /tmp/new >> {SRC}/check_copy.py"}, 2),
    ("rm of a gate source", "Bash",
     {"command": f"rm -f {SRC}/check_motion.py"}, 2),
    ("sed -i on tokens.yml", "Bash",
     {"command": f"sed -i 's/40/20/' {DS}/config/tokens.yml"}, 2),
    ("mv onto settings.json", "Bash", {"command": "mv /tmp/a .claude/settings.json"}, 2),
    ("tee into a fenced script", "Bash",
     {"command": "tee scripts/lint-refs.sh < /tmp/x"}, 2),
    ("git checkout of tokens.yml", "Bash",
     {"command": f"git checkout -- {DS}/config/tokens.yml"}, 2),
    ("cp INTO a fenced path", "Bash",
     {"command": f"cp /tmp/x.html {DS}/compositions/scla-stat.html"}, 2),
    ("mv OUT of a fenced path (removes the original)", "Bash",
     {"command": f"mv {SRC}/check_copy.py /tmp/"}, 2),
    ("Write to a template", "Write",
     {"file_path": f"{REPO}/{DS}/compositions/scla-stat.html"}, 2),
    ("Edit to a gate", "Edit", {"file_path": f"{REPO}/{SRC}/tokens.py"}, 2),
    ("Write to .claude rules", "Write",
     {"file_path": f"{REPO}/.claude/rules/video-production.md"}, 2),

    # --- ordinary build work must stay free --------------------------------
    ("running a gate", "Bash", {"command": f"python3 {SRC}/check_copy.py ws"}, 0),
    ("running the linter", "Bash", {"command": "bash scripts/lint-refs.sh"}, 0),
    ("2>/dev/null on a gate run", "Bash",
     {"command": f"python3 {SRC}/check_ink.py frames 2>/dev/null"}, 0),
    ("cp OUT of a fenced path (the prepare step)", "Bash",
     {"command": f"cp {DS}/config/tokens.yml "
                 "projects/video-production/renders-hyperframes/m2_demo/tokens.yml"}, 0),
    ("workspace write", "Write",
     {"file_path": f"{REPO}/projects/video-production/renders-hyperframes/"
                   "m2_demo/index.html"}, 0),
    ("redirect into a WORKSPACE file", "Bash",
     {"command": "echo x > projects/video-production/renders-hyperframes/"
                 "m2_demo/timing.json"}, 0),
]

name = {0: "ALLOW", 2: "BLOCK"}
bad = 0
print(f"{'case':<58}{'live':>7}{'fixed':>8}{'want':>7}")
for label, tool, inp, want in CASES:
    live, fixed = run(LIVE, tool, inp), run(FIXED, tool, inp)
    ok = fixed == want
    bad += not ok
    flag = "" if ok else "   <-- WRONG"
    print(f"{label:<58}{name.get(live,live):>7}{name.get(fixed,fixed):>8}"
          f"{name[want]:>7}{flag}")

print()
if bad:
    print(f"FAIL — {bad} case(s) wrong after the fix")
    sys.exit(1)
print("PASS — every case correct after the fix, and no safety case regressed")
