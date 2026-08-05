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
                  preflight_ok=False, verified=False, journal=None, age_min=0):
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
        if preflight_ok or verified:
            (ws / "qa").mkdir(exist_ok=True)
        if preflight_ok:
            (ws / "qa" / "PREFLIGHT-OK").write_text("preflight exit 0")
        if verified:
            (ws / "qa" / "VERIFIED").write_text('{"mp4": "x.mp4", "sha256": "x"}')
        if journal:
            stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 60 * 41))
            (ws / ".build-log.tsv").write_text(f"{stamp}\t{journal}\tdetail here\n")
        if age_min:
            old = time.time() - age_min * 60
            for p in sorted(ws.rglob("*"), reverse=True):
                os.utime(p, (old, old))
            os.utime(ws, (old, old))
        return ws

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


check("scripts/batch-status.sh exists", STATUS.is_file(), str(STATUS))

# ---------------------------------------------------------------------------
print("== the folder name is the stage name ==")
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

# ---------------------------------------------------------------------------
print("== NEEDS REVIEW and RENDERED are derivable from disk ==")
t = Tree()
t.script("prog-a", "ready", "at-gate_prog-a")
t.script("prog-a", "ready", "rendered_prog-a")
t.workspace("at-gate_prog-a", lane="template", voiced=True, timed=True, preflight_ok=True)
t.workspace("rendered_prog-a", lane="template", voiced=True, timed=True,
            preflight_ok=True, verified=True)
d = t.status()
f = flat(d)
check("qa/PREFLIGHT-OK is what makes NEEDS REVIEW readable from disk",
      f["at-gate_prog-a"]["stage"] == "needs-review", f["at-gate_prog-a"])
check("...without it, 'gate-clean, awaiting your eyes' exists only in a dead "
      "session's memory", d["totals"]["needs_review"] == 1, d["totals"])
check("qa/VERIFIED outranks it — an MP4 exists", f["rendered_prog-a"]["stage"] == "rendered")
check("RENDERED's next action is the publish", "--publish" in f["rendered_prog-a"]["next"])
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
t.workspace("stale_prog-a", lane="template", voiced=True, age_min=120)
t.workspace("stale-done_prog-a", lane="template", voiced=True, timed=True,
            verified=True, age_min=120)
d = t.status(stall_minutes=30)
f = flat(d)
check("a workspace written to just now is BUILDING, not STALLED",
      f["fresh_prog-a"]["stage"] == "untimed" and d["totals"]["building"] == 1, d["totals"])
check("an incomplete workspace idle past the threshold is STALLED",
      f["stale_prog-a"]["stage"] == "stalled", f["stale_prog-a"])
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

t.publish("refused_prog-a", "prog-a", "2026-08-04", "https://sclc.wistia.com/medias/zzz999")
d = t.status()
check("a quarantine whose base later PUBLISHED is resolved — the row stays, the "
      "alarm does not", d["totals"]["rejected"] == 0, d["totals"])
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
check("the stage table uses the folder names as the stage names",
      all(s in doc for s in ("**RAW**", "**READY**", "**BUILDING**",
                             "**NEEDS REVIEW**", "**RENDERED**", "**PUBLISHED**")))
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
