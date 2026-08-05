# Why this folder breaks the repo's project convention

Every other project here uses `README.md` / `AGENTS.md` / `run.sh` / `src/` / `config/`
/ `docs/` / `logs/`. This one keeps `assets/`, `hyperframes.json`, `meta.json` and
`package.json` at its root instead (and, until the template lane retired on
2026-08-05, `index.html` + `compositions/` — both now under `_archive/`).

That is not drift. HyperFrames required it while this was a renderable project,
and the shell is kept so the version pin and asset URLs stay where the
toolchain and old workspaces expect them.

## What HyperFrames imposes

| Path | Why it can't move |
|---|---|
| `assets/` | Fonts and brand SVGs are referenced by relative URL from inside `<template>` blocks, which the composited render evaluates relative to the project root — and every freeform workspace copies them from here. |
| `hyperframes.json`, `meta.json`, `package.json` | Read by the CLI at the project root by name. |

## The one we opted out of

HyperFrames also auto-discovers a design spec at the project root, resolving
**`frame.md` → `design.md` → `DESIGN.md`** and taking the first that exists
(`.claude/skills/hyperframes-creative/references/design-spec.md` defines this, and
`ls frame.md design.md DESIGN.md | head -1` is literally how it looks).

We deliberately no longer satisfy that. On 2026-07-29 `frame.md` was split into
`config/tokens.yml` (machine-read) and a prose contract (human-read, retired to
`_archive/` with the template lane on 2026-08-05), so a generic HyperFrames
workflow landing here would find **no spec at all**.

**Why that's acceptable:** SCLA lesson videos never route through generic HyperFrames
workflow skills — `AGENTS.md` says so explicitly, and `/produce-video` → `/refine-scripts`
→ `/render-lessons` is the only sanctioned path. Those skills name `tokens.yml` directly.

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
