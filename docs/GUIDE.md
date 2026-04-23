# 📖 The Guide — How to Use This Template

> Written to be skimmable. TL;DR is first. Come back to the cheat sheet
> at the bottom whenever you're stuck.

---

## 🚀 If you only read one thing

1. Click **"Use this template"** on GitHub → get a fresh repo for your client.
2. Fill in **`client.config.yml`** (the client's name + where their stuff lives).
3. Open **Claude Code** in that repo and type **`/onboard`**.
4. Claude produces a full knowledge base, brand guide, workflow map, and
   source-of-truth wiki in `client/`.

That's it. Everything below is just the *why* and *how-it-works*.

---

## 🧠 The mental model (one picture)

```
             YOU                                  CLAUDE CODE
              │                                         │
    (edit client.config.yml) ──────────────────────►   │
              │                                         │
              │                                   /onboard
              │                                         │
              │     ┌─────────────┬─────────────┬───────┼─────────┬───────────────┐
              │     ▼             ▼             ▼       ▼         ▼               ▼
              │   SCRAPE        BRAND      KNOWLEDGE  WORK-    SOURCE-OF-    GATES
              │  (ingestor)   (brand-      (know-     FLOWS    TRUTH         (you approve
              │               analyst)     architect)  (mapper) (curator)     between
              │     │             │             │       │         │           stages)
              ▼     ▼             ▼             ▼       ▼         ▼
         client/_raw/    client/brand/   client/        client/   client/
         (the raw scraped        knowledge-base/  workflows/  source-of-truth/
           source material)      (the wiki)                     (the team's
                                                                daily driver)
```

**Takeaway:** you fill in one file, run one command, review Claude's output
at each stage, and end up with a living workspace the client's team uses.

---

## 🧩 6 words to know (glossary)

| Word | Plain meaning |
|---|---|
| **Claude Code** | A terminal app from Anthropic. You chat with Claude and it can read/write files, run commands, etc. |
| **Agent** | A specialized "mini-Claude" focused on one job (e.g. `brand-analyst`). Think of it as an employee with a specific role. |
| **Skill** | A specific capability (e.g. `web-scraper`). Agents call skills like you'd call a coworker with expertise. |
| **Slash command** | Something you type like `/onboard`. Shortcut to kick off a workflow. |
| **`.claude/`** | A folder in a repo where Claude Code looks for agents, commands, skills, and settings. |
| **Template repo** | A GitHub repo marked "reusable starter." Press a button → get a fresh copy with no shared history. |

**Not a fork.** A fork is connected to the parent and shares history. A
template is a clean stamp-out. We want templates for client work so each
client's data stays isolated.

---

## 🗂️ What every folder does (annotated tree)

```
📁 /                                  ← the template root
│
├─ 📘 README.md                       ← overview + "what is this"
├─ 📘 TEMPLATE.md                     ← "this is the template, don't put client data here"
├─ 📘 CLAUDE.md                       ← context Claude reads at every session
├─ 📝 client.config.yml               ← ⭐ the ONE file you edit per client
├─ 📘 .gitignore                      ← what NOT to commit
│
├─ 📁 docs/                           ← you are reading this
│   └─ 📘 GUIDE.md                    ← this file
│
├─ 📁 .claude/                        ← 🤖 the engine Claude uses
│   ├─ ⚙️  settings.json              ← permissions + auto-hooks
│   ├─ 📁 agents/                     ← the 5 specialists
│   │   ├─ ingestor.md                   → scrapes sources
│   │   ├─ brand-analyst.md              → builds brand guide
│   │   ├─ knowledge-architect.md        → builds wiki
│   │   ├─ workflow-mapper.md            → maps processes
│   │   └─ source-of-truth-curator.md    → stitches it all together
│   ├─ 📁 commands/                   ← the slash commands you type
│   │   ├─ onboard.md      (/onboard — full pipeline)
│   │   ├─ ingest.md       (/ingest — just the scraping step)
│   │   ├─ brand.md        (/brand — just the brand guide step)
│   │   ├─ kb.md           (/kb — just the knowledge base step)
│   │   ├─ workflows.md    (/workflows — just the workflow step)
│   │   └─ status.md       (/status — progress dashboard)
│   ├─ 📁 skills/                     ← specific capabilities
│   │   ├─ web-scraper/
│   │   ├─ doc-ingester/
│   │   ├─ brand-extractor/
│   │   └─ workflow-analyzer/
│   └─ 📁 hooks/                      ← auto-triggered scripts
│       └─ stamp-frontmatter.sh
│
├─ 📁 templates/                      ← fill-in shapes agents use
│   ├─ kb-entry.md
│   ├─ brand-guide.md
│   ├─ workflow.md
│   └─ automation-opportunity.md
│
├─ 📁 scripts/                        ← utilities you run outside Claude
│   ├─ bootstrap.sh                   → (local alternative to GitHub template)
│   └─ update-engine.sh               → pull latest .claude/ from the template
│
├─ 📁 client/                         ← 📤 EVERYTHING CLAUDE PRODUCES GOES HERE
│   ├─ 📁 _raw/                       ← untouched scraped sources (audit trail)
│   │   ├─ web/                       → scraped websites
│   │   ├─ docs/                      → imported PDFs, Google Docs, etc.
│   │   ├─ assets/                    → logos, images
│   │   └─ artifacts/                 → Slack exports, tickets, meeting notes
│   ├─ 📁 knowledge-base/             → glossary, people, products, tools, FAQs
│   ├─ 📁 brand/                      → voice, visual identity, design tokens
│   ├─ 📁 workflows/                  → current-state + automation opportunities
│   └─ 📁 source-of-truth/            → 👥 THE CLIENT'S TEAM OWNS THIS
│
└─ 📁 .github/
    └─ workflows/
        └─ template-cleanup.yml       → optional: wipe placeholders on first use
```

### Why this shape?

- **One folder per stage** of the pipeline → easy to reason about, easy to swap parts.
- **`_raw/` is read-only** → we never overwrite the evidence trail.
- **`source-of-truth/` is the client's** → after first generation, never auto-overwritten.
- **Everything is markdown** → inspectable, git-friendly, no mystery databases.

---

## 🛠️ Using it for a NEW CLIENT (the 4 big steps)

### Step 1 — Spawn a fresh repo for the client *(30 seconds)*

```
          ┌─────────────────────────────────┐
          │  github.com/.../client-onboarding   ← this template
          │                                  │
          │   [ 🟢 Use this template ▼ ]    │  ← click this button
          │                                  │
          └──────────┬──────────────────────┘
                     │
                     ▼
          ┌─────────────────────────────────┐
          │  Create a new repository         │
          │                                  │
          │  Owner:   your-org    ▼          │
          │  Name:    acme-onboarding        │
          │                                  │
          │  ○ Public   ⦿ Private  ← ALWAYS │
          │                                  │
          │  [ Create repository ]           │
          └─────────────────────────────────┘
```

**Why private?** Client data is confidential. Default to private, always.

---

### Step 2 — Fill in `client.config.yml` *(5 minutes)*

This is the **only file you edit per client.** Open it, drop in the client's
info and sources.

```yaml
client:
  name: "Acme Corp"             ← ⭐ REQUIRED
  slug: "acme-corp"             ← ⭐ REQUIRED  (lowercase, kebab-case)
  industry: "B2B logistics"
  primary_contact:
    name: "Jane Doe"
    email: "jane@acme.com"
    role: "COO"

sources:
  websites:
    - url: "https://acme.com"          ← ⭐ crawl their site
      crawl_depth: 2
      include_assets: true

  docs:
    - path: "inbox/"                    ← drop PDFs/DOCX here manually
    - url: "https://docs.google.com/..."

  artifacts:
    - label: "Slack #general export"
      path: "inbox/slack-export.zip"    ← drop Slack/ticket exports here
```

**🟢 Green fields = you fill these in.**
**🟡 Empty lists = leave empty if not applicable.**

Full field list is in the file itself (it's well-commented).

---

### Step 3 — Let Claude do the work *(15–30 min, most of it waiting)*

Open the repo in Claude Code and type:

```
/onboard
```

Claude will walk through 5 stages, pausing between each for you to review:

```
  1. INGEST       →  scrapes websites + imports docs     → client/_raw/
         [ you review: did it get everything? ]
                         ▼
  2. BRAND        →  builds brand guide from web copy    → client/brand/
         [ you review: do the colors/voice look right? ]
                         ▼
  3. KNOWLEDGE    →  builds wiki from docs               → client/knowledge-base/
         [ you review: any hallucinations? any gaps? ]
                         ▼
  4. WORKFLOWS    →  maps processes + automation opps    → client/workflows/
         [ you review: are the top 5 recommendations sane? ]
                         ▼
  5. CURATE       →  stitches everything into a wiki     → client/source-of-truth/
         [ you review: is this something the client can use tomorrow? ]
```

**If a stage looks wrong:** just say so in chat. Claude will fix it or ask
what went wrong. You can re-run individual stages with `/ingest`, `/brand`,
`/kb`, or `/workflows`.

**Check progress at any point with `/status`** — it'll show you:

```
📊 Onboarding status — Acme Corp

  Ingest          ✅  (12 files, 0 errors)
  Brand           ⚠️  (confidence: low — only homepage ingested)
  Knowledge Base  ✅  (confidence: medium)
  Workflows       ❌  (no artifacts in _raw/artifacts/)
  Source of Truth ❌  (not generated yet)

  Open TODOs: 14

  👉 Suggested next: /workflows (after adding Slack export)
```

---

### Step 4 — Hand off to the client's team

When you're happy with `client/source-of-truth/`:

1. On GitHub: **Settings → Collaborators → Add people** (the client's team).
2. Share the link to `client/source-of-truth/README.md`.
3. Tell them: **"This is yours now. Edit freely. The pipeline won't overwrite it."**

Optionally, copy `client/source-of-truth/*.md` into their Notion, Confluence,
or wherever they actually live.

---

## 🆘 When things break

| Symptom | Probable fix |
|---|---|
| `/onboard` says *"client.config.yml is incomplete"* | Fill in `client.name` and `client.slug`. |
| Scraper returns empty pages | The site is JS-heavy. Export pages manually into `client/_raw/docs/inbox/`. |
| Brand guide says `confidence: low` everywhere | Only scraped one page. Add more URLs in `client.config.yml` → `sources.websites`. |
| Workflow mapper says "no artifacts" | Drop Slack/ticket exports into `client/_raw/artifacts/inbox/` then re-run `/workflows`. |
| A stage looks hallucinated | Search for `TODO: needs input` in `client/`. Real gaps are marked; fabrications are a bug — tell Claude. |
| I edited `client/brand/` and it got wiped | That's expected — `/brand` regenerates. Move refinements into `client/source-of-truth/`, which is never overwritten. |

---

## ⚡ Cheat sheet

### Commands

| Command | What it does | When to use |
|---|---|---|
| `/onboard` | Full pipeline with gates | Start here for every new client |
| `/ingest` | Scrape sources only | Sources changed |
| `/brand` | Brand guide only | Re-run after adding brand assets |
| `/kb` | Knowledge base only | Re-run after adding docs |
| `/workflows` | Workflows only | Re-run after adding artifacts |
| `/status` | Progress dashboard | Check progress any time |

### Paths

| Path | What's there |
|---|---|
| `client.config.yml` | ⭐ The one file you edit per client |
| `client/_raw/docs/inbox/` | Drop PDFs/DOCX here before `/ingest` |
| `client/_raw/artifacts/inbox/` | Drop Slack/ticket exports here |
| `client/source-of-truth/README.md` | The thing you hand off |

### Shell

```bash
# First time using the template locally (alternative to GitHub's "Use this template")
./scripts/bootstrap.sh acme-corp

# Pull latest engine improvements into an existing client repo
./scripts/update-engine.sh
```

---

## 🔄 Keeping it fresh across many clients

The template improves over time. Existing client repos don't auto-update —
you pull engine changes on demand:

```bash
cd ~/work/acme-onboarding
./scripts/update-engine.sh
```

That script pulls the latest `.claude/`, `templates/`, and `scripts/` from
the template repo. It **never touches** `client/` or `client.config.yml`.

After it runs, you'll see changes with `git status`. Review, commit, done.

---

## ❓ FAQ

**Q: Do I need to know Claude Code deeply to use this?**
A: No. If you can edit a YAML file and type `/onboard`, you're 95% done.

**Q: What if the client doesn't want their stuff on GitHub?**
A: Keep the repo private with only your team, then export
`client/source-of-truth/` to wherever they prefer (Notion, Confluence, etc.).
The GitHub repo is just where the pipeline runs.

**Q: Can two people work on the same client repo at once?**
A: Yes. It's a normal git repo — branch, PR, merge as usual.

**Q: The pipeline overwrote my brand edits!**
A: `/brand`, `/kb`, and `/workflows` regenerate their outputs. Preserve
refinements by moving them into `client/source-of-truth/` (never overwritten).

**Q: What if I want to add a new type of output, like a pricing guide?**
A: Add an agent in `.claude/agents/`, add a command in `.claude/commands/`,
add a template in `templates/`. The `CLAUDE.md` contract shows the shape.
