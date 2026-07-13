# Governance — How This Repo Stays Healthy

The single rulebook. Read this before any structural change.

> *The KB should look like a small, well-run organization — not a hoarder's basement.*

---

## Content Rules (absolute)

1. **Never fabricate SCLA facts.** If it's not in the files, mark it `TODO: needs input`.
   No guessed numbers, names, dates, or quotes — ever.
2. **Prefer quoting over paraphrasing.** Keep traceability: cite into
   `_archive/source-dumps/`.
3. **Never route to the archive.** `_archive/` is read-only provenance. Never list an
   `_archive/` path as a canonical owner, routing target, "see also", or "load this"
   pointer. Do not edit or overwrite archived files (hook-enforced). Follow a `source:`
   citation into `_archive/source-dumps/` ONLY when explicitly tracing a fact's provenance.
4. **Reference pages stay lean.** Pages under the knowledge folders (`brand/`,
   `member-support/`, `operations/`, `programs/`, `partnerships/`, `projects/`) and
   `context/` carry current-state facts only. The why / what-changed / history of a
   decision lives in `decisions/log.md` — never narrate rationale, status-date-owner
   metadata, or change history inside a reference page.
5. **Credentials go in `.env` only** — never hardcoded in any tracked file.
6. **Log structural changes** in `decisions/log.md` (append-only) and push with `./sync.sh`
   (main branch only).

---

## Canonical Owners (one question, one file)

Every fact has exactly one home; every other mention is a quote + pointer.

| Question | Canonical file |
| --- | --- |
| What is SCLA? (identity, scale, values) | `context/me.md` |
| Current goals / priorities / success criteria | `context/goals.md` |
| Who's on the team | `operations/team-roster.md` |
| Brand colors / type / logo | `brand/visual-identity.md` |
| Voice and tone | `brand/voice-and-tone.md` |
| Brand naming / tagline | `brand/brand-guide.md` |
| Why we decided X | `decisions/log.md` |

**Documented exceptions** (intentional copies, do not "fix"):
- `member-support/faqs.md` keeps self-contained member-facing answers (it feeds AI
  triage); eligibility facts mirror `member-support/products-services.md` (canonical).
- `member-support/people.md` is the platform admin-panel snapshot — unique account
  data, not a roster copy.

---

## Hard Stops (live enforcement)

What is actually enforced by tooling today — nothing aspirational:

- `hooks/governance-check.sh` (PreToolUse on Write/Edit/Bash) blocks:
  editing or overwriting anything in `_archive/`; banned directory names
  (`notes/`, `misc/`, `tmp/`, `inbox/`); any new path whose first segment is
  outside the Approved Root Layout; parallel decisions logs; scoped `CLAUDE.md`
  outside `projects/` and `programs/`; empty future-home placeholder dirs; `archive` instead of
  `_archive`.
- `.claude/settings.json` — tool permissions; `git push --force` denied.
- `hooks/skill-eval.sh` + `hooks/skill-rules.json` — skill routing on every prompt.
  The registry lists **implemented skills only**.
- `hooks/pre-tool.sh` / `hooks/post-tool.sh` / `hooks/stop.sh` — tool-budget logging.
- `hooks/doctor.sh`, `hooks/context-mode-cache-heal.mjs`, `hooks/cleanup-worktrees.sh` — self-healing.
- `scripts/lint-refs.sh` — repo health linter (manual run; see Health Checks).
- Registration split: project `.claude/settings.json` carries only the video
  snag-retro render reminder; the governance/budget/self-healing hooks above are
  registered in **global** `~/.claude/settings.json` — a fresh clone has no rails
  until they are re-registered there.

---

## Approved Root Layout

Files: `CLAUDE.md`, `MAP.md`, `GOVERNANCE.md`, `connections.md`, `endpoints.md`,
`scla.config.yml`, `sync.sh`, `.gitignore`, `.mcp.json`.
Directories: `.claude`, `.devcontainer`, `_archive`, `audits`, `brand`, `context`,
`decisions`, `hooks`, `member-support`, `operations`, `partnerships`, `programs`,
`projects`, `references`, `scripts`, `templates` (plus gitignored `.remember/`, `.env`).

Anything new at root needs a decisions-log entry first, then an update to the
`APPROVED_ROOT` list in `hooks/governance-check.sh` — the hook blocks it otherwise.

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
- Raw Drive exports anywhere live — interpreted facts only; raw goes to `_archive/source-dumps/`.
- `notes/`, `misc/`, `tmp/` folders — graveyards.
- Pre-created empty folders or empty placeholder files — structure reflects actual usage.
- A second routing table (CLAUDE.md owns task routing; MAP.md owns locations) or a
  parallel decisions file — one log: `decisions/log.md`.

---

## Growth Guide (add when, not before)

| Add | When |
| --- | --- |
| `references/{tool}-api.md` | A new tool is wired in `connections.md` |
| `scheduled-tasks/` | The team has a real recurring automation (none yet) |
| `operations/sops/` | A recurring process gets handed to someone new |
| `.claude/agents/` | A repeatable multi-step research/writing task emerges |
| Scoped `CLAUDE.md` under `projects/` or `programs/` | A sub-scope needs isolated context |
| Folder-hub README.md | A live folder reaches 3+ files (see MAP.md "Routing tiers") |

Create each only with its first real content, log the creation, and add new roots to
the hook's approved list.

---

## Health Checks

Run `bash scripts/lint-refs.sh` before any `structure:` commit and after any move/rename.
It verifies: referenced paths exist, root word budgets hold (CLAUDE.md ≤600, MAP.md ≤700,
GOVERNANCE.md ≤1000), no stale `decisions-log.md` or retired nested-layout paths, no
template placeholders, critical files present, no stale brand hex values, no archive
routing pointers, and skill-rules.json lists implemented skills only. Exit 0 = healthy.

---

## Branch Naming

Format: `DD-MM-YYYY-<short-description>` — lowercase, hyphen-separated, ≤ 5 words
(e.g. `28-06-2026-update-voice-tone`).

---

## Commit Discipline

| Prefix | Use for |
| --- | --- |
| `context:` | Changes to `context/` |
| `kb:` | Changes to `brand/`, `member-support/`, `operations/`, `programs/`, `partnerships/` |
| `ops:` | Changes to `hooks/`, `scripts/` |
| `skill:` | Adding or modifying `.claude/skills/` |
| `structure:` | Moves, folder changes, CLAUDE.md/MAP.md/GOVERNANCE.md edits |
| `project:` | Changes inside `projects/` |
| `endpoints:` | `connections.md` or `endpoints.md` |
| `fix:` | Bug fixes in scripts or hooks |
| `docs:` | Audits, decisions log, references |

`structure:` commits require reading this file first. Source-of-truth edits must name
every changed fact in the commit message.
