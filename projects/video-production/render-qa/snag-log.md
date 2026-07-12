# Snag log — render-session retros + gauntlet retirement ledger

The self-improvement loop for SCLA video production. Every render session appends
a retro here; `/produce-video` reads it at preflight to avoid known snags; each
recurring snag is tracked toward a structural fix that can retire a gauntlet lane.
Design: `snag-loop-design.md`. Sibling to `BUILD-LOG.md`.

**How to use it**
- On every render session, append a `## <date> · <stem>` block under *Session
  entries*. Tag each snag `[env] [tooling] [authoring] [upstream] [defect]`, give
  its resolution + rough time cost, and add a `Caught-by:` line for any gauntlet
  lane that FAILed (with the lane's `defect-class`).
- Promote any snag that recurs into the *Retirement ledger*. For a class with a
  structural fix in place, keep a per-template clean-render tally (9 cells). A
  recurrence resets that template's cell to 0.
- A lane is retirement-eligible only when its defect class shows **≥5 clean
  renders on every one of the 9 templates** since its fix landed. Nominate here;
  the human records the actual retirement in `decisions/log.md`.

Templates (tally order): title · chips · statement · quote · points · steps ·
compare · career-map · numeral.

---

## Session entries

## 2026-07-12 · career-building_early-career-boost (seed)
Caught-by: —
- [env] `npx hyperframes tts` resolved the wrong Python; `kokoro_onnx` was missing
  on that interpreter → set `HYPERFRAMES_PYTHON` to the env that has it. ~15 min.
  (findPython() respects `HYPERFRAMES_PYTHON`.)

_First real entry seeds the format; extend it, don't rewrite it._

---

## Retirement ledger

| Snag class | Occurrences | Structural fix | Retires | Per-template clean tally (9) | Status |
| --- | --- | --- | --- | --- | --- |
| TTS wrong python path | 1 | pin `HYPERFRAMES_PYTHON` in produce-video preflight | — (env, not a lane) | n/a | open |

_No lane is retirement-eligible yet. Add a row the first time a `[defect]` snag
recurs; start its per-template tally once a structural fix is in place._
