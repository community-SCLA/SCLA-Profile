#!/usr/bin/env python3
"""tokens.py — design-system/config/tokens.yml, LOADED. The design spec stops
describing the gates and starts being them.

Before 2026-07-29 this lived in the frontmatter of `frame.md`, 709 lines of
which nothing read. Its frontmatter was real YAML, but every normative number in
it was hand-copied into a checker under a "keep in sync" comment (check_text.py:
`BODY_FLOOR = 32  # tokens.yml typography.min-size — normative, keep
in sync`). Nothing verified the copy. So `spacing.frame-padding: "120px"` — a
safe margin declared in the spec since the system was built — was enforced by
exactly nothing, and a career-map card ran straight through the footer on the
2026-07-28 build.

On 2026-07-29 the file was split: the numbers became `config/tokens.yml` (this
module's source) and the prose became a separate contract doc, which no code
reads. That split is the point — a human document that is also machine
load-bearing gets edited by humans and silently breaks gates. The program
display-name map moved here for the same reason: preflight.py had been parsing
it out of a markdown table.

Resolution order (a workspace carries its own copy, and that copy is what its
build was authored against):
    <workspace>/tokens.yml  ->  design-system/config/tokens.yml

Both a bare YAML document and a `---`-fenced frontmatter block parse, so a
workspace copy stays valid whichever form it was written in.

Usage:  python3 tokens.py [workspace]        # print the loaded token set
Exit:   0 loaded · 2 tokens.yml missing or unparseable
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# src/ -> render-qa/ -> video-production/
DESIGN_SYSTEM = Path(__file__).resolve().parents[2] / "design-system"
_CACHE: dict[str, dict] = {}


# --------------------------------------------------------------------------
# Frontmatter parsing
# --------------------------------------------------------------------------
def _split_frontmatter(text: str) -> str:
    """A bare YAML document, or the frontmatter of a fenced one."""
    if text.lstrip().startswith("---"):
        m = re.match(r"^\s*---\n(.*?)\n---\s*\n", text, re.S)
        if not m:
            raise ValueError("opens with '---' but has no closing fence")
        return m.group(1)
    return text


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
def tokens_path(ws=None) -> Path:
    """The tokens.yml governing this build — the workspace's own copy first."""
    if ws:
        local = Path(ws) / "tokens.yml"
        if local.is_file():
            return local
    return DESIGN_SYSTEM / "config" / "tokens.yml"


def load(ws=None) -> dict:
    path = tokens_path(ws)
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


def _footer_reserve(ws=None) -> float:
    """Height of the bottom band owned by footer chrome. Content stays above.
    Private: no gate reads it directly since the template lane retired
    (2026-08-05) — it exists to derive content_bottom(), which the live gates
    (check_ink, check_fit) do read."""
    return px(_spacing(ws).get("footer-reserve"), 120)


def content_bottom(ws=None) -> float:
    """Lowest y a content element may occupy. Derived unless declared."""
    declared = _spacing(ws).get("content-bottom")
    if declared is not None:
        return px(declared)
    return canvas(ws)[1] - _footer_reserve(ws)


def palette(ws=None) -> dict:
    """name -> hex for every brand color (tokens.yml `colors:`). Consumed by
    check_brand.py, which grades every color literal in a freeform build's CSS
    against this set — the machine-readable half of brand/visual-identity.md
    (whose hexes these mirror; check 6 guards the legacy set)."""
    return {k: str(v) for k, v in (load(ws).get("colors") or {}).items()}


def brand_faces(ws=None) -> list[str]:
    """Normalized allowed typeface names (tokens.yml `typography:` display/
    body). Consumed by check_brand.py: every font-family stack in a freeform
    build must lead with one of these."""
    ty = load(ws).get("typography") or {}
    faces = set()
    for key in ("display", "body"):
        v = str(ty.get(key) or "").strip().strip("'\"")
        if v:
            faces.add(slugify(v))
    return sorted(faces)


