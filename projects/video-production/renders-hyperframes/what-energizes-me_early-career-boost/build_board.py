#!/usr/bin/env python3
"""build_board.py — emit index.html + compositions/board.html for this build.

The HTML is the authored artifact; this script is how it is authored without
hand-typing 700 absolute timestamps. Every time it writes is DERIVED from
timing.json (beat windows) and audio_meta.json (the word that earns each
reveal) — nothing here is hand-tuned, and re-running after a re-synthesis
reproduces the composition exactly.

One carrying object: the Energizing Work Worksheet at wall size. See design.md.

    python3 build_board.py
"""
import json
import math
import random
import re
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# tokens.yml colors, as rgb triples. check_brand.py grades every literal in the
# emitted CSS/SVG against tokens.yml `colors:` at any alpha, so every paint in
# this file is built from this table.
# ---------------------------------------------------------------------------
C = {
    "navy": (13, 36, 55),
    "blue": (51, 147, 214),
    "gold": (234, 171, 45),
    "ink": (41, 47, 53),
    "paper": (255, 255, 255),
    "cultured": (246, 246, 249),
    "fill_subtle": (229, 239, 246),
    "border": (204, 206, 223),
    "muted_video": (95, 111, 150),
}


def rgba(name, a=1.0):
    r, g, b = C[name]
    return f"rgba({r},{g},{b},{a})" if a < 1 else f"rgb({r},{g},{b})"


# ---------------------------------------------------------------------------
# GEOMETRY — every number inside the loaded keep-outs (safe-area 72,
# frame-padding 120, content-bottom 960); see design.md's geometry table.
# ---------------------------------------------------------------------------
BOARD = dict(x=150, y=126, w=1620, h=832)      # 82% of the safe area
HEAD_RULE_Y = 250
RAIL_LINE_Y = 262
RAIL_Y = 270
COLHEAD_Y = 342
COL_RULE_Y = 394
FIELD_TOP, FIELD_BOT = 406, 870
CHIP_Y = 890                  # the struck attractors sit on the board's foot
GUTTER_X = 905
COL_L, COL_R, COL_END = 250, 905, 1560
LEFT_MARGIN_X = 196
RES_X, RES_W = 1580, 160
DIR_X = 1752

SLIP_W, SLIP_H = 96, 64
L_X0, R_X0, X_PITCH = 287, 942, 121
ROW_Y = [406, 502, 598, 694]
L_ROWS, R_ROWS = 4, 3
N_RES = 32
BAR_H, BAR_PITCH = 10, 14

BANDS = [(406, 140), (568, 140), (730, 140)]
PIN_Y = [406 + i * 55 for i in range(9)]

HEAP = [(700 + c * 140, 660 + r * 56) for r in range(3) for c in range(6)]

# ---------------------------------------------------------------------------
# THE BEAT PLAN.  Two arrivals per beat, both on that beat's own word timings:
# one at the opening word, one in the BACK HALF. A beat whose picture is
# finished halfway through is dead air for the rest of it.
# ---------------------------------------------------------------------------
HEADINGS = {
    "s02": "Specific to You",
    "s03": "A More Reliable Question",
    "s05": "Energy Is Observable",
    "s06": "You Already Have Data",
    "s10": "That Pattern Is a Signal",
    "s11": "Two Columns",
    "s12": "The Energizing Work Worksheet",
    "s13": "What You're Not Doing",
    "s15": "Look for Patterns",
    "s17": "The Ingredients of Work That Fits You",
    "s18": "Genuinely Hard to Name",
    "s20": "Not Always Obvious",
    "s21": "Several Experiences, Side by Side",
    "s22": "The Tasks That Feel Most Engaging",
    "s23": "The Ways You Like to Contribute",
    "s24": "Early Clues About Roles or Paths",
    "s25": "A Structured Conversation",
    "s27": "Not One Path",
    "s28": "Better Language and Insight",
    "s29": "Now It's Your Turn",
    "s30": "Your AI Energy Coach",
    "s32": "Answer Honestly",
    "s33": "One Question at a Time",
    "s34": "It Reflects Back the Patterns",
    "s36": "Be Specific and Honest",
    "s38": "End the Conversation Any Time",
    "s39": "Two or Three Patterns",
    "s40": "Enough to Point Yourself Somewhere",
}

CHIPS = [
    ("c1", "Passion", "s03", "s04"),
    ("c2", "A Lightning-Bolt Answer", "s14", "s14"),
    ("c3", "A Job Title", "s16", "s16"),
    ("c4", "What You Should Enjoy", "s26", "s26"),
]

TAGS = ["Organizing", "Creating", "Helping", "Solving", "Analyzing"]

# (beat, [sides]) — every slip comes OUT of the reserve, so placements and
# reserve bars are conserved 1:1. Slips placed before s15 land in the heap.
PLACEMENTS = [
    ("s07", list("LLRLR")), ("s08", list("LLR")), ("s09", list("RR")),
    ("s10", list("LRL")), ("s13", list("LR")), ("s14", list("LL")),
    ("s16", list("LRL")), ("s17", list("LRLR")), ("s18", list("L")),
    ("s19", list("R")), ("s20", list("LLR")), ("s39", list("LRL")),
]
MIGRATION_BEAT = "s15"          # the heap flies up into the two columns
PAYOFF_BEAT = "s39"             # the reserve's last three bars are spent


def stem_words(text):
    return re.findall(r"[A-Za-z][A-Za-z'’]*", text)


class Clock:
    """Absolute times, derived only from timing.json + audio_meta.json."""

    def __init__(self):
        t = json.loads((WS / "timing.json").read_text())
        m = json.loads((WS / "audio_meta.json").read_text())
        r = json.loads((WS / "audio_request.json").read_text())
        self.total = float(t["total"])
        self.rows = {row["id"]: row for row in t["rows"]}
        self.order = [ln["id"] for ln in r["lines"]]
        self.text = {ln["id"]: ln["text"] for ln in r["lines"]}
        self.voices = {v["id"]: v for v in m["voices"]}

    def span(self, bid):
        row = self.rows[bid]
        words = self.voices[bid]["words"]
        a0 = float(row["audio_start"])
        return a0, a0 + max(float(w["end"]) for w in words)

    def frac(self, bid, f):
        """f of the way through this beat's SPOKEN span."""
        a0, a1 = self.span(bid)
        return round(a0 + (a1 - a0) * f, 3)

    def word(self, bid, needle, nth=0):
        """The start of the nth occurrence of `needle` in this beat's words."""
        a0 = float(self.rows[bid]["audio_start"])

        def norm(s):
            return re.sub(r"[^a-z]", "", s.lower())

        want = norm(needle)
        hits = [w for w in self.voices[bid]["words"] if norm(w["text"]) == want]
        if not hits:   # "lightning" inside the token "lightning-bolt"
            hits = [w for w in self.voices[bid]["words"]
                    if norm(w["text"]).startswith(want)]
        if len(hits) <= nth:
            raise KeyError(f"{bid}: word {needle!r}#{nth} not found in "
                           f"{[w['text'] for w in self.voices[bid]['words']]}")
        return round(a0 + float(hits[nth]["start"]), 3)

    def open(self, bid):
        """The beat's picture leads its own audio — vis_start."""
        return round(float(self.rows[bid]["vis_start"]), 3)


