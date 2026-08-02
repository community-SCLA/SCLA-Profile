#!/usr/bin/env python3
"""boxmodel.py — where a template's text actually lands on the 1920x1080 frame.

WHY THIS EXISTS. On 2026-07-29 scene-19 of the criteria lesson shipped with
"Grounded in what you value" printed straight through "Use it on any career
decision". The tooling that was supposed to stop it did not:

  * `check_layout.py` ran the real browser inspector at all 60 sample points and
    returned PASS with zero findings, not even advisory. `hyperframes inspect`
    grades text against its OWN container; two absolutely-positioned siblings
    landing on the same pixels is not a case it models. It never will be — that
    is a design decision upstream, not a bug we can wait out.
  * `check_capacity.py` measured the string correctly (407px of Proxima 700 at
    32px in a 320px box -> 2 lines) and passed it, because the template declared
    no `maxLines` and the default budget is 3. Capacity knows how many lines a
    string takes. It does not know that the second line lands on another
    element.

Both gates were right about their own question and neither owned the real one:
*given the wrapped line count, does this text box intersect anything?* That is
answerable with no browser and no render, from the template's own CSS plus the
real font metrics — so it belongs at plan stage, where a fix is a JSON edit.

This module is the geometry half: it resolves elements to absolute frame boxes.
`check_geometry.py` is the gate that grades them.

WHAT IT MODELS (and what it does not — read this before trusting a PASS):
  * `position: absolute` with left/right/top/bottom/inset, resolved against the
    nearest positioned ancestor. This is how every SCLA template places its
    content, so it is the case that matters.
  * normal-flow block children of a positioned box, stacked vertically with
    margin-top/margin-bottom.
  * `display: flex` rows (children left-to-right, honouring `gap`).
  * `display: grid; place-items: center` (single child centred both axes).
  * shrink-to-fit width for an absolutely-positioned box with no explicit width.
  * text height as wrapped-line-count x line-height, wrapped in the vendored
    Proxima Nova via textmetrics.py.
  * the INK box, not the layout box: a centred one-line caption in a 540px box
    occupies only the glyph run, centred. Grading layout boxes would invent
    collisions that a viewer never sees.

  NOT modelled: floats, tables, inline flow between siblings, transforms,
  writing modes, `calc()`, CSS variables, percentage lengths, attribute-selector
  and combinator rules (theme overrides are colour-only by spec, so skipping
  them is safe). An element this module cannot place is reported as UNPLACED
  rather than silently dropped — a blind spot the caller can see is a blind spot
  that can be closed.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

import textmetrics

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
VOID = {"br", "img", "input", "meta", "link", "hr", "source", "use", "path",
        "polygon", "circle", "rect", "line", "ellipse", "stop"}

# Sub-pixel slack before a flex row is considered full. Font metrics and the
# browser's own rounding differ by well under a pixel; breaking a row on that
# would invent a row and, with it, an overflow that is not there.
TOL_WRAP = 1.0
RULE_RX = re.compile(r"([^{}]+)\{([^{}]*)\}")
LEN_RX = re.compile(r"-?[\d.]+")


class Doc(HTMLParser):
    """The template's element tree plus its stylesheet, indexed for lookup."""

    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.nodes: list[dict] = []
        self.by_id: dict[str, dict] = {}
        self._stack: list[dict] = []
        self._id_css: dict[str, dict] = {}
        self._class_css: dict[str, dict] = {}
        self._tag_css: dict[str, dict] = {}
        self._index_css(html)
        self.feed(html)

    # -- stylesheet ---------------------------------------------------------
    def _index_css(self, html: str) -> None:
        """{'id': decls}, {'class': decls}, {'tag': decls} — later rules win.

        Only simple selectors and simple descendant chains are indexed, keyed on
        the trailing compound. Anything with an attribute selector is skipped
        outright: those are the `#root[data-theme=...]` blocks, which the design contract
        pins to colour only.
        """
        for style in re.findall(r"<style>(.*?)</style>", html, re.S):
            # Strip CSS comments BEFORE the rule regex. A /* ... */ comment
            # containing a colon parses as a declaration, and one sitting inside
            # a block silently displaced #sh-number's `left` — the model read
            # x=0 for an element at left:120 and reported breaches that were
            # not there. A model that mis-measures is worse than no model, so
            # comments die at the door. (2026-07-29.)
            style = re.sub(r"/\*.*?\*/", " ", style, flags=re.S)
            for sel, block in RULE_RX.findall(style):
                d = _decls(block)
                for one in sel.split(","):
                    one = one.strip()
                    if not one or "[" in one or "@" in one or "%" in one:
                        continue
                    tail = one.split()[-1]
                    # pseudo-elements draw decoration, never our text
                    if "::" in tail:
                        continue
                    tail = tail.split(":")[0]
                    if not re.fullmatch(r"[.#]?[\w-]+", tail):
                        continue
                    if tail.startswith("#"):
                        self._id_css.setdefault(tail[1:], {}).update(d)
                    elif tail.startswith("."):
                        self._class_css.setdefault(tail[1:], {}).update(d)
                    else:
                        self._tag_css.setdefault(tail, {}).update(d)

    # -- tree ---------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        node = {
            "tag": tag,
            "id": a.get("id"),
            "classes": (a.get("class") or "").split(),
            "attrs": a,
            "parent": self._stack[-1] if self._stack else None,
            "children": [],
            "text": "",
        }
        if node["parent"] is not None:
            node["parent"]["children"].append(node)
        self.nodes.append(node)
        if node["id"]:
            self.by_id.setdefault(node["id"], node)
        if tag not in VOID:
            self._stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self._stack:
            self._stack.pop()

    def handle_endtag(self, tag):
        """Pop to the matching open tag — never blindly.

        `<circle ...></circle>` is written as a pair in these templates, but
        `circle` is in VOID and was never pushed, so an unconditional pop ate
        `<svg>` and then `<div id="root">`. Everything after scla-stat's ring
        SVG became a child of <body>, was never placed, and the gate reported
        `0 painted boxes` for that template as if it were clean. A gate that
        silently grades nothing is worse than no gate.
        """
        if tag in VOID:
            return
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i]["tag"] == tag:
                del self._stack[i:]
                return

    def handle_data(self, data):
        if self._stack and data.strip():
            self._stack[-1]["text"] += data

    # -- cascade ------------------------------------------------------------
    def decls(self, node: dict) -> dict:
        """Merged declarations for one element (tag, then class, then id)."""
        d = dict(self._tag_css.get(node["tag"], {}))
        for c in node["classes"]:
            d.update(self._class_css.get(c, {}))
        if node["id"]:
            d.update(self._id_css.get(node["id"], {}))
        inline = node["attrs"].get("style")
        if inline:
            d.update(_decls(inline))
        return d


