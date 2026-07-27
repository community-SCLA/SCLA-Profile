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
  6. pacing                        — Motion v2 (frame.md "Pacing budget",
                                     2026-07-27): per scene, visual events =
                                     entrance settle (1.2s) + every compiled
                                     cue + the closing beat (duration-0.5);
                                     largest event gap FAILs above 4.5s (WARN
                                     3.5s). Duration caps: 12.5s standard,
                                     title 6.5s, outro 8.5s (title/outro are
                                     duration-capped, gap-exempt). Background
                                     drift never counts — pacing is graded on
                                     communicative beats, not pixel motion.
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
from hfp_common import ffprobe_duration, get_attr, norm_token, parse_scenes

CHECK_BOUNDARIES = Path(__file__).resolve().parent / "check_boundaries.py"
TOL = 0.002

# pacing gate (Motion v2, 2026-07-27 — normative numbers in frame.md
# "Pacing budget"): a failing scene is re-authored (split it, add cues, move
# the boundary), never waved through on background drift.
GAP_FAIL = 4.5        # s without a visual event -> FAIL
GAP_WARN = 3.5        # s without a visual event -> WARN
SCENE_CAP = 12.5      # s, standard scene duration cap
TITLE_CAP = 6.5       # s, scla-title (duration-capped, gap-exempt)
OUTRO_CAP = 8.5       # s, scla-outro (duration-capped, gap-exempt)
ENTRANCE_SETTLE = 1.2 # s, Motion v2 entrance budget = first visual event
CLOSING_BEAT = 0.5    # s before scene end the closing beat lands

# HeyGen swap (landed 2026-07-22, see decisions/log.md, same detection idiom
#   as compile_timeline.words_path_for()): the illustrated pipeline's default
#   TTS is HeyGen starfish, so this check reads assets/voice/narration.words.json
#   (native word timestamps, synth_narration.py) when present, else falls back
#   to Whisper's transcript.json (--provider kokoro workspaces). Detected
#   per-workspace by which file is on disk, not a global flag — a hardcoded
#   switch would silently skip the fidelity gate on every kokoro workspace
#   (narration.words.json never exists there, and the "file missing" branch
#   below is a WARN+skip, not a failure). Note: HeyGen words are the exact
#   synthesized text (no Whisper mishears), so script_match is a near-exact
#   check on HeyGen workspaces — the RATE_WARN/RATE_FAIL/RUN_FAIL thresholds
#   below still pass as-is (strictly better) and were left untightened;
#   revisit if HeyGen-path noise ever shows up in practice.
HEYGEN_WORDS_FILE = "narration.words.json"  # synth_narration.py / heygen-tts.mjs output

# script_match thresholds — whisper small.en's known noise floor is ~1 mishear
# per ~360 words (~0.3%), so the gate is threshold-based, never exact-match.
RATE_WARN = 0.005   # ≤ this: PASS, diffs printed as warnings (noise floor)
RATE_FAIL = 0.02    # > this: FAIL — the TTS read the wrong text
RUN_FAIL = 4        # ≥ this many consecutive missed words: FAIL — a sentence
                    # was misread/dropped, not a transcription hiccup
LESSON_SCRIPTS = Path(__file__).resolve().parent.parent / "lesson-scripts"

DASH_RE = re.compile(r"[‒–—―/-]+")


_NUM_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
_NUM_SCALES = {"hundred": 100, "thousand": 1000, "million": 1000000, "billion": 1000000000}


def _fold_number_words(toks):
    """Collapse runs of spelled-out cardinal number words into a single digit
    token ('eighty thousand' -> '80000', 'forty' -> '40'). Applied SYMMETRICALLY
    to both the script and the transcript, so it only ever removes number-FORMAT
    noise (whisper writes spoken numbers as digits: '80,000' -> norm '80000';
    small numbers like 'one' it keeps as a word) — value fidelity is preserved
    because a genuine misread lands on different digits and still mismatches.
    Non-number words are untouched."""
    out, i, n = [], 0, len(toks)
    while i < n:
        j, total, current, saw = i, 0, 0, False
        while j < n and (toks[j] in _NUM_UNITS or toks[j] in _NUM_SCALES):
            w = toks[j]
            if w in _NUM_UNITS:
                current += _NUM_UNITS[w]
            elif w == "hundred":
                current = (current or 1) * 100
            else:  # thousand / million / billion
                total += (current or 1) * _NUM_SCALES[w]
                current = 0
            saw = True
            j += 1
        if saw:
            out.append(str(total + current))
            i = j
        else:
            out.append(toks[i])
            i += 1
    return out


