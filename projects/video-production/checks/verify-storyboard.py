#!/usr/bin/env python3
"""Storyboard gate for the SCLA lesson-video studio (stage 3 of PROCESS.md).

    python3 verify-storyboard.py --lesson <path/to/lessons/<program>/<stem>> [--draft]

Grades `storyboard.md` in the lesson dir: beats keyed to the real narration
word timings and covering the full runtime, every beat naming a visual and
tracing to design-system tokens, no hand-picked hex colors, no retired names.

--draft grades an author's draft (no Panel Verdict required — and an author
who writes `Approved: yes` into their own draft FAILS). Without --draft the
file must carry a `## Panel Verdict` section with `Approved: yes` and the
critic-panel run name — the storyboarded stage's exit form, written only by
the orchestrator.

Prints every failure with its reason; exit 0 only when everything passes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

fails: list[str] = []


def fail(msg: str) -> None:
    fails.append(msg)


def parse_time(cell: str):
    """Accept `mm:ss`, `mm:ss.s`, or bare seconds."""
    cell = cell.strip()
    m = re.fullmatch(r"(\d{1,2}):(\d{2}(?:\.\d+)?)", cell)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    m = re.fullmatch(r"\d+(?:\.\d+)?s?", cell)
    if m:
        return float(cell.rstrip("s"))
    return None


def section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
                  text, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else ""


def audio_duration(words_path: Path):
    """Last word-timing end, from the common shapes verify-round scripts accept."""
    try:
        data = json.loads(words_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{words_path}: not valid JSON ({exc})")
        return None
    seq = data.get("words") if isinstance(data, dict) else data
    if not isinstance(seq, list) or not seq:
        fail(f"{words_path}: unrecognized word-timing shape")
        return None
    ends = []
    for w in seq:
        if isinstance(w, dict):
            for k in ("end", "end_s", "end_time", "endTime"):
                if k in w:
                    try:
                        ends.append(float(w[k]))
                    except (TypeError, ValueError):
                        pass
                    break
    return max(ends) if ends else None


def token_vocabulary(tokens_path: Path) -> set[str]:
    """Every name a storyboard may cite: colors, type-scale roles, components,
    motion keys. Parsed leniently so this works without PyYAML."""
    vocab: set[str] = set()
    try:
        import yaml
        data = yaml.safe_load(tokens_path.read_text(encoding="utf-8"))
        for block in ("colors", "components", "motion"):
            vocab |= set((data.get(block) or {}).keys())
        vocab |= set(((data.get("typography") or {}).get("scale") or {}).keys())
    except Exception:
        for m in re.finditer(r"^\s{2}([a-z][a-z0-9-]*):", tokens_path.read_text(encoding="utf-8"), re.M):
            vocab.add(m.group(1))
    return vocab


def retired_names(tokens_path: Path) -> list[str]:
    text = tokens_path.read_text(encoding="utf-8")
    block = re.search(r"^retired-names:\s*$([\s\S]*?)(?=^\S|\Z)", text, re.M)
    if not block:
        return []
    return re.findall(r'-\s*"?([^"\n]+?)"?\s*$', block.group(1), re.M)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lesson", required=True, type=Path,
                    help="lessons/<program>/<stem> directory")
    ap.add_argument("--draft", action="store_true",
                    help="grade an author draft: Panel Verdict not required, "
                         "self-approval forbidden")
    a = ap.parse_args()

    lesson = a.lesson.resolve()
    vp = lesson.parent.parent.parent  # .../projects/video-production
    tokens_path = vp / "design-system" / "config" / "tokens.yml"
    sb = lesson / "storyboard.md"
    wj = lesson / "audio" / "narration.words.json"

    if not tokens_path.exists():
        print(f"FATAL: {tokens_path} not found — --lesson must point at "
              f"lessons/<program>/<stem> inside projects/video-production")
        return 2
    if not sb.exists():
        print(f"FAIL: {sb} missing — the storyboard is the stage-3 artifact")
        return 1
    text = sb.read_text(encoding="utf-8")

    # --- beats keyed to the real narration clock ---
    dur = None
    if not wj.exists():
        fail(f"{wj} missing — beats must be keyed to real word timings, "
             f"which means narration (stage 2) comes first")
    else:
        dur = audio_duration(wj)

    beats_sec = section(text, "Beats")
    if not beats_sec:
        fail(f"{sb}: no '## Beats' section")
    rows = []
    for line in beats_sec.splitlines():
        if re.match(r"^\s*\|", line) and not re.match(r"^\s*\|[\s:|-]+\|?\s*$", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and not re.search(r"start", cells[min(1, len(cells) - 1)], re.I):
                rows.append(cells)
    # drop a header row that names the columns
    rows = [r for r in rows if not re.search(r"visual", " ".join(r), re.I)
            or parse_time(r[1] if len(r) > 1 else "") is not None]

    if len(rows) < 8:
        fail(f"{sb}: only {len(rows)} beat row(s) parsed — a lesson video "
             f"needs at least 8 beats (frequent scene changes, no static "
             f"stretch). Beats are '| # | start | end | visual | on-screen "
             f"| tokens |' table rows.")

    vocab = token_vocabulary(tokens_path)
    prev_start = -1.0
    last_end = None
    for i, r in enumerate(rows, 1):
        if len(r) < 6:
            fail(f"{sb}: beat row {i} has {len(r)} cells — need "
                 f"| # | start | end | visual | on-screen | tokens |")
            continue
        start, end = parse_time(r[1]), parse_time(r[2])
        if start is None or end is None:
            fail(f"{sb}: beat {i} has unparseable time(s) {r[1]!r}/{r[2]!r} "
                 f"(use mm:ss.s or seconds)")
            continue
        if start <= prev_start:
            fail(f"{sb}: beat {i} starts at {start}s, not after the previous "
                 f"beat's start — beats must ascend")
        if end <= start:
            fail(f"{sb}: beat {i} ends at {end}s, at or before its own start")
        if end - start > 20.0:
            fail(f"{sb}: beat {i} runs {end - start:.1f}s — longer than the "
                 f"20s static-stretch ceiling; split it")
        if dur is not None and end > dur + 3.0:
            fail(f"{sb}: beat {i} ends at {end:.1f}s but narration runs "
                 f"{dur:.1f}s — the beat outlives the audio")
        prev_start = start
        last_end = end
        if not r[3]:
            fail(f"{sb}: beat {i} has an empty visual cell")
        toks = r[5]
        cited = [t for t in re.findall(r"[a-z][a-z0-9-]+", toks.lower()) if t in vocab]
        if not cited:
            fail(f"{sb}: beat {i} tokens cell {toks!r} cites no known token "
                 f"from design-system/config/tokens.yml — every design choice "
                 f"traces to a token, nothing hand-picked")
        if re.search(r"#[0-9a-fA-F]{3,8}\b", toks):
            fail(f"{sb}: beat {i} tokens cell carries a raw hex value — cite "
                 f"the token name, never a hand-picked color")

    if rows and dur is not None and last_end is not None and last_end < dur - 3.0:
        fail(f"{sb}: beats end at {last_end:.1f}s but narration runs "
             f"{dur:.1f}s — the storyboard leaves dead air uncovered")
    if rows and (t0 := parse_time(rows[0][1]) if len(rows[0]) > 1 else None) \
            is not None and t0 > 1.0:
        fail(f"{sb}: first beat starts at {t0}s — the video must open on a "
             f"designed frame, not dead air")

    # --- copy hygiene ---
    for name in retired_names(tokens_path):
        if re.search(re.escape(name), text, re.IGNORECASE):
            fail(f"{sb}: contains retired name {name!r} — must never reach a "
                 f"viewer in copy or design")

    # --- verdict discipline ---
    verdict = section(text, "Panel Verdict")
    approved = bool(re.search(r"approved:\s*yes", verdict, re.IGNORECASE))
    if a.draft:
        if approved:
            fail(f"{sb}: draft carries 'Approved: yes' — the author never "
                 f"writes its own verdict; the panel and orchestrator do")
    else:
        if not verdict:
            fail(f"{sb}: no '## Panel Verdict' section — stage storyboarded "
                 f"requires the critic-panel verdict")
        else:
            if not approved:
                fail(f"{sb}: Panel Verdict does not say 'Approved: yes'")
            if not re.search(r"run:\s*\S+", verdict, re.IGNORECASE):
                fail(f"{sb}: Panel Verdict names no Ringer run")
            if not re.search(r"20\d\d-\d\d-\d\d", verdict):
                fail(f"{sb}: Panel Verdict carries no date")

    if fails:
        print(f"FAIL — {len(fails)} problem(s):")
        for f in fails:
            print(f"  • {f}")
        return 1
    mode = "draft" if a.draft else "approved"
    print(f"PASS — storyboard.md holds ({mode} mode): {len(rows)} beats keyed "
          f"to the narration clock, all tracing to tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
