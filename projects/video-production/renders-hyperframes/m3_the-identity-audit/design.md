# design.md — m3_the-identity-audit

Program: Career Transitions (from `tokens.yml programs:`)
Lesson title: The Identity Audit (from the canonical stem)
Concept: **Lens A — "The Stack"** (see CONCEPT.md)

## Carrying object

One object carries the whole lesson: a **five-band stack** at `x 120–860`,
`y 236–844`. It is present in all 31 beats at fixed coordinates and is never
redrawn. Every argument move is a *state change* on that stack:

| Beat | Stack state change |
| --- | --- |
| b01 | band 1 appears alone |
| b02 | gold rule lands on top of band 1 ("only the top layer") |
| b03 | bands 2–5 grow in beneath it, staggered downward |
| b05 / b06 / b07 | release dot (gold), not-yet dot (blue), reframe ring on three different bands |
| b08 | the three dots clear |
| b09 | numerals 1–5 land |
| b10 / b12 / b13 / b15 / b17 | that band's gold accent + its name arrive as the layer is spoken |
| b18 | numerals dim — the stack cools to a reference while the questions are asked |
| b30 | a gold end-mark lands on all five bands |
| b31 | a gold rule resolves beneath the whole stack |

The right column (`x 940–1800`) is the only surface that turns over, and it
turns over one thought at a time. Two structures there accumulate rather than
swap: the three audit questions (b20–b22) and the three rituals (b25–b27).

## Beat-to-frame map

| Beat | Narration (source sentence) | Right column | Stack |
| --- | --- | --- | --- |
| b01 | Career identity is layered. | h1 "The Identity Audit" | band 1 in |
| b02 | The role you held is only the top layer. | h2 "Only the Top Layer" | top rule |
| b03 | Underneath sit the routines… | h2 "What Sits Underneath" | bands 2–5 in |
| b04 | Here's the good news… | h2 "The Good News" + line | — |
| b05 | Some of those layers are ready to be released. | h2 "Ready to Be Released" | gold dot, band 2 |
| b06 | Some aren't yet. | h2 "Some Aren't Yet" | blue dot, band 4 |
| b07 | And some don't need to be released at all… | h2 "Some Only Need Reframing" | ring, band 5 |
| b08 | That's what this audit is for… | h2 "Sorting It Layer by Layer" + line | dots clear |
| b09 | There are five layers to audit. | h2 "Five Layers to Audit" | numerals 1–5 |
| b10 | The first is your Role or Title… | h2 "Role or Title" + line | band 1 named |
| b11 | It's often the easiest layer to release… | h2 "Easiest Outside, Hardest Inside" + line | — |
| b12 | The second is your Routines and Environment… | h2 + 4-item list | band 2 named |
| b13 | The third is your Relationships… | h2 + 4-item list | band 3 named |
| b14 | Some of your people will travel forward… | h2 "Who Travels Forward" + 2-card compare | — |
| b15 | The fourth is your Sense of Expertise… | h2 + line | band 4 named |
| b16 | This is often the hardest layer to release… | h2 + line | — |
| b17 | And the fifth is your Internal Story… | h2 + line | band 5 named |
| b18 | So how do you actually run the audit? | h2 "How to Run the Audit" | numerals dim |
| b19 | Take each layer, one at a time… | h2 "Three Questions per Layer" + note | — |
| b20–b22 | First / Second / And third… | the three questions accumulate | — |
| b23 | That last question matters more than it looks… | gold underline under question 3 + note | — |
| b24 | As Forbes reported in twenty twenty-six… | h2 "Career Grief Is Real", cite, line | — |
| b25–b27 | A written letter / A curated list / A quiet dinner | the three rituals accumulate | — |
| b28 | These are not soft, optional extras. | h2 "Not Soft, Optional Extras" | — |
| b29 | They are evidence-based practices… | h2 "Evidence-Based Practices" + line | — |
| b30 | So work the audit layer by layer… | h2 "Layer by Layer" + 3-item list | end-marks |
| b31 | That's how you close this chapter well… | h2 "Close This Chapter Well" + line | base rule |

## Motion logic

Establish → transform → settle, once per element and never again.

- Beat copy enters on opacity + a 18px rise, 0.5s, 0.14s stagger, starting
  0.12s after the beat's visual start — settled well inside the beat.
- Persistent stack elements enter the same way, 0.15s after their cue beat.
- Exits are opacity-only, 0.3s, right column only. Furniture never moves again.
- The closing rule is the one scale move in the build (`scaleX` 0 → 1).
- **No tween in this composition carries `repeat` or `yoyo`.** There is no
  ambient, keep-alive or looping motion anywhere.

All cue times are read from the DOM at runtime — every tween is positioned from
the `data-start` of the beat it belongs to, and those values come from
`timing.json` and are never hand-tuned.

## Geometry against tokens.yml

- canvas 1920×1080; safe-area 72; frame-padding 120; content-bottom 960.
- All content sits inside `x 120–1800`, `y 222–881`.
- The only element in the outer band is the program eyebrow at
  `x 120–~450, y 56–88`, which lies inside the declared chrome region
  `100,50,700,110`.
- Palette and typeface come only from the workspace `tokens.yml`; the vendored
  Proxima Nova 400/700/900 faces are loaded from `assets/fonts/`.

## Note on the provider intermediate

`scripts/video-audio.sh` batches the 31 beats into one provider request whose
raw response lands at `assets/voice/narration.wav`, then splits it into the 31
per-beat clips that `audio_meta.json` declares and `plan_timing.py` normalises.
The raw pre-split chunk is retained at `assets/voice/source/narration.wav` —
it is provenance, not a timeline asset: the composition's audio is the 31
per-beat clips placed at their `timing.json` `audio_start` values.
