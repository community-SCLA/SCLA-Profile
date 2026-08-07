# Design direction

## Carrying object

One route rail runs across the bottom of every frame, from **Shift** to **Next
Chapter**, with seven named stations. A gold traveller advances station to
station as the argument moves. The rail and the program eyebrow are persistent
furniture drawn once outside the beat clips, so they never redraw — the lesson
reads as one continuous journey rather than a stack of slides.

Inside an act the frame ACCUMULATES: cards, chips and numbered moves are added
next to the ones already on screen and stay in the same positions. Only the act
transitions replace the field.

## Frame

- Canvas 1920×1080. All content sits inside x 130–1790 and y 150–950.
- Program eyebrow top left (inside the declared chrome region).
- Heading band at y 176. Stage (the accumulating field) at y 376.
- Route rail at y 803 with station labels at y 838.

## Palette and type

- Navy-deep field; paper and cultured for text; gold for the traveller, the
  active state and the numbers that carry the claim; blue for evidence chips;
  muted video blue for the inactive rail.
- Heading 64px / 900. Title card 100px / 900. Body 40–44px. Labels 22–24px.
- Cards and chips are outlined, never filled, so a beat adds ink rather than
  repainting the frame.

## Acts

| Station | Beats | What arrives |
| --- | --- | --- |
| Shift | ct-welcome … ct-quiet | four signals accumulate one per beat |
| Name It | ct-name-it | the field clears to a single naming line |
| Horizon | ct-researchers, ct-horizon | the two researchers, then the 3–5 and 5-year numbers, then the struck-out short horizons |
| Permission | ct-permission … ct-gets-done | the permission slip is built line by line |
| Tracks | ct-foundation … ct-redirection | Track 1, then 2, then 3 |
| Three Moves | ct-three-things … ct-third | three numbered moves fill in |
| Next Chapter | ct-one-promise … ct-question | the honest terrain, the evidence, the closing question |

## Motion

- Entrance: 0.5s per element, 0.13s stagger, settled well inside the beat.
- Each beat carries a slow parallax rise across its whole duration, so a long
  beat keeps breathing instead of freezing once its entrance has settled.
- The traveller advances with a 0.6s transform tween at each act boundary.
- No infinite repeats. Nothing on the rail ever redraws.
