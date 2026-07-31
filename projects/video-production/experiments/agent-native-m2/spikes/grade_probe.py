#!/usr/bin/env python3
"""grade_probe.py — check_geometry.py's rules, run against a runtime probe.

Same four rules, same tokens, same TOLERANCE. The only thing that changes is the
input: real getBoundingClientRect/Range ink boxes at N sample times, instead of
boxmodel.py's static resolution of template CSS.

Two differences that are the whole point:
  * an element is graded only where it is actually VISIBLE (effective opacity),
    so time-multiplexed overlays are not judged against each other;
  * the boxes are the browser's, so flow, flex, grid, calc() and % all work.

    python3 grade_probe.py <probe.json> [--tokens-ws <dir>] [--json]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/workspaces/SCLA-Profile/projects/video-production/render-qa/src")
import tokens  # noqa: E402

TOLERANCE = 6.0        # same as check_geometry.py
VISIBLE = 0.05         # effective opacity above which an element is on screen

# Mirrors boxmodel.is_label_class: uppercase + tracked furniture owns the outer
# band. Approximated here from the probe's computed values.
def is_label(el):
    return el.get("upper") or (el["fontSize"] <= 32 and el.get("tracked"))


def name(el):
    if el["id"]:
        return "#" + el["id"]
    if el["cls"]:
        return "." + el["cls"][0]
    return "<" + el["tag"] + ">"


def overlap(a, b):
    dx = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    dy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return dx, dy


def main(argv):
    probe = json.loads(Path(argv[0]).read_text())
    ws = None
    if "--tokens-ws" in argv:
        ws = argv[argv.index("--tokens-ws") + 1]
    canvas_w, canvas_h = tokens.canvas(ws)
    safe = tokens.safe_area(ws)
    bottom_limit = tokens.content_bottom(ws)
    padding = tokens.frame_padding(ws)

    findings = []
    for sample in probe["samples"]:
        t = sample["t"]
        painted = [e for e in sample["elements"]
                   if e.get("ink") and e["opacity"] > VISIBLE and e["text"]]

        # 1. collisions — real ink, real visibility, one moment in time
        for i, a in enumerate(painted):
            for b in painted[i + 1:]:
                dx, dy = overlap(a["ink"], b["ink"])
                if dx > TOLERANCE and dy > TOLERANCE:
                    findings.append({
                        "t": t, "rule": "text-collision",
                        "detail": f"{name(a)} overlaps {name(b)} by "
                                  f"{dx:.0f}x{dy:.0f}px — {a['text'][:50]!r} "
                                  f"lands on {b['text'][:50]!r}"})

        # 2/3/4. bounds
        for e in painted:
            ink = e["ink"]
            right, bottom = ink["x"] + ink["w"], ink["y"] + ink["h"]
            if bottom > bottom_limit + TOLERANCE:
                findings.append({
                    "t": t, "rule": "footer-breach",
                    "detail": f"{name(e)} ends at y={bottom:.0f} below "
                              f"content-bottom {bottom_limit:.0f} — {e['text'][:50]!r}"})
            edges = []
            if ink["x"] < safe - TOLERANCE:
                edges.append(f"left x={ink['x']:.0f}")
            if right > canvas_w - safe + TOLERANCE:
                edges.append(f"right x={right:.0f}")
            if ink["y"] < safe - TOLERANCE:
                edges.append(f"top y={ink['y']:.0f}")
            if bottom > canvas_h - safe + TOLERANCE:
                edges.append(f"bottom y={bottom:.0f}")
            if edges:
                findings.append({
                    "t": t, "rule": "safe-area-breach",
                    "detail": f"{name(e)} crosses the {safe:.0f}px keep-out "
                              f"({', '.join(edges)}) — {e['text'][:50]!r}"})
            pad = []
            if ink["x"] < padding - TOLERANCE:
                pad.append(f"left x={ink['x']:.0f}")
            if right > canvas_w - padding + TOLERANCE:
                pad.append(f"right x={right:.0f}")
            if pad:
                findings.append({
                    "t": t, "rule": "padding-breach",
                    "detail": f"{name(e)} crosses the {padding:.0f}px inset "
                              f"({', '.join(pad)}) — {e['text'][:50]!r}"})

    graded = sum(len([e for e in s["elements"]
                      if e.get("ink") and e["opacity"] > VISIBLE and e["text"]])
                 for s in probe["samples"])
    if "--json" in argv:
        print(json.dumps({"pass": not findings, "graded": graded,
                          "findings": findings}, indent=1))
    else:
        import collections
        print(f"[probe-geometry] {graded} visible painted text box(es) across "
              f"{len(probe['samples'])} sample(s)")
        for k, v in collections.Counter(f["rule"] for f in findings).most_common():
            print(f"  {v:>4}  {k}")
        for f in findings[:25]:
            print(f"  !! t={f['t']:.2f} [{f['rule']}] {f['detail']}")
        if len(findings) > 25:
            print(f"  … and {len(findings) - 25} more")
        print("PROBE-GEOMETRY: " + ("PASS" if not findings
                                    else f"FAIL ({len(findings)})"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
