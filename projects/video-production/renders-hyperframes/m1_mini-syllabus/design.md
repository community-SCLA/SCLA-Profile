# Design direction

## Frame

- 1920 × 1080, with generous 120px frame padding and a persistent 120px footer reserve.
- Navy background with paper cards, blue route lines, and gold active markers.
- A six-stop route along the footer shows progress without competing with the main message.

## Type

- Proxima Nova with the system fallback from `tokens.yml`.
- Display copy is 72–104px, bold or black; supporting copy is 36–44px.
- Small uppercase labels are at least 22px.

## Motion

- Each beat uses a short rise-and-fade entrance, staggered across headline and cards.
- The route line draws forward and the active checkpoint changes once per beat.
- Transitions are simple crossfades; no infinite or non-deterministic animation.

## Accessibility

- High-contrast paper-on-navy and navy-on-paper combinations.
- Meaning never depends on color alone; every checkpoint is numbered and labeled.
- On-screen copy stays concise and within the safe area.
