#!/usr/bin/env python3
"""check_variety.py — the frame must not repeat itself.

frame.md has carried a "variety rule" since Motion v2 (2026-07-27) as prose:
max 2 consecutive scenes of one template, >=5 distinct forms per lesson,
illustration-capable templates for concrete narration. Prose did not hold. The
2026-07-28 `better-decisions` build put 21 scenes on 5 templates — 8 of them
scla-statement, an unbroken run of 5 near-identical scla-condition/chips slides
— and every existing gate passed it. The owner's verdict was "boring, doesn't
have a lot of visual variety". This makes the rule a gate.

Seven rules (5 documented inline at their code, 6-7 added 2026-07-28):

  1. NO ONE-ITEM LIST. A list slot that resolves to exactly one item renders
     the bullet/pill/point illustration around a single fact. You would never
     render a single bullet point. Either the scene has a real list (>=2) or it
     should not be using a list-bearing form at all. (0 items = slot correctly
     blanked, which check_slots.py governs.)

  2. MAX 2 CONSECUTIVE scenes may share a template family. Three in a row is
     the same slide three times to a viewer.

  3. MIN DISTINCT FORMS across the content scenes (title/outro excluded),
     scaled to runtime — a 160s lesson on 4 forms is a slideshow.

  4. NO FORM EXCEEDS `MAX_SHARE` of the content SECONDS (falling back to scene
     count only pre-compile, where durations are placeholders). Passing rules 2
     and 3 while putting 42% of the video on one template still reads as
     monotony.

  6. THEME-BLOCK CAP. No more than MAX_CANVAS_RUN consecutive content scenes,
     and no more than MAX_CANVAS_SECONDS continuously, on one background
     canvas (light vs navy). Template variety is not canvas variety: the
     rejected build sat 9 consecutive scenes / 78.3s on the light canvas. The
     seconds half skips gracefully pre-compile (data-duration is a placeholder
     until compile_timeline runs; this gate also fires at plan stage) — the
     scene-count half always enforces.

  7. COMPOSITION (TWO-REGION) COVERAGE. At least MIN_TWO_REGION_SHARE of the
     content scenes must place content in two spatially separate regions —
     a split panel, a heading band over a diagram, or a text column beside a
     right-side living-icon hero. The reference does this on ~35% of scenes;
     the rejected build on 0% (every scene one centered block of type).

Unused templates are reported as info, not failure — they are the builder's
menu of remaining options, not an obligation.

Usage:  python3 check_variety.py <workspace> [--json]
Exit:   0 clean · 1 violations · 2 bad args
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import parse_scenes, get_attr

# Forms that frame the lesson rather than carry a beat of it.
CHROME = {"scla-title", "scla-outro"}

# Slots whose value is a delimited list, and the delimiter that splits them.
LIST_SLOTS = {
    "chips": ",",
    "lines": "|",
    "subBeats": "|",
    "bullets": "|",
}
# Numbered slot families: point1..point4, item1..item4, ...
NUMBERED_SLOTS = ("point", "item", "step", "card")

# Thresholds calibrated 2026-07-28 against the owner's named reference video,
# what-makes-for-a-dream-job (Wistia gryylc7qns, 187.5s) — "great movement,
# great pacing, great illustrations" — measured frame by frame. A gate that
# rejects the reference is a broken gate, so every number below is set to PASS
# that video and FAIL the rejected better-decisions build:
#
#                                   reference (pass)   rejected (fail)
#   distinct content forms            6 families         4 families
#   largest single-form share         36%                42%
#   scenes carrying artwork           79%                33%
#   distinct artwork assets           ~11                6 (one reused)
#   longest same-family run           5 (exempt, below)  3 (not exempt)
MIN_FORMS_SHORT = 4      # lessons < LONG_SECONDS
MIN_FORMS_LONG = 6       # >= LONG_SECONDS   (was 5; reference has 6)
MIN_FORMS_EPIC = 7       # >= EPIC_SECONDS
LONG_SECONDS = 90
EPIC_SECONDS = 150
MAX_CONSECUTIVE = 2
MAX_SHARE = 0.40         # reference peaks at 36% — do NOT tighten past this

# A long run of ONE template is not automatically monotony. The reference's
# best passage is five consecutive condition scenes, and it works because each
# one carries different artwork, advances a visible progress indicator, and
# gets out fast. A run may extend to RUN_EXEMPT_MAX only if EVERY scene in it
# satisfies all three. A run with no progress indicator — every statement run
# in the rejected build — stays capped at MAX_CONSECUTIVE.
RUN_EXEMPT_MAX = 6
RUN_EXEMPT_MAX_DURATION = 7.0

# Artwork: the largest measured gap between the two videos (79% vs 33%), and
# entirely ungated until now. "Boring" is mostly this.
MIN_ARTWORK_SHARE = 0.60
MIN_DISTINCT_ASSETS = 5
MAX_ASSET_REUSE = 2
MAX_CONSECUTIVE_BARE = 2

# Slots that carry artwork rather than copy.
ART_SLOTS = ("icon", "icons")
# Slots that mark a scene's position in an enumerated series.
PROGRESS_SLOTS = ("num", "total", "step", "stepIndex")

# --- rule 6: theme-block cap ------------------------------------------------
# Template -> background canvas, derived 2026-07-28 by reading each
# design-system/compositions/scla-*.html base background. Navy templates open
# on the radial dark-navy token (#0d2437 -> #0a1e2f); light templates open on
# paper/cultured (#ffffff / #f6f6f9). Two judged calls, both from the markup
# and frame.md's template table:
#   scla-quote — a NAVY CARD sitting ON a light canvas (.q-bg is #f6f6f9)
#       -> "light".
#   scla-stat  — split frame: 820px navy panel left, light field right
#       -> "split", which matches NEITHER canvas and so breaks both runs.
# THIS DICT IS THE ONE PLACE the map lives. Freshness: tests/test_variety.py
# greps every template's first `background:` declaration against this map, so
# a template edit that flips a canvas breaks the test loudly instead of
# silently rotting the map.
CANVAS = {
    "scla-title": "navy",
    "scla-statement": "navy",
    "scla-outro": "navy",
    "scla-quote": "light",
    "scla-stat": "split",
    "scla-chips": "light",
    "scla-condition": "light",
    "scla-career-map": "light",
    "scla-loop": "light",
    "scla-morph": "light",
    "scla-points": "light",
    "scla-steps": "light",
}
# Calibration (2026-07-28): the rejected build ran 9 consecutive light scenes
# over 78.3s — both caps are set to fail it. The reference's only comparable
# light stretch (9 scenes / 78s in the fixture) is bisected by its EXEMPT
# five-scene condition series (advancing stepper, distinct artwork, <=6s
# each), which is why a rule-2-exempt enumerated run also breaks the canvas
# run below: measured on canvas alone the two videos are identical, and a gate
# that rejects the owner's reference is a broken gate. What separates them is
# whether the stretch contains a certified-varied series.
MAX_CANVAS_RUN = 6
MAX_CANVAS_SECONDS = 65.0

# --- rule 7: composition (two-region) coverage --------------------------------
# Classified from each template's actual layout markup (read 2026-07-28):
#   ALWAYS two-region —
#     scla-stat        #sh-panel: full-height 820px navy panel left, light
#                      context column right (split frame)
#     scla-steps       #st-panel heading band on top, step track + nodes +
#                      captions as a separate diagram band below
#     scla-loop        #lp-panel heading band on top, oval ring diagram below
#     scla-career-map  #cm-head heading block over the #cm-stage route map
#   TWO-REGION WHEN THE ICON HERO IS FILLED —
#     scla-condition   left text column + #cd-iconwrap hero at x=1370
#     scla-statement   #sm-iconwrap hero at x=1400 (block narrows when set)
#     scla-chips       #cc-iconwrap hero at x=1430 (chip column narrows)
#   NEVER two-region (verified, not guessed) —
#     scla-morph       `icons` renders INSIDE each card, same region
#     scla-points      `icons` renders inline per list row (.kp-icon,
#                      margin-left:auto), same region; #kp-rail is furniture
#     scla-quote / scla-title / scla-outro — no icon slot, one block
# Calibration: reference fixture = 6/14 content scenes (43%; the real video
# measured ~35% frame by frame) — PASSES. Rejected = 0/19 (0%) — FAILS. Both
# land decisively on their side of the threshold, so this is a HARD GATE.
TWO_REGION_ALWAYS = {"scla-stat", "scla-steps", "scla-loop", "scla-career-map"}
TWO_REGION_ICON_HERO = {"scla-condition", "scla-statement", "scla-chips"}
MIN_TWO_REGION_SHARE = 0.25   # reference 43% (fixture) / ~35% (measured); rejected 0%


def family(src: str) -> str:
    """compositions/scla-statement__i3.html -> scla-statement.

    Instance clones carry a `__<suffix>` (canonically `__i2` from
    instance_templates.py, but pre-compiler hand-built workspaces used
    `__scene_04`). No base template name contains `__`, so strip at the
    first one — an unrecognized suffix scheme must never let a clone
    masquerade as its own family and undercount runs/caps.
    """
    name = Path(src or "").stem
    return name.split("__", 1)[0] or "?"


def list_counts(variables: dict) -> dict:
    """{slot_label: item_count} for every list-bearing slot the scene fills."""
    counts = {}
    for slot, sep in LIST_SLOTS.items():
        raw = (variables.get(slot) or "").strip()
        if raw:
            counts[slot] = len([x for x in raw.split(sep) if x.strip()])
    for stem in NUMBERED_SLOTS:
        filled = [k for k, v in variables.items()
                  if re.fullmatch(rf"{stem}\d+", k) and str(v).strip()]
        if filled:
            counts[f"{stem}1..N"] = len(filled)
    return counts


def art_assets(variables: dict) -> list:
    """The artwork asset names a scene actually renders."""
    out = []
    for slot in ART_SLOTS:
        raw = (variables.get(slot) or "").strip()
        if raw:
            out.extend(x.strip() for x in raw.split(",") if x.strip())
    return out


def run_is_exempt(block) -> tuple[bool, str]:
    """Whether a same-family run earns the enumerated-series exemption.

    All three must hold for EVERY scene: an advancing progress indicator, its
    own artwork (no reuse inside the run), and a short duration. This is what
    separates the reference video's five-scene condition run from the rejected
    build's three-scene statement runs.
    """
    if len(block) > RUN_EXEMPT_MAX:
        return False, f"Runs may never exceed {RUN_EXEMPT_MAX}."
    missing = [s["id"] for s in block
               if not any(str(s["variables"].get(k, "")).strip()
                          for k in PROGRESS_SLOTS)]
    if missing:
        return False, (f"No advancing progress indicator on "
                       f"{', '.join(missing)} — a run this long is only "
                       f"allowed for an enumerated series (First/Second/…).")
    art = [art_assets(s["variables"]) for s in block]
    bare = [s["id"] for s, a in zip(block, art) if not a]
    if bare:
        return False, (f"No artwork on {', '.join(bare)} — every scene in a "
                       f"long run needs its own illustration.")
    flat = [a for scene_art in art for a in scene_art]
    if len(set(flat)) < len(block):
        return False, ("Artwork repeats inside the run — each scene needs a "
                       "distinct asset.")
    long_ones = [f"{s['id']} ({s['duration']:.1f}s)" for s in block
                 if s["duration"] > RUN_EXEMPT_MAX_DURATION]
    if long_ones:
        return False, (f"Too slow to sustain the run: {', '.join(long_ones)} "
                       f"exceed {RUN_EXEMPT_MAX_DURATION:.0f}s.")
    return True, ""


def two_region(fam: str, variables: dict) -> bool:
    """Whether a scene places content in two spatially separate regions."""
    if fam in TWO_REGION_ALWAYS:
        return True
    if fam in TWO_REGION_ICON_HERO and str(variables.get("icon", "")).strip():
        return True
    return False


def check(ws: Path):
    html = (ws / "index.html").read_text()
    scenes = parse_scenes(html)
    problems, info = [], []
    if not scenes:
        return ["no scene slots found"], info, {}

    fams = []
    for s in scenes:
        fams.append(family(get_attr(s["tag"], "data-composition-src")))

    # --- rule 1: no one-item list ------------------------------------------
    for s, fam in zip(scenes, fams):
        for slot, n in list_counts(s["variables"]).items():
            if n == 1:
                problems.append(
                    f"{s['id']} ({fam}): slot '{slot}' has exactly ONE item — "
                    f"renders the bullet/pill illustration around a single "
                    f"point. Give it >=2 items, or move the scene to a form "
                    f"that states one idea (scla-statement/scla-quote/scla-stat)."
                )

    # --- rule 2: max consecutive, with the enumerated-series exemption ------
    exempt_idx = set()   # scene indices inside an earned enumerated-series run
    run_start = 0
    for i in range(1, len(fams) + 1):
        if i == len(fams) or fams[i] != fams[run_start]:
            block = scenes[run_start:i]
            run = len(block)
            if run > MAX_CONSECUTIVE:
                ok, why = run_is_exempt(block)
                if not ok:
                    ids = ", ".join(s["id"] for s in block)
                    problems.append(
                        f"{run} consecutive scenes on {fams[run_start]} "
                        f"({ids}) — max is {MAX_CONSECUTIVE}. {why}"
                    )
                else:
                    exempt_idx.update(range(run_start, i))
                    info.append(
                        f"{run}-scene {fams[run_start]} run exempt "
                        f"(enumerated series: advancing progress, distinct "
                        f"artwork, each <={RUN_EXEMPT_MAX_DURATION:.0f}s)")
            run_start = i

    # --- rule 6: theme-block cap (canvas monotony) ---------------------------
    # Consecutive CONTENT scenes on one canvas (title/outro are navy bookends,
    # not part of a theme block). A run breaks on: canvas change, the split
    # scla-stat frame, an unmapped family, or a rule-2-exempt enumerated
    # series (see the calibration note at MAX_CANVAS_RUN — without that
    # carve-out this rule rejects the owner's reference video).
    idx_content = [k for k, f in enumerate(fams) if f not in CHROME]
    durations_compiled = all(
        scenes[k]["duration"] == scenes[k]["duration"]  # NaN != NaN — the
        for k in idx_content)                           # pre-compile marker
    if idx_content and not durations_compiled:
        info.append(
            "rule 6: data-duration not compiled yet (placeholder pre-"
            "compile) — canvas seconds cap skipped, scene-count cap still "
            "enforced")
    blocks = []   # (canvas, [scene index, ...]) or None as a break marker
    for k in idx_content:
        canvas = CANVAS.get(fams[k])
        if canvas is None:
            info.append(f"rule 6: no canvas mapping for {fams[k]} — "
                        f"treated as a canvas break")
        if canvas not in ("light", "navy") or k in exempt_idx:
            blocks.append(None)
            continue
        if blocks and blocks[-1] and blocks[-1][0] == canvas:
            blocks[-1][1].append(k)
        else:
            blocks.append((canvas, [k]))
    for b in blocks:
        if not b:
            continue
        canvas, ks = b
        first, last = scenes[ks[0]]["id"], scenes[ks[-1]]["id"]
        if len(ks) > MAX_CANVAS_RUN:
            problems.append(
                f"{len(ks)} consecutive content scenes on the {canvas} canvas "
                f"({first}..{last}) — max is {MAX_CANVAS_RUN} before the "
                f"background must change (theme-block cap)."
            )
        if durations_compiled:
            secs = sum(scenes[k]["duration"] for k in ks)
            if secs > MAX_CANVAS_SECONDS:
                problems.append(
                    f"{secs:.1f}s continuously on the {canvas} canvas "
                    f"({first}..{last}) — max is {MAX_CANVAS_SECONDS:.0f}s "
                    f"before the background must change (theme-block cap)."
                )

    # --- rules 3 & 4: distribution across content scenes --------------------
    content = [(s, f) for s, f in zip(scenes, fams) if f not in CHROME]
    tally = {}
    for _, f in content:
        tally[f] = tally.get(f, 0) + 1
    runtime = max((s["start"] + s["duration"] for s in scenes), default=0.0)
    if runtime >= EPIC_SECONDS:
        need = MIN_FORMS_EPIC
    elif runtime >= LONG_SECONDS:
        need = MIN_FORMS_LONG
    else:
        need = MIN_FORMS_SHORT
    distinct = len(tally)
    if distinct < need:
        problems.append(
            f"only {distinct} distinct content forms across {len(content)} "
            f"scenes ({runtime:.0f}s) — need >={need}. Used: "
            f"{', '.join(sorted(tally))}."
        )
    if content:
        # Share is graded on SECONDS, not scene count (2026-07-29).
        #
        # check_continuity.py requires a scene to carry a real beat and orders
        # fragments merged; grading share by COUNT made that merge look like a
        # variety regression — fold two 2.4s chips scenes into one 4.8s chips
        # scene and chips' share rises even though the viewer sees exactly the
        # same form for exactly the same time. The two gates pulled against each
        # other for a purely arithmetic reason.
        #
        # Time dissolves it: a merge is share-neutral by construction, because
        # the seconds do not move. It is also the truer measure — monotony is
        # something a viewer experiences over time, not per slide. The threshold
        # is unchanged, and the reference video still passes it (pinned by
        # tests/test_variety.py).
        by_secs = {}
        for sc, fam in content:
            d = sc.get("duration")
            by_secs[fam] = by_secs.get(fam, 0.0) + (
                d if isinstance(d, (int, float)) and d == d and d > 0 else 0.0)
        secs, total = by_secs, sum(by_secs.values())
        if total > 0:
            top, top_s = max(secs.items(), key=lambda kv: kv[1])
            share = top_s / total
            unit = f"{top_s:.0f}s/{total:.0f}s"
        else:
            # Plan stage: durations are placeholders until compile_timeline
            # resolves them, so fall back to the count form.
            top, top_n = max(tally.items(), key=lambda kv: kv[1])
            share = top_n / len(content)
            unit = f"{top_n}/{len(content)} scenes (pre-compile estimate)"
        if share > MAX_SHARE:
            problems.append(
                f"{top} carries {unit} of the content "
                f"({share:.0%}) — no single form may exceed {MAX_SHARE:.0%}."
            )

    # --- rule 5: artwork coverage ------------------------------------------
    # Measured 2026-07-28: the reference video carries artwork on 79% of its
    # content scenes with ~11 distinct devices (a real bar chart, a compass, an
    # advancing 5-dot stepper, mirrored figure glyphs, strike-through
    # annotation); the rejected build managed 33% with 6 assets, one of them
    # used twice, every one a flat monoline icon parked in the same right-hand
    # slot. Nothing counted pictures until now, which is why "boring" could
    # pass every gate.
    if content:
        with_art = [(s, f) for s, f in content if art_assets(s["variables"])]
        share = len(with_art) / len(content)
        if share < MIN_ARTWORK_SHARE:
            problems.append(
                f"only {len(with_art)}/{len(content)} content scenes carry "
                f"artwork ({share:.0%}) — need >={MIN_ARTWORK_SHARE:.0%}. Type "
                f"on a flat field is not an illustration."
            )
        assets = [a for s, _ in content for a in art_assets(s["variables"])]
        uniq = sorted(set(assets))
        if len(uniq) < MIN_DISTINCT_ASSETS:
            problems.append(
                f"only {len(uniq)} distinct artwork asset(s) "
                f"({', '.join(uniq) or 'none'}) — need "
                f">={MIN_DISTINCT_ASSETS} across the lesson."
            )
        overused = {a: assets.count(a) for a in uniq
                    if assets.count(a) > MAX_ASSET_REUSE}
        if overused:
            problems.append(
                "artwork reused past the limit: " + ", ".join(
                    f"{a} x{n}" for a, n in sorted(overused.items())) +
                f" (max {MAX_ASSET_REUSE} each)."
            )
        bare_run, worst, worst_ids = 0, 0, []
        current = []
        for s, _ in content:
            if art_assets(s["variables"]):
                bare_run, current = 0, []
            else:
                bare_run += 1
                current.append(s["id"])
                if bare_run > worst:
                    worst, worst_ids = bare_run, list(current)
        if worst > MAX_CONSECUTIVE_BARE:
            problems.append(
                f"{worst} consecutive scenes with no artwork at all "
                f"({', '.join(worst_ids)}) — max is {MAX_CONSECUTIVE_BARE}."
            )

    # --- rule 7: composition (two-region) coverage ---------------------------
    if content:
        two = [s["id"] for s, f in content if two_region(f, s["variables"])]
        share = len(two) / len(content)
        info.append(f"two-region coverage: {len(two)}/{len(content)} content "
                    f"scenes ({share:.0%})")
        if share < MIN_TWO_REGION_SHARE:
            problems.append(
                f"only {len(two)}/{len(content)} content scenes ({share:.0%}) "
                f"place content in two spatially separate regions — need "
                f">={MIN_TWO_REGION_SHARE:.0%}. Reach for a split/diagram form "
                f"(scla-stat, scla-steps, scla-loop, scla-career-map) or fill "
                f"the right-column icon hero on scla-condition/scla-statement/"
                f"scla-chips."
            )

    # --- info: the menu the builder didn't touch ----------------------------
    available = {p.stem for p in (ws / "compositions").glob("scla-*.html")
                 if "__i" not in p.stem}
    unused = sorted(available - set(fams))
    if unused:
        info.append(f"unused templates available: {', '.join(unused)}")
    info.append("distribution: " + ", ".join(
        f"{k}x{v}" for k, v in sorted(tally.items(), key=lambda kv: -kv[1])))
    return problems, info, tally


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    ws = Path(args[0]).resolve()
    problems, info, tally = check(ws)
    if "--json" in sys.argv[1:]:
        print(json.dumps({"pass": not problems, "problems": problems,
                          "info": info, "distribution": tally}, indent=2))
    else:
        for line in info:
            print(f"  info: {line}")
        for p in problems:
            print(f"  !! {p}")
        print("VARIETY: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
