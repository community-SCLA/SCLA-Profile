# AI-Powered Video Production Guide
## SCLA · Synthesia + HeyGen + Wistia + Claude

**Active subscriptions:** Synthesia ✓ · HeyGen ✓ · Wistia ✓

---

## Quick Reference: What Does What

| Tool | Primary Role in SCLA Pipeline |
|---|---|
| **Claude** | Script generation, QA reviews, workflow automation, bulk CSV prep |
| **Synthesia** | AI avatar training/course videos (structured, longer-form) |
| **HeyGen** | AI avatar short-form videos, translation/dubbing, personalized outreach |
| **Wistia** | Video hosting, course library, analytics, embedding |

---

## Part 1: Your Production Scale (Know Your Numbers)

Based on the SCLA video production planning document, here's what you're building toward:

### Monthly Volume

| Month | Video Hours | Courses | Certificates | Learning Activities | Social | Company Tour | Events | Selling |
|---|---|---|---|---|---|---|---|---|
| May, Sep, Oct | ~16 hrs | 4 | 5 | 8 | 14 | 4 | 3 | 2 |
| Jun, Jul, Aug, Nov | **~30 hrs** | 8 | 10 | 15 | 22 | 8 | 6 | 4 |

### What "30 hours of video" Actually Means

- 30 hours = **1,800 minutes** of finished video per peak month
- At 44 videos per course × 2–7 min each = 88–308 minutes **per course** 
- Social media: 22 videos × 60–90 sec = 22–33 minutes
- Company Tour: 8 videos × 8 min each = 64 minutes

### The Critical Scale Reality

> **Synthesia's Creator plan allows 30 min/month. HeyGen's Creator plan allows ~10 min of premium Avatar IV video per month.**
>
> At 1,800 min/month target, **you will need Enterprise-tier on whichever platform handles course video bulk.** Plan for this budget conversation before scaling. Both platforms require contacting sales for nonprofit/education pricing — do this now, before committing to a pipeline.

---

## Part 2: Video Types & AI Suitability

### Which Videos Can AI Fully Handle vs. Partially vs. Not At All

| Production Type | AI-Suitable? | Best Tool | Human Required For |
|---|---|---|---|
| **AI Actor + B-Roll & Graphics** | ✅ Fully | Synthesia or HeyGen | Script approval, first-run QA |
| **Screen Recording Style** | ✅ Mostly | HeyGen (voiceover) + manual screen capture | Screen recording itself |
| **AI Voiceover (any style)** | ✅ Fully | Synthesia or HeyGen voice | Script approval |
| **Live Actor + Screen Recording + B-Roll** | ⚠️ Partial | Wistia (hosting only) | Full filming, editing |
| **Live Actor + B-Roll & Graphics** | ⚠️ Partial | Wistia (hosting only) | Full filming, editing |
| **Social Media Videos** | ✅ Mostly | HeyGen short-form | Script/concept approval |
| **Company Tour Videos** | ⚠️ Partial | HeyGen (AI narration layer) | Footage of actual facilities |
| **Event Videos** | ❌ Manual | Wistia (hosting) | Live filming, editing |
| **Infomercial Style** | ✅ Mostly | Synthesia or HeyGen | Script, branding review |

### Recommended Default Tool by Video Type

| Video Type | Recommended Tool | Why |
|---|---|---|
| Courses & Certificate courses | **Synthesia** | Better avatar consistency for 5–15 min training videos; SCORM export (Enterprise); structured learning templates |
| Learning Activities (shorter) | **HeyGen** | More expressive avatars for shorter content; Video Agent auto-generates from prompt |
| Social Media (60–90 sec) | **HeyGen** | Faster turnaround; more engaging avatar expressiveness; 700+ social templates |
| Translation of any finished video | **HeyGen** | 175+ languages with lip-sync; bulk translate via CSV; stronger multilingual pipeline |
| Hosting & distribution (all videos) | **Wistia** | All finished videos from any tool upload here for hosting, analytics, and embedding |

---

## Part 3: The 6-Step SCLA Production Process → Where AI Fits

Your current production process maps like this:

