#!/usr/bin/env python3
"""check_pace.py — does this build deliver ideas fast enough, against a
backdrop that holds?

THE HOLE THIS CLOSES.  On 2026-08-04 the owner reviewed two freeform cuts of
the same lesson, approved one and called the other "SO boring".  Every gate in
`render-qa/src/` passed the boring one and one gate QUARANTINED the approved
one.  That is the whole reason this file exists: the gate set measured animacy,
and the owner was responding to STRUCTURE.

Measured on the two cuts (both 1 lesson, ~155s, same script, same voice):

                                   APPROVED      REJECTED   discriminates?
    beats                          26            17
    beats per minute               10.26          6.47      YES
    median beat duration            5.15s         9.12s     YES
    share of runtime in >8s beats  45%           79%        YES
    mean inter-beat churn           3.34%        10.07%     YES (inverted)
    twin-beat pairs                 2 (8%)        0         INVERTED — the
                                                            approved cut looks
                                                            worse on this one
    longest static span             5.5s          3.75s     INVERTED — ditto

The last two rows are why nothing already in `src/` could catch this.  The
rejected cut changes something every ~2.5s and draws a brand-new picture every
beat; it is MORE animated by every metric the pipeline owns.  It is boring
because each idea takes 9.3s to arrive and nothing on screen accumulates.

So the three rules here grade the two things that DO discriminate:

  1. `beat-pace`        — ideas per minute.  Graded on `timing.json` at PLAN
                          stage, before a pixel is authored, because the fix is
                          re-splitting the beat manifest and re-synthesizing —
                          cheap before step 5, expensive after.
  2. `long-beat-share`  — how much of the runtime is spent inside a single
                          long beat.  A build can hit the median and still park
                          in three 15s beats.
  3. `carrier-drift`    — the carrying-object rule made measurable.  A
                          persistent visual system that RE-SORTS produces low
                          beat-to-beat churn; a slideshow of unrelated pictures
                          produces high churn.  This is a BAND, not a floor:
                          the bottom of the band is owned by `check_presence`'s
                          stagnation rules, which stay authoritative.

Every threshold below sits in the GAP between the approved and the rejected
cut, with margin on both sides — the calibration idiom `check_diversity` uses
for FREEZE_MAXDIFF.  A number pulled from taste rather than from a build is
exactly the kind of gate the repo has switched off before.

STATED LIMIT — these thresholds are calibrated on n=2, and both cuts are the
SAME LESSON.  That is enough to fix a direction (idea rate over animacy) and
not enough to claim a general law about pace across every lesson this pipeline
will ever build.  A future lesson that genuinely wants a slower shape is an
OWNER DECISION that pins a second reference build, recorded in
`decisions/log.md` — never a CLI flag, never a loosened constant here. Same
posture as the ink gate's declared keep-out region (`check_ink.py`).

Wired into `preflight.py`'s freeform branch: the two timing rules
(`beat-pace`, `long-beat-share`) run in `--static` (the fix is re-splitting
`audio_request.json`, free before synthesis); `carrier-drift` runs in the full
gate over the `snapshots/` grid `check_freeform_ink` already produces.
Blocking, not advisory — STD-38's teach-first posture is for unpinned taste
numbers, and an advisory pace gate would reproduce the exact failure this file
exists to close: the boring cut passed everything advisory and shipped to the
gate clean.

    python3 check_pace.py <workspace>            # timing rules (plan stage)
    python3 check_pace.py <workspace> --stills   # + carrier-drift, needs snapshots
"""
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import Finding, typed  # noqa: E402

# ---------------------------------------------------------------------------
# THRESHOLDS.  Each is stated as: approved cut | threshold | rejected cut.
# ---------------------------------------------------------------------------

# 5.15s | 7.0 | 9.12s  — margin 1.85s below, 2.12s above.  Near-symmetric, so
# neither cut is sitting on the line.
MAX_MEDIAN_BEAT = 7.0

# 10.26 | 8.0 | 6.47  — margin 2.26 above, 1.53 below.  Deliberately nearer the
# rejected cut: this rule should stop a 6-beats-per-minute build, not police the
# difference between a good build and a slightly better one.
MIN_BEATS_PER_MIN = 8.0

# A beat this long has to carry its own internal structure to stay watchable.
# Not a violation by itself — it is what LONG_BEAT_SHARE counts.
LONG_BEAT_SEC = 8.0

# 45% | 60% | 79% — margin 15pts either side.
MAX_LONG_BEAT_SHARE = 0.60

# 3.34% | 6.0% | 10.07% — margin 2.7pts below, 4.1pts above.  A CEILING, which
# is the counter-intuitive half: high beat-to-beat churn means every beat threw
# the frame away and started again.  The floor is check_presence's job.
MAX_MEAN_CHURN = 0.060

# Below this a cut is not "carrying" anything, it is frozen, and the finding
# belongs to check_presence/check_diversity rather than here.  Stated so this
# file cannot be read as licensing a still image.
FROZEN_MEAN_CHURN = 0.004


def beats(ws: Path):
    """[(id, vis_dur)] from timing.json, plus the total runtime."""
    tj = ws / "timing.json"
    if not tj.is_file():
        return None, None
    data = json.loads(tj.read_text())
    rows = data.get("rows") or []
    out = [(r.get("id"), float(r["vis_dur"])) for r in rows if "vis_dur" in r]
    return out, float(data.get("total") or sum(d for _, d in out))


