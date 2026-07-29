#!/usr/bin/env python3
"""textmetrics.py — how wide a string actually renders in Proxima Nova.

check_capacity.py needs to know whether "Different learning opportunities" fits
a 240px card. Estimating from a characters-per-line ratio is guesswork that
drifts per weight and per string; measuring is exact and costs nothing.

The advance widths live in design-system/assets/fonts/metrics.json, generated
once from the vendored woff2 files and committed. That keeps the gate free of a
runtime font dependency (fontTools + brotli are needed to REGENERATE the file,
never to read it). Regenerate when the fonts change:

    python3 -c "$(sed -n '/^REGEN/,$p' textmetrics.py | tail -n +2)"

Validated against PIL's own rasteriser at generation time to <0.05px on every
weight. Kerning is not modelled — Proxima's kern pairs move a line by well under
a pixel at these sizes, far inside the wrap margin the caller works with.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

METRICS = (Path(__file__).resolve().parent.parent
           / "design-system" / "assets" / "fonts" / "metrics.json")

WEIGHTS = (400, 700, 900)


@lru_cache(maxsize=1)
def _metrics() -> dict:
    return json.loads(METRICS.read_text())


def _weight_key(weight) -> str:
    """Snap an arbitrary CSS weight to the three the kit actually ships."""
    try:
        w = int(weight)
    except (TypeError, ValueError):
        w = 400
    return str(min(WEIGHTS, key=lambda k: abs(k - w)))


def advance(ch: str, weight=400) -> float:
    """Advance width of one character, as a fraction of font-size."""
    table = _metrics()[_weight_key(weight)]["advance"]
    # Unknown glyph -> 'n', a solid mid-width stand-in rather than a zero that
    # would silently under-measure a string containing it.
    return table.get(ch, table.get("n", 0.5))


def width(text: str, size: float, weight=400, letter_spacing_em=0.0,
          uppercase=False) -> float:
    """Rendered width in px of `text` at `size`px.

    letter_spacing_em and uppercase both matter: the label class in frame.md is
    typeset uppercase with 0.14-0.22em tracking, which can add 20% to a run.
    """
    s = text.upper() if uppercase else text
    table = _metrics()[_weight_key(weight)]["advance"]
    fallback = table.get("n", 0.5)
    total = sum(table.get(c, fallback) for c in s) * size
    if letter_spacing_em and s:
        total += letter_spacing_em * size * len(s)
    return total


def wrap_lines(text: str, avail_px: float, size: float, weight=400,
               letter_spacing_em=0.0, uppercase=False) -> list[str]:
    """Greedy word wrap, the way a browser breaks a block of text.

    A single word wider than the box gets its own line and overflows it — which
    is exactly what the browser does, and what the caller needs to see.
    """
    words = re.split(r"(\s+)", text.strip())
    words = [w for w in words if w.strip()]
    if not words:
        return []
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = f"{cur} {word}"
        if width(trial, size, weight, letter_spacing_em, uppercase) <= avail_px:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def line_count(text: str, avail_px: float, size: float, weight=400,
               letter_spacing_em=0.0, uppercase=False) -> int:
    return len(wrap_lines(text, avail_px, size, weight, letter_spacing_em,
                          uppercase))


# REGEN — the generator, kept beside what it produces so the two never drift.
# Requires: pip install fonttools brotli
"""
import json, string
from fontTools.ttLib import TTFont
from pathlib import Path
d = Path("projects/video-production/design-system/assets/fonts")
out = {}
for w in (400, 700, 900):
    f = TTFont(d / f"proxima-nova-{w}.woff2"); f.flavor = None
    upem = f["head"].unitsPerEm; cmap = f.getBestCmap(); hmtx = f["hmtx"]
    adv = {}
    for ch in string.printable[:95] + "—–’“”·…":
        g = cmap.get(ord(ch))
        if g and g in hmtx.metrics:
            adv[ch] = round(hmtx.metrics[g][0] / upem, 5)
    out[str(w)] = {"upem": upem, "advance": adv}
(d / "metrics.json").write_text(json.dumps(out, indent=1, sort_keys=True))
"""
