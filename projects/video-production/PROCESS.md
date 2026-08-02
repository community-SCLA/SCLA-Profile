# PROCESS.md — the agent contract for SCLA lesson videos

This is what an agent obeys when it works on a lesson video. It is normative.
The project README is for people and carries no rules; anything binding is
here or in an executable check under `checks/`.

The job, verbatim from the owner, is in `brief.md`. Read it once before your
first lesson.

## The unit of work is a lesson

One lesson = one script, one status record, one workspace, one MP4, one Wistia
media. Its identity is its **stem**: the script filename without `.txt`.

```
lesson-scripts/<program>/refined/<stem>.txt     the narration source
lessons/<program>/<stem>/status.yml             where it stands
lessons/<program>/<stem>/workspace/             the HyperFrames project (tracked)
lessons/<program>/<stem>/audio/                 narration + word timings (gitignored)
lessons/<program>/<stem>/render/                the MP4 (gitignored)
```

## Script rules

These are the live rules from the retired script-library README, kept because
they still bind.

- **The stem is the lesson's identity and never changes.** It is the script
  filename, the lesson directory name, and the base of the delivered MP4.
  Renaming a stem breaks the lock below and orphans the status record.
- **A working artifact carries NO date.** Not the script, not the lesson
  directory, not the workspace. Only the delivered MP4 is dated, with the date
  it was rendered: `<stem>_YYYY-MM-DD.mp4`. A name that moves cannot be a lock.
- **`mkdir lessons/<program>/<stem>/` is the build lock.** Creating that
  directory is how one agent claims a lesson. If it already exists, another
  agent owns the lesson — read its `status.yml` and pick a different one.
- **Narration is plain spoken text.** No cues, no shot lists, no `[On screen:`
  brackets, no markdown, no headings, no bullets. If it cannot be spoken aloud
  as written, it is not narration.
- **Lowercase stems throughout** — no spaces, no capitals, no `+`. Underscores
  separate parts; hyphens go inside a part.
- **`refined/` is the only home for a narration-ready script.** A script never
  leaves it, not when it is built and not when it is published — publication is
  a field in `status.yml`, not a location. Sibling folders hold scripts that
  are *not* narration-ready: `unrefined/` (drafted, needs refinement) and
  `blocked/` (quarantined, waiting on the owner).

## Where a lesson stands

`lessons/<program>/<stem>/status.yml`, one per lesson, written by whichever
agent completes a stage:

```yaml
stem: m2_the-value-of-building-mid-career-momentum
program: mid-career-momentum
script: projects/video-production/lesson-scripts/mid-career-momentum/refined/m2_the-value-of-building-mid-career-momentum.txt
stage: composed          # scripted|narrated|composed|rendered|published|blocked
next_action: "Render 1920x1080, then publish to the program's Wistia project"
blocked: null            # non-null iff stage == blocked
wistia_hashed_id: null   # set only at published; never invented
render_date: null        # set only at published
updated: 2026-08-02
```

A blocked lesson names who it waits on, so the board can show the owner only
their own queue:

```yaml
stage: blocked
blocked:
  on: owner              # owner | vendor | upstream
  reason: "Never defines or demonstrates a 'visibility action' despite the title"
  since: 2026-07-22
next_action: "Owner decides: rewrite the script or drop the lesson"
```

`stage` and `next_action` are the two fields a resuming session reads. A record
is never deleted — a published lesson keeps its record and its workspace, so a
correction is an edit, not a rebuild. `checks/verify-status-records.py` grades
every record; `checks/status.py` prints all of them.

## The six stages

Each stage names what must be true to leave it. Do not advance a stage until
its exit criteria pass; do not skip a stage.

### 1. Scripted
The refined `.txt` reads as narration.
*Exit:* `checks/verify-narration-fixes.py --dir lesson-scripts/<program>/refined`
exits 0; no `[On screen:` cues or other shot direction; no name from
`design-system/config/tokens.yml` `retired-names:` appears in the spoken copy;
`status.yml` exists at stage `scripted`.

### 2. Narrated
Narration audio exists with word timings.
*Exit:* `audio/narration.mp3` and `audio/narration.words.json` both exist,
synthesized with the pinned voice from `design-system/config/tokens.yml`
(`provider: heygen`, `voice_id: 442360a3e0894fbd85024ff64cc2b928`, `speed: 1.0`)
— never a hand-picked voice; no audio gap or dead pause beyond the agreed
threshold; the transcript's word count reconciles with the script.

### 3. Composed
A HyperFrames workspace renders end to end.
*Exit:* `workspace/` validates; every color, type size and spacing value traces
to `design-system/config/tokens.yml` — nothing hand-picked; body copy at or
above the 40px floor and labels at or above 20px; no element crosses the 72px
safe area or drops below the 960px content bottom; the title-card eyebrow is
derived from the `programs:` map, never authored; frequent scene changes, no
static stretch, no text/illustration overlap, no sameness between scenes or
between videos; the timeline matches the narration with no drift.

### 4. Rendered
An MP4 exists on disk.
*Exit:* `render/<stem>_<render-date>.mp4` plays its full length; no dead,
empty or default frames anywhere in the runtime; audio stays in sync to the
end; the thumbnail is pulled after entrances settle (the whole entrance settles
by 1.2s), never frame 0.

### 5. Published
The video is live on Wistia and plays.
*Exit:* uploaded to that program's Wistia project, looked up in
`config/endpoints.json` — never hardcoded; title per the convention there;
description derived from that lesson's own opening narration; the custom still
set from the stage-4 thumbnail; a fresh GET of the media returns 200; and
`status.yml` records `stage: published`, the real `wistia_hashed_id` and the
`render_date`. **The upload token cannot delete** — get the upload right the
first time, because a wrong one cannot be removed by any agent.

### 6. Blocked
Any stage may exit sideways to `blocked` when it needs a decision an agent
cannot make.
*Exit:* there is no automatic exit. The record must carry `blocked.on`
(`owner`, `vendor` or `upstream`), a `reason` a reader can act on, a `since`
date, and a `next_action` addressed to whoever is named. The owner resolves it;
an agent then rewrites the record back to the stage the work actually resumes
at.

## Never

- Never open, cite, port or restore anything under an `_archive/` folder.
- Never invent a Wistia ID, a hashed ID or any other integration ID. Unknown
  stays `null`.
- Never delete a status record or a workspace.
- Never rename a stem.
- Never advance a stage whose exit criteria you have not actually run.
