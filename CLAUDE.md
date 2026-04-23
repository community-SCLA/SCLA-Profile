# Claude Project Context — Client Onboarding

You are operating inside a **client onboarding workspace**. Every session, your
goal is to move the client one step closer to having a complete, living source
of truth their team can work from.

---

## The contract

1. **Client inputs** live in `client.config.yml` (URLs, doc paths, repos).
2. **Raw scrapes** go to `client/_raw/` — never edit these by hand.
3. **Structured outputs** go to `client/{knowledge-base,brand,workflows,source-of-truth}/`.
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
| 1. Ingest | `ingestor` | `client.config.yml` | `client/_raw/**` |
| 2. Brand | `brand-analyst` | `client/_raw/web/`, `client/_raw/assets/` | `client/brand/**` |
| 3. Knowledge | `knowledge-architect` | `client/_raw/docs/`, `client/_raw/web/` | `client/knowledge-base/**` |
| 4. Workflows | `workflow-mapper` | `client/_raw/artifacts/`, `client/_raw/docs/` | `client/workflows/**` |
| 5. Curate | `source-of-truth-curator` | all of `client/**` | `client/source-of-truth/**` |

Each stage is an **idempotent overwrite**: re-running regenerates the stage's
outputs from scratch based on the latest `_raw/` contents. Users edit only in
`client/source-of-truth/` (which is never overwritten after first generation).

---

## Orchestration

- `/onboard` runs all 5 stages with human-in-the-loop gates between them.
- `/ingest`, `/brand`, `/kb`, `/workflows` run a single stage.
- `/status` reports completion and confidence per stage.

---

## Working rules for Claude

- **Never fabricate client facts.** If `_raw/` doesn't contain evidence for a
  claim, mark the field `TODO: needs input` with a comment explaining what
  you need.
- **Prefer quoting over paraphrasing** in the knowledge base. Include
  `source:` links back into `_raw/` for traceability.
- **Flag automation opportunities inline.** Any time you see repeated manual
  steps in `_raw/artifacts/`, open a `workflows/automation-opportunities.md`
  entry.
- **One agent, one directory.** Don't have the `brand-analyst` write to
  `knowledge-base/`. Cross-references go through `source-of-truth-curator`.
- **Collaborate, don't own.** The goal is a workspace the *client's team*
  runs day-to-day. Write for them, not for Claude.

---

## Directory cheat sheet

```
client/_raw/web/              ← scraped HTML/markdown of the client's sites
client/_raw/docs/             ← imported Google Docs, PDFs, Notion exports
client/_raw/assets/           ← logos, screenshots, brand PDFs
client/_raw/artifacts/        ← Slack exports, tickets, meeting notes, Looms
client/knowledge-base/        ← structured wiki (glossary, people, products…)
client/brand/                 ← voice, visual identity, tokens, asset index
client/workflows/             ← current state, pain points, automation opps
client/source-of-truth/       ← charter, decision log, team handbook (owned by client)
```
