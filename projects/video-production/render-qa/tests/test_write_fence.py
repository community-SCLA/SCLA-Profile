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
  - too tight — it blocks work that must keep happening, which is how a guard
    gets switched off within a day.

The 2026-08-04 rebuild widened "too tight" past the build lane. The fence is now
gated on a SENTINEL (renders-hyperframes/.build-in-progress) rather than on an
SCLA_SYSTEM_SESSION env flag, because that flag could not tell the owner from
the subagents they dispatch — the two share one process — and so it fenced the
owner out of their own repo. Every block below is therefore asserted twice: it
must fire while a build is armed, and it must NOT fire when none is.

Every case runs the real script as a subprocess with a crafted PreToolUse
payload on stdin, exactly as Claude Code invokes it, against a THROWAWAY project
dir — so a test run can never leave the live repo fenced.

Run:  python3 tests/test_write_fence.py   (exit 0 = all pass)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
REPO = RQ.parents[2]
FENCE = REPO / "scripts" / "write-fence.sh"

# A disposable stand-in for the repo. The fence only ever string-matches paths
# against CLAUDE_PROJECT_DIR and stats one sentinel file, so a bare directory
# tree is a faithful subject — and arming it cannot fence the real session
# running these tests.
PROJ = Path(tempfile.mkdtemp(prefix="write-fence-test-"))
SENTINEL = PROJ / "projects/video-production/renders-hyperframes/.build-in-progress"

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def arm(stem="m2_demo"):
    SENTINEL.parent.mkdir(parents=True, exist_ok=True)
    SENTINEL.write_text(f"2026-08-04T00:00:00Z\t{stem}\n")


def disarm():
    SENTINEL.unlink(missing_ok=True)


def run(tool, payload_input, system_session=False, env_extra=None):
    """(exit_code, stderr) from the real hook script."""
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(PROJ))
    env.pop("SCLA_SYSTEM_SESSION", None)
    env.pop("VIDEO_BUILD_SESSION_TTL", None)
    if system_session:
        env["SCLA_SYSTEM_SESSION"] = "1"
    env.update(env_extra or {})
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
# The gate itself. This is the change of 2026-08-04, and it is the first thing
# graded because everything below depends on which state the fence is in.
print("== the sentinel is the gate: no build in flight, no fence ==")
disarm()
for path in [
    "projects/video-production/design-system/config/tokens.yml",
    "projects/video-production/render-qa/src/check_copy.py",
    "scripts/batch-ship.sh",
    ".claude/settings.json",
]:
    check(f"DISARMED: the owner may write {path}",
          allowed("Write", {"file_path": str(PROJ / path)}), path)
check("DISARMED: the owner may edit a script from Bash too",
      allowed("Bash", {"command": f"sed -i 's/a/b/' {PROJ}/scripts/batch-ship.sh"}))

arm()
check("ARMED: the same write is refused",
      blocked("Write", {"file_path": str(PROJ / "scripts/batch-ship.sh")}))
check("ARMED: the same Bash edit is refused",
      blocked("Bash", {"command": f"sed -i 's/a/b/' {PROJ}/scripts/batch-ship.sh"}))

print("== an armed builder cannot disarm the fence it stands inside ==")
check("ARMED: rm of the sentinel is refused",
      blocked("Bash", {"command": f"rm -f {SENTINEL}"}))
check("ARMED: overwriting the sentinel is refused",
      blocked("Write", {"file_path": str(SENTINEL)}))
check("ARMED: a redirect that truncates the sentinel is refused",
      blocked("Bash", {"command": f"echo '' > {SENTINEL}"}))
check("...but RUNNING build-session.sh disarm is allowed — the script does the "
      "rm, and the hook grades the tool call",
      allowed("Bash", {"command": "bash scripts/build-session.sh disarm m2_demo"}))
check("...and so is the close-out command the skill actually issues",
      allowed("Bash", {"command": "bash scripts/build-release.sh m2_demo"}))

print("== a sentinel a dead run never cleaned up expires ==")
old = SENTINEL.stat().st_mtime - 40000        # ~11h, past the 6h default
os.utime(SENTINEL, (old, old))
check("an EXPIRED sentinel does not fence (default 6h TTL)",
      allowed("Write", {"file_path": str(PROJ / "scripts/batch-ship.sh")}))
