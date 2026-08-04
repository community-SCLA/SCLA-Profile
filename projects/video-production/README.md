# Video production

SCLA's lesson-video factory. An approved script goes in; a Wistia-hosted MP4 comes out.

**Agents: read `CLAUDE.md`, not this file.** This is the human door.

## What it makes

**Illustrated lesson videos** — `design-system/` holds the branded scene templates and
the design contract; `render-qa/` derives every timing and grades every frame. No
per-minute avatar cost. This is the only path in this tree: the talking-head lane was
deleted 2026-08-04 (its code path had already gone on 2026-08-02), and a lesson that
genuinely needs a human face is a HeyGen web-UI job done by hand, outside the factory.

## How to run it

One call: `/produce-video`. It refines raw scripts, builds one pilot video, stops for
your approval, then drains the queue unattended. `bash scripts/batch-status.sh` tells
you what's left, read from disk alone.

## Two things that will confuse you otherwise

**State is the folder, and the folder is named for the stage.** Nothing narrates the
pipeline. A script's location *is* its stage — `inbox/` (raw), then `ready/` (approved,
waiting to build), then `published/` (live on Wistia). A working artifact carries no
date at all; only the delivered MP4 does.

**Authors declare text; tools compute every number.** A builder writes narration spans
and cue phrases into `scenes.json`. Timings, boundaries and durations are derived. A
hand-edited `data-start` is a defect, not a shortcut.

## Layout

Standard project shape — `src/` code, `config/` settings, `docs/` read-once notes,
`logs/` run history. `design-system/` is the exception: HyperFrames dictates its
layout, and that divergence is written down in `design-system/docs/README.md`.