def _decls(block: str) -> dict:
    out = {}
    for part in block.split(";"):
        k, _, v = part.partition(":")
        if k.strip() and v.strip():
            out[k.strip().lower()] = v.strip()
    return out


def _px(value, default=None):
    """`120`, `"120px"`, `-4px` -> float. Percentages and calc() are NOT lengths
    this module can resolve, and return the default rather than a wrong number."""
    if value is None:
        return default
    s = str(value)
    if "%" in s or "calc(" in s or "var(" in s:
        return default
    m = LEN_RX.search(s)
    return float(m.group(0)) if m else default


def _em(value, default=0.0):
    if value is None:
        return default
    m = re.search(r"(-?[\d.]+)\s*em", str(value))
    return float(m.group(1)) if m else default


def _inset(d: dict) -> dict:
    """left/right/top/bottom, with `inset` shorthand expanded."""
    out = {k: _px(d.get(k)) for k in ("left", "right", "top", "bottom")}
    ins = d.get("inset")
    if ins:
        parts = [_px(p) for p in ins.split()]
        if len(parts) == 1:
            parts *= 4
        elif len(parts) == 2:
            parts = [parts[0], parts[1], parts[0], parts[1]]
        elif len(parts) == 3:
            parts = [parts[0], parts[1], parts[2], parts[1]]
        for k, v in zip(("top", "right", "bottom", "left"), parts[:4]):
            if out[k] is None:
                out[k] = v
    return out


