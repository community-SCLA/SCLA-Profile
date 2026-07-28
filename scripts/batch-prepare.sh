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
           Each carries its verbatim span of the script as data-narration
           (HTML-escape inner double quotes as &quot;; split only at sentence
           ends) and placeholder timing numbers the compiler will overwrite:

        <div class="clip" data-composition-src="compositions/scla-title.html"
             data-start="0" data-duration="1" data-track-index="1"
             data-narration="The first sentence of the script, verbatim."
             data-vars='{"title":"...","kicker":"..."}'></div>

           Where a scene has reveals, add cue anchors quoting phrases verbatim
           from the transcript:
             data-cue-anchors='{"chipCues":["exact phrase","another phrase"]}'
           Available templates: see compositions/ (scla-title, scla-chips,
           scla-steps, scla-stat, scla-quote, scla-points, scla-statement,
           scla-loop, scla-morph, scla-condition, scla-career-map, scla-outro).
      -->

      <div id="hf-rail-track"></div>
      <div id="hf-rail-fill"></div>

      <audio src="assets/voice/narration.wav" data-audio-track></audio>
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
cp -a _run/scaffold <stem>
cd <stem>
```

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
  # from the SKILL rather than restated, so they cannot drift.
  awk '/^\*\*Assemble `index.html` FIRST\*\*/,/^\*\*Stop here\. No render in this phase\.\*\*/' "$SKILL" \
    | sed '1,/^- \*\*Add the host-root progress rail/{ /^\*\*Assemble `index.html` FIRST\*\*/d }' \
    || true

  cat <<'FTR'

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
