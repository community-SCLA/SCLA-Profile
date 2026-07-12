# Video Production Pipeline — Claude Context

SCLA's AI-powered video pipeline (Synthesia + HeyGen) for producing 16–30 hours of video per month at scale.

**Active subscriptions:** Synthesia · HeyGen · Wistia

## Files in This Project

| File | Purpose |
|---|---|
| `status.md` | Live production status — setup checklist, owner, accounts, blockers |
| `notion-queue.md` | **Team-facing intake** — the Notion video request queue: flow, status gates, database schema. How non-Claude-Code team members request videos and how a session works the queue. |
| `script-templates/heygen-lesson-script.md` | HeyGen lesson script scaffold (program-agnostic). Worked example: `programs/early-career-boost/video-style.md` |
| `script-templates/course-script-prompt.md` | Claude prompt for course/certificate videos (Synthesia; B-roll markers) |
| `script-templates/heygen-narration-prompt.md` | Claude prompt for plain narration → `avatar-pipeline/` (no cues to strip) |
| `script-templates/social-script-prompt.md` | Claude prompt for social media videos |
| `script-templates/batch-csv-template.md` | CSV specs for Synthesia + HeyGen bulk generation |
| `script-templates/qa-checklist.md` | Video QA checklist for the human review step |
| `design-system/` | **SCLA video design system** — nine branded scene templates, design tokens (`frame.md`), pinned narration voice, demo reel. The illustrated-video path for lesson videos. See its `CLAUDE.md`. |
| `avatar-pipeline/` | Code path — Python + HeyGen API turns `.txt` scripts into rendered MP4s (batch, resumable). See its `CLAUDE.md`. |
| `renders-hyperframes/` | **Local-only build workspaces** (gitignored) — one HyperFrames workspace per illustrated video while in production; delivered builds move to `renders-hyperframes/_archive/<stem>/` via `scripts/archive-lesson.sh`. See its `README.md`. |
| `lesson-scripts/` | Curated library — approved narration scripts, one folder per program (the rendered video goes to Wistia, not here). Naming convention in its `README.md`. |
| `renders-mp4/` | Local staging for finished **HyperFrames-rendered** MP4s (gitignored), one folder per program mirroring `lesson-scripts/` — viewable locally before the Wistia upload, named with the render date. See its `README.md`. Avatar-rendered MP4s stage separately, in `avatar-pipeline/output/videos/`. |
| `hyperframes-skills-reference.md` | Reference table for the locally-installed HyperFrames skill pack (`.agents/skills/`) — separate tool from `avatar-pipeline/`, for authoring HTML video compositions directly. |

## Tool Routing (Don't Mix These Up)

- **Produce a video end to end (local)** → `/produce-video` — the one-call orchestrator that walks the full pipeline (script → build → render → verify → file → archive) from a Notion row or a raw script, stopping only at the two human gates. This is the render-capable half the cloud queue routine can't run.
- **Video requests from the team** → the Notion queue (`notion-queue.md`) — the default intake; "work the video queue" means processing its rows
- **Illustrated lesson videos (default for concept lessons, frameworks, processes)** → HyperFrames via `design-system/` — brand-owned motion graphics + pinned TTS voice, no per-minute avatar credits; one of three style packages per video (`design-system/frame.md` → "Style packages")
- **HeyGen (avatar)** → translations/multilingual, quick-turn social talking heads, true human-presence moments
- **HeyGen web UI vs. code path** → web UI for one-off/visually-designed videos; `avatar-pipeline/` for repeatable batch rendering from finalized scripts
- **Synthesia** → long-form avatar courses — under re-evaluation (setup never completed; decide before any Enterprise commitment)
- **Hosting / analytics** → **Wistia** (`sclc.wistia.com`) — the delivered MP4 is uploaded to Wistia at the publish gate; the Wistia URL goes in the Notion **Final video** field. Before upload, finished MP4s stage locally so they're viewable: HyperFrames renders in `renders-mp4/<program-slug>/`, avatar renders in `avatar-pipeline/output/videos/`. Rendered MP4s are **not committed to the repo** (only the approved `.txt` script is tracked).

Peak months (Jun/Jul/Aug/Nov) hit ~30 hrs/1,800 min — requires Synthesia **Enterprise** tier; HeyGen Business/Enterprise with weekly credit monitoring.

## Critical Rules

- **Never fabricate SCLA course content** — always work from provided outlines/source material
- **Always flag scripts for human approval** before render — script → render is a manual gate, never automated
- **Adversarial QA before the human gate** — `/adversarial-qa` runs four independent reviewer lanes (Timing / Layout / Facts / Presence) as subagents; all four must PASS post-render or the cut is blocked (fix → re-render → re-run all). It supplements the human QA gate, never replaces it
- **No FERPA/PII data** in any prompt sent to an AI tool

## Brand

Source of truth: `brand/visual-identity.md` (colors, logo, type) and `brand/voice-and-tone.md` (voice). Do not restate hex values here — they drift. Audience: college students 18–24.

## Current Phase

See `status.md`.
