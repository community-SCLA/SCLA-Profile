# Design direction

## The carrying object

One route, drawn once at the bottom of the frame and never redrawn: six numbered
stops named for the six acts of the lesson. It is the lesson's own progress bar,
which is what beat 5 talks about, so the furniture and the argument are the same
object. Across the whole runtime it only ever advances — the gold fill grows one
sixth per act and the active stop lights.

Nothing else is thrown away and redrawn either. Inside an act the frame only
ACCUMULATES: the label and heading land first, the supporting line next, then the
chips, then the closing note. Every element sits at a fixed absolute position, so
a later reveal never reflows an earlier one and the settled pixels are identical
from beat to beat.

## Frame

- 1920 × 1080. Content lives between x 120–1800 and y 126–940.
- The route occupies y 826–940; nothing is authored below y 940, so the 960px
  content-bottom reserve stays clear.
- Navy field, faint 96px grid, a single blue glow top-right. No filled panels:
  a large solid card appearing mid-lesson throws away a fifth of the frame, which
  is the opposite of a carrying object.

## Type

- Proxima Nova (400/700/900), vendored.
- Act heading 72px/900; supporting line 40px/400; chips 32px/700; notes 32px/700;
  labels and stop names 26/20px 900 uppercase. Marker numerals are sized by their
  circles and declared exempt at the rule.

## Motion

- One paused GSAP timeline. Every on-frame element declares its own entrance time
  in markup (`data-at`), so the timeline is a reading of the composition rather
  than a second script of the lesson.
- Entrances only: 26px rise + fade over 0.6s, spread across the beat they belong
  to. No exits, no keep-alive motion, no repeats — a beat's content stays put
  until its act ends.

## Beats

Six acts over seventeen beats, one beat per sentence of the approved script:

1. **Welcome** — welcome, ready-for-more
2. **Your Career Map** — journey, checkpoint, progress
3. **Simple Tools** — tools, support
4. **Mid-Career Choices** — complicated, pressures, promotion, redesign, change-lanes
5. **Your Next Move** — next-move, build-momentum
6. **Your 90-Day Commitment** — commitment, anchor, begin

## Accessibility

- Paper and pale-blue copy on navy; gold reserved for labels, markers and the CTA.
- Every stop is numbered as well as coloured, so the route never depends on colour.
- On-screen copy is compression of its own beat, never new claims.
