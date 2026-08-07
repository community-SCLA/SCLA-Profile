# Design — You've Built Momentum

## Frame

- Canvas: 1920×1080.
- Background: deep navy with restrained pale-blue panels.
- Safe padding: 120px; content ends above the 120px footer reserve.
- Persistent chrome: program label at upper left, lesson progress at upper right, and a slim gold momentum rail near the bottom.

## Type

- Proxima Nova with the token fallback stack.
- Headlines: 72–104px, weight 900.
- Supporting copy: 40–46px, weight 400 or 700.
- Labels: 22px, weight 700, uppercase, 0.14em tracking.
- All essential text remains at or above the 40px body floor.

## Color

- Navy `#0d2437` and navy-deep `#0a1e2f` carry the background.
- Gold `#eaab2d` marks progress, numbered reminders, and the final action.
- Blue `#3393d6` marks structure and connections.
- Paper and cultured white provide high-contrast reading surfaces.

## Composition system

- The carrying object is the persistent gold momentum rail: it stays in place for the full lesson while its marker advances through the same field, so each beat updates one compact stage instead of replacing the frame.
- Beat content stays inside a consistent 1280px-wide center stage, preserving the surrounding field and rail from one idea to the next.
- Milestone cards use a 12px radius, 2px blue border, and short gold rule.
- The system view uses four equal cards: Outcome, Visibility, Relationships, Results.
- Reminder beats use a 74px gold point marker and one concise instruction.
- The final path uses three outlined destination chips flowing into a gold arrow.

## Motion

- Each scene enters within 1.2 seconds using opacity, 24–36px vertical travel, and a drawn rule.
- Scene content exits in 0.3 seconds; persistent chrome remains.
- The momentum rail scales horizontally across the full lesson.
- The closing beat adds one final gold resolve in its last second.
- The GSAP timeline is paused and seekable; no infinite motion is present.
