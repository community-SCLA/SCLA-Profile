#!/usr/bin/env python3
"""check_capacity.py — copy must fit the box the template gives it.

The 2026-07-28 build put two strings into slots too small to hold them, and no
gate had an opinion because every existing text check grades SIZE and
PROVENANCE, never FIT:

  * scene-15 `scla-stat` suffix = "–5 possible paths" — prose in a slot beside a
    300px numeral. The 3 and the label collided; `hyperframes inspect` did see
    it, at severity "info", which the gate discarded (check_layout.py fixes
    that half).
  * scene-16 `scla-career-map` path3 = "Different learning opportunities" —
    506.6px of text in a 240px card, so the card grew to three lines and pushed
    through the footer rule. Nothing saw that at all.

Both are the same defect: a value that cannot fit. That is knowable before any
render, from the template's own CSS and the real font metrics, so this gate runs
at PLAN stage — a builder learns the string is too long while it is still a JSON
edit.

How it works:
  1. Templates bind slots to elements as `getElementById("x").textContent =
     vars.y`, which is regex-extractable.
  2. The element's CSS box (width, padding, font-size/weight, tracking,
     uppercase) is resolved from the template's own <style> block, walking
     ancestors for inherited properties and the nearest explicit width.
  3. textmetrics.py measures the real rendered width in the vendored Proxima
     Nova and word-wraps it the way a browser would.
  4. The resulting line count is graded against the slot's `maxLines` budget,
     declared in the template's variable schema beside the CSS that creates the
     constraint. Undeclared slots get DEFAULT_MAX_LINES.

Usage:  python3 check_capacity.py <workspace> [--json]
Exit:   0 clean · 1 over capacity · 2 bad args
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textmetrics
from hfp_common import Finding, get_attr, parse_scenes, typed

# A slot with no declared budget still gets one — an unenforced slot is how both
# of the 2026-07-28 defects shipped. Three lines is generous for a card or a
# heading and still catches prose stuffed into a label.
DEFAULT_MAX_LINES = 3

BIND_RX = re.compile(
    r'getElementById\(\s*["\']([\w-]+)["\']\s*\)\s*\.textContent\s*=\s*'
    r'(?:String\()?\s*vars\.(\w+)')
RULE_RX = re.compile(r"([^{}]+)\{([^{}]*)\}")
SCHEMA_RX = re.compile(
    r'\{"id"\s*:\s*"([^"]+)"[^}]*?"maxLines"\s*:\s*(\d+)')


class _Tree(HTMLParser):
    """Parent map + id/class for every element, so inherited CSS can be walked."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes: dict[str, dict] = {}
        self._stack: list[dict] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        node = {"tag": tag, "id": a.get("id"),
                "classes": (a.get("class") or "").split(),
                "parent": self._stack[-1] if self._stack else None}
        if node["id"]:
            self.nodes[node["id"]] = node
        if tag not in ("br", "img", "input", "meta", "link", "path", "use"):
            self._stack.append(node)

    def handle_endtag(self, tag):
        if self._stack:
            self._stack.pop()


def _decls(block: str) -> dict:
    out = {}
    for part in block.split(";"):
        k, _, v = part.partition(":")
        if k.strip() and v.strip():
            out[k.strip()] = v.strip()
    return out


def _css_index(html: str):
    """{'#id': decls} and {'.class': decls}, later rules winning."""
    ids, classes = {}, {}
    for style in re.findall(r"<style>(.*?)</style>", html, re.S):
        for sel, block in RULE_RX.findall(style):
            d = _decls(block)
            for one in sel.split(","):
                one = one.strip()
                # Only simple trailing selectors — enough for these templates
                # and honest about what it does not model (combinators,
                # attribute selectors, theme overrides).
                m = re.fullmatch(r"[.#][\w-]+", one)
                if not m:
                    m2 = re.search(r"([.#][\w-]+)$", one)
                    if not m2 or "[" in one:
                        continue
                    one = m2.group(1)
                (ids if one.startswith("#") else classes).setdefault(
                    one[1:], {}).update(d)
    return ids, classes


def _px(value, default=None):
    if value is None:
        return default
    m = re.search(r"-?[\d.]+", str(value))
    return float(m.group(0)) if m else default


def _em(value, default=0.0):
    if value is None:
        return default
    m = re.search(r"(-?[\d.]+)\s*em", str(value))
    return float(m.group(1)) if m else 0.0


def _chain(node):
    while node:
        yield node
        node = node["parent"]


