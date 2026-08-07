# Design — The Momentum Map

## Frame system

- Canvas: 1920 × 1080, with 120 px frame padding and content held above 960 px.
- The top-left program label remains the only persistent chrome. Numeric scene
  counters such as `12 / 20` are not shown; they read as presentation progress,
  not authored video.
- Primary backgrounds alternate between deep navy and cultured paper.
- A single momentum-map carrier occupies the open half of every frame. It
  evolves from an experience ledger, to a noise orbit, to rising steps, three
  branches, a fit target, and a final directional arrow.

## Typography

- Proxima Nova is loaded from the workspace's three local WOFF2 files, using
  900 for display, 700 for emphasis, and 400 for supporting language.
- Display copy stays within the 60–72 px heading range; supporting copy stays
  at or above 40 px.
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
- Direction route: one continuous geometric map with circular decision nodes.
- Choice cards: three equal cards with simple geometric icons and clear labels.
- Fit test: three rings for VALUES, ENERGY, and REAL LIFE.
- Final goal: a large `90 DAYS` waypoint followed by four rising step markers.

## Motion

- Each beat enters within 1.2 seconds; content and the map use distinct motion
  directions so the carrier reads as an evolving subject.
- The gold dot advances along one continuous rising route in every scene. Its
  starting position matches the previous scene, so the repeated carrier shows
  accumulated momentum instead of behaving like a static chart.
- Use transforms, opacity, SVG stroke drawing, and clip-path reveals only.
- No infinite animation. All animation belongs to one paused, seekable GSAP timeline.
- The final second adds one gold pulse around the named goal.