def main():
    ck = Clock()
    js = []          # timeline statements
    body = []        # markup
    css = []

    def add(stmt):
        js.append("          " + stmt)

    # ---- slip bookkeeping -------------------------------------------------
    slips = []       # dicts: id, side, slot, x, y, beat, heap
    l_used = r_used = 0
    heap_i = 0
    for beat, sides in PLACEMENTS:
        for side in sides:
            if side == "L":
                slot, l_used = l_used, l_used + 1
                row, col = divmod(slot, 5)
                x, y = L_X0 + col * X_PITCH, ROW_Y[row]
            else:
                slot, r_used = r_used, r_used + 1
                row, col = divmod(slot, 5)
                x, y = R_X0 + col * X_PITCH, ROW_Y[row]
            s = dict(i=len(slips), side=side, row=row, col=col, x=x, y=y,
                     beat=beat, heap=None)
            if ck.order.index(beat) < ck.order.index(MIGRATION_BEAT):
                s["heap"] = HEAP[heap_i]
                heap_i += 1
            slips.append(s)
    assert l_used <= L_ROWS * 5 and r_used <= R_ROWS * 5, (l_used, r_used)

    early = [s for s in slips if s["beat"] != PAYOFF_BEAT]
    # Reading order across BOTH columns, row by row — the order the question-pin
    # sweeps, so the ink map grows in a direction a viewer can follow.
    pin_order = sorted(early, key=lambda s: (s["row"], 0 if s["side"] == "L" else 1,
                                             s["col"]))
    po = [s["i"] for s in pin_order]

    # ---- threads ----------------------------------------------------------
    rng = random.Random(7)
    hub_a, hub_b = po[3], po[16]
    cross = [(s["i"], t["i"]) for s in early for t in early
             if s["side"] == "L" and t["side"] == "R"]
    same = [(s["i"], t["i"]) for s in early for t in early
            if s["side"] == t["side"] and s["i"] < t["i"]]
    rng.shuffle(cross)
    rng.shuffle(same)
    hub_pairs = ([(hub_a, j) for j in rng.sample([s["i"] for s in early if s["i"] != hub_a], 6)]
                 + [(hub_b, j) for j in rng.sample([s["i"] for s in early if s["i"] != hub_b], 6)])
    THREADS = {
        "s21": cross[0:3] + same[0:2] + [("late", cross[3:6] + same[2:3])],
        "s22": [("late", cross[6:8] + same[3:4])],
        "s24": [("late", cross[8:10] + same[4:5])],
        "s25": [("late", cross[10:12])],
        "s26": cross[12:15] + [("late", [])],
        "s27": [("late", same[5:7])],
        "s28": hub_pairs[0:4] + [("late", [])],
        "s29": [("late", cross[15:17])],
        "s30": hub_pairs[4:7] + [("late", hub_pairs[7:9])],
        "s31": same[7:9] + [("late", cross[25:28])],
        "s32": [("late", hub_pairs[9:12])],
        "s34": cross[17:20] + [("late", [])],
        "s35": same[9:11] + [("late", cross[28:31])],
        "s36": [("late", cross[20:23])],
        "s37": cross[31:36] + [("late", same[11:14])],
        "s38": [("late", cross[23:25])],
    }

    # flatten into an ordered, de-duplicated thread list
    thread_moves = []      # (beat, when, [(a,b)...])
    seen = set()
    for bid in ["s21", "s22", "s24", "s25", "s26", "s27", "s28", "s29",
                "s30", "s31", "s32", "s34", "s35", "s36", "s37", "s38"]:
        opening, late = [], []
        for item in THREADS[bid]:
            if isinstance(item, tuple) and item and item[0] == "late":
                late += list(item[1])
            else:
                opening.append(item)
        for when, pairs in (("open", opening), ("late", late)):
            keep = []
            for a, b in pairs:
                key = tuple(sorted((a, b)))
                if key in seen or a == b:
                    continue
                seen.add(key)
                keep.append(key)
            if keep:
                thread_moves.append((bid, when, keep))
    threads = [p for _, _, ps in thread_moves for p in ps]

    # ---- interior strokes -------------------------------------------------
    # Monotone: a slip's stroke count only ever rises, and rises UNEVENLY, so
    # the board gains texture rather than population.
    def grp(a, b):
        return po[a:b]

    STROKES = [
        ("s19", "late", grp(0, 4), 1), ("s20", "late", grp(4, 9), 1),
        ("s22", "open", grp(0, 6), 2), ("s25", "open", grp(9, 14), 1),
        ("s27", "open", grp(14, 18), 1), ("s28", "late", grp(6, 10), 2),
        ("s29", "open", grp(18, 22), 1), ("s31", "open", grp(10, 14), 2),
        ("s32", "late", grp(22, 26), 1), ("s33", "late", grp(0, 6), 3),
        ("s34", "late", grp(14, 18), 2), ("s35", "open", grp(26, 29), 1),
        ("s36", "open", grp(0, 6), 4), ("s37", "open", grp(25, 29), 2),
        ("s37", "late", grp(18, 22), 2),
    ]
    level = {s["i"]: 0 for s in slips}
    for bid, _when, ids, n in STROKES:
        for i in ids:
            assert n > level[i], f"{bid}: slip {i} stroke {n} not > {level[i]}"
            level[i] = n

    # =======================================================================
    # CSS
    # =======================================================================
    css.append(f"""
      #root {{ position: absolute; inset: 0; width: 1920px; height: 1080px;
               font-family: "Proxima Nova", sans-serif; overflow: hidden; }}
      #bd-wall {{ position: absolute; inset: 0; background: {rgba('cultured')}; }}
      #bd-wash {{ position: absolute; left: 960px; top: 540px; width: 2000px;
                  height: 1300px; margin: -650px 0 0 -1000px;
                  background: radial-gradient(ellipse at center,
                    {rgba('blue', 0.10)} 0%, {rgba('blue', 0.04)} 42%,
                    {rgba('cultured', 0)} 72%); will-change: transform; }}
      #bd-board {{ position: absolute; left: {BOARD['x']}px; top: {BOARD['y']}px;
                   width: {BOARD['w']}px; height: {BOARD['h']}px;
                   background: {rgba('paper')}; border: 2px solid {rgba('border')};
                   border-radius: 10px; opacity: 0; }}
      .bd-pin {{ position: absolute; width: 14px; height: 14px; border-radius: 50%;
                 background: {rgba('blue', 0.55)}; opacity: 0; }}
      .bd-rule {{ position: absolute; height: 2px; background: {rgba('border')};
                  transform-origin: left center; opacity: 0; }}
      .bd-ruled {{ position: absolute; height: 2px; background: {rgba('border', 0.7)};
                   transform-origin: left center; opacity: 0; }}
      #bd-gutter {{ position: absolute; left: {GUTTER_X}px; top: {FIELD_TOP}px;
                    width: 2px; height: {FIELD_BOT - FIELD_TOP}px;
                    background: {rgba('blue', 0.55)}; transform-origin: top center; }}
      #bd-gstrike {{ position: absolute; width: 480px; height: 5px;
                     left: 665px; top: 636px; background: {rgba('gold')};
                     transform-origin: center center; opacity: 0; }}
      .bd-hd {{ position: absolute; left: 190px; top: 142px; width: 1080px;
                font-size: 58px; font-weight: 900; line-height: 1.18;
                letter-spacing: -0.015em; color: {rgba('navy')}; opacity: 0; }}
      #bd-title {{ position: absolute; left: 190px; top: 392px; width: 1300px;
                   font-size: 104px; font-weight: 900; line-height: 1.08;
                   letter-spacing: -0.02em; color: {rgba('navy')}; opacity: 0; }}
      #bd-titlerule {{ position: absolute; left: 190px; top: 348px; width: 220px;
                       height: 8px; background: {rgba('gold')};
                       transform-origin: left center; transform: scaleX(0); }}
      #bd-corner {{ position: absolute; left: 1478px; top: 140px; width: 268px;
                    opacity: 0; }}
      .bd-cap {{ font-size: 26px; font-weight: 700; letter-spacing: 0.14em;
                 text-transform: uppercase; color: {rgba('muted_video')}; }}
      #bd-cticks {{ margin-top: 14px; display: flex; gap: 12px; }}
      #bd-cticks span {{ display: block; width: 40px; height: 6px;
                         background: {rgba('blue', 0.5)}; }}
      #bd-chips {{ position: absolute; left: 190px; top: {CHIP_Y}px; display: flex;
                   gap: 40px; align-items: center; }}
      .bd-chip {{ position: relative; font-size: 40px; font-weight: 700;
                  color: {rgba('ink')}; opacity: 0; white-space: nowrap; }}
      .bd-chip i {{ position: absolute; left: -6px; top: 50%; display: block;
                    width: calc(100% + 12px); height: 4px; background: {rgba('gold')};
                    transform-origin: left center; transform: scaleX(0);
                    font-style: normal; }}
      #bd-rail {{ position: absolute; left: 250px; top: {RAIL_Y}px; width: 1310px;
                  display: flex; gap: 26px; }}
      .bd-tag {{ font-size: 26px; font-weight: 700; letter-spacing: 0.14em;
                 text-transform: uppercase; color: {rgba('navy')};
                 border: 2px solid {rgba('blue', 0.45)}; border-radius: 100px;
                 padding: 8px 22px; opacity: 0; }}
      #bd-railline {{ position: absolute; left: 250px; top: {RAIL_LINE_Y}px;
                      width: 1310px; height: 2px; background: {rgba('blue', 0.3)};
                      transform-origin: left center; transform: scaleX(0); }}
      #bd-colheads {{ position: absolute; left: 250px; top: {COLHEAD_Y}px;
                      width: 1310px; display: flex; }}
      .bd-colhead {{ flex: 1; text-align: center; font-size: 30px; font-weight: 900;
                     letter-spacing: 0.14em; text-transform: uppercase;
                     color: {rgba('navy')}; opacity: 0; }}
      .bd-slip {{ position: absolute; width: {SLIP_W}px; height: {SLIP_H}px;
                  border: 2px solid {rgba('border')}; border-radius: 6px;
                  background: {rgba('fill_subtle', 0.5)}; opacity: 0; }}
      .bd-slip .edge {{ position: absolute; left: 0; bottom: -2px; width: 100%;
                        height: 8px; opacity: 0; }}
      .bd-slip .flat {{ background: {rgba('muted_video', 0.75)}; }}
      .bd-slip .stroke {{ position: absolute; left: 14px; height: 6px;
                          background: {rgba('ink', 0.62)}; transform-origin: left center;
                          transform: scaleX(0); }}
      .bd-bar {{ position: absolute; left: {RES_X}px; width: {RES_W}px;
                 height: {BAR_H}px; background: {rgba('navy', 0.32)};
                 border-radius: 2px; opacity: 0; }}
      #bd-resout {{ position: absolute; left: {RES_X - 6}px; width: {RES_W + 12}px;
                    border: 2px dashed {rgba('border')}; border-radius: 6px;
                    opacity: 0; }}
      #bd-threads {{ position: absolute; inset: 0; }}
      #bd-track {{ position: absolute; left: {LEFT_MARGIN_X}px; top: {FIELD_TOP}px;
                   width: 2px; height: {FIELD_BOT - FIELD_TOP}px;
                   background: {rgba('border')}; transform-origin: top center;
                   transform: scaleY(0); }}
      #bd-qpin {{ position: absolute; left: {LEFT_MARGIN_X - 11}px;
                  top: {PIN_Y[0] - 12}px; width: 24px; height: 24px;
                  border-radius: 50%; background: {rgba('gold')}; opacity: 0; }}
      #bd-qtick {{ position: absolute; left: {LEFT_MARGIN_X + 6}px;
                   top: {PIN_Y[0] - 2}px; width: 44px; height: 3px;
                   background: {rgba('gold', 0.7)}; opacity: 0; }}
      #bd-dir {{ position: absolute; left: {DIR_X}px; top: {FIELD_TOP}px; width: 3px;
                 height: {FIELD_BOT - FIELD_TOP}px; background: {rgba('gold', 0.25)};
                 transform-origin: top center; transform: scaleY(0); }}
      .bd-dtick {{ position: absolute; left: {DIR_X - 12}px; width: 26px; height: 3px;
                   background: {rgba('gold', 0.35)}; opacity: 0; }}
      #bd-arrow {{ position: absolute; left: {DIR_X - 13}px; top: {FIELD_BOT - 4}px;
                   width: 28px; height: 28px;
                   border-right: 4px solid {rgba('gold')};
                   border-bottom: 4px solid {rgba('gold')};
                   transform-origin: center; opacity: 0; }}
      .bd-band {{ position: absolute; left: 250px; width: 1490px;
                  background: {rgba('fill_subtle', 0.75)};
                  border-top: 3px solid {rgba('gold', 0.55)};
                  border-radius: 6px; opacity: 0; }}
      .bd-bandhead {{ position: absolute; left: 268px; font-size: 26px;
                      font-weight: 700; letter-spacing: 0.14em;
                      text-transform: uppercase; color: {rgba('navy')};
                      opacity: 0; }}
    """)

    # =======================================================================
    # MARKUP
    # =======================================================================
    body.append('<div id="bd-wall"></div>'
                '<div id="bd-wash" data-layout-allow-overflow></div>')
    body.append('<div id="bd-board"></div>')
    for n, (px, py) in enumerate([(BOARD['x'] + 26, BOARD['y'] + 26),
                                  (BOARD['x'] + BOARD['w'] - 40, BOARD['y'] + 26),
                                  (BOARD['x'] + 26, BOARD['y'] + BOARD['h'] - 40),
                                  (BOARD['x'] + BOARD['w'] - 40,
                                   BOARD['y'] + BOARD['h'] - 40)]):
        body.append(f'<span class="bd-pin" id="bd-pin{n}" '
                    f'style="left:{px}px;top:{py}px"></span>')

    body.append(f'<div class="bd-rule" id="bd-headrule" '
                f'style="left:{BOARD["x"]}px;top:{HEAD_RULE_Y}px;'
                f'width:{BOARD["w"]}px"></div>')
    body.append(f'<div class="bd-rule" id="bd-colrule" '
                f'style="left:250px;top:{COL_RULE_Y}px;width:1310px"></div>')
    for i in range(11):
        body.append(f'<div class="bd-ruled" id="bd-r{i}" '
                    f'style="left:262px;top:{FIELD_TOP + 8 + i * 38}px;'
                    f'width:1286px"></div>')
    body.append('<div id="bd-gutter"></div><div id="bd-gstrike"></div>')

    body.append('<h1 id="bd-title">What Energizes Me</h1>')
    body.append('<div id="bd-titlerule"></div>')
    body.append('<div id="bd-corner"><div class="bd-cap">Last Lesson</div>'
                '<div id="bd-cticks">' + "".join("<span></span>" for _ in range(5))
                + '</div></div>')

    for bid, text in sorted(HEADINGS.items()):
        body.append(f'<h2 class="bd-hd" id="bd-hd-{bid}" data-role="heading">'
                    f'{text}</h2>')

    body.append('<div id="bd-chips" data-role="list">')
    for cid, label, _a, _b in CHIPS:
        body.append(f'  <div class="bd-chip" id="bd-{cid}">{label}<i></i></div>')
    body.append('</div>')

    body.append('<div id="bd-railline"></div>')
    body.append('<div id="bd-rail" data-role="list">')
    for n, tag in enumerate(TAGS):
        body.append(f'  <span class="bd-tag" id="bd-tag{n}">{tag}</span>')
    body.append('</div>')

    body.append('<div id="bd-colheads" data-role="compare">')
    body.append('  <div class="bd-colhead" id="bd-colL" data-role="card">Energizes</div>')
    body.append('  <div class="bd-colhead" id="bd-colR" data-role="card">Drains</div>')
    body.append('</div>')

    body.append('<div id="bd-track"></div><div id="bd-qpin"></div>'
                '<div id="bd-qtick"></div>')
    body.append('<div id="bd-dir"></div>')
    for n, ty in enumerate([520, 660, 800]):
        body.append(f'<div class="bd-dtick" id="bd-dt{n}" style="top:{ty}px"></div>')
    body.append('<div id="bd-arrow"></div>')

    for n, (by, bh) in enumerate(BANDS):
        body.append(f'<div class="bd-band" id="bd-band{n}" '
                    f'style="top:{by}px;height:{bh}px"></div>')
    for n in range(3):
        body.append(f'<div class="bd-bandhead" id="bd-bh{n}" '
                    f'style="top:{BANDS[n][0] + 54}px">{TAGS[[0, 1, 3][n]]}</div>')

    # reserve: bar 0 at the bottom, stack grows up. Only ever falls.
    for n in range(N_RES):
        top = FIELD_BOT - BAR_H - n * BAR_PITCH
        body.append(f'<div class="bd-bar" id="bd-bar{n}" style="top:{top}px"></div>')
    body.append(f'<div id="bd-resout" style="top:{FIELD_BOT - BAR_H - (N_RES - 1) * BAR_PITCH - 6}px;'
                f'height:{(N_RES - 1) * BAR_PITCH + BAR_H + 12}px"></div>')

    body.append('<svg id="bd-threads" viewBox="0 0 1920 1080" width="1920" height="1080">')
    for n, (a, b) in enumerate(threads):
        sa, sb = slips[a], slips[b]
        x1, y1 = sa["x"] + SLIP_W / 2, sa["y"] + SLIP_H / 2
        x2, y2 = sb["x"] + SLIP_W / 2, sb["y"] + SLIP_H / 2
        body.append(f'  <line id="bd-th{n}" x1="{x1:.0f}" y1="{y1:.0f}" '
                    f'x2="{x2:.0f}" y2="{y2:.0f}" stroke="{rgba("blue", 0.42)}" '
                    f'stroke-width="2" opacity="0"></line>')
    body.append('</svg>')

    for s in slips:
        inner = ['<span class="edge"></span>']
        for k in range(4):
            inner.append(f'<span class="stroke" style="top:{12 + k * 12}px;'
                         f'width:{[64, 48, 68, 42][k]}px"></span>')
        body.append(f'<div class="bd-slip" id="bd-s{s["i"]}" '
                    f'style="left:{s["x"]}px;top:{s["y"]}px">'
                    + "".join(inner) + '</div>')

    # =======================================================================
    # TIMELINE — every time absolute, derived from the clock
    # =======================================================================
    add('const IN = "power3.out";')
    add('const POP = "back.out(1.5)";')
    add('function arrive(sel, t, dy, dur) {')
    add('  tl.set(sel, { opacity: 1, y: dy }, t);')
    add('  tl.to(sel, { y: 0, duration: dur || 0.42, ease: IN }, t);')
    add('}')
    add('function leave(sel, t, dy) {')
    add('  tl.to(sel, { opacity: 0, y: dy, duration: 0.28, ease: "power2.in" }, t);')
    add('}')
    add('function ink(sel, t, dur) {')
    add('  tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: dur || 0.5, '
        'ease: "power2.out" }, t);')
    add('}')
    add('function grow(sel, t, dur) {')
    add('  tl.fromTo(sel, { scaleY: 0 }, { scaleY: 1, duration: dur || 0.6, '
        'ease: "power2.out" }, t);')
    add('}')
    add('function show(sel, t, dur) {')
    add('  tl.to(sel, { opacity: 1, duration: dur || 0.35, ease: "power2.out" }, t);')
    add('}')
    add('function pop(sel, t) {')
    add('  tl.fromTo(sel, { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, '
        'duration: 0.4, ease: POP }, t);')
    add('}')
    add("")

    # ---- one ambient breath, on the background wash alone -----------------
    legs = max(2, int(ck.total / 8) * 2)
    add(f'tl.fromTo("#bd-wash", {{ scale: 1, opacity: 0.9 }}, '
        f'{{ scale: 1.045, opacity: 1, duration: 8, ease: "sine.inOut", '
        f'yoyo: true, repeat: {legs - 1} }}, 0); '
        f'/* motion-allow: background depth-drift on a non-content wash layer; '
        f'design.md sanctions ambient breath on the background only */')
    add("")

    # Initial transform state lives in the TIMELINE, not in CSS, for anything a
    # plain tl.to() later touches — GSAP overwrites the whole CSS transform.
    add('tl.set("#bd-gutter", { scaleY: 0 }, 0);')
    add('tl.set("#bd-arrow", { rotation: 45 }, 0);')
    add("")

    heap_slips = [s for s in slips if s["heap"]]
    for s in heap_slips:
        hx, hy = s["heap"]
        rot = [-2.4, 1.8, -1.2, 2.6, -1.8, 1.1][s["i"] % 6]
        add(f'tl.set("#bd-s{s["i"]}", {{ x: {hx - s["x"]}, y: {hy - s["y"]}, '
            f'rotation: {rot} }}, 0);')
    add("")

    placed_at, sided = {}, set()
    res_left = N_RES

    def place(ids, t, stagger=0.14):
        """A slip leaves the reserve and lands on the board. Conserved 1:1."""
        nonlocal res_left
        for k, i in enumerate(ids):
            tt = round(t + k * stagger, 3)
            res_left -= 1
            add(f'tl.to("#bd-bar{res_left}", {{ opacity: 0, duration: 0.18 }}, '
                f'{tt});')
            add(f'tl.fromTo("#bd-s{i}", {{ opacity: 0, scale: 0.6 }}, '
                f'{{ opacity: 1, scale: 1, duration: 0.4, ease: POP }}, {tt});')
            placed_at[i] = tt

    SERR = (f'"repeating-linear-gradient(135deg, {rgba("gold")} 0 6px, '
            f'{rgba("gold", 0)} 6px 12px)"')
    FLAT = f'"{rgba("muted_video", 0.75)}"'

    def side_edge(ids, t, kind, stagger=0.1):
        """The charge arrives ONCE per slip and is never re-marked."""
        for k, i in enumerate(ids):
            assert i not in sided, f"slip {i} sided twice"
            tt = round(t + k * stagger, 3)
            add(f'tl.set("#bd-s{i} .edge", {{ background: '
                f'{SERR if kind == "serr" else FLAT} }}, {tt});')
            add(f'tl.fromTo("#bd-s{i} .edge", {{ scaleX: 0 }}, {{ scaleX: 1, '
                f'opacity: 1, duration: 0.32, ease: "power2.out" }}, {tt});')
            sided.add(i)

    def strokes(ids, t, level, stagger=0.07):
        # A slip's children are <span class="edge"> then four <span class="stroke">,
        # and nth-of-type counts SPANS — so stroke L is nth-of-type(L + 1).
        for k, i in enumerate(ids):
            tt = round(t + k * stagger, 3)
            add(f'tl.fromTo("#bd-s{i} .stroke:nth-of-type({level + 1})", '
                f'{{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.3, '
                f'ease: "power2.out" }}, {tt});')

    def thread(pairs, t, stagger=0.11):
        for k, pr in enumerate(pairs):
            n = threads.index(pr)
            add(f'tl.fromTo("#bd-th{n}", {{ opacity: 0 }}, {{ opacity: 1, '
                f'duration: 0.34, ease: "power2.out" }}, {round(t + k * stagger, 3)});')

    head_done = set()
    HEAD_AT = {}   # beat -> absolute time override, filled below

    def heading(bid, t=None):
        """Idempotent: a heading arrives exactly ONCE and is never re-marked."""
        if bid not in HEADINGS or bid in head_done:
            return
        head_done.add(bid)
        prev = [b for b in HEADINGS if ck.order.index(b) < ck.order.index(bid)]
        t = HEAD_AT.get(bid, ck.open(bid)) if t is None else t
        if prev:
            last = max(prev, key=lambda b: ck.order.index(b))
            add(f'leave("#bd-hd-{last}", {round(t - 0.36, 3)}, -38);')
        add(f'arrive("#bd-hd-{bid}", {t}, 54);')

    # ----- every heading, once, in beat order ------------------------------
    # Emitted in ONE ordered pass so each heading's exit is chained to the beat
    # that actually follows it; every later heading() call is a no-op.
    HEAD_AT["s02"] = round(ck.open("s02") + 0.18, 3)
    for bid in sorted(HEADINGS, key=lambda b: ck.order.index(b)):
        heading(bid)
    add("")

    # ----- s01 · title card ------------------------------------------------
    add(f'ink("#bd-titlerule", {ck.frac("s01", 0.02)}, 0.5);')
    add(f'arrive("#bd-title", {ck.frac("s01", 0.06)}, 70, 0.5);')
    add(f'tl.set("#bd-corner", {{ x: -1288, y: 486, scale: 1.5, opacity: 0 }}, 0);')
    add(f'show("#bd-corner", {ck.word("s01", "five")}, 0.4);')

    # ----- s02 · the board is born ----------------------------------------
    t = ck.open("s02")
    add(f'leave("#bd-title", {t}, -60);')
    add(f'tl.to("#bd-titlerule", {{ opacity: 0, duration: 0.3 }}, {t});')
    add(f'tl.fromTo("#bd-board", {{ opacity: 0, scale: 0.965 }}, {{ opacity: 1, '
        f'scale: 1, duration: 0.6, ease: IN }}, {t});')
    heading("s02", round(t + 0.18, 3))
    add(f'tl.to("#bd-corner", {{ x: 0, y: 0, scale: 1, duration: 0.7, '
        f'ease: IN }}, {round(t + 0.1, 3)});')
    t1 = ck.frac("s02", 0.10)
    for i in range(11):
        add(f'ink("#bd-r{i}", {round(t1 + i * 0.05, 3)}, 0.45);')
        add(f'tl.set("#bd-r{i}", {{ opacity: 1 }}, {round(t1 + i * 0.05, 3)});')
    t2 = ck.frac("s02", 0.66)
    add(f'ink("#bd-headrule", {t2}, 0.6);')
    add(f'tl.set("#bd-headrule", {{ opacity: 1 }}, {t2});')
    add(f'tl.fromTo("#bd-gutter", {{ scaleY: 0 }}, {{ scaleY: 0.3, '
        f'duration: 0.55, ease: "power2.out" }}, {round(t2 + 0.12, 3)});')

    # ----- s03 · the first attractor arrives -------------------------------
    heading("s03")
    add(f'pop("#bd-c1", {ck.word("s03", "passionate")});')
    t2 = ck.frac("s03", 0.70)
    add(f'tl.to("#bd-colL", {{ opacity: 0.4, duration: 0.35 }}, {t2});')
    add(f'tl.to("#bd-colR", {{ opacity: 0.4, duration: 0.35 }}, {round(t2 + 0.12, 3)});')

    # ----- s04 · the columns take hold, the first attractor is struck ------
    t2 = ck.frac("s04", 0.06)
    add(f'tl.to("#bd-gutter", {{ scaleY: 0.75, duration: 0.6, ease: "power2.out" }}, {t2});')
    add(f'tl.to("#bd-colL", {{ opacity: 1, duration: 0.4 }}, {round(t2 + 0.1, 3)});')
    add(f'tl.to("#bd-colR", {{ opacity: 1, duration: 0.4 }}, {round(t2 + 0.2, 3)});')
    add(f'ink("#bd-c1 i", {ck.word("s04", "vague")}, 0.42);')
    for n in range(4):
        add(f'pop("#bd-pin{n}", {round(ck.frac("s04", 0.74) + n * 0.09, 3)});')

    # ----- s05 · the sheet inks up ----------------------------------------
    heading("s05")
    t2 = ck.frac("s05", 0.5)
    add(f'tl.to("#bd-gutter", {{ scaleY: 0.9, duration: 0.5, ease: "power2.out" }}, {t2});')
    add(f'tl.to("#bd-board", {{ borderColor: "{rgba("navy", 0.35)}", '
        f'duration: 0.5 }}, {round(t2 + 0.1, 3)});')

    # ----- s06 · THE RESERVE ARRIVES ---------------------------------------
    heading("s06")
    t2 = ck.word("s06", "data")
    for n in range(N_RES):
        add(f'tl.fromTo("#bd-bar{n}", {{ opacity: 0, x: 40 }}, {{ opacity: 1, '
            f'x: 0, duration: 0.3, ease: IN }}, {round(t2 + n * 0.022, 3)});')

    # ----- s07..s20 · the board fills --------------------------------------
    idx = 0
    for bid, sides in PLACEMENTS:
        if bid == PAYOFF_BEAT:
            continue
        ids = [slips[idx + k]["i"] for k in range(len(sides))]
        idx += len(sides)
        half = max(1, len(ids) // 2)
        if bid == "s07":
            # one slip per named noun, straight off the voice
            for k, noun in enumerate(["classes", "jobs", "projects",
                                      "volunteer", "group"]):
                place([ids[k]], ck.word("s07", noun))
        else:
            heading(bid)
            place(ids[:half], ck.frac(bid, 0.12))
            place(ids[half:], ck.frac(bid, 0.66))

    # sides — the charge arrives on the words that name it, ONCE per slip.
    # s08 sides the slips already on the board ("buzzing"); s09 does the drain
    # side ("flat"); every slip placed after that arrives already charged, 0.3s
    # behind its own landing, so nothing settled is ever re-marked.
    L_early = [s["i"] for s in early if s["side"] == "L" and s["beat"] == "s07"]
    R_early = [s["i"] for s in early if s["side"] == "R"
               and s["beat"] in ("s07", "s08")]
    side_edge(L_early, ck.word("s08", "buzzing"), "serr")
    side_edge(R_early, ck.word("s09", "flat"), "flat")
    for s in slips:
        i = s["i"]
        if i in sided or s["beat"] == PAYOFF_BEAT:
            continue
        tt = round(placed_at[i] + 0.30, 3)
        add(f'tl.set("#bd-s{i} .edge", {{ background: '
            f'{SERR if s["side"] == "L" else FLAT} }}, {tt});')
        add(f'tl.fromTo("#bd-s{i} .edge", {{ scaleX: 0 }}, {{ scaleX: 1, '
            f'opacity: 1, duration: 0.3, ease: "power2.out" }}, {tt});')
        sided.add(i)

    # ----- s11 · the gutter completes --------------------------------------
    add(f'tl.to("#bd-gutter", {{ scaleY: 1, duration: 0.7, ease: IN }}, '
        f'{ck.word("s11", "columns")});')
    t2 = ck.frac("s11", 0.6)
    add(f'ink("#bd-colrule", {t2}, 0.6);')
    add(f'tl.set("#bd-colrule", {{ opacity: 1 }}, {t2});')

    # ----- s12 · the board is named ----------------------------------------
    heading("s12")
    t2 = ck.frac("s12", 0.55)
    add(f'ink("#bd-railline", {t2}, 0.6);')
    add(f'tl.to("#bd-colrule", {{ backgroundColor: "{rgba("navy", 0.45)}", '
        f'duration: 0.4 }}, {round(t2 + 0.2, 3)});')

    # ----- s13/s14/s16/s26 · the struck chips ------------------------------
    heading("s13")
    add(f'pop("#bd-c2", {ck.word("s14", "lightning")});')
    add(f'ink("#bd-c2 i", {ck.frac("s14", 0.72)}, 0.4);')
    add(f'pop("#bd-c3", {ck.word("s16", "title")});')
    add(f'ink("#bd-c3 i", {ck.frac("s16", 0.85)}, 0.4);')

    # ----- s15 · THE MIGRATION ---------------------------------------------
    heading("s15")
    t2 = ck.word("s15", "patterns")
    for k, s in enumerate(heap_slips):
        add(f'tl.to("#bd-s{s["i"]}", {{ x: 0, y: 0, rotation: 0, duration: 0.75, '
            f'ease: IN }}, {round(t2 + k * 0.035, 3)});')
    add(f'grow("#bd-dir", {ck.frac("s15", 0.72)}, 0.6);')

    # ----- s17 -------------------------------------------------------------
    heading("s17")

    # ----- s18 · the question-pin arrives ----------------------------------
    heading("s18")
    t2 = ck.frac("s18", 0.6)
    add(f'grow("#bd-track", {t2}, 0.5);')
    add(f'tl.set("#bd-track", {{ opacity: 1 }}, {t2});')
    add(f'pop("#bd-qpin", {round(t2 + 0.25, 3)});')
    add(f'show("#bd-qtick", {round(t2 + 0.3, 3)}, 0.3);')

    # ----- strokes ---------------------------------------------------------
    # s37's opening move is word-anchored below (one slip per named noun), so
    # it is skipped here rather than emitted twice.
    for bid, when, ids, n in STROKES:
        if (bid, when) == ("s37", "open"):
            continue
        strokes(ids, ck.frac(bid, 0.12 if when == "open" else 0.62), n)

    # ----- threads ---------------------------------------------------------
    for bid, when, pairs in thread_moves:
        thread(pairs, ck.frac(bid, 0.12 if when == "open" else 0.6))

    for bid in ["s19", "s20", "s21", "s22", "s24", "s25", "s27", "s28",
                "s29", "s30", "s32", "s33", "s34", "s36", "s38"]:
        heading(bid)

    # ----- s23 · the tag rail ----------------------------------------------
    heading("s23")
    for k, noun in enumerate(["organizing", "creating", "helping", "solving",
                              "analyzing"]):
        add(f'pop("#bd-tag{k}", {ck.word("s23", noun)});')
    add(f'tl.to("#bd-railline", {{ backgroundColor: "{rgba("blue")}", '
        f'duration: 0.4 }}, {ck.frac("s23", 0.82)});')

    # ----- s24 · the direction edge gains ticks ----------------------------
    for n in range(3):
        add(f'show("#bd-dt{n}", {round(ck.frac("s24", 0.14) + n * 0.14, 3)}, 0.3);')

    # ----- s26 · the fourth chip -------------------------------------------
    add(f'pop("#bd-c4", {ck.word("s26", "should")});')
    add(f'ink("#bd-c4 i", {ck.frac("s26", 0.86)}, 0.4);')

    # ----- the pin descends, one notch per coach beat ----------------------
    PIN = [("s22", 1), ("s25", 2), ("s27", 3), ("s29", 4), ("s31", 5),
           ("s33", 6), ("s33", 7), ("s33", 8)]
    pin_when = {"s33": ["engaged", "capable", "flow"]}
    n33 = 0
    for bid, notch in PIN:
        if bid == "s33":
            t2 = ck.word("s33", pin_when["s33"][n33])
            n33 += 1
        else:
            t2 = ck.frac(bid, 0.16)
        dy = round(PIN_Y[notch] - PIN_Y[0], 1)
        add(f'tl.to(["#bd-qpin", "#bd-qtick"], {{ y: {dy}, duration: 0.45, '
            f'ease: IN }}, {t2});')
    add(f'tl.to(["#bd-qpin", "#bd-qtick"], {{ y: {round(PIN_Y[8] - PIN_Y[0], 1)}, '
        f'duration: 0.5, ease: IN }}, {ck.frac("s35", 0.16)});')
    add(f'tl.to("#bd-qpin", {{ backgroundColor: "{rgba("border")}", '
        f'duration: 0.4 }}, {ck.frac("s38", 0.2)});')
    add(f'tl.to("#bd-qtick", {{ opacity: 0.35, duration: 0.4 }}, '
        f'{ck.frac("s38", 0.2)});')
    for n in range(3):
        add(f'tl.to("#bd-dt{n}", {{ opacity: 0.75, duration: 0.35 }}, '
            f'{round(ck.frac("s38", 0.62) + n * 0.1, 3)});')

    # ----- s37 · the last blank slips ink, one per named noun --------------
    for k, noun in enumerate(["classes", "jobs", "projects", "roles"]):
        i = po[25 + k]
        add(f'tl.fromTo("#bd-s{i} .stroke:nth-of-type(3)", {{ scaleX: 0 }}, '
            f'{{ scaleX: 1, duration: 0.3, ease: "power2.out" }}, '
            f'{ck.word("s37", noun)});')

    # ----- s39 · the gutter is struck, the bands rule across ---------------
    heading("s39")
    t2 = ck.word("s39", "patterns")
    add(f'tl.set("#bd-gstrike", {{ rotation: 75.4, scaleX: 0, opacity: 1 }}, '
        f'{round(t2 - 0.01, 3)});')
    add(f'tl.to("#bd-gstrike", {{ scaleX: 1, duration: 0.45, ease: IN }}, {t2});')
    add(f'tl.to("#bd-gutter", {{ opacity: 0.22, duration: 0.4 }}, '
        f'{round(t2 + 0.1, 3)});')
    for n in range(3):
        add(f'tl.fromTo("#bd-band{n}", {{ opacity: 0, scaleX: 0.4 }}, '
            f'{{ opacity: 1, scaleX: 1, duration: 0.5, ease: IN }}, '
            f'{round(t2 + 0.18 + n * 0.12, 3)});')
    tail_ids = [slips[idx + k]["i"] for k in range(3)]
    place(tail_ids, ck.frac("s39", 0.68), 0.12)
    for i in tail_ids:
        s = slips[i]
        tt = round(placed_at[i] + 0.26, 3)
        paint = (f'"repeating-linear-gradient(135deg, {rgba("gold")} 0 6px, '
                 f'{rgba("gold", 0)} 6px 12px)"' if s["side"] == "L"
                 else f'"{rgba("muted_video", 0.75)}"')
        add(f'tl.set("#bd-s{i} .edge", {{ background: {paint} }}, {tt});')
        add(f'tl.to("#bd-s{i} .edge", {{ opacity: 1, duration: 0.25 }}, {tt});')
        add(f'tl.fromTo("#bd-s{i} .stroke:nth-of-type(2)", {{ scaleX: 0 }}, '
            f'{{ scaleX: 1, duration: 0.28 }}, {round(tt + 0.1, 3)});')
    add(f'show("#bd-resout", {ck.frac("s39", 0.92)}, 0.4);')

    # ----- s40 · the re-sort, the payoff -----------------------------------
    heading("s40")
    t2 = ck.frac("s40", 0.06)
    lanes = [[], [], []]
    for k, s in enumerate(sorted(slips, key=lambda s: (s["side"] != "L",
                                                       s["row"], s["col"]))):
        lanes[k % 3].append(s)
    for li, lane in enumerate(lanes):
        by, bh = BANDS[li]
        n = len(lane)
        span = min(1176, n * 108)
        x0 = 470
        for k, s in enumerate(lane):
            nx = x0 + (span - SLIP_W) * (k / max(1, n - 1))
            ny = by + (bh - SLIP_H) / 2
            add(f'tl.to("#bd-s{s["i"]}", {{ x: {nx - s["x"]:.1f}, '
                f'y: {ny - s["y"]:.1f}, duration: 0.8, ease: IN }}, '
                f'{round(t2 + k * 0.018, 3)});')
    add(f'tl.to("#bd-threads", {{ opacity: 0.18, duration: 0.5 }}, {t2});')
    t3 = ck.frac("s40", 0.52)
    for n, tagn in enumerate([0, 1, 3]):
        add(f'tl.to("#bd-tag{tagn}", {{ opacity: 0, duration: 0.25 }}, '
            f'{round(t3 + n * 0.14, 3)});')
        add(f'pop("#bd-bh{n}", {round(t3 + 0.12 + n * 0.14, 3)});')
    for tagn in (2, 4):
        add(f'tl.to("#bd-tag{tagn}", {{ opacity: 0.28, duration: 0.4 }}, {t3});')
    add(f'tl.to("#bd-dir", {{ backgroundColor: "{rgba("gold")}", duration: 0.5 }}, '
        f'{round(t3 + 0.2, 3)});')
    add(f'pop("#bd-arrow", {round(t3 + 0.42, 3)});')

    # =======================================================================
    # WRITE
    # =======================================================================
    comp = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
  </head>
  <body>
    <template>
      <style>
        @font-face {{
          font-family: "Proxima Nova";
          src: url("assets/fonts/proxima-nova-400.woff2") format("woff2");
          font-weight: 400; font-style: normal; font-display: block;
        }}
        @font-face {{
          font-family: "Proxima Nova";
          src: url("assets/fonts/proxima-nova-700.woff2") format("woff2");
          font-weight: 700; font-style: normal; font-display: block;
        }}
        @font-face {{
          font-family: "Proxima Nova";
          src: url("assets/fonts/proxima-nova-900.woff2") format("woff2");
          font-weight: 900; font-style: normal; font-display: block;
        }}
      </style>
      <style>{"".join(css)}
      </style>

      <div id="root" data-composition-id="board" data-width="1920" data-height="1080">
        {chr(10) + (chr(10) + "        ").join(body)}
      </div>

      <script>
        window.__timelines = window.__timelines || {{}};
        (function () {{
          const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
          window.__timelines["board"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""
    (WS / "compositions").mkdir(exist_ok=True)
    (WS / "compositions" / "board.html").write_text(comp)

    audio = "\n      ".join(
        f'<audio id="vo-{r["id"]}" src="assets/voice/{r["id"]}.wav" '
        f'data-start="{r["audio_start"]}" data-duration="{r["audio_dur"]}" '
        f'data-track-index="10" data-volume="1"></audio>'
        for r in (ck.rows[b] for b in ck.order))

    index = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      /* Brand face — vendored woff2, declared once in the HOST head. Sub-comps
         are cloned INTO this document, so the face resolves for them too. */
      @font-face {{
        font-family: "Proxima Nova";
        src: url("assets/fonts/proxima-nova-400.woff2") format("woff2");
        font-weight: 400; font-style: normal; font-display: block;
      }}
      @font-face {{
        font-family: "Proxima Nova";
        src: url("assets/fonts/proxima-nova-700.woff2") format("woff2");
        font-weight: 700; font-style: normal; font-display: block;
      }}
      @font-face {{
        font-family: "Proxima Nova";
        src: url("assets/fonts/proxima-nova-900.woff2") format("woff2");
        font-weight: 900; font-style: normal; font-display: block;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden;
                    background: {rgba('cultured')}; }}
      body {{ font-family: "Proxima Nova", sans-serif;
              -webkit-font-smoothing: antialiased; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
      /* The program eyebrow — the ONLY element in the top keep-out, inside the
         rectangle tokens.yml `chrome-regions` grants to label furniture. */
      #chrome {{ position: absolute; left: 120px; top: 58px; display: flex;
                 align-items: center; gap: 18px; opacity: 0; z-index: 5; }}
      #chrome-mark {{ display: block; width: 10px; height: 28px;
                      background: {rgba('gold')}; }}
      #chrome-text {{ font-size: 26px; font-weight: 700; letter-spacing: 0.16em;
                      text-transform: uppercase; color: {rgba('muted_video')}; }}
      #root > div[data-composition-src] {{ position: absolute; inset: 0; z-index: 1; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0"
         data-duration="{ck.total}" data-width="1920" data-height="1080">
      <div id="chrome">
        <span id="chrome-mark"></span>
        <span id="chrome-text">Early Career Boost</span>
      </div>

      <!-- ONE carrying object for the whole runtime: the Energizing Work
           Worksheet at wall size. s02 -> s40, built once, never left.
           See design.md. -->
      <div id="el-board" data-composition-id="board"
           data-composition-src="compositions/board.html" data-start="0"
           data-duration="{ck.total}" data-track-index="1"
           data-width="1920" data-height="1080"></div>

      <!-- Narration — HeyGen starfish, Oxana (tokens.yml voice.voice_id).
           One element per beat at GLOBAL time; every number below is
           timing.json's, computed by make_timing.py from the real wavs. -->
      {audio}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#chrome", {{ opacity: 0, x: -20 }},
                {{ opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }}, 0.25);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (WS / "index.html").write_text(index)
    print(f"board.html: {len(body)} elements, {len(js)} timeline statements, "
          f"{len(slips)} slips, {len(threads)} threads, {len(HEADINGS)} headings")
    print(f"index.html: root {ck.total}s, {len(ck.order)} audio clips")
    return 0


if __name__ == "__main__":
    sys.exit(main())
