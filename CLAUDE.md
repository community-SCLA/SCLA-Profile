# SCLA Profile — Company Knowledge Base

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
| Start a new project | `/new-from-template` |
| Why a decision was made | `decisions/log.md` |
| 2026-07 refactor — what ran, why, residues | `audits/2026-07-28-repo-audit-brief.md` (§0.0 ledger: open residues) |
| Integrations, endpoint IDs | `config/endpoints.json` |

## Commands

```bash
bash scripts/lint-refs.sh          # the repo's ONLY lint/test entry point — 11 checks,
                                   # incl. the STD-35 enforcement audit (check 10). Check 11
                                   # (render-qa suite) idles: the suite retired 2026-08-02.
bash scripts/with-secrets.sh CMD   # Infisical injection — required for HeyGen/Wistia calls
```

## Video production — retired 2026-08-02

The illustrated-lesson factory (skills, gates, render workspaces, scene templates) was
retired to `projects/video-production/_archive/`, which is **read-only provenance, not a
routing target** — do not load it to do work. Four essentials stayed live under
`projects/video-production/design-system/`: the tokens file (HeyGen voice ID, type
scale, colors, spacing) at `projects/video-production/design-system/config/tokens.yml`,
plus the vendored fonts, the logo SVGs, and the CLI pin in package.json beside it. The
script library at `projects/video-production/lesson-scripts/` is untouched. Any new
pipeline starts from those and from `decisions/log.md`.

## Rules

Standing rules live in `.claude/rules/` (auto-discovered): `.claude/rules/repo-hygiene.md`. Headline: **never load or route to `_archive/`**.

## Tool usage discipline (context budget)
- Read files with the Read tool, not `cat`/`head`/`tail`. Read specific line ranges when you know roughly where to look.
- Use plain `ls` scoped to ONE directory. No `ls -la`, no recursive/whole-tree listings.
- Use Grep/Glob for searching, not `find` or `grep` in Bash.
- Never re-read a file already read this session.