```
Step 1: Style Sheet Completed        → MANUAL (define once per video type, reuse)
Step 2: Script Finalized & Approved  → AI-ASSISTED (Claude drafts, human approves)
Step 3: Graphics and Photos Chosen   → AI-ASSISTED (Synthesia/HeyGen templates + brand kit)
Step 4: Video Created & Placed       → AUTOMATED (Synthesia or HeyGen renders)
Step 5: Audio Voice-Over Created     → AUTOMATED (AI voice built into Step 4)
Step 6: Review and Approve           → MANUAL (always — quality gate)
```

The biggest time savings come from collapsing Steps 2–5 into a single automated pipeline once Step 1 (style sheet/template) is set up. Each video type only needs one setup investment.

---

## Part 4: Step-by-Step Workflows

---

### Workflow A: Course / Certificate Video (AI Actor + B-Roll Style)
*Target: 5–15 min training videos, structured learning content*
*Tool chain: Claude → Synthesia → Wistia*

**Estimated time per video after first template setup: 30–60 min human effort**

#### Step 1 — Script Generation (Claude)

Open Claude Code or claude.ai and use a prompt like:

```
I'm creating a training video for an SCLA course called [Course Name].
The audience is college students preparing for [topic].
The video should be [X] minutes long, structured as:
1. Hook / Problem Statement
2. Key Concept Explanation
3. Practical Example or Story
4. Key Takeaways
5. Call to Action

Tone: Warm, professional, encouraging. SCLA voice (see brand guidelines).
Format: Write each scene as a separate paragraph. Include [B-ROLL: description] markers
where motion graphics would appear. Keep each paragraph to ~30 seconds of speaking time.

Topic: [paste your course content or outline here]
```

Claude will return a scene-by-scene script with B-roll markers. **Human review required before proceeding.**

#### Step 2 — Build/Reuse Synthesia Template

First time only (one-time setup per course style):
1. Log into Synthesia → **New Video** → **Choose Template**
2. Pick an educational/training template that matches your style sheet
3. Set brand colors (SCLA gold `#eaab2d`, blue `#3393d6`)
4. Select your preferred avatar (stock avatar, or upload a custom one)
5. Save as a **Brand Kit** — this becomes the reusable template for all course videos

For each new video:
1. Open your saved template → **Duplicate**
2. Paste the Claude-generated script into scene fields
3. Place B-roll markers using Synthesia's media library or upload your own assets

#### Step 3 — Generate Video (Synthesia — AUTOMATED)

Click **Generate** — Synthesia renders the video. At Enterprise tier: multiple videos can render concurrently.

**Expected render time:** ~5–15 minutes per finished minute of video.

Receive email/in-app notification when done.

#### Step 4 — QA Review (Human — REQUIRED)

Watch the complete video. Check:
- [ ] Script accuracy — no hallucinated facts
- [ ] Avatar lip sync quality
- [ ] B-roll / graphics appropriate timing
- [ ] SCLA branding consistent
- [ ] Audio levels balanced
- [ ] Length matches target

If revisions needed: Edit script in Synthesia editor, regenerate only changed scenes (faster than full re-render).

#### Step 5 — Export and Upload to Wistia

1. Synthesia: **Download MP4** (or at Enterprise, use SCORM export for LMS)
2. Wistia: Drag-and-drop upload to the appropriate folder/channel
3. Wistia auto-generates: transcript, captions, AI chapters, embed code
4. Set access control (public, password, or gated)
5. Embed in your course platform or share link

---

### Workflow B: Learning Activity / Short Video (AI Actor, under 3 min)
*Target: Micro-learning, module intros, concept explainers*
*Tool chain: Claude (optional) → HeyGen → Wistia*

**Estimated time per video after first template setup: 15–30 min human effort**

#### Option 1 — HeyGen Video Agent (Fastest)

1. Log into HeyGen → **Video Agent**
2. Type a prompt:
   ```
   Create a 90-second training video for SCLA college students about [topic].
   Tone: energetic and professional. Use a diverse, professional-looking avatar.
   End with: "Visit your SCLA dashboard to complete the activity."
   ```
3. HeyGen generates script, selects visuals, picks avatar, creates voiceover — **FULLY AUTOMATED**
4. Review output (human QA) → adjust if needed → approve
5. Download and upload to Wistia

#### Option 2 — Script + HeyGen Avatar Studio (More Control)

