#!/usr/bin/env python3
"""check_brand.py — brand colors and the brand typeface, mechanized.

The gap the agent-native adoption brief missed (review, 2026-07-30): on the
template lane, brand is guaranteed BY CONSTRUCTION — every scene instantiates
an scla-* template that already carries the palette and the vendored face. A
freeform build authors its own CSS, and until this gate existed nothing read
what it authored: the proposed brand-truth.md would be prose, and a written
rule is a request (STD-35). The owner's floor for the whole freeform lane is
"use the lesson script, brand colors and brand fonts" — two of those three
had no mechanism.

WHAT IT GRADES — index.html + compositions/*.html, three surfaces: <style>
blocks (including inside <template>), inline style="…" attributes, and SVG
fill=/stroke= attributes.

  off-brand-color   A color literal (#hex / rgb() / rgba() / a color keyword)
                    that is not one of tokens.yml `colors:` at any alpha.
                    Alpha variants of a brand color are brand (the reference
                    build's rgba(255,255,255,.78) body copy is white).
  off-brand-font    A font-family stack that does not LEAD with a brand face
                    (tokens.yml `typography:` display/body). Fallbacks after
                    the brand face are fine; leading with one is not.
  missing-font-asset  An @font-face whose src names a file the workspace does
                    not carry — the face would silently fall back on the
                    render box.

A deliberate exception is declared where it lives:  /* brand-allow: <reason> */
on the same line — stated, never absorbed into a looser gate.

Usage:  python3 check_brand.py <workspace> [--json]
Exit:   0 clean · 1 violations · 2 bad args / nothing to grade
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tokens
from hfp_common import Finding, typed

STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style\s*>", re.S | re.I)
INLINE_RE = re.compile(r"""\bstyle\s*=\s*("([^"]*)"|'([^']*)')""", re.I)
SVG_PAINT_RE = re.compile(r"""\b(?:fill|stroke)\s*=\s*["']([^"']+)["']""", re.I)
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB_RE = re.compile(r"\brgba?\(([^)]+)\)")
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}]+)", re.I)
FONT_FACE_SRC_RE = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", re.I)
VAR_DEF_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;}]+)")
ALLOW_RE = re.compile(r"/\*\s*brand-allow\s*:\s*[^*]+\*/", re.I)

# CSS values that are not colors, or inherit one that is graded elsewhere.
NON_COLORS = {"none", "transparent", "currentcolor", "inherit", "initial",
              "unset", "revert"}
KEYWORDS = {"white": (255, 255, 255), "black": (0, 0, 0)}


def _hex_rgb(h: str):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    if len(h) == 8:
        h = h[:6]
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def brand_rgbs(ws):
    out = set()
    for v in tokens.palette(ws).values():
        rgb = _hex_rgb(v) if str(v).startswith("#") else None
        if rgb:
            out.add(rgb)
    return out


def _colors_in(text: str):
    """Every color literal in a CSS/attribute string -> (repr, rgb|None)."""
    found = []
    for m in HEX_RE.finditer(text):
        found.append((m.group(0), _hex_rgb(m.group(0))))
    for m in RGB_RE.finditer(text):
        parts = [p.strip() for p in re.split(r"[,/ ]+", m.group(1)) if p.strip()]
        try:
            rgb = tuple(int(float(p.rstrip("%")) * 2.55) if p.endswith("%")
                        else int(float(p)) for p in parts[:3])
        except ValueError:
            rgb = None
        found.append((m.group(0)[:40], rgb))
    return found


