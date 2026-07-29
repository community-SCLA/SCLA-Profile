# Video Production Pipeline — Claude Context

SCLA's AI-powered video pipeline (Synthesia + HeyGen) for producing 16–30 hours of video per month at scale.

**Active subscriptions:** Synthesia · HeyGen · Wistia

## Layout

Standard project shape (`src/` · `config/` · `docs/` · `logs/`), with `design-system/`
the sole exception — HyperFrames dictates its layout, and the divergence is written
down in `design-system/docs/README.md`. `ls` answers "what's here"; this section carries
only what `ls` cannot tell you:

- `design-system/` — the illustrated path. **Two spec files, not interchangeable:**
  `config/tokens.yml` is the numbers (parsed by `render-qa/src/tokens.py`; the gates
  grade against it) and `docs/design-contract.md` is the prose (no code reads it). They
  were one file, `frame.md`, until 2026-07-29. See its `CLAUDE.md`.
- `render-qa/` — the deterministic gates. `src/` is the toolchain, `tests/` pins it,
  `logs/snag-log.md` is the rolling retro.
- `avatar-pipeline/` — HeyGen API path, batch and resumable. See its `CLAUDE.md`.
- `lesson-scripts/` — **a script's folder is its state**: raw at a program root →
  `refined/` → `rendered/`. The video goes to Wistia, never here. `refinement-log.md`
  is a human ledger, never a decision input.
- `renders-hyperframes/` — local build workspaces, gitignored. Delivered builds **stay
  put**; retiring one to `_archive/<stem>/` is a human-only call, never automated.
- `renders-mp4/` — local MP4 staging, gitignored, mirroring `lesson-scripts/` and split
  into `hyperframes/` + `avatar/`. Both render paths file here.
- `docs/notion-queue.md` — Notion, **retired as intake 2026-07-13**. Its remaining role
  (Wistia-link ledger) is an open decision; the file documents the old flow until it lands.

## Tool Routing (Don't Mix These Up)

- **Produce a video end to end (local)** → `/produce-video` — the thin dispatcher over the two workhorse skills: `/refine-scripts` (raw script → `refined/`, one cold subagent per script) then `/render-lessons` (refined script → HyperFrames workspace → MP4 → Wistia, one cold subagent per video). It stops at **one** human gate: BUILD stops per video for a one-off, AUTO-BATCH stops after its pilot and that approval covers the whole queue (2026-07-28, `decisions/log.md`). Once granted, render → verify → file → Wistia runs in one uninterrupted pass (2026-07-22). Resume an interrupted batch with `bash scripts/batch-status.sh`.
- **Script/lesson state** → the folder it sits in (`lesson-scripts/README.md`) — raw at program root, `refined/`, workspace at the hyperframe gate, MP4 at review, `rendered/`. `refinement-log.md` is a ledger, never a decision input.
- **Notion intake** → retired as intake 2026-07-13; scripts enter as `.txt` files at `lesson-scripts/<program-slug>/` root. What remains in Notion (Wistia-link ledger, the polling routine's fate) is an open decision — until settled, `notion-queue.md` describes the old flow and the Wistia URL lives in `refinement-log.md`.
- **Illustrated lesson videos (default for concept lessons, frameworks, processes)** → HyperFrames via `design-system/` — brand-owned motion graphics + pinned TTS voice, no per-minute avatar credits; one of three style packages per video (`design-system/docs/design-contract.md` → "Style packages")
- **HeyGen (avatar)** → translations/multilingual, quick-turn social talking heads, true human-presence moments
- **HeyGen web UI vs. code path** → web UI for one-off/visually-designed videos; `avatar-pipeline/` for repeatable batch rendering from finalized scripts
- **Synthesia** → long-form avatar courses — under re-evaluation (setup never completed; decide before any Enterprise commitment)
- **Hosting / analytics** → **Wistia** (account, upload mechanics, auth status: repo-root `config/endpoints.json` → "Wistia") — uploaded automatically via `scripts/wistia-upload.sh` as the last step of `/render-lessons` SHIP (no separate human review before publish, 2026-07-22); the URL is recorded in `refinement-log.md`. Finished MP4s stage locally first, one folder per program with two subfolders: HyperFrames renders in `renders-mp4/<program-slug>/hyperframes/`, avatar renders in `renders-mp4/<program-slug>/avatar/`. Rendered MP4s are **not committed to the repo** (only the `.txt` script is tracked).

Peak months (Jun/Jul/Aug/Nov) hit ~30 hrs/1,800 min — requires Synthesia **Enterprise** tier; HeyGen Business/Enterprise with weekly credit monitoring.

## Critical Rules

The standing constraints — fabrication ban, PILOT GATE (the one human checkpoint per batch, never self-approved), the mechanized guards that replace the per-video human eye, one-pass SHIP, publish-before-next-starts, never-archive-automatically, snag-log retro at session end, no FERPA/PII, brand source of truth — live in **`.claude/rules/video-production.md`**, auto-loaded for sessions working under `projects/video-production/`. Cold subagents: read that file first.

Operational details that stay here:
- **QA model (2026-07-13)** — deterministic gates (`render-qa/src/preflight.py` pre-render, `render-qa/src/verify_render.py` post-render) must pass and the builder reviews the `qa/frames/` dump before the hyperframe gate and again before publish. `/adversarial-qa` (four cold-context reviewer lanes) is an on-demand deep audit — run it when a cut resists diagnosis or the user asks to "try to break it", not on every render. Facts are checked once at script stage (`/refine-scripts`), not per render.
- **Script approval is async, not blocking:** `refined/` is an open review buffer (edit/veto any time), guarded by the qa-facts pass at refinement and the script-vs-transcript diff gate in `preflight.py`.
- **Snag-log semantics** — sessions read **only the latest entry**; unresolved items are owner-actionable by definition (the agent fixes anything it can in-session, never rolls fixable work forward), and a non-empty Open list means the session asks the human directly at close-out (AskUserQuestion when interactive).

## Brand

Source of truth: `brand/visual-identity.md` (colors, logo, type) and `brand/voice-and-tone.md` (voice). Do not restate hex values here — they drift. Audience: college students 18–24.

## Current Phase

**State is the folder** — nothing narrates it, so read it directly:
`lesson-scripts/<program>/refined/*.txt` = queued to build ·
`renders-hyperframes/<stem>/` = built, waiting at the hyperframe gate ·
`lesson-scripts/<program>/rendered/*.txt` = gate-clean build exists ·
Wistia URL in `lesson-scripts/refinement-log.md` = published.
(`status.md` and `PIPELINE-MAP.md` were removed 2026-07-27 — both narrated a
pipeline shape that had already changed underneath them.)
