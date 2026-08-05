#!/usr/bin/env python3
"""build_wall.py — emit compositions/wall.html and the index.html clip/audio
rows from the COMPUTED timings.

Every time in the output comes from timing.json (which came from the real wav
durations) or from a narration word timestamp in audio_meta.json. Nothing here
is hand-tuned; re-running after a re-synthesis reproduces the composition.

    python3 build_wall.py
"""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent

T = json.loads((WS / "timing.json").read_text())
META = json.loads((WS / "audio_meta.json").read_text())
TOTAL = T["total"]
ROW = {r["id"]: r for r in T["rows"]}
VOICE = {v["id"]: v for v in META["voices"]}


def vis(bid):
    return ROW[bid]["vis_start"]


def word_at(bid, needle, nth=1):
    """Absolute start time of the nth narration word containing `needle`.

    This is the word-timestamp-driven half of the reveal contract: a sub-event
    inside a beat lands on the word that earns it, not on a fraction someone
    typed. Falls back to the beat's own picture start if the word is absent, so
    a script edit degrades to a beat-level cue instead of crashing.
    """
    seen = 0
    for w in VOICE[bid]["words"]:
        if needle.lower() in w["text"].lower():
            seen += 1
            if seen == nth:
                return round(ROW[bid]["audio_start"] + float(w["start"]), 3)
    return round(vis(bid) + 0.05, 3)


# ---------------------------------------------------------------------------
# GEOMETRY — every number below is canvas px, and every one of them is inside
# the keep-out bands check_ink grades (x 114..1806, y 114..966).
# ---------------------------------------------------------------------------
WALL_X = 900            # left edge of the wall column
U = 70                  # one unit
JOINT = 6               # hairline joint between neighbours
BASE_Y = 900            # bottom of course 0
CH = 72                 # course (slab) height
PITCH = 80              # course pitch: 72 slab + 8 joint

RAIL_X = 1766
RAIL_W = 8
RAIL_TOP = 188          # the rail's faint upper end

COPY_X = 120
COPY_W = 660
COPY_Y = 236

# course k: solid slabs as (unit_offset, unit_width). Joints are staggered
# course to course on purpose — no two neighbouring courses break in the same
# place, which is what makes the mass read as bonded rather than as a grid.
COURSES = {
    0: [(0, 3), (6, 3), (9, 3)],            # (3,3) at offset 3 is THE NOTCH
    1: [(0, 2), (2, 3), (5, 3), (8, 2), (10, 2)],
    2: [(0, 3), (3, 3), (6, 2), (8, 3), (11, 1)],
    3: [(0, 1), (1, 3), (4, 2), (6, 3), (9, 3)],
    4: [(0, 2), (2, 2), (4, 3), (7, 3), (10, 2)],
    5: [(0, 3), (3, 1), (4, 3), (7, 2), (9, 3)],   # the hatched band
    7: [(0, 3), (3, 3), (6, 3), (9, 3)],           # slot 3 is the commitment
}
WINDOWS = [(0, 4), (4, 4), (8, 4)]          # course 6 — the three voids
QUEUE = [(0, 3), (4, 3), (8, 3)]            # course 8 — the unfilled ghost queue
NOTCH = (3, 3)                              # the hole in course 0, open from s01

GHOST_ALPHA = {0: .26, 1: .26, 2: .24, 3: .21, 4: .18,
               5: .15, 6: .11, 7: .075, 8: .05}

FACES = ["dot", "arc", "nib"]               # the three ways of working

BLUE = "#3393d6"
GOLD = "#eaab2d"


def sx(off):
    return WALL_X + U * off


def sw(units):
    return U * units - JOINT


def cy(k):
    return BASE_Y - PITCH * k - CH


def built_top(k):
    """Canvas y of the top edge of course k — what the rail must agree with."""
    return cy(k)


# ---------------------------------------------------------------------------
# MARKUP
# ---------------------------------------------------------------------------
def glyph(kind):
    return f'<span class="gl gl-{kind}"></span>'


parts = []
A = parts.append

# --- ghost scaffold (present from the title beat; fades out toward the top) --
A('      <div id="ghost">')
for k in sorted(GHOST_ALPHA):
    if k == 6:
        cells = WINDOWS
    elif k == 8:
        cells = QUEUE
    elif k == 0:
        cells = COURSES[0] + [NOTCH]
    else:
        cells = COURSES.get(k, [])
    for off, n in cells:
        A(f'        <div class="gh" style="left:{sx(off)}px;top:{cy(k)}px;'
          f'width:{sw(n)}px;height:{CH}px;opacity:{GHOST_ALPHA[k]}"></div>')
A('      </div>')

