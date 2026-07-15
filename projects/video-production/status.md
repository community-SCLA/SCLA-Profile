# Video Production Pipeline — Status

**Current phase:** Illustrated pipeline live and delivering — 2 lessons published to Wistia, 2 more at MP4 review (per-scene narration synthesis landed 2026-07-14; the 5 piloted design-system upgrades promoted 2026-07-15)  
**Owner:** TODO  
**Last refreshed:** 2026-07-15 (pipeline review session)

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
- **Do Not Just Ask What AI Replaces** + **Finding/Creating a Career Purpose Statement** (Early Career Boost) — MP4s filed (verify PASS) but **owner-vetoed**: they carry the banned in-place text motion (decision 2026-07-15); need re-author + re-render on the stripped templates, back through the normal gates
- **Career-Building Is a Repeatable Process** (Early Career Boost) — live on Wistia but **publish disputed** (gate-bypass claim uncorroborated, close-out never ran) and carries the vetoed text motion — recommendation: take down + re-cut; owner ruling needed, see `refinement-log.md` row + snag-log
- **Build Direction Before You Build a Plan** (Early Career Boost) — workspace at the hyperframe gate
- **Better Decisions Come From Better Criteria** (Early Career Boost) — workspace built; **facts-provenance blocker** (lesson body/outline never filed as source — needs owner input before ship). An unlogged render attempt was aborted 2026-07-15

### Illustrated Lesson Videos (Early Career Boost)
| Video | Script | Render | Published |
|---|---|---|---|
| Mini Syllabus | Approved | Delivered 2026-07-08 (workspace archived) | Wistia pending (URL `TODO` since migration) |
| What Makes for a Dream Job | Approved | 2026-07-15, verify PASS (pilot for the 5 promoted upgrades) | **Wistia** `6g95getfl2` (owner waived MP4-review gate) |
| Career-Building Is a Repeatable Process | Approved | 2026-07-15, verify PASS | **Wistia** `zyr1fq35t7` — ⚠ publish disputed (see Active Work) |
| Do Not Just Ask What AI Replaces | Approved | 2026-07-15, verify PASS (0 warnings) | at MP4 review |
| Finding/Creating a Career Purpose Statement | Approved | 2026-07-15, verify PASS | at MP4 review |
| Build Direction Before You Build a Plan | Approved | at hyperframe gate | — |
| Better Decisions Come From Better Criteria | Approved | blocked (facts provenance) | — |

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
