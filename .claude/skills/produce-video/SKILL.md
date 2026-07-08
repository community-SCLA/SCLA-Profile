---
name: produce-video
description: Run the full illustrated-video production loop locally, end to end, in one call — from a raw script/`.txt` handed directly or info given straight in conversation — so you never re-prompt each step. Drafts/refines/files the script, builds the HyperFrames lesson in its style package, bakes scene defaults, checks, renders, frame-verifies the MP4, files it, and archives the workspace. Stops only at the two mandatory human gates (script approval, QA). Use for "produce this video", "make the video from this script", or "run the illustrated pipeline locally".
---

# produce-video — local illustrated-video pipeline orchestrator

## Overview

This is the **local-container orchestrator** for SCLA's illustrated-video pipeline.
It sequences the existing build recipe — `projects/video-production/design-system/CLAUDE.md`
(the 8-step HyperFrames build, voice, style packages, the render/variable gap) —
into a single run so you don't run a prompt per step. Read it as you hit each
phase; this skill only handles sequencing, the two human gates, and the render
landmines below.

**Why local:** rendering needs the local HyperFrames toolchain (headless Chrome,
ffmpeg) that isn't available in a hosted/cloud session.

**Scope:** the illustrated (HyperFrames) path only. HeyGen avatar videos stay
blocked (API key 403 — see `design-system/CLAUDE.md` → "Upgrade path"); don't
render them.

## Two hard rules this skill never breaks

1. **Never cross a human gate.** Script approval and QA are human-only — stop,
   post what's needed, hand control back. Don't self-approve to keep the run going.
2. **Never fabricate SCLA content.** Draft only from provided source material; no
   FERPA/PII in any prompt. No source material given for a script that needs
   drafting → stop and say so.

## Workflow

### Step 0 — Preflight

The entry point is whatever the user hands you directly in conversation — a
`.txt` path or raw script text. The human gates below are direct check-ins
with the user; there's no external system to sync.

Preflight, from repo root:

```bash
date +%Y-%m-%d                                    # today's date for the stem
pkill -f "hyperframes preview" 2>/dev/null || true # stale preview servers cross-contaminate renders
cat /proc/mounts | grep /dev/shm                  # need ≥256M for headless Chrome validate/render
```

If `/dev/shm` is under ~256M: `sudo mount -o remount,size=512M /dev/shm`
(the devcontainer normally does this on start). Confirm the CLI pin (0.7.42) matches
`design-system/package.json` before init.

Then announce the plan: which video(s), and that you'll pause at the two gates.

### Step 1 — Script (draft / refine / verbatim) → approval gate

Determine the script's status by asking the user:

- **Needs drafting** — draft narration from the source material using the matching
  `templates/` prompt (lesson → `heygen-lesson-script.md`; narration → `heygen-narration-prompt.md`;
  social → `social-script-prompt.md`). The `.txt` is plain spoken lines only — no cues,
  headings, or shot list.
- **Provided as-is** — file verbatim, do not redraft.
- **Provided, needs refinement** — refine per `## Refinement notes` + Notes; don't rewrite.

Set the **stem** = `<section>_<program-slug>_<YYYY-MM-DD>` (naming: `videos/README.md`)
and save to `projects/video-production/videos/<program-slug>/<stem>.txt`
(Program = Other → `videos/other/<request-slug>/`, flag in Notes).

**→ SCRIPT GATE.** Show the script to the user for approval. Stop here — resume
only when they approve. Revision requests loop back through this step.

### Step 2 — Sync the approved text

After approval, **the user's approved text is the source of truth.** Copy it back
over the repo `.txt` so production renders what was approved, not the pre-edit draft.

### Step 3 — Workspace + narration

Follow `design-system/CLAUDE.md` → "Building a lesson video" steps 2–3:

```bash
cd projects/video-production/lessons
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <stem> --example=blank --non-interactive
# copy in frame.md, compositions/, assets/ from ../design-system/
cd <stem>
npx hyperframes tts "$(cat ../../videos/<program-slug>/<stem>.txt)" \
  --provider kokoro --voice af_heart --speed 0.95 -o assets/voice/narration.wav
npx hyperframes transcribe assets/voice/narration.wav --model small.en
```

