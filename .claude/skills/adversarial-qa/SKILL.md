---
name: adversarial-qa
description: Independent adversarial QA gauntlet for SCLA video builds — four reviewer lanes (Timing, Layout, Facts, Presence) each try to break the cut; all four must clear before the human QA gate, and any fix + re-render voids all clears. Use before render (plan audit) and after every render (full gauntlet) of an illustrated HyperFrames lesson or a HeyGen avatar video. Invoke whenever a video build reaches Step 5/6 of /produce-video, whenever the user says "QA the render", "try to break it", "run the gauntlet", "adversarial review", or asks whether a cut is ready for human review — even if they don't name this skill.
---

# adversarial-qa — try to break the render

Four independent review lanes, each hunting a different failure class. The build
agent never grades its own work: each lane runs as a **separate subagent with a
cold context** that receives only file paths and its lane charter — never the
builder's claims about what was fixed. Lanes report findings; the builder fixes;
lanes re-review. This exists because the first at-scale render shipped with
mid-word cuts, an un-spoken 4-step overview, and a 12.6s static card that
`npm run check` could never catch — machine lint checks contracts, not judgment.

## Deterministic first — agents judge, they don't re-derive (2026-07-10)

Since the timeline compiler landed (`projects/video-production/render-qa/`),
most of what the lanes used to hunt by hand is checked deterministically:

- **Pre-render:** `render-qa/preflight.py <workspace>` — anchor/cue drift
  (compiler re-derivation), boundary rules, clip coverage, theme consistency.
- **Post-render:** `render-qa/verify_render.py <workspace> [mp4]` — container
  truth, presence v2 (blank frames, ≥5s stagnation, audio-vs-video), and the
  **shared frame evidence** (`<workspace>/qa/frames/`, 3 full-res stills per
  scene) all lanes read.

**The orchestrator runs these once, BEFORE launching any agents.** A non-zero
exit means fix and re-run — do not spend agent tokens on a cut a script already
rejects. Lanes receive the checker JSON as machine evidence (this is not
"builder claims" — it is the same tool they would run themselves) plus the
shared frame dump, and spend their context on judgment: does the reveal land on
the right word, does the frame depict the sentence, is a flagged low-variance
frame actually bare. Retirement path: as judgment calls get codified into
checkers, lanes shrink — the deterministic gate is the pipeline's future;
the agent lanes are its safety net until the checkers have earned trust.

## The four lanes

| Lane | Agent | Hunts for | Primary evidence |
| --- | --- | --- | --- |
| 01 Timing | `qa-timing` | DRIFT — cue/boundary vs narration | `scripts/check_boundaries.py` + transcript vs frames |
| 02 Layout | `qa-layout` | OVERFLOW — bounds, clipping, tokens | rendered frames, eyeballed |
| 03 Facts | `qa-facts` | MISMATCH — script claim vs source | script `.txt` vs source material |
| 04 Presence | `qa-presence` | GAPS — empty/default/dead frames | `scripts/check_presence.py` + frames |

## Release rule

**The deterministic gate and every launched lane must PASS.** One FAIL blocks
release. After a fix + re-render, the deterministic stage always re-runs (it is
free); the agent lanes re-run **scoped to the blast radius of the fix**:

- fix touched timing, audio, scene structure, or composition markup → re-run
  **all four** lanes (a timing fix can create a layout break);
- fix touched only on-screen text inside `data-variable-values` (no timing, no
  audio, no geometry) → re-run Layout (02) + Facts (03); Timing (01) and
  Presence (04) clears carry over **only if** `preflight.py` and
  `verify_render.py` still pass on the new render.

Lanes never edit files and never soften a finding to keep the pipeline moving;
the human QA gate still follows a clean gauntlet and is never replaced by it.

## When to run

- **Plan audit (pre-render)** — after the compiler has applied
  (`compile_timeline.py --apply`), run `render-qa/preflight.py`. If it passes,
  launch **Lane 03 (Facts) only** — boundary/cue/coverage hunting is now fully
  deterministic pre-render, so Lanes 01/02/04 add nothing before an MP4 exists.
