# Video QA Checklist

Run this checklist on every video before uploading to Wistia. Human review is required — this step cannot be skipped or automated.

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
- [ ] Captions will be auto-generated on Wistia upload (verify after upload)
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

Before uploading to Wistia, record completion:

| Field | Value |
|---|---|
| Video title | |
| Reviewer name | |
| Review date | |
| Pass / Fail | |
| Notes | |
