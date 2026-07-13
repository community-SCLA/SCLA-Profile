#!/usr/bin/env python3
"""Synthetic-fixture tests for preflight.py's script-fidelity gate (check 5).

Attacks the failure modes the gate exists for: a TTS misread sailing through
(dropped sentence, wrong text), plus the noise it must tolerate (whisper
small.en's ~1-in-360 mishears, dash-compound tokens like 'buzzwords—just').
No TTS, whisper, or render is run — transcripts are hand-built JSON.

Run:  python3 tests/test_script_match.py   (exit 0 = all pass)
"""

import json
import shutil
import sys
from pathlib import Path

PIPE = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(PIPE))
from preflight import (RATE_FAIL, RATE_WARN, RUN_FAIL, check_script_match,
                       diff_script_transcript, locate_script,
                       tokenize_for_diff)

TMP = Path("/tmp/claude-1000/-workspaces-SCLA-Profile/a8d1e2cc-c774-48f0-990a-1419eccd5a79/scratchpad/script-match-tests")

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


def make_fixture(stem, script_text, transcript_words):
    """Workspace named <stem> + a lesson-scripts tree the stem resolves into."""
    if TMP.exists():
        shutil.rmtree(TMP)
    ws = TMP / "renders" / stem
    (ws / "assets" / "voice").mkdir(parents=True)
    t, words = 0.0, []
    for w in transcript_words:
        words.append({"text": w, "start": round(t, 2), "end": round(t + 0.3, 2)})
        t += 0.35
    (ws / "assets" / "voice" / "transcript.json").write_text(json.dumps(words))
    slug = stem.split("_")[1]
    scripts_root = TMP / "lesson-scripts"
    (scripts_root / slug).mkdir(parents=True)
    (scripts_root / slug / f"{stem}.txt").write_text(script_text)
    return ws, scripts_root


# A ~360-word approved script: 12 sentences x 30 words, unique-ish tokens so
# the diff can't accidentally resync on repeated filler.
SENTENCES = [
    " ".join(f"s{si}word{wi}" for wi in range(29)) + f" close{si}."
    for si in range(12)
]
SCRIPT = " ".join(SENTENCES)
SCRIPT_WORDS = SCRIPT.split()
STEM = "brand-you-intro_early-career-boost_2026-07-13"

print("== unit: tokenization ==")
check("dash compound splits (em dash, no spaces)",
      tokenize_for_diff("buzzwords—just noise") == ["buzzwords", "just", "noise"])
check("en dash and slash split too",
      tokenize_for_diff("3–5 years, on/off") == ["3", "5", "years", "onoff"]
      or tokenize_for_diff("3–5 years, on/off") == ["3", "5", "years", "on", "off"])
check("punctuation and case normalize",
      tokenize_for_diff("It’s DONE.") == tokenize_for_diff("its done"))
check("whitespace collapses",
      tokenize_for_diff("a  b\n\tc") == ["a", "b", "c"])

print("== unit: diff mechanics ==")
rate, run, segs = diff_script_transcript(["a", "b", "c", "d"], ["a", "b", "c", "d"])
check("identical lists: zero rate, zero run, no segments",
      rate == 0 and run == 0 and not segs)
rate, run, segs = diff_script_transcript(["a", "b", "c", "d"], ["a", "x", "c", "d"])
check("single substitution counted once", rate == 0.25 and run == 1 and len(segs) == 1)
check("segment shows both sides", "[b]" in segs[0] and "[x]" in segs[0])
rate, run, segs = diff_script_transcript(list("abcdefgh"), list("abgh"))
check("deletion run length counts dropped words", run == 4)

print("== unit: script location from workspace stem ==")
ws, root = make_fixture(STEM, SCRIPT, SCRIPT_WORDS)
found = locate_script(ws, scripts_root=root)
check("stem resolves to lesson-scripts/<slug>/<stem>.txt",
      found is not None and found.name == f"{STEM}.txt"
      and found.parent.name == "early-career-boost")
check("malformed stem (no 3 parts) returns None",
      locate_script(ws.parent / "just-one-part", scripts_root=root) is None)
