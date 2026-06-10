# Guardrails — How This Repo Stays Healthy

This file documents every enforcement mechanism in the system.
Read it when something feels off or before making a structural change.

---

## Layer 1 — Hard Stops (Real-Time)

Enforced by `.claude/settings.json` PreToolUse hooks. These fire before the action executes.

| Trigger | What happens | Why |
|---|---|---|
| `mkdir` with a path not in the approved folder list | Warning printed; Claude must confirm | Prevents folder sprawl |
| Reading `_tools/graphify/GRAPH_REPORT.md` directly | Blocked | 12MB — destroys context |
| Reading any `*.log` file over 1MB | Warning: use `tail` instead | Log files balloon |

**Approved root-level directories** (any new dir outside this list triggers a warning):
`context`, `memory`, `decisions`, `projects`, `scheduled-tasks`, `skills`, `scripts`,
`references`, `docs`, `audits`, `_templates`, `_tools`, `.claude`, `.github`,
`.planning`, `.understand-anything`, `.vscode`, `hooks`

---

## Layer 2 — Weekly Automated Scan (Friday)

Run by `weekly-ops-audit` every Friday. Surfaces drift in the Notion audit report.

**Repo Health checks run every Friday:**

1. **New directory detector** — compares `ls -d */` against the approved list above. Flags anything new.
2. **Skills sync drift** — compares `~/.claude/registry.json` count against `skills/README.md` table rows. Flags mismatches.
3. **Root clutter check** — flags any files at root not in the approved list.
4. **Endpoint ID audit** — greps scripts for hardcoded Notion UUIDs (36-char pattern); flags any not in `endpoints.md`.
5. **Ghost file check** — verifies critical files exist on disk.

Approved root files: `CLAUDE.md`, `MAP.md`, `EXPANSIONS.md`, `GUARDRAILS.md`, `connections.md`,
`endpoints.md`, `.gitignore`, `.env.example`, `.infisical.json`

After the audit, the script automatically calls:
```bash
python3 skills/sync.py --write
```

---

## Layer 3 — Soft Rules (Every Session)

Claude reads these from CLAUDE.md. Not enforceable by code, but Claude follows them.

### Before creating a new file:
- Does it fit an existing folder? If yes → put it there.
- Will this be touched 3+ times in the next month? If no → don't create it yet.

### Before creating a new folder:
Run the three-question test from `EXPANSIONS.md`:
1. Is this conceptually new?
2. Will I touch it 3+ times in the next month?
3. Could a future skill route here naturally?

Two yeses = add. One yes = wait. Log the decision in `decisions/log.md`.

### Before modifying CLAUDE.md:
- Read the current version fully first
- Only add/change sections that reflect actual current behavior
- Never remove rules — if a rule is wrong, replace it with a better one
- Commit separately with prefix `structure:` so it's visible in git log

### Before adding a skill:
1. Check `skills/README.md` — does something like this already exist?
2. Register in `~/.claude/registry.json`
3. Run `python3 skills/sync.py --write`
4. Log in `decisions/log.md`: what it does, when to use it

---

## Layer 4 — Commit Discipline

Every commit message uses a prefix. This makes the git log a readable ops record.

| Prefix | Use for |
|---|---|
| `context:` | Changes to `context/`, `memory/` |
| `ops:` | Changes to `scheduled-tasks/`, `scripts/` |
| `skill:` | Adding or modifying skills |
| `structure:` | Moving files, adding folders, changing CLAUDE.md or MAP.md |
| `project:` | Changes inside a `projects/` subdirectory |
| `endpoints:` | Updates to `connections.md` or `endpoints.md` |
| `fix:` | Bug fixes in scripts or automations |
| `docs:` | Updating references, audits, decisions log |

**Rule:** `structure:` commits require reading GUARDRAILS.md first.

---

## What the Weekly Audit Report Looks Like

Every Friday, the ops audit Notion page includes a **Repo Health** section:

```
## Repo Health
New folders:        None  ✅  (or: [folder-name] — not in approved list ⚠️)
Skills in sync:     107/107 ✅  (or: N skills in registry missing from README ⚠️)
Root clutter:       None  ✅
Hardcoded IDs:      None  ✅
Critical files:     All present ✅
Skills README:      Auto-updated ✅
```

If any row shows ⚠️, the "What Needs Attention" section tells you exactly what to fix.

---

## The Anti-Sprawl Checklist

Before any session where you're building something new, Claude should run through this:

- [ ] Does this belong in an existing project? (`projects/`)
- [ ] Is this an automation that runs on schedule? (`scheduled-tasks/`)
- [ ] Is this a reusable procedure? (`skills/`)
- [ ] Is this a utility script? (`scripts/`)
- [ ] Is this a document shape I'll reuse? (`_templates/`)
- [ ] Is this reference material? (`references/`)
- [ ] Is this a strategy doc? (`docs/`)
- [ ] None of the above → log in `decisions/log.md` before creating anything