- **Full gauntlet (post-render)** — after every render, before the human QA
  gate: `render-qa/verify_render.py` first, then all four lanes against the MP4
  + shared evidence. This is not optional and not memory-dependent: a
  PostToolUse hook in `.claude/settings.json` detects every HyperFrames render
  command and injects this requirement into the session automatically.

## How to run it

1. Run the deterministic stage yourself:
   `python3 projects/video-production/render-qa/verify_render.py <workspace> --json`
   (post-render; `preflight.py` pre-render). Exit ≠ 0 → fix first, no agents.
2. Collect the inputs (absolute paths): workspace dir, `index.html`,
   `assets/voice/transcript.json`, `assets/voice/narration.wav`, the approved
   script `.txt`, the source material, the MP4, the shared frame dir
   (`<workspace>/qa/frames/`), and the checker JSON paths.
3. Launch the applicable lanes **in parallel, in one turn**, via the Agent tool
   (`subagent_type` = the lane agent name). Give each lane ONLY:
   - the file paths above (including the shared `qa/frames/` — lanes read it
     instead of re-extracting; they may extract *extra* frames to chase a
     suspicion),
   - the mode (`plan` or `render`).
   Do **not** summarize the build, list known issues, or say what was already
   fixed — pre-briefing a reviewer defeats the adversarial design. Checker
   output is machine evidence and is exempt from that rule.
4. Collect the verdicts. Every lane replies with `VERDICT: PASS|FAIL` plus a
   findings table (severity, defect-class, scene/timestamp, description, evidence
   path). The `defect-class` slug is what the snag-log retirement ledger tallies.
5. Apply the release rule. On FAIL: fix, re-render, GOTO 1. On all-PASS: hand
   the lane reports to the human at the QA gate as supporting evidence.
6. Record the outcome in `projects/video-production/render-qa/snag-log.md`. On any
   FAIL, add each blocking finding to this session's entry as a `[defect]` line
   with a `Caught-by: <lane> (<defect-class>)` note, and update the retirement
   ledger (increment/reset the per-template tally per the log's own instructions).
   This is what makes gauntlet retirement evidence-driven — see `snag-loop-design.md`.

## Bundled checkers (deterministic — the orchestrator runs them; lanes read the output)

- `scripts/check_boundaries.py <workspace>` — parses `index.html` scene slots +
  `transcript.json` (+ `ffprobe` on the wav): per-scene last-word gap vs the
  ≥0.5s rule, mid-word/mid-sentence cuts, question-ending air, final-scene hold
  vs true audio end. Exit 1 = violations found. JSON with `--json`.
- `scripts/check_presence.py <video.mp4> <outdir> [--workspace <ws>]` — v2:
  samples 2 fps + the exact final frame; flags near-blank frames (stddev AND
  content-pixel count — textured/navy canvases no longer false-positive),
  pixel-static stagnation (≥5s while narration speaks = violation, 3–5s =
  warning for the lane to judge), audio-outliving-video. `--workspace` enables
  the 0.7s entrance-grace window and transcript-aware stagnation. Exit 1 =
  violations. JSON with `--json`.
- `projects/video-production/render-qa/{compile_timeline,preflight,verify_render}.py`
  — the compiler and the two one-command gates (see "Deterministic first").

Scripts are evidence generators, not the verdict: a lane may FAIL a cut the
scripts pass (e.g., a reveal that lands on the wrong word, a fact the script
can't see) and must confirm script findings against real frames before failing.

## Failure-class references (what each lane greps the rules from)

- Timing + Presence rules: `projects/video-production/design-system/frame.md` →
  "Scene boundaries, padding & endings" + "Every scene earns its seconds"
- Layout tokens/bounds: `frame.md` frontmatter + "The frame" + "Type rules"
- Facts: `projects/video-production/CLAUDE.md` → "Never fabricate SCLA content";
  the source material named in the request/Notion row
- Avatar-path presence: avatar visible the full runtime (HeyGen builds only)
