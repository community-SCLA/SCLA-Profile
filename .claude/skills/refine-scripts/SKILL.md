---
name: refine-scripts
description: Batch-refine SCLA lesson scripts — drains every raw .txt sitting at lesson-scripts/<program-slug>/ root into that program's refined/ folder, one cold subagent per script so the orchestrating session never loads script bodies into its own context. Mandatory qa-facts pass on anything drafted or refined. Never renders, never blocks for approval — refined/ is the open human review buffer. Upstream half of the SCLA lesson pipeline (dispatcher: /produce-video; downstream: /render-lessons).
---

# refine-scripts — drain raw scripts into `refined/`

**State is the folder, not a table.** A script's location *is* its lifecycle:

```
lesson-scripts/<program-slug>/*.txt         raw intake, HyperFrames route — queue
lesson-scripts/<program-slug>/avatar/*.txt  raw intake, HeyGen-avatar route — queue
lesson-scripts/<program-slug>/refined/      refined HyperFrames queue — /render-lessons
lesson-scripts/<program-slug>/refined/avatar/  refined avatar queue — avatar-pipeline
lesson-scripts/<program-slug>/rendered/     published (MP4 filed + on Wistia)
```

**Render route = location.** A raw script's folder declares how it renders:
program root → illustrated (HyperFrames), `avatar/` subfolder → talking-head
(HeyGen). Refinement preserves the split: root → `refined/`, `avatar/` →
`refined/avatar/`. The two never mix — `/render-lessons` builds only `refined/`
root; `avatar-pipeline/config.json` points only into `refined/avatar/`.

**Compiled-bundle intake:** when a program arrives as one `.txt` holding every
lesson, split it into per-lesson raws first. Each lesson block's route comes from
its `Render: avatar` / `Render: hyperframes` tag; with no tag, infer (script
written as an AI-avatar read → avatar; script carrying production notes →
HyperFrames) and **list the inferred routing for the human to confirm before
refining**. Avatar-route raws are written to `avatar/`, the rest to the root.

`refinement-log.md` is a **ledger only** (dates, locations, notes for humans) —
never read it to decide what to do; the folders decide.

## Orchestrator protocol (context discipline)

The session that runs this skill is a dispatcher. It lists queues, spawns
subagents, moves nothing by hand it doesn't have to, and **never reads a script
body inline** — that's what keeps a multi-script batch from blowing up one
session's context.

1. **Queue:** `ls` each `lesson-scripts/<program-slug>/` root **and** its
   `avatar/` subfolder — every `*.txt` in either is raw (root = HyperFrames
   route → `refined/`; `avatar/` = HeyGen route → `refined/avatar/`). Use a
   non-recursive `ls` per folder, not a recursive `find` (don't re-sweep
   `refined/`). (`mkdir -p` the target `refined/` or `refined/avatar/` on first
   use; absolute paths — the governance hook rejects relative/variable forms.)
   The per-script subagent's target path mirrors the source: a raw at
   `avatar/<stem>.txt` refines to `refined/avatar/<stem>.txt`.
2. **Skip list:** any raw script whose ledger row (or filename) carries an open
   human question (e.g. "does a pointer-to-a-PDF lesson need a video at all?")
   is **skipped, not refined blind** — leave it at root, keep the ledger note,
   and name it in the close-out so the human answers it.
3. **Per script, dispatch one cold subagent** (general-purpose; strong model —
   this is brand-voice + judgment work, the highest-stakes text in the
   pipeline). Prompt it with *paths, not content*:
   - the raw `.txt` path and the target path
     `lesson-scripts/<program-slug>/refined/<same-stem>.txt`
   - "Read the **Refinement rules** section of
     `.claude/skills/refine-scripts/SKILL.md` and `brand/voice-and-tone.md`,
     then refine the script accordingly. Write the result to the target path.
     Report: word count before/after, what you cut, any claim you could not
     verify."
4. **Facts pass:** for every drafted/refined script, spawn the `qa-facts` agent
   (cold context is the point) with only file paths: the refined `.txt` + the
   source material. A verbatim user-provided script skips this (the human owns
   it). Unverifiable claims → the script still moves to `refined/`, but the
   ledger row and close-out flag it loudly.
5. **Book-keeping (orchestrator, not subagent):** `git mv`/remove the raw
   original once the refined copy exists (the stem stays identical), update the
   ledger row (Refined date + notes), commit per the repo flow.

## Refinement rules (the subagent reads this section)

- Strip capture noise hard: `LESSON CAPTURE` headers, `[IMAGE]`/`[VIDEO]`
  markers, chart-description prose, duplicated paragraphs, inserted stat
  tangents.
- **Never cut a callback to what the viewer already built or named** — a named
  tool, "Module N", their purpose statement. Keep enumerated source lists
  complete.
- Output is plain spoken lines only — no cues, headings, or shot lists; ~580
  words is the working target for a lesson (match the seven 2026-07-12
  refinements in `refined/` for register).
- Spoken enumerations should resolve (end on a question or closing item) so
  scenes can cut cleanly.
- Never fabricate SCLA content; anything not in the source material is
  `TODO: needs input`, surfaced in the report, never invented. No FERPA/PII.
- Prompt templates for drafting from scratch: `projects/video-production/script-templates/`.

## Close-out

Report per script: stem, before/after word counts, facts verdict, skipped-with-
question items. `refined/` is now the render queue — remind the human they can
read/edit/delete anything there at any time before a `/render-lessons` run
drains it; nothing blocks on them.

Any **skipped-with-question item is owner-actionable** — **ask the human
directly** what to do with it (AskUserQuestion when the session is interactive),
don't just list it and move on. If a snag rolled forward to
`render-qa/snag-log.md`'s Open list, surface it the same way per its header
rules — the human should never have to open the log.
