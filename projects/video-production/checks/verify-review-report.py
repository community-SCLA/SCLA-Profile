#!/usr/bin/env python3
"""Verify a check-print lane report — SCLA-owned, video-native.

Replaces the generic review-swarm template checker, which graded video QA
prose against a CODE reviewer's rubric (file:line evidence, P0-P3 only, a
1200-word cap, an exact '# Review Report' title) and failed correct reports
on formatting. Rule here: strict on substance, tolerant on format.

Substance this enforces:
  * the report exists and is thick enough to be real work
  * every required section is present (case-insensitive substring — a
    heading may be '## Findings', '### Findings', '**Findings**' or
    'Findings:'; the checker does not care)
  * each finding carries a LOCATOR a human can navigate to: a timestamp
    (1:23, 83.45s), a beat reference (beat 7), or a file:line — any one
  * each finding carries a severity from a tolerant vocabulary
    (P0-P3, blocker/critical/major/minor/nit, high/medium/low)
  * cited timestamps actually exist inside the render (--render) — a
    fabricated 4:12 in a 2:38 video is a hard failure

Format this deliberately does NOT enforce: title text, heading depth,
word counts, summary line counts, field ordering.

Exit 0 only when every substance gate passes.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_BYTES = 800
DEFAULT_SECTIONS = ("Summary", "Findings", "Assumptions")

# a finding starts at 'Finding:', '### Finding 3:', '1.' or '1)' at line start
FINDING_START = re.compile(
    r"^\s*(?:#{0,4}\s*)?(?:finding\b\s*\d*\s*[:.\-]|\d+[.)]\s)",
    re.IGNORECASE | re.MULTILINE,
)
TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(?:\.\d+)?\b")
SECONDS = re.compile(r"\b\d{1,4}(?:\.\d+)?\s*s(?:ec|econds)?\b", re.IGNORECASE)
BEAT = re.compile(r"\bbeats?\s*\d+\b", re.IGNORECASE)
FILE_LINE = re.compile(r"\b[\w./-]+\.\w+:\d+\b")
SEVERITY = re.compile(
    r"\b(?:P[0-3]|blocker|critical|major|minor|nit|high|medium|low)\b",
    re.IGNORECASE,
)

fails = []


def fail(name, detail):
    fails.append(f"FAIL [{name}]: {detail}")


def resolve_render(path):
    """Accept the MP4 itself or a lesson dir; a dir resolves to its newest
    dated render, so a manifest never has to name a render date."""
    if path.is_dir():
        found = sorted(path.glob("render/*.mp4")) or sorted(path.glob("*.mp4"))
        return found[-1] if found else None
    return path if path.is_file() else None


def render_duration(path):
    """Seconds of the render, or None when ffprobe cannot read it."""
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return None


def heading_level(line):
    """Depth of a heading line: 1-6 for #.., 3 for a bold-only line, 0 otherwise."""
    m = re.match(r"^[^\S\n]*(#{1,6})\s+\S", line)
    if m:
        return len(m.group(1))
    if re.match(r"^[^\S\n]*\*\*[^*]+\*\*[:\s]*$", line):
        return 3
    return 0


def section_body(text, heading):
    """Body under a heading, ending at the next heading of the SAME depth or
    shallower — so '### Finding:' blocks stay inside '## Findings' and the
    methodology section below it stays out."""
    lines = text.splitlines()
    needle = heading.lower()
    for index, line in enumerate(lines):
        level = heading_level(line)
        stripped = re.sub(r"[#*:]", "", line).strip().lower()
        if stripped != needle:
            continue
        level = level or 2
        body = []
        for follow in lines[index + 1:]:
            follow_level = heading_level(follow)
            if follow_level and follow_level <= level:
                break
            body.append(follow)
        return "\n".join(body).strip()
    return ""


def locators(block):
    return (TIMESTAMP.findall(block) + SECONDS.findall(block)
            + BEAT.findall(block) + FILE_LINE.findall(block))


def cited_seconds(block):
    """Every timestamp in the block converted to seconds."""
    out = []
    for stamp in TIMESTAMP.findall(block):
        mins, _, secs = stamp.partition(":")
        out.append((stamp, int(mins) * 60 + float(secs)))
    for raw in SECONDS.findall(block):
        out.append((raw, float(re.sub(r"[^\d.]", "", raw))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--surface", required=True,
                    help="what this lane audited — echoed into the verdict")
    ap.add_argument("--require", nargs="+", default=list(DEFAULT_SECTIONS))
    ap.add_argument("--render", type=Path,
                    help="MP4 the lane reviewed; timestamps are range-checked against it")
    ap.add_argument("--export", type=Path,
                    help="copy the report here on success so it survives a deleted worktree")
    ap.add_argument("--min-bytes", type=int, default=MIN_BYTES)
    args = ap.parse_args()

    if "{{" in args.surface or "}}" in args.surface:
        fail("placeholder_unfilled", "--surface still contains an unfilled placeholder")

    if not args.report.is_file():
        print(f"FAIL [missing_report]: {args.report} does not exist")
        return 1
    text = args.report.read_text(encoding="utf-8", errors="replace")
    size = len(text.encode())
    if size < args.min_bytes:
        fail("report_too_thin", f"{size} bytes; floor is {args.min_bytes} — too thin to be real review work")

    lowered = text.lower()
    for heading in args.require:
        if heading.lower() not in lowered:
            fail("missing_section", f"no '{heading}' section found anywhere in the report")

    findings = section_body(text, "Findings") or text
    declared_clean = re.search(r"\bno findings\b", findings, re.IGNORECASE)

    duration = None
    if args.render:
        render = resolve_render(args.render)
        if render is None:
            fail("render_missing", f"no MP4 found at {args.render} — cannot range-check cited timestamps")
        else:
            duration = render_duration(render)
            if duration is None:
                fail("render_unreadable", f"ffprobe cannot read {render}")

    starts = [m.start() for m in FINDING_START.finditer(findings)]
    if not starts and not declared_clean:
        fail("findings_unreadable",
             "Findings section has no recognizable finding blocks and does not say 'no findings' — "
             "start each finding with 'Finding:' or a numbered list item")

    blocks = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(findings)
        blocks.append(findings[start:end])

    for index, block in enumerate(blocks, start=1):
        head = block.strip().splitlines()[0][:70] if block.strip() else "(empty)"
        if not locators(block):
            fail("finding_no_locator",
                 f"finding {index} ({head}) cites no timestamp, beat, or file:line — "
                 "a finding nobody can navigate to is not actionable")
        if not SEVERITY.search(block):
            fail("finding_no_severity",
                 f"finding {index} ({head}) carries no severity "
                 "(P0-P3, blocker/major/minor/nit, or high/medium/low)")
        if duration:
            for raw, secs in cited_seconds(block):
                if secs > duration + 0.5:
                    fail("timestamp_out_of_range",
                         f"finding {index} cites {raw} ({secs:.1f}s) but the render is only "
                         f"{duration:.1f}s long — that moment does not exist")

    if fails:
        for item in fails:
            print(item)
        return 1

    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.report, args.export)
        print(f"exported {args.report} -> {args.export}")
    verdict = "no findings" if not blocks else f"{len(blocks)} finding(s), all located and graded"
    print(f"PASS [review_contract]: {args.report} — {verdict} for {args.surface}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
