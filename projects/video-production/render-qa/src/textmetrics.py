#!/usr/bin/env python3
"""textmetrics.py — how wide a string actually renders in Proxima Nova.

check_capacity.py needs to know whether "Different learning opportunities" fits
a 240px card. Estimating from a characters-per-line ratio is guesswork that
drifts per weight and per string; measuring is exact and costs nothing.

The advance widths live in design-system/assets/fonts/metrics.json, generated
once from the vendored woff2 files and committed. That keeps the gate free of a
runtime font dependency (fontTools + brotli are needed to REGENERATE the file,
never to read it). Regenerate when the fonts change:

    python3 -c "import re,pathlib; \
exec(pathlib.Path('textmetrics.py').read_text().split('# REGEN')[1].split('\"\"\"')[1])"

(The old one-liner here grepped `/^REGEN/` against a line that begins `# REGEN`,
so it matched nothing, ran an empty program, and reported success — which is
why `lineHeight` appeared to regenerate and did not, 2026-07-29.)

Validated against PIL's own rasteriser at generation time to <0.05px on every
weight. Kerning is not modelled — Proxima's kern pairs move a line by well under
a pixel at these sizes, far inside the wrap margin the caller works with.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

# src/ -> render-qa/ -> video-production/
METRICS = (Path(__file__).resolve().parents[2]
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


def normal_line_height(weight=400) -> float:
    """`line-height: normal` as a multiple of font-size, from the real font.

    Chrome resolves `normal` from the font's hhea ascent/descent/lineGap (OS/2
    USE_TYPO_METRICS is off on this kit), which puts Proxima at 1.404/1.447/
    1.477 by weight. boxmodel.py assumed 1.2 until 2026-07-29 and therefore
    under-measured the height of every block that does not set line-height
    explicitly — by 20% on a 44px chip, which is how four wrapped chip rows
    were modelled as ending 43px higher than they really do, clear of a footer
    they in fact ran through.
    """
    m = _metrics()[_weight_key(weight)]
    # Older metrics.json predates this key; 1.2 keeps callers running rather
    # than crashing, and the accessor test below fails loudly if it is missing.
    return float(m.get("lineHeight") or 1.2)


def advance(ch: str, weight=400) -> float:
    """Advance width of one character, as a fraction of font-size."""
    table = _metrics()[_weight_key(weight)]["advance"]
    # Unknown glyph -> 'n', a solid mid-width stand-in rather than a zero that
    # would silently under-measure a string containing it.
    return table.get(ch, table.get("n", 0.5))


def width(text: str, size: float, weight=400, letter_spacing_em=0.0,
          uppercase=False) -> float:
    """Rendered width in px of `text` at `size`px.

    letter_spacing_em and uppercase both matter: the label class in the design contract is
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
    # `line-height: normal` — what the browser uses when the CSS says nothing.
    # Chrome derives it from hhea ascent/descent/lineGap unless OS/2
    # USE_TYPO_METRICS (fsSelection bit 7) is set, which it is not on this kit.
    # Proxima lands at 1.40-1.48 depending on weight, NOT the 1.2 the box model
    # assumed until 2026-07-29 — a 17-23% under-measure of every un-line-heighted
    # block, which is most of them.
    hhea = f["hhea"]
    out[str(w)] = {
        "upem": upem,
        "lineHeight": round(
            (hhea.ascent - hhea.descent + hhea.lineGap) / upem, 5),
        "advance": adv,
    }
(d / "metrics.json").write_text(json.dumps(out, indent=1, sort_keys=True))
"""
