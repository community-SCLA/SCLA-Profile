#!/usr/bin/env python3
"""Regression tests for the lean SCLA video control plane."""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
VP = RQ.parent
REPO = VP.parents[1]
SRC = RQ / "src"
RUN = VP / "run.sh"
STATE_TOOL = SRC / "run_state.py"
sys.path.insert(0, str(SRC))
from preflight import check_audio_contract, check_workspace_sources  # noqa: E402
from tokens import load as load_tokens  # noqa: E402
from continuous_audio import prepare as prepare_continuous  # noqa: E402
from continuous_audio import split as split_continuous  # noqa: E402
from workspace_revision import workspace_revision  # noqa: E402

PASS = FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def run(command, *, env=None):
    return subprocess.run(command, capture_output=True, text=True, env=env)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


print("== source graph and route budgets ==")
agent_sources = [REPO / "AGENTS.md", REPO / "CLAUDE.md"]
agent_sources += [p for p in (REPO / ".claude").rglob("*.md")
                  if "_archive" not in p.parts]
for path in VP.rglob("AGENTS.md"):
    if "_archive" not in path.parts:
        agent_sources.append(path)
for path in VP.rglob("CLAUDE.md"):
    if "_archive" not in path.parts:
        agent_sources.append(path)
agent_sources += list((VP / "contracts").glob("*.md"))
hits = [str(p.relative_to(REPO)) for p in set(agent_sources)
        if "README" in p.read_text(encoding="utf-8", errors="replace")]
check("no agent source routes to a human overview", not hits, hits)

orch = [REPO / "AGENTS.md", VP / "CLAUDE.md",
        REPO / ".claude/rules/video-production.md",
        REPO / ".claude/skills/render-lessons/SKILL.md"]
builder = [REPO / "AGENTS.md", VP / "CLAUDE.md",
           REPO / ".claude/rules/video-production.md", VP / "contracts/builder.md"]
words = lambda paths: sum(len(p.read_text().split()) for p in paths)
check("orchestrator fixed route <= 2500 words", words(orch) <= 2500, words(orch))
check("builder fixed route <= 3000 words", words(builder) <= 3000, words(builder))
kit = (VP / "contracts/builder.md").read_text()
prepare = (REPO / "scripts/batch-prepare.sh").read_text()
render_skill = (REPO / ".claude/skills/render-lessons/SKILL.md").read_text()
cloud_dispatch = (REPO / "scripts/cloud-dispatch.sh").read_text()
check("generated kit source has no extraction-marker residue",
      "BUILD-KIT:BEGIN" not in kit and "BUILD-KIT:END" not in kit)
check("build kit is copied from one tracked contract",
      'cp "$CONTRACT" "$RUN/BUILD-KIT.md"' in prepare)
check("AUTO-BATCH owns stem selection and parallel scheduling",
      "Never ask" in render_skill and "user to choose, copy, or paste stems" in render_skill and
      "parallel in-session subagents" in render_skill and
      "`--cloud` uses Cloud tasks" in render_skill and
      "Return each passing lesson immediately" in render_skill and
      "must not be redelegated" in render_skill and
      "approve STEM" in render_skill and
      "run.sh drain" in render_skill and
      "run.sh dispatch-merged --stem STEM" in render_skill)
check("Cloud dispatch submits instead of merely printing",
      "CODEX_CLOUD_BIN:-codex" in cloud_dispatch and
      "cloud exec --env" in cloud_dispatch and
      "Cloud inputs before dispatch" in cloud_dispatch and
      "Unrelated dirty lesson workspaces do not block" in cloud_dispatch and
      '[[ "$LOCAL_HEAD" == "$UPSTREAM_HEAD" ]]' in cloud_dispatch)
audio_wrapper = (REPO / "scripts/video-audio.sh").read_text()
check("TTS failures use bounded retries and durable receipts",
      'VIDEO_TTS_RETRIES:-2' in audio_wrapper and
      '--error-class tts' in audio_wrapper and 'record-failure' in audio_wrapper)


print("== explicit scope and persistent approval ==")
tmp = Path(tempfile.mkdtemp(prefix="video-control-test-"))
test_vp = tmp / "video-production"
for stage in ("inbox", "ready", "published"):
    (test_vp / "lesson-scripts" / "prog-a" / stage).mkdir(parents=True)
(test_vp / "renders-hyperframes").mkdir(parents=True)
(test_vp / "render-qa").mkdir(parents=True)
(test_vp / "lesson-scripts" / "published.tsv").write_text(
    "# base\tprogram\trender_date\twistia_url\n")
