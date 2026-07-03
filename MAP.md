# SCLA Profile — Atlas

Where everything lives, and why it exists. Task routing lives in `CLAUDE.md`; rules live in `GOVERNANCE.md`.

## Routing tiers

1. **`CLAUDE.md` (root)** — task → one file: a leaf for single-fact tasks, a folder hub for open-ended ones.
2. **Folder hubs (README.md)** — every live folder with 3+ files carries one, listing each file's purpose: `member-support/`, `programs/`, `projects/`, `projects/grants/`, `templates/`, `brand/assets/`.
3. **Scoped `CLAUDE.md`** — only under `projects/*` and `programs/` for scopes needing isolated context (`projects/video-production/`, `programs/`). Hook-enforced.

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
context/                ← who we are
├── me.md               ← org identity (canonical; @-imported by root CLAUDE.md)
└── goals.md            ← current goals + current priorities (merged 2026-07-03)

brand/                  ← visual-identity.md (canonical colors/type/logo),
                          voice-and-tone.md, brand-guide.md (naming/tagline),
                          assets/ (SVG logos + README.md catalog)

member-support/         ← faqs.md (canonical member answers), glossary.md,
                          people.md (platform admin snapshot), products-services.md,
                          community-platform.md, README.md (folder hub),
                          member-support-integration.md (case/queue operating model)

operations/             ← team-roster.md (canonical roster)

programs/               ← README.md (folder hub), CLAUDE.md (scoped context),
                          programs-overview.md (canonical directory), course-catalog.md,
                          credentials-framework.md, scla-leadership-program.md,
                          career-readiness-accelerator.md,
                          one subfolder per program: early-career-boost/ (video-style.md)

partnerships/           ← NIC.md

projects/               ← grants/ (one folder per grant, new-grant.sh scaffolder),
                          video-production/ (scoped CLAUDE.md + templates/, incl.
                          heygen-lesson-script.md), kb-integration-plan.md
                          (FAQ→surfaces wiring plan), drive-review-brief.md
```

## Tooling

```
hooks/             ← live Claude Code hooks: governance-check.sh (structural
                     enforcement), skill-eval (routing), pre/post-tool + stop
                     (budget logging), doctor.sh, cache-heal, worktree cleanup,
                     skill-rules.json (routing registry — implemented skills only)
scripts/           ← lint-refs.sh (health linter), setup.sh, merge-settings.py
.claude/skills/    ← kb-audit, new-from-template
templates/         ← project scaffolds (grant/campaign/content/program) + README.md hub;
                     video script templates live in projects/video-production/templates/
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
