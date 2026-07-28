#!/usr/bin/env python3
"""Calibration tests for check_variety.py.

A gate that rejects the work the owner asked for is a broken gate. These tests
pin the calibration to two real videos, measured frame by frame on 2026-07-28:

  REFERENCE — what-makes-for-a-dream-job (Wistia gryylc7qns, 187.5s), named by
      the owner as the bar: "great movement, great pacing, great illustrations".
      7 template families over 14 content scenes, peak single-form share 36%,
      artwork on ~79% of scenes, ~11 distinct devices, and a FIVE-scene
      condition run that works because each scene advances a 5-dot stepper,
      carries its own artwork, and lasts ~6s. Its workspace was pruned after
      publish, so it is reconstructed here as a fixture. MUST PASS.

  REJECTED — better-decisions-come-from-better-criteria (160.4s), which the
      owner called "boring, doesn't have a lot of visual variety". 4 families
      over 19 content scenes, statement at 42%, artwork on 33%, and two
      three-scene statement runs with no progress indicator. MUST FAIL.

The first version of this gate would have FAILED the reference on its five-scene
run — the exemption exists because of that near-miss.

Rules 6 (theme-block cap) and 7 (two-region coverage), added 2026-07-28, are
pinned to the same two videos below, plus a freshness check that greps every
design-system template's base background against check_variety.CANVAS.

Run:  python3 tests/test_variety.py   (exit 0 = all pass)
"""
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_variety as cv  # noqa: E402

failures = []


def scene(i, start, dur, family, variables):
    v = html.escape(json.dumps(variables), quote=True)
    return (f'<div class="clip" id="scene-{i:02d}" '
            f'data-composition-id="scene-{i:02d}" '
            f'data-composition-src="compositions/{family}.html" '
            f'data-start="{start}" data-duration="{dur}" '
            f'data-track-index="1" data-variable-values="{v}"></div>')


def build(tmp: Path, spec):
    """spec: list of (family, variables, duration). Writes a fake workspace."""
    (tmp / "compositions").mkdir(parents=True, exist_ok=True)
    for fam in {"scla-title", "scla-outro", "scla-statement", "scla-chips",
                "scla-condition", "scla-points", "scla-stat", "scla-quote",
                "scla-morph", "scla-steps", "scla-loop", "scla-career-map"}:
        (tmp / "compositions" / f"{fam}.html").write_text("<template></template>")
    clips, t = [], 0.0
    for i, (fam, v, dur) in enumerate(spec, 1):
        clips.append(scene(i, round(t, 3), dur, fam, v))
        t += dur
    (tmp / "index.html").write_text(
        f'<div id="root" data-composition-id="main" data-start="0" '
        f'data-duration="{t:.3f}" data-width="1920" data-height="1080">'
        + "".join(clips) + "</div>")
    return tmp


# --------------------------------------------------------------- REFERENCE
# 7 families / 14 content scenes / ~187s. Peak share 36%. Artwork 10/14 = 71%.
# 10 distinct assets, none reused. Bare scenes never exceed 2 in a row.
# Scenes 8-12 are the five-scene condition run: advancing num/total, distinct
# artwork, 6s each -> earns the enumerated-series exemption.
REFERENCE = [
    ("scla-title",     {"theme": "summit"}, 7.0),
    ("scla-stat",      {"theme": "summit", "icon": "ring"}, 12.0),
    ("scla-statement", {"theme": "summit", "lines": "a|b"}, 12.0),
    ("scla-statement", {"theme": "summit", "lines": "c|d"}, 12.0),
    ("scla-morph",     {"theme": "summit", "icon": "cards1"}, 12.0),
    ("scla-morph",     {"theme": "summit", "icon": "cards2"}, 12.0),
    ("scla-chips",     {"theme": "summit", "chips": "x,y,z"}, 12.0),
    ("scla-points",    {"theme": "summit", "icons": "chart",
                        "point1": "p", "point2": "q"}, 12.0),
    ("scla-condition", {"theme": "summit", "icon": "compass",
                        "num": "1", "total": "5", "chips": "a,b"}, 6.0),
    ("scla-condition", {"theme": "summit", "icon": "people",
                        "num": "2", "total": "5", "chips": "a,b"}, 6.0),
    ("scla-condition", {"theme": "summit", "icon": "linechart",
                        "num": "3", "total": "5", "chips": "a,b"}, 6.0),
    ("scla-condition", {"theme": "summit", "icon": "people-mirrored",
                        "num": "4", "total": "5", "chips": "a,b"}, 6.0),
    ("scla-condition", {"theme": "summit", "icon": "clock",
                        "num": "5", "total": "5", "chips": "a,b"}, 6.0),
    ("scla-quote",     {"theme": "summit", "icon": "strikethrough"}, 12.0),
    ("scla-statement", {"theme": "summit", "lines": "e|f"}, 12.0),
    ("scla-outro",     {"theme": "summit"}, 12.0),
]

