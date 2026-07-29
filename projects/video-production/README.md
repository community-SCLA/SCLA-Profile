# Video production

SCLA's lesson-video factory. A refined script goes in; a Wistia-hosted MP4 comes out.

**Agents: read `CLAUDE.md`, not this file.** This is the human door.

## The two render paths

- **Illustrated** (default for concept lessons) — `design-system/` holds the branded
  scene templates and the design contract; `render-qa/` derives every timing and grades
  every frame. No per-minute avatar cost.
- **Avatar** — `avatar-pipeline/` drives the HeyGen API for talking-head and
  translation work.

## How to run it

One call: `/produce-video`. It refines raw scripts, builds one pilot video, stops for
your approval, then drains the queue unattended. `bash scripts/batch-status.sh` tells
you what's left, read from disk alone.

## Two things that will confuse you otherwise

**State is the folder.** Nothing narrates the pipeline. A script's location *is* its
stage — raw at a program root, then `refined/`, then `rendered/`. A stem carries exactly
one date: the most recent action.

**Authors declare text; tools compute every number.** A builder writes narration spans
and cue phrases into `scenes.json`. Timings, boundaries and durations are derived. A
hand-edited `data-start` is a defect, not a shortcut.

## Layout

Standard project shape — `src/` code, `config/` settings, `docs/` read-once notes,
`logs/` run history. `design-system/` is the exception: HyperFrames dictates its
layout, and that divergence is written down in `design-system/docs/README.md`.
