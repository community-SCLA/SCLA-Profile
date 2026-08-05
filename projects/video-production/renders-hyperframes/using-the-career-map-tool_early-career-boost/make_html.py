#!/usr/bin/env python3
"""make_html.py — emit index.html + compositions/sheet.html against the FROZEN
timings.

Nothing here is hand-tuned: every cue time is read out of timing.json (computed
by make_timing.py from the real wavs) and audio_meta.json's per-clip word
timestamps.  Each beat gets TWO arrivals — one on its opening words, one in its
back half on a real word onset — so no beat's picture is finished at its
midpoint.

    python3 make_html.py
"""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent
T = json.loads((WS / "timing.json").read_text())
META = json.loads((WS / "audio_meta.json").read_text())
ROWS = {r["id"]: r for r in T["rows"]}
ORDER = [r["id"] for r in T["rows"]]
WORDS = {v["id"]: v["words"] for v in META["voices"]}
TOTAL = T["total"]

# --- colours, straight from tokens.yml `colors:` ---------------------------
NAVY_DEEP = "#0a1e2f"
NAVY = "#0d2437"
BLUE = "#3393d6"
GOLD = "#eaab2d"
INK = "#292f35"
CULTURED = "#f6f6f9"
BORDER = "#cccedf"
MUTED = "#5f6f96"
PAPER = "#ffffff"
FILL = "#e5eff6"


def cue(bid, frac):
    """Absolute time of the word onset nearest `frac` through a beat's words."""
    row, words = ROWS[bid], WORDS[bid]
    if not words:
        return row["vis_start"] + row["vis_dur"] * frac
    i = min(len(words) - 1, max(0, int(round((len(words) - 1) * frac))))
    return round(row["audio_start"] + float(words[i]["start"]), 3)


def a1(bid):
    """First arrival — the beat's picture starts as its first word lands."""
    return round(ROWS[bid]["vis_start"] + 0.08, 3)


def a2(bid, frac=0.58):
    """Second arrival — a real word onset in the beat's BACK HALF."""
    row = ROWS[bid]
    t = cue(bid, frac)
    floor = row["vis_start"] + row["vis_dur"] * 0.45
    return round(max(t, floor), 3)


def a3(bid, frac=0.8):
    return a2(bid, frac)


# ---------------------------------------------------------------------------
# GEOMETRY (canvas px).  Content lives inside x 114..1806 / y 114..966 — the
# tokens.yml padding ring and content-bottom band the pixel gate grades.
# ---------------------------------------------------------------------------
SHEET = (152, 152, 1616, 792)

APPROACHES = ["Traditional path", "Fast track", "Entrepreneurial",
              "Work-life balance", "Location independent", "Social impact"]
SHELF_X, SHELF_W, TILE_H = 1268, 456, 72
SHELF_TOPS = [322, 414, 506, 598, 690, 782]
FIELD_SLOT_X = 720
FIELD_SLOT_TOPS = [384, 476, 568]
COL_L, COL_R = 240, 1180
# Every tile owns ONE row for the rest of the video and only ever moves
# HORIZONTALLY after b28 — so no two marks can ever occupy the same box, at
# rest or mid-move. The re-sort is a full 940px crossing of the sheet.
PLOT = {           # tile -> (x at b28/b29, its permanent row)
    0: (COL_L, 420), 1: (COL_R, 330), 2: (COL_L, 600),
    3: (COL_R, 510), 4: (COL_R, 690), 5: (COL_L, 780),
}
ZONE_X = {0: COL_R, 2: COL_R,      # Prioritize (upper right)
          1: COL_L, 3: COL_L,      # Explore (upper left)
          5: COL_R,                # Enjoy or Side (lower right)
          4: COL_L}                # Park (lower left)
ZONE_BEAT = {"b36": [0, 2], "b37": [1, 3], "b38": [5], "b39": [4]}
# the three tiles that leave the shelf at b09 (pinned into the field)
PINNED = [0, 1, 3]
LEFTOVER = [2, 4, 5]
RISER_X = [740, 800, 860, 960, 1020, 1080]

LANE_X, LANE_W = 580, 650
LANE_TOPS = [745, 805, 865]
CHIP_LEFTS = [596, 700, 804, 908, 1012]
CHIP_W, CHIP_H = 80, 20
STAIR_H = [20, 28, 36, 44, 52]

HEADINGS = [
    ("hd03", "Open the Tool"),
    ("hd06", "Your Career Paths"),
    ("hd10", "The Profile Section"),
    ("hd14", "More Detail for Each Approach"),
    ("hd16", "Regenerating the Map"),
    ("hd19", "Your Summary"),
    ("hd22", "Your Generated Paths"),
    ("hd25", "Your Personalized Roadmap"),
    ("hd28", "Your Options Side by Side"),
    ("hd30", "Two Axes"),
    ("hd34", "Long-Term Value"),
    ("hd36", "Four Zones"),
    ("hd40", "What You Notice While You Score"),
    ("hd42", "The Quadrant Worksheet"),
    ("hd43", "Two Things at Once"),
    ("hd45", "The Same Criteria for Every Option"),
]


def px(**kw):
    return " ".join(f"{k.replace('_', '-')}: {v}px;" for k, v in kw.items())