def resolve_box(el_id, tree, id_css, class_css):
    """Rendered text box + type for one element: (avail_px, size, weight,
    tracking_em, uppercase). Returns None when the template does not constrain
    the width, in which case the slot cannot overflow and is not graded."""
    node = tree.nodes.get(el_id)
    if not node:
        return None

    def decls(n):
        d = {}
        for c in n["classes"]:
            d.update(class_css.get(c, {}))
        if n["id"]:
            d.update(id_css.get(n["id"], {}))
        return d

    own = decls(node)
    size = weight = tracking = None
    upper = False
    for n in _chain(node):
        d = decls(n)
        if size is None and "font-size" in d:
            size = _px(d["font-size"])
        if weight is None and "font-weight" in d:
            weight = _px(d["font-weight"])
        if tracking is None and "letter-spacing" in d:
            tracking = _em(d["letter-spacing"])
        if not upper and d.get("text-transform", "").startswith("uppercase"):
            upper = True

    # Nearest explicit width, minus the horizontal padding between it and here.
    avail = None
    pad = 0.0
    for n in _chain(node):
        d = decls(n)
        p = d.get("padding")
        if p:
            parts = p.split()
            side = parts[1] if len(parts) > 1 else parts[0]
            pad += 2 * (_px(side) or 0)
        pad += (_px(d.get("padding-left"), 0) or 0)
        pad += (_px(d.get("padding-right"), 0) or 0)
        w = _px(d.get("width")) if "width" in d else None
        if w:
            avail = w - pad
            break
    if not avail or avail <= 0:
        return None
    return (avail, size or 32.0, weight or 400, tracking or 0.0, upper)


def check(ws: Path):
    findings = []
    index = ws / "index.html"
    scenes = parse_scenes(index.read_text(encoding="utf-8", errors="replace"))
    cache: dict[str, tuple] = {}

    for sc in scenes:
        src = get_attr(sc["tag"], "data-composition-src")
        if not src:
            continue
        comp = ws / src
        if not comp.is_file():
            continue
        if src not in cache:
            html = comp.read_text(encoding="utf-8", errors="replace")
            tree = _Tree()
            tree.feed(html)
            ids, classes = _css_index(html)
            # Declared bindings win. Inferring them from
            # `getElementById("x").textContent = vars.y` silently missed every
            # template that binds in a loop — scla-loop's four captions were
            # invisible to this gate, so the 2026-07-29 two-line overflow was
            # never graded at all. A template now says which slot each element
            # renders, beside the CSS that constrains it.
            binds = dict((slot, el) for el, slot in BIND_RX.findall(html))
            for m in re.finditer(r'id="([\w-]+)"[^>]*\sdata-slot="(\w+)"'
                                 r'|data-slot="(\w+)"[^>]*\sid="([\w-]+)"', html):
                el, slot = (m.group(1), m.group(2)) if m.group(1) else (
                    m.group(4), m.group(3))
                binds[slot] = el
            budgets = {s: int(n) for s, n in SCHEMA_RX.findall(html)}
            cache[src] = (tree, ids, classes, binds, budgets)
        tree, ids, classes, binds, budgets = cache[src]

        for slot, value in (sc["variables"] or {}).items():
            el = binds.get(slot)
            if not el or not str(value).strip():
                continue
            box = resolve_box(el, tree, ids, classes)
            if not box:
                continue
            avail, size, weight, tracking, upper = box
            budget = budgets.get(slot, DEFAULT_MAX_LINES)
            lines = textmetrics.wrap_lines(str(value), avail, size, weight,
                                           tracking, upper)
            if len(lines) > budget:
                w = textmetrics.width(str(value), size, weight, tracking, upper)
                findings.append(Finding(
                    "slot-over-maxlines",
                    f"{sc['id']} ({comp.name}) slot {slot!r}: "
                    f"{str(value)!r} renders {w:.0f}px at {size:g}px/"
                    f"{int(weight)} into a {avail:.0f}px box — {len(lines)} "
                    f"lines, budget {budget}. Shorten it to about "
                    f"{_fit_chars(str(value), lines, budget)} characters, or "
                    f"use a form built for a longer line."))
    return findings


def _fit_chars(value, lines, budget) -> int:
    """Roughly how many characters would fit the budget — actionable guidance,
    not a second gate."""
    if not lines:
        return len(value)
    return max(4, int(len(value) * budget / len(lines)))


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    ws = Path(args[0]).resolve()
    findings = check(ws)
    if "--json" in argv:
        print(json.dumps({"pass": not findings, "problems": findings,
                          "findings": typed(findings)}, indent=2))
    else:
        for f in findings:
            print(f"  !! {f}")
        print("CAPACITY: " + ("PASS" if not findings
                              else f"FAIL ({len(findings)})"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
