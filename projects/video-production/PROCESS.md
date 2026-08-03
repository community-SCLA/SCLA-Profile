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
lessons/<program>/<stem>/storyboard.md          the approved design, beat by beat (tracked)
lessons/<program>/<stem>/workspace/             the HyperFrames project (tracked)
lessons/<program>/<stem>/audio/                 narration + word timings (gitignored)
lessons/<program>/<stem>/render/                the MP4 (gitignored)
lessons/<program>/<stem>/qa/certification.md    the gauntlet + screening verdict (tracked)
```

## How a video is made — the studio, not a lone builder

No single agent takes a lesson from script to MP4 on its own word. The work
is split across Ringer rounds with **independent verification between every
creative decision and the next stage**:

1. **Author** — one worker per lesson synthesizes narration (stage 2) and
   drafts `storyboard.md` (stage 3 draft): every beat keyed to the word
   timings, every visual traced to tokens.
2. **Critic panel** — separate read-only workers, each with a distinct lens
   (brand & design-system cohesion; motion & engagement; instructional
   clarity for the SCLA audience), review the SAME storyboards in parallel
   and file structured findings. They never edit. The orchestrator
   synthesizes, gets fixes made, and records the verdict in
   `storyboard.md` — only then is the lesson `storyboarded`.
3. **Builder** — one worker per lesson implements the approved storyboard in
   HyperFrames (stage 4) and renders the MP4 (stage 5). A deviation from the
   storyboard is recorded in `storyboard.md`, never silent.
4. **QA gauntlet** — four auditors per video, none of whom built it, each
   inspecting rendered pixels (extracted frames), not exit codes: presence
   (no blank/dead/default frames), layout (safe area, type floors, overlap,
   token colors), timing (visuals land on the spoken cue), fidelity
   (on-screen and spoken copy match the script and SCLA fact base — nothing
   fabricated, no retired names).
5. **Screening panel** — fixed member personas drawn from who SCLA serves
   watch the actual video and grade hook, clarity, pacing, engagement, and
   whether they would keep watching. The same panel re-runs after changes.
6. **Fix loop** — confirmed findings go to fix workers who did not find
   them; the gauntlet and panel then re-run until clean. Only the
   orchestrator writes `qa/certification.md` — a builder never does.

Two structural rules make this honest: **a finding is only real once the
orchestrator confirms it against the artifact**, and **no agent advances a
stage on its own self-report** — gates read process exit codes and pixels.

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
stage: composed          # scripted|narrated|storyboarded|composed|rendered|certified|published|blocked
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

## The eight stages

Each stage names what must be true to leave it. Do not advance a stage until
its exit criteria pass; do not skip a stage. A stage whose exit criteria
include review by other agents (`storyboarded`, `certified`) is advanced only
by the orchestrator after that review — never by the worker whose output is
under review.

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

### 3. Storyboarded
The design exists on paper and survived independent critique before any code.
*Exit:* `storyboard.md` sits in the lesson dir and passes
`checks/verify-storyboard.py --lesson lessons/<program>/<stem>` — every beat
keyed to the narration word timings and covering the full runtime, every
visual concept and on-screen line named, every color/type/spacing choice
traced to `design-system/config/tokens.yml`, no retired name anywhere; AND a
`## Panel Verdict` section records that an independent critic panel (Ringer,
≥2 critics, distinct lenses, none of them the author) reviewed it and the
orchestrator resolved every P0/P1 finding and wrote `Approved: yes` with the
run name and date. The author never writes its own verdict.

### 4. Composed
A HyperFrames workspace renders end to end and implements the storyboard.
*Exit:* `workspace/` validates; the composition implements the approved
`storyboard.md` beat for beat (a deliberate deviation is recorded there,
never silent); every color, type size and spacing value traces
to `design-system/config/tokens.yml` — nothing hand-picked; body copy at or
above the 40px floor and labels at or above 20px; no element crosses the 72px
safe area or drops below the 960px content bottom; the title-card eyebrow is
derived from the `programs:` map, never authored; frequent scene changes, no
static stretch, no text/illustration overlap, no sameness between scenes or
between videos; the timeline is driven by `audio/narration.words.json` with
no drift.

### 5. Rendered
An MP4 exists on disk.
*Exit:* `render/<stem>_<render-date>.mp4` plays its full length; no dead,
empty or default frames anywhere in the runtime; audio stays in sync to the
end; the thumbnail is pulled after entrances settle (the whole entrance settles
by 1.2s), never frame 0; AND
`checks/verify-video-quality.py --dir lessons/<program>/<stem>` exits 0 — the
owner-feedback gates of 2026-08-03: palette balance (blue/gold present,
near-black rationed), no blank frames, no interior dead-air, no exposed
clicks, and the 40px/700 type floors in the workspace source.

### 6. Certified
Workers who did not build the video looked at its pixels and said so.
*Exit:* `qa/certification.md` sits in the lesson dir and passes
`checks/verify-certification.py --lesson lessons/<program>/<stem>` — all four
gauntlet lanes (presence, layout, timing, fidelity) ran against extracted
frames of the actual MP4 and PASS with zero open P0/P1 findings; the
screening panel of member personas watched it and a majority would keep
watching; the file names the Ringer run(s) and date. Written only by the
orchestrator from run artifacts — never by the builder, and never from a
worker's self-reported gate result: re-run the verifiers and read the exit
codes.

### 7. Published
The video is live on Wistia and plays. Only a `certified` lesson may be
published, and only after the owner's explicit sign-off on the actual MP4.
*Exit:* uploaded to that program's Wistia project, looked up in
`config/endpoints.json` — never hardcoded; title per the convention there;
description derived from that lesson's own opening narration; the custom still
set from the stage-4 thumbnail; a fresh GET of the media returns 200; and
`status.yml` records `stage: published`, the real `wistia_hashed_id` and the
`render_date`. **The upload token cannot delete** — get the upload right the
first time, because a wrong one cannot be removed by any agent.

### 8. Blocked
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
- Never grade your own build. Certification and storyboard approval come only
  from workers who did not produce the artifact, synthesized by the
  orchestrator.
- Never trust a worker's self-reported gate result — re-run the check and
  read the process exit code.
