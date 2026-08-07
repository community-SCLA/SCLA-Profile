# Design — Testing Your Next Chapter

## Direction

An editorial field guide: crisp white and cultured-paper cards on deep navy, with SCLA blue as the evidence trail and gold reserved for decisive moments. The composition uses generous spacing, strong typographic hierarchy, and simple diagrams rather than decorative imagery.

## Layout

- 1920×1080 canvas with 120px frame padding and a clear footer reserve.
- Persistent top-left module label and restrained lower-right progress marker.
- Headlines stay under two lines; supporting text is presented as short phrases rather than narration-sized paragraphs.
- The three experiments use consistent numbered cards and distinct diagram motifs.

## Type and color

- Proxima Nova with system fallback; navy, blue, gold, paper, cultured, and subtle-fill tokens only.
- Display text 88–108px; headings 60–72px; body 40–46px; labels 22px.
- No gradients. Contrast remains high on every scene.

## Motion

- A single paused GSAP timeline is registered as `m5_testing-your-next-chapter`.
- Entrances settle within 1.2 seconds; exits clear content in roughly 0.3 seconds.
- Evidence marks draw left-to-right; cards enter with short vertical lifts and opacity fades.
- Final second adds a gold endpoint and the words “Let’s design them.”

