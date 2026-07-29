#!/usr/bin/env python3
"""tokens.py — frame.md's frontmatter, LOADED. The design spec stops describing
the gates and starts being them.

Before 2026-07-29 frame.md was 675 lines that nothing read. Its frontmatter is
real YAML, but every normative number in it was hand-copied into a checker under
a "keep in sync" comment (check_text.py: `BODY_FLOOR = 32  # frame.md
frontmatter typography.min-size — normative, keep in sync`). Nothing verified
the copy. So `spacing.frame-padding: "120px"` — a safe margin declared in the
spec since the system was built — was enforced by exactly nothing, and a
career-map card ran straight through the footer on the 2026-07-28 build.

This module makes the frontmatter the loaded source of truth. A checker imports
its floors from here; changing a number in frame.md changes the gate. There is
no second copy to drift.

Resolution order for frame.md (a workspace carries its own copy, and that copy
is what its build was authored against):
    <workspace>/frame.md  ->  design-system/frame.md

Usage:  python3 tokens.py [workspace]        # print the loaded token set
Exit:   0 loaded · 2 frame.md missing or unparseable
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DESIGN_SYSTEM = Path(__file__).resolve().parent.parent / "design-system"
_CACHE: dict[str, dict] = {}


# --------------------------------------------------------------------------
# Frontmatter parsing
# --------------------------------------------------------------------------
def _split_frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        raise ValueError("frame.md has no YAML frontmatter block")
    return m.group(1)


def _parse_yaml(src: str) -> dict:
    """PyYAML when available, else a small parser for the shape we own.

    The fallback exists so a CI runner without PyYAML fails the *content*, never
    the *import* — a gate that crashes is worse than a gate that is absent, and
    both are worse than one that just works.
    """
    try:
        import yaml  # noqa: PLC0415
        return yaml.safe_load(src) or {}
    except ImportError:
        pass

    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw in src.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key, rest = key.strip(), rest.strip()
        # Strip trailing comments, but never inside a quoted scalar ("#0d2437").
        if rest[:1] in ('"', "'"):
            q = rest[0]
            end = rest.find(q, 1)
            rest = rest[: end + 1] if end != -1 else rest
        elif "#" in rest:
            rest = rest.split("#", 1)[0].strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if not rest:
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
            continue
        parent[key] = _scalar(rest)
    return root


def _scalar(text: str):
    if text[:1] in ('"', "'") and text[-1:] == text[:1] and len(text) > 1:
        return text[1:-1]
    if text.startswith("["):
        inner = text.strip("[]")
        return [_scalar(p.strip()) for p in inner.split(",") if p.strip()]
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def frame_path(ws=None) -> Path:
    """The frame.md that governs this build — the workspace's own copy first."""
    if ws:
        local = Path(ws) / "frame.md"
        if local.is_file():
            return local
    return DESIGN_SYSTEM / "frame.md"


def load(ws=None) -> dict:
    path = frame_path(ws)
    key = str(path)
    if key not in _CACHE:
        _CACHE[key] = _parse_yaml(_split_frontmatter(
            path.read_text(encoding="utf-8", errors="replace")))
    return _CACHE[key]


def px(value, default=None) -> float:
    """`120`, `"120px"`, `120.0` -> 120.0. Tokens may be written either way."""
    if value is None:
        if default is None:
            raise ValueError("no value and no default")
        return float(default)
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"-?[\d.]+", str(value))
    if not m:
        raise ValueError(f"not a length: {value!r}")
    return float(m.group(0))


def canvas(ws=None) -> tuple[int, int]:
    raw = str(load(ws).get("canvas", "1920x1080"))
    w, _, h = raw.partition("x")
    return int(w), int(h)


def min_size(ws=None) -> tuple[float, float]:
    """(body_floor, label_floor) in px — check_text.py's grading floors."""
    ms = (load(ws).get("typography") or {}).get("min-size") or {}
    return px(ms.get("body"), 32), px(ms.get("label"), 20)


def _spacing(ws=None) -> dict:
    return load(ws).get("spacing") or {}


def frame_padding(ws=None) -> float:
    return px(_spacing(ws).get("frame-padding"), 120)


def safe_area(ws=None) -> float:
    """Hard outer keep-out in px. Nothing may cross into the outer band."""
    return px(_spacing(ws).get("safe-area"), 72)


def footer_reserve(ws=None) -> float:
    """Height of the bottom band owned by footer chrome. Content stays above."""
    return px(_spacing(ws).get("footer-reserve"), 120)


def content_bottom(ws=None) -> float:
    """Lowest y a content element may occupy. Derived unless declared."""
    declared = _spacing(ws).get("content-bottom")
    if declared is not None:
        return px(declared)
    return canvas(ws)[1] - footer_reserve(ws)


def summary(ws=None) -> dict:
    body, label = min_size(ws)
    w, h = canvas(ws)
    return {
        "frame_md": str(frame_path(ws)),
        "canvas": {"w": w, "h": h},
        "min_size": {"body": body, "label": label},
        "spacing": {
            "frame_padding": frame_padding(ws),
            "safe_area": safe_area(ws),
            "footer_reserve": footer_reserve(ws),
            "content_bottom": content_bottom(ws),
        },
    }


def main(argv) -> int:
    ws = argv[0] if argv and not argv[0].startswith("--") else None
    try:
        data = summary(ws)
    except (OSError, ValueError) as exc:
        print(f"tokens: cannot load frame.md — {exc}", file=sys.stderr)
        return 2
    if "--json" in argv:
        print(json.dumps(data, indent=2))
        return 0
    print(f"[tokens] loaded from {data['frame_md']}")
    print(f"  canvas          {data['canvas']['w']}x{data['canvas']['h']}")
    print(f"  min-size        body >= {data['min_size']['body']:g}px, "
          f"label >= {data['min_size']['label']:g}px")
    sp = data["spacing"]
    print(f"  frame-padding   {sp['frame_padding']:g}px  (nominal content inset)")
    print(f"  safe-area       {sp['safe_area']:g}px  (HARD outer keep-out)")
    print(f"  footer-reserve  {sp['footer_reserve']:g}px (footer chrome band)")
    print(f"  content-bottom  {sp['content_bottom']:g}px (lowest content y)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
