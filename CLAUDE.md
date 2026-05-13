# SCLA Profile — Company Knowledge Base

This project is the living knowledge base for **The Society for Collegiate Leadership & Achievement (SCLA)**. It contains brand, workflows, and source-of-truth documentation for the organization.

---

## Context Files

Load these selectively as needed — not all at once.

| File | What's in it |
| --- | --- |
| `context/me.md` | What SCLA is, who we serve, org identity |
| `context/goals.md` | What we're trying to accomplish |
| `context/current-priorities.md` | Active work and near-term focus |

---

## Projects

| Area | Path | Purpose |
| --- | --- | --- |
| Brand | `scla/brand/` | Voice, tone, visual identity, brand guide |
| Knowledge Base | `scla/knowledge-base/` | Glossary, people, products & services, FAQs |
| Operations | `scla/operations/` | How the team operates, pain points, automation opps |
| Source of Truth | `scla/source-of-truth/` | Charter, decisions log, team handbook, onboarding |
| Programs | `scla/programs/` | Program documentation |
| Projects | `scla/projects/` | Active project tracking |
| Docs (staged) | `docs/` | Drive staging, grants, superpowers |
| Templates | `templates/` | Reusable project/content/grant templates |

---

## Sync

```bash
./sync.sh   # must be on main branch; commits, pushes, and updates workspace submodule
```

---

## Rules

- **Never fabricate SCLA facts.** If it's not in the files, mark it `TODO: needs input`.
- **Prefer quoting over paraphrasing.** Keep traceability to source documents.
- **`scla/source-of-truth/` is team-owned.** Treat it as authoritative. Don't overwrite without explicit instruction.
- **Credentials go in `.env` only** — never hardcoded.
- **`sync.sh`** handles git sync to the parent workspace submodule — run it to push local changes up.
