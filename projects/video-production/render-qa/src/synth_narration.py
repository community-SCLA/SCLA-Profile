#!/usr/bin/env python3
"""Per-scene narration synthesis for SCLA HyperFrames lesson builds.

WHY THIS EXISTS (2026-07-14): the single-take flow synthesized the whole
script as one Kokoro take, which speaks with ~0.03s inter-sentence gaps, then
surgically inserted digital-zero silence at Whisper-estimated boundaries
(compile_timeline.insert_silences). Whisper word timestamps are ±30-100ms, so
splices landed inside voiced audio — words cut in half, dead dropouts between
scenes, and orphaned silences left behind whenever an anchor moved after
--apply. This tool deletes that whole failure class: scene boundaries become
REAL silence, known sample-exactly at synthesis time.

What it does:
  1. Reads every scene slot's data-narration from index.html (the scene's
     verbatim span of the approved script; HTML-escaped in the attribute).
  2. Verifies the concatenated scene texts token-match the approved script
     (same tokenizer as preflight's script gate) — BEFORE any TTS runs.
  3. Synthesizes one clip per scene, cached by a hash of (provider, voice,
     speed, text) — only changed scenes re-synthesize. Default provider is
     HeyGen starfish (heygen-tts.mjs), which returns native per-word
     timestamps with the clip; --provider kokoro falls back to the local
     engine (no timestamps — chain `npx hyperframes transcribe` after).
  4. Trims each clip's lead/tail silence (peak-based, guarded, faded); on the
     HeyGen path the same trim offset shifts that clip's word timestamps so
     they stay aligned to the trimmed audio.
  5. Caps IN-SCENE silence at MAX_INSCENE_GAP (compress_gaps, 2026-07-28) —
     the provider's own mid-sentence pauses, which nothing else governs.
  6. Concatenates with real gaps: air after the scene's last sentence (0.3s,
     0.45s after a question) + 0.15s lead before the next scene. Each clip's
     (trim-shifted) words are re-offset again by its placement in the
     concatenation, turning per-clip HeyGen timestamps into the whole-file
     absolute times compile_timeline.py expects.
  7. Writes assets/voice/narration.wav + assets/voice/scene-times.json — the
     manifest compile_timeline.py consumes instead of anchor-guessing
     boundaries. On the HeyGen path also writes assets/voice/narration.words.json
     (flat [{id,text,start,end}], the same shape a Whisper transcript.json
     uses — compile_timeline.py / preflight.py read it when USE_HEYGEN_WORDS
     is on). Deletes stale transcript.json / narration.words.json / *.pre-pad.*
     from a previous run's provider so a forgotten re-transcribe or a stale
     words file fails loudly downstream instead of silently misaligning.

Default (HeyGen) path needs no further step before compile_timeline.py — word
timestamps came back with the synthesis. --provider kokoro still needs:
  npx hyperframes transcribe assets/voice/narration.wav --model small.en

Usage:
    synth_narration.py <workspace> [--provider heygen|kokoro] [--voice <id>]
                       [--speed 1.0] [--max-gap 0.5]
                       [--script <approved.txt>] [--force] [--json]
"""

import hashlib
import json
import os
import subprocess
import sys
import time
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import parse_scenes

# Boundary air (mirrors compile_timeline's rules; the gap becomes REAL silence
# here instead of a post-hoc splice).
AIR = 0.3            # after a normal sentence end (0.2 hard rule + 0.1 margin)
AIR_QUESTION = 0.45  # after a question (0.35 hard rule + 0.1 margin)
LEAD = 0.15          # silence before the next scene's first word
FINAL_HOLD = 1.1     # final scene visual hold past the last word (1.0 + 0.1)

# IN-SCENE silence cap (2026-07-28). The three constants above govern SCENE
# BOUNDARIES only — nothing governed the pauses HeyGen's Oxana puts INSIDE a
# clip. Measured on the reference build: 0.98–1.26s of real silence at
# sentence/clause boundaries mid-scene, non-deterministic on identical syntax
# ("First," -> 0.48s, "Fourth," -> 1.14s), so it cannot be written around in
# the script. It reads as a fault rather than a beat because the picture dies
# with the sound: compile_timeline.resolve_cues() derives every pointCue/chipCue
# from these same word timestamps, so a 1.2s hole in the audio is also 1.2s of
# a frozen frame (owner: "strange sound gaps / a major glitch or lag").
# 0.5 sits just above AIR_QUESTION so a mid-sentence pause can never outlast a
# scene change — the longest silence in a lesson is always a boundary.
MAX_INSCENE_GAP = 0.5
INSCENE_FADE = 0.008  # declick ramp at each excision splice (~8ms)

