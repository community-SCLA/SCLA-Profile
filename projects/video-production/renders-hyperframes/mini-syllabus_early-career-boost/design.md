# design.md — brand truth for `mini-syllabus_early-career-boost`

Design source of record for this one video. Brand values are LOADED from this
workspace's own `tokens.yml` copy (colors, type floors, spacing, the pinned
Oxana voice); nothing here restates a hex value that a gate also reads.

Lesson: `lesson-scripts/early-career-boost/ready/mini-syllabus_early-career-boost.txt`.
Lane: freeform (agent-native) — no templates, no `scenes.json`, no compiler.
Judge-selected concept: `renders-hyperframes/_concepts/mini-syllabus_early-career-boost/CONCEPT.md`
(Pitch B, "the foundation wall", with Pitch A's single subtraction grafted into
the payoff). Sharpened here only against the real timings; not replaced.

## Concept angle

> A career foundation wall laid course by course inside a ghosted scaffold,
> with **one block-sized notch left open in its base from the first beat until
> the last** — and the slab the learner writes on the working face is lifted
> back OUT of the wall and seated into that notch.

**Persistence: beats s01 → s18, i.e. 100% of the ~99s runtime.** The plinth,
the empty notch and the ghost scaffold are all on screen in the title beat, so
the object is never introduced mid-video. Every later beat is another way of
reading the same wall: a course laid, a face acquired, a band turned over, an
opening cut, an appendage clipped on, a slab removed.

**The rule, stated out loud:** *if an element cannot be justified as another
way of reading the same wall, it does not exist.* There is no second
illustration on any frame. Copy holds the left column; the wall holds the
right. Nothing is parked beside a row of text.

## What each beat asks the wall to say

| Beat | What the wall does | Script line it comes from |
| --- | --- | --- |
| s01 | plinth, the empty notch, the ghost scaffold — nothing built | title card |
| s02 | the first two slabs land in course 0 | "We're really glad you're here" |
| s03 | course 0 completes — the starting point is a floor, not a dot | "this is your starting point" |
| s04 | course 1 completes → **skyline: bottom third** | "each step builds your career foundation" |
| s05 | the graduated rail arrives, inked to the built height, faint above | "your progress bar always shows where you are and what's ahead" |
| s06 | course 2 lands **and every slab already placed acquires its glyph face** (TRANSFORM 1) | "click-through activities, short reflections, and uploads" |
| s07 | course 3; the hinged **sight-arm** clips on at the wall's left edge and fans over the unbuilt ghost | "the Career Mapping Tool to explore different pathways" |
| s08 | course 4; the **help tether** clips in from the frame margin and never leaves → **skyline: mid-frame** | "help is one click away in the hashtag questionsupport channel" |
| s09 | the sight-arm re-aims at the empty scaffold above the build line | "Now — what you'll actually learn" |
| s10 | course 5 lands **hatched and hollow** — a new kind of element | "starts with the right mindset" |
| s11 | the hatched band is ringed and **turned over to solid in place**, positions unchanged (TRANSFORM 2) | "limiting beliefs … a growth mindset instead" |
| s12 | course 6 sets its first **open window frame** — the first void in the piece | "What makes a dream job today?" |
| s13 | window two | "Which skills matter in an AI-driven world?" |
| s14 | window three, with **three notches cut along its sill** → **skyline: two-thirds** | "networking, building a résumé, and searching…" |
| s15 | the **commitment slab** is scored on the working course from two feeds at once | "in your Workbook, or with the AI-Career Commitment tool" |
| s16 | both feeds ink; course 7 closes around the commitment slab | "Try both for the practice" |
| s17 | the commitment slab **lifts out**, leaving a clean socket, travels down the outside and **seats into the base notch**; the plinth inks up as it takes the load | "You'll submit it as your first step" |
| s18 | the rail completes to the top of the built mass; three faint outlined slabs queue in the ghost and stay unfilled → **skyline: settled full** | "activities, milestones, and skills that move you toward your goals" |

## The accumulation contract (measured, not asserted)

1. **Mass, monotonically.** Courses only ever increase. Solid skyline at the
   four milestone stills: **y≈748 → y≈508 → y≈428 → y≈268** (top edge of the
   solid mass, canvas y). Four different pictures before a word is read.
2. **Kinds of element.** solid slab → three glyph faces → hatched/hollow slab →
   open void. The on-frame vocabulary grows and never resets.
3. **Silhouette, permanently.** The sight-arm (s07) and the help tether (s08)
   arrive once each, change the outline, and are in every later frame.
4. **Material already on screen, re-read.** s06 gives slabs laid plain in act 1
   their glyph faces where they already sit; s11 turns the hatched band over
   without moving it. Neither is reachable by adding an element.
5. **One hole closes, one hole opens.** The base notch is open from s01 and
   closed exactly once, at s17. The socket in course 7 opens exactly once, at
   s17, and stays open.

Counts drawn on frame are only the counts the narration speaks: three ways of
working, three real questions, three moves. The ghost scaffold fades toward the
top so its courses can never be counted, and nothing is captioned with a number.

## Palette

Every value comes from `tokens.yml colors:` (loaded by `check_brand.py`, which
fails any literal that is not one of them at any alpha).

| Role | Token | Use |
| --- | --- | --- |
| Page ground | `navy-deep` | full-bleed background CHILD, never the root |
| Ground lift | `navy` | radial lift behind the wall, plinth body, void interiors |
| Foreground | `paper` | display type, headings |
| Body / secondary | `paper` at ~0.76 alpha | statements and list copy on navy |
| Structure | `blue` | slabs, ghost lattice, rail, joints, sight-arm, tether |
| Focus accent | `gold` | **rationed**: the one region the narration is naming right now, the notch hairline, the commitment slab |

