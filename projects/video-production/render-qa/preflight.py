#!/usr/bin/env python3
"""One-command pre-render gate for SCLA HyperFrames lesson builds.

Runs every deterministic check that used to be spread across QA lanes and
ad-hoc scripts, in one pass, BEFORE the expensive render:

  1. compile_timeline.py --check   — anchors resolve, no boundary/cue drift,
                                     no missing padding (the 2026-07-10
                                     cue-mismatch class dies here)
  2. check_boundaries.py           — frame.md pacing rules vs transcript
                                     (independent implementation: air, mid-word
                                     /mid-sentence cuts, question air, final
                                     hold, root-vs-audio)
  3. coverage                      — scene clips tile 0 → root exactly: first
                                     scene at 0, no gaps/overlaps, last scene
                                     end == root duration, audio attr == true
                                     wav duration (ffprobe)
  4. variables                     — every scene sets theme; one theme per
                                     video; cue counts match list lengths
                                     (also enforced by the compiler)

Exit 0 = cleared for render. Exit 1 = fix and re-run. This is the gate that
lets the QA gauntlet's agent lanes shrink to judgment-only work.

Usage:  preflight.py <workspace> [--json]
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import ffprobe_duration, parse_scenes

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECK_BOUNDARIES = REPO_ROOT / ".claude/skills/adversarial-qa/scripts/check_boundaries.py"
TOL = 0.002


def run_tool(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0]).resolve()
    sections, failed = {}, False

    # 1. compiler check
    rc, out = run_tool([sys.executable, str(Path(__file__).parent / "compile_timeline.py"),
                        str(ws), "--check"])
    sections["compile_check"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 2. boundary rules (independent checker)
    rc, out = run_tool([sys.executable, str(CHECK_BOUNDARIES), str(ws)])
    sections["boundaries"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 3. coverage
    html = (ws / "index.html").read_text()
    scenes = parse_scenes(html)
    problems = []
    if scenes:
        scenes.sort(key=lambda s: s["start"])
        if abs(scenes[0]["start"]) > TOL:
            problems.append(f"first scene starts at {scenes[0]['start']}s, not 0")
        for a, b in zip(scenes, scenes[1:]):
            edge = a["start"] + a["duration"]
            if abs(edge - b["start"]) > TOL:
                kind = "gap" if edge < b["start"] else "overlap"
                problems.append(f"{kind} of {abs(edge - b['start']):.3f}s between "
                                f"{a['id']} (ends {edge:.3f}) and {b['id']} "
                                f"(starts {b['start']:.3f}) — bare canvas / double-draw")
        import re as _re
        root = _re.search(r'id="root"[^>]*data-duration="([\d.]+)"', html)
        last_end = scenes[-1]["start"] + scenes[-1]["duration"]
        if root and abs(float(root.group(1)) - last_end) > TOL:
            problems.append(f"root duration {root.group(1)}s != last scene end "
                            f"{last_end:.3f}s")
        audio_attr = _re.search(r'<audio\b[^>]*data-duration="([\d.]+)"', html)
        wav = ffprobe_duration(ws / "assets/voice/narration.wav")
        if audio_attr and wav and abs(float(audio_attr.group(1)) - wav) > 0.05:
            problems.append(f"<audio> data-duration {audio_attr.group(1)}s != "
                            f"true wav duration {wav:.3f}s (ffprobe)")
    else:
        problems.append("no scene slots found")
    sections["coverage"] = {"pass": not problems, "output": "\n".join(problems) or "ok"}
    failed |= bool(problems)

    # 4. variables: one theme per video
    themes = {s["variables"].get("theme") for s in scenes if s["variables"]}
    theme_problems = []
    if len(themes) > 1:
        theme_problems.append(f"mixed style packages in one video: {sorted(themes)}")
    if None in themes or "" in themes:
        theme_problems.append("scene(s) missing the theme variable")
    sections["variables"] = {"pass": not theme_problems,
                             "output": "\n".join(theme_problems) or
                                       f"theme={next(iter(themes), '?')} on all scenes"}
    failed |= bool(theme_problems)

    verdict = "FAIL" if failed else "PASS"
    if as_json:
        print(json.dumps({"verdict": verdict, "sections": sections}, indent=2))
    else:
        print(f"PREFLIGHT VERDICT: {verdict}")
        for name, sec in sections.items():
            mark = "ok " if sec["pass"] else "!! "
            print(f"\n[{mark}] {name}")
            print("  " + sec["output"].replace("\n", "\n  "))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
