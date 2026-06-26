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
| Know what SCLA is / org facts | `context/me.md` (canonical live owner) |
| Check current goals or priorities | `context/goals.md`, `context/current-priorities.md` |
| Look up brand colors, logo, type | `scla/brand/visual-identity.md` |
| Write in SCLA's voice | `scla/brand/voice-and-tone.md` |
| Check brand naming/tagline facts | `scla/brand/brand-guide.md` |
| Find a team member or role | `scla/operations/team-roster.md` |
| Answer a member-facing question | `scla/member-support/faqs.md` |
| Look up a program | `scla/programs/programs-overview.md` |
| Work on a grant | `scla/projects/grants/` (one folder per grant + RFP briefs) |
| Work on video production | `scla/projects/video-production/CLAUDE.md` |
| Review past decisions | `decisions/log.md` |
| Debug an integration | `connections.md` |
| Look up an endpoint ID | `endpoints.md` |
| Start a new project | `templates/` + `/new-from-template` |
| Trace a fact to its source | `_archive/source-dumps/README.md` (index only) |

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
├── member-support/         ← index.md (AI-facing org summary), glossary.md, people.md,
│                             products-services.md, faqs.md, community-platform.md,
│                             kb-integration-plan.md, member-support-integration.md
├── operations/             ← team-roster.md (canonical roster), current-state.md,
│                             pain-points.md, automation-opportunities.md
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
templates/         ← project-campaign / content / grant / program scaffolds
audits/            ← kb-audit score snapshots
_inbox/            ← ingest staging (INGEST_MANIFEST.md triggers /ingest)
_archive/          ← superseded framework docs (dated names) + source-dumps/ (raw Drive exports —
                     provenance only, never load by default) + source-of-truth/ (archived charter,
                     handbook, onboarding — read-only provenance) + member-support/TODOS.md
                     (archived gap tracker)
```

---

## Not here (by design)

- `references/`, `scheduled-tasks/` — don't exist yet; create when real content exists (see GOVERNANCE.md "Future homes").
- Raw source material — only in `_archive/source-dumps/`, reached via `source:` citations.
