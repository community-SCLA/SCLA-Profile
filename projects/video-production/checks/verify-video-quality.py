#!/usr/bin/env python3
"""Owner-feedback quality gate for a rendered lesson video (stage 5).

    python3 verify-video-quality.py --dir <dir-with-render,audio,workspace>

Every threshold below exists because the owner saw the defect on screen
(2026-08-03 review of build-direction-before-you-build-a-plan_early-career-boost):
clicking in the narration, dead-air gaps between sentences, a black-and-white
video from a blue-and-gold brand, body text below the 40px floor and not bold.
A preference is not real until it is a gate — this file is the gate.

Gates (all must pass; each prints its measurements):
  render    1920x1080 MP4 with audio, video covers the narration
  frames    no featureless content run >= 0.25s anywhere, graded at 20fps.
            Ink = pixels deviating >30 from BOTH their row and column median,
            so a departing flat band counts as empty (the per-frame-median
            version scored a navy stripe on paper as 15% ink and passed a
            hole the final-verify lane caught at 00:03); footer furniture
            never excuses an empty frame
  palette   near-black <= 12% of pixels video-wide; full-dark frames <= 10%
            of samples; brand blue >= 3%; gold >= 0.5%; >= 60% of frames
            carry visible blue/gold accent
  silence   no interior dead-air stretch >= 0.9s (a BGM bed under the
            narration is the accepted fix for TTS sentence gaps)
  clicks    <= 3 high-frequency ticks audible inside quiet stretches of the
            whole mix (the HeyGen voice ships ~59 mouth-tick artifacts per
            2.5min; a noise-gated narration under a music bed passes, raw
            narration alone does not — adeclick provably does NOT fix these)
  type      workspace source declares no font-size under 40px and no
            font-weight under 700 (exempt with /* text-floor-exempt: why */
            or /* weight-exempt: why */ on the same or preceding line)

Exit 0 only when every gate passes.
"""
import argparse
import array
import json
import re
import subprocess
import sys
from pathlib import Path

# --- thresholds (owner review 2026-08-03; measured on the rejected render:
#     dark 26.4%, blue 0.6%, gold 0.0%, 4 gaps >= 1.0s, click clusters at
#     0:26 / 1:11 / 1:29 / 2:03-2:08 — every gate below fails that file) ---
DARK_SHARE_MAX = 0.12       # video-wide near-black pixel share
DARK_FRAME_SHARE_MAX = 0.10 # share of sampled frames that are >60% near-black
BLUE_SHARE_MIN = 0.03       # video-wide brand-blue pixel share
GOLD_SHARE_MIN = 0.005      # video-wide gold pixel share
ACCENT_FRAME_MIN = 0.60     # share of frames with >=0.5% blue+gold pixels
SILENCE_DB = "-45dB"
SILENCE_MAX_S = 0.9
CLICK_HF_RMS = 250          # 20ms high-passed (6kHz) RMS that reads as a tick
CLICK_QUIET_RMS = 1200      # full-band RMS below which the tick is exposed
CLICK_TICKS_MAX = 3
FONT_PX_MIN = 40
FONT_WEIGHT_MIN = 700
BLANK_INK_SHARE = 0.0002    # content-region ink share below which a frame is featureless — essentially zero; deliberately spare transition frames (a lone rule mid-seam, ~0.1%) are content, a flat field is not

fails = []


