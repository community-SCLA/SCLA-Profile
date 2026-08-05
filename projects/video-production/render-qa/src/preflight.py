#!/usr/bin/env python3
"""One-command pre-render gate for SCLA HyperFrames lesson builds.

Runs every deterministic check that used to be spread across QA lanes and
ad-hoc scripts, in one pass, BEFORE the expensive render:

  1. compile_timeline.py --check   — anchors resolve, no boundary/cue drift,
                                     no missing padding (the 2026-07-10
                                     cue-mismatch class dies here)
  2. check_boundaries.py           — design-contract.md pacing rules vs transcript
                                     (independent implementation: air, mid-word
                                     /mid-sentence cuts, question air, final
                                     hold, root-vs-audio)
  2c. composition_freshness        — workspace compositions/ is copied once at
                                     init and never refreshed (render-qa
                                     friction log, 2026-07-27 C2): compares
                                     each non-instanced composition's
                                     <style>/<script> content against the
                                     current design-system/compositions/
                                     source. Instanced clones (basename__
                                     suffix.html) are skipped — their ids are
                                     deliberately renamed and can't be diffed
                                     against the un-namespaced source.
  3. coverage                      — scene clips tile 0 → root exactly: first
                                     scene at 0, no gaps/overlaps, last scene
                                     end == root duration, audio attr == true
                                     wav duration (ffprobe)
  4. variables                     — every scene sets theme; one theme per
                                     video; cue counts match list lengths
                                     (also enforced by the compiler)
  5. script_match                  — approved lesson script (.txt) vs the
                                     whisper transcript, word-level diff.
  6. pacing                        — Motion v2 (design-contract.md "Pacing budget",
                                     2026-07-27): per scene, visual events =
                                     entrance settle (1.2s) + every compiled
                                     cue + the closing beat (duration-0.5);
                                     largest event gap FAILs above 4.0s (WARN
                                     3.0s). Duration caps: 12.5s standard,
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
  7. text                          — check_text.py: minimum on-frame text size
                                     (floors LOADED from tokens.yml
                                     typography.min-size via tokens.py; body
                                     rose 32 -> 40px on 2026-07-29 because the
                                     floor had been set AT the smallest size in
                                     use, so it could never fire; tokens.yml
                                     typography.min-size) and no on-frame line
                                     that restates its own scene's label or
                                     heading. Both owner calls, 2026-07-27, off
                                     a 30px sub-beat repeating the eyebrow
                                     already sitting at the top of the frame.

Exit 0 = cleared for render. Exit 1 = fix and re-run. This is the gate that
lets the QA gauntlet's agent lanes shrink to judgment-only work.

--static (2026-07-28): run ONLY the sections that are meaningful on a freshly
compiled workspace with NO voice assets — the scene-plan stage, before any TTS
has run. Sections that need audio/transcript/timing (compile_check, boundaries,
coverage, script_match, pacing, inscene_gaps) are SKIPPED with a "(static
mode)" note, never failed. Same exit semantics: 0 = the plan is clean, 1 = fix
the plan. This is the code path scripts/hyperframe-guard.sh runs on every
scenes.json/index.html write, so the authoring-time guard and the hard gate
are one source of truth.

Usage:  preflight.py <workspace> [--script <approved.txt>] [--json] [--static]
"""

import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

# src/ -> render-qa/ -> video-production/
DESIGN_SYSTEM_COMPOSITIONS = Path(__file__).resolve().parents[2] / "design-system" / "compositions"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tokens
from hfp_common import (ffprobe_duration, get_attr, load_beats, norm_token,
                        onframe_strings, parse_scenes)
from stem import StemError, base as stem_base, is_canonical

CHECK_BOUNDARIES = Path(__file__).resolve().parent / "check_boundaries.py"
TOL = 0.002

# pacing gate (Motion v2, 2026-07-27 — normative numbers in design-contract.md
# "Pacing budget"): a failing scene is re-authored (split it, add cues, move
# the boundary), never waved through on background drift.
GAP_FAIL = 4.0        # s without a visual event -> FAIL (tightened 2026-07-28:
                      # the pilot's 4.5s empty-heading hold passed at 4.5)
GAP_WARN = 3.0        # s without a visual event -> WARN
SCENE_CAP = 12.5      # s, standard scene duration cap
TITLE_CAP = 6.5       # s, scla-title (duration-capped, gap-exempt)
OUTRO_CAP = 8.5       # s, scla-outro (duration-capped, gap-exempt)
ENTRANCE_SETTLE = 1.2 # s, Motion v2 entrance budget = first visual event
CLOSING_BEAT = 0.5    # s before scene end the closing beat lands

# in-scene silence gate (2026-07-28). HeyGen's Oxana emits 0.98-1.26s of real
# silence at sentence/clause boundaries INSIDE a scene, non-deterministically
# (3x variance on identical syntax), and the picture dies with the sound
# because compile_timeline.resolve_cues() derives every cue from these same
# word timestamps — the owner reported it as "strange sound gaps / a major
# glitch or lag". synth_narration.compress_gaps() now caps in-scene silence at
# 0.5s; this gate is the regression guard, set slack above that cap so it fires
# only if the compressor stops running (kokoro path, a provider swap, a
# hand-edited words file), never on the compressor's own output.
INSCENE_GAP_FAIL = 0.8  # s of in-scene inter-word silence -> FAIL

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
LESSON_SCRIPTS = Path(__file__).resolve().parents[2] / "lesson-scripts"

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


# The stage folders a script can sit in, newest naming first. The stage folder
# is NOT the program — `lesson-scripts/<program>/<stage>/<stem>.txt` — so every
# slug derivation has to step over it. Keeping the retired `refined`/`rendered`
# names costs nothing and keeps pre-rename workspaces resolving.
#
# This list used to be written out twice more, and both copies missed the
# 2026-08-04 inbox/ready/published rename: `check_title_card` and
# `check_freeform_title` stepped over "refined"/"rendered" only, so every
# script in a `ready/` folder resolved to the program 'ready' and the title
# card check failed on EVERY current build, template and freeform alike.
# One constant, three readers (found on the 2026-08-04 freeform trial).
STAGE_DIRS = ("ready", "inbox", "published", "refined", "rendered")


