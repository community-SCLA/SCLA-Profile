#!/usr/bin/env python3
"""test_diversity.py — firing proofs for check_diversity.py, the pre-render
freeze gate, and for hfp_common.load_words, the word-timing adapter it and
check_presence both read.

Same discipline as test_ink.py: stills are GENERATED, not stored, so the fixture
has no font or asset dependency. A comb of 1px lines on navy is guaranteed local
contrast; a comb drawn at the same place twice is a pixel-identical frame, which
is exactly what a frozen video looks like to this gate.

The load_words cases matter as much as the freeze cases. check_presence read only
the two FLAT word files, so on a freeform build (per-beat wavs + audio_meta.json)
it found none, and its `not words` fallback silently graded every static run as
if narration ran wall to wall — the gate ran stricter than designed and could not
report why. The per-beat offset case below is the proof that shape now loads,
and the silent-hold case is the proof the strictness is actually gone.

Run:  python3 tests/test_diversity.py   (exit 0 = all pass)
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))

from PIL import Image, ImageDraw

import check_diversity
from check_diversity import MAX_SAMPLE_GAP
from check_presence import STAGNANT_FAIL
from hfp_common import load_words, speech_in

sys.path.insert(0, str(Path(__file__).resolve().parent))
from firing import fires as _fires

PASS = FAIL = 0
TMP = Path(tempfile.gettempdir()) / "scla-diversity-tests"
NAVY = (10, 30, 47)
W, H = 480, 270
STEP = MAX_SAMPLE_GAP  # the densest legal grid


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def fires(checker, rule, label, cond, detail=""):
    return _fires(check, checker, rule, label, cond, detail)


def rules_of(items):
    return {getattr(i, "rule_id", "?") for i in (items or [])}


def stills(name, specs, step=STEP):
    """specs is [(offset_x, beat_or_None)] — one still per grid slot. Two slots
    sharing an offset render identical frames (a frozen picture)."""
    d = TMP / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    for i, (off, beat) in enumerate(specs):
        img = Image.new("RGB", (W, H), NAVY)
        draw = ImageDraw.Draw(img)
        for x in range(60 + off, 60 + off + 120, 3):
            draw.line((x, 90, x, 150), fill=(255, 255, 255))
        t = i * step
        fn = (f"f{t:07.2f}s_{beat}_mid.png" if beat
              else f"frame-{i:03d}-at-{t:.2f}s.png")
        img.save(d / fn)
    return d


def workspace(name, words, clip="s01", audio_start=10.0):
    """A freeform-shaped workspace: audio_meta.json (per-beat, clip-relative
    word times) + timing.json (the per-beat offset those times need)."""
    ws = TMP / name
    shutil.rmtree(ws, ignore_errors=True)
    ws.mkdir(parents=True)
    (ws / "audio_meta.json").write_text(json.dumps({
        "voices": [{"id": clip, "duration_s": 30.0, "words": words}]}))
    (ws / "timing.json").write_text(json.dumps({
        "total": 60.0, "rows": [{"id": clip, "audio_start": audio_start,
                                 "vis_start": audio_start - 0.2,
                                 "vis_dur": 30.0}]}))
    return ws


# ---------------------------------------------------------------------------
# 1. A frozen run fires; a moving one does not.
n = int(STAGNANT_FAIL / STEP) + 2          # a run comfortably past the floor
frozen = stills("frozen", [(0, None)] * n + [(200, None), (260, None)])
report, problems, _ = check_diversity.check(frozen)
fires("check_diversity", "static-span",
      f"{(n - 1) * STEP:.1f}s of pixel-identical stills fires static-span",
      "static-span" in rules_of(problems), str(problems))

moving = stills("moving", [(i * 25, None) for i in range(n + 2)])
report, problems, _ = check_diversity.check(moving)
check("stills that change every slot pass",
      report is not None and not problems, str(problems))

# ---------------------------------------------------------------------------
# 2. A grid too sparse to see a STAGNANT_FAIL freeze must say so, not pass.
sparse = stills("sparse", [(i * 25, None) for i in range(5)],
                step=MAX_SAMPLE_GAP * 2)
report, problems, _ = check_diversity.check(sparse)
fires("check_diversity", "grid-too-sparse",
      "a grid coarser than the freeze it must detect fires grid-too-sparse",
      "grid-too-sparse" in rules_of(problems), str(problems))

# ---------------------------------------------------------------------------
# 3. Nothing gradeable is a failure, never a pass.
one = stills("one", [(0, None)])
report, problems, _ = check_diversity.check(one)
fires("check_diversity", "nothing-graded",
      "a single still returns report=None so the caller must fail",
      report is None and "nothing-graded" in rules_of(problems),
      f"report={report} problems={problems}")

empty = TMP / "empty"
shutil.rmtree(empty, ignore_errors=True)
empty.mkdir(parents=True)
report, problems, _ = check_diversity.check(empty)
check("an empty stills dir returns report=None too",
      report is None and problems, f"report={report}")

# ---------------------------------------------------------------------------
# 4. Twin beats — advisory, and only graded when stills carry beat labels.
twins = stills("twins", [(0, "s01"), (0, "s01"), (0, "s02"), (0, "s02"),
                         (240, "s03"), (240, "s03")])
report, problems, warns = check_diversity.check(twins)
fires("check_diversity", "twin-beats",
      "two consecutive beats drawing near-identical frames warn as twin-beats",
      "twin-beats" in rules_of(warns), str(warns))
check("…and twin-beats WARNS rather than blocking (STD-38, uncalibrated)",
      "twin-beats" not in rules_of(problems), str(problems))
check("beat-labelled stills report twins_graded=True",
      report and report.get("twins_graded"), str(report))

report, _, warns = check_diversity.check(moving)
check("unlabelled stills report the twin rule graded NOTHING, not clean",
      report and not report["twins_graded"]
      and "twin-beats-not-graded" in rules_of(warns), str(warns))

# ---------------------------------------------------------------------------
# 5. load_words: the freeform per-beat shape, offset onto the real timeline.
ws = workspace("ws-freeform", [{"text": "hello", "start": 0.5, "end": 0.9},
                               {"text": "there", "start": 1.0, "end": 1.4}])
words = load_words(ws)
check("audio_meta.json + timing.json load as flat words",
      len(words) == 2, str(words))
check("…each offset by its beat's audio_start (0.5 + 10.0 = 10.5)",
      words and abs(words[0]["start"] - 10.5) < 1e-6, str(words[:1]))
check("speech_in sees them on the absolute timeline",
      speech_in(words, 10.4, 10.6) and not speech_in(words, 0.0, 5.0),
      str(words))

flat = TMP / "ws-flat" / "assets" / "voice"
flat.mkdir(parents=True, exist_ok=True)
(flat / "narration.words.json").write_text(
    json.dumps([{"text": "x", "start": 1.0, "end": 2.0}]))
check("the flat narration.words.json shape still wins when present",
      len(load_words(flat.parents[1])) == 1, str(load_words(flat.parents[1])))
check("a workspace with no word source returns [] (caller decides meaning)",
      load_words(TMP / "nope") == [], "expected []")

# ---------------------------------------------------------------------------
# 6. A frozen span during SILENCE is not a defect — the whole point of the
#    adapter. Same stills, same freeze, words moved off the span.
quiet = workspace("ws-quiet", [{"text": "w", "start": 0.1, "end": 0.2}])
_, problems, _ = check_diversity.check(frozen, ws=quiet)
check("a frozen span with no narration over it does NOT fire",
      "static-span" not in rules_of(problems), str(problems))

loud = workspace("ws-loud", [{"text": "a", "start": i * 0.4, "end": i * 0.4 + 0.3}
                             for i in range(60)], audio_start=0.0)
_, problems, _ = check_diversity.check(frozen, ws=loud)
check("…and the same span WITH narration over it does fire",
      "static-span" in rules_of(problems), str(problems))

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
