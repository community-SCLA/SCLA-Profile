# design.md — brand truth for `skills-for-the-ai-era-future_early-career-boost`

Design source of record for this one video. Brand values are LOADED from this
workspace's own `tokens.yml` copy (colors, type floors, spacing bands, the
pinned Oxana voice); nothing here restates a hex value a gate also reads.

Lesson: `lesson-scripts/early-career-boost/ready/skills-for-the-ai-era-future_early-career-boost.txt`
Lane: freeform (agent-native) — no templates, no `scenes.json`, no compiler.
Starting contract: `_concepts/skills-for-the-ai-era-future_early-career-boost/CONCEPT.md`
(judge-selected Pitch B, with Pitch A's lone stack grafted in).

**Every number below is the number the build actually carries.** The beat ids
are the 31 beats in `audio_request.json`; the geometry is the geometry in
`compositions/strip.html`; the runtime is `timing.json`'s 196.69s.

## Concept angle

> A brick skyline of skills that rises, sinks and is finally traced into one
> wave — one strip of stacked bricks standing on a single horizon rule, walked
> by one small figure, arriving on the first content beat and never left.

**Persistence: beats s02 → s31, i.e. ~96% of the runtime.** The horizon rule is
drawn on s01 and the first bricks on s02; the strip is never rebuilt, never
cleared and never left. Every later element is another way of reading it.

**The rule, stated out loud:** *if an element cannot be justified as another way
of reading the same strip, it does not exist.* Nothing on this frame is
introduced except as a brick ON a column, a brick UNDER the rule, a wash ACROSS
the strip, a notch ON a brick, a label ABOVE it (on a leader where exactly one
column is named), the figure walking the tops with its trail and rack, or the
closing stroke across the tops.

### Sharpenings of CONCEPT.md, made against the real gates

All narrowing rather than replacing; CONCEPT.md's accumulation contract is
unchanged.

1. **"Full frame width" becomes full CONTENT width.** The horizon rule spans
   x 180 → 1790, not 0 → 1920: `check_ink.py` grades real pixels against the
   safe-area (72px) and frame-padding (120px) keep-outs, and a literally
   full-bleed rule is ink inside both.
2. **One brick per course, not five tiles per course.** A fifth-of-a-column
   tile is ~18px wide at 1920×1080 and reads as texture, not mass — which is
   the congestion failure the judge's note names. Each brick is a rounded rect
   the width of its column with a deterministic ±4px edge jitter, so the
   profile still reads as hand-laid rather than measured.
3. **Rack tiles stay BLANK, like every other brick.** CONCEPT.md says tile
   faces stay blank in one place and calls the rack tiles "lettered" in
   another. Blank wins: lettering inside a 24px tile cannot clear the 40px body
   floor, and CONCEPT.md's own guard says the label count drops before the type
   size does. The naming stays in the label group, one group on frame at a time.
4. **The ghost stratum carries columns only, no ghost bed.** Offset (−30, +18)
   behind the live strip; a ghost bed offset downward would put ink below the
   content-bottom band.

## Palette

Every value comes from `tokens.yml colors:` (loaded by `check_brand.py`, which
fails any literal that is not one of them at any alpha).

| Role | Token | Use |
| --- | --- | --- |
| Page ground | `navy-deep` | full-bleed background child, never the root |
| Ground lift | `navy` | radial lift behind the strip |
| Foreground copy | `paper` | headings, title, the eyebrow at 0.72 |
| Body / secondary | `paper` at 0.78–0.80 | sub-lines, label rows |
| Standing bricks | `fill-subtle` at 0.93 | the columns — the brightest mass on frame |
| The bed | `muted-video` at 0.72 | the flat courses under the rule — the tasks AI is very good at |
| Structure | `blue` | the ghost stratum (dashed) and the category washes |
| The rule | `paper` at 0.92 | the one line that never moves |
| The detached column | `fill-subtle` at 0.44 | drawn once, apart, never traced |
| Focus accent | `gold` | **rationed**: the walker, its dotted trail, the notches, the rack, the "nearly total" line, the closing crest stroke |

Gold has exactly one job — *where the argument is pointing right now* — and is
never decoration. It arrives with the walker and closes with the crest.

## Type

Proxima Nova only, the vendored woff2 400/700/900 in `assets/fonts/`.
Hierarchy is weight, size and colour — never a second family.

| Role | Size | Weight |
| --- | --- | --- |
| Lesson title (title card) | 92px | 900 |
| Beat heading | 56px | 900 |
| Title sub-line | 44px | 400 |
| Label rows / sub-lines | 40px | 400 |
| Eyebrow (program banner) | 22px | 700, uppercase, 0.14em |

Body floor is the tokens.yml floor (40px); the label rows sit AT it and nothing
sits below it. Headings are `<h2>` (the title `<h1>`), Title Case, no terminal
period. Nothing is ever lettered inside a brick.

## Frame

1920×1080. All ink lives inside x 150…1790, y 58…950 — inside the safe-area,
frame-padding and content-bottom bands `check_ink.py` grades on real pixels.

| Band | y | x |
| --- | --- | --- |
| Program eyebrow (declared `chrome-regions`) | 58 → 84 | 150 → 480 |
| Heading | 140 → 208 | 180 → 1500 |
| Label rows (≤6) or one sub-line | 244 → 520 | 182 → 1262 |
| *clear air* | 520 → 596 | — |
| Columns (≤7 bricks, 30px each, 34px pitch) | 598 → 832 | 200 → 1786 |
| Horizon rule | 838 → 843 | 180 → 1790 |
| Bed (≤3 courses) | 850 → 948 | 190 → 1750 |

The ghost stratum is offset (−30, +18) behind the live strip, so its lowest ink
is 850. There is no brandline: the eyebrow is the only chrome, and a second
footer line would be ink in the bottom band for no gain.

## Motion

- **Entrances only.** 0.45–0.9s, `power3.out` / `power2.in` / `power3.inOut`,
  each pinned to a real narration word onset from `audio_meta.json`.
- **No repeating tween anywhere in this build** — no `repeat`, no `yoyo`, not
  even on the background. Settled content never re-animates in place
  (`check_motion.py`), and this build claims no `motion-allow` exception at all.
- **Bricks that leave a column are never deleted** — they translate down into
  the bed. The drawing keeps its own past, so "these skills lost value" is
  shown rather than asserted.
- **One re-arrangement in the whole runtime**: on s20 the three twice-banded
  columns slide out of the line and land as one block to the RIGHT of
  everything. It reads as an event because it is the only time anything already
  placed moves sideways.

## Every beat earns its back half

Each beat carries a copy arrival in its front half and a **strip arrival in its
back half** — bricks laid, a brick sinking, a wash, a notch, a footstep, a rack
tile, a stroke. No beat's picture is finished at its midpoint, and no two
neighbouring beats show the same strip.

| Beat | Heading | What the strip does |
| --- | --- | --- |
| s01 | Skills for the AI Era Future | the rule draws in, in three strokes — nothing stands on it yet |
| s02 | Careers Are More Than Tasks | the bed lays a full course; four columns stand up |
| s03 | The Skills Hardest to Automate | column 1 grows twice more, labelled on a leader |
| s04 | Direct AI Rather Than Compete | three more named columns rise, one per label row |
| s05 | Think Back Ten Years | the dashed ghost stratum arrives behind, offset down-left |
| s06 | Learn to Code, and It Worked | the tall ghost spike grows to full height — **M1** |
| s07 | Today That Advice Is Ambiguous | three bricks leave the spike and land in the bed |
| s08 | That Is the Real Lesson | a fourth leaves; the bed takes a second course |
| s09 | A Long Stretch Comes First | the second course completes, a third begins |
| s10 | Some Values Fall, Others Rise | three bricks sink from three columns; three rise on three others |
| s11 | Keep Moving Toward Rising Skills | the walker arrives on a top; the first footsteps appear |
| s12 | Which Skills Rise in Value? | the walker steps right; two new columns start right of everything |
| s13 | Four Categories Worth Watching | four band outlines are pencilled across the strip |
| s14 | Work That Needs Human Judgment | band 1 washes; a brick lands inside it — **M2** |
| s15 | Building and Deploying AI | band 2 washes; the column inside it doubles |
| s16 | Things People Want More Of | band 3 washes; two columns grow under it |
| s17 | Specialized Skills Take Time | band 4 washes; a new column lands, right of everything |
| s18 | You Do Not Need All Four | a column grows ahead of the walker; the walker steps onto it |
| s19 | Look for Two at Once | notches are cut into every brick of the three twice-banded columns |
| s20 | Transferable to Almost Any Career | **the one re-arrangement**: the notched columns slide into a block, equalize, and the empty rack appears |
| s21 | Use AI to Get Work Done | rack tile 1 |
| s22 | Take Care of Yourself | rack tile 2 |
| s23 | Agency and Decision-Making | rack tiles 3, 4 and 5 |
| s24 | Above All, Learning How to Learn | rack tile 6 — the rack is full; the walker moves up the strip — **M3** |
| s25 | You Do Not Out-Compute a Machine | the walker steps into the sorted block; the trail lengthens |
| s26 | A Thoughtful Human with Powerful Tools | the walker crosses the block to the crest |
| s27 | What the History Tells Us | the ghost stratum re-lights and each ghost column gains a brick |
| s28 | Only When It Is Nearly Total | a dashed "nearly total" line is drawn high above the bed; the bed grows toward it and stops |
| s29 | Some Down, Others Up | one brick sinks at the left, one rises under the walker at the right |
| s30 | The Goal Is Not One Safe Job | one tall blank column is drawn apart at the right, with a clear gap and no trail reaching it |
| s31 | Ride the Wave | the crest stroke traces every top, in six strokes, left edge to right — and stops short of the detached column |

## What accumulates (the shuffle test, by construction)

| Counter | s02 | M1 ≈49s | M2 ≈99s | M3 ≈148s | M4 ≈195s |
| --- | --- | --- | --- | --- | --- |
| Live columns | 4 | 8 | 8 | 11 | 11 + 1 apart |
| Bricks standing | 8 | 20 | 26 | 41 | 44 |
| Strip right edge | x 992 | x 992 | x 992 | x 1600 | x 1786 |
| Bed courses | 1 | 1 (+3 fallen) | 3 | 3 | 3 |
| Trail dots | 0 | 0 | 3 | 5 | 8 |
| Category bands | 0 | 0 | 1 | 4 | 4 |
| Notched bricks | 0 | 0 | 0 | 15 | 15 |
| Rack tiles | – | – | – | 6 | 6 |
| Crest stroke | no | no | no | no | yes |

Every row is monotonic and every row is legible from a still with the text
unreadable. Any two stills can be ordered by strip width and trail length alone.

## The payoff beat

The final beat, on the script's own closing line about riding the wave. One
continuous gold stroke is traced across the top of every column that has
accumulated over the whole runtime, and the silhouette resolves into the wave
the narration names. Nothing new is invented: the stroke only connects tops
already on screen, which is exactly why it cannot exist at 0:10 — at s02 there
are four two-brick columns and no profile to trace.

Set apart at the far right, with a clear gap and no trail reaching it, stands
one tall blank column the crest stroke does not touch: the single job that will
never be automated, which the script rejects by name on s30. It is drawn once,
never labelled, and the stroke simply stops before it.

## Copy discipline

On-frame copy compresses the beat's own narration and introduces no fact, count
or sequence claim the voice does not say. The title card is DERIVED: the eyebrow
is the `programs:` display name for `early-career-boost`, the title is the
stem's title segment with hyphens as spaces. No numbers anywhere on the strip —
no axis, no gridline, no tick, no legend, no count.

**One punctuation-only edit to the narration, recorded here because it is the
only place the beat manifest differs from the approved `.txt`:** the sentence
break between "Personal effectiveness and agency." and "Prioritization,
forecasting, and decision-making." is a comma in the manifest, joining them into
one sentence. Without it the script reads as a three-item spoken list ending
without a conjunction, which `check_copy.py`'s `missing-conjunction` rule blocks
at the gate. The join changes **zero tokens** — `script_match` reports 0.00%
mismatch — so no word the owner approved was added, removed or altered.