def program_of(script_path) -> str:
    """The program folder a script belongs to, stepping over its stage folder."""
    p = Path(script_path)
    return p.parents[1].name if p.parent.name in STAGE_DIRS else p.parent.name


def locate_script(ws: Path, scripts_root: Path = LESSON_SCRIPTS):
    """The workspace dir name IS the script stem. The program is the folder the
    script lives in (lesson-scripts/<program>/…), not a segment of the stem — so
    we locate by searching every program's state folders for a matching stem,
    rather than parsing program out of the name. This is convention-agnostic:
    it works for both <section>_<program>_<date> and m<#>_<title>_<date> stems.

    Scripts live in state folders (location = lifecycle state, and the folder
    name IS the stage name since 2026-08-04): ready/ (the render queue) is the
    normal home while a build exists; inbox/ is raw intake; published/ covers
    re-verification of a shipped lesson.

    Matched on BASE, not the full stem. Since 2026-07-28 a stem's date is the
    date of the most recent action on *that artifact*, so a workspace built on
    the 28th from a script refined on the 6th legitimately has a different
    stem from its own script. Exact-filename matching (what this did before)
    silently found nothing in that case, and check_script_match's missing-script
    branch is a WARN-and-skip — so the fabrication guard would have quietly
    disarmed itself on every build rather than failing loudly."""
    try:
        want = stem_base(ws.name)
    except StemError:
        want = None
    if not scripts_root.is_dir():
        # A missing script library is "no script found", not a crash. It used
        # to raise FileNotFoundError straight out of the gate (2026-07-29).
        return None
    for program in sorted(p for p in scripts_root.iterdir() if p.is_dir()):
        for sub in STAGE_DIRS:
            exact = program / sub / f"{ws.name}.txt"
            if exact.is_file():
                return exact
            if want is None:
                continue
            for candidate in sorted((program / sub).glob("*.txt")
                                    if (program / sub).is_dir() else []):
                try:
                    if stem_base(candidate.stem) == want:
                        return candidate
                except StemError:
                    continue
    return None


def check_script_match(ws: Path, script_path=None, scripts_root=LESSON_SCRIPTS):
    """The script-vs-transcript fidelity gate (check 5) — the render-stage half
    of the fabrication ban.

    A MISSING APPROVED SCRIPT IS A HARD FAILURE (2026-07-29). This branch used
    to return `pass: True` with a WARN, which is the worst possible answer: the
    one gate standing between a build and fabricated on-screen content
    disarmed itself precisely when it could not verify anything, and reported
    green while doing it. "I could not check" is not "it is fine". A gate that
    passes when it cannot grade is how `nothing-graded` and the CANVAS claim
    got here too.

    The escape hatch stays explicit: pass --script <path> to name the script
    yourself. Silence is not an escape hatch."""
    if script_path is None:
        script_path = locate_script(ws, scripts_root)
        if script_path is None:
            return {"pass": False, "output":
                    f"FAIL: no approved script found for stem {ws.name!r} under "
                    f"{scripts_root} (matched on BASE, not the full stem) and no "
                    f"--script given. The script-vs-transcript diff is the "
                    f"render-stage half of the fabrication ban — it cannot be "
                    f"skipped silently. File the script in the program's "
                    f"ready/ folder, or pass --script <path> explicitly."}
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


def check_inscene_gaps(ws: Path, max_gap=INSCENE_GAP_FAIL):
    """The in-scene silence gate (check 9, 2026-07-28).

    Grades only the silence BETWEEN words of the SAME scene. Scene-boundary
    silence is deliberate (synth_narration's air + lead, 0.3/0.45 + 0.15) and
    is graded by check_boundaries, so the two are told apart with the synthesis
    manifest's per-scene windows rather than a magic-number threshold — without
    that manifest every boundary would read as a 0.6s in-scene gap.

    Reads the whole-file words (narration.words.json), never the per-scene
    scenes/scene-NN.words.json: those are the provider's untouched response, so
    they still carry the pauses compress_gaps() excised from the audio."""
    voice = ws / "assets" / "voice"
    words_path = voice / HEYGEN_WORDS_FILE
    manifest_path = voice / "scene-times.json"
    if not words_path.is_file():
        return {"pass": True, "output":
                f"WARN: {HEYGEN_WORDS_FILE} missing (kokoro/legacy workspace) "
                f"— in-scene gap check SKIPPED"}
    if not manifest_path.is_file():
        return {"pass": True, "output":
                "WARN: assets/voice/scene-times.json missing — cannot separate "
                "in-scene silence from scene-boundary air, check SKIPPED"}
    words = json.loads(words_path.read_text())
    scenes = json.loads(manifest_path.read_text()).get("scenes", [])
    if len(words) < 2 or not scenes:
        return {"pass": True, "output": "too few words/scenes to grade"}

    def scene_of(t):
        for i, s in enumerate(scenes):
            if t <= s["end"] + TOL:
                return i
        return len(scenes) - 1

    problems, worst, worst_at = [], 0.0, ""
    for prev, nxt in zip(words, words[1:]):
        gap = nxt["start"] - prev["end"]
        if gap <= 0 or scene_of(prev["end"]) != scene_of(nxt["start"]):
            continue  # overlap, or the boundary air check_boundaries owns
        if gap > worst:
            worst, worst_at = gap, f"{prev['text']!r} -> {nxt['text']!r}"
        if gap > max_gap:
            problems.append(
                f"{gap:.2f}s of silence inside scene "
                f"{scene_of(prev['end']) + 1:02d} at {nxt['start']:.2f}s "
                f"({prev['text']!r} -> {nxt['text']!r}) — over the {max_gap}s "
                f"cap; audio AND picture both hold there (cues derive from "
                f"these timestamps)")
    if problems:
        problems.append("re-run synth_narration.py (it caps in-scene silence "
                        "at MAX_INSCENE_GAP) then compile_timeline.py --apply")
    return {"pass": not problems,
            "output": "\n".join(problems) or
                      f"ok — largest in-scene gap {worst:.2f}s ≤ {max_gap}s"
                      + (f" ({worst_at})" if worst_at else "")}


