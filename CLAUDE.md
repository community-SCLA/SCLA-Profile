# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

# SCLA Profile — Company Knowledge Base

Markdown knowledge base for the org in `scla.config.yml` — no app, no build. The
"code" is prose plus the linter keeping it honest.

**Session boot:** match the task below, load the ONE file it names, stop.
No matching row? Ask — never load a whole folder or fall back to a README.

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
| Video process — stages, exit criteria, script rules | `projects/video-production/PROCESS.md` |
| A lesson's stage / next action | `projects/video-production/lessons/<program>/<stem>/status.yml` |
| Where every lesson stands | `projects/video-production/checks/status.py` |
| Video design tokens | `projects/video-production/design-system/config/tokens.yml` |
| Worker-swarm delegation | the `ringer` skill; `config/ringer-engines.toml` |
| Start a new project | `/new-from-template` |
| Why a decision was made | `decisions/log.md` |
| Integrations, endpoint IDs | `config/endpoints.json` |

## Commands

```bash
bash scripts/lint-refs.sh          # the repo's ONLY lint/test entry point — 14 checks, also in CI
python3 scripts/check-enforcement.py --json   # check 10 alone + gap inventory
bash scripts/with-secrets.sh CMD   # Infisical injection for HeyGen/Wistia calls
./sync.sh                          # pull/commit/push main + bump the submodule
```

## Editing this file

`CLAUDE.md` is graded by `scripts/check-enforcement.py`: under 600 words (check 2),
every backticked path resolvable on a fresh clone (check 1), each normative sentence
tagged Mechanism or Convention — a mechanism that doesn't exist hard-fails check 10.

## Video production

Being rebuilt on HyperFrames: every lesson a fully illustrated branded MP4, no
avatars, published to its program's Wistia project. The guide is
`projects/video-production/PROCESS.md`; per-lesson state lives in
`projects/video-production/lessons/<program>/<stem>/status.yml`, and
`projects/video-production/checks/status.py` prints the board. Retired components
sit in `projects/video-production/_archive/` — read-only provenance, never a build input.

## Rules

Each rule names its enforcement mechanism, or is honestly labelled a **convention** (a request, not a guarantee).

- **Never load, route to, or "fix" anything under an `_archive/` folder — archives are read-only provenance.** *(Mechanism: `scripts/lint-refs.sh` check 7, run in CI on every push.)*
- **Deletion is the default disposition, not archiving — git history is the archive.** *(Convention.)*
- **The root is closed: `ls` at root is the approved set — new work goes under `projects/`, new config under `config/` or `.claude/`.** *(Convention.)*
- **No credentials or session state in the repo — secrets live only in Infisical.** *(Mechanisms: the `.gitignore` credential shield; `scripts/lint-refs.sh` check 9's no-secret-material scan.)*
- **Integration IDs live in `config/endpoints.json`, never hand-written into markdown and never invented (unknown stays `null`).** *(Mechanism: `scripts/lint-refs.sh` check 9 + CI.)*
- **Ringer tasks pin `"engine": "claude"` — the only engine; unset never defaults.** *(Mechanism: `scripts/lint-refs.sh` check 12 + CI.)*
- **Every lesson has a status.yml naming its stage and next action; a stage is left only when its PROCESS.md exit criteria pass.** *(Mechanism: `projects/video-production/checks/verify-status-records.py` — `scripts/lint-refs.sh` check 13 + CI.)*
- **A README is for people; agents never route to one — what an agent must obey lives in a PROCESS.md or a check.** *(Mechanism: `scripts/lint-refs.sh` check 14 + CI.)*

## Tool usage discipline (context budget)
- Read tool over `cat`/`head`/`tail`; specific line ranges when you know where to look.
- Plain `ls`, scoped to ONE directory — no `ls -la`, no recursive/whole-tree listings.
- Grep/Glob to search, never `find`/`grep` in Bash. Never re-read a file read this session.