def gate(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'} [{name}]: {detail}")
    if not ok:
        fails.append(name)


def run(cmd):
    return subprocess.run(cmd, capture_output=True)


def ffprobe_json(path):
    p = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", str(path)])
    return json.loads(p.stdout) if p.returncode == 0 else None


def newest_render(d):
    r = sorted((d / "render").glob("*_20??-??-??.mp4")) if (d / "render").is_dir() else []
    return r[-1] if r else None


def check_render(mp4, audio_dur):
    meta = ffprobe_json(mp4)
    if not meta:
        gate("render", False, f"ffprobe cannot read {mp4}")
        return None
    v = [s for s in meta["streams"] if s["codec_type"] == "video"]
    au = [s for s in meta["streams"] if s["codec_type"] == "audio"]
    dur = float(meta["format"]["duration"])
    ok = bool(v) and bool(au) and (v[0]["width"], v[0]["height"]) == (1920, 1080) \
        and (audio_dur is None or dur >= audio_dur - 1.0)
    gate("render", ok,
         f"{mp4.name}: {v[0]['width']}x{v[0]['height'] if v else '?'} "
         f"{dur:.1f}s, audio stream {'present' if au else 'MISSING'}, "
         f"narration {audio_dur:.1f}s" if v else f"{mp4.name}: no video stream")
    return dur




def check_frames_and_palette(mp4):
    """One 4fps decode grades both gates, vectorized.

    frames: a frame is content-blank when <0.3% of its content-region pixels
    (above the footer band, y<960 full-scale) differ from the region's median
    color — footer furniture (rail, brandline) does not excuse an empty frame,
    which is how the 2026-08-03 rebuild's 0.7-0.9s white handoffs passed a
    whole-frame stddev test. Only runs >= 0.5s (2+ consecutive samples) fail:
    sub-0.2s transition dips are legitimate.
    """
    import numpy as np
    FPS = 20
    raw = run(["ffmpeg", "-v", "error", "-i", str(mp4),
               "-vf", f"fps={FPS},scale=192:108", "-f", "rawvideo",
               "-pix_fmt", "rgb24", "-"]).stdout
    n = len(raw) // (192 * 108 * 3)
    if not n:
        gate("frames", False, "could not decode frames")
        gate("palette", False, "no frames to grade")
        return
    a = np.frombuffer(raw[:n * 192 * 108 * 3], np.uint8).reshape(n, 108, 192, 3)
    a16 = a.astype(np.int16)
    r, g, b = a16[..., 0], a16[..., 1], a16[..., 2]
    dark = (r < 60) & (g < 60) & (b < 70)
    blue = ~dark & (b > 110) & (b > r + 30) & (g > 60)
    gold = ~dark & ~blue & (r > 180) & (g > 130) & (b < 110)

    content = a16[:, :96, :, :]                      # y<960 at full scale
    row_med = np.median(content, axis=2)             # (n, 96, 3)
    col_med = np.median(content, axis=1)             # (n, 192, 3)
    dev_row = (np.abs(content - row_med[:, :, None, :]) > 30).any(axis=3)
    dev_col = (np.abs(content - col_med[:, None, :, :]) > 30).any(axis=3)
    ink = dev_row & dev_col                          # deviates from BOTH
    ink_share = ink.mean(axis=(1, 2))
    blank_mask = ink_share < BLANK_INK_SHARE
    runs = []
    i = 0
    while i < n:
        if blank_mask[i]:
            j = i
            while j < n and blank_mask[j]:
                j += 1
            if j - i >= 5:                           # >= 0.25s at 20fps
                runs.append((round(i / FPS, 2), round((j - i) / FPS, 2)))
            i = j
        else:
            i += 1
    gate("frames", not runs,
         f"{n} samples at {FPS}fps; featureless content runs (start_s, dur_s): {runs}"
         if runs else f"{n} samples at {FPS}fps, no featureless content run >= 0.25s")

    px_per, nf = 192 * 108, n
    d = dark.mean()
    bl = blue.mean()
    go = gold.mean()
    df = (dark.mean(axis=(1, 2)) > 0.60).mean()
    af = ((blue | gold).mean(axis=(1, 2)) >= 0.005).mean()
    ok = d <= DARK_SHARE_MAX and df <= DARK_FRAME_SHARE_MAX \
        and bl >= BLUE_SHARE_MIN and go >= GOLD_SHARE_MIN and af >= ACCENT_FRAME_MIN
    gate("palette", ok,
         f"near-black {d:.1%} (max {DARK_SHARE_MAX:.0%}), dark frames {df:.1%} "
         f"(max {DARK_FRAME_SHARE_MAX:.0%}), blue {bl:.1%} (min {BLUE_SHARE_MIN:.0%}), "
         f"gold {go:.2%} (min {GOLD_SHARE_MIN:.1%}), frames with accent {af:.0%} "
         f"(min {ACCENT_FRAME_MIN:.0%})")


def check_silence(mp4, dur):
    p = subprocess.run(
        ["ffmpeg", "-i", str(mp4), "-af",
         f"silencedetect=noise={SILENCE_DB}:d={SILENCE_MAX_S}", "-f", "null", "-"],
        capture_output=True, text=True)
    log = p.stdout + p.stderr
    gaps = []
    for m in re.finditer(r"silence_start: ([\d.]+).*?silence_duration: ([\d.]+)",
                         log, re.S):
        start, d = float(m.group(1)), float(m.group(2))
        if start > 1.0 and (dur is None or start + d < dur - 1.5):
            gaps.append((round(start, 1), round(d, 2)))
    gate("silence", not gaps,
         f"interior dead-air >= {SILENCE_MAX_S}s at {SILENCE_DB}: {gaps}" if gaps
         else f"no interior dead-air >= {SILENCE_MAX_S}s at {SILENCE_DB}")


def check_clicks(mp4):
    import math
    hf = array.array("h", run(
        ["ffmpeg", "-v", "error", "-i", str(mp4), "-af", "highpass=f=6000",
         "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]).stdout)
    fb = array.array("h", run(
        ["ffmpeg", "-v", "error", "-i", str(mp4),
         "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]).stdout)
    W = 320  # 20ms at 16kHz
    ticks, last = [], -1.0
    for i in range(0, min(len(hf), len(fb)) - W, W):
        h = math.sqrt(sum(x * x for x in hf[i:i + W]) / W)
        f = math.sqrt(sum(x * x for x in fb[i:i + W]) / W)
        if h > CLICK_HF_RMS and f < CLICK_QUIET_RMS:
            t = i / 16000.0
            if t - last > 0.3:
                ticks.append(round(t, 2))
            last = t
    gate("clicks", len(ticks) <= CLICK_TICKS_MAX,
         f"{len(ticks)} exposed high-frequency tick(s) in quiet stretches "
         f"(max {CLICK_TICKS_MAX}) at {ticks[:10]}")


EXEMPT_SIZE = re.compile(r"text-floor-exempt\s*:")
EXEMPT_WEIGHT = re.compile(r"weight-exempt\s*:")


def check_type(ws):
    if not ws.is_dir():
        gate("type", False, f"{ws} missing")
        return
    size_hits, weight_hits = [], []
    files = [f for f in ws.rglob("*")
             if f.suffix in (".html", ".css") and "node_modules" not in f.parts]
    for f in files:
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines):
            prev = lines[i - 1] if i else ""
            for m in re.finditer(
                    r"(?:font-size|--fs[\w-]*|--font[\w-]*|--text[\w-]*)\s*:"
                    r"\s*(\d+(?:\.\d+)?)(px|rem|em)", line):
                px = float(m.group(1)) * (1 if m.group(2) == "px" else 16)
                if px < FONT_PX_MIN and not (
                        EXEMPT_SIZE.search(line) or EXEMPT_SIZE.search(prev)):
                    size_hits.append(
                        f"{f.name}:{i + 1} {m.group(1)}{m.group(2)} (~{px:.0f}px)")
            for m in re.finditer(r"(?:font-weight|--fw[\w-]*)\s*:\s*(\d+)\b", line):
                if int(m.group(1)) < FONT_WEIGHT_MIN and not (
                        EXEMPT_WEIGHT.search(line) or EXEMPT_WEIGHT.search(prev)):
                    weight_hits.append(f"{f.name}:{i + 1} weight {m.group(1)}")
    ok = not size_hits and not weight_hits
    gate("type", ok,
         f"sizes under {FONT_PX_MIN}px: {size_hits or 'none'}; "
         f"weights under {FONT_WEIGHT_MIN}: {weight_hits or 'none'} "
         f"({len(files)} source file(s) scanned)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True,
                    help="lesson dir or exported pilot dir (render/, audio/, workspace/)")
    a = ap.parse_args()
    d = Path(a.dir)
    mp4 = newest_render(d)
    if not mp4:
        print(f"FAIL [render]: no dated MP4 under {d}/render/")
        return 1
    narr = d / "audio" / "narration.mp3"
    audio_dur = None
    if narr.exists():
        meta = ffprobe_json(narr)
        if meta:
            audio_dur = float(meta["format"]["duration"])
    dur = check_render(mp4, audio_dur)
    check_frames_and_palette(mp4)
    check_silence(mp4, dur)
    check_clicks(mp4)
    check_type(d / "workspace")
    if fails:
        print(f"FAIL — {len(fails)} gate(s) failed: {', '.join(fails)}")
        return 1
    print("PASS — all owner-feedback quality gates hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
