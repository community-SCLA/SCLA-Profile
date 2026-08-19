#!/usr/bin/env python3
"""Reject two visual structures that can look broken while ordinary layout passes.

The browser layout inspector is good at text-vs-text overlap and canvas escape.
It cannot reliably infer that an empty, absolutely positioned border is meant
to highlight a different element, or that a flex child should remain inside a
visually bounded parent. Those two gaps produced the owner-rejected
``m5_skills-for-the-ai-era`` cut on 2026-08-11.

Rules:

``detached-focus-overlay``
    An empty absolute/fixed border named as a focus/highlight/spotlight. These
    overlays use canvas coordinates and silently cross unrelated layouts. Put
    the emphasis on the actual target element with border/outline/box-shadow.

``flex-child-auto-min-overflow``
    A growing child (``flex``/``flex-grow``) inside a fixed-height column flex
    container still has the CSS default ``min-height:auto``. Dense content can
    force it through the parent's border. Require both ``min-height:0`` and a
    clipping/scrolling overflow mode; then the browser inspector can detect any
    clipped text instead of certifying escaped geometry.

Usage: python3 check_visual_structure.py <workspace> [--json]
Exit: 0 clean · 1 violation · 2 bad args / nothing to grade
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import Finding, typed  # noqa: E402

STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
FOCUS_NAME = re.compile(
    r"(?:^|[-_])(spotlight|highlight|focus(?:ed|ing)?|focus-ring|"
    r"focus-box|focus-outline|outline)(?:$|[-_])", re.I)
PX = re.compile(r"^\d+(?:\.\d+)?px$", re.I)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}


def _css_props(body: str) -> dict[str, str]:
    props = {}
    for declaration in body.split(";"):
        if ":" not in declaration:
            continue
        name, value = declaration.split(":", 1)
        props[name.strip().lower()] = value.strip().lower()
    return props


def _simple_match(selector: str, node: dict) -> bool:
    """Match the literal single-element selectors used by lesson CSS.

    Complex selectors are deliberately ignored instead of guessed. The two
    unsafe structures use element-level geometry declarations; requiring those
    declarations to be readable keeps the gate deterministic.
    """
    selector = selector.strip()
    if not selector or re.search(r"[\s>+~\[:*]", selector):
        return False
    tag = re.match(r"^[A-Za-z][\w-]*", selector)
    if tag and tag.group(0).lower() != node["tag"]:
        return False
    ids = re.findall(r"#([\w-]+)", selector)
    if ids and node["attrs"].get("id", "") not in ids:
        return False
    classes = set(re.findall(r"\.([\w-]+)", selector))
    return classes.issubset(node["classes"])


class _Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        values = {k.lower(): (v or "") for k, v in attrs}
        node = {
            "tag": tag.lower(), "attrs": values,
            "classes": set(values.get("class", "").split()),
            "children": [], "text": "", "parent": self.stack[-1] if self.stack else None,
        }
        index = len(self.nodes)
        self.nodes.append(node)
        if self.stack:
            self.nodes[self.stack[-1]]["children"].append(index)
        if tag.lower() not in VOID:
            self.stack.append(index)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.nodes[self.stack[-1]]["tag"] == tag.lower():
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and data.strip():
            self.nodes[self.stack[-1]]["text"] += " " + data.strip()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.nodes[self.stack[i]]["tag"] == tag.lower():
                del self.stack[i:]
                return


def _styles(raw_html: str, nodes: list[dict]) -> list[dict[str, str]]:
    rules = []
    for block in STYLE_BLOCK.findall(raw_html):
        for group, body in CSS_RULE.findall(block):
            props = _css_props(body)
            for selector in group.split(","):
                rules.append((selector.strip(), props))
    computed = []
    for node in nodes:
        style = {}
        for selector, props in rules:
            if _simple_match(selector, node):
                style.update(props)
        style.update(_css_props(node["attrs"].get("style", "")))
        computed.append(style)
    return computed


def _has_border(style: dict[str, str]) -> bool:
    for name in ("border", "border-width", "outline", "outline-width"):
        value = style.get(name, "")
        if value and not re.match(r"^(?:0(?:px)?|none)(?:\s|$)", value):
            return True
    return False


def _grows(style: dict[str, str]) -> bool:
    grow = style.get("flex-grow")
    if grow:
        try:
            return float(grow) > 0
        except ValueError:
            return True
    flex = style.get("flex", "").split()
    if not flex:
        return False
    try:
        return float(flex[0]) > 0
    except ValueError:
        return flex[0] not in {"none", "initial", "0", "0px"}


def grade(raw_html: str):
    tree = _Tree()
    tree.feed(raw_html)
    tree.close()
    styles = _styles(raw_html, tree.nodes)
    findings = []

    for i, node in enumerate(tree.nodes):
        style = styles[i]
        names = [node["attrs"].get("id", ""), *node["classes"]]
        is_focus = any(FOCUS_NAME.search(name) for name in names if name)
        empty = not node["text"].strip() and not node["children"]
        transparent = style.get("background", "transparent") in {
            "transparent", "none", "rgba(0,0,0,0)", "rgba(0, 0, 0, 0)"}
        if (is_focus and empty and transparent and _has_border(style)
                and style.get("position") in {"absolute", "fixed"}):
            label = (f"#{node['attrs']['id']}" if node["attrs"].get("id")
                     else "." + ".".join(sorted(node["classes"])))
            findings.append({
                "rule": "detached-focus-overlay",
                "detail": (
                    f"{label} is an empty positioned focus border. Detached "
                    "highlight geometry can cross unrelated layouts while "
                    "text/canvas checks remain green. Remove it and emphasize "
                    "the actual target element with its own border, outline, "
                    "or box-shadow"),
            })

        fixed_column = (
            style.get("display") in {"flex", "inline-flex"}
            and style.get("flex-direction", "row") == "column"
            and PX.fullmatch(style.get("height", "")))
        if not fixed_column:
            continue
        for child_index in node["children"]:
            child = tree.nodes[child_index]
            child_style = styles[child_index]
            if not _grows(child_style):
                continue
            min_zero = child_style.get("min-height") in {"0", "0px"}
            clips = child_style.get("overflow") in {"hidden", "clip", "auto", "scroll"}
            if min_zero and clips:
                continue
            parent_label = (f"#{node['attrs']['id']}" if node["attrs"].get("id")
                            else "." + ".".join(sorted(node["classes"])))
            child_label = (f"#{child['attrs']['id']}" if child["attrs"].get("id")
                           else "." + ".".join(sorted(child["classes"])))
            findings.append({
                "rule": "flex-child-auto-min-overflow",
                "detail": (
                    f"{child_label} grows inside fixed-height column "
                    f"{parent_label} without both min-height:0 and bounded "
                    "overflow. CSS min-height:auto can force the child through "
                    "the parent's border. Add min-height:0 plus overflow:hidden "
                    "or overflow:auto, then let the browser text-clipping gate "
                    "verify the settled frame"),
            })
    return findings


def _files(workspace: Path):
    files = sorted(workspace.glob("compositions/*.html"))
    index = workspace / "index.html"
    if index.is_file():
        files.append(index)
    return files


def check(workspace: Path):
    files = _files(Path(workspace))
    if not files:
        return None, [Finding("nothing-graded", f"no HTML under {workspace}")]
    problems = []
    for path in files:
        for finding in grade(path.read_text(encoding="utf-8", errors="replace")):
            problems.append(Finding(
                finding["rule"], f"{path.name}: {finding['detail']}"))
    return {"files": len(files)}, problems


def main(argv):
    args = [value for value in argv if not value.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    report, problems = check(Path(args[0]))
    if "--json" in argv:
        print(json.dumps({"pass": report is not None and not problems,
                          "report": report, "findings": typed(problems)}, indent=2))
    else:
        if report is not None:
            print(f"[visual-structure] {report['files']} HTML file(s)")
        for problem in problems:
            print(f"  !! {problem}")
        print("VISUAL STRUCTURE: " + (
            "PASS" if report is not None and not problems
            else f"FAIL ({len(problems)})"))
    return 0 if report is not None and not problems else (2 if report is None else 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
