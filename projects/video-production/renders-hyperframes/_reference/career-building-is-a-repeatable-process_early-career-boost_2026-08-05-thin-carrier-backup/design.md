# design.md — brand truth for this composition

Design source of record for `career-building-is-a-repeatable-process_early-career-boost`
(freeform / agent-native lane, `.claude/skills/render-lessons/SKILL.md` →
"Freeform build sequence"). Every normative number comes from the workspace
copy of `tokens.yml` — the gates read that copy. No SCLA scene template
participates in this build: the HTML is the authored artifact.

## Concept angle

> The script's own climax names a five-step loop — Clarify, Widen, Set
> Criteria, Test, Decide/Act/Review — and says to run it again. So the video
> **builds that loop first and reads everything else through it**: the "series
> of small and major decisions" from the opening becomes the loop's track
> being laid down; the three modules become three arcs on the same track; the
> four planning questions become four spokes off the same hub; "reused, not
> frozen" becomes one lap traveled on the same ring; and only then do the five
> named steps light the same five node positions that were waiting empty the
> whole time. The viewer's own next action is a marker that joins that ring
> and comes to rest on it.

**The carrying object is the ring** — a five-node circular track, right of
centre. It is laid down starting at beat **s03** ("built through a series of
decisions") and is on screen, in some form, through the final beat **s37**
(the last frame of the video) — **35 of 37 beats, ~97% of the beat count and
~92% of runtime** (it is absent only for the two-beat cold open, s01–s02,
which is deliberately a single bare point — the myth the ring then replaces).
Nothing added to the frame after s03 is a new object: every later mark is
another way of reading the ring — an arc on it, a spoke off its hub, a lap
around it, a node lighting. If a beat's content cannot be stated as one of
those four operations on the ring, it does not belong on screen. (Rule
stated in full: *if an element cannot be justified as another way of reading
the same object, it does not exist.*)

## Beat plan (acts → the same ring, read four ways)

| Act | Beats | Sub-comp | The ring is… | Text band says |
| --- | --- | --- | --- | --- |
| 1 — The myth | s01–s02 | `opening.html` | absent — one bare point, then it dims | one big right choice |
| 2 — The track lays down | s03–s06 | `opening.html` | born: marks scatter, draw into a 5-node ring, four life-facets pulse in turn, the ring closes as "a process" | a series of decisions → a process |
| 3 — Three arcs | s07–s10 | `build.html` | the SAME ring, now split into three lit arcs, one per module | what you already logged |
| 4 — Progress + the two questions | s11–s15 | `build.html` | the ring pulses as a whole; a faint earlier ring appears beside it and fades; two opposite nodes tag with the two recurring questions | that is genuine progress |
| 5 — Four spokes | s16–s19 | `build.html` | four spokes draw from the hub, one per planning question, timed to their own words | direction · skills · people · actions |
| 6 — One lap | s20–s24 | `loop.html` | a marker travels once all the way around the SAME ring | reused, not frozen |
| 7 — The five steps | s25–s32 | `loop.html` | the five node positions — empty since s03 — light and label in turn; a pin marks the hub | you now own a process |
| 8 — Your lap | s33–s37 | `closing.html` | a second marker ("you") joins the ring at node 1 and comes to rest on node 5 | take it this week |

## Palette (dark — the decision-making register this audience is in)

Every colour literal in the CSS is a `tokens.yml` `colors:` value at some
alpha; nothing else is authored.

| Role | Token | Hex | Use |
| --- | --- | --- | --- |
| Page ground | `navy-deep` | `#0a1e2f` | full-bleed background **child**, never the root itself |
| Ground lift | `navy` | `#0d2437` | radial lift behind the ring, arc fills |
| Foreground | `paper` | `#ffffff` | display type, headings |
| Body / secondary | `paper` @ .78 | `rgba(255,255,255,.78)` | body copy on navy (≈8:1) |
| Structure / label | `blue` | `#3393d6` | eyebrow, rules, unlit nodes/track, spokes at rest |
| Focus accent | `gold` | `#eaab2d` | **one job only**: the node, arc or marker the lesson is pointing at *right now* |

Gold never decorates. If gold is on the frame, it is the current claim.

## Type

Proxima Nova only, vendored `woff2` (400/700/900) from
`design-system/assets/fonts/`, `@font-face`d **inside each sub-composition's
`<template>`**. Every `font-family` stack leads with `'Proxima Nova'`.

| Role | Size | Weight | Tracking |
| --- | --- | --- | --- |
| Display (title card) | 96px | 900 | -0.02em |
| Heading | 68px | 900 | -0.015em |
| Accent line | 52px | 700 | -0.01em |
| Body | 44px | 400 | 0 |
| Node label | 40px | 700 | 0 |
| Eyebrow (label class) | 26px | 700 | 0.16em, uppercase |

The 40px body floor (`tokens.yml typography.min-size.body`) holds. The
eyebrow is the only sub-40px rule and is label class by construction
(uppercase **and** letter-spaced).

Hierarchy is carried by weight, size and colour — house style's serif/sans
pairing is deliberately overridden, because brand truth is Proxima Nova on
every SCLA surface and a serif here would be off-brand.

## Frame

1920×1080. Bands are fixed for the whole runtime so the ring never has to
move to make room for copy:

- **Chrome** — program eyebrow at x 120, inside the declared chrome rectangle
  (`tokens.yml chrome-regions`). Nothing else sits above y 150.
- **Text band** — x 130–980, y 190 → 620. Heading at the top; body / accent
  lines under it.
- **Ring band** — hub at (1340, 580), radius 300px (track), node markers at
  radius 300, labels at radius 400. Ring bounding box roughly x 940–1740,
  y 180–980 — inside the 120px frame padding and the 72px safe area on every
  side, content never below y 960 (`check_ink` grades real pixels).
- Background treatment: navy radial lift behind the ring + a 120px hairline
  grid at 5%. One shared slow breath on the radial lift, finite repeat.

## Motion

- Arrivals are **binary + a whip from below** — `autoAlpha` 0→1 with y 26→0,
  0.4–0.6s `power3.out`. Never a fade used as an arrival.
- Reveals are pinned to real word timestamps out of `audio_meta.json` where a
  beat carries more than one reveal (s04's four facets, s19's four spokes,
  s27–s31's node lights); a single-reveal beat lands at its own
  `timing.json` `vis_start` + a small lead.
- Exits are 0.28s `power2.in` and complete before the replacing element
  begins, so two text blocks never share pixels at any sampled instant.
- Settled content never re-animates in place. The only repeating tween in the
  build is the background radial lift's breath, declared inline where it
  lives with `/* motion-allow: … */`.
- The ring re-sorts by moving/relabelling existing marks (`x`/`y`/colour/
  opacity), never by rebuilding the whole track: the five node positions
  computed in `opening.html` are the same positions every later act lights.
  Because each act is a separate sub-composition file, "the same ring" means
  each file's script recomputes the identical node/track geometry (pure
  index → (x, y) arithmetic, no randomness) and opens on the exact end-state
  the previous act left it in, rather than one literal persisting DOM node —
  the pixels are continuous even though the mount is not.
- Deterministic only: finite repeat counts, no clocks, no randomness.

## Copy discipline

Every on-frame string is lifted or condensed from the approved refined
script — no claim reaches the frame that the narration does not make.
Headings are Title Case with no terminal period and carry
`data-role="heading"`. Body copy stays sentence case. On-frame copy lives in
markup, never in JS string literals. No wording departs from the refined
script; the narration beat manifest is a verbatim split, sentence by
sentence (two adjacent short sentences merged only where they are one
continuous clause: s34 = "They just started earlier. Now, so have you.").
