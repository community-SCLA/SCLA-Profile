#!/usr/bin/env python3
"""check_geometry.py — no text may land on other text, or below the frame.

THE DEFECT THIS OWNS. Scene-19 of the 2026-07-29 criteria build printed
"Grounded in what you value" through "Use it on any career decision". Three
gates ran and all three passed it:

  * check_layout.py  — the real browser inspector, 60 samples, PASS with zero
    findings. `hyperframes inspect` grades text against its own container; two
    absolutely-positioned siblings sharing pixels is not a case it models.
  * check_capacity.py — never looked. It infers slot bindings from
    `getElementById("x").textContent = vars.y`, and scla-loop binds its captions
    in a `forEach` loop, so step1..step4 were invisible to it. (Fixed the same
    day: templates now DECLARE the binding with `data-slot`, beside the CSS that
    creates the constraint, instead of the gate guessing it from JS.)
  * check_text.py — graded the size (32px, exactly the then-floor) and the
    provenance. Neither is the question.

The question none of them owned is: given the wrapped line count, does this text
box intersect anything? boxmodel.py answers where every string lands; this gate
grades the result. Static, no browser, no render — so it fires at plan stage,
where the fix is a JSON edit rather than a re-synthesis and a re-render.

THREE RULES:

  text-collision   Two painted glyph runs overlap by more than TOLERANCE on both
                   axes. Graded on INK boxes, not layout boxes — a centred
                   one-line caption in a 540px box paints ~230px in the middle,
                   and flagging the empty 300px either side would be a gate
                   crying wolf until someone switched it off. Intentional
                   layering opts out with `data-layout-allow-overlap` ON THE
                   ELEMENT — stated, never tolerated by a loosened threshold.

  footer-breach    A content element's ink crosses content-bottom (frame.md
                   spacing.content-bottom, loaded via tokens.py). This is the
                   2026-07-28 career-map defect: a card grew to three lines and
                   ran through the footer rule.

  safe-area-breach A content element's ink crosses into the outer keep-out band
                   (frame.md spacing.safe-area).

  padding-breach   BODY-class content crosses the nominal content inset
                   (frame.md spacing.frame-padding). frame-padding has been
                   declared since the system was built and was enforced by
                   nothing at all — tokens.py exposed frame_padding() and no
                   caller ever read it. Graded on body class only: the inset is
                   the target for PRIMARY CONTENT, and frame.md hands the outer
                   band to label-class furniture (brandline, scene index, rail
                   label, eyebrow) by name, so grading chrome against it would
                   fail every template in the system. Decorative bleed opts out
                   with `data-layout-allow-overflow`, which the ghost numerals
                   in scla-steps/scla-loop already declare.

FOOTER CHRME IS NOT CONTENT. frame.md gives the bottom `footer-reserve` band to
the brandline, scene index and progress rail by name, and every one of them is
label-class furniture (uppercase + tracked) declared with `bottom:` inside that
band. Those are derived as chrome and exempted from the two bounds rules — they
ARE the band. They stay graded for collisions and for the left/right/top edges.
Anything body-class down there is content in the footer's seat and fails.

Usage:  python3 check_geometry.py <workspace-or-design-system> [--json]
                                  [--verbose]
Exit:   0 clean · 1 violation · 2 bad args / nothing to grade
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boxmodel
import tokens
from hfp_common import get_attr, parse_scenes

# Sub-pixel slop in the wrap model (kerning is not modelled; see textmetrics)
# plus the difference between a glyph's line box and its actual ink. Below this
# on either axis, two runs are adjacent, not colliding.
TOLERANCE = 6.0

# Slot bindings the gate can still infer when a template has not declared them.
# Declaring `data-slot` is the supported form; this stays as a bridge so an
# undeclared template degrades to partial coverage instead of silent zero.
BIND_RX = re.compile(
    r'getElementById\(\s*["\']([\w-]+)["\']\s*\)\s*\.textContent\s*=\s*'
    r'(?:String\()?\s*vars\.(\w+)')


def _widest_variant(value: str) -> str:
    """A pipe-separated slot renders ONE segment at a time (sub-beats swap in
    place), so the box it needs is the widest segment, not the joined string."""
    parts = [p.strip() for p in str(value).split("|") if p.strip()]
    if len(parts) <= 1:
        return str(value).strip()
    return max(parts, key=len)


def _texts_for(html: str, variables: dict) -> dict:
    """element-id / slot-name -> the string that will actually be painted."""
    texts = {slot: _widest_variant(v) for slot, v in (variables or {}).items()}
    for el_id, slot in BIND_RX.findall(html):
        if slot in (variables or {}):
            texts[el_id] = _widest_variant(variables[slot])
    return texts


def _is_footer_chrome(layout: boxmodel.Layout, node: dict,
                      footer_reserve: float, canvas_h: float) -> bool:
    d = layout.doc.decls(node)
    bottom = boxmodel._px(d.get("bottom"))
    return (bottom is not None and bottom < footer_reserve
            and boxmodel.is_label_class(layout.doc, node))


def _name(node: dict) -> str:
    if node["id"]:
        return "#" + node["id"]
    if node["classes"]:
        return "." + node["classes"][0]
    return "<" + node["tag"] + ">"


def grade(html: str, variables: dict, ws=None):
    """Findings for one template instantiated with one scene's variables."""
    doc = boxmodel.Doc(html)
    layout = boxmodel.Layout(doc, _texts_for(html, variables),
                             canvas=tokens.canvas(ws))
    canvas_w, canvas_h = tokens.canvas(ws)
    safe = tokens.safe_area(ws)
    bottom_limit = tokens.content_bottom(ws)
    footer_reserve = tokens.footer_reserve(ws)
    padding = tokens.frame_padding(ws)

    painted = []
    for node in layout.text_nodes():
        ink = layout.ink(node)
        if ink is None:
            continue
        painted.append((node, ink))

    findings = []

    # 1. collisions
    for i, (a, abox) in enumerate(painted):
        for b, bbox in painted[i + 1:]:
            if a is b["parent"] or b is a["parent"]:
                continue  # a wrapper and its own text are the same ink
            if ("data-layout-allow-overlap" in a["attrs"]
                    or "data-layout-allow-overlap" in b["attrs"]):
                continue
            dx, dy = abox.overlap(bbox)
            if dx > TOLERANCE and dy > TOLERANCE:
                findings.append({
                    "rule": "text-collision",
                    "detail": (f"{_name(a)} {abox} overlaps {_name(b)} {bbox} "
                               f"by {dx:.0f}x{dy:.0f}px — "
                               f"{layout.text_of(a)!r} lands on "
                               f"{layout.text_of(b)!r}"),
                })

    # 2/3. bounds — chrome owns the footer band and is not graded against it
    for node, ink in painted:
        if "data-layout-allow-overflow" in node["attrs"]:
            continue
        chrome = _is_footer_chrome(layout, node, footer_reserve, canvas_h)
        if not chrome and ink.bottom > bottom_limit + TOLERANCE:
            findings.append({
                "rule": "footer-breach",
                "detail": (f"{_name(node)} ends at y={ink.bottom:.0f}, below "
                           f"content-bottom {bottom_limit:.0f} — "
                           f"{layout.text_of(node)!r} runs into the footer band"),
            })
        edges = []
        if ink.x < safe - TOLERANCE:
            edges.append(f"left x={ink.x:.0f}")
        if ink.right > canvas_w - safe + TOLERANCE:
            edges.append(f"right x={ink.right:.0f}")
        if ink.y < safe - TOLERANCE:
            edges.append(f"top y={ink.y:.0f}")
        if not chrome and ink.bottom > canvas_h - safe + TOLERANCE:
            edges.append(f"bottom y={ink.bottom:.0f}")
        if edges:
            findings.append({
                "rule": "safe-area-breach",
                "detail": (f"{_name(node)} crosses the {safe:.0f}px keep-out "
                           f"({', '.join(edges)}) — {layout.text_of(node)!r}"),
            })

        # 4. the nominal content inset — body class only (see the docstring).
        if boxmodel.is_label_class(layout.doc, node):
            continue
        pad_edges = []
        if ink.x < padding - TOLERANCE:
            pad_edges.append(f"left x={ink.x:.0f}")
        if ink.right > canvas_w - padding + TOLERANCE:
            pad_edges.append(f"right x={ink.right:.0f}")
        if ink.y < padding - TOLERANCE:
            pad_edges.append(f"top y={ink.y:.0f}")
        if not chrome and ink.bottom > canvas_h - padding + TOLERANCE:
            pad_edges.append(f"bottom y={ink.bottom:.0f}")
        if pad_edges:
            findings.append({
                "rule": "padding-breach",
                "detail": (f"{_name(node)} crosses the {padding:.0f}px content "
                           f"inset ({', '.join(pad_edges)}) — "
                           f"{layout.text_of(node)!r}. Body content lives inside "
                           f"frame-padding; declare decorative bleed with "
                           f"data-layout-allow-overflow"),
            })

    return findings, layout, painted


