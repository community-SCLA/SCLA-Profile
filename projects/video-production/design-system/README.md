# SCLA video design system

The brand-owned illustrated-video system: twelve reusable scene templates, one token
file, a pinned narration voice, and a demo reel that renders all twelve with real
lesson content.

**Agents: read `AGENTS.md`.** This is the human door.

## The one thing to understand

There are two spec files and they are not interchangeable:

| | |
|---|---|
| `config/tokens.yml` | **The numbers.** Colors, type scale, minimum text sizes, spacing, the pinned voice, the program display names. `render-qa/src/tokens.py` parses this and the gates grade against it. Change a number here and a gate's verdict changes. |
| `docs/design-contract.md` | **The prose.** Animacy rules, pacing, the variety contract, the template table. No code reads it. |

They were one 709-line file called `frame.md` until 2026-07-29. Splitting them was the
point: a human document that is also machine load-bearing gets edited by humans and
silently breaks gates — and on more than one occasion its prose *outranked* the owner,
because the pipeline correctly obeyed the spec and violated the instruction.

If a sentence in the contract disagrees with `tokens.yml`, `tokens.yml` wins and the
sentence is a bug.

## Working here

`npm run check` after **any** composition edit — it runs the framework's own lint plus
the repo's text, layout and motion gates over the demo reel, so a shared template
defect is caught once, here, instead of once per video that later uses it.

`npm run dev` is a long-running server. Background it.

## Why this folder isn't shaped like the others

HyperFrames dictates the layout — see `docs/README.md`.