# ---------------------------------------------------------------------------
# MARKUP
# ---------------------------------------------------------------------------
def markup():
    m = []
    ad = m.append

    # --- the board and the sheet ------------------------------------------
    ad(f'<div id="sheet" style="{px(left=SHEET[0], top=SHEET[1], width=SHEET[2], height=SHEET[3])}">'
       f'<div id="grid"></div></div>')
    ad('<div id="clipbar"></div>')
    for i, top in enumerate((250, 340, 430, 520, 610, 700, 790, 880)):
        ad(f'<div class="hole" style="{px(top=top)}"></div>')

    # --- the four fixed region rules --------------------------------------
    ad('<div id="ruleH" class="rule"></div>')
    ad('<div id="ruleV1" class="rule"></div>')
    ad('<div id="ruleV2" class="rule"></div>')
    ad('<div id="ruleLower" class="rule"></div>')
    ad('<div id="tintM" class="tint"></div><div id="tintF" class="tint"></div>'
       '<div id="tintS" class="tint"></div>')

    # --- header band -------------------------------------------------------
    ad('<h1 id="title" data-role="heading">Using the Career Map Tool</h1>')
    for hid, text in HEADINGS:
        ad(f'<div id="{hid}" class="hd" data-role="heading">{text}</div>')

    # --- the intake margin -------------------------------------------------
    ad('<div id="ctlBegin" class="ctlrow" data-role="list">'
       '<span class="ctl">Start</span><span class="ctl">Get started</span></div>')
    ad('<div id="profileBox"></div>')
    ad('<div id="profileLabel" class="reglabel">profile</div>')
    ad('<div id="profileLines" data-role="list">'
       '<div class="mline" id="ml1">your name</div>'
       '<div class="mline" id="ml2">your preferred industry</div>'
       '<div class="mline" id="ml3">your general background</div></div>')
    ad('<div id="slip"><span class="sliplabel">resume</span></div>')
    ad('<div id="slipFold"></div>')
    ad('<div id="tie"></div><div id="beginRule"></div><div id="genRule"></div>')
    for i in range(3):
        ad(f'<div class="tietick" id="tt{i}"></div>')

    # --- the control rail in the header band -------------------------------
    ad('<div id="ctlGen" class="ctlrow" data-role="list">'
       '<span class="ctl">generate</span><span class="ctl">update</span></div>')

    # --- the field: the section strip, the slots, the tiles ----------------
    ad('<div id="section">Map Your Career</div>')
    ad('<div id="sectionBracket"></div>')
    for i, top in enumerate(FIELD_SLOT_TOPS):
        ad(f'<div class="slot" id="slot{i}" style="{px(top=top)}"></div>')

    ad('<div id="shelf" data-role="list">')
    for i, name in enumerate(APPROACHES):
        ad(f'  <div class="tile" id="tile{i}" style="{px(top=SHELF_TOPS[i])}">'
           f'<span class="tilelabel">{name}</span>'
           f'<span class="pin"></span>'
           f'<span class="det det-a"></span><span class="det det-b"></span></div>')
    ad('</div>')

    # --- the regenerate confirmation --------------------------------------
    ad('<div id="panel"></div>')
    ad('<div id="warn">removes your old career approaches and jobs</div>')
    ad('<div id="confirm" data-role="compare">'
       '<span class="card" data-role="card">Regenerate</span>'
       '<span class="card" data-role="card">Cancel</span></div>')

    # --- the lower field: summary band, lanes, chips, stats ----------------
    ad('<div id="band"></div>')
    for i in range(8):
        ad(f'<div class="btick" id="bt{i}" style="{px(left=580 + i * 92)}"></div>')
    for L, top in enumerate(LANE_TOPS):
        ad(f'<div class="lane" id="lane{L}" style="{px(top=top)}"></div>')
        for c, left in enumerate(CHIP_LEFTS):
            ad(f'<div class="chip" id="chip{L}{c}" '
               f'style="{px(left=left, top=top - 10)}"></div>')
    ad('<div id="stats" data-role="list">'
       '<div class="stat" id="st0">the number of roles</div>'
       '<div class="stat" id="st1">the industry</div>'
       '<div class="stat" id="st2">the focus</div></div>')
    ad('<div id="laneBracket"></div><div id="lanePin"></div>')
    ad('<div id="overviewFrame"></div>')
    ad('<div id="ticks" data-role="list">'
       '<div class="tick" id="tk0">the time frame</div>'
       '<div class="tick" id="tk1">your preferred industry</div>'
       '<div class="tick" id="tk2">your five-year goal</div></div>')
    ad('<div id="stair"></div>')
    ad('<div id="timeBand"></div>')
    for i in range(3):
        ad(f'<div class="ttick" id="tq{i}"></div>')
    ad('<div id="showMore" class="ctlrow single"><span class="ctl">Show more</span></div>')

    # --- the axes, then the marks on them, then the labels ON TOP ----------
    for q, (left, top, w, h) in enumerate(((208, 316, 689, 360), (903, 316, 809, 360),
                                           (208, 682, 689, 258), (903, 682, 809, 258))):
        ad(f'<div class="quad" id="q{q}" style="{px(left=left, top=top, width=w, height=h)}"></div>')
    ad('<div id="fitBand"></div><div id="valBand"></div>')
    ad('<div id="axisH"></div><div id="axisV"></div><div id="fitEdge"></div>')
    ad('<div id="axisHTickL" class="endtick"></div><div id="axisHTickR" class="endtick"></div>')
    ad('<div id="axisVTickT" class="endtick v"></div><div id="axisVTickB" class="endtick v"></div>')
    for i, x in enumerate(RISER_X):
        ad(f'<div class="riser" id="rs{i}" style="{px(left=x)}"></div>')
    for i, x in enumerate(RISER_X):
        ad(f'<div class="dot" id="dt{i}" style="{px(left=x - 6)}"></div>')
    ad('<div id="span"></div><div id="spanL"></div><div id="spanR"></div>')
    ad('<div id="weakBar"></div>')
    ad('<div id="caret"></div><div id="cross"></div>')
    for i in range(3):
        ad(f'<div class="ray" id="ry{i}"></div>')
    ad('<div id="frameA"></div><div id="frameB"></div>')
    for i in range(6):
        ad(f'<div class="crit" id="cr{i}"></div>')
    ad('<div id="axisHLabel" class="axislabel">personal fit and energy</div>')
    ad('<div id="axisVLabel" class="axislabel">long-term value</div>')
    ad('<div id="vticks" data-role="list">'
       '<div class="vtick" id="vt0">skills</div>'
       '<div class="vtick" id="vt1">connections</div>'
       '<div class="vtick" id="vt2">credentials</div>'
       '<div class="vtick" id="vt3">options</div></div>')
    for zid, label, left, top in (
            ("znP", "Prioritize", 920, 340),
            ("znE", "Explore", 700, 340),
            ("znS", "Enjoy or Side", 920, 862),
            ("znK", "Park", 700, 862)):
        ad(f'<div id="{zid}" class="zone" style="{px(left=left, top=top)}">{label}</div>')
    return "\n      ".join(m)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def css():
    tile_css = "\n".join(
        f"      #tile{i} {{ left: {SHELF_X}px; }}" for i in range(6))
    return f"""
      @font-face {{ font-family: "Proxima Nova"; src: url("assets/fonts/proxima-nova-400.woff2") format("woff2"); font-weight: 400; font-style: normal; font-display: block; }}
      @font-face {{ font-family: "Proxima Nova"; src: url("assets/fonts/proxima-nova-700.woff2") format("woff2"); font-weight: 700; font-style: normal; font-display: block; }}
      @font-face {{ font-family: "Proxima Nova"; src: url("assets/fonts/proxima-nova-900.woff2") format("woff2"); font-weight: 900; font-style: normal; font-display: block; }}

      #root {{ position: absolute; inset: 0; width: 1920px; height: 1080px;
               font-family: "Proxima Nova", sans-serif; overflow: hidden; }}
      #root div, #root span, #root h1 {{ position: absolute; box-sizing: border-box; }}

      /* ---- the sheet itself ---- */
      #sheet {{ background: {CULTURED}; box-shadow: 0 0 0 2px rgba(204, 206, 223, 0.9); }}
      #grid {{ position: absolute; inset: 0;
        background-image:
          repeating-linear-gradient(to right, rgba(204, 206, 223, 0.55) 0 1px, rgba(246, 246, 249, 0) 1px 44px),
          repeating-linear-gradient(to bottom, rgba(204, 206, 223, 0.55) 0 1px, rgba(246, 246, 249, 0) 1px 44px); }}
      #clipbar {{ left: 810px; top: 132px; width: 300px; height: 40px;
        background: {MUTED}; border-radius: 6px; }}
      .hole {{ left: 176px; width: 16px; height: 16px; border-radius: 50%;
        background: {NAVY_DEEP}; opacity: 0.22; }}

      /* ---- the four fixed region rules ---- */
      .rule {{ background: {BORDER}; }}
      #ruleH {{ left: 208px; top: 300px; width: 1504px; height: 2px; }}
      #ruleV1 {{ left: 700px; top: 300px; width: 2px; height: 380px; }}
      #ruleV2 {{ left: 1256px; top: 300px; width: 2px; height: 580px; }}
      #ruleLower {{ left: 208px; top: 680px; width: 1048px; height: 2px; }}
      .tint {{ background: rgba(229, 239, 246, 0.5); }}
      #tintM {{ left: 208px; top: 316px; width: 480px; height: 364px; }}
      #tintF {{ left: 712px; top: 316px; width: 532px; height: 364px; }}
      #tintS {{ left: 1268px; top: 316px; width: 456px; height: 564px; }}

      /* ---- header band ---- */
      #title {{ left: 208px; top: 190px; width: 1490px; font-size: 78px;
        font-weight: 900; line-height: 1.08; color: {NAVY}; }}
      .hd {{ left: 208px; top: 196px; width: 1040px; font-size: 54px;
        font-weight: 900; line-height: 1.1; color: {NAVY}; }}

      /* ---- the intake margin ---- */
      .ctlrow {{ display: flex; gap: 16px; align-items: stretch; }}
      #root .ctl, #root .card {{ position: relative; }}
      #shelf {{ left: 0; top: 0; }}
      #ctlBegin {{ left: 216px; top: 318px; height: 52px; }}
      #ctlGen {{ left: 1290px; top: 200px; height: 52px; }}
      #showMore {{ left: 1268px; top: 866px; height: 52px; }}
      .ctl {{ position: relative; display: inline-flex; align-items: center;
        padding: 0 14px; height: 52px; font-size: 40px; font-weight: 700;
        line-height: 1.15; color: {NAVY}; background: {PAPER};
        border: 2px solid {INK}; border-radius: 6px; white-space: nowrap; }}
      #profileBox {{ left: 208px; top: 376px; width: 480px; height: 236px;
        border: 2px solid {BORDER}; border-radius: 6px; }}
      .reglabel {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.14em; color: {MUTED}; line-height: 1.2; }}
      #profileLabel {{ left: 224px; top: 386px; }}
      #profileLines {{ left: 224px; top: 428px; width: 452px; height: 190px; }}
      .mline {{ left: 0; width: 452px; height: 46px; font-size: 40px;
        font-weight: 400; line-height: 1.15; color: {INK};
        border-bottom: 2px solid {BORDER}; white-space: nowrap; }}
      #ml1 {{ top: 0; }} #ml2 {{ top: 54px; }} #ml3 {{ top: 108px; }}
      #slip {{ left: 216px; top: 624px; width: 300px; height: 52px;
        background: {CULTURED}; border: 2px solid {INK}; border-radius: 4px; }}
      .sliplabel {{ left: 14px; top: 2px; font-size: 40px; font-weight: 700;
        line-height: 1.15; color: {INK}; }}
      #slipFold {{ left: 484px; top: 624px; width: 32px; height: 32px;
        background: {BORDER}; }}
      #tie {{ left: 516px; top: 648px; width: 204px; height: 3px; background: {GOLD}; }}
      .tietick {{ left: 706px; width: 14px; height: 14px; background: {GOLD}; border-radius: 50%; }}
      #tt0 {{ top: 412px; }} #tt1 {{ top: 504px; }} #tt2 {{ top: 596px; }}

      /* ---- the field ---- */
      #section {{ left: 720px; top: 318px; width: 516px; height: 52px;
        padding-left: 14px; background: {FILL}; border-left: 10px solid {BLUE};
        font-size: 40px; font-weight: 700; line-height: 1.25; color: {NAVY}; }}
      #sectionBracket {{ left: 712px; top: 312px; width: 524px; height: 62px;
        border: 2px solid {BLUE}; border-radius: 6px; }}
      .slot {{ left: {FIELD_SLOT_X}px; width: {SHELF_W}px; height: {TILE_H}px;
        background: {FILL}; border: 2px dashed {MUTED}; border-radius: 8px; }}

      .tile {{ width: {SHELF_W}px; height: {TILE_H}px; background: {PAPER};
        border: 2px solid {INK}; border-radius: 8px; }}
{tile_css}
      .tilelabel {{ left: 24px; top: 10px; font-size: 40px; font-weight: 700;
        line-height: 1.15; color: {INK}; white-space: nowrap; }}
      .pin {{ left: 8px; top: 8px; width: 12px; height: 12px; border-radius: 50%;
        background: {GOLD}; opacity: 0; }}
      .det {{ left: 24px; height: 5px; background: {BORDER}; opacity: 0; }}
      .det-a {{ top: 56px; width: 300px; }}
      .det-b {{ top: 64px; width: 214px; }}

      /* ---- the regenerate confirmation ---- */
      #panel {{ left: 300px; top: 690px; width: 700px; height: 244px;
        background: {CULTURED}; border: 3px solid {NAVY}; border-radius: 8px; }}
      #warn {{ left: 324px; top: 716px; width: 652px; font-size: 40px;
        font-weight: 400; line-height: 1.2; color: {INK}; }}
      #confirm {{ left: 324px; top: 836px; width: 652px; height: 56px;
        display: flex; gap: 16px; }}
      .card {{ position: relative; display: inline-flex; align-items: center;
        justify-content: center; height: 56px; padding: 0 12px; font-size: 40px;
        font-weight: 700; line-height: 1.15; color: {NAVY}; background: {PAPER};
        border: 2px solid {NAVY}; border-radius: 6px; white-space: nowrap; }}

      /* ---- the lower field ---- */
      #band {{ left: {LANE_X}px; top: 690px; width: {LANE_W}px; height: 8px;
        background: {BLUE}; }}
      .btick {{ top: 712px; width: 3px; height: 10px; background: {BLUE}; }}
      .lane {{ left: {LANE_X}px; width: {LANE_W}px; height: 3px; background: {MUTED}; }}
      .chip {{ width: {CHIP_W}px; height: {CHIP_H}px; background: {CULTURED};
        border: 2px solid {INK}; border-radius: 3px; }}
      #stats {{ left: 216px; top: 722px; width: 350px; height: 170px; }}
      .stat {{ left: 0; width: 350px; height: 46px; font-size: 40px;
        font-weight: 400; line-height: 1.15; color: {INK}; white-space: nowrap; }}
      #st0 {{ top: 0; }} #st1 {{ top: 60px; }} #st2 {{ top: 120px; }}
      #laneBracket {{ left: 566px; top: 726px; width: 678px; height: 40px;
        border: 3px solid {GOLD}; border-radius: 4px; }}
      #lanePin {{ left: 548px; top: 738px; width: 16px; height: 16px;
        border-radius: 50%; background: {GOLD}; }}
      #overviewFrame {{ left: 560px; top: 684px; width: 684px; height: 256px;
        border: 2px solid {BLUE}; border-radius: 6px; }}
      #ticks {{ left: 216px; top: 890px; width: 1010px; height: 46px; }}
      .tick {{ height: 46px; font-size: 40px; font-weight: 400; line-height: 1.15;
        color: {INK}; white-space: nowrap; }}
      #tk0 {{ left: 0; top: 0; }} #tk1 {{ left: 264px; top: 0; }} #tk2 {{ left: 684px; top: 0; }}
      #stair {{ left: 596px; top: 700px; width: 496px; height: 3px; background: {GOLD}; }}

      /* ---- the axes and the zones ---- */
      #axisH {{ left: 208px; top: 676px; width: 1504px; height: 6px; background: {GOLD}; }}
      #axisV {{ left: 897px; top: 316px; width: 6px; height: 618px; background: {GOLD}; }}
      .axislabel {{ font-size: 26px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.14em; color: {NAVY}; line-height: 1.2; white-space: nowrap; }}
      #axisHLabel {{ left: 700px; top: 692px; }}
      #axisVLabel {{ left: 920px; top: 302px; }}
      .endtick {{ width: 22px; height: 6px; background: {GOLD}; }}
      .endtick.v {{ width: 6px; height: 22px; }}
      #axisHTickL {{ left: 208px; top: 660px; }}
      #axisHTickR {{ left: 1690px; top: 660px; }}
      #axisVTickT {{ left: 897px; top: 316px; }}
      #axisVTickB {{ left: 897px; top: 912px; }}
      #vticks {{ left: 936px; top: 430px; width: 240px; height: 248px; }}
      .vtick {{ left: 0; width: 240px; height: 44px; font-size: 40px;
        font-weight: 400; line-height: 1.1; color: {INK}; white-space: nowrap; }}
      #vt0 {{ top: 204px; }} #vt1 {{ top: 136px; }} #vt2 {{ top: 68px; }} #vt3 {{ top: 0; }}
      .riser {{ top: 684px; width: 8px; height: 96px; background: {BLUE}; }}
      .dot {{ top: 664px; width: 22px; height: 22px; border-radius: 50%; background: {GOLD}; }}
      #span {{ left: 728px; top: 788px; width: 364px; height: 6px; background: {BLUE}; }}
      #spanL {{ left: 728px; top: 768px; width: 6px; height: 26px; background: {BLUE}; }}
      #spanR {{ left: 1086px; top: 768px; width: 6px; height: 26px; background: {BLUE}; }}
      #fitEdge {{ left: 208px; top: 656px; width: 1504px; height: 16px;
        background: rgba(234, 171, 45, 0.55); }}
      #fitBand {{ left: 208px; top: 684px; width: 1504px; height: 62px;
        background: rgba(234, 171, 45, 0.16); }}
      #valBand {{ left: 871px; top: 316px; width: 52px; height: 618px;
        background: rgba(234, 171, 45, 0.16); }}
      #timeBand {{ left: 216px; top: 876px; width: 1010px; height: 5px; background: {MUTED}; }}
      .ttick {{ top: 858px; width: 4px; height: 22px; background: {MUTED}; }}
      #tq0 {{ left: 216px; }} #tq1 {{ left: 480px; }} #tq2 {{ left: 900px; }}
      #weakBar {{ left: 240px; top: 720px; width: 456px; height: 10px; background: {GOLD}; }}
      #beginRule {{ left: 216px; top: 380px; width: 400px; height: 8px; background: {GOLD}; }}
      #genRule {{ left: 720px; top: 662px; width: 456px; height: 8px; background: {GOLD}; }}
      .zone {{ font-size: 48px; font-weight: 900; line-height: 1.5; color: {NAVY};
        padding-bottom: 4px; border-bottom: 5px solid {GOLD}; white-space: nowrap; }}
      .quad {{ background: transparent; border: 3px dashed rgba(51, 147, 214, 0.45); }}
      #caret {{ left: 700px; top: 468px; width: 20px; height: 20px;
        border-left: 4px solid {GOLD}; border-top: 4px solid {GOLD}; }}
      #cross {{ left: 700px; top: 800px; width: 34px; height: 6px; background: {GOLD}; }}
      .ray {{ left: 742px; width: 120px; height: 5px; background: {GOLD}; }}
      #ry0 {{ top: 782px; }} #ry1 {{ top: 800px; }} #ry2 {{ top: 818px; }}
      #frameA {{ left: 200px; top: 312px; width: 1520px; height: 626px;
        border: 2px solid {BLUE}; border-radius: 6px; }}
      #frameB {{ left: 186px; top: 298px; width: 1548px; height: 654px;
        border: 2px solid {BORDER}; border-radius: 6px; }}
      .crit {{ width: 26px; height: 26px; background: {GOLD}; }}
"""


