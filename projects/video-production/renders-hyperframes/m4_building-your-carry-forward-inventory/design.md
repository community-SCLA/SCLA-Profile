# Design — The Carry-Forward Inventory Case

## Concept

The lesson takes place inside one persistent inventory case. Four fixed drawers hold the portable assets from a prior career: Skills and Capabilities, Values and Drivers, Relationships and Network, and Insights and Perspective. The case stays on screen while the lower sorting bay separates old context from genuine assets and the four drawers visibly fill.

## Persistent Carrier

- One fixed inventory case with four labeled drawers.
- A portability filter that physically separates old context from genuine assets.
- Four category-matched sets of asset marks that fill only when their drawer is discussed.
- A carry case that gathers all four named categories and moves toward the next chapter.
- A right-side insight panel that delivers one concise idea per narrated sentence.

## Visual System

- 1920 × 1080 deep-navy field with a white insight panel.
- Gold marks the selected portable asset and forward direction.
- Blue organizes categories and structural hierarchy.
- Local Proxima Nova faces and a pinned local GSAP runtime only.
- Header and all meaningful visual states remain inside declared safe regions.

## Motion

- One paused, seek-safe GSAP timeline.
- Every sentence insight appears within one second.
- Early beats push old context away while the genuine-asset case gains emphasis.
- Category beats open, illuminate, and fill the matching drawer; the recap inspects those completed drawers in sequence.
- Final beats brighten the filled carry case, reveal the next-chapter destination, and move the inventory forward.
- No playback rail, scene counter, full-runtime tween, or decorative progress surrogate is present.
- Motion is deterministic at arbitrary seek times, with no timers or infinite loops.