def _style_script_digest(html_text: str) -> str:
    """Hash of every <style>/<script> block's inner text.

    Not a whole-file hash: HyperFrames re-serializes composition HTML on
    catalog/build (quote style, self-closing tags, injected data-hf-id
    attrs), so a byte-for-byte diff of the full file false-positives on
    every already-initialized workspace, fresh or not. <style>/<script>
    content is RAWTEXT and passes through that re-serialization unchanged,
    and it's where every real template edit (motion, tokens, layout) lives —
    so it's the reliable freshness signal.
    """
    blocks = re.findall(r"<(?:style|script)\b[^>]*>(.*?)</(?:style|script)>", html_text, re.S)
    return hashlib.sha256("".join(blocks).encode("utf-8")).hexdigest()


def check_title_card(ws: Path, scenes, script_override=None,
                     scripts_root=LESSON_SCRIPTS):
    """Title-card provenance gate (check 7b). The eyebrow must equal the
    program's on-screen display name from tokens.yml's `programs:` map (was a
    markdown table in frame.md until 2026-07-29), the map itself must name the
    lesson-scripts folders it keys on (tokens.programs_problems — the banner
    rule, 2026-07-29), and the title must be the stem's title segment de-kebabed
    (case-insensitive). All three were builder-invented before 2026-07-28."""
    problems = []
    title_scene = None
    for sc in scenes:
        src = get_attr(sc["tag"], "data-composition-src") or ""
        if "scla-title" in src:
            title_scene = sc
            break
    if title_scene is None:
        return {"pass": True, "output": "no scla-title scene — skipped"}

    # Program = the lesson-scripts folder the script lives in.
    script = Path(script_override) if script_override else locate_script(ws)
    if script is None:
        return {"pass": False,
                "output": "cannot locate script to derive the program slug"}
    program = program_of(script)

    # Display names come from the workspace's tokens.yml copy. This used to
    # scrape a markdown table out of design-contract.md — a checker parsing prose, which
    # is exactly the coupling the 2026-07-29 split removed.
    display = tokens.programs(ws)
    if not display:
        return {"pass": False,
                "output": "tokens.yml declares no `programs:` map "
                          "(is the workspace scaffold stale?)"}
    # Grade the MAP before grading the eyebrow against it. Comparing an eyebrow
    # to an unvalidated map is a gate that certifies whatever the map says — how
    # an Early Career Boost lesson shipped banner-labelled "Career Accelerator"
    # with 7b green (owner, 2026-07-29).
    problems.extend(tokens.programs_problems(ws))

    vars_ = title_scene["variables"]
    want_eyebrow = display.get(program)
    got_eyebrow = str(vars_.get("eyebrow", "")).strip()
    if want_eyebrow is None:
        problems.append(f"program '{program}' missing from tokens.yml's "
                        f"`programs:` map — add it there, never on the fly")
    elif got_eyebrow.lower() != want_eyebrow.lower():
        problems.append(f"eyebrow {got_eyebrow!r} != display name "
                        f"{want_eyebrow!r} for program {program}")

    # Stem title segment: strip a leading m<N>_ and the trailing
    # [_<program>]_<date> parts, de-kebab the rest.
    stem = ws.name
    parts = stem.split("_")
    if re.fullmatch(r"m\d+", parts[0]):
        parts = parts[1:]
    if parts and re.fullmatch(r"\d{4}-\d{2}-\d{2}", parts[-1]):
        parts = parts[:-1]
    if parts and parts[-1] == program:
        parts = parts[:-1]
    want_title_words = "_".join(parts).replace("-", " ").split()
    # A trailing part number (`...-resume-pt1`, `...-tool-pt2`) is a FILING
    # convention that tells two halves of one lesson apart on disk — it is not
    # part of the lesson's name and must not reach the frame (owner,
    # 2026-07-29; check_copy's `part-reference` rule rejects it in copy). Both
    # gates have to agree, or removing it from the title card to satisfy one
    # fails the other, which is exactly what happened when the rule landed.
    if want_title_words and re.fullmatch(r"pt\.?\d+", want_title_words[-1], re.I):
        want_title_words = want_title_words[:-1]
    got_title_words = re.sub(r"[^\w\s]", "", str(vars_.get("title", ""))).lower().split()
    if [w.lower() for w in want_title_words] != got_title_words:
        problems.append(
            f"title {vars_.get('title', '')!r} != stem title "
            f"\"{' '.join(want_title_words)}\" — the title card carries the "
            f"lesson title, never narration or a paraphrase")

    return {"pass": not problems,
            "output": "\n".join(problems) or
                      f"eyebrow={got_eyebrow!r} title ok ({program})"}


