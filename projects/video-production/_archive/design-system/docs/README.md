# Why this folder breaks the repo's project convention

Every other project here uses `README.md` / `AGENTS.md` / `run.sh` / `src/` / `config/`
/ `docs/` / `logs/`. This one keeps `index.html`, `compositions/`, `assets/`,
`hyperframes.json`, `meta.json` and `package.json` at its root instead.

That is not drift. HyperFrames requires it.

## What HyperFrames imposes

| Path | Why it can't move |
|---|---|
| `index.html` | The host composition. `hyperframes render/preview/lint` resolve it at the project root. |
| `compositions/` | Sub-compositions are referenced by **relative** `data-composition-src` (`compositions/scla-title.html`) from the host and from every workspace copy. Moving the folder rewrites every reference in every template and every built workspace. |
| `assets/` | Fonts and brand SVGs are referenced by relative URL from inside `<template>` blocks, which the composited render evaluates relative to the project root. |
| `hyperframes.json`, `meta.json`, `package.json` | Read by the CLI at the project root by name. |

## The one we opted out of

HyperFrames also auto-discovers a design spec at the project root, resolving
**`frame.md` → `design.md` → `DESIGN.md`** and taking the first that exists
(`.claude/skills/hyperframes-creative/references/design-spec.md` defines this, and
`ls frame.md design.md DESIGN.md | head -1` is literally how it looks).

We deliberately no longer satisfy that. On 2026-07-29 `frame.md` was split into
`config/tokens.yml` (machine-read) and `docs/design-contract.md` (human-read), so a
generic HyperFrames workflow landing here would find **no spec at all**.

**Why that's acceptable:** SCLA lesson videos never route through generic HyperFrames
workflow skills — `AGENTS.md` says so explicitly, and `/produce-video` → `/refine-scripts`
→ `/render-lessons` is the only sanctioned path. Those skills name both files directly.

**Why it's written down:** the failure mode is silent. A generic workflow would not
error; it would proceed with no brand spec and produce something plausible and
off-brand.

## To circle back

Two ways to close it, if we ever want generic HyperFrames workflows to work here:

1. **Restore a root `frame.md` as a pointer** — a short file whose frontmatter is
   generated from `config/tokens.yml` and whose body links to the contract. Cheap, but
   it reintroduces a generated file that can go stale unless a gate diffs it.
2. **Upstream a config key** — ask HyperFrames to let `hyperframes.json` declare the
   spec path, instead of hardcoding three filenames.

Option 2 is the honest fix. Neither is scheduled.
