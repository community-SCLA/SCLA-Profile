# Video QA Checklist

Run this checklist on every video before publishing to Wistia. Human review is required — this step cannot be skipped or automated.

---

## Standard QA (All Videos)

### Script & Content
- [ ] All facts, statistics, and program details are accurate
- [ ] No hallucinated or invented SCLA-specific content
- [ ] Tone matches SCLA brand voice (warm, professional, encouraging)
- [ ] No jargon that target audience (college students 18–24) wouldn't know
- [ ] CTA is clear and the linked URL/action is correct

### Technical Quality
- [ ] Audio is clear — no background noise, clipping, or distortion
- [ ] No sudden volume jumps between scenes
- [ ] Video resolution is 1920×1080 (HD)
- [ ] No watermarks visible (verify subscription tier allows export)
- [ ] Runtime matches target length (±10%)

### Visual Quality
- [ ] Avatar lip sync is accurate throughout — no obvious mismatches
- [ ] B-roll / motion graphics appear at correct moments
- [ ] No frozen frames or rendering artifacts
- [ ] SCLA branding visible (logo, colors `#eaab2d` / `#3393d6`)
- [ ] Text overlays are readable and correctly spelled

### Accessibility
- [ ] Captions are generated on upload to Wistia (verify after upload)
- [ ] No critical information conveyed by color alone
- [ ] Speaker pace is appropriate (not too fast for comprehension)

---

## Extended QA (Courses & Certificate Videos)

- [ ] Learning objectives stated in opening scene
- [ ] Key terms defined clearly on first use
- [ ] Examples are relevant to college student audience
- [ ] Transition to next video is clear
- [ ] Video number and course name visible in opening frame
- [ ] Length is appropriate for content complexity (not padded)

---

## Illustrated Video QA (HyperFrames / design-system)

- [ ] Deterministic gates green on this exact render: `render-qa/preflight.py` (pre-render) and `render-qa/verify_render.py` (post-render) both exit 0; every scene carries `data-anchor-end` (timing is compiled, never hand-typed)
- [ ] Builder frame review done on this exact render — `qa/frames/` dump (3 stills per scene) checked against the transcript; if an `/adversarial-qa` deep audit was run, every launched lane returned PASS and reports are attached
- [ ] `npm run check` passes with 0 errors (lint + validate + inspect)
- [ ] Frames reviewed by a human at **several points per scene** (start, mid, late) — one midpoint still can't reveal a stagnant frame
- [ ] Design tokens match `design-system/frame.md` — no off-palette colors, Proxima Nova renders (not a fallback sans)
- [ ] Narration voice matches the pinned voice in `frame.md` (no silent provider drift)
- [ ] On-screen text is synced to the narration (right words visible while spoken)
- [ ] Video teaches with sound OFF — on-screen text carries the key moves
- [ ] Scene templates instantiated via variables, not forked copies
- [ ] One style package throughout — every scene's `theme` variable matches the assigned package (summit/horizon/cadence), no mixed looks

### Animacy & illustration (`frame.md` → "Every scene earns its seconds")
- [ ] **No stagnant frame beyond ~2s** — every scene keeps developing across its full duration; no title card or slide parked static over ongoing narration
- [ ] **Reveals hit the spoken cue** — enumerated items appear as the narration says them (`pointCues` / `stepCues` mapped from word timings), not on an even timer
- [ ] **Illustration depicts the narration** — each scene *shows* the idea, not just labels it; nothing generic that ignores the sentence being spoken
- [ ] **Statements aren't quotes** — quotation treatment (`scla-quote`) only on a **named person's** words; program/SCLA theses use `scla-statement`
- [ ] **Numerals read right** — scene index is small in the lower-right; any large numeral is a genuine stat or the spoken step, never a slide number or a bare cardinal

### Pacing, cuts & endings (`frame.md` → "Scene boundaries, padding & endings")
- [ ] **Every cut lands ≥0.5s after the scene's last spoken word ends** — verify against `transcript.json`; no scene cuts mid-word or mid-sentence
- [ ] **Questions finish their inflection** before the cut (extra air after a question mark)
- [ ] **The video ends on populated content** — final scene outlives the narration (check the wav's true duration with `ffprobe`) and holds its text ≥1s after the last word; no bare-canvas tail, no clipped audio
- [ ] **Opening enumeration has its own scene** — the title card is off before the narration starts listing; listed items land as a kinetic reveal on their cues
- [ ] **Reveal forms vary** — consecutive list scenes use different forms (chips pop / slide-in / numbered points / grid); a steps overview appears only where the narration enumerates the steps
- [ ] **Statements ≥~6s don't sit static** — no per-word emphasis; the template's built-in reading ripple + late-phase resolve should be enough, no bare held sentence

---

## Translation QA (Multilingual Videos)

- [ ] Translated audio sounds natural — not robotic or stilted
- [ ] Lip sync matches translated language cadence
- [ ] Cultural references are appropriate for target region
- [ ] On-screen text has also been translated (not just voiceover)
- [ ] Subtitle timing matches translated speech

**For Spanish translations:** Ask a native speaker to review before publishing. Do not rely on Claude alone.

---

## If the Video Fails QA

| Issue | Fix |
|---|---|
| Lip sync off | Regenerate affected scenes only (don't re-render entire video) |
| Script error | Edit script in Synthesia/HeyGen editor → regenerate scene |
| Audio quality issue | Check source voice/clone settings; regenerate with adjusted parameters |
| Branding missing | Update template → re-render (template fix benefits all future videos) |
| HeyGen stall (stuck at 33% or 50%) | Resubmit the job — documented platform bug |
| Wrong length | Trim script to target word count (target: 130 words ≈ 1 minute) |

---

## QA Sign-Off

Before publishing to Wistia, record completion:

| Field | Value |
|---|---|
| Video title | |
| Reviewer name | |
| Review date | |
| Pass / Fail | |
| Notes | |
