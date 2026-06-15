# SCLA Profile — Navigation Map
**The Society for Collegiate Leadership & Achievement — knowledge base atlas**
Last updated: 2026-06-11

> This file routes; it does not load content. Find your target below, load that one file, stop.

---

## Session Boot

```
Every session → load context/me.md (org summary + working prefs).
Then identify the task → load ONE target from Task Routing.
Stop. Do not load more.
```

Dynamic session memory lives in `.remember/` (gitignored, local-only — handoffs, daily logs). It is not part of the curated KB.

---

## Task Routing

| I need to... | Load this |
| --- | --- |
| Know what SCLA is / org facts | `scla/source-of-truth/charter.md` (canonical) |
| Check current goals or priorities | `context/goals.md`, `context/current-priorities.md` |
| Look up brand colors, logo, type | `scla/brand/visual-identity.md` |
| Write in SCLA's voice | `scla/brand/voice-and-tone.md` |
| Check brand naming/tagline facts | `scla/brand/brand-guide.md` |
| Find a team member or role | `scla/operations/team-roster.md` |
| Answer a member-facing question | `scla/knowledge-base/faqs.md` |
| Look up a program | `scla/programs/programs-overview.md` |
| Work on a grant | `scla/projects/grants/` (one folder per grant + RFP briefs) |
| Work on video production | `scla/projects/video-production/CLAUDE.md` |
| Review past decisions | `decisions/log.md` |
| Debug an integration | `connections.md` |
| Learn how a tool connects (endpoints, auth, queries) | `references/{tool}-api.md` |
| Look up an endpoint ID | `endpoints.md` |
| Start a new project | `templates/` + `/new-from-template` |
| Trace a fact to its source | `docs/_archive/source-dumps/README.md` (index only) |

---

## File Map

### Root
```
CLAUDE.md          ← entry point: routing + rules one-liners
MAP.md             ← this file
GOVERNANCE.md      ← rulebook: hard stops, folder/commit discipline, growth rules
connections.md     ← active integrations: tool, method, auth, status
endpoints.md       ← known IDs (repo, org URLs); unknowns marked TODO: needs input
decisions/log.md   ← append-only decisions log
scla.config.yml    ← org metadata + ingest configuration
sync.sh            ← commit + push + parent-submodule update (main branch only)
```

### Identity & Context
```
context/
├── me.md                   ← session boot: org one-liner, brief roster, working prefs
├── goals.md                ← Q2 2026 goals + success criteria (working copy)
└── current-priorities.md   ← active work
```

### SCLA Knowledge
```
scla/
├── brand/                  ← visual-identity.md (colors/type, canonical), voice-and-tone.md,
│                             brand-guide.md, assets/ (SVG logos + index.md)
├── knowledge-base/         ← index.md (AI-facing org summary), glossary.md, people.md,
│                             products-services.md, faqs.md, community-platform.md,
│                             TODOS.md (gap tracker — pages still needing staff input)
├── operations/             ← team-roster.md (canonical roster), current-state.md,
│                             pain-points.md, automation-opportunities.md
├── source-of-truth/        ← charter.md (canonical org facts), mission.md,
│                             team-handbook.md, onboarding.md, rituals.md,
│                             program-names.md, voice-decisions.md
├── programs/               ← programs-overview.md, course-catalog.md, credentials-framework.md,
│                             scla-leadership-program.md, career-readiness-accelerator.md
├── partnerships/           ← NIC.md
└── projects/               ← grants/ (new-grant.sh scaffolder), video-production/
```

### Operations & Tooling
```
hooks/             ← live Claude Code hooks: skill-eval (routing), pre/post-tool + stop
                     (tool-budget logging), doctor.sh, cache-heal, worktree cleanup,
                     skill-rules.json (routing registry — implemented skills only)
scripts/           ← setup.sh, merge-settings.py, lint-refs.sh (repo health linter)
.claude/skills/    ← ingest, kb-audit, new-from-template, onboard
references/        ← per-tool integration references ({tool}-api.md) for connected MCP tools
templates/         ← project-campaign / content / grant / program scaffolds
audits/            ← kb-audit score snapshots
_inbox/            ← ingest staging (INGEST_MANIFEST.md triggers /ingest)
_archive/          ← superseded root files, orphaned docs (dated names)
docs/_archive/     ← raw Drive source dumps — provenance only, never load by default
```

---

## Not here (by design)

- `scheduled-tasks/` — doesn't exist yet; create when a real recurring automation exists (see GOVERNANCE.md "Future homes").
- Raw source material — only in `docs/_archive/source-dumps/`, reached via `source:` citations.
