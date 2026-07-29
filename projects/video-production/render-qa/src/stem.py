#!/usr/bin/env python3
"""stem.py — the single owner of lesson-stem naming.

A lesson's name is `<title>_<program>_<YYYY-MM-DD>`.

  base   `<title>_<program>`   — the IMMUTABLE identity of the lesson.
  date   `<YYYY-MM-DD>`        — a MUTABLE state stamp: the date of the most
                                 recent pipeline action on that artifact.

Two rules, and everything else follows:

  1. Exactly ONE date suffix. Never two, never zero. A name that has
     accumulated `..._2026-07-06_2026-07-28_18-49-26` is malformed — the new
     date REPLACES the old one, it is never appended.
  2. The date always means "when this artifact was last acted on":
       lesson-scripts/<prog>/<stem>.txt          capture date
       lesson-scripts/<prog>/refined/<stem>.txt  refine date
       renders-hyperframes/<stem>/               build date
       renders-mp4/<prog>/**/<stem>.mp4          render date
       lesson-scripts/<prog>/rendered/<stem>.txt render date
     So a script refined on the 6th and built on the 28th produces a
     workspace named `..._2026-07-28`, not `..._2026-07-06`.

Because the date moves, the date is NOT an identity key. `base` is. Anything
that needs to ask "is this lesson done?" must key on base (published.tsv
column 1) — keying on the full stem breaks the moment the date is restamped.

CLI:
    python3 stem.py base    <stem|path>            -> title_program
    python3 stem.py date    <stem|path>            -> YYYY-MM-DD
    python3 stem.py restamp <stem|path> [--date D] -> title_program_D  (D=today)
    python3 stem.py normalize <stem|path> [--date D] -> as restamp, but also
                                                     repairs an already-malformed
                                                     multi-date name (renderer output)
    python3 stem.py check   <stem|path>            -> exit 0 if canonical
Exit 2 on a malformed stem, with the reason on stderr.
"""
from __future__ import annotations

import datetime as _dt
import re
import sys
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# A trailing render clock (`_18-49-26`) is the HyperFrames CLI's doing, not
# ours; strip it as noise rather than mistaking it for part of the title.
CLOCK_RE = re.compile(r"^\d{2}-\d{2}-\d{2}$")


class StemError(ValueError):
    """A name that does not obey the one-date rule."""


def _strip_path(value: str) -> str:
    """Accept a bare stem, a filename, or a full path."""
    text = str(value).strip().rstrip("/")
    if "/" in text:
        text = Path(text).name
    for suffix in (".mp4", ".txt", ".json", ".wav"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return text


def split(value: str) -> tuple[str, str]:
    """-> (base, date). Raises StemError unless exactly one date is present."""
    text = _strip_path(value)
    if not text:
        raise StemError("empty stem")
    parts = text.split("_")

    # Drop trailing clock segments the renderer appends after its date.
    while len(parts) > 1 and CLOCK_RE.match(parts[-1]):
        parts.pop()

    dates = [i for i, p in enumerate(parts) if DATE_RE.match(p)]
    if not dates:
        raise StemError(f"no YYYY-MM-DD date suffix in {text!r}")
    if len(dates) > 1:
        found = ", ".join(parts[i] for i in dates)
        raise StemError(
            f"{len(dates)} date suffixes in {text!r} ({found}) — a stem carries "
            f"exactly one, and a new date replaces the old one rather than "
            f"being appended"
        )
    at = dates[0]
    if at != len(parts) - 1:
        raise StemError(
            f"date {parts[at]!r} is not the final segment of {text!r} — the "
            f"date is always the suffix"
        )
    base = "_".join(parts[:at])
    if not base:
        raise StemError(f"{text!r} is a bare date with no title_program base")
    return base, parts[at]


def base(value: str) -> str:
    """The immutable identity: title_program."""
    return split(value)[0]


def date(value: str) -> str:
    """The mutable state stamp."""
    return split(value)[1]


def restamp(value: str, when: str | None = None) -> str:
    """Replace the date with `when` (default today). Never appends."""
    stem_base = base(value)
    if when is None:
        when = _dt.date.today().isoformat()
    elif not DATE_RE.match(when):
        raise StemError(f"{when!r} is not a YYYY-MM-DD date")
    return f"{stem_base}_{when}"


def normalize(value: str, when: str | None = None) -> str:
    """Coerce ANY accumulated name to canonical form.

    Unlike `restamp`, this tolerates a name that already violates the one-date
    rule: the base is everything before the FIRST date segment, and every later
    date/clock segment is discarded. This exists for exactly one caller — the
    HyperFrames CLI names its output `<workspace-dir>_<date>_<clock>.mp4`, so
    the renderer's own output is malformed by construction and must be
    normalized on the way out rather than gated on the way in.
    """
    text = _strip_path(value)
    parts = text.split("_")
    first = next((i for i, p in enumerate(parts) if DATE_RE.match(p)), None)
    if first is None:
        raise StemError(f"no YYYY-MM-DD date suffix in {text!r}")
    stem_base = "_".join(parts[:first])
    if not stem_base:
        raise StemError(f"{text!r} is a bare date with no title_program base")
    if when is None:
        when = _dt.date.today().isoformat()
    elif not DATE_RE.match(when):
        raise StemError(f"{when!r} is not a YYYY-MM-DD date")
    return f"{stem_base}_{when}"


def is_canonical(value: str) -> bool:
    try:
        split(value)
    except StemError:
        return False
    return True


def check(value: str) -> tuple[bool, str]:
    """-> (ok, message). Never raises — for gate call sites."""
    try:
        b, d = split(value)
    except StemError as exc:
        return False, str(exc)
    return True, f"{b} @ {d}"


def main() -> int:
    argv = sys.argv[1:]
    when = None
    if "--date" in argv:
        i = argv.index("--date")
        if i + 1 >= len(argv):
            print("--date requires a YYYY-MM-DD value", file=sys.stderr)
            return 2
        when = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) < 2:
        print(__doc__)
        return 2
    verb, value = argv[0], argv[1]
    try:
        if verb == "base":
            print(base(value))
        elif verb == "date":
            print(date(value))
        elif verb == "restamp":
            print(restamp(value, when))
        elif verb == "normalize":
            print(normalize(value, when))
        elif verb == "check":
            b, d = split(value)
            print(f"ok: base={b} date={d}")
        else:
            print(f"unknown verb {verb!r}", file=sys.stderr)
            return 2
    except StemError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
