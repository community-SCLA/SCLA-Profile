#!/usr/bin/env bash
# batch-prepare.sh — build the per-run kit that every build subagent shares.
#
# Creates renders-hyperframes/_run/ holding:
#   BUILD-KIT.md   an exact copy of the compact tracked builder contract.
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
CONTRACT="$VP/contracts/builder.md"

PIN="$(grep -o 'hyperframes@[0-9.]*' "$DS/package.json" | head -1)"
[[ -n "$PIN" ]] || { echo "FATAL: no hyperframes pin in design-system/package.json" >&2; exit 1; }

FORCE_REBUILD=0
if [[ "${1:-}" == "--force" ]]; then
  # Preserve run.json: scope, approval and retry state must survive a scaffold
  # refresh and a new agent session.
  FORCE_REBUILD=1
  rm -f "$RUN/BUILD-KIT.md"
fi
mkdir -p "$RUN"

# A scaffold built at a different pin (or before a token/asset edit) is
# stale — rebuild rather than silently reusing it.
REBUILD="$FORCE_REBUILD"
if [[ -d "$RUN/scaffold" ]]; then
  DS_SIG="$PIN $(find "$DS/config/tokens.yml" "$DS/assets" -type f -newer "$RUN/scaffold" 2>/dev/null | wc -l)"
  if [[ "$(cat "$RUN/scaffold/.pin" 2>/dev/null)" != "$PIN" || "${DS_SIG#* }" != "0" ]]; then
    echo "== scaffold stale (pin or design-system changed) — rebuilding"
    REBUILD=1
  fi
else
  REBUILD=1
fi

# ---------------------------------------------------------------- scaffold
if [[ "$REBUILD" == "1" ]]; then
  echo "== scaffolding a workspace at $PIN (once for the whole batch)"
  NEXT="$RUN/scaffold-next-$$"
  OLD_CREATED="$(jq -r '.createdAt // empty' "$RUN/scaffold/meta.json" 2>/dev/null || true)"
  rm -rf "$NEXT"
  trap 'rm -rf "$NEXT" 2>/dev/null || true' EXIT
  ( cd "$RUN" && HYPERFRAMES_SKIP_SKILLS=1 npx --yes "$PIN" init "$(basename "$NEXT")" \
      --example=blank --non-interactive ) || {
    echo "FATAL: hyperframes init failed" >&2; exit 1; }

  # tokens.yml is what the GATES read (tokens.py prefers the workspace copy) AND
  # what the builder designs against — palette, type floors, pinned voice,
  # program display names. The fonts and brand SVGs are the only other design
  # inputs a freeform build consumes.
  cp "$DS/config/tokens.yml" "$NEXT/tokens.yml"
  rm -rf "$NEXT/assets"; cp -a "$DS/assets" "$NEXT/assets"
  mkdir -p "$NEXT/compositions"

  # init writes AGENTS.md and CLAUDE.md that route to the generic hyperframes
  # workflows this pipeline forbids (/produce-video: "never route SCLA lesson
  # videos into generic hyperframes workflow skills") and name `npm run check`
  # as the gate when the real gate is preflight.py. Nothing in the pipeline
  # reads either file: a cold build subagent is handed _run/BUILD-KIT.md by
  # path in its prompt, and anyone opening a workspace inherits
  # projects/video-production/CLAUDE.md from the parent tree. Delete rather
  # than correct — a workspace carries no agent instructions of its own.
  rm -f "$NEXT/AGENTS.md" "$NEXT/CLAUDE.md"

  # The temporary directory is an atomic-build detail, not project identity.
  # Normalize vendor metadata so every refresh is stable and cache-friendly.
  CREATED="${OLD_CREATED:-$(date -u +%Y-%m-%dT%H:%M:%S.000Z)}"
  jq --arg created "$CREATED" '.id="scaffold" | .name="scaffold" | .createdAt=$created' \
    "$NEXT/meta.json" > "$NEXT/meta.json.tmp" && mv "$NEXT/meta.json.tmp" "$NEXT/meta.json"
  jq '.name="scaffold"' "$NEXT/package.json" > "$NEXT/package.json.tmp" \
    && mv "$NEXT/package.json.tmp" "$NEXT/package.json"

  echo "$PIN" > "$NEXT/.pin"
  rm -rf "$RUN/scaffold"
  mv "$NEXT" "$RUN/scaffold"
  trap - EXIT
  echo "   scaffold ready ($(du -sh "$RUN/scaffold" | cut -f1)) — tokens + fonts + brand assets wired"
else
  echo "== scaffold already present — reusing (use --force to rebuild)"
fi

# ---------------------------------------------------------------- build kit
echo "== writing BUILD-KIT.md"
[[ -f "$CONTRACT" ]] || { echo "FATAL: missing builder contract: $CONTRACT" >&2; exit 1; }
cp "$CONTRACT" "$RUN/BUILD-KIT.md"

if grep -q 'BUILD-KIT:BEGIN\|BUILD-KIT:END' "$RUN/BUILD-KIT.md"; then
  echo "FATAL: extraction-marker residue in generated build kit" >&2
  exit 1
fi

WORDS="$(wc -w < "$RUN/BUILD-KIT.md")"
if (( WORDS > 3000 )); then
  echo "FATAL: builder route budget exceeded ($WORDS > 3000 words)" >&2
  exit 1
fi
echo "   BUILD-KIT.md: $WORDS words"
echo
echo "Run kit ready at renders-hyperframes/_run/  (pin $PIN)"
