# Design — The Next-Chapter Experiment Board

## Concept

The lesson lives inside one persistent experiment board. A fixed learning loop replaces the old “reflect until certain” model: Act, Observe, Gather Evidence, Reflect, and Adjust. Three fixed test cards—Informational Interview, Trial Project, and Shadow Day—stay visible while the lesson moves from introspection to evidence.

## Persistent Carrier

- One fixed experiment board with a single learning question.
- A fixed action-and-evidence cycle that changes emphasis at the lesson's six
  conceptual phases.
- Three fixed experiment cards representing the module’s practical tests.
- A circular evidence map keeps acting, observing, gathering, reflecting, and
  adjusting visibly connected without tracking playback.
- A right-side insight panel delivers one concise idea per narrated sentence without
  clearing between beats.

## Beat-to-Frame Progression

- **Beats 1–5 — Reflection:** the loop dominates while the three field tests wait
  in the background; the insight panel uses open editorial layouts.
- **Beats 6–13 — Action:** the tests move forward and action insights adopt a
  structured field-label treatment.
- **Beats 14–24 — Feedback:** the evidence cycle emphasizes observation while
  insights appear as collected notes.
- **Beats 25–31 — Three tests:** the test row becomes the dominant board layer and
  the right panel shifts to a dark field-card treatment.
- **Beats 32–37 — One question:** the learning question moves forward, the rest of
  the board recedes, and the right panel becomes a focused question field.
- **Beats 38–40 — Evidence:** the full board and evidence cycle settle together
  to resolve the lesson.

## Visual System

- 1920 × 1080 deep-navy testing field with a white insight panel.
- Gold marks the active experiment and newly gathered evidence.
- Blue structures the learning loop and experiment cards.
- Local Proxima Nova faces and a pinned local GSAP runtime only.
- Header and experiment-board elements remain inside declared safe regions.

## Motion

- One paused, seek-safe GSAP timeline.
- Every sentence insight is fully present at its boundary; spatial movement gives
  the handoff energy without creating a blank right-card interval.
- The active learning-loop stage and experiment card illuminate without replacing the board.
- Phase-local evidence-cycle highlights and beat-specific board motion maintain continuity.
- No playback rail, scene counter, footer progress strip, or full-runtime tween is present.
- Motion is deterministic at arbitrary seek times, with no timers or infinite loops.
