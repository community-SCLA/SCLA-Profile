# HyperFrames Element Candidates for a More Polished, Engaging Lesson Stack — 2026-07-14

**Type:** Proposal / survey. A menu of HyperFrames capabilities the SCLA illustrated-lesson stack did **not** yet use, evaluated for polish and engagement.
**Status (updated 2026-07-15):** Ruled on in two rounds — see `decisions/log.md` 2026-07-14 (pilot) and 2026-07-15 (promotion).
- **Adopted (7):** #2 progress rail · #4 living icons (brand-native SVG substituted for Lottie) · #5 FLIP hand-off (as `scla-morph`) · #8 depth-drift parallax · #9 stat rings — promoted 2026-07-15 — plus, ruled later the same day after the review surfaced them: #6 SVG shape morph and #7 text-trail kinetic type (weight steps limited to the self-hosted 400/700/900; no VF interpolation) — both as sanctioned arsenal recipes in `frame.md`, staged-beat motion only under the reaffirmed animacy ban.
- **Explicitly deferred:** #1 open captions and #3 ambient audio bed (out of the promotion's scope — they touch the render pipeline, gates, and the sound-off decision); #10 lower-thirds (owner passed over it 2026-07-15; revisit if attributed quotes become common); cursor demos (parked below).
**Original status note:** Reconstructed fresh — a prior session discussed this but nothing was persisted, so this is a new survey from first principles, not a transcript recovery.
**Scope:** The illustrated path only (`design-system/`, the nine `scla-*` templates). Avatar-pipeline untouched.
**Owner decision needed** before any of this reaches `frame.md`'s motion-rotation table — this is a candidate list, not a change.

---

## Method

Surveyed three surfaces and subtracted what's already sanctioned:
1. **Already in the arsenal** — `frame.md` → "Motion rotation — the sanctioned arsenal" (18 recipes, surveyed 2026-07-09) + the 9 templates.
2. **The HyperFrames skill pack** — `hyperframes-animation` (7 runtime adapters), `-keyframes`, `-media`, `-registry`, `media-use` (full map in `hyperframes-skills-reference.md`).
3. **Brand + determinism constraints** — `frame.md` doctrine (`power3` eases, resolve-in-back-half, seek-safe, no `Math.random`/`repeat:-1`), sound-off teaching design (decisions/log.md 2026-07-07), audience 18–24.

**Key reframe that shapes the ranking:** the videos are designed to **teach with sound off** (decision of record). That makes *open on-screen captions* the single highest-leverage addition and *demotes* an ambient audio layer to a sound-on nicety.

## What's already covered (do not re-propose)

Word glow, CSS marker emphases, chip spring-pops, grid-card assemble, kinetic type, SVG path-draw, MotionPath travel, stat count-ups + bars/fills, in-scene camera (zoom/pan/DOF), comparison-split, constellation/network, spatial pan-stations, clip/mask reveals, scale-swap/card-morph hand-offs, brand-safe scene transitions, `flowchart` + `data-chart` registry blocks, per-word caption reference. All GSAP-driven.

**Confirmed off-limits (leave off-limits):** WebGPU liquid-glass, VFX/glitch packs, social-platform overlays — off-brand or determinism-hostile.

---

## Candidate additions — ranked by leverage

Each: what it is · source skill/recipe · which templates it strengthens · why it lifts engagement · risk. Confidence tagged where a specific recipe/block name needs verification against the live catalog (`npx hyperframes catalog` / the skill files in `.agents/skills/`) before it's written into `frame.md`.

### Tier 1 — highest leverage, adopt first

**1. Open captions / karaoke subtitle track (accessibility + sound-off engagement).**
The lessons teach sound-off but carry no burned-in captions today. `hyperframes-media` authors captions from the transcript we already generate (`transcript.json`) — either the quiet verbatim `anchor` identity or a brand-styled karaoke read that tracks the VO word-by-word.
- *Strengthens:* all nine — a persistent bottom band, brand-tokened, present on every scene.
- *Why:* doubles as accessibility (WCAG) and as the sound-off comprehension layer the design intends; retention lift on social auto-play-muted contexts is large for the 18–24 audience.
- *Risk:* low. Deterministic (transcript-driven, seek-safe). Must respect safe-bounds so it never collides with `scla-outro`/`scla-stat` lower text. Decide one identity and pin it in `frame.md`.

**2. Persistent progress / chapter indicator.**
A thin brand-gold progress rail or chapter pip that advances across the whole runtime. Likely a `hyperframes-registry` component or a small host-root overlay track. *(Confidence: capability certain; exact registry block name — verify against catalog.)*
- *Strengthens:* host composition (spans all scenes), not a template.
- *Why:* "how much is left" is a documented completion-rate lever; cheap, unobtrusive, on-brand.
- *Risk:* low. Pure timeline-proportional width — trivially deterministic.

**3. Ambient audio bed + sparing SFX.**
One low bed of BGM under the VO plus 3–4 tuned SFX (chip pop, route-trace whoosh, stat-tick, outro resolve) via `hyperframes-media` / `media-use resolve` (HeyGen audio-library or local Lyria fallback).
- *Strengthens:* chips, career-map, stat, outro especially.
- *Why:* lifts sound-on viewing and production sheen. **Demoted from what it'd be otherwise** because the design target is sound-off — so this is polish, not core.
- *Risk:* low-medium. Must be a fixed asset (frozen via media-use ledger), leveled well under VO, and licensed. Brand tone forbids anything "hype/EDM" — keep it calm and warm.

