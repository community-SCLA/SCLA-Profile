# Video Production Pipeline — Claude Context

SCLA's AI-powered video pipeline (Synthesia + HeyGen + HyperFrames) for producing 16–30 hours of video per month at scale. Active subscriptions: Synthesia · HeyGen · Wistia.

## Task Routing

Match the task, load the ONE file it names, stop.

| Task | Load |
| --- | --- |
| Produce a video end to end (one call) | `/produce-video` |
| Illustrated lesson video (default: concepts, frameworks, processes) | `/render-lessons` → "Build sequence" (freeform — the HTML is the authored artifact; brand tokens: `design-system/CLAUDE.md`) |
| Authoring inside a build workspace (`renders-hyperframes/<stem>/`) | `renders-hyperframes/_run/BUILD-KIT.md` — workspaces carry no CLAUDE.md/AGENTS.md of their own |
| Deterministic render gates / QA toolchain | `render-qa/README.md` |
| Script/lesson state (`inbox/` → `ready/` → `published/`) | `lesson-scripts/README.md` |
| Wistia link ledger | `lesson-scripts/published.tsv` (machine key) + `lesson-scripts/refinement-log.md` (human-facing) |
| Standing constraints (fabrication ban, PILOT GATE, mechanized guards...) | `.claude/rules/video-production.md` (auto-loaded here; cold subagents read it first) |
| Session close-out retro | `render-qa/logs/snag-log.md` (read ONLY the latest entry) |
| Brand facts — colors, logo, type, voice | `brand/visual-identity.md`, `brand/voice-and-tone.md` |
| Why a decision was made | `decisions/log.md` |
| What's left in the queue / what's stuck / what's published where | `PIPELINE-STATUS.md` (generated doc, human-readable) or `bash scripts/batch-status.sh` (live, terminal) |

## Which Tool

| Video is... | Use |
| --- | --- |
| Concept lesson, framework, process (**default**) | **HyperFrames**, freeform-authored — brand motion graphics + pinned TTS voice, no per-minute avatar cost. Tokens/fonts: `design-system/`; sequence: `/render-lessons` |
| Translation/multilingual, quick-turn social, needs a human face | **HeyGen** — web UI only; the batch/resumable code path (`avatar-pipeline/`) was removed 2026-08-02 |
| Long-form avatar course | **Synthesia** — under re-evaluation, setup never completed; decide before any Enterprise commitment |
| Hosting / analytics | **Wistia** — auto-uploaded by `scripts/wistia-upload.sh` as the last step of SHIP, URL recorded in `refinement-log.md`; auth status in repo-root `config/endpoints.json` → "Wistia" |

Peak months (Jun/Jul/Aug/Nov) hit ~30 hrs/1,800 min — needs Synthesia Enterprise; HeyGen Business/Enterprise with weekly credit monitoring.

## Layout (what `ls` can't tell you)

- `design-system/` is the one layout exception — HyperFrames dictates its shape (`design-system/docs/README.md` explains the divergence).
- Two files, not interchangeable: `design-system/config/tokens.yml` (the numbers, loaded by `render-qa/src/tokens.py` — what the gates grade against) and `.claude/rules/video-production.md` (every gated rule, each naming its checker). The template lane's authoring-menu doc retired with the lane 2026-08-05 (decisions/log.md); a freeform build's design intent lives in its own `design.md`.
- `renders-hyperframes/` and `renders-mp4/` are local, gitignored staging. Delivered builds stay put; retiring one to `_archive/` is a human-only call, never automated.
- Rendered MP4s are **never committed** — only the `.txt` script is tracked.

## Current Phase

State is the folder — nothing narrates it, so read it directly:
The folder name IS the stage name: `lesson-scripts/<program>/inbox/*.txt` = raw · `ready/*.txt` = queued to build · `renders-hyperframes/<stem>/` = in flight, read its stage with `bash scripts/batch-status.sh` · `published/*.txt` + a `published.tsv` row = live on Wistia. Anything in `published/` without that row is STRANDED.
