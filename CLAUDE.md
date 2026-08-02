# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# SCLA Profile — Company Knowledge Base

Markdown knowledge base for the org in `scla.config.yml` — no app, no build. The
"code" is prose plus the linter keeping it honest.

**Session boot:** match the task below, load the ONE file it names, stop.
No matching row? Open that folder's README.md hub if it has one — never the whole folder.

## Task Routing

| Task | Load |
| --- | --- |
| SCLA facts — identity, scale, mission | `context/me.md` |
| Brand colors, logo, type | `brand/visual-identity.md` |
| Voice & tone | `brand/voice-and-tone.md` |
| Naming, tagline | `brand/brand-guide.md` |
| Member-facing answer | `member-support/faqs.md` |
| Partner org | `partnerships/NIC.md` |
| Grant work | `projects/grants/` |
| Video essentials — voice ID, font, colors, spacing | `projects/video-production/design-system/config/tokens.yml` |
| Lesson script library (raw / refined / rendered) | `projects/video-production/lesson-scripts/README.md` |
| Worker-swarm delegation | the `ringer` skill; `config/ringer-engines.toml` |
| Start a new project | `/new-from-template` |
| Why a decision was made | `decisions/log.md` |
| Integrations, endpoint IDs | `config/endpoints.json` |

## Commands

```bash
bash scripts/lint-refs.sh          # the repo's ONLY lint/test entry point — 11 checks.
                                   # Also runs in CI on every push, non-blocking.
python3 scripts/check-enforcement.py --json   # check 10 alone + its full gap inventory
bash scripts/with-secrets.sh CMD   # Infisical injection — required for HeyGen/Wistia calls
./sync.sh                          # pull/commit/push main + bump the workspace submodule
```

## Editing this file

`CLAUDE.md` is the one doc graded by `scripts/check-enforcement.py`: under 600 words
(check 2), every backticked path resolvable on a fresh clone (check 1), each normative
sentence tagged Mechanism or Convention — naming a mechanism that doesn't exist
hard-fails check 10.

## Video production

**The project is live.** What retired on 2026-08-02 is a list of components, not the
project; they sit in `projects/video-production/_archive/`.

Live — build here: the script library at `projects/video-production/lesson-scripts/`,
and four essentials under `projects/video-production/design-system/` — tokens (HeyGen
voice ID, type scale, colors, spacing), the vendored fonts, the logo SVGs, and the
package.json CLI pin.

Retired: the /refine-scripts, /render-lessons and /produce-video skills; the render-qa
gate suite (check 11 idles); the renders-hyperframes and renders-mp4 staging trees;
the scene templates; the avatar pipeline (now HeyGen's web UI plus
hyperframes-media); and the refinement-log ledger.
A new pipeline starts from those plus `decisions/log.md`.

## Rules

Each rule names its enforcement mechanism, or is honestly labelled a **convention** (a request, not a guarantee).

- **Never load, route to, or "fix" anything under an `_archive/` folder — archives are read-only provenance.** *(Mechanism: `scripts/lint-refs.sh` check 7, run in CI on every push.)*
- **Deletion is the default disposition, not archiving — git history is the archive.** *(Convention.)*
- **The root is closed: `ls` at root is the approved set — new work goes under `projects/`, new config under `config/` or `.claude/`.** *(Convention.)*
- **No credentials or session state in the repo — secrets live only in Infisical.** *(Mechanisms: the `.gitignore` credential shield; `scripts/lint-refs.sh` check 9's no-secret-material scan.)*
- **Integration IDs live in `config/endpoints.json`, never hand-written into markdown and never invented (unknown stays `null`).** *(Mechanism: `scripts/lint-refs.sh` check 9 + CI.)*
- **Ringer tasks pin `"engine": "claude"` — the only engine; unset never defaults.** *(Mechanism: `scripts/lint-refs.sh` check 12 + CI.)*

## Tool usage discipline (context budget)
- Read tool over `cat`/`head`/`tail`; specific line ranges when you know where to look.
- Plain `ls`, scoped to ONE directory — no `ls -la`, no recursive/whole-tree listings.
- Grep/Glob to search, never `find`/`grep` in Bash. Never re-read a file read this session.
