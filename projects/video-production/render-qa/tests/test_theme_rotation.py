#!/usr/bin/env python3
"""test_theme_rotation.py — style-package rotation is a computation, not a rule.

The defect this pins was invisible for a week and would have shipped 12
identical-looking videos. `design-contract.md` said rotate by the program's
STARTED-BUILD count, `= count(*.txt in rendered/) mod 3`. On 2026-07-28 the
script stopped moving at build time and started moving at publish time, so that
folder came to mean *published*. The sentence did not change. mid-career-momentum
had 14 builds and 0 published lessons, so its count was 0, so `summit` was the
answer forever.

Nothing failed. A rotation stuck on one value produces no error, no gate hit and
no complaint — it produces a batch of videos that all look the same, noticed
only by a human, late. So the test that matters is not "does it return a legal
package" but "does it actually MOVE, and does it move for the right reason".

Run:  python3 tests/test_theme_rotation.py   (exit 0 = all pass)
"""
import shutil
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))
from theme_for import (PACKAGES, published_bases, started_bases, theme_for,
                       workspace_bases)

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
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="theme-rotation-test-"))
        self.lessons = self.root / "lesson-scripts"
        self.ws = self.root / "renders-hyperframes"
        self.ws.mkdir(parents=True)
        self.lessons.mkdir(parents=True)
        (self.lessons / "published.tsv").write_text(
            "# base\tprogram\trender_date\twistia_url\n")

    def script(self, program, stage, stem):
        d = self.lessons / program / stage
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{stem}.txt").write_text("narration.")

    def workspace(self, name):
        (self.ws / name).mkdir(parents=True, exist_ok=True)

    def publish(self, base, program):
        with (self.lessons / "published.tsv").open("a") as f:
            f.write(f"{base}\t{program}\t2026-08-01\thttps://sclc.wistia.com/medias/x{base[:4]}\n")

    def theme(self, program, offset=0):
        return theme_for(program, lessons=self.lessons, workspaces=self.ws,
                         offset=offset)

    def started(self, program):
        return started_bases(program, lessons=self.lessons, workspaces=self.ws)

    def clean(self):
        shutil.rmtree(self.root, ignore_errors=True)


print("== the rotation moves, and moves in order ==")
t = Tree()
seen = []
for i in range(6):
    stem = f"lesson{i}_prog-a"
    t.script("prog-a", "ready", stem)
    seen.append(t.theme("prog-a"))
    t.workspace(stem)                     # each build claims its workspace
check("an empty program starts at the head of the rotation", seen[0] == PACKAGES[0], seen)
check("each started build advances it", seen[:3] == list(PACKAGES), seen)
check("and it wraps", seen == list(PACKAGES) * 2, seen)
t.clean()

print("== THE 2026-08-04 DEFECT: builds that never published still count ==")
t = Tree()
for i in range(14):
    stem = f"m{i}_built_prog-a"
    t.script("prog-a", "ready", stem)
    t.workspace(stem)
check("14 built, 0 published — the started count is 14, not 0",
      len(t.started("prog-a")) == 14, t.started("prog-a"))
check("...so the next lesson is NOT the head of the rotation",
      t.theme("prog-a") != PACKAGES[0], t.theme("prog-a"))
spread = {t.theme("prog-a", offset=i) for i in range(12)}
check("...and a 12-lesson batch spreads across all three packages, which the "
      "published-only count could never do", spread == set(PACKAGES), spread)
t.clean()

print("== the count is a UNION, because a workspace survives publication ==")
t = Tree()
t.script("prog-a", "published", "shipped_prog-a")
t.publish("shipped_prog-a", "prog-a")
t.workspace("shipped_prog-a")             # pruned in place, never deleted
check("a lesson that is both published AND still has its workspace counts ONCE",
      len(t.started("prog-a")) == 1, t.started("prog-a"))
check("...summing the two sets instead would skip a package",
      len(published_bases("prog-a", t.lessons))
      + len(workspace_bases("prog-a", t.lessons, t.ws)) == 2)
t.clean()

print("== attribution: a workspace name carries no program ==")
t = Tree()
t.script("prog-a", "ready", "mine_prog-a")
t.script("prog-b", "ready", "theirs_prog-b")
t.workspace("mine_prog-a")
t.workspace("theirs_prog-b")
check("a workspace is attributed via the folder its script lives in",
      t.started("prog-a") == {"mine_prog-a"}, t.started("prog-a"))
check("...and another program's build does not inflate this one's count",
      len(t.started("prog-a")) == 1 and len(t.started("prog-b")) == 1)
t.clean()

print("== scaffolding is not a lesson ==")
t = Tree()
t.script("prog-a", "ready", "real_prog-a")
t.workspace("real_prog-a")
t.workspace("_run")
t.workspace("_reference")
t.workspace(".render.lock")
check("underscore and dot folders are skipped, as everywhere else in the pipeline",
      t.started("prog-a") == {"real_prog-a"}, t.started("prog-a"))
t.clean()

print("== a script in any stage folder attributes its workspace ==")
t = Tree()
t.script("prog-a", "inbox", "raw_prog-a")
t.script("prog-a", "ready", "ready_prog-a")
t.script("prog-a", "published", "done_prog-a")
for s in ("raw_prog-a", "ready_prog-a", "done_prog-a"):
    t.workspace(s)
check("inbox/, ready/ and published/ all attribute a workspace to the program",
      len(t.started("prog-a")) == 3, t.started("prog-a"))
t.clean()

print("== every answer is a real package ==")
t = Tree()
t.script("prog-a", "ready", "x_prog-a")
check("no offset ever produces a package that does not exist",
      all(t.theme("prog-a", offset=i) in PACKAGES for i in range(30)))
check("the rotation has exactly the three documented packages",
      PACKAGES == ("summit", "horizon", "cadence"), PACKAGES)
t.clean()

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