def _pad4(d: dict) -> tuple[float, float, float, float]:
    """(top, right, bottom, left) padding, shorthand expanded."""
    top = right = bottom = left = 0.0
    p = d.get("padding")
    if p:
        parts = [_px(x, 0.0) or 0.0 for x in p.split()]
        if len(parts) == 1:
            top = right = bottom = left = parts[0]
        elif len(parts) == 2:
            top = bottom = parts[0]
            right = left = parts[1]
        elif len(parts) == 3:
            top, right, bottom = parts[0], parts[1], parts[2]
            left = parts[1]
        else:
            top, right, bottom, left = parts[:4]
    top += _px(d.get("padding-top"), 0.0) or 0.0
    right += _px(d.get("padding-right"), 0.0) or 0.0
    bottom += _px(d.get("padding-bottom"), 0.0) or 0.0
    left += _px(d.get("padding-left"), 0.0) or 0.0
    return top, right, bottom, left


def _border4(d: dict) -> tuple[float, float, float, float]:
    """(top, right, bottom, left) border WIDTHS.

    A 3px border on a chip is 6px of box on each axis. That is small until it
    is multiplied by four stacked rows, and it is the outer edge — the line the
    viewer actually sees meeting the footer — so it belongs in the box.
    `border: none` and `border: 0` resolve to 0 by _px's own parsing.
    """
    out = {}
    for i, side in enumerate(("top", "right", "bottom", "left")):
        spec = d.get(f"border-{side}") or d.get("border") or ""
        if not spec or "none" in spec:
            out[side] = 0.0
            continue
        head = spec.split()[0] if spec.split() else ""
        out[side] = _px(head, 0.0) or 0.0
    return out["top"], out["right"], out["bottom"], out["left"]


def _pad(d: dict) -> tuple[float, float]:
    """(left, right) horizontal padding — the pair most callers want."""
    _, right, _, left = _pad4(d)
    return left, right


# ---------------------------------------------------------------------------
# Type resolution
# ---------------------------------------------------------------------------
def typeface(doc: Doc, node: dict) -> dict:
    """Inherited type properties for one element."""
    size = weight = tracking = line_height = align = None
    upper = False
    n = node
    while n is not None:
        d = doc.decls(n)
        if size is None and "font-size" in d:
            size = _px(d["font-size"])
        if weight is None and "font-weight" in d:
            weight = _px(d["font-weight"])
        if tracking is None and "letter-spacing" in d:
            tracking = _em(d["letter-spacing"])
        if line_height is None and "line-height" in d:
            line_height = d["line-height"]
        if align is None and "text-align" in d:
            align = d["text-align"].split()[0]
        if not upper and d.get("text-transform", "").startswith("uppercase"):
            upper = True
        n = n["parent"]
    size = size or 32.0
    # `normal` comes from the real vendored font (1.40-1.48 by weight), not the
    # 1.2 this assumed until 2026-07-29 — see textmetrics.normal_line_height.
    default_lh = size * textmetrics.normal_line_height(weight or 400)
    if line_height in (None, "normal"):
        lh = default_lh
    else:
        raw = str(line_height).strip()
        lh = (_px(raw, default_lh) if any(u in raw for u in ("px", "em", "%"))
              else float(raw) * size)
    # A vertical rail label runs DOWN the frame: its inline axis is y, so the
    # box is line-height wide and text-length tall. Modelling it as horizontal
    # would place the box somewhere it never paints.
    wm = None
    n = node
    while n is not None and wm is None:
        wm = doc.decls(n).get("writing-mode")
        n = n["parent"]
    return {"size": size, "weight": weight or 400, "tracking": tracking or 0.0,
            "uppercase": upper, "line_height": lh, "align": align or "left",
            "vertical": bool(wm and wm.startswith("vertical"))}


