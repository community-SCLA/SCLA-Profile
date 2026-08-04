#!/usr/bin/env python3
"""theme_for.py — which style package a program's next lesson gets.

THE ONE PLACE THAT ANSWERS THIS. It used to be a sentence in two documents
(`design-contract.md` "Style packages" and `render-lessons/SKILL.md`), and the
sentence said:

    rotate summit -> horizon -> cadence by the program's STARTED-BUILD count,
    = count(*.txt in lesson-scripts/<program>/rendered/) mod 3

which stopped being true on 2026-07-28 without anyone editing it. That was the
day a gate-clean build stopped moving its own script and publish started doing
it instead — so `rendered/` (now `published/`) went from meaning "a build was
started" to meaning "this is live on Wistia". The words "started-build count"
stayed; the folder underneath them changed meaning.

The consequence was silent and total: mid-career-momentum had 14 builds and 0
published lessons, so its count was 0, so every one of the next 12 videos would
have been assigned `summit`. A rotation that always returns the same value is
not a rotation, and nothing failed — the videos would simply all have looked
alike.

Prose that restates a computation drifts from it. Prose that cites a script
cannot, which is why both documents now point here instead of describing this.

THE COUNT IS A UNION, NOT A SUM. A published lesson's workspace survives
publication (workspaces are pruned in place, never deleted — that is a
human-only call), so adding "published rows" to "live workspaces" counts those
lessons twice and the rotation skips a package. The set of BASES that have ever
been started is what "started-build count" always meant.

Usage:
    python3 theme_for.py <program-slug>              -> the next theme
    python3 theme_for.py <program-slug> --explain    -> and how it got there
    python3 theme_for.py <program-slug> --count      -> the started-build count

Import:
    from theme_for import theme_for, started_bases
"""
import sys
from pathlib import Path

# The rotation itself. Order matters and is the contract; adding a package means
# adding a data-theme block to all twelve templates plus a row in
# design-contract.md (see "Style packages").
PACKAGES = ("summit", "horizon", "cadence")

VP = Path(__file__).resolve().parents[2]
LESSONS = VP / "lesson-scripts"
WORKSPACES = VP / "renders-hyperframes"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stem import base as stem_base, StemError


def _base(name: str) -> str:
    try:
        return stem_base(name)
    except StemError:
        return name


def published_bases(program: str, lessons: Path = None) -> set:
    """Bases this program has delivered, from published.tsv — the machine key."""
    lessons = lessons or LESSONS
    tsv = lessons / "published.tsv"
    out = set()
    if not tsv.is_file():
        return out
    for line in tsv.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) >= 2 and cols[1] == program:
            out.add(_base(cols[0]))
    return out


def workspace_bases(program: str, lessons: Path = None,
                    workspaces: Path = None) -> set:
    """Bases with a live build workspace, attributed to this program.

    A workspace name carries no program, so it is attributed by finding the
    script: the program is the folder its .txt lives in, across all three stage
    folders. Same join batch-status.sh does — a workspace can never be found by
    gluing a program onto a stem."""
    lessons = lessons or LESSONS
    workspaces = workspaces or WORKSPACES
    if not workspaces.is_dir():
        return set()
    mine = set()
    for stage in ("inbox", "ready", "published"):
        d = lessons / program / stage
        if d.is_dir():
            mine.update(_base(f.stem) for f in d.glob("*.txt"))
    out = set()
    for w in workspaces.iterdir():
        # `_` and `.` folders are scaffolding, reference material and locks —
        # never lessons. Same skip batch-status.sh uses.
        if not w.is_dir() or w.name.startswith((".", "_")):
            continue
        b = _base(w.name)
        if b in mine:
            out.add(b)
    return out


def started_bases(program: str, lessons: Path = None,
                  workspaces: Path = None) -> set:
    """Every base this program has ever STARTED a build for — the union."""
    return (published_bases(program, lessons)
            | workspace_bases(program, lessons, workspaces))


def theme_for(program: str, lessons: Path = None, workspaces: Path = None,
              offset: int = 0) -> str:
    """The package the program's next lesson gets.

    `offset` is for an orchestrator assigning several videos in one batch: the
    Nth video queued this session takes offset=N, so consecutive builds keep
    rotating instead of all reading the same pre-batch count."""
    n = len(started_bases(program, lessons, workspaces)) + offset
    return PACKAGES[n % len(PACKAGES)]


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: theme_for.py <program-slug> [--explain|--count] "
              "[--offset N]", file=sys.stderr)
        return 2
    program = argv[1]
    flags = argv[2:]
    offset = 0
    if "--offset" in flags:
        try:
            offset = int(flags[flags.index("--offset") + 1])
        except (IndexError, ValueError):
            print("--offset needs an integer", file=sys.stderr)
            return 2

    if not (LESSONS / program).is_dir():
        print(f"no such program: lesson-scripts/{program}", file=sys.stderr)
        return 2

    pub = published_bases(program)
    ws = workspace_bases(program)
    started = pub | ws

    if "--count" in flags:
        print(len(started) + offset)
        return 0
    if "--explain" in flags:
        print(f"program:        {program}")
        print(f"published:      {len(pub)}")
        print(f"live workspaces:{len(ws):>3}  ({len(pub & ws)} of them also published)")
        print(f"started (union):{len(started):>3}"
              + (f"  + offset {offset}" if offset else ""))
        print(f"rotation:       {' -> '.join(PACKAGES)}")
        print(f"theme:          {theme_for(program, offset=offset)}")
        return 0
    print(theme_for(program, offset=offset))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
