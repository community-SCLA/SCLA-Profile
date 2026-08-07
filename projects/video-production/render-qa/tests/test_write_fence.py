#!/usr/bin/env python3
"""test_write_fence.py — scripts/write-fence.sh is verified by INVOKING it.

BUILD-PLAN step 2.1's done-condition is explicit that the block must be
"observed, not assumed", and test_guard_contract.py already established why: a
guard is checked by running it, never by reading it. The 2026-07-28 layout
refactor left the then-live plan-stage guard pointing at a moved path, so every firing
printed "can't open file" instead of a verdict — output that looked alive while
grading nothing. Reading the script would not have caught that. Running it does.

A fence has TWO failure modes and both are graded here:
  - too loose — the shared machinery it exists to protect stays writable;
  - too tight — it blocks work that must keep happening, which is how a guard
    gets switched off within a day.

The fence is gated on per-stem leases under
`renders-hyperframes/.build-in-progress/` rather than on an
SCLA_SYSTEM_SESSION env flag, because that flag could not tell the owner from
the subagents they dispatch — the two share one process — and so it fenced the
owner out of their own repo. Every block below is therefore asserted twice: it
must fire while a build is armed, and it must NOT fire when none is.

Every case runs the real script as a subprocess with a crafted PreToolUse
payload on stdin, exactly as Claude Code invokes it, against a THROWAWAY project
dir — so a test run can never leave the live repo fenced.

Run:  python3 tests/test_write_fence.py   (exit 0 = all pass)
"""
import hashlib
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
BUILD_CLAIM = REPO / "scripts" / "build-claim.sh"
SOURCE_CHECKPOINT = RQ / "src" / "source_checkpoint.py"
WORKSPACE_REVISION = RQ / "src" / "workspace_revision.py"

# A disposable stand-in for the repo. The fence only ever string-matches paths
# against CLAUDE_PROJECT_DIR and asks build-session.sh for live leases, so a
# minimal copied driver is a faithful subject — and arming it cannot fence the real session
# running these tests.
PROJ = Path(tempfile.mkdtemp(prefix="write-fence-test-"))
SENTINEL = PROJ / "projects/video-production/renders-hyperframes/.build-in-progress"
(PROJ / "scripts").mkdir(parents=True)
shutil.copy2(REPO / "scripts" / "build-session.sh", PROJ / "scripts" / "build-session.sh")

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
    SENTINEL.mkdir(parents=True, exist_ok=True)
    subprocess.run(["bash", str(PROJ / "scripts" / "build-session.sh"),
                    "arm", stem], check=True, capture_output=True, text=True)


def disarm():
    shutil.rmtree(SENTINEL, ignore_errors=True)


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
lease = SENTINEL / "m2_demo"
old = lease.stat().st_mtime - 40000        # ~11h, past the 6h default
os.utime(lease, (old, old))
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

print("== FP8: a mutator taints its own sub-command, not the whole line ==")
check("a destructive verb in ONE sub-command does not fence a fenced path "
      "named in ANOTHER — this exact command was refused on install day",
      allowed("Bash", {"command":
              f"find {PROJ}/projects/video-production/renders-hyperframes/m2_demo "
              "-exec touch {} + ; bash scripts/batch-status.sh"}))
check("...and the same shape with && instead of ;",
      allowed("Bash", {"command":
              f"rm -rf {PROJ}/projects/video-production/renders-hyperframes/m2_demo/qa "
              "&& bash scripts/lint-refs.sh"}))
check("but a mutator in the SAME sub-command as a fenced path still blocks",
      blocked("Bash", {"command":
              f"bash scripts/lint-refs.sh ; rm -f {PROJ}/scripts/batch-ship.sh"}))
check("...and the segment split does not lose a verb from its own arguments",
      blocked("Bash", {"command":
              f"echo start && rm -rf {PROJ}/projects/video-production/render-qa/src "
              "&& echo done"}))
check("the fenced DIRECTORY is fenced, not only its contents — `rm -rf` on the "
      "gates directory itself named no trailing slash and went through",
      blocked("Bash", {"command": f"rm -rf {PROJ}/scripts"})
      and blocked("Bash", {"command": f"rm -rf {PROJ}/scripts/"})
      and blocked("Write", {"file_path": str(PROJ / "projects/video-production/render-qa/src")}))