# --- the plinth, and the notch that stays open until the last beat -----------
A(f'      <div id="plinth" style="left:{WALL_X - 16}px;top:{BASE_Y + 4}px;'
  f'width:{U * 12 + 32}px"></div>')
A(f'      <div id="notch" style="left:{sx(NOTCH[0])}px;top:{cy(0)}px;'
  f'width:{sw(NOTCH[1])}px;height:{CH}px"></div>')

# --- the solid courses ------------------------------------------------------
# beat that lays each course / each slab
LAY = {}
for i, (off, n) in enumerate(COURSES[0]):
    LAY[(0, i)] = "s02" if i < 2 else "s03"
for k, beat in ((1, "s04"), (2, "s06"), (3, "s07"), (4, "s08"), (5, "s10")):
    for i in range(len(COURSES[k])):
        LAY[(k, i)] = beat
for i in range(len(COURSES[7])):
    LAY[(7, i)] = "s15" if i == 1 else "s16"

face_n = 0
for k in (0, 1, 2, 3, 4, 5, 7):
    for i, (off, n) in enumerate(COURSES[k]):
        beat = LAY[(k, i)]
        face = FACES[face_n % 3]
        face_n += 1
        sid = f"slab-{k}-{i}"
        cls = ["slab", f"g-{beat}"]
        if k == 5:
            cls.append("slab-hatched")
        if k == 7 and i == 1:
            sid = "slab-commit"
            cls.append("slab-commit")
        # courses 0 and 1 are laid PLAIN and acquire their faces at s06 —
        # material already on screen, re-read (the concept's first transform).
        late = k in (0, 1)
        gl = glyph(face)
        if late:
            gl = f'<span class="gl-late g-s06">{gl}</span>'
        A(f'      <div id="{sid}" class="{" ".join(cls)}" '
          f'style="left:{sx(off)}px;top:{cy(k)}px;width:{sw(n)}px;'
          f'height:{CH}px">{gl}'
          + ('<span class="hatch"></span>' if k == 5 else '')
          + ('<span class="score"></span><span class="score s2"></span>'
             '<span class="score s3"></span>' if sid == "slab-commit" else '')
          + '</div>')

# the ring that marks the hatched band before it turns over
A(f'      <div id="band-ring" class="g-s11" style="left:{sx(0) - 8}px;'
  f'top:{cy(5) - 8}px;width:{U * 12 + 16 - JOINT}px;height:{CH + 16}px"></div>')

# --- course 6: the three open windows ---------------------------------------
WIN_LABEL = ["Dream job", "AI-driven world", "How you move"]
WIN_BEAT = ["s12", "s13", "s14"]
for i, (off, n) in enumerate(WINDOWS):
    A(f'      <div id="win-{i}" class="win {"g-" + WIN_BEAT[i]}" '
      f'style="left:{sx(off)}px;top:{cy(6)}px;width:{sw(n)}px;height:{CH}px">'
      f'<span class="win-label">{WIN_LABEL[i]}</span></div>')
# the three moves, cut as notches along the third window's sill
for i in range(3):
    A(f'      <div id="sill-{i}" class="sill g-s14" '
      f'style="left:{sx(WINDOWS[2][0]) + 44 + i * 76}px;'
      f'top:{cy(6) + CH - 9}px"></div>')

# --- course 8: the queue that stays unfilled ---------------------------------
for i, (off, n) in enumerate(QUEUE):
    A(f'      <div id="queue-{i}" class="queue g-s18" '
      f'style="left:{sx(off)}px;top:{cy(8)}px;width:{sw(n)}px;'
      f'height:{CH}px"></div>')

# --- the socket the commitment slab leaves behind ---------------------------
A(f'      <div id="socket" style="left:{sx(3)}px;top:{cy(7)}px;'
  f'width:{sw(3)}px;height:{CH}px"></div>')

# --- the two feeds that score the commitment slab ---------------------------
# NOTE the ids: an id whose first 3-8 characters are all hex digits reads to
# check_brand.py as a colour literal (`#feed-a` parses as #feed + "-a"), so the
# scoring feeds are `supply-*`, never `feed-*`.
A('      <div id="supply-a" class="supply g-s15"></div>')
A('      <div id="supply-b" class="supply g-s15"></div>')

# --- the graduated rail: inked height == built height, always ---------------
A(f'      <div id="rail" style="left:{RAIL_X}px;top:{RAIL_TOP}px;'
  f'width:{RAIL_W}px;height:{BASE_Y - RAIL_TOP}px"></div>')
A(f'      <div id="rail-ink" style="left:{RAIL_X}px;top:{BASE_Y}px;'
  f'width:{RAIL_W}px"></div>')
for k in range(1, 9):
    A(f'      <div class="tick" style="left:{RAIL_X - 8}px;'
      f'top:{BASE_Y - PITCH * k}px"></div>')
