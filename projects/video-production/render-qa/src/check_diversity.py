#!/usr/bin/env python3
"""check_diversity.py — is the picture still moving, and do the beats differ?
Graded from snapshot stills, BEFORE the render is spent.

WHY THIS EXISTS. On the template lane `preflight.py` check 6 (`check_pacing`)
answers "how long does this scene sit with no visual event?" from the compiled
cue list — arithmetic on the plan, no browser, no render. That gate is SKIPPED
on the freeform lane and cannot be ported: its input is `data-variable-values`,
`build_index.py`'s private authoring protocol, and a freeform build's reveals
live in arbitrary GSAP JS, which this repo has already established cannot be
scanned reliably (it is why the ripple ban was re-specced as a pixel test,
PIPELINE-IF-ADOPTED §2). `check_variety` is skipped for the same class of
reason. Both deferrals named the same compensating control — "owned by the
per-video human preview" (decisions/log.md 2026-07-30) — and on 2026-07-31 that
control was measured against a real cut: a human watched
`build-direction-before-you-build-a-plan`, approved it, and `check_presence`
then found three spans of 5.0-5.5s of pixel-identical video under continuous
narration, two of them running straight THROUGH a scene cut.

The owner's approval was not the failure. "Did the picture hold perfectly still
for five seconds" is a stopwatch measurement, not a taste judgement, and it was
handed to the one instrument that cannot perform it. Monotony IS taste and stays
with the human; this gate takes back the measurement.

WHAT IT IS. `check_presence.py` already answers exactly this question — but only
AFTER a 19-minute render, from the delivered MP4. This is the same rule, the same
constants, the same run-of-identical-samples algorithm, run instead over the
stills `batch-precheck.sh` already captures minutes into the build. Post-render
`check_presence` stays authoritative; this is the cheap early copy.

  python3 check_diversity.py <stills-dir> [--ws <workspace>] [--json]
                             [--freeze-churn 0.002] [--twin-churn 0.004]

Exit: 0 clean · 1 finding · 2 bad args / nothing gradeable

CALIBRATION (2026-07-31, against the 78 real stills of the cut above). Churn is
the fraction of cells on a 240x135 luminance grid that move by more than 4/255.
Measured: a span `check_presence` independently called frozen reads **0.00000**;
the smallest genuine reveal in the same video reads **0.00852**. The floor is a
hard zero and the nearest true positive is 850x above it, so FREEZE_CHURN sits
at 0.002 — two orders of magnitude clear of a real change, and non-zero so
snapshot dither can never manufacture motion that is not there.

THE TWIN RULE REPORTS, IT DOES NOT BLOCK (STD-38). "These two beats look too
alike" needs a threshold calibrated against the owner's reference video, the way
`check_variety`'s thresholds are pinned to `what-makes-for-a-dream-job` — and no
clean reference stills exist on disk to calibrate against. Blocking on an
uncalibrated taste threshold is how a gate starts rejecting good work and gets
switched off. It warns until someone pins it; the freeze rule blocks today.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_presence import STAGNANT_FAIL, STAGNANT_WARN  # noqa: E402
from hfp_common import Finding, load_words, speech_in, typed  # noqa: E402

GRID = (240, 135)   # text survives this downscale; a 96x54 grid averages it away
DELTA = 4           # per-cell luminance move that counts as a change (0-255)
FREEZE_CHURN = 0.002
# BOTH criteria must hold for a pair to count as still, and this is the one that
# matters. Churn alone called 100.8s->108.0s frozen on the 2026-07-31 cut when
# check_presence — reading the same video at 2fps — had not: a single small
# element moved, which is 0.19% of the grid (under the churn floor) but 80/255
# on the cells it touched. Measured over all 63 adjacent pairs of that video,
# genuinely-static pairs top out at maxdiff 4 and the nearest real change reads
# 11, so 6 sits in the gap with margin on both sides. A gate that reports a
# freeze the authoritative gate cannot see would be retired within a week.
FREEZE_MAXDIFF = 6
TWIN_CHURN = 0.004

# SAMPLING MATH — why the grid is this dense and why the threshold is relaxed.
#
# A run of identical samples proves stillness only across the instants actually
# sampled, so a measured span is a LOWER BOUND: a true freeze of length L
# straddling the grid shows up as little as L - Δ. Grading a lower bound against
# STAGNANT_FAIL therefore misses real freezes — measured on the 2026-07-31 cut, a
# 5.0s freeze that check_presence fails read 4.8s on a 2.4s grid and would have
# passed here, which is the worst possible outcome: an early gate that says clean
# and a late gate that blocks after the render is spent.
#
# A freeze loses part of an interval at EACH end, so density is what buys
# accuracy — not a looser threshold. Both were tuned against the three spans
# check_presence fails on the 2026-07-31 cut, when STAGNANT_FAIL was still 5.0
# (it moved to 6.0 in BUILD-PLAN A1, 2026-08-04 — see check_presence.py). The
# Δ = FAIL/4 relationship below is what the formula still expresses; the worked
# numbers are the historical measurement that chose it, not a restatement at
# the new constant:
#     Δ = FAIL/3, threshold FAIL-Δ  -> the 5.0s freeze at 74.0s measured 3.32s
#                                      against 3.34s and was MISSED by 0.02s
#     Δ = FAIL/4, threshold FAIL-2Δ -> 11 violations where the MP4 has 3; every
#                                      2-interval run fires, which converts the
#                                      whole gray zone into failures
#     Δ = FAIL/4, threshold FAIL-Δ  -> all three fire, plus two 4.0-4.5s holds
#                                      that check_presence warns on. Adopted:
#                                      one interval is the mean overhang, and an
#                                      early gate should sit slightly hot — a
#                                      false stop costs a re-author, a miss costs
#                                      a 19-minute render and a blocked ship.
MAX_SAMPLE_GAP = STAGNANT_FAIL / 4.0

# Timestamps are read back out of filenames at 1/100s, so EVERY time comparison
# here carries that much slop and both of them bit during calibration: a perfect
# 1.25s grid measured 1.26s wide (33.125 and 34.375 round to 33.12 and 34.38) and
# fired grid-too-sparse, then the real 5.0s freeze at 74.0s measured 3.74s
# against a 3.75s threshold (78.125 and 74.375 round to 78.12 and 74.38) and was
# demoted to a warning by one hundredth of a second. Precision loss is a property
# of the input, so it is spent once, here, rather than rediscovered per rule.
TIME_EPS = 0.02

# f0074.64s_s15_mid.png  (verify_render.py's per-beat evidence)
# frame-00-at-9.46s.png  (the hyperframes `snapshot` CLI's own naming)
NAME_RES = (
    re.compile(r"^f(?P<t>\d+(?:\.\d+)?)s_(?P<beat>.+?)_(?P<pos>\w+)\.png$", re.I),
    re.compile(r"-at-(?P<t>\d+(?:\.\d+)?)s\.png$", re.I),
    re.compile(r"(?P<t>\d+(?:\.\d+)?)s\.png$", re.I),
)


def frame_time(name: str):
    """(t, beat) parsed from a still's filename, or (None, None)."""
    for rx in NAME_RES:
        m = rx.search(name)
        if m:
            try:
                return float(m.group("t")), (m.groupdict().get("beat"))
            except (ValueError, IndexError):
                continue
    return None, None


