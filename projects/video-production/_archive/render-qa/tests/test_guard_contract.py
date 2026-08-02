#!/usr/bin/env python3
"""test_guard_contract.py — preflight.py --json is a frozen wire contract.

`scripts/hyperframe-guard.sh` is the plan-stage guard and the ONLY machine
consumer of `preflight.py --static --json`. Until 2026-07-29 its jq extraction
ran with `2>/dev/null`: if `.output` stopped being a string, jq errored, the
redirect ate the error, the violation string came back EMPTY, and the
crash-fallback did not fire because `.verdict` still parsed — so the guard
exited 0 and reported CLEAN on every failing plan. A silent guard is worse than
no guard, because the pipeline is built to trust it.

This suite runs the guard's REAL jq programs, extracted verbatim from the shell
script between its GUARD_*_JQ markers. It never pastes a copy: a copy is a
second source of truth and the two would drift, which is the exact class of
failure this whole build exists to stop.

Five assertions, engineered against a workspace that FAILS a preflight section
and a workspace that passes clean:

  1. `preflight.py --static --json` runs as a real subprocess with 2>&1
     captured, exactly as the guard invokes it.
  2. stdout's first byte is `{` — catches any stray print() ahead of the JSON.
  3. The guard's real violation program emits a NON-EMPTY string naming the
     failing section — catches the silent-clean failure.
  4. The same pipeline on a CLEAN workspace emits the empty string — catches
     the inverse (renaming `pass` makes every clean section look violated).
  5. Every section key matches ^[a-z_]+$.

Run:  python3 tests/test_guard_contract.py   (exit 0 = all pass)
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
REPO = RQ.parents[2]
GUARD = REPO / "scripts" / "hyperframe-guard.sh"
DESIGN_SYSTEM = RQ.parent / "design-system"

failures = []
TMP = Path(tempfile.mkdtemp())


def check(label, cond, detail=""):
    if cond:
        print(f"  ok  {label}")
    else:
        failures.append(f"{label}  {detail}")
        print(f"  FAIL {label}  {detail}")


# ---------------------------------------------------------------------------
# The guard's two entry points must EXIST at the path it invokes them from.
# The 2026-07-28 layout refactor moved the toolchain to render-qa/src/ and left
# the guard's RQ pointing at render-qa/, so from that day every hook firing
# printed "can't open file" instead of a verdict. It looked like output, so it
# looked alive; it graded nothing. A jq shape contract cannot catch a python
# interpreter that never started.
_rq = re.search(r'^RQ="(.*?)"', GUARD.read_text(), re.M)
_rq_dir = (_rq.group(1).replace("$REPO", str(REPO)) if _rq else "")
for _entry in ("preflight.py", "build_index.py"):
    check(f"the guard's {_entry} path resolves",
          bool(_rq_dir) and Path(_rq_dir, _entry).is_file(),
          f"{_rq_dir}/{_entry} does not exist")


# ---------------------------------------------------------------------------
# Extract the guard's REAL jq programs. Not a copy — the file itself.
def extract_jq(name: str) -> str:
    src = GUARD.read_text()
    m = re.search(rf"# --- {name}_BEGIN ---\n{name}='(.*?)'\n# --- {name}_END ---",
                  src, re.S)
    if not m:
        failures.append(f"could not extract {name} from {GUARD} — the markers "
                        f"the test keys on are gone, so this suite is no longer "
                        f"testing the real guard")
        return ""
    return m.group(1)


VIOL_JQ = extract_jq("GUARD_VIOL_JQ")
SHAPE_JQ = extract_jq("GUARD_SHAPE_JQ")
check("the guard's jq programs are extractable from the shell script",
      bool(VIOL_JQ) and bool(SHAPE_JQ))


# ---------------------------------------------------------------------------
def build_workspace(name: str, scenes: list) -> Path:
    """A minimal but REAL workspace: live design-system compositions, a compiled
    index.html. Without templates check_slots prints a clean PASS on zero
    templates and the capacity/size gates silently no-op — a corpus that proves
    nothing while going green is worse than none."""
    ws = TMP / name
    ws.mkdir(parents=True, exist_ok=True)
    shutil.copytree(DESIGN_SYSTEM / "compositions", ws / "compositions",
                    dirs_exist_ok=True)
    shutil.copy(DESIGN_SYSTEM / "config" / "tokens.yml", ws / "tokens.yml")
    clips, t = [], 0.0
    for fam, variables, dur, narration in scenes:
        i = len(clips) + 1
        v = json.dumps(variables).replace('"', "&quot;")
        clips.append(
            f'<div class="clip" id="scene-{i:02d}" '
            f'data-composition-id="scene-{i:02d}" '
            f'data-composition-src="compositions/{fam}.html" '
            f'data-start="{t:.3f}" data-duration="{dur}" data-track-index="1" '
            f'data-narration="{narration}" data-variable-values="{v}"></div>')
        t += dur
    (ws / "index.html").write_text(
        f'<html><body><div id="root" data-composition-id="main" data-start="0" '
        f'data-duration="{t:.3f}" data-width="1920" data-height="1080">'
        + "".join(clips) + "</div></body></html>")
    return ws


def run_guard_pipeline(ws: Path):
    """Exactly what run_gates() does: subprocess with 2>&1, then the real jq."""
    p = subprocess.run(
        [sys.executable, str(RQ / "src" / "preflight.py"), "--static", "--json", str(ws)],
        capture_output=True, text=True)
    out = p.stdout + p.stderr          # the guard captures 2>&1 into one string
    viol = subprocess.run(["jq", "-r", VIOL_JQ], input=out,
                          capture_output=True, text=True)
    shape = subprocess.run(["jq", "-e", SHAPE_JQ], input=out,
                           capture_output=True, text=True)
    return p.stdout, viol, shape


# A workspace engineered to FAIL: one statement family repeated (variety), a
# heading in sentence case with a terminal period (copy), sub-floor scenes
# (continuity). Several sections fail at once, which is the realistic case.
FAILING = build_workspace("failing", [
    ("scla-title", {"theme": "summit", "eyebrow": "Lesson", "title": "Opening"},
     6.0, "Opening line."),
] + [
    ("scla-statement",
     {"theme": "summit", "statement": "a sentence case statement.",
      "lines": "one|two"},
     3.0, f"Statement {i}.")
    for i in range(1, 9)
] + [
    ("scla-outro", {"theme": "summit", "cta": "Start Today", "next": "Next up"},
     8.0, "Closing line."),
])

CLEAN = RQ.parent / "renders-hyperframes" / (
    "better-decisions-come-from-better-criteria_early-career-boost_2026-07-29")


# ---------------------------------------------------------------------------
# 1 + 2. The subprocess runs, and stdout is JSON from its very first byte.
stdout, viol, shape = run_guard_pipeline(FAILING)
check("preflight --static --json emits JSON from the first byte "
      "(no stray print ahead of it)",
      stdout.lstrip() and stdout.lstrip()[0] == "{",
      repr(stdout[:120]))

payload = None
try:
    payload = json.loads(stdout[stdout.find("{"):])
except (json.JSONDecodeError, ValueError) as exc:
    check("preflight --json is parseable", False, str(exc))

# 3. The guard's REAL jq names the failing section — the silent-clean check.
check("the guard's jq emits a NON-EMPTY violation string on a failing plan",
      viol.returncode == 0 and viol.stdout.strip() != "",
      f"rc={viol.returncode} stdout={viol.stdout[:200]!r} stderr={viol.stderr[:200]!r}")
named = re.findall(r"!! \[([a-z_]+)\]", viol.stdout)
check("the violation string NAMES the failing section(s)",
      bool(named), f"got {viol.stdout[:200]!r}")
if payload:
    really_failed = sorted(k for k, v in payload["sections"].items()
                           if not v.get("pass"))
    check("every failing section appears in the guard's output",
          sorted(set(named)) == really_failed,
          f"jq named {sorted(set(named))}, preflight failed {really_failed}")
check("the shape assertion passes on a well-formed payload",
      shape.returncode == 0, shape.stderr[:200])

# 5. Key discipline: the wire contract pins section names to ^[a-z_]+$.
if payload:
    bad_keys = [k for k in payload["sections"] if not re.fullmatch(r"[a-z_]+", k)]
    check("every section key matches ^[a-z_]+$", not bad_keys, str(bad_keys))
    bad_types = [
        k for k, v in payload["sections"].items()
        if not isinstance(v.get("pass"), bool) or not isinstance(v.get("output"), str)]
    check("sections[].pass is a bool and sections[].output is a string",
          not bad_types, str(bad_types))


# ---------------------------------------------------------------------------
# 4. The inverse: a CLEAN workspace must emit the EMPTY string. Renaming `pass`
#    would make every clean section look violated, which is just as wrong.
if CLEAN.is_dir():
    c_stdout, c_viol, c_shape = run_guard_pipeline(CLEAN)
    check("the guard's jq emits the EMPTY string on a clean plan",
          c_viol.returncode == 0 and c_viol.stdout.strip() == "",
          f"rc={c_viol.returncode} stdout={c_viol.stdout[:300]!r}")
    check("the shape assertion also passes on the clean plan",
          c_shape.returncode == 0, c_shape.stderr[:200])
else:
    print(f"  ~~  clean-plan half SKIPPED: {CLEAN.name} is not on disk "
          f"(workspaces are gitignored). The failing half still ran.")


# ---------------------------------------------------------------------------
# The shape assertion must actually REJECT a drifted payload — otherwise it is
# decoration. This is the specific drift that used to pass silently.
DRIFTED = json.dumps({"verdict": "FAIL", "sections": {
    "variety": {"pass": False, "output": ["a", "list", "not", "a", "string"]}}})
r = subprocess.run(["jq", "-e", SHAPE_JQ], input=DRIFTED,
                   capture_output=True, text=True)
check("the shape assertion REJECTS sections[].output that stopped being a string",
      r.returncode != 0, f"rc={r.returncode}")
RENAMED = json.dumps({"verdict": "FAIL", "sections": {
    "variety": {"passed": False, "output": "x"}}})
r = subprocess.run(["jq", "-e", SHAPE_JQ], input=RENAMED,
                   capture_output=True, text=True)
check("the shape assertion REJECTS a renamed `pass` key",
      r.returncode != 0, f"rc={r.returncode}")
BADKEY = json.dumps({"verdict": "FAIL", "sections": {
    "Variety-Check": {"pass": False, "output": "x"}}})
r = subprocess.run(["jq", "-e", SHAPE_JQ], input=BADKEY,
                   capture_output=True, text=True)
check("the shape assertion REJECTS a section key outside ^[a-z_]+$",
      r.returncode != 0, f"rc={r.returncode}")

shutil.rmtree(TMP, ignore_errors=True)
if failures:
    print(f"\nFAIL ({len(failures)})")
    sys.exit(1)
print("test_guard_contract: the plan-stage guard cannot go silently clean")
