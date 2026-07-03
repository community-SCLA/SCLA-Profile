# SCLA Profile — Atlas

Where everything lives, and why it exists. Task routing lives in `CLAUDE.md`; rules live in `GOVERNANCE.md`.

## Routing tiers

1. **`CLAUDE.md` (root)** — task → one file: a leaf for single-fact tasks, a folder hub for open-ended ones.
2. **Folder hubs (README.md)** — every live folder with 3+ files carries one, listing each file's purpose: `member-support/`, `projects/`, `projects/grants/`, `brand/assets/`. Exception: `programs/programs-overview.md` doubles as the programs hub (its directory table is canonical content).
3. **Scoped `CLAUDE.md`** — only under `projects/*` for sub-projects needing isolated context (`projects/video-production/`). Hook-enforced.

---

## Root

```
CLAUDE.md          ← entry point: task routing + the two session-binding rules
MAP.md             ← this file: the atlas
GOVERNANCE.md      ← the single rulebook
connections.md     ← HOW we connect: every system, mechanism, auth state
endpoints.md       ← WHICH IDs: URLs, database and folder IDs
scla.config.yml    ← org metadata (name, slug, industry, website)
sync.sh            ← commit + push + parent-submodule update (main branch only)
decisions/log.md   ← append-only decisions log
```

## Knowledge

```
context/                ← who we are; loaded at session boot
├── me.md               ← org identity (canonical)
├── goals.md            ← current goals
└── current-priorities.md ← active work

brand/                  ← visual-identity.md (canonical colors/type/logo),
                          voice-and-tone.md, brand-guide.md (naming/tagline),
                          assets/ (SVG logos + README.md catalog)

member-support/         ← faqs.md (canonical member answers), glossary.md,
                          people.md (platform admin snapshot), products-services.md,
                          community-platform.md, README.md (folder hub),
                          kb-integration-plan.md (FAQ→surfaces wiring),
                          member-support-integration.md (case/queue operating model)

operations/             ← team-roster.md (canonical roster)

programs/               ← programs-overview.md (canonical), course-catalog.md,
                          credentials-framework.md, scla-leadership-program.md,
                          career-readiness-accelerator.md,
                          early-career-boost-video-style.md

partnerships/           ← NIC.md

projects/               ← grants/ (one folder per grant, new-grant.sh scaffolder),
                          video-production/ (scoped CLAUDE.md + templates)
```

## Tooling

```
hooks/             ← live Claude Code hooks: governance-check.sh (structural
                     enforcement), skill-eval (routing), pre/post-tool + stop
                     (budget logging), doctor.sh, cache-heal, worktree cleanup,
                     skill-rules.json (routing registry — implemented skills only)
scripts/           ← lint-refs.sh (health linter), setup.sh, merge-settings.py
.claude/skills/    ← kb-audit, new-from-template
templates/         ← project/content/grant/program + HeyGen script scaffolds
references/        ← per-connected-tool API notes (notion-api.md)
audits/            ← kb-audit score snapshots
_archive/          ← read-only provenance: source-dumps/ (raw Drive exports,
                     indexed by its README.md) + superseded docs. Never a
                     routing target.
```

---

## Not here (by design)

- `scheduled-tasks/`, `.claude/agents/`, `operations/sops/` — created only with their first real content (see GOVERNANCE.md "Growth Guide").
- `.remember/` — gitignored local session memory; not part of the curated KB.
- Raw source material — only in `_archive/source-dumps/`, reached via `source:` citations.
