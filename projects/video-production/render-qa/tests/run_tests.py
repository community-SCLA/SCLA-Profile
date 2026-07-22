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

PIPE = Path(__file__).resolve().parents[0].parent
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
check("final cut = end + final hold", abs(s2["cut"] - (s2["end"] + 1.1)) < 0.001, f"{s2}")
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

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
