# Client Onboarding Template

> 🧱 **This is a GitHub Template repo, not a working client project.**
> **Don't put real client data here.** Press **"Use this template"** to spin up
> a fresh private repo for each client. See [TEMPLATE.md](./TEMPLATE.md).

A plug-and-play Claude Code workspace for onboarding a new client end-to-end:
**scrape** their scattered sources → **structure** them into a knowledge base →
**codify** their brand → **map** their workflows → **ship** them a living
source of truth their team can collaborate in.

**👉 New here?** Read the **[📖 friendly guide with pictures](./docs/GUIDE.md)**
first. It assumes no prior Claude Code / agents / GitHub-template knowledge.

---

## The pipeline at a glance

```
                    ┌─────────────────────────────────────────┐
                    │       client.config.yml (you edit)      │
                    │  sites · docs · drives · repos · tools  │
                    └────────────────────┬────────────────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────────────────┐
    │                   /onboard  (orchestrator command)              │
    └───┬──────────────────┬──────────────────┬─────────────────┬─────┘
        │                  │                  │                 │
        ▼                  ▼                  ▼                 ▼
  ┌───────────┐      ┌───────────┐     ┌─────────────┐   ┌────────────┐
  │ ingestor  │      │  brand-   │     │ knowledge-  │   │ workflow-  │
  │  agent    │      │ analyst   │     │ architect   │   │  mapper    │
  └─────┬─────┘      └─────┬─────┘     └──────┬──────┘   └──────┬─────┘
        │                  │                  │                 │
        ▼                  ▼                  ▼                 ▼
  client/_raw/        client/brand/    client/knowledge-   client/workflows/
  (scraped source)   (guide + tokens)        base/         (current state +
                                           (wiki)          automation opps)
        │                  │                  │                 │
        └──────────────────┴────────┬─────────┴─────────────────┘
                                    ▼
                       ┌────────────────────────┐
                       │ source-of-truth-       │
                       │ curator  agent         │
                       └───────────┬────────────┘
                                   ▼
                       client/source-of-truth/
                       (charter · decisions · handbook)
```

Every box is a file in `.claude/` you can open, read, and edit.
Nothing is magic — it's markdown all the way down.

---

## Repo layout

```
.
├── CLAUDE.md                 ← Project-wide context Claude loads every session
├── client.config.yml         ← Per-client inputs: sources, targets, contacts
│
├── .claude/                  ← The plug-and-play engine
│   ├── settings.json         ← Permissions + hooks
│   ├── agents/               ← 5 specialized subagents (one per pipeline stage)
│   ├── commands/             ← 6 slash commands (/onboard, /ingest, /brand…)
│   └── skills/               ← 4 reusable capabilities (scraper, extractor…)
│
├── client/                   ← Everything produced for this client
│   ├── _raw/                 ← Untouched scraped inputs (audit trail)
│   ├── knowledge-base/       ← Structured wiki: glossary, people, products
│   ├── brand/                ← Brand guide: voice, visual identity, tokens
│   ├── workflows/            ← Current state + automation opportunities
│   └── source-of-truth/      ← Charter, decision log, team handbook
│
├── templates/                ← Markdown templates agents fill in
└── scripts/
    └── bootstrap.sh          ← Clone this repo for a new client in one command
```

---

## Quickstart

**Preferred path — GitHub Template:**

1. On GitHub, click **"Use this template" → "Create a new repository"**.
2. Name it `<client-slug>-onboarding`, set it to **Private**.
3. Clone locally, edit `client.config.yml`, open Claude Code, run `/onboard`.

**Local alternative (no GitHub):**

```bash
./scripts/bootstrap.sh acme-corp
cd ../acme-corp-onboarding
$EDITOR client.config.yml
# open Claude Code here:
/onboard
```

`/onboard` walks through: **ingest → brand → kb → workflows → source-of-truth**,
pausing at each phase so you can review. Run any phase on its own with
`/ingest`, `/brand`, `/kb`, `/workflows`. Check progress with `/status`.

### Keeping existing client repos in sync with the template

```bash
./scripts/update-engine.sh     # pulls the latest .claude/, templates/, scripts/
```

This never touches `client/` or `client.config.yml`. See
[scripts/update-engine.sh](./scripts/update-engine.sh).

---

## What makes it plug-and-play

| Property | How it shows up |
|---|---|
| **Composable** | Each agent does one job and writes to one directory. Swap any agent, the pipeline still runs. |
| **Inspectable** | All outputs are markdown in `client/`. No databases, no opaque state. |
| **Resumable** | Re-running `/onboard` picks up where you left off via `/status`. |
| **Forkable** | `bootstrap.sh` clones the template into a fresh repo per client. |
| **Collaborative** | `client/source-of-truth/` is designed to be the team's daily-driver wiki. |

---

## Extending

- **New source type?** Add a skill under `.claude/skills/` and reference it
  from the `ingestor` agent.
- **New output artifact?** Add a template under `templates/` and a sub-agent
  that produces it.
- **Automation hook?** Drop a shell script in `.claude/hooks/` and wire it
  into `.claude/settings.json`.

See `CLAUDE.md` for the full contract each component must follow.
