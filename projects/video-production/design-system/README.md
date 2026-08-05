# SCLA video design system

The brand token & asset store for SCLA lesson videos: one token file, the
vendored brand typeface, the logo SVGs, and the pinned render-CLI version.
The twelve scene templates and the demo reel retired to `_archive/` on
2026-08-05 with the template lane (`decisions/log.md`) — nothing renderable
lives here anymore; every video is authored freeform in its own workspace.

**Agents: read `AGENTS.md`.** This is the human door.

## The one thing to understand

`config/tokens.yml` is **the numbers**: colors, type scale, minimum text
sizes, spacing bands, the pinned voice, the program display names, the retired
names. `render-qa/src/tokens.py` parses it and the gates grade against it —
change a number here and a gate's verdict changes.

The gated *rules* (each naming its checker) live in
`.claude/rules/video-production.md`. A build's own design intent lives in that
build's `design.md`. There is deliberately no prose spec in this folder: a
human document that is also machine load-bearing gets edited by humans and
silently breaks gates — and on more than one occasion the old prose spec
*outranked* the owner, because the pipeline correctly obeyed the spec and
violated the instruction.

## Working here

Treat any `tokens.yml` edit as a gate edit: run `bash scripts/lint-refs.sh`
(it runs the render-qa suite) after. Workspaces grade against their own copied
`tokens.yml`; preflight's freshness section catches drift.

`package.json` exists to carry the pinned `hyperframes` version —
`check_layout.py` reads it and every render runs at it. Bump deliberately,
never drop.

## Why this folder isn't shaped like the others

HyperFrames dictated the layout when this was a renderable project — see
`docs/README.md` for what that cost and why the shell remains.