def check_timing(ws: Path):
    """(report, problems).  report is None when nothing was gradeable — the
    caller FAILS on that, never passes.  A gate that grades zero beats and
    exits 0 is the failure mode this whole lane was rebuilt to close."""
    rows, total = beats(ws)
    if not rows or not total:
        return None, [Finding(
            "nothing-graded",
            f"{ws}: no readable timing.json rows — pace cannot be graded. "
            f"Nothing to grade is a failure, never a pass.")]

    durs = [d for _, d in rows]
    median = statistics.median(durs)
    bpm = len(durs) * 60.0 / total
    long_secs = sum(d for d in durs if d > LONG_BEAT_SEC)
    share = long_secs / total

    report = {"beats": len(durs), "total": round(total, 2),
              "median": round(median, 2), "bpm": round(bpm, 2),
              "long_share": round(share, 3),
              "longest": round(max(durs), 2)}
    problems = []

    if median > MAX_MEDIAN_BEAT:
        problems.append(Finding(
            "beat-pace",
            f"median beat is {median:.2f}s against a {MAX_MEDIAN_BEAT}s "
            f"ceiling — the typical idea takes too long to arrive. The "
            f"owner-approved reference cut runs 5.15s. Fix by SPLITTING the "
            f"beat manifest (audio_request.json) into more, shorter beats, "
            f"not by trimming narration."))

    if bpm < MIN_BEATS_PER_MIN:
        problems.append(Finding(
            "beat-pace",
            f"{len(durs)} beats over {total:.1f}s is {bpm:.2f} beats/min "
            f"against a {MIN_BEATS_PER_MIN} floor. The approved reference "
            f"delivers 10.26. This is the single measurement that separated "
            f"the approved cut from the one the owner called boring."))

    if share > MAX_LONG_BEAT_SHARE:
        problems.append(Finding(
            "long-beat-share",
            f"{share*100:.0f}% of the runtime sits inside beats longer than "
            f"{LONG_BEAT_SEC}s ({long_secs:.1f}s of {total:.1f}s), against a "
            f"{MAX_LONG_BEAT_SHARE*100:.0f}% ceiling; longest beat is "
            f"{max(durs):.1f}s. A build can clear the median and still park "
            f"in a handful of very long beats — this is that case."))

    return report, problems


def check_stills(ws: Path):
    """carrier-drift over one still per beat (the snapshots/ grid the freeform
    sequence already produces at step 7 — no extra render is spent)."""
    from check_diversity import cells, churn, load_frames  # noqa: E402

    snaps = ws / "snapshots"
    frames = load_frames(snaps) if snaps.is_dir() else []
    if len(frames) < 3:
        return None, [Finding(
            "nothing-graded",
            f"{snaps}: {len(frames)} timestamped still(s) — need at least 3 to "
            f"measure carrier drift. Snapshot every beat midpoint first.")]

    prev, churns = None, []
    for _t, _b, p in frames:
        c = cells(p)
        if prev is not None:
            churns.append(churn(prev, c)[0])
        prev = c

    mean = statistics.mean(churns)
    report = {"stills": len(frames), "pairs": len(churns),
              "mean_churn": round(mean * 100, 2)}
    problems = []

    if mean > MAX_MEAN_CHURN:
        problems.append(Finding(
            "carrier-drift",
            f"consecutive beats change {mean*100:.2f}% of the frame on "
            f"average, against a {MAX_MEAN_CHURN*100:.0f}% ceiling — the build "
            f"is throwing the frame away and redrawing it each beat rather "
            f"than re-sorting one carrying object. The approved reference cut "
            f"reads 3.34%: one field of marks, built once in act 2 and only "
            f"ever re-grouped. Name the carrying object in design.md and let "
            f"it PERSIST; do not answer this by adding motion."))
    elif mean < FROZEN_MEAN_CHURN:
        problems.append(Finding(
            "carrier-drift",
            f"consecutive beats change only {mean*100:.2f}% of the frame — "
            f"that is not a carrying object, it is a still image. The floor "
            f"here is deliberately low because stagnation is check_presence's "
            f"call, so reaching it at all means the beats are not doing work."))

    return report, problems


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    ws = Path(args[0])

    report, problems = check_timing(ws)
    s_report, s_problems = (None, [])
    if "--stills" in argv:
        s_report, s_problems = check_stills(ws)
        problems = problems + s_problems

    if "--json" in argv:
        print(json.dumps({"pass": not problems and report is not None,
                          "report": report, "stills": s_report,
                          "problems": problems,
                          "findings": typed(problems)}, indent=2))
        return 1 if problems else (0 if report else 2)

    if report is None:
        for p in problems:
            print(f"  !! {p}")
        return 2

    print(f"[pace] {report['beats']} beats over {report['total']}s — "
          f"{report['bpm']} beats/min, median {report['median']}s, "
          f"longest {report['longest']}s, "
          f"{report['long_share']*100:.0f}% of runtime in >{LONG_BEAT_SEC}s beats")
    if s_report:
        print(f"[pace] carrier: {s_report['pairs']} beat pairs, "
              f"mean churn {s_report['mean_churn']}%")
    elif "--stills" in argv:
        for p in s_problems:
            print(f"  !! {p}")
    for p in problems:
        print(f"  !! {p}")
    print("PACE: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
