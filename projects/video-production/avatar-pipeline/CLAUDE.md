# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated course video pipeline that turns lesson scripts into avatar-narrated videos. Two-stage workflow: load scripts (local files or Google Docs) → create avatar videos with narration via the HeyGen API (HeyGen generates both the voice and the video in one call). Single Python file (`generate_videos.py`) handles the full pipeline with resumable state tracking.

## Where This Fits SCLA's Video Pipeline

This folder is the **code path** for HeyGen production — use it for repeatable, batch course rendering. For one-off or visually-designed videos, use the HeyGen web UI. Routing across all tools lives in `../CLAUDE.md`.

**Upstream (authoring):** scripts here start life in `../script-templates/heygen-lesson-script.md`. That template produces a rich doc — body copy, `[On screen:]` / `[Graphic:]` cues, and a shot list. This pipeline consumes **plain narration only**: copy just the spoken lines from section 3 of the script into a `.txt`, dropping all cues, headings, and the shot list. Cues are for the human building visuals in HeyGen, not for the avatar to read.

Once a narration script is approved, it lives in its program's **avatar** queue at `../lesson-scripts/<program-slug>/refined/avatar/` — the curated home for avatar-route scripts (`/refine-scripts` puts it there; the rendered video goes to Wistia, not here) — and `config.json` points at it (e.g. `../lesson-scripts/mid-career-momentum/refined/avatar/m1_the-value-of-building-mid-career-momentum_2026-07-20.txt`). This is a single source of truth: the pipeline reads the script from its permanent home instead of a separate staging copy, so nothing needs moving except the rendered `.mp4` at the end. The local `scripts/` folder is reserved for `example-lesson.txt`, the generic onboarding demo used by the Quick Start below — not real production content.

**Downstream (hosting):** the pipeline concatenates a lesson's HeyGen chunks into **one video per lesson** and files it, already named `m<#>_<title-slug>_<render-date>.mp4` (the [`lesson-scripts/README.md`](../lesson-scripts/README.md) convention), straight into `../renders-mp4/<program-slug>/avatar/` (gitignored, alongside the illustrated path's `hyperframes/` renders). Per-chunk intermediates stay in `output/videos/`. Once a human has reviewed the MP4, **upload to Wistia** (account + auth status: repo-root `endpoints.md` → "Wistia"); record the Wistia URL in `../lesson-scripts/refinement-log.md`. The `.mp4` is not committed to the repo — only the approved `.txt` script lives in `../lesson-scripts/<program-slug>/refined/avatar/`.

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
"program": "Mid-Career Momentum",
"program_slug": "mid-career-momentum",
"lessons": {
  "1.0": {
    "title": "The Value of Building Mid-Career Momentum",
    "module": 1,
    "source": "local",
    "file": "../lesson-scripts/mid-career-momentum/refined/avatar/m1_the-value-of-building-mid-career-momentum_2026-07-20.txt"
  }
}
```

`program_slug` sets the render folder (`renders-mp4/<program-slug>/avatar/`);
each lesson's `module` + `title` build the filename `m<#>_<title-slug>_<render-date>.mp4`.
For local files, the approved `.txt` lives in `../lesson-scripts/<program-slug>/refined/avatar/` (the avatar queue — see "Where This Fits SCLA's Video Pipeline" above), not in this folder. For Google Docs, use `"source": "google_doc"` with a `"doc_id"`.

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
| Program name/slug | `config.json → program`, `program_slug` | Program identity — `program_slug` (kebab-case, matches `lesson-scripts/<slug>/`) sets the render folder `renders-mp4/<slug>/avatar/` |
| API key | `.env` | HeyGen authentication |
| Avatar ID/name | `config.json → avatar` | Your HeyGen avatar |
| Voice ID | `config.json → voice` | Your HeyGen voice |
| Voice settings | `config.json → voice.settings` | Speed (and other HeyGen voice options) |
| Chunk size | `config.json → pipeline.max_chunk_words` | Max words per chunk |
| Concurrent limit | `config.json → pipeline.concurrent_limit` | Parallel video requests |
| Lessons | `config.json → lessons` | Your course structure — each lesson's `module` (the `m<#>` in the filename) + `title` (slugified for the filename); `file` points into `../lesson-scripts/<program-slug>/refined/avatar/`, not a local `scripts/` copy |

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
  videos/          # Per-chunk HeyGen MP4 intermediates (resumable)

../renders-mp4/<program-slug>/avatar/
  m<#>_<title-slug>_<render-date>.mp4   # one assembled video per lesson (the deliverable)
```

Each lesson's chunks are concatenated (ffmpeg, stream-copy) into a single
titled MP4 filed under its program's `avatar/` subfolder — the human-facing
deliverable. `output/videos/` keeps the raw chunks so a re-run resumes without
re-rendering completed parts.

## Troubleshooting

**"config.json has placeholder values"** — Edit config.json and replace all `YOUR_*` values with your real IDs.

**"Set HEYGEN_API_KEY in .env"** — Copy `.env.example` to `.env` and add your API key.

**HeyGen video failed** — Check the error message. Common causes: avatar not found, voice ID not found, script too long, account out of credits.

**Voice not found / bad voice ID** — Run `python generate_videos.py --list-voices` to see valid HeyGen voice IDs and update `config.json`.

**gws not found** — The `gws` CLI is needed for Google Docs export. If you're using local script files, you can ignore this.
