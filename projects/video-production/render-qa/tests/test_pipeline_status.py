#!/usr/bin/env python3
"""test_pipeline_status.py — the state model in scripts/batch-status.sh.

That script is the resume key: a fresh session with no memory of the last one
reads it and knows what to do next. Everything downstream — PIPELINE-STATUS.md,
AUTO-BATCH's drain order, the owner's whole picture of the factory — is the same
read, so a state it gets wrong is wrong in four places at once.

It is graded by RUNNING it against fixture trees, one per state, and reading
`--json`. Not by reading it: the four defects this suite was written for were
all of the "looks right, reports the wrong thing" kind, and only a fixture whose
answer is known in advance catches those.

The four (all 2026-08-04, all previously reported as something else):
  - lane blindness — every probe assumed the TEMPLATE lane, so a freeform
    workspace read as "nothing authored yet" and was told to restart a build
    that the mkdir lock would refuse;
  - inbox blindness — the blocked-script scan covered the render queue only, so
    a raw script carrying SCRIPT PENDING was reported as nothing at all;
  - no stall notion — an abandoned workspace was indistinguishable from one
    being actively written to;
  - no orphan notion — a workspace matching no script was looked up by nothing,
    so no code path could see it.

Run:  python3 tests/test_pipeline_status.py   (exit 0 = all pass)
"""
import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
REPO = RQ.parents[2]
STATUS = REPO / "scripts" / "batch-status.sh"
SHIP = REPO / "scripts" / "batch-ship.sh"
VERIFY_RENDER = RQ / "src" / "verify_render.py"
sys.path.insert(0, str(RQ / "src"))
from workspace_revision import (  # noqa: E402
    read_revision_marker,
    revision_files,
    workspace_revision,
)

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


