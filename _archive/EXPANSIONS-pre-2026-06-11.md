# EXPANSIONS — what to add as this repo grows

The KB ships lean on purpose. As you use it, you'll outgrow the base. This doc tells you what to add, when, and why — and what not to add.

> *The KB structure should look like a small, well-run organization — not a hoarder's basement.*

---

## What ships (don't remove)

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Root operating manual — authoritative |
| `context/` | Org identity, goals, current priorities |
| `connections.md` | System registry (team inventory + AI-reachability) |
| `scla/brand/` | Voice, tone, visual identity |
| `scla/source-of-truth/` | Charter, decisions log, team handbook, onboarding |
| `scla/operations/` | How the team operates, pain points, automation opportunities |
| `scla/knowledge-base/` | Glossary, people, products & services, FAQs |
| `scla/programs/` | Program documentation |
| `scla/partnerships/` | Partner org docs |
| `scla/projects/` | Active project tracking |
| `docs/grants/` | Grant briefs and RFP working docs |
| `templates/` | Reusable project/content/grant scaffolds |
| `.claude/skills/` | Installed skills |
| `docs/_archive/source-dumps/` | Raw Drive exports for provenance tracing only — do not load into context |

---

## What to add as you grow

| Add | When | Why |
|---|---|---|
| `audits/` | After first `/kb-audit` run | Track score over time; watch it climb |
| `references/{tool}-api.md` | Each time a new tool is wired in `connections.md` | Research once, reference forever; `/kb-audit` checks for this |
| `scla/operations/sops/` | When a recurring process gets handed to someone new | Consistent execution without re-explaining |
| `.claude/agents/` | When a repeatable multi-step research or writing task emerges | Keeps main session lean; sub-assistants run on their own context |
| Scoped `CLAUDE.md` in a sub-area | When a sub-project (e.g. a major grant, new program) needs isolated context | Scoped context without polluting the root |
| `scripts/` | When connecting a tool that has no MCP and needs a custom API script | Most second connections are scripts, not MCPs |

---

## What NOT to add

- **Don't dump raw Drive exports into `scla/` or `references/`.** That's what `docs/_archive/source-dumps/` is for. Interpreted facts only in the live KB.
- **Don't create `notes/`, `misc/`, `tmp/`, or `inbox/` folders.** Graveyards. Use `docs/_archive/` if something is old; write a proper file in the right place if it's new.
- **Don't pre-create folders you don't need yet.** Empty folders are noise. The structure should reflect actual usage, not hoped-for usage.
- **Don't fork `CLAUDE.md`.** One canonical root file. Sub-areas can have scoped ones; the root is authoritative.
- **Don't add parallel decisions files.** One decisions log at `scla/source-of-truth/decisions-log.md`.

---

## The two-yeses test

Before creating any new folder, ask:
1. Is this conceptually distinct from everything that already exists?
2. Will we touch this 3+ times in the next month?

Two yeses → add it. One yes → wait.

If you can't find something, that's a signal to consolidate — not to add another folder.
