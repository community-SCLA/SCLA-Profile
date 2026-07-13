# render-qa/ — the deterministic toolchain for illustrated lesson videos

Built 2026-07-10 to end the class of defects that dominated the first at-scale
builds: hand-typed scene boundaries and cue times reconciled against the
narration *after* the fact (26 boundary violations, mid-word cuts, a backfired
transcript "repair", emergency silence padding, 14 cue-phrase mismatches).
The inversion: **authors declare anchors (phrases from the transcript);
these tools compute every number.** Used by `/produce-video` Steps 5–6 and
`/adversarial-qa`; the authoring contract lives in `design-system/frame.md`.

| Tool | When | What it does |
| --- | --- | --- |
| `compile_timeline.py <ws> --apply` | after TTS + transcribe + assemble | Resolves `data-anchor-end` / `data-cue-anchors` phrases in the transcript; inserts boundary silence into `narration.wav` (0.6s air + 0.15s lead, 0.9s after questions) and shifts `transcript.json`; writes every `data-start`/`data-duration`, numeric cue, `sceneDuration`, audio + root duration. Idempotent. `--check` = drift detector (exit 1 on any). |
| `preflight.py <ws>` | before every render | One-command pre-render gate: compiler drift check + `check_boundaries.py` (independent pacing rules) + clip coverage (tile 0→root, no gaps/overlaps) + one-theme-per-video. Exit 0 = cleared to render. |
| `verify_render.py <ws> [mp4]` | after every render | Container truth (streams/duration/resolution) + presence v2 (blank frames by stddev **and** content pixels, ≥5s stagnation tripwire, audio-vs-video) + writes the shared QA frame evidence: `<ws>/qa/frames/` — 3 full-res stills per scene for the gauntlet lanes and the human gate. Exit 0 before anyone reviews the cut. |
| `hfp_common.py` | library | Transcript loading, normalized duplicate-safe phrase matching (forward pointer, positional), scene-slot parse/rewrite, apostrophe-safe attribute JSON. |
| `tests/run_tests.py` | after editing any tool | 20 adversarial fixtures: duplicate words, missing/unresolvable anchors, cue-count mismatches, unclaimed transcript tails, question air, padding idempotency, `data-hf-id` parsing trap, apostrophe injection. Must print `20 passed, 0 failed`. |

## The authoring contract (normative copy: `design-system/frame.md`)

```html
<div … data-anchor-end="hiding somewhere."
      data-cue-anchors='{"chipCues":["right job","right major","right city","right path"]}'
      data-start="0" data-duration="1" …>
```

- `data-anchor-end` — the scene's last spoken phrase, verbatim transcript
  words (punctuation/case ignored). Scenes are matched **in order** with a
  forward pointer, so duplicate phrases across scenes are safe.
- `data-cue-anchors` — one transcript phrase per cue item, in spoken order.
  On-screen labels may paraphrase; anchors may not.
- Numbers in `data-start`/`data-duration`/cue variables are compiler-owned.
  Hand-editing them is a defect: re-run `--apply`.

## Failure philosophy

Every unresolvable anchor, unclaimed transcript tail, or count mismatch is a
**fatal, named error before render time** — the same defects used to surface
as QA findings on a finished MP4 (or not at all). If `--apply` fails, nothing
is written to `index.html` (already-inserted audio padding is kept — it is
valid regardless).

Backups: the first padding run copies originals to
`assets/voice/narration.pre-pad.wav` / `transcript.pre-pad.json`.
