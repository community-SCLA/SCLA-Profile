# Skill: new-from-template

Use this skill to start a **new, greenfield** project. (To bring an *existing* repo into
the framework, use `/ingest-project` instead.)

## What this does

Creates a new project folder under `projects/`. The **default** is the generic,
best-practice project skeleton — it fits almost any project. For projects that genuinely
match a specialized domain, you can additionally lay down an opt-in blueprint from
`_templates/_examples/`.

## Steps

### 1. Scaffold the generic skeleton (default for almost everything)

From the repo root:

```bash
python3 scripts/ingest.py scaffold <project-name>
```

This creates `projects/<project-name>/` with `CLAUDE.md`, `context/` (overview, people,
decisions), `planning/roadmap.md`, and the `_inbox/` + `_archive/` slots.

### 2. Fill the placeholders

Read each scaffolded file and replace its `[PLACEHOLDER]` tokens with real values — infer
what you can, ask the user for the rest. Delete any slot file that genuinely doesn't apply
(e.g. `context/people.md` for a solo project). Add the project to the root `MAP.md` Task
Routing table and Projects map.

**For most projects, you're done here.** The steps below are only for the specialized
lead-gen domain templates.

### 3. (Opt-in only) Add a domain blueprint

Only if the project really is a content-driven lead-gen consultancy, lay down a domain
blueprint from `_templates/_examples/`:

- `framework` — two-layer lead gen framework (`_templates/_examples/lead-gen-framework-template.md`)
- `roadmap` — four-phase execution roadmap (`_templates/_examples/four-phase-roadmap-template.md`)

Collect its placeholder values (`PROJECT_NAME`, `EXECUTION_LEAD`, `STRATEGY_PARTNER`,
`PRIMARY_CHANNEL`, `ICP`, `CORE_VALUE_PROP`, service tiers, tools — see the template
header for the full list), then run from the repo root:

```bash
python3 _templates/new-from-template.py \
  <framework|roadmap> \
  projects/<project-name>/planning/<framework|roadmap>.md \
  "PROJECT_NAME=<value>" "EXECUTION_LEAD=<value>" ...
```

Run once per template type needed.

## Notes

- The generic skeleton is always the base. Domain blueprints sit *on top* of it (in
  `planning/`), they don't replace it.
- If a target file already exists, treat it as an existing instance — confirm before overwriting.
- Unfilled `[KEY]` placeholders stay visible in the output so nothing is silently wrong.
