#!/usr/bin/env python3
"""check_copy.py — standing owner rules about the words themselves.

Two rules, both given repeatedly as feedback and neither previously written
anywhere a machine could read (owner, 2026-07-28: "I have given preferences
that, for whatever reason, have not been recorded down and not enforced").

  1. HEADINGS ARE TITLE CASE. On-frame headings are headings, not prose. Every
     principal word is capitalised; articles, coordinating conjunctions and
     short prepositions stay lowercase unless they lead or close the heading.
     A heading also carries no terminal period (? and ! are fine) — the
     2026-07-28 build mixed "The sunk cost problem is especially common." with
     "Broaden your options" on adjacent scenes.

  2. ENUMERATIONS TAKE A CONJUNCTION. A spoken list of three or more items
     needs "and" or "or" before the final item. Without it the narration just
     stops, and the listener cannot hear that the list ended. This is a
     NARRATION rule (checked against data-narration), not a chip-label rule —
     chips may stay bare.
     e.g. "Meaning? Mentorship? Growth?" -> "Meaning? Mentorship? Or growth?"
          "The right city. The right path." -> "...or the right path."

Usage:  python3 check_copy.py <workspace> [--json]
Exit:   0 clean · 1 violations · 2 bad args
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import parse_scenes

# Slots that render as an on-frame heading.
HEADING_SLOTS = ("heading", "statement", "title")

# Words that stay lowercase mid-heading (articles, coordinators, short preps).
MINOR = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "if", "in",
    "into", "nor", "of", "off", "on", "onto", "or", "over", "per", "so",
    "the", "to", "up", "via", "vs", "with", "yet",
}
WORD_RX = re.compile(r"[A-Za-z][A-Za-z'’]*")
CONJ_RX = re.compile(r"\b(and|or)\b", re.I)


def _cap(word: str, force: bool) -> str:
    """Capitalise one word unless it is a minor word mid-heading."""
    # Leave acronyms and intentional inner caps alone (AI, SCLA, iOS).
    if any(c.isupper() for c in word[1:]):
        return word
    if not force and word.lower() in MINOR:
        return word.lower()
    return word[:1].upper() + word[1:]


def titlecase(text: str) -> str:
    """The expected Title Case form, preserving punctuation and acronyms."""
    tokens = re.split(r"(\s+)", text)
    carriers = [i for i, t in enumerate(tokens) if WORD_RX.search(t)]
    out = list(tokens)
    for pos, i in enumerate(carriers):
        # First and last word are always capitalised, whatever they are.
        force = pos == 0 or pos == len(carriers) - 1
        # Hyphenated compounds capitalise every part ("Long-Term", "Self-Aware").
        parts = tokens[i].split("-")
        out[i] = "-".join(
            re.sub(WORD_RX, lambda m: _cap(m.group(0), force or j > 0), part,
                   count=1)
            for j, part in enumerate(parts))
    return "".join(out)


def heading_problems(scenes):
    problems = []
    for s in scenes:
        for slot in HEADING_SLOTS:
            raw = (s["variables"].get(slot) or "").strip()
            if not raw:
                continue
            body = raw.rstrip()
            if body.endswith("."):
                problems.append(
                    f"{s['id']} '{slot}': heading ends in a period — "
                    f"{raw!r}. Headings take no terminal period.")
                body = body[:-1].rstrip()
            want = titlecase(body)
            if want != body:
                problems.append(
                    f"{s['id']} '{slot}': not Title Case.\n"
                    f"      is:     {body!r}\n"
                    f"      should: {want!r}")
    return problems


def _items(narration: str):
    """Split narration into the fragments a listener hears as list items."""
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+", narration.strip())
            if p.strip()]


def enumeration_problems(scenes):
    problems = []
    for s in scenes:
        text = (s["narration"] or "").strip()
        if not text:
            continue

        # (a) run of >=3 short parallel fragments, e.g. "Income? Meaning? Growth?"
        frags = _items(text)
        run = []
        for frag in frags + [""]:
            words = WORD_RX.findall(frag)
            if frag and len(words) <= 5:
                run.append(frag)
                continue
            if len(run) >= 3 and not CONJ_RX.search(run[-1]):
                problems.append(
                    f"{s['id']}: spoken list of {len(run)} items ends without "
                    f"'and'/'or' — ...{run[-2]!r} {run[-1]!r}. Add the "
                    f"conjunction to the final item.")
            run = []

        # (b) comma list of >=3 inside one sentence.
        #     Commas also separate clauses and introduce quoted speech, which
        #     are NOT lists — "someone thinks, "I already put so much time into
        #     this, I cannot change now," even when the fit is weak" tripped the
        #     naive version. Two discriminators keep those out: real list items
        #     are short, and a sentence carrying quoted speech is reported
        #     speech rather than an enumeration.
        for sentence in frags:
            if '"' in sentence or "“" in sentence:
                continue
            parts = [p.strip() for p in sentence.split(",") if p.strip()]
            if len(parts) < 3 or any(len(WORD_RX.findall(p)) > 6 for p in parts):
                continue
            if not CONJ_RX.search(parts[-1]):
                problems.append(
                    f"{s['id']}: comma list of {len(parts)} items ends without "
                    f"'and'/'or' — ...{parts[-1]!r}. Add the conjunction to "
                    f"the final item.")
    return problems


def check(ws: Path):
    scenes = parse_scenes((ws / "index.html").read_text())
    if not scenes:
        return ["no scene slots found"]
    return heading_problems(scenes) + enumeration_problems(scenes)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    ws = Path(args[0]).resolve()
    problems = check(ws)
    if "--json" in sys.argv[1:]:
        print(json.dumps({"pass": not problems, "problems": problems}, indent=2))
    else:
        for p in problems:
            print(f"  !! {p}")
        print("COPY: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
