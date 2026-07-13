#!/usr/bin/env python3
"""Full-runtime presence checker for rendered SCLA videos (v2).

Samples the MP4 at 2 fps plus the exact final frame (ffmpeg -> tiny PPM/PGM,
parsed in pure Python — no PIL needed) and hunts GAPS:
  - near-blank frames (low pixel stddev AND almost no content pixels — the v1
    stddev-only heuristic flagged textured white canvases and navy cards as
    blank; content-pixel counting fixes that false-positive class, 2026-07-10)
  - stagnant frames: >=3.0s of pixel-identical video while narration is
    speaking (frame.md forbids a static frame beyond ~2s; 3.0s is the
    deterministic tripwire, the lane agent judges the 2-3s gray zone)
  - audio stream outliving the video stream (clipped narration / blank tail)

With --workspace <dir> (recommended) the checker reads index.html scene starts
and assets/voice/transcript.json:
  - a low-variance frame inside the 0.7s entrance window after a scene start
    is reported as a WARN note, not a violation, unless it is truly featureless
    — templates paint furniture at t=0 (frame.md), so a genuinely bare
    entrance is still caught
  - stagnation is only a violation while spoken words overlap the static run

Usage:
    check_presence.py <video.mp4> <outdir> [--workspace <dir>] [--json]

Writes sampled frames to <outdir> (kept for the lane agent / human to eyeball).
Exit 1 when any violation is found.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

BLANK_STDDEV = 8.0     # 0-255 scale
CONTENT_DEV = 12       # a byte deviating this much from frame mean = content
MIN_CONTENT_PX = 15    # fewer content pixels than this + low stddev = blank
HARD_BLANK_STDDEV = 1.5  # below this even an entrance window is a violation
ENTRANCE_GRACE = 0.7   # seconds after a scene start where entrances are legal
STAGNANT_WARN = 3.0    # pixel-identical this long while narration speaks: warn
STAGNANT_FAIL = 5.0    # ... this long: violation (nothing in frame.md allows it)
FPS = 2


def ffprobe_duration(path, stream):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", "stream=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    ).stdout.strip().splitlines()
    try:
        return float(out[0])
    except (IndexError, ValueError):
        return None


def read_pnm(path):
    """Raw bytes of a binary P6 PPM / P5 PGM (skips header + comments)."""
    data = Path(path).read_bytes()
    fields, rest = [], data
    needed = 4 if data[:2] == b"P6" else 3
    while len(fields) < needed:
        nl = rest.find(b"\n")
        line, rest = rest[:nl], rest[nl + 1:]
        if not line.startswith(b"#"):
            fields.extend(line.split())
    return rest


def stats(pixels):
    n = len(pixels)
    if n == 0:
        return 0.0, 0.0, 0
    mean = sum(pixels) / n
    var = sum((b - mean) ** 2 for b in pixels) / n
    content = sum(1 for b in pixels if abs(b - mean) > CONTENT_DEV) // 3
    return mean, var ** 0.5, content


def scene_starts_from(workspace):
    html = (Path(workspace) / "index.html").read_text()
    starts = []
    for m in re.finditer(r"<div\b[^>]*data-composition-src[^>]*>", html, re.S):
        s = re.search(r'data-start="([\d.]+)"', m.group(0))
        if s:
            starts.append(float(s.group(1)))
    return sorted(starts)


def words_from(workspace):
    p = Path(workspace) / "assets" / "voice" / "transcript.json"
    return json.loads(p.read_text()) if p.exists() else []


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    workspace = None
    if "--workspace" in argv:
        workspace = argv[argv.index("--workspace") + 1]
    args = [a for a in argv if not a.startswith("--")
            and (workspace is None or a != workspace)]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    video, outdir = Path(args[0]), Path(args[1])
    outdir.mkdir(parents=True, exist_ok=True)

    v_dur = ffprobe_duration(video, "v:0")
    a_dur = ffprobe_duration(video, "a:0")
    starts = scene_starts_from(workspace) if workspace else []
    words = words_from(workspace) if workspace else []

    # Color pass for blank detection; tiny gray pass for motion detection.
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
         "-vf", f"fps={FPS},scale=128:72", str(outdir / "s%05d.ppm")], check=True)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
         "-vf", f"fps={FPS},scale=48:27,format=gray", str(outdir / "g%05d.pgm")],
        check=True)
    # Exact final frame, full size (the empty-ending failure lives here).
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-sseof", "-0.05", "-i", str(video), "-frames:v", "1",
         str(outdir / "final.png")], check=True)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-sseof", "-0.05", "-i", str(video),
         "-vf", "scale=128:72", "-frames:v", "1", str(outdir / "zfinal.ppm")],
        check=True)

    findings, warns, frames = [], [], []

    def near_scene_start(t):
        # fps-filter sample timestamps are quantized (±1/FPS), so accept
        # samples labeled just before the boundary too
        return any(-(1 / FPS + 0.01) < t - s < ENTRANCE_GRACE for s in starts)

    for ppm in sorted(outdir.glob("*.ppm")):
        t = (int(ppm.stem[1:]) - 1) / FPS if ppm.name.startswith("s") else v_dur
        mean, std, content = stats(read_pnm(ppm))
        frames.append({"t": round(t, 2), "file": ppm.name, "mean": round(mean, 1),
                       "stddev": round(std, 2), "content_px": content})
        if std < BLANK_STDDEV and content < MIN_CONTENT_PX:
            entry = {"rule": "near-blank-frame", "t": round(t, 2),
                     "detail": f"{ppm.name} stddev {std:.1f}, {content} content "
                               f"px — likely bare canvas (confirm visually)"}
            # Inside the entrance window only a truly featureless frame fails:
            # faint light-canvas furniture (rings + a short scene index) sits
            # at stddev <1 with a handful of content px (calibrated on the
            # 2026-07-10 22:00 render); a pre-furniture-fix bare flash has
            # 0-2 content px AND stddev <1.5.
            hard_blank = std < HARD_BLANK_STDDEV and content < 3
            if workspace and near_scene_start(t) and not hard_blank:
                entry["rule"] = "entrance-window-lowvar"
                entry["detail"] += " [inside 0.7s entrance grace]"
                warns.append(entry)
            else:
                findings.append(entry)

    # Stagnation: consecutive identical gray thumbs while narration speaks.
    grays = sorted(outdir.glob("g*.pgm"))
    run_start, prev = None, None
    static_runs = []
    for i, pgm in enumerate(grays):
        t = (int(pgm.stem[1:]) - 1) / FPS
        px = read_pnm(pgm)
        same = prev is not None and len(px) == len(prev) and \
            max(abs(a - b) for a, b in zip(px, prev)) <= 1
        if same and run_start is None:
            run_start = t - 1 / FPS
        if not same and run_start is not None:
            static_runs.append((run_start, t - 1 / FPS))
            run_start = None
        prev = px
    if run_start is not None:
        static_runs.append((run_start, (len(grays) - 1) / FPS))

    def narration_in(a, b):
        return any(w["start"] < b and w["end"] > a for w in words)

    for a, b in static_runs:
        if b - a >= STAGNANT_WARN and (not words or narration_in(a, b)):
            entry = {"rule": "stagnant-frame", "t": round(a, 2),
                     "detail": f"video pixel-static {a:.1f}s → {b:.1f}s "
                               f"({b - a:.1f}s) while narration speaks "
                               f"— animacy defect (frame.md ~2s rule)"}
            if b - a >= STAGNANT_FAIL:
                findings.append(entry)
            else:
                entry["detail"] += " [3-5s gray zone — lane judges]"
                warns.append(entry)

    if v_dur is not None and a_dur is not None and a_dur > v_dur + 0.05:
        findings.append({"rule": "audio-outlives-video",
                         "detail": f"audio {a_dur:.2f}s > video {v_dur:.2f}s — "
                                   f"narration clipped or blank tail"})

    result = {"video_duration": v_dur, "audio_duration": a_dur,
              "sampled": len(frames), "violations": findings, "warnings": warns,
              "verdict": "FAIL" if findings else "PASS"}
    if as_json:
        result["frames"] = frames
        print(json.dumps(result, indent=2))
    else:
        print(f"video={v_dur}s audio={a_dur}s frames_sampled={len(frames)}")
        print(f"VERDICT: {result['verdict']} ({len(findings)} violation(s), "
              f"{len(warns)} warning(s))")
        for f in findings:
            print(f"  - [{f['rule']}] {f.get('t', '')} {f['detail']}")
        for w in warns:
            print(f"  ? [{w['rule']}] {w.get('t', '')} {w['detail']}")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