def is_label_class(doc: Doc, node: dict) -> bool:
    """The design contract's label class: uppercase AND letter-spaced. Mirrors
    check_text.classify() so the two gates cannot disagree about what a label
    is."""
    n = node
    upper = tracked = False
    while n is not None:
        d = doc.decls(n)
        if d.get("text-transform", "").startswith("uppercase"):
            upper = True
        if "letter-spacing" in d:
            tracked = True
        n = n["parent"]
    return upper and tracked


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
class Box:
    __slots__ = ("x", "y", "w", "h")

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = float(x), float(y), float(w), float(h)

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h

    def overlap(self, other: "Box") -> tuple[float, float]:
        """(horizontal, vertical) overlap in px; <=0 on either axis = no hit."""
        return (min(self.right, other.right) - max(self.x, other.x),
                min(self.bottom, other.bottom) - max(self.y, other.y))

    def __repr__(self):
        return (f"Box({self.x:.0f},{self.y:.0f} {self.w:.0f}x{self.h:.0f} "
                f"-> {self.right:.0f},{self.bottom:.0f})")


class Layout:
    """Absolute frame boxes for a template instantiated with one scene's text.

    `texts` maps element id -> the string that element will actually render.
    Elements absent from it fall back to their static HTML text; an element
    whose text resolves to empty is treated as not present (the templates
    `.remove()` their empty slots).
    """

    def __init__(self, doc: Doc, texts: dict, canvas=(1920, 1080)):
        self.doc = doc
        self.texts = texts
        self.canvas = canvas
        self.boxes: dict[int, Box] = {}
        self.unplaced: list[dict] = []
        self._expand_repeats()
        root = doc.by_id.get("root") or (doc.nodes[0] if doc.nodes else None)
        if root is not None:
            self.boxes[id(root)] = Box(0, 0, canvas[0], canvas[1])
            self._place_children(root, self.boxes[id(root)])

    # -- run-time repetition -------------------------------------------------
    def _expand_repeats(self) -> None:
        """Turn a `data-geometry-repeat` prototype into one box per list item.

        The single empty prototype that `data-geometry-proto` gives a sub-beat
        works because sub-beats swap in place: one box, shown one line at a
        time. A chip row is the other shape — N pills of DIFFERENT widths on
        screen at once — and one prototype cannot stand in for it. Before this,
        chips were simply invisible to the gate: scene-17 of who-will-walk
        graded four boxes, all of them chrome, while the four chips the owner
        was looking at ran through the footer.

        A template declares `data-geometry-repeat="<sep>"` on the prototype and
        names the slot with `data-slot`; the prototype is replaced, in place,
        by one clone per item. A prototype may carry structure — scla-statement's
        line is a flex row of a bullet dot and a text span — in which case the
        item text lands on the descendant marked `data-geometry-text` and the
        rest of the subtree is cloned as is, so the bullet still occupies its
        16px of the row. A flat prototype takes the text itself.
        """
        for proto in [n for n in self.doc.nodes
                      if "data-geometry-repeat" in n["attrs"]]:
            parent = proto.get("parent")
            if parent is None or proto not in parent["children"]:
                continue
            sep = proto["attrs"].get("data-geometry-repeat") or ","
            slot = proto["attrs"].get("data-slot")
            raw = str(self.texts.get(slot, "") or "") if slot else ""
            items = [s.strip() for s in raw.split(sep) if s.strip()]
            clones = [self._clone_for(proto, parent, item) for item in items]
            i = parent["children"].index(proto)
            parent["children"][i:i + 1] = clones
            self.doc.nodes = [n for n in self.doc.nodes
                              if n is not proto and not self._within(n, proto)]

    @staticmethod
    def _within(node: dict, ancestor: dict) -> bool:
        cur = node.get("parent")
        while cur is not None:
            if cur is ancestor:
                return True
            cur = cur.get("parent")
        return False

    def _clone_for(self, proto: dict, parent: dict, item: str) -> dict:
        """Deep-copy `proto`, dropping the repeat markers, with `item` as text."""
        STRIP = ("data-slot", "data-geometry-repeat", "data-geometry-proto")

        def copy(src: dict, new_parent: dict | None) -> dict:
            node = dict(src)
            node["attrs"] = {k: v for k, v in src["attrs"].items()
                             if k not in STRIP}
            node["id"] = None
            node["parent"] = new_parent
            node["children"] = []
            node["text"] = ""
            self.doc.nodes.append(node)
            for kid in src["children"]:
                node["children"].append(copy(kid, node))
            return node

        clone = copy(proto, parent)
        # Find the marked text carrier in the CLONE (same walk order as proto).
        target, stack = None, [(proto, clone)]
        while stack:
            src, dst = stack.pop()
            if "data-geometry-text" in src["attrs"]:
                target = dst
                break
            stack.extend(zip(src["children"], dst["children"]))
        (target or clone)["text"] = item
        return clone

    # -- cascade -------------------------------------------------------------
    def _decls(self, node: dict) -> dict:
        """`Doc.decls`, plus any geometry a template applies CONDITIONALLY.

        scla-chips narrows its chip column to `right: 620px` in JavaScript when
        a hero icon is set, reserving the right third of the frame for the
        glyph. Nothing in the CSS says so, so the model placed chips in a
        1680px-wide field the browser had already cut to 1180px — it packed two
        rows where the render produced four, and the fourth ran through the
        footer. That is the module's own stated failure mode ("a box only the
        browser knows about is a box no gate can grade") arriving through an
        inline style instead of a created element.

        A template DECLARES the conditional box with
        `data-geometry-alt-if="<slot>" data-geometry-alt="<css decls>"`, and
        its script reads the same attribute rather than repeating the number —
        so the declaration cannot drift from the behaviour.
        """
        d = self.doc.decls(node)
        gate = node["attrs"].get("data-geometry-alt-if")
        if gate and str(self.texts.get(gate, "") or "").strip():
            d = dict(d, **_decls(node["attrs"].get("data-geometry-alt") or ""))
        return d

    # -- text ---------------------------------------------------------------
    def text_of(self, node: dict) -> str:
        if node["id"] in self.texts:
            return str(self.texts[node["id"]] or "").strip()
        slot = node["attrs"].get("data-slot")
        if slot is not None:
            return str(self.texts.get(slot, "") or "").strip()
        if any(c["tag"] not in VOID for c in node["children"]):
            return ""
        return node["text"].strip()

    def is_present(self, node: dict) -> bool:
        """Whether this element exists on the frame for this scene.

        Templates `.remove()` the furniture belonging to an empty slot — an
        unused step takes its node AND its caption with it. A slot-bound element
        vanishes with its own text; anything else that vanishes with a slot says
        so with `data-present-if="<slot>"`, because a phantom box invents
        collisions and a missing box hides them.
        """
        gate = node["attrs"].get("data-present-if")
        if gate is not None and not str(self.texts.get(gate, "") or "").strip():
            return False
        bound = (node["id"] in self.texts
                 or node["attrs"].get("data-slot") is not None)
        return bool(self.text_of(node)) if bound else True

    def wrapped(self, node: dict, width: float) -> list[str]:
        t = self.text_of(node)
        if not t:
            return []
        f = typeface(self.doc, node)
        return textmetrics.wrap_lines(t, width, f["size"], f["weight"],
                                      f["tracking"], f["uppercase"])

    # -- measurement --------------------------------------------------------
    def _run_length(self, node: dict) -> float:
        """Length of the unwrapped glyph run, along whichever axis it runs."""
        t = self.text_of(node)
        if not t:
            return 0.0
        f = typeface(self.doc, node)
        return textmetrics.width(t, f["size"], f["weight"], f["tracking"],
                                 f["uppercase"])

    def _content_width(self, node: dict) -> float:
        """Shrink-to-fit BORDER-BOX width — text, plus its own padding/border.

        Padding and border were omitted until 2026-07-29, which understated a
        chip pill by 98px (46px padding a side, 3px border a side). Two
        consequences, both live: the flex-wrap packer fitted more chips per row
        than the browser does, and `ink()` then wrapped the label to two lines
        inside a box far too narrow for it. The pill is what a viewer sees, so
        the pill is what gets measured.
        """
        if not self.text_of(node):
            return 0.0
        f = typeface(self.doc, node)
        run = f["line_height"] if f["vertical"] else self._run_length(node)
        d = self._decls(node)
        _, pr, _, pl = _pad4(d)
        _, br, _, bl = _border4(d)
        return run + pl + pr + bl + br

    def _height(self, node: dict, width: float) -> float:
        d = self._decls(node)
        explicit = _px(d.get("height"))
        if explicit is not None:
            return explicit
        if node["tag"] in VOID:
            return 0.0
        if self.text_of(node) and typeface(self.doc, node)["vertical"]:
            return self._run_length(node)
        pt, _, pb, _ = _pad4(d)
        bt, _, bb, _ = _border4(d)
        lines = self.wrapped(node, max(1.0, width - _pad(d)[0] - _pad(d)[1]))
        if lines:
            # Border-box, as above: a padded pill is taller than its glyphs.
            return (len(lines) * typeface(self.doc, node)["line_height"]
                    + pt + pb + bt + bb)
        return pt + self._content_height(node, width) + pb + bt + bb

    def _flow_children(self, node: dict) -> list[dict]:
        return [c for c in node["children"]
                if self.is_present(c)
                and self._decls(c).get("position") not in ("absolute",
                                                              "fixed")]

    def _content_height(self, node: dict, width: float) -> float:
        """Height of the in-flow children, per this element's display mode.

        A flex ROW and a grid are as tall as their tallest child; a block and a
        flex COLUMN are as tall as the stack. Getting this wrong is not
        cosmetic: modelling `#kp-list` (flex column) as a row put all four list
        items at the same y and manufactured four collisions that do not exist.
        """
        d = self._decls(node)
        display = (d.get("display") or "block").split()[0]
        gap = _px(d.get("gap"), 0.0) or 0.0
        kids = self._flow_children(node)
        if not kids:
            return 0.0
        row = display == "flex" and "column" not in (d.get("flex-direction")
                                                     or "row")
        if display == "grid" or row:
            return max(self._height(c, _px(self._decls(c).get("width"))
                                    or width) for c in kids)
        total = 0.0
        for i, c in enumerate(kids):
            cd = self._decls(c)
            total += (_px(cd.get("margin-top"), 0.0) or 0.0)
            total += self._height(c, _px(cd.get("width")) or width)
            total += (_px(cd.get("margin-bottom"), 0.0) or 0.0)
            if display == "flex" and i:
                total += gap
        return total

    # -- placement ----------------------------------------------------------
    def _place_children(self, parent: dict, pbox: Box) -> None:
        pd = self._decls(parent)
        display = (pd.get("display") or "block").split()[0]
        pt, pr, pb, pl = _pad4(pd)
        inner = Box(pbox.x + pl, pbox.y + pt,
                    max(0.0, pbox.w - pl - pr), max(0.0, pbox.h - pt - pb))

        flow = self._flow_children(parent)
        out_of_flow = [c for c in parent["children"]
                       if self.is_present(c)
                       and self._decls(c).get("position") in ("absolute",
                                                                 "fixed")]

        if display == "flex":
            self._place_flex(parent, pd, inner, flow)
        elif display == "grid":
            self._place_grid(parent, pd, inner, flow)
        else:
            cursor = inner.y
            for child in flow:
                cd = self._decls(child)
                cursor += (_px(cd.get("margin-top"), 0.0) or 0.0)
                w = _px(cd.get("width")) or inner.w
                h = self._height(child, w)
                self._commit(child, Box(inner.x, cursor, w, h))
                cursor += h + (_px(cd.get("margin-bottom"), 0.0) or 0.0)

        for child in out_of_flow:
            self._place_absolute(child, pbox)

    def _place_flex(self, parent, pd, inner, flow):
        """flex row and flex column, honouring `gap`, `align-items: center` and
        `flex-wrap: wrap`.

        A ROW child whose main-axis size cannot be resolved — a void element
        sized by its intrinsic aspect, e.g. a logo <img> given only a height —
        makes every later sibling's x unknowable. Those are recorded UNPLACED
        rather than guessed. An invented coordinate produces an invented
        collision, and a gate that cries wolf is a gate that gets switched off.

        WRAP (2026-07-29). Without it a wrapping row was modelled as one
        infinitely long line, so its height was one chip and its overflow was
        always downward-invisible. scla-chips' `#cc-field` is `flex-wrap: wrap`
        at top:470 in a 1080 frame: four long chips stack into four rows and end
        at y≈1000, through the footer band and the brandline. The owner reported
        exactly that ("the points are rendered too low in the frame and violate
        the border padding"), and check_geometry returned PASS — it had never
        seen a chip box at all. Row height is the tallest child in the row, and
        `gap: <row> <column>` is read in that order, as CSS does.
        """
        gap_parts = str(pd.get("gap") or "").split()
        row_gap = _px(gap_parts[0], 0.0) or 0.0 if gap_parts else 0.0
        col_gap = (_px(gap_parts[1], 0.0) or 0.0) if len(gap_parts) > 1 else row_gap
        column = "column" in (pd.get("flex-direction") or "row")
        centred = "center" in (pd.get("align-items") or "")
        wrap = "wrap" in (pd.get("flex-wrap") or "")
        extent = self._content_height(parent, inner.w)
        cursor = inner.y if column else inner.x
        row_y, row_h = inner.y, 0.0
        blocked = False
        for child in flow:
            cd = self._decls(child)
            mt = _px(cd.get("margin-top"), 0.0) or 0.0
            mb = _px(cd.get("margin-bottom"), 0.0) or 0.0
            w = _px(cd.get("width"))
            if w is None and not column:
                w = self._content_width(child) or None
            h = self._height(child, w if w else inner.w)
            if blocked or (not column and w is None):
                self.unplaced.append(
                    {"node": child,
                     "why": "flex-row sibling with unresolvable intrinsic width"})
                blocked = True
                continue
            if column:
                cw = w if w is not None else (
                    self._content_width(child) if centred else inner.w)
                x = inner.x + (inner.w - cw) / 2 if centred else inner.x
                self._commit(child, Box(x, cursor + mt, cw or inner.w, h))
                cursor += mt + h + mb + row_gap
            elif wrap:
                # Break BEFORE placing when this child would pass the right
                # edge — and never on the first child of a row, or an
                # over-wide item would loop a row per item forever.
                if cursor > inner.x and cursor + w > inner.x + inner.w + TOL_WRAP:
                    row_y += row_h + row_gap
                    cursor, row_h = inner.x, 0.0
                self._commit(child, Box(cursor, row_y, w, h))
                row_h = max(row_h, h)
                cursor += w + col_gap
            else:
                y = inner.y + (extent - h) / 2 if centred else inner.y
                self._commit(child, Box(cursor, y, w, h))
                cursor += w + col_gap

    def _place_grid(self, parent, pd, inner, flow):
        centred = "center" in (pd.get("place-items") or pd.get("align-items")
                               or "")
        for child in flow:
            cd = self._decls(child)
            w = _px(cd.get("width")) or self._content_width(child) or inner.w
            h = self._height(child, w)
            if centred:
                self._commit(child, Box(inner.x + (inner.w - w) / 2,
                                        inner.y + (inner.h - h) / 2, w, h))
            else:
                self._commit(child, Box(inner.x, inner.y, w, h))

    def _place_absolute(self, node: dict, cb: Box) -> None:
        d = self._decls(node)
        ins = _inset(d)
        pad_l, pad_r = _pad(d)

        w = _px(d.get("width"))
        if w is None and ins["left"] is not None and ins["right"] is not None:
            w = cb.w - ins["left"] - ins["right"]
        if w is not None:
            w += pad_l + pad_r
        if w is None:
            # shrink-to-fit: max-content, capped by the room actually available
            avail = cb.w - (ins["left"] or 0.0) - (ins["right"] or 0.0)
            content = self._content_width(node) + pad_l + pad_r
            w = min(content, avail) if content else avail
        if w is None or w <= 0:
            self.unplaced.append({"node": node, "why": "no resolvable width"})
            return

        # A container stretched between OPPOSING insets takes its height from
        # the containing block, exactly as `width` does above — CSS resolves
        # top+bottom the same way it resolves left+right, but only the width
        # half of that was implemented. An `inset: 0` wrapper therefore measured
        # 1920x0, and every absolutely positioned child resolving against it was
        # placed relative to a zero-height box: `#kp-subbeat-host` put the
        # sub-beat prototype at y=-180, failing safe-area AND padding on three
        # templates that render correctly in a browser. Two build agents read
        # that as a template defect and abandoned `subBeats` to get around it.
        # Restricted to text-free nodes so a text box's ink stays the height of
        # its own lines rather than the height of the stretched box.
        h = None
        if (ins["top"] is not None and ins["bottom"] is not None
                and not self.text_of(node)):
            h = cb.h - ins["top"] - ins["bottom"]
        if h is None or h <= 0:
            h = self._height(node, max(1.0, w - pad_l - pad_r))

        if ins["left"] is not None:
            x = cb.x + ins["left"]
        elif ins["right"] is not None:
            x = cb.right - ins["right"] - w
        else:
            x = cb.x
        if ins["top"] is not None:
            y = cb.y + ins["top"]
        elif ins["bottom"] is not None:
            y = cb.bottom - ins["bottom"] - h
        else:
            self.unplaced.append({"node": node, "why": "no top/bottom/inset"})
            return

        self._commit(node, Box(x, y, w, h))

    def _commit(self, node: dict, box: Box) -> None:
        self.boxes[id(node)] = box
        d = self._decls(node)
        positioned = d.get("position") in ("absolute", "relative", "fixed")
        self._place_children(node, box if positioned else box)

    # -- results ------------------------------------------------------------
    def ink(self, node: dict) -> Box | None:
        """The glyph run's box, not the layout box.

        A one-line centred caption in a 540px box paints ~230px of ink in the
        middle of it. Grading the layout box would invent collisions the viewer
        never sees, and inventing collisions is how a gate gets switched off.
        """
        box = self.boxes.get(id(node))
        if box is None:
            return None
        d = self._decls(node)
        pad_t, pad_r, pad_b, pad_l = _pad4(d)
        bt, br, bb, bl = _border4(d)
        avail = max(1.0, box.w - pad_l - pad_r - bl - br)
        top = box.y + pad_t + bt
        f = typeface(self.doc, node)
        if f["vertical"]:
            if not self.text_of(node):
                return None
            return Box(box.x + pad_l + bl, top, f["line_height"],
                       self._run_length(node))
        lines = self.wrapped(node, avail)
        if not lines:
            return None
        widest = max(textmetrics.width(ln, f["size"], f["weight"],
                                       f["tracking"], f["uppercase"])
                     for ln in lines)
        widest = min(widest, avail)
        left = box.x + pad_l + bl
        if f["align"] == "center":
            left += (avail - widest) / 2
        elif f["align"] == "right":
            left += avail - widest
        return Box(left, top, widest, len(lines) * f["line_height"])

    def text_nodes(self) -> list[dict]:
        """Every element that paints text, in document order."""
        return [n for n in self.doc.nodes
                if id(n) in self.boxes and self.is_present(n)
                and self.text_of(n)]
