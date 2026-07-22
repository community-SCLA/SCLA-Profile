#!/usr/bin/env python3
"""Timeline compiler for SCLA HyperFrames lesson builds.

THE INVERSION THIS TOOL EXISTS FOR: scene boundaries and reveal cues are never
hand-typed again. The author declares WHAT anchors each scene and cue (verbatim
phrases from the narration transcript); this compiler computes every number —
scene data-start/data-duration, silence padding in the narration, cue times,
audio and root durations — from assets/voice/transcript.json. Every timing
defect in the 2026-07-09/10 sessions (26 boundary violations, mid-word cuts,
the backfired transcript "repair", 7.65s of emergency padding, 14 cue-phrase
mismatches) traces to hand-authored numbers reconciled after the fact.

TWO MODES (2026-07-14, per-scene synthesis — see decisions/log.md):
  - PER-SCENE (assets/voice/scene-times.json present, written by
    synth_narration.py): boundaries are sample-exact from the manifest; no
    data-anchor-end needed; NO silence is ever inserted into the wav. This is
    the default for new builds — the insert_silences path measurably spliced
    words in half (Whisper timestamps are ±30-100ms; Kokoro's natural gaps are
    ~0.03s) and left orphaned silences behind when anchors moved after --apply.
  - LEGACY (no manifest): everything below, kept for workspaces built on the
    single-take flow.

Authoring contract (in index.html):
  - every scene slot carries  data-narration="<verbatim script span>"
    (per-scene mode) OR  data-anchor-end="<last spoken phrase of the scene>"
    (legacy; verbatim words from transcript.json; punctuation/case ignored)
  - scenes with reveal cues carry  data-cue-anchors='{"chipCues":["phrase",...],
    "pointCues":[...], "stepCues":[...], "mapCue":"phrase"}'
  - hand-written data-start / data-duration / numeric cues are placeholders;
    this tool owns them.

What --apply does (idempotent — a second run is a no-op):
  1. Resolve each scene's end anchor in the transcript (forward pointer,
     duplicate-safe: matching is positional, never global text search).
  2. Compute required air after the scene's last word: 0.3s (0.2 rule + 0.1
     margin), 0.45s after a question, plus a 0.15s lead before the next scene's
     first word. Natural narration gaps are 30-60ms (measured 2026-07-10), so
     the compiler inserts precision silence into narration.wav at each short
     boundary and shifts transcript.json — padding is part of the build, not
     an emergency repair. Each inserted silence is fenced by an 8ms fade so the
     splice can't step from voiced audio to digital zero (the boundary click
     class, measured 2026-07-14 at up to 25% FS — see decisions/log.md).
  3. Set every scene's data-start/data-duration on the computed boundaries;
     surplus silence is split between air-after and lead-before (capped).
  4. Resolve every cue anchor inside its scene's word window and write local-
     second cue values (and sceneDuration) into data-variable-values.
  5. Set the <audio> data-duration to the true (padded) wav length and the
     root data-duration to the final scene end
     (= max(audio_end + 0.05, last_word_end + 1.1) — the video outlives the
     narration, never the reverse).

--check recomputes everything and diffs against what index.html currently
says (exit 1 on drift) — the deterministic replacement for the QA lanes'
cue-drift and boundary hunting.

Usage:
    compile_timeline.py <workspace> --check [--json]
    compile_timeline.py <workspace> --apply [--json]
"""

import json
import re
import shutil
import sys
import wave
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import (MatchError, ffprobe_duration, find_phrase, get_attr,
                        json_attr, load_transcript, parse_scenes, set_attr)

AIR = 0.3            # after a normal sentence end (0.2 hard rule + 0.1 margin)
AIR_QUESTION = 0.45  # after a question (0.35 hard rule + 0.1 margin)
LEAD = 0.15          # silence before the next scene's first word
FINAL_HOLD = 1.1     # final scene holds past the last word (1.0 rule + 0.1)
AUDIO_TAIL = 0.05    # root must outlive the audio by at least this
MAX_EXTRA_AIR = 0.9  # cap on surplus silence assigned to air-after
DECLICK = 0.008      # fade (s) into/out of each inserted silence — kills the
                     # voiced-audio-to-zero splice click at scene boundaries
CUE_KEYS = ("pointCues", "stepCues", "chipCues", "mapCue", "subCues")
# cue key -> (list variable it must match 1:1, separator of that variable)
LIST_PAIRS = {"chipCues": ("chips", ","), "subCues": ("subBeats", "|")}

