# Snag log — render-session memory

Cross-session memory for SCLA video production. `/produce-video` Step 0 reads
**Known snags** before building; Step 7 appends anything new. Keep it small and
actionable — this is a checklist, not a ledger. History lives in the dated
session notes below (append-only). Sibling: `BUILD-LOG.md` (the 2026-07-10
pipeline overhaul record).

## Known snags — read before building

- [upstream] Idle pulses that animate `scale` + SVG `opacity` together can leave
  ghost/double-draw artifacts in the streaming encode (seen on scla-career-map,
  2026-07-10). Use translate-only pulses; the y-nudge pattern renders clean.
- [env] `npx hyperframes tts` can resolve a Python without `kokoro_onnx` — set
  `HYPERFRAMES_PYTHON` to the interpreter that has it (also in /produce-video Step 0).
- [upstream] hyperframes ≥0.7.56 removed `tts --provider` (kokoro is the only
  built-in engine now) — run `tts` without it; `--voice`/`--speed` still work.
  The /produce-video Step 2 command block predates this (2026-07-13).
- [authoring] whisper emits em-dash compounds as ONE token (`buzzwords—just`);
  anchor/cue phrases can't match inside them — quote the compound verbatim from
  the transcript, or pick a phrase that clears it (2026-07-13).

Resolved structurally (no longer live, kept for pattern-matching): zero-gap
padding non-convergence (compile_timeline keys shifts by word index since
2026-07-13); hand-typed timing drift (compiler owns all numbers since 2026-07-10);
bare-canvas entrance flashes (furniture paints at t=0 in all 9 templates).

## Session notes

### 2026-07-13 · finding-creating-a-career-purpose-statement (first post-refactor run)
- [upstream] `tts --provider` flag rejected by CLI 0.7.56 (flag removed upstream;
  kokoro is the sole built-in engine) → dropped the flag. ~3 min. Skill Step 2
  command block needs the same edit.
- [observation] whisper transcript reads "I am honest enough" where the script
  says "Specific enough" (~24s) — no script-vs-transcript gate exists to catch
  TTS misreads; flagged for human QA listen. Full run report:
  `oversight-brief_first-post-refactor-run_2026-07-13.md`.

### 2026-07-12 · career-building_early-career-boost (seed)
- [env] `npx hyperframes tts` resolved the wrong Python; `kokoro_onnx` was missing
  on that interpreter → set `HYPERFRAMES_PYTHON` to the env that has it. ~15 min.

### 2026-07-13 · pipeline overhaul (no render)
- [defect] `compile_timeline.py --check` crashed (2-tuple unpack after the
  3-tuple insertions migration) → fixed line 248; tests 20/20. This is what made
  preflight print a traceback instead of "run --apply".
- [tooling] `hooks/pre-tool.sh` hard-blocked every session at 80 tool calls —
  a full build needs 150–300 → defaults raised to 500/350.
- [tooling] check_boundaries.py `attr()` regex matched `data-hf-id` when asked
  for `id` → anchored with a lookbehind; scene ids in findings are now correct.
