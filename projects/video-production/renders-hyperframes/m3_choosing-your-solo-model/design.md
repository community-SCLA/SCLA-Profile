# Design direction

## Frame

- 1920 × 1080, 30 fps, 111 seconds.
- Navy stage with a slim gold progress rail, persistent program label, and quiet dot-grid texture.
- All primary content stays inside 120 px frame padding and above the reserved footer.

## Type

- Proxima Nova with the system fallback from `tokens.yml`.
- Large, short headings; supporting text never below 40 px.
- Uppercase labels use wide tracking and blue or gold for navigation.

## Components

- **Model cards:** white panels with a blue top rule and a gold numbered marker.
- **Project track:** brief, work, and deliverable nodes connected left to right.
- **Diagnostic lens:** concentric rings that resolve into a concise plan card.
- **Embedded team:** a central gold role connected to three blue team nodes.
- **Choice path:** a strong freelance starting node branching toward consulting and fractional roles.

## Motion

- One paused GSAP timeline controls every transition and can be sought deterministically.
- Each scene enters within 1.2 seconds using opacity, position, and small scale changes.
- Scene content exits in 0.3 seconds; persistent frame furniture remains.
- No infinite animation. Ambient accents use one finite yoyo only.

