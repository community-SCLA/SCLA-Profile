#!/usr/bin/env python3
"""Deterministic timing checker for SCLA HyperFrames lesson builds.

Checks every scene boundary in index.html against the narration transcript:
  - >=0.2s of air between a scene's last spoken word and its cut (frame.md ->
    "Scene boundaries, padding & endings")
  - no mid-word cuts (boundary before the last word's end = negative gap)
  - boundaries land on sentence ends (last word in the scene carries . ! ? )
  - question endings get extra air (>=0.35s after a '?')
  - final scene: root duration covers the wav's true audio end and holds >=1.0s
    after the last spoken word

Usage:
    check_boundaries.py <workspace-dir> [--json]

Expects <workspace>/index.html and either assets/voice/narration.words.json
(HeyGen native word timestamps, synth_narration.py's default provider) or
assets/voice/transcript.json (Whisper, --provider kokoro workspaces) — same
per-workspace detection as compile_timeline.words_path_for(). Uses ffprobe on
assets/voice/narration.wav when present.

Exit code 1 when any violation is found. This script is an evidence generator
for the qa-timing lane, not the whole verdict — cue-to-word alignment and
on-screen entrance timing still need judgment against real frames.
"""

import html
import json
import re
import subprocess
import sys
from pathlib import Path

MIN_AIR = 0.2
MIN_QUESTION_AIR = 0.35
MIN_FINAL_HOLD = 1.0
HEYGEN_WORDS_FILE = "narration.words.json"  # synth_narration.py / heygen-tts.mjs output


def words_path_for(ws: Path):
    """Whichever transcript exists for this workspace — HeyGen's native words
    file if synth_narration.py wrote one, else the Whisper transcript.json.
    Mirrors compile_timeline.words_path_for()."""
    voice_dir = ws / "assets" / "voice"
    heygen = voice_dir / HEYGEN_WORDS_FILE
    return heygen if heygen.is_file() else voice_dir / "transcript.json"


def wav_duration(path: Path):
    if not path.exists():
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return float(out)
    except Exception:
        return None


