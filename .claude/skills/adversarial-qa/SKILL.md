---
name: adversarial-qa
description: On-demand adversarial deep audit for SCLA video builds — four independent reviewer lanes (Timing, Layout, Facts, Presence) try to break a cut. NOT part of the default /produce-video run (deterministic gates + builder self-review + the human QA gate cover it). Invoke only when the user explicitly asks ("QA the render", "try to break it", "run the gauntlet", "adversarial review") or as escalation when a human rejects a cut and the cause isn't obvious.
---

# adversarial-qa — try to break the render (escalation tool)

Four independent review lanes, each hunting a different failure class. Each lane
runs as a separate subagent with a cold context that receives only file paths
and its charter — never the builder's claims about what was fixed. This is the
deep-audit escalation path, not a standing gate: the default pipeline relies on
the deterministic checkers plus the builder's frame review and the human QA gate.

## Deterministic first — agents judge, they don't re-derive

Run the machine checks before spending any agent tokens:

- **Pre-render:** `projects/video-production/render-qa/preflight.py <workspace>`
  — anchor/cue drift, boundary rules, clip coverage, theme consistency.
- **Post-render:** `render-qa/verify_render.py <workspace> [mp4]` — container
  truth, presence v2 (blank frames, stagnation, audio-vs-video), and the shared
  frame evidence (`<workspace>/qa/frames/`, 3 stills per scene) all lanes read.

A non-zero exit means fix and re-run — do not launch agents on a cut a script
already rejects.

## The four lanes

| Lane | Agent | Hunts for | Primary evidence |
| --- | --- | --- | --- |
| 01 Timing | `qa-timing` | DRIFT — cue/boundary vs narration | checker JSON + transcript vs frames |
| 02 Layout | `qa-layout` | OVERFLOW — bounds, clipping, tokens | rendered frames, eyeballed |
| 03 Facts | `qa-facts` | MISMATCH — script claim vs source | script `.txt` vs source material |
| 04 Presence | `qa-presence` | GAPS — empty/default/dead frames | checker JSON + frames |

Lane 03 (Facts) can also run alone at script stage — /produce-video Step 1 uses
it that way for scripts drafted from source material, since facts are a property
of the script, not the render.

## How to run it

1. Run the deterministic stage yourself (`verify_render.py --json` post-render,
   `preflight.py` pre-render). Exit != 0 → fix first, no agents.
2. Collect absolute paths: workspace, `index.html`, `assets/voice/transcript.json`,
   `assets/voice/narration.wav`, the approved script `.txt`, the source material,
   the MP4, `qa/frames/`, and the checker JSON.
3. Launch the lanes in parallel, in one turn, via the Agent tool. Give each lane
   ONLY the paths and the mode (`plan` or `render`) — never a summary of the
   build or what was already fixed; pre-briefing a reviewer defeats the
   adversarial design. Checker output is machine evidence and is exempt.
4. Collect verdicts: each lane replies `VERDICT: PASS|FAIL` plus a findings
   table (severity, defect-class, scene/timestamp, description, evidence path).
5. Release rule while this audit is in play: every launched lane must PASS.
   After a fix + re-render, the deterministic stage always re-runs; re-run
   agent lanes scoped to the fix's blast radius (timing/audio/structure fix →
   all lanes; text-only variable fix → Layout + Facts, with Timing/Presence
   clears carrying over only if preflight + verify still pass).
6. Note any real snag the audit surfaced in
   `projects/video-production/render-qa/snag-log.md` (one line under Known
   snags if it's recurrent-worthy).

Lanes never edit files and never soften a finding; the human QA gate still
follows and is never replaced by this audit.

## Bundled checkers (evidence generators, not the verdict)

- `scripts/check_boundaries.py <workspace>` — per-scene last-word air vs the
  0.5s rule, mid-word/mid-sentence cuts, question air, final-scene hold. `--json`.
- `scripts/check_presence.py <video.mp4> <outdir> [--workspace <ws>]` — v2:
  near-blank frames, pixel-static stagnation, audio-outliving-video;
  `--workspace` enables entrance-grace + transcript-aware stagnation. `--json`.
- `render-qa/{compile_timeline,preflight,verify_render}.py` — the compiler and
  the two one-command gates.

A lane may FAIL a cut the scripts pass (a reveal on the wrong word, a fact the
script can't see) and must confirm script findings against real frames before
failing.

## Failure-class references

- Timing + Presence rules: `projects/video-production/design-system/frame.md`
  → "Scene boundaries, padding & endings" + "Every scene earns its seconds"
- Layout tokens/bounds: `frame.md` frontmatter + "The frame" + "Type rules"
- Facts: `projects/video-production/CLAUDE.md` → "Never fabricate SCLA content";
  the source material named in the request
- Avatar-path presence: avatar visible the full runtime (HeyGen builds only)
