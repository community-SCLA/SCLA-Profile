# SCLA Profile — Company Knowledge Base

This repo is the living knowledge base for **The Society for Collegiate Leadership & Achievement (SCLA)**: brand, workflows, and source-of-truth documentation. This file is routing only — load targets, not content.

| Root companion | When to read it |
| --- | --- |
| `MAP.md` | Find where any fact or task lives — the repo atlas |
| `GOVERNANCE.md` | The rulebook: hard stops, folder discipline, commit prefixes, growth rules |
| `decisions/log.md` | Why structural and strategic choices were made (append-only) |

---

## Context Files

Load these selectively as needed — not all at once.

| File | What's in it |
| --- | --- |
| `context/me.md` | What SCLA is, who we serve, org identity (canonical live owner) |
| `context/goals.md` | What we're trying to accomplish |
| `context/current-priorities.md` | Active work and near-term focus |

---

## Projects

| Area | Path | Purpose |
| --- | --- | --- |
| Brand | `scla/brand/` | Voice, tone, visual identity, brand guide |
| Member Support | `scla/member-support/` | Glossary, people, products & services, FAQs, member support integration |
| Operations | `scla/operations/` | Team roster, how the team operates, pain points, automation opps |
| Programs | `scla/programs/` | Program documentation |
| Partnerships | `scla/partnerships/` | Partner orgs (e.g. NIC) |
| Projects | `scla/projects/` | Active project tracking — grants (briefs + RFP working docs), video production |
| Templates | `templates/` | Reusable project/content/grant templates |

---

## Provenance — do not load by default

`_archive/source-dumps/` holds **raw, unedited Google Drive exports** kept only so the
curated pages above stay traceable. It is ~2 MB of source material with one file per Drive doc.

- **Do not read these files into context, and never route to `_archive/` as a place to load canonical info** unless you are tracing a specific citation.
- Start from the curated `scla/` pages; follow a `source:` link into the archive only when you
  need the underlying detail.
- The index at `_archive/source-dumps/README.md` maps each slug to its original Drive path.

---

## Sync

```bash
./sync.sh   # must be on main branch; commits, pushes, and updates workspace submodule
```

---

## Rules

One-liners — full text and rationale in `GOVERNANCE.md`.

- **Never fabricate SCLA facts** — if it's not in the files, mark it `TODO: needs input`.
- **Prefer quoting over paraphrasing** — cite into `_archive/source-dumps/`.
- **Never route to the archive** — `_archive/` is read-only provenance, never a canonical owner, routing target, or "load this" pointer. Follow a `source:` citation into `_archive/source-dumps/` only when explicitly tracing provenance.
- **Reference pages stay lean** — pages under `scla/` and `context/` carry current-state facts only; why/history/status-metadata lives in `decisions/log.md`.
- **Credentials go in `.env` only** — never hardcoded.
- **Log structural changes** in `decisions/log.md`; push with `./sync.sh`.