check("...and a fresh one still does, with the same TTL in force",
      blocked("Write", {"file_path": str(PROJ / "scripts/batch-ship.sh")},
              env_extra={"VIDEO_BUILD_SESSION_TTL": "999999"}))
arm()

# ---------------------------------------------------------------------------
print("== armed: the shared machinery is fenced (Write/Edit) ==")
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
          blocked("Write", {"file_path": str(PROJ / path)}), path)

check("the scla-stat incident itself is now physically blocked",
      blocked("Edit", {"file_path": str(
          PROJ / "projects/video-production/design-system/compositions"
                 "/scla-stat.html")}))
check("a RELATIVE path is fenced too (the resolved path is what matters)",
      blocked("Write", {"file_path":
                        "projects/video-production/render-qa/src/tokens.py"}))

# ---------------------------------------------------------------------------
print("== ...and the actual job is not, in EITHER state ==")
WORKSPACE_WRITES = [
    "projects/video-production/renders-hyperframes/m2_demo/scenes.json",
    "projects/video-production/renders-hyperframes/m2_demo/index.html",
    "projects/video-production/renders-hyperframes/m2_demo/compositions/map.html",
    "projects/video-production/renders-hyperframes/m2_demo/.build-log.tsv",
    "projects/video-production/lesson-scripts/mid-career-momentum/ready/m2.txt",
    "projects/video-production/render-qa/docs/BUILD-PLAN-agent-native-2026-08-04.md",
]
for path in WORKSPACE_WRITES:
    check(f"ARMED: Write to {path} is ALLOWED",
          allowed("Write", {"file_path": str(PROJ / path)}), path)
disarm()
for path in WORKSPACE_WRITES:
    check(f"DISARMED: Write to {path} is ALLOWED",
          allowed("Write", {"file_path": str(PROJ / path)}), path)
arm()

# _run/ is fenced but its SIBLING workspaces must not be — a prefix bug here
# would fence the whole build lane, which is how a guard gets switched off.
check("renders-hyperframes/_run is fenced but <stem>/ beside it is not",
      blocked("Write", {"file_path": str(
          PROJ / "projects/video-production/renders-hyperframes/_run/BUILD-KIT.md")})
      and allowed("Write", {"file_path": str(
          PROJ / "projects/video-production/renders-hyperframes/"
                 "_runaway_stem/index.html")}))

# ---------------------------------------------------------------------------
print("== Bash-mediated writes: the routing-around vector ==")
for cmd in [
    f"cp /tmp/x.html {PROJ}/projects/video-production/design-system/compositions/scla-stat.html",
    f"echo 'x' > {PROJ}/scripts/batch-ship.sh",
    f"cat /tmp/new >> {PROJ}/projects/video-production/render-qa/src/check_copy.py",
    f"sed -i 's/40/20/' {PROJ}/projects/video-production/design-system/config/tokens.yml",
    f"rm -f {PROJ}/projects/video-production/render-qa/src/check_motion.py",
    f"mv /tmp/a {PROJ}/.claude/settings.json",
    f"tee {PROJ}/scripts/lint-refs.sh < /tmp/x",
    f"git checkout -- {PROJ}/projects/video-production/design-system/config/tokens.yml",
]:
    check(f"BLOCKED: {cmd[:62]}", blocked("Bash", {"command": cmd}), cmd)

print("== ...while reading and RUNNING the same files stays free ==")
for cmd in [
    "python3 projects/video-production/render-qa/src/check_copy.py ws",
    "bash scripts/lint-refs.sh",
    "python3 projects/video-production/render-qa/tests/run_tests.py",
    "grep -n tokens projects/video-production/design-system/config/tokens.yml",
    "cat scripts/batch-status.sh",
    "bash scripts/batch-status.sh --write",
    "git status",
    "npx --yes hyperframes@0.7.79 render",
    # Copying OUT of a fenced path is a READ. batch-prepare.sh does exactly
    # this on every prepare; blocking it would block the pipeline working.
    "cp projects/video-production/design-system/config/tokens.yml "
    "projects/video-production/renders-hyperframes/m2_demo/tokens.yml",
]:
    check(f"ALLOWED: {cmd[:62]}", allowed("Bash", {"command": cmd}), cmd)

