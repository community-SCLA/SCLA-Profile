#!/usr/bin/env python3
"""One-command pre-render gate for SCLA HyperFrames lesson builds.

Runs every deterministic check that used to be spread across QA lanes and
ad-hoc scripts, in one pass, BEFORE the expensive render.

A build workspace is freeform (agent-native): the HTML is the authored
artifact, and the authoring contract is audio_request.json (the beats) +
timing.json (computed, never hand-tuned) + design.md + the composition itself.
The template lane — the scenes.json → index.html compiler and its slot-shaped
gates — was retired to render-qa/_archive/ on 2026-08-05 (decisions/log.md).

Sections:

  compile_check   — the timing contract: every beat has a computed timing row,
                    the timeline covers the root duration, and the ending
                    keeps the MIN_FINAL_HOLD floor
  boundaries      — check_boundaries.py per-clip adapter: air, mid-word cuts,
                    final hold, measured on the clip wavs themselves
  composition_freshness — the workspace's tokens.yml copy vs the spec (the
                    gates read the COPY); stale composition copies for any
                    workspace carrying a compositions/ dir
  coverage        — scene clips tile 0 → root exactly: first at 0, no gaps or
                    overlaps, last end == root duration, audio attr == true
                    wav duration (ffprobe)
  script_match    — the fabrication ban: the beat manifest (the exact text
                    sent to the TTS engine) diffs against the approved lesson
                    script, word-level; static and free, so it runs at plan
                    stage too
  pace            — check_pace.py: beat-pace / long-beat-share (timing.json,
                    runs in --static) + carrier-drift (snapshots/, full gate)
  text            — check_text.py: minimum on-frame text size (floors LOADED
                    from tokens.yml typography.min-size via tokens.py) and no
                    on-frame line restating its own scene's label or heading
  title_card      — program banner + lesson title present in on-frame MARKUP
                    text; display names from tokens.yml `programs:`
  brand           — check_brand.py: colors + typeface from the machine-readable
                    brand tokens, graded on the workspace's own CSS
  inscene_gaps    — no mid-scene silence past INSCENE_GAP_FAIL. The rule is
                    live and lane-neutral; its flat-words adapter for per-beat
                    audio is deferred, so an absent narration.words.json WARNs
                    and skips — visibly, never silently
  forms           — check_forms.py: one-item-list / one-card graded on element
                    structure
  copy            — check_copy.py: standing owner preferences about the words
  continuity      — check_continuity.py: one thought per scene
  fit             — check_fit.py: does each string fit the content area at the
                    minimum legal type size (ADVISORY per STD-38; the pixel
                    ink gate is the hard backstop)
  geometry        — check_ink.py over one snapshot still per beat — bounds
                    from real pixels; full gate only
  motion          — check_motion.py: settled content never re-animates
  layout          — check_layout.py: the browser inspector pass; full gate only
  stem            — the workspace name is the undated base

Exit 0 = cleared for render. Exit 1 = fix and re-run. This is the gate that
lets the QA gauntlet's agent lanes shrink to judgment-only work.

--static (2026-07-28): run ONLY the sections that are meaningful on a
workspace with NO voice assets — the plan stage, before any TTS has run.
Sections that need audio/timing/snapshots (boundaries, coverage, geometry,
layout, inscene_gaps, carrier-drift) are SKIPPED with a "(static mode)" note,
never failed. Same exit semantics: 0 = the plan is clean, 1 = fix the plan.

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
from hfp_common import (ffprobe_duration, load_beats, norm_token,
                        onframe_strings, parse_scenes)
from stem import StemError, base as stem_base, is_canonical

CHECK_BOUNDARIES = Path(__file__).resolve().parent / "check_boundaries.py"
TOL = 0.002

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
                f"WARN no-word-timings: {HEYGEN_WORDS_FILE} missing — the "
                f"flat-words adapter for per-beat clip audio is deferred, so "
                f"the in-scene silence rule (no >{max_gap}s mid-scene hole) "
                f"is NOT graded on this build"}
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


def check_composition_freshness(ws: Path):
    """Workspace compositions/ vs the design-system source (C2, 2026-07-27).

    compositions/ is copied into each workspace once at init and never
    refreshed — a design-system template fix (like the B1 icon-flash fix)
    lands silently invisible in every workspace already on disk. This
    compares each non-instanced composition file's <style>/<script> content
    against design-system/compositions/<same name>.html. Instanced clones
    (basename__suffix.html, from the retired template compiler or a hand-namespaced
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
    # retargeted to config/tokens.yml when the spec was split.)
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
# The freeform (agent-native) authoring contract — the pipeline's only lane
# since 2026-08-05 (decisions/log.md; introduced 2026-07-30). A workspace has
# no scenes.json, no compiler and no template slots; its contract is
# audio_request.json (the beats) + timing.json (computed, never hand-tuned) +
# design.md + the composition HTML itself.
# ---------------------------------------------------------------------------

def check_timing(ws: Path, html: str, static=False):
    """The timing contract: every beat has a computed timing row, the timeline
    covers the root duration, and the ending keeps the MIN_FINAL_HOLD floor
    the owner has rejected twice. check_boundaries grades the wav-level form
    of that floor on the per-clip wavs; this grades the timing-level form."""
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


def check_script_match(ws: Path, script_override=None,
                       scripts_root=LESSON_SCRIPTS):
    """The fabrication ban, freeform form: the BEAT MANIFEST — the exact text
    sent to the TTS engine — diffs against the approved script. Static and
    free, so it runs at plan stage too. (The spoken-audio half, whisper vs
    wav, needs the flat-words adapter and is deferred; what was SENT is graded
    here, and the engine's own word timestamps are what drive the reveals.)
    A missing approved script is a HARD FAILURE (2026-07-29): the one gate
    standing between a build and fabricated on-screen content must never
    disarm itself precisely when it cannot verify anything — 'I could not
    check' is never 'it is fine'. The escape hatch stays explicit: pass
    --script <path>. Silence is not an escape hatch."""
    script_path = script_override or locate_script(ws, scripts_root)
    if script_path is None:
        return {"pass": False, "output":
                f"FAIL: no approved script found for stem {ws.name!r} under "
                f"{scripts_root} and no --script given. The script-vs-beats "
                f"diff is the render-stage half of the fabrication ban — it "
                f"cannot be skipped silently."}
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
    if rate > RATE_WARN:
        lines.append(f"WARN: mismatch rate {rate:.2%} is above the "
                     f"TTS-normalization noise floor (~{RATE_WARN:.1%}) — "
                     f"eyeball the diffs above before rendering")
    return {"pass": True, "output": "\n".join(lines)}


def check_title(ws: Path, script_override=None):
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


def check_ink(ws: Path):
    """The freeform geometry gate: check_ink.py over one snapshot still per
    beat. The retired static CSS box model cannot grade freeform CSS — measured
    at 281 false findings on a build verified clean across 34 stills — so
    bounds come from real pixels, and text-on-text comes from check_layout's
    per-beat inspector pass. Missing or thin snapshots FAIL: nothing-graded is never a pass."""
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


def check_pace(ws: Path, static: bool):
    """BUILD-PLAN B1 (2026-08-04): the owner approved one freeform cut of a
    lesson and rejected another, and every rule in this file passed the
    rejected cut while QUARANTINING the approved one — the gate set measured
    animacy, and the owner was responding to idea rate and a carrying object
    (see check_pace.py's module docstring for the full story and its stated
    n=2 calibration limit). The two timing rules (beat-pace, long-beat-share)
    read timing.json alone, so they run in --static; carrier-drift needs the
    snapshots/ grid check_ink already requires a still per beat for,
    so it only runs in the full gate. BLOCKING, not advisory — an advisory
    pace gate would reproduce the exact failure this file exists to close:
    the boring cut passed everything advisory and shipped to the gate clean."""
    args = [sys.executable, str(Path(__file__).parent / "check_pace.py"), str(ws)]
    if not static:
        args.append("--stills")
    rc, out = run_tool(args)
    return {"pass": rc == 0, "output": out.strip()}


def check_audio_contract(ws: Path, static: bool):
    """The request and provider receipt must match the pinned production voice."""
    problems, notes = [], []
    declared = tokens.load(ws).get("voice") or {}
    expected_request = {
        "provider": declared.get("provider"),
        "voice": declared.get("voice_id"),
        "speed": float(declared.get("speed", 1.0)),
    }
    try:
        request = json.loads((ws / "audio_request.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"pass": False, "output": f"audio_request.json unreadable: {exc}"}
    for key, wanted in expected_request.items():
        actual = request.get(key)
        if key == "speed" and actual is not None:
            actual = float(actual)
        if actual != wanted:
            problems.append(f"request {key}={actual!r}; production requires {wanted!r}")

    if static:
        notes.append("provider receipt deferred until synthesis")
    else:
        try:
            meta = json.loads((ws / "audio_meta.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"pass": False, "output": f"audio_meta.json unreadable: {exc}"}
        receipt = {"provider": meta.get("tts_provider"),
                   "voice": meta.get("voice_id"), "speed": meta.get("speed")}
        for key, wanted in expected_request.items():
            actual = receipt[key]
            if key == "speed" and actual is None and not (ws / ".scla-control-v2").exists():
                notes.append("legacy metadata has no speed receipt")
                continue
            if key == "speed" and actual is not None:
                actual = float(actual)
            if actual != wanted:
                problems.append(f"metadata {key}={actual!r}; production requires {wanted!r}")
        voices = meta.get("voices")
        if not isinstance(voices, list) or not voices:
            problems.append("audio metadata declares no voice clips")
        else:
            for voice in voices:
                rel = voice.get("path") if isinstance(voice, dict) else None
                if not rel or not (ws / rel).is_file():
                    problems.append(f"declared audio clip is missing: {rel!r}")
    output = "\n".join(problems + [f"note: {x}" for x in notes]) or "ok"
    return {"pass": not problems, "output": output}


def check_workspace_sources(ws: Path):
    """Mechanical generators are shared infrastructure, not build artifacts."""
    if not (ws / ".scla-control-v2").exists():
        return {"pass": True, "output": "legacy workspace; v2 source policy not applied"}
    forbidden = sorted(path.name for path in ws.glob("make_*.py") if path.is_file())
    if forbidden:
        return {"pass": False,
                "output": "workspace generators are forbidden: " + ", ".join(forbidden)}
    return {"pass": True, "output": "ok"}


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

    def static_skip(needs):
        """A voice/timing section deferred in --static mode: an informational
        pass, never a failure — the assets it grades don't exist yet."""
        return {"pass": True,
                "output": f"SKIPPED (static mode) — needs {needs}; "
                          f"runs in the full gate after narration synthesis"}

    # 1. the timing contract — every beat timed, the timeline covers the root
    #    duration, MIN_FINAL_HOLD kept. (This section used to invoke the
    #    scenes.json compiler's --check; the compiler retired with the
    #    template lane, 2026-08-05.)
    sections["compile_check"] = check_timing(ws, html, static_mode)
    failed |= not sections["compile_check"]["pass"]

    # 2. boundary rules (independent checker) — air, mid-word cuts, final
    #    hold, graded on the per-clip wavs via check_boundaries' adapter.
    if static_mode:
        sections["boundaries"] = static_skip(
            "the per-clip wavs + audio_meta.json word timings")
    else:
        rc, out = run_tool([sys.executable, str(CHECK_BOUNDARIES), str(ws)])
        sections["boundaries"] = {"pass": rc == 0, "output": out.strip()}
        failed |= rc != 0

    # 2c. freshness (2026-07-27, C2) — the gates read the WORKSPACE's copied
    #     tokens.yml, so its drift from the spec hard-fails; composition
    #     copies are graded for any workspace that carries them.
    sections["composition_freshness"] = check_composition_freshness(ws)
    failed |= not sections["composition_freshness"]["pass"]

    # Production request + provider receipt. This catches voice drift before an
    # expensive render and verifies arbitrary clip ids through the manifest.
    sections["audio_contract"] = check_audio_contract(ws, static_mode)
    failed |= not sections["audio_contract"]["pass"]

    # New workspaces author the composition directly. Mechanical timing/audio
    # work belongs to tracked shared utilities, never bespoke make_*.py files.
    sections["workspace_sources"] = check_workspace_sources(ws)
    failed |= not sections["workspace_sources"]["pass"]

    # 3. coverage
    if static_mode:
        # Pre-TTS the scene starts/durations are placeholders, so tiling and
        # wav-vs-attr checks are meaningless — but the parsed scenes still
        # feed the static sections below.
        sections["coverage"] = static_skip("computed clip timings")
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

    # 5. script fidelity — the fabrication ban's render-stage half: the beat
    #    manifest (the exact text SENT to the engine) diffs against the
    #    approved script. Static and free, so it runs at plan stage too.
    sections["script_match"] = check_script_match(ws, script_override)
    failed |= not sections["script_match"]["pass"]

    # 6b. pace — beat-pace / long-beat-share / carrier-drift (BUILD-PLAN B1,
    #     2026-08-04, check_pace.py). Calibrated on n=2 (one lesson, two
    #     cuts) — see check_pace.py's docstring for the stated limit before
    #     tightening these numbers.
    sections["pace"] = check_pace(ws, static_mode)
    failed |= not sections["pace"]["pass"]

    # 7. text — minimum on-frame text size + no restatement of label/heading
    #    (owner calls 2026-07-27; floors LOADED from tokens.yml typography.min-size).
    #    Static: reads the workspace's composition CSS and scene variables, so
    #    it costs nothing and catches unreadable/duplicate copy pre-render.
    rc, out = run_tool([sys.executable, str(Path(__file__).parent / "check_text.py"),
                        str(ws)])
    sections["text"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 7b. title card — eyebrow and title are DERIVED, never authored (rule
    #     stated in .claude/rules/video-production.md "The banner is the
    #     program folder's name"). The program's display name comes from
    #     tokens.yml's `programs:` map; graded on extracted on-frame markup.
    sections["title_card"] = check_title(ws, script_override)
    failed |= not sections["title_card"]["pass"]

    # 7c. brand — colors + typeface come from the machine-readable brand
    #     tokens, graded on the workspace's own CSS. Nothing else owns brand
    #     truth here (the gap the adoption brief missed: brand-truth.md would
    #     be prose, and prose is a request).
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_brand.py"),
                        str(ws)])
    sections["brand"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 9. in-scene silence — no inter-word hole inside a scene may run past
    #    INSCENE_GAP_FAIL (the owner read one as "a major glitch or lag",
    #    2026-07-28). The rule is live and lane-neutral; check_inscene_gaps
    #    WARNs and skips, visibly, when no flat narration.words.json exists
    #    (the per-beat clip-audio adapter is deferred).
    if static_mode:
        sections["inscene_gaps"] = static_skip(
            "narration.words.json + scene-times.json")
    else:
        sections["inscene_gaps"] = check_inscene_gaps(ws)
        failed |= not sections["inscene_gaps"]["pass"]

    # 10. forms — one-item-list / one-card, graded on ELEMENT STRUCTURE
    #     (check_forms.py; rehomed from the retired template-family checker,
    #     BUILD-PLAN step 1.3a). Leaving these to the preview would be exactly
    #     the deferral the rules file forbids ("a measurement is never
    #     delegated to the human preview").
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_forms.py"),
                        str(ws)])
    sections["forms"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 11. copy — standing owner preferences about the words themselves, given
    #     repeatedly and enforced nowhere until 2026-07-28: Title Case
    #     headings with no terminal period, "and"/"or" before the final item
    #     of a spoken list, the placeholder scan, unspoken-symbol.
    rc, out = run_tool([sys.executable, str(Path(__file__).parent / "check_copy.py"),
                        str(ws)])
    sections["copy"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 11b. continuity — one thought per scene, no thought split across scenes.
    #      Runs static — it reads narration and durations, never audio.
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_continuity.py"),
                        str(ws)] + (["--static"] if static_mode else []))
    sections["continuity"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 11c. fit — does each string fit the CONTENT AREA at the minimum legal
    #      type size, measured in the real vendored font (check_fit.py).
    #      ADVISORY per STD-38 — deliberately not OR-ed into `failed`; the
    #      hard backstop is the pixel ink gate below, which does block.
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_fit.py"),
                        str(ws)])
    sections["fit"] = {"pass": True, "output": out.strip()}

    # 11cc. geometry — bounds from REAL PIXELS: check_ink.py over one snapshot
    #      still per beat. (The static CSS box model was measured CONFIDENTLY
    #      WRONG on freeform CSS — 281 false findings on a build verified
    #      clean across 34 stills — and retired with the template lane.)
    #      Text-on-text is the layout inspector pass below.
    if static_mode:
        sections["geometry"] = static_skip(
            "browser snapshots of the built HTML (check_ink)")
    else:
        sections["geometry"] = check_ink(ws)
        failed |= not sections["geometry"]["pass"]

    # 11c-bis. motion — settled content may not re-animate in place. The owner
    #      banned keep-alive motion 2026-07-14 and reaffirmed it 07-15; three
    #      MP4s shipped with it, one published. Static — reads the workspace's
    #      own composition files, so it fires at plan stage alongside fit.
    rc, out = run_tool([sys.executable,
                        str(Path(__file__).parent / "check_motion.py"),
                        str(ws)])
    sections["motion"] = {"pass": rc == 0, "output": out.strip()}
    failed |= rc != 0

    # 11d. layout — the inspector, run at EVERY scene and believed. Needs a
    #      browser and ~2 minutes, so it is skipped in --static (plan-stage)
    #      mode and runs as a hard block before the render.
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