def chrome_regions(ws=None) -> list[tuple[int, int, int, int]]:
    """Declared label-chrome rectangles (x0, y0, x1, y1) that the pixel gate
    (check_ink.py) blanks before grading its keep-out bands. The design
    contract hands the outer band to label furniture — brandline, eyebrow —
    BY NAME, and a pixel gate cannot tell furniture from content on its own;
    the region is therefore declared here and printed on every run, never
    tolerated by a loosened threshold (same doctrine as
    data-layout-allow-overlap). tokens.yml key: `chrome-regions`, a list of
    "x0,y0,x1,y1" strings."""
    out = []
    for raw in load(ws).get("chrome-regions") or []:
        parts = [int(px(p)) for p in str(raw).split(",")]
        if len(parts) == 4:
            out.append(tuple(parts))
    return out


def programs(ws=None) -> dict:
    """program-slug -> on-screen display name. The title card's `eyebrow` is
    derived from this, never authored (preflight.py check 7b). Lived as a
    markdown table inside frame.md until 2026-07-29, which meant a checker
    parsed prose."""
    return load(ws).get("programs") or {}


def retired_names() -> list[str]:
    """Names no render may speak or display (tokens.yml `retired-names`).

    Distinct from `programs()`, which only grades the banner: a retired name can
    also sit in a script's narration, which is how "your broader Career
    Accelerator journey" reached synthesized audio in two mid-career-momentum
    lessons after the banner alias had already been reverted. Consumed by
    check_copy.py in workspace mode (narration + on-frame copy) and script mode.

    READ FROM THE SPEC, NEVER THE WORKSPACE COPY — deliberately unlike every
    other accessor here. Layout tokens are per-workspace by design (a build is
    graded against the geometry it was authored under), but a retired name is a
    repo-wide editorial fact with no legitimate per-workspace value. Honouring
    the copy would mean every workspace created before a name was retired
    silently opts out of the ban, which is the exact shape of hole this gate
    exists to close.
    """
    return [str(n) for n in (load(None).get("retired-names") or []) if str(n).strip()]


def slugify(display: str) -> str:
    """Display name -> lesson-scripts folder slug. Lowercase, every run of
    non-alphanumerics collapsed to one hyphen."""
    return re.sub(r"[^a-z0-9]+", "-", str(display).strip().lower()).strip("-")


def programs_problems(ws=None) -> list[str]:
    """The banner rule, mechanized (owner, 2026-07-29 — "a MUST").

    The title card's eyebrow is the program's name, and the program's name is
    the `lesson-scripts/<slug>/` folder the script lives in. So a display name
    is only legal if it slugifies back to its own key: "Mid-Career Momentum" ->
    mid-career-momentum passes, "Career Accelerator" under the key
    early-career-boost does not. That one shipped — a whole Early Career Boost
    lesson banner-labelled Career Accelerator, and every gate passed it, because
    the map was free text and the eyebrow check only compared the eyebrow to the
    map. Checking the eyebrow against an unchecked map checks nothing.

    Returns a list of human-readable problems; empty means the map is clean."""
    problems = []
    for slug, display in sorted((programs(ws) or {}).items()):
        if not str(display).strip():
            problems.append(f"program '{slug}' has an empty display name")
        elif slugify(display) != slug:
            problems.append(
                f"program '{slug}' declares display name {display!r}, which "
                f"slugifies to '{slugify(display)}' — a banner must be the "
                f"program folder's own name, never a rebrand or an alias")
    return problems


def summary(ws=None) -> dict:
    body, label = min_size(ws)
    w, h = canvas(ws)
    return {
        "tokens_file": str(tokens_path(ws)),
        "canvas": {"w": w, "h": h},
        "min_size": {"body": body, "label": label},
        "spacing": {
            "frame_padding": frame_padding(ws),
            "safe_area": safe_area(ws),
            "footer_reserve": _footer_reserve(ws),
            "content_bottom": content_bottom(ws),
        },
    }


def main(argv) -> int:
    ws = argv[0] if argv and not argv[0].startswith("--") else None
    try:
        data = summary(ws)
    except (OSError, ValueError) as exc:
        print(f"tokens: cannot load tokens.yml — {exc}", file=sys.stderr)
        return 2
    if "--json" in argv:
        print(json.dumps(data, indent=2))
        return 0
    print(f"[tokens] loaded from {data['tokens_file']}")
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