1. Generate script in Claude (same prompt structure as Workflow A, shorter)
2. HeyGen → **Avatar Studio** → select avatar + voice
3. Paste script → Generate → QA → export to Wistia

---

### Workflow C: Social Media Videos (60–90 sec)
*Target: Instagram, TikTok, LinkedIn, YouTube Shorts*
*Tool chain: HeyGen → direct publish or Wistia*

**Estimated time per video: 15–20 min human effort**

1. Claude → generate a 60-second script optimized for social:
   ```
   Write a 60-second social media script for SCLA's [platform] audience.
   Topic: [X]. Hook in first 3 seconds. End with a clear CTA.
   Format: Short punchy sentences. No jargon. One idea per line.
   ```
2. HeyGen → 700+ templates → choose "Social" category → select vertical (9:16) or square (1:1) format
3. Paste script → select avatar → generate
4. Review → export → post directly or upload to Wistia for tracking

**Tip:** For social videos, HeyGen's Batch Mode lets you create multiple variations (different avatars, slight script changes) from one CSV. A/B test which avatar performs better.

---

### Workflow D: Translation / Multilingual Videos (Any Finished Video)
*Target: All course/certificate videos in additional languages*
*Tool chain: HeyGen Video Translation → Wistia (update existing)*

**Estimated time per video: 5 min human effort + automated render**

1. Start from any **finished MP4** (from Synthesia, HeyGen, or traditional production)
2. HeyGen → **Video Translate** tab
3. Upload your MP4 → select target language(s) — choose from 175+ options
4. Select translation mode:
   - **Hyperrealistic** (recommended): Full AI lip-sync re-animation — avatar's mouth visibly speaks the new language. Best for avatar videos.
   - **Audio Dubbing**: Voice-only translation — mouth doesn't move. Works for live-actor footage.
5. Submit → AUTOMATED render (~5 min per minute of video)
6. Review translated output (human QA — check for tone accuracy, cultural appropriateness)
7. Upload to Wistia → add as a new media item linked to the original course

**Bulk translation workflow (many videos at once):**
1. Prepare a CSV: `video_url, target_language_code, output_name`
2. Use HeyGen API bulk endpoint (`/v2/video_translate`) — or set up a Make.com scenario
3. Batch generates all language variants concurrently (up to 10 simultaneous)
4. Completed videos auto-upload to Wistia via Zapier

---

### Workflow E: Screen Recording Videos
*Target: Software tutorials, platform walkthroughs, how-to guides*
*Tool chain: Screen recorder → HeyGen (voice layer) → Wistia*

**AI can handle voiceover; screen recording is always manual**

1. **Record screen** using Loom, OBS, or QuickTime (MANUAL — cannot be automated)
2. Edit recording if needed (cut mistakes, add highlights)
3. Claude → generate narration script matching the screen actions
4. HeyGen → **Avatar Studio** → Upload your screen recording as the background
   - OR: Use HeyGen's avatar as a picture-in-picture overlay on the screen recording
5. Voiceover generated from script → synced to video
6. Export → upload to Wistia

**Alternative:** Use a cloned voice in HeyGen. If an SCLA team member records 2 minutes of clean audio once, their voice can narrate all future screen recordings automatically — no re-recording needed.

---

### Workflow F: Batch Course Production (High Volume)
*Target: Producing 44-video course libraries efficiently*
*Tool chain: Claude (CSV gen) → Synthesia bulk API or HeyGen Batch Mode → Wistia*

This workflow is for when you're building out a full course at once.

#### Step 1 — Generate All Scripts at Once (Claude)

```
I'm creating a complete course with 44 videos for SCLA. 
Here is the course outline: [paste outline]

For each section, write a [2-4 min] script following this structure:
- Scene 1: Hook + learning objective (30 sec)
- Scene 2: Core concept explanation (60-90 sec)
- Scene 3: Example or application (60-90 sec)  
- Scene 4: Summary + transition to next video (30 sec)

Format the output as a CSV with columns:
video_number, video_title, scene_1_script, scene_2_script, scene_3_script, scene_4_script

Use SCLA's warm, professional, encouraging voice throughout.
```

Claude returns a complete CSV of all 44 video scripts.

