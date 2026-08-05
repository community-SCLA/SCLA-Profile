#!/usr/bin/env python3
"""check_forms.py — the owner's content-FORM rules, on markup instead of slots.

Two standing owner rules lived from 2026-07-29 in the retired template-family
variety checker, which read `data-variable-values` — the retired compiler's
private authoring protocol. Both would have died with the compiler, and
neither is about templates:

  one-item-list   "a list slot with exactly one item is a defect" — it draws
                  the bullet/pill illustration around a single fact. The owner's
                  words: "you would never just render a single bullet point."
                  Five scenes of the 2026-07-28 build did exactly that.
  one-card        A comparison region holding ONE card: a comparison with
                  nothing to compare, with any caption stranded beside empty
                  space. On the template path this hid from one-item-list
                  because scla-morph's two options are SCALAR slots, not a list.

Rehomed here per BUILD-PLAN step 1.3a. `check_diversity.py` could not take them
— it is a perceptual hash of beat midpoints and structurally cannot express
"this list has one item." A retirement that drops a rule to prose is a
regression even when the video improves, which is why `check-enforcement.py`
exists at all.

WHAT IT READS. Rendered markup: `<ul>`/`<ol>` element structure, which is HTML
semantics rather than any convention an author has to know, plus two DECLARED
containers for the shapes HTML has no tag for:

    data-role="list"     a list drawn as something other than <ul>/<ol>
                         (a pill row, a chip cluster, a stack of rows)
    data-role="compare"  a comparison region; its cards are the element
                         children, or those marked data-role="card"

The declared forms follow `data-role="heading"` — the freeform contract's
existing annotation — for the same reason: a gate must not guess which div is
a list, and a gate that guesses wrong reports confidently on nothing. An author
who draws a list as bare divs and declares nothing gets no grading here, and
that is a stated limit rather than a silent one: it is printed on every run.

A build with no lists at all is CLEAN, not ungraded — a lesson is allowed to
contain no list. `nothing-graded` is reserved for having no markup to read.

  python3 check_forms.py <workspace> [--json]

Exit: 0 clean · 1 a form violation · 2 bad args / nothing to read
"""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import Finding, typed  # noqa: E402

LIST_TAGS = ("ul", "ol")
# Tags that never close and so must never be pushed on the element stack —
# an unpopped <img> would swallow every sibling into a phantom subtree.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class _Forms(HTMLParser):
    """Element-structure walker.

    HTMLParser (not a regex) because "how many items does this list have"
    is a NESTING question: a regex counting <li> between <ul> and </ul> counts
    a nested list's items as the outer list's, and reports a real one-item list
    as clean. It also gives <script>/<style> CDATA handling for free, so markup
    quoted inside a JS string is never mistaken for markup.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # open elements: [tag, attrs, kids, texts]
        self.lists = []          # closed list-ish containers
        self.compares = []       # closed comparison regions

    # -- structure ----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if self.stack:
            self.stack[-1][2].append((tag, a))
        if tag in VOID:
            return
        self.stack.append([tag, a, [], []])

    def handle_startendtag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if self.stack:
            self.stack[-1][2].append((tag, a))

    def handle_data(self, data):
        if self.stack and data.strip():
            self.stack[-1][3].append(data.strip())

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] != tag:
                continue
            # Everything above `i` was left unclosed; drop it rather than
            # letting one stray </div> unwind the whole document.
            for frame in self.stack[i:]:
                self._close(frame)
            del self.stack[i:]
            return

    def close(self):
        super().close()
        for frame in reversed(self.stack):
            self._close(frame)
        self.stack = []

    # -- collection ---------------------------------------------------------
    def _close(self, frame):
        tag, attrs, kids, texts = frame
        role = attrs.get("data-role", "").strip().lower()
        text = " ".join(texts)[:80]
        if tag in LIST_TAGS:
            n = sum(1 for k, _ in kids if k == "li")
            self.lists.append({"kind": f"<{tag}>", "n": n, "text": text,
                               "id": attrs.get("id", "")})
        elif role == "list":
            n = sum(1 for k, _ in kids if k not in VOID)
            self.lists.append({"kind": 'data-role="list"', "n": n,
                               "text": text, "id": attrs.get("id", "")})
        elif role == "compare":
            cards = [k for k, ka in kids
                     if ka.get("data-role", "").strip().lower() == "card"]
            n = len(cards) if cards else sum(1 for k, _ in kids if k not in VOID)
            self.compares.append({"n": n, "text": text,
                                  "id": attrs.get("id", "")})


def _files(ws: Path):
    ws = Path(ws)
    files = sorted(ws.glob("compositions/*.html"))
    idx = ws / "index.html"
    if idx.exists():
        files.append(idx)
    return files


def check(ws: Path):
    """(report, problems). `problems` is never empty on an unreadable build:
    nothing to grade is a failure, never a pass."""
    files = _files(ws)
    if not files:
        return None, [Finding(
            "nothing-graded",
            f"no composition or index markup under {ws} — this gate can read "
            f"NOTHING. A gate that passes having looked at nothing is the most "
            f"expensive bug class in this pipeline.")]

    problems, report = [], {"files": len(files), "lists": 0, "compares": 0,
                            "declared": 0}
    for f in files:
        p = _Forms()
        p.feed(f.read_text(encoding="utf-8", errors="replace"))
        p.close()
        report["lists"] += len(p.lists)
        report["compares"] += len(p.compares)
        report["declared"] += sum(1 for L in p.lists if L["kind"] != "<ul>"
                                  and L["kind"] != "<ol>") + len(p.compares)
        for L in p.lists:
            if L["n"] != 1:
                continue
            where = f"#{L['id']}" if L["id"] else L["kind"]
            problems.append(Finding(
                "one-item-list",
                f"{f.name}: {where} is a list with exactly ONE item — it draws "
                f"the bullet/pill illustration around a single fact "
                f"({L['text']!r}). Give it >=2 items, or state the idea in a "
                f"form that is not a list."))
        for c in p.compares:
            if c["n"] >= 2:
                continue
            where = f"#{c['id']}" if c["id"] else 'data-role="compare"'
            problems.append(Finding(
                "one-card",
                f"{f.name}: {where} is a comparison region holding "
                f"{c['n']} card(s) — a comparison with nothing to compare, and "
                f"any caption is stranded beside empty space ({c['text']!r}). "
                f"Fill both sides, or state the idea in a form that is not a "
                f"comparison."))
    return report, problems


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    report, problems = check(Path(args[0]))
    if "--json" in argv:
        print(json.dumps({"pass": not problems and report is not None,
                          "report": report, "problems": problems,
                          "findings": typed(problems)}, indent=2))
    elif report is None:
        for p in problems:
            print(f"  !! {p}")
        return 2
    else:
        print(f"[forms] {report['files']} file(s): {report['lists']} list(s), "
              f"{report['compares']} comparison region(s) — "
              f"{report['declared']} declared via data-role")
        if not report["lists"] and not report["compares"]:
            # Stated, not silent: a build drawing lists as bare divs declares
            # nothing and is graded on nothing, and must say so out loud.
            print("  note: no <ul>/<ol> and no data-role=\"list\"/\"compare\" "
                  "found — if this lesson shows a list, DECLARE it or these "
                  "two owner rules grade nothing on this build")
        for p in problems:
            print(f"  !! {p}")
        print("FORMS: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
