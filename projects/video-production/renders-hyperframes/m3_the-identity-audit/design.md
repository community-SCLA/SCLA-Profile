# design.md — m3_the-identity-audit

Program: Career Transitions (from `tokens.yml programs:`)
Lesson title: The Identity Audit (from the canonical stem)
Concept: **Lens A — "The Stack"** (see CONCEPT.md)

## Carrying object

One object carries the whole lesson: a **five-band stack** at `x 120–860`,
`y 236–844`. It is present in all 27 beats at fixed coordinates and is never
redrawn. Every argument move is a *state change* on that stack:

| Beat | Stack state change |
| --- | --- |
| b01 | band 1 appears alone |
| b02 | gold rule lands on top of band 1 ("only the top layer") |
| b03 | bands 2–5 grow in beneath it, staggered downward |
| b05 / b06 / b07 | release dot (gold), not-yet dot (blue), reframe ring on three different bands |
| b08 | the three dots clear |
| b08 (+4.6s) | numerals 1–5 land |
| b08 (+9.0s) / b12 / b13 / b15 / b17 | that band's gold accent + its name arrive as the layer is spoken |
| b18 | numerals dim — the stack cools to a reference while the questions are asked |
| b29 (+5.4s) | a gold end-mark lands on all five bands and the numerals relight |
| b31 | a gold rule resolves beneath the whole stack |

The right column (`x 940–1800`) is the only surface that turns over, and it
turns over one thought at a time. Two structures there accumulate rather than
swap: the three audit questions (b20–b22) and the three rituals (b25–b27).

## Beat-to-frame map

27 beats. A beat is a synthesis unit, not a frame: three of them carry more than
one sentence and stage their visuals across the beat (see "Why 27 and not 31").

| Beat | Narration (source sentences) | Right column | Stack |
| --- | --- | --- | --- |
| b01 | Career identity is layered. | h1 "The Identity Audit" | band 1 in |
| b02 | The role you held is only the top layer. | h2 "Only the Top Layer" | top rule |
| b03 | Underneath sit the routines… | h2 "What Sits Underneath" | bands 2–5 grow in, one per spoken clause, across the whole beat |
| b04 | Here's the good news… | h2 "The Good News" + line | — |
| b05 | Some of those layers are ready to be released. | h2 "Ready to Be Released" | gold dot, band 2 |
| b06 | Some aren't yet. | h2 "Some Aren't Yet" | blue dot, band 4 |
| b07 | And some don't need to be released at all… | h2 "Some Only Need Reframing" | ring, band 5 |
| b08 | That's what this audit is for… / There are five layers to audit. / The first is your Role or Title… | h2 "Sorting It Layer by Layer" + line | dots clear; numerals 1–5 land at +4.6s; band 1 accent + name at +9.0s |
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
| b23 | That last question matters more than it looks… | gold bar beside question 3 + note | — |
| b24 | As Forbes reported in twenty twenty-six… | h2 "Career Grief Is Real", cite, line | — |
| b25–b26 | A written letter / A curated list | the rituals accumulate | — |
| b27 | A quiet dinner with a colleague… / These are not soft, optional extras. | third ritual, then the statement line at +3.4s | — |
| b29 | They are evidence-based practices… / So work the audit layer by layer… | h2 "Evidence-Based Practices" + line; rituals clear at +4.6s and the three-verb recap arrives from +5.8s | end-marks on all five bands, numerals relight, from +5.4s |
| b31 | That's how you close this chapter well… | h2 "Close This Chapter Well" + line | base rule resolves at +5.2s |

## Why 27 and not 31

The lesson was first cut one sentence per beat (31 beats). Four of those beats
failed `check_boundaries`: HeyGen's word-end timestamp for `down.`, `audit.`,
`chapter.` and `cleanly.` runs 0.22–0.41s past the last audible sample, so the
beat's visual cut landed less than the required 0.2s after the (over-stated)
spoken end. The provider timestamps are not tunable and hand-editing a timestamp
is forbidden, so the fix is structural: those four sentences were folded into
the beat that follows, until each beat ends on a word whose timestamp matches
its audio. That produced beats `b08` (3 sentences), `b27` and `b29`
(2 sentences each); their extra sentences are staged inside the beat with
explicit cue offsets rather than given their own frame. Measured margin after
the change: every non-final beat clears the 0.2s floor, tightest at 0.21s.

## Motion logic

Establish → transform → settle, once per element and never again.

- Beat copy enters on opacity + an 18px rise, 0.5s each. The stagger is derived
  from the beat's own duration (entrances span ~half the beat, capped at 3.2s
  apart) so no shot sits frozen: the pinned `hyperframes check` motion pass
  reports 0 frozen spans against a 5s ceiling.
- An element carrying `data-lag` enters at that explicit offset instead, which
  is how the multi-sentence beats stage their second and third ideas.
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

`scripts/video-audio.sh` batches the 27 beats into one provider request whose
raw response lands at `assets/voice/narration.wav`, then splits it into the 27
per-beat clips that `audio_meta.json` declares and `plan_timing.py` normalises.
The raw pre-split chunk is retained at `assets/voice/source/narration.wav` —
it is provenance, not a timeline asset: the composition's audio is the 27
per-beat clips placed at their `timing.json` `audio_start` values. Moving it out
of `assets/voice/` also stops the coverage gate comparing the whole 140s chunk
against the first beat's `<audio data-duration>`.

A background bed was retrieved by the shared audio engine to
`assets/bgm/track.mp3`, but it is 98s against a 152s runtime, so it is **not**
wired into the composition: a mid-video loop seam is an audible defect I cannot
review from stills, and no gate or contract requires a music bed. The asset is
on disk if the owner wants one added.