#### Step 2 — Bulk Generate in Synthesia

1. Synthesia → your course template (from Workflow A setup)
2. Upload the script CSV
3. Map CSV columns to scene slots in the template
4. Submit batch → Synthesia generates all 44 videos concurrently (Enterprise tier)
5. Receive notification when all are done
6. Spot-check 5–10 videos for QA (not all 44 unless resources allow)

#### Step 3 — Bulk Upload to Wistia

1. Wistia Upload API: Use a simple script or Zapier to upload all MP4s at once
2. Set metadata (title, description) from the original CSV
3. Wistia auto-organizes into the correct channel/folder
4. Embed codes generated automatically for each video

---

## Part 5: Claude's Specific Roles in the Pipeline

Claude can handle multiple distinct jobs in this workflow:

### 1. Script Generation
Best prompt pattern:
```
Audience: [SCLA college student members, age 18-24]
Course: [Course name]
Video: [Video number and title]
Duration: [X minutes]
Style: [AI avatar / voiceover only / screen recording narration]
Tone: Warm, professional, encouraging. Avoid jargon. Active voice.
Source material: [paste course content, outline, or notes]

Write a scene-by-scene script. Mark [B-ROLL: description] where motion graphics belong.
Each scene should be ~30 seconds of narrated content.
```

### 2. Script QA / Fact Check
After AI generates scripts (especially from HeyGen Video Agent):
```
Review this AI-generated script for an SCLA training video.
Check for: factual accuracy, tone alignment with SCLA brand, 
any claims that need verification, unclear instructions, or awkward phrasing.
Flag anything that needs human review before production.

Script: [paste script]
```

### 3. Bulk CSV Preparation
Ask Claude to format scripts into the exact CSV structure Synthesia or HeyGen's batch import requires. This eliminates manual data entry for large course builds.

### 4. Translation Review
After HeyGen translates a video, ask Claude to review the translated transcript:
```
Review this Spanish translation of an SCLA training video transcript.
Check for: accuracy, natural phrasing for Latin American college students, 
any cultural references that need adaptation, and SCLA brand tone.

Original English: [transcript]
Spanish translation: [transcript]
```

### 5. Wistia Metadata Generation
```
Generate Wistia metadata for these 44 course videos:
- Video title (SEO-friendly, under 60 chars)
- Description (2-3 sentences, include keywords)
- Tags (5-7 per video)
- Chapter markers (based on script scenes)

Course: [name]
Videos: [paste script CSV]
```

### 6. Production Status Tracking
Claude can maintain a production tracker in Notion or a spreadsheet, tracking which videos are in which stage of the pipeline (scripted, in render, in QA, uploaded, published).

---

## Part 6: Manual vs. Automated — Complete Reference

### Always Manual (Cannot Be AI-Automated)

| Task | Why It's Manual | Who Does It |
|---|---|---|
| Live actor filming | Requires a real human on camera | Video team / contractor |
| Screen recording | Must capture real-time computer actions | Content creator |
| Style sheet creation | Strategic brand decision | Design / brand team |
| Script approval | Accuracy and brand gate | Content owner |
| Final video QA | Quality and factual accuracy | Editor / content lead |
| Avatar selection (first time) | Brand representation decision | Brand team |
| Template setup (first time) | One-time configuration | Ops / video team |
| Clean voice recording (for cloning) | Requires a quiet environment + human | Speaker (one-time) |
| Pricing negotiation with vendors | Relationship/contract work | Leadership |

### AI-Automated (With Proper Setup)

| Task | Tool | Setup Required |
|---|---|---|
| Script generation (draft) | Claude | Prompt template |
| AI voiceover from script | Synthesia / HeyGen | Avatar/voice selected |
| Avatar video rendering | Synthesia / HeyGen | Template ready |
| Bulk video generation from CSV | Synthesia (Enterprise) / HeyGen Batch | Template + CSV |
| Video translation / dubbing | HeyGen | Source video + language selection |
| Upload to Wistia | Wistia Upload API + Zapier | One-time Zap setup |
| Caption/transcript generation | Wistia | Auto on upload |
| AI chapter creation | Wistia | Auto on upload |
| Analytics collection | Wistia | Auto after embed |
| Delivery notifications | Zapier (HeyGen → Slack/email) | One-time Zap setup |
| Metadata assignment at upload | Wistia API | Script/Zap setup |