(test_vp / "render-qa" / "quarantine.log").write_text("")
a = test_vp / "lesson-scripts/prog-a/ready/lesson-a_prog-a.txt"
b = test_vp / "lesson-scripts/prog-a/ready/lesson-b_prog-a.txt"
c = test_vp / "lesson-scripts/prog-a/ready/lesson-c_prog-a.txt"
a.write_text("Lesson A.")
b.write_text("Lesson B.")
c.write_text("Lesson C.")
b_before = (digest(b), b.stat().st_mtime_ns)
state_file = test_vp / "renders-hyperframes/_run/run.json"
env = dict(os.environ, VIDEO_VP_ROOT=str(test_vp), VIDEO_REPO_ROOT=str(REPO),
           VIDEO_RUN_STATE=str(state_file), VIDEO_RUN_STATE_TOOL=str(STATE_TOOL),
           VIDEO_PRIORITY="prog-a")
r = run(["bash", str(RUN), "produce", "--stem", "lesson-a_prog-a"], env=env)
state = json.loads(state_file.read_text())
check("named production selects exactly one stem", r.returncode == 0 and
      state["items"] == [{"stem": "lesson-a_prog-a", "program": "prog-a"}],
      state["items"])
legacy_shape = json.loads(state_file.read_text())
legacy_shape["version"] = 3
legacy_shape["items"][0]["stage"] = "ready"
state_file.write_text(json.dumps(legacy_shape))
r = run(["bash", str(RUN), "migrate-state"], env=env)
migrated_shape = json.loads(state_file.read_text())
check("v3 selection labels migrate in place to identity-only v4 state",
      r.returncode == 0 and migrated_shape["version"] == 4 and
      migrated_shape["items"] ==
      [{"stem": "lesson-a_prog-a", "program": "prog-a"}],
      migrated_shape)
check("named production does not touch unrelated queue entries",
      b_before == (digest(b), b.stat().st_mtime_ns) and not
      (test_vp / "renders-hyperframes/lesson-b_prog-a").exists())
r = run(["bash", str(RUN), "delegate", "--stem", "lesson-b_prog-a"], env=env)
check("cloud delegation cannot escape the active run scope",
      r.returncode != 0 and "outside the active run" in r.stderr, r.stderr)
before_bad_batch = state_file.read_bytes()
r = run(["bash", str(RUN), "batch"], env=env)
check("batch requires explicit program or all scope",
      r.returncode == 2 and state_file.read_bytes() == before_bad_batch)
r = run(["bash", str(RUN), "batch", "--program", "prog-a"], env=env)
state = json.loads(state_file.read_text())
check("explicit rolling batch replaces an unfinished named scope", r.returncode == 0 and
      {x["stem"] for x in state["items"]} ==
      {"lesson-a_prog-a", "lesson-b_prog-a", "lesson-c_prog-a"})
check("normal batch keeps local source authoring",
      state["authoring_backend"] == "local" and
      state["authoring_concurrency"] == 3, state)
outside = run([sys.executable, str(STATE_TOOL), "can-claim",
               "not-selected_prog-a"], env=env)
check("local claims cannot escape explicit selection",
      outside.returncode != 0 and "outside the active run" in outside.stderr,
      outside.stderr)
claim_stem = "claim-race_prog-a"
(test_vp / f"lesson-scripts/prog-a/ready/{claim_stem}.txt").write_text("Claim race.")
r = run(["bash", str(RUN), "batch", "--program", "prog-a"], env=env)
claimers = [subprocess.Popen(
    [sys.executable, str(STATE_TOOL), "claim-local", claim_stem,
     "--program", "prog-a"], env=env, stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL) for _ in range(2)]
claim_results = [proc.wait() for proc in claimers]
check("parallel local workspace claims have exactly one winner",
      sorted(claim_results) == [0, 1] and
      (test_vp / f"renders-hyperframes/{claim_stem}").is_dir(), claim_results)
shutil.rmtree(test_vp / f"renders-hyperframes/{claim_stem}")
(test_vp / f"lesson-scripts/prog-a/ready/{claim_stem}.txt").unlink()
r = run(["bash", str(RUN), "batch", "--program", "prog-a", "--cloud"], env=env)
cloud_state = json.loads(state_file.read_text())
check("cloud batch records isolated Codex Cloud authoring",
      r.returncode == 0 and cloud_state["authoring_backend"] == "cloud" and
      cloud_state["authoring_concurrency"] == 6, cloud_state)
cloud_local_claim = run([sys.executable, str(STATE_TOOL), "can-claim",
                         "lesson-a_prog-a"], env=env)
check("Cloud-selected authoring cannot race a local NEW claim",
      cloud_local_claim.returncode != 0 and
      "selection uses Cloud authoring" in cloud_local_claim.stderr,
      cloud_local_claim.stderr)
