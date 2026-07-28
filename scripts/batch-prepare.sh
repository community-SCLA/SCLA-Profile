#!/usr/bin/env bash
# batch-prepare.sh — build the per-run kit that every build subagent shares.
#
# Creates renders-hyperframes/_run/ holding:
#   BUILD-KIT.md   the hot path: command sequence + landmines + scaffold usage,
#                  extracted VERBATIM from the owning docs (never summarised —
#                  a lossy paraphrase of a design contract is how brand drift
#                  starts). It navigates frame.md; it does not replace it.
#   scaffold/      a workspace already `hyperframes init`'d at the pinned
#                  version with compositions/, assets/, the host-root progress
#                  rail and the <audio> host in place, plus one commented slot
#                  example. Builds `cp -a` this instead of running init 30 times.
#
# Why this exists: each build subagent had been cold-reading frame.md, the
# pattern exemplar's full index.html and all 12 composition templates —
# ~25-45k tokens of re-derivation per video. The scaffold removes the exemplar
# and template reads (real working markup beats reading an example), leaving
# frame.md, which stays mandatory because it IS the contract.
#
# _run/ is gitignored and regenerated every run, so unlike a hand-maintained
# doc it cannot drift out of sync with its sources.
#
# Usage:  bash scripts/batch-prepare.sh [--force]
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VP="$REPO/projects/video-production"
DS="$VP/design-system"
RUN="$VP/renders-hyperframes/_run"
SKILL="$REPO/.claude/skills/render-lessons/SKILL.md"

PIN="$(grep -o 'hyperframes@[0-9.]*' "$DS/package.json" | head -1)"
[[ -n "$PIN" ]] || { echo "FATAL: no hyperframes pin in design-system/package.json" >&2; exit 1; }

[[ "${1:-}" == "--force" ]] && rm -rf "$RUN"
mkdir -p "$RUN"

# A scaffold built at a different pin (or before a design-system edit) is
# stale — rebuild rather than silently reusing it.
if [[ -d "$RUN/scaffold" ]]; then
  DS_SIG="$PIN $(find "$DS/compositions" "$DS/frame.md" -type f -newer "$RUN/scaffold" 2>/dev/null | wc -l)"
  if [[ "$(cat "$RUN/scaffold/.pin" 2>/dev/null)" != "$PIN" || "${DS_SIG#* }" != "0" ]]; then
    echo "== scaffold stale (pin or design-system changed) — rebuilding"
    rm -rf "$RUN/scaffold"
  fi
fi

# ---------------------------------------------------------------- scaffold
if [[ ! -d "$RUN/scaffold" ]]; then
  echo "== scaffolding a workspace at $PIN (once for the whole batch)"
  ( cd "$RUN" && HYPERFRAMES_SKIP_SKILLS=1 npx --yes "$PIN" init scaffold \
      --example=blank --non-interactive ) || {
    echo "FATAL: hyperframes init failed" >&2; exit 1; }

  cp "$DS/frame.md" "$RUN/scaffold/frame.md"
  rm -rf "$RUN/scaffold/compositions"; cp -a "$DS/compositions" "$RUN/scaffold/compositions"
  rm -rf "$RUN/scaffold/assets";       cp -a "$DS/assets"       "$RUN/scaffold/assets"

  # init writes a CLAUDE.md routing to skills this repo deleted.
  printf '# Build workspace. Sequence + commands: _run/BUILD-KIT.md. Design contract: frame.md\n' \
    > "$RUN/scaffold/CLAUDE.md"

  # The blank example has no rail and no <audio> host, and every build needs
  # both. Wiring them here (per frame.md "Host-root progress rail") means no
  # build can forget them, and no subagent has to read another build to copy
  # the pattern. Colours are frame.md's, not restated anywhere else.
  cat > "$RUN/scaffold/index.html" <<'HTML'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }
      body { font-family: "Inter", sans-serif; }
      code, pre, .monospace { font-family: "JetBrains Mono", monospace; }

      /* Host-root progress rail — spans the whole runtime, not scene motion.
         Not a scene clip, so the deterministic gates ignore it. */
      #hf-rail-track { position: absolute; left: 0; bottom: 48px; width: 1920px; height: 4px; background: #cccedf; opacity: .28; }
      #hf-rail-fill  { position: absolute; left: 0; bottom: 48px; width: 1920px; height: 4px; background: #eaab2d;
                       transform-origin: left center; transform: scaleX(0); }
    </style>
  </head>
  <body>
    <!-- data-duration is COMPILER-OWNED. Leave the placeholder; never type a real number. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="10"
         data-width="1920" data-height="1080">

      <!-- SCENE SLOTS GO HERE — one per beat of the refined script.
           Copy this shape EXACTLY; every attribute below is load-bearing and
           each was a real gate failure caught on the 2026-07-28 pilot build:

        <div class="clip" id="scene-01" data-composition-id="scene-01"
             data-composition-src="compositions/scla-title.html"
             data-start="0" data-duration="1" data-track-index="1"
             data-narration="The first sentence of the script, verbatim."
             data-variable-values='{"eyebrow":"...","title":"...","sceneIndex":"01 / TITLE","theme":"summit","sceneDuration":""}'></div>

           - `data-variable-values` is the ONLY attribute compile_timeline.py
             reads. Naming it `data-vars` silently yields zero cue resolution.
           - `data-composition-id` is a hard lint error when missing.
           - `sceneDuration` must be PRE-DECLARED (even empty) — the compiler
             updates existing keys, it never adds new ones.
           - timing numbers here are placeholders; the compiler owns them.

           Where a scene has reveals, add cue anchors quoting phrases verbatim
           from the transcript:
             data-cue-anchors='{"chipCues":["exact phrase","another phrase"]}'
           Available templates: see compositions/ (scla-title, scla-chips,
           scla-steps, scla-stat, scla-quote, scla-points, scla-statement,
           scla-loop, scla-morph, scla-condition, scla-career-map, scla-outro).
      -->

      <div id="hf-rail-track"></div>
      <div id="hf-rail-fill"></div>

      <!-- id + data-start are REQUIRED. Without them lint warns "audio will be
           SILENT in renders" — and the render really is silent. -->
      <audio id="narration-audio" src="assets/voice/narration.wav" data-audio-track data-start="0"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });

      // Rail span is read from the compiler-owned data-duration — never hand-typed.
      const total = parseFloat(document.getElementById("root").dataset.duration) || 0;
      tl.fromTo("#hf-rail-fill", { scaleX: 0 }, { scaleX: 1, duration: total, ease: "none" }, 0);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