# ---------------------------------------------------------------------------
print("== direction matters for the copy family ==")
check("copying INTO a fenced path is still blocked",
      blocked("Bash", {"command":
              f"cp /tmp/tokens.yml {PROJ}/projects/video-production/design-system/"
              "config/tokens.yml"}))
check("but `mv` OUT of a fenced path is blocked — it removes the original",
      blocked("Bash", {"command":
              f"mv {PROJ}/projects/video-production/render-qa/src/check_copy.py /tmp/"}))

print("== the explicit override survives, for anyone who wants it back ==")
check("SCLA_SYSTEM_SESSION=1 allows the template edit even while armed",
      allowed("Edit", {"file_path": str(
          PROJ / "projects/video-production/design-system/config/tokens.yml")},
          system_session=True))
check("...and the same edit without the flag is blocked",
      blocked("Edit", {"file_path": str(
          PROJ / "projects/video-production/design-system/config/tokens.yml")}))

# ---------------------------------------------------------------------------
print("== a fence that cannot read the call must refuse, not shrug ==")
env = dict(os.environ, CLAUDE_PROJECT_DIR=str(PROJ))
env.pop("SCLA_SYSTEM_SESSION", None)
p = subprocess.run(["bash", str(FENCE)], input="not json at all",
                   capture_output=True, text=True, env=env)
check("an unparseable payload is REFUSED (fail closed), not allowed",
      p.returncode == 2, f"rc={p.returncode}")

check("a blocked call explains itself and names the fenced prefix",
      "design-system" in run("Write", {"file_path": str(
          PROJ / "projects/video-production/design-system/x.html")})[1])
check("the block tells the agent to REPORT the problem, not patch it",
      "REPORT" in run("Write", {"file_path": str(
          PROJ / "scripts/x.sh")})[1])
check("...and it does NOT offer an env flag as the escape hatch — a build "
      "subagent that reads one will set it",
      "SCLA_SYSTEM_SESSION" not in run("Write", {"file_path": str(
          PROJ / "scripts/x.sh")})[1])

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
      blocked("Bash", {"command": f"echo x > {PROJ}/scripts/batch-ship.sh"}))
check("...and a redirect into a WORKSPACE file is still allowed",
      allowed("Bash", {"command":
              f"echo x > {PROJ}/projects/video-production/renders-hyperframes/"
              "m2_demo/timing.json"}))

print("== the credential path: with-secrets.sh is fenced AND mandatory ==")
check("TTS via with-secrets, redirecting into the build's OWN workspace",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh node audio.mjs --provider heygen "
              f"> {PROJ}/projects/video-production/renders-hyperframes/"
              "m2_demo/audio_meta.json"}))
check("a credentialed publish with 2>/dev/null is ALLOWED",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh bash scripts/wistia-upload.sh "
              "out.mp4 2>/dev/null"}))
check("but leaking the injected env INTO a fenced path is still blocked",
      blocked("Bash", {"command":
              f"bash scripts/with-secrets.sh env > {PROJ}/scripts/leaked.env"}))

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
              f"echo x > {PROJ}/projects/video-production/render-qa/src/preflight.py"}))

print("== the documented TTS form has no redirect and must stay ALLOWED ==")
check("audio.mjs --out (a flag, not a redirect) through with-secrets",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh node m/scripts/audio.mjs "
              "--request ./audio_request.json --hyperframes . "
              "--out ./audio_meta.json --only tts --provider heygen"}))

# ---------------------------------------------------------------------------
print("== build-session.sh is the only thing that moves the gate ==")
BS = REPO / "scripts" / "build-session.sh"
check("scripts/build-session.sh exists", BS.is_file(), str(BS))
check("...and is syntactically valid bash",
      subprocess.run(["bash", "-n", str(BS)], capture_output=True).returncode == 0)
check("`arm` with no stem is refused — a sentinel must say WHOSE build it is",
      subprocess.run(["bash", str(BS), "arm"], capture_output=True).returncode != 0)

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

shutil.rmtree(PROJ, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