refined_dir = root / "early-career-boost" / "refined"
refined_dir.mkdir()
(refined_dir / f"{STEM}.txt").write_text(SCRIPT)
check("refined/ copy wins over program root",
      locate_script(ws, scripts_root=root).parent.name == "refined")
(refined_dir / f"{STEM}.txt").unlink()

print("== gate: clean match passes ==")
sec = check_script_match(ws, scripts_root=root)
check("clean match: PASS", sec["pass"], sec["output"])
check("clean match: rate 0.00% reported", "0.00%" in sec["output"])
check("clean match: no mismatch warnings", "WARN @" not in sec["output"])

print("== gate: 1-in-360 mishear passes with warning ==")
heard = list(SCRIPT_WORDS)
heard[100] = "mishear"  # one whisper flub in ~360 words
ws, root = make_fixture(STEM, SCRIPT, heard)
sec = check_script_match(ws, scripts_root=root)
check("noise-floor mishear: PASS", sec["pass"], sec["output"])
check("noise-floor mishear: diff printed as warning",
      "WARN @" in sec["output"] and "mishear" in sec["output"])

print("== gate: dropped sentence fails ==")
heard = SCRIPT_WORDS[:60] + SCRIPT_WORDS[90:]  # sentence 3 never spoken
ws, root = make_fixture(STEM, SCRIPT, heard)
sec = check_script_match(ws, scripts_root=root)
check("dropped sentence: FAIL", not sec["pass"], sec["output"])
check("dropped sentence: run rule named",
      "consecutive mismatched words" in sec["output"])

print("== gate: misread sentence fails ==")
heard = list(SCRIPT_WORDS)
heard[150:156] = ["totally", "different", "words", "were", "spoken", "here"]
ws, root = make_fixture(STEM, SCRIPT, heard)
sec = check_script_match(ws, scripts_root=root)
check("misread sentence (6-word run): FAIL", not sec["pass"], sec["output"])

print("== gate: high scatter rate fails ==")
heard = list(SCRIPT_WORDS)
for i in range(0, 330, 30):  # 11 scattered flubs > 2%, every run stays short
    heard[i] = f"flub{i}"
ws, root = make_fixture(STEM, SCRIPT, heard)
sec = check_script_match(ws, scripts_root=root)
check("scattered >2% mismatch: FAIL", not sec["pass"], sec["output"])
check("scattered >2%: rate rule named", "mismatch rate" in sec["output"]
      and "does not match" in sec["output"])

print("== gate: middle zone passes with elevated warning ==")
heard = list(SCRIPT_WORDS)
for i in (30, 120, 210, 300):  # 4/360 ≈ 1.1%: between warn and fail
    heard[i] = f"flub{i}"
ws, root = make_fixture(STEM, SCRIPT, heard)
sec = check_script_match(ws, scripts_root=root)
check("middle zone: PASS", sec["pass"], sec["output"])
check("middle zone: noise-floor warning printed",
      "above the whisper" in sec["output"])

print("== gate: dash compounds don't count as misses ==")
ws, root = make_fixture(STEM, "No buzzwords — just plain talk.",
                        ["No", "buzzwords—just", "plain", "talk."])
sec = check_script_match(ws, scripts_root=root)
check("dash compound normalized on both sides: PASS", sec["pass"], sec["output"])

print("== gate: missing script warns and skips ==")
ws, root = make_fixture(STEM, SCRIPT, SCRIPT_WORDS)
(root / "early-career-boost" / f"{STEM}.txt").unlink()
sec = check_script_match(ws, scripts_root=root)
check("missing script: gate not failed", sec["pass"], sec["output"])
check("missing script: loud WARN + SKIPPED",
      "WARN" in sec["output"] and "SKIPPED" in sec["output"])

print("== gate: explicit --script override ==")
ws, root = make_fixture(STEM, SCRIPT, SCRIPT_WORDS)
override = TMP / "elsewhere.txt"
override.write_text(SCRIPT)
sec = check_script_match(ws, script_path=override, scripts_root=root / "nonexistent")
check("--script override used: PASS", sec["pass"], sec["output"])
sec = check_script_match(ws, script_path=TMP / "missing.txt", scripts_root=root)
check("--script pointing at a missing file: FAIL (explicit path must exist)",
      not sec["pass"], sec["output"])

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
