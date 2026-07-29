#!/usr/bin/env python3
"""Adversarial fixture tests for the pipeline toolchain.

Each case is an attack on a known historical failure mode:
  duplicate words (the "process." bug, 2026-07-10), missing anchors, cue-count
  mismatches, unclaimed transcript tails, question air, padding idempotency,
  ASCII-apostrophe attribute injection, and the data-hf-id/id parsing trap.

Run:  python3 tests/run_tests.py   (exit 0 = all pass)
"""

import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

PIPE = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(PIPE))
from hfp_common import MatchError, find_phrase, get_attr, json_attr, load_transcript

TMP = Path(tempfile.gettempdir()) / "scla-pipeline-tests"

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


def make_wav(path, seconds, rate=24000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        n = int(seconds * rate)
        frames = b"".join(struct.pack("<h", int(8000 * math.sin(i / 20))) for i in range(n))
        w.writeframes(frames)


def make_workspace(words, scenes_html, seconds):
    if TMP.exists():
        shutil.rmtree(TMP)
    (TMP / "assets" / "voice").mkdir(parents=True)
    (TMP / "assets" / "voice" / "transcript.json").write_text(json.dumps(words))
    make_wav(TMP / "assets" / "voice" / "narration.wav", seconds)
    (TMP / "index.html").write_text(f"""<!DOCTYPE html>
<html><body>
<div data-hf-id="hf-root1" id="root" data-composition-id="main" data-start="0" data-duration="10" data-width="1920" data-height="1080">
{scenes_html}
<audio data-hf-id="hf-aud" id="narration" class="clip" src="assets/voice/narration.wav" data-start="0" data-duration="{seconds}" data-track-index="2"></audio>
</div></body></html>""")
    return TMP


def compile_run(ws, *flags):
    return subprocess.run([sys.executable, str(PIPE / "compile_timeline.py"), str(ws), *flags],
                          capture_output=True, text=True)


def W(text, start, end):
    return {"text": text, "start": start, "end": end}


print("== unit: phrase matching ==")
words = load_transcript(Path("/dev/stdin")) if False else None
ws_words = [W("Here", 0.0, 0.2), W("is", 0.2, 0.35), W("a", 0.35, 0.4),
            W("process.", 0.4, 0.9), W("A", 1.0, 1.1), W("simple", 1.1, 1.5),
            W("process.", 1.5, 2.0)]
for i, w_ in enumerate(ws_words):
    w_["idx"] = i
    import re as _re
    w_["norm"] = _re.sub(r"[^0-9a-z]+", "", w_["text"].lower())
# duplicate word: forward pointer must select by position, not first-in-text
first, last = find_phrase(ws_words, "process.", 0, label="t")
check("duplicate word — first occurrence from lo=0", last == 3)
first, last = find_phrase(ws_words, "process.", 4, label="t")
check("duplicate word — second occurrence from lo=4", last == 6)
first, last = find_phrase(ws_words, "simple process", 0, label="t")
check("multi-word phrase spans words", (first, last) == (5, 6))
try:
    find_phrase(ws_words, "banana", 0, label="t")
    check("missing phrase raises", False)
except MatchError as e:
    check("missing phrase raises with window text", "banana" in str(e) and "Here" in str(e))

print("== unit: attribute parsing (data-hf-id trap) ==")
tag = '<div data-hf-id="hf-y4po" class="clip" id="el-01" data-start="0.0">'
check("id does not match data-hf-id", get_attr(tag, "id") == "el-01")
check("json_attr strips ASCII apostrophes",
      "'" not in json_attr({"h": "one 'right' answer"}))

print("== e2e: two-scene compile with padding, question air, duplicate anchor ==")
# Natural gaps of 0.05s — the compiler must pad. Scene 1 ends on a question.
tr = [W("Do", 0.0, 0.2), W("you", 0.2, 0.4), W("care?", 0.4, 1.0),
      W("Here", 1.05, 1.3), W("is", 1.3, 1.5), W("a", 1.5, 1.6),
      W("process.", 1.6, 2.2), W("A", 2.25, 2.4), W("simple", 2.4, 2.8),
      W("process.", 2.8, 3.4)]
scenes = """
<div data-hf-id="hf-s1" class="clip" id="s1" data-composition-id="scla-title" data-composition-src="compositions/scla-title.html" data-variable-values='{"title":"x","sceneDuration":"1"}' data-anchor-end="care?" data-start="0" data-duration="1" data-track-index="1"></div>
<div data-hf-id="hf-s2" class="clip" id="s2" data-composition-id="scla-chips" data-composition-src="compositions/scla-chips.html" data-variable-values='{"chips":"One,Two","chipCues":"9,9","sceneDuration":"1"}' data-cue-anchors='{"chipCues":["here","simple process."]}' data-anchor-end="simple process." data-start="1" data-duration="2" data-track-index="1"></div>
"""
ws = make_workspace(tr, scenes, 3.5)
r = compile_run(ws, "--check")
check("check fails before padding", r.returncode == 1, r.stdout)
check("check names the padding need", "boundary silence" in r.stdout)
r = compile_run(ws, "--apply", "--json")
check("apply exits 0", r.returncode == 0, r.stdout + r.stderr)
out = json.loads(r.stdout)
tr2 = json.loads((ws / "assets/voice/transcript.json").read_text())
check("transcript shifted by padding", tr2[3]["start"] > 1.05)
html = (ws / "index.html").read_text()
q_gap = None
s1 = get_attr([t for t in html.split("<div") if 'id="s1"' in t][0], "data-duration")
care_end = tr2[2]["end"]
check("question boundary gets 0.45s air", abs(float(s1) - (care_end + 0.45)) < 0.02,
      f"s1 dur {s1} vs care? end {care_end}")
check("duplicate anchor: scene2 cue lands on SECOND process.",
      '"chipCues":"' in html and json.loads(get_attr(
          [t for t in html.split("<div") if 'id="s2"' in t][0].replace("’", "'"),
          "data-variable-values"))["chipCues"].split(",")[1] != "9")
r = compile_run(ws, "--check")
check("idempotent: check passes after apply", r.returncode == 0, r.stdout)
r2 = compile_run(ws, "--apply")
r = compile_run(ws, "--check")
check("double-apply stays converged", r.returncode == 0, r.stdout)

print("== e2e: failure modes stay loud ==")
# unclaimed tail: anchor scene 2 at the FIRST process., leaving words unclaimed
scenes_bad = scenes.replace('data-anchor-end="simple process."', 'data-anchor-end="process."')
ws = make_workspace(tr, scenes_bad, 3.5)
r = compile_run(ws, "--apply")
check("unclaimed transcript tail is fatal", r.returncode == 1 and "unclaimed" in r.stdout, r.stdout)
html_after = (ws / "index.html").read_text()
check("index.html untouched on fatal error", 'data-start="1"' in html_after)

# cue-count mismatch: 2 chips, 1 anchor
scenes_bad = scenes.replace('{"chipCues":["here","simple process."]}', '{"chipCues":["here"]}')
ws = make_workspace(tr, scenes_bad, 3.5)
r = compile_run(ws, "--apply")
check("cue-count mismatch is fatal", r.returncode == 1 and "needs its cue" in r.stdout, r.stdout)

# anchor missing from transcript
scenes_bad = scenes.replace('data-anchor-end="care?"', 'data-anchor-end="banana split?"')
ws = make_workspace(tr, scenes_bad, 3.5)
r = compile_run(ws, "--apply")
check("unresolvable anchor is fatal", r.returncode == 1 and "banana" in r.stdout, r.stdout)

# scene missing anchor entirely
scenes_bad = scenes.replace('data-anchor-end="care?" ', "")
ws = make_workspace(tr, scenes_bad, 3.5)
r = compile_run(ws, "--check")
check("missing data-anchor-end is fatal", r.returncode == 1 and "missing data-anchor-end" in r.stdout)

# cue anchor outside its scene window (phrase spoken in scene 1)
scenes_bad = scenes.replace('{"chipCues":["here","simple process."]}', '{"chipCues":["do you","simple process."]}')
ws = make_workspace(tr, scenes_bad, 3.5)
r = compile_run(ws, "--apply")
check("cue anchor outside scene window is fatal", r.returncode == 1, r.stdout)

print("== e2e: per-scene synthesis (manifest mode) ==")
import synth_narration as sn


def make_clip(path, lead_sil, voiced, tail_sil, rate=24000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = b"\x00\x00" * int(lead_sil * rate)
        frames += b"".join(struct.pack("<h", int(8000 * math.sin(i / 20)))
                           for i in range(int(voiced * rate)))
        frames += b"\x00\x00" * int(tail_sil * rate)
        w.writeframes(frames)


def make_manifest_workspace():
    """Two data-narration scenes (no data-anchor-end), pre-seeded clips whose
    manifest shas match, so synth_narration runs its full concat path without
    invoking TTS."""
    if TMP.exists():
        shutil.rmtree(TMP)
    clips = TMP / "assets" / "voice" / "scenes"
    clips.mkdir(parents=True)
    texts = ["Do you care?",
             'The answer is &quot;a simple process.&quot;']  # &quot; unescape trap
    make_clip(clips / "scene-01.wav", 0.10, 1.0, 0.30)
    make_clip(clips / "scene-02.wav", 0.05, 1.0, 0.20)
    # Clip-relative HeyGen word timestamps (heygen is the default provider —
    # a cache hit still needs these on disk, same as the wav itself, or
    # synth_narration.py dies loudly rather than silently reusing a clip with
    # no words). Values just need to sit inside each clip's voiced window.
    (clips / "scene-01.words.json").write_text(json.dumps([
        {"text": "Do", "start": 0.15, "end": 0.35},
        {"text": "you", "start": 0.40, "end": 0.60},
        {"text": "care?", "start": 0.65, "end": 1.05}]))
    (clips / "scene-02.words.json").write_text(json.dumps([
        {"text": "a", "start": 0.20, "end": 0.35},
        {"text": "simple", "start": 0.40, "end": 0.70},
        {"text": "process.", "start": 0.75, "end": 1.00}]))
    import html as _html
    entries = []
    provider, speed = sn.DEFAULT_PROVIDER, sn.DEFAULT_SPEED
    voice = sn.DEFAULT_VOICE[provider]
    for i, t in enumerate(texts, start=1):
        raw = _html.unescape(t)
        sha = hashlib.sha1(
            f"{provider}|{voice}|{speed}|{raw}".encode()).hexdigest()[:16]
        entries.append({"clip": f"scenes/scene-{i:02d}.wav", "sha": sha})
    (TMP / "assets" / "voice" / "scene-times.json").write_text(
        json.dumps({"scenes": entries}))
    # stale artifacts that synth must clear
    (TMP / "assets" / "voice" / "transcript.json").write_text("[]")
    (TMP / "assets" / "voice" / "narration.pre-pad.wav").write_bytes(b"x")
    (TMP / "index.html").write_text(f"""<!DOCTYPE html>
<html><body>
<div data-hf-id="hf-root1" id="root" data-composition-id="main" data-start="0" data-duration="10" data-width="1920" data-height="1080">
<div data-hf-id="hf-s1" class="clip" id="s1" data-composition-id="scla-title" data-composition-src="compositions/scla-title.html" data-variable-values='{{"title":"x","theme":"summit","sceneDuration":"1"}}' data-narration="{texts[0]}" data-start="0" data-duration="1" data-track-index="1"></div>
<div data-hf-id="hf-s2" class="clip" id="s2" data-composition-id="scla-chips" data-composition-src="compositions/scla-chips.html" data-variable-values='{{"chips":"One,Two","chipCues":"9,9","theme":"summit","sceneDuration":"1"}}' data-cue-anchors='{{"chipCues":["a","simple"]}}' data-narration="{texts[1]}" data-start="1" data-duration="2" data-track-index="1"></div>
<audio data-hf-id="hf-aud" id="narration" class="clip" src="assets/voice/narration.wav" data-start="0" data-duration="3.5" data-track-index="2"></audio>
</div></body></html>""")
    return TMP


ws = make_manifest_workspace()
r = subprocess.run([sys.executable, str(PIPE / "synth_narration.py"), str(ws)],
                   capture_output=True, text=True)
check("synth runs clip-cached (no TTS)", r.returncode == 0, r.stdout + r.stderr)
check("synth reuses unchanged clips", "keep scene-01" in r.stdout, r.stdout)
mani = json.loads((ws / "assets/voice/scene-times.json").read_text())
s1, s2 = mani["scenes"]
check("clip 1 trimmed to guards (~1.12s)", abs((s1["end"] - s1["start"]) - 1.12) < 0.06,
      f"{s1}")
check("question gets question air", s1["question"] and abs(s1["cut"] - (s1["end"] + 0.45)) < 0.001, f"{s1}")
check("real gap between scenes = air + lead",
      abs(s2["start"] - (s1["end"] + 0.45 + 0.15)) < 0.001, f"{s1} {s2}")
# Read the constant, never re-type it: this line said 1.1 and went red the day
# the owner asked for a longer ending, which is a test asserting a number rather
# than the behaviour that the final cut is the last word plus the declared hold.
sys.path.insert(0, str(PIPE))
import synth_narration as _synth  # noqa: E402
check("final cut = end + final hold",
      abs(s2["cut"] - (s2["end"] + _synth.FINAL_HOLD)) < 0.001,
      f"{s2} hold={_synth.FINAL_HOLD}")
check("stale transcript/pre-pad cleared",
      not (ws / "assets/voice/transcript.json").exists()
      and not (ws / "assets/voice/narration.pre-pad.wav").exists())
with wave.open(str(ws / "assets/voice/narration.wav"), "rb") as wv:
    total = wv.getnframes() / wv.getframerate()
check("wav length == manifest audio_end", abs(total - mani["audio_end"]) < 0.002,
      f"{total} vs {mani['audio_end']}")
# the inserted gap must be true digital silence
with wave.open(str(ws / "assets/voice/narration.wav"), "rb") as wv:
    data = wv.readframes(wv.getnframes())
import array as _array
smp = _array.array("h"); smp.frombytes(data)
g0, g1 = int((s1["end"] + 0.05) * 24000), int((s2["start"] - 0.05) * 24000)
check("gap is real silence", max(abs(x) for x in smp[g0:g1]) == 0)

print("== e2e: compile_timeline manifest mode ==")
# Whole-file absolute words for the synthesized wav, inside each manifest
# window — overwrites what synth_narration.py itself derived from the
# fixture per-clip words.json files, since compute() prefers
# narration.words.json (HeyGen path) over transcript.json when present.
tr = [W("Do", s1["start"] + 0.05, s1["start"] + 0.3),
      W("you", s1["start"] + 0.3, s1["start"] + 0.6),
      W("care?", s1["start"] + 0.6, s1["end"] - 0.02),
      W("a", s2["start"] + 0.05, s2["start"] + 0.3),
      W("simple", s2["start"] + 0.3, s2["start"] + 0.7),
      W("process.", s2["start"] + 0.7, s2["end"] - 0.02)]
(ws / "assets/voice/narration.words.json").write_text(json.dumps(tr))
r = compile_run(ws, "--apply", "--json")
check("manifest apply exits 0 (no data-anchor-end needed)", r.returncode == 0,
      r.stdout + r.stderr)
out = json.loads(r.stdout)
check("boundaries come from manifest", abs(out["boundaries"][0] - s1["cut"]) < 0.001
      and abs(out["boundaries"][1] - s2["cut"]) < 0.01, str(out["boundaries"]))
html = (ws / "index.html").read_text()
cues = json.loads(get_attr([t for t in html.split("<div") if 'id="s2"' in t][0]
                           .replace("’", "'"), "data-variable-values"))["chipCues"]
check("cues resolve inside the manifest window", cues.split(",")[0] != "9", cues)
r = compile_run(ws, "--check")
check("manifest mode idempotent", r.returncode == 0, r.stdout)
check("no padding ever in manifest mode",
      not (ws / "assets/voice/narration.pre-pad.wav").exists())

# scene-count mismatch is fatal
mani["scenes"] = mani["scenes"][:1]
(ws / "assets/voice/scene-times.json").write_text(json.dumps(mani))
r = compile_run(ws, "--check")
check("manifest/scene-count mismatch is fatal",
      r.returncode == 1 and "re-run" in r.stdout, r.stdout)

# missing data-narration on one scene is fatal for synth
html2 = (ws / "index.html").read_text().replace(
    f'data-narration="Do you care?" ', "")
(ws / "index.html").write_text(html2)
r = subprocess.run([sys.executable, str(PIPE / "synth_narration.py"), str(ws)],
                   capture_output=True, text=True)
check("missing data-narration is fatal", r.returncode == 1
      and "missing data-narration" in r.stdout, r.stdout)

print("== unit: in-scene gap compressor (PCM math) ==")
# The Oxana defect (2026-07-28): 0.98-1.26s of REAL silence at sentence/clause
# boundaries INSIDE a scene, which nothing governed — scene-boundary air is the
# only silence the pipeline ever managed. Synthetic clip, exact frame counts:
# the compressor's whole job is to remove samples and shift the timestamps that
# describe them by the identical amount, so the two can never disagree.
RATE = 24000


def frames(spec, rate=RATE):
    """[(seconds, constant int16 value), ...] -> mono frame array."""
    a = _array.array("h")
    for secs, val in spec:
        a.extend([val] * int(round(secs * rate)))
    return a


# 0.2s room tone | 0.3s word A | 1.2s room tone | 0.3s word B | 0.2s room tone.
# Room tone rather than digital zero so the declick fade is observable.
clip = frames([(0.2, 200), (0.3, 8000), (1.2, 200), (0.3, 8000), (0.2, 200)])
gap_words = [{"text": "A", "start": 0.2, "end": 0.5},
             {"text": "B", "start": 1.7, "end": 2.0}]
out, new_words, removed, n_cuts = sn.compress_gaps(clip, gap_words, RATE, 1, 0.5)
check("one over-cap gap -> one cut", n_cuts == 1, str(n_cuts))
check("removed == gap - cap (1.2 - 0.5)", abs(removed - 0.7) < 1e-9, str(removed))
check("output shorter by exactly the removed frames",
      len(out) == len(clip) - int(0.7 * RATE), f"{len(out)} vs {len(clip)}")
check("caller's clip is not mutated",
      len(clip) == int(2.2 * RATE) and clip[0] == 200 and max(clip) == 8000)
check("word before the cut does not move",
      new_words[0]["start"] == 0.2 and new_words[0]["end"] == 0.5, str(new_words[0]))
check("word after the cut shifts back by the removed duration",
      abs(new_words[1]["start"] - 1.0) < 1e-9 and abs(new_words[1]["end"] - 1.3) < 1e-9,
      str(new_words[1]))
check("surviving gap == the cap exactly",
      abs((new_words[1]["start"] - new_words[0]["end"]) - 0.5) < 1e-9)
check("audio and words still agree: word B's start indexes voiced samples",
      out[int(new_words[1]["start"] * RATE) + 10] == 8000,
      str(out[int(new_words[1]["start"] * RATE) + 10]))
splice = int(round((0.5 + 0.25) * RATE))  # cap/2 of decay kept after word A
check("splice is declicked on both sides",
      abs(out[splice - 1]) < 20 and abs(out[splice]) < 20,
      f"{out[splice - 1]} -> {out[splice]}")
check("fade is local — room tone untouched away from the splice",
      out[splice - 3000] == 200 and out[splice + 3000] == 200)
out2, words2, removed2, cuts2 = sn.compress_gaps(clip, gap_words, RATE, 1, 0.5)
check("deterministic: same input -> byte-identical output",
      out2.tobytes() == out.tobytes() and words2 == new_words and removed2 == removed)

# Two over-cap gaps: the second word's shift must be CUMULATIVE, not per-gap.
clip3 = frames([(0.2, 200), (0.3, 8000), (1.2, 200), (0.3, 8000),
                (1.2, 200), (0.3, 8000), (0.2, 200)])
w3 = [{"text": "A", "start": 0.2, "end": 0.5}, {"text": "B", "start": 1.7, "end": 2.0},
      {"text": "C", "start": 3.2, "end": 3.5}]
out3, nw3, removed3, cuts3 = sn.compress_gaps(clip3, w3, RATE, 1, 0.5)
check("two over-cap gaps -> two cuts, 1.4s removed",
      cuts3 == 2 and abs(removed3 - 1.4) < 1e-9, f"{cuts3}/{removed3}")
check("third word shifts by BOTH removals",
      abs(nw3[2]["start"] - 1.8) < 1e-9 and abs(nw3[2]["end"] - 2.1) < 1e-9, str(nw3[2]))
check("output length matches the cumulative removal",
      len(out3) == len(clip3) - int(1.4 * RATE))

# Under the cap: nothing may be touched (identity, not a re-encode).
clip4 = frames([(0.2, 200), (0.3, 8000), (0.4, 200), (0.3, 8000)])
w4 = [{"text": "A", "start": 0.2, "end": 0.5}, {"text": "B", "start": 0.9, "end": 1.2}]
out4, nw4, removed4, cuts4 = sn.compress_gaps(clip4, w4, RATE, 1, 0.5)
check("gap at/under the cap is left alone", cuts4 == 0 and removed4 == 0.0
      and out4 is clip4 and nw4 is w4)
check("a single-word clip has no inter-word gap to cut",
      sn.compress_gaps(clip4, w4[:1], RATE, 1, 0.5)[3] == 0)

print("== e2e: gap compression through synth_narration + the preflight guard ==")
from preflight import INSCENE_GAP_FAIL, check_inscene_gaps


def write_wav(path, data, rate=RATE):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def make_gap_workspace():
    """Scene 1's clip carries a 1.25s pause between 'you' and 'care?' — the
    Oxana defect in miniature. Clips are pre-seeded with matching shas so the
    full trim/compress/concat path runs without invoking TTS."""
    if TMP.exists():
        shutil.rmtree(TMP)
    clips = TMP / "assets" / "voice" / "scenes"
    clips.mkdir(parents=True)
    texts = ["Do you care?", "A simple process."]
    write_wav(clips / "scene-01.wav",
              frames([(0.10, 0), (0.55, 8000), (1.20, 0), (0.45, 8000), (0.30, 0)]))
    write_wav(clips / "scene-02.wav",
              frames([(0.05, 0), (1.00, 8000), (0.20, 0)]))
    (clips / "scene-01.words.json").write_text(json.dumps([
        {"text": "Do", "start": 0.15, "end": 0.35},
        {"text": "you", "start": 0.40, "end": 0.60},
        {"text": "care?", "start": 1.85, "end": 2.25}]))  # 1.25s in-scene hole
    (clips / "scene-02.words.json").write_text(json.dumps([
        {"text": "A", "start": 0.10, "end": 0.30},
        {"text": "simple", "start": 0.35, "end": 0.70},
        {"text": "process.", "start": 0.75, "end": 1.00}]))
    entries = []
    provider, speed = sn.DEFAULT_PROVIDER, sn.DEFAULT_SPEED
    voice = sn.DEFAULT_VOICE[provider]
    for i, t in enumerate(texts, start=1):
        sha = hashlib.sha1(f"{provider}|{voice}|{speed}|{t}".encode()).hexdigest()[:16]
        entries.append({"clip": f"scenes/scene-{i:02d}.wav", "sha": sha})
    (TMP / "assets" / "voice" / "scene-times.json").write_text(
        json.dumps({"scenes": entries}))
    (TMP / "index.html").write_text(f"""<!DOCTYPE html>
<html><body>
<div data-hf-id="hf-root1" id="root" data-composition-id="main" data-start="0" data-duration="10" data-width="1920" data-height="1080">
<div data-hf-id="hf-s1" class="clip" id="s1" data-composition-id="scla-title" data-composition-src="compositions/scla-title.html" data-variable-values='{{"title":"x","theme":"summit","sceneDuration":"1"}}' data-narration="{texts[0]}" data-start="0" data-duration="1" data-track-index="1"></div>
<div data-hf-id="hf-s2" class="clip" id="s2" data-composition-id="scla-chips" data-composition-src="compositions/scla-chips.html" data-variable-values='{{"chips":"One,Two","chipCues":"9,9","theme":"summit","sceneDuration":"1"}}' data-narration="{texts[1]}" data-start="1" data-duration="2" data-track-index="1"></div>
<audio data-hf-id="hf-aud" id="narration" class="clip" src="assets/voice/narration.wav" data-start="0" data-duration="3.5" data-track-index="2"></audio>
</div></body></html>""")
    return TMP


ws = make_gap_workspace()
r = subprocess.run([sys.executable, str(PIPE / "synth_narration.py"), str(ws)],
                   capture_output=True, text=True)
check("synth with a gappy clip exits 0", r.returncode == 0, r.stdout + r.stderr)
check("per-scene trim summary printed",
      "scene-01: trimmed 0.75s across 1 gap" in r.stdout, r.stdout)
check("clean scene reports nothing", "scene-02: trimmed" not in r.stdout, r.stdout)
gmani = json.loads((ws / "assets/voice/scene-times.json").read_text())
check("manifest records the cap and the total removed",
      gmani["max_inscene_gap"] == sn.MAX_INSCENE_GAP
      and abs(gmani["gap_trimmed"] - 0.75) < 0.002, str(gmani.get("gap_trimmed")))
g1, g2 = gmani["scenes"]
gwords = json.loads((ws / "assets/voice/narration.words.json").read_text())
inscene = [b["start"] - a["end"] for a, b in zip(gwords, gwords[1:])
           if b["start"] <= g1["end"] + 0.002]
check("no in-scene gap survives above the cap",
      max(inscene) <= sn.MAX_INSCENE_GAP + 0.002, str(inscene))
check("the compressed gap sits AT the cap (nothing else was touched)",
      abs(max(inscene) - sn.MAX_INSCENE_GAP) < 0.005, str(inscene))
with wave.open(str(ws / "assets/voice/narration.wav"), "rb") as wv:
    gtotal = wv.getnframes() / wv.getframerate()
check("wav length still == manifest audio_end", abs(gtotal - gmani["audio_end"]) < 0.002,
      f"{gtotal} vs {gmani['audio_end']}")
check("last word ends inside its scene's audio",
      gwords[-1]["end"] <= g2["end"] + 0.002, f"{gwords[-1]} vs {g2}")

sec = check_inscene_gaps(ws)
check("preflight guard passes on compressed output", sec["pass"], sec["output"])
gp = ws / "assets/voice/narration.words.json"
gp.write_text(json.dumps([
    W("Do", g1["start"] + 0.05, g1["start"] + 0.20),
    W("care?", g1["start"] + 1.25, g1["start"] + 1.45)]))
sec = check_inscene_gaps(ws)
check(f"guard FAILs an in-scene gap over {INSCENE_GAP_FAIL}s", not sec["pass"], sec["output"])
check("guard names the offending words", "'Do'" in sec["output"]
      and "care?" in sec["output"], sec["output"])
gp.write_text(json.dumps([
    W("Do", g1["start"] + 0.05, g1["start"] + 0.20),
    W("care?", g2["start"] + 0.05, g2["start"] + 0.20)]))
sec = check_inscene_gaps(ws)
check("guard ignores the SCENE-BOUNDARY gap (air + lead is deliberate)",
      sec["pass"], sec["output"])
gp.unlink()
sec = check_inscene_gaps(ws)
check("guard skips (WARN, not FAIL) with no words file",
      sec["pass"] and "SKIPPED" in sec["output"], sec["output"])

print(f"\n{PASS} passed, {FAIL} failed  (run_tests.py's own cases)")

# The sibling test_*.py files used to be runnable but unrun: nothing invoked
# them, so `python3 tests/run_tests.py` reported green while test_variety.py,
# test_gates.py, test_stem.py, test_build_index.py and test_script_match.py were
# never executed by anything, in CI or out. A test that nothing runs is a
# convention, not a mechanism (repo-hygiene STD-35). One command now runs them
# all, and scripts/lint-refs.sh runs that command.
SUITE_FAIL = 0
for path in sorted(Path(__file__).resolve().parent.glob("test_*.py")):
    print(f"\n== {path.name} ==")
    r = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    tail = [ln for ln in r.stdout.strip().splitlines() if ln.strip()]
    print("\n".join(tail[-3:]) if tail else "(no output)")
    if r.returncode != 0:
        SUITE_FAIL += 1
        print(r.stdout[-2000:])
        print(r.stderr[-1000:], file=sys.stderr)

if SUITE_FAIL:
    print(f"\n{SUITE_FAIL} sibling suite(s) FAILED")
sys.exit(1 if (FAIL or SUITE_FAIL) else 0)