state_file.write_text(json.dumps(state))
selected_state = state
empty_state = dict(state)
empty_state["items"] = []
state_file.write_text(json.dumps(empty_state))
r = run(["bash", str(RUN), "approve", "BATCH"], env=env)
check("an empty batch cannot receive review approval",
      r.returncode != 0 and "no selected workspaces" in r.stderr, r.stderr)
state_file.write_text(json.dumps(selected_state))
r = run(["bash", str(RUN), "batch", "--program", "prog-a", "--cloud"], env=env)
check("Cloud dispatch uses an explicitly selected Cloud batch", r.returncode == 0,
      r.stderr)
r = run(["bash", str(RUN), "delegate", "--stem", "lesson-a_prog-a"], env=env)
check("selected stems get an exact source-only cloud prompt",
      r.returncode == 0 and
      "bash scripts/cloud-author.sh lesson-a_prog-a prog-a" in r.stdout and
      "bash scripts/cloud-review-ready.sh lesson-a_prog-a" in r.stdout and
      "REVIEW_READY: PASS" in r.stdout and
      "Do not call HeyGen" in r.stdout, r.stderr + r.stdout)
fake_codex = tmp / "fake-codex"
fake_log = tmp / "fake-codex.log"
fake_codex.write_text(
    "#!/usr/bin/env bash\n"
    "printf '%s\\n' \"$@\"\n"
    "printf 'CWD=%s\\n' \"$PWD\"\n"
    "printf diagnostic > error.log\n"
    "sleep 0.2\n"
    "printf 'CALL\\n' >> \"$FAKE_CODEX_LOG\"\n")
fake_codex.chmod(0o755)
repo_error_log_before = digest(REPO / "error.log")
dispatch_env = dict(env, CODEX_CLOUD_BIN=str(fake_codex),
                    CODEX_CLOUD_ALLOW_DIRTY="1", FAKE_CODEX_LOG=str(fake_log))
r = run(["bash", str(RUN), "dispatch", "--stem", "lesson-a_prog-a"],
        env=dispatch_env)
check("dispatch submits the generated assignment through codex cloud exec",
      r.returncode == 0 and "cloud\nexec\n--env\n6a74d3f8935c819189b90cf480d14dfe" in r.stdout and
      "Work only on lesson-a_prog-a" in r.stdout and
      f"CWD={REPO}" not in r.stdout and digest(REPO / "error.log") == repo_error_log_before,
      r.stderr + r.stdout)
first_dispatch = json.loads(state_file.read_text())["dispatches"]["lesson-a_prog-a"]
r_duplicate = run(["bash", str(RUN), "dispatch", "--stem", "lesson-a_prog-a"],
                  env=dispatch_env)
check("a submitted Cloud lesson cannot be dispatched twice",
      r_duplicate.returncode != 0 and "duplicate task" in r_duplicate.stderr and
      fake_log.read_text().count("CALL") == 1 and first_dispatch["state"] == "submitted",
      r_duplicate.stderr)
check("a pending Cloud task blocks a competing local claim",
      run([sys.executable, str(STATE_TOOL), "can-claim", "lesson-a_prog-a"],
          env=env).returncode != 0)
(test_vp / "renders-hyperframes/lesson-b_prog-a").mkdir()
r = run(["bash", str(RUN), "batch", "--program", "prog-a", "--cloud"], env=env)
workspace_item = next(x for x in json.loads(state_file.read_text())["items"]
                      if x["stem"] == "lesson-b_prog-a")
check("selection stores identity, not a stale lifecycle label",
      r.returncode == 0 and workspace_item ==
      {"stem": "lesson-b_prog-a", "program": "prog-a"},
      workspace_item)
r = run([sys.executable, str(STATE_TOOL), "locate", "lesson-b_prog-a"], env=env)
located_workspace = json.loads(r.stdout)
check("locate keeps the source program while surfacing an existing workspace",
      located_workspace["stage"] == "workspace" and
      located_workspace["program"] == "prog-a", located_workspace)
r = run(["bash", str(RUN), "delegate", "--stem", "lesson-b_prog-a"], env=env)
check("existing workspaces resume locally instead of duplicate Cloud delegation",
      r.returncode != 0 and "resume it locally" in r.stderr, r.stderr)
