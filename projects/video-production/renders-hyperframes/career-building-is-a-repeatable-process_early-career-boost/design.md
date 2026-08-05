# design.md — brand truth for `career-building-is-a-repeatable-process_early-career-boost`

Design source of record for this ONE video. Every normative number is LOADED
from this workspace's own `tokens.yml` copy (palette, type floors, spacing,
safe-area, the pinned Oxana voice); nothing here restates a hex value a gate
also reads.

Lesson script (verbatim source for every beat):
`lesson-scripts/early-career-boost/ready/career-building-is-a-repeatable-process_early-career-boost.txt`
Lane: freeform (agent-native) — the HTML is the authored artifact.
Starting contract: `_concepts/career-building-is-a-repeatable-process_early-career-boost/CONCEPT.md`
Taste bracket: `design-system/docs/taste.md`.

## Why this build exists

A previous cut of this exact lesson passed every deterministic gate including
the new pace gates and was rejected by the owner as **visually thin**: a
headline plus a static six-dot circle on empty navy for 42 beats. The circle
persisted and never earned anything. That cut is pinned at
`renders-hyperframes/_reference/…_2026-08-05-thin-carrier-backup/` as the
negative reference. Two rules fall out of it and are held here:

1. The carrying object must **gain** something almost every beat — stones,
   flags, filled slots, a corrected line, spokes, ticks, parallel paths.
2. **The six-station loop does not exist on screen before the payoff.** It is
   what the journey turns out to have been made of, not the opening wallpaper.

## Concept angle

> **A stone path laid decision by decision across the whole canvas — carried
> from the title card to the last frame — which near the end surrenders the
> six-station wheel that turns out to have been pressing it all along.**

