#!/usr/bin/env python3
"""stem.py — the single owner of lesson-stem naming.

A lesson's identity is `<title>_<program>` — the **base**. That is the name of
every working artifact, and it never changes.

  working    lesson-scripts/<prog>/<base>.txt           raw
             lesson-scripts/<prog>/refined/<base>.txt   queued to build
             renders-hyperframes/<base>/                build workspace
             lesson-scripts/<prog>/rendered/<base>.txt  gate-clean build exists
  delivered  renders-mp4/<prog>/**/<base>_<DATE>.mp4    render date, frozen

Two rules, and everything else follows:

  1. A working artifact carries NO date. Its name IS its identity, so the
     directory entry is the lock: `mkdir renders-hyperframes/<base>` succeeds
     exactly once, which is what makes concurrent builds safe. A name-based
     "does this already exist?" check cannot be defeated by a name that moves,
     because the name no longer moves.
  2. Only a DELIVERED artifact carries a date, and it means the date it was
     rendered — a fact about an event that happened once. It is frozen at
     publish and never restamped.

"When was this last acted on" is mtime. The filesystem tracks it natively and
cannot drift; a date suffix maintained by code is denormalized mtime, and it
drifted (2026-07-29: the same lesson held two workspaces, `..._2026-07-28` and
`..._2026-07-29`, because a rebuild restamped its way into a second directory
instead of reusing the first).

`base()` is tolerant by construction: it strips any trailing date and render-
clock segments, so it accepts a legacy dated name, an accumulated
`..._2026-07-06_2026-07-28_18-49-26`, and a bare base alike. That tolerance is
what let the convention be dropped without a flag day.

CLI:
    python3 stem.py base      <stem|path>            -> title_program
    python3 stem.py date      <stem|path>            -> YYYY-MM-DD (exit 1 if none)
    python3 stem.py delivered <stem|path> [--date D] -> title_program_D  (D=today)
    python3 stem.py check     <stem|path>            -> exit 0 if a canonical
                                                        WORKING name (no date)
Exit 2 on a name with no usable base, with the reason on stderr.
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
    """A name with no usable `<title>_<program>` base."""


def _strip_path(value: str) -> str:
    """Accept a bare stem, a filename, or a full path."""
    text = str(value).strip().rstrip("/")
    if "/" in text:
        text = Path(text).name
    for suffix in (".mp4", ".txt", ".json", ".wav"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return text


def _parts(value: str) -> list[str]:
    text = _strip_path(value)
    if not text:
        raise StemError("empty stem")
    return text.split("_")


def base(value: str) -> str:
    """The identity: `title_program`, with every trailing date/clock removed.

    Tolerant on purpose — legacy dated names, the renderer's accumulated
    `_<date>_<clock>` output, and an already-bare base all resolve to the same
    string. Only TRAILING segments are stripped, so a date-like segment inside
    a title is left alone.
    """
    parts = _parts(value)
    while len(parts) > 1 and (DATE_RE.match(parts[-1]) or CLOCK_RE.match(parts[-1])):
        parts.pop()
    stem_base = "_".join(parts)
    if not stem_base or DATE_RE.match(stem_base) or CLOCK_RE.match(stem_base):
        raise StemError(f"{_strip_path(value)!r} has no title_program base")
    return stem_base


def date(value: str) -> str | None:
    """The render date of a DELIVERED artifact, or None for a working one."""
    parts = _parts(value)
    while len(parts) > 1 and CLOCK_RE.match(parts[-1]):
        parts.pop()
    if len(parts) > 1 and DATE_RE.match(parts[-1]):
        return parts[-1]
    return None


def delivered(value: str, when: str | None = None) -> str:
    """`<base>_<when>` — the name of a delivered artifact. Never appends.

    The one naming transition left in the pipeline: a working artifact becomes
    a delivered MP4 and gains the render date at that moment. Callers are
    `batch-ship.sh` (filing the MP4) and nothing else.
    """
    stem_base = base(value)
    if when is None:
        when = _dt.date.today().isoformat()
    elif not DATE_RE.match(when):
        raise StemError(f"{when!r} is not a YYYY-MM-DD date")
    return f"{stem_base}_{when}"


def is_canonical(value: str) -> bool:
    """True if `value` is a canonical WORKING name: a base with no date."""
    try:
        return base(value) == _strip_path(value)
    except StemError:
        return False


def check(value: str) -> tuple[bool, str]:
    """-> (ok, message). Never raises — for gate call sites."""
    try:
        b = base(value)
    except StemError as exc:
        return False, str(exc)
    if b != _strip_path(value):
        return False, (
            f"{_strip_path(value)!r} carries a date suffix; a working artifact "
            f"is named for its base alone ({b!r}). Only a delivered MP4 is dated."
        )
    return True, b


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
            d = date(value)
            if d is None:
                print(f"{value!r} carries no date (working artifact)", file=sys.stderr)
                return 1
            print(d)
        elif verb == "delivered":
            print(delivered(value, when))
        elif verb == "check":
            ok, msg = check(value)
            if not ok:
                print(f"FATAL: {msg}", file=sys.stderr)
                return 2
            print(f"ok: base={msg}")
        elif verb in ("restamp", "normalize"):
            print(
                f"FATAL: `{verb}` was removed on 2026-07-29 — working artifacts "
                f"no longer carry a date, so there is nothing to restamp. Use "
                f"`base` for a workspace/script name, or `delivered` for the "
                f"filed MP4. (decisions/log.md)",
                file=sys.stderr)
            return 2
        else:
            print(f"unknown verb {verb!r}", file=sys.stderr)
            return 2
    except StemError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
