#!/usr/bin/env python3
"""ink_bands.py — the bounds half of check_geometry, measured from real pixels.

check_geometry's three bounds rules (safe-area, frame-padding, content-bottom)
all ask one question: is there INK where there must not be? boxmodel.py answers
it by resolving template CSS to boxes. This answers it from the rendered frame —
no CSS model, no font metrics, no framework internals, and it cannot be fooled
by flow, flex, grid, calc(), % or time.

Ink is LOCAL CONTRAST, not absolute colour: a radial glow or faint grid varies
smoothly; glyph edges do not.

  python3 ink_bands.py <frame.png|dir> [--tokens-ws <dir>] [--json]
                       [--threshold 60] [--min-px 40]

Exit: 0 clean · 1 ink in a keep-out band · 2 bad args
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

# spikes/ -> agent-native-m2/ -> experiments/ -> video-production/
sys.path.insert(
    0, str(Path(__file__).resolve().parents[3] / "render-qa" / "src"))
import tokens  # noqa: E402

DEFAULT_THRESHOLD = 60
DEFAULT_MIN_PX = 40
# Same slack check_geometry.py allows: the difference between a glyph line
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
    # DECLARED chrome, never tolerated by a loosened threshold — same doctrine as
    # data-layout-allow-overlap. The design contract hands the outer band to
    # label-class furniture (brandline, eyebrow, scene index) BY NAME, and a
    # pixel gate cannot tell furniture from content on its own. Until this is a
    # token, the region is passed in and printed, so an exemption is always
    # visible in the output.
    from PIL import ImageDraw
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
        # here exactly as check_geometry exempts footer chrome.
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

    target = Path(args[0])
    frames = sorted(target.glob("*.png")) if target.is_dir() else [target]
    if not frames:
        print("no PNG frames under %s" % target, file=sys.stderr)
        return 2

    allow = []
    for i, a in enumerate(argv):
        if a == "--allow-region":
            allow.append(tuple(int(v) for v in argv[i + 1].split(",")))
    reports = [grade(f, ws, threshold, min_px, allow) for f in frames]
    findings = [f for r in reports for f in r["findings"]]

    if "--json" in argv:
        print(json.dumps({"pass": not findings, "frames": len(frames),
                          "threshold": threshold, "min_px": min_px,
                          "reports": reports, "findings": findings}, indent=1))
    else:
        print(f"[ink-bands] {len(frames)} frame(s), edge threshold {threshold}, "
              f"band floor {min_px}px, tolerance {TOLERANCE}px")
        for r in allow:
            print(f"  declared chrome region (not graded): {r}")
        print(f"{'frame':<28}{'edges':>9}{'safe':>8}{'pad':>8}{'footer':>8}")
        for r in reports:
            c = r["counts"]
            print(f"{r['frame']:<28}{r['edge_px']:>9}"
                  f"{c['safe-area-breach']:>8}{c['padding-breach']:>8}"
                  f"{c['footer-breach']:>8}")
        for f in findings:
            e = f["extent"]
            print(f"  !! {f['frame']} [{f['rule']}] {f['px']} ink px in the band, "
                  f"x {e['x0']}..{e['x1']} y {e['y0']}..{e['y1']}")
        print("INK-BANDS: " + ("PASS" if not findings else f"FAIL ({len(findings)})"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