A(f'      <div id="rail-cap" style="left:{RAIL_X - 12}px;'
  f'top:{built_top(7) - 3}px"></div>')

# --- the hinged sight-arm, and the help tether ------------------------------
A('      <div id="sight-arm" data-layout-allow-overlap data-layout-allow-overflow>'
  '<span class="arm-hinge"></span>'
  '<span class="arm-bar arm-a"></span>'
  '<span class="arm-bar arm-b"></span>'
  '<span class="arm-fan"></span></div>')
A('      <div id="tether" data-layout-allow-overlap>'
  '<span class="teth-clamp"></span>'
  '<span class="teth-line"></span>'
  '<span class="teth-drop"></span>'
  '<span class="teth-end"></span></div>')

WALL = "\n".join(parts)


# ---------------------------------------------------------------------------
# COPY — every line traces to its own beat's narration. Headings are Title
# Case with no terminal period (check_copy.py grades data-role="heading").
# ---------------------------------------------------------------------------
def block(bid, kicker, heading, extra="", title=False):
    tag = "h1" if title else "h2"
    return (
        f'      <div id="say-{bid}" class="say{" say-title" if title else ""}">\n'
        f'        <p class="kicker">{kicker}</p>\n'
        f'        <{tag} data-role="heading" class="head">{heading}</{tag}>\n'
        f'{extra}'
        f'      </div>')


def stmt(text):
    return f'        <p class="stmt">{text}</p>\n'


def listing(items):
    rows = "".join(
        f'          <p class="li">{t}</p>\n' for t in items)
    return ('        <div class="list" data-role="list">\n'
            f'{rows}'
            '        </div>\n')


def compare(a, b):
    return ('        <div class="cmp" data-role="compare">\n'
            f'          <div class="card" data-role="card">{a}</div>\n'
            f'          <div class="card" data-role="card">{b}</div>\n'
            '        </div>\n')


COPY = [
    block("s01", "Welcome", "Mini Syllabus",
          stmt("Early Career Boost starts here."), title=True),
    block("s02", "Welcome", "Glad You’re Here"),
    block("s03", "Your starting point", "Your Starting Point",
          stmt("Exploring your future, or figuring out what comes next.")),
    block("s04", "How this track works", "Each Step Builds Your Foundation",
          stmt("Each step builds on the one before it.")),
    block("s05", "How this track works", "Your Progress Bar Shows Where You Are",
          stmt("Always showing where you are, and what’s ahead.")),
    block("s06", "How you’ll learn", "You’ll Learn by Doing",
          listing(["Click-through activities", "Short reflections", "Uploads"])),
    block("s07", "How you’ll learn", "Tools to Explore Your Pathways",
          stmt("The Career Mapping Tool opens up different pathways.")),
    block("s08", "How you’ll learn", "Help Is One Click Away",
          stmt("One click away in #questionsupport.")),
    block("s09", "What you’ll learn", "What You’ll Actually Learn"),
    block("s10", "Mindset", "It Starts with the Right Mindset"),
    block("s11", "Mindset", "From Limiting Beliefs to a Growth Mindset",
          compare("Limiting beliefs", "A growth mindset")),
    block("s12", "The real questions", "What Makes a Dream Job Today?"),
    block("s13", "The real questions", "Which Skills Matter in an AI-Driven World?"),
    block("s14", "The real questions", "And How Do You Actually Move?",
          stmt("Networking, building a résumé, and searching for the "
               "right opportunities.")),
    block("s15", "Your commitment statement", "Write Your Career Commitment Statement",
          listing(["In your Workbook", "Or with the AI-Career Commitment tool"])),
    block("s16", "Your commitment statement", "Try Both for the Practice"),
    block("s17", "Your first step", "Submit It as Your First Step",
          stmt("Career development isn’t about thinking, it’s about doing.")),
    block("s18", "Your first step", "Keep Building from Here",
          stmt("Short activities, milestones, and skills that move you "
               "toward your goals.")),
]
COPY_HTML = "\n".join(COPY)


# ---------------------------------------------------------------------------
# TIMELINE — entrances only, cued to the word that earns them.
# ---------------------------------------------------------------------------
BEATS = [f"s{i:02d}" for i in range(1, 19)]
js = []
J = js.append

