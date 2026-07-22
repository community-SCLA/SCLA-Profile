# Video Production Pipeline — Claude Context

SCLA's AI-powered video pipeline (Synthesia + HeyGen) for producing 16–30 hours of video per month at scale.

**Active subscriptions:** Synthesia · HeyGen · Wistia

## Files in This Project

| File | Purpose |
|---|---|
| `status.md` | Live production status — setup checklist, owner, accounts, blockers |
| `PIPELINE-MAP.md` | **Human reference** — the live annotated flow map of the lesson-video pipeline (skills, folders, the two checkpoints). Not loaded by agents; update it whenever the pipeline flow changes. |
| `notion-queue.md` | Notion queue doc — **retired as intake 2026-07-13** (scripts now enter at `lesson-scripts/<program-slug>/` root). Notion's remaining role (Wistia-link ledger, routine fate) is an open decision; the file documents the old flow until that lands. |
| `script-templates/heygen-lesson-script.md` | HeyGen lesson script scaffold (program-agnostic). Worked example: `programs/early-career-boost/video-style.md` |
| `script-templates/course-script-prompt.md` | Claude prompt for course/certificate videos (Synthesia; B-roll markers) |
| `script-templates/heygen-narration-prompt.md` | Claude prompt for plain narration → `avatar-pipeline/` (no cues to strip) |
| `script-templates/social-script-prompt.md` | Claude prompt for social media videos |
| `script-templates/batch-csv-template.md` | CSV specs for Synthesia + HeyGen bulk generation |
| `script-templates/qa-checklist.md` | Video QA checklist for the human review step |
| `design-system/` | **SCLA video design system** — nine branded scene templates, design tokens (`frame.md`), pinned narration voice, demo reel. The illustrated-video path for lesson videos. See its `CLAUDE.md`. |
| `avatar-pipeline/` | Code path — Python + HeyGen API turns `.txt` scripts into rendered MP4s (batch, resumable). See its `CLAUDE.md`. |
| `renders-hyperframes/` | **Local-only build workspaces** (gitignored) — one HyperFrames workspace per illustrated video while in production; delivered builds move to `renders-hyperframes/_archive/<stem>/` via `scripts/archive-lesson.sh`. See its `README.md`. |
| `lesson-scripts/` | Curated script library, one folder per program — **a script's folder is its state**: raw at root → `refined/` → `rendered/` (the video itself goes to Wistia, not here). Naming + state semantics in its `README.md`; `refinement-log.md` is the human-facing ledger. |
| `renders-mp4/` | Local staging for finished MP4s (gitignored), one folder per program mirroring `lesson-scripts/`, split into `hyperframes/` + `avatar/` subfolders — **both render paths file here**, viewable locally before the Wistia upload, named with the render date. See its `README.md`. |
| `hyperframes-skills-reference.md` | Reference table for the locally-installed HyperFrames skill pack (`.agents/skills/`) — separate tool from `avatar-pipeline/`, for authoring HTML video compositions directly. |

## Tool Routing (Don't Mix These Up)

- **Produce a video end to end (local)** → `/produce-video` — the thin dispatcher over the two workhorse skills: `/refine-scripts` (raw script → `refined/`, one cold subagent per script) then `/render-lessons` BUILD (refined script → HyperFrames workspace, one cold subagent per video). It always stops at the hyperframe gate; `ship <stem>` is the one explicit human call into `/render-lessons` — once granted, SHIP renders, verifies, files, and publishes to Wistia in one uninterrupted pass (2026-07-22, `decisions/log.md`).
- **Script/lesson state** → the folder it sits in (`lesson-scripts/README.md`) — raw at program root, `refined/`, workspace at the hyperframe gate, MP4 at review, `rendered/`. `refinement-log.md` is a ledger, never a decision input.
- **Notion intake** → retired as intake 2026-07-13; scripts enter as `.txt` files at `lesson-scripts/<program-slug>/` root. What remains in Notion (Wistia-link ledger, the polling routine's fate) is an open decision — until settled, `notion-queue.md` describes the old flow and the Wistia URL lives in `refinement-log.md`.
- **Illustrated lesson videos (default for concept lessons, frameworks, processes)** → HyperFrames via `design-system/` — brand-owned motion graphics + pinned TTS voice, no per-minute avatar credits; one of three style packages per video (`design-system/frame.md` → "Style packages")
- **HeyGen (avatar)** → translations/multilingual, quick-turn social talking heads, true human-presence moments
- **HeyGen web UI vs. code path** → web UI for one-off/visually-designed videos; `avatar-pipeline/` for repeatable batch rendering from finalized scripts
- **Synthesia** → long-form avatar courses — under re-evaluation (setup never completed; decide before any Enterprise commitment)
- **Hosting / analytics** → **Wistia** (account, upload mechanics, auth status: repo-root `endpoints.md` → "Wistia") — uploaded automatically via `scripts/wistia-upload.sh` as the last step of `/render-lessons` SHIP (no separate human review before publish, 2026-07-22); the URL is recorded in `refinement-log.md`. Finished MP4s stage locally first, one folder per program with two subfolders: HyperFrames renders in `renders-mp4/<program-slug>/hyperframes/`, avatar renders in `renders-mp4/<program-slug>/avatar/`. Rendered MP4s are **not committed to the repo** (only the `.txt` script is tracked).

Peak months (Jun/Jul/Aug/Nov) hit ~30 hrs/1,800 min — requires Synthesia **Enterprise** tier; HeyGen Business/Enterprise with weekly credit monitoring.

## Critical Rules

- **Never fabricate SCLA course content** — always work from provided outlines/source material
- **One human checkpoint (2026-07-13, replaces the old script/QA gates; MP4 REVIEW/PUBLISH gate removed 2026-07-22 — see `decisions/log.md`):**
  1. **HYPERFRAME GATE** — a human previews every built hyperframe before it may become an MP4. Hyperframe → MP4 runs only on an explicit `ship <stem>`. **No automation ever takes a script to an MP4 in one shot.**
  Once granted, SHIP renders, verifies, files, and uploads to Wistia in one uninterrupted pass — no second human review before publish. The deterministic `verify_render.py` gate plus builder frame self-review are the quality bar from SHIP onward.
  Script approval is **async, not blocking**: `refined/` is an open review buffer (edit/veto any time), guarded by the mandatory qa-facts pass at refinement and the script-vs-transcript diff gate in `preflight.py`. Never self-approve the hyperframe gate.
- **QA model (2026-07-13)** — deterministic gates (`render-qa/preflight.py` pre-render, `render-qa/verify_render.py` post-render) must pass and the builder reviews the `qa/frames/` dump before the hyperframe gate and again before publish. `/adversarial-qa` (four cold-context reviewer lanes) is an on-demand deep audit — run it when a cut resists diagnosis or the user asks to "try to break it", not on every render. Facts are checked once at script stage (`/refine-scripts`), not per render
- **Self-improvement loop (2026-07-13, ask-model 2026-07-14)** — every render/build session ends by prepending an entry to `render-qa/snag-log.md` per its header rules (hook-enforced): sessions read **only the latest entry**; unresolved items are **owner-actionable by definition** (the agent fixes anything it can in-session, never rolls fixable work forward), and a non-empty Open list means the session **asks the human directly** to resolve each item at close-out (AskUserQuestion when interactive) — you are never asked to go read the log
- **No FERPA/PII data** in any prompt sent to an AI tool

## Brand

Source of truth: `brand/visual-identity.md` (colors, logo, type) and `brand/voice-and-tone.md` (voice). Do not restate hex values here — they drift. Audience: college students 18–24.

## Current Phase

See `status.md`.
