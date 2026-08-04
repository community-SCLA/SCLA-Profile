#!/usr/bin/env python3
"""test_write_fence.py — scripts/write-fence.sh is verified by INVOKING it.

BUILD-PLAN step 2.1's done-condition is explicit that the block must be
"observed, not assumed", and test_guard_contract.py already established why: a
guard is checked by running it, never by reading it. The 2026-07-28 layout
refactor left hyperframe-guard.sh pointing at a moved path, so every firing
printed "can't open file" instead of a verdict — output that looked alive while
grading nothing. Reading the script would not have caught that. Running it does.

A fence has TWO failure modes and both are graded here:
  - too loose — the shared machinery it exists to protect stays writable;
  - too tight — it blocks the ordinary build work the pipeline must keep doing,
    which is how a guard gets switched off within a day.

Every case runs the real script as a subprocess with a crafted PreToolUse
payload on stdin, exactly as Claude Code invokes it.

Run:  python3 tests/test_write_fence.py   (exit 0 = all pass)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
REPO = RQ.parents[2]
FENCE = REPO / "scripts" / "write-fence.sh"

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def run(tool, payload_input, system_session=False):
    """(exit_code, stderr) from the real hook script."""
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO))
    env.pop("SCLA_SYSTEM_SESSION", None)
    if system_session:
        env["SCLA_SYSTEM_SESSION"] = "1"
    p = subprocess.run(
        ["bash", str(FENCE)], input=json.dumps(
            {"tool_name": tool, "tool_input": payload_input}),
        capture_output=True, text=True, env=env)
    return p.returncode, p.stderr


def blocked(tool, inp, **kw):
    return run(tool, inp, **kw)[0] == 2


def allowed(tool, inp, **kw):
    return run(tool, inp, **kw)[0] == 0


check("the fence script exists at the path settings.json invokes",
      FENCE.is_file(), str(FENCE))
check("the fence script is syntactically valid bash",
      subprocess.run(["bash", "-n", str(FENCE)],
                     capture_output=True).returncode == 0)

# ---------------------------------------------------------------------------
print("== the shared machinery is fenced (Write/Edit) ==")
for path in [
    "projects/video-production/design-system/compositions/scla-stat.html",
    "projects/video-production/design-system/config/tokens.yml",
    "projects/video-production/renders-hyperframes/_run/scaffold/index.html",
    "projects/video-production/render-qa/src/check_copy.py",
    "scripts/batch-ship.sh",
    ".claude/rules/video-production.md",
    ".claude/settings.json",
]:
    check(f"Write to {path} is BLOCKED",
          blocked("Write", {"file_path": str(REPO / path)}), path)

check("the scla-stat incident itself is now physically blocked",
      blocked("Edit", {"file_path": str(
          REPO / "projects/video-production/design-system/compositions"
                 "/scla-stat.html")}))
check("a RELATIVE path is fenced too (the resolved path is what matters)",
      blocked("Write", {"file_path":
                        "projects/video-production/render-qa/src/tokens.py"}))

# ---------------------------------------------------------------------------
print("== ...and the actual job is not ==")
for path in [
    "projects/video-production/renders-hyperframes/m2_demo/scenes.json",
    "projects/video-production/renders-hyperframes/m2_demo/index.html",
    "projects/video-production/renders-hyperframes/m2_demo/compositions/map.html",
    "projects/video-production/lesson-scripts/mid-career-momentum/refined/m2.txt",
    "projects/video-production/render-qa/docs/BUILD-PLAN-agent-native-2026-08-04.md",
]:
    check(f"Write to {path} is ALLOWED",
          allowed("Write", {"file_path": str(REPO / path)}), path)

# _run/ is fenced but its SIBLING workspaces must not be — a prefix bug here
# would fence the whole build lane, which is how a guard gets switched off.
check("renders-hyperframes/_run is fenced but <stem>/ beside it is not",
      blocked("Write", {"file_path": str(
          REPO / "projects/video-production/renders-hyperframes/_run/BUILD-KIT.md")})
      and allowed("Write", {"file_path": str(
          REPO / "projects/video-production/renders-hyperframes/"
                 "_runaway_stem/index.html")}))

# ---------------------------------------------------------------------------
print("== Bash-mediated writes: the routing-around vector ==")
for cmd in [
    "cp /tmp/x.html projects/video-production/design-system/compositions/scla-stat.html",
    "echo 'x' > scripts/batch-ship.sh",
    "cat /tmp/new >> projects/video-production/render-qa/src/check_copy.py",
    "sed -i 's/40/20/' projects/video-production/design-system/config/tokens.yml",
    "rm -f projects/video-production/render-qa/src/check_motion.py",
    "mv /tmp/a .claude/settings.json",
    "tee scripts/lint-refs.sh < /tmp/x",
    "git checkout -- projects/video-production/design-system/config/tokens.yml",
]:
    check(f"BLOCKED: {cmd[:62]}", blocked("Bash", {"command": cmd}), cmd)

print("== ...while reading and RUNNING the same files stays free ==")
for cmd in [
    "python3 projects/video-production/render-qa/src/check_copy.py ws",
    "bash scripts/lint-refs.sh",
    "python3 projects/video-production/render-qa/tests/run_tests.py",
    "grep -n tokens projects/video-production/design-system/config/tokens.yml",
    "cat scripts/batch-status.sh",
    "git status",
    "npx --yes hyperframes@0.7.79 render",
    # Copying OUT of a fenced path is a READ. batch-prepare.sh does exactly
    # this on every prepare; blocking it would block the pipeline working.
    "cp projects/video-production/design-system/config/tokens.yml "
    "projects/video-production/renders-hyperframes/m2_demo/tokens.yml",
]:
    check(f"ALLOWED: {cmd[:62]}", allowed("Bash", {"command": cmd}), cmd)

# ---------------------------------------------------------------------------
print("== the deliberate system session, and only it, may proceed ==")
check("copying INTO a fenced path is still blocked (direction matters)",
      blocked("Bash", {"command":
              "cp /tmp/tokens.yml projects/video-production/design-system/"
              "config/tokens.yml"}))
check("but `mv` OUT of a fenced path is blocked — it removes the original",
      blocked("Bash", {"command":
              "mv projects/video-production/render-qa/src/check_copy.py /tmp/"}))

check("SCLA_SYSTEM_SESSION=1 allows the template edit",
      allowed("Edit", {"file_path": str(
          REPO / "projects/video-production/design-system/config/tokens.yml")},
          system_session=True))
check("...and the same edit without the flag is blocked",
      blocked("Edit", {"file_path": str(
          REPO / "projects/video-production/design-system/config/tokens.yml")}))

# ---------------------------------------------------------------------------
print("== a fence that cannot read the call must refuse, not shrug ==")
env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO))
env.pop("SCLA_SYSTEM_SESSION", None)
p = subprocess.run(["bash", str(FENCE)], input="not json at all",
                   capture_output=True, text=True, env=env)
check("an unparseable payload is REFUSED (fail closed), not allowed",
      p.returncode == 2, f"rc={p.returncode}")

check("a blocked call explains itself and names the fenced prefix",
      "design-system" in run("Write", {"file_path": str(
          REPO / "projects/video-production/design-system/x.html")})[1])
check("the block tells the agent to REPORT the problem, not patch it",
      "REPORTED" in run("Write", {"file_path": str(
          REPO / "scripts/x.sh")})[1])

# ---------------------------------------------------------------------------
print("== data is not command, and a redirect is graded by its TARGET ==")
check("a commit whose MESSAGE names a fenced path is ALLOWED",
      allowed("Bash", {"command":
              "git commit -F - <<'MSG'\n"
              "a probe write under scripts/ was blocked\n"
              "we ran touch scripts/__fence_probe to verify\n"
              "MSG"}))
check("`2>/dev/null` on a read-only command naming a fenced path is ALLOWED",
      allowed("Bash", {"command":
              "python3 projects/video-production/render-qa/src/check_ink.py "
              "frames 2>/dev/null"}))
check("a '>' inside a quoted sed replacement is not a redirect",
      allowed("Bash", {"command":
              "env | sed 's/=.*/=<set>/' ; head -20 scripts/with-secrets.sh"}))
check("but a REAL redirect into a fenced path is still blocked",
      blocked("Bash", {"command": "echo x > scripts/batch-ship.sh"}))
check("...and a redirect into a WORKSPACE file is still allowed",
      allowed("Bash", {"command":
              "echo x > projects/video-production/renders-hyperframes/"
              "m2_demo/timing.json"}))

print("== the credential path: with-secrets.sh is fenced AND mandatory ==")
check("TTS via with-secrets, redirecting into the build's OWN workspace",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh node audio.mjs --provider heygen "
              "> projects/video-production/renders-hyperframes/"
              "m2_demo/audio_meta.json"}))
check("a credentialed publish with 2>/dev/null is ALLOWED",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh bash scripts/wistia-upload.sh "
              "out.mp4 2>/dev/null"}))
check("but leaking the injected env INTO a fenced path is still blocked",
      blocked("Bash", {"command":
              "bash scripts/with-secrets.sh env > scripts/leaked.env"}))

print("== FP6/FP7: read-only commands, observed live on 2026-08-04 ==")
check("a bare `ls` of a fenced dir with 2>/dev/null is ALLOWED",
      allowed("Bash", {"command":
              "ls .claude/skills/hyperframes-media/ 2>/dev/null"}))
check("capturing a GATE's own output to a non-fenced scratch path is ALLOWED",
      allowed("Bash", {"command":
              "python3 projects/video-production/render-qa/src/preflight.py "
              "projects/video-production/renders-hyperframes/m2_demo "
              "> /tmp/pf.txt"}))
check("...but writing INTO the gate directory is still blocked",
      blocked("Bash", {"command":
              "echo x > projects/video-production/render-qa/src/preflight.py"}))

print("== the documented TTS form has no redirect and must stay ALLOWED ==")
check("audio.mjs --out (a flag, not a redirect) through with-secrets",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh node m/scripts/audio.mjs "
              "--request ./audio_request.json --hyperframes . "
              "--out ./audio_meta.json --only tts --provider heygen"}))

# ---------------------------------------------------------------------------
print("== the hook is actually registered, or none of the above runs ==")
settings = json.loads((REPO / ".claude" / "settings.json").read_text())
pre = settings.get("hooks", {}).get("PreToolUse", [])
cmds = [h.get("command", "") for entry in pre for h in entry.get("hooks", [])]
check("settings.json registers write-fence.sh as a PreToolUse hook",
      any("write-fence.sh" in c for c in cmds), str(cmds))
matchers = [e.get("matcher", "") for e in pre
            if any("write-fence.sh" in h.get("command", "")
                   for h in e.get("hooks", []))]
check("...on Write, Edit AND Bash — Bash is the routing-around vector",
      any(all(t in m for t in ("Write", "Edit", "Bash")) for m in matchers),
      str(matchers))

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