J("        var tl = gsap.timeline({ paused: true });")
J("")
J("        /* The copy column: one block per beat, handed over with autoAlpha")
J("           so a settled block is visibility:hidden and cannot be read as")
J("           overlapping the next one.")
J("")
J("           The handoff is STRICTLY SEQUENTIAL — the outgoing block finishes")
J("           at vis-0.08 and the incoming one starts at vis+0.04. A crossfade")
J("           puts two headings on the same 660px column for ~0.14s, and")
J("           check_layout samples transition seams precisely because that is")
J("           where transient collisions hide: it read the seam as")
J("           content_overlap on p.kicker / h2.head / p.stmt-vs-p.li. */")
for i, b in enumerate(BEATS):
    t0 = round(vis(b) + 0.04, 3)
    J(f'        tl.fromTo("#say-{b}", {{ autoAlpha: 0, y: 20 }}, '
      f'{{ autoAlpha: 1, y: 0, duration: 0.44, ease: "power3.out" }}, {t0});')
    if i + 1 < len(BEATS):
        t1 = round(vis(BEATS[i + 1]) - 0.26, 3)
        J(f'        tl.to("#say-{b}", {{ autoAlpha: 0, duration: 0.18, '
          f'ease: "power2.in" }}, {t1});')
J("")
J("        /* The scaffold, the plinth and the open notch are on frame from")
J("           the first second — the hole the last beat closes is authored")
J("           into the title card, not announced at the end. */")
J('        tl.fromTo("#ghost .gh", { autoAlpha: 0 }, { autoAlpha: 1, '
  'duration: 0.5, ease: "power2.out", stagger: 0.012 }, 0.15);')
J('        tl.fromTo("#plinth", { autoAlpha: 0, scaleX: 0.86 }, '
  '{ autoAlpha: 1, scaleX: 1, duration: 0.6, ease: "power3.out" }, 0.1);')
J('        tl.fromTo("#notch", { autoAlpha: 0 }, { autoAlpha: 1, '
  'duration: 0.6, ease: "power2.out" }, 0.55);')
J("")

# --- slabs, course by course, on the word that lays them --------------------
# A beat's PRIMARY move is cued to a word EARLY in its own line, so the beat's
# state is on frame at its own midpoint — which is where every sampled gate and
# every contact-sheet reader looks. Cueing the mass on a late word (the first
# pass cued course 0 on "starting", 0.6s past the midpoint) puts the whole build
# one beat behind its narration and makes adjacent stills read as twins.
# Secondary, staggered detail keeps its own later word below.
CUE = {
    "s02": word_at("s02", "really"),
    "s03": word_at("s03", "exploring"),
    "s04": word_at("s04", "move"),
    "s06": word_at("s06", "learn"),
    "s07": word_at("s07", "use"),
    "s08": word_at("s08", "stuck"),
    "s10": word_at("s10", "career"),
    "s15": word_at("s15", "write"),
    "s16": word_at("s16", "both"),
}
J("        /* Mass, monotonically: a course is laid on the word that lays it,")
J("           and no slab ever moves again. */")
for beat in ("s02", "s03", "s04", "s06", "s07", "s08", "s10", "s15", "s16"):
    J(f'        tl.fromTo(".g-{beat}", {{ autoAlpha: 0, y: 26 }}, '
      f'{{ autoAlpha: 1, y: 0, duration: 0.5, ease: "back.out(1.25)", '
      f'stagger: 0.07 }}, {CUE[beat]});')
J("")
J("        /* TRANSFORM 1 — the slabs already standing in courses 0 and 1")
J("           acquire their own faces where they sit. Nothing is added. */")
J(f'        tl.fromTo(".gl-late", {{ autoAlpha: 0, scale: 0.4 }}, '
  f'{{ autoAlpha: 1, scale: 1, duration: 0.42, ease: "back.out(2)", '
  f'stagger: 0.05 }}, {word_at("s06", "activities")});')
J("")
J("        /* The rail is DERIVED: its inked height is the built height, in")
J("           every frame. Each step below is (900 - top of the built course). */")
RAIL_STEPS = [("s05", 1, round(vis("s05") + 0.45, 3)),
              ("s06", 2, round(CUE["s06"] + 0.3, 3)),
              ("s07", 3, round(CUE["s07"] + 0.3, 3)),
              ("s08", 4, round(CUE["s08"] + 0.3, 3)),
              ("s10", 5, round(CUE["s10"] + 0.3, 3)),
              ("s12", 6, word_at("s12", "real")),
              ("s16", 7, round(CUE["s16"] + 0.3, 3))]
J('        tl.fromTo("#rail", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, '
  f'ease: "power2.out" }}, {round(vis("s05") + 0.1, 3)});')
J('        tl.fromTo(".tick", { autoAlpha: 0, scaleX: 0.3 }, { autoAlpha: 1, '
  'scaleX: 1, duration: 0.4, ease: "power3.out", stagger: 0.05 }, '
  f'{round(vis("s05") + 0.2, 3)});')
first = True
for beat, k, t in RAIL_STEPS:
    h = BASE_Y - built_top(k)
    if first:
        J(f'        tl.fromTo("#rail-ink", {{ height: 0 }}, {{ height: {h}, '
          f'duration: 0.55, ease: "power2.out" }}, {t});')
        first = False
    else:
        J(f'        tl.to("#rail-ink", {{ height: {h}, duration: 0.5, '
          f'ease: "power2.out" }}, {t});')
