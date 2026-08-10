#!/usr/bin/env python3
"""test_ink.py — firing proofs for check_ink.py, the pixel bounds gate.

The repo's own discipline (spikes/ink_bands.py fixture, promoted with the
checker): clean frames must pass, planted ink must fire — and fire the RIGHT
rule. The x=80 case is the one that matters: ink between the safe-area (72px)
and frame-padding (120px) bands must fire padding-breach and NOT
safe-area-breach, proving the two rules discriminate rather than one shadowing
the other.

Frames are generated, not stored: a comb of 1px white lines on navy is
guaranteed local contrast (glyph-edge shaped) with no font dependency.

Run:  python3 tests/test_ink.py   (exit 0 = all pass)
"""
import shutil
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))

from PIL import Image, ImageDraw

import check_ink
import tokens

sys.path.insert(0, str(Path(__file__).resolve().parent))
from firing import fires as _fires

PASS = FAIL = 0
TMP = Path(tempfile.gettempdir()) / "scla-ink-tests"


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def fires(checker, rule, label, cond, detail=""):
    return _fires(check, checker, rule, label, cond, detail)


W, H = tokens.canvas(None)
NAVY = (10, 30, 47)


def frame(name, combs):
    """A navy frame with text-like ink combs at the given (x, y) origins."""
    d = TMP / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    for (x, y) in combs:
        for xi in range(x, x + 40, 2):
            draw.line((xi, y, xi, y + 14), fill=(255, 255, 255))
    img.save(d / "frame.png")
    return d


def zoned_frames(name, active_zones, count=4):
    """A short sampled video with dense text-like ink in selected 3x3 zones."""
    d = TMP / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    pad = int(tokens.frame_padding(None))
    bottom = int(tokens.content_bottom(None))
    fw, fh = W - 2 * pad, bottom - pad
    for frame_index in range(count):
        img = Image.new("RGB", (W, H), NAVY)
        draw = ImageDraw.Draw(img)
        for zone in active_zones:
            row, col = divmod(zone, 3)
            x0 = pad + col * fw // 3 + 120
            y0 = pad + row * fh // 3 + 80
            for xi in range(x0, x0 + 220, 4):
                draw.line((xi, y0, xi, y0 + 110), fill=(255, 255, 255))
        img.save(d / f"frame-{frame_index:02d}.png")
    return d


def rules_of(problems):
    return {getattr(p, "rule_id", "?") for p in (problems or [])}


# Clean: ink only in the primary content field.
_, problems, _ = check_ink.check(frame("clean", [(900, 500), (400, 700)]))
check("a clean frame (ink well inside all bands) passes",
      not problems, str(problems))

# Below content-bottom (960): footer-breach.
_, problems, _ = check_ink.check(frame("footer", [(900, 1000)]))
fires("check_ink", "footer",
      "ink planted at y=1000 (below content-bottom 960) fires footer-breach",
      "footer-breach" in rules_of(problems), str(problems))

# Inside the 72px outer keep-out: safe-area-breach.
_, problems, _ = check_ink.check(frame("safe", [(20, 500)]))
fires("check_ink", "safe-area",
      "ink planted at x=20 (inside the 72px keep-out) fires safe-area-breach",
      "safe-area-breach" in rules_of(problems), str(problems))

# Between safe-area (72) and frame-padding (120): padding-breach ONLY —
# the discrimination proof.
_, problems, _ = check_ink.check(frame("pad", [(80, 500)]))
got = rules_of(problems)
fires("check_ink", "padding",
      "ink planted at x=80 fires padding-breach",
      "padding-breach" in got, str(problems))
check("…and does NOT fire safe-area-breach (rules discriminate)",
      "safe-area-breach" not in got, str(problems))

# A declared chrome region is blanked, and nothing-to-grade fails loud.
d = frame("chrome", [(120, 60)])
_, problems, _ = check_ink.check(d, extra_allow=[(100, 50, 700, 110)])
check("ink inside a declared chrome region is not graded",
      not problems, str(problems))

# Frame use is video-wide: four occupied zones throughout a sampled video is
# the owner-reported "small elements beside a huge blank scene" defect. Five
# zones is the minimum balanced field and remains clean.
_, problems, _ = check_ink.check(zoned_frames("underfilled", [0, 1, 3, 4]))
fires("check_ink", "frame-underfilled",
      "four of nine active content zones across the sampled video FAILS",
      "frame-underfilled" in rules_of(problems), str(problems))
_, problems, _ = check_ink.check(zoned_frames("balanced", [0, 1, 3, 4, 7]))
check("five active content zones across the sampled video passes utilization",
      "frame-underfilled" not in rules_of(problems), str(problems))

empty = TMP / "empty"
shutil.rmtree(empty, ignore_errors=True)
empty.mkdir(parents=True)
reports, problems, _ = check_ink.check(empty)
check("an empty frame set returns None (caller must fail, never pass)",
      reports is None and problems, f"reports={reports} problems={problems}")

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