# Clip edge trim: peak-based so a breathy tail isn't misread as silence.
# Parallel provider calls for cache misses (network-bound). Lowered 5 -> 3 on
# 2026-07-27: at 5, HeyGen let ~5 clips through and then rejected the rest with
# "request/transcode error" — a 21-scene build lost 16 clips, while sequential
# calls succeeded every time. Override with TTS_WORKERS=1 to force sequential.
TTS_WORKERS = max(1, int(os.environ.get("TTS_WORKERS", "3")))
TTS_RETRIES = 3          # attempts per clip before the build fails
TTS_BACKOFF = 2.0        # seconds, doubled each retry (2s, 4s, 8s)

TRIM_THRESHOLD = 300     # |int16| below this is "silent" (~ -40 dBFS)
TRIM_WIN = 0.02          # scan window (s)
GUARD_LEAD = 0.04        # keep this much silence before the first voiced win
GUARD_TAIL = 0.08        # keep this much decay after the last voiced window
EDGE_FADE = 0.005        # fade at trimmed edges — never step to digital zero

# Repo-root-relative: render-qa/ -> video-production/ -> projects/ -> repo root.
# Skills live in .claude/skills/ (materialized from .agents/ 2026-07-28, P4).
HEYGEN_TTS = Path(__file__).resolve().parents[3] / \
    ".claude/skills/hyperframes-media/scripts/heygen-tts.mjs"
WORDS_FILENAME = "narration.words.json"  # must match compile_timeline.py /
                                          # preflight.py HEYGEN_WORDS_FILE

DEFAULT_PROVIDER = "heygen"
DEFAULT_VOICE = {"heygen": "442360a3e0894fbd85024ff64cc2b928",  # Oxana, en-US
                 "kokoro": "af_heart"}
DEFAULT_SPEED = "1.0"  # 0.95 -> 1.0 on 2026-07-28 (owner: "the WPM could
                       # increase, ever slightly"). Changes the clip cache key,
                       # so the next build re-synthesizes every scene.


def die(msg, code=1):
    print(f"[synth_narration] FAIL\n  ! {msg}")
    sys.exit(code)


def tts(text: str, out: Path, provider: str, voice: str, speed: str, cwd: Path,
        words_out: Path = None):
    """Synthesize one clip. On provider=heygen with words_out set, also writes
    that clip's native word timestamps (clip-relative seconds) as a flat
    [{text,start,end}] json — caller shifts them into whole-file time."""
    if provider == "heygen":
        cmd = ["node", str(HEYGEN_TTS), text, "-o", str(out),
               "--voice", voice, "--speed", speed]
        if words_out is not None:
            cmd += ["--words", str(words_out)]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        if p.returncode != 0 or not out.is_file():
            die(f"heygen tts failed for {out.name}: "
                f"{(p.stdout + p.stderr).strip()[-500:]}")
        if words_out is not None and not words_out.is_file():
            die(f"heygen tts for {out.name} returned no word timestamps "
                f"({words_out.name} missing) — cannot build {WORDS_FILENAME}")
    else:
        cmd = ["npx", "hyperframes", "tts", text,
               "--voice", voice, "--speed", speed, "-o", str(out)]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        if p.returncode != 0 or not out.is_file():
            die(f"tts failed for {out.name}: {(p.stdout + p.stderr).strip()[-500:]}")