# TODO(heygen-swap): the illustrated pipeline is moving its TTS from local Kokoro
#   to HeyGen starfish (see design-system/frame.md voice: + decisions/log.md
#   2026-07-22). HeyGen returns NATIVE per-word timestamps from
#   .claude/skills/hyperframes-media/scripts/heygen-tts.mjs (--words →
#   assets/voice/narration.words.json, flat [{id,text,start,end}]), so the
#   separate Whisper `npx hyperframes transcribe` pass is DROPPED. The words file
#   is the same flat shape load_transcript() already consumes (text/start/end;
#   the extra `id` is ignored). Default stays Whisper until the diff session:
#   flip USE_HEYGEN_WORDS to True AND repoint synth_narration.py at the HeyGen
#   provider. CAVEAT (not a pure flag flip): in per-scene mode synth_narration.py
#   concatenates per-clip audio with inserted boundary silence, so per-clip
#   HeyGen timestamps must be shifted by each clip's placement in the concat
#   (scene-times.json manifest) to become the whole-file absolute times that
#   Whisper produces today. See the consumption branch in compute() and the
#   diff-session note in decisions/log.md 2026-07-22.
USE_HEYGEN_WORDS = False  # TODO(heygen-swap): flip to True once the voice is pinned
HEYGEN_WORDS_FILE = "narration.words.json"  # heygen-tts.mjs --words output