def parse_scenes(index_html: str):
    """Pull scene slots (id, composition id, start, duration) out of index.html."""
    scenes = []
    for m in re.finditer(r"<div\b[^>]*data-composition-src[^>]*>", index_html, re.S):
        tag = m.group(0)

        def attr(name):
            # (?<![\w-]) keeps `id` from matching inside `data-hf-id` etc.
            a = re.search(rf'(?<![\w-]){name}="([^"]*)"', tag)
            return a.group(1) if a else None

        start, dur = attr("data-start"), attr("data-duration")
        if start is None or dur is None:
            continue
        scenes.append({
            "id": attr("id") or attr("data-composition-id") or "?",
            "comp": attr("data-composition-id") or "?",
            "start": float(start),
            "end": float(start) + float(dur),
            "narration": attr("data-narration") or "",
        })
    scenes.sort(key=lambda s: s["start"])
    root = re.search(r'id="root"[^>]*data-duration="([\d.]+)"', index_html)
    root_duration = float(root.group(1)) if root else None
    return scenes, root_duration


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0])
    index_path = ws / "index.html"
    transcript_path = words_path_for(ws)
    wav_path = ws / "assets" / "voice" / "narration.wav"
    if not index_path.exists() or not transcript_path.exists():
        print(f"missing {index_path} or {transcript_path}", file=sys.stderr)
        sys.exit(2)

    words = json.loads(transcript_path.read_text())
    scenes, root_duration = parse_scenes(index_path.read_text())
    audio_end = wav_duration(wav_path)
    last_word_end = max(w["end"] for w in words)

    # Per-scene synthesis manifest (synth_narration.py) = sample-exact ground
    # truth for where each scene's audio really ends. Whisper word-end
    # timestamps are ±30-100ms and pad the last word of a run INTO trailing
    # silence, so judging air against them false-flags manifest-cut builds.
    manifest_path = ws / "assets" / "voice" / "scene-times.json"
    manifest = None
    if manifest_path.exists():
        try:
            ms = json.loads(manifest_path.read_text())["scenes"]
            if len(ms) == len(scenes):
                manifest = ms
                last_word_end = ms[-1]["end"]
        except (json.JSONDecodeError, KeyError):
            pass

    findings = []
    report = []
    for i, sc in enumerate(scenes):
        if manifest:
            # window by the next scene's manifest AUDIO start — whisper can
            # drift a boundary word's start into the silence gap past the cut
            lo = manifest[i - 1]["cut"] if i else 0.0
            hi = manifest[i + 1]["start"] if i + 1 < len(manifest) else float("inf")
            in_scene = [w for w in words if lo - 0.5 <= w["start"] < hi]
        else:
            in_scene = [w for w in words if sc["start"] <= w["start"] < sc["end"]]
        is_last = i == len(scenes) - 1
        if not in_scene:
            findings.append({"scene": sc["id"], "rule": "empty-scene",
                             "detail": "no narration words start inside this scene"})
            continue
        last = max(in_scene, key=lambda w: w["end"])
        spoken_end = manifest[i]["end"] if manifest else last["end"]
        gap = round(sc["end"] - spoken_end, 3)
        # Whether a scene ends mid-sentence is a property of its SCRIPT span
        # (data-narration), not the whisper transcript: whisper can drift the next
        # scene's first word (start AND end) into this window and be picked as a
        # spurious "last word" (e.g. a split landing on "…in. | Second,"). The
        # script text is authoritative, so read the sentence terminator from it and
        # fall back to whisper only when a scene carries no data-narration.
        script_text = html.unescape(sc.get("narration", "")).strip()
        text = script_text.split()[-1] if script_text else last["text"].strip()
        sentence_end = bool(re.search(r"[.!?][\"')\]]*$", text))
        # question flag: the manifest (script punctuation) is authoritative —
        # whisper sometimes hears a rising statement as "?" and vice versa
        is_question = (manifest[i].get("question", False) if manifest
                       else text.rstrip("\"')]").endswith("?"))
        row = {"scene": sc["id"], "cut_at": sc["end"], "last_word": text,
               "last_word_end": spoken_end, "gap": gap,
               "sentence_end": sentence_end}
        report.append(row)

        if gap < 0:
            findings.append({"scene": sc["id"], "rule": "mid-word-cut",
                             "detail": f"cut {abs(gap):.2f}s BEFORE last word "
                                       f"'{text}' finishes ({last['end']:.2f}s)"})
        elif not is_last and gap < MIN_AIR:
            findings.append({"scene": sc["id"], "rule": "insufficient-air",
                             "detail": f"only {gap:.2f}s after '{text}' "
                                       f"(need >= {MIN_AIR}s)"})
        if is_question and not is_last and gap < MIN_QUESTION_AIR:
            findings.append({"scene": sc["id"], "rule": "question-clipped",
                             "detail": f"question '{text}' gets {gap:.2f}s air "
                                       f"(need >= {MIN_QUESTION_AIR}s for the inflection)"})
        if not sentence_end and not is_last:
            findings.append({"scene": sc["id"], "rule": "mid-sentence-cut",
                             "detail": f"scene's last word '{text}' does not end "
                                       f"a sentence — the boundary splits a thought"})
        if is_last:
            hold = round(sc["end"] - last_word_end, 3)
            if hold < MIN_FINAL_HOLD:
                findings.append({"scene": sc["id"], "rule": "final-hold",
                                 "detail": f"final scene holds {hold:.2f}s after the "
                                           f"last spoken word (need >= {MIN_FINAL_HOLD}s)"})
            if audio_end is not None and root_duration is not None and root_duration < audio_end:
                findings.append({"scene": sc["id"], "rule": "audio-outlives-video",
                                 "detail": f"root duration {root_duration}s < audio "
                                           f"{audio_end:.2f}s — narration gets clipped"})
            if root_duration is not None and abs(sc["end"] - root_duration) > 0.001:
                findings.append({"scene": sc["id"], "rule": "tail-after-last-scene",
                                 "detail": f"last scene ends {sc['end']}s but root runs "
                                           f"{root_duration}s — bare-canvas tail"})

    result = {"scenes": report, "violations": findings,
              "root_duration": root_duration, "audio_end": audio_end,
              "verdict": "FAIL" if findings else "PASS"}
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        for r in report:
            mark = "ok " if r["sentence_end"] and r["gap"] >= MIN_AIR else "!! "
            print(f"{mark}{r['scene']:<18} cut {r['cut_at']:>8.2f}  "
                  f"last '{r['last_word']}' ends {r['last_word_end']:>8.2f}  "
                  f"gap {r['gap']:>+6.2f}s  sentence_end={r['sentence_end']}")
        print(f"\nroot={root_duration}s audio={audio_end}s")
        print(f"VERDICT: {result['verdict']} ({len(findings)} violation(s))")
        for f in findings:
            print(f"  - [{f['rule']}] {f['scene']}: {f['detail']}")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