def tts_retrying(*args, **kwargs):
    """`tts` with bounded retry (2026-07-27). Provider-side rejections under
    concurrency are transient — HeyGen returns "request/transcode error" for a
    burst and then serves the identical text fine moments later. `tts` reports
    every failure through `die`, so SystemExit is the failure signal here, not
    an abort. The final attempt re-raises untouched, so a genuinely bad clip
    still fails the build loudly."""
    label = kwargs.get("out") or (args[1] if len(args) > 1 else "clip")
    for attempt in range(1, TTS_RETRIES + 1):
        try:
            return tts(*args, **kwargs)
        except (SystemExit, Exception):
            if attempt == TTS_RETRIES:
                raise
            delay = TTS_BACKOFF * (2 ** (attempt - 1))
            print(f"  retry {attempt}/{TTS_RETRIES - 1} for "
                  f"{getattr(label, 'name', label)} in {delay:.0f}s",
                  file=sys.stderr, flush=True)
            time.sleep(delay)


def read_wav(path: Path):
    with wave.open(str(path), "rb") as r:
        params = r.getparams()
        if params.sampwidth != 2:
            die(f"{path.name}: expected 16-bit PCM, got sampwidth={params.sampwidth}")
        data = array("h")
        data.frombytes(r.readframes(r.getnframes()))
    return params, data


def trim_clip(data, rate, chan, trim_tail=True):
    """Trim lead/tail silence (peak-scan in TRIM_WIN windows, guarded), fade
    the cut edges. Returns (new array, trim_offset_seconds) — trim_offset is
    how much was cut from the START, so a caller holding word timestamps
    against the ORIGINAL clip can shift them: local_time - trim_offset.
    Never trims into voiced audio.

    trim_tail=False keeps the clip's natural decay intact. The FINAL clip is
    synthesized this way (2026-07-29): tail-trimming exists to tighten the
    splice against the NEXT clip, and the last clip has no next clip, so the
    trim buys nothing and costs the word its release. The owner heard exactly
    that — "the audio didn't fully complete the last word... it got cut off."
    Measured on the rejected build: scene-25.wav ran 4.754s but only 4.574s
    reached narration.wav, whose final 100ms still carried signal (peak 1327,
    ~-28 dBFS) before EDGE_FADE ramped it to zero and the file simply ended."""
    n = len(data) // chan
    win = max(1, int(TRIM_WIN * rate))

    def window_peak(w0):
        seg = data[w0 * chan:(w0 + win) * chan]
        return max((abs(s) for s in seg), default=0)

    first = 0
    while first < n and window_peak(first) < TRIM_THRESHOLD:
        first += win
    if first >= n:
        return data[:], 0.0  # all silence — leave untouched, caller will notice
    last = n
    if trim_tail:
        while last > first and window_peak(max(0, last - win)) < TRIM_THRESHOLD:
            last -= win
    a = max(0, first - int(GUARD_LEAD * rate))
    b = min(n, last + int(GUARD_TAIL * rate)) if trim_tail else n
    out = data[a * chan:b * chan]
    f = int(EDGE_FADE * rate)
    m = len(out) // chan
    for p in range(min(f, m)):
        g = (p + 1) / (f + 1)
        for c in range(chan):
            out[p * chan + c] = int(out[p * chan + c] * g)
            # Only fade the tail where we actually cut one. An untrimmed tail
            # already decays to the provider's own silence; fading it again
            # shaves the release the trim was skipped to preserve.
            if trim_tail:
                q = (m - 1 - p) * chan + c
                out[q] = int(out[q] * g)
    return out, a / rate


