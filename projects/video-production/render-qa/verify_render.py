#!/usr/bin/env python3
"""One-command post-render gate + shared QA evidence generator.

Run immediately after `npm run render`. Does three jobs in one pass:

  1. Container truth — ffprobe the MP4: video/audio stream durations vs the
     composition's root duration (±0.15s), resolution 1920×1080, both streams
     present.
  2. Presence v2 — runs check_presence.py with --workspace (entrance-grace,
     content-pixel blank detection, stagnation tripwire, audio-vs-video).
  3. Frame evidence — extracts per-scene strategic frames (start+0.3s,
     midpoint, end−0.3s) at full resolution into <workspace>/qa/frames/,
     named f<time>s_<sceneid>_<pos>.png. This is THE shared frame set: the
     QA lanes and the human gate read these instead of each re-extracting
     their own (one ffmpeg pass instead of four).

Exit 0 = render verified, evidence ready; exit 1 = deterministic defect found
(do not launch agent lanes — fix and re-render first).

Usage:  verify_render.py <workspace> [<video.mp4>] [--json]
        (default MP4: newest file in <workspace>/renders/)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import ffprobe_duration, parse_scenes

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECK_PRESENCE = REPO_ROOT / ".claude/skills/adversarial-qa/scripts/check_presence.py"
DUR_TOL = 0.15


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0]).resolve()
    if len(args) > 1:
        mp4 = Path(args[1]).resolve()
    else:
        renders = sorted((ws / "renders").glob("*.mp4"),
                         key=lambda p: p.stat().st_mtime)
        if not renders:
            print(f"no MP4 in {ws / 'renders'}", file=sys.stderr)
            sys.exit(2)
        mp4 = renders[-1]

    sections, failed = {"mp4": str(mp4)}, False
    html = (ws / "index.html").read_text()
    scenes = parse_scenes(html)
    root = re.search(r'id="root"[^>]*data-duration="([\d.]+)"', html)
    root_dur = float(root.group(1)) if root else None

    # 1. container truth
    v_dur = ffprobe_duration(mp4, "v:0")
    a_dur = ffprobe_duration(mp4, "a:0")
    probs = []
    if v_dur is None:
        probs.append("no video stream")
    if a_dur is None:
        probs.append("no audio stream")
    if v_dur and root_dur and abs(v_dur - root_dur) > DUR_TOL:
        probs.append(f"video stream {v_dur:.2f}s vs root {root_dur:.2f}s "
                     f"(>±{DUR_TOL}s)")
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0", str(mp4)],
        capture_output=True, text=True).stdout.strip()
    if res and res != "1920,1080":
        probs.append(f"resolution {res} != 1920,1080")
    sections["container"] = {"pass": not probs,
                             "output": "\n".join(probs) or
                                       f"video={v_dur}s audio={a_dur}s root={root_dur}s {res}"}
    failed |= bool(probs)

    # 2. presence v2
    qa_dir = ws / "qa" / "presence"
    p = subprocess.run([sys.executable, str(CHECK_PRESENCE), str(mp4),
                        str(qa_dir), "--workspace", str(ws)],
                       capture_output=True, text=True)
    sections["presence"] = {"pass": p.returncode == 0,
                            "output": (p.stdout + p.stderr).strip()}
    failed |= p.returncode != 0

    # 3. shared frame evidence — purge first: stale frames from an earlier cut
    # misled a QA lane on 2026-07-10; only this render's evidence may live here
    frames_dir = ws / "qa" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("*.png"):
        old.unlink()
    extracted = []
    for sc in scenes:
        end = sc["start"] + sc["duration"]
        for pos, t in (("early", sc["start"] + 0.3),
                       ("mid", sc["start"] + sc["duration"] / 2),
                       ("late", end - 0.3)):
            t = max(0.0, min(t, (v_dur or end) - 0.05))
            name = f"f{t:07.2f}s_{sc['id']}_{pos}.png"
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
                 str(frames_dir / name)], check=False)
            if (frames_dir / name).is_file() and (frames_dir / name).stat().st_size > 0:
                extracted.append(name)
    sections["frames"] = {"pass": len(extracted) == 3 * len(scenes),
                          "output": f"{len(extracted)} frames -> {frames_dir}"}
    failed |= len(extracted) != 3 * len(scenes)

    verdict = "FAIL" if failed else "PASS"
    if as_json:
        print(json.dumps({"verdict": verdict, "sections": sections}, indent=2))
    else:
        print(f"VERIFY-RENDER VERDICT: {verdict}   ({mp4.name})")
        for name, sec in sections.items():
            if not isinstance(sec, dict):
                continue
            mark = "ok " if sec["pass"] else "!! "
            print(f"\n[{mark}] {name}")
            print("  " + sec["output"].replace("\n", "\n  "))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