check("...while a SIBLING whose name merely starts the same is not fenced",
      allowed("Bash", {"command": f"rm -rf {PROJ}/scripts-scratch/x"}))

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
print("== build claim distinguishes a new scaffold from an overwrite-safe resume ==")
checkpoint_ignore_probe = (
    "projects/video-production/renders-hyperframes/m2_ignore_probe/"
    "source-revisions/.blobs/"
    + "a" * 64
)
check("source checkpoint revisions and blobs stay out of version control",
      subprocess.run(
          ["git", "check-ignore", "-q", "--", checkpoint_ignore_probe],
          cwd=REPO, capture_output=True,
      ).returncode == 0,
      checkpoint_ignore_probe)
CLAIM_PROJ = Path(tempfile.mkdtemp(prefix="build-claim-checkpoint-test-"))


def copy_claim_dependency(source, relative):
    destination = CLAIM_PROJ / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


for source, relative in [
    (BUILD_CLAIM, "scripts/build-claim.sh"),
    (REPO / "scripts" / "build-session.sh", "scripts/build-session.sh"),
    (REPO / "scripts" / "build-log.sh", "scripts/build-log.sh"),
    (SOURCE_CHECKPOINT,
     "projects/video-production/render-qa/src/source_checkpoint.py"),
    (WORKSPACE_REVISION,
     "projects/video-production/render-qa/src/workspace_revision.py"),
    (RQ / "src" / "run_state.py",
     "projects/video-production/render-qa/src/run_state.py"),
    (RQ / "src" / "stem.py",
     "projects/video-production/render-qa/src/stem.py"),
]:
    copy_claim_dependency(source, relative)

claim_vp = CLAIM_PROJ / "projects/video-production"
claim_scaffold = claim_vp / "renders-hyperframes/_run/scaffold"
claim_scaffold.mkdir(parents=True)
(claim_scaffold / "assets/brand").mkdir(parents=True)
(claim_scaffold / "index.html").write_text("SCAFFOLD SENTINEL\n", encoding="utf-8")
(claim_scaffold / ".pin").write_text("pinned-runtime\n", encoding="utf-8")
(claim_scaffold / "assets/brand/logo.svg").write_text(
    "<svg><!-- scaffold logo --></svg>\n", encoding="utf-8")
(claim_vp / "lesson-scripts/mid-career-momentum").mkdir(parents=True)

claim_stem = "m2_checkpoint_demo"
claim_workspace = claim_vp / "renders-hyperframes" / claim_stem
run_file = claim_vp / "renders-hyperframes/_run/run.json"
run_file.write_text(json.dumps({
    "version": 4,
    "mode": "produce",
    "scope": {"kind": "stem", "value": claim_stem},
    "items": [{"stem": claim_stem, "program": "mid-career-momentum"}],
    "authoring_backend": "local",
    "dispatches": {},
    "approvals": {},
}), encoding="utf-8")


def run_claim(*extra, stem=claim_stem):
    return subprocess.run(
        ["bash", str(CLAIM_PROJ / "scripts/build-claim.sh"),
         stem, "mid-career-momentum", *extra],
        cwd=CLAIM_PROJ, capture_output=True, text=True,
        env=dict(os.environ, VIDEO_BUILD_SESSION_TTL="999999"))


def release_claim(stem=claim_stem):
    subprocess.run(
        ["bash", str(CLAIM_PROJ / "scripts/build-session.sh"),
         "release", stem],
        cwd=CLAIM_PROJ, capture_output=True, check=True,
    )


new_claim = run_claim()
check("NEW claim succeeds", new_claim.returncode == 0, new_claim.stderr)
check("NEW claim hydrates index.html from the scaffold itself",
      (claim_workspace / "index.html").read_text(encoding="utf-8")
      == "SCAFFOLD SENTINEL\n")
check("NEW claim hydrates hidden scaffold files and visual assets",
      (claim_workspace / ".pin").read_text(encoding="utf-8") == "pinned-runtime\n"
      and (claim_workspace / "assets/brand/logo.svg").is_file())
release_claim()

# Make the scaffold and workspace intentionally disagree. A resume that still
# runs the retired unconditional cp -a will destroy this authored sentinel.
(claim_scaffold / "index.html").write_text(
    "CHANGED SCAFFOLD — MUST NOT REPLACE AUTHORED SOURCE\n", encoding="utf-8")
authored_index = "AUTHORED INDEX — RECOVER THIS EXACT CUT\n"
(claim_workspace / "index.html").write_text(authored_index, encoding="utf-8")
(claim_workspace / "design.md").write_text("# Authored design\n", encoding="utf-8")
(claim_workspace / "assets/illustrations").mkdir(parents=True)
(claim_workspace / "assets/illustrations/route.svg").write_text(
    "<svg><!-- authored route --></svg>\n", encoding="utf-8")
(claim_workspace / "linked-illustrations").symlink_to(
    "assets/illustrations", target_is_directory=True)
