#!/usr/bin/env python3
"""
HeyGen Studio: Automated Course Video Pipeline
================================================

This script takes your lesson scripts and turns them into avatar-narrated
videos using the HeyGen API. HeyGen handles BOTH the voice narration and
the avatar video in a single step — no separate audio tool needed.

The pipeline has 4 stages per lesson:
  Export/Load script → Split into chunks → Create video (voice + avatar)
  → Poll for completion & download

All progress is saved to state.json, so you can stop and resume at any time.

Usage:
    python generate_videos.py                 # Process all lessons
    python generate_videos.py --dry-run       # Export/split only (no API calls)
    python generate_videos.py --module 1      # Process one module
    python generate_videos.py --lesson 1.0    # Process one lesson
    python generate_videos.py --max-parts 1   # Limit chunks per lesson (good for testing)
    python generate_videos.py --status        # Show progress summary
    python generate_videos.py --list-voices   # List available HeyGen voices
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ── Configuration ─────────────────────────────────────────────────────────
# All settings are loaded from config.json — edit that file to customize.

def load_config():
    """
    Read config.json and return a validated configuration dictionary.

    This is where all your personal settings live: avatar ID, voice ID,
    lesson list, etc. If anything is missing or still has placeholder
    values, this function will tell you what to fix.
    """
    config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        print("[ERROR] config.json not found!")
        print("  Edit config.json in this folder and fill in your avatar, voice, and lesson values.")
        sys.exit(1)

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    # Check for placeholder values that haven't been customized yet
    errors = []

    avatar_id = config.get("avatar", {}).get("id", "")
    if not avatar_id or "YOUR_" in avatar_id:
        errors.append('  - Set avatar.id in config.json (find it in HeyGen dashboard under "Avatars")')

    voice_id = config.get("voice", {}).get("id", "")
    if not voice_id or "YOUR_" in voice_id:
        errors.append('  - Set voice.id in config.json to a HeyGen voice ID (run: python generate_videos.py --list-voices)')

    lessons = config.get("lessons", {})
    if not lessons:
        errors.append("  - Add at least one lesson to config.json")

    program_slug = config.get("program_slug", "")
    if not program_slug or "YOUR_" in program_slug:
        errors.append('  - Set program_slug in config.json (kebab-case, matches lesson-scripts/<program-slug>/, e.g. "mid-career-momentum")')

    if errors:
        print("[ERROR] config.json has placeholder values that need to be filled in:")
        for e in errors:
            print(e)
        sys.exit(1)

    return config


# Load config at module level so all functions can access it
CONFIG = load_config()

# API key comes from .env file (never put this in config.json!)
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

# Avatar settings from config.json
HEYGEN_AVATAR_NAME = CONFIG["avatar"]["name"]
HEYGEN_AVATAR_ID = CONFIG["avatar"]["id"]

# Voice settings from config.json — this is now a HeyGen voice ID.
HEYGEN_VOICE_ID = CONFIG["voice"]["id"]
HEYGEN_VOICE_SETTINGS = CONFIG["voice"].get("settings", {"speed": 1.0})

# Pipeline settings from config.json
PIPELINE = CONFIG.get("pipeline", {})
MAX_CHUNK_WORDS = PIPELINE.get("max_chunk_words", 200)
HEYGEN_CONCURRENT_LIMIT = PIPELINE.get("concurrent_limit", 3)

# Lesson data from config.json
LESSONS = CONFIG["lessons"]

# Program identity — the render lands in renders-mp4/<program_slug>/avatar/ and
# its filename uses the program's lessons (see finalize_lesson).
PROGRAM_NAME = CONFIG.get("program", "")
PROGRAM_SLUG = CONFIG["program_slug"]

# Output directories (relative to this script's location)
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = OUTPUT_DIR / "scripts"
VIDEOS_DIR = OUTPUT_DIR / "videos"          # per-chunk intermediates (resumable)
STATE_FILE = BASE_DIR / "state.json"

# Finished, human-facing renders stage per program alongside the illustrated
# (HyperFrames) renders — one folder per program, split by render path:
#   renders-mp4/<program-slug>/avatar/      ← this pipeline (HeyGen talking-head)
#   renders-mp4/<program-slug>/hyperframes/ ← illustrated path (/render-lessons)
RENDERS_MP4_DIR = (BASE_DIR / ".." / "renders-mp4").resolve()
AVATAR_RENDERS_DIR = RENDERS_MP4_DIR / PROGRAM_SLUG / "avatar"


def slugify(text):
    """Kebab-case a title for a filename: lowercase, spaces/underscores → -,
    drop anything that isn't a-z 0-9 or -, collapse repeats. Hyphens live
    *inside* a name part; underscores separate the three stem parts."""
    text = text.lower().strip()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def lesson_module(lesson_id, lesson_info):
    """Module number for the filename's m<#> prefix. Explicit `module` in
    config wins; otherwise fall back to the lesson key's integer part
    (e.g. '3.5' → '3')."""
    module = lesson_info.get("module")
    if module is not None:
        return str(module)
    return lesson_id.split(".")[0]


def render_stem(lesson_id, lesson_info):
    """The MP4 stem + Wistia title: m<#>_<title-slug>_<render-date>.
    Render date is today (the file records when it was rendered, not the
    script's approval date) — matches the repo naming rule."""
    module = lesson_module(lesson_id, lesson_info)
    title_slug = slugify(lesson_info.get("title", f"lesson-{lesson_id}"))
    return f"m{module}_{title_slug}_{date.today().isoformat()}"


# ── State Management ─────────────────────────────────────────────────────
# State is saved to state.json after each step. This means if the script
# crashes or you stop it, you can just run it again and it picks up where
# it left off — no re-doing work that already succeeded.

def load_state():
    """Load the pipeline state from state.json, or create a fresh one."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"avatar_id": None, "lessons": {}}


def save_state(state):
    """Write the pipeline state to state.json."""
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# Thread lock for saving state from multiple threads at once
_state_lock = threading.Lock()


def save_state_safe(state):
    """Thread-safe version of save_state (used during concurrent processing)."""
    with _state_lock:
        save_state(state)


# ── Step 1: Load or Export Script ─────────────────────────────────────────
# Each lesson needs a plain text script. You can either:
#   - Drop a .txt file in the scripts/ folder (source: "local")
#   - Export from Google Docs via the gws CLI (source: "google_doc")

def load_or_export_script(lesson_id, lesson_info):
    """
    Get the script text for a lesson.

    If source is "local", reads from the file path in config.json.
    If source is "google_doc", exports from Google Docs using the gws CLI.
    """
    output_file = SCRIPTS_DIR / f"lesson-{lesson_id}.txt"

    if output_file.exists():
        print(f"  [skip] Script already exported: {output_file.name}")
        return output_file

    source = lesson_info.get("source", "local")

    if source == "local":
        # Read from a local file in the scripts/ folder
        local_path = BASE_DIR / lesson_info.get("file", "")
        if not local_path.exists():
            print(f"  [ERROR] Script file not found: {local_path}")
            print(f"  Make sure the file exists, or update config.json with the correct path.")
            return None
        # Copy to the output scripts directory
        text = local_path.read_text(encoding="utf-8")
        output_file.write_text(text, encoding="utf-8")
        print(f"  Loaded local script: {local_path.name}")
        return output_file

    elif source == "google_doc":
        # Export from Google Docs using the gws CLI tool
        # You need gws installed: https://github.com/nicholasgasior/gws
        doc_id = lesson_info.get("doc_id", "")
        if not doc_id or "YOUR_" in doc_id:
            print(f"  [ERROR] No Google Doc ID set for lesson {lesson_id}")
            print(f"  Update config.json with the doc_id, or switch to source: 'local'")
            return None

        print(f"  Exporting Google Doc {doc_id}...")
        params = json.dumps({"fileId": doc_id, "mimeType": "text/plain"})
        result = subprocess.run(
            ["gws", "drive", "files", "export", "--params", params, "--output", str(output_file)],
            capture_output=True, text=True, shell=True
        )
        if result.returncode != 0:
            print(f"  [ERROR] gws export failed: {result.stderr}")
            print(f"  Is the gws CLI installed? Try: gws --version")
            return None

        print(f"  Exported: {output_file.name}")
        return output_file

    else:
        print(f"  [ERROR] Unknown source type '{source}' for lesson {lesson_id}")
        print(f"  Use 'local' or 'google_doc' in config.json")
        return None


# ── Step 2: Split Scripts ─────────────────────────────────────────────────
# Long scripts get split into smaller chunks because:
#   - Shorter clips = faster HeyGen processing
#   - If one chunk fails, you don't lose the whole lesson

def split_script(lesson_id):
    """Split a lesson script into chunks at sentence boundaries."""
    source = SCRIPTS_DIR / f"lesson-{lesson_id}.txt"
    if not source.exists():
        print(f"  [ERROR] Script not found: {source}")
        return []

    text = source.read_text(encoding="utf-8").strip()
    # Remove BOM (byte order mark) if present
    if text.startswith("﻿"):
        text = text[1:]

    words = text.split()
    total_words = len(words)

    # If the script is short enough, keep it as one chunk
    if total_words <= MAX_CHUNK_WORDS:
        chunk_file = SCRIPTS_DIR / f"lesson-{lesson_id}-part-1.txt"
        chunk_file.write_text(text, encoding="utf-8")
        print(f"  Single chunk: {total_words} words")
        return [{"part": 1, "words": total_words, "file": str(chunk_file)}]

    # Split at sentence boundaries (periods, exclamation marks, question marks)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_words = 0
    part = 1

    for sentence in sentences:
        sentence_words = len(sentence.split())
        # If adding this sentence would exceed the limit, start a new chunk
        if current_words + sentence_words > MAX_CHUNK_WORDS and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_file = SCRIPTS_DIR / f"lesson-{lesson_id}-part-{part}.txt"
            chunk_file.write_text(chunk_text, encoding="utf-8")
            chunks.append({"part": part, "words": current_words, "file": str(chunk_file)})
            print(f"  Part {part}: {current_words} words")
            part += 1
            current_chunk = []
            current_words = 0

        current_chunk.append(sentence)
        current_words += sentence_words

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunk_words = len(chunk_text.split())
        chunk_file = SCRIPTS_DIR / f"lesson-{lesson_id}-part-{part}.txt"
        chunk_file.write_text(chunk_text, encoding="utf-8")
        chunks.append({"part": part, "words": chunk_words, "file": str(chunk_file)})
        print(f"  Part {part}: {chunk_words} words")

    return chunks


# ── Step 3: HeyGen Avatar Lookup ─────────────────────────────────────────
# This finds your avatar in HeyGen's system. If you've set the avatar ID
# in config.json, it uses that directly. Otherwise, it searches by name.

def lookup_avatar(state):
    """Find the avatar_id for your configured avatar."""
    if HEYGEN_AVATAR_ID and "YOUR_" not in HEYGEN_AVATAR_ID:
        state["avatar_id"] = HEYGEN_AVATAR_ID
        save_state(state)
        print(f"  Using configured avatar_id: {HEYGEN_AVATAR_ID}")
        return HEYGEN_AVATAR_ID

    if state.get("avatar_id"):
        print(f"  Using cached avatar_id: {state['avatar_id']}")
        return state["avatar_id"]

    # Search for the avatar by name via the HeyGen API.
    # v3 avatars are two calls deep: /v3/avatars lists groups (characters),
    # /v3/avatars/looks?group_id=... lists that group's looks — a look's `id`
    # is the avatar_id POST /v3/videos actually expects.
    print(f"  Looking up avatar: {HEYGEN_AVATAR_NAME}...")
    url = "https://api.heygen.com/v3/avatars"
    headers = {"X-Api-Key": HEYGEN_API_KEY, "Accept": "application/json"}

    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"  [ERROR] HeyGen avatars API error {resp.status_code}: {resp.text[:200]}")
        return None

    groups = resp.json().get("data", [])

    for group in groups:
        if HEYGEN_AVATAR_NAME.lower() in group.get("name", "").lower():
            group_id = group["id"]
            looks_resp = requests.get(
                "https://api.heygen.com/v3/avatars/looks",
                headers=headers, params={"group_id": group_id}, timeout=30,
            )
            if looks_resp.status_code != 200:
                print(f"  [ERROR] HeyGen avatar looks API error {looks_resp.status_code}: {looks_resp.text[:200]}")
                return None
            looks = looks_resp.json().get("data", [])
            if not looks:
                print(f"  [ERROR] Avatar group '{group['name']}' has no looks.")
                return None
            avatar_id = looks[0]["id"]
            state["avatar_id"] = avatar_id
            save_state(state)
            print(f"  Found avatar: {group['name']} -> {avatar_id}")
            return avatar_id

    # If we didn't find it, show what's available so the user can fix config
    print(f"  [ERROR] Avatar '{HEYGEN_AVATAR_NAME}' not found.")
    print(f"  Available avatars in your account:")
    for g in groups[:10]:
        print(f"    - {g.get('name', 'unnamed')} ({g.get('id', '?')})")
    print(f"  Update avatar.id and avatar.name in config.json with one of these.")
    return None


def list_voices():
    """Print the HeyGen voices available in your account."""
    if not HEYGEN_API_KEY or HEYGEN_API_KEY.startswith("your_"):
        print("[ERROR] Set HEYGEN_API_KEY in your .env file first.")
        return

    print("Fetching HeyGen voices...")
    url = "https://api.heygen.com/v3/voices"
    headers = {"X-Api-Key": HEYGEN_API_KEY, "Accept": "application/json"}

    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"[ERROR] HeyGen voices API error {resp.status_code}: {resp.text[:200]}")
        return

    voices = resp.json().get("data", [])
    if not voices:
        print("No voices found.")
        return

    print(f"\n{len(voices)} voices available. Copy a voice_id into config.json (voice.id):\n")
    for v in voices:
        name = v.get("name", "unnamed")
        lang = v.get("language", "?")
        gender = v.get("gender", "?")
        vid = v.get("voice_id", "?")
        print(f"  {vid}  |  {name} ({gender}, {lang})")


# ── Step 4: HeyGen Video Generation ──────────────────────────────────────
# HeyGen creates the video in one call: it reads your script text with the
# chosen HeyGen voice AND renders the avatar lip-syncing to it.

def create_heygen_video(avatar_id, input_text, title):
    """Create an avatar video in HeyGen from script text using a HeyGen voice."""
    print(f"  Creating HeyGen video: {title}...")
    url = "https://api.heygen.com/v3/videos"
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "type": "avatar",
        "avatar_id": avatar_id,
        "script": input_text,
        "voice_id": HEYGEN_VOICE_ID,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "title": title,
    }
    # Apply optional voice settings (e.g. speed) from config.json
    if HEYGEN_VOICE_SETTINGS:
        payload["voice_settings"] = HEYGEN_VOICE_SETTINGS

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        print(f"  [ERROR] HeyGen video create error {resp.status_code}: {resp.text[:300]}")
        return None

    data = resp.json()
    video_id = data.get("data", {}).get("video_id")
    print(f"  Video queued: video_id={video_id}")
    return video_id


def poll_video_status(video_id, timeout=1200):
    """
    Poll HeyGen until the video is done rendering.

    HeyGen renders videos asynchronously. This function checks every 30
    seconds until the video is completed, failed, or times out (20 min).
    """
    url = f"https://api.heygen.com/v3/videos/{video_id}"
    headers = {"X-Api-Key": HEYGEN_API_KEY, "Accept": "application/json"}

    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"  [WARN] Status poll error {resp.status_code}")
            time.sleep(30)
            continue

        data = resp.json().get("data", {})
        status = data.get("status")
        elapsed = int(time.time() - start)

        if status == "completed":
            video_url = data.get("video_url")
            print(f"  Video completed in {elapsed}s: {video_url}")
            return video_url
        elif status == "failed":
            error = data.get("failure_message") or data.get("failure_code", "unknown")
            print(f"  [ERROR] Video failed after {elapsed}s: {error}")
            return None
        else:
            print(f"  Status: {status} ({elapsed}s elapsed)...", end="\r")
            time.sleep(30)

    print(f"  [ERROR] Video timed out after {timeout}s")
    return None


def download_video(video_url, output_file):
    """Download the completed video file."""
    print(f"  Downloading video to {output_file.name}...")
    resp = requests.get(video_url, timeout=300, stream=True)
    if resp.status_code != 200:
        print(f"  [ERROR] Download failed: {resp.status_code}")
        return False

    with open(output_file, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"  Downloaded: {output_file.name} ({size_mb:.1f} MB)")
    return True


# ── Main Pipeline ─────────────────────────────────────────────────────────

def get_module(lesson_id):
    """Extract the module number from a lesson ID (e.g., '1.2' -> '1')."""
    return lesson_id.split(".")[0]


def submit_chunk(lesson_id, lesson_info, chunk_state, state, avatar_id):
    """
    Process a single chunk into a HeyGen video request.
    Returns (part_number, video_id, status).
    """
    part = chunk_state["part"]

    if chunk_state.get("video_status") == "completed":
        print(f"  [skip] Part {part} already completed.")
        return (part, chunk_state.get("heygen_video_id"), "completed")

    # Create the avatar video directly from the script text (HeyGen voice)
    if not chunk_state.get("heygen_video_id"):
        text = Path(chunk_state["script_file"]).read_text(encoding="utf-8").strip()
        if not text:
            print(f"  [ERROR] Empty chunk file: {chunk_state['script_file']}")
            return (part, None, "create_failed")

        title = f"Lesson {lesson_id} Part {part}"
        video_id = create_heygen_video(avatar_id, text, title)
        if not video_id:
            return (part, None, "create_failed")
        chunk_state["heygen_video_id"] = video_id
        chunk_state["video_status"] = "pending"
        save_state_safe(state)

    return (part, chunk_state["heygen_video_id"], chunk_state["video_status"])


def poll_and_download_chunk(lesson_id, chunk_state, state):
    """Poll for video completion and download. Returns (part, success)."""
    part = chunk_state["part"]
    video_id = chunk_state["heygen_video_id"]

    if chunk_state.get("video_status") in ("completed", "failed"):
        return (part, chunk_state["video_status"] == "completed")

    print(f"  Polling video for part {part} (video_id={video_id})...")
    video_url = poll_video_status(video_id)

    if video_url:
        video_file = VIDEOS_DIR / f"lesson-{lesson_id}-part-{part}.mp4"
        if download_video(video_url, video_file):
            chunk_state["video_status"] = "completed"
            chunk_state["video_file"] = str(video_file)
        else:
            chunk_state["video_status"] = "download_failed"
    else:
        chunk_state["video_status"] = "failed"

    save_state_safe(state)
    return (part, chunk_state["video_status"] == "completed")


def finalize_lesson(lesson_id, lesson_info, lesson_state, state):
    """Assemble a lesson's completed chunk MP4s into ONE titled render and file
    it at renders-mp4/<program-slug>/avatar/<stem>.mp4 (stem = m<#>_<title>_<date>).

    HeyGen returns one clip per ~200-word chunk; the deliverable is one video per
    lesson, so we concatenate the chunks in order. Returns the final path, or None
    if any chunk is still incomplete (nothing to assemble yet — e.g. under
    --max-parts, or a mid-run state)."""
    chunks = sorted(lesson_state.get("chunks", []), key=lambda c: c["part"])
    parts = []
    for cs in chunks:
        if cs.get("video_status") != "completed" or not cs.get("video_file"):
            print(f"  [finalize] Part {cs.get('part')} not completed — skipping assembly.")
            return None
        p = Path(cs["video_file"])
        if not p.is_file():
            print(f"  [finalize] Missing chunk file {p} — skipping assembly.")
            return None
        parts.append(p)
    if not parts:
        return None

    AVATAR_RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    final_path = AVATAR_RENDERS_DIR / f"{render_stem(lesson_id, lesson_info)}.mp4"

    if len(parts) == 1:
        shutil.copy2(parts[0], final_path)
    else:
        # ffmpeg concat demuxer, stream-copy — every chunk is the same HeyGen
        # avatar/codec, so no re-encode is needed.
        listfile = VIDEOS_DIR / f"concat-{lesson_id}.txt"
        listfile.write_text(
            "".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
        result = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(listfile), "-c", "copy", str(final_path)],
            capture_output=True, text=True)
        listfile.unlink(missing_ok=True)
        if result.returncode != 0:
            print(f"  [finalize] ffmpeg concat failed:\n{result.stderr[-800:]}")
            return None

    lesson_state["final_video"] = str(final_path)
    save_state(state)
    print(f"  [finalize] Filed render → renders-mp4/{PROGRAM_SLUG}/avatar/{final_path.name}")
    return final_path


def process_lesson(lesson_id, state, avatar_id, dry_run=False, max_parts=None):
    """Process a single lesson through the full pipeline."""
    lesson_info = LESSONS[lesson_id]
    lesson_state = state["lessons"].setdefault(lesson_id, {
        "title": lesson_info.get("title", f"Lesson {lesson_id}"),
        "chunks": [],
    })

    print(f"\n{'='*60}")
    print(f"Lesson {lesson_id}: {lesson_info.get('title', 'Untitled')}")
    print(f"{'='*60}")

    # Step 1: Load or export script
    print("\n[1/4] Loading script...")
    script_file = load_or_export_script(lesson_id, lesson_info)
    if not script_file:
        return False

    # Step 2: Split script into chunks
    print("\n[2/4] Splitting script...")
    chunks = split_script(lesson_id)
    if not chunks:
        return False

    # Update state with chunk info (preserves existing progress)
    existing_chunks = {c["part"]: c for c in lesson_state.get("chunks", [])}
    for chunk in chunks:
        part = chunk["part"]
        if part not in existing_chunks:
            existing_chunks[part] = {
                "part": part,
                "words": chunk["words"],
                "script_file": chunk["file"],
                "heygen_video_id": None,
                "video_status": None,
                "video_file": None,
            }
        else:
            existing_chunks[part]["words"] = chunk["words"]
            existing_chunks[part]["script_file"] = chunk["file"]

    lesson_state["chunks"] = [existing_chunks[p] for p in sorted(existing_chunks)]
    save_state(state)

    if dry_run:
        print("\n[DRY RUN] Skipping API calls.")
        return True

    # Process chunks in batches (to respect HeyGen's concurrent video limit)
    chunks_to_process = lesson_state["chunks"]
    if max_parts:
        chunks_to_process = chunks_to_process[:max_parts]

    # Skip chunks that are already done
    todo = [cs for cs in chunks_to_process if cs.get("video_status") != "completed"]
    skipped = len(chunks_to_process) - len(todo)
    if skipped:
        print(f"\n  Skipping {skipped} already-completed parts.")

    if not todo:
        print("\n  All parts already completed.")
        finalize_lesson(lesson_id, lesson_info, lesson_state, state)
        return True

    total_batches = (len(todo) + HEYGEN_CONCURRENT_LIMIT - 1) // HEYGEN_CONCURRENT_LIMIT
    print(f"\n  Processing {len(todo)} parts in {total_batches} batch(es) of {HEYGEN_CONCURRENT_LIMIT}...")

    all_submit_failures = []
    all_completed = 0
    all_failed = 0

    for batch_idx in range(0, len(todo), HEYGEN_CONCURRENT_LIMIT):
        batch = todo[batch_idx:batch_idx + HEYGEN_CONCURRENT_LIMIT]
        batch_num = batch_idx // HEYGEN_CONCURRENT_LIMIT + 1
        part_nums = [cs["part"] for cs in batch]
        print(f"\n-- Batch {batch_num}/{total_batches} (parts {part_nums}) --")

        # Phase 1: Submit the batch (create video from text)
        print(f"  [Submit] Submitting {len(batch)} chunks...")
        pending_polls = []
        with ThreadPoolExecutor(max_workers=HEYGEN_CONCURRENT_LIMIT) as pool:
            future_to_cs = {
                pool.submit(submit_chunk, lesson_id, lesson_info, cs, state, avatar_id): cs
                for cs in batch
            }
            for future in as_completed(future_to_cs):
                cs = future_to_cs[future]
                try:
                    part, video_id, status = future.result()
                except Exception as e:
                    print(f"  Part {cs['part']}: EXCEPTION - {e}")
                    all_submit_failures.append(cs["part"])
                    continue

                if status == "completed":
                    print(f"  Part {part}: already done, skipping.")
                    all_completed += 1
                elif video_id:
                    print(f"  Part {part}: submitted (video_id={video_id})")
                    pending_polls.append(cs)
                else:
                    print(f"  Part {part}: FAILED at submission ({status})")
                    all_submit_failures.append(part)

        if not pending_polls:
            continue

        # Phase 2: Poll and wait for videos to finish rendering
        print(f"  [Poll] Waiting for {len(pending_polls)} videos...")
        with ThreadPoolExecutor(max_workers=len(pending_polls)) as pool:
            future_to_part = {
                pool.submit(poll_and_download_chunk, lesson_id, cs, state): cs["part"]
                for cs in pending_polls
            }
            for future in as_completed(future_to_part):
                part = future_to_part[future]
                try:
                    _, success = future.result()
                except Exception as e:
                    print(f"  Part {part}: EXCEPTION during poll - {e}")
                    success = False
                if success:
                    all_completed += 1
                    print(f"  Part {part}: completed")
                else:
                    all_failed += 1
                    print(f"  Part {part}: FAILED")

    total_processed = all_completed + all_failed + len(all_submit_failures)
    print(f"\n  Results: {all_completed}/{total_processed} videos completed successfully.")
    if all_submit_failures:
        print(f"  Submit failures: parts {all_submit_failures}")
    if all_failed:
        print(f"  Video failures: {all_failed}")

    success = len(all_submit_failures) == 0 and all_failed == 0
    if success:
        finalize_lesson(lesson_id, lesson_info, lesson_state, state)
    return success


def show_status(state):
    """Print a summary of current pipeline progress."""
    print("\n" + "=" * 60)
    print("Pipeline Status")
    print("=" * 60)

    total_chunks = 0
    completed = 0
    failed = 0
    pending = 0

    for lid in sorted(LESSONS.keys()):
        lesson = state.get("lessons", {}).get(lid, {})
        chunks = lesson.get("chunks", [])
        if not chunks:
            print(f"  Lesson {lid}: not started")
            continue

        statuses = []
        for c in chunks:
            total_chunks += 1
            vs = c.get("video_status", "pending")
            if vs == "completed":
                completed += 1
                statuses.append("done")
            elif vs == "failed":
                failed += 1
                statuses.append("FAIL")
            else:
                pending += 1
                statuses.append(vs or "pending")

        parts_str = " | ".join(f"P{c['part']}:{s}" for c, s in zip(chunks, statuses))
        print(f"  Lesson {lid}: [{parts_str}]")

    print(f"\nTotal: {total_chunks} chunks | {completed} completed | {failed} failed | {pending} pending")


def main():
    parser = argparse.ArgumentParser(description="HeyGen Studio: Automated Course Video Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Export and split scripts only, no API calls")
    parser.add_argument("--module", type=str, help="Process only this module (e.g., 1)")
    parser.add_argument("--lesson", type=str, help="Process only this lesson (e.g., 1.0)")
    parser.add_argument("--max-parts", type=int, help="Only process first N parts per lesson")
    parser.add_argument("--status", action="store_true", help="Show current pipeline status")
    parser.add_argument("--list-voices", action="store_true", help="List available HeyGen voices and exit")
    args = parser.parse_args()

    if args.list_voices:
        list_voices()
        return

    state = load_state()

    if args.status:
        show_status(state)
        return

    # Validate API key (only needed when actually calling APIs)
    if not args.dry_run:
        if not HEYGEN_API_KEY or HEYGEN_API_KEY.startswith("your_"):
            print("[ERROR] Set HEYGEN_API_KEY in your .env file")
            print("  1. Copy .env.example to .env")
            print("  2. Add your HeyGen API key")
            sys.exit(1)

    # Create output directories
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    # Figure out which lessons to process
    if args.lesson:
        if args.lesson not in LESSONS:
            print(f"[ERROR] Unknown lesson: {args.lesson}")
            print(f"  Available lessons: {', '.join(sorted(LESSONS.keys()))}")
            sys.exit(1)
        lesson_ids = [args.lesson]
    elif args.module:
        prefix = str(args.module) + "."
        lesson_ids = [lid for lid in sorted(LESSONS.keys()) if lid.startswith(prefix)]
        if not lesson_ids:
            print(f"[ERROR] No lessons found for module {args.module}")
            print(f"  Available lessons: {', '.join(sorted(LESSONS.keys()))}")
            sys.exit(1)
    else:
        lesson_ids = sorted(LESSONS.keys())

    print(f"Processing {len(lesson_ids)} lesson(s): {', '.join(lesson_ids)}")

    # Look up avatar (skip in dry run since we don't need it)
    avatar_id = None
    if not args.dry_run:
        avatar_id = lookup_avatar(state)
        if not avatar_id:
            print("[ERROR] Could not find avatar. Check avatar.id in config.json.")
            sys.exit(1)

    # Process each lesson through the pipeline
    success = 0
    for lid in lesson_ids:
        if process_lesson(lid, state, avatar_id, dry_run=args.dry_run, max_parts=args.max_parts):
            success += 1

    print(f"\n{'='*60}")
    print(f"Done. {success}/{len(lesson_ids)} lessons processed successfully.")
    if not args.dry_run:
        show_status(state)


if __name__ == "__main__":
    main()
