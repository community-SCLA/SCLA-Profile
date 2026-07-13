# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated course video pipeline that turns lesson scripts into avatar-narrated videos. Two-stage workflow: load scripts (local files or Google Docs) → create avatar videos with narration via the HeyGen API (HeyGen generates both the voice and the video in one call). Single Python file (`generate_videos.py`) handles the full pipeline with resumable state tracking.

## Where This Fits SCLA's Video Pipeline

This folder is the **code path** for HeyGen production — use it for repeatable, batch course rendering. For one-off or visually-designed videos, use the HeyGen web UI. Routing across all tools lives in `../CLAUDE.md`.

**Upstream (authoring):** scripts here start life in `../script-templates/heygen-lesson-script.md`. That template produces a rich doc — body copy, `[On screen:]` / `[Graphic:]` cues, and a shot list. This pipeline consumes **plain narration only**: copy just the spoken lines from section 3 of the script into a `.txt`, dropping all cues, headings, and the shot list. Cues are for the human building visuals in HeyGen, not for the avatar to read.

Once a narration script is approved, save it directly into its program's folder under `../lesson-scripts/<program-slug>/` — the curated home for the approved script (the rendered video goes to Wistia, not here) — and point `config.json` at it there (e.g. `../lesson-scripts/early-career-boost/lesson-1.0_early-career-boost_2026-07-06.txt`). This is a single source of truth: the pipeline reads the script from its permanent home instead of a separate staging copy, so nothing needs moving except the rendered `.mp4` at the end. The local `scripts/` folder is reserved for `example-lesson.txt`, the generic onboarding demo used by the Quick Start below — not real production content.

**Downstream (hosting):** finished MP4s land in `output/videos/` (self-contained, gitignored) — once a human has reviewed the MP4, rename per the [`lesson-scripts/README.md`](../lesson-scripts/README.md) convention and **upload to Wistia** (account + auth status: repo-root `endpoints.md` → "Wistia"); record the Wistia URL in `../lesson-scripts/refinement-log.md`. The `.mp4` is not committed to the repo — only the approved `.txt` script lives in `../lesson-scripts/<program-slug>/`.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your API keys

```bash
cp .env.example .env
```

Then edit `.env` and add your real API key:
- **HeyGen API key** — get it at https://app.heygen.com/settings/api

### 3. Configure your avatar and voice

Edit `config.json`:

```json
{
  "avatar": {
    "id": "paste-your-heygen-avatar-id-here",
    "name": "Your Avatar Name"
  },
  "voice": {
    "id": "paste-your-heygen-voice-id-here"
  }
}
```

**How to find your avatar ID:**
1. Go to https://app.heygen.com and navigate to "Avatars"
2. Click on your avatar
3. The avatar ID is in the URL or shown in the avatar details

**How to find your voice ID:**
Run `python generate_videos.py --list-voices` to print every HeyGen voice in your account with its ID, then copy the one you want into `config.json`. (You can also browse voices in the HeyGen dashboard.)

### 4. Add your lessons

Edit the `lessons` section in `config.json`:

```json
"lessons": {
  "1.0": {
    "title": "My First Lesson",
    "source": "local",
    "file": "../lesson-scripts/<program-slug>/lesson-1.0_<program-slug>_2026-07-06.txt"
  }
}
```

For local files, save the approved `.txt` script into `../lesson-scripts/<program-slug>/` (its permanent home — see "Where This Fits SCLA's Video Pipeline" above), not into this folder. For Google Docs, use `"source": "google_doc"` with a `"doc_id"`.

### 5. Test with a dry run

```bash
python generate_videos.py --dry-run
```

This exports and splits scripts without making any API calls (no credits used).

### 6. Generate your first video

```bash
python generate_videos.py --lesson 1.0 --max-parts 1
```

Start with one lesson and one chunk to verify everything works before processing your full course.

## Commands

