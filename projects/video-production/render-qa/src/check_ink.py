#!/usr/bin/env python3
"""check_ink.py — the bounds half of geometry, measured from real pixels.

The three bounds rules (safe-area, frame-padding, content-bottom) all ask one
question: is there INK where there must not be? The retired static box model answered it by
resolving template CSS to boxes — a model that is CONFIDENTLY WRONG on freeform
HTML (281 findings on a build verified clean across 34 stills; HANDOFF-agent-
native-verdict §2). This answers it from the rendered frame — no CSS model, no
font metrics, no framework internals — so it cannot be fooled by flow, flex,
grid, calc(), % or time. Promoted from experiments/agent-native-m2/spikes/
ink_bands.py after its firing fixture validated (clean stills pass; planted
text at y=1000 / x=20 / x=80 fires the right rule and ONLY the right rule).

Ink is LOCAL CONTRAST, not absolute colour: a radial glow or faint grid varies
smoothly; glyph edges do not.

Known limit, stated not hidden: a pixel gate cannot tell label-class chrome
from body content. The brandline sits inside the 72px keep-out BY GRANT of the
design contract, so chrome regions are DECLARED (tokens.yml `chrome-regions`,
printed on every run) — never tolerated by a loosened threshold. Same doctrine
as data-layout-allow-overlap.

  python3 check_ink.py <frame.png|dir> [--tokens-ws <dir>] [--json]
                       [--threshold 60] [--min-px 40] [--allow-region x0,y0,x1,y1]

Exit: 0 clean · 1 ink in a keep-out band · 2 bad args / no frames
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tokens  # noqa: E402
from hfp_common import Finding, typed  # noqa: E402

DEFAULT_THRESHOLD = 60
DEFAULT_MIN_PX = 40
# Same slack the retired geometry gate allowed: the difference between a glyph line
# box and its ink, plus antialiasing at the exact band edge. Without it the
# brandline at left:120px reports a padding-breach from its own left
# antialias column at x=119.
TOLERANCE = 6


def edge_image(img, threshold):
    """Mask of high-local-contrast pixels (glyph and hairline edges)."""
    g = img.convert("L")
    lo = g.filter(ImageFilter.MinFilter(3))
    hi = g.filter(ImageFilter.MaxFilter(3))
    return ImageChops.difference(hi, lo).point(
        lambda v: 255 if v > threshold else 0).convert("L")


def _count(mask, box):
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        return 0, None
    crop = mask.crop(box)
    n = sum(1 for v in crop.getdata() if v)
    if not n:
        return 0, None
    bb = crop.getbbox()
    return n, {"x0": x0 + bb[0], "y0": y0 + bb[1],
               "x1": x0 + bb[2], "y1": y0 + bb[3]}


def grade(path, ws=None, threshold=DEFAULT_THRESHOLD, min_px=DEFAULT_MIN_PX,
          allow=None):
    img = Image.open(path)
    w, h = tokens.canvas(ws)
    if img.size != (w, h):
        img = img.resize((w, h))
    safe = int(tokens.safe_area(ws))
    pad = int(tokens.frame_padding(ws))
    bottom = int(tokens.content_bottom(ws))
    mask = edge_image(img, threshold)
    # DECLARED chrome from tokens.yml `chrome-regions` plus any --allow-region,
    # blanked out of the mask so furniture the design contract grants by name
    # never grades — and always printed, so an exemption is visible.
    d = ImageDraw.Draw(mask)
    for r in (allow or []):
        d.rectangle(r, fill=0)

    def ring(inset, include_bottom=True):
        i = max(0, inset - TOLERANCE)
        boxes = [(0, 0, w, i),
                 (0, i, i, h - i),
                 (w - i, i, w, h - i)]
        if include_bottom:
            boxes.append((0, h - i, w, h))
        return boxes

    counts, extents = {}, {}
    for rule, boxes in (
        ("safe-area-breach", ring(safe)),
        # frame-padding targets PRIMARY CONTENT; the design contract hands the
        # bottom band to label furniture by name, so the bottom edge is excluded
        # here exactly as the retired geometry gate exempted footer chrome.
        ("padding-breach", ring(pad, include_bottom=False)),
        ("footer-breach", [(0, bottom + TOLERANCE, w, h)]),
    ):
        total, ext = 0, None
        for b in boxes:
            n, e = _count(mask, b)
            total += n
            if e:
                ext = e if ext is None else {
                    "x0": min(ext["x0"], e["x0"]), "y0": min(ext["y0"], e["y0"]),
                    "x1": max(ext["x1"], e["x1"]), "y1": max(ext["y1"], e["y1"])}
        counts[rule], extents[rule] = total, ext

    findings = [{"frame": path.name, "rule": r, "px": n, "extent": extents[r]}
                for r, n in counts.items() if n > min_px]
    edge_px = sum(1 for v in mask.getdata() if v)
    return {"frame": path.name, "edge_px": edge_px, "counts": counts,
            "findings": findings}


def check(target: Path, ws=None, threshold=DEFAULT_THRESHOLD,
          min_px=DEFAULT_MIN_PX, extra_allow=None):
    """(reports, problems, allow) — problems is None-safe: an empty frame set
    returns (None, [reason], allow) and the caller must FAIL, never pass."""
    allow = list(tokens.chrome_regions(ws)) + list(extra_allow or [])
    frames = sorted(Path(target).glob("*.png")) if Path(target).is_dir() \
        else [Path(target)]
    if not frames:
        return None, [f"no PNG frames under {target} — nothing to grade is a "
                      f"failure, never a pass"], allow
    reports = [grade(f, ws, threshold, min_px, allow) for f in frames]
    problems = [Finding(f["rule"],
                        f"{f['frame']} [{f['rule']}] {f['px']} ink px in the "
                        f"band, x {f['extent']['x0']}..{f['extent']['x1']} "
                        f"y {f['extent']['y0']}..{f['extent']['y1']}")
                for r in reports for f in r["findings"]]
    return reports, problems, allow


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2

    def opt(name, default, cast=int):
        return cast(argv[argv.index(name) + 1]) if name in argv else default

    ws = opt("--tokens-ws", None, str)
    threshold = opt("--threshold", DEFAULT_THRESHOLD)
    min_px = opt("--min-px", DEFAULT_MIN_PX)
    extra = []
    for i, a in enumerate(argv):
        if a == "--allow-region":
            extra.append(tuple(int(v) for v in argv[i + 1].split(",")))

    reports, problems, allow = check(Path(args[0]), ws, threshold, min_px, extra)
    if reports is None:
        for p in problems:
            print(f"  !! {p}", file=sys.stderr)
        return 2

    if "--json" in argv:
        print(json.dumps({"pass": not problems, "frames": len(reports),
                          "threshold": threshold, "min_px": min_px,
                          "chrome_regions": [list(r) for r in allow],
                          "reports": reports, "problems": problems,
                          "findings": typed(problems)}, indent=1))
    else:
        print(f"[ink] {len(reports)} frame(s), edge threshold {threshold}, "
              f"band floor {min_px}px, tolerance {TOLERANCE}px")
        for r in allow:
            print(f"  declared chrome region (not graded): {tuple(r)}")
        print(f"{'frame':<32}{'edges':>9}{'safe':>8}{'pad':>8}{'footer':>8}")
        for r in reports:
            c = r["counts"]
            print(f"{r['frame']:<32}{r['edge_px']:>9}"
                  f"{c['safe-area-breach']:>8}{c['padding-breach']:>8}"
                  f"{c['footer-breach']:>8}")
        for p in problems:
            print(f"  !! {p}")
        print("INK: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
