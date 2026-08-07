# Design — The Momentum Map

## Frame system

- Canvas: 1920 × 1080, with 120 px frame padding and content held above 960 px.
- Persistent top-left program label and top-right progress marker occupy the chrome.
- Primary backgrounds alternate between deep navy and cultured paper.
- A thin gold route line links scenes and provides continuity.

## Typography

- Proxima Nova (system fallback), using 900 for display, 700 for emphasis, and
  400 for supporting language.
- Display copy stays between 84–112 px; supporting copy stays at or above 40 px.
- Labels use uppercase blue or gold text at 22 px with generous tracking.

## Palette

- Deep navy `#0a1e2f`: reflection and uncertainty.
- Navy `#0d2437`: primary ink.
- Blue `#3393d6`: structure and available options.
- Gold `#eaab2d`: deliberate movement and the selected route.
- Cultured `#f6f6f9` and paper `#ffffff`: clarity and action.

## Scene motifs

- Work-history markers: small outlined tiles labeled PROJECTS, TEAMS, STAKEHOLDERS.
- Noise cloud: offset words and fine orbit lines, contained rather than chaotic.
- Direction route: an SVG path with circular decision nodes.
- Choice cards: three equal cards with simple geometric icons and clear labels.
- Fit test: three rings for VALUES, ENERGY, and REAL LIFE.
- Final goal: a large `90 DAYS` waypoint followed by four rising step markers.

## Motion

- Each beat enters within 1.2 seconds and exits in 0.3 seconds.
- Use transforms, opacity, SVG stroke drawing, and clip-path reveals only.
- No infinite animation. All animation belongs to one paused, seekable GSAP timeline.
- The final second adds one gold pulse around the named goal.

