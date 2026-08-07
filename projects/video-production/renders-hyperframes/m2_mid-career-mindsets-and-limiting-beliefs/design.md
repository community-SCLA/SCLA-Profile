# Design direction

## Frame
- 1920×1080, with a 120 px content inset and a quiet 120 px footer reserve.
- Navy foundation, white and cultured-paper cards, blue structure, and gold decision accents.
- Proxima Nova with system sans-serif fallback; headings 64–88 px, body copy 40–46 px, labels 22 px.

## Visual language
- One persistent editorial career map is the carrying object for the entire lesson. It never resets between beats.
- A fixed map field holds belief, leverage, experiment, redesign, and next-path nodes; each beat only re-sorts emphasis by advancing one route marker and activating the relevant node.
- A compact insight rail changes the current phrase without replacing the map, so the viewer watches one system accumulate rather than a sequence of unrelated slides.
- Persistent top label identifies the Mid-Career Momentum program.
- Eighteen short semantic beats deliver one complete thought at a time while preserving the source narration verbatim.
- Gold marks only the active choice or next move.

## Motion
- One paused GSAP master timeline, seeked by HyperFrames.
- The career map remains present; only the active node, route marker, and insight phrase change at a beat boundary.
- Insight phrases use deterministic 0.25–0.45 second from/to reveals. Route progress draws forward with finite transforms; no infinite animation.
- Beat handoffs are continuity cuts inside the shared field. The final beat resolves the route in gold.

## Accessibility
- High-contrast type, minimum 22 px labels and 40 px explanatory text.
- Meaning never depends on color alone; labels accompany every node and path.
