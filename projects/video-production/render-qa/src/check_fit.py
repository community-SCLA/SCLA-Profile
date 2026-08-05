#!/usr/bin/env python3
"""check_fit.py — plan-stage copy fit for the freeform lane. ADVISORY.

The retired per-slot capacity gate was the pipeline's cheapest: it failed a too-long string
while the fix is still a text edit, rather than after a render has been spent.
It does that by resolving a TEMPLATE's declared `maxLines` and slot CSS, so it
dies with the compiler. This is its rehome (BUILD-PLAN step 1.3c).

WHAT SURVIVES THE MOVE, and it is the important half: the measurement is still
made in the REAL vendored font via `textmetrics.py`, generated from the
committed woff2 metrics. Estimating characters-per-line is guesswork that drifts
per weight and per string. `textmetrics` is font truth, not template mechanics,
and is not part of the template retirement.

WHAT CANNOT SURVIVE: the per-slot budget. A freeform layout is designed around
its copy, so there is no declared box to measure against and no `maxLines` to
read. What IS still knowable without any CSS model is the frame itself — the
content area, from tokens.yml — and the smallest type size the pipeline permits.
So this asks the one question that needs no template and no browser:

    Does this string fit the content area AT THE MINIMUM LEGAL TYPE SIZE?

A string that does not is broken at every legal size, because every legal size
is larger. That makes a finding here a geometric fact rather than a taste call,
and it makes the gate deliberately PERMISSIVE: real copy is set far above the
40px floor, so anything this flags is badly wrong rather than merely tight.

ADVISORY, per STD-38. It exits 0 with findings printed, and `preflight.py` does
not block on it. Two reasons, both honest: a permissive budget aimed at the plan
stage should teach before it nags, and the HARD backstop for this question
already exists and does block — `check_ink.py` grades real rendered pixels
against the same keep-out bands (step 1.4). This gate's value is that it answers
before the pixels exist; it is not the thing standing between a bad frame and a
render. Arm it (`--strict`) only after a reference build has pinned the budget.

  python3 check_fit.py <workspace> [--json] [--strict]

Exit: 0 clean OR advisory findings · 1 findings with --strict · 2 nothing to read
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textmetrics  # noqa: E402
import tokens  # noqa: E402
from hfp_common import Finding, onframe_strings, typed  # noqa: E402

# Weight matters: heavier faces are wider, so measuring a heading at 400 would
# under-measure it. Headings in this system are set in the 900 display weight.
HEADING_WEIGHT = 900
BODY_WEIGHT = 400


def budget(ws=None):
    """The frame's content area and the largest block that can occupy it at the
    minimum legal type size. All four numbers are LOADED from tokens.yml —
    never hand-copied — per the rules file's "tokens.yml is LOADED, not quoted".
    """
    cw, _ = tokens.canvas(ws)
    safe = tokens.safe_area(ws)
    body_floor, _label_floor = tokens.min_size(ws)
    avail_w = cw - 2 * safe
    avail_h = tokens.content_bottom(ws) - safe
    line_px = body_floor * textmetrics.normal_line_height(BODY_WEIGHT)
    return {"avail_w": avail_w, "avail_h": avail_h, "size": body_floor,
            "line_px": line_px, "max_lines": int(avail_h // line_px)}


def check(ws: Path, strings=None):
    """(report, problems). Findings are advisory; the caller decides."""
    # `strings` may be supplied directly (fixtures, and any caller that already
    # extracted them), in which case there need be no workspace at all.
    ws = Path(ws) if ws is not None else None
    if strings is None:
        strings = onframe_strings(ws)
    if not strings:
        return None, [Finding(
            "nothing-graded",
            f"no on-frame strings found under {ws} — this gate can measure "
            f"NOTHING. A gate that passes having looked at nothing is the most "
            f"expensive bug class in this pipeline.")]

    # A workspace's COPIED tokens.yml governs, because that is what the build
    # was made against — same doctrine as preflight's composition_freshness.
    b = budget(ws if ws is not None and (ws / "tokens.yml").exists() else None)
    problems = []
    for fname, role, text in strings:
        weight = HEADING_WEIGHT if role == "heading" else BODY_WEIGHT
        lines = textmetrics.line_count(text, b["avail_w"], b["size"], weight)
        if lines > b["max_lines"]:
            problems.append(Finding(
                "fit-impossible",
                f"{fname}: this {role} needs {lines} lines to fit "
                f"{b['avail_w']:.0f}px at the {b['size']:.0f}px MINIMUM type "
                f"size, but only {b['max_lines']} fit the content area — so it "
                f"does not fit at ANY legal size. Cut the copy or split the "
                f"beat: {text[:90]!r}", severity="warning"))
        elif role == "heading" and lines > 1:
            # A heading is set at DISPLAY size, several times the body floor.
            # So "cannot be one line even at the smallest legal size" is again
            # a fact rather than a preference, and it means the real heading
            # runs to several lines. The 3-line-at-floor threshold this rule
            # first carried was ~240 characters — a bound no real heading could
            # reach, which is a rule that cannot fire dressed as a rule.
            problems.append(Finding(
                "fit-heading-long",
                f"{fname}: this heading needs {lines} lines even at the "
                f"{b['size']:.0f}px MINIMUM size, so it cannot be one line at "
                f"any legal size — at real display size it will run longer "
                f"still. A heading is a title, not a sentence: "
                f"{text[:90]!r}", severity="warning"))
    return {"strings": len(strings), **b}, problems


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    strict = "--strict" in argv
    report, problems = check(Path(args[0]))
    if "--json" in argv:
        print(json.dumps({"pass": not problems, "advisory": not strict,
                          "report": report, "problems": problems,
                          "findings": typed(problems)}, indent=2))
    elif report is None:
        for p in problems:
            print(f"  !! {p}")
        return 2
    else:
        print(f"[fit] {report['strings']} on-frame string(s) measured in the "
              f"real vendored font at the {report['size']:.0f}px floor — "
              f"content area {report['avail_w']:.0f}x{report['avail_h']:.0f}px, "
              f"{report['max_lines']} lines max")
        for p in problems:
            print(f"  {'!!' if strict else '~~'} {p}")
        verdict = "PASS" if not problems else (
            f"FAIL ({len(problems)})" if strict
            else f"ADVISORY ({len(problems)}) — not blocking, per STD-38")
        print(f"FIT: {verdict}")
    return 1 if (problems and strict) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