def cells(path: Path):
    return list(Image.open(path).convert("L")
                .resize(GRID, Image.BILINEAR).getdata())


def churn(a, b):
    """(fraction of cells moved more than DELTA, largest single-cell move)."""
    if len(a) != len(b):
        return 1.0, 255
    diffs = [abs(x - y) for x, y in zip(a, b)]
    return sum(1 for v in diffs if v > DELTA) / len(diffs), max(diffs)


def is_still(a, b, freeze_churn=FREEZE_CHURN) -> bool:
    """Nothing moved: almost no cells changed AND none changed much."""
    frac, peak = churn(a, b)
    return frac < freeze_churn and peak <= FREEZE_MAXDIFF


def load_frames(target: Path):
    """[(t, beat, path)] sorted by time — only stills whose name carries one."""
    files = sorted(target.glob("*.png")) if target.is_dir() else [target]
    out = []
    for p in files:
        t, beat = frame_time(p.name)
        if t is not None:
            out.append((t, beat, p))
    out.sort(key=lambda r: r[0])
    return out


def check(target: Path, ws=None, freeze_churn=FREEZE_CHURN,
          twin_churn=TWIN_CHURN):
    """(report, problems, warns). `report` is None when nothing was gradeable —
    the caller must FAIL on that, never pass. A gate that grades zero elements
    and exits 0 is the single most expensive bug shape in this pipeline's
    history (HANDOFF-agent-native-verdict §0)."""
    frames = load_frames(Path(target))
    if len(frames) < 2:
        return None, [Finding(
            "nothing-graded",
            f"{target}: {len(frames)} still(s) carry a parseable timestamp — "
            f"need at least 2. Nothing to grade is a failure, never a pass.")], []

    words = load_words(Path(ws)) if ws else []
    problems, warns = [], []

    if ws and not words:
        warns.append(Finding(
            "no-word-timings",
            f"{ws} yielded no narration word timings — every still span is "
            f"being graded as if narration ran wall to wall, so a deliberate "
            f"silent hold will read as a defect", "warn"))

    # 1. Is the grid dense enough to see a STAGNANT_FAIL freeze at all?
    gaps = [(b[0] - a[0], a[0], b[0]) for a, b in zip(frames, frames[1:])]
    worst = max(gaps, key=lambda g: g[0]) if gaps else (0.0, 0.0, 0.0)
    if worst[0] > MAX_SAMPLE_GAP + TIME_EPS:
        problems.append(Finding(
            "grid-too-sparse",
            f"stills are up to {worst[0]:.1f}s apart ({worst[1]:.1f}s → "
            f"{worst[2]:.1f}s); {MAX_SAMPLE_GAP:.1f}s is the widest grid that "
            f"can detect a {STAGNANT_FAIL:.1f}s freeze. Sample more densely — "
            f"this run cannot report the freeze rule either way."))

    px = {p: cells(p) for _, _, p in frames}

    # 2. Freeze: runs of adjacent low-churn pairs, same shape as
    #    check_presence's static_runs, from stills instead of MP4 samples.
    runs, run_start = [], None
    for (ta, _, pa), (tb, _, pb) in zip(frames, frames[1:]):
        still = is_still(px[pa], px[pb], freeze_churn)
        if still and run_start is None:
            run_start = ta
        if not still and run_start is not None:
            runs.append((run_start, ta))
            run_start = None
    if run_start is not None:
        runs.append((run_start, frames[-1][0]))

    # A measured span understates the truth by up to one sampling interval, so
    # both thresholds drop by exactly that much (see SAMPLING MATH above).
    slack = min(worst[0], MAX_SAMPLE_GAP)
    fail_at, warn_at = STAGNANT_FAIL - slack, STAGNANT_WARN - slack

    for a, b in runs:
        span = b - a
        if span < warn_at - TIME_EPS:
            continue
        if words and not speech_in(words, a, b):
            continue  # a deliberate silent hold is not a defect
        entry = (f"stills pixel-static {a:.1f}s → {b:.1f}s ({span:.1f}s)"
                 f"{' while narration speaks' if words else ''} — the picture "
                 f"is not moving. Re-author the beat; do NOT re-animate "
                 f"settled content (that motion is banned and check_motion "
                 f"will reject it).")
        if span >= fail_at - TIME_EPS:
            problems.append(Finding("static-span", entry))
        else:
            warns.append(Finding(
                "static-span", entry + f" [{STAGNANT_WARN:.0f}-"
                f"{STAGNANT_FAIL:.0f}s gray zone]", "warn"))

    # 3. Twins — advisory until pinned to the owner's reference video.
    #    One representative per beat, and it must be the SETTLED frame: an
    #    entrance still is mid-animation, so comparing first-frames measures how
    #    alike two entrances look rather than how alike two beats look.
    #    Only gradeable when the stills say which beat they belong to. With
    #    unlabelled names every frame is its own "beat", so the rule degenerates
    #    into a second, noisier copy of the freeze rule above — it must report
    #    that it graded nothing rather than emit that noise.
    reps, twins_graded = [], any(b for _, b, _ in frames)
    if twins_graded:
        groups = {}
        for t, beat, p in frames:
            groups.setdefault(beat, []).append((t, p))
        for key, items in groups.items():
            items.sort()
            t, p = items[len(items) // 2]
            reps.append((t, key, p))
        reps.sort()
        for (ta, ka, pa), (tb, kb, pb) in zip(reps, reps[1:]):
            c, _ = churn(px[pa], px[pb])
            if c < twin_churn:
                warns.append(Finding(
                    "twin-beats",
                    f"{ka} ({ta:.1f}s) and {kb} ({tb:.1f}s) differ by only "
                    f"{c:.4f} churn — consecutive beats are drawing nearly the "
                    f"same picture", "warn"))
    else:
        warns.append(Finding(
            "twin-beats-not-graded",
            "stills carry no beat labels, so the twin-beats rule graded "
            "nothing (it needs f<t>s_<beat>_<pos>.png naming)", "warn"))

    report = {"stills": len(frames), "beats": len(reps) or None,
              "max_gap_s": round(worst[0], 2), "twins_graded": twins_graded,
              "words": len(words), "static_runs": len(runs)}
    return report, problems, warns


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2

    def opt(name, default, cast=float):
        return cast(argv[argv.index(name) + 1]) if name in argv else default

    ws = opt("--ws", None, str)
    report, problems, warns = check(
        Path(args[0]), ws,
        opt("--freeze-churn", FREEZE_CHURN), opt("--twin-churn", TWIN_CHURN))

    if "--json" in argv:
        print(json.dumps({"pass": report is not None and not problems,
                          "report": report,
                          "problems": [str(p) for p in problems],
                          "warnings": [str(w) for w in warns],
                          "findings": typed(problems + warns)}, indent=1))
    else:
        if report:
            print(f"[diversity] {report['stills']} still(s) over "
                  f"{report["beats"]} beat(s), widest gap "
                  f"{report['max_gap_s']}s (limit {MAX_SAMPLE_GAP:.1f}s), "
                  f"{report['words']} narration word(s), "
                  f"{report['static_runs']} static run(s)")
        for p in problems:
            print(f"  !! {p}")
        for w in warns:
            print(f"  ?  {w}")
        print("DIVERSITY: " + ("PASS" if report is not None and not problems
                               else f"FAIL ({len(problems)})"))
    if report is None:
        return 2
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
