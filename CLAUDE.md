# Claude Project Context — SCLA Knowledge Base

You are operating inside the **SCLA knowledge base workspace**. Every session, your
goal is to move SCLA one step closer to having a complete, living source
of truth the team can work from.

---

## The contract

1. **SCLA inputs** live in `scla.config.yml` (URLs, doc paths, repos).
2. **Raw scrapes** go to `scla/_raw/` — never edit these by hand.
3. **Structured outputs** go to `scla/{knowledge-base,brand,operations,source-of-truth}/`.
4. **Every output file** starts with the frontmatter:
   ```yaml
   ---
   source: <path or URL in _raw/>
   generated_by: <agent name>
   last_updated: <YYYY-MM-DD>
   confidence: low | medium | high
   ---
   ```
5. **Templates** in `templates/` define the shape of each artifact. Agents
   fill them in — they do not invent new structures.

---

## The pipeline (5 stages, each a subagent)

| Stage | Agent | Reads | Writes |
|---|---|---|---|
| 1. Ingest | `ingestor` | `scla.config.yml` | `scla/_raw/**` |
| 2. Brand | `brand-analyst` | `scla/_raw/web/`, `scla/_raw/assets/`, `scla/source-of-truth/mission.md`, `scla/source-of-truth/voice-decisions.md` | `scla/brand/**` |
| 3. Knowledge | `knowledge-architect` | `scla/_raw/docs/`, `scla/_raw/web/`, `scla/source-of-truth/program-names.md`, `scla/source-of-truth/decisions-log.md` | `scla/knowledge-base/**`, `scla/programs/**`, `scla/members/**`, `scla/partnerships/**` |
| 4. Workflows | `workflow-mapper` | `scla/_raw/artifacts/`, `scla/_raw/docs/`, `scla/source-of-truth/decisions-log.md` | `scla/operations/**` |
| 5. Curate | `source-of-truth-curator` | all of `scla/**` | `scla/source-of-truth/**` (merge-only) + merges `kb-deltas.md` into `knowledge-base/` |

Each stage is an **idempotent overwrite**: re-running regenerates the stage's
outputs from scratch based on the latest `_raw/` contents. Human edits live only in
`scla/source-of-truth/` (which is write-protected on re-runs via PROPOSED_CHANGES.md).

---

## Orchestration

These are **Claude slash commands** — invoke them in Claude Code (type `/onboard` in the chat).

- `/onboard` runs all 5 stages with human-in-the-loop gates between them.
- `/ingest`, `/brand`, `/kb`, `/workflows` run a single stage.
- `/status` reports completion and confidence per stage.

---

## Context mode

This project uses the context-mode plugin. The pipeline ingests large volumes of web pages and documents — route all of it through context-mode to keep raw output out of the conversation context.

| Task | Use |
|------|-----|
| Crawl websites, run shell commands (any output >20 lines) | `ctx_batch_execute` |
| Search across indexed content, follow-up questions | `ctx_search` |
| Fetch external URLs (SCLA website, docs) | `ctx_fetch_and_index` |
| Analyze a file's contents | `ctx_execute_file` |
| Direct file edits | `Read` + `Edit`/`Write` as normal |

Do NOT use raw `Bash` for web scraping or commands that produce large output. Do NOT use `WebFetch` directly — route through `ctx_fetch_and_index`. Pipeline agents (`ingestor`, `brand-analyst`, etc.) must use context-mode for all fetches and command output.

---

## Rules

- **Never fabricate SCLA facts.** If `scla/_raw/` doesn't contain evidence for a
  claim, mark the field `TODO: needs input` with a comment explaining what
  you need.
- **Prefer quoting over paraphrasing** in the knowledge base. Include
  `source:` links back into `scla/_raw/` for traceability.
- **Flag automation opportunities inline.** Any time you see repeated manual
  steps in `scla/_raw/artifacts/`, open a `scla/operations/automation-opportunities.md`
  entry.
- **One agent, one directory.** Don't have the `brand-analyst` write to
  `knowledge-base/`. Exception: `knowledge-architect` writes to `knowledge-base/`,
  `programs/`, `members/`, and `partnerships/` — all are knowledge outputs.
  Cross-references go through `source-of-truth-curator`.
- **Collaborate, don't own.** The goal is a workspace the *SCLA team*
  runs day-to-day. Write for them, not for Claude.

---

## Projects

This repo IS the SCLA knowledge base project. It has no sub-projects.

## Context Files

Load selectively — not all at once:
- `context/me.md` — who runs this project and their role
- `context/goals.md` — what this project is trying to achieve
- `context/current-priorities.md` — what's actively being worked on right now

## Directory cheat sheet

```
scla/_raw/web/              ← scraped HTML/markdown of thescla.org
scla/_raw/docs/             ← imported Google Docs, PDFs, Notion exports
scla/_raw/assets/           ← logos, screenshots, brand PDFs
scla/_raw/artifacts/        ← Gemini meeting notes, Slack exports, stakeholder docs
scla/knowledge-base/        ← SCLA history, FAQs, glossary
scla/brand/                 ← voice, visual identity, tokens, asset index
scla/operations/            ← team structure, workflows, SOPs, automation ops
scla/programs/              ← program details and overviews
scla/members/               ← member journey, pledge process, onboarding
scla/partnerships/          ← partner profiles and relationship data
scla/source-of-truth/       ← mission, program names, voice decisions, decisions log, team handbook
scla/projects/              ← active project work (grants, campaigns, programs, content)
```
