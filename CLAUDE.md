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
| Partnerships | `scla/partnerships/` | Partner orgs (e.g. NIC) |
| Projects | `scla/projects/` | Active project tracking (grants live here) |
| Grants | `docs/grants/` | Grant briefs and RFP working docs |
| Templates | `templates/` | Reusable project/content/grant templates |

---

## Provenance — do not load by default

`docs/_archive/source-dumps/` holds **raw, unedited Google Drive exports** kept only so the
curated pages above stay traceable. It is ~2 MB of source material with one file per Drive doc.

- **Do not read these files into context** unless you are tracing a specific citation.
- Start from the curated `scla/` pages; follow a `source:` link into the archive only when you
  need the underlying detail.
- The index at `docs/_archive/source-dumps/README.md` maps each slug to its original Drive path.

---

## Sync

```bash
./sync.sh   # must be on main branch; commits, pushes, and updates workspace submodule
```

---

## Rules

- **Never fabricate SCLA facts.** If it's not in the files, mark it `TODO: needs input`.
- **Prefer quoting over paraphrasing.** Keep traceability to source documents. Cite into `docs/_archive/source-dumps/` (see Provenance above), not deleted ingest paths.
- **`scla/source-of-truth/` is team-owned.** Treat it as authoritative. Don't overwrite without explicit instruction.
- **Credentials go in `.env` only** — never hardcoded.
- **`sync.sh`** handles git sync to the parent workspace submodule — run it to push local changes up.