(claim_workspace / "assets/voice").mkdir(parents=True)
voice_content = b"generated voice"
(claim_workspace / "assets/voice/narration.wav").write_bytes(voice_content)
(claim_workspace / "assets/voice/narration-copy.mp3").write_bytes(voice_content)
(claim_workspace / "qa").mkdir()
(claim_workspace / "qa/PREFLIGHT-OK").write_text("generated QA\n", encoding="utf-8")
(claim_workspace / "snapshots").mkdir()
(claim_workspace / "snapshots/frame.png").write_bytes(b"generated snapshot")
(claim_workspace / "node_modules/cache").mkdir(parents=True)
(claim_workspace / "node_modules/cache/module.js").write_text(
    "generated cache\n", encoding="utf-8")

unsafe_link_revision = subprocess.run(
    [sys.executable, str(WORKSPACE_REVISION), str(claim_workspace)],
    capture_output=True, text=True,
)
check("render-affecting symlinks are rejected instead of blessing mutable targets",
      unsafe_link_revision.returncode != 0
      and "symlink is not revision-safe" in unsafe_link_revision.stderr,
      unsafe_link_revision.stderr)
(claim_workspace / "linked-illustrations").unlink()

first_resume = run_claim("--resume")
check("RESUME succeeds", first_resume.returncode == 0, first_resume.stderr)
release_claim()
check("RESUME leaves the authored index sentinel byte-for-byte unchanged",
      (claim_workspace / "index.html").read_text(encoding="utf-8") == authored_index)

checkpoint_root = claim_workspace / "source-revisions"
checkpoints = sorted(path for path in checkpoint_root.iterdir()
                     if path.is_dir() and not path.name.startswith("."))
check("RESUME creates exactly one content-addressed source checkpoint",
      len(checkpoints) == 1, str(checkpoints))
checkpoint = checkpoints[0]
manifest_path = checkpoint / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest_files = {entry["path"] for entry in manifest["files"]}
check("checkpoint manifest binds workspace, revision, timestamp, and file list",
      manifest["workspace"] == claim_stem
      and manifest["revision"] == checkpoint.name
      and manifest.get("created_at", "").endswith("Z")
      and "index.html" in manifest_files)
check("checkpoint recovers authored HTML, design, and visual assets",
      (checkpoint / "index.html").read_text(encoding="utf-8") == authored_index
      and (checkpoint / "design.md").is_file()
      and (checkpoint / "assets/illustrations/route.svg").is_file())
check("unsafe symlink is absent from the recoverable checkpoint",
      "linked-illustrations" not in manifest_files
      and not (checkpoint / "linked-illustrations").exists())
voice_entries = [
    entry for entry in manifest["files"]
    if entry["path"].startswith("assets/voice/")
]
voice_sha = hashlib.sha256(voice_content).hexdigest()
voice_blob = checkpoint_root / ".blobs" / voice_sha
check("voice paths are recoverable through content-addressed manifest entries",
      len(voice_entries) == 2
      and all(entry["kind"] == "blob" for entry in voice_entries)
      and all(entry["sha256"] == voice_sha for entry in voice_entries)
      and all(entry["blob"] == f".blobs/{voice_sha}" for entry in voice_entries)
      and voice_blob.read_bytes() == voice_content)
check("identical voice content is stored once instead of copied per path",
      sorted(path.name for path in (checkpoint_root / ".blobs").iterdir())
      == [voice_sha]
      and not (checkpoint / "assets/voice/narration.wav").exists()
      and not (checkpoint / "assets/voice/narration-copy.mp3").exists())
check("checkpoint omits QA, snapshots, caches, and build logs",
      not (checkpoint / "qa").exists()
      and not (checkpoint / "snapshots").exists()
      and not (checkpoint / "node_modules").exists()
      and not (checkpoint / ".build-log.tsv").exists())

manifest_before = manifest_path.read_bytes()
manifest_mtime_before = manifest_path.stat().st_mtime_ns
voice_blob_mtime_before = voice_blob.stat().st_mtime_ns

# A reserved cloud record blocks a competing NEW workspace. A result becomes
# locally resumable only after the control plane records that it was merged.
cloud_owned_stem = "m2_cloud_owned"
run_file.write_text(json.dumps({
    "version": 4,
    "mode": "batch",
    "scope": {"kind": "program", "value": "mid-career-momentum"},
    "items": [
        {"stem": claim_stem, "program": "mid-career-momentum"},
        {"stem": cloud_owned_stem, "program": "mid-career-momentum"},
    ],
    "authoring_backend": "local",
    "dispatches": {
        cloud_owned_stem: {"state": "reserved"},
        claim_stem: {"state": "merged"},
    },
    "approvals": {},
}), encoding="utf-8")
cloud_claim = run_claim(stem=cloud_owned_stem)
check("NEW claim refuses a stem reserved for an external cloud task",
      cloud_claim.returncode != 0
      and not (claim_vp / "renders-hyperframes" / cloud_owned_stem).exists(),
      cloud_claim.stderr)
