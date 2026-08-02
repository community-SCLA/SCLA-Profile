#!/usr/bin/env python3
"""Deterministic on-frame TEXT gate for SCLA HyperFrames lesson builds.

Two checks, both static (no browser, no render) — they run in preflight, before
the expensive render:

  1. size   — minimum on-frame text size (design-contract.md -> "Type rules" ->
              "Minimum on-frame text size", frontmatter typography.min-size).
              Every `font-size: <n>px` rule in the workspace's compositions is
              graded against a floor picked from how the rule is TYPESET:
                * label class  (`text-transform: uppercase` AND `letter-spacing`)
                  -> 20px floor. Eyebrows, scene index, brandline, chips,
                  attribution — the tracked furniture.
                * body class   (everything else) -> 32px floor. Anything the
                  viewer reads as a sentence: points, captions, card copy,
                  sub-beats, notes.
              A rule opts out with `/* text-floor-exempt: <reason> */` on the
              line above it (marker numerals sized by their circle).

  2. restate — no line restates the label or heading (design-contract.md -> "Type rules").
              A sub-beat / caption / point whose words are a subset of, or >=80%
              overlap with, that scene's `label` or `heading` is a second,
              smaller copy of a line already on the frame at full size. Owner
              call 2026-07-27, off the scla-points scene that put "Your role is
              not fixed" at 30px along the bottom while the eyebrow above it
              already read "REFRAME 3 - YOUR ROLE IS NOT FIXED".

Usage:  check_text.py <workspace-dir> [--json]

Exit code 1 when any violation is found; 0 = clean. Also runnable against the
design system itself (`check_text.py design-system`) to grade the templates.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tokens
from hfp_common import Finding, norm_phrase, parse_scenes

# LOADED from tokens.yml typography.min-size — not a copy of it.
# These were hand-maintained constants under a "keep in sync" comment until
# 2026-07-29; nothing verified the copy, so the spec and the gate could disagree
# silently. tokens.py makes tokens.yml the single source (see its docstring).
BODY_FLOOR, LABEL_FLOOR = tokens.min_size()

EXEMPT_RE = re.compile(r"/\*\s*text-floor-exempt:")
# a CSS rule: everything up to `{`, then the declaration block
RULE_RE = re.compile(r"([^{}/]+)\{([^{}]*)\}")
FONT_SIZE_RE = re.compile(r"font-size:\s*([\d.]+)px")

# Which variable keys carry viewer-read lines (vs. cue lists, themes, numbers).
# Restatement is graded on these; `label` and `heading` are the reference lines.
LINE_KEYS_RE = re.compile(
    r"^(subBeats|point\d*|step\d*|caption\d*|line\d*|chips?\d*|note\d*|item\d*"
    r"|lines|captions|takeaway|cardA\w*|cardB\w*)$"
)
REFERENCE_KEYS = ("label", "heading", "kicker", "statement")
OVERLAP_FAIL = 0.8  # >= this share of a line's words already in label/heading


def classify(decls: str) -> str:
    """label class = uppercase AND letter-spaced (the design contract's label spec);
    everything else is body class."""
    return ("label" if "uppercase" in decls and "letter-spacing" in decls
            else "body")


def check_sizes(css_files):
    """Grade every font-size rule in the given files against its class floor."""
    findings, graded = [], 0
    for path in css_files:
        src = path.read_text()
        for m in RULE_RE.finditer(src):
            selector, decls = m.group(1), m.group(2)
            fs = FONT_SIZE_RE.search(decls)
            if not fs:
                continue
            # exemption comment anywhere in the ~200 chars before the rule
            head = src[max(0, m.start() - 200):m.start()]
            if EXEMPT_RE.search(head):
                continue
            graded += 1
            size = float(fs.group(1))
            kind = classify(decls)
            floor = LABEL_FLOOR if kind == "label" else BODY_FLOOR
            if size < floor:
                sel = " ".join(selector.split())[-70:]
                fix = ("raise it, or retypeset it as a label "
                       "(uppercase + letter-spacing) if it is really metadata"
                       if kind == "body" else "raise it")
                findings.append(Finding(
                    "text-below-min-size",
                    f"{path.name}: `{sel}` renders {kind}-class text at "
                    f"{size:g}px, below the {floor}px {kind} floor — {fix} "
                    f"(tokens.yml typography.min-size)"))
    return findings, graded


def _lines_from(value, key=""):
    """A variable's viewer-read lines. subBeats is pipe-separated; `chips` is
    comma-separated (each chip renders as its own pill and is graded as its
    own line — the un-split list diluted overlap below the gate, 2026-07-28);
    the rest are single strings."""
    parts = [p.strip() for p in str(value).split("|") if p.strip()]
    if key == "chips":
        parts = [c.strip() for p in parts for c in p.split(",") if c.strip()]
    return parts


def check_restatement(scenes):
    """Flag any line that just repeats the scene's label or heading."""
    findings = []
    graded = 0
    for sc in scenes:
        vars_ = sc.get("variables") or {}
        refs = {k: norm_phrase(str(vars_[k])) for k in REFERENCE_KEYS
                if vars_.get(k) and str(vars_[k]).strip()}
        if not refs:
            continue
        for key, value in vars_.items():
            if not LINE_KEYS_RE.match(key) or not str(value).strip():
                continue
            for line in _lines_from(value, key):
                toks = norm_phrase(line)
                if len(toks) < 2:
                    continue
                graded += 1
                for ref_key, ref_toks in refs.items():
                    if not ref_toks:
                        continue
                    shared = sum(1 for t in toks if t in ref_toks)
                    overlap = shared / len(toks)
                    if overlap >= OVERLAP_FAIL:
                        findings.append(Finding(
                            "restates-heading",
                            f"{sc['id']}: {key} \"{line}\" restates {ref_key} "
                            f"\"{vars_[ref_key]}\" ({overlap:.0%} of its words "
                            f"are already on the frame) — drop the line or give "
                            f"it something the frame is not already showing "
                            f"(design-contract.md \"Never restate the label or heading\")"))
                        break
    return findings, graded


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0]).resolve()
    comps = sorted((ws / "compositions").glob("*.html"))
    index = ws / "index.html"

    size_findings, size_graded = check_sizes(comps)
    if index.is_file():
        restate_findings, restate_graded = check_restatement(
            parse_scenes(index.read_text()))
    else:
        restate_findings, restate_graded = [], 0

    findings = size_findings + restate_findings
    result = {
        "verdict": "FAIL" if findings else "PASS",
        "size": {"graded": size_graded, "violations": size_findings},
        "restate": {"graded": restate_graded, "violations": restate_findings},
    }
    if as_json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(f"size:    {size_graded} font-size rule(s) in "
              f"{len(comps)} composition(s), {len(size_findings)} below floor "
              f"(body >= {BODY_FLOOR}px, label >= {LABEL_FLOOR}px)")
        print(f"restate: {restate_graded} on-frame line(s) graded, "
              f"{len(restate_findings)} restating the label/heading")
        for f in findings:
            print(f"  - {f}")
        print(f"VERDICT: {result['verdict']}")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
