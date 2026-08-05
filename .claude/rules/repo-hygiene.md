---
description: Repo-wide hygiene rules — unconditional, every session (P1, 2026-07-28)
---

# Repo hygiene

Each rule names its enforcement mechanism, or is honestly labelled a **convention** (a request, not a guarantee — see decisions/log.md on why prose governance was deleted).

- **Archives are read-only provenance, never routing targets.** Never load, route to, or "fix" anything under an `_archive/` folder. *(Mechanism: `scripts/lint-refs.sh` check 7, run in CI on every push.)*
- **Archiving is allowed.** When a file's provenance is worth keeping over outright deletion, move it into a nested `_archive/` folder inside its own directory (e.g. `docs/_archive/`, `lesson-scripts/<program>/_archive/`) — never a new root-level `_archive/` (the root is closed, see below). Once archived, it's read-only provenance per the rule above; do not spend effort correcting a file that's been archived or is slated for deletion. *(Convention.)*
- **The root is closed.** No new files or folders at the repo root beyond the current approved set (`ls` at root is the set; the refactor target is 21 items). New work goes under `projects/`, new config under `config/` or `.claude/`. *(Convention — the old `governance-check.sh` gate was deleted rather than armed, P3/R10.)*
- **No credentials or session state in the repo.** Secrets live only in Infisical; the Infisical machine-identity pair lives only in the Codespaces secret vault. *(Mechanisms: the `.gitignore` credential shield (S14) and `lint-refs.sh` check 10's no-secret-material scan on the registry.)*
- **Machine-first registries.** Integration IDs and endpoints live in `config/endpoints.json` — schema-validated, single-write. Never hand-write an ID into markdown; never invent an ID (unknown stays `null`). *(Mechanism: `lint-refs.sh` check 10 + CI.)*