### Partially Automated (Human Trigger + AI Execution)

| Task | Human Trigger | AI Execution |
|---|---|---|
| Course video production | Approve script + click Generate | Rendering, voiceover |
| Batch translation | Submit source video + language list | All render jobs |
| Bulk course production | Upload script CSV + approve template | All 44+ videos |
| Social media adaptation | Approve concept | Script variation + render |

---

## Part 7: One-Time Setup Checklist

Complete these once to enable all workflows above:

### Synthesia Setup
- [ ] Log in and verify subscription tier (confirm Enterprise for bulk production)
- [ ] Create SCLA Brand Kit: upload logo, set colors (`#eaab2d`, `#3393d6`), set fonts
- [ ] Create or import an SCLA course avatar (custom from video recording, or select stock)
- [ ] Build 3 master templates: Course Video, Certificate Video, Learning Activity
- [ ] Test bulk CSV import with 3 sample scripts → verify output quality
- [ ] Contact Synthesia sales about nonprofit/education pricing (email: sales@synthesia.io)

### HeyGen Setup
- [ ] Log in and verify subscription tier
- [ ] Record a 2-minute voice sample for voice cloning (quiet room, external mic, natural speech)
- [ ] Create cloned voice in HeyGen → Voice Cloning → test output quality
- [ ] Set up 3 templates: Short-form Social, Learning Activity, Company Tour narration
- [ ] Configure Instant Avatar if desired (2-min webcam recording)
- [ ] Test Video Agent with 2–3 topic prompts → evaluate output quality
- [ ] Contact HeyGen sales about education/nonprofit pricing (contact form at heygen.com)

### Wistia Setup
- [ ] Confirm account plan supports your total storage needs
- [ ] Create Channels for: Courses, Certificate Programs, Social, Company Tour
- [ ] Set up folder structure mirroring your content hierarchy
- [ ] Configure player branding (SCLA colors, logo)
- [ ] Connect HubSpot (if in use) for viewer analytics sync
- [ ] Set up Zapier: "HeyGen video complete → upload to Wistia" automation
- [ ] Test embed codes in your course platform (Canvas/LMS)
- [ ] Generate API key for bulk upload scripting

### Claude Prompt Library
- [ ] Save course script generation prompt to a shared team doc
- [ ] Save social script prompt
- [ ] Save QA/fact-check prompt
- [ ] Save bulk CSV generation prompt
- [ ] Save translation review prompt
- [ ] Share with all content creators

