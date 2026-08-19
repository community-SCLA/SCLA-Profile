#!/usr/bin/env python3
"""Per-beat metadata for the scene contact sheet.

Narration comes from audio_meta.json (voices[].words), the one source every
lesson carries; on-frame copy is scraped from the beat's own markup when the
lesson uses a parseable clip element. Program membership comes from
run.sh status --json's published ledger.
"""
import json, re, subprocess, sys
from pathlib import Path

VP = Path("/workspaces/SCLA-Profile/projects/video-production")
WSROOT = VP / "renders-hyperframes"
OUT = Path(sys.argv[1])
THUMBS = OUT.parent / "thumbs"

status = json.loads(subprocess.run(
    ["./run.sh", "status", "--json"], cwd=VP, capture_output=True, text=True).stdout)
prog_of = {p["base"]: p["program"] for p in status["published"]}
wistia_of = {p["base"]: p.get("wistia_url") for p in status["published"]}

CLIP = re.compile(r'<(section|div)\b([^>]*\bclass="[^"]*\bclip\b[^"]*"[^>]*)>', re.I)
ATTR = re.compile(r'([:\w-]+)\s*=\s*"([^"]*)"')
TAGS = re.compile(r"<[^>]+>")
ENT = {"&quot;": '"', "&#39;": "'", "&amp;": "&", "&lt;": "<", "&gt;": ">",
       "&nbsp;": " ", "&mdash;": "—", "&ndash;": "–", "&hellip;": "…"}


def unesc(s):
    for a, b in ENT.items():
        s = s.replace(a, b)
    return s


def clips(html):
    """(attrs, inner text) per clip element, in document order."""
    out = []
    for m in CLIP.finditer(html):
        tag = m.group(1)
        attrs = {k.lower(): unesc(v) for k, v in ATTR.findall(m.group(2))}
        # balanced scan for the matching close tag (clips can nest same-tag children)
        depth, i = 1, m.end()
        open_re = re.compile(rf"<{tag}\b", re.I)
        close_re = re.compile(rf"</{tag}\s*>", re.I)
        while depth and i < len(html):
            o, c = open_re.search(html, i), close_re.search(html, i)
            if not c:
                break
            if o and o.start() < c.start():
                depth, i = depth + 1, o.end()
            else:
                depth, i = depth - 1, c.end()
        inner = html[m.end():i]
        text = re.sub(r"\s+", " ", unesc(TAGS.sub(" ", inner))).strip()
        out.append((attrs, text))
    return out


def narration_map(ws):
    """clip id -> narration text, rebuilt from the word timings."""
    p = ws / "audio_meta.json"
    if not p.is_file():
        return {}
    try:
        voices = json.loads(p.read_text()).get("voices") or []
    except json.JSONDecodeError:
        return {}
    return {v["id"]: " ".join(w.get("text", "") for w in v.get("words") or []).strip()
            for v in voices if v.get("id")}


lessons = []
for ws in sorted(WSROOT.iterdir()):
    idx, tim = ws / "index.html", ws / "timing.json"
    if not idx.is_file():
        continue
    html = idx.read_text(encoding="utf-8", errors="replace")
    if tim.is_file():
        t = json.loads(tim.read_text())
        rows, total, lane = t["rows"], t.get("total", 0), "freeform"
    else:
        # retired template lane: no timing.json; the captured grid is the record
        rows = [{} for _ in sorted((THUMBS / ws.name).glob("*.jpg"))]
        total, lane = 0, "template (retired)"
    narr = narration_map(ws)
    cl = clips(html)
    beats = []
    for i, r in enumerate(rows):
        attrs, text = cl[i] if i < len(cl) else ({}, "")
        cid = r.get("id") or attrs.get("data-beat-id") or f"b{i+1}"
        beats.append({
            "n": i + 1,
            "id": attrs.get("data-beat-id") or cid,
            "start": round(r.get("vis_start", 0.0), 2),
            "dur": round(r.get("vis_dur", 0.0), 2),
            "narration": narr.get(cid) or attrs.get("data-narration", ""),
            "onframe": text[:240],
        })
    lessons.append({
        "stem": ws.name, "program": prog_of.get(ws.name, "unpublished"),
        "wistia": wistia_of.get(ws.name), "runtime": round(total, 1), "lane": lane,
        "beat_count": len(rows), "beats": beats,
    })

OUT.write_text(json.dumps(lessons, indent=1))
tot = sum(l["beat_count"] for l in lessons)
withn = sum(1 for l in lessons for b in l["beats"] if b["narration"])
witho = sum(1 for l in lessons for b in l["beats"] if b["onframe"])
print(f"{len(lessons)} lessons, {tot} beats, {withn} with narration, {witho} with on-frame copy")
print("no narration at all:", [l["stem"] for l in lessons
                               if not any(b["narration"] for b in l["beats"])])