```bash
# Full pipeline (all lessons)
python generate_videos.py

# Export and split scripts only (no API calls)
python generate_videos.py --dry-run

# Process a single module
python generate_videos.py --module 1

# Process a single lesson
python generate_videos.py --lesson 1.0

# Limit chunks per lesson (useful for testing)
python generate_videos.py --max-parts 1

# Show progress summary
python generate_videos.py --status

# List available HeyGen voices (to find your voice ID)
python generate_videos.py --list-voices
```

## Architecture

Everything lives in `generate_videos.py`. The pipeline processes lessons through four sequential stages per chunk:

1. **Load Script** — Read from local `.txt` file or export Google Doc via `gws` CLI
2. **Split** — Sentence-boundary splitting into chunks (configurable word limit)
3. **Create Video** — POST to HeyGen's video generation API with avatar + script text; HeyGen narrates it using the configured HeyGen voice
4. **Poll & Download** — Poll status every 30s until complete, then download MP4

### State Management

`state.json` tracks every step per lesson chunk. The pipeline skips completed steps on re-run, so you can stop and resume at any time. If a step fails, just fix the issue and run again — completed work is preserved.

### Concurrency

Videos are processed in batches (default: 3 at a time) to respect HeyGen's API rate limits.

## Configuration

All settings live in `config.json`:

| Setting | Location | Purpose |
|---|---|---|
| API key | `.env` | HeyGen authentication |
| Avatar ID/name | `config.json → avatar` | Your HeyGen avatar |
| Voice ID | `config.json → voice` | Your HeyGen voice |
| Voice settings | `config.json → voice.settings` | Speed (and other HeyGen voice options) |
| Chunk size | `config.json → pipeline.max_chunk_words` | Max words per chunk |
| Concurrent limit | `config.json → pipeline.concurrent_limit` | Parallel video requests |
| Lessons | `config.json → lessons` | Your course structure — `file` points into `../lesson-scripts/<program-slug>/`, not a local `scripts/` copy |

**Lesson key convention:** `<section>.<position>` — the platform's section number and the lesson's position within that section's component list, per the program's `video-style.md` outline (e.g. `programs/early-career-boost/video-style.md`). Example: `"3.5"` = Section 3, 5th lesson-only component listed.

## Supplementary Scripts

### heygen_update.py

Browser automation (requires Playwright) for upgrading videos when HeyGen releases a new motion engine. Only needed for version upgrades.

```bash
pip install playwright && playwright install chromium
python heygen_update.py generate   # Build progress file from state.json
python heygen_update.py update     # Upgrade all pending videos
python heygen_update.py status     # Check progress
```

### redownload_videos.py

After upgrading videos with `heygen_update.py`, this script downloads the re-rendered versions.

```bash
python redownload_videos.py          # Download all
python redownload_videos.py --status # Check which are ready
```

## Using Claude Code With This Project

Claude Code can help you customize and extend this pipeline. Here are some things you can ask:

- "Add lessons 2.0 through 2.5 to my config"
- "My lesson 1.0 failed — help me debug it"
- "Change the chunk size to 150 words"
- "Show me the current pipeline status and explain what's left"
- "Help me set up Google Docs export with the gws CLI"
- "Switch me to a different HeyGen voice"

## Output Structure

```
output/
  scripts/         # Exported and split text files
  videos/          # Downloaded HeyGen MP4 files
```

## Troubleshooting

**"config.json has placeholder values"** — Edit config.json and replace all `YOUR_*` values with your real IDs.

**"Set HEYGEN_API_KEY in .env"** — Copy `.env.example` to `.env` and add your API key.

**HeyGen video failed** — Check the error message. Common causes: avatar not found, voice ID not found, script too long, account out of credits.

**Voice not found / bad voice ID** — Run `python generate_videos.py --list-voices` to see valid HeyGen voice IDs and update `config.json`.

**gws not found** — The `gws` CLI is needed for Google Docs export. If you're using local script files, you can ignore this.
