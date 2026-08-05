#!/usr/bin/env python3
"""build_board.py — author index.html + compositions/board.html for this build.

The HTML is the artifact; this file is how it stays honest. Every time it
writes is READ from timing.json (computed from the real clip durations) and
every colour is a tokens.yml value, so `python3 make_timing.py && python3
build_board.py` reproduces the composition exactly.

ONE carrying object: the decision board (design.md). Marks only ever ARRIVE,
travel ONCE, or are LIFTED at the end — nothing re-animates in place.

WHY EVERY BEAT IS STAGED. `check_diversity` grades a uniform ~1.5s grid and
fails any run of ~4.5s where the pixels hold still while narration is speaking.
A beat that lands all of its content in its first half-second looks right at
its midpoint and is frozen for the rest of the beat. So each beat carries a
LIST of reveals, spread across its own speaking window: the answer to a frozen
beat is new content arriving, never idle motion on settled content (banned,
`check_motion.py`).

REVISION 1 (post-render vision review). The first cut passed every
deterministic gate and failed a review on real pixels: every beat's second half
changed 0.00%, and neighbouring beats were byte-for-byte the same picture. Two
causes, both fixed here:

  1. EVERY MARK WAS TOO FAINT TO MEASURE. The ruled surface was a 1.5px stroke
     at 0.17 alpha — under `check_diversity`'s DELTA of 4 once an 8x8 grid cell
     averages it, i.e. literally invisible to the instrument AND to a viewer on
     a phone. Structural strokes are now 2-3px at 0.30-0.55, pins carry a seat
     ring, and strips are wider. A reveal that cannot be measured is a reveal
     that did not happen.
  2. HALF THE BEATS HAD TWO REVEALS AND THE REST HAD ONE. Every beat now
     carries 3-8, and the ones the review named are CUED to their own word
     timestamps (see CUES) rather than spread evenly — so the picture develops
     on the clause that earns it and keeps developing to the last word.
"""
import json
import random
from pathlib import Path

WS = Path(__file__).resolve().parent
T = json.loads((WS / "timing.json").read_text())
ROWS = T["rows"]
TOTAL = T["total"]
VS = {r["id"]: r["vis_start"] for r in ROWS}
VD = {r["id"]: r["vis_dur"] for r in ROWS}
AD = {r["id"]: r["audio_dur"] for r in ROWS}
IDS = [r["id"] for r in ROWS]

# tokens.yml colors:
NAVY, NAVY_DEEP = "#0d2437", "#0a1e2f"
BLUE, GOLD, PAPER, MUTED = "#3393d6", "#eaab2d", "#ffffff", "#5f6f96"

# ---------------------------------------------------------------------------
# COPY — every line traces to its own beat's narration (BUILD-KIT rule 1).
# Headings are Title Case with no terminal period; body copy stays sentence case.
# ---------------------------------------------------------------------------
COPY = {
    "s01": ("How to Make Strong Career Decisions", None),
    "s02": ("Too Much Weight on One Factor", "a pro and con list makes it easy"),
    "s03": ("The More Powerful Methods",
            "a pro and con list does not push you toward them"),
    "s04": ("A Reality Check",
            "career decisions usually involve real uncertainty"),
    "s05": ("Far Less Likely to Miss Something",
            "this process will not make your decision easy"),
    "s06": ("Your Best Next Step", "here is the surprising part"),
    "s07": ("Most People Use No Process at All",
            "we are not naturally good at complex decisions"),
    "s08": ("The Best Possible Position to Decide",
            "it will not tell you what to do"),
    # REVISION 1, defect 1: the voice speaks FOUR choices and the frame showed
    # three, unjoined. The list is now the spoken list, joined with "or" before
    # the final item (check_copy rule c).
    "s09": ("A Repeatable Loop",
            "run it for any choice: which internship, which major, "
            "which offer, or which next move"),
    "s10": ("Step One: Clarify the Decision",
            "exactly what you are choosing, and by when"),
    "s11": ("Step Two: Widen Your Options",
            "vague decisions produce vague answers"),
    "s12": ("Considering Too Few Options",
            "one of the most serious mistakes people make"),
    "s13": ("Even One Extra Option",
            "it can improve how satisfied you are with the outcome"),
    "s14": ("More Paths Than Feels Comfortable",
            "before you narrow anything down"),
    "s15": ("Step Three: Set Your Criteria",
            "the three to seven factors that truly matter to you"),
    "s16": ("The Factors That Truly Matter",
            "fit, energy, career capital, impact, satisfaction, "
            "and any practical constraints"),
    "s17": ("Step Four: Test Your Assumptions",
            "rate your options against those criteria, not against your mood"),
    "s18": ("Lower the Risk on the One Assumption",
            "find your biggest uncertainty"),
    "s19": ("Run a Cheap Experiment",
            "a single informational interview or a weekend project"),
    "s20": ("Step Five: Decide and Commit", "make the call"),
    "s21": ("Set a Date to Check Back In", "trust your gut as one input"),
    "s22": ("A Mood Is Not a Verdict", "sleep on big decisions"),
    "s23": ("Revisited, Not Carved in Stone",
            "this is a loop, not a one-time event"),
    "s24": ("Things You Cannot Know Right Now", "that is the whole idea"),
    "s25": ("Use That Same Skill Again and Again",
            "once you know how to make one good decision"),
}

# ---------------------------------------------------------------------------
# THE BOARD. Frame coords; every mark inside x[130,1790] y[400,930], which
# clears the safe-area, frame-padding and content-bottom bands by 16px+.
# ---------------------------------------------------------------------------
RAIL_X, RAIL_W = 150, 46
RCX = RAIL_X + RAIL_W / 2
HOLE_Y = [520, 605, 690, 775, 860]
BX0, BY0, BX1, BY1 = 430, 405, 1740, 930

# Entry field: four bands, strongly jittered in x. Strip half-width is 52 and
# ring radius 28, so two pins may not sit closer than 108px in x unless they
# are 100px apart in y — every pair below clears that, which is what keeps the
# punched strips from overprinting each other before the re-sort.
# Ranked rows are 510/615/720 at x 540/780/1020/1260; p13-p15 are the overrun
# and are never re-sorted (design.md).
PINS = [
    # id, arrival beat, entry x,y, ranked x,y (None = overrun, never re-sorted)
    ("p01", "s11", 500, 512, 540, 510), ("p02", "s11", 968, 512, 780, 510),
    ("p03", "s11", 1160, 512, 1020, 510), ("p04", "s13", 1652, 512, 1260, 510),
    ("p05", "s14", 612, 622, 540, 615), ("p06", "s14", 830, 622, 780, 615),
    ("p07", "s14", 1310, 622, 1020, 615), ("p08", "s14", 1520, 622, 1260, 615),
    ("p09", "s14", 520, 732, 540, 720), ("p10", "s14", 1020, 732, 780, 720),
    ("p11", "s14", 1240, 732, 1020, 720), ("p12", "s14", 1600, 732, 1260, 720),
    ("p13", "s14", 700, 836, None, None), ("p14", "s14", 1120, 836, None, None),
    ("p15", "s14", 1450, 836, None, None),
]
# Cells filled out of SIX — six because the narration names exactly six factors
# ("fit, energy, career capital, impact, satisfaction, and any practical
# constraints") and the criteria bar shows exactly six slots. A strip that
# counted five would contradict the spoken list on screen.
CRIT_N = 6
FILLED = {"p01": 6, "p02": 6, "p03": 5, "p04": 5, "p05": 5, "p06": 4,
          "p07": 4, "p08": 4, "p09": 3, "p10": 3, "p11": 2, "p12": 2,
          "p13": 1, "p14": 1, "p15": 1}
