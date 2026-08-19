#!/usr/bin/env python3
"""Assemble the interactive scene contact sheet from the captured frame grid.

Reads lessons.json (metadata) + thumbs/<stem>/NNN.jpg (one still per beat),
collapses runs of near-identical consecutive stills into one card, re-encodes
each representative still as a small WebP data URI, and splices the result into
template.html as one embedded JSON block.
"""
import base64
import io
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

KH = Path(__file__).resolve().parent
THUMBS = KH / "thumbs"
WIDTH = 448
QUALITY = 62
MERGE_BELOW = 0.6  # mean abs difference on a 64x36 grey signature

PROGRAMS = [
    ("early-career-boost", "ECB", "Early Career Boost"),
    ("mid-career-momentum", "MCM", "Mid-Career Momentum"),
    ("career-transitions", "CT", "Career Transitions"),
    ("entrepreneur-accelerator", "EA", "Entrepreneur Accelerator"),
]
SHORT = {k: s for k, s, _ in PROGRAMS}
ORDER = {k: i for i, (k, _, _) in enumerate(PROGRAMS)}

SMALL = {"a", "an", "and", "as", "at", "be", "but", "by", "for", "from", "in",
         "is", "of", "on", "or", "the", "to", "with"}


def title_of(stem, program):
    """Human lesson title from the canonical stem."""
    s = stem
    if s.endswith("_" + program):
        s = s[: -len(program) - 1]
    mod = ""
    m = re.match(r"^(m\d+)_(.*)$", s)
    if m:
        mod, s = m.group(1).upper(), m.group(2)
    words = s.replace("-", " ").split()
    out = []
    for i, w in enumerate(words):
        out.append(w.capitalize() if (i == 0 or w not in SMALL) else w)
    t = " ".join(out)
    return f"{mod} - {t}" if mod else t


def signature(path):
    im = Image.open(path).convert("L").resize((64, 36), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32)


def webp_uri(path):
    im = Image.open(path).convert("RGB")
    im = im.resize((WIDTH, round(WIDTH * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=QUALITY, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    lessons_meta = json.load(open(KH / "lessons.json"))
    # freeform first, the retired template lane last inside its program
    lessons_meta.sort(key=lambda l: (ORDER.get(l["program"], 9),
                                     0 if l["lane"] == "freeform" else 1,
                                     l["stem"]))

    per_program = {}
    lessons_out = []
    frames_kept = frames_total = 0

    for meta in lessons_meta:
        prog = meta["program"]
        idx = per_program.get(prog, 0) + 1
        per_program[prog] = idx
        lcode = f"{SHORT.get(prog, 'X')}-{idx:02d}"

        files = sorted((THUMBS / meta["stem"]).glob("*.jpg"))
        beats = meta["beats"]
        frames_total += len(files)
        sigs = [signature(f) for f in files]

        # group consecutive stills that are visually indistinguishable
        groups, cur = [], [0]
        for i in range(1, len(files)):
            if float(np.abs(sigs[i] - sigs[i - 1]).mean()) < MERGE_BELOW:
                cur.append(i)
            else:
                groups.append(cur)
                cur = [i]
        if cur:
            groups.append(cur)

        scenes = []
        for n, g in enumerate(groups, 1):
            last = g[-1]                      # fullest state of the run
            b = beats[last] if last < len(beats) else {}
            first = beats[g[0]] if g[0] < len(beats) else {}
            narration = " ".join(
                beats[i].get("narration", "") for i in g if i < len(beats)).strip()
            scenes.append({
                "code": f"{lcode}.{n:02d}",
                "beat": (first.get("n") or g[0] + 1),
                "spans": len(g),
                "t": first.get("start", 0.0),
                "narr": narration[:600],
                "copy": (b.get("onframe") or "")[:200],
                "img": webp_uri(files[last]),
            })
        frames_kept += len(scenes)

        lessons_out.append({
            "code": lcode,
            "stem": meta["stem"],
            "title": title_of(meta["stem"], prog),
            "program": prog,
            "runtime": meta["runtime"],
            "wistia": meta["wistia"],
            "lane": meta["lane"],
            "beats": meta["beat_count"],
            "scenes": scenes,
        })

    data = {
        "programs": [{"key": k, "short": s, "label": l} for k, s, l in PROGRAMS],
        "lessons": lessons_out,
        "stats": {"lessons": len(lessons_out), "frames": frames_total,
                  "cards": frames_kept},
    }
    raw = json.dumps(data, separators=(",", ":"))
    template = (KH / "template.html").read_text()
    out = Path(sys.argv[1] if len(sys.argv) > 1 else KH / "scene-harvest.html")
    out.write_text(template.replace("__DATA__", raw).replace("__PICKS__", "{}"))
    print(f"{len(lessons_out)} lessons - {frames_total} frames - {frames_kept} cards")
    print(f"{out} - {out.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