class Tree:
    """A throwaway projects/video-production/ with only what the tool reads."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="pipeline-status-test-"))
        (self.root / "lesson-scripts").mkdir()
        (self.root / "renders-hyperframes").mkdir()
        (self.root / "render-qa").mkdir()
        self.pubtsv = self.root / "lesson-scripts" / "published.tsv"
        self.pubtsv.write_text("# base\tprogram\trender_date\twistia_url\n")
        self.qlog = self.root / "render-qa" / "quarantine.log"
        self.qlog.write_text("")

    def script(self, program, stage, stem, body="a spoken line."):
        d = self.root / "lesson-scripts" / program / stage
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{stem}.txt").write_text(body)

    def workspace(self, name, *, lane=None, voiced=False, timed=False,
                  preflight_ok=False, visual_review=None, verified=False,
                  render_start=True, render_pending=None,
                  encode_review_required=True, encode_review=None,
                  failure=None, journal=None, age_min=0):
        """A workspace at a chosen stage. `lane` picks which artifacts exist —
        that is the whole point: the two lanes share no probe."""
        ws = self.root / "renders-hyperframes" / name
        (ws / "assets" / "voice").mkdir(parents=True)
        if lane == "template":
            (ws / "scenes.json").write_text("[]")
            if voiced:
                (ws / "assets" / "voice" / "narration.wav").write_bytes(b"\0")
        elif lane == "freeform":
            (ws / "design.md").write_text("# design")
            (ws / "audio_request.json").write_text("{}")
            if voiced:
                # Beat ids are deliberately not s-prefixed. Status must trust
                # the manifest and verify its paths, never guess a filename.
                (ws / "assets" / "voice" / "b01.wav").write_bytes(b"\0")
                (ws / "audio_meta.json").write_text(json.dumps({
                    "voices": [{"id": "b01", "path": "assets/voice/b01.wav"}]
                }))
                (ws / "timing.json").write_text("{}")
        if lane:
            (ws / "index.html").write_text(
                '<div class="clip" data-start="1.5"></div>' if timed
                else '<div class="clip" data-start="0"></div>')
        revision = workspace_revision(ws)
        if (preflight_ok or visual_review or verified or render_pending
                or encode_review or failure):
            (ws / "qa").mkdir(exist_ok=True)
        if preflight_ok:
            if preflight_ok == "legacy":
                (ws / "qa" / "PREFLIGHT-OK").write_text("preflight exit 0")
            else:
                (ws / "qa" / "PREFLIGHT-OK").write_text(json.dumps({
                    "version": 1, "preflight_exit": 0,
                    "source_revision": revision,
                }))
        if visual_review:
            if isinstance(visual_review, dict):
                receipt = dict(visual_review)
            elif visual_review == "flat":
                receipt = {"BLOCKING_DEFECT": "PASS", "TASTE": "FLAT",
                           "RECOMMENDATION": "REVISE"}
            else:
                receipt = {"BLOCKING_DEFECT": "PASS", "TASTE": "ALIVE",
                           "RECOMMENDATION": "PROCEED"}
            receipt.setdefault("source_revision", revision)
            (ws / "qa" / "VISUAL-REVIEW.json").write_text(json.dumps(receipt))
        verified_sha = None
        fixture_render_attempt = 1
        if verified or render_pending:
            (ws / "renders").mkdir(exist_ok=True)
            mp4 = ws / "renders" / f"{name}_2026-08-07.mp4"
            original_bytes = f"encoded {name}".encode()
            verified_sha = hashlib.sha256(original_bytes).hexdigest()
            if verified != "missing" and render_pending != "missing":
                mp4.write_bytes(original_bytes)
            if render_start:
                if isinstance(render_start, dict):
                    render_receipt = dict(render_start)
                else:
                    render_receipt = {"backend": "cloud", "task_key": f"test-{name}"}
                render_receipt.setdefault("source_revision", revision)
                render_receipt.setdefault("mp4", str(mp4))
                render_receipt.setdefault("encode_review_required",
                                          encode_review_required)
                render_receipt.setdefault("attempt", 1)
                fixture_render_attempt = render_receipt["attempt"]
                if verified or render_pending in (True, "complete"):
                    render_receipt.setdefault("completed_at", "2026-08-07T00:00:00Z")
                    render_receipt.setdefault("completed_sha256", verified_sha)
                    render_receipt.setdefault("completed_bytes", len(original_bytes))
                (ws / "qa" / "RENDER-START.json").write_text(
                    json.dumps(render_receipt))
        if verified:
            (ws / "qa" / "VERIFIED").write_text(json.dumps({
                "mp4": str(mp4), "sha256": verified_sha,
                "source_revision": revision,
                "encode_review_required": encode_review_required,
                "render_attempt": fixture_render_attempt,
            }))
            if verified == "mutated":
                mp4.write_bytes(b"mutated after verification")
        if encode_review:
            if isinstance(encode_review, dict):
                encode_receipt = dict(encode_review)
            elif encode_review == "fail":
                encode_receipt = {"verdict": "FAIL", "findings": ["audio truncates"]}
            else:
                encode_receipt = {"verdict": "PASS", "findings": []}
            encode_receipt.setdefault("source_revision", revision)
            encode_receipt.setdefault("sha256", verified_sha)
            encode_receipt.setdefault("render_attempt", fixture_render_attempt)
            (ws / "qa" / "ENCODE-REVIEW.json").write_text(
                json.dumps(encode_receipt))
        if failure:
            (ws / "qa" / "failure.json").write_text(json.dumps(failure))
        if journal:
            stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 60 * 41))
            steps = journal if isinstance(journal, list) else [journal]
            (ws / ".build-log.tsv").write_text("".join(
                f"{stamp}\t{step}\tdetail here\n" for step in steps))
        if age_min:
            old = time.time() - age_min * 60
            for p in sorted(ws.rglob("*"), reverse=True):
                os.utime(p, (old, old))
            os.utime(ws, (old, old))
        return ws

    def approvals(self, values):
        run_dir = self.root / "renders-hyperframes" / "_run"
        run_dir.mkdir(exist_ok=True)
        (run_dir / "run.json").write_text(json.dumps({
            "mode": "batch", "items": [
                {"stem": stem, "program": "prog-a", "stage": "ready"}
                for stem in values
            ],
            "approvals": values,
        }))

    def run_state(self, **values):
        run_dir = self.root / "renders-hyperframes" / "_run"
        run_dir.mkdir(exist_ok=True)
        path = run_dir / "run.json"
        state = json.loads(path.read_text()) if path.is_file() else {}
        state.update(values)
        path.write_text(json.dumps(state))

    def publish(self, base, program, date, url):
        with self.pubtsv.open("a") as f:
            f.write(f"{base}\t{program}\t{date}\t{url}\n")

    def quarantine(self, stem, program, reason):
        with self.qlog.open("a") as f:
            f.write(f"2026-08-04T00:00:00Z\t{stem}\t{program}\t{reason}\n")

    def status(self, stall_minutes=30):
        env = dict(os.environ, VIDEO_VP_ROOT=str(self.root),
                   VIDEO_STALL_MINUTES=str(stall_minutes),
                   VIDEO_PRIORITY="prog-a prog-b")
        p = subprocess.run(["bash", str(STATUS), "--json"],
                           capture_output=True, text=True, env=env)
        if p.returncode != 0:
            raise AssertionError(f"batch-status.sh exited {p.returncode}: {p.stderr[-800:]}")
        return json.loads(p.stdout)

    def write_doc(self):
        out = self.root / "PIPELINE-STATUS.md"
        env = dict(os.environ, VIDEO_VP_ROOT=str(self.root),
                   VIDEO_PRIORITY="prog-a prog-b")
        subprocess.run(["bash", str(STATUS), "--write", str(out)],
                       capture_output=True, text=True, env=env, check=True)
        return out.read_text()

    def clean(self):
        shutil.rmtree(self.root, ignore_errors=True)


def flat(doc):
    """Every in-flight entry across programs, keyed by stem."""
    return {x["stem"]: x for p in doc["programs"] for x in p["in_flight"]}


def publish_receipt_probe(*, encode=None, clean_streak=0,
                          encode_review_required=None,
                          render_revision="current", arm_exit=0):
    """Run the real publish guards in a mini repo; the upload is a local stub."""
    root = Path(tempfile.mkdtemp(prefix="pipeline-publish-test-"))
    try:
        scripts = root / "scripts"
        src = root / "projects" / "video-production" / "render-qa" / "src"
        ws = (root / "projects" / "video-production" / "renders-hyperframes" /
              "receipt-probe_prog-a")
        scripts.mkdir(parents=True)
        src.mkdir(parents=True)
        (ws / "qa").mkdir(parents=True)
        (ws / "renders").mkdir()
        (root / "projects" / "video-production" / "lesson-scripts").mkdir()
        shutil.copy2(SHIP, scripts / "batch-ship.sh")
        shutil.copy2(RQ / "src" / "stem.py", src / "stem.py")
        shutil.copy2(RQ / "src" / "workspace_revision.py",
                     src / "workspace_revision.py")
        (scripts / "build-session.sh").write_text(
            f"#!/usr/bin/env bash\nexit {arm_exit}\n")
        (scripts / "batch-status.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
        sentinel = root / "upload-was-called"
        (scripts / "wistia-upload.sh").write_text(
            "#!/usr/bin/env bash\n"
            "printf called > \"$SHIP_TEST_SENTINEL\"\n"
            "echo 'local upload stub stopped here' >&2\n"
            "exit 55\n")
        (src / "run_state.py").write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "from pathlib import Path\n"
            "vp = Path(__file__).resolve().parents[2]\n"
            "cmd = sys.argv[1] if len(sys.argv) > 1 else ''\n"
            "if cmd == 'post-review-required':\n"
            "    path = vp / 'renders-hyperframes/_run/run.json'\n"
            "    state = json.loads(path.read_text()) if path.is_file() else {}\n"
            "    raise SystemExit(0 if int(state.get('cloud_clean_streak', 0)) < 3 else 1)\n"
            "raise SystemExit(0)\n")
        (ws / "index.html").write_text(
            '<main id="root" data-duration="1"><div class="clip" '
            'data-start="0"></div></main>')
        revision = workspace_revision(ws)
        mp4 = ws / "renders" / "receipt-probe_prog-a_2026-08-07.mp4"
        mp4.write_bytes(b"verified encoded bytes")
        digest = hashlib.sha256(mp4.read_bytes()).hexdigest()
        bound_revision = revision if render_revision == "current" else render_revision
        required = (clean_streak < 3 if encode_review_required is None
                    else encode_review_required)
        (ws / "qa" / "RENDER-START.json").write_text(json.dumps({
            "source_revision": bound_revision,
            "backend": "cloud",
            "task_key": f"probe-{bound_revision}",
            "attempt": 1,
            "mp4": str(mp4),
            "encode_review_required": required,
            "completed_at": "2026-08-07T00:00:00Z",
            "completed_sha256": digest,
            "completed_bytes": mp4.stat().st_size,
        }))
        (ws / "qa" / "VERIFIED").write_text(json.dumps({
            "source_revision": revision,
            "mp4": str(mp4),
            "sha256": digest,
            "encode_review_required": required,
            "render_attempt": 1,
        }))
        if encode is not None:
            receipt = {
                "source_revision": revision,
                "sha256": digest,
                "verdict": "PASS",
                "findings": [],
                "render_attempt": 1,
            }
            receipt.update(encode if isinstance(encode, dict) else {})
            (ws / "qa" / "ENCODE-REVIEW.json").write_text(json.dumps(receipt))
        run_dir = ws.parent / "_run"
        run_dir.mkdir()
        (run_dir / "run.json").write_text(json.dumps({
            "cloud_clean_streak": clean_streak,
        }))
        env = dict(os.environ, SHIP_TEST_SENTINEL=str(sentinel))
        result = subprocess.run(
            ["bash", str(scripts / "batch-ship.sh"),
             "receipt-probe_prog-a", "prog-a", "--publish"],
            capture_output=True, text=True, env=env)
        return result, sentinel.is_file()
    finally:
        shutil.rmtree(root, ignore_errors=True)


check("scripts/batch-status.sh exists", STATUS.is_file(), str(STATUS))
check("scripts/batch-ship.sh exists", SHIP.is_file(), str(SHIP))
ship_source = SHIP.read_text()
check("cloud render idempotency includes the exact source revision",
      ('RENDER_TASK_KEY="scla-${STEM}-${RENDER_DATE}-${RENDER_REVISION}'
       '-a${RENDER_ATTEMPT}"') in ship_source
      and '"$RENDER_TASK_KEY"' in ship_source)
check("a failed encoded attempt cannot be reused under the same cloud task key",
      'encode.get("render_attempt") == attempt' in ship_source
      and "PREVIOUS_RENDER_ATTEMPT + 1" in ship_source)
check("shipping resumes with stale-lease takeover but fails closed on a live owner",
      'arm "$STEM" --resume' in ship_source
      and "could not acquire exclusive lesson lease" in ship_source)
check("render start is persisted before verification",
      "qa/RENDER-START.json" in ship_source
      and "completed_sha256" in ship_source
      and "completed_bytes" in ship_source)
check("local renders keep encode review required; retirement stamps only new cloud renders",
      'ENCODE_REVIEW_REQUIRED="true"' in ship_source
      and 'if [[ "$RENDER_BACKEND" == "cloud" ]]' in ship_source)

# ---------------------------------------------------------------------------
print("== workspace revisions bind receipts to authored content ==")
t = Tree()
ws = t.workspace("revision_prog-a", lane="freeform", voiced=True, timed=True)
(ws / "assets" / "illustrations").mkdir()
(ws / "assets" / "illustrations" / "hero.png").write_bytes(b"hero-v1")
(ws / "assets" / "bgm").mkdir()
(ws / "assets" / "bgm" / "score.mp3").write_bytes(b"music-v1")
selected = {p.relative_to(ws).as_posix() for p in revision_files(ws)}
check("render inputs include manifests, timing, illustrations, and BGM",
      {"audio_meta.json", "timing.json", "assets/illustrations/hero.png",
       "assets/bgm/score.mp3"}.issubset(selected), sorted(selected))
check("render inputs include the exact generated narration bytes",
      "assets/voice/b01.wav" in selected, sorted(selected))

revision = workspace_revision(ws)
(ws / "qa").mkdir()
(ws / "qa" / "evidence.json").write_text('{"result":"PASS"}')
(ws / "snapshots").mkdir()
(ws / "snapshots" / "frame.jpg").write_bytes(b"frame")
(ws / "node_modules").mkdir()
(ws / "node_modules" / "runtime.js").write_text("generated")
(ws / "source-revisions").mkdir()
(ws / "source-revisions" / "copy.html").write_text("checkpoint")
(ws / ".build-log.tsv").write_text("now\tgate\tpass\n")
check("QA, snapshots, dependencies, checkpoints, and logs do not churn it",
      workspace_revision(ws) == revision)
(ws / "assets" / "voice" / "b01.wav").write_bytes(b"different voice")
check("changing narration bytes creates a new source revision",
      workspace_revision(ws) != revision)

changed = []
for relative, payload in (
        ("audio_meta.json", '{"voices":[],"version":2}'),
        ("timing.json", '{"duration":42}'),
        ("assets/illustrations/hero.png", "hero-v2"),
        ("assets/bgm/score.mp3", "music-v2")):
    before = workspace_revision(ws)
    (ws / relative).write_text(payload)
    changed.append(workspace_revision(ws) != before)
check("each manifest/timing/visual/music edit creates a new revision", all(changed), changed)

current_revision = workspace_revision(ws)
cli = subprocess.run(
    [sys.executable, str(RQ / "src" / "workspace_revision.py"), str(ws)],
    capture_output=True, text=True, check=True).stdout.strip()
check("the revision CLI prints the same digest as the Python API",
      cli == current_revision and len(cli) == 64, cli)
(ws / "qa" / "PREFLIGHT-OK").write_text(json.dumps({
    "source_revision": current_revision,
}))
check("a JSON gate marker exposes its bound revision",
      read_revision_marker(ws) == current_revision)
(ws / "qa" / "PREFLIGHT-OK").write_text("preflight exit 0")
check("a legacy unbound gate marker is rejected", read_revision_marker(ws) is None)
t.clean()

verify_root = Path(tempfile.mkdtemp(prefix="verify-render-source-test-"))
try:
    (verify_root / "qa").mkdir()
    (verify_root / "renders").mkdir()
    (verify_root / "index.html").write_text(
        '<main id="root" data-duration="1"><div class="clip" '
        'data-start="0"></div></main>')
    fake_mp4 = verify_root / "renders" / "old.mp4"
    fake_mp4.write_bytes(b"not opened because provenance fails first")
    (verify_root / "qa" / "RENDER-START.json").write_text(json.dumps({
        "source_revision": "older-source",
        "backend": "cloud",
        "task_key": "old-key",
    }))
    (verify_root / "qa" / "VERIFIED").write_text("stale marker")
    verify_result = subprocess.run(
        [sys.executable, str(VERIFY_RENDER), str(verify_root), str(fake_mp4), "--json"],
        capture_output=True, text=True)
    verify_payload = json.loads(verify_result.stdout)
    check("verify_render refuses bytes rendered from a different source revision",
          verify_result.returncode == 1
          and verify_payload["sections"]["render_source"]["pass"] is False,
          verify_result.stdout + verify_result.stderr)
    check("a provenance refusal removes any older VERIFIED marker",
          not (verify_root / "qa" / "VERIFIED").exists())
    (verify_root / "qa" / "RENDER-START.json").write_text(json.dumps({
        "source_revision": workspace_revision(verify_root),
        "backend": "cloud",
        "task_key": "partial-key",
        "attempt": 1,
        "mp4": str(fake_mp4),
        "encode_review_required": True,
    }))
    partial_verify = subprocess.run(
        [sys.executable, str(VERIFY_RENDER), str(verify_root), str(fake_mp4), "--json"],
        capture_output=True, text=True)
    partial_payload = json.loads(partial_verify.stdout)
    check("verify_render refuses nonempty bytes without atomic render completion",
          partial_verify.returncode == 1
          and "incomplete" in
              partial_payload["sections"]["render_source"]["output"],
          partial_verify.stdout + partial_verify.stderr)
finally:
    shutil.rmtree(verify_root, ignore_errors=True)

# ---------------------------------------------------------------------------
print("== script folders identify queue lifecycle ==")
t = Tree()
t.script("prog-a", "inbox", "raw-one_prog-a")
t.script("prog-a", "ready", "ready-one_prog-a")
t.script("prog-a", "published", "done-one_prog-a")
t.publish("done-one_prog-a", "prog-a", "2026-08-01", "https://sclc.wistia.com/medias/abc123")
d = t.status()
check("a script in inbox/ counts as RAW", d["totals"]["raw"] == 1, d["totals"])
check("a script in ready/ with no workspace counts as READY",
      d["totals"]["queued"] == 1, d["totals"])
check("a script in published/ WITH a tsv row is published, not stranded",
      d["totals"]["published"] == 1 and d["totals"]["stranded"] == 0, d["totals"])
t.clean()

print("== STRANDED: published/ without a published.tsv row ==")
t = Tree()
t.script("prog-a", "published", "orphaned-publish_prog-a")
d = t.status()
check("published/ with no tsv row is STRANDED", d["totals"]["stranded"] == 1, d["totals"])
check("...and it is NOT counted as live", d["totals"]["published"] == 0, d["totals"])
t.clean()

# ---------------------------------------------------------------------------
print("== lane detection: the same probe cannot grade both lanes ==")
t = Tree()
for stem, kw in [
    ("tpl-scaffold_prog-a", dict(lane=None)),
    ("tpl-planned_prog-a",  dict(lane="template")),
    ("tpl-untimed_prog-a",  dict(lane="template", voiced=True)),
    ("tpl-composed_prog-a", dict(lane="template", voiced=True, timed=True)),
    ("ff-planned_prog-a",   dict(lane="freeform")),
    ("ff-untimed_prog-a",   dict(lane="freeform", voiced=True)),
    ("ff-composed_prog-a",  dict(lane="freeform", voiced=True, timed=True)),
]:
    t.script("prog-a", "ready", stem)
    t.workspace(stem, **kw)
d = t.status()
f = flat(d)
check("a bare scaffold reads as scaffolded", f["tpl-scaffold_prog-a"]["stage"] == "scaffolded",
      f["tpl-scaffold_prog-a"])
check("template lane is detected from scenes.json",
      f["tpl-planned_prog-a"]["lane"] == "template", f["tpl-planned_prog-a"])
check("freeform lane is detected from design.md — NOT from a missing scenes.json",
      f["ff-planned_prog-a"]["lane"] == "freeform", f["ff-planned_prog-a"])
check("THE 2026-08-04 DEFECT: a freeform workspace with a design and no audio is "
      "'planned', not 'nothing authored yet'",
      f["ff-planned_prog-a"]["stage"] == "planned", f["ff-planned_prog-a"])
check("...and it is never told to restart the build",
      "rm -rf" not in f["ff-planned_prog-a"]["next"], f["ff-planned_prog-a"]["next"])
check("...an unselected stem is explicitly selected through the control plane",
      "run.sh produce --stem" in f["ff-planned_prog-a"]["next"],
      f["ff-planned_prog-a"]["next"])
check("a template workspace with no narration is 'planned'",
      f["tpl-planned_prog-a"]["stage"] == "planned", f["tpl-planned_prog-a"])
check("voiced but untimed is 'untimed' on the template lane",
      f["tpl-untimed_prog-a"]["stage"] == "untimed", f["tpl-untimed_prog-a"])
check("voiced but untimed is 'untimed' on the freeform lane too",
      f["ff-untimed_prog-a"]["stage"] == "untimed", f["ff-untimed_prog-a"])
check("timed on both lanes reaches 'composed'",
      f["tpl-composed_prog-a"]["stage"] == "composed"
      and f["ff-composed_prog-a"]["stage"] == "composed")
check("a scaffold-only workspace is restarted through explicit named scope",
      "run.sh produce --stem" in f["tpl-scaffold_prog-a"]["next"] and
      "rm -rf" not in f["tpl-scaffold_prog-a"]["next"],
      f["tpl-scaffold_prog-a"]["next"])
t.clean()

t = Tree()
t.script("prog-a", "ready", "unsafe-symlink_prog-a")
unsafe_ws = t.workspace("unsafe-symlink_prog-a", lane="template", voiced=True,
                        timed=True)
(unsafe_ws / "assets" / "illustrations").mkdir()
(unsafe_ws / "assets" / "illustrations" / "linked.png").symlink_to(
    unsafe_ws / "index.html")
unsafe = flat(t.status())["unsafe-symlink_prog-a"]
check("an unsafe render-affecting symlink becomes needs-revision, not a status crash",
      unsafe["phase"] == "needs-revision"
      and unsafe["condition"] == "invalid-source"
      and any("symlink" in finding for finding in unsafe["findings"]), unsafe)
t.clean()

# ---------------------------------------------------------------------------
print("== visual review and RENDERED are derivable from disk ==")
t = Tree()
t.script("prog-a", "ready", "awaiting_prog-a")
t.script("prog-a", "ready", "at-gate_prog-a")
t.script("prog-a", "ready", "rendered_prog-a")
t.workspace("awaiting_prog-a", lane="template", voiced=True, timed=True,
            preflight_ok=True)
t.workspace("at-gate_prog-a", lane="template", voiced=True, timed=True,
            preflight_ok=True, visual_review="proceed")
t.workspace("rendered_prog-a", lane="template", voiced=True, timed=True,
            preflight_ok=True, verified=True, encode_review="pass")
d = t.status()
f = flat(d)
check("a gate receipt without the durable visual verdict waits for visual review",
      f["awaiting_prog-a"]["stage"] == "awaiting-visual-review",
      f["awaiting_prog-a"])
check("PASS + ALIVE + PROCEED is what makes NEEDS REVIEW readable from disk",
      f["at-gate_prog-a"]["stage"] == "needs-review", f["at-gate_prog-a"])
check("both durable human checkpoints have separate totals",
      d["totals"]["awaiting_visual_review"] == 1
      and d["totals"]["needs_review"] == 1, d["totals"])
check("qa/VERIFIED outranks it — an MP4 exists", f["rendered_prog-a"]["stage"] == "rendered")
check("RENDERED's next action is the publish", "--publish" in f["rendered_prog-a"]["next"])
t.clean()

# ---------------------------------------------------------------------------
print("== encode review is bound to the verified source and MP4 bytes ==")
t = Tree()
for stem in ("encode-missing_prog-a", "encode-pass_prog-a", "encode-fail_prog-a",
             "encode-stale-source_prog-a", "encode-stale-sha_prog-a",
             "encode-stale-attempt_prog-a"):
    t.script("prog-a", "ready", stem)
t.workspace("encode-missing_prog-a", lane="template", voiced=True, timed=True,
            verified=True)
t.workspace("encode-pass_prog-a", lane="template", voiced=True, timed=True,
            verified=True, encode_review="pass")
t.workspace("encode-fail_prog-a", lane="template", voiced=True, timed=True,
            verified=True, encode_review="fail")
t.workspace("encode-stale-source_prog-a", lane="template", voiced=True, timed=True,
            verified=True, encode_review={
                "source_revision": "older-source", "sha256": "x", "verdict": "PASS",
            })
t.workspace("encode-stale-sha_prog-a", lane="template", voiced=True, timed=True,
            verified=True, encode_review={
                "sha256": "older-mp4", "verdict": "PASS",
            })
t.workspace("encode-stale-attempt_prog-a", lane="template", voiced=True, timed=True,
            verified=True, render_start={"attempt": 2}, encode_review={
                "render_attempt": 1, "verdict": "PASS",
            })
d = t.status()
f = flat(d)
check("VERIFIED without the still-required encode receipt is not RENDERED",
      f["encode-missing_prog-a"]["phase"] == "awaiting-encode-review"
      and f["encode-missing_prog-a"]["condition"] is None,
      f["encode-missing_prog-a"])
check("same-source, same-MP4-sha PASS is RENDERED",
      f["encode-pass_prog-a"]["phase"] == "rendered",
      f["encode-pass_prog-a"])
check("a current FAIL preserves phase, rejects publish, and exposes findings",
      f["encode-fail_prog-a"]["phase"] == "awaiting-encode-review"
      and f["encode-fail_prog-a"]["condition"] == "rejected"
      and f["encode-fail_prog-a"]["stage"] == "rejected"
      and "audio truncates" in f["encode-fail_prog-a"]["findings"],
      f["encode-fail_prog-a"])
check("a PASS for older source or MP4 bytes remains awaiting review",
      all(f[stem]["phase"] == "awaiting-encode-review"
          and f[stem]["condition"] == "stale-encode-review"
          for stem in ("encode-stale-source_prog-a", "encode-stale-sha_prog-a",
                       "encode-stale-attempt_prog-a")),
      {stem: f[stem] for stem in
       ("encode-stale-source_prog-a", "encode-stale-sha_prog-a",
        "encode-stale-attempt_prog-a")})
check("encode checkpoints have separate awaiting/rejected/stale counts",
      d["totals"]["awaiting_encode_review"] == 4
      and d["totals"]["rejected"] == 1
      and d["totals"]["stale_encode_review"] == 3,
      d["totals"])
t.clean()

t = Tree()
t.script("prog-a", "ready", "old-review-required_prog-a")
t.script("prog-a", "ready", "new-review-retired_prog-a")
t.workspace("old-review-required_prog-a", lane="template", voiced=True, timed=True,
            verified=True, encode_review_required=True)
t.workspace("new-review-retired_prog-a", lane="template", voiced=True, timed=True,
            verified=True, encode_review_required=False)
t.run_state(cloud_clean_streak=3)
f = flat(t.status())
check("a later 3/3 streak cannot retroactively bless an older unreviewed render",
      f["old-review-required_prog-a"]["phase"] == "awaiting-encode-review",
      f["old-review-required_prog-a"])
check("only a render stamped after retirement can omit the encode receipt",
      f["new-review-retired_prog-a"]["phase"] == "rendered"
      and "stamped" in f["new-review-retired_prog-a"]["state"],
      f["new-review-retired_prog-a"])
t.clean()

missing_publish, upload_called = publish_receipt_probe()
check("publish refuses a missing required encode receipt before any upload call",
      missing_publish.returncode == 3 and not upload_called
      and "encode review is still required" in missing_publish.stderr,
      missing_publish.stdout + missing_publish.stderr)
passing_publish, upload_called = publish_receipt_probe(encode={})
check("publish accepts a same-source, same-sha PASS and reaches only the local stub",
      passing_publish.returncode == 3 and upload_called
      and "local upload stub stopped here" in passing_publish.stdout,
      passing_publish.stdout + passing_publish.stderr)
stale_render_publish, upload_called = publish_receipt_probe(
    encode={}, render_revision="older-source")
check("publish refuses a render-start receipt for older source before upload",
      stale_render_publish.returncode == 3 and not upload_called
      and "belongs to different source" in stale_render_publish.stderr,
      stale_render_publish.stdout + stale_render_publish.stderr)
retired_publish, upload_called = publish_receipt_probe(clean_streak=3)
check("publish honors a per-render retirement stamp without an encode receipt",
      retired_publish.returncode == 3 and upload_called,
      retired_publish.stdout + retired_publish.stderr)
retroactive_publish, upload_called = publish_receipt_probe(
    clean_streak=3, encode_review_required=True)
check("publish does not use the current global streak to bless an older render",
      retroactive_publish.returncode == 3 and not upload_called
      and "encode review is still required" in retroactive_publish.stderr,
      retroactive_publish.stdout + retroactive_publish.stderr)
lease_refusal, upload_called = publish_receipt_probe(
    encode={}, arm_exit=9)
check("render/publish fails closed when the exclusive lesson lease cannot arm",
      lease_refusal.returncode == 2 and not upload_called
      and "could not acquire exclusive lesson lease" in lease_refusal.stderr,
      lease_refusal.stdout + lease_refusal.stderr)

t = Tree()
for stem in ("awaiting-verify_prog-a", "partial-render_prog-a",
             "missing-mp4_prog-a", "mutated-mp4_prog-a"):
    t.script("prog-a", "ready", stem)
t.workspace("awaiting-verify_prog-a", lane="template", voiced=True, timed=True,
            render_pending="complete")
t.workspace("partial-render_prog-a", lane="template", voiced=True, timed=True,
            render_pending="partial")
t.workspace("missing-mp4_prog-a", lane="template", voiced=True, timed=True,
            verified="missing", encode_review="pass")
t.workspace("mutated-mp4_prog-a", lane="template", voiced=True, timed=True,
            verified="mutated", encode_review="pass")
d = t.status()
f = flat(d)
check("a completed current-source MP4 without VERIFIED awaits verification, not render",
      f["awaiting-verify_prog-a"]["phase"] == "awaiting-verification"
      and f["awaiting-verify_prog-a"]["condition"] is None
      and "without rendering it again" in f["awaiting-verify_prog-a"]["next"],
      f["awaiting-verify_prog-a"])
check("a nonempty partial MP4 without atomic completion is never reused",
      f["partial-render_prog-a"]["phase"] == "interrupted-render"
      and f["partial-render_prog-a"]["condition"] == "incomplete-render",
      f["partial-render_prog-a"])
check("missing or mutated verified bytes are invalid, never RENDERED",
      all(f[stem]["phase"] == "awaiting-verification"
          and f[stem]["condition"] == "invalid-render"
          for stem in ("missing-mp4_prog-a", "mutated-mp4_prog-a")),
      {stem: f[stem] for stem in ("missing-mp4_prog-a", "mutated-mp4_prog-a")})
check("invalid and incomplete render conditions have durable separate counts",
      d["totals"]["invalid_render"] == 2
      and d["totals"]["incomplete_render"] == 1,
      d["totals"])
t.clean()

# ---------------------------------------------------------------------------
print("== gate, review, approval, and render receipts are revision-bound ==")
t = Tree()
for stem in ("legacy-gate_prog-a", "stale-gate_prog-a", "flat_prog-a",
             "approved_prog-a", "stale-render_prog-a",
             "wrong-render-source_prog-a"):
    t.script("prog-a", "ready", stem)
t.workspace("legacy-gate_prog-a", lane="template", voiced=True, timed=True,
            preflight_ok="legacy")
stale_gate = t.workspace("stale-gate_prog-a", lane="template", voiced=True,
                         timed=True, preflight_ok=True)
(stale_gate / "index.html").write_text(
    '<div class="clip" data-start="2.0">new cut</div>')
t.workspace("flat_prog-a", lane="template", voiced=True, timed=True,
            preflight_ok=True, visual_review="flat")
approved = t.workspace("approved_prog-a", lane="template", voiced=True, timed=True,
                       preflight_ok=True, visual_review="proceed")
stale_render = t.workspace("stale-render_prog-a", lane="template", voiced=True,
                           timed=True, preflight_ok=True, verified=True,
                           encode_review="pass")
(stale_render / "index.html").write_text(
    '<div class="clip" data-start="3.0">post-render edit</div>')
t.workspace("wrong-render-source_prog-a", lane="template", voiced=True, timed=True,
            verified=True, render_start={"source_revision": "older-source"},
            encode_review="pass")
t.approvals({"approved_prog-a": {
    "revision": workspace_revision(approved),
    "approved_at": "2026-08-07T00:00:00Z",
    "approved_by": "owner",
}})
d = t.status()
f = flat(d)
check("legacy PREFLIGHT-OK is composed with a stale-gate condition",
      f["legacy-gate_prog-a"]["phase"] == "composed"
      and f["legacy-gate_prog-a"]["condition"] == "stale-gate",
      f["legacy-gate_prog-a"])
check("editing source after a pass invalidates that gate",
      f["stale-gate_prog-a"]["phase"] == "composed"
      and f["stale-gate_prog-a"]["condition"] == "stale-gate"
      and f["stale-gate_prog-a"]["gate_revision"]
          != f["stale-gate_prog-a"]["revision"], f["stale-gate_prog-a"])
check("FLAT/REVISE is durable NEEDS REVISION, never ready for owner approval",
      f["flat_prog-a"]["stage"] == "needs-revision", f["flat_prog-a"])
check("an owner approval counts only for the exact current revision",
      f["approved_prog-a"]["stage"] == "approved", f["approved_prog-a"])
check("editing source after VERIFIED makes the render stale",
      f["stale-render_prog-a"]["phase"] == "composed"
      and f["stale-render_prog-a"]["condition"] == "stale-render",
      f["stale-render_prog-a"])
check("VERIFIED cannot relabel an MP4 whose render task used older source",
      f["wrong-render-source_prog-a"]["phase"] == "composed"
      and f["wrong-render-source_prog-a"]["condition"] == "stale-render"
      and f["wrong-render-source_prog-a"]["render_revision"] == "older-source",
      f["wrong-render-source_prog-a"])
check("stale receipts retain compatible totals without pretending work is done",
      d["totals"]["stale_gate"] == 2
      and d["totals"]["stale_render"] == 2
      and d["totals"]["rendered"] == 0, d["totals"])

# Once the source changes, gate, visual verdict, and approval all become stale.
(approved / "index.html").write_text(
    '<div class="clip" data-start="4.0">changed after approval</div>')
approved_state = flat(t.status())["approved_prog-a"]
check("a later edit cannot inherit an earlier owner approval",
      approved_state["phase"] == "composed"
      and approved_state["condition"] == "stale-gate", approved_state)
t.clean()

# ---------------------------------------------------------------------------
print("== NEEDS SCRIPT is scanned in BOTH inbox/ and ready/ ==")
t = Tree()
t.script("prog-a", "inbox", "raw-blocked_prog-a",
         "SCRIPT PENDING\nthe source never defines the four parts.\n")
t.script("prog-a", "ready", "ready-blocked_prog-a",
         "line one.\nTODO: needs input — which tool does this lesson name?\n")
d = t.status()
blocked = {b["stem"]: b for p in d["programs"] for b in p["needs_script"]}
check("THE 2026-08-04 DEFECT: a marker in inbox/ is seen (it used to report 0)",
      "raw-blocked_prog-a" in blocked, list(blocked))
check("a marker in ready/ is seen too", "ready-blocked_prog-a" in blocked, list(blocked))
check("both are counted", d["totals"]["needs_script"] == 2, d["totals"])
check("a blocked raw script is NOT also counted as RAW", d["totals"]["raw"] == 0, d["totals"])
check("a blocked ready script is NOT also counted as READY",
      d["totals"]["queued"] == 0, d["totals"])
check("the folder is named, so the owner knows where to go",
      blocked["raw-blocked_prog-a"]["folder"] == "inbox", blocked["raw-blocked_prog-a"])
check("the marker's own paragraph is carried, not just the marker word",
      "four parts" in blocked["raw-blocked_prog-a"]["detail"],
      blocked["raw-blocked_prog-a"]["detail"])
t.clean()

# ---------------------------------------------------------------------------
print("== STALLED is a statement about time, not a different job ==")
t = Tree()
t.script("prog-a", "ready", "fresh_prog-a")
t.script("prog-a", "ready", "stale_prog-a")
t.script("prog-a", "ready", "stale-done_prog-a")
t.workspace("fresh_prog-a", lane="template", voiced=True, age_min=0)
stale_workspace = t.workspace("stale_prog-a", lane="template", voiced=True,
                              age_min=120)
(stale_workspace / "source-revisions/recent-checkpoint").mkdir(parents=True)
(stale_workspace / "source-revisions/recent-checkpoint/manifest.json").write_text(
    "{}\n")
t.workspace("stale-done_prog-a", lane="template", voiced=True, timed=True,
            verified=True, encode_review="pass", age_min=120)
d = t.status(stall_minutes=30)
f = flat(d)
check("a workspace written to just now is BUILDING, not STALLED",
      f["fresh_prog-a"]["stage"] == "untimed" and d["totals"]["building"] == 1, d["totals"])
check("an incomplete workspace idle past the threshold is STALLED",
      f["stale_prog-a"]["stage"] == "stalled", f["stale_prog-a"])
check("creating a recovery checkpoint does not disguise stalled production work",
      f["stale_prog-a"]["condition"] == "stalled", f["stale_prog-a"])
check("STALLED is a condition; the last completed production phase remains readable",
      f["stale_prog-a"]["phase"] == "untimed"
      and f["stale_prog-a"]["condition"] == "stalled", f["stale_prog-a"])
check("a COMPLETE workspace is never STALLED however old it is — it is waiting "
      "on a human, which is not the same thing",
      f["stale-done_prog-a"]["stage"] == "rendered", f["stale-done_prog-a"])
check("STALLED keeps the stage's own next action; it does not order a delete of "
      "a workspace holding narration",
      "rm -rf" not in f["stale_prog-a"]["next"], f["stale_prog-a"]["next"])
d = t.status(stall_minutes=999)
check("the threshold is honored — raise it and nothing is stalled",
      t.status(stall_minutes=999)["totals"]["stalled"] == 0)
check("...drop it to zero and both INCOMPLETE builds stall — but the verified "
      "one still does not, because completeness outranks the clock",
      t.status(stall_minutes=0)["totals"]["stalled"] == 2,
      t.status(stall_minutes=0)["totals"])
t.clean()

print("== the build journal says where an interrupted build stopped ==")
t = Tree()
t.script("prog-a", "ready", "interrupted_prog-a")
t.workspace("interrupted_prog-a", lane="freeform", voiced=True, journal="voice", age_min=41)
f = flat(t.status())
check("the last completed step is reported by name",
      "voice" in (f["interrupted_prog-a"]["journal"] or ""), f["interrupted_prog-a"])
check("...with a stable UTC timestamp (generated status cannot age into drift)",
      "UTC" in (f["interrupted_prog-a"]["journal"] or "") and
      "ago" not in (f["interrupted_prog-a"]["journal"] or ""),
      f["interrupted_prog-a"])
t.clean()

t = Tree()
t.script("prog-a", "ready", "released_prog-a")
t.workspace("released_prog-a", lane="freeform", voiced=True,
            journal=["claim", "timing", "gate", "release"])
released = flat(t.status())["released_prog-a"]
check("control events do not hide the last meaningful completed phase",
      released["last_completed_phase"] == "gate", released)
t.clean()

# ---------------------------------------------------------------------------
print("== REJECTED stops being an accident of branch order ==")
t = Tree()
t.script("prog-a", "ready", "refused_prog-a")
t.workspace("refused_prog-a", lane="template", voiced=True, timed=True)
t.quarantine("refused_prog-a", "prog-a", "verify_render.py non-zero")
d = t.status()
check("an unresolved quarantine row makes the lesson REJECTED",
      flat(d)["refused_prog-a"]["stage"] == "rejected", d["totals"])
check("...counted as REJECTED, not as an ordinary build",
      d["totals"]["rejected"] == 1 and d["totals"]["building"] == 0, d["totals"])
check("REJECTED is a condition; composition progress is preserved",
      flat(d)["refused_prog-a"]["phase"] == "composed"
      and flat(d)["refused_prog-a"]["condition"] == "rejected",
      flat(d)["refused_prog-a"])

t.publish("refused_prog-a", "prog-a", "2026-08-04", "https://sclc.wistia.com/medias/zzz999")
d = t.status()
check("a quarantine whose base later PUBLISHED is resolved — the row stays, the "
      "alarm does not", d["totals"]["rejected"] == 0, d["totals"])
t.clean()

t = Tree()
t.script("prog-a", "ready", "structured-failure_prog-a")
t.script("prog-a", "ready", "resolved-failure_prog-a")
t.workspace("structured-failure_prog-a", lane="template", voiced=True, timed=True,
            failure={"reason": "preflight rejected the cut",
                     "next_action": "correct the timing"})
t.workspace("resolved-failure_prog-a", lane="template", voiced=True, timed=True,
            failure={"reason": "old failure",
                     "resolved_at": "2026-08-07T00:00:00Z"})
t.quarantine("resolved-failure_prog-a", "prog-a", "older qlog incident")
d = t.status()
f = flat(d)
check("an unresolved failure.json rejects the cut even with no quarantine log row",
      f["structured-failure_prog-a"]["condition"] == "rejected"
      and "preflight rejected" in f["structured-failure_prog-a"]["state"],
      f["structured-failure_prog-a"])
check("resolved failure.json suppresses its older qlog incident without deleting either",
      f["resolved-failure_prog-a"]["condition"] != "rejected",
      f["resolved-failure_prog-a"])
t.clean()

t = Tree()
t.script("prog-a", "ready", "refused2_prog-a")
t.workspace("refused2_prog-a", lane="template", voiced=True, timed=True)
t.quarantine("refused2_prog-a", "prog-a", "verify_render.py non-zero")
t.quarantine("refused2_prog-a", "prog-a", "resolved: re-rendered clean 2026-08-04")
d = t.status()
check("a later `resolved` row in the log clears it without deleting history",
      d["totals"]["rejected"] == 0, d["totals"])
t.clean()

# ---------------------------------------------------------------------------
print("== ORPHAN: a workspace no script can reach ==")
t = Tree()
t.script("prog-a", "ready", "has-script_prog-a")
t.workspace("has-script_prog-a", lane="template", voiced=True)
t.workspace("nobodys-child_prog-a-backup", lane="freeform", voiced=True, timed=True)
d = t.status()
check("THE 2026-08-04 DEFECT: a workspace matching no script is reported",
      d["totals"]["orphan"] == 1, d["totals"])
check("...and named", d["orphans"][0]["workspace"] == "nobodys-child_prog-a-backup",
      d["orphans"])
check("a workspace that HAS a script is not an orphan",
      all(o["workspace"] != "has-script_prog-a" for o in d["orphans"]))
t.clean()

t = Tree()
t.script("prog-a", "ready", "real_prog-a")
t.workspace("real_prog-a", lane="template", voiced=True)
os.rename(t.root / "renders-hyperframes" / "real_prog-a",
          t.root / "renders-hyperframes" / "_reference")
d = t.status()
check("an underscore folder is skipped by the workspace scan, so filing "
      "reference material under _reference/ ends the orphan report",
      d["totals"]["orphan"] == 0, d)
t.clean()

# ---------------------------------------------------------------------------
print("== the generated document ==")
t = Tree()
t.script("prog-a", "inbox", "raw_prog-a")
t.script("prog-a", "ready", "queued_prog-a")
t.script("prog-a", "ready", "blocked_prog-a", "SCRIPT PENDING\nneeds the real numbers.\n")
t.script("prog-a", "published", "live_prog-a")
t.publish("live_prog-a", "prog-a", "2026-08-01", "https://sclc.wistia.com/medias/abc123")
t.workspace("stalled_prog-a", lane="freeform", voiced=True, age_min=200)
t.script("prog-a", "ready", "stalled_prog-a")
doc = t.write_doc()
check("the doc carries a Delivered table", "## Delivered" in doc)
check("...with a clickable Wistia link",
      "(https://sclc.wistia.com/medias/abc123)" in doc, doc[:0])
check("...and the local MP4 path, so the receipt answers both questions",
      "renders-mp4/prog-a/live_prog-a_2026-08-01.mp4" in doc)
check("the table distinguishes production phases and conditions",
      "Phase or condition" in doc
      and all(s in doc for s in ("**RAW**", "**READY**", "**BUILDING**",
                                 "**NEEDS REVIEW**", "**AWAITING ENCODE REVIEW**",
                                 "**RENDERED**", "**PUBLISHED**")))
check("the generated prose never equates a folder name with stage",
      "folder name is the stage name" not in doc.lower())
check("stalled work is resumed in place, not released and rebuilt",
      "resume that phase in place" in doc
      and "lock released, then a rebuild" not in doc.lower())
check("rendered means receipts are content- and MP4-bound",
      "render-complete and `qa/VERIFIED` receipts match current source" in doc
      and "actual MP4 bytes" in doc)
check("exception states are in the table too",
      all(s in doc for s in ("*NEEDS SCRIPT*", "*STALLED*", "*REJECTED*",
                             "*STRANDED*", "*ORPHAN*")))
check("a blocked script's own question reaches the doc", "real numbers" in doc)
check("a stalled build is surfaced under a needs-a-human heading",
      "Needs a human right now" in doc and "stalled_prog-a" in doc)
check("the doc is idempotent — regenerating it byte-for-byte matches",
      t.write_doc() == doc)
t.clean()

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