### Zapier / Make Automation
- [ ] Zap 1: HeyGen video complete → upload MP4 to Wistia folder
- [ ] Zap 2: Wistia upload complete → post notification to Slack (#video-production)
- [ ] Zap 3 (optional): Google Sheet row added → trigger HeyGen batch video generation
- [ ] Zap 4 (optional): HeyGen translation complete → add to Wistia with language tag

---

## Part 8: Recommended Workflow by Video Type (Quick Reference)

| If you're making... | Use this workflow |
|---|---|
| A new course video (AI avatar, 5-15 min) | Workflow A: Claude → Synthesia → Wistia |
| A learning activity (AI avatar, <3 min) | Workflow B: HeyGen Video Agent → Wistia |
| A social media video (60-90 sec) | Workflow C: Claude → HeyGen → Social/Wistia |
| A translated version of any video | Workflow D: HeyGen Video Translation → Wistia |
| A screen recording tutorial | Workflow E: Screen record → HeyGen voice layer → Wistia |
| A full 44-video course at once | Workflow F: Claude CSV → Synthesia Batch → Wistia bulk upload |
| A live actor video | Traditional production → Wistia hosting |
| A company tour video | Film footage manually → HeyGen AI narration overlay → Wistia |

---

## Part 9: Pricing Realities & What to Negotiate

### At SCLA's Scale (30 hrs/month peak)

| Tool | Minimum Viable Plan | Estimated Monthly Cost | Nonprofit Leverage |
|---|---|---|---|
| **Synthesia** | Enterprise (only tier with unlimited minutes) | ~$2,500+/mo or ~$30K/yr | No public discount — negotiate directly; mention nonprofit status + volume |
| **HeyGen** | Business ($149/mo + credit top-ups) or Enterprise | $149–$500+/mo depending on volume | Contact sales; `.edu` email may help; annual billing saves ~20% |
| **Wistia** | Plus ($19/mo) to Pro ($79/mo) | $19–$79/mo | No official discount — ask directly; they've made accommodations historically |
| **Zapier** (automation) | Professional ($49/mo) | $49/mo | Zapier has a verified nonprofit program — 15% discount |

**Immediate action:** Contact Synthesia and HeyGen sales before building out your full pipeline. Volume commitments at the Enterprise tier almost always come with custom pricing. Lead with: nonprofit mission, number of learners served, total video volume, and annual commitment.

### Cost-Reduction Strategies

1. **Use HeyGen for short-form, Synthesia for long-form** — don't duplicate across both platforms for the same video type. Assign each a lane.
2. **Batch render during off-peak hours** — HeyGen processes faster at non-peak times (avoid 9am–5pm PST for large batches).
3. **Translate only top-performing videos** — use Wistia analytics to identify which courses get the most watch time before investing in translation.
4. **Re-use avatar templates** — the more you reuse a built template, the lower the per-video labor cost. Don't build a new template for each course.
5. **AI voiceover over AI avatar** for content that doesn't benefit from a talking head (pure screen recordings, data-heavy content) — credits cost less.

---

## Part 10: Known Limitations & Gotchas

### Synthesia
- **Minute caps are hard** — going over on a paid plan isn't possible; jobs queue or fail. Monitor usage.
- **Google Slides requires PPTX export first** — add this step to your workflow.
- **Interactive videos can't be downloaded as MP4** — choose between interactivity and portability when designing a video.
- **SCORM export is Enterprise-only** — if your LMS requires SCORM, you must be on Enterprise.

### HeyGen
- **Renders occasionally stall at 33% or 50%** — documented bug; resubmit the job if it hangs >30 min.
- **Premium credits (Avatar IV) burn fast** — 20 credits/minute means 200 monthly credits = 10 min of Avatar IV video. Monitor credit usage weekly.
- **Billing surprises** — multiple users report unexpected overages. Set a credit alert threshold in account settings.
- **Long-form consistency** — HeyGen avatars are noticeably less consistent beyond 3 minutes. Use Synthesia for longer course content.
- **No free API credits** as of 2026 — all API usage is paid.

### Wistia
- **Not a native LMS** — no SCORM, no gradebook sync. Integration with Canvas/Moodle is iframe-only.
- **No official nonprofit discount** — contact support@wistia.com and ask directly.
- **Viewer-level analytics require CRM integration** — without HubSpot (or similar), you see aggregate numbers only.

### Claude
- **Always review AI-generated scripts before production** — Claude can be confidently wrong about specific SCLA program details, dates, or statistics. Fact-checking is a required human step.
- **Don't feed FERPA/PII data into Claude** for script generation — use anonymized examples and general course content only.

---

## Part 11: Month-by-Month Ramp Strategy

Rather than trying to automate everything at once, here's a practical sequence:

### Month 1 — Foundation
- Set up Synthesia and HeyGen templates and brand kits
- Record voice clone in HeyGen
- Set up Wistia channels and folder structure
- Build Claude prompt library
- Produce first 5 AI-avatar videos using Workflow A
- Test Wistia analytics setup

### Month 2 — Batch Production
- Run first Workflow F batch (full course, 44 videos)
- Set up Zapier automations (HeyGen → Wistia, notifications)
- Produce social media video series using Workflow C
- Review analytics from Month 1 videos → identify what's working

### Month 3 — Translation & Scale
- Identify top 10 most-watched course videos
- Run Workflow D to translate those into priority languages
- Start producing learning activities using HeyGen Video Agent
- Tune prompt library based on script quality learnings

### Month 4+ — Full Pipeline
- All five workflows running in parallel
- Batch course production at full 30-hr/month volume
- Monthly analytics review → content strategy feedback loop
- Ongoing: renegotiate vendor pricing based on actual volume data

---

*Source: SCLA video production planning document (Google Doc), Synthesia/HeyGen/Wistia platform research.*