RANK_ROW_Y = (510, 615, 720)
DRIFT = [(880, 512, 24), (1046, 706, -38), (640, 800, 12), (1128, 466, -19),
         (960, 858, 33), (1210, 828, -27)]
CATCH = DRIFT[:4]            # the four strays the process catches at s05
TALLY_AT = (700, 596)        # pushed to (205, 843) at step one
TALLY_TO = (-495, 247)
CRIT_X, CRIT_Y, CRIT_W, CRIT_H = 1020, 412, 500, 62
SLIP_X, SLIP_W, SLIP_H = 214, 190, 46
SLIP_Y = (466, 546, 626, 706)


def pin_group(pid, cx, cy, filled):
    """A pin: gold head, offset shadow, a blue seat ring, and (revealed later)
    its punched strip. The seat ring is REVISION 1 — a bare r=14 head moved
    0.03% of the frame, which is under the measurement floor of every pixel
    gate in the lane and under the notice floor of a viewer."""
    cells = []
    for i in range(CRIT_N):
        x = -38 + i * 14
        if i < filled:
            cells.append(f'<rect x="{x}" y="38" width="11" height="13" rx="2" '
                         f'fill="{PAPER}" fill-opacity="0.92"/>')
        else:
            cells.append(f'<rect x="{x}" y="38" width="11" height="13" rx="2" '
                         f'fill="none" stroke="{BLUE}" stroke-width="2" '
                         f'stroke-opacity="0.7"/>')
    return (
        f'<g id="{pid}" opacity="0"><g transform="translate({cx},{cy})">'
        f'<circle cx="0" cy="0" r="24" fill="none" stroke="{BLUE}" '
        f'stroke-width="3.5" stroke-opacity="0.6"/>'
        f'<ellipse cx="6" cy="16" rx="17" ry="5" fill="{NAVY_DEEP}" '
        f'fill-opacity="0.75"/><circle cx="0" cy="0" r="15" fill="{GOLD}"/>'
        f'<g id="{pid}s" opacity="0">'
        f'<rect x="-46" y="30" width="92" height="28" rx="6" fill="{NAVY}" '
        f'stroke="{BLUE}" stroke-width="2" stroke-opacity="0.8"/>'
        f'{"".join(cells)}</g></g></g>')


def socket(sid, cx, cy):
    """An empty option slot — the room a decision has for an option it has not
    considered yet. Same radius as a pin's seat ring, so a pin landing in one
    reads as the slot being filled rather than as a new object."""
    return (f'<g id="{sid}" opacity="0">'
            f'<circle cx="{cx}" cy="{cy}" r="24" fill="none" stroke="{BLUE}" '
            f'stroke-width="4" stroke-opacity="0.55" '
            f'stroke-dasharray="9 11"/></g>')


def stipple(tag, lo, hi, n):
    rnd = random.Random(hash(tag) & 0xFFFF)
    out = [f'<g id="{tag}" opacity="0">']
    for _ in range(n):
        t = lo + (hi - lo) * rnd.random() ** 0.7
        x = 1320 + t * 460
        y = 412 + rnd.random() * 516
        r = 2.2 + rnd.random() * 3.0
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" '
                   f'fill="{MUTED}" fill-opacity="{0.18 + t * 0.5:.2f}"/>')
    out.append('</g>')
    return "".join(out)