def check_composition_freshness(ws: Path):
    """Workspace compositions/ vs the design-system source (C2, 2026-07-27).

    compositions/ is copied into each workspace once at init and never
    refreshed — a design-system template fix (like the B1 icon-flash fix)
    lands silently invisible in every workspace already on disk. This
    compares each non-instanced composition file's <style>/<script> content
    against design-system/compositions/<same name>.html. Instanced clones
    (basename__suffix.html, from instance_templates.py or a hand-namespaced
    duplicate) are skipped: their ids are deliberately renamed per-slot, so
    they can't be diffed against the un-namespaced source without re-running
    the clone step.
    """
    ws_comp_dir = ws / "compositions"
    if not ws_comp_dir.is_dir():
        return {"pass": True, "output": "no compositions/ dir in this workspace"}
    stale, skipped, checked = [], [], 0
    for f in sorted(ws_comp_dir.glob("*.html")):
        if "__" in f.stem:
            skipped.append(f.name)
            continue
        src = DESIGN_SYSTEM_COMPOSITIONS / f.name
        if not src.exists():
            skipped.append(f"{f.name} (no matching design-system source)")
            continue
        checked += 1
        if _style_script_digest(f.read_text()) != _style_script_digest(src.read_text()):
            stale.append(f.name)
    lines = []
    if stale:
        lines.append("stale — refresh from design-system/compositions/ before building: "
                     + ", ".join(stale))
    else:
        lines.append(f"ok — {checked} composition(s) match design-system/compositions/ "
                     f"(style+script)")
    if skipped:
        lines.append(f"not checked ({len(skipped)} instanced clone(s)/unmatched): "
                     + ", ".join(skipped))

    # tokens.yml is copied into the workspace at init exactly like compositions/,
    # and tokens.py reads the WORKSPACE copy when one exists — so every gate
    # that imports a normative number (type floors, safe-area, footer-reserve,
    # content-bottom) grades this build against the snapshot, not the spec.
    # Without this, raising typography.min-size 32 -> 40 on 2026-07-29 silently
    # did not apply to any workspace already on disk: the number "moves in one
    # place" only for workspaces built afterwards. Same failure mode as stale
    # compositions, same remedy — refresh the copy. (2026-07-29, Phase 2;
    # retargeted from design-contract.md to config/tokens.yml when the spec was split.)
    ws_tokens = ws / "tokens.yml"
    src_tokens = DESIGN_SYSTEM_COMPOSITIONS.parent / "config" / "tokens.yml"
    if ws_tokens.is_file() and src_tokens.is_file():
        # summary() carries the scalars; `programs` is a map and lives outside it,
        # so it is compared separately and folded in with its real values — an
        # earlier version added the key to `drift` but formatted from summary(),
        # which printed the useless "programs: workspace None vs spec None".
        ws_tok, src_tok = dict(tokens.summary(ws)), dict(tokens.summary(None))
        ws_tok["programs"] = tokens.programs(ws)
        src_tok["programs"] = tokens.programs(None)
        drift = sorted(k for k in set(ws_tok) | set(src_tok)
                       if k != "tokens_file" and ws_tok.get(k) != src_tok.get(k))
        if drift:
            stale = stale or ["tokens.yml"]
            lines.append(
                "stale tokens.yml — this workspace's copy declares different "
                "normative token(s) than design-system/config/tokens.yml, and "
                "the gates read the COPY: "
                + "; ".join(f"{k}: workspace {ws_tok.get(k)!r} vs spec "
                            f"{src_tok.get(k)!r}" for k in drift)
                + ". Refresh tokens.yml from design-system/config/ before building.")
        else:
            lines.append("ok — tokens.yml matches design-system/config/tokens.yml")
    elif not ws_tokens.is_file():
        lines.append("no tokens.yml in this workspace — gates fall back to "
                     "design-system/config/tokens.yml")

    return {"pass": not stale, "output": "\n".join(lines)}


