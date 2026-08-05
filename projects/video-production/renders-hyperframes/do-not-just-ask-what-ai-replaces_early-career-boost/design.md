# design.md — brand truth for `do-not-just-ask-what-ai-replaces_early-career-boost`

Design source of record for this one video. Brand values are LOADED from this
workspace's own `tokens.yml` copy (colors, type floors, spacing, the pinned
Oxana voice); nothing here restates a number a gate also reads.

Lesson: `lesson-scripts/early-career-boost/ready/do-not-just-ask-what-ai-replaces_early-career-boost.txt`
Lane: freeform (agent-native) — no templates, no `scenes.json`, no compiler.
Judged concept: `renders-hyperframes/_concepts/<stem>/CONCEPT.md` (Pitch B,
task-bricks re-laid into a doorway, with Pitch A's retreating shadow grafted in).

## Concept angle

> One slab of role-work, labelled once, broken into task-bricks and re-laid —
> never emptied — into a doorway with a clear opening in it, while a hard-edged
> shadow retreats off the frame it opened on.

**Persistence: beats s01 → s35, i.e. 100% of the runtime.** The slab is on
frame in the title beat; by ~0:30 (≈16%) every brick that will ever exist has
already arrived, so everything after that is re-arrangement, not arrival. No
brick ever leaves the frame — that is load-bearing, because the closing void is
only an argument if it was made by re-laying, not by deleting.

**The rule, stated out loud:** *if an element cannot be justified as another way
of reading the same wall, it does not exist.* There is no second illustration,
no icon, no decorative object. The masonry IS the hero illustration.

## The carrying object

| Part | What it is | When it exists |
| --- | --- | --- |
| The slab | one large rectangle, 2px dashed internal scoring (the cut-lines of a thing about to be demolished) | s01–s05, then it comes apart |
| The bricks | flat rectangles, 4px radius, 2px stroke, near-transparent fill, irregular widths, 6px mortar gap, running bond | s05 → end |
| The datum | ONE 2px blue rule, drawn once at s10 and never redrawn | s10 → end |
| The loop path | 3px polyline with four small square nodes | s30 → end |
| The shadow | one hard-edged angled quadrilateral in `navy-deep` over the `navy` ground — no face, no figure, nothing representational | s01, monotonically retreating, gone at s35 |

**Weight is the only encoding.** A task that becomes less scarce loses height
and stretches wide into a thin strip below the datum. A task that becomes more
valuable grows taller and picks up a second stroke above the datum. Thin-and-wide
versus tall-and-double is tellable apart at thumbnail size with every label
hidden.

**Motion discipline.** A brick performs exactly one action per beat — one lay,
one migration, one thickening — and is pixel-static afterwards. The shadow
retreats at most once per beat. Nothing re-animates in place; the only declared
exception is the background glow, which is not content.

## Milestone frames — the accumulation contract

Held from `CONCEPT.md`, re-pinned to the real beat grid:

| Mark | Beat | Silhouette |
| --- | --- | --- |
| 0% | s01 | **solid rectangle** — one scored slab under a shadow that covers the left half |
| 25% | s09 | **scatter** — the slab is gone as a shape and wholly present as ~40 loose unlabelled pieces at mixed angles; the datum is being drawn with nothing on it yet; bricks inside the shadow are dimmer |
| 50% | s18 | **two courses of obviously different heights** — a wide flat band of thin strips low, a short tall row of double-stroked bricks above the datum, one brick mid-migration between them; the shadow is off the upper course |
| 75% | s26 | **stratified wall, one line crossing** — upper course at full height edge to edge and fully lettered, lower strip fully lettered and unmistakably thinner; the shadow is a sliver at the extreme left |
| 100% | s35 | **aperture** — two piers, a three-brick lintel, the strip as a threshold, the loop closed around the doorframe, a clear void where the shadow lay, and no shadow |

What accumulates, in order: edges (one outline → many) → a datum and a side for
every brick → a thickness differential → lettering to a fixed budget, maxed at
s26 → a connecting path that crosses between the courses for the first time →
an opening, the widest silhouette of the video. Maximum ink lands at s26; every
gain after that is structural, not textual.

## The payoff beat

**s34, "look for the openings instead of the threats."** The upper course splits
and moves outward into two piers, the lintel drops in, and the void appears
where the opening shadow lay. No brick left the frame, so the opening was made
by re-laying, not by deleting — the script's own "most roles are not deleted —
they are reshaped," drawn instead of said. **s35** gets one legal move: the last
sliver of shadow clears out through the void, then the frame holds pixel-static
through the final hold.

A second, smaller re-read runs underneath: the **judgment** brick is laid at
s13, thickened at s26, and ends in the lintel at s34 — one piece with a
three-act life a viewer can trace backwards.

## Palette

Every value is a `tokens.yml colors:` token at some alpha (`check_brand.py`
fails any literal that is not).

| Role | Token | Use |
| --- | --- | --- |
| Page ground | `navy` | full-bleed background child, never the root |
| Shadow | `navy-deep` | the retreating quadrilateral; darker than the ground by design, and low-contrast enough that it is a tone, not an edge |
| Lift | `blue` at low alpha | one radial glow behind the wall |
| Foreground | `paper` | display type, headings |
| Body / secondary | `paper` at ~0.76 | body lines |
| Structure | `blue` | the datum, brick strokes, the loop path |
| Focus accent | `gold` | **rationed**: the brick the narration is naming right now, the lintel, the aperture threshold |

Gold never decorates — it marks what the wall is pointing at.

## Type

Proxima Nova only, the vendored woff2 400/700/900 in `assets/fonts/`.
Hierarchy is weight, size and colour — never a second family.

| Role | Size | Weight |
| --- | --- | --- |
| Lesson title (title card) | 104px | 900 |
| Beat heading | 62px | 900 |
| Body line | 42px | 400 |
| Brick label (upper course) | 30px | 700, uppercase, 0.10em |
| Brick label (lower strip) | 26px | 700, uppercase, 0.10em |
| Eyebrow / datum captions | 26px | 700, uppercase, 0.14em |

Brick labels are label-class furniture by typesetting (uppercase + tracked), not
body copy: they are one- to three-word nouns cut from the narration, sitting
inside a drawn object. Anything the viewer reads as a sentence is ≥42px.

## Frame

- 1920×1080. Nothing content-bearing crosses the safe area, the frame padding
  or the content-bottom band — all three LOADED from `tokens.yml` and graded on
  real pixels by `check_ink.py`.
- Head band y 150→330 (heading), body line y 350→410.
- Wall canvas y 430→945, x 150→1770. The datum is a single rule at y=706.
- The program eyebrow is the only element in the top keep-out, inside the
  `chrome-regions` rectangle `tokens.yml` declares by name.
- The shadow spans to the frame edges deliberately. It is drawn `navy-deep` on
  `navy` — about five grayscale levels apart — so it reads as a tone on screen
  and carries no glyph-grade edge into a keep-out band.

## Motion

- Entrances only: 0.35–0.7s, `power3.out` / `back.out`, pinned to the word
  timestamp that earns them. Nothing settled re-animates in place.
- The wall is only ever *laid, migrated, thickened or lettered* — never rebuilt
  and never cleared.
- One ambient breath, on the background glow alone, declared inline with
  `/* motion-allow: … */`.
