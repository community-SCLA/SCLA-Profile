# Brief — Hybrid composite: HeyGen avatar + HyperFrames on-screen overlays

**For:** a future diff session (net-new build). **Owner:** community@thescla.org.
**Status:** not started — scoped 2026-07-22, deferred by owner from the
Mid-Career Momentum pipeline setup.

## Goal

Produce lesson videos that show **Ann (HeyGen avatar) speaking** *and* carry the
script's **production notes as on-screen text/illustrations** — the one thing
neither current path does alone. Today: the avatar path
([`avatar-pipeline/`](avatar-pipeline/CLAUDE.md)) renders a talking head and
**drops** every `[On screen:]` / `[Graphic:]` cue; the illustrated path
([`design-system/`](design-system/CLAUDE.md) via `/render-lessons`) renders the
cues as motion graphics but has **no avatar**. This build marries the two.

## Why this is a separate build, not a config change

The avatar pipeline calls HeyGen's `POST /v3/videos` with plain narration and
gets back a finished MP4 — HeyGen does not composite arbitrary branded graphics
from our cues. So overlays have to be composited **after** the avatar render, in
HyperFrames, where we already own timed branded motion. That's a new
composition pattern (avatar as a media layer + cue-driven overlays), plus a
timing bridge — real work, gated like any other lesson video.

## Approach (recommended)

1. **Render the avatar clip** via `avatar-pipeline/` — the pure-narration `.txt`
   for the lesson. Prefer a HeyGen output that eases compositing: transparent /
   green-screen background if the account/avatar supports it, else a plain
   full-frame render. (If green-screen: `hyperframes remove-background` or the
   `media-use` background removal can key it — see `hyperframes-media`.)
2. **Author a HyperFrames composition** (`hyperframes-core`) that plays the
   avatar MP4 as a **framework-owned media layer** (a `<video>` track, seek-safe
   — do NOT hand-animate it) and layers the production notes above it as timed
   `scla-*` overlays: lower-thirds, side cards, callouts, stat rings — drawn on
   the brand tokens in [`design-system/frame.md`](design-system/frame.md).
   Decide the frame split up front (avatar right-third / lower-third vs.
   full-frame with lower-third overlays) — this is the main creative call.
3. **Bridge the timing.** Overlays must land on the words that motivate them.
   The avatar MP4's narration timing isn't authored by us, so derive it:
   transcribe the rendered avatar clip (`npx hyperframes transcribe`, the same
   Whisper step the illustrated path already uses) to get word timings, then
   anchor each cue to its phrase. (Check whether HeyGen can return caption/word
   timestamps for the avatar render directly — if so, prefer that over Whisper,
   same as the TTS-swap entry in `decisions/log.md`, 2026-07-22.)
4. **Gate it** through the existing render-qa stack (`preflight.py`,
   `verify_render.py`, and `qa-presence`, which already checks avatar-visible
   -throughout on avatar videos), then the human hyperframe gate → MP4 review →
   Wistia, exactly like every other lesson video.

## Inputs the notes provide

The refined/illustrated script keeps its cues and shot list (that's why
production-notes lessons route to the illustrated side, not the avatar `.txt`).
Each `[On screen:]` (text/data) and `[Graphic:]` (diagram/card) cue, plus the
shot-list line, is one overlay to place. Cue convention lives in
[`script-templates/heygen-lesson-script.md`](script-templates/heygen-lesson-script.md).

## Naming & foldering

The deliverable is a HyperFrames render (with an avatar layer), so it files to
`renders-mp4/<program-slug>/hyperframes/` under the universal
`m<#>_<title>_<render-date>.mp4` convention — **unless** the owner wants a third
sibling subfolder (e.g. `hybrid/`) to distinguish it. Confirm at kickoff.

## Watch-outs

- **Seek-safety:** the avatar clip is a fixed media asset — HyperFrames plays it
  on the single paused timeline. Never re-time or re-animate the avatar itself;
  overlays are the only authored motion (`hyperframes-core` media rules).
- **Timing drift:** Whisper word timestamps are ±30–100ms (the exact issue
  behind the 2026-07-14 per-scene-TTS rebuild). Anchor overlays to phrase onsets
  with a little lead, and expect `qa-timing` to police it.
- **Animacy doctrine still applies:** overlays obey the in-place-motion ban
  (`decisions/log.md`, 2026-07-15) — staged entrances on cue, no idle jitter of
  settled content.
- **Presence:** the avatar must be visible throughout on these (they're avatar
  videos) — `qa-presence` will fail an overlay that fully occludes Ann.
- **Cost:** ~1 HeyGen credit per ~10s of avatar render (quota 15000, per
  `endpoints.md`); the HyperFrames overlays add no per-minute credit.

## Acceptance

One Mid-Career Momentum lesson built end-to-end as a hybrid, passing all
deterministic gates + the human hyperframe gate, with a repeatable composition
pattern documented back into `design-system/` (or a note in `frame.md`) so the
next hybrid is a copy, not a re-invention.

## Pointers

- Avatar render: [`avatar-pipeline/CLAUDE.md`](avatar-pipeline/CLAUDE.md)
- Composition contract + media layers: `hyperframes-core`, `hyperframes-creative`
- Background removal / transcription: `hyperframes-media`
- Brand tokens + templates: [`design-system/frame.md`](design-system/frame.md)
- Gates: [`render-qa/README.md`](render-qa/README.md)
