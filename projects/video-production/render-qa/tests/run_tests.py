#!/usr/bin/env python3
"""Adversarial fixture tests for the pipeline toolchain.

Each case is an attack on a known historical failure mode:
  duplicate words (the "process." bug, 2026-07-10), missing anchors, cue-count
  mismatches, unclaimed transcript tails, question air, padding idempotency,
  ASCII-apostrophe attribute injection, and the data-hf-id/id parsing trap.

Run:  python3 tests/run_tests.py   (exit 0 = all pass)
"""

import json
import math
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

PIPE = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(PIPE))
from hfp_common import MatchError, find_phrase, get_attr, json_attr, load_transcript

TMP = Path("/tmp/claude-1000/-workspaces-SCLA-Profile/2e9b86d8-f35e-486c-9a3a-d3eae4b18e6f/scratchpad/pipeline-tests")

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
check("question boundary gets 0.9s air", abs(float(s1) - (care_end + 0.9)) < 0.02,
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

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
