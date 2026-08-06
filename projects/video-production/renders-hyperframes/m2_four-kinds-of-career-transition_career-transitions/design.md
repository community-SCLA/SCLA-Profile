# Design: The Transition Compass

## Frame system

- Canvas: 1920 × 1080, 16:9.
- Safe area: 120px horizontal, 72px vertical, with the bottom 120px reserved.
- Background: SCLA deep navy (`#0a1e2f`) with a full-bleed child layer.
- Main panels: white or cultured paper, 12px corners, restrained 2px borders.
- Active information: gold (`#eaab2d`); structural information: blue (`#3393d6`).

## Type

- Proxima Nova with system sans-serif fallback.
- Scene titles: 72–92px, weight 900.
- Supporting copy: 40–46px, weight 400 or 700.
- Labels: 21–25px uppercase, weight 700, 0.14em tracking.
- Keep copy to short visual phrases; narration carries the detail.

## Persistent grammar

**The carrying object is the two-axis compass.** It is built once in scene 2 and
then re-sorted, never redrawn: every quadrant scene carries the same 2×2 map with
one quadrant outlined in gold and the marker parked inside it. Growth Pivot uses
the large left-column compass that introduces the device; Reinvention, Rebuild and
Forced Reinvention use the compact upper-right badge this file reserves for it. The
marker never leaves the quadrant the frame's kicker claims.

The bottom rail is furniture, not content: its caption sits above the rail line on
transparent ground, so no rail geometry is ever painted over. Directional lines,
nodes, and stepping stones reuse the same blue/gold map vocabulary.

## Frame-to-frame budget

This lesson draws ten materially different pictures, so beat-to-beat churn is the
scarce resource (`check_pace` carrier-drift, 6% ceiling; this cut measures 5.89%).
Content therefore stays inside the established ink footprint: new elements are type
and outlines rather than new paper masses, and the compass is the shared mark that
persists across the four quadrant scenes.

## Motion

- Entrance groups settle within 1.2 seconds.
- Axis lines draw with `scaleX` / `scaleY` from a fixed origin.
- Cards enter with short opacity and vertical-position moves.
- Route nodes reveal sequentially at finite intervals.
- No infinite loops, clocks, random values, network requests, or animation of layout properties.
- Each scene exits in 0.3 seconds; the final scene adds one route resolution during its last second.

## Scene plan

1. **Tactics before type** — three tactic cards fan in, dim, and make room for the central question.
2. **Build the compass** — axes draw; four quadrants label themselves clockwise.
3. **Growth Pivot** — familiar domain remains fixed while scope, complexity, and visibility rise.
4. **Reinvention** — a milestone route connects skater, editor, design director, and founder.
5. **Rebuild** — an external shock bends a route while transferable strengths cross intact.
6. **Forced Reinvention** — constraints reshape the path and open a new destination.
7. **Forced ≠ failed** — a direct language correction resolves into grief, support, transfer, experiment.
8. **The hidden trail** — one apparent leap zooms out into accumulated adjacent steps.
9. **Match the tactics** — each quadrant receives one concise action prescription.
10. **Choose the next step** — the full model simplifies to NAME → MATCH → MOVE.

