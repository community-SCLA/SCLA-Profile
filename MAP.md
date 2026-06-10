# [YOUR_NAME] Ops — Navigation Map
**[YOUR_NAME] | [YOUR_FOCUS_AREAS]**
Last updated: [DATE]

> This file is the visual index of the entire repo. It does not load content — it routes.
> Claude: read this when you need to find something. Don't load what you don't need.

---

## Session Boot

```
Every session → Load context/me.md first, always.
Then identify task → load ONE entry from Task Routing below.
Stop. Do not load more.
```

---

## Task Routing

| I need to... | Load this | Notes |
|---|---|---|
| Write in [YOUR_NAME]'s voice | `context/me.md` | Already loaded in boot |
| *Your project 1 — replace with e.g. "Client: Acme"* | `projects/<your-folder>/CLAUDE.md` | |
| *Your project 2 — replace with e.g. "Job search"* | `projects/<your-folder>/CLAUDE.md` | |
| Start a new project from scratch | Run `/new-from-template` | Defaults to the generic skeleton |
| Run a scheduled task | `scheduled-tasks/<name>/` — that task's file only | One at a time |
| Debug an integration | `connections.md` | |
| Look up an endpoint ID | `endpoints.md` | |
| Review architectural decisions | `decisions/log.md` | |
| Work on a skill | See Skills Registry | Invoke via `Skill("name")` |

---

## File Map

### Identity & Context
```
context/
├── me.md               ← WHO [YOUR_NAME] IS — voice, tone, comm style, working prefs
├── goals.md            ← Career targets, priorities, hard requirements
├── work.md             ← Current employment status and availability
└── archives/           ← Superseded context files
```

### Memory (Session Recall)
```
memory/
├── MEMORY.md           ← Index. Start here.
├── overview.md         ← Big picture: world + current quarter priorities
└── glossary.md         ← Acronyms, shorthand, project paths
```

### Operations
```
connections.md          ← Every active integration: tool, connection method, auth, status
endpoints.md            ← Frequently used IDs: databases, folders, channels
decisions/
└── log.md              ← Append-only: architectural and strategic decisions
```

### Projects
Each project uses the generic lean standard folder (from `_templates/project-skeleton/`).
Build a new one with `/new-from-template`; ingest an existing repo with `/ingest-project`.
```
projects/
├── [project-1]/
│   ├── CLAUDE.md        ← entry: purpose, status, how to work here
│   ├── context/         ← overview.md, people.md, decisions.md
│   ├── planning/        ← roadmap.md (milestones/status)
│   ├── _inbox/          ← unsorted ingested content → triage to empty
│   └── _archive/        ← raw source + INGEST-LEDGER.md — NEVER read directly
└── example-project/    ← Template example — replace with real projects
    └── CLAUDE.md
```

### Automations
```
scheduled-tasks/
├── _config/            ← Shared config
├── _lib/               ← Shared library code
├── weekly-ops-audit/   ← Runs every Friday — repo health + skills sync
└── example-task/       ← Template stub — replace with real tasks
```

### Skills
```
skills/
├── README.md           ← Skills registry — invoke via Skill("name")
├── sync.py             ← Auto-syncs ~/.claude/registry.json → README.md
└── new-from-template/
```

### Templates (Reusable Shapes)
```
_templates/
├── project-skeleton/   ← DEFAULT project shape (generic, best-practice) — copied by /new-from-template
├── _examples/          ← Opt-in domain blueprints (lead-gen framework, four-phase roadmap)
└── new-from-template.py ← Fills [KEY] placeholders for the opt-in domain templates
```

### Scripts & Utilities
```
scripts/
├── setup.sh            ← Optional: copies hooks + merges settings (run after /onboard)
├── merge-settings.py   ← Merges hooks + safety rules into ~/.claude/settings.json
├── auto-sync.sh        ← Git auto-sync utility
└── notion-mcp.sh       ← Starts the Notion MCP server
```

### Tool Artifacts (Never Read Directly)
```
_tools/
└── graphify/
    └── GRAPH_REPORT.md  ← 12MB+. NEVER read directly. Use: graphify query / graphify path

projects/*/_archive/      ← Per-project: raw ingested source + INGEST-LEDGER.md.
                            NEVER read in a normal session. Exists only to prove
                            completeness and recover mistaken prunes.
```

### Hooks
```
hooks/                  ← Claude Code hook scripts — copied to ~/.claude/hooks/ by setup.sh
```

### Config
```
.claude/settings.json   ← Claude Code tool config + PreToolUse hooks (project-level)
```