def board_svg():
    p = []
    a = p.append
    a('<svg id="board" viewBox="0 390 1920 690" width="1920" height="690" '
      'xmlns="http://www.w3.org/2000/svg" data-layout-allow-overlap="true">')

    # 1. the faint square rule — navy on navy-deep, a luma step of ~5, far
    #    under the ink gate's local-contrast threshold, so a full-bleed
    #    surface creates no ink in any keep-out band.
    a('<g id="g-rulev" opacity="0">')
    for x in range(130, 1791, 62):
        a(f'<line x1="{x}" y1="400" x2="{x}" y2="930" stroke="{NAVY}" '
          f'stroke-width="2"/>')
    a('</g><g id="g-ruleh" opacity="0">')
    for y in range(400, 931, 62):
        a(f'<line x1="130" y1="{y}" x2="1790" y2="{y}" stroke="{NAVY}" '
          f'stroke-width="2"/>')
    a('</g>')

    # 2. the rail — the five-step process. One hole per step, punched on the
    #    way past and never remarked on.
    a(f'<g id="g-rail" opacity="0"><rect x="{RAIL_X}" y="400" width="{RAIL_W}" '
      f'height="540" rx="20" fill="{NAVY}" fill-opacity="0.9" stroke="{BLUE}" '
      f'stroke-width="2.5" stroke-opacity="0.5"/></g>')
    a(f'<g id="g-railcap" opacity="0"><line x1="{RAIL_X + 8}" y1="410" '
      f'x2="{RAIL_X + RAIL_W - 8}" y2="410" stroke="{BLUE}" stroke-width="3" '
      f'stroke-opacity="0.8"/><line x1="{RAIL_X + 8}" y1="930" '
      f'x2="{RAIL_X + RAIL_W - 8}" y2="930" stroke="{BLUE}" stroke-width="3" '
      f'stroke-opacity="0.8"/></g>')
    # the run of the process, drawn once all five holes are punched (s20).
    # Emitted BEFORE the holes so the holes stay punched through it.
    a(f'<g id="g-railrun" opacity="0"><line x1="{RCX}" y1="437" '
      f'x2="{RCX}" y2="{HOLE_Y[-1]}" stroke="{BLUE}" stroke-width="9" '
      f'stroke-opacity="0.7"/></g>')
    a(f'<g id="g-peg" opacity="0"><circle cx="{RCX}" cy="437" r="13" '
      f'fill="{BLUE}"/></g>')
    a('<g id="g-railticks" opacity="0">')
    for y in (470, 560, 650, 740, 830, 905):
        a(f'<line x1="{RAIL_X + 5}" y1="{y}" x2="{RAIL_X + 21}" y2="{y}" '
          f'stroke="{BLUE}" stroke-width="3" stroke-opacity="0.6"/>')
    a('</g>')
    a(f'<g id="g-tick" opacity="0"><line x1="{RCX + 18}" y1="437" '
      f'x2="{RCX + 92}" y2="437" stroke="{BLUE}" stroke-width="7" '
      f'stroke-linecap="round"/></g>')
    a(f'<g id="g-tick2" opacity="0"><path d="M{RCX + 96},437 l-20,-16 m20,16 '
      f'l-20,16" fill="none" stroke="{GOLD}" stroke-width="6" '
      f'stroke-linecap="round"/></g>')
    for i, y in enumerate(HOLE_Y, start=1):
        a(f'<g id="g-hole{i}" opacity="0">'
          f'<circle cx="{RCX}" cy="{y}" r="14" fill="{NAVY_DEEP}"/>'
          f'<path d="M{RCX - 14},{y} a14,14 0 0 1 14,-14" fill="none" '
          f'stroke="{BLUE}" stroke-width="3" stroke-opacity="0.9"/></g>')
    # the repeatable loop — the arc that returns the board to its own start
    a(f'<g id="g-return" opacity="0"><path pathLength="1" d="M{RCX},916 '
      f'C134,942 134,432 {RCX},428" fill="none" stroke="{BLUE}" '
      f'stroke-width="3.5" stroke-opacity="0.6" stroke-dasharray="1" '
      f'stroke-dashoffset="1"/></g>')

    # 3. the working surface becomes readable (s08), one quadrant at a time.
    #    REVISION 1: 2px at 0.30 rather than 1.5px at 0.17. The old value
    #    resolved to a per-cell luminance move of ~3 against a threshold of 4 —
    #    the whole surface arriving changed 0.0% of the graded frame.
    quads = (("g-surf1", 470, 1090, 452, 676), ("g-surf2", 1090, 1700, 452, 676),
             ("g-surf3", 470, 1090, 676, 900), ("g-surf4", 1090, 1700, 676, 900))
    for tag, x0, x1, y0, y1 in quads:
        a(f'<g id="{tag}" opacity="0">')
        for y in range(y0, y1, 112):
            a(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{BLUE}" '
              f'stroke-width="2" stroke-opacity="0.30"/>')
        a('</g>')

    # 4. uncertainty, creeping in from the right in three bands
    a(stipple("g-stipa", 0.55, 1.0, 92))
    a(stipple("g-stipb", 0.25, 0.72, 78))
    a(stipple("g-stipc", 0.0, 0.4, 62))
    a(stipple("g-stipd", 0.62, 1.0, 62))

    # 5. the pro-and-con tally: two columns of flat marks, ONE grossly
    #    oversized, shouldering its neighbours out of line. Never erased.
    # data-layout-allow-overflow: the ONE authored move in the build carries
    # this group 495px left at step one. The inspector measures the GSAP
    # transform as an overflow of the svg's own box even though the landing
    # position (205, 843) is well inside it — the layering is declared, not
    # tolerated by a loosened gate.
    a(f'<g id="g-tally" opacity="1" data-layout-allow-overflow '
      f'transform="translate{TALLY_AT}">')
    a('<g id="g-tallyL" opacity="0">')
    for x, dy in ((0, 0), (26, -6), (86, -4), (112, 2)):
        a(f'<rect x="{x}" y="{dy}" width="9" height="80" fill="{PAPER}" '
          f'fill-opacity="0.6"/>')
    a('</g>')
    a(f'<g id="g-tallyBig" opacity="0"><rect x="50" y="-34" width="15" '
      f'height="148" fill="{GOLD}" fill-opacity="0.95"/></g>')
    a(f'<g id="g-tallyweight" opacity="0"><path d="M20,126 L20,142 L94,142 '
      f'L94,126" fill="none" stroke="{GOLD}" stroke-width="8" '
      f'stroke-opacity="0.9"/></g>')
    # The right column is pitched at 22px so the whole tally is 216px wide —
    # narrow enough to sit in the 234px gutter between the rail (ends x 196)
    # and the scored boundary (starts x 430) once step one pushes it out.
    a('<g id="g-tallyR" opacity="0">')
    for i in range(4):
        a(f'<rect x="{140 + i * 22}" y="0" width="9" height="80" '
          f'fill="{PAPER}" fill-opacity="0.6"/>')
    a('</g></g>')

    # 6. marks anchored to nothing
    for i, (x, y, rot) in enumerate(DRIFT, start=1):
        a(f'<g id="g-drift{i}" opacity="0"><g transform="translate({x},{y}) '
          f'rotate({rot})"><rect x="-4" y="-44" width="8" height="88" '
          f'fill="{PAPER}" fill-opacity="0.55"/><rect x="-21" y="20" '
          f'width="42" height="8" fill="{PAPER}" fill-opacity="0.35"/>'
          f'</g></g>')

    # 6b. what the process CATCHES (s05). The narration's claim is that working
    #     through it makes you far less likely to MISS something, so the art
    #     rings the strays one at a time — new content arriving on the beat's
    #     own word timings, never a pulse on a mark already there.
    for i, (x, y, _r) in enumerate(CATCH, start=1):
        a(f'<g id="g-catch{i}" opacity="0">'
          f'<circle cx="{x}" cy="{y}" r="42" fill="none" stroke="{GOLD}" '
          f'stroke-width="7" stroke-opacity="0.9"/></g>')

    # 6c. the best next step (s06) — the process walked, one tread at a time,
    #     then struck out at s07 because most people never walk it.
    a(f'<g id="g-stepsa" opacity="0"><path pathLength="1" d="M205,437 L290,437 '
      f'L290,505 L375,505" fill="none" stroke="{BLUE}" stroke-width="6" '
      f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1" '
      f'stroke-dashoffset="1"/></g>')
    a(f'<g id="g-stepsb" opacity="0"><path pathLength="1" d="M375,505 L375,573 '
      f'L460,573 L460,641 L545,641" fill="none" stroke="{BLUE}" '
      f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round" '
      f'stroke-dasharray="1" stroke-dashoffset="1"/></g>')
    a(f'<g id="g-stepcap" opacity="0"><circle cx="545" cy="641" r="30" '
      f'fill="none" stroke="{GOLD}" stroke-width="5"/>'
      f'<circle cx="545" cy="641" r="15" fill="{GOLD}"/></g>')
    a(f'<g id="g-nostep" opacity="0"><path d="M505,601 l80,80 m0,-80 l-80,80" '
      f'fill="none" stroke="{GOLD}" stroke-width="8" '
      f'stroke-linecap="round"/></g>')
    a(f'<g id="g-gut" opacity="0"><path pathLength="1" d="M250,870 C560,930 '
      f'820,700 1120,870" fill="none" stroke="{PAPER}" stroke-width="5" '
      f'stroke-opacity="0.55" stroke-linecap="round" stroke-dasharray="1" '
      f'stroke-dashoffset="1"/></g>')

    # 6d. the choices this loop can be run for (s09) — a bracket in the left
    #     gutter that fills with one slip per choice the narration names.
    a(f'<g id="g-choicebox" opacity="0"><rect x="204" y="452" width="210" '
      f'height="320" rx="12" fill="none" stroke="{BLUE}" stroke-width="3" '
      f'stroke-opacity="0.55" stroke-dasharray="18 14"/></g>')
    for i, y in enumerate(SLIP_Y, start=1):
        a(f'<g id="g-slip{i}" opacity="0">'
          f'<rect x="{SLIP_X}" y="{y + 6}" width="14" height="{SLIP_H - 12}" '
          f'rx="4" fill="{GOLD}"/>'
          f'<rect x="{SLIP_X + 30}" y="{y + 17}" width="150" height="12" '
          f'rx="3" fill="{PAPER}" fill-opacity="0.55"/></g>')

    # 7. the scored boundary, its corner ticks, its dated tag (empty date line)
    a(f'<g id="g-bound" opacity="0"><rect x="{BX0}" y="{BY0}" '
      f'width="{BX1 - BX0}" height="{BY1 - BY0}" fill="none" stroke="{BLUE}" '
      f'stroke-width="3.5" stroke-opacity="0.9"/></g>')
    a('<g id="g-corners" opacity="0">')
    for cx, cy, dx, dy in ((BX0, BY0, 1, 1), (BX1, BY0, -1, 1),
                           (BX0, BY1, 1, -1), (BX1, BY1, -1, -1)):
        a(f'<path d="M{cx + dx * 34},{cy + dy * 12} L{cx + dx * 12},'
          f'{cy + dy * 12} L{cx + dx * 12},{cy + dy * 34}" fill="none" '
          f'stroke="{GOLD}" stroke-width="5"/>')
    a('</g>')
    a(f'<g id="g-tag" opacity="0"><path d="M1548,412 L1710,412 L1734,436 '
      f'L1734,474 L1548,474 Z" fill="{NAVY}" stroke="{BLUE}" '
      f'stroke-width="2.5"/><line x1="1572" y1="452" x2="1712" y2="452" '
      f'stroke="{BLUE}" stroke-width="2.5" stroke-opacity="0.75"/></g>')
    a(f'<g id="g-margin" opacity="0"><rect x="{BX0 + 34}" y="{BY0 + 34}" '
      f'width="{BX1 - BX0 - 68}" height="{BY1 - BY0 - 68}" fill="none" '
      f'stroke="{BLUE}" stroke-width="2.5" stroke-opacity="0.45" '
      f'stroke-dasharray="14 16"/></g>')

    a(f'<g id="g-short" opacity="0"><rect x="900" y="570" width="800" '
      f'height="230" rx="10" fill="none" stroke="{GOLD}" stroke-width="4" '
      f'stroke-opacity="0.75" stroke-dasharray="20 16"/></g>')

    # 8. rank rules — the rows the field is about to be sorted into
    a('<g id="g-rank" opacity="0">')
    for y in RANK_ROW_Y:
        a(f'<line x1="484" y1="{y + 68}" x2="1340" y2="{y + 68}" '
          f'stroke="{BLUE}" stroke-width="3" stroke-opacity="0.42"/>')
    a('</g>')

    # 9. empty option slots, then the pins that fill them
    for i, (_pid, _b, ex, ey, _sx, _sy) in enumerate(PINS, start=1):
        a(socket(f"g-slot{i}", ex, ey))
    for pid, _b, ex, ey, _sx, _sy in PINS:
        a(pin_group(pid, ex, ey, FILLED[pid]))
    a(f'<g id="g-halo" opacity="0"><circle cx="1652" cy="512" r="32" '
      f'fill="none" stroke="{GOLD}" stroke-width="6" '
      f'stroke-opacity="0.85"/></g>')

    # 10. the criteria — SIX slots, written down empty (s15) and named one by
    #     one (s16). Six because the narration names six factors; a bar of five
    #     would put a count on screen the voice contradicts.
    a(f'<g id="g-crit" opacity="0">'
      f'<rect x="{CRIT_X}" y="{CRIT_Y}" width="{CRIT_W}" height="{CRIT_H}" '
      f'rx="10" fill="{NAVY}" stroke="{BLUE}" stroke-width="3"/>'
      f'<rect x="{CRIT_X + 4}" y="{CRIT_Y + 4}" width="12" '
      f'height="{CRIT_H - 8}" rx="4" fill="{GOLD}"/></g>')
    for i in range(CRIT_N):
        cx = CRIT_X + 12 + i * 80
        a(f'<g id="g-crit{i + 1}" opacity="0"><rect x="{cx}" '
          f'y="{CRIT_Y + 16}" width="66" height="30" rx="4" fill="none" '
          f'stroke="{BLUE}" stroke-width="2.5" stroke-opacity="0.8"/></g>')
    for i in range(CRIT_N):
        cx = CRIT_X + 12 + i * 80
        a(f'<g id="g-critf{i + 1}" opacity="0"><rect x="{cx}" '
          f'y="{CRIT_Y + 16}" width="66" height="30" rx="4" fill="{PAPER}" '
          f'fill-opacity="0.92"/></g>')

    # 11. the biggest uncertainty, and the threads that test it
    a(f'<g id="g-riskband" opacity="0"><rect x="1360" y="540" width="340" '
      f'height="260" rx="8" fill="none" stroke="{GOLD}" stroke-width="3.5" '
      f'stroke-opacity="0.7" stroke-dasharray="18 14"/></g>')
    a(f'<g id="g-uncert" opacity="0"><path d="M1490,630 l80,80 m0,-80 l-80,80" '
      f'fill="none" stroke="{GOLD}" stroke-width="7" '
      f'stroke-linecap="round"/></g>')
    a(f'<g id="g-uncertring" opacity="0"><circle cx="1530" cy="670" r="62" '
      f'fill="none" stroke="{GOLD}" stroke-width="5" stroke-opacity="0.75" '
      f'stroke-dasharray="16 12"/></g>')
    a(f'<g id="g-thra" opacity="0"><path pathLength="1" d="M540,510 C960,470 '
      f'1320,520 1530,670" fill="none" stroke="{BLUE}" stroke-width="4" '
      f'stroke-linecap="round" stroke-dasharray="1" '
      f'stroke-dashoffset="1"/></g>')
    a(f'<g id="g-thrb" opacity="0"><path pathLength="1" d="M1530,670 C1620,840 '
      f'1180,870 830,660" fill="none" stroke="{BLUE}" stroke-width="4" '
      f'stroke-linecap="round" stroke-dasharray="1" '
      f'stroke-dashoffset="1"/></g>')

    # 12. the cleared window — stipple replaced by clean ruled surface
    a(f'<g id="g-win" opacity="0"><rect x="1380" y="560" width="280" '
      f'height="200" fill="{NAVY}" stroke="{BLUE}" stroke-width="3"/></g>')
    a('<g id="g-winrule" opacity="0">')
    for y in range(596, 760, 32):
        a(f'<line x1="1404" y1="{y}" x2="1636" y2="{y}" stroke="{GOLD}" '
          f'stroke-width="2.5" stroke-opacity="0.7"/>')
    a('</g>')
    a(f'<g id="g-winmark" opacity="0"><path d="M1424,690 l30,30 l58,-72" '
      f'fill="none" stroke="{GOLD}" stroke-width="7" stroke-linecap="round" '
      f'stroke-linejoin="round"/></g>')

    # 13. the committed thread — the heaviest line in the video, drawn once
    a(f'<g id="g-commit" opacity="0"><path pathLength="1" d="M{RCX},437 '
      f'C300,432 420,452 540,510" fill="none" stroke="{PAPER}" '
      f'stroke-width="8" stroke-linecap="round" stroke-dasharray="1" '
      f'stroke-dashoffset="1"/></g>')
    a(f'<g id="g-chosen" opacity="0"><circle cx="540" cy="510" r="38" '
      f'fill="none" stroke="{GOLD}" stroke-width="7"/></g>')
    a(f'<g id="g-verdictmark" opacity="0"><circle cx="540" cy="510" r="54" '
      f'fill="none" stroke="{PAPER}" stroke-width="5" '
      f'stroke-opacity="0.8"/></g>')

    # 14. the review tag hanging off the committed pin, and the date set on it
    a(f'<g id="g-lead" opacity="0"><line x1="556" y1="472" x2="600" y2="432" '
      f'stroke="{BLUE}" stroke-width="3.5"/></g>')
    a(f'<g id="g-revtag" opacity="0"><path d="M600,400 L780,400 L806,426 '
      f'L806,470 L600,470 Z" fill="{NAVY}" stroke="{GOLD}" '
      f'stroke-width="3"/><rect x="600" y="400" width="180" height="14" '
      f'fill="{GOLD}" fill-opacity="0.9"/></g>')
    a('<g id="g-datemark" opacity="0">')
    for x in (626, 674, 722):
        a(f'<rect x="{x}" y="432" width="36" height="9" fill="{GOLD}" '
          f'fill-opacity="0.85"/>')
    a('</g>')
    a(f'<g id="g-checkback" opacity="0"><path pathLength="1" d="M540,570 '
      f'C520,860 340,930 200,912" fill="none" stroke="{BLUE}" '
      f'stroke-width="4" stroke-opacity="0.8" stroke-linecap="round" '
      f'stroke-dasharray="1" stroke-dashoffset="1"/></g>')
    a(f'<g id="g-input" opacity="0"><path d="M540,600 l0,-46 m0,0 l-16,20 '
      f'm16,-20 l16,20" fill="none" stroke="{BLUE}" stroke-width="5" '
      f'stroke-linecap="round"/></g>')

    # 15. a mood is not a verdict — two oversized strays, struck through.
    #     Deliberately the same shape as the tally's oversized mark: the board
    #     is showing the SAME mistake it opened with, in the same language.
    a(f'<g id="g-mood1" opacity="0"><rect x="874" y="786" width="12" '
      f'height="110" fill="{GOLD}" fill-opacity="0.9"/></g>')
    a(f'<g id="g-mood2" opacity="0"><rect x="934" y="776" width="12" '
      f'height="110" fill="{GOLD}" fill-opacity="0.9"/></g>')
    a(f'<g id="g-struck" opacity="0"><path d="M840,770 L990,910 M990,770 '
      f'L840,910" fill="none" stroke="{PAPER}" stroke-width="7" '
      f'stroke-linecap="round"/></g>')

    # 16. the review scale, and the loop drawn heavy so it visibly closes
    a('<g id="g-measure" opacity="0">')
    for x in range(470, 1701, 82):
        a(f'<line x1="{x}" y1="{BY1 - 24}" x2="{x}" y2="{BY1}" '
          f'stroke="{BLUE}" stroke-width="3.5" stroke-opacity="0.6"/>')
    a('</g>')
    a(f'<g id="g-measurebase" opacity="0"><line x1="470" y1="{BY1 - 24}" '
      f'x2="1700" y2="{BY1 - 24}" stroke="{BLUE}" stroke-width="3" '
      f'stroke-opacity="0.5"/></g>')
    a(f'<g id="g-revisit" opacity="0"><path pathLength="1" d="M{RCX},916 '
      f'C134,942 134,432 {RCX},428" fill="none" stroke="{PAPER}" '
      f'stroke-width="5" stroke-linecap="round" stroke-dasharray="1" '
      f'stroke-dashoffset="1"/></g>')
    a(f'<g id="g-loopcap" opacity="0"><path d="M{RCX - 18},450 L{RCX},428 '
      f'L{RCX + 18},450" fill="none" stroke="{GOLD}" stroke-width="6" '
      f'stroke-linecap="round" stroke-linejoin="round"/></g>')
    a(f'<g id="g-loopring" opacity="0"><circle cx="{RCX}" cy="437" r="34" '
      f'fill="none" stroke="{GOLD}" stroke-width="6"/></g>')
    a('</svg>')
    return "".join(p)


# ---------------------------------------------------------------------------
# THE SCHEDULE. Per beat, an ordered list of reveals. Where CUES names times,
# each reveal lands on the word that earns it; otherwise reveals are spread
# evenly across the beat's own speaking window. Either way the LAST reveal sits
# near the last word, which is what keeps a beat's second half developing.
# ---------------------------------------------------------------------------
FADE = ('tl.to("{sel}", {{ opacity: {op}, duration: {d}, ease: "power2.out" }}, {t});')
DRAW = ('tl.set("{sel}", {{ opacity: 1 }}, {t});'
        'tl.to("{sel} path", {{ strokeDashoffset: 0, duration: {d}, '
        'ease: "power2.inOut" }}, {t});')


def show(sel, d=0.55, op=1):
    return lambda t: FADE.format(sel=sel, op=op, d=d, t=t)


def draw(sel, d=1.1):
    return lambda t: DRAW.format(sel=sel, d=d, t=t)


def enter(sel, d=0.5):
    return lambda t: (f'tl.fromTo("{sel}", {{ opacity: 0, y: -16 }}, '
                      f'{{ opacity: 1, y: 0, duration: {d}, '
                      f'ease: "power3.out" }}, {t});')


def move(pids, d=0.85):
    def f(t):
        out = []
        for pid, dx, dy in pids:
            out.append(f'tl.to("#{pid}", {{ x: {dx}, y: {dy}, duration: {d}, '
                       f'ease: "power3.inOut" }}, {t});')
        return "".join(out)
    return f


def group(fns, step=0.13):
    return lambda t: "".join(f(round(t + i * step, 3)) for i, f in enumerate(fns))


def land(pid, n):
    """A pin arriving IN its slot: the empty socket goes as the pin lands."""
    return group([enter(f"#{pid}"), show(f"#g-slot{n}", 0.35, 0)], step=0.0)


RANKED = {p[0]: (p[4] - p[2], p[5] - p[3]) for p in PINS if p[4] is not None}
NUM = {p[0]: i + 1 for i, p in enumerate(PINS)}
STRIPS_A = ["p01", "p02", "p03"]
STRIPS_B = ["p05", "p06", "p07", "p08"]
STRIPS_C = ["p09", "p10", "p11", "p12"]
STRIPS_D = ["p13", "p14", "p15"]

# Everything laid down before the boundary is scored, swept in one move at
# step one. A wholesale authored change at a beat boundary, not idle motion.
SWEEP = ([f"#g-drift{i}" for i in range(1, 7)]
         + [f"#g-catch{i}" for i in range(1, 5)]
         + ["#g-stepsa", "#g-stepsb", "#g-stepcap", "#g-nostep", "#g-gut",
            "#g-choicebox"]
         + [f"#g-slip{i}" for i in range(1, 5)])

SCHEDULE = {
    "s01": [show("#g-rulev", 0.7), show("#g-ruleh", 0.7), show("#g-rail", 0.6),
            show("#g-railcap", 0.5)],
    "s02": [show("#g-tallyL", 0.5), show("#g-tallyR", 0.5),
            show("#g-tallyBig", 0.5), show("#g-tallyweight", 0.5)],
    "s03": [show("#g-drift1", 0.45), show("#g-drift2", 0.45),
            show("#g-drift3", 0.45), show("#g-drift4", 0.45)],
    "s04": [show("#g-stipa", 0.7), show("#g-stipb", 0.7), show("#g-stipc", 0.7)],
    # s05 — "far less likely to MISS something": the process rings each stray.
    "s05": [group([show("#g-peg", 0.45), show("#g-railticks", 0.6)]),
            show("#g-catch1", 0.5), show("#g-catch2", 0.5),
            show("#g-catch3", 0.5), show("#g-catch4", 0.5)],
    # s06 — "the best next step": the process is walked, tread by tread.
    "s06": [group([show("#g-tick", 0.45), show("#g-tick2", 0.45)]),
            draw("#g-stepsa", 0.7), draw("#g-stepsb", 0.8),
            show("#g-stepcap", 0.5)],
    # s07 — most people never walk it; the gut path is drawn instead.
    "s07": [show("#g-nostep", 0.45),
            group([show("#g-drift5", 0.45), show("#g-drift6", 0.45)]),
            draw("#g-gut", 1.4), show("#g-stipd", 0.7)],
    "s08": [show("#g-surf1", 0.6), show("#g-surf2", 0.6),
            show("#g-surf3", 0.6), show("#g-surf4", 0.6)],
    # s09 — one slip per choice the narration names, arriving as it is spoken.
    "s09": [draw("#g-return", 1.3), show("#g-choicebox", 0.55),
            show("#g-slip1", 0.45), show("#g-slip2", 0.45),
            show("#g-slip3", 0.45), show("#g-slip4", 0.45)],
    "s10": [group([show(s, 0.5, 0) for s in SWEEP], step=0.06),
            show("#g-bound", 0.6),
            move([("g-tally", *TALLY_TO)], 0.9),
            group([show("#g-corners", 0.5), show("#g-tag", 0.5)]),
            show("#g-hole1", 0.45)],
    # s11 — defect 2: the content rectangle may not sit empty under "widen
    # your options". Empty slots arrive on "vague answers", options land on
    # "step two / widen / options".
    "s11": [group([show(f"#g-slot{i}", 0.5) for i in (1, 3, 6, 8, 11)]),
            land("p01", 1), show("#g-hole2", 0.45), show("#g-margin", 0.6),
            land("p06", 6), land("p11", 11)],
    # s12 — "considering too few options" reads as the room still unfilled.
    "s12": [group([show(f"#g-slot{i}", 0.5) for i in (2, 4, 5)]),
            group([show(f"#g-slot{i}", 0.5) for i in (7, 9, 10)]),
            group([show(f"#g-slot{i}", 0.5) for i in (12, 13)]),
            group([show(f"#g-slot{i}", 0.5) for i in (14, 15)]
                  + [show("#g-short", 0.55)])],
    "s13": [land("p04", 4), show("#p04s", 0.45), show("#g-halo", 0.5),
            land("p02", 2)],
    "s14": [group([land("p03", 3), land("p05", 5), land("p07", 7)]),
            group([land("p08", 8), land("p09", 9), land("p10", 10)]),
            group([land("p12", 12), land("p13", 13)]),
            group([land("p14", 14), land("p15", 15),
                   show("#g-short", 0.5, 0)])],
    # s15 — defect 3: the count on screen must agree with the voice. Six empty
    # criteria slots are written down, one per factor the next beat names.
    "s15": [show("#g-hole3", 0.45),
            group([show("#g-crit", 0.55), show("#g-crit1", 0.4)]),
            show("#g-crit2", 0.4)]
           + [show(f"#g-crit{i}", 0.4) for i in range(3, CRIT_N + 1)],
    "s16": [show(f"#g-critf{i}", 0.4) for i in range(1, CRIT_N + 1)],
    "s17": [group([show(f"#{p}s", 0.45) for p in STRIPS_A]),
            show("#g-rank", 0.6),
            group([show("#g-halo", 0.4, 0),
                   move([(p, *RANKED[p]) for p in ("p01", "p02", "p03", "p04")])]),
            move([(p, *RANKED[p]) for p in ("p05", "p06", "p07", "p08")]),
            move([(p, *RANKED[p]) for p in ("p09", "p10", "p11", "p12")]),
            group([show(f"#{p}s", 0.45) for p in STRIPS_B]),
            group([show(f"#{p}s", 0.45) for p in STRIPS_C]),
            group([show(f"#{p}s", 0.45) for p in STRIPS_D]),
            show("#g-hole4", 0.45)],
    "s18": [show("#g-riskband", 0.55), show("#g-uncert", 0.5),
            show("#g-uncertring", 0.5), draw("#g-thra", 1.2)],
    "s19": [draw("#g-thrb", 1.2), show("#g-win", 0.5),
            show("#g-winrule", 0.5), show("#g-winmark", 0.45)],
    "s20": [draw("#g-commit", 2.2), show("#g-hole5", 0.45),
            show("#g-railrun", 0.5), show("#g-chosen", 0.5)],
    "s21": [show("#g-lead", 0.4), show("#g-revtag", 0.5),
            show("#g-datemark", 0.4), draw("#g-checkback", 1.1),
            show("#g-input", 0.4)],
    # s22 — the mood marks are struck; NOTHING already on the board is dimmed.
    # Revision 1 removed a `#p12 -> opacity 0.42` hold that read on real pixels
    # as a node stuck mid-fade for 3.1s.
    "s22": [show("#g-mood1", 0.45), show("#g-mood2", 0.45),
            show("#g-struck", 0.4), show("#g-verdictmark", 0.5)],
    # s23 — the loop closes on the carrying object: the return arc is redrawn
    # at double weight, capped, and the peg it started from is ringed.
    "s23": [group([show("#g-measure", 0.6), show("#g-measurebase", 0.6)]),
            draw("#g-revisit", 1.4), show("#g-loopcap", 0.4),
            show("#g-loopring", 0.5)],
    "s24": [group([show("#g-thra", 0.6, 0), show("#g-thrb", 0.6, 0),
                   show("#g-uncert", 0.5, 0), show("#g-uncertring", 0.5, 0),
                   show("#g-riskband", 0.5, 0)]),
            group([show("#g-struck", 0.4, 0), show("#g-mood1", 0.4, 0),
                   show("#g-mood2", 0.4, 0), show("#g-datemark", 0.4, 0),
                   show("#g-input", 0.4, 0), show("#g-lead", 0.4, 0),
                   show("#g-revtag", 0.5, 0), show("#g-checkback", 0.5, 0)],
                  step=0.08),
            group([show(f"#{p}", 0.5, 0) for p in
                   ("p04", "p08", "p12", "p07", "p11")]),
            group([show(f"#{p}", 0.5, 0) for p in
                   ("p03", "p06", "p10", "p02", "p05")])],
    "s25": [group([show("#g-commit", 0.6, 0), show("#g-chosen", 0.5, 0),
                   show("#g-verdictmark", 0.5, 0), show("#p01", 0.5, 0),
                   show("#p09", 0.5, 0)]),
            group([show("#g-revisit", 0.6, 0), show("#g-loopcap", 0.4, 0),
                   show("#g-loopring", 0.5, 0), show("#p13", 0.5, 0),
                   show("#p14", 0.5, 0), show("#p15", 0.5, 0)], step=0.08),
            group([show("#g-win", 0.5, 0), show("#g-winrule", 0.5, 0),
                   show("#g-winmark", 0.4, 0), show("#g-crit", 0.5, 0),
                   show("#g-rank", 0.6, 0)]
                  + [show(f"#g-crit{i}", 0.4, 0) for i in range(1, CRIT_N + 1)]
                  + [show(f"#g-critf{i}", 0.4, 0) for i in range(1, CRIT_N + 1)],
                  step=0.05),
            group([show("#g-surf1", 0.6, 0), show("#g-surf2", 0.6, 0),
                   show("#g-surf3", 0.6, 0), show("#g-surf4", 0.6, 0),
                   show("#g-margin", 0.6, 0), show("#g-measure", 0.5, 0),
                   show("#g-measurebase", 0.5, 0), show("#g-railrun", 0.5, 0),
                   show("#g-tag", 0.6, 0)], step=0.08)],
}

# ---------------------------------------------------------------------------
# CUES — absolute times, read off assets/voice word timestamps in
# audio_meta.json. Only for the beats the vision review named; everything else
# keeps the even spread. len(CUES[b]) must equal len(SCHEDULE[b]).
# ---------------------------------------------------------------------------
CUES = {
    "s02": [11.20, 11.90, 13.32, 14.38],
    # peg | four strays ringed, on "work through it / far / miss / important"
    "s05": [34.13, 35.71, 37.47, 38.51, 39.03],
    # arrow | two treads | the step reached, on "likely / best / step / part"
    "s06": [41.14, 42.04, 42.88, 44.14],
    # the surface becomes readable, quadrant by quadrant
    "s08": [58.00, 59.70, 61.30, 62.80],
    # loop | the choice frame | one slip per choice as it is named
    "s09": [65.62, 66.72, 68.10, 69.60, 70.80, 71.90],
    "s12": [87.66, 88.05, 89.58, 90.55],
    # empty slots on "vague answers", options on "step two / widen / options"
    "s11": [80.90, 82.10, 82.60, 83.76, 84.60, 85.30],
    # p04 on "one extra option", its strip on "improve", halo on "satisfied"
    "s13": [93.43, 94.09, 95.75, 97.31],
    # step three | the criteria bar | six slots on "three to seven factors"
    "s15": [105.62, 106.55, 107.61, 109.36, 110.02, 110.81, 111.62],
    # one filled slot per factor the voice names
    "s16": [113.53, 114.30, 115.20, 116.10, 117.44, 119.11],
    # risk band | the X | its ring | the thread out to it
    "s14": [99.20, 100.00, 101.36, 102.38],
    "s18": [131.86, 132.68, 134.60, 135.28],
    "s19": [138.51, 139.45, 141.35, 142.41],
    "s20": [144.87, 145.61, 146.53, 147.91],
    "s21": [149.49, 150.51, 151.35, 152.49, 153.43],
    "s22": [155.49, 157.43, 158.05, 158.63],
    "s23": [160.68, 162.30, 164.20, 165.56],
    "s25": [175.40, 177.80, 178.90, 179.90],
}


def beat_blocks():
    out = []
    for bid in IDS:
        head, sub = COPY[bid]
        cls = "beat beat-title" if bid == "s01" else "beat"
        tag = "h1" if bid == "s01" else "h2"
        sub_html = f'<p class="sub" id="b-{bid}">{sub}</p>' if sub else ""
        out.append(f'<div class="{cls}" id="c-{bid}">'
                   f'<{tag} data-role="heading" id="h-{bid}">{head}</{tag}>'
                   f'{sub_html}</div>')
    return "\n        ".join(out)


def reveal_times(bid, n):
    """When this beat's n reveals land. CUES wins; otherwise spread from 26%
    into the beat out to the last word."""
    s, dur = VS[bid], VD[bid]
    if bid in CUES:
        ts = CUES[bid]
        assert len(ts) == n, f"{bid}: {len(ts)} cues for {n} reveals"
        for t in ts:
            assert s <= t <= s + dur, f"{bid}: cue {t} outside beat"
        assert ts == sorted(ts), f"{bid}: cues out of order"
        return list(ts)
    t0 = round(s + min(1.9, dur * 0.26), 3)
    t1 = round(s + min(dur - 0.85, AD[bid] + 0.1), 3)
    if n == 1:
        return [t0]
    return [round(t0 + (t1 - t0) * k / (n - 1), 3) for k in range(n)]