J("")
J("        /* s07 — the sight-arm clips on and fans over what is not built. */")
J('        tl.fromTo("#sight-arm", { autoAlpha: 0, rotation: 12, '
  'transformOrigin: "6px 50%" }, { autoAlpha: 1, rotation: 0, duration: 0.6, '
  f'ease: "power3.out" }}, {round(CUE["s07"] + 0.4, 3)});')
J("        /* s09 — it re-aims at the empty scaffold. Nothing new arrives. */")
J('        tl.to("#sight-arm", { rotation: -22, transformOrigin: "6px 50%", '
  f'duration: 0.7, ease: "power2.inOut" }}, {word_at("s09", "Now")});')
J("")
J("        /* s08 — the help tether clips in and is in every later frame. */")
J('        tl.fromTo("#tether", { autoAlpha: 0, x: -34 }, { autoAlpha: 1, '
  f'x: 0, duration: 0.55, ease: "power3.out" }}, '
  f'{round(CUE["s08"] + 0.35, 3)});')
J("")
J("        /* TRANSFORM 2 — the hatched band is ringed, then turned over to")
J("           solid faces IN PLACE. No slab moves; the band is re-read. */")
J('        tl.fromTo("#band-ring", { autoAlpha: 0, scale: 1.06, '
  'transformOrigin: "50% 50%" }, { autoAlpha: 1, scale: 1, duration: 0.45, '
  f'ease: "power3.out" }}, {word_at("s11", "limiting")});')
J('        tl.to(".slab-hatched .hatch", { autoAlpha: 0, duration: 0.5, '
  f'ease: "power2.inOut", stagger: 0.06 }}, {word_at("s11", "growth")});')
J('        tl.to("#band-ring", { borderColor: "rgba(51,147,214,0.55)", '
  f'duration: 0.45 }}, {round(vis("s12") + 0.05, 3)});')
J("")
J("        /* s12-s14 — the first voids in the piece: three open windows. */")
for i, b in enumerate(WIN_BEAT):
    key = ("real", "skills", "move")[i]
    J(f'        tl.fromTo("#win-{i}", {{ autoAlpha: 0, scaleY: 0.4, '
      f'transformOrigin: "50% 100%" }}, {{ autoAlpha: 1, scaleY: 1, '
      f'duration: 0.5, ease: "power3.out" }}, {word_at(b, key)});')
J('        tl.fromTo(".sill", { autoAlpha: 0, y: -8 }, { autoAlpha: 1, y: 0, '
  'duration: 0.35, ease: "power3.out", stagger: 0.12 }, '
  f'{word_at("s14", "networking")});')
J("")
J("        /* s15 — the commitment slab is scored on the working face from")
J("           two feeds at once, and stays hollow until both have run. */")
J('        tl.fromTo(".supply", { autoAlpha: 0, scaleX: 0 }, { autoAlpha: 1, '
  'scaleX: 1, transformOrigin: "0% 50%", duration: 0.55, ease: "power3.out", '
  f'stagger: 0.18 }}, {word_at("s15", "commitment")});')
J('        tl.fromTo(".score", { autoAlpha: 0, scaleX: 0 }, { autoAlpha: 1, '
  'scaleX: 1, transformOrigin: "0% 50%", duration: 0.35, ease: "power2.out", '
  f'stagger: 0.1 }}, {word_at("s15", "short")});')
J('        tl.to("#slab-commit", { backgroundColor: "rgba(234,171,45,0.92)", '
  f'duration: 0.5, ease: "power2.out" }}, {word_at("s16", "practice")});')
J("")
J("        /* s17 — THE PAYOFF. One subtraction: the slab leaves the course it")
J("           was already in, leaving a clean socket, and drops into the notch")
J("           that has been open since the third second. The wall settles. */")
J(f'        tl.to("#slab-commit", {{ x: 92, duration: 0.42, '
  f'ease: "power2.inOut" }}, {word_at("s17", "submit")});')
J(f'        tl.fromTo("#socket", {{ autoAlpha: 0 }}, {{ autoAlpha: 1, '
  f'duration: 0.3 }}, {round(word_at("s17", "submit") + 0.3, 3)});')
J(f'        tl.to("#slab-commit", {{ y: {cy(0) - cy(7)}, duration: 0.8, '
  f'ease: "power2.in" }}, {word_at("s17", "first")});')
J(f'        tl.to("#slab-commit", {{ x: 0, duration: 0.34, '
  f'ease: "power3.out" }}, {round(word_at("s17", "first") + 0.8, 3)});')
