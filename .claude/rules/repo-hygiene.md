---
description: Repo-wide hygiene rules — unconditional, every session (P1, 2026-07-28)
---

# Repo hygiene

Each rule names its enforcement mechanism, or is honestly labelled a **convention** (a request, not a guarantee — see decisions/log.md on why prose governance was deleted).

- **Archives are read-only provenance, never routing targets.** Never load, route to, or "fix" anything under an `_archive/` folder. *(Mechanism: `scripts/lint-refs.sh` check 7, run in CI on every push.)*
- **Deletion is the default disposition, not archiving.** Git history is the archive. Do not create new `_archive/` folders; do not spend effort correcting a file that is slated for deletion. *(Convention.)*
- **The root is closed.** No new files or folders at the repo root beyond the current approved set (`ls` at root is the set; the refactor target is 21 items). New work goes under `projects/`, new config under `config/` or `.claude/`. *(Convention — the old `governance-check.sh` gate was deleted rather than armed, P3/R10.)*
- **No credentials or session state in the repo.** Secrets live only in Infisical; the Infisical machine-identity pair lives only in the Codespaces secret vault. *(Mechanisms: the `.gitignore` credential shield (S14) and `lint-refs.sh` check 10's no-secret-material scan on the registry.)*
- **Machine-first registries.** Integration IDs and endpoints live in `config/endpoints.json` — schema-validated, single-write. Never hand-write an ID into markdown; never invent an ID (unknown stays `null`). *(Mechanism: `lint-refs.sh` check 10 + CI.)*
- **A written rule is a request; only a mechanism is a guarantee (Playbook STD-35).** Any rule that must hold every single time is enforced by a hook, a CI check, a lint, or a gate — never by a sentence. A doc may therefore never *claim* enforcement it doesn't have: an annotation must either name a mechanism that exists and is actually invoked, or say `Convention` out loud. Prose cannot be made enforceable; it can only be made unable to lie about being enforced. *(Mechanism: `scripts/check-enforcement.py`, run as `lint-refs.sh` check 10 in CI — hard-fails a broken claim, and reports the unbacked-rule gap inventory without blocking, per STD-38.)*
- **Don't write down what the file tree shows.** No hand-maintained inventories of folders, programs, or skills in docs — `ls` answers those. *(Convention; lint-refs check 1 catches dangling paths in CLAUDE.md.)*