def _fade_edges(seg, chan, fade, fade_in, fade_out):
    """Ramp the head (fade_in) and/or tail (fade_out) of an int16 frame array to
    ~0 over `fade` frames, so it meets an adjacent silence with no step. Caps the
    ramp at half the segment when both ends fade, so a short scene between two
    silences never double-scales its middle."""
    n = len(seg) // chan
    if n == 0 or fade <= 0:
        return
    f = min(fade, n // 2 if (fade_in and fade_out) else n)
    if f <= 0:
        return
    if fade_in:
        for p in range(f):
            g = (p + 1) / (f + 1)  # ~0 at the silence edge -> 1 into the audio
            base = p * chan
            for c in range(chan):
                seg[base + c] = int(seg[base + c] * g)
    if fade_out:
        for p in range(f):
            g = (f - p) / (f + 1)  # 1 in the audio -> ~0 at the silence edge
            base = (n - f + p) * chan
            for c in range(chan):
                seg[base + c] = int(seg[base + c] * g)


def insert_silences(wav_path: Path, transcript_path: Path, insertions):
    """Insert silence into the wav at the given (word_idx, time, seconds) points
    and shift transcript timestamps. Shift is keyed by word index, not time
    value: at a zero-natural-gap boundary the last word of one scene and the
    first word of the next can share the exact same timestamp, and a
    time-keyed shift would move both together, leaving the gap at 0 forever
    (see snag-log 2026-07-12, "padding did not converge"). Indexing by word
    guarantees only words at/after the cut shift.

    Each splice is fenced by a DECLICK fade: the tail of the audio before the
    silence ramps to ~0 and the head of the audio after it ramps up from ~0, so
    the wav never steps from voiced samples straight to digital zero. Without
    this, boundary cuts landing mid-decay produced audible pops up to 25% FS
    (measured 2026-07-14). Backs up originals once (.pre-pad.wav/.json)."""
    for suffix, p in (("wav", wav_path), ("json", transcript_path)):
        bak = p.with_name(p.stem + ".pre-pad." + suffix)
        if not bak.exists():
            shutil.copy2(p, bak)

    with wave.open(str(wav_path), "rb") as r:
        params = r.getparams()
        frames = r.readframes(r.getnframes())
    rate, width, chan = params.framerate, params.sampwidth, params.nchannels
    bpf = width * chan
    can_fade = width == 2  # int16 PCM — the only format the pipeline's TTS emits
    fade = int(round(DECLICK * rate)) if can_fade else 0

    samples = array("h") if can_fade else None
    if can_fade:
        samples.frombytes(frames)

    out = array("h") if can_fade else bytearray()
    pos, shift, prev_sil = 0, 0.0, False  # pos in frames
    words = json.loads(transcript_path.read_text())
    shifts = []  # (first_shifted_word_idx, cumulative_shift_after)
    for word_idx, t, dur in sorted(insertions, key=lambda ins: ins[1]):
        cut_f = int(round(t * rate))
        sil_f = int(round(dur * rate))
        if can_fade:
            seg = samples[pos * chan:cut_f * chan]
            _fade_edges(seg, chan, fade, fade_in=prev_sil, fade_out=True)
            out += seg
            out += array("h", bytes(sil_f * bpf))
        else:
            out += frames[pos * bpf:cut_f * bpf]
            out += b"\x00" * (sil_f * bpf)
        pos = cut_f
        shift += dur
        shifts.append((word_idx, shift))
        prev_sil = True
    if can_fade:
        tail = samples[pos * chan:]
        _fade_edges(tail, chan, fade, fade_in=prev_sil, fade_out=False)
        out += tail
        data = out.tobytes()
    else:
        out += frames[pos * bpf:]
        data = bytes(out)

    with wave.open(str(wav_path), "wb") as w:
        w.setparams(params)
        w.writeframes(data)

    def shift_for(idx):
        s = 0.0
        for boundary_idx, cum in shifts:
            if idx >= boundary_idx:
                s = cum
        return s

    for i, w_ in enumerate(words):
        s = shift_for(i)
        w_["start"], w_["end"] = round(w_["start"] + s, 3), round(w_["end"] + s, 3)
    transcript_path.write_text(json.dumps(words, indent=2))
    return len(data) // bpf / rate


def load_manifest(ws: Path):
    """Per-scene synthesis manifest (synth_narration.py). None = legacy
    single-take flow (anchor-derived boundaries + silence insertion)."""
    p = ws / "assets" / "voice" / "scene-times.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text())


def compute(ws: Path):
    """Resolve timing -> full plan. Returns (plan, problems).

    Two modes:
      - PER-SCENE (scene-times.json present): boundaries are sample-exact from
        the synthesis manifest; scene word windows are cut by TIME; no
        data-anchor-end needed and no silence is ever inserted. Whisper serves
        only cue anchors + the preflight script gate.
      - LEGACY (no manifest): boundaries anchored by data-anchor-end phrases,
        short gaps padded by insert_silences. Kept for workspaces built on the
        single-take flow."""
    index_path = ws / "index.html"
    html = index_path.read_text()
    # TODO(heygen-swap): word timings are Whisper today; HeyGen supplies them
    #   natively (no transcribe pass). Same flat text/start/end shape either way,
    #   so this is the only consumption site that changes here. Default path
    #   (flag off) is unchanged — see USE_HEYGEN_WORDS note at top of file.
    voice_dir = ws / "assets" / "voice"
    if USE_HEYGEN_WORDS:
        words = load_transcript(voice_dir / HEYGEN_WORDS_FILE)
    else:
        words = load_transcript(voice_dir / "transcript.json")
    scenes = parse_scenes(html)
    problems = []

    if not scenes:
        return None, ["no scene slots found in index.html"]

    manifest = load_manifest(ws)
    if manifest is not None:
        ms = manifest["scenes"]
        if len(ms) != len(scenes):
            return None, [f"scene-times.json has {len(ms)} scenes but "
                          f"index.html has {len(scenes)} — re-run "
                          f"synth_narration.py after editing scene slots"]
        # Word windows are cut at the NEXT scene's manifest audio start, not at
        # the visual cut: whisper can drift a boundary word's start into the
        # silence gap (measured +0.33s, 2026-07-14), and the manifest knows
        # exactly where the next scene's audio begins.
        prev_edge = 0.0
        for i_sc, (sc, m) in enumerate(zip(scenes, ms)):
            edge = ms[i_sc + 1]["start"] if i_sc + 1 < len(ms) else None
            lo = next((i for i, w in enumerate(words)
                       if w["start"] >= prev_edge - 1e-9), None)
            hi = len(words) if edge is None else next(
                (i for i, w in enumerate(words)
                 if w["start"] >= edge - 1e-9), len(words))
            if lo is None or hi <= lo:
                problems.append(f"{sc['id']}: no transcript words inside its "
                                f"manifest window [{prev_edge}..{edge}] — "
                                f"stale transcript? re-run transcribe after "
                                f"synth_narration.py")
                return None, problems
            sc["first_word_idx"], sc["last_word_idx"] = lo, hi - 1
            sc["end_word"] = words[hi - 1]
            sc["air"] = m.get("air", AIR)
            sc["manifest_cut"] = m["cut"]
            prev_edge = edge if edge is not None else m["cut"]
        return {"scenes": scenes, "words": words, "insertions": [],
                "manifest": manifest, "html": html,
                "index_path": index_path}, problems

    missing = [s["id"] for s in scenes if not s["anchor_end"]]
    if missing:
        return None, [f"scenes missing data-anchor-end: {', '.join(missing)} "
                      f"— the compiler owns timing only when every scene is anchored"]

    # Pass 1: anchor every scene end, forward pointer (duplicate-safe).
    ptr = 0
    for sc in scenes:
        try:
            first, last = find_phrase(words, sc["anchor_end"], ptr, label=sc["id"])
        except MatchError as e:
            problems.append(str(e))
            return None, problems
        sc["end_word"] = words[last]
        sc["first_word_idx"] = ptr
        sc["last_word_idx"] = last
        ptr = last + 1
    if ptr < len(words):
        tail = " ".join(w["text"] for w in words[ptr:])
        problems.append(f"transcript words after the final scene's anchor are "
                        f"unclaimed: \"{tail[:200]}\" — extend the last scene's "
                        f"data-anchor-end to the true final phrase")
        return None, problems

    # Pass 2: required air + padding plan.
    insertions = []
    for i, sc in enumerate(scenes):
        is_q = sc["end_word"]["text"].rstrip("\"')]").endswith("?")
        sc["air"] = AIR_QUESTION if is_q else AIR
        if i + 1 < len(scenes):
            nxt = words[sc["last_word_idx"] + 1]
            natural = nxt["start"] - sc["end_word"]["end"]
            need = sc["air"] + LEAD
            if natural < need - 1e-9:
                # insert in the middle of the existing natural gap
                at = sc["end_word"]["end"] + max(natural, 0) / 2
                insertions.append((sc["last_word_idx"] + 1, round(at, 3),
                                   round(need - natural, 3)))
    return {"scenes": scenes, "words": words, "insertions": insertions,
            "html": html, "index_path": index_path}, problems


def plan_boundaries(scenes, words, audio_end):
    """Scene boundary times. Per-scene mode: sample-exact cuts from the
    synthesis manifest (final cut still guarded against the true wav end).
    Legacy mode: anchored word ends (assumes gaps sufficient)."""
    if scenes and "manifest_cut" in scenes[0]:
        bounds = [sc["manifest_cut"] for sc in scenes]
        bounds[-1] = round(max(bounds[-1], (audio_end or 0) + AUDIO_TAIL,
                               scenes[-1]["end_word"]["end"] + FINAL_HOLD), 3)
        return bounds
    bounds = []
    for i, sc in enumerate(scenes):
        if i + 1 < len(scenes):
            nxt_start = words[sc["last_word_idx"] + 1]["start"]
            natural = nxt_start - sc["end_word"]["end"]
            surplus = max(0.0, natural - (sc["air"] + LEAD))
            cut = sc["end_word"]["end"] + sc["air"] + min(surplus / 2, MAX_EXTRA_AIR)
            cut = min(cut, nxt_start - LEAD + 1e-9)
        else:
            cut = max((audio_end or 0) + AUDIO_TAIL,
                      sc["end_word"]["end"] + FINAL_HOLD)
        bounds.append(round(cut, 3))
    return bounds


def resolve_cues(sc, words, scene_start):
    """Cue anchor phrases -> local seconds inside this scene's word window."""
    out, problems = {}, []
    anchors = sc.get("cue_anchors") or {}
    lo, hi = sc["first_word_idx"], sc["last_word_idx"] + 1
    for key, val in anchors.items():
        if key not in CUE_KEYS:
            problems.append(f"{sc['id']}: unknown cue key {key!r} in data-cue-anchors")
            continue
        phrases = [val] if isinstance(val, str) else list(val)
        cues, ptr = [], lo
        for ph in phrases:
            try:
                first, last = find_phrase(words, ph, ptr, hi, label=f"{sc['id']}·{key}")
            except MatchError as e:
                problems.append(str(e))
                continue
            cues.append(round(words[first]["start"] - scene_start, 2))
            ptr = first + 1  # cues may overlap ranges but stay ordered
        if isinstance(val, str):
            out[key] = f"{cues[0]:g}" if cues else ""
        else:
            out[key] = ",".join(f"{c:g}" for c in cues)
        listvar, sep = LIST_PAIRS.get(key, (None, ","))
        if listvar and listvar in sc["variables"]:
            n_items = len([x for x in str(sc["variables"][listvar]).split(sep) if x.strip()])
            if n_items != len(phrases):
                problems.append(f"{sc['id']}: {listvar} has {n_items} items but "
                                f"{key} anchors {len(phrases)} phrases — every "
                                f"item needs its cue")
    return out, problems


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    apply_ = "--apply" in argv
    check = "--check" in argv or not apply_
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0]).resolve()
    wav = ws / "assets" / "voice" / "narration.wav"
    tr = ws / "assets" / "voice" / "transcript.json"

    plan, problems = compute(ws)
    if problems:
        report(problems, None, as_json, mode="anchor-resolution")

    # Padding (apply mode actually inserts; check mode reports it as drift).
    if plan["insertions"]:
        if apply_:
            insert_silences(wav, tr, plan["insertions"])
            plan, problems = compute(ws)  # recompute on padded timeline
            if problems or plan["insertions"]:
                report(problems + [f"padding did not converge: {plan['insertions']}"],
                       None, as_json, mode="padding")
        else:
            problems.append(
                f"narration needs {sum(d for *_, d in plan['insertions']):.2f}s of "
                f"boundary silence at {len(plan['insertions'])} points "
                f"(run --apply): {plan['insertions']}")

    scenes, words = plan["scenes"], plan["words"]
    audio_end = ffprobe_duration(wav)
    bounds = plan_boundaries(scenes, words, audio_end)

    html = plan["html"]
    changes = []
    prev_end = 0.0
    for sc, cut in zip(scenes, bounds):
        start = round(prev_end, 3)
        dur = round(cut - start, 3)
        cues, cue_problems = resolve_cues(sc, words, start)
        problems.extend(cue_problems)

        new_vars = dict(sc["variables"])
        new_vars.update(cues)
        if "sceneDuration" in new_vars:
            new_vars["sceneDuration"] = f"{dur:g}"

        def drift(name, old, new):
            if old != new:
                changes.append({"scene": sc["id"], "field": name,
                                "current": old, "computed": new})

        drift("data-start", f"{sc['start']:g}", f"{start:g}")
        drift("data-duration", f"{sc['duration']:g}", f"{dur:g}")
        for k, v in cues.items():
            drift(k, str(sc["variables"].get(k, "")), str(v))

        if apply_:
            new_tag = set_attr(sc["tag"], "data-start", f"{start:g}")
            new_tag = set_attr(new_tag, "data-duration", f"{dur:g}")
            new_tag = set_attr(new_tag, "data-variable-values", json_attr(new_vars), quote="'")
            html = html.replace(sc["tag"], new_tag, 1)
        prev_end = cut

    root_end = f"{bounds[-1]:g}"
    m_root = re.search(r'id="root"[^>]*data-duration="([\d.]+)"', html)
    if m_root and m_root.group(1) != root_end:
        changes.append({"scene": "root", "field": "data-duration",
                        "current": m_root.group(1), "computed": root_end})
    m_audio = re.search(r'<audio\b[^>]*data-duration="([\d.]+)"', html)
    audio_attr = f"{audio_end:g}" if audio_end else None
    if m_audio and audio_attr and m_audio.group(1) != audio_attr:
        changes.append({"scene": "narration", "field": "data-duration",
                        "current": m_audio.group(1), "computed": audio_attr})

    if apply_ and not problems:
        html = re.sub(r'(id="root"[^>]*data-duration=")[\d.]+(")',
                      lambda m: m.group(1) + root_end + m.group(2), html)
        if audio_attr:
            html = re.sub(r'(<audio\b[^>]*data-duration=")[\d.]+(")',
                          lambda m: m.group(1) + audio_attr + m.group(2), html)
        plan["index_path"].write_text(html)
    elif apply_ and problems:
        problems.append("index.html NOT written — resolve the problems above "
                        "(note: boundary silence padding, if any, was already "
                        "applied to narration.wav/transcript.json and is safe)")

    report(problems, {"changes": changes, "boundaries": bounds,
                      "audio_end": audio_end, "root_end": root_end,
                      "padded": bool(plan["insertions"]) if not apply_ else False,
                      "applied": apply_}, as_json,
           mode="apply" if apply_ else "check")


def report(problems, result, as_json, mode):
    ok = not problems and (result is None or mode == "apply" or not result["changes"])
    verdict = "PASS" if ok else "FAIL"
    if mode == "apply" and not problems:
        verdict = "APPLIED"
    payload = {"mode": mode, "verdict": verdict, "problems": problems,
               **(result or {})}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"[compile_timeline:{mode}] {verdict}")
        for p in problems:
            print(f"  ! {p}")
        for c in (result or {}).get("changes", []):
            print(f"  ~ {c['scene']}.{c['field']}: {c['current']} -> {c['computed']}")
        if result:
            print(f"  root={result['root_end']}s audio={result['audio_end']}s")
    sys.exit(0 if verdict in ("PASS", "APPLIED") else 1)


if __name__ == "__main__":
    main()
