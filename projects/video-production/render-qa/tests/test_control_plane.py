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
check("generated kit source has no extraction-marker residue",
      "BUILD-KIT:BEGIN" not in kit and "BUILD-KIT:END" not in kit)
check("build kit is copied from one tracked contract",
      'cp "$CONTRACT" "$RUN/BUILD-KIT.md"' in prepare)
check("AUTO-BATCH owns stem selection and parallel scheduling",
      "Never ask the user to choose, copy, or" in render_skill and
      "parallel in-session subagents" in render_skill and
      "Separate Codex Cloud tasks are an" in render_skill and
      "only when every selected stem is `PUBLISHED`" in render_skill)
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
a.write_text("Lesson A.")
b.write_text("Lesson B.")
b_before = (digest(b), b.stat().st_mtime_ns)
state_file = test_vp / "renders-hyperframes/_run/run.json"
env = dict(os.environ, VIDEO_VP_ROOT=str(test_vp), VIDEO_REPO_ROOT=str(REPO),
           VIDEO_RUN_STATE=str(state_file), VIDEO_RUN_STATE_TOOL=str(STATE_TOOL),
           VIDEO_PRIORITY="prog-a")
r = run(["bash", str(RUN), "produce", "--stem", "lesson-a_prog-a"], env=env)
state = json.loads(state_file.read_text())
check("named production selects exactly one stem", r.returncode == 0 and
      [x["stem"] for x in state["items"]] == ["lesson-a_prog-a"], r.stderr)
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
check("explicit program batch selects that program", r.returncode == 0 and
      {x["stem"] for x in state["items"]} == {"lesson-a_prog-a", "lesson-b_prog-a"})
r = run(["bash", str(RUN), "delegate", "--stem", "lesson-a_prog-a"], env=env)
check("selected stems get an exact source-only cloud prompt",
      r.returncode == 0 and
      "bash scripts/cloud-author.sh lesson-a_prog-a prog-a" in r.stdout and
      "Do not call HeyGen" in r.stdout, r.stderr + r.stdout)
check("new runs separate authoring, TTS, render, and publish capacity",
      state["authoring_concurrency"] == 3 and state["tts_concurrency"] == 2 and
      state["cloud_render_concurrency"] == 2 and state["publish_concurrency"] == 1,
      state)
(test_vp / "renders-hyperframes/lesson-a_prog-a/qa").mkdir(parents=True)
r = run([sys.executable, str(STATE_TOOL), "can-ship", "lesson-a_prog-a"], env=env)
check("batch shipping is mechanically blocked before pilot approval",
      r.returncode != 0 and "pilot is not approved" in r.stderr, r.stderr)
(test_vp / "renders-hyperframes/lesson-a_prog-a/qa/PREFLIGHT-OK").write_text("")
r = run(["bash", str(RUN), "approve", "lesson-a_prog-a"], env=env)
approved = json.loads(state_file.read_text())["pilot"]
r3 = run([sys.executable, str(STATE_TOOL), "can-ship", "lesson-a_prog-a"], env=env)
r2 = run(["bash", str(RUN), "resume"], env=env)
check("pilot approval persists across sessions", r.returncode == 0 and
      approved["approved_at"] and json.loads(state_file.read_text())["pilot"] == approved and
      approved["approved_at"] in r2.stdout and r3.returncode == 0)


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
for clean_stem in ("clean-one_prog-a", "clean-two_prog-a", "clean-three_prog-a"):
    clean_ws = test_vp / "renders-hyperframes" / clean_stem
    clean_ws.mkdir()
    run([sys.executable, str(STATE_TOOL), "record-success", "--workspace",
         str(clean_ws), "--stem", clean_stem, "--phase", "cloud-render"], env=env)
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
    ws = test_vp / "renders-hyperframes" / stem
    ws.mkdir()
    parallel.append(subprocess.Popen(
        [sys.executable, str(STATE_TOOL), "record-success", "--workspace",
         str(ws), "--stem", stem, "--phase", "cloud-render"], env=env))
parallel_ok = all(proc.wait() == 0 for proc in parallel)
state = json.loads(state_file.read_text())
check("parallel render completions cannot overwrite run-state updates",
      parallel_ok and all(stem in state["results"] for stem in parallel_stems) and
      state["cloud_clean_streak"] == 3, state)
failure("lesson-a_prog-a")
state = json.loads(state_file.read_text())
check("a cloud-render failure automatically returns capacity to two",
      state["cloud_render_concurrency"] == 2 and
      state["cloud_clean_streak"] == 0, state)


print("== idempotent per-stem leases ==")
lease_repo = Path(tempfile.mkdtemp(prefix="video-lease-test-"))
(lease_repo / "scripts").mkdir()
shutil.copy2(REPO / "scripts/build-session.sh", lease_repo / "scripts/build-session.sh")
lease_cmd = ["bash", str(lease_repo / "scripts/build-session.sh")]
check("lease arm succeeds", run(lease_cmd + ["arm", "a"]).returncode == 0)
run(lease_cmd + ["arm", "a"])
run(lease_cmd + ["arm", "b"])
lease_dir = lease_repo / "projects/video-production/renders-hyperframes/.build-in-progress"
check("reclaim refreshes one lease instead of duplicating it",
      sorted(p.name for p in lease_dir.iterdir()) == ["a", "b"])
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