def run_tool(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ---------------------------------------------------------------------------
# Freeform (agent-native) lane sections — 2026-07-30, decisions/log.md.
# A freeform workspace has no scenes.json, no compiler and no template slots;
# its authoring contract is audio_request.json (the beats) + timing.json
# (computed, never hand-tuned) + design.md + the composition HTML itself.
# Verdict provenance: render-qa/docs/HANDOFF-agent-native-verdict-2026-07-30.md
# ---------------------------------------------------------------------------

def check_freeform_timing(ws: Path, html: str, static=False):
    """Replaces compile_check on the freeform lane: every beat has a computed
    timing row, the timeline covers the root duration, and the ending keeps
    the MIN_FINAL_HOLD floor the owner has rejected twice. check_boundaries
    grades the wav-level form of that floor on the template lane; this grades
    the timing-level form the freeform contract can see (its full wav adapter
    is deferred)."""
    from check_boundaries import MIN_FINAL_HOLD
    problems = []
    beats = load_beats(ws) or []
    if not beats:
        problems.append("audio_request.json carries no narration lines")
    tp = ws / "timing.json"
    if not tp.is_file():
        if static and beats:
            return {"pass": True, "output":
                    f"{len(beats)} beat(s) in the manifest — timing.json not "
                    f"yet computed (plan stage); the full gate requires it"}
        problems.append("timing.json missing — compute beat timings from "
                        "audio_meta.json (never hand-tune) before the full gate")
        return {"pass": False, "output": "\n".join(problems)}
    untimed = [b["id"] for b in beats if b["duration"] != b["duration"]]
    if untimed:
        problems.append(f"beat(s) with no timing row: {', '.join(untimed)}")
    t = json.loads(tp.read_text())
    rows, total = t.get("rows") or [], t.get("total")
    root = re.search(r'id="root"[^>]*data-duration="([\d.]+)"', html)
    if root and total and abs(float(root.group(1)) - float(total)) > 0.05:
        problems.append(f"root data-duration {root.group(1)}s != timing.json "
                        f"total {total}s — the timeline and the manifest disagree")
    hold = None
    if rows and total:
        last = max(rows, key=lambda r: (r.get("audio_start") or 0))
        end = (last.get("audio_start") or 0) + (last.get("audio_dur") or 0)
        hold = float(total) - end
        if hold < MIN_FINAL_HOLD:
            problems.append(
                f"final hold {hold:.2f}s < the {MIN_FINAL_HOLD}s floor — the "
                f"last word needs air to land (the owner rejected a 1.1s "
                f"ending twice; the producer target is 1.8s). Extend the "
                f"closing hold in timing.json's total / root duration.")
    ok = (f"{len(beats)} beat(s), all timed"
          + (f"; final hold {hold:.2f}s" if hold is not None else ""))
    return {"pass": not problems, "output": "\n".join(problems) or ok}


def check_freeform_script_match(ws: Path, script_override=None):
    """The fabrication ban, freeform form: the BEAT MANIFEST — the exact text
    sent to the TTS engine — diffs against the approved script. Static and
    free, so it runs at plan stage too. (The spoken-audio half, whisper vs
    wav, needs the flat-words adapter and is deferred; what was SENT is graded
    here, and the engine's own word timestamps are what drive the reveals.)
    A missing approved script is a hard failure, same as check_script_match —
    'I could not check' is never 'it is fine'."""
    script_path = script_override or locate_script(ws)
    if script_path is None:
        return {"pass": False, "output":
                f"FAIL: no approved script found for stem {ws.name!r} under "
                f"{LESSON_SCRIPTS} and no --script given. The script-vs-beats "
                f"diff is the freeform half of the fabrication ban — it cannot "
                f"be skipped silently."}
    script_path = Path(script_path)
    if not script_path.is_file():
        return {"pass": False, "output": f"--script {script_path} does not exist"}
    beats = load_beats(ws) or []
    heard_toks = tokenize_for_diff(" ".join(b["narration"] for b in beats))
    script_toks = tokenize_for_diff(script_path.read_text())
    if not script_toks:
        return {"pass": False, "output": f"approved script {script_path} is empty"}
    if not heard_toks:
        return {"pass": False,
                "output": "audio_request.json carries no narration text"}
    rate, max_run, segments = diff_script_transcript(script_toks, heard_toks)
    lines = [f"script: {script_path}",
             f"{len(script_toks)} script words vs {len(heard_toks)} beat words "
             f"— mismatch rate {rate:.2%}, longest miss run {max_run}"]
    lines += [f"WARN {s}" for s in segments]
    if max_run >= RUN_FAIL:
        lines.append(f"FAIL: {max_run} consecutive mismatched words — a "
                     f"sentence was rewritten or dropped, not a TTS "
                     f"normalization")
        return {"pass": False, "output": "\n".join(lines)}
    if rate > RATE_FAIL:
        lines.append(f"FAIL: mismatch rate {rate:.2%} > {RATE_FAIL:.1%} — the "
                     f"beat manifest does not carry the approved script")
        return {"pass": False, "output": "\n".join(lines)}
    return {"pass": True, "output": "\n".join(lines)}


def check_freeform_title(ws: Path, script_override=None):
    """The banner rule on the freeform lane: the program's display name and
    the lesson's title must appear in on-frame MARKUP text (chrome built up in
    JS is invisible to every gate, so the freeform contract requires it in
    markup). Compared slug-to-slug, so case and punctuation are free and an
    alias can never pass — same doctrine as tokens.programs_problems()."""
    problems = list(tokens.programs_problems(ws))
    script_path = script_override or locate_script(ws)
    slug = None
    if script_path is not None:
        slug = program_of(script_path)
    joined = tokens.slugify(" ".join(t for _, _, t in onframe_strings(ws)))
    if slug is None:
        problems.append("cannot resolve the program folder (no approved "
                        "script located) — the banner cannot be verified")
    else:
        display = (tokens.programs(ws) or {}).get(slug)
        if not display:
            problems.append(f"program '{slug}' has no display name in "
                            f"tokens.yml `programs:`")
        elif tokens.slugify(display) not in joined:
            problems.append(f"program banner {display!r} not found in any "
                            f"on-frame markup text — the eyebrow names the "
                            f"program on every frame")
    try:
        base = stem_base(ws.name)
        title_seg = re.sub(r"^m\d+_", "", base)
        if slug and title_seg.endswith(f"_{slug}"):
            title_seg = title_seg[: -len(slug) - 1]
        title_seg = re.sub(r"-pt\d+$", "", title_seg)
        if title_seg and title_seg not in joined:
            problems.append(f"lesson title (stem segment {title_seg!r}) not "
                            f"found in any on-frame markup text — the title "
                            f"card carries the lesson's name")
    except StemError:
        pass  # the stem section below owns naming failures
    return {"pass": not problems,
            "output": "\n".join(problems) or "program banner + lesson title "
                                             "found in on-frame markup"}


def check_freeform_ink(ws: Path):
    """The freeform geometry gate: check_ink.py over one snapshot still per
    beat. boxmodel cannot run here — measured at 281 false findings on a build
    verified clean across 34 stills (HANDOFF §2) — so bounds come from real
    pixels, and text-on-text comes from check_layout's per-beat inspector
    pass. Missing or thin snapshots FAIL: nothing-graded is never a pass."""
    beats = load_beats(ws) or []
    snaps = ws / "snapshots"
    pngs = sorted(snaps.glob("*.png")) if snaps.is_dir() else []
    if len(pngs) < max(1, len(beats)):
        return {"pass": False, "output":
                f"{len(pngs)} snapshot still(s) under {snaps} for "
                f"{len(beats)} beat(s) — the pixel bounds gate needs at least "
                f"one still per beat midpoint. Run the pinned CLI: "
                f"npx hyperframes@<pin> snapshot . --at <beat midpoints> "
                f"--no-end -o snapshots"}
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_ink.py"),
                        str(snaps), "--tokens-ws", str(ws)])
    return {"pass": rc == 0, "output": out.strip()}


