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

    # (a) run of >=3 short parallel fragments, e.g. "Income? Meaning? Growth?"
    #
    # THE RUN IS DETECTED ACROSS THE WHOLE NARRATION STREAM, NOT PER SCENE
    # (2026-07-29). Scoping this per scene silently disabled the rule the owner
    # has given more often than any other: the 2026-07-28 build split
    #   "Do you care most about learning? Security? Income? | Flexibility?
    #    Meaning? | Mentorship? Growth?"
    # across scenes 11/12/13, leaving runs of 2, 2 and 2 — never reaching the
    # >=3 threshold in any single scene, so the missing conjunction on "Growth?"
    # sailed through a gate written precisely to catch it. Same for scenes 2/3
    # ("The right job. The right major. | The right city. The right path.").
    # A viewer hears one list; the checker must grade one list. The violation is
    # attributed to the scene owning the FINAL item, which is where the
    # conjunction has to go.
    #
    # (The scene split is itself a defect — check_continuity.py owns that.)
    stream = [(s["id"], frag)
              for s in scenes
              for frag in _items((s["narration"] or "").strip())]
    # A run of short sentences is not automatically a list. Rhetorical pairs and
    # triads look identical to a length test — "That's the whole game." "Let's
    # build your roadmap." / "You don't apologize for it." "You claim it." —
    # and forcing an "or" into those would be wrong. Real list items are
    # PREDICATE-FREE: noun phrases ("The right job.") or bare questions
    # ("Security?"). An item with its own subject and verb is a sentence, so it
    # ends the run rather than joining it. Found by sweeping the 32-script
    # library, where a pure length test flagged 17 scripts and a visible share
    # of those were rhetoric, not enumeration.
    SUBJECTS = {"i", "you", "we", "they", "he", "she", "it", "that", "this",
                "there", "both", "each", "these", "those", "everyone", "nobody"}
    CONTRACTION_RX = re.compile(r"'(s|ll|ve|re|d|t)\b|n't\b", re.I)

    def _is_sentence(frag):
        words = WORD_RX.findall(frag)
        if not words:
            return False
        return (words[0].lower() in SUBJECTS
                or bool(CONTRACTION_RX.search(frag)))

    def _term(frag):
        """The item's terminal mark. Items in one spoken list share it: a run of
        '?' fragments is one question list, and a '.' fragment after them is the
        next thought, not its final item. Without this, 'Mentorship? Growth?'
        absorbed the following scene's 'Second, broaden your options.' (4 words,
        under the length gate) and mis-blamed that scene for the missing
        conjunction."""
        m = re.search(r"[.?!]", frag[::-1])
        return frag[::-1][m.start()] if m else ""

    run = []
    for sid, frag in stream + [(None, "")]:
        if frag and len(WORD_RX.findall(frag)) <= 5 and not _is_sentence(frag):
            if run and _term(frag) != _term(run[0][1]):
                pass  # terminator switch closes the run below, then restarts it
            else:
                run.append((sid, frag))
                continue
        if len(run) >= 3 and not CONJ_RX.search(run[-1][1]):
            spans = sorted({r[0] for r in run}, key=[r[0] for r in run].index)
            across = (f" (the list runs across {len(spans)} scenes: "
                      f"{', '.join(spans)} — merge them)" if len(spans) > 1
                      else "")
            problems.append(
                f"{run[-1][0]}: spoken list of {len(run)} items ends without "
                f"'and'/'or' — ...{run[-2][1]!r} {run[-1][1]!r}. Add the "
                f"conjunction to the final item{across}.")
        # A terminator switch both closes the old run and opens a new one.
        run = ([(sid, frag)]
               if frag and len(WORD_RX.findall(frag)) <= 5
               and not _is_sentence(frag) else [])

    # (c) a DANGLING CONJUNCTION FRAGMENT — the conjunction rule's own blast
    #     radius. Rule (a) says a spoken list needs "and"/"or" before its final
    #     item, and the cheapest way to satisfy it is to bolt the word onto the
    #     front of the last fragment: "The right job. The right major. The right
    #     city. Or the right path." That passes (a) and sounds wrong. Oxana
    #     reads a predicate-free fragment closed by a period with rising,
    #     unfinished intonation — the owner heard scene-02 of the 2026-07-29
    #     build as "she didn't complete the sentence… ended on a question mark".
    #     A list that takes a conjunction has to become ONE sentence:
    #         "The right job, the right major, the right city, or the right path."
    #     Question lists are exempt and deliberately so: "Security? Income? Or
    #     growth?" is how the rising list is meant to sound, and comma-joining it
    #     would destroy the very inflection that makes it work. The terminal mark
    #     is the discriminator, which is why this grades '.' only.
    DANGLING_RX = re.compile(r"^(and|or|but|nor)\b", re.I)
    # `_is_sentence` keys on a leading pronoun, which a conjunction hides:
    # "But titles are only labels." is a complete sentence and read as a
    # fragment by that test alone. A finite verb anywhere in the run is the
    # cheap, honest discriminator — no POS tagger, and it fails toward silence
    # rather than toward nagging. A library sweep put this at 3 flags in 32
    # refined scripts, all of them real.
    FINITE = {"is", "are", "was", "were", "am", "be", "been", "has", "have",
              "had", "do", "does", "did", "can", "could", "will", "would",
              "shall", "should", "may", "might", "must", "get", "gets", "got",
              "go", "goes", "come", "comes", "make", "makes", "mean", "means",
              "need", "needs", "take", "takes", "stay", "stays", "look",
              "looks", "feel", "feels", "seem", "seems", "become", "becomes"}
    for s in scenes:
        frags_c = _items((s["narration"] or "").strip())
        for pos, frag in enumerate(frags_c):
            # Only the LAST fragment of the run can dangle. Mid-paragraph, a
            # short conjunction fragment is a topic label that the next sentence
            # immediately completes — "And working with AI. Knowing how to
            # prompt it, check it, and combine its outputs… is a baseline skill."
            # — and that reads correctly aloud. What the owner heard on
            # scene-02 was a fragment with NOTHING after it: the paragraph, and
            # the scene, simply stopped mid-thought. Both live scripts that this
            # rule flagged before the positional test were of the harmless kind.
            if pos != len(frags_c) - 1:
                continue
            if not DANGLING_RX.match(frag.strip()) or not frag.rstrip().endswith("."):
                continue
            # Same two discriminators rule (a) uses, for the same reason: a
            # LONG clause opening with "But" is ordinary prose ("But it should
            # not make the decision for you."), and so is anything carrying its
            # own subject. Only a short predicate-free fragment is a list item
            # that has been given a full stop it cannot carry.
            words = WORD_RX.findall(frag)
            if (_is_sentence(frag) or len(words) > 5
                    or any(w.lower() in FINITE for w in words)):
                continue
            problems.append(
                f"{s['id']}: {frag!r} is a dangling conjunction fragment — a "
                f"list item wearing a full stop. It reads as an unfinished "
                f"sentence. Join the run into ONE sentence with commas "
                f"(\"a, b, c, or d.\") instead of bolting the conjunction onto "
                f"a separate fragment.")

    for s in scenes:
        text = (s["narration"] or "").strip()
        if not text:
            continue
        frags = _items(text)

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


def check_script(path: Path):
    """Grade a refined lesson script (.txt) — enumeration rules only.

    This is where the rule actually belongs (2026-07-29). The missing "or" the
    owner reported on the 2026-07-28 build was not introduced by the builder:
    line 1 of the approved script reads "The right job. The right major. The
    right city. The right path." and line 13 "...Meaning? Mentorship? Growth?".
    The render pipeline faithfully spoke a script that was already wrong, and
    the render gate could only report it after a video existed.

    Catching it at /refine-scripts means the script arrives render-ready, and
    the fix is a text edit instead of a re-synthesis + re-render. Heading rules
    do not apply here — a script has narration, not on-frame headings.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    scenes = [{"id": f"line {i}", "narration": p, "variables": {}}
              for i, p in enumerate(paragraphs, 1)]
    return enumeration_problems(scenes)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    target = Path(args[0]).resolve()
    if "--script" in sys.argv[1:] or target.suffix == ".txt":
        problems = check_script(target)
    else:
        problems = check(target)
    if "--json" in sys.argv[1:]:
        print(json.dumps({"pass": not problems, "problems": problems}, indent=2))
    else:
        for p in problems:
            print(f"  !! {p}")
        print("COPY: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
