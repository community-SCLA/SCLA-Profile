# Governance — How This Repo Stays Healthy

The single rulebook. Merges the former GUARDRAILS.md and EXPANSIONS.md (archived in
`_archive/` with `-pre-2026-06-11` suffixes). Read this before any structural change.

> *The KB should look like a small, well-run organization — not a hoarder's basement.*

---

## Content Rules (absolute)

1. **Never fabricate SCLA facts.** If it's not in the files, mark it `TODO: needs input`.
   No guessed numbers, names, dates, or quotes — ever.
2. **Prefer quoting over paraphrasing.** Keep traceability: cite into
   `_archive/source-dumps/` (never into deleted ingest paths).
3. **Never route to the archive.** `_archive/` is read-only provenance. Never list an
   `_archive/` path as a canonical owner, routing target, "see also", or "load this"
   pointer. It is a historical record only — canonical org facts live in `context/me.md`
   (identity) and `context/goals.md` (goals). Do not edit or relocate archived files.
   Follow a `source:` citation into `_archive/source-dumps/` ONLY when explicitly tracing
   a fact's provenance.
4. **Reference pages stay lean.** Pages under `scla/` and `context/` carry current-state
   facts only. The why / what-changed / history of a decision lives in `decisions/log.md` —
   never narrate rationale, status-date-owner metadata, or change history inside a
   reference page.
5. **Credentials go in `.env` only** — never hardcoded in any tracked file.
6. **Log structural changes** in `decisions/log.md` (append-only) and push with `./sync.sh`
   (main branch only).

---

## Canonical Owners (one question, one file)

Every fact has exactly one home; every other mention is a quote + pointer.

| Question | Canonical file |
| --- | --- |
| What is SCLA? (identity, scale, values) | `context/me.md` (canonical live owner) |
| Current goals / success criteria | `context/goals.md` |
| Who's on the team | `scla/operations/team-roster.md` |
| Brand colors / type / logo | `scla/brand/visual-identity.md` |
| Voice and tone | `scla/brand/voice-and-tone.md` |
| Why we decided X | `decisions/log.md` |

**Documented exceptions** (intentional copies, do not "fix"):
- `context/me.md` is the canonical live org-identity owner and carries a brief name list — session boot needs it without extra loads.
- The archived team-handbook and charter (in the read-only source-of-truth archive) carry a frozen roster copy and the original success criteria. These are provenance, NOT routing targets — the live owners are `scla/operations/team-roster.md` and `context/goals.md`. Reach the archive only to trace provenance.
- `scla/member-support/faqs.md` keeps self-contained member-facing answers (it feeds AI triage); eligibility facts mirror `scla/member-support/products-services.md` (canonical).
- `scla/member-support/people.md` keeps the platform admin-panel snapshot — unique account data, not a roster copy.

---

## Hard Stops (live enforcement)

What is actually enforced by tooling today — nothing aspirational:

- `.claude/settings.json` — tool permissions; `git push --force` denied.
- `hooks/skill-eval.sh` + `hooks/skill-rules.json` — skill routing on every prompt.
  The registry lists **implemented skills only**; routing to phantom skills is the
  framework's collapse failure mode.
- `hooks/pre-tool.sh` / `hooks/post-tool.sh` / `hooks/stop.sh` — tool-budget logging.
- `hooks/doctor.sh`, `hooks/context-mode-cache-heal.mjs`, `hooks/cleanup-worktrees.sh` — self-healing.
- `scripts/lint-refs.sh` — repo health linter (manual run; see Health Checks).

---

## Approved Root Layout

Files: `CLAUDE.md`, `MAP.md`, `GOVERNANCE.md`, `connections.md`, `endpoints.md`,
`scla.config.yml`, `sync.sh`, `.gitignore`.
Directories: `.claude`, `_archive`, `_inbox`, `audits`, `context`, `decisions`,
`hooks`, `references`, `scla`, `scripts`, `templates` (plus gitignored `.remember/`).

Anything new at root needs a decisions-log entry first.

---

## Soft Rules (every session)

**Before creating a file:** Does it fit an existing folder? Will it be touched 3+ times
in the next month? No to either → don't create it.

**Before creating a folder — the three-question test:**
1. Conceptually new? 2. Touched 3+ times next month? 3. Could a skill route here naturally?
Two yeses = add (and log it). One yes = wait. Can't find something? Consolidate — don't add.

**Before modifying CLAUDE.md / MAP.md / this file:** read the current version fully;
reflect actual behavior only; never silently remove a rule — replace it with a better one;
commit separately with prefix `structure:`.

**What NOT to add:**
- Raw Drive exports into `scla/` or anywhere live — interpreted facts only; raw goes to `_archive/source-dumps/`.
- `notes/`, `misc/`, `tmp/` folders — graveyards.
- Pre-created empty folders — structure reflects actual usage, not hoped-for usage.
- A second `CLAUDE.md` at root or a parallel decisions file — one log: `decisions/log.md`.

---

## Growth Guide (add when, not before)

| Add | When |
| --- | --- |
| `references/{tool}-api.md` | A new tool is wired in `connections.md` — research once, reference forever |
| `scheduled-tasks/` | The team has a real recurring automation (none yet) |
| `scla/operations/sops/` | A recurring process gets handed to someone new |
| `.claude/agents/` | A repeatable multi-step research/writing task emerges |
| Scoped `CLAUDE.md` in a sub-area | A sub-project (major grant, new program) needs isolated context |

**Future homes:** `references/` and `scheduled-tasks/` are intentionally absent. Create
each only with its first real content, and log the creation.

---

## Health Checks

Run `bash scripts/lint-refs.sh` before any `structure:` commit and after any move/rename.
It verifies: referenced paths exist, root word budgets hold (CLAUDE.md ≤600, MAP.md ≤700,
GOVERNANCE.md ≤1000), no stale `decisions-log.md` paths, no template placeholders, critical
files present, no stale brand hex values, and no archived source-of-truth routing
pointers in the live KB. Exit 0 = healthy.

---

## Branch Naming

Format: `DD-MM-YYYY-<short-description>` (e.g. `28-06-2026-update-voice-tone`)

- Date-first keeps branches chronologically sortable
- Description: lowercase, hyphen-separated, ≤ 5 words
- Example: `28-06-2026-add-grant-brief-template`

---

## Commit Discipline

| Prefix | Use for |
| --- | --- |
| `context:` | Changes to `context/` |
| `kb:` | Changes to `scla/` content |
| `ops:` | Changes to `hooks/`, `scripts/` |
| `skill:` | Adding or modifying `.claude/skills/` |
| `structure:` | Moves, folder changes, CLAUDE.md/MAP.md/GOVERNANCE.md edits |
| `project:` | Changes inside `scla/projects/` |
| `endpoints:` | `connections.md` or `endpoints.md` |
| `fix:` | Bug fixes in scripts or hooks |
| `docs:` | Audits, decisions log, references |

`structure:` commits require reading this file first. Source-of-truth edits must name
every changed fact in the commit message.
