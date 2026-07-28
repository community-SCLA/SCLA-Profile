#!/usr/bin/env python3
"""Fixture tests for stem.py — the one-date naming rule.

Each case is an attack on the failure mode the module exists for: the
2026-07-28 review, where a video refined on 2026-07-06 and rendered on
2026-07-28 reached the owner named for the refine date, with the HyperFrames
CLI's own `_<date>_<clock>` suffix stacked on top of it. The rule is that a
stem carries exactly ONE date, meaning the most recent action, and that the
date is therefore never an identity key — `base` is.

Run:  python3 tests/test_stem.py   (exit 0 = all pass)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stem import (StemError, base, date, is_canonical, normalize,  # noqa: E402
                  restamp, split)

REAL = "better-decisions-come-from-better-criteria_early-career-boost_2026-07-06"
# What the HyperFrames CLI actually emitted for that build.
RENDERED = REAL + "_2026-07-28_18-49-26.mp4"

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


# --- the happy path -------------------------------------------------------
ok("split", split(REAL),
   ("better-decisions-come-from-better-criteria_early-career-boost", "2026-07-06"))
ok("base", base(REAL),
   "better-decisions-come-from-better-criteria_early-career-boost")
ok("date", date(REAL), "2026-07-06")
ok("is_canonical", is_canonical(REAL), True)

# --- restamp REPLACES, never appends (the whole point) --------------------
ok("restamp", restamp(REAL, "2026-07-28"),
   "better-decisions-come-from-better-criteria_early-career-boost_2026-07-28")
ok("restamp is idempotent", restamp(restamp(REAL, "2026-07-28"), "2026-07-28"),
   restamp(REAL, "2026-07-28"))
ok("restamp preserves base", base(restamp(REAL, "2026-07-28")), base(REAL))

# --- accepts paths, filenames and trailing slashes ------------------------
ok("path", base(f"/a/b/{REAL}/"), base(REAL))
ok("txt suffix", date(REAL + ".txt"), "2026-07-06")
ok("mp4 suffix", date(REAL + ".mp4"), "2026-07-06")

# --- the malformed names that motivated the module ------------------------
raises("double date rejected", split, RENDERED)
raises("no date rejected", split, "no-date-here_program")
raises("bare date rejected", split, "2026-07-06")
raises("date not final rejected", split, "title_2026-07-06_program")
raises("empty rejected", split, "")
raises("bad --date rejected", restamp, REAL, "07/28/2026")
ok("is_canonical on malformed", is_canonical(RENDERED), False)

# --- normalize repairs what the renderer emits ----------------------------
# Lenient by design: base is everything before the FIRST date, later date and
# clock segments are discarded. This is the ONLY caller-facing leniency.
ok("normalize renderer output", normalize(RENDERED, "2026-07-28"),
   "better-decisions-come-from-better-criteria_early-career-boost_2026-07-28")
ok("normalize is idempotent",
   normalize(normalize(RENDERED, "2026-07-28"), "2026-07-28"),
   normalize(RENDERED, "2026-07-28"))
ok("normalize == restamp on a clean stem",
   normalize(REAL, "2026-07-28"), restamp(REAL, "2026-07-28"))
raises("normalize still needs a date", normalize, "no-date-here_program")

# --- the identity invariant that published.tsv depends on -----------------
# The same lesson wears three stems at once (refine / build / render dates).
# All three must resolve to one key, or publish would double-upload.
stems = [REAL, restamp(REAL, "2026-07-28"), restamp(REAL, "2026-08-01")]
ok("base is stable across restamps", len({base(s) for s in stems}), 1)

if failures:
    print(f"FAIL ({len(failures)})")
    for f in failures:
        print("  " + f)
    sys.exit(1)
print("test_stem: all pass")