def check(target: Path):
    index = target / "index.html"
    if not index.is_file():
        return None, [f"no index.html in {target}"]
    scenes = parse_scenes(index.read_text(encoding="utf-8", errors="replace"))
    if not scenes:
        return None, ["no scene slots found in index.html"]

    ws = target if (target / "frame.md").is_file() else None
    report = {"scenes": [], "unplaced": 0, "graded": 0}
    problems = []
    cache: dict[str, str] = {}

    for sc in scenes:
        src = get_attr(sc["tag"], "data-composition-src")
        if not src:
            continue
        comp = target / src
        if not comp.is_file():
            continue
        if src not in cache:
            cache[src] = comp.read_text(encoding="utf-8", errors="replace")
        findings, layout, painted = grade(cache[src], sc["variables"], ws)
        # A scene that grades NOTHING is a coverage hole wearing a PASS. This
        # fired for real: a `</circle>` end tag unbalanced the tree and orphaned
        # every element after scla-stat's ring SVG, and the gate reported the
        # template clean because it had looked at none of it.
        if not painted:
            findings = [{"rule": "nothing-graded",
                         "detail": "no painted text box could be resolved for "
                                   "this scene — the gate looked at nothing, "
                                   "which is not the same as finding nothing"}
                        ] + findings
        report["graded"] += len(painted)
        report["unplaced"] += len(layout.unplaced)
        report["scenes"].append({
            "id": sc["id"], "composition": Path(src).name,
            "painted": len(painted), "unplaced": len(layout.unplaced),
            "findings": findings,
        })
        for f in findings:
            problems.append(f"{sc['id']} ({Path(src).name}) [{f['rule']}] "
                            f"{f['detail']}")
    return report, problems


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    target = Path(args[0]).resolve()
    report, problems = check(target)
    if report is None:
        for p in problems:
            print(f"  !! {p}", file=sys.stderr)
        return 2

    if "--json" in argv:
        print(json.dumps({"pass": not problems, "problems": problems,
                          "report": report}, indent=2))
    else:
        print(f"[geometry] {report['graded']} painted text box(es) across "
              f"{len(report['scenes'])} scene(s); "
              f"{report['unplaced']} element(s) unplaced")
        if "--verbose" in argv:
            for s in report["scenes"]:
                print(f"  {s['id']:<12} {s['composition']:<24} "
                      f"{s['painted']:>2} boxes, {len(s['findings'])} finding(s)")
        for p in problems:
            print(f"  !! {p}")
        print("GEOMETRY: " + ("PASS" if not problems
                              else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
