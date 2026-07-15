# render-qa/ — the deterministic toolchain for illustrated lesson videos

Built 2026-07-10 to end the class of defects that dominated the first at-scale
builds: hand-typed scene boundaries and cue times reconciled against the
narration *after* the fact (26 boundary violations, mid-word cuts, a backfired
transcript "repair", emergency silence padding, 14 cue-phrase mismatches).
The inversion: **authors declare text (per-scene narration spans + cue
phrases); these tools compute every number.** Used by `/render-lessons`
(BUILD gates + SHIP verify) and `/adversarial-qa`; the authoring contract
lives in `design-system/frame.md`.

**2026-07-14 — per-scene synthesis replaced the single-take + inserted-silence
flow.** The old flow synthesized the whole script as one Kokoro take (natural
sentence gaps ~0.03s) and spliced digital-zero silence at Whisper-estimated
boundaries; Whisper word timestamps are ±30–100ms (both directions — they also
drift into silence), so splices measurably landed inside voiced audio, cutting
words in half, and re-anchoring after `--apply` left orphaned silences in the
wav. `synth_narration.py` deletes the whole failure class: boundaries are real
silence, known sample-exactly. The legacy path in `compile_timeline.py`
remains only for pre-manifest workspaces.

| Tool | When | What it does |
| --- | --- | --- |
| `synth_narration.py <ws>` | after assembling `index.html`, before transcribe | Per-scene TTS: verifies every scene's `data-narration` against the approved script (exact token match, BEFORE any TTS), synthesizes one Kokoro clip per scene (cached by text hash — edits re-synthesize only changed scenes), trims clip edge silence, concatenates with REAL boundary gaps (0.3s air + 0.15s lead; 0.45s air after questions), writes `narration.wav` + the sample-exact boundary manifest `assets/voice/scene-times.json`, and deletes any stale `transcript.json` so a forgotten re-transcribe fails loudly. |
| `compile_timeline.py <ws> --apply` | after synth + transcribe | Manifest mode (default for new builds): scene boundaries come from `scene-times.json`; cue phrases in `data-cue-anchors` resolve against the whisper transcript inside each scene's manifest window; writes every `data-start`/`data-duration`, numeric cue, `sceneDuration`, audio + root duration. No silence is ever inserted. Legacy mode (no manifest): `data-anchor-end` anchoring + boundary-silence insertion, kept for old workspaces. Idempotent. `--check` = drift detector (exit 1 on any). |
| `preflight.py <ws> [--script <path>]` | before every render | One-command pre-render gate: compiler drift check + `check_boundaries.py` (independent pacing rules; manifest = ground truth for spoken ends and question flags — whisper word ends drift into silence) + clip coverage (tile 0→root, no gaps/overlaps) + one-theme-per-video + script fidelity (approved `lesson-scripts/` `.txt` vs the whisper transcript, word-level diff — threshold-based because whisper small.en mishears ~1/360: isolated misses PASS with warnings, mismatch rate >2% or ≥4 consecutive missed words FAILs; spelled numbers fold to digits on both sides; script auto-located from the workspace stem or passed via `--script`; missing script = WARN + skip). Exit 0 = cleared to render. |
| `verify_render.py <ws> [mp4]` | after every render | Container truth (streams/duration/resolution) + presence v2 (blank frames by stddev **and** content pixels, ≥5s stagnation tripwire, audio-vs-video) + writes the shared QA frame evidence: `<ws>/qa/frames/` — 3 full-res stills per scene for the gauntlet lanes and the human gate. Exit 0 before anyone reviews the cut. |
| `hfp_common.py` | library | Transcript loading, normalized duplicate-safe phrase matching (forward pointer, positional), scene-slot parse/rewrite (incl. `data-narration`), apostrophe-safe attribute JSON. |
| `tests/run_tests.py` | after editing any tool | 36 adversarial fixtures: duplicate words, missing/unresolvable anchors, cue-count mismatches, unclaimed transcript tails, question air, legacy padding idempotency, `data-hf-id` parsing trap, apostrophe injection, per-scene synth (clip cache, trim, real-silence gaps, stale-artifact hygiene), manifest-mode compile (boundaries, cue windows, idempotency, count mismatch). Must print `36 passed, 0 failed`. |
| `tests/test_script_match.py` | after editing `preflight.py` | Synthetic fixtures for the script-fidelity gate: clean match, noise-floor mishear (passes with warning), dropped/misread sentence (fails), >2% mismatch rate (fails), dash-compound tokenization, stem-based script location, missing script warn+skip. |

## The authoring contract (normative copy: `design-system/frame.md`)

```html
<div … data-narration="Ask where you are hiding somewhere. …"
      data-cue-anchors='{"chipCues":["right job","right major","right city","right path"]}'
      data-start="0" data-duration="1" …>
```

- `data-narration` — the scene's verbatim span of the refined script (split at
  sentence ends; HTML-escape inner double quotes as `&quot;`). The
  concatenation across scenes must equal the script — `synth_narration.py`
  enforces this exactly, before any TTS.
- `data-cue-anchors` — one transcript phrase per cue item, in spoken order.
  On-screen labels may paraphrase; anchors may not. (`subCues` pairs with the
  pipe-separated `subBeats` variable; other cue lists pair comma-separated.)
- `data-anchor-end` — legacy only (pre-manifest workspaces). Never author it
  on a new build.
- Numbers in `data-start`/`data-duration`/cue variables are compiler-owned.
  Hand-editing them is a defect: re-run `--apply`.

## Failure philosophy

Every unresolvable cue phrase, script/narration mismatch, or count mismatch is
a **fatal, named error before render time** — the same defects used to surface
as QA findings on a finished MP4 (or not at all). If `--apply` fails, nothing
is written to `index.html`. If a scene's narration text changes,
`synth_narration.py` re-synthesizes that clip only, and the deleted stale
transcript forces the re-transcribe step.
