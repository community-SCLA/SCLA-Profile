#!/usr/bin/env python3
"""check_layout.py — run the layout inspector at EVERY scene, and believe it.

The overlap the owner reported on scene-15 of the 2026-07-28 build was found by
the tooling we already run, and thrown away twice over:

  1. SAMPLING. `npm run check` inspects 9 points across the whole runtime. On a
     149.5s / 25-scene lesson that is one sample per ~16.6s, so 16 scenes were
     never looked at. Re-running at every scene midpoint surfaced the collision
     immediately:
        content_overlap  t=79.03  #sh-number over #sh-stat-label
        "3-5 possible paths"
  2. SEVERITY. That finding is emitted at severity "info", so `ok` stayed true
     and `errorCount` stayed 0. The gate read the exit code and passed the
     build.

Two text blocks sitting on top of each other is not an "info". This gate samples
one point per scene (plus transition seams, where transient overlaps hide) and
treats overlap as fatal whatever severity upstream assigns it. Everything else
upstream calls an error stays an error; warnings and other infos are reported
and do not block.

Usage:  check_layout.py <workspace> [--json] [--samples-only]
Exit:   0 clean · 1 fatal finding · 2 bad args / inspector could not run
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import parse_scenes

DESIGN_SYSTEM = Path(__file__).resolve().parent.parent / "design-system"

# Codes that block regardless of the severity the inspector assigns them.
FATAL_CODES = {"content_overlap", "text_overflow", "text_clipped",
               "canvas_overflow", "clip_escape", "motion_off_frame"}

# Codes that are real when they PERSIST and noise when they flash. A wipe or a
# cross-fade momentarily puts text behind the panel that is sliding over it, and
# the inspector reports that honestly — but it is not a defect. Verified on the
# 2026-07-28 build: `text_occluded` fired on scene-04 for 3ms, and the rendered
# frame shows the heading perfectly legible on its navy canvas. A block of text
# genuinely buried stays buried, so persistence is the discriminator.
TRANSIENT_CODES = {"text_occluded"}
PERSIST_SPAN = 0.5     # seconds between firstSeen and lastSeen
PERSIST_COUNT = 3      # or this many separate sightings

# Transition seams are where transient overlaps live, but they multiply samples;
# cap so a 25-scene lesson stays a ~2 minute check rather than a ~10 minute one.
MAX_TRANSITION_SAMPLES = 40


def pinned_cli() -> str:
    """The hyperframes version this project pins — never `@latest`, so the gate
    cannot change verdict because upstream shipped."""
    pkg = DESIGN_SYSTEM / "package.json"
    if pkg.is_file():
        m = re.search(r"hyperframes@([0-9][0-9.]*)", pkg.read_text())
        if m:
            return f"hyperframes@{m.group(1)}"
        try:
            dep = json.loads(pkg.read_text()).get("devDependencies", {})
            v = (dep.get("hyperframes") or "").lstrip("^~")
            if v:
                return f"hyperframes@{v}"
        except json.JSONDecodeError:
            pass
    return "hyperframes"


def scene_times(ws: Path):
    """(midpoint, scene_id) for every scene clip."""
    scenes = parse_scenes((ws / "index.html").read_text(
        encoding="utf-8", errors="replace"))
    out = []
    for sc in scenes:
        start, dur = sc.get("start"), sc.get("duration")
        if not isinstance(start, (int, float)) or not isinstance(dur, (int, float)):
            continue
        if start != start or dur != dur or dur <= 0:  # NaN / placeholder
            continue
        out.append((round(start + dur / 2, 2), sc["id"], start, start + dur))
    return out


def run_inspect(ws: Path, times):
    cmd = ["npx", "--yes", pinned_cli(), "inspect", ".", "--json",
           "--at", ",".join(f"{t:.2f}" for t, *_ in times),
           "--at-transitions",
           "--max-transition-samples", str(MAX_TRANSITION_SAMPLES)]
    p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True)
    body = p.stdout.strip()
    start = body.find("{")
    if start == -1:
        return None, (p.stderr or body)[-800:]
    try:
        return json.loads(body[start:]), None
    except json.JSONDecodeError as exc:
        return None, f"unparseable inspector output: {exc}"


def attribute(t, times):
    for _, sid, lo, hi in times:
        if lo <= t < hi:
            return sid
    return "?"


def check(ws: Path):
    times = scene_times(ws)
    if not times:
        return None, ["no scene clips with resolved timing in index.html"], []
    data, err = run_inspect(ws, times)
    if data is None:
        return None, [f"inspector could not run: {err}"], []

    fatal, other = [], []
    for issue in data.get("issues", []):
        code = issue.get("code", "?")
        sev = issue.get("severity", "?")
        t = issue.get("time", issue.get("firstSeen", 0)) or 0
        where = attribute(t, times)
        span = (issue.get("lastSeen", t) or t) - (issue.get("firstSeen", t) or t)
        persistent = (span >= PERSIST_SPAN
                      or (issue.get("occurrences") or 1) >= PERSIST_COUNT)
        blocking = code in FATAL_CODES or sev == "error"
        if code in TRANSIENT_CODES and not persistent:
            blocking = False
        line = (f"{where} (t={t:.2f}s) [{code}/{sev}] "
                f"{issue.get('selector','?')} vs "
                f"{issue.get('containerSelector','?')}: "
                f"{issue.get('message','')}"
                f"{' — ' + repr(issue['text'][:60]) if issue.get('text') else ''}"
                f"{'' if blocking else '  (transient — advisory)'}")
        (fatal if blocking else other).append(line)
    return data, fatal, other


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    ws = Path(args[0]).resolve()
    if "--samples-only" in argv:
        for t, sid, _, _ in scene_times(ws):
            print(f"{sid} {t:.2f}")
        return 0

    data, fatal, other = check(ws)
    if data is None:
        for f in fatal:
            print(f"  !! {f}", file=sys.stderr)
        return 2

    if "--json" in argv:
        print(json.dumps({"pass": not fatal, "fatal": fatal,
                          "advisory": other,
                          "samples": len(data.get("samples", []))}, indent=2))
    else:
        print(f"[layout] {len(data.get('samples', []))} samples "
              f"(one per scene + transition seams)")
        for f in fatal:
            print(f"  !! {f}")
        for o in other:
            print(f"  -- {o}")
        print("LAYOUT: " + ("PASS" if not fatal else f"FAIL ({len(fatal)})"))
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
