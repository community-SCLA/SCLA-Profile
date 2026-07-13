# Video Production Pipeline — Status

**Current phase:** Illustrated pipeline live and delivering (first video shipped; pipeline overhauled 2026-07-09 — CLI 0.7.45 removed the manual bake step, renders now come straight from `index.html` scene values)  
**Owner:** TODO

---

## Setup Checklist

### Synthesia
- [ ] Verify subscription tier (Enterprise required for bulk volume)
- [ ] Create SCLA Brand Kit (logo, gold `#eaab2d`, blue `#3393d6`, fonts)
- [ ] Create/select SCLA course avatar
- [ ] Build 3 master templates: Course Video · Certificate Video · Learning Activity
- [ ] Test bulk CSV import with 3 sample scripts
- [ ] Contact Synthesia sales re: nonprofit pricing

### HeyGen
- [ ] Verify subscription tier (Business or Enterprise)
- [ ] Record 2-min voice sample for cloning (quiet room, external mic)
- [ ] Create cloned voice — test output quality
- [ ] Build 3 templates: Short-form Social · Learning Activity · Company Tour narration
- [ ] Configure Instant Avatar (optional — 2-min webcam recording)
- [ ] Test Video Agent with 3 prompts
- [ ] Contact HeyGen sales re: education pricing

### Hosting / analytics (Wistia)
- [x] Decide hosting/analytics platform — **Wistia** (account URL: `endpoints.md` → "Wistia"); decided 2026-07-08 (`decisions/log.md`)
- [ ] Set up channel/folder structure matching content
- [ ] Configure player branding (SCLA colors, logo)
- [ ] Generate API key and test embed codes in the course platform

### Zapier Automations
- [ ] Zap 1: HeyGen video complete → upload MP4 to Wistia
- [ ] Zap 2: Wistia upload complete → Slack #video-production notification
- [ ] Zap 3: Google Sheet row added → HeyGen batch trigger (optional)
- [ ] Zap 4: HeyGen translation complete → Wistia with language tag (optional)

### Claude Prompt Library
- [ ] Share course-script-prompt.md with all content creators
- [ ] Share social-script-prompt.md with social team
- [ ] Share qa-checklist.md with editors
- [ ] Share batch-csv-template.md with ops

---

## Production Status

### Active Work
- **Build Direction Before You Build a Plan** (Early Career Boost) — assembled in `renders-hyperframes/`, pre-QA
- **Better Decisions Come From Better Criteria** (Early Career Boost) — script approved + narration generated; assembly not started (also serves as design-system demo-reel content)

### First 5 AI Videos (Month 1 Goal)
| Video | Course | Script Status | Render Status | Published |
|---|---|---|---|---|
| Mini Syllabus | Early Career Boost | Approved | Delivered (`lesson-scripts/early-career-boost/`, workspace archived) | Wistia pending |
| Build Direction Before You Build a Plan | Early Career Boost | Approved | Pre-QA | — |
| Better Decisions Come From Better Criteria | Early Career Boost | Approved | Not assembled | — |

### Blockers
- [ ] **HeyGen API key has no API permission** — every endpoint returns 403 ("Ask your Space Admin"). Blocks `avatar-pipeline/` renders AND HeyGen TTS for illustrated videos (local Kokoro voice covers the gap). Fix: Space Admin grants API access, or `npx hyperframes auth login`.
- [ ] Enterprise tier confirmation (Synthesia) — only if long-form avatar courses survive re-evaluation
- [ ] Voice clone recording not yet done (avatar path)

---

## Ramp Schedule

| Phase | Timeline | Milestone |
|---|---|---|
| Month 1 | TBD | Foundation setup, first 5 AI videos |
| Month 2 | TBD | First full 44-video course batch |
| Month 3 | TBD | First translation run, social pipeline live |
| Month 4+ | TBD | Full 30 hr/month pipeline running |

---

## Vendor Contacts Log

| Date | Vendor | Contact Type | Outcome |
|---|---|---|---|
| — | Synthesia | — | — |
| — | HeyGen | — | — |