### Tier 2 — real polish, adopt selectively

**4. Lottie micro-animations for icons.**
The Lottie runtime adapter (already in `hyperframes-animation`, unused by us) drives lightweight vector icon animations, timeline-seeked so they stay deterministic.
- *Strengthens:* `scla-points`, `scla-steps` (an icon per point/step that animates on its cue), `scla-outro` (animated wordmark accent).
- *Why:* small living details are what read as "polished" vs. "templated"; far lighter than 3D.
- *Risk:* medium. Must source/brand-recolor Lotties and drive them off the paused timeline (no autoplay loop). Curate a small approved set, don't open the floodgates.

**5. FLIP layout hand-offs.**
`hyperframes-keyframes` FLIP: an element smoothly re-flows to a new position/size across a beat instead of cross-fading.
- *Strengthens:* `scla-points` → collapse the list and promote the one point the VO lands on; `scla-chips` → gather chips into a cluster; `scla-career-map` → the winning route settling.
- *Why:* the buttery "the thing you were looking at *became* the next thing" motion; higher perceived quality than swap-fades.
- *Risk:* low-medium. Seek-safe FLIP is well-supported; just needs careful anchor timing.

**6. SVG shape morph (not just draw).**
We draw paths (`svg-path-draw`); we don't *morph* one shape into another. `hyperframes-keyframes` SVG morph.
- *Strengthens:* `scla-steps` (an icon morphs step→step to show transformation), brand-mark reveals, `scla-stat` iconography.
- *Why:* signals change/progress more vividly than a cut; distinctive.
- *Risk:* medium. Morph targets must have compatible path structure — needs asset prep. Use sparingly.

**7. Variable-font / text-trail kinetic type.**
`hyperframes-keyframes` text trails + variable-font weight animation for the "the words ARE the visual" beats, a step up from the current per-word slide-in.
- *Strengthens:* `scla-statement`, `scla-title`, any kinetic-type moment.
- *Why:* modern, energetic, on-trend for the age group — without leaving typography (stays brand-safe).
- *Risk:* low-medium. Proxima Nova is not a variable font in our kit — weight animation limited to the 400/700/900 we self-host, so lean on trails/optical motion rather than true VF interpolation. Verify before promising VF.

### Tier 3 — situational / verify before committing

**8. Subtle parallax depth on hero scenes.**
Layered transform-based parallax (CSS/GSAP, *not* Three.js) — 2–3 background layers drift at different rates on `scla-title` / `scla-statement` / `scla-outro`.
- *Why:* depth and richness on the otherwise-static navy hero cards.
- *Risk:* low if CSS-transform only. Explicitly **avoid** the Three.js/TypeGPU adapters here — heavier, and 3D risks the off-brand line. Keep it 2.5D.

**9. Richer stat visuals — progress rings / gauges / sparklines.**
Extend `scla-stat` via `data-chart` restyle: an animated ring or gauge, not only a count-up number.
- *Strengthens:* `scla-stat`.
- *Why:* a single number lands harder with a proportional visual; still one-number-is-the-point discipline.
- *Risk:* low — `data-chart` is already sanctioned; this is a new *use* of it. Restyle to tokens.

**10. Lower-thirds / name-and-role cards.** *(Confidence: `motion-graphics` does lower-thirds; confirm as a reusable component.)*
- *Strengthens:* `scla-quote` (attributed lines get a proper lower-third instead of static attribution).
- *Why:* editorial credibility on quotes.
- *Risk:* low; overlaps existing quote treatment — only worth it if quotes become common.

**Explicitly parked (not now):** cursor/pointer demos (`hyperframes-keyframes`) — only relevant if a lesson demos a UI/tool, which the concept-lesson format doesn't; revisit if product-walkthrough lessons appear.

---

## Recommended first wave (if adopting)

1. **Open captions** (Tier 1 #1) — biggest engagement + accessibility win, deterministic, touches every video.
2. **Progress indicator** (Tier 1 #2) — cheap, high completion-rate leverage.
3. **Lottie icon micro-animations** (Tier 2 #4) — the clearest "looks more polished" upgrade to the two most-used templates (points/steps).

Audio bed (#3) is a strong fourth but gated on the sound-off reframe and licensing — treat as its own decision.

## How adoption works (so this doesn't drift)

Anything approved here becomes: (a) a new row in `frame.md` → "Motion rotation" naming the recipe, and/or (b) a new capability wired into the relevant `scla-*` template(s) as CSS/timeline — **never a template fork** (frame.md rule). Log the decision in `decisions/log.md`. Captions/audio also touch `/render-lessons` (new build steps) and the deterministic gates (`render-qa/`) — those changes ride with the decision, not this doc.

## Open questions for the owner

1. **Sound-off vs. sound-on** — do we commit to open captions as standard (Tier 1 #1)? That's the pivot the whole ranking hangs on.
2. **Audio layer** — worth adding a BGM/SFX bed at all given the sound-off design, and do we have licensed tracks?
3. **Polish budget** — adopt the recommended first wave (3 items) as a batch, or pilot one on the next build and review?

---

*Reconstruction note: this replaces a lost prior-session discussion. Saved here so it survives; update in place if the owner rules on any candidate.*