Voice is pinned (`frame.md` → `voice:`) — don't re-decide it.

### Step 4 — Assemble + pick the style package

Build `index.html`: one scene slot per beat from the seven templates, sized to the word
timings, `<audio>` narration at the host root. Copy the demo-reel pattern from
`../design-system/index.html`.

**Make every scene move — the animacy rules (`design-system/frame.md`; graded at QA).**
The templates are the floor, not the finish. Before you size a scene:

- **Map the narration to reveal cues.** From `assets/voice/transcript.json`, get the
  local second each enumerated item is spoken and pass it in `pointCues`
  (`scla-points`) / `stepCues` (`scla-steps`). Items land on the word, not a timer.
- **No stagnant frame beyond ~2s.** A long beat with nothing left to reveal is too
  long — split it. Title cards hold only for the opening line, never over content.
- **Illustrate what's said** — draw the thing (path/map, thinking figure, comparison,
  per-item icons on cue); author bespoke illustrated scenes for concrete narration.
- **Statement vs. quote** — a program thesis is `scla-statement` (bold, unattributed);
  `scla-quote` is only a **named person's** words.
- **Numerals** — scene index small, lower-right; a hero numeral is only a real stat or
  the spoken step, never deck position.

**Style package** — one per video, on every scene. Use the user's pick. If they
don't have one, count that program's delivered `.mp4` files with a matching
illustrated script stem in `videos/<program-slug>/` and rotate summit → horizon
→ cadence (count mod 3); tell the user which one you picked and why.

### Step 5 — Bake scene defaults (the render/variable fix — do not skip)

`hyperframes render` (0.7.38–0.7.42) leaves `getVariables()` empty inside
sub-compositions, so each scene renders its template's **JS-side `defaults`**, not
the `data-variable-values` you passed in `index.html`. Preview/snapshot inject
correctly, so it looks right in snapshots but renders as silent fallback content
(exit 0). Filed upstream: heygen-com/hyperframes#2064.

Before rendering, bake each scene's real content into that scene file's `defaults`
object. For any template mounted more than once (e.g. `scla-points`), make one
per-instance file per mount, each with a unique `data-composition-id` +
`window.__timelines[...]` key. Keep `data-variable-values` for preview parity.
Worked example: `lessons/mini-syllabus_early-career-boost_2026-07-06/`.

### Step 6 — Check + snapshot → QA gate

```bash
npm run check                                  # lint + validate + inspect — always
npx hyperframes snapshot --at <scene-midpoints> # stills for eyeball review
```

Fix anything `check` flags before proceeding.

**→ QA GATE.** Show the snapshots to the user and hand off `templates/qa-checklist.md`
(illustrated section). Stop here — resume only when they sign off.

### Step 7 — Render, frame-verify, file

```bash
pkill -f "hyperframes preview" 2>/dev/null || true   # again — stale servers contaminate renders
npm run render
# frame-verify: snapshots can't catch the render/variable gap — check the actual MP4
ffmpeg -ss <t> -i out.mp4 -frames:v 1 /tmp/frame.png   # one per scene; eyeball real content
```

If a frame shows fallback content, return to Step 5 — a scene's defaults weren't baked.
Once verified, rename the MP4 to `<stem>` and move it beside its script in
`../videos/<program-slug>/`. Upload to Wistia (title = stem); the `.mp4` is **not**
committed.

### Step 8 — Archive the workspace

```bash
cd <repo-root>
bash scripts/archive-lesson.sh <stem>   # → lessons/_archive/<stem>/ (gitignored)
```

## Closing out

Report per video: stem, style package, gate outcomes, and the Wistia URL (or that
upload is pending). Drafted/approved scripts get committed to `main` per the repo's
PR flow. If a HyperFrames bug bit this run and isn't already filed, write it up and
file it upstream before ending (see the render gap in Step 5 as the template).