HTML

  echo "$PIN" > "$RUN/scaffold/.pin"
  echo "   scaffold ready ($(du -sh "$RUN/scaffold" | cut -f1)) — rail + audio host wired"
else
  echo "== scaffold already present — reusing (use --force to rebuild)"
fi

# ---------------------------------------------------------------- build kit
echo "== writing BUILD-KIT.md"
{
  cat <<'HDR'
# BUILD-KIT — read this, then frame.md, then your script. Nothing else.

Generated per run by `scripts/batch-prepare.sh`. Never edit by hand; never
commit. If this contradicts `frame.md` or the render-lessons SKILL, THEY WIN —
report the contradiction rather than following this file.

## Your job

Turn ONE refined script into a gate-clean HyperFrames workspace. You do not
render. You do not publish. You stop when compile, preflight and check are all
green, and you report five fields.

## Start from the scaffold — do NOT run `hyperframes init`

```bash
cd projects/video-production/renders-hyperframes
[ ! -e <stem> ] || { echo "workspace <stem> already exists — STOP, report, do not build"; exit 1; }
cp -a _run/scaffold <stem>
cd <stem>
```

If the workspace already exists, STOP and report it — `cp -a` onto an existing
directory NESTS the scaffold inside it and every gate then reads stale files.

The scaffold already has `compositions/`, `assets/`, `frame.md`, the pinned
toolchain, the host-root progress rail and the `<audio>` host. This replaces
reading a pattern-exemplar `index.html` — you are editing real working markup
instead of imitating an example.

## What to read, in order

1. **This file.**
2. **`frame.md`** (in your workspace) — the design contract, and it is
   normative. Mandatory sections: *the animacy rules*, *the pacing rules*,
   *illustration over text*, *type rules*, *scene templates*, *style packages*
   for your assigned theme, and *host-root progress rail*.
3. **Your refined script.** Verbatim source for every `data-narration`.

Do not read other builds' `index.html`, the demo reel, or other skills.

## Assemble index.html FIRST

One scene slot per beat, from the design-system templates. `<audio>` at the
host root. Then:

HDR

  # The authoring landmines and the command sequence are extracted verbatim
  # from the SKILL rather than restated, so they cannot drift. Marker-bounded:
  # the old regex anchors matched mid-paragraph text and silently dumped the
  # whole SKILL (orchestrator phases included) into every builder's context.
  KIT_BODY="$(awk '/<!-- BUILD-KIT:BEGIN/,/<!-- BUILD-KIT:END/' "$SKILL" | sed '1d;$d')"
  [[ -n "$KIT_BODY" ]] || { echo "FATAL: BUILD-KIT markers missing from $SKILL" >&2; exit 1; }
  if grep -qE 'Phase (SHIP|AUTO-BATCH)|batch-ship' <<<"$KIT_BODY"; then
    echo "FATAL: orchestrator content leaked between BUILD-KIT markers in $SKILL" >&2; exit 1
  fi
  printf '%s\n' "$KIT_BODY"

  cat <<'FTR'

## RULES THAT NO OTHER DOC WILL TEACH YOU

Discovered by real pilot builds that passed every static check and still
produced broken videos. None are optional.

### 1. Clone shared templates — run `instance_templates.py` BEFORE compiling

If two scenes point at the same `compositions/<name>.html`, **every scene that
shares a template renders completely blank** — background and footer only, no
heading, no content. On one pilot that was 18 of 21 scenes. The only scenes
that survived were the three using a template no other scene used.

So the build loop is FIVE commands, not four — the clone step comes first:

```bash
python3 ../../render-qa/instance_templates.py .          # clone shared templates -> per-scene files
../../../../scripts/with-secrets.sh python3 ../../render-qa/synth_narration.py .
python3 ../../render-qa/compile_timeline.py . --apply
python3 ../../render-qa/preflight.py .
npm run check
```

Re-run `instance_templates.py` any time you add or repoint a scene.

### 2. Every slot is authored copy or an explicit "" — nothing in between

Each template declares its variables in a JSON schema block at the top of
`compositions/<name>.html`. Slot defaults are `[[slot-name]]` placeholders: a
slot you leave out of `data-variable-values` renders its placeholder ON
SCREEN, and `preflight.py` (`check_slots.py`) fails the build for it — as it
also fails any slot whose value still IS placeholder text (`[[...]]`, `...`,
`TODO`).

Before authoring a scene, read the schema block at the top of its template
(the first ~15 lines — not the whole file) and enumerate its slots. Every
content slot gets either copy authored from YOUR SCRIPT, or `""` to hide it.
`sceneDuration`, every `*Cues` slot, and the title card's `meta` are
compiler-owned: pre-declare them (empty or placeholder value) and never type
their content yourself.

### 3. On-screen copy must trace to the narration

Headings, labels and points may compress or excerpt the scene's own narration
— they must never introduce facts, counts, or sequence claims the narration
does not say ("two more ways", "step 3 of 5", a stat). When unsure, use the
narration's own words. Never reuse wording from THIS document or from any
template's schema block: those are instructions to you, not lesson content.

### 4. No dead air — an event at least every ~3 seconds

After a scene's entrance settles (~1.2s), something visible must keep
happening on what the narration is saying: the next cued item, a `subBeats`
live line, an illustration beat. `preflight.py` FAILS any event gap over 4.0s
and warns over 3.0s. If the narration for a scene has a long span with
nothing to cue, split the scene at a sentence end or add `subBeats` — never
stretch a heading over silence.

### 5. Enumerated set spread across the lesson -> `scla-condition`, NOT `scla-steps`

`scla-steps` renders nodes `1..N` where N = the count of non-empty step slots,
and activates them in sequence **within one scene**. It has no notion of "this
scene is step 3 of 4." So if you give one steps scene a single step, it renders
a lone node numbered "1" on an empty four-node rail — even when the scene is
labelled STEP TWO. The pilot did this four times.

Choose by how the narration delivers the set:

- **All items spoken together, one passage** -> ONE `scla-steps` scene with
  every step slot filled and one `stepCues` entry per step.
- **Items introduced one at a time, separated by other scenes** ->
  `scla-condition` per item (number badge + "N of M" progress dots), which is
  exactly what frame.md prescribes: *"Split an enumerated set into one of these
  per item, not a timed 5-row list."*

Same rule for `scla-loop` (it shares the steps contract).

## Report exactly these five fields, no prose

```
workspace: <path>
scenes:    <n>
theme:     <summit|horizon|cadence>
gates:     synth=<exit> compile=<exit> preflight=<exit> check=<exit>
status:    <one line>
```

## Hard rules

- **Never type a timing number.** The compiler owns every number.
- **Never fabricate SCLA content.** Work only from the refined script.
- **No FERPA/PII** in any prompt sent to an AI tool.
- Never call `synth_narration.py` bare — only via `scripts/with-secrets.sh`
  (the ambient `HEYGEN_API_KEY` is stale and returns 403).
- Do **not** run `npm run render`. The orchestrator ships.
FTR
} > "$RUN/BUILD-KIT.md"

WORDS="$(wc -w < "$RUN/BUILD-KIT.md")"
echo "   BUILD-KIT.md: $WORDS words"
echo
echo "Run kit ready at renders-hyperframes/_run/  (pin $PIN)"
