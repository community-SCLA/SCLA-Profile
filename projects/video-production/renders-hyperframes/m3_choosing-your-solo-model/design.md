# Design direction

## Frame

- 1920 × 1080, 30 fps, 119.251 seconds.
- Navy stage with a persistent Solo Model Decision Board, program label, and quiet dot-grid texture.
- All primary content stays inside 120 px frame padding and above the reserved footer.

## Type

- Proxima Nova with the system fallback from `tokens.yml`.
- Large, short headings; supporting text never below 40 px.
- Uppercase labels use wide tracking and blue or gold for navigation.

## Visual carrier and components

- **Solo Model Decision Board:** one persistent three-column field for Freelance, Consulting, and Fractional work. It never resets; each sentence reveals or emphasizes the relevant promise inside the same board.
- **Model cards:** dark panels whose gold active state moves from projects to insight to embedded outcomes.
- **Decision criteria:** a compact set of chips keeps “how you work,” starting point, and next direction visible without behaving like playback progress.
- **Beat copy:** the left editorial column advances one concise idea at a time while the board accumulates evidence.

## Motion

- One paused GSAP timeline controls every transition and can be sought deterministically.
- Each scene enters within 1.2 seconds using opacity, position, and small scale changes.
- Scene content exits in 0.3 seconds; persistent frame furniture remains.
- No infinite animation. Ambient accents use one finite yoyo only.