**One accent region per beat.** Everything already placed drops to quiet blue
and is pixel-static thereafter — no wobble, no keep-alive, no re-marking.

## Type

Proxima Nova only, the vendored `woff2` 400/700/900 in `assets/fonts/`.
Hierarchy is weight, size and colour — never a second family.

| Role | Size | Weight |
| --- | --- | --- |
| Lesson title (title card) | 104px | 900 |
| Beat heading | 62px | 900 |
| Statement / list copy | 42px | 400 |
| Eyebrow / kicker / chip | 26px | 700, uppercase, 0.14em |

Body floor is the tokens.yml floor (40px); nothing viewer-read is set at it.
Headings carry `data-role="heading"`, are Title Case and take no terminal
period. Declared lists carry `data-role="list"`, comparisons `data-role="compare"`.

## Frame

- 1920×1080. All content lives inside x 120…1800, y 120…955 — clear of the
  safe-area (72), frame-padding (120) and content-bottom (960) bands that
  `check_ink.py` grades on real pixels.
- Copy column: x 120…760. Wall column: x 900…1740. They never share a band, so
  there is no text-over-text seam for the layout inspector to find.
- The wall's baseline plinth sits at y 900; courses are 72px on an 80px pitch.
- The graduated rail runs at x 1766…1774, from y 900 to y 188.
- The program eyebrow is the only element in the top keep-out, inside the
  `chrome-regions` rectangle `tokens.yml` declares by name.

## Motion

- Entrances only: 0.35–0.7s, `power3.out` / `back.out(1.4)`, cued to the word
  timestamp that earns them. Nothing settled re-animates in place.
- The wall is only ever *extended, re-faced, opened or unloaded* — never rebuilt.
- One ambient breath, on the background glow alone, declared inline with
  `/* motion-allow: … */`.

## Deviation from CONCEPT.md, and why

Two, both forced by the concept's own tests:

1. CONCEPT.md put the three window frames in "the top course" and the
   commitment slab in the same course. Held literally that gives the 75% and
   100% stills the same solid skyline, which the concept's own skyline test
   forbids. Sharpened against the real 18-beat timing: the windows take course
   6 and the working course is 7, so the solid skyline still rises between the
   two milestones (428 → 268).
2. CONCEPT.md asks for the whole wall to settle a few pixels onto the seated
   slab. A whole-object nudge moves every pixel on frame; measured, that one
   beat pair alone read 15.9% inter-beat churn and pushed the build's mean to
   6.74% against `check_pace.py`'s 6.0% carrier-drift ceiling — i.e. the
   settle made the persisting object score as a frame being thrown away and
   redrawn. The load transfer is drawn instead: the plinth inks up as it takes
   the weight. Mean churn with the change: **5.70%**.

Everything else in the contract is kept as written.

## Revision — 2026-08-05, post-render stagnation

The first render passed every pre-render gate and then failed `verify_render`:
the frame held pixel-static for 6.0s inside s03 while the voice kept talking,
with 3.5s holds inside s14 and s18. The cause was structural, not decorative —
each of those beats said everything it had to say inside its first second and
then had nothing left arriving. **The fix is content, never keep-alive motion:
nothing that had already entered was touched.**

What now arrives in the back half of each affected beat:

| Beat | Second-half arrival | Word it is cued to |
| --- | --- | --- |
| s03 | the **starting datum** struck along the bed joint above course 0 | "this is your starting point" |
| s03 | the **build envelope** — the scaffold's two extents, one per side | "part of your broader … journey" |
| s04 | course 1 laid slab by slab across the sentence (spacing only) | "as you move through this track…" |
| s05 | the **hollow run of the rail** above the ink head | "…and what's ahead" |
| s08 | the tether **pays its line out** to the channel | "hashtag questionsupport channel" |
| s14 | the three sill notches cut one per named move | "networking" / "résumé" / "searching" |
| s15 | one supply feed per source, not both at once | "Workbook" / "AI-Career Commitment tool" |
| s18 | one queued slab per named thing | "activities" / "milestones" / "skills" |
| s18 | the **goal line** capping the envelope, and one last opening left on it | "toward" / "your goals" |

Three long beats (s03, s05, s14) also hand their statement line over on its own
word instead of with the heading. The wall now carries **two datums** — the
starting line struck at s03 and the goal line struck at s18 — which is the same
one-hole-closes-one-hole-opens symmetry the base notch and the socket already
had. Longest remaining hold anywhere in the cut: **2.7s**.

Rejected during this pass: re-aiming the sight-arm onto the window row at s14.
It is a legal move (the instrument re-positions; nothing settled is re-marked),
but at every angle that clears the beat's own words its lower bar is drawn
straight through the first window's label.

## Measured against the contract

| Check | Result |
| --- | --- |
| beats / pace | 18 beats, 97.43s, **11.08 beats/min**, median 5.4s, 19% of runtime in >8s beats |
| carrier drift | **5.77%** mean inter-beat churn (ceiling 6.0%; approved reference 3.34%) |
| longest hold | **2.7s** between visual arrivals (violation floor 6.0s, warn 3.0s) |
| twin beats | 0 of 17 pairs |
| pixel bounds | 18/18 stills clean on safe-area, frame-padding and content-bottom |
| contrast | 25/25 text checks pass WCAG AA |
