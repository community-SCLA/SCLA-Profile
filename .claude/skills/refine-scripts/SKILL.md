---
name: refine-scripts
description: Batch-refine SCLA lesson scripts — drains every raw .txt in lesson-scripts/<program-slug>/inbox/ into that program's ready/ folder, one cold subagent per script so the orchestrating session never loads script bodies into its own context. Mandatory qa-facts pass on anything drafted or refined. Never renders, never blocks for approval — ready/ is the open human review buffer. Upstream half of the SCLA lesson pipeline (dispatcher: /produce-video; downstream: /render-lessons).
---

# refine-scripts — drain `inbox/` into `ready/`

**State is the folder, not a table.** A script's location *is* its lifecycle:

```
lesson-scripts/<program-slug>/inbox/        RAW — captured, not yet refined (this skill's queue)
lesson-scripts/<program-slug>/ready/        READY — refined + approved, /render-lessons builds it
lesson-scripts/<program-slug>/published/    PUBLISHED — live on Wistia
```

**The folder name IS the stage name** (2026-08-04), and a raw script never sits
loose at the program root — it goes in `inbox/`. One route, one destination:
`inbox/` → `ready/`. The `avatar/` split this skill used to preserve is gone,
deleted with the avatar lane on 2026-08-04: every lesson is illustrated
(HyperFrames). A lesson that genuinely needs a talking head is a HeyGen web-UI
job the owner does by hand, not a folder in this tree.

**Compiled-bundle intake:** when a program arrives as one `.txt` holding every
lesson, split it into per-lesson raws in `inbox/` first, then refine each.

`refinement-log.md` is a **ledger only** (dates, locations, notes for humans) —
never read it to decide what to do; the folders decide.

## Orchestrator protocol (context discipline)

The session that runs this skill is a dispatcher. It lists queues, spawns
subagents, moves nothing by hand it doesn't have to, and **never reads a script
body inline** — that's what keeps a multi-script batch from blowing up one
session's context.

1. **Queue:** `ls` each `lesson-scripts/<program-slug>/inbox/` — every `*.txt`
   there is raw and refines to `ready/<same-stem>.txt`. Use a non-recursive `ls`
   per folder, not a recursive `find` (don't re-sweep `ready/`). If you find a
   loose `*.txt` at a program root, `git mv` it into `inbox/` before doing
   anything else: raw scripts are not filed at the root, and
   `lint-refs.sh` check 13 fails on one that is.
2. **Skip list:** any raw script whose ledger row (or filename) carries an open
   human question (e.g. "does a pointer-to-a-PDF lesson need a video at all?")
   is **skipped, not refined blind** — leave it in `inbox/`, keep the ledger
   note, and name it in the close-out so the human answers it.
3. **Per script, dispatch one cold subagent** (general-purpose; strong model —
   this is brand-voice + judgment work, the highest-stakes text in the
   pipeline). Prompt it with *paths, not content*:
   - the raw `.txt` path and the target path
     `lesson-scripts/<program-slug>/ready/<same-stem>.txt`
   - "Read the **Refinement rules** section of
     `.claude/skills/refine-scripts/SKILL.md` and `brand/voice-and-tone.md`,
     then refine the script accordingly. Write the result to the target path.
     Report: word count before/after, what you cut, any claim you could not
     verify."
3b. **Copy gate on the output (orchestrator, mechanical — not a judgement call):**
   the moment a refined `.txt` exists, run it through the same checker the build
   uses, and do not move on until it is clean or you can name why a finding is
   wrong:

   ```bash
   python3 projects/video-production/render-qa/src/check_copy.py \
       lesson-scripts/<program-slug>/ready/<stem>.txt
   ```

   Exit 0 = clean. Each finding names the list and the item missing its
   conjunction; fix it **in the script**, here, and re-run.

   This step exists because the conjunction rule below was already written in
   this file as prose and was violated anyway: the 2026-07-28 `better-decisions`
   build shipped "Meaning? Mentorship? Growth?" with no connector, and the
   defect was in the approved script, not the frame. The owner then had to spend
   a review catching by eye something a command answers in 200ms. A rule a
   subagent is asked to remember is a request; a command it must run is a
   mechanism (repo-hygiene STD-35).

   **It reports, it does not block.** A sweep of the 32-script library found a
   minority of findings are rhetoric or definitions rather than lists — "Not
   five months. Five years.", "Consulting is insight." Those legitimately take
   no conjunction. Judge each finding; fix the real ones. Never "fix" a false
   positive by bending the sentence.

4. **Facts pass:** for every drafted/refined script, spawn the `qa-facts` agent
   (cold context is the point) with only file paths: the refined `.txt` + the
   source material. A verbatim user-provided script skips this (the human owns
   it). Unverifiable claims → the script still moves to `ready/`, but the
   ledger row and close-out flag it loudly.
5. **Book-keeping (orchestrator, not subagent):** `git mv`/remove the raw
   original once the refined copy exists (the stem stays identical), update the
   ledger row (Refined date + notes), run `bash scripts/batch-status.sh --write`
   to regenerate `projects/video-production/PIPELINE-STATUS.md` (a build
   artifact of the ledger + folders, never hand-edited — see its own header),
   stage it alongside the ledger/script changes, commit per the repo flow.

## Refinement rules (the subagent reads this section)

- Strip capture noise hard: `LESSON CAPTURE` headers, `[IMAGE]`/`[VIDEO]`
  markers, chart-description prose, duplicated paragraphs, inserted stat
  tangents.
- **Never cut a callback to what the viewer already built or named** — a named
  tool, "Module N", their purpose statement. Keep enumerated source lists
  complete.
- Output is plain spoken lines only — no cues, headings, or shot lists; ~580
  words is the working target for a lesson (match the seven 2026-07-12
  refinements in `ready/` for register).
- **Every spoken list of ≥3 items MUST carry "and" or "or" before its final
  item.** Not a preference — `render-qa/src/check_copy.py` fails the build on it at
  preflight, and the repair is here in the script, not downstream in the frame.
  Applies whether the items are one comma list or separate fragments:
  "Meaning? Mentorship? Growth?" → "Meaning? Mentorship? **Or** growth?";
  "…different learning opportunities, different next steps." → "…**or**
  different next steps." Without the conjunction the narration doesn't resolve,
  it just stops, and the listener can't hear the list ended. (Owner has raised
  this twice — 2026-07-27 and 2026-07-28.)
- Spoken enumerations should otherwise resolve (end on a question or closing
  item) so scenes can cut cleanly.
- **~14-word declarative sentences; no long comma chains.** A comma-heavy
  sentence drops the TTS to ~115 wpm and reads as slow. Decided with Motion v2
  on 2026-07-27 and never written down until 2026-07-28.
- Never fabricate SCLA content; anything not in the source material is
  `TODO: needs input`, surfaced in the report, never invented. No FERPA/PII.
- Prompt templates for drafting from scratch: `projects/video-production/script-templates/`.

## Close-out

Report per script: stem, before/after word counts, facts verdict, skipped-with-
question items. `ready/` is now the render queue — remind the human they can
read/edit/delete anything there at any time before a `/render-lessons` run
drains it; nothing blocks on them.

Any **skipped-with-question item is owner-actionable** — **ask the human
directly** what to do with it (AskUserQuestion when the session is interactive),
don't just list it and move on. If a snag rolled forward to
`render-qa/logs/snag-log.md`'s Open list, surface it the same way per its header
rules — the human should never have to open the log.
