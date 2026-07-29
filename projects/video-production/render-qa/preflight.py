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
  6. pacing                        — Motion v2 (frame.md "Pacing budget",
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
                                     (floors LOADED from frame.md
                                     typography.min-size via tokens.py; body
                                     rose 32 -> 40px on 2026-07-29 because the
                                     floor had been set AT the smallest size in
                                     use, so it could never fire; frame.md
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

DESIGN_SYSTEM_COMPOSITIONS = Path(__file__).resolve().parents[1] / "design-system" / "compositions"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import ffprobe_duration, get_attr, norm_token, parse_scenes
from stem import StemError, base as stem_base, is_canonical

CHECK_BOUNDARIES = Path(__file__).resolve().parent / "check_boundaries.py"
TOL = 0.002

# pacing gate (Motion v2, 2026-07-27 — normative numbers in frame.md
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
    rendered/ covers re-verification of a shipped lesson.

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
    for program in sorted(p for p in scripts_root.iterdir() if p.is_dir()):
        for sub in ("refined", "", "rendered"):
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
    program's on-screen display name from frame.md's 'Title card & outro
    sources' table, and the title must be the stem's title segment de-kebabed
    (case-insensitive). Both were builder-invented before 2026-07-28."""
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
    program = script.parent.parent.name if script.parent.name in (
        "refined", "rendered") else script.parent.name

    # Display-name table from the workspace's frame.md copy.
    display = {}
    frame = ws / "frame.md"
    if frame.is_file():
        in_table = False
        for ln in frame.read_text(encoding="utf-8", errors="replace").splitlines():
            if ln.startswith("| Program slug"):
                in_table = True
                continue
            if in_table:
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                if len(cells) == 2 and cells[0] and not cells[0].startswith("-"):
                    display[cells[0]] = cells[1]
                elif not ln.strip().startswith("|"):
                    break
    if not display:
        return {"pass": False,
                "output": "frame.md has no 'Program slug' display-name table "
                          "(is the workspace scaffold stale?)"}

    vars_ = title_scene["variables"]
    want_eyebrow = display.get(program)
    got_eyebrow = str(vars_.get("eyebrow", "")).strip()
    if want_eyebrow is None:
        problems.append(f"program '{program}' missing from frame.md's "
                        f"display-name table — add it there, never on the fly")
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
    return {"pass": not stale, "output": "\n".join(lines)}


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
    static_mode = "--static" in argv
    sections, failed = {}, False

    def static_skip(needs):
        """A voice/timing section deferred in --static mode: an informational
        pass, never a failure — the assets it grades don't exist yet."""
        return {"pass": True,
                "output": f"SKIPPED (static mode) — needs {needs}; "
                          f"runs in the full gate after narration synthesis"}

    # 1. compiler check
    if static_mode:
        sections["compile_check"] = static_skip("word timestamps + narration audio")
    else:
        rc, out = run_tool([sys.executable, str(Path(__file__).parent / "compile_timeline.py"),
                            str(ws), "--check"])
        sections["compile_check"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 2. boundary rules (independent checker)
    if static_mode:
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
    html = (ws / "index.html").read_text()
    scenes = parse_scenes(html)
    scenes.sort(key=lambda s: s["start"])
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
    if static_mode:
        sections["script_match"] = static_skip(
            "the synthesized transcript (narration.words.json / transcript.json)")
    else:
        sections["script_match"] = check_script_match(ws, script_override)
        failed |= not sections["script_match"]["pass"]

    # 6. pacing — Motion v2 cue-gap budget + scene duration caps
    if static_mode:
        sections["pacing"] = static_skip(
            "compiled cue times + real scene durations")
    else:
        sections["pacing"] = check_pacing(scenes)
        failed |= not sections["pacing"]["pass"]

    # 7. text — minimum on-frame text size + no restatement of label/heading
    #    (owner calls 2026-07-27; frame.md typography.min-size + "Type rules").
    #    Static: reads the workspace's composition CSS and scene variables, so
    #    it costs nothing and catches unreadable/duplicate copy pre-render.
    rc, out = run_tool([sys.executable, str(Path(__file__).parent / "check_text.py"),
                        str(ws)])
    sections["text"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 7b. title card — eyebrow and title are DERIVED, never authored (frame.md
    #     "Title card & outro sources"). eyebrow must be the program's display
    #     name from frame.md's table (run 2 of the 2026-07-28 stability loop
    #     invented a program name; run 1 used the pre-rebrand one — neither
    #     traceable); title must be the stem's title segment, de-kebabed.
    sections["title_card"] = check_title_card(ws, scenes, script_override)
    failed |= not sections["title_card"]["pass"]

    # 8. slots — every template slot a scene doesn't use must be blanked with "".
    #    An omitted slot renders the template's PLACEHOLDER DEFAULT: plausible,
    #    on-brand copy the lesson script never said. No other gate catches it —
    #    check_text grades size and restatement, not provenance — and it is a
    #    fabrication-ban violation, so it fails hard. (Added 2026-07-28 after the
    #    AUTO-BATCH pilot shipped 15 placeholder lines across 6 scenes.)
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
    if static_mode:
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
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_geometry.py"),
                        str(ws)])
    sections["geometry"] = {"pass": rc == 0, "output": out.strip()}
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

    # 12. stem — the workspace name must be canonical: <title>_<program>_<DATE>
    #     with exactly ONE date, meaning the date of the most recent action on
    #     this artifact (here, the build). The owner reviewed a video still
    #     named for its 2026-07-06 refine date after a 2026-07-28 render, with
    #     the HyperFrames CLI's own _<date>_<clock> stacked on top of that.
    #     render-qa/stem.py owns the rule (2026-07-28).
    stem_ok, stem_msg = (True, "")
    if not is_canonical(ws.name):
        try:
            stem_base(ws.name)
        except StemError as exc:
            stem_ok, stem_msg = False, str(exc)
    sections["stem"] = {
        "pass": stem_ok,
        "output": (f"workspace name {ws.name!r} is not a canonical stem: "
                   f"{stem_msg}\n  fix: python3 render-qa/stem.py normalize "
                   f"{ws.name!r} --date <build-date>, then rename the directory")
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
