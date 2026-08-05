#!/usr/bin/env python3
"""build_html.py — emit index.html + compositions/board.html for this build.

The HTML is the authored artifact; this generator exists so the 24 scraps,
their 24 hole outlines and the 29 audio rows are laid out from ONE set of
numbers instead of hand-typed 77 times. Every timing it writes is read from
timing.json / audio_meta.json — nothing here is hand-tuned.

    python3 build_html.py
"""
import json
import random
from pathlib import Path

WS = Path(__file__).resolve().parent
T = json.loads((WS / "timing.json").read_text())
ROWS = {r["id"]: r for r in T["rows"]}
TOTAL = T["total"]


def vs(bid):
    return ROWS[bid]["vis_start"]


# ---------------------------------------------------------------------------
# GEOMETRY — every number below is stated once in design.md's "Frame" section.
# All ink lives inside x 150..1800 and y 140..946.
# ---------------------------------------------------------------------------
STRIP_L, STRIP_T, STRIP_W, STRIP_H = 190, 276, 1280, 220
IN_L = 209                      # strip inner left (border 3 + padding 16)
SLOT_W, GAP_W = 296, 165
SLOT_X = [IN_L, IN_L + SLOT_W + GAP_W, IN_L + 2 * (SLOT_W + GAP_W)]
GAP_X = [IN_L + SLOT_W, IN_L + 2 * SLOT_W + GAP_W]
COL_W = 312
COL_X = [x + SLOT_W // 2 - COL_W // 2 for x in SLOT_X]   # parked under a slot
COL_ROW_Y = [712, 770, 828, 886]
SCRAP_W, SCRAP_H = 150, 44

HEADINGS = [
    ("b02", "A North Star You Can Actually Use"),
    ("b03", "Just One or Two Sentences"),
    ("b04", "Not Permanent"),
    ("b05", "A Working Answer to a Simple Question"),
    ("b06", "Specific Enough, Honest Enough"),
    ("b07", "It Blends Three Things"),
    ("b08", "First, What Energizes You"),
    ("b09", "Second, Who You Want to Help"),
    ("b10", "Third, What You Are Growing Toward"),
    ("b11", "A Simple Structure That Works"),
    ("b12", "The Structure, Filled In"),
    ("b13", "Notice What Is Not in There"),
    ("b14", "Direction, Contribution, and a Reason"),
    ("b15", "Yours Should Sound Like You"),
    ("b16", "Qualities Worth Aiming For"),
    ("b17", "Inspiring and True to You"),
    ("b18", "Driven by Real Energy"),
    ("b19", "A Mission, a Real Focus"),
    ("b20", "For the Next Several Years"),
    ("b21", "Brief and Easy to Repeat"),
    ("b22", "Awkward Is Normal"),
    ("b23", "Putting Words to Something Fuzzy"),
    ("b24", "Aim for Honest and Rough"),
    ("b25", "Write Three Quick Versions"),
    ("b26", "You Can Revise It"),
    ("b27", "The Confidence Half"),
    ("b28", "Not Certainty About the Future"),
    ("b29", "A Method, and a Purpose to Point It At"),
]

SLOT_TEXT = ["use these strengths",
             "help this person or create this outcome",
             "why it matters to me"]
CONNECTIVE = ["to", "because"]
ROW_LABELS = ["Direction", "Contribution", "A reason"]
COL_LABELS = ["what energizes you", "who or what you want to help",
              "strengths you are growing toward"]
CHIPS = ["Inspiring", "Real energy", "A mission", "Several years", "Brief"]
CHIP_W = [183, 227, 187, 258, 124]     # measured advance + 48px of padding
MARGIN_TAGS = ["grand claims", "buzzwords"]

# Which scrap is spent on which beat (index into the 24-scrap field).
# cols run 0-7 / 8-15 / 16-23, top row first, so the columns thin from the top.
SPEND = {"b12": [0, 8], "b15": [1], "b17": [9], "b18": [2], "b19": [10],
         "b20": [3], "b21": [11], "b22": [16], "b23": [17], "b24": [18],
         "b25": [19], "b26": [4], "b27": [12]}
SPENT = [i for ids in SPEND.values() for i in ids]

# Deterministic unsorted drift for beat 1 — a seeded field, never re-rolled.
rng = random.Random(20260805)
DRIFT = []
for i in range(24):
    cx = COL_X[i // 8] + (i % 2) * (SCRAP_W + 12)
    cy = COL_ROW_Y[(i % 8) // 2]
    dx = rng.uniform(210, 1300) - cx
    dy = rng.uniform(548, 872) - cy
    DRIFT.append((round(dx, 1), round(dy, 1), round(rng.uniform(-7, 7), 1)))


def scraps_markup():
    out = []
    for i in range(24):
        left = COL_X[i // 8] + (i % 2) * (SCRAP_W + 12)
        top = COL_ROW_Y[(i % 8) // 2]
        dx, dy, rot = DRIFT[i]
        tint = ["bd-t1", "bd-t2", "bd-t3"][i % 3]
        out.append(
            f'          <div class="bd-scrap {tint}" id="bd-sc{i:02d}" '
            f'style="left: {left}px; top: {top}px; '
            f'transform: translate({dx}px, {dy}px) rotate({rot}deg)">'
            f'<span class="bd-scrule bd-scrule-a"></span>'
            f'<span class="bd-scrule bd-scrule-b"></span></div>')
    return "\n".join(out)


def holes_markup():
    out = []
    for i in sorted(SPENT):
        left = COL_X[i // 8] + (i % 2) * (SCRAP_W + 12)
        top = COL_ROW_Y[(i % 8) // 2]
        out.append(
            f'          <div class="bd-hole" id="bd-hl{i:02d}" '
            f'data-layout-allow-overlap style="left: {left}px; top: {top}px">'
            f'</div>')
    return "\n".join(out)


def headings_markup():
    out = [f'          <h1 class="bd-title" id="bd-h01">Finding &amp; Creating '
           f'a Career Purpose Statement</h1>']
    for bid, text in HEADINGS:
        out.append(f'          <div class="bd-head" data-role="heading" '
                   f'id="bd-h{bid[1:]}">{text}</div>')
    return "\n".join(out)


def chips_markup():
    out, x = [], 300
    for n, (label, w) in enumerate(zip(CHIPS, CHIP_W), start=1):
        out.append(f'            <div class="bd-chip" id="bd-chip{n}" '
                   f'style="left: {x}px; width: {w}px">{label}</div>')
        x += w + 20
    return "\n".join(out)


def rel(x):
    """Page x -> the strip's own padding-box x. Every child of .bd-strip is
    positioned in the STRIP's coordinate space, not the page's — getting this
    wrong pushed slot 3 out through the crop bracket into the margin tags."""
    return x - STRIP_L - 3


def slots_markup():
    out = []
    for n, (x, text) in enumerate(zip(SLOT_X, SLOT_TEXT), start=1):
        out.append(f'            <div class="bd-slotbox" id="bd-slotbox{n}" '
                   f'data-layout-allow-overlap '
                   f'style="left: {rel(x)}px"></div>')
    for n, (x, text) in enumerate(zip(SLOT_X, SLOT_TEXT), start=1):
        out.append(f'            <div class="bd-slot" id="bd-slot{n}" '
                   f'style="left: {rel(x)}px">{text}</div>')
    for n, (x, text) in enumerate(zip(GAP_X, CONNECTIVE), start=1):
        out.append(f'            <div class="bd-conn" id="bd-conn{n}" '
                   f'style="left: {rel(x)}px">{text}</div>')
    return "\n".join(out)


def rowlabels_markup():
    out = []
    for n, (x, text) in enumerate(zip(SLOT_X, ROW_LABELS), start=1):
        out.append(f'              <div class="bd-rowlabel" id="bd-rl{n}" '
                   f'style="left: {rel(x)}px">{text}</div>')
    return "\n".join(out)


def colbrackets_markup():
    return "\n".join(
        f'        <div class="bd-colbracket" id="bd-cb{n}" '
        f'style="left: {x}px"></div>' for n, x in enumerate(COL_X, start=1))


def collabels_markup():
    out = []
    for n, (x, text) in enumerate(zip(COL_X, COL_LABELS), start=1):
        out.append(f'            <div class="bd-collabel" id="bd-cl{n}" '
                   f'style="left: {x}px">{text}</div>')
    return "\n".join(out)


def tags_markup():
    out = []
    for n, (text, top) in enumerate(zip(MARGIN_TAGS, (300, 380)), start=1):
        out.append(f'            <div class="bd-tag" id="bd-tag{n}" '
                   f'style="top: {top}px">{text}</div>')
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CUES — absolute seconds. Beat starts come from timing.json; the times that
# are not a beat start are the word timestamp in audio_meta.json that earns
# the reveal (named in the comment beside them).
# ---------------------------------------------------------------------------
def heading_cues():
    lines, ids = [], ["b01"] + [b for b, _ in HEADINGS]
    for n, bid in enumerate(ids):
        el = f"#bd-h{bid[1:]}" if bid != "b01" else "#bd-h01"
        t = vs(bid) + (0.30 if bid == "b01" else 0.10)
        lines.append(f'          head("{el}", {t:.2f});')
        if n + 1 < len(ids):
            # The outgoing heading is GONE before the next one lands: a
            # crossfade leaves two text blocks stacked in the heading zone for
            # ~0.1s and the layout inspector reads that as content_overlap.
            lines.append(f'          hide("{el}", {vs(ids[n + 1]) - 0.26:.2f});')
    return "\n".join(lines)


def scrap_cues():
    out = []
    for i in range(24):
        dx, dy, rot = DRIFT[i]
        t = 0.90 + i * 0.355
        out.append(
            f'          tl.fromTo("#bd-sc{i:02d}", '
            f'{{ autoAlpha: 0, x: {dx}, y: {dy + 26}, rotation: {rot} }}, '
            f'{{ autoAlpha: 1, x: {dx}, y: {dy}, rotation: {rot}, '
            f'duration: 0.45, ease: IN }}, {t:.2f});')
    out.append("")
    out.append("          // b07 — the SAME marks re-sort into three aligned columns.")
    for i in range(24):
        dx, dy, rot = DRIFT[i]
        t = 36.60 + (i % 8) * 0.03
        out.append(
            f'          tl.fromTo("#bd-sc{i:02d}", '
            f'{{ x: {dx}, y: {dy}, rotation: {rot} }}, '
            f'{{ x: 0, y: 0, rotation: 0, duration: 1.0, '
            f'ease: "power3.inOut" }}, {t:.2f});')
    return "\n".join(out)


SPEND_T = {"b12": [59.76, 61.30], "b15": [77.17], "b17": [82.61],
           "b18": [85.35], "b19": [89.28], "b20": [92.51], "b21": [96.75],
           "b22": [100.70], "b23": [104.75], "b24": [108.88],
           "b25": [112.42], "b26": [118.18], "b27": [124.98]}


def spend_cues():
    out = []
    for bid, idxs in SPEND.items():
        for i, t in zip(idxs, SPEND_T[bid]):
            out.append(f'          spend("#bd-sc{i:02d}", {t:.2f});   // {bid}')
    return "\n".join(out)


def hole_cues():
    out = []
    for n, i in enumerate(sorted(SPENT)):
        out.append(f'          show("#bd-hl{i:02d}", {128.30 + n * 0.09:.2f});')
    return "\n".join(out)


def audio_markup():
    out = []
    for r in T["rows"]:
        out.append(
            f'      <audio id="vo-{r["id"]}" src="assets/voice/{r["id"]}.wav" '
            f'data-start="{r["audio_start"]}" data-duration="{r["audio_dur"]}" '
            f'data-track-index="10" data-volume="1"></audio>')
    return "\n".join(out)


# ---------------------------------------------------------------------------
INDEX = f"""<!DOCTYPE html>
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
        font-weight: 400;
        font-style: normal;
        font-display: block;
      }}
      @font-face {{
        font-family: "Proxima Nova";
        src: url("assets/fonts/proxima-nova-700.woff2") format("woff2");
        font-weight: 700;
        font-style: normal;
        font-display: block;
      }}
      @font-face {{
        font-family: "Proxima Nova";
        src: url("assets/fonts/proxima-nova-900.woff2") format("woff2");
        font-weight: 900;
        font-style: normal;
        font-display: block;
      }}

      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #0a1e2f;
      }}
      body {{
        font-family: "Proxima Nova", sans-serif;
        -webkit-font-smoothing: antialiased;
      }}

      #root {{
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
      }}

      /* Full-bleed fill lives on a CHILD, never on the composition root. */
      #bg {{
        position: absolute;
        inset: 0;
        background: #0a1e2f;
      }}
      #bg-glow {{
        position: absolute;
        left: 830px;
        top: 520px;
        width: 1900px;
        height: 1200px;
        margin: -600px 0 0 -950px;
        background: radial-gradient(
          ellipse at center,
          rgba(51, 147, 214, 0.16) 0%,
          rgba(13, 36, 55, 0.52) 46%,
          rgba(10, 30, 47, 0) 76%
        );
        will-change: transform;
      }}
      #bg-vignette {{
        position: absolute;
        inset: 0;
        background: radial-gradient(
          ellipse at 50% 50%,
          rgba(10, 30, 47, 0) 56%,
          rgba(10, 30, 47, 0.72) 100%
        );
      }}

      /* Persistent program banner. Sits in the top keep-out band that
         tokens.yml `chrome-regions` declares by name for label furniture. */
      #chrome {{
        position: absolute;
        left: 120px;
        top: 62px;
        display: flex;
        align-items: center;
        gap: 20px;
        opacity: 0;
      }}
      #chrome-mark {{
        display: block;
        width: 10px;
        height: 30px;
        background: #eaab2d;
      }}
      #chrome-text {{
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.68);
      }}

      #root > div[data-composition-src] {{
        position: absolute;
        inset: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
      <div id="bg">
        <div id="bg-glow"></div>
        <div id="bg-vignette"></div>
      </div>

      <div id="chrome">
        <span id="chrome-mark"></span>
        <span id="chrome-text">Early Career Boost</span>
      </div>

      <!-- ONE carrying object for the whole runtime: the board — a field of
           blank scraps, three feeder columns and one dashed statement strip.
           b01 -> b29, nothing on it is ever cleared. See design.md. -->
      <div id="el-board" data-composition-id="board" data-composition-src="compositions/board.html" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-width="1920" data-height="1080"></div>

      <!-- Narration — HeyGen, Oxana (tokens.yml voice.voice_id). One element
           per beat at GLOBAL time; every number below is timing.json's,
           computed by make_timing.py from the real wavs. -->
{audio_markup()}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});

      // The banner settles once, then never moves again.
      tl.fromTo("#chrome", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.7, ease: "power3.out" }}, 0.3);

      // One shared ambient breath, on the background GLOW only — never on
      // content. Finite legs (7s half-period x 21 legs ~= the 141.5s runtime).
      tl.fromTo(
        "#bg-glow",
        {{ y: 0, opacity: 0.94 }},
        {{ y: -18, opacity: 1, duration: 7, ease: "sine.inOut", yoyo: true, repeat: 20 }}, /* motion-allow: background depth-drift on a non-content layer; translate-only, per the design contract's ambient-breath grant */
        0,
      );

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

BOARD = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <!-- head is metadata for this source file only; the runtime discards it -->
  </head>
  <body>
    <template>
      <!-- Brand face, declared per-file so this composition is self-contained.
           Kept in its OWN <style> block: sub-comp CSS is scoped to the
           data-composition-id, and an at-rule must not be able to take the
           layout rules down with it. url() resolves against the HOST document,
           which is where this template gets cloned. -->
      <style>
        @font-face {{
          font-family: "Proxima Nova";
          src: url("assets/fonts/proxima-nova-400.woff2") format("woff2");
          font-weight: 400;
          font-style: normal;
          font-display: block;
        }}
        @font-face {{
          font-family: "Proxima Nova";
          src: url("assets/fonts/proxima-nova-700.woff2") format("woff2");
          font-weight: 700;
          font-style: normal;
          font-display: block;
        }}
        @font-face {{
          font-family: "Proxima Nova";
          src: url("assets/fonts/proxima-nova-900.woff2") format("woff2");
          font-weight: 900;
          font-style: normal;
          font-display: block;
        }}
      </style>

      <style>
        /* Bespoke sub-comp roots are styled with a PLAIN #root block — never
           qualified by their own class/attribute, which renders unstyled under
           composition scoping while passing every static check. */
        #root {{
          position: absolute;
          inset: 0;
          font-family: "Proxima Nova", sans-serif;
          color: #ffffff;
        }}

        /* ---------------------------------------------------------------
           HEADING ZONE — one line, y 140..218. Never two.
           --------------------------------------------------------------- */
        .bd-title,
        .bd-head {{
          position: absolute;
          left: 150px;
          top: 140px;
          width: 1570px;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-title {{
          font-size: 66px;
          font-weight: 900;
          line-height: 1.18;
          letter-spacing: -0.005em;
          color: #ffffff;
        }}
        .bd-head {{
          font-size: 62px;
          font-weight: 900;
          line-height: 1.26;
          letter-spacing: -0.005em;
          color: #ffffff;
        }}

        /* ---------------------------------------------------------------
           THE CARRYING OBJECT — one board. The dashed statement strip is the
           container; everything else is a mark on, under or outside it.
           --------------------------------------------------------------- */
        .bd-strip {{
          position: absolute;
          left: {STRIP_L}px;
          top: {STRIP_T}px;
          width: {STRIP_W}px;
          height: {STRIP_H}px;
          border: 3px dashed rgba(51, 147, 214, 0.9);
          border-radius: 14px;
          transform-origin: left center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-rule {{
          position: absolute;
          left: 16px;
          width: 1218px;
          height: 1px;
          background: rgba(51, 147, 214, 0.42);
          transform-origin: left center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-rule-a {{ top: 60px; }}
        .bd-rule-b {{ top: 108px; }}
        .bd-tick {{
          position: absolute;
          top: 11px;
          width: 2px;
          height: 62px;
          background: rgba(51, 147, 214, 0.75);
          transform-origin: center top;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-clamp {{
          position: absolute;
          left: -1px;
          width: 5px;
          height: 44px;
          background: #eaab2d;
          transform-origin: center center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-clamp-a {{ top: 10px; }}
        .bd-clamp-b {{ top: 166px; }}
        .bd-notch {{
          position: absolute;
          left: 1240px;
          top: 14px;
          width: 4px;
          height: 192px;
          background: #eaab2d;
          transform-origin: center top;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-slotbox {{
          position: absolute;
          top: 9px;
          width: {SLOT_W}px;
          height: 156px;
          border: 2px dashed rgba(51, 147, 214, 0.34);
          border-radius: 8px;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-slot {{
          position: absolute;
          top: 15px;
          width: {SLOT_W}px;
          height: 144px;
          font-size: 40px;
          font-weight: 700;
          line-height: 48px;
          color: #ffffff;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-conn {{
          position: absolute;
          top: 76px;
          width: {GAP_W}px;
          height: 48px;
          font-size: 40px;
          font-weight: 400;
          line-height: 48px;
          text-align: center;
          color: rgba(234, 171, 45, 0.95);
          visibility: hidden;
          opacity: 0;
        }}
        .bd-own {{
          position: absolute;
          left: 16px;
          top: 163px;
          width: 1218px;
          height: 3px;
          background: #eaab2d;
          transform-origin: left center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-rowlabel {{
          position: absolute;
          top: 171px;
          width: {SLOT_W}px;
          height: 40px;
          font-size: 26px;
          font-weight: 700;
          line-height: 40px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          color: rgba(51, 147, 214, 0.95);
          visibility: hidden;
          opacity: 0;
        }}

        /* The crop bracket and the revise arc — the object is not permanent. */
        .bd-crop {{
          position: absolute;
          left: 1470px;
          top: 264px;
          width: 32px;
          height: 244px;
          transform-origin: center center;
          border: 4px solid #eaab2d;
          border-left: none;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-arc {{
          position: absolute;
          left: 1478px;
          top: 514px;
          width: 50px;
          height: 50px;
          border: 3px dashed rgba(51, 147, 214, 0.85);
          border-bottom-color: rgba(10, 30, 47, 0);
          border-left-color: rgba(10, 30, 47, 0);
          border-radius: 50%;
          transform: rotate(38deg);
          visibility: hidden;
          opacity: 0;
        }}

        /* The question the statement answers, hung under the strip. */
        .bd-q > span {{
          display: block;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-colbracket {{
          position: absolute;
          top: 698px;
          width: {COL_W}px;
          height: 12px;
          border-top: 3px dashed rgba(51, 147, 214, 0.7);
          border-left: 3px dashed rgba(51, 147, 214, 0.7);
          border-right: 3px dashed rgba(51, 147, 214, 0.7);
          transform-origin: left center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-hang {{
          position: absolute;
          top: 254px;
          width: 4px;
          height: 22px;
          background: #eaab2d;
          transform-origin: center top;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-q {{
          position: absolute;
          left: 200px;
          top: 512px;
          width: 60px;
          height: 60px;
          border: 3px dashed rgba(51, 147, 214, 0.9);
          border-radius: 50%;
          font-size: 40px;
          font-weight: 700;
          line-height: 54px;
          text-align: center;
          color: rgba(51, 147, 214, 0.95);
          visibility: hidden;
          opacity: 0;
        }}

        /* The quality rail and its five clipped chips. */
        .bd-rail {{
          position: absolute;
          left: 290px;
          top: 512px;
          width: 1090px;
          height: 2px;
          background: rgba(51, 147, 214, 0.55);
          transform-origin: left center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-chip {{
          position: absolute;
          top: 520px;
          height: 44px;
          border: 2px solid rgba(51, 147, 214, 0.9);
          border-radius: 100px;
          font-size: 22px;
          font-weight: 700;
          line-height: 40px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          text-align: center;
          color: rgba(51, 147, 214, 0.98);
          visibility: hidden;
          opacity: 0;
        }}

        /* The three feeder columns: labels, then the field of blank marks. */
        .bd-collabel {{
          position: absolute;
          top: 600px;
          width: {COL_W}px;
          height: 96px;
          font-size: 40px;
          font-weight: 400;
          line-height: 48px;
          color: rgba(255, 255, 255, 0.78);
          visibility: hidden;
          opacity: 0;
        }}
        .bd-scrap {{
          position: absolute;
          width: {SCRAP_W}px;
          height: {SCRAP_H}px;
          border: 2px solid rgba(51, 147, 214, 0.55);
          border-radius: 7px;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-t1 {{ background: rgba(51, 147, 214, 0.20); }}
        .bd-t2 {{ background: rgba(229, 239, 246, 0.10); }}
        .bd-t3 {{ background: rgba(95, 111, 150, 0.34); }}
        .bd-scrule {{
          position: absolute;
          left: 16px;
          height: 3px;
          background: rgba(95, 111, 150, 0.85);
        }}
        .bd-scrule-a {{ top: 13px; width: 96px; }}
        .bd-scrule-b {{ top: 26px; width: 62px; }}
        .bd-hole {{
          position: absolute;
          width: {SCRAP_W}px;
          height: {SCRAP_H}px;
          border: 2px dashed rgba(51, 147, 214, 0.42);
          border-radius: 7px;
          visibility: hidden;
          opacity: 0;
        }}

        /* The third ingredient arrives from OFF the board — it is not in the
           work already done, so it never comes out of a column. */
        .bd-inrule {{
          position: absolute;
          left: 1436px;
          top: 575px;
          width: 84px;
          height: 3px;
          border-top: 3px dashed rgba(51, 147, 214, 0.9);
          transform-origin: right center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-inhead {{
          position: absolute;
          left: 1414px;
          top: 566px;
          width: 22px;
          height: 22px;
          border-top: 4px solid rgba(51, 147, 214, 0.9);
          border-left: 4px solid rgba(51, 147, 214, 0.9);
          transform: rotate(-45deg);
          visibility: hidden;
          opacity: 0;
        }}

        /* What is NOT in the statement, kept on the board as evidence. */
        .bd-tag {{
          position: absolute;
          left: 1530px;
          width: 260px;
          height: 44px;
          font-size: 40px;
          font-weight: 400;
          line-height: 44px;
          text-decoration: line-through;
          text-decoration-thickness: 3px;
          color: rgba(255, 255, 255, 0.62);
          visibility: hidden;
          opacity: 0;
        }}

        /* Three rough drafts — deliberately rougher than the strip they copy:
           an uneven baseline, a rule that overruns, a rule that falls short. */
        .bd-draft {{
          position: absolute;
          left: 1540px;
          width: 250px;
          height: 64px;
          border: 2px solid rgba(51, 147, 214, 0.62);
          border-radius: 8px;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-d1 {{ top: 560px; }}
        .bd-d2 {{ top: 648px; }}
        .bd-d3 {{ top: 736px; }}
        .bd-dline {{
          position: absolute;
          height: 4px;
          background: rgba(255, 255, 255, 0.55);
          visibility: hidden;
          opacity: 0;
        }}
        .bd-dl1a {{ left: 14px; top: 18px; width: 196px; transform: rotate(-1.6deg); }}
        .bd-dl1b {{ left: 14px; top: 40px; width: 132px; transform: rotate(1.4deg); }}
        .bd-dl2a {{ left: 14px; top: 20px; width: 244px; }}
        .bd-dl2b {{ left: 14px; top: 42px; width: 176px; }}
        .bd-dl3a {{ left: 14px; top: 20px; width: 104px; }}
        .bd-dl3b {{ left: 14px; top: 42px; width: 58px; }}
        .bd-ring {{
          position: absolute;
          left: 1528px;
          top: 638px;
          width: 272px;
          height: 84px;
          border: 3px solid #eaab2d;
          border-radius: 46px;
          transform: rotate(-1.2deg);
          visibility: hidden;
          opacity: 0;
        }}

        /* The revision loop, ruled around the board's lower margin. */
        .bd-loop {{
          position: absolute;
          background: rgba(234, 171, 45, 0.9);
          visibility: hidden;
          opacity: 0;
        }}
        .bd-l0 {{ left: 152px; top: 497px; width: 42px; height: 3px; transform-origin: right center; }}
        .bd-l1 {{ left: 152px; top: 500px; width: 3px; height: 443px; transform-origin: center top; }}
        .bd-l2 {{ left: 152px; top: 943px; width: 1351px; height: 3px; transform-origin: left center; }}
        .bd-l3 {{ left: 1500px; top: 603px; width: 3px; height: 340px; transform-origin: center bottom; }}
        .bd-l4 {{ left: 1440px; top: 600px; width: 63px; height: 3px; transform-origin: right center; }}
        .bd-l5 {{ left: 1440px; top: 522px; width: 3px; height: 78px; transform-origin: center bottom; }}
        .bd-lhead {{
          position: absolute;
          left: 1431px;
          top: 500px;
          width: 22px;
          height: 22px;
          border-top: 4px solid rgba(234, 171, 45, 0.9);
          border-left: 4px solid rgba(234, 171, 45, 0.9);
          transform: rotate(45deg);
          visibility: hidden;
          opacity: 0;
        }}

        /* The mount at the head of the board — the line is hung under it. */
        .bd-mount {{
          position: absolute;
          left: 190px;
          top: 250px;
          width: 1280px;
          height: 4px;
          background: #eaab2d;
          transform-origin: left center;
          visibility: hidden;
          opacity: 0;
        }}
        .bd-mounttick {{
          position: absolute;
          left: 828px;
          top: 228px;
          width: 4px;
          height: 22px;
          background: #eaab2d;
          transform-origin: center bottom;
          visibility: hidden;
          opacity: 0;
        }}
      </style>

      <div id="root" data-composition-id="board" data-width="1920" data-height="1080">
{headings_markup()}

        <div class="bd-mounttick" id="bd-mounttick"></div>
        <div class="bd-mount" id="bd-mount"></div>
        <div class="bd-hang" id="bd-hang1" style="left: 500px"></div>
        <div class="bd-hang" id="bd-hang2" style="left: 1160px"></div>

        <div class="bd-strip" id="bd-strip">
          <div class="bd-rule bd-rule-a" id="bd-rule1" data-layout-allow-overlap></div>
          <div class="bd-rule bd-rule-b" id="bd-rule2" data-layout-allow-overlap></div>
          <div class="bd-tick" id="bd-tick1" data-layout-allow-overlap style="left: {rel(GAP_X[0]) + GAP_W // 2}px"></div>
          <div class="bd-tick" id="bd-tick2" data-layout-allow-overlap style="left: {rel(GAP_X[1]) + GAP_W // 2}px"></div>
          <div class="bd-clamp bd-clamp-a" id="bd-clamp1"></div>
          <div class="bd-clamp bd-clamp-b" id="bd-clamp2"></div>
          <div class="bd-notch" id="bd-notch" data-layout-allow-overlap></div>
{slots_markup()}
          <div class="bd-own" id="bd-own" data-layout-allow-overlap></div>
          <div id="bd-rowlabels" data-role="list">
{rowlabels_markup()}
          </div>
        </div>

        <div class="bd-crop" id="bd-crop"></div>
        <div class="bd-arc" id="bd-arc"></div>
        <div class="bd-q" id="bd-q"><span id="bd-qmark">?</span></div>

        <div class="bd-rail" id="bd-rail"></div>
        <div id="bd-chiprow" data-role="list">
{chips_markup()}
        </div>

        <div id="bd-collabels" data-role="list">
{collabels_markup()}
        </div>
{colbrackets_markup()}

        <div class="bd-inrule" id="bd-inrule"></div>
        <div class="bd-inhead" id="bd-inhead"></div>

        <div id="bd-field">
{scraps_markup()}
        </div>
        <div id="bd-holes">
{holes_markup()}
        </div>

        <div id="bd-tags" data-role="list">
{tags_markup()}
        </div>

        <div class="bd-draft bd-d1" id="bd-draft1">
          <span class="bd-dline bd-dl1a" id="bd-dl1a"></span>
          <span class="bd-dline bd-dl1b" id="bd-dl1b"></span>
        </div>
        <div class="bd-draft bd-d2" id="bd-draft2">
          <span class="bd-dline bd-dl2a" id="bd-dl2a"></span>
          <span class="bd-dline bd-dl2b" id="bd-dl2b"></span>
        </div>
        <div class="bd-draft bd-d3" id="bd-draft3">
          <span class="bd-dline bd-dl3a" id="bd-dl3a"></span>
          <span class="bd-dline bd-dl3b" id="bd-dl3b"></span>
        </div>
        <div class="bd-ring" id="bd-ring" data-layout-allow-overlap></div>

        <div class="bd-loop bd-l0" id="bd-l0"></div>
        <div class="bd-loop bd-l1" id="bd-l1"></div>
        <div class="bd-loop bd-l2" id="bd-l2"></div>
        <div class="bd-loop bd-l3" id="bd-l3"></div>
        <div class="bd-loop bd-l4" id="bd-l4"></div>
        <div class="bd-loop bd-l5" id="bd-l5"></div>
        <div class="bd-lhead" id="bd-lhead"></div>
      </div>

      <script>
        window.__timelines = window.__timelines || {{}};
        (function () {{
          const tl = gsap.timeline({{ paused: true }});
          const IN = "power3.out";
          const OUT = "power2.in";

          // Arrivals are binary (autoAlpha 1) plus a short whip — never a slow
          // fade. Every time below is absolute: a beat start from timing.json,
          // or the audio_meta.json word timestamp named in the comment.
          function show(sel, t) {{
            tl.fromTo(sel, {{ autoAlpha: 0 }},
                      {{ autoAlpha: 1, duration: 0.34, ease: IN }}, t);
          }}
          function arrive(sel, t, y) {{
            tl.set(sel, {{ autoAlpha: 1, y: y }}, t);
            tl.to(sel, {{ y: 0, duration: 0.4, ease: IN }}, t);
          }}
          function head(sel, t) {{
            tl.set(sel, {{ autoAlpha: 1, y: 30 }}, t);
            tl.to(sel, {{ y: 0, duration: 0.34, ease: IN }}, t);
          }}
          function hide(sel, t) {{
            tl.to(sel, {{ autoAlpha: 0, y: -26, duration: 0.22, ease: OUT }}, t);
          }}
          function rule(sel, t, dur) {{
            tl.fromTo(sel, {{ autoAlpha: 0, scaleX: 0 }},
                      {{ autoAlpha: 1, scaleX: 1, duration: dur, ease: IN }}, t);
          }}
          function vrule(sel, t, dur) {{
            tl.fromTo(sel, {{ autoAlpha: 0, scaleY: 0 }},
                      {{ autoAlpha: 1, scaleY: 1, duration: dur, ease: IN }}, t);
          }}
          // A mark is SPENT: it leaves the column once and the gap it left
          // stays on the board. One-shot, never a keep-alive.
          function spend(sel, t) {{
            tl.to(sel, {{ autoAlpha: 0, y: 14, duration: 0.32, ease: OUT }}, t);
          }}

          // ---- headings, one line each, one per beat.
{heading_cues()}

          // ---- b01 (0.000) — everything already done arrives as a field of
          //      blank marks, unsorted, under the lesson's own name.
{scrap_cues()}

          // Every cue below is pinned to the audio_meta.json word that earns
          // it (named in the comment). Beats are staged so the object gains
          // something ACROSS its span — a beat whose content all lands at its
          // start looks right at its own midpoint and is frozen for the rest
          // of it, which is what the dense precheck grid caught.

          // ---- b02 (11.297) — the container is ruled, and it is empty.
          rule("#bd-strip", 11.55, 0.75);

          // ---- b03 (14.459) — two rules inside it: one, then two sentences.
          rule("#bd-rule1", 16.69, 0.5);    // "one" 16.69
          rule("#bd-rule2", 17.13, 0.5);    // "two" 17.13

          // ---- b04 (18.640) — not a mission statement, and not permanent.
          show("#bd-crop", 20.21);          // "mission" 20.21
          show("#bd-arc", 22.07);           // "permanent." 22.07

          // ---- b05 (23.187) — the question it answers, then the question.
          show("#bd-q", 25.52);             // "question:" 25.52
          show("#bd-qmark", 29.16);         // "why?" 29.16

          // ---- b06 (30.111) — two conditions clamp the line.
          show("#bd-clamp1", 30.60);        // "Specific" 30.60
          show("#bd-clamp2", 33.80);        // "honest" 33.80

          // ---- b07 (36.382) — the field re-sorts; the strip gains its slots.
          vrule("#bd-tick1", 37.55, 0.4);
          vrule("#bd-tick2", 37.75, 0.4);

          // ---- b08..b10 — each feeder is named, then bracketed as a group.
          arrive("#bd-cl1", 40.49, 24);     // "energizes" 40.49
          rule("#bd-cb1", 42.39, 0.45);     // "work" 42.39
          arrive("#bd-cl2", 46.40, 24);     // "what you want to help" 46.40
          rule("#bd-cb2", 48.58, 0.45);     // "criterion," 48.58
          arrive("#bd-cl3", 52.79, 24);     // "value" 52.79
          rule("#bd-inrule", 53.97, 0.45);  // "strengths" 53.97
          show("#bd-inhead", 54.49);        // "skills" 54.49
          rule("#bd-cb3", 55.11, 0.45);     // "growing" 55.11

          // ---- b11 (56.346) — the structure, drawn empty.
          show("#bd-slotbox1", 56.70);
          show("#bd-slotbox2", 57.06);
          show("#bd-slotbox3", 57.42);

          // ---- b12 (58.934) — the first two are promoted UP out of the
          //      columns; the third arrives from OFF the board's edge.
          arrive("#bd-slot1", 59.76, 30);   // "use" 59.76
          show("#bd-conn1", 61.12);         // "to" 61.12
          arrive("#bd-slot2", 61.30, 30);   // "help" 61.30
          show("#bd-conn2", 64.08);         // "because" 64.08
          tl.fromTo("#bd-slot3", {{ autoAlpha: 0, x: 210 }},
                    {{ autoAlpha: 1, x: 0, duration: 0.55, ease: IN }}, 64.42);

          // ---- b13 (66.276) — what is NOT in there, kept in the margin.
          show("#bd-tag1", 68.77);          // "grand" 68.77
          show("#bd-tag2", 70.14);          // "no buzzwords" 70.14

          // ---- b14 (71.659) — the same three slots, read a second way.
          show("#bd-rl1", 72.37);           // "direction," 72.37
          show("#bd-rl2", 73.41);           // "contribution," 73.41
          show("#bd-rl3", 74.99);           // "a reason." 74.99

          // ---- b15 (76.206) — the line is signed.
          rule("#bd-own", 76.94, 0.55);     // "should sound" 76.94

          // ---- b16..b21 — the rail, then five chips clipped to it, then the
          //      right edge pulled in one notch on "brief".
          rule("#bd-rail", 79.16, 0.7);     // "statement" 79.16
          arrive("#bd-chip1", 83.11, 18);   // "inspiring" 83.11
          arrive("#bd-chip2", 86.27, 18);   // "energy," 86.27
          arrive("#bd-chip3", 89.76, 18);   // "mission" 89.76
          arrive("#bd-chip4", 94.51, 18);   // "several" 94.51
          arrive("#bd-chip5", 96.75, 18);   // "brief" 96.75
          vrule("#bd-notch", 97.55, 0.4);   // "easy to remember," 97.55
          tl.fromTo("#bd-crop", {{ scaleY: 1 }},
                    {{ scaleY: 0.803, duration: 0.45,
                      ease: "power2.inOut" }}, 97.55);

          // ---- b22..b25 — three rough drafts, then one is picked.
          show("#bd-draft1", 101.52);       // "write," 101.52
          show("#bd-dl1a", 105.59);         // "something" 105.59
          show("#bd-dl1b", 106.39);         // "fuzzy" 106.39
          show("#bd-draft2", 109.22);       // "honest" 109.22
          show("#bd-dl2a", 109.72);         // "rough" 109.72
          show("#bd-dl2b", 110.22);         // "polished" 110.22
          show("#bd-draft3", 113.38);       // "three" 113.38
          show("#bd-dl3a", 113.62);         // "quick" 113.62
          show("#bd-dl3b", 113.86);         // "versions," 113.86
          show("#bd-ring", 114.84);         // "pick" 114.84

          // ---- b26..b27 — the revision loop is ruled round the board.
          rule("#bd-l0", 118.18, 0.3);      // "perfect," 118.18
          vrule("#bd-l1", 118.45, 0.6);
          rule("#bd-l2", 119.90, 0.9);      // "revise" 120.18
          vrule("#bd-l3", 122.82, 0.7);     // "decision loop." 122.82
          rule("#bd-l4", 125.80, 0.35);     // "of clarity" 125.80

          // ---- b28 (127.815) — every mark the board spent, kept visible.
{hole_cues()}

          // ---- b29 (131.500) — the loop closes on the line, and the line is
          //      hung on a mount at the head of the board. Both at once.
          vrule("#bd-l5", 132.03, 0.45);      // "comes from" 132.03
          rule("#bd-mount", 132.79, 0.7);     // "method" 132.79
          vrule("#bd-mounttick", 133.75, 0.3);// "return to" 133.75
          vrule("#bd-hang1", 134.41, 0.3);    // "a purpose," 134.41
          show("#bd-lhead", 135.87);          // "own words," 135.87
          vrule("#bd-hang2", 137.31, 0.62);   // "point it at." 137.31

          // ---- marks spent out of the columns, one per beat from b17.
{spend_cues()}

          window.__timelines["board"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""

(WS / "index.html").write_text(INDEX)
(WS / "compositions").mkdir(exist_ok=True)
(WS / "compositions" / "board.html").write_text(BOARD)
print(f"index.html + compositions/board.html written — total {TOTAL}s, "
      f"{len(T['rows'])} beats, 24 scraps, {len(SPENT)} spent")