def check(ws: Path):
    ws = Path(ws)
    files = ([ws / "index.html"] if (ws / "index.html").exists() else []) \
        + sorted(ws.glob("compositions/*.html"))
    if not files:
        return None, [f"no composition HTML under {ws} — nothing to grade"]
    palette = brand_rgbs(ws)
    faces = tokens.brand_faces(ws)
    if not palette or not faces:
        return None, ["tokens.yml carries no colors:/typography: — the brand "
                      "gate has no truth to grade against"]
    problems = []
    graded = {"colors": 0, "fonts": 0, "faces": 0}
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="replace")
        css_blocks = STYLE_RE.findall(raw)
        css = "\n".join(css_blocks)
        # One level of custom-property indirection: --ink: #fff; color: var(--ink)
        vars_ = dict(VAR_DEF_RE.findall(css))

        surfaces = [("style", line) for block in css_blocks
                    for line in block.splitlines()]
        surfaces += [("inline", m.group(2) or m.group(3) or "")
                     for m in INLINE_RE.finditer(raw)]
        for kind, line in surfaces:
            if ALLOW_RE.search(line):
                continue
            for shown, rgb in _colors_in(line):
                graded["colors"] += 1
                if rgb is not None and rgb not in palette:
                    problems.append(Finding(
                        "off-brand-color",
                        f"{f.name}: {shown!r} is not a brand color at any "
                        f"alpha (tokens.yml colors:) — {line.strip()[:80]!r}. "
                        f"Deliberate exceptions declare "
                        f"/* brand-allow: <reason> */ on the line."))
            for m in FONT_FAMILY_RE.finditer(line):
                stack = m.group(1).strip()
                vm = re.match(r"var\((--[\w-]+)\)", stack)
                if vm:
                    stack = vars_.get(vm.group(1), stack)
                lead = tokens.slugify(stack.split(",")[0].strip().strip("'\""))
                graded["fonts"] += 1
                if lead and lead not in faces:
                    problems.append(Finding(
                        "off-brand-font",
                        f"{f.name}: font-family leads with {lead!r} — the "
                        f"brand face is {', '.join(faces)} (tokens.yml "
                        f"typography:). Fallbacks come AFTER the brand face."))
        for kind, line in [("svg", m.group(1)) for m in SVG_PAINT_RE.finditer(raw)]:
            if line.strip().lower() in NON_COLORS or line.startswith("url("):
                continue
            for shown, rgb in _colors_in(line) or \
                    ([(line, KEYWORDS[line.strip().lower()])]
                     if line.strip().lower() in KEYWORDS else []):
                graded["colors"] += 1
                if rgb is not None and rgb not in palette:
                    problems.append(Finding(
                        "off-brand-color",
                        f"{f.name}: SVG paint {shown!r} is not a brand color "
                        f"(tokens.yml colors:)"))
        # @font-face srcs must resolve to vendored files.
        for block in css_blocks:
            for face in re.finditer(r"@font-face\s*{[^}]*}", block, re.S):
                graded["faces"] += 1
                for src in FONT_FACE_SRC_RE.findall(face.group(0)):
                    if src.startswith(("data:", "http")):
                        continue
                    rel = (f.parent / src).resolve() if not src.startswith("/") \
                        else ws / src.lstrip("/")
                    candidates = [rel, ws / src.lstrip("./")]
                    if not any(c.is_file() for c in candidates):
                        problems.append(Finding(
                            "missing-font-asset",
                            f"{f.name}: @font-face src {src!r} does not exist "
                            f"in the workspace — the face silently falls back "
                            f"on the render box"))
    if not graded["colors"] and not graded["fonts"]:
        problems.append(Finding(
            "nothing-graded",
            "no color literal and no font-family found in any composition — "
            "this gate graded NOTHING, which is a failure, never a pass"))
    return graded, problems


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    graded, problems = check(Path(args[0]).resolve())
    if graded is None:
        for p in problems:
            print(f"  !! {p}", file=sys.stderr)
        return 2
    if "--json" in argv:
        print(json.dumps({"pass": not problems, "graded": graded,
                          "problems": problems,
                          "findings": typed(problems)}, indent=2))
    else:
        print(f"[brand] {graded['colors']} color literal(s), "
              f"{graded['fonts']} font stack(s), {graded['faces']} @font-face "
              f"block(s) graded against tokens.yml")
        for p in problems:
            print(f"  !! {p}")
        print("BRAND: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