def crit_css():
    out = []
    for ti in range(6):
        left, top = ZONE_X[ti], PLOT[ti][1]
        out.append(f"      #cr{ti} {{ left: {left + SHELF_W - 30}px; top: {top + 14}px; }}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# TIMELINE
# ---------------------------------------------------------------------------
def timeline():
    js = []
    add = js.append

    def show(sel, t, dy=14, dur=0.45, stag=0.0):
        add(f'      arrive("{sel}", {t}, {dy}, {dur}, {stag});')

    def hide(sel, t, dur=0.35):
        add(f'      leave("{sel}", {t}, {dur});')

    def grow(sel, t, prop, val, dur=0.5):
        add(f'      tl.to("{sel}", {{ {prop}: {val}, duration: {dur}, ease: OUT }}, {t});')

    def move(ti, t, left, top, dur=0.7):
        dx = left - SHELF_X
        dy = top - SHELF_TOPS[ti]
        add(f'      tl.to("#tile{ti}", {{ x: {dx}, y: {dy}, duration: {dur}, '
            f'ease: "power3.inOut" }}, {t});')

    def swap(old_sel, new_sel, t, dy=-20):
        """Headings share one box, so the outgoing one is CUT, not faded."""
        add(f'      tl.set("{old_sel}", {{ autoAlpha: 0 }}, {t});')
        show(new_sel, round(t + 0.22, 3), dy)

    def draw(sel, t, axis="scaleX", origin="left center", dur=0.55):
        add(f'      tl.set("{sel}", {{ transformOrigin: "{origin}" }});')
        add(f'      tl.fromTo("{sel}", {{ {axis}: 0, autoAlpha: 0 }}, '
            f'{{ {axis}: 1, autoAlpha: 1, duration: {dur}, ease: OUT }}, {t});')

    # b01 — the sheet exists
    add('      // b01 — the sheet, its grid, its clip and its rail')
    show("#sheet", a1("b01"), 0, 0.7)
    show("#grid", a1("b01") + 0.15, 0, 0.8)
    show("#clipbar", a1("b01") + 0.1, -10, 0.5)
    show(".hole", a1("b01") + 0.3, 0, 0.4, 0.05)
    show("#title", a2("b01", 0.35), 22, 0.6)
    draw("#ruleH", a2("b01", 0.75))

    # b02 — the regions are ruled
    add('      // b02 — the sheet is ruled into its four fixed regions')
    draw("#ruleV1", a1("b02"), "scaleY", "center top")
    draw("#ruleV2", a1("b02") + 0.12, "scaleY", "center top")
    draw("#ruleLower", a2("b02"))
    show(".tint", a2("b02") + 0.2, 0, 0.6, 0.08)

    # b03 — open the tool
    add('      // b03 — the header band takes the step')
    swap("#title", "#hd03", a1("b03"))
    show("#profileBox", a2("b03"), 0, 0.5)

    # b04 — the landing section
    add('      // b04 — the section titled Map Your Career')
    show("#section", a1("b04"), 16)
    show("#sectionBracket", a2("b04"), 0, 0.5)

    # b05 — the two button words
    add('      // b05 — the control block the landing screen offers')
    show("#ctlBegin", a1("b05"), 14)
    add(f'      tl.fromTo("#ctlBegin .ctl:nth-child(2)", {{ borderColor: "{BORDER}" }}, '
        f'{{ borderColor: "{GOLD}", duration: 0.4, ease: OUT }}, {a2("b05")});')
    draw("#beginRule", a2("b05", 0.7))

    # b06 — the shelf appears
    add('      // b06 — the shelf, six empty tiles')
    swap("#hd03", "#hd06", a1("b06"))
    show(".tile", a2("b06"), 12, 0.4, 0.07)

    # b07 — the slots and the pins
    add('      // b07 — where a selection lands, and the pins on three tiles')
    show(".slot", a1("b07"), 10, 0.45, 0.08)
    for i in PINNED:
        show(f"#tile{i} .pin", a2("b07") + 0.12 * PINNED.index(i), 0, 0.3)

    # b08 — the six names letter in
    add('      // b08 — the six approach names, lettered in two waves')
    for i in range(3):
        show(f"#tile{i} .tilelabel", cue("b08", 0.30) + 0.14 * i, 0, 0.35)
    for i in range(3, 6):
        show(f"#tile{i} .tilelabel", cue("b08", 0.66) + 0.14 * (i - 3), 0, 0.35)

    # b09 — three tiles leave the shelf
    add('      // b09 — three tiles lift off the shelf into the field')
    for n, i in enumerate(PINNED):
        move(i, a1("b09") + 0.1 * n, FIELD_SLOT_X, FIELD_SLOT_TOPS[n])
    for n, i in enumerate(PINNED):
        add(f'      tl.to("#tile{i}", {{ borderColor: "{GOLD}", duration: 0.4, '
            f'ease: OUT }}, {a2("b09") + 0.1 * n});')

    # b10 — the profile section
    add('      // b10 — the profile section opens in the margin')
    swap("#hd06", "#hd10", a1("b10"))
    show("#profileLabel", a2("b10"), 8, 0.4)

    # b11 — three profile lines
    add('      // b11 — the three things it asks for')
    show("#ml1", a1("b11"), 10, 0.4)
    show("#ml2", a2("b11, 0.5"[:3]) if False else a2("b11", 0.5), 10, 0.4)
    show("#ml3", a2("b11", 0.78), 10, 0.4)

    # b12 — the resume slip
    add('      // b12 — the resume slip clips over the margin')
    show("#slip", a1("b12"), -14)
    show("#slipFold", a2("b12"), 0, 0.35)

    # b13 — the tie to the tiles
    add('      // b13 — the slip lines the map up with the tiles')
    draw("#tie", a1("b13"))
    add(f'      tl.to("#slip", {{ borderColor: "{GOLD}", duration: 0.4, ease: OUT }}, {a1("b13")});')
    for n, i in enumerate(PINNED):
        add(f'      tl.to("#tile{i}", {{ borderColor: "{GOLD}", borderWidth: 5, '
            f'duration: 0.45, ease: OUT }}, {a2("b13") + 0.1 * n});')
    for i in range(3):
        show(f"#tt{i}", a2("b13") + 0.12 * i, 0, 0.3)

    # b14 — the tiles thicken
    add('      // b14 — each pinned tile gains interior detail')
    swap("#hd10", "#hd14", a1("b14"))
    for n, i in enumerate(PINNED):
        show(f"#tile{i} .det-a", a2("b14", 0.5) + 0.1 * n, 0, 0.3)
        show(f"#tile{i} .det-b", a2("b14", 0.78) + 0.1 * n, 0, 0.3)

    # b15 — the generate control
    add('      // b15 — the button that generates or updates the map')
    show("#ctlGen", a1("b15"), 12)
    add(f'      tl.fromTo("#ctlGen .ctl:nth-child(1)", {{ borderColor: "{BORDER}" }}, '
        f'{{ borderColor: "{GOLD}", duration: 0.4, ease: OUT }}, {a2("b15")});')
    draw("#genRule", a2("b15", 0.72))

    # b16 — the confirmation
    add('      // b16 — the confirmation covers the field')
    swap("#hd14", "#hd16", a1("b16"))
    show("#panel", a2("b16", 0.5), 18, 0.5)

    # b17 — the warning, and the subtraction
    add('      // b17 — the honest subtraction: the pinned marks go to outline')
    show("#warn", a1("b17"), 12)
    for n, i in enumerate(PINNED):
        add(f'      tl.to("#tile{i}", {{ autoAlpha: 0.3, duration: 0.45, ease: OUT }}, '
            f'{a2("b17") + 0.08 * n});')

    # b18 — the two controls, then the panel goes
    add('      // b18 — Regenerate or Cancel, then the sheet comes back')
    show("#confirm", a1("b18"), 12)
    hide("#panel", a2("b18", 0.72), 0.4)
    hide("#warn", a2("b18", 0.72), 0.4)
    hide("#confirm", a2("b18", 0.72), 0.4)
    for i in PINNED:
        add(f'      tl.to("#tile{i}", {{ autoAlpha: 1, duration: 0.45, ease: OUT }}, '
            f'{a2("b18", 0.78)});')

    # b19 — the summary band
    add('      // b19 — the summary, a ruled band with plain ticks')
    swap("#hd16", "#hd19", a1("b19"))
    draw("#band", a2("b19", 0.5))
    for i in range(8):
        show(f"#bt{i}", a2("b19", 0.75) + 0.04 * i, 0, 0.25)

    # b20 — the first lane and its jobs
    add('      // b20 — the first path lane, with its job chips')
    draw("#lane0", a1("b20"))
    for c in range(len(CHIP_LEFTS)):
        show(f"#chip0{c}", a2("b20", 0.5) + 0.09 * c, 8, 0.3)

    # b21 — show more
    add('      // b21 — Show more expands one job')
    show("#showMore", a1("b21"), 12)
    grow("#chip04", a2("b21", 0.6), "height", 44)
    add(f'      tl.to("#chip04", {{ y: -24, duration: 0.5, ease: OUT }}, {a2("b21", 0.6)});')

    # b22 — the rest of the lanes
    add('      // b22 — the lower field rules into lanes')
    swap("#hd19", "#hd22", a1("b22"))
    draw("#lane1", a1("b22") + 0.15)
    for c in range(len(CHIP_LEFTS)):
        show(f"#chip1{c}", a1("b22") + 0.45 + 0.08 * c, 8, 0.3)
    draw("#lane2", a2("b22", 0.6))
    for c in range(len(CHIP_LEFTS)):
        show(f"#chip2{c}", a2("b22", 0.6) + 0.3 + 0.08 * c, 8, 0.3)

    # b23 — the quick stats
    add('      // b23 — the quick stats at each lane head')
    show("#st0", a1("b23"), 10, 0.4)
    show("#st1", a2("b23", 0.5), 10, 0.4)
    show("#st2", a2("b23", 0.8), 10, 0.4)

    # b24 — the selected path
    add('      // b24 — one lane is bracketed as the selected path')
    show("#laneBracket", a1("b24"), 0, 0.45)
    add(f'      tl.to("#lane0", {{ backgroundColor: "{GOLD}", height: 6, duration: 0.4, '
        f'ease: OUT }}, {a1("b24")});')
    for c in range(len(CHIP_LEFTS)):
        add(f'      tl.to("#chip0{c}", {{ backgroundColor: "{GOLD}", duration: 0.35, '
            f'ease: OUT }}, {a2("b24") + 0.07 * c});')
    show("#lanePin", a2("b24"), 0, 0.3)

    # b25 — the overview
    add('      // b25 — the overview frames the whole roadmap')
    swap("#hd22", "#hd25", a1("b25"))
    show("#overviewFrame", a2("b25", 0.5), 0, 0.5)

    # b26 — the three things to check
    add('      // b26 — the three things to check, ticked below the lanes')
    draw("#timeBand", a1("b26"))
    for i in range(3):
        show(f"#tq{i}", a1("b26") + 0.1 * i, 0, 0.3)
    show("#tk0", a1("b26"), 10, 0.4)
    show("#tk1", a2("b26", 0.52), 10, 0.4)
    show("#tk2", a2("b26", 0.82), 10, 0.4)

    # b27 — the staircase
    add('      // b27 — responsibilities grow: the selected jobs step upward')
    for c in range(len(CHIP_LEFTS)):
        add(f'      tl.to("#chip0{c}", {{ height: {STAIR_H[c]}, y: {-(STAIR_H[c] - CHIP_H)}, '
            f'duration: 0.5, ease: OUT }}, {a1("b27") + 0.09 * c});')
    draw("#stair", a2("b27", 0.6))

    # b28 — the shelf empties
    add('      // b28 — the form clears and the last three tiles come down')
    swap("#hd25", "#hd28", a1("b28"))
    for sel in ("#ctlBegin", "#profileBox", "#profileLabel", "#profileLines",
                "#slip", "#slipFold", "#tie", ".tietick", "#section",
                "#sectionBracket", "#ctlGen", ".slot", "#showMore", "#genRule",
                "#beginRule",
                "#band", ".btick", "#stats", "#ticks", "#laneBracket",
                "#lanePin", "#overviewFrame", "#stair", "#timeBand", ".ttick"):
        hide(sel, a1("b28") + 0.05, 0.4)
    for sel in (".lane", ".chip"):
        add(f'      tl.to("{sel}", {{ autoAlpha: 0.12, duration: 0.5, ease: OUT }}, '
            f'{a1("b28") + 0.05});')
    for n, i in enumerate(LEFTOVER):
        move(i, a2("b28", 0.55) + 0.12 * n, PLOT[i][0], PLOT[i][1])

    # b29 — six options, side by side
    add('      // b29 — the form rules ghost; six options line up side by side')
    for sel in ("#ruleV1", "#ruleV2", "#ruleLower", "#tintM", "#tintF", "#tintS"):
        add(f'      tl.to("{sel}", {{ autoAlpha: 0.14, duration: 0.5, ease: OUT }}, {a1("b29")});')
    for n, i in enumerate(PINNED):
        move(i, a2("b29", 0.5) + 0.12 * n, PLOT[i][0], PLOT[i][1])

    # b30 — the payoff: two axes
    add('      // b30 — THE PAYOFF: two heavy strokes rule across the marks')
    swap("#hd28", "#hd30", a1("b30"))
    draw("#axisH", a1("b30") + 0.2, "scaleX", "left center", 0.7)
    draw("#axisV", a2("b30", 0.62), "scaleY", "center bottom", 0.7)

    # b31 — the horizontal axis is named
    add('      // b31 — the horizontal axis is named')
    draw("#fitEdge", a1("b31"), "scaleX", "left center", 0.6)
    show("#axisHLabel", a2("b31", 0.55), 10, 0.4)
    show("#axisHTickL", a2("b31", 0.8), 0, 0.3)
    show("#axisHTickR", a2("b31", 0.8) + 0.1, 0, 0.3)

    # b32 — every option is scored against the fit axis
    add('      // b32 — a riser for every option, scored against the fit axis')
    draw("#fitBand", a1("b32"), "scaleX", "left center", 0.6)
    for i in range(3):
        draw(f"#rs{i}", a1("b32") + 0.35 + 0.1 * i, "scaleY", "center top", 0.4)
    for i in range(3, 6):
        draw(f"#rs{i}", a2("b32", 0.6) + 0.1 * (i - 3), "scaleY", "center top", 0.4)

    # b33 — the feet become marks
    add('      // b33 — the drop feet land as marks on the axis')
    add(f'      tl.to("#fitBand", {{ backgroundColor: "rgba(234, 171, 45, 0.36)", '
        f'duration: 0.5, ease: OUT }}, {a1("b33")});')
    for i in range(3):
        show(f"#dt{i}", a1("b33") + 0.08 * i, 0, 0.3)
    for i in range(3, 6):
        show(f"#dt{i}", a2("b33", 0.55) + 0.08 * (i - 3), 0, 0.3)
    draw("#span", a3("b33", 0.8))
    show("#spanL", a3("b33", 0.86), 0, 0.3)
    show("#spanR", a3("b33", 0.86), 0, 0.3)

    # b34 — the vertical axis is named
    add('      // b34 — the vertical axis is named')
    swap("#hd30", "#hd34", a1("b34"))
    show("#axisVLabel", a2("b34", 0.5), 10, 0.4)
    show("#axisVTickT", a2("b34", 0.8), 0, 0.3)
    show("#axisVTickB", a2("b34", 0.86), 0, 0.3)

    # b35 — what the vertical axis measures
    add('      // b35 — what long-term value is made of')
    draw("#valBand", a1("b35"), "scaleY", "center bottom", 0.6)
    show("#vt0", a1("b35"), 10, 0.35)
    show("#vt1", a1("b35") + 0.5, 10, 0.35)
    show("#vt2", a2("b35", 0.62), 10, 0.35)
    show("#vt3", a2("b35", 0.84), 10, 0.35)

    # b36 — four zones, and the first one
    add('      // b36 — four zones, and the first re-placement')
    swap("#hd34", "#hd36", a1("b36"))
    show(".quad", a1("b36") + 0.2, 0, 0.5, 0.06)
    show("#znP", a2("b36", 0.62), 12, 0.4)
    for sel in ("#rs0", "#rs1", "#rs2", "#rs3", "#rs4", "#rs5",
                "#fitBand", "#valBand", "#span", "#spanL", "#spanR"):
        hide(sel, a1("b36"), 0.4)
    for n, i in enumerate(ZONE_BEAT["b36"]):
        move(i, a2("b36", 0.68) + 0.12 * n, ZONE_X[i], PLOT[i][1])

    # b37 — Explore
    add('      // b37 — Explore')
    show("#znE", a1("b37"), 12, 0.4)
    for n, i in enumerate(ZONE_BEAT["b37"]):
        move(i, a2("b37", 0.55) + 0.12 * n, ZONE_X[i], PLOT[i][1])

    # b38 — Enjoy or Side
    add('      // b38 — Enjoy or Side')
    show("#znS", a1("b38"), 12, 0.4)
    for i in ZONE_BEAT["b38"]:
        move(i, a2("b38", 0.55), ZONE_X[i], PLOT[i][1])

    # b39 — Park
    add('      // b39 — Park, and the field is fully sorted')
    show("#znK", a1("b39"), 12, 0.4)
    for n, i in enumerate(ZONE_BEAT["b39"]):
        move(i, a2("b39", 0.5) + 0.12 * n, ZONE_X[i], PLOT[i][1])

    # b40 — what you notice
    add('      // b40 — the noticing, not the score')
    swap("#hd36", "#hd40", a1("b40"))
    show("#caret", a2("b40", 0.6), 0, 0.35)

    # b41 — the safe option reads weak
    add('      // b41 — one plotted option reads weak on what mattered')
    for i in (0, 1, 2, 3, 5):
        add(f'      tl.to("#tile{i}", {{ autoAlpha: 0.42, duration: 0.5, ease: OUT }}, '
            f'{a1("b41")});')
    show("#weakBar", a1("b41") + 0.2, 0, 0.4)
    show("#cross", a2("b41", 0.5), 0, 0.35)
    for i in range(3):
        draw(f"#ry{i}", a2("b41", 0.6) + 0.1 * i, "scaleX", "left center", 0.35)

    # b42 — the worksheet
    add('      // b42 — the worksheet this lesson hands you')
    swap("#hd40", "#hd42", a1("b42"))
    for i in (0, 1, 2, 3, 5):
        add(f'      tl.to("#tile{i}", {{ autoAlpha: 1, duration: 0.5, ease: OUT }}, '
            f'{a1("b42") + 0.2});')
    show("#frameA", a2("b42", 0.62), 0, 0.5)

    # b43 — two things at once
    add('      // b43 — two things at once')
    swap("#hd42", "#hd43", a1("b43"))
    show("#frameB", a2("b43", 0.6), 0, 0.45)

    # b44 — the frame widens
    add('      // b44 — the frame widens across every zone')
    add(f'      tl.to("#frameA", {{ borderColor: "{GOLD}", duration: 0.5, ease: OUT }}, {a1("b44")});')
    for i in range(3):
        show(f"#cr{i}", a2("b44", 0.55) + 0.1 * i, 0, 0.3)

    # b45 — the same criteria on every option
    add('      // b45 — the same criteria, marked on every option')
    swap("#hd43", "#hd45", a1("b45"))
    for i in range(3, 6):
        show(f"#cr{i}", a2("b45", 0.5) + 0.1 * (i - 3), 0, 0.3)
    add(f'      tl.to(".zone", {{ scale: 1.0, autoAlpha: 1, duration: 0.4, ease: OUT }}, {a2("b45", 0.8)});')

    return "\n".join(js)


HIDDEN = """
      /* Everything that ARRIVES starts hidden; the timeline is the only thing
         that reveals it, so a seek to any frame is deterministic. */
      #title, .hd, #ruleH, #ruleV1, #ruleV2, #ruleLower, .tint, #sheet, #grid,
      #clipbar, .hole, #ctlBegin, #ctlGen, #showMore, #profileBox, #profileLabel,
      #ml1, #ml2, #ml3, #slip, #slipFold, #tie, .tietick, #section,
      #sectionBracket, .slot, .tile, #panel, #warn, #confirm, #band, .btick,
      .lane, .chip, .stat, #laneBracket, #lanePin, #overviewFrame, .tick,
      #stair, #axisH, #axisV, .axislabel, .endtick, .vtick, .riser, .dot, #span,
      #spanL, #spanR, #fitEdge, #fitBand, #valBand, #timeBand, .ttick, #weakBar,
      #beginRule, #genRule,
      .zone, .quad, #caret, #cross, .ray, #frameA, #frameB, .crit {
        opacity: 0;
        visibility: hidden;
      }
"""

SUB = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
  </head>
  <body>
    <template>
      <style>{css}{hidden}{crit}
      </style>

      <div id="root" data-composition-id="sheet" data-width="1920" data-height="1080">
      {markup}
      </div>

      <script>
        (function () {{
          window.__timelines = window.__timelines || {{}};
          const tl = gsap.timeline({{ paused: true }});
          const OUT = "power3.out";

          // One entrance shape for every mark: it arrives, then it holds.
          const arrive = function (sel, t, dy, dur, stag) {{
            tl.fromTo(sel, {{ autoAlpha: 0, y: dy || 0 }},
              {{ autoAlpha: 1, y: 0, duration: dur || 0.45, ease: OUT,
                 stagger: stag || 0 }}, t);
          }};
          const leave = function (sel, t, dur) {{
            tl.to(sel, {{ autoAlpha: 0, duration: dur || 0.35, ease: "power2.in" }}, t);
          }};

{timeline}

          window.__timelines["sheet"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""

HOST = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Proxima Nova"; src: url("assets/fonts/proxima-nova-400.woff2") format("woff2"); font-weight: 400; font-style: normal; font-display: block; }}
      @font-face {{ font-family: "Proxima Nova"; src: url("assets/fonts/proxima-nova-700.woff2") format("woff2"); font-weight: 700; font-style: normal; font-display: block; }}
      @font-face {{ font-family: "Proxima Nova"; src: url("assets/fonts/proxima-nova-900.woff2") format("woff2"); font-weight: 900; font-style: normal; font-display: block; }}

      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: {navy_deep}; }}
      body {{ font-family: "Proxima Nova", sans-serif; -webkit-font-smoothing: antialiased; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}

      /* Full-bleed fill lives on a CHILD, never on the composition root. */
      #bg {{ position: absolute; inset: 0; background: {navy_deep}; }}
      #bg-glow {{ position: absolute; left: 960px; top: 560px; width: 1900px;
        height: 1200px; margin: -600px 0 0 -950px;
        background: radial-gradient(ellipse at center,
          rgba(13, 36, 55, 0.95) 0%, rgba(10, 30, 47, 0.65) 46%,
          rgba(10, 30, 47, 0) 76%); will-change: transform; }}
      #bg-vignette {{ position: absolute; inset: 0;
        background: radial-gradient(ellipse at 50% 50%, rgba(10, 30, 47, 0) 54%,
          rgba(10, 30, 47, 0.72) 100%); }}

      /* Persistent program banner, inside the tokens.yml chrome-regions box. */
      #chrome {{ position: absolute; left: 130px; top: 58px; display: flex;
        align-items: center; gap: 18px; opacity: 0; }}
      #chrome-mark {{ display: block; width: 10px; height: 28px; background: {gold}; }}
      #chrome-text {{ font-size: 26px; font-weight: 700; letter-spacing: 0.16em;
        text-transform: uppercase; color: rgba(255, 255, 255, 0.7); line-height: 1.1; }}

      #root > div[data-composition-src] {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
      <div id="bg">
        <div id="bg-glow"></div>
        <div id="bg-vignette"></div>
      </div>

      <div id="chrome">
        <span id="chrome-mark"></span>
        <span id="chrome-text">Early Career Boost</span>
      </div>

      <!-- ONE carrying object for the whole runtime: the worksheet sheet.
           b01 -> b45, clipped to the board, only ever marked and re-sorted. -->
      <div id="el-sheet" data-composition-id="sheet" data-composition-src="compositions/sheet.html" data-start="0" data-duration="{total}" data-track-index="1" data-width="1920" data-height="1080"></div>

      <!-- Narration — HeyGen starfish, Oxana (tokens.yml voice.voice_id).
           One clip per beat at GLOBAL time; every number is timing.json's,
           computed by make_timing.py from the real wavs. -->
{audio}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});

      // The banner settles once, then never moves again.
      tl.fromTo("#chrome", {{ opacity: 0, x: -20 }},
        {{ opacity: 1, x: 0, duration: 0.7, ease: "power3.out" }}, 0.25);

      // One ambient breath, on the background GLOW only — never on content.
      tl.fromTo("#bg-glow", {{ scale: 1 }},
        {{ scale: 1.045, duration: 8, ease: "sine.inOut", yoyo: true, repeat: {legs} }}, /* motion-allow: background depth-drift on a non-content layer; design.md sanctions ambient breath on the background glow alone */
        0);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def main():
    audio = "\n".join(
        f'      <audio id="vo-{r["id"]}" src="assets/voice/{r["id"]}.wav" '
        f'data-start="{r["audio_start"]}" data-duration="{r["audio_dur"]}" '
        f'data-track-index="10" data-volume="1"></audio>'
        for r in T["rows"])
    legs = max(2, int(TOTAL / 8.0))
    (WS / "index.html").write_text(
        HOST.format(total=TOTAL, audio=audio, navy_deep=NAVY_DEEP, gold=GOLD,
                    legs=legs))
    (WS / "compositions").mkdir(exist_ok=True)
    (WS / "compositions" / "sheet.html").write_text(
        SUB.format(css=css(), hidden=HIDDEN, crit=crit_css(),
                   markup=markup(), timeline=timeline()))
    print(f"index.html + compositions/sheet.html written — {TOTAL}s, "
          f"{len(ORDER)} beats")


if __name__ == "__main__":
    main()
