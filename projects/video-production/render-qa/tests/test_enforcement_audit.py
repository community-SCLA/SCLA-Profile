#!/usr/bin/env python3
"""test_enforcement_audit.py — the STD-35 auditor's own false negatives.

WHY THIS LIVES HERE. `scripts/check-enforcement.py` is a repo-level script, not
a render-qa gate, so this is off-domain by one folder. It sits here anyway
because `run_tests.py` is the repo's only automated test runner and
`lint-refs.sh` check 11 is the only thing CI invokes — a test filed anywhere
else is a test nothing runs, which is the failure mode this whole build exists
to end.

WHAT IT PINS. On 2026-07-29 the auditor that grades every other doc's claims
was itself under-reporting, in four ways. Each is a silent false negative: the
audit says "0 broken" and a reader trusts it. That is worse than no audit,
because a passing check is read as evidence.

  1. LINTCHECK required whitespace after the filename. Every real citation in
     the repo is backticked — ``lint-refs.sh` check 11` — so 1 of 6 matched and
     five citations of a numbered check went unverified. One of them named a
     check that did not exist at the time.
  2. PATHISH did not match `.jsonl` (or `.tsv`), so an annotation citing a
     ledger read as "names no mechanism".
  3. invokers() scanned a fixed six-file list that omitted two real gate
     runners (the plan-stage guard, retired 2026-08-05, and
     `batch-precheck.sh`).
  4. invokers() matched a filename ANYWHERE in a caller, comments included, so
     a checker merely mentioned in a comment counted as invoked. This is the
     dangerous direction: it manufactures the false safety the script exists to
     detect.

And one false POSITIVE, in the hard-failing direction: bare-keyword parens in
ordinary prose ("→ (gate) → MP4") were read as annotations naming no mechanism.
A spurious BROKEN CLAIM trains readers to wave the audit through.

Run:  python3 tests/test_enforcement_audit.py   (exit 0 = all pass)
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
AUDITOR = REPO / "scripts/check-enforcement.py"

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}\n        {detail}")


spec = importlib.util.spec_from_file_location("check_enforcement", AUDITOR)
ce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ce)

# --- 1. the backticked citation form, which is the only form actually used ---
for text, want in (("`lint-refs.sh` check 11", ["11"]),
                   ("lint-refs.sh check 7", ["7"]),
                   ("`lint-refs.sh` check 6 + CI", ["6"])):
    check(f"LINTCHECK matches {text!r}", ce.LINTCHECK.findall(text) == want,
          f"got {ce.LINTCHECK.findall(text)}")

# ...and the numbers cited have to be numbers lint-refs.sh actually prints.
checks = ce.lint_checks()
check("lint-refs.sh numbers all of its checks, including the test suite",
      "11" in checks, f"discovered {sorted(checks, key=int)}")

# --- 2. ledger extensions resolve ---
for tok in ("published.tsv", "transcript.jsonl", "preflight.py", "review.sh"):
    check(f"PATHISH matches `{tok}`", ce.PATHISH.findall(f"`{tok}`") == [tok],
          f"got {ce.PATHISH.findall(chr(96) + tok + chr(96))}")

# --- 3/4. invokers: the real runners are scanned, comments are not ---
# Driven against a synthetic repo, because in the real one preflight.py invokes
# nearly everything and `setdefault` credits the first caller — so the live map
# cannot distinguish "the guard is scanned" from "the guard is skipped".
tmp = Path(tempfile.mkdtemp(prefix="scla-enf-"))
(tmp / "scripts").mkdir(parents=True)
(tmp / "render-qa").mkdir(parents=True)
(tmp / "scripts/batch-precheck.sh").write_text(
    "#!/bin/sh\n# we should really run check_nothing_at_all.py here\n"
    "python3 check_only_precheck_runs.py \"$1\"\n")
orig_repo, orig_vp = ce.REPO, ce.VP
try:
    ce.REPO, ce.VP = tmp, tmp
    found = ce.invokers()
finally:
    ce.REPO, ce.VP = orig_repo, orig_vp

check("batch-precheck.sh is scanned as a caller",
      "check_only_precheck_runs.py" in found, str(sorted(found)))
check("a checker named ONLY in a comment does not count as invoked",
      "check_nothing_at_all.py" not in found, str(sorted(found)))

# --- 5. prose parentheses are not annotations ---
for prose in ("# render-lessons — refined script → hyperframe → (gate) → MP4",
              "**Owner:** someone@example.org (gates answered in session)",
              "No second human review before publish (gate removed 2026-07-22, "
              "`decisions/log.md`). *(Convention.)*"):
    kinds = [m.group("mech") for m in ce.ANNOTATION.finditer(prose)
             if m.group("mech")]
    check(f"prose paren is not read as a mechanism annotation: {prose[:46]!r}",
          not kinds, f"matched {kinds}")

# ...while the real annotation forms still are.
for real, kind in (("*(Mechanism: `preflight.py`)*", "mech"),
                   ("*(Mechanisms: `check_copy.py`, `check_forms.py`)*", "mech"),
                   ("*(Gate: `lint-refs.sh` check 10)*", "mech"),
                   ("*(Convention.)*", "conv")):
    m = ce.ANNOTATION.search(real)
    check(f"real annotation still parses: {real[:38]!r}",
          m is not None and m.group(kind) is not None, str(m))

# --- 6. the whole audit still comes out clean on the live repo ---
broken, unbacked, backed = ce.grade()
check("the live repo has 0 broken claims", not broken,
      "\n        ".join(f"{b['file']}:{b['line']} {b['problem']}"
                        for b in broken))
check("the gap inventory has real recall (the -/*/| line filter capped it "
      "near 17%)", len(unbacked) > 100, f"{len(unbacked)} unbacked")
check("the most-read normative doc in the repo is graded at all",
      ".claude/skills/render-lessons/SKILL.md" in ce.GRADED, str(ce.GRADED))

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