J(f'        tl.to("#notch", {{ autoAlpha: 0, duration: 0.25 }}, '
  f'{round(word_at("s17", "first") + 0.9, 3)});')
# CONCEPT.md asks for the whole wall to settle a few pixels onto the seated
# slab. A whole-object nudge moves every pixel on frame, which check_pace's
# carrier-drift reads as the frame being thrown away and redrawn — the exact
# opposite of what a settling wall means. The load transfer is drawn instead:
# the plinth takes the weight and inks up. One cued resolve, no motion on
# settled content, no second subtraction.
J(f'        tl.to("#plinth", {{ backgroundColor: "rgba(51,147,214,0.62)", '
  f'duration: 0.5, ease: "power2.out" }}, '
  f'{round(word_at("s17", "doing"), 3)});')
J("")
J("        /* s18 — three faint slabs queue in the scaffold and stay unfilled;")
J("           the rail caps at the top of the built mass. */")
J('        tl.fromTo(".queue", { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, '
  'duration: 0.5, ease: "power3.out", stagger: 0.14 }, '
  f'{word_at("s18", "activities")});')
J('        tl.fromTo("#rail-cap", { autoAlpha: 0, scaleX: 0.2 }, '
  '{ autoAlpha: 1, scaleX: 1, duration: 0.4, ease: "power3.out" }, '
  f'{word_at("s18", "milestones")});')
J("")
J('        window.__timelines["wall"] = tl;')

TIMELINE = "\n".join(js)