def _fade_edges(seg, chan, fade, fade_in, fade_out):
    """Ramp the head (fade_in) and/or tail (fade_out) of an int16 frame array to
    ~0 over `fade` frames, so a splice never steps between two sample values.
    Same idiom as compile_timeline._fade_edges — including the half-segment cap,
    so a short kept span between two excisions never double-scales its middle."""
    n = len(seg) // chan
    if n == 0 or fade <= 0:
        return
    f = min(fade, n // 2 if (fade_in and fade_out) else n)
    if f <= 0:
        return
    if fade_in:
        for p in range(f):
            g = (p + 1) / (f + 1)  # ~0 at the splice -> 1 into the audio
            base = p * chan
            for c in range(chan):
                seg[base + c] = int(seg[base + c] * g)
    if fade_out:
        for p in range(f):
            g = (f - p) / (f + 1)  # 1 in the audio -> ~0 at the splice
            base = (n - f + p) * chan
            for c in range(chan):
                seg[base + c] = int(seg[base + c] * g)


def compress_gaps(data, words, rate, chan, max_gap):
    """Cap every IN-SCENE inter-word silence in one clip at `max_gap` seconds.

    Runs BEFORE trim_clip, on the raw clip and its raw (clip-relative) provider
    word timestamps, so the trim + concat offset math downstream is untouched:
    it still sees one clip and one word list that agree with each other.

    Only the space BETWEEN words is eligible — a clip's lead and tail silence
    belong to trim_clip and the boundary air, and are never seen here. For each
    over-long pause the middle is excised and max_gap/2 of decay is kept on
    each side, so neither the preceding word's tail nor the next word's onset
    moves. Cut points are integer frames off the word timestamps, so the same
    clip always yields the same bytes.

    Returns (new frame array, new word list, seconds removed, gaps cut). Word
    timestamps after each cut are shifted back by everything removed before
    them, keeping the list truthful against the returned audio."""
    n = len(data) // chan
    cuts, shifted, removed = [], [], 0.0
    for i, w in enumerate(words):
        if i:
            a = int(round((words[i - 1]["end"] + max_gap / 2) * rate))
            b = int(round((w["start"] - max_gap / 2) * rate))
            a, b = min(max(a, 0), n), min(max(b, 0), n)
            if b > a:  # only true when the gap exceeded max_gap
                cuts.append((a, b))
                removed += (b - a) / rate
        shifted.append({**w, "start": w["start"] - removed,
                        "end": w["end"] - removed})
    if not cuts:
        return data, words, 0.0, 0
    fade = int(round(INSCENE_FADE * rate))
    out = array("h")
    pos = 0
    for a, b in cuts:
        seg = data[pos * chan:a * chan]
        _fade_edges(seg, chan, fade, fade_in=pos > 0, fade_out=True)
        out += seg
        pos = b
    seg = data[pos * chan:]  # tail past the last cut; its own end is trim_clip's
    _fade_edges(seg, chan, fade, fade_in=True, fade_out=False)
    out += seg
    return out, shifted, removed, len(cuts)


def verify_script(scene_texts, ws: Path, script_override):
    """Concatenated data-narration must token-match the approved script —
    it is copy-paste, so the match is exact, not threshold-based."""
    from preflight import locate_script, tokenize_for_diff, diff_script_transcript
    script_path = Path(script_override) if script_override else locate_script(ws)
    if script_path is None:
        print(f"  WARN approved script not found for stem {ws.name!r} and no "
              f"--script given — narration-vs-script check SKIPPED")
        return
    script_toks = tokenize_for_diff(script_path.read_text())
    narr_toks = tokenize_for_diff(" ".join(scene_texts))
    if script_toks != narr_toks:
        _, _, segments = diff_script_transcript(script_toks, narr_toks)
        die("data-narration does not match the approved script "
            f"({script_path}):\n  ! " + "\n  ! ".join(segments[:20]))


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    force = "--force" in argv

    def opt(name, default):
        if name in argv:
            i = argv.index(name)
            if i + 1 >= len(argv):
                die(f"{name} requires a value", 2)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return default

    provider = opt("--provider", DEFAULT_PROVIDER)
    if provider not in DEFAULT_VOICE:
        die(f"--provider must be one of {sorted(DEFAULT_VOICE)}, got {provider!r}", 2)
    voice = opt("--voice", DEFAULT_VOICE[provider])
    speed = opt("--speed", DEFAULT_SPEED)
    try:
        max_gap = float(opt("--max-gap", MAX_INSCENE_GAP))
    except ValueError:
        die("--max-gap must be a number (seconds)", 2)
    if max_gap <= 0:
        die(f"--max-gap must be > 0, got {max_gap}", 2)
    script_override = opt("--script", None)
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0]).resolve()
    voice_dir = ws / "assets" / "voice"
    clips_dir = voice_dir / "scenes"
    clips_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = voice_dir / "scene-times.json"

    scenes = parse_scenes((ws / "index.html").read_text())
    if not scenes:
        die("no scene slots found in index.html")
    missing = [s["id"] for s in scenes if not s["narration"]]
    if missing:
        die(f"scene(s) missing data-narration: {', '.join(missing)} — "
            f"per-scene synthesis is all-or-nothing (legacy single-take flow "
            f"needs no data-narration at all)")
    texts = [s["narration"] for s in scenes]
    verify_script(texts, ws, script_override)

    old = {}
    if manifest_path.is_file():
        try:
            old = {c["clip"]: c.get("sha") for c in
                   json.loads(manifest_path.read_text()).get("scenes", [])}
        except (json.JSONDecodeError, KeyError):
            old = {}

    need_words = provider == "heygen"

    # Synthesize (or reuse) per-scene clips. Each clip is an independent
    # network round-trip to the provider, so the misses are synthesized in
    # parallel (2026-07-27: 14 sequential HeyGen calls cost ~100s of every
    # build iteration; a small pool cuts that to ~25s). Clip files are
    # per-scene, the cache key is content-addressed, and results are assembled
    # in scene order afterwards, so the output stays byte-identical.
    plan = []
    for i, (sc, text) in enumerate(zip(scenes, texts), start=1):
        clip_rel = f"scenes/scene-{i:02d}.wav"
        clip = clips_dir / f"scene-{i:02d}.wav"
        words_path = clips_dir / f"scene-{i:02d}.words.json"
        sha = hashlib.sha1(f"{provider}|{voice}|{speed}|{text}".encode()).hexdigest()[:16]
        stale = force or not clip.is_file() or old.get(clip_rel) != sha
        if not stale and need_words and not words_path.is_file():
            die(f"scene-{i:02d}: cached clip has no {words_path.name} "
                f"(missing or from a pre-HeyGen run) — re-run with --force")
        plan.append({"i": i, "sc": sc, "text": text, "clip": clip, "clip_rel": clip_rel,
                     "words_path": words_path, "sha": sha, "stale": stale})

    misses = [p for p in plan if p["stale"]]
    if misses:
        with ThreadPoolExecutor(max_workers=min(TTS_WORKERS, len(misses))) as pool:
            futures = {
                pool.submit(tts_retrying, p["text"], p["clip"], provider, voice,
                            speed, ws, p["words_path"] if need_words else None): p
                for p in misses
            }
            for fut in as_completed(futures):
                fut.result()  # re-raises the worker's SystemExit/exception here

    entries = []
    raw_words = []  # per-scene: clip-relative [{text,start,end}], heygen only
    for p in plan:
        verb = "tts " if p["stale"] else "keep"
        note = f"({len(p['text'].split())} words)" if p["stale"] else "(unchanged)"
        print(f"  {verb} scene-{p['i']:02d}  {note}")
        raw_words.append(json.loads(p["words_path"].read_text()) if need_words else [])
        entries.append({"i": p["i"] - 1, "id": p["sc"]["id"], "clip": p["clip_rel"],
                        "sha": p["sha"], "text_words": len(p["text"].split()),
                        "question": p["text"].rstrip().rstrip("\"')]").endswith("?")})

    # Trim + concatenate with real gaps. On the HeyGen path, each clip's raw
    # (clip-relative) word timestamps are shifted twice: once by the trim
    # offset (silence cut from the clip's head), once by the clip's placement
    # in the concatenation — turning them into whole-file absolute times.
    out = array("h")
    rate = chan = None
    cursor = 0.0
    all_words = []
    gap_trimmed = 0.0
    for i, (e, sc) in enumerate(zip(entries, scenes)):
        params, data = read_wav(clips_dir / Path(e["clip"]).name)
        if rate is None:
            rate, chan = params.framerate, params.nchannels
        elif (params.framerate, params.nchannels) != (rate, chan):
            die(f"{e['clip']}: format {params.framerate}Hz/{params.nchannels}ch "
                f"differs from first clip {rate}Hz/{chan}ch")
        # In-scene gap compressor (2026-07-28) — HeyGen path only: without word
        # timestamps there is no way to tell a mid-sentence pause from a
        # deliberate one. Runs before the trim so both the clip and its raw
        # words come out of it consistent, and everything below (trim offset,
        # concat offset, scene-times.json, and every cue compile_timeline.py
        # derives from these words) recomputes off the compressed audio.
        if need_words:
            data, raw_words[i], cut_s, n_cuts = compress_gaps(
                data, raw_words[i], rate, chan, max_gap)
            if n_cuts:
                gap_trimmed += cut_s
                e["gap_trimmed"] = round(cut_s, 3)
                print(f"  {Path(e['clip']).stem}: trimmed {cut_s:.2f}s across "
                      f"{n_cuts} gap{'s' if n_cuts != 1 else ''}")
        is_final = i == len(entries) - 1
        clip_data, trim_offset = trim_clip(data, rate, chan,
                                           trim_tail=not is_final)
        e["start"] = round(cursor, 3)
        cursor += len(clip_data) / chan / rate
        e["end"] = round(cursor, 3)
        if need_words:
            shift = e["start"] - trim_offset
            kept_end = trim_offset + (len(clip_data) // chan) / rate
            for w in raw_words[i]:
                if w["end"] <= trim_offset or w["start"] >= kept_end:
                    continue  # fell entirely in the trimmed silence
                all_words.append({
                    "text": w["text"],
                    "start": round(max(w["start"], trim_offset) + shift, 3),
                    "end": round(min(w["end"], kept_end) + shift, 3)})
        air = AIR_QUESTION if e["question"] else AIR
        e["air"] = air
        if i + 1 < len(entries):
            e["cut"] = round(e["end"] + air, 3)
            gap = air + LEAD
        else:
            e["cut"] = round(e["end"] + FINAL_HOLD, 3)
            # Was 0.0 until 2026-07-29 — the manifest promised a FINAL_HOLD the
            # wav never contained, so narration.wav stopped dead on the last
            # word's decay while the video held 1.1s past it. Every other scene
            # got 0.3s of real silence to land in; the one place a listener most
            # needs it was the only place without it. Now the wav runs to the
            # same point the composition does.
            gap = FINAL_HOLD
        out += clip_data
        out += array("h", bytes(int(round(gap * rate)) * 2 * chan))
        cursor += gap

    wav_path = voice_dir / "narration.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(chan)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(out.tobytes())
    audio_end = round(len(out) / chan / rate, 3)

    manifest = {"mode": "per-scene", "provider": provider, "voice": voice,
                "speed": speed, "rate": rate, "audio_end": audio_end,
                "air": AIR, "air_question": AIR_QUESTION, "lead": LEAD,
                "final_hold": FINAL_HOLD, "max_inscene_gap": max_gap,
                "gap_trimmed": round(gap_trimmed, 3), "scenes": entries}
    manifest_path.write_text(json.dumps(manifest, indent=2))

    words_written = 0
    if need_words:
        words_path = voice_dir / WORDS_FILENAME
        with_ids = [{"id": f"w{idx}", **w} for idx, w in enumerate(all_words)]
        words_path.write_text(json.dumps(with_ids, indent=2))
        words_written = len(with_ids)

    # Stale-artifact hygiene: the old transcript/words/padding belong to the
    # old audio (or a different provider). Deleting them makes a forgotten
    # re-transcribe, or a stale words file from a since-abandoned provider
    # switch, fail loudly instead of silently misaligning.
    removed = []
    stale_names = ["transcript.json", "transcript.pre-pad.json", "narration.pre-pad.wav"]
    if not need_words:
        stale_names.append(WORDS_FILENAME)
    for stale in stale_names:
        p = voice_dir / stale
        if p.exists():
            p.unlink()
            removed.append(stale)

    if as_json:
        print(json.dumps({"verdict": "OK", "provider": provider,
                          "audio_end": audio_end, "scenes": len(entries),
                          "words": words_written, "removed": removed,
                          "max_inscene_gap": max_gap,
                          "gap_trimmed": round(gap_trimmed, 3)}, indent=2))
    else:
        print(f"[synth_narration] OK — {provider}, {len(entries)} scenes, "
              f"audio {audio_end}s -> {wav_path.relative_to(ws)}")
        if gap_trimmed:
            print(f"  in-scene silence capped at {max_gap}s — "
                  f"{gap_trimmed:.2f}s removed in total")
        if words_written:
            print(f"  words {words_written} -> {(voice_dir / WORDS_FILENAME).relative_to(ws)}")
        if removed:
            print(f"  removed stale: {', '.join(removed)}")
        if not need_words:
            print("  next: npx hyperframes transcribe assets/voice/narration.wav "
                  "--model small.en")
    sys.exit(0)


if __name__ == "__main__":
    main()
