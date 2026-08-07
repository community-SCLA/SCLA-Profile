# Design: The Through-Line

## Frame

The 1920×1080 canvas uses a 120px outer inset and reserves the lower 120px for captions. A slim program label and progress line remain stable while one persistent career-map field carries the whole lesson.

## Type and color

Proxima Nova is used throughout, with system sans-serif fallback. Headlines use navy or paper at 54–64px; supporting text stays at 40px or above. Navy provides authority, blue signals forward direction, and gold marks current evidence and progress.

## Persistent carrier

The through-line map never resets. Six fixed nodes—Reframe, Alex, Jordan, Priya, Four Moves, and Next Path—stay in place for all 35 complete-sentence beats. Each beat advances one small route signal, activates the relevant node, and swaps only the compact insight rail. The viewer watches one body of evidence accumulate rather than 35 separate slides.

## Motion

One paused, seekable GSAP timeline owns all motion. Insight phrases reveal with deterministic from/to opacity and horizontal movement. Route signals progress in place; the background glow uses one finite breathe. No infinite animation, wall-clock timing, or full-frame replacement.

## Accessibility

Contrast remains high, important text is never conveyed by color alone, labels are at least 20px, and explanatory text is at least 40px.
