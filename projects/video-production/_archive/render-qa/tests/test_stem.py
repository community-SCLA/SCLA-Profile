#!/usr/bin/env python3
"""Fixture tests for stem.py — working names carry NO date.

The module used to enforce a one-date rule: every artifact carried a date
meaning "most recent action," restamped at each transition. That rule was
dropped on 2026-07-29 (decisions/log.md) because a name that moves cannot be
used as a lock — the same lesson ended up holding two build workspaces,
`..._2026-07-28` and `..._2026-07-29`, since a rebuild restamped its way into
a second directory instead of reusing the first.

Now: a working artifact is named for its base alone, so `mkdir <base>` is the
build mutex. Only a delivered MP4 carries a date, and it is the render date,
frozen at publish.

Each case below attacks one of the two things that must hold: `base()` is
tolerant enough that legacy dated names still resolve (no flag day), and
`check()` is strict enough that a NEW dated working name is rejected.

Run:  python3 tests/test_stem.py   (exit 0 = all pass)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from stem import (StemError, base, check, date, delivered,  # noqa: E402
                  is_canonical)

BASE = "better-decisions-come-from-better-criteria_early-career-boost"
# Legacy names still on disk when the convention was dropped.
LEGACY = BASE + "_2026-07-06"
# What the HyperFrames CLI actually emits for a build.
RENDERED = BASE + "_2026-07-28_18-49-26.mp4"

failures = []


def ok(label, got, want):
    if got != want:
        failures.append(f"{label}: got {got!r}, want {want!r}")


def raises(label, fn, *a, **kw):
    try:
        fn(*a, **kw)
    except StemError:
        return
    except Exception as exc:                       # wrong exception type
        failures.append(f"{label}: raised {type(exc).__name__}, want StemError")
        return
    failures.append(f"{label}: no StemError raised")


# --- a working name is its own base ---------------------------------------
ok("base of a base", base(BASE), BASE)
ok("is_canonical on a base", is_canonical(BASE), True)
ok("no date on a working name", date(BASE), None)

# --- tolerance: every legacy shape resolves to the same identity ----------
# This is what let the convention be dropped without renaming the world in
# one transaction — a dated name still keys correctly while it exists.
ok("base strips a legacy date", base(LEGACY), BASE)
ok("base strips date+clock", base(RENDERED), BASE)
ok("base is idempotent", base(base(RENDERED)), BASE)
ok("one identity across every shape",
   len({base(s) for s in (BASE, LEGACY, RENDERED, BASE + "_2026-08-01")}), 1)

# --- strictness: a NEW dated working name is a defect ---------------------
ok("is_canonical rejects a dated name", is_canonical(LEGACY), False)
ok("is_canonical rejects renderer output", is_canonical(RENDERED), False)
ok("check rejects a dated name", check(LEGACY)[0], False)
ok("check accepts a base", check(BASE), (True, BASE))

# --- accepts paths, filenames and trailing slashes ------------------------
ok("path", base(f"/a/b/{BASE}/"), BASE)
ok("txt suffix", base(BASE + ".txt"), BASE)
ok("mp4 suffix", base(RENDERED), BASE)

# --- delivered() is the one remaining naming transition -------------------
ok("delivered adds the render date", delivered(BASE, "2026-07-29"),
   BASE + "_2026-07-29")
ok("delivered replaces, never appends", delivered(LEGACY, "2026-07-29"),
   BASE + "_2026-07-29")
ok("delivered is idempotent",
   delivered(delivered(BASE, "2026-07-29"), "2026-07-29"), BASE + "_2026-07-29")
ok("delivered preserves base", base(delivered(BASE, "2026-07-29")), BASE)
ok("delivered survives renderer output", delivered(RENDERED, "2026-07-29"),
   BASE + "_2026-07-29")
raises("delivered rejects a bad date", delivered, BASE, "07/29/2026")

# --- names with no usable base --------------------------------------------
raises("empty rejected", base, "")
raises("bare date rejected", base, "2026-07-06")
raises("bare clock rejected", base, "18-49-26")

# --- a date-like segment INSIDE a title is not stripped -------------------
# Only trailing segments go; otherwise a legitimate title could be eaten.
ok("mid-name date survives", base("title_2026-07-06_program"),
   "title_2026-07-06_program")

if failures:
    print(f"FAIL ({len(failures)})")
    for f in failures:
        print("  " + f)
    sys.exit(1)
print("test_stem: all pass")