# ---------------------------------------------------------------------------
CSS = f"""
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
      #root {{
        position: relative;
        width: 1920px;
        height: 1080px;
        font-family: "Proxima Nova", sans-serif;
      }}
      #root span,
      #root div,
      #root p,
      #root h1,
      #root h2 {{
        box-sizing: border-box;
      }}
      #wall-body {{
        position: absolute;
        inset: 0;
      }}
      #ghost .gh {{
        position: absolute;
        border: 2px solid rgba(51, 147, 214, 0.85);
        border-radius: 5px;
        background: rgba(51, 147, 214, 0.04);
      }}
      #plinth {{
        position: absolute;
        height: 30px;
        border-radius: 4px;
        background: rgba(51, 147, 214, 0.34);
      }}
      #notch {{
        position: absolute;
        border: 2px dashed rgba(234, 171, 45, 0.62);
        border-radius: 5px;
        background: rgba(10, 30, 47, 0.55);
      }}
      #socket {{
        position: absolute;
        border: 2px dashed rgba(255, 255, 255, 0.34);
        border-radius: 5px;
        background: rgba(10, 30, 47, 0.7);
        opacity: 0;
      }}
      .slab {{
        position: absolute;
        z-index: 3;
        border-radius: 5px;
        background: {BLUE};
        display: flex;
        align-items: center;
        justify-content: center;
      }}
      .slab-hatched {{
        background: rgba(51, 147, 214, 0.9);
      }}
      .hatch {{
        position: absolute;
        inset: 0;
        border-radius: 5px;
        border: 2px solid rgba(51, 147, 214, 0.9);
        background: repeating-linear-gradient(
          -45deg,
          rgba(51, 147, 214, 0.55) 0px,
          rgba(51, 147, 214, 0.55) 5px,
          rgba(10, 30, 47, 0.96) 5px,
          rgba(10, 30, 47, 0.96) 13px
        );
      }}
      .slab-commit {{
        background: rgba(10, 30, 47, 0.9);
        border: 3px solid {GOLD};
        z-index: 6;
      }}
      .score {{
        position: absolute;
        left: 26px;
        top: 24px;
        width: 150px;
        height: 4px;
        border-radius: 2px;
        background: rgba(234, 171, 45, 0.85);
      }}
      .score.s2 {{
        top: 36px;
        width: 118px;
      }}
      .score.s3 {{
        top: 48px;
        width: 140px;
      }}
      .gl {{
        position: relative;
        display: block;
      }}
      .gl-late {{
        display: block;
      }}
      .gl-dot {{
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: rgba(10, 30, 47, 0.82);
      }}
      .gl-arc {{
        width: 26px;
        height: 13px;
        border: 5px solid rgba(10, 30, 47, 0.82);
        border-bottom: 0;
        border-radius: 26px 26px 0 0;
      }}
      .gl-nib {{
        width: 0;
        height: 0;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-bottom: 18px solid rgba(10, 30, 47, 0.82);
      }}
      #band-ring {{
        position: absolute;
        border: 3px solid {GOLD};
        border-radius: 9px;
        opacity: 0;
      }}
      .win {{
        position: absolute;
        border: 4px solid rgba(51, 147, 214, 0.95);
        border-radius: 5px;
        background: rgba(10, 30, 47, 0.92);
        display: flex;
        align-items: center;
        justify-content: center;
      }}
      .win-label {{
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.82);
        text-align: center;
      }}
      .sill {{
        position: absolute;
        width: 26px;
        height: 9px;
        border-radius: 2px;
        background: {GOLD};
      }}
      .queue {{
        position: absolute;
        border: 2px dashed rgba(51, 147, 214, 0.5);
        border-radius: 5px;
      }}
      #rail {{
        position: absolute;
        border-radius: 5px;
        background: rgba(51, 147, 214, 0.24);
      }}
      #rail-ink {{
        position: absolute;
        height: 0;
        border-radius: 5px;
        background: rgba(51, 147, 214, 0.95);
        transform: translateY(-100%);
      }}
      .tick {{
        position: absolute;
        width: 30px;
        height: 4px;
        border-radius: 2px;
        background: rgba(255, 255, 255, 0.34);
      }}
      #rail-cap {{
        position: absolute;
        width: 32px;
        height: 6px;
        border-radius: 3px;
        background: {GOLD};
        opacity: 0;
      }}
      /* The two feeds run UNDER the courses (z below .slab): at s15 they cross
         open scaffold into the commitment slab, and at s16 the course closes
         over them. Occlusion by new material, never a second subtraction. */
      .supply {{
        position: absolute;
        z-index: 2;
        height: 4px;
        border-radius: 2px;
        background: rgba(234, 171, 45, 0.8);
      }}
      #supply-a {{
        left: {sx(0) - 4}px;
        top: {cy(7) + 22}px;
        width: {sx(3) - sx(0) + 4}px;
      }}
      #supply-b {{
        left: {sx(0) - 4}px;
        top: {cy(7) + 50}px;
        width: {sx(3) - sx(0) + 4}px;
      }}
      /* The sight-arm is a COMPACT instrument clamped to the wall's left
         edge — short bars, so it reads as a tool mounted on the object and
         never as a scratch drawn across the finished face. */
      #sight-arm {{
        position: absolute;
        z-index: 7;
        left: {WALL_X - 22}px;
        top: {cy(5) + 30}px;
        width: 190px;
        height: 12px;
        opacity: 0;
      }}
      .arm-hinge {{
        position: absolute;
        left: 0;
        top: -8px;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 4px solid {GOLD};
        background: rgba(10, 30, 47, 0.95);
      }}
      .arm-bar {{
        position: absolute;
        left: 13px;
        top: 4px;
        width: 172px;
        height: 5px;
        border-radius: 3px;
        background: rgba(234, 171, 45, 0.9);
        transform-origin: 0% 50%;
      }}
      .arm-a {{
        transform: rotate(-12deg);
      }}
      .arm-b {{
        transform: rotate(-46deg);
      }}
      .arm-fan {{
        position: absolute;
        left: 13px;
        top: -58px;
        width: 134px;
        height: 134px;
        border-radius: 50%;
        border: 3px dashed rgba(234, 171, 45, 0.34);
        clip-path: polygon(50% 50%, 100% 10%, 100% 62%);
      }}
      /* The help tether enters from the frame margin, in the gutter LEFT of
         the wall, and clamps onto the wall's side. It is never drawn on the
         face, where it would vanish into the slabs. */
      #tether {{
        position: absolute;
        z-index: 7;
        left: {WALL_X - 118}px;
        top: {cy(3) + 12}px;
        width: 130px;
        height: 268px;
        opacity: 0;
      }}
      .teth-clamp {{
        position: absolute;
        right: 0;
        top: 0;
        width: 30px;
        height: 40px;
        border-radius: 5px;
        border: 3px solid rgba(51, 147, 214, 0.95);
        background: rgba(10, 30, 47, 0.95);
      }}
      .teth-line {{
        position: absolute;
        left: 22px;
        top: 18px;
        width: 76px;
        height: 5px;
        border-radius: 3px;
        background: rgba(51, 147, 214, 0.75);
      }}
      .teth-end {{
        position: absolute;
        left: 4px;
        bottom: 0;
        width: 36px;
        height: 36px;
        border-radius: 7px;
        border: 4px solid rgba(51, 147, 214, 0.85);
        background: rgba(10, 30, 47, 0.95);
      }}
      .teth-drop {{
        position: absolute;
        left: 22px;
        top: 18px;
        width: 5px;
        height: 214px;
        border-radius: 3px;
        background: rgba(51, 147, 214, 0.75);
      }}

      .say {{
        position: absolute;
        left: {COPY_X}px;
        top: {COPY_Y}px;
        width: {COPY_W}px;
        opacity: 0;
        visibility: hidden;
      }}
      .kicker {{
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: {BLUE};
        margin-bottom: 22px;
      }}
      .head {{
        font-size: 54px;
        font-weight: 900;
        line-height: 1.08;
        letter-spacing: -0.005em;
        color: rgba(255, 255, 255, 0.96);
      }}
      .say-title .head {{
        font-size: 88px;
        line-height: 1.03;
      }}
      .stmt {{
        margin-top: 26px;
        font-size: 42px;
        font-weight: 400;
        line-height: 1.34;
        color: rgba(255, 255, 255, 0.76);
      }}
      .list {{
        margin-top: 28px;
      }}
      .li {{
        position: relative;
        padding-left: 34px;
        margin-bottom: 16px;
        font-size: 42px;
        font-weight: 400;
        line-height: 1.3;
        color: rgba(255, 255, 255, 0.82);
      }}
      .li::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 22px;
        width: 16px;
        height: 6px;
        border-radius: 3px;
        background: {GOLD};
      }}
      .cmp {{
        margin-top: 28px;
        display: flex;
        gap: 24px;
      }}
      .card {{
        width: 306px;
        padding: 22px 20px;
        border-radius: 12px;
        border: 2px solid rgba(51, 147, 214, 0.55);
        background: rgba(13, 36, 55, 0.75);
        font-size: 40px;
        font-weight: 700;
        line-height: 1.2;
        color: rgba(255, 255, 255, 0.9);
      }}
"""

