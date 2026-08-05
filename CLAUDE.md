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
| Grant work | `projects/grants/` |
| Video production | `projects/video-production/CLAUDE.md` |
| Produce a video (one call; stops at the pilot gate) | `/produce-video` |
| Refine raw lesson scripts (batch) | `/refine-scripts` |
| Build / ship / publish lesson videos | `/render-lessons` |
| What shipped where (Wistia links) | `projects/video-production/PIPELINE-STATUS.md` → Delivered |
| Illustrated lesson video (default) | `projects/video-production/CLAUDE.md` |
| Start a new project | `/new-from-template` |
| Why a decision was made | `decisions/log.md` |
| Gate-enforcement rebuild (unarmed owner feedback) | `projects/video-production/render-qa/docs/HANDOFF-self-improving-gates-2026-07-29.md` |
| 2026-07 refactor — what ran, why, residues | `audits/2026-07-28-repo-audit-brief.md` (§0.0 ledger: open residues) |
| Integrations, endpoint IDs | `config/endpoints.json` |

## Commands

```bash
bash scripts/lint-refs.sh          # the repo's ONLY lint/test entry point — 14 checks,
                                   # incl. the render-qa suite (12), the STD-35 audit (10),
                                   # lesson-script layout (13) and PIPELINE-STATUS
                                   # freshness (14). CI runs it on every push.
python3 projects/video-production/render-qa/tests/run_tests.py   # that suite alone
python3 projects/video-production/render-qa/tests/test_variety.py # one file — each runs standalone
bash scripts/batch-status.sh       # resume key: the whole pipeline, read from disk alone
bash scripts/build-claim.sh S P    # the ONE way a build starts (lock + fence + journal + status)
bash scripts/build-release.sh S    # ...and the one way it ends
bash scripts/review.sh             # gate every build, serve previews of the clean ones
bash scripts/with-secrets.sh CMD   # Infisical injection — required for HeyGen/Wistia calls
```

## Rules

Standing rules live in `.claude/rules/` (auto-discovered): `.claude/rules/repo-hygiene.md` (always) and `.claude/rules/video-production.md` (factory work). Headline: **never load or route to `_archive/`**.

## Tool usage discipline (context budget)
- Read files with the Read tool, not `cat`/`head`/`tail`. Read specific line ranges when you know roughly where to look.
- Use plain `ls` scoped to ONE directory. No `ls -la`, no recursive/whole-tree listings.
- Use Grep/Glob for searching, not `find` or `grep` in Bash.
- Never re-read a file already read this session.

## Response Output
- Each session output is to be clear, concise and to the point
- It is to follow the What(the situation), So What (What was done), and Now What (the path forward,actions items, etc)
- You are to use lay language, avoid jargon and technical language