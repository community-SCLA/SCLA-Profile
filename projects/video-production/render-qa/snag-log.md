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

Resolved structurally (no longer live, kept for pattern-matching): zero-gap
padding non-convergence (compile_timeline keys shifts by word index since
2026-07-13); hand-typed timing drift (compiler owns all numbers since 2026-07-10);
bare-canvas entrance flashes (furniture paints at t=0 in all 9 templates).

## Session notes

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
