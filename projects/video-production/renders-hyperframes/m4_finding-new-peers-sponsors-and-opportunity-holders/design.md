# Design

## Direction

Use a clean editorial map on deep navy. People appear as labeled circular
nodes connected by thin blue and gold paths. White cards provide contrast for
definitions and search steps. The learner is always the visual anchor.

## System

- Canvas: 1920 × 1080
- Palette: navy `#0d2437`, deep navy `#0a1e2f`, blue `#3393d6`, gold
  `#eaab2d`, paper `#ffffff`, cultured `#f6f6f9`
- Type: Proxima Nova with system sans-serif fallback
- Frame padding: 120px; content stays above 960px
- Headlines: 64–84px, 900 weight; body: 40–46px

## Motion

Each clip has a short entrance, a readable hold, and a clean exit. Nodes scale
in, paths draw from the learner outward, and cards rise by 24px. Motion is
finite and fully controlled by one paused GSAP timeline. The final connection
draws during the last second as the additive resolve.

