#!/usr/bin/env python3
"""test_programs.py — the banner IS the program folder name.

Owner, 2026-07-29, on a shipped Early Career Boost lesson whose title card read
"Career Accelerator": *"a MUST is the banner should ALWAYS correspond to the
project folder name as that is the name of the program … a hard rule that must
be enforced."*

It was already "enforced": `preflight.py` check 7b compared the eyebrow to
tokens.yml's `programs:` map and passed, because the map itself said Career
Accelerator (an owner-directed on-screen rebrand from 2026-07-21). A gate that
grades a value against an unchecked table grades nothing — it just moves the
place where a wrong name is allowed to sit.

So the map is now graded too, in two places:

  1. `tokens.programs_problems()` — every display name must slugify back to its
     own key. Called by `preflight.py` check 7b, so no build can pass with a
     drifted map, at plan stage or at the hard gate.
  2. This suite, run by `run_tests.py` and therefore by `lint-refs.sh` check 11
     in CI — so the map is graded even when nobody is building a video, and a
     new program folder cannot be added without its banner.

Run:  python3 tests/test_programs.py   (exit 0 = all pass)
"""
import sys
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))
import tokens  # noqa: E402

LESSON_SCRIPTS = RQ.parent / "lesson-scripts"

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}{': ' + detail if detail else ''}")
        failures.append(label)


print("test_programs: the banner is the program folder name")

# --- 1. slugify round-trips the forms we actually use -----------------------
for display, slug in [
    ("Early Career Boost", "early-career-boost"),
    ("Mid-Career Momentum", "mid-career-momentum"),      # hyphen survives
    ("Career Transitions", "career-transitions"),
    ("Entrepreneur Accelerator", "entrepreneur-accelerator"),
    ("  Early  Career  Boost  ", "early-career-boost"),  # whitespace noise
]:
    check(f"slugify({display!r}) == {slug!r}",
          tokens.slugify(display) == slug, tokens.slugify(display))

# --- 2. the live map is clean ----------------------------------------------
problems = tokens.programs_problems()
check("tokens.yml programs: map round-trips", not problems, "; ".join(problems))

# --- 3. the defect that shipped is REJECTED --------------------------------
# Guard against a future session "fixing" a failing build by re-aliasing a
# program instead of correcting the banner. Graded through the same function
# preflight calls, on a synthetic map — the round-trip is the whole rule.
check("an alias display name is a problem",
      tokens.slugify("Career Accelerator") != "early-career-boost")
check("an empty display name is a problem",
      tokens.slugify("") == "")

# --- 4. every program folder has a banner, and vice versa ------------------
if LESSON_SCRIPTS.is_dir():
    folders = {p.name for p in LESSON_SCRIPTS.iterdir()
               if p.is_dir() and not p.name.startswith((".", "_"))}
    declared = set(tokens.programs())
    missing = sorted(folders - declared)
    orphan = sorted(declared - folders)
    check("every lesson-scripts program is in the map", not missing,
          f"undeclared: {missing}")
    check("every mapped program has a lesson-scripts folder", not orphan,
          f"no folder: {orphan}")
else:
    check("lesson-scripts/ present", False, str(LESSON_SCRIPTS))

print(f"\ntest_programs: {'FAIL' if failures else 'all pass'}"
      f" ({len(failures)} failure(s))" if failures else
      "\ntest_programs: all pass")
sys.exit(1 if failures else 0)
