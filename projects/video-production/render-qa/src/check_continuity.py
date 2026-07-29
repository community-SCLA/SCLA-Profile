#!/usr/bin/env python3
"""check_continuity.py — one thought per scene. No thought split across scenes.

The 2026-07-28 `better-decisions` build passed every gate in the pipeline and
the owner rejected it for reasons no checker had an opinion about:

  "Slides 10, 11, and 12 really should all be a single slide. Spreading the same
   thought across several different slides and rendering them in different
   styles is not what we're going for."
  "Having a simple statement on a single frame doesn't make sense, it needs to
   be folded into another slide. Otherwise it just feels like a blip... don't
   spread a single sentence across multiple frames."

Nothing graded scene CONTENT WEIGHT. check_boundaries verified the cut landed on
a sentence terminator — and it did, because "Growth?" is a punctuated fragment.
check_variety graded template distribution. check_copy graded the words. A scene
carrying two words was structurally invisible.

Worse, fragmentation actively DISABLED the rule the owner has repeated most: a
seven-item list split across three scenes leaves runs of 2/2/2, so check_copy's
">=3 items need a conjunction" test never fired on any of them. (That test now
runs on the joined narration stream — check_copy.py, same date. This file owns
the split itself.)

Three rules:

  1. SPLIT SENTENCE. A scene whose narration opens with a coordinating
     conjunction (But / And / Or / So / Yet / Nor) or a lowercase word is the
     back half of the previous scene's sentence, given its own frame. The
     2026-07-28 build did this twice: scene-07 "Or they stay committed to a
     path..." and scene-22 "But it should not make the decision for you."
     Merge it into the scene before it.

  2. BLIP. A content scene must carry a real beat. Post-compile the test is
     DURATION (< MIN_SCENE_SEC); at plan stage, before compile_timeline has
     resolved real durations, it falls back to a word-count proxy. On the
     rejected build a 4.5s line separates every scene the owner objected to
     (2.2-3.9s) from every scene they did not (4.8-11.1s).
     The proxy is deliberately conservative — it under-flags rather than
     false-flags, because the authoritative test runs post-compile anyway.

  3. ENUMERATION SPANS SCENES. Two or more consecutive scenes built only of
     short parallel fragments sharing a terminator are one spoken list cut into
     pieces. The viewer hears "Security? Income? Flexibility? Meaning?
     Mentorship? Growth?" as one question; rendering it as three slides in three
     different styles is the defect the owner named first.

Chrome scenes (title, outro) are exempt from 2 and 3 — they frame the lesson
rather than carry a beat of it. Rule 1 applies everywhere.

Usage:  python3 check_continuity.py <workspace> [--json] [--static]
Exit:   0 clean · 1 violations · 2 bad args
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import Finding, get_attr, parse_scenes, typed

# Forms that frame the lesson rather than carry a beat (mirrors check_variety).
CHROME = {"scla-title", "scla-outro"}

# A scene shorter than this is a blip, not a beat. Calibrated on the rejected
# 2026-07-28 build: every scene the owner objected to fell at 2.18-3.86s, every
# scene they did not at 4.75-11.07s. Pinned by tests/test_continuity.py.
MIN_SCENE_SEC = 4.5

# Plan-stage proxy. Measured narration rate on the reference build is ~2.65
# words/sec including boundary air, so MIN_SCENE_SEC is ~12 words. Under-flags
# by design (a 12-word scene can still compile short) — rule 2's duration form
# is authoritative and runs before any render is spent.
WORDS_PER_SEC = 2.65
MIN_WORDS = int(MIN_SCENE_SEC * WORDS_PER_SEC)

# Openers that make a scene the back half of the previous scene's sentence.
COORDINATORS = ("but", "and", "or", "so", "yet", "nor")
# Below this, a conjunction-opening single clause is a dangling tail; at or above
# it, the clause carries a beat of its own. See split_sentence_problems().
COORDINATOR_MAX_WORDS = 15
WORD_RX = re.compile(r"[A-Za-z][A-Za-z'’]*")


def _fragments(narration: str):
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+", (narration or "").strip())
            if p.strip()]


def _terminator(frag: str) -> str:
    m = re.search(r"[.?!]", frag[::-1])
    return frag[::-1][m.start()] if m else ""


def _template(scene) -> str:
    src = get_attr(scene["tag"], "data-composition-src") or ""
    # Instanced clones are `scla-chips__i3.html` — the family is the stem.
    return Path(src).stem.split("__")[0]


def _words(narration: str):
    return WORD_RX.findall(narration or "")


def split_sentence_problems(scenes):
    """Rule 1 — a scene that opens mid-sentence."""
    problems = []
    for i, s in enumerate(scenes):
        text = (s["narration"] or "").strip()
        if not text or i == 0:
            continue
        first = WORD_RX.search(text)
        if not first:
            continue
        word = first.group(0)
        lead = text[: first.start()]
        prev = scenes[i - 1]["id"]
        # A scene may OPEN on a contrast if it then develops the thought — two
        # or more sentences is a beat of its own, not a dangling tail. Only an
        # undeveloped single clause is the back half of the previous scene.
        # Without this, scene-04 ("But most strong career decisions do not come
        # from finding a perfect answer. They come from choosing among...") —
        # 27 words over two sentences and 9.9s on screen — was flagged as a
        # fragment alongside the real ones.
        # ...and only when the clause is SHORT. Calibrated against the owner's
        # own judgment on the 2026-07-28 build: they rejected scene-22 ("But it
        # should not make the decision for you." — 9 words, 2.5s) and said
        # nothing about scene-07 ("Or they stay committed to a path because they
        # have already invested time into it, even if it is no longer the best
        # fit." — 24 words, 6.6s), which is the third item of a list and carries
        # its own weight. A long clause that opens on a conjunction is a beat; a
        # short one is a dangling tail. Without this the gate also fought the
        # pacing cap: that 24-word item cannot merge upward without pushing its
        # scene past the 12.5s duration ceiling.
        if (word.lower() in COORDINATORS and len(_fragments(text)) == 1
                and len(WORD_RX.findall(text)) < COORDINATOR_MAX_WORDS):
            problems.append(Finding(
                "split-sentence",
                f"{s['id']}: a single clause opening with {word!r} — this is "
                f"either the back half of {prev}'s sentence or the final item "
                f"of a list {prev} started, given its own frame. "
                f"Merge it into {prev}. ({text[:60]!r})"))
        elif word[0].islower() and not lead.strip():
            problems.append(Finding(
                "opens-lowercase",
                f"{s['id']}: narration opens lowercase ({word!r}) — the "
                f"sentence starts in {prev}. Merge it into {prev}. "
                f"({text[:60]!r})"))
    return problems


def blip_problems(scenes, static=False):
    """Rule 2 — a content scene that carries no real beat."""
    problems = []
    for s in scenes:
        if _template(s) in CHROME:
            continue
        text = (s["narration"] or "").strip()
        if not text:
            continue
        words = _words(text)
        dur = s.get("duration")
        # A placeholder duration (pre-compile) is not evidence; use the proxy.
        usable = (not static and isinstance(dur, (int, float))
                  and dur == dur and dur > 0)
        if usable:
            if dur < MIN_SCENE_SEC:
                problems.append(Finding(
                    "scene-blip",
                    f"{s['id']}: {dur:.2f}s on screen — under the "
                    f"{MIN_SCENE_SEC}s floor, so it reads as a blip rather than "
                    f"a beat. Fold it into an adjacent scene. ({text[:60]!r})"))
        elif len(words) < MIN_WORDS:
            problems.append(Finding(
                "too-few-words",
                f"{s['id']}: {len(words)} spoken words — under the {MIN_WORDS}-word "
                f"plan-stage floor (~{MIN_SCENE_SEC}s). Fold it into an adjacent "
                f"scene. ({text[:60]!r})"))
    return problems


def enumeration_span_problems(scenes):
    """Rule 3 — one spoken list cut across consecutive scenes."""
    problems = []
    run = []  # scenes that are pure short-fragment lists sharing a terminator

    def close():
        if len(run) >= 2:
            ids = ", ".join(s["id"] for s in run)
            items = [f for s in run for f in _fragments(s["narration"])]
            problems.append(Finding(
                "list-split-across-scenes",
                f"{run[0]['id']}: one spoken list of {len(items)} items is split "
                f"across {len(run)} scenes ({ids}) — "
                f"{', '.join(repr(i) for i in items[:4])}"
                f"{'...' if len(items) > 4 else ''}. The viewer hears one list; "
                f"render it as one scene."))
        run.clear()

    for s in scenes:
        frags = _fragments(s["narration"])
        is_list = (
            _template(s) not in CHROME
            and len(frags) >= 1
            and all(len(_words(f)) <= 5 for f in frags)
            and len({_terminator(f) for f in frags}) == 1
        )
        if is_list and (not run or _terminator(frags[0])
                        == _terminator(_fragments(run[-1]["narration"])[0])):
            run.append(s)
        else:
            close()
            if is_list:
                run.append(s)
    close()
    return problems


def check(ws: Path, static=False):
    scenes = parse_scenes((ws / "index.html").read_text(
        encoding="utf-8", errors="replace"))
    if not scenes:
        return ["no scene slots found in index.html"]
    return (split_sentence_problems(scenes)
            + blip_problems(scenes, static=static)
            + enumeration_span_problems(scenes))


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    ws = Path(args[0]).resolve()
    problems = check(ws, static="--static" in argv)
    if "--json" in argv:
        print(json.dumps({"pass": not problems, "problems": problems,
                          "findings": typed(problems)}, indent=2))
    else:
        for p in problems:
            print(f"  !! {p}")
        print("CONTINUITY: " + ("PASS" if not problems
                                else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