def check_freeform_pace(ws: Path, static: bool):
    """BUILD-PLAN B1 (2026-08-04): the owner approved one freeform cut of a
    lesson and rejected another, and every rule in this file passed the
    rejected cut while QUARANTINING the approved one — the gate set measured
    animacy, and the owner was responding to idea rate and a carrying object
    (see check_pace.py's module docstring for the full story and its stated
    n=2 calibration limit). The two timing rules (beat-pace, long-beat-share)
    read timing.json alone, so they run in --static; carrier-drift needs the
    snapshots/ grid check_freeform_ink already requires a still per beat for,
    so it only runs in the full gate. BLOCKING, not advisory — an advisory
    pace gate would reproduce the exact failure this file exists to close:
    the boring cut passed everything advisory and shipped to the gate clean."""
    args = [sys.executable, str(Path(__file__).parent / "check_pace.py"), str(ws)]
    if not static:
        args.append("--stills")
    rc, out = run_tool(args)
    return {"pass": rc == 0, "output": out.strip()}


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
    static_mode = "--static" in argv
    sections, failed = {}, False

    html = (ws / "index.html").read_text()
    scenes = parse_scenes(html)
    scenes.sort(key=lambda s: s["start"])
    # Freeform (agent-native) lane detection: state is the folder — no scene
    # slot carries data-narration (the compiler's private protocol) and the
    # beat manifest exists. No flag to remember, nothing to mis-declare.
    # decisions/log.md 2026-07-30.
    freeform = (not any(s["narration"] is not None for s in scenes)
                and (ws / "audio_request.json").is_file())

    def static_skip(needs):
        """A voice/timing section deferred in --static mode: an informational
        pass, never a failure — the assets it grades don't exist yet."""
        return {"pass": True,
                "output": f"SKIPPED (static mode) — needs {needs}; "
                          f"runs in the full gate after narration synthesis"}

    def freeform_skip(why):
        """A template-lane section with no referent on the freeform lane: an
        informational pass that SAYS why, so a skipped rule is always visible
        and never silently lost (the §3 unowned-rules lesson)."""
        return {"pass": True, "output": f"SKIPPED (freeform lane) — {why}"}

    def template_skip(why):
        """A freeform-lane section with no referent on the template lane —
        the reverse of freeform_skip, same visibility discipline."""
        return {"pass": True, "output": f"SKIPPED (template lane) — {why}"}

    # 1. compiler check — freeform has no compiler; its timing contract
    # (every beat timed, timeline covers root, MIN_FINAL_HOLD kept) is graded
    # directly from the manifest.
    if freeform:
        sections["compile_check"] = check_freeform_timing(ws, html, static_mode)
        failed |= not sections["compile_check"]["pass"]
    elif static_mode:
        sections["compile_check"] = static_skip("word timestamps + narration audio")
    else:
        rc, out = run_tool([sys.executable, str(Path(__file__).parent / "compile_timeline.py"),
                            str(ws), "--check"])
        sections["compile_check"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 2. boundary rules (independent checker)
    if freeform and static_mode:
        # Plan stage: the clip wavs and their word timings do not exist yet.
        sections["boundaries"] = static_skip(
            "the per-clip wavs + audio_meta.json word timings")
    elif static_mode:
        sections["boundaries"] = static_skip("the transcript + narration.wav")
    else:
        rc, out = run_tool([sys.executable, str(CHECK_BOUNDARIES), str(ws)])
        sections["boundaries"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 2b. one template file per slot (2026-07-27). HyperFrames keys a
    # sub-composition's timeline and element ids to the FILE, so two slots
    # sharing one template collide: the surviving timeline animates one
    # instance and the others render blank headers. Invisible in Studio
    # preview (per-scene iframes) — composited render only.
    if freeform:
        sections["instance_templates"] = freeform_skip(
            "one-template-file-per-slot is compiler mechanics; a freeform "
            "build authors unique composition files by construction")
    else:
        rc, out = run_tool([sys.executable, str(Path(__file__).parent / "instance_templates.py"),
                            str(ws), "--check"])
        sections["instance_templates"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 2c. compositions/ freshness (2026-07-27, C2) — copied once at init,
    # never refreshed; catches a workspace silently building on a stale
    # pre-fix template.
    sections["composition_freshness"] = check_composition_freshness(ws)
    failed |= not sections["composition_freshness"]["pass"]

    # 3. coverage
    if static_mode:
        # Pre-TTS the scene starts/durations are placeholders, so tiling and
        # wav-vs-attr checks are meaningless — but the parsed scenes still
        # feed the static sections below (variables, title_card).
        sections["coverage"] = static_skip("compiled scene timings + narration.wav")
    else:
        problems = []
        if scenes:
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
    if freeform:
        sections["variables"] = freeform_skip(
            "theme/sceneDuration are compiler slot variables; brand truth is "
            "graded by the brand section below, monotony by the per-video "
            "human preview")
    else:
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

    # 5. script fidelity — the fabrication ban's render-stage half. Freeform:
    # the beat manifest (what was SENT to the engine) diffs against the
    # approved script, static and free. Template: approved script vs the
    # synthesized transcript.
    if freeform:
        sections["script_match"] = check_freeform_script_match(ws, script_override)
        failed |= not sections["script_match"]["pass"]
    elif static_mode:
        sections["script_match"] = static_skip(
            "the synthesized transcript (narration.words.json / transcript.json)")
    else:
        sections["script_match"] = check_script_match(ws, script_override)
        failed |= not sections["script_match"]["pass"]

    # 6. pacing — Motion v2 cue-gap budget + scene duration caps
    if freeform:
        sections["pacing"] = freeform_skip(
            "the cue-gap budget reads compiled cue variables; freeform "
            "reveals are word-timestamp-driven and pacing is owned by the "
            "per-video human preview")
    elif static_mode:
        sections["pacing"] = static_skip(
            "compiled cue times + real scene durations")
    else:
        sections["pacing"] = check_pacing(scenes)
        failed |= not sections["pacing"]["pass"]

    # 6b. pace — beat-pace / long-beat-share / carrier-drift (BUILD-PLAN B1,
    #     2026-08-04, check_pace.py). Freeform-only: the template lane's idea
    #     rate is bounded by its own scene-duration caps and cue-gap budget
    #     (the `pacing` section above), and monotony there is `check_variety`'s
    #     job. Calibrated on n=2 (one lesson, two cuts) — see check_pace.py's
    #     docstring for the stated limit before tightening these numbers.
    if freeform:
        sections["pace"] = check_freeform_pace(ws, static_mode)
        failed |= not sections["pace"]["pass"]
    else:
        sections["pace"] = template_skip(
            "idea rate is bounded by the template lane's own scene-duration "
            "caps and cue-gap budget (the pacing section above); monotony "
            "there is check_variety's job")

    # 7. text — minimum on-frame text size + no restatement of label/heading
    #    (owner calls 2026-07-27; tokens.yml typography.min-size + "Type rules").
    #    Static: reads the workspace's composition CSS and scene variables, so
    #    it costs nothing and catches unreadable/duplicate copy pre-render.
    rc, out = run_tool([sys.executable, str(Path(__file__).parent / "check_text.py"),
                        str(ws)])
    sections["text"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 7b. title card — eyebrow and title are DERIVED, never authored (design-contract.md
    #     "Title card & outro sources"). eyebrow must be the program's display
    #     name from tokens.yml's `programs:` map (run 2 of the 2026-07-28 stability loop
    #     invented a program name; run 1 used the pre-rebrand one — neither
    #     traceable); title must be the stem's title segment, de-kebabed.
    #     Freeform: same rule, graded on extracted on-frame markup text.
    if freeform:
        sections["title_card"] = check_freeform_title(ws, script_override)
    else:
        sections["title_card"] = check_title_card(ws, scenes, script_override)
    failed |= not sections["title_card"]["pass"]

    # 7c. brand — colors + typeface come from the machine-readable brand
    #     tokens, graded on the workspace's own CSS. Templates guarantee brand
    #     by construction, so this runs on the freeform lane only — the one
    #     lane where nothing else owns it (the gap the adoption brief missed:
    #     brand-truth.md would be prose, and prose is a request).
    if freeform:
        rc, out = run_tool([sys.executable,
                            str(Path(__file__).parent / "check_brand.py"),
                            str(ws)])
        sections["brand"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 8. slots — every template slot a scene doesn't use must be blanked with "".
    #    An omitted slot renders the template's PLACEHOLDER DEFAULT: plausible,
    #    on-brand copy the lesson script never said. No other gate catches it —
    #    check_text grades size and restatement, not provenance — and it is a
    #    fabrication-ban violation, so it fails hard. (Added 2026-07-28 after the
    #    AUTO-BATCH pilot shipped 15 placeholder lines across 6 scenes.)
    if freeform:
        sections["slots"] = freeform_skip(
            "the data-slot / placeholder-default protocol is the compiler's; "
            "the placeholder scan is rehomed in check_copy (runs below, over "
            "extracted on-frame markup text)")
    else:
        rc, out = run_tool([sys.executable, str(Path(__file__).parent / "check_slots.py"),
                            str(ws)])
        sections["slots"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 9. in-scene silence — no inter-word hole inside a scene may run past
    #    INSCENE_GAP_FAIL. Oxana pauses 0.98-1.26s mid-scene at sentence and
    #    clause boundaries, non-deterministically (identical syntax measured at
    #    0.48s and 1.14s), and the frame freezes with the audio because every
    #    cue is derived from these same word timestamps — the owner read it as
    #    "a major glitch or lag" (2026-07-28). synth_narration.compress_gaps()
    #    excises the excess at synthesis; this is the guard that keeps a future
    #    provider or voice change from silently reintroducing the class.
    if freeform:
        sections["inscene_gaps"] = freeform_skip(
            "needs per-word timestamps in the flat-words shape; the audio "
            "engine owns gap compression on this lane (adapter deferred with "
            "check_boundaries')")
    elif static_mode:
        sections["inscene_gaps"] = static_skip(
            "narration.words.json + scene-times.json")
    else:
        sections["inscene_gaps"] = check_inscene_gaps(ws)
        failed |= not sections["inscene_gaps"]["pass"]

    # 10. variety — the frame must not repeat itself. The Motion v2 variety rule
    #     (max 2 consecutive scenes per template, >=5 distinct forms) was decided
    #     2026-07-27 and left as prose in decisions/log.md; it reached neither
    #     frame.md nor the build skill. The next build put 21 scenes on 5
    #     templates — 8 of them scla-statement, an unbroken run of 5 lookalike
    #     slides, six templates untouched — and every gate here passed it. Owner
    #     verdict: "boring, doesn't have a lot of visual variety" (2026-07-28).
    #     Also fails a list slot holding exactly ONE item: that draws the
    #     bullet/pill illustration around a single fact ("you would never just
    #     render a single bullet point"), which 5 scenes of that build did.
    if freeform:
        # Template-FAMILY counting genuinely has no referent here (there are no
        # families), and monotony stays with check_diversity + the human
        # preview. But the two rules in this file that are about CONTENT FORM
        # rather than templates — one-item-list and one-card — do have a
        # referent, and they run: BUILD-PLAN step 1.3a rehomed them onto
        # element structure in check_forms.py. Leaving them to the preview
        # would be exactly the deferral the rules file forbids ("a measurement
        # is never delegated to the human preview").
        sections["variety"] = freeform_skip(
            "template-family counting has no referent here; monotony on this "
            "lane is owned by check_diversity + the per-video human preview "
            "(decisions/log.md 2026-07-30). The one-item-list / one-card rules "
            "are NOT skipped — see the `forms` section below")
        rc, out = run_tool([sys.executable,
                            str(Path(__file__).parent / "check_forms.py"),
                            str(ws)])
        sections["forms"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0
    else:
        rc, out = run_tool([sys.executable, str(Path(__file__).parent / "check_variety.py"),
                            str(ws)])
        sections["variety"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 11. copy — standing owner preferences about the words themselves, given
    #     repeatedly and enforced nowhere until 2026-07-28. Headings are Title
    #     Case with no terminal period (frame.md had said the OPPOSITE —
    #     "sentence case for titles and body" — so 0 of 17 headings in the
    #     reviewed build were Title Case and the pipeline was faithfully
    #     following a rule that contradicted the owner). Spoken lists of >=3
    #     items take "and"/"or" before the final item; that sat in frame.md as
    #     the soft word "prefer", carrying the very example the owner then
    #     complained about ("Mentorship? Growth?").
    rc, out = run_tool([sys.executable, str(Path(__file__).parent / "check_copy.py"),
                        str(ws)])
    sections["copy"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 11b. continuity — one thought per scene, no thought split across scenes.
    #      The 2026-07-28 build spread a seven-item list over three scenes in
    #      three different styles, gave a comma-joined clause ("But it should
    #      not make the decision for you.") its own 2.5s frame, and split a
    #      four-item list across two more. Every gate passed it. Fragmentation
    #      also DISABLED the conjunction rule: runs of 2/2/2 never reach the
    #      >=3 threshold check_copy grades, which is why "Mentorship? Growth?"
    #      shipped without its "or" from a gate written to catch exactly that.
    #      Runs static — it reads narration and durations, never audio.
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_continuity.py"),
                        str(ws)] + (["--static"] if static_mode else []))
    sections["continuity"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 11c. capacity — copy must fit the box the template gives it, measured in
    #      the real vendored font rather than estimated from a ratio. Two
    #      strings on the 2026-07-28 build could not fit their slots:
    #      "–5 possible paths" as a stat suffix beside a 300px numeral, and
    #      "Different learning opportunities" (507px of Proxima 900 at 34px) in
    #      a 240px card, which grew to three lines and pushed through the footer
    #      rule. Static and cheap, so a builder learns at plan stage.
    if freeform:
        # Slot capacity needs slots, and a freeform layout is designed around
        # its copy — so the per-slot maxLines budget genuinely cannot move.
        # The plan-stage QUESTION does move, and no longer counts as an
        # accepted loss (BUILD-PLAN step 1.3c): check_fit.py asks "does this
        # string fit the content area at the MINIMUM legal type size", still
        # measured in the real vendored font. ADVISORY per STD-38 — it is
        # deliberately not OR-ed into `failed`. The hard backstop is the ink
        # gate below, which grades real pixels and does block.
        sections["capacity"] = freeform_skip(
            "per-slot maxLines needs slots. The plan-stage fit question moved "
            "to the `fit` section below (check_fit.py); hard enforcement is "
            "the pixel ink gate")
        rc, out = run_tool([sys.executable,
                            str(Path(__file__).parent / "check_fit.py"),
                            str(ws)])
        sections["fit"] = {"pass": True, "output": out.strip()}
    else:
        rc, out = run_tool([sys.executable,
                            str(Path(__file__).parent / "check_capacity.py"),
                            str(ws)])
        sections["capacity"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 11cc. geometry — no text may land on other text, or below the frame. The
    #      2026-07-29 build printed "Grounded in what you value" straight
    #      through "Use it on any career decision" on scene-19, and every gate
    #      passed it: check_layout ran the real browser inspector at 60 sample
    #      points and returned zero findings (sibling-vs-sibling collision is
    #      not a case `hyperframes inspect` models), while check_capacity had
    #      never graded that slot at all because scla-loop binds its captions in
    #      a loop the bind regex could not see. boxmodel.py resolves every
    #      string to a frame box from the template CSS + real font metrics, so
    #      this is static and cheap and runs at plan stage too.
    if freeform:
        # boxmodel is CONFIDENTLY WRONG on freeform CSS — measured at 281
        # false findings on a build verified clean across 34 stills (HANDOFF
        # §2) — so it must not run here. Bounds come from real pixels
        # (check_ink over per-beat snapshots); text-on-text from the per-beat
        # layout inspector pass below.
        if static_mode:
            sections["geometry"] = static_skip(
                "browser snapshots of the built HTML (check_ink)")
        else:
            sections["geometry"] = check_freeform_ink(ws)
            failed |= not sections["geometry"]["pass"]
    else:
        rc, out = run_tool([sys.executable,
                            str(Path(__file__).parent / "check_geometry.py"),
                            str(ws)])
        sections["geometry"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 11c-bis. motion — settled content may not re-animate in place. The owner
    #      banned keep-alive motion 2026-07-14 and reaffirmed it 07-15; a
    #      session restored it the next day because check_presence fails a 5s
    #      pixel-static hold and a bob is a two-line fix while re-authoring the
    #      scene is not. Three MP4s shipped with it, one published. The motion
    #      is now deleted from the templates and this keeps it deleted — static,
    #      reads the workspace's own copied compositions, so it fires at plan
    #      stage alongside geometry.
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_motion.py"),
                        str(ws)])
    sections["motion"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 11d. layout — the inspector, run at EVERY scene and believed. `npm run
    #      check` samples 9 points across the whole runtime (one per ~16.6s on a
    #      25-scene lesson, so most scenes are never looked at) and treats
    #      `content_overlap` as severity "info", which the gate discarded. Both
    #      of the owner's layout complaints were visible to tooling we already
    #      ran. Needs a browser and ~2 minutes, so it is skipped in --static
    #      (plan-stage) mode and runs as a hard block before the render.
    if static_mode:
        sections["layout"] = static_skip("a rendered browser pass")
    else:
        rc, out = run_tool([sys.executable,
                            str(Path(__file__).parent / "check_layout.py"),
                            str(ws)])
        sections["layout"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 12. stem — a workspace is a WORKING artifact, so its name is the base
    #     `<title>_<program>` and carries no date. The name is therefore the
    #     identity, which is what makes `mkdir renders-hyperframes/<base>` the
    #     build lock for concurrent sessions. A dated workspace name defeats
    #     that lock silently: it is how one lesson came to hold both
    #     `..._2026-07-28` and `..._2026-07-29`. Dates survive only on the
    #     delivered MP4. render-qa/stem.py owns the rule (2026-07-29).
    stem_ok, stem_msg = (True, "")
    try:
        want = stem_base(ws.name)
    except StemError as exc:
        stem_ok, stem_msg, want = False, str(exc), None
    else:
        if not is_canonical(ws.name):
            stem_ok = False
            stem_msg = (f"it carries a date suffix; a build workspace is named "
                        f"for its base alone")
    sections["stem"] = {
        "pass": stem_ok,
        "output": (f"workspace name {ws.name!r} is not canonical: {stem_msg}"
                   + (f"\n  fix: mv {ws.name!r} {want!r}" if want else ""))
        if not stem_ok else f"{ws.name} — canonical"}
    failed |= not stem_ok

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