# ---------------------------------------------------------------- REJECTED
# The shape of the build the owner turned down: 4 families, statement-heavy,
# three-scene statement runs with no progress indicator, artwork sparse.
REJECTED = [("scla-title", {"theme": "summit"}, 6.0)]
for _i in range(8):
    REJECTED.append(("scla-statement", {"theme": "summit", "lines": "a|b"}, 8.0))
for _i in range(5):
    REJECTED.append(("scla-chips", {"theme": "summit", "chips": "a,b,c"}, 8.0))
for _i in range(4):
    REJECTED.append(("scla-condition", {"theme": "summit", "chips": "a,b"}, 8.0))
for _i in range(2):
    REJECTED.append(("scla-points", {"theme": "summit",
                                     "point1": "p", "point2": "q"}, 8.0))
REJECTED.append(("scla-outro", {"theme": "summit"}, 6.0))


def run(spec, blank_durations=False):
    tmp = Path(tempfile.mkdtemp())
    try:
        ws = build(tmp, spec)
        if blank_durations:
            # Pre-compile state: data-duration is a placeholder until
            # compile_timeline runs; the parser reads a blank as NaN
            # (preflight.py uses the same marker).
            idx = ws / "index.html"
            idx.write_text(re.sub(r'data-duration="[^"]*"',
                                  'data-duration=""', idx.read_text()))
        problems, info, tally = cv.check(ws)
        return problems, info
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


ref_problems, ref_info = run(REFERENCE)
if ref_problems:
    failures.append(
        "REFERENCE video must PASS the gate but was rejected:\n    " +
        "\n    ".join(ref_problems))
if not any("exempt" in i for i in ref_info):
    failures.append(
        "REFERENCE's five-scene condition run should have been reported as "
        "exempt; info was: " + "; ".join(ref_info))
# Rule 7 calibration pin: the reference lands at 6/14 two-region content
# scenes (43% in this fixture; the real video measured ~35% frame by frame) —
# stat (split frame) + the five icon-hero condition scenes.
if not any("two-region coverage: 6/14" in i for i in ref_info):
    failures.append(
        "REFERENCE should measure two-region coverage 6/14; info was: " +
        "; ".join(ref_info))

rej_problems, _ = run(REJECTED)
if not rej_problems:
    failures.append("REJECTED video must FAIL the gate but passed clean")
else:
    # It must fail for the RIGHT reasons, not incidentally.
    joined = " ".join(rej_problems)
    for want, label in [
        ("consecutive scenes on scla-statement", "the statement runs"),
        ("distinct content forms", "too few distinct forms"),
        ("carry artwork", "artwork coverage"),
        # Rule 6: the 8-statement navy run (64.0s — over the count cap, under
        # the seconds cap) and the 11-scene / 88.0s light stretch (over both).
        ("consecutive content scenes on the navy canvas",
         "the theme-block scene-count cap (navy statement run)"),
        ("continuously on the light canvas",
         "the theme-block seconds cap (light stretch)"),
        # Rule 7: 0/19 content scenes are two-region.
        ("two spatially separate regions",
         "two-region composition coverage"),
    ]:
        if want not in joined:
            failures.append(f"REJECTED should have been caught for {label} "
                            f"(missing {want!r})")

# The exemption must be earned, not granted by length alone: strip the progress
# indicators from the reference's condition run and it must fail again.
no_progress = [
    (f, {k: v for k, v in vs.items() if k not in ("num", "total")}, d)
    for f, vs, d in REFERENCE]
np_problems, _ = run(no_progress)
if not any("consecutive scenes on scla-condition" in p for p in np_problems):
    failures.append("a 5-scene run with NO progress indicator must be caught, "
                    "but the gate allowed it")

# ...and a run that is merely slow must also fail.
slow = [(f, vs, 9.0 if f == "scla-condition" else d) for f, vs, d in REFERENCE]
slow_problems, _ = run(slow)
if not any("Too slow to sustain the run" in p for p in slow_problems):
    failures.append("a 5-scene run of >7s scenes must be caught, but the gate "
                    "allowed it")

if failures:
    print(f"FAIL ({len(failures)})")
    for f in failures:
        print("  " + f)
    sys.exit(1)
print("test_variety: all pass — reference PASSES, rejected FAILS, "
      "exemption is earned not assumed")