**Persistence: beats s02 → s38, i.e. ~97% of the runtime** (s01 is the title
card, where the path's *cause* — the abandoned boulder — is already on frame).
The path is never cleared, never rebuilt and never left. Every element is one
of exactly four things: a **stone laid on the route**, a **mark attached to a
stone** (flag, tick, ring, caption), the **route line itself**, or the **wheel
that presses the route**.

**The rule, stated out loud:** *if an element cannot be justified as another
way of reading the same path, it does not exist.* There is no second
illustration, no icon beside a label, and no decorative object anywhere.

## What accumulates (the anti-thin contract)

| Quantity | start | end |
| --- | --- | --- |
| stones laid on the route | 0 | 18 (+1 pressed by the wheel) |
| abandoned boulder off-trail | bright | dim, struck through, never removed |
| milestone flags | 0 | 3 |
| plan slots | 0 outlines | 4 outlines → 4 filled |
| superseded stretch kept as faded history | none | 3 stones, visible |
| corrected (gold) run | none | 3 stones on a new line |
| wheel spokes | 0 | 6 |
| station ticks on the walked path | 0 | 6, each named |
| paths on screen | 1 | 4 (3 fainter, unlabelled) |
| gold "this week" stone | none | 1, at the leading edge |

The closing frame could not have been drawn at 0:10. Nothing re-animates in
place; every change is an addition, a one-shot dim, or a one-shot re-colour of
a stretch that stays exactly where it was laid.

## Milestone frames (the accumulation contract)

Percentages are of the computed runtime and are re-stated against the real
`timing.json` after synthesis (see "Computed timings" at the foot of this file).

- **~25% — the recap flags.** Boulder dim and struck off-trail at frame left.
  Nine stones walked across the lower-left third. Three flag poles of rising
  height carry the module gains: strengths/values/energy · five criteria ·
  Career Purpose Statement. The walked stretch is gold — the progress the
  narration names — and a foundation slab sits under it.
- **~50% — the plan slots.** The path has reached mid-canvas. Ahead of the
  leading edge, four **empty dashed outlines** wait on the route, each named:
  direction · skills · people · ninety days. Behind, everything from 25% is
  untouched. The frame now reads left-to-right as *history → here → plan*.
- **~68% — the corrected line.** One already-laid stretch is re-laid: the
  superseded stones stay visible as faded history and a new gold run bends
  away above them. Nothing is erased — the path now records a change of mind.
- **~75% — the wheel.** A six-station wheel assembles at the top right, one
  spoke per beat, and as each spoke lands a gold **tick with its station name**
  is added to the stretch of path that spoke explains (Clarify · Widen ·
  Criteria · Test · Decide · Review). The tool was inside the journey all along.
- **100% — the pull-back.** Three fainter parallel paths fade in around yours,
  each starting further back. The completed wheel rolls one stone forward and
  presses a new stone, which glows gold: the step to take this week.

## Payoff beat

The wheel assembly (s26 → s31), re-read by the closing pull-back (s33 → s38):
your one path becomes one of many, all pressed by the same wheel. This is the
deliberate rebuttal of the rejected-thin cut, which *opened* with the six-dot
loop and never earned it. Here the loop does not exist before s26.

## The frame

1920×1080. Nothing content-bearing crosses the safe area, the frame padding or
the content-bottom band — all three LOADED from `tokens.yml` and graded on real
pixels by `check_ink.py`.

| Band | Extent | What lives there |
| --- | --- | --- |
| Program eyebrow | x 130–560, y 64–96 | the one element in the top keep-out, inside the `chrome-regions` rectangle `tokens.yml` declares by name |
| Headline band | x 130–1210, y 140–280 | the beat heading (max 2 lines) |
| Sub-line band | x 130–1210, y 300–400 | one optional body line under the heading |
| Path world | x 150–1790, y 150–950 | the SVG: route, stones, boulder, flags, slots, ticks, wheel, parallel paths |

The headline block is capped at 1080px wide precisely so it can never reach the
wheel column (x ≥ 1387).

## The route (authored geometry, one cubic)

Cubic Bézier `M 200,900 C 640,912 1010,640 1440,478`, arc length 1321px,
sampled at 18 evenly-spaced stone seats:

```
 1 (200,900)   2 (278,899)   3 (356,893)   4 (432,881)   5 (508,865)
 6 (583,844)   7 (657,820)   8 (730,793)   9 (802,764)  10 (873,733)
11 (944,700)  12 (1014,667) 13 (1085,634) 14 (1155,601) 15 (1225,568)
16 (1296,537) 17 (1368,506) 18 (1440,478)
```

Seats 11–14 are the four plan slots. Seats 16–18 are the stretch that gets
superseded at ~68%; the corrected gold run replaces them at
(1288,480) · (1352,424) · (1418,380). The wheel is centred at (1545,330),
r 158 — clear of every stone by ≥ 30px and clear of the headline block by
177px. The 19th stone, pressed by the wheel at the end, sits at (1500,352)
on the corrected line's continuation.

Stone sizes carry "some small, some major": major seats are 56×34px rounded
rects, minor seats 38×24px, both rotated to the route tangent.

## Palette

Every value comes from `tokens.yml colors:` (loaded by `check_brand.py`, which
fails any literal that is not one of them at any alpha).

| Role | Token | Use |
| --- | --- | --- |
| Page ground | `navy-deep` | full-bleed background child, never the root |
| Ground lift | `navy` | radial lift behind the route |
| Foreground | `paper` | display type, stone faces |
| Body / secondary | `paper` at ~0.78 alpha | body copy on navy |
| Structure | `blue` | route line, unwalked stones, flag poles, wheel rim |
| Focus accent | `gold` | **rationed**: the walked/progress stretch, the corrected run, the six station ticks, the final "this week" stone |
| History | `muted-video` | the abandoned boulder and the superseded stretch |

Gold never decorates. It only ever marks *what the path is pointing at now* or
*what the path has earned*.

## Type

Proxima Nova only, the vendored woff2 400/700/900 in `assets/fonts/`.
Hierarchy is weight, size and colour — never a second family.

| Role | Size | Weight |
| --- | --- | --- |
| Lesson title (title card) | 104px | 900 |
| Beat heading | 60px | 900 |
| Sub-line / body | 40px | 400 |
| Station + milestone label | 26px | 700, uppercase, 0.14em |
| Program eyebrow | 26px | 700, uppercase, 0.16em |

Body floor is the tokens.yml floor (40px); the only type below it is the
label class, whose own floor is 20px. Headings are `data-role="heading"`,
Title Case, no terminal period.

## Motion

- **A beat's accumulation is spread ACROSS the beat, on its own word onsets.**
  Every cue time in `compositions/path.html` other than the beat starts is a
  narration word onset read from `audio_meta.json`'s per-clip word timestamps,
  offset by that clip's `audio_start` in `timing.json`. The first cut landed
  each beat's whole gain in its first second and then held: nine windows of
  4.5–7.5s went pixel-static while the voice kept speaking, which
  `preflight.py`'s one-still-per-beat grid cannot see and `batch-precheck.sh`'s
  ~1.5s / 123-still grid blocks on (`check_diversity` `static-span`). The fix is
  AUTHORING — a flag now draws its pole, lands its pennant and gains its label
  on three different words; a sub-line arrives clause by clause; four captions
  arrive on the four things the sentence names. **No idle motion was added.**
- **The seam between two beats is ATOMIC.** Two constraints meet at every
  heading change and only one shape satisfies both: the heading band may never
  be empty (a 0.04s gap between the outgoing exit and the incoming entrance
  produced a headless frame at 29.25s and 174.75s), and two headings may never
  be on screen together (`check_layout` reads BOXES, not opacity, so any
  cross-fade is a fatal `content_overlap` and the band is far too shallow to
  separate two 2-line headings in y). So the outgoing heading is cut and the
  incoming one lit on the SAME instant, and only the 26px settle animates.
  Both halves are `tl.set()`: a zero-duration set restores the value it found
  when the playhead scrubs back, so seeking is exact — a `fromTo` whose FROM
  state is `autoAlpha: 1` is not an option, because gsap renders a fromTo
  immediately on build and that put all 37 headings on frame at t=0.
- **Every label knocks the line out behind itself** (`paint-order: stroke fill`
  over a `navy-deep` stroke). A line running through a label's glyphs reads as
  a strike-through — and on this frame a gold slash is used *deliberately* to
  cancel "one big right choice", so an accidental crossing carries exactly the
  wrong meaning. The dashed other-journeys were re-routed out of the label
  field entirely (lanes solved numerically against every label box, the rolled
  wheel and the frame bounds); the flag poles cannot be moved off their own
  stones, so they now pass visibly BEHIND the words, which reads as depth.
- Entrances only: 0.4–0.7s, `power3.out` / `back.out(1.4)`, cued to a word.
- Settled content never re-animates in place. The route is only ever
  *extended, marked, re-coloured or dimmed* — never rebuilt, never wobbled.
- Spokes draw additively (`stroke-dasharray`), one pass, then static — never
  by lifting marks off the settled stones.
- One ambient breath, on the background glow alone, declared inline with
  `/* motion-allow: … */`.

## Beat table — what the path is asked to say

Every heading is a compression of that beat's own narration; no on-frame line
introduces a fact, a count or a sequence claim the narration does not make.

| Beat | Heading | What the path gains |
| --- | --- | --- |
| s01 | Career Building Is a Repeatable Process | title card; the bright boulder — "one big right choice" — alone at frame left |
| s02 | Careers Do Not Work That Way | boulder dims and is struck off-trail; seats 1–2 laid, route line begins |
| s03 | A Series of Decisions | seats 3–5 laid, mixed major/minor sizes |
| s04 | What Those Decisions Shape | four captions climb off the walked stones: skills, confidence, relationships, opportunities |
| s05 | Not a Perfect Answer | captions clear; seats 6–7 laid; a gold strike lands on the boulder |
| s06 | It Gave You a Process | seats 8–9 laid; the leading-edge marker takes its place |
| s07 | Look Back at Where You Started | the origin seat gains a ring and its label |
| s08 | Module 1 | flag 1 rises from seat 3 |
| s09 | Module 2 | flag 2 rises from seat 6, taller |
| s10 | Module 3 | flag 3 rises from seat 9, tallest |
| s11 | That Is Genuine Progress | the whole walked stretch turns gold |
| s12 | Things You Build | a foundation slab appears under the walked stretch |
| s13 | Go Back to What You Wrote | the origin ring gains an outer dashed ring |
| s14 | Notice What Has Shifted | two gold chevrons appear on the early stretch |
| s15 | A Clearer Question Moves You Forward | seat 10 laid; the leading edge advances |
| s16 | A Practical Plan | the route ahead appears as a dashed guide |
| s17 | A Useful Plan Is Not Elaborate | four empty dashed slots appear on seats 11–14 |
| s18 | Specific Enough to Guide Action | the four slots gain a bracket |
| s19 | Deciding a Few Things | the four slots fill and are named, one per phrase |
| s20 | Meant to Be Reused | the dashed guide goes solid through the filled slots |
| s21 | Not a One-Time Assignment | the foundation slab extends the full walked length |
| s22 | Your Map Is Not Frozen | a faint alternate line leaves seat 15 |
| s23 | Your Direction Can and Will Change | the corrected gold run is laid; seats 16–18 dim to history |
| s24 | Not a Sign You Did Something Wrong | the faded stretch keeps a marker — kept, not erased |
| s25 | You Now Own a Process | a gold outline traces the whole laid route once |
| s26 | Run the Loop Again | **the wheel appears** — hub and rim only, no spokes |
| s27 | Clarify the Decision | spoke 1; tick + CLARIFY on its stretch |
| s28 | Widen Your Options | spoke 2; tick + WIDEN |
| s29 | Set Your Criteria | spoke 3; tick + CRITERIA |
| s30 | Test Your Biggest Uncertainty | spoke 4; tick + TEST |
| s31 | Decide, Act, and Review | spokes 5 and 6; ticks + DECIDE and REVIEW; the wheel completes |
| s32 | Keep It Where You Will See It | flag 3 brightens to gold and gains a keep marker |
| s33 | Every Professional Is Running This Loop | three fainter parallel paths fade in |
| s34 | They Just Started Earlier | the parallel paths gain earlier origins |
| s35 | So Have You | your own origin gains a gold start marker |
| s36 | Momentum, Not a Perfect Future | the wheel rolls one seat forward and presses stone 19 |
| s37 | The Step You Named for Yourself | stone 19 glows gold |
| s38 | Take It This Week | stone 19 gains its label; the full frame holds |

## Computed timings

From the real clip durations via `make_timing.py` — never hand-tuned.
**38 beats over 184.331s** — 12.37 beats/min, median beat 4.32s, longest 12.46s
(the 40-word plan sentence), 23% of runtime inside beats over 8s. Mean
inter-beat churn over the 38-still grid is **3.14%**, against the
owner-approved reference's 3.34% and the rejected-slow cut's 10.07%: one
object, re-read, never thrown away.

The concept's milestone percentages land where they were promised:

| Milestone | Real time | Beat | The picture |
| --- | --- | --- | --- |
| 25% | 46.1s | s09 *Module 2* | boulder struck off-trail, 9 stones walked, flags 1–2 planted, flag 3 lands 0.6s later |
| 50% | 92.2s | s18 *Specific Enough to Guide Action* | path at mid-canvas, gold walked stretch + foundation behind, four EMPTY plan seats and their name rules ahead |
| 68% | 125.4s | s24 *Not a Sign You Did Something Wrong* | the corrected gold run is laid, the superseded stretch is faded but kept, dotted gold along it |
| 75% | 138.3s | s26 *Run the Loop Again* | **the wheel first exists** — rim and hub only, no spokes, at 135.4s = 73.5% of runtime |
| 100% | 184.3s | s38 *Take It This Week* | everything above, plus six named ticks, six spokes, three fainter journeys, and one gold stone at the leading edge |

Measured accumulation, from `check_ink.py`'s per-frame edge-pixel count: the
frame carries **13,419** ink pixels at beat 2 and **76,199** at beat 36, rising
monotonically across the runtime. The last frame could not have been drawn at
0:10.