drains = [subprocess.Popen(
    ["bash", str(RUN), "drain"], env=dispatch_env,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
drain_results = [proc.communicate() + (proc.returncode,) for proc in drains]
r_again = run(["bash", str(RUN), "drain"], env=dispatch_env)
dispatches = json.loads(state_file.read_text())["dispatches"]
check("concurrent Cloud drains converge on one task per READY lesson",
      all(result[2] == 0 for result in drain_results) and
      r_again.returncode == 0 and
      dispatches["lesson-c_prog-a"]["state"] == "submitted" and
      fake_log.read_text().count("CALL") == 2 and
      "no untouched" in r_again.stdout,
      drain_results + [(r_again.stdout, r_again.stderr, r_again.returncode)])
for stage in ("inbox", "ready", "published"):
    (test_vp / "lesson-scripts" / "prog-b" / stage).mkdir(parents=True)
(test_vp / "lesson-scripts/prog-b/ready/lesson-d_prog-b.txt").write_text("D")
run(["bash", str(RUN), "batch", "--program", "prog-b", "--cloud"], env=env)
cross_scope = json.loads(state_file.read_text())
cross_scope["authoring_concurrency"] = 3
cross_scope["dispatches"]["orphan_prog-old"] = {
    "state": "reserved", "program": "prog-old",
    "reserved_at": "2020-01-01T00:00:00Z", "reservation_id": "old",
}
state_file.write_text(json.dumps(cross_scope))
global_view = run([sys.executable, str(STATE_TOOL), "dispatchable"], env=env)
global_dispatch = json.loads(global_view.stdout)
check("dispatch capacity counts durable active work outside the new scope",
      global_view.returncode == 0 and global_dispatch["active"] == 3 and
      global_dispatch["available"] == 0 and global_dispatch["items"] == [],
      global_dispatch)
check("stale reservations surface as a safety hold without blind resubmit",
      any(x["stem"] == "orphan_prog-old" and
          x["condition"] == "stale-reservation"
          for x in global_dispatch["blocked"]), global_dispatch)
cross_scope["dispatches"].pop("orphan_prog-old")
state_file.write_text(json.dumps(cross_scope))
run(["bash", str(RUN), "batch", "--program", "prog-a", "--cloud"], env=env)
check("new runs separate authoring, TTS, render, and publish capacity",
      state["authoring_concurrency"] == 3 and state["tts_concurrency"] == 2 and
      state["cloud_render_concurrency"] == 2 and state["publish_concurrency"] == 1,
      state)


def make_reviewable(stem):
    workspace = test_vp / "renders-hyperframes" / stem
    (workspace / "qa").mkdir(parents=True, exist_ok=True)
    (workspace / "index.html").write_text(
        '<main data-duration="1"><div class="clip" data-start="0"></div></main>')
    revision = workspace_revision(workspace)
    (workspace / "qa/PREFLIGHT-OK").write_text(
        json.dumps({"source_revision": revision}))
    verdict = run([sys.executable, str(STATE_TOOL), "record-visual-review", stem,
                   "--blocking-defect", "PASS", "--taste", "ALIVE",
                   "--recommendation", "PROCEED"], env=env)
    return workspace, revision, verdict


lesson_a_ws, lesson_a_revision, visual_a = make_reviewable("lesson-a_prog-a")
check("the visual-review receipt is validated and revision-bound",
      visual_a.returncode == 0 and
      json.loads((lesson_a_ws / "qa/VISUAL-REVIEW.json").read_text())["revision"] ==
      lesson_a_revision, visual_a.stderr)
pending_resume = run([sys.executable, str(STATE_TOOL), "can-resume",
                      "lesson-a_prog-a", "--program", "prog-a"], env=env)
merged_handoff = run(["bash", str(RUN), "dispatch-merged", "--stem",
                      "lesson-a_prog-a", "--task-ref", "task://lesson-a"], env=env)
safe_resume = run([sys.executable, str(STATE_TOOL), "can-resume",
                   "lesson-a_prog-a", "--program", "prog-a"], env=env)
check("submitted Cloud ownership blocks resume until an explicit merged handoff",
      pending_resume.returncode != 0 and "externally owned" in pending_resume.stderr and
      merged_handoff.returncode == 0 and safe_resume.returncode == 0 and
      json.loads(state_file.read_text())["dispatches"]["lesson-a_prog-a"]["state"] ==
      "merged", pending_resume.stderr + merged_handoff.stderr + safe_resume.stderr)
bad_visual = run([sys.executable, str(STATE_TOOL), "record-visual-review",
                  "lesson-a_prog-a", "--blocking-defect", "PASS",
                  "--taste", "FLAT", "--recommendation", "PROCEED"], env=env)
check("a FLAT visual review cannot recommend PROCEED",
      bad_visual.returncode != 0 and "must recommend REVISE" in bad_visual.stderr,
      bad_visual.stderr)
r = run([sys.executable, str(STATE_TOOL), "can-ship", "lesson-a_prog-a"], env=env)
check("batch shipping is blocked before that lesson's rolling approval",
      r.returncode != 0 and "review approval" in r.stderr, r.stderr)
state = json.loads(state_file.read_text())
state["cloud_clean_streak"] = 3
state_file.write_text(json.dumps(state))
r = run(["bash", str(RUN), "cloud-limit", "4"], env=env)
check("clean cloud streak scales independently of unfinished siblings",
      r.returncode == 0, r.stderr)
state = json.loads(state_file.read_text())
state["cloud_clean_streak"] = 0
state_file.write_text(json.dumps(state))
r = run(["bash", str(RUN), "approve", "lesson-a_prog-a"], env=env)
approved_one = json.loads(state_file.read_text())["review"]
r_a = run([sys.executable, str(STATE_TOOL), "can-ship", "lesson-a_prog-a"], env=env)
r_b = run([sys.executable, str(STATE_TOOL), "can-ship", "lesson-b_prog-a"], env=env)
check("one clean batch lesson can be approved and shipped independently",
      r.returncode == 0 and approved_one["stems"] == ["lesson-a_prog-a"] and
      r_a.returncode == 0 and r_b.returncode != 0, r.stderr + r_b.stderr)
r = run(["bash", str(RUN), "produce", "--stem", "lesson-b_prog-a"], env=env)
r = run(["bash", str(RUN), "batch", "--program", "prog-a"], env=env)
cross_scope_approval = json.loads(state_file.read_text())["approvals"]
check("per-lesson approval survives selecting another scope and returning",
      r.returncode == 0 and
      cross_scope_approval["lesson-a_prog-a"]["revision"] == lesson_a_revision,
      cross_scope_approval)
r = run(["bash", str(RUN), "batch", "--program", "prog-a"], env=env)
reselected_review = json.loads(state_file.read_text())["review"]
check("reselecting a batch preserves rolling lesson approvals",
      r.returncode == 0 and reselected_review == approved_one,
      reselected_review)
r = run(["bash", str(RUN), "approve", "BATCH"], env=env)
check("batch approval refuses a partial review set",
      r.returncode != 0 and "lesson-b_prog-a" in r.stderr, r.stderr)
make_reviewable("lesson-b_prog-a")
make_reviewable("lesson-c_prog-a")
r = run(["bash", str(RUN), "approve", "BATCH"], env=env)
approved = json.loads(state_file.read_text())["review"]
r3 = run([sys.executable, str(STATE_TOOL), "can-ship", "lesson-a_prog-a"], env=env)
r2 = run(["bash", str(RUN), "resume"], env=env)
check("optional full-batch approval persists across sessions", r.returncode == 0 and
      approved["approved_at"] and set(approved["stems"]) ==
      {"lesson-a_prog-a", "lesson-b_prog-a", "lesson-c_prog-a"} and
      json.loads(state_file.read_text())["review"] == approved and
      approved["approved_at"] in r2.stdout and r3.returncode == 0)
legacy = json.loads(state_file.read_text())
legacy.pop("approvals")
state_file.write_text(json.dumps(legacy))
r = run(["bash", str(RUN), "batch", "--program", "prog-a"], env=env)
migrated = json.loads(state_file.read_text())["approvals"]
legacy_ship = run([sys.executable, str(STATE_TOOL), "can-ship",
                   "lesson-a_prog-a"], env=env)
check("stem-only legacy review stays unbound and requires fresh approval",
      r.returncode == 0 and
      migrated["lesson-a_prog-a"]["revision"] is None and
      migrated["lesson-a_prog-a"]["source"] == "legacy-review-unbound" and
      legacy_ship.returncode != 0 and "current revision" in legacy_ship.stderr,
      migrated)
lesson_a_ws.joinpath("index.html").write_text("<main>changed after approval</main>")
r = run([sys.executable, str(STATE_TOOL), "can-ship", "lesson-a_prog-a"], env=env)
check("editing an approved workspace invalidates its shipping approval",
      r.returncode != 0 and "current revision" in r.stderr, r.stderr)
r = run(["bash", str(RUN), "resume", "--json"], env=env)
merged_resume = json.loads(r.stdout)
merged_a = next(x for x in merged_resume["selection"]
                if x["stem"] == "lesson-a_prog-a")
check("resume --json returns one selected view with live, approval, and dispatch state",
      r.returncode == 0 and merged_a["observed"] and merged_a["approval"] and
      merged_a["dispatch"], merged_resume)


print("== durable failures, retry limits, and circuit breaker ==")
for stem in ("lesson-a_prog-a", "lesson-b_prog-a"):
    (test_vp / "renders-hyperframes" / stem / "qa/logs").mkdir(parents=True)
log = test_vp / "renders-hyperframes/lesson-a_prog-a/qa/logs/cloud.log"
log.write_text("provider output: credential rejected\n")


def failure(stem, error="cloud-render"):
    ws = test_vp / "renders-hyperframes" / stem
    return run([sys.executable, str(STATE_TOOL), "record-failure",
                "--workspace", str(ws), "--stem", stem, "--program", "prog-a",
                "--error-class", error, "--reason", "cloud command failed",
                "--command", "hyperframes cloud render", "--exit-code", "1",
                "--log", str(log),
                "--next-action", "fix cloud credentials, then authorize retry"], env=env)


failure("lesson-a_prog-a")
failure("lesson-a_prog-a")
receipt_path = test_vp / "renders-hyperframes/lesson-a_prog-a/qa/failure.json"
receipt = json.loads(receipt_path.read_text())
check("failed command output and recovery survive the session",
      receipt["attempt"] == 2 and receipt["command"] == "hyperframes cloud render" and
      receipt["exit_code"] == 1 and
      receipt["log"] == str(log) and "credential rejected" in log.read_text() and
      "authorize retry" in receipt["next_action"], receipt)
r = run([sys.executable, str(STATE_TOOL), "can-attempt",
         str(test_vp / "renders-hyperframes/lesson-a_prog-a")], env=env)
check("a third same-stem attempt is refused",
      r.returncode == 3 and "RETRY_EXHAUSTED" in r.stdout, r.stdout)

with (test_vp / "render-qa/quarantine.log").open("a") as handle:
    handle.write("2026-08-05T00:00:00Z\tlesson-a_prog-a\tprog-a\tcloud command failed\n")
r = run(["bash", str(REPO / "scripts/batch-status.sh"), "--json"], env=env)
doc = json.loads(r.stdout)
entry = next(x for p in doc["programs"] for x in p["in_flight"]
             if x["stem"] == "lesson-a_prog-a")
check("status reports the recorded recovery, not an unrelated verifier",
      "fix cloud credentials" in entry["next"] and "verify_render.py" not in entry["next"], entry)

failure("lesson-b_prog-a")
state = json.loads(state_file.read_text())
check("two consecutive videos with one error class open the circuit",
      state["circuit_breaker"]["open"] and
      state["circuit_breaker"]["stems"] == ["lesson-a_prog-a", "lesson-b_prog-a"],
      state["circuit_breaker"])
check("driver owns one concise close-out record",
      state["last_closeout"]["stem"] == "lesson-b_prog-a" and
      state["results"]["lesson-b_prog-a"]["status"] == "failed")
r = run(["bash", str(RUN), "cloud-limit", "4"], env=env)
check("four cloud renders are refused before a clean streak",
      r.returncode != 0 and "three consecutive" in r.stderr, r.stderr)


def make_verified_cut(stem):
    clean_ws = test_vp / "renders-hyperframes" / stem
    (clean_ws / "qa").mkdir(parents=True, exist_ok=True)
    (clean_ws / "renders").mkdir(exist_ok=True)
    (clean_ws / "index.html").write_text(f"<main>{stem}</main>")
    revision = workspace_revision(clean_ws)
    mp4 = clean_ws / "renders" / f"{stem}.mp4"
    mp4.write_bytes(f"encoded {stem}".encode())
    mp4_digest = digest(mp4)
    (clean_ws / "qa/RENDER-START.json").write_text(json.dumps({
        "source_revision": revision,
        "backend": "cloud",
        "attempt": 1,
        "mp4": str(mp4),
        "encode_review_required": True,
        "completed_at": "2026-08-07T00:00:00Z",
        "completed_sha256": mp4_digest,
        "completed_bytes": mp4.stat().st_size,
    }))
    (clean_ws / "qa/VERIFIED").write_text(json.dumps({
        "source_revision": revision,
        "mp4": str(mp4),
        "sha256": mp4_digest,
        "encode_review_required": True,
        "render_attempt": 1,
    }))
    return clean_ws


backend_mismatch_ws = make_verified_cut("backend-mismatch_prog-a")
backend_mismatch = run([
    sys.executable, str(STATE_TOOL), "record-encode-review",
    "backend-mismatch_prog-a", "--backend", "local", "--verdict", "PASS",
], env=env)
check("encode review cannot relabel a cloud render as local",
      backend_mismatch.returncode != 0
      and "rendered by cloud" in backend_mismatch.stderr
      and not (backend_mismatch_ws / "qa/ENCODE-REVIEW.json").exists(),
      backend_mismatch.stdout + backend_mismatch.stderr)

for clean_stem in ("clean-one_prog-a", "clean-two_prog-a", "clean-three_prog-a"):
    clean_ws = make_verified_cut(clean_stem)
    run([sys.executable, str(STATE_TOOL), "record-success", "--workspace",
         str(clean_ws), "--stem", clean_stem, "--phase", "cloud-render"], env=env)
state = json.loads(state_file.read_text())
check("deterministic render success alone does not count as encode-reviewed",
      state["cloud_clean_streak"] == 0, state)
for clean_stem in ("clean-one_prog-a", "clean-two_prog-a", "clean-three_prog-a"):
    run([sys.executable, str(STATE_TOOL), "record-encode-review", clean_stem,
         "--backend", "cloud", "--verdict", "PASS"], env=env)
r = run([sys.executable, str(STATE_TOOL), "post-review-required"], env=env)
check("post-render review retires only after three clean cloud renders",
      r.returncode == 1 and "retired" in r.stdout, r.stdout)
r = run(["bash", str(RUN), "cloud-limit", "4"], env=env)
limits = run(["bash", str(RUN), "limits"], env=env)
check("three clean cloud renders unlock capacity four",
      r.returncode == 0 and json.loads(limits.stdout)["cloud_render"] == 4,
      r.stderr + limits.stdout + limits.stderr)
parallel_stems = [f"parallel-{i}_prog-a" for i in range(6)]
parallel = []
for stem in parallel_stems:
    ws = make_verified_cut(stem)
    parallel.append(subprocess.Popen(
        [sys.executable, str(STATE_TOOL), "record-success", "--workspace",
         str(ws), "--stem", stem, "--phase", "cloud-render"], env=env))
parallel_ok = all(proc.wait() == 0 for proc in parallel)
parallel = [subprocess.Popen(
    [sys.executable, str(STATE_TOOL), "record-encode-review", stem,
     "--backend", "cloud", "--verdict", "PASS"], env=env,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for stem in parallel_stems]
parallel_ok = parallel_ok and all(proc.wait() == 0 for proc in parallel)
state = json.loads(state_file.read_text())
check("parallel reviewed render completions cannot overwrite run-state updates",
      parallel_ok and all(stem in state["results"] for stem in parallel_stems) and
      state["cloud_clean_streak"] == 3, state)
failure("lesson-a_prog-a")
state = json.loads(state_file.read_text())
check("a cloud-render failure automatically returns capacity to two",
      state["cloud_render_concurrency"] == 2 and
      state["cloud_clean_streak"] == 0, state)


print("== exclusive per-stem leases ==")
lease_repo = Path(tempfile.mkdtemp(prefix="video-lease-test-"))
(lease_repo / "scripts").mkdir()
shutil.copy2(REPO / "scripts/build-session.sh", lease_repo / "scripts/build-session.sh")
lease_cmd = ["bash", str(lease_repo / "scripts/build-session.sh")]
owners = [subprocess.Popen(lease_cmd + ["arm", "a"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) for _ in range(2)]
owner_results = [proc.wait() for proc in owners]
check("parallel same-stem lease arms have exactly one owner",
      sorted(owner_results) == [0, 1], owner_results)
live_retry = run(lease_cmd + ["arm", "a"])
check("a live lease refuses a second resume worker",
      live_retry.returncode == 1 and "live build owner" in live_retry.stderr,
      live_retry.stderr)
run(lease_cmd + ["arm", "b"])
lease_dir = lease_repo / "projects/video-production/renders-hyperframes/.build-in-progress"
check("different stems retain independent parallel leases",
      sorted(p.name for p in lease_dir.iterdir()) == ["a", "b"])
old = time.time() - 2
os.utime(lease_dir / "a", (old, old))
resume_env = dict(os.environ, VIDEO_BUILD_SESSION_TTL="21600",
                  VIDEO_BUILD_RESUME_TAKEOVER_AGE="1")
resumers = [subprocess.Popen(lease_cmd + ["arm", "a", "--resume"],
                             env=resume_env, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True) for _ in range(2)]
resume_results = [proc.communicate() + (proc.returncode,) for proc in resumers]
check("a stalled resume lease has one takeover winner, not a six-hour deadlock",
      sorted(x[2] for x in resume_results) == [0, 1] and
      any("resuming stalled" in x[1] for x in resume_results), resume_results)
run(lease_cmd + ["release", "a"])
check("releasing one stem preserves the parallel holder",
      [p.name for p in lease_dir.iterdir()] == ["b"] and
      run(lease_cmd + ["status"]).returncode == 0)
run(lease_cmd + ["release", "b"])
check("all leases fully release", not lease_dir.exists())
check("an unscoped release is refused", run(lease_cmd + ["release"]).returncode == 2)


print("== pinned audio and shared timing ==")
audio_ws = Path(tempfile.mkdtemp(prefix="video-audio-test-"))
(audio_ws / "assets/voice").mkdir(parents=True)
shutil.copy2(VP / "design-system/config/tokens.yml", audio_ws / "tokens.yml")
(audio_ws / ".scla-control-v2").write_text("")
voice_id = "442360a3e0894fbd85024ff64cc2b928"
request = {"provider": "heygen", "voice": voice_id, "speed": 1.0,
           "lines": [{"id": "b01", "text": "First idea."},
                     {"id": "beat-any", "text": "Second idea."}]}
(audio_ws / "audio_request.json").write_text(json.dumps(request))


def make_wav(path, seconds=0.9, rate=24000):
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        frames = b"".join(struct.pack("<h", int(7000 * math.sin(i / 17)))
                          for i in range(int(seconds * rate)))
        handle.writeframes(frames)


provider_request_path = audio_ws / "provider_request.json"
provider_request = prepare_continuous(audio_ws, provider_request_path, 4800)
make_wav(audio_ws / "assets/voice/narration.wav", seconds=2.0)
provider_meta = {
    "tts_provider": "heygen", "voice_id": voice_id, "speed": 1.0,
    "voices": [{
        "id": "narration", "path": "assets/voice/narration.wav",
        "duration_s": 2.0,
        "words": [
            {"text": "First", "start": 0.10, "end": 0.30},
            {"text": "idea.", "start": 0.35, "end": 0.60},
            {"text": "Second", "start": 1.00, "end": 1.20},
            {"text": "idea.", "start": 1.25, "end": 1.55},
        ],
    }],
    "total_duration_s": 2.0,
}
provider_meta_path = audio_ws / "provider_meta.json"
provider_meta_path.write_text(json.dumps(provider_meta))
meta = split_continuous(audio_ws, provider_meta_path, 4800)
check("one normal lesson becomes one provider request and local beat clips",
      len(provider_request["lines"]) == 1 and
      meta["scla_synthesis"]["provider_requests"] == 1 and
      [x["id"] for x in meta["voices"]] == ["b01", "beat-any"] and
      all((audio_ws / x["path"]).is_file() for x in meta["voices"]), meta)
sec = check_audio_contract(audio_ws, static=False)
check("actual provider, voice, speed, and arbitrary clip paths match tokens",
      sec["pass"], sec["output"])
request["speed"] = 0.9
(audio_ws / "audio_request.json").write_text(json.dumps(request))
sec = check_audio_contract(audio_ws, static=False)
check("provider/voice/speed drift fails preflight", not sec["pass"] and
      "speed" in sec["output"], sec["output"])
request["speed"] = 1.0
(audio_ws / "audio_request.json").write_text(json.dumps(request))

r = run([sys.executable, str(SRC / "plan_timing.py"), str(audio_ws)])
first = {name: digest(audio_ws / name) for name in
         ("audio_meta.json", "timing.json", "assets/voice/b01.wav",
          "assets/voice/beat-any.wav")}
r2 = run([sys.executable, str(SRC / "plan_timing.py"), str(audio_ws)])
second = {name: digest(audio_ws / name) for name in first}
timing = json.loads((audio_ws / "timing.json").read_text())
rows = timing["rows"]
gap = rows[1]["audio_start"] - (rows[0]["audio_start"] + rows[0]["audio_dur"])
tail = timing["total"] - (rows[-1]["audio_start"] + rows[-1]["audio_dur"])
check("shared timing accepts arbitrary beat ids",
      r.returncode == 0 and [x["id"] for x in rows] == ["b01", "beat-any"],
      r.stderr)
check("shared timing uses the single configured gap and final hold",
      abs(gap - 0.65) < 0.002 and abs(tail - 1.80) < 0.002, (gap, tail))
check("shared timing generation is idempotent",
      r2.returncode == 0 and first == second, r2.stdout + r2.stderr)

(audio_ws / "make_html.py").write_text("# forbidden\n")
sec = check_workspace_sources(audio_ws)
check("v2 workspaces cannot introduce make_*.py generators",
      not sec["pass"] and "make_html.py" in sec["output"], sec["output"])
(audio_ws / "make_html.py").unlink()
check("shared-only v2 workspace passes source policy",
      check_workspace_sources(audio_ws)["pass"])

token_voice = load_tokens(audio_ws)["voice"]
check("production voice declares no automatic fallback", "fallback" not in token_voice)

shutil.rmtree(tmp, ignore_errors=True)
shutil.rmtree(lease_repo, ignore_errors=True)
shutil.rmtree(audio_ws, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