def tokenize_for_diff(text: str):
    """Lowercase word tokens for the script-vs-transcript diff. Em/en-dash,
    hyphen and slash compounds split into separate tokens first (whisper emits
    'buzzwords—just' as one token); punctuation then stripped per token; spelled
    cardinal numbers folded to digits so 'eighty thousand' == whisper's '80,000'
    (number-heavy stat lessons otherwise trip the fidelity gate on pure format)."""
    return _fold_number_words(
        [t for t in (norm_token(w)
                     for w in DASH_RE.sub(" ", text.lower()).split()) if t])


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
    """The workspace dir name IS the script stem. The program is the folder the
    script lives in (lesson-scripts/<program>/…), not a segment of the stem — so
    we locate by searching every program's state folders for a matching stem,
    rather than parsing program out of the name. This is convention-agnostic:
    it works for both <section>_<program>_<date> and m<#>_<title>_<date> stems.

    Scripts live in state folders (location = lifecycle state): refined/ (the
    render queue) is the normal home while a build exists; root is raw intake;
    rendered/ covers re-verification of a shipped lesson."""
    filename = f"{ws.name}.txt"
    for program in sorted(p for p in scripts_root.iterdir() if p.is_dir()):
        for sub in ("refined", "", "rendered"):
            candidate = program / sub / filename
            if candidate.is_file():
                return candidate
    return None


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
    # Native HeyGen words file if synth_narration.py wrote one, else the
    # Whisper transcript.json (--provider kokoro workspaces). Same flat
    # text/start/end shape either way.
    heygen_words = ws / "assets/voice" / HEYGEN_WORDS_FILE
    tr_path = heygen_words if heygen_words.is_file() else ws / "assets/voice/transcript.json"
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


def _cue_values(variables):
    """Every compiled numeric cue in a scene's data-variable-values: any
    '*Cues' comma list plus the single-value cue keys (mapCue, iconCue)."""
    vals = []
    for k, v in variables.items():
        raw = str(v)
        if k.endswith("Cues"):
            parts = raw.split(",")
        elif k in ("mapCue", "iconCue"):
            parts = [raw]
        else:
            continue
        for p in parts:
            try:
                vals.append(float(p.strip()))
            except ValueError:
                pass
    return vals


def check_pacing(scenes):
    """The pacing gate (check 6) — Motion v2. Events per scene = entrance
    settle + compiled cues + closing beat; grade the largest gap, and cap
    scene durations. title/outro are duration-capped and gap-exempt (they
    legitimately carry zero cues)."""
    problems, warns = [], []
    for s in scenes:
        dur = s["duration"]
        if dur != dur:  # NaN — placeholder pre-compile; compile_check owns it
            continue
        tpl = Path(get_attr(s["tag"], "data-composition-src") or "").stem
        if tpl == "scla-title":
            if dur > TITLE_CAP:
                problems.append(f"{s['id']}: title card runs {dur:.1f}s > "
                                f"{TITLE_CAP}s — a title holds only for the "
                                f"opening line; land the rest in a content scene")
            continue
        if tpl == "scla-outro":
            if dur > OUTRO_CAP:
                problems.append(f"{s['id']}: outro runs {dur:.1f}s > "
                                f"{OUTRO_CAP}s — tighten the closing span")
            continue
        if dur > SCENE_CAP:
            problems.append(f"{s['id']}: {dur:.1f}s > {SCENE_CAP}s cap — "
                            f"split the scene at a sentence end")
        events = [ENTRANCE_SETTLE] + _cue_values(s["variables"])
        events.append(max(dur - CLOSING_BEAT, ENTRANCE_SETTLE))
        events = sorted(e for e in events if 0 <= e <= dur + 1e-9)
        worst, seg = 0.0, (0.0, 0.0)
        for a, b in zip(events, events[1:]):
            if b - a > worst:
                worst, seg = b - a, (a, b)
        if worst > GAP_FAIL:
            problems.append(f"{s['id']}: {worst:.1f}s with no visual event "
                            f"({seg[0]:.1f}s→{seg[1]:.1f}s of {dur:.1f}s) — "
                            f"add cues, split the scene, or move the boundary")
        elif worst > GAP_WARN:
            warns.append(f"WARN {s['id']}: largest event gap {worst:.1f}s "
                         f"(>{GAP_WARN}s) — room for one more cued beat")
    out = problems + warns
    return {"pass": not problems,
            "output": "\n".join(out) or
                      f"ok — caps held, every event gap ≤ {GAP_WARN}s"}


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

    # 2b. one template file per slot (2026-07-27). HyperFrames keys a
    # sub-composition's timeline and element ids to the FILE, so two slots
    # sharing one template collide: the surviving timeline animates one
    # instance and the others render blank headers. Invisible in Studio
    # preview (per-scene iframes) — composited render only.
    rc, out = run_tool([sys.executable, str(Path(__file__).parent / "instance_templates.py"),
                        str(ws), "--check"])
    sections["instance_templates"] = {"pass": rc == 0, "output": out.strip()}
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
    # Motion v2 (2026-07-27): exits/closing beats key off sceneDuration, and the
    # compiler only injects it when the scene DECLARES the key — a slot without
    # it silently runs on the template's fallback and mistimes its exit.
    no_sdur = [s["id"] for s in scenes if "sceneDuration" not in s["variables"]]
    if no_sdur:
        theme_problems.append(f"scene(s) missing the sceneDuration variable "
                              f"(exits/closing beats mistime without it): "
                              f"{', '.join(no_sdur)}")
    sections["variables"] = {"pass": not theme_problems,
                             "output": "\n".join(theme_problems) or
                                       f"theme={next(iter(themes), '?')} on all scenes"}
    failed |= bool(theme_problems)

    # 5. script fidelity — approved script vs whisper transcript
    sections["script_match"] = check_script_match(ws, script_override)
    failed |= not sections["script_match"]["pass"]

    # 6. pacing — Motion v2 cue-gap budget + scene duration caps
    sections["pacing"] = check_pacing(scenes)
    failed |= not sections["pacing"]["pass"]

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
