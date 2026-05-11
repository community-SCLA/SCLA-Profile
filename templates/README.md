# `templates/` — the shapes agents fill in

Every artifact an agent produces has a template here. Agents don't invent
new structures; they copy the template, fill it in from `_raw/`, and save
the result under `scla/`.

## Templates

### Pipeline templates (agent-generated, frontmatter required)

| Template | Used by | Output location |
|---|---|---|
| `kb-entry.md` | `knowledge-architect` | `scla/knowledge-base/*.md` |
| `brand-guide.md` | `brand-analyst` | `scla/brand/brand-guide.md` |
| `workflow.md` | `workflow-mapper` | sections in `scla/operations/current-state.md` |
| `automation-opportunity.md` | `workflow-mapper` | rows/sections in `scla/operations/automation-opportunities.md` |

### Project templates (human-managed, not overwritten by pipeline)

| Template | Used by | Output location |
|---|---|---|
| `project-grant.md` | `/project grant` command | `scla/projects/grants/` |
| `project-campaign.md` | `/project campaign` command | `scla/projects/campaigns/` |
| `project-content.md` | `/project content` command | `scla/projects/content/` |
| `project-program.md` | `/project program` command | `scla/projects/programs/` |

## Rules

- **Frontmatter is mandatory** on every output — `source`, `generated_by`,
  `last_updated`, `confidence`. The hook at `.claude/hooks/stamp-frontmatter.sh`
  stamps a default if the agent forgets.
- **Template fields in `<angle brackets>`** are placeholders — replace them.
- **Blank sections** get `TODO: needs input` with a specific question, never
  fabricated content.

## Adding a new template

1. Drop a new markdown file here with placeholder fields.
2. Reference it from the agent that should use it (e.g.
   `.claude/agents/<agent>.md`).
3. Update this README's table.
