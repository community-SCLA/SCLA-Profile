#!/usr/bin/env bash
# batch-prepare.sh — build the per-run kit that every build subagent shares.
#
# Creates renders-hyperframes/_run/ holding:
#   BUILD-KIT.md   the hot path: command sequence + landmines + scaffold usage,
#                  extracted VERBATIM from the owning docs (never summarised).
#   scaffold/      a workspace already `hyperframes init`'d at the pinned
#                  version with tokens.yml, the vendored Proxima set and the
#                  brand SVGs in place. Builds `cp -a` this instead of a
#                  network install per video.
#
# Why this exists: each build subagent had been cold-running `hyperframes init`
# (a network install) and re-copying the same token/font/brand assets per
# video. The scaffold does both once per run. The template lane's compositions
# and its authoring-menu doc retired 2026-08-05 (decisions/log.md) — a freeform
# build authors its own HTML, so the scaffold ships assets, not templates.
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

# A scaffold built at a different pin (or before a token/asset edit) is
# stale — rebuild rather than silently reusing it.
if [[ -d "$RUN/scaffold" ]]; then
  DS_SIG="$PIN $(find "$DS/config/tokens.yml" "$DS/assets" -type f -newer "$RUN/scaffold" 2>/dev/null | wc -l)"
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

  # tokens.yml is what the GATES read (tokens.py prefers the workspace copy) AND
  # what the builder designs against — palette, type floors, pinned voice,
  # program display names. The fonts and brand SVGs are the only other design
  # inputs a freeform build consumes.
  cp "$DS/config/tokens.yml" "$RUN/scaffold/tokens.yml"
  rm -rf "$RUN/scaffold/assets"; cp -a "$DS/assets" "$RUN/scaffold/assets"
  mkdir -p "$RUN/scaffold/compositions"

  # init writes AGENTS.md and CLAUDE.md that route to the generic hyperframes
  # workflows this pipeline forbids (/produce-video: "never route SCLA lesson
  # videos into generic hyperframes workflow skills") and name `npm run check`
  # as the gate when the real gate is preflight.py. Nothing in the pipeline
  # reads either file: a cold build subagent is handed _run/BUILD-KIT.md by
  # path in its prompt, and anyone opening a workspace inherits
  # projects/video-production/CLAUDE.md from the parent tree. Delete rather
  # than correct — a workspace carries no agent instructions of its own.
  rm -f "$RUN/scaffold/AGENTS.md" "$RUN/scaffold/CLAUDE.md"

  echo "$PIN" > "$RUN/scaffold/.pin"
  echo "   scaffold ready ($(du -sh "$RUN/scaffold" | cut -f1)) — tokens + fonts + brand assets wired"
else
  echo "== scaffold already present — reusing (use --force to rebuild)"
fi

# ---------------------------------------------------------------- build kit
echo "== writing BUILD-KIT.md"
{
  cat <<'HDR'
# BUILD-KIT — read this, then your script. Nothing else.

Generated per run by `scripts/batch-prepare.sh`. Never edit by hand; never
commit. If this contradicts `.claude/rules/video-production.md` or the
render-lessons SKILL, THEY WIN — report the contradiction rather than
following this file. Where a gate and any prose disagree, the gate is right.

## Your job

Turn ONE refined script into a gate-clean HyperFrames workspace. You author
the HTML yourself — there are no templates and no compiler (the template lane
retired 2026-08-05). You do not render. You do not publish. You stop when the
gates are green, and you report five fields.

## Start from the scaffold — do NOT run `hyperframes init`

The workspace is named `<title>_<program>` — the script's name with any date
suffix stripped. No date. `render-qa/src/stem.py` owns that; never hand-slice a
suffix. (Dates live on the delivered MP4 only.)

**`build-claim.sh` starts every build — there is no other way in.** It takes
the atomic `mkdir` lock (exactly one of N concurrent subagents wins), arms the
write fence, opens the build journal, and regenerates `PIPELINE-STATUS.md`:

```bash
bash scripts/build-claim.sh <base> <program-slug>   # exits non-zero if claimed
cd projects/video-production/renders-hyperframes/<base>
cp -a ../_run/scaffold/. .     # note the /. — copies CONTENTS into the claimed dir
```

The trailing `/.` is load-bearing: without it the scaffold nests *inside* your
workspace and every gate then reads stale files.

If the claim fails, STOP and report it. Do not delete the other directory, do
not pick a different name, do not build into it.

The scaffold has `tokens.yml` (palette, type floors, pinned voice, program
display names — the gates read the workspace copy), the vendored Proxima
woff2 set and the brand SVGs under `assets/`, and the pinned toolchain.

## What to read, in order

1. **This file.**
2. **`tokens.yml`** (in your workspace) — every normative number and name.
3. **Your refined script.** Verbatim source for every beat's narration.

Do not read other builds' `index.html`, archived templates, or other skills.

HDR

  # The authoring sequence and landmines are extracted verbatim from the SKILL
  # rather than restated, so they cannot drift. Marker-bounded: the old regex
  # anchors matched mid-paragraph text and silently dumped the whole SKILL
  # (orchestrator phases included) into every builder's context.
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

### 1. On-screen copy must trace to the narration

Headings, labels and points may compress or excerpt the beat's own narration
— they must never introduce facts, counts, or sequence claims the narration
does not say ("two more ways", "step 3 of 5", a stat). When unsure, use the
narration's own words. Never reuse wording from THIS document: these are
instructions to you, not lesson content.

### 2. Title card is DERIVED — never invent it

The eyebrow is the program display name from tokens.yml's `programs:` map;
the title is the stem's title segment, hyphens to spaces — never the opening
narration sentence, never a paraphrase. Both must appear in on-frame MARKUP
text (chrome built in JS is invisible to every gate). `preflight.py` fails
both.

### 3. Headings stand alone — never a fragment completed by later copy

A heading must read as a complete phrase by itself ("Where people look for
the answer"), never a fragment that later items finish ("The right" + "The
right job / The right major" — a real pilot defect that read as truncated
text on screen). If a beat would show a title plus a large empty area at its
midpoint, give it a sub-line or tighten the beat.

### 4. The freeform contract the gates read

On-frame copy lives in **markup, never JS strings**; headings carry
`data-role="heading"` (or are `<h1>`–`<h3>`); declared lists that are not
`<ul>`/`<ol>` carry `data-role="list"`, comparisons `data-role="compare"`.
Deliberate exceptions are declared where they live (`/* motion-allow: … */`,
`/* brand-allow: … */`, `/* text-floor-exempt: … */`). Colors are
`tokens.yml colors:` at any alpha; every `font-family` leads with the brand
face; body text ≥ 40px.

## Report exactly these five fields, no prose

```
workspace: <path>
beats:     <n>
concept:   <the design.md concept angle, one line>
gates:     static=<exit> synth=<exit> pace=<exit> preflight=<exit> check=<exit>
status:    <one line>
```

## Hard rules

- **Never hand-tune a timing number.** timing.json is COMPUTED from
  audio_meta.json durations.
- **Never fabricate SCLA content.** Work only from the refined script.
- **No FERPA/PII** in any prompt sent to an AI tool.
- Never synthesize bare — only via `scripts/with-secrets.sh`
  (the ambient `HEYGEN_API_KEY` is stale and returns 403).
- Do **not** run `npm run render`. The orchestrator ships.
FTR
} > "$RUN/BUILD-KIT.md"

WORDS="$(wc -w < "$RUN/BUILD-KIT.md")"
echo "   BUILD-KIT.md: $WORDS words"
echo
echo "Run kit ready at renders-hyperframes/_run/  (pin $PIN)"