def timeline_js():
    js = ["const tl = gsap.timeline({ paused: true });"]
    marks = []
    halves = []
    for i, bid in enumerate(IDS):
        s, dur = VS[bid], VD[bid]
        e = round(s + dur, 3)
        # exactly one copy block is displayed at any instant, so the layout
        # inspector never samples two headings sharing the frame.
        js.append(f'tl.set("#c-{bid}", {{ display: "block" }}, {s});')
        js.append(f'tl.fromTo("#h-{bid}", {{ opacity: 0, y: 24 }}, '
                  f'{{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, '
                  f'{round(s + 0.12, 3)});')
        marks.append(round(s + 0.12, 3))
        if COPY[bid][1]:
            sub_t = round(s + min(1.15, dur * 0.2), 3)
            js.append(f'tl.fromTo("#b-{bid}", {{ opacity: 0, y: 18 }}, '
                      f'{{ opacity: 1, y: 0, duration: 0.45, '
                      f'ease: "power3.out" }}, {sub_t});')
            marks.append(sub_t)
        if i < len(IDS) - 1:
            js.append(f'tl.to("#c-{bid}", {{ opacity: 0, duration: 0.3, '
                      f'ease: "power2.in" }}, {round(e - 0.3, 3)});')
            js.append(f'tl.set("#c-{bid}", {{ display: "none" }}, {e});')
            marks.append(round(e - 0.3, 3))
        ev = SCHEDULE.get(bid, [])
        if ev:
            ts = reveal_times(bid, len(ev))
            for fn, t in zip(ev, ts):
                js.append(fn(t))
                marks.append(t)
            # every beat must still be developing after its own midpoint —
            # this is the exact defect revision 1 exists to close.
            mid = s + dur / 2.0
            halves.append((bid, sum(1 for t in ts if t >= mid)))
    import re as _re
    straddle = []
    joined = "\n".join(js)
    for m in _re.finditer(r'tl\.(?:to|fromTo)\("([^"]+)",(.*?)\},\s*([0-9.]+)\);',
                          joined, _re.S):
        sel, body, t0 = m.group(1), m.group(2), float(m.group(3))
        if "strokeDashoffset" in body or sel.startswith("#c-"):
            continue
        dm = _re.search(r"duration:\s*([0-9.]+)", body)
        if not dm:
            continue
        t1 = t0 + float(dm.group(1))
        for bid in IDS:
            mid = VS[bid] + VD[bid] / 2.0
            if t0 < mid < t1:
                straddle.append((bid, sel, round(t0, 3), round(t1, 3)))
    marks = sorted(set(marks))
    worst = max(b - a for a, b in zip(marks, marks[1:]))
    js.append('window.__timelines["board"] = tl;')
    return "\n        ".join(js), worst, marks, halves, straddle


# Root-relative, in BOTH files. A sub-composition is served with the PROJECT
# ROOT as its base URL, not compositions/ — "../assets/..." renders fine but
# 404s in preview, and `hyperframes check` fails it as
# invalid_parent_traversal_in_asset_path.
FONTS = "".join(
    f'@font-face{{font-family:"Proxima Nova";src:url("assets/fonts/'
    f'proxima-nova-{w}.woff2") format("woff2");font-weight:{w};'
    f'font-style:normal;font-display:block;}}' for w in (400, 700, 900))

TL_JS, WORST_GAP, MARKS, HALVES, STRADDLE = timeline_js()

BOARD = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <style>
      {FONTS}
    </style>
    <style>
      #root {{
        position: absolute;
        inset: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        font-family: "Proxima Nova", system-ui, sans-serif;
      }}
      #board {{
        position: absolute;
        left: 0;
        top: 390px;
        width: 1920px;
        height: 690px;
      }}
      #copy {{
        position: absolute;
        left: 150px;
        top: 138px;
        width: 1600px;
        height: 244px;
      }}
      .beat {{
        position: absolute;
        left: 0;
        top: 0;
        width: 1600px;
        display: none;
      }}
      .beat h2 {{
        font-family: "Proxima Nova", system-ui, sans-serif;
        font-size: 64px;
        font-weight: 900;
        line-height: 1.06;
        letter-spacing: -0.012em;
        color: {PAPER};
      }}
      .beat-title h1 {{
        font-family: "Proxima Nova", system-ui, sans-serif;
        font-size: 92px;
        font-weight: 900;
        line-height: 1.07;
        letter-spacing: -0.016em;
        color: {PAPER};
        max-width: 1400px;
      }}
      .beat .sub {{
        font-family: "Proxima Nova", system-ui, sans-serif;
        font-size: 44px;
        font-weight: 400;
        line-height: 1.24;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 24px;
        max-width: 1560px;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="board" data-width="1920" data-height="1080">
      {board_svg()}
      <div id="copy">
        {beat_blocks()}
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      {TL_JS}
    </script>
  </body>
</html>
"""

AUDIO = "\n      ".join(
    f'<audio id="vo-{r["id"]}" src="assets/voice/{r["id"]}.wav" '
    f'data-start="{r["audio_start"]}" data-duration="{r["audio_dur"]}" '
    f'data-track-index="10" data-volume="1"></audio>' for r in ROWS)

INDEX = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      {FONTS}
    </style>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        margin: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: {NAVY_DEEP};
      }}
      body {{
        font-family: "Proxima Nova", system-ui, sans-serif;
      }}
      #bg {{
        position: absolute;
        inset: 0;
        background: {NAVY_DEEP};
      }}
      #bg-lift {{
        position: absolute;
        inset: 0;
        background: radial-gradient(
          124% 80% at 52% 64%,
          rgba(13, 36, 55, 1) 0%,
          rgba(10, 30, 47, 1) 74%
        );
      }}
      #chrome-text {{
        position: absolute;
        left: 120px;
        top: 60px;
        font-family: "Proxima Nova", system-ui, sans-serif;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: rgba(51, 147, 214, 0.95);
      }}
      #chrome-rule {{
        position: absolute;
        left: 120px;
        top: 99px;
        width: 128px;
        height: 4px;
        background: {GOLD};
      }}
      #root > div[data-composition-src] {{
        position: absolute;
        inset: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
      <div id="bg"><div id="bg-lift"></div></div>

      <div id="chrome"><span id="chrome-text">Early Career Boost</span><span id="chrome-rule"></span></div>

      <!-- ONE carrying object for the whole runtime: the decision board.
           s01 -> s25 — marked, punched, re-sorted once, then stripped back.
           Never rebuilt, never left. See design.md. -->
      <div id="el-board" data-composition-id="board" data-composition-src="compositions/board.html" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-width="1920" data-height="1080"></div>

      <!-- Narration — HeyGen, Oxana (tokens.yml voice.voice_id). One element
           per beat at GLOBAL time; every number is read from timing.json. -->
      {AUDIO}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.set("#chrome", {{ opacity: 1 }}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

(WS / "compositions").mkdir(exist_ok=True)
(WS / "compositions" / "board.html").write_text(BOARD)
(WS / "index.html").write_text(INDEX)
flat = [b for b, n in HALVES if n == 0]
print(f"wrote index.html + compositions/board.html — {len(IDS)} beats, "
      f"{TOTAL}s, {len(MARKS)} cued reveals, worst quiet gap {WORST_GAP:.2f}s")
print(f"beats with a reveal after their own midpoint: "
      f"{sum(1 for _b, n in HALVES if n)}/{len(HALVES)}"
      + (f" — FLAT: {flat}" if flat else ""))
print(f"reveals sampled mid-fade by the graded grid: {len(STRADDLE)}"
      + (" — " + ", ".join(f"{b}{s}" for b, s, _a, _z in STRADDLE)
         if STRADDLE else ""))
