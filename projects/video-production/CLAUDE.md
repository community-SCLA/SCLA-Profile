# Video Production Pipeline — Claude Context

SCLA's AI-powered video pipeline (Synthesia + HeyGen) for producing 16–30 hours of video per month at scale.

**Active subscriptions:** Synthesia · HeyGen

## Files in This Project

| File | Purpose |
|---|---|
| `status.md` | Live production status — setup checklist, owner, accounts, blockers |
| `templates/heygen-lesson-script.md` | HeyGen lesson script scaffold (program-agnostic). Worked example: `programs/early-career-boost/video-style.md` |
| `templates/course-script-prompt.md` | Claude prompt for course/certificate videos (Synthesia; B-roll markers) |
| `templates/heygen-narration-prompt.md` | Claude prompt for plain narration → `heygen-pipeline/` (no cues to strip) |
| `templates/social-script-prompt.md` | Claude prompt for social media videos |
| `templates/batch-csv-template.md` | CSV specs for Synthesia + HeyGen bulk generation |
| `templates/qa-checklist.md` | Video QA checklist for the human review step |
| `heygen-pipeline/` | Code path — Python + HeyGen API turns `.txt` scripts into rendered MP4s (batch, resumable). See its `CLAUDE.md`. |

## Tool Routing (Don't Mix These Up)

- **Synthesia** → course + certificate videos (5–15 min, structured, consistent avatar)
- **HeyGen** → learning activities, social, translations, screen-recording voiceover (<3 min or multilingual)
- **HeyGen web UI vs. code path** → web UI for one-off/visually-designed videos; `heygen-pipeline/` for repeatable batch rendering from finalized scripts
- **Hosting / analytics** → `TODO: not yet decided` (previously Wistia; SCLA is no longer standardizing on it)

Peak months (Jun/Jul/Aug/Nov) hit ~30 hrs/1,800 min — requires Synthesia **Enterprise** tier; HeyGen Business/Enterprise with weekly credit monitoring.

## Critical Rules

- **Never fabricate SCLA course content** — always work from provided outlines/source material
- **Always flag scripts for human approval** before render — script → render is a manual gate, never automated
- **No FERPA/PII data** in any prompt sent to an AI tool

## Brand

Source of truth: `brand/visual-identity.md` (colors, logo, type) and `brand/voice-and-tone.md` (voice). Do not restate hex values here — they drift. Audience: college students 18–24.

## Current Phase

See `status.md`.
