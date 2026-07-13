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
  5. script_match                  — approved lesson script (.txt) vs the
                                     whisper transcript, word-level diff.
                                     Threshold-based, never exact-match:
                                     whisper small.en mishears ~1 word in ~360,
                                     so isolated misses pass with printed
                                     warnings; a high mismatch rate or a run of
                                     consecutive misses (= a misread/dropped
                                     sentence) fails. Script auto-located from
                                     the workspace stem, or pass --script.

Exit 0 = cleared for render. Exit 1 = fix and re-run. This is the gate that
lets the QA gauntlet's agent lanes shrink to judgment-only work.

Usage:  preflight.py <workspace> [--script <approved.txt>] [--json]
"""

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import ffprobe_duration, norm_token, parse_scenes

CHECK_BOUNDARIES = Path(__file__).resolve().parent / "check_boundaries.py"
TOL = 0.002

# script_match thresholds — whisper small.en's known noise floor is ~1 mishear
# per ~360 words (~0.3%), so the gate is threshold-based, never exact-match.
RATE_WARN = 0.005   # ≤ this: PASS, diffs printed as warnings (noise floor)
RATE_FAIL = 0.02    # > this: FAIL — the TTS read the wrong text
RUN_FAIL = 4        # ≥ this many consecutive missed words: FAIL — a sentence
                    # was misread/dropped, not a transcription hiccup
LESSON_SCRIPTS = Path(__file__).resolve().parent.parent / "lesson-scripts"

DASH_RE = re.compile(r"[‒–—―/-]+")


def tokenize_for_diff(text: str):
    """Lowercase word tokens for the script-vs-transcript diff. Em/en-dash,
    hyphen and slash compounds split into separate tokens first (whisper emits
    'buzzwords—just' as one token); punctuation then stripped per token."""
    return [t for t in (norm_token(w)
                        for w in DASH_RE.sub(" ", text.lower()).split()) if t]


def diff_script_transcript(script_toks, heard_toks):
    """Word-level diff. Returns (mismatch_rate, longest_miss_run, segments) —
    segments are human-readable mismatch lines with surrounding context."""
    sm = difflib.SequenceMatcher(a=script_toks, b=heard_toks, autojunk=False)
    mismatch, max_run, segments = 0, 0, []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        n = max(i2 - i1, j2 - j1)
        mismatch += n
        max_run = max(max_run, n)
        pre = " ".join(script_toks[max(0, i1 - 3):i1])
        post = " ".join(script_toks[i2:i2 + 3])
        said = " ".join(script_toks[i1:i2]) or "(nothing)"
        heard = " ".join(heard_toks[j1:j2]) or "(nothing)"
        segments.append(f"@ script word {i1}: …{pre} [{said}] {post}… "
                        f"-> transcript heard [{heard}]")
    return mismatch / len(script_toks), max_run, segments


def locate_script(ws: Path, scripts_root: Path = LESSON_SCRIPTS):
    """Workspace dir name is the script stem <section>_<program-slug>_<date>;
    the approved script is lesson-scripts/<program-slug>/<stem>.txt."""
    parts = ws.name.split("_")
    if len(parts) != 3:
        return None
    candidate = scripts_root / parts[1] / f"{ws.name}.txt"
    return candidate if candidate.is_file() else None


def check_script_match(ws: Path, script_path=None, scripts_root=LESSON_SCRIPTS):
    """The script-vs-transcript fidelity gate (check 5). Never crashes the
    gate on a missing approved script — WARNs and skips instead."""
    if script_path is None:
        script_path = locate_script(ws, scripts_root)
        if script_path is None:
            return {"pass": True, "output":
                    f"WARN: approved script not found for stem {ws.name!r} "
                    f"under {scripts_root} and no --script given — "
                    f"script-vs-transcript check SKIPPED"}
    script_path = Path(script_path)
    if not script_path.is_file():
        return {"pass": False,
                "output": f"--script {script_path} does not exist"}
    tr_path = ws / "assets/voice/transcript.json"
    if not tr_path.is_file():
        return {"pass": True, "output":
                f"WARN: {tr_path} missing — script-vs-transcript check "
                f"SKIPPED (compile_check already reports the transcript)"}
    script_toks = tokenize_for_diff(script_path.read_text())
    heard_toks = tokenize_for_diff(
        " ".join(w["text"] for w in json.loads(tr_path.read_text())))
    if not script_toks:
        return {"pass": False,
                "output": f"approved script {script_path} is empty"}
    rate, max_run, segments = diff_script_transcript(script_toks, heard_toks)
    lines = [f"script: {script_path}",
             f"{len(script_toks)} script words vs {len(heard_toks)} transcript "
             f"words — mismatch rate {rate:.2%}, longest miss run {max_run}"]
    lines += [f"WARN {s}" for s in segments]
    if max_run >= RUN_FAIL:
        lines.append(f"FAIL: {max_run} consecutive mismatched words — a "
                     f"sentence was misread or dropped, not a whisper hiccup")
        return {"pass": False, "output": "\n".join(lines)}
    if rate > RATE_FAIL:
        lines.append(f"FAIL: mismatch rate {rate:.2%} > {RATE_FAIL:.1%} — "
                     f"the narration does not match the approved script")
        return {"pass": False, "output": "\n".join(lines)}
    if rate > RATE_WARN:
        lines.append(f"WARN: mismatch rate {rate:.2%} is above the whisper "
                     f"small.en noise floor (~{RATE_WARN:.1%}) — eyeball the "
                     f"diffs above before rendering")
    return {"pass": True, "output": "\n".join(lines)}


def run_tool(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    script_override = None
    if "--script" in argv:
        i = argv.index("--script")
        if i + 1 >= len(argv):
            print("--script requires a path", file=sys.stderr)
            sys.exit(2)
        script_override = Path(argv[i + 1]).resolve()
        del argv[i:i + 2]
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

    # 5. script fidelity — approved script vs whisper transcript
    sections["script_match"] = check_script_match(ws, script_override)
    failed |= not sections["script_match"]["pass"]

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