DOC = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="wall" data-width="1920" data-height="1080">
      <div id="wall-body">
{WALL}
      </div>

{COPY_HTML}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      (function () {{
{TIMELINE}
      }})();
    </script>
  </body>
</html>
"""

(WS / "compositions").mkdir(exist_ok=True)
(WS / "compositions" / "wall.html").write_text(DOC, encoding="utf-8")

# --- index.html -------------------------------------------------------------
audio_rows = "\n".join(
    f'      <audio id="vo-{r["id"]}" src="assets/voice/{r["id"]}.wav" '
    f'data-start="{r["audio_start"]}" data-duration="{r["audio_dur"]}" '
    f'data-track-index="10" data-volume="1"></audio>'
    for r in T["rows"])

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
      #stage-bg {{
        position: absolute;
        inset: 0;
        background: #0a1e2f;
      }}
      #stage-glow {{
        position: absolute;
        left: 1320px;
        top: 640px;
        width: 1700px;
        height: 1400px;
        margin: -700px 0 0 -850px;
        background: radial-gradient(
          ellipse at center,
          rgba(51, 147, 214, 0.16) 0%,
          rgba(13, 36, 55, 0.5) 46%,
          rgba(10, 30, 47, 0) 74%
        );
        will-change: transform;
      }}
      #stage-vignette {{
        position: absolute;
        inset: 0;
        background: radial-gradient(
          ellipse at 50% 50%,
          rgba(10, 30, 47, 0) 55%,
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
        color: rgba(255, 255, 255, 0.66);
      }}

      #root > div[data-composition-src] {{
        position: absolute;
        inset: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
      <div id="stage-bg">
        <div id="stage-glow"></div>
        <div id="stage-vignette"></div>
      </div>

      <div id="chrome">
        <span id="chrome-mark"></span>
        <span id="chrome-text">Early Career Boost</span>
      </div>

      <!-- ONE carrying object for the whole runtime: the foundation wall,
           laid course by course inside its own ghost scaffold, with the base
           notch open from s01 to s17. See design.md. -->
      <div id="stage-wall" data-composition-id="wall" data-composition-src="compositions/wall.html" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-width="1920" data-height="1080"></div>

      <!-- Narration — HeyGen starfish, Oxana (tokens.yml voice.voice_id).
           One element per beat at GLOBAL time; every number below is
           timing.json's, computed by make_timing.py from the real wavs. -->
{audio_rows}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});

      // The banner settles once, then never moves again.
      tl.fromTo("#chrome", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.7, ease: "power3.out" }}, 0.25);

      // One shared ambient breath, on the background GLOW only — never on
      // content. Finite legs sized to the runtime.
      tl.fromTo(
        "#stage-glow",
        {{ scale: 1, opacity: 0.96 }},
        {{ scale: 1.028, opacity: 1, duration: 9, ease: "sine.inOut", yoyo: true, repeat: {int(TOTAL // 9)} }}, /* motion-allow: background depth-drift on a non-content layer; the design contract sanctions ambient breath on the background glow only */
        0,
      );

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(WS / "index.html").write_text(INDEX, encoding="utf-8")

mids = [round(r["vis_start"] + r["vis_dur"] / 2, 2) for r in T["rows"]]
(WS / "qa").mkdir(exist_ok=True)
(WS / "qa" / "beat-midpoints.txt").write_text(",".join(str(m) for m in mids) + "\n")
print("wrote compositions/wall.html + index.html")
print("root duration", TOTAL)
print("midpoints", ",".join(str(m) for m in mids))
