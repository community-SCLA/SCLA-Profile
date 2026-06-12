# Video Production Pipeline — Claude Context

## What This Project Is

This project defines SCLA's AI-powered video production pipeline using Synthesia, HeyGen, and Wistia. It is the operational playbook for producing 16–30 hours of video per month at scale.

**Active subscriptions:** Synthesia · HeyGen · Wistia

---

## Files in This Project

| File | Purpose |
|---|---|
| `video-production-ai-guide.md` | Master instructional guide — workflows, tool routing, setup checklist, pricing |
| `status.md` | Live production status — setup progress, active work, blockers |
| `templates/course-script-prompt.md` | Ready-to-use Claude prompt for course/certificate videos |
| `templates/social-script-prompt.md` | Ready-to-use Claude prompt for social media videos |
| `templates/batch-csv-template.md` | CSV format specs for Synthesia and HeyGen bulk generation |
| `templates/qa-checklist.md` | Video QA checklist for human review step |

---

## Key Context for Claude

### Tool Routing (Don't Mix These Up)
- **Synthesia** → course videos and certificate videos (5–15 min, structured, consistent avatar)
- **HeyGen** → learning activities, social media, translations, screen recording voiceover (<3 min or multilingual)
- **Wistia** → ALL finished videos land here; it is the single hosting/analytics layer

### Scale Reality
- Peak months (Jun/Jul/Aug/Nov): **30 hours = 1,800 min/month**
- This requires **Enterprise tier** on Synthesia for unlimited minutes
- HeyGen Business or Enterprise for volume; monitor credit burndown weekly

### SCLA Brand
- Primary gold: `#F1B32E`
- Primary blue: `#55A4DD`
- TODO [TEAM DECISION]: these hex values conflict with the production-CSS brand system in `scla/brand/visual-identity.md` (gold `#eaab2d`, blue `#3393d6`). Confirm which set is correct for video before the next render batch; update this project's templates and guide when decided.
- Voice: Warm, professional, encouraging. No jargon. Active voice. Target audience: college students 18–24.

### Critical Rules
- **Never fabricate SCLA course content** — always work from provided outlines/source material
- **Always flag scripts for human approval** before production commences — never send directly to render
- **Don't include FERPA/PII data** in any prompts sent to AI tools
- Script approval → video render is a manual gate, not an automated step

---

## Production Contacts

| Role | Contact | Notes |
|---|---|---|
| Synthesia account | TODO | Confirm Enterprise tier |
| HeyGen account | TODO | Confirm plan + API key |
| Wistia account | TODO | Confirm API key location |
| Zapier automations | TODO | HeyGen→Wistia zap owner |

---

## Current Phase

See `status.md` for live progress on setup checklist and active production.