second_resume = run_claim("--resume")
check("RESUME stays available after a cloud result is recorded as merged",
      second_resume.returncode == 0, second_resume.stderr)
release_claim()
checkpoints_after = sorted(path for path in checkpoint_root.iterdir()
                           if path.is_dir() and not path.name.startswith("."))
check("repeated RESUME reuses the digest instead of duplicating a checkpoint",
      checkpoints_after == checkpoints, str(checkpoints_after))
check("repeated RESUME never overwrites the existing checkpoint manifest",
      manifest_path.read_bytes() == manifest_before
      and manifest_path.stat().st_mtime_ns == manifest_mtime_before)
check("repeated RESUME does not duplicate or rewrite the voice blob",
      sorted(path.name for path in (checkpoint_root / ".blobs").iterdir())
      == [voice_sha]
      and voice_blob.stat().st_mtime_ns == voice_blob_mtime_before)

replacement_voice = b"a meaningfully different rendition"
(claim_workspace / "assets/voice/narration.wav").write_bytes(replacement_voice)
revision_after_voice_change = subprocess.run(
    [sys.executable, str(WORKSPACE_REVISION), str(claim_workspace)],
    check=True, capture_output=True, text=True,
).stdout.strip()
check("changing only a voice binary changes the workspace revision",
      revision_after_voice_change != checkpoint.name)

changed_voice_resume = run_claim("--resume")
check("RESUME checkpoints the changed rendition instead of reusing the old cut",
      changed_voice_resume.returncode == 0, changed_voice_resume.stderr)
release_claim()
changed_checkpoint = checkpoint_root / revision_after_voice_change
changed_manifest = json.loads(
    (changed_checkpoint / "manifest.json").read_text(encoding="utf-8")
)
changed_voice_entry = next(
    entry for entry in changed_manifest["files"]
    if entry["path"] == "assets/voice/narration.wav"
)
replacement_sha = hashlib.sha256(replacement_voice).hexdigest()
replacement_blob = checkpoint_root / changed_voice_entry["blob"]
check("both old and changed voice renditions remain recoverable by content hash",
      changed_checkpoint.is_dir()
      and changed_voice_entry["sha256"] == replacement_sha
      and changed_voice_entry["blob"] == f".blobs/{replacement_sha}"
      and replacement_blob.read_bytes() == replacement_voice
      and voice_blob.read_bytes() == voice_content)
check("the changed checkpoint still retains authored source and visual assets",
      (changed_checkpoint / "index.html").read_text(encoding="utf-8")
      == authored_index
      and (changed_checkpoint / "design.md").is_file()
      and (changed_checkpoint / "assets/illustrations/route.svg").is_file())

changed_manifest_path = changed_checkpoint / "manifest.json"
changed_manifest_bytes = changed_manifest_path.read_bytes()
changed_manifest_path.write_text("{}\n", encoding="utf-8")
corrupt_manifest_resume = run_claim("--resume")
check("RESUME rejects an existing checkpoint with a corrupted manifest",
      corrupt_manifest_resume.returncode != 0,
      corrupt_manifest_resume.stderr)
changed_manifest_path.write_bytes(changed_manifest_bytes)

recovery_visual = changed_checkpoint / "assets/illustrations/route.svg"
recovery_visual_bytes = recovery_visual.read_bytes()
recovery_visual.write_bytes(b"corrupted recovery visual")
corrupt_file_resume = run_claim("--resume")
check("RESUME rejects a copied checkpoint file whose hash no longer matches",
      corrupt_file_resume.returncode != 0,
      corrupt_file_resume.stderr)
recovery_visual.write_bytes(recovery_visual_bytes)

replacement_blob.write_bytes(b"corrupted voice blob")
corrupt_blob_resume = run_claim("--resume")
check("RESUME rejects a voice blob whose content-address no longer matches",
      corrupt_blob_resume.returncode != 0,
      corrupt_blob_resume.stderr)
replacement_blob.write_bytes(replacement_voice)
check("RESUME succeeds again after all immutable recovery bytes are restored",
      run_claim("--resume").returncode == 0)

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
shutil.rmtree(CLAIM_PROJ, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
