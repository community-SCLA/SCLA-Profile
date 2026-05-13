# SCLA-Profile Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate SCLA-Profile from a generic template skeleton to a fully SCLA-native knowledge base — merging all existing pipeline data, renaming all references, restructuring directories, and implementing four architectural improvements (C1–C3, C5).

**Architecture:** Merge the unmerged `onboard-flow` branch to recover April 2026 pipeline work, restructure `client/` into the SCLA-native `scla/` layout, update all agents/commands/hooks to use new paths and read from `source-of-truth/` before generating output, then run Stage 5 to produce the initial `source-of-truth/` files.

**Tech Stack:** Bash, Markdown, YAML, Claude Code agents/hooks, Git

---

## File Map

**Create:**
- `scla/` — new top-level knowledge base directory
- `scla/_raw/{web,docs,artifacts,assets}/` — ingestion cache (migrated from `client/_raw/`)
- `scla/{brand,programs,members,operations,partnerships,knowledge-base}/` — output dirs
- `scla/source-of-truth/{mission,program-names,voice-decisions,decisions-log,team-handbook}.md` — stub files
- `scla/projects/{grants,campaigns,programs,content}/.gitkeep` — project work dirs
- `scla.config.yml` — renamed from `client.config.yml`

**Modify:**
- `.claude/hooks/stamp-frontmatter.sh` — upgrade to validator; update path guard `client/` → `scla/`
- `.claude/agents/ingestor.md` — update all `client/` paths
- `.claude/agents/brand-analyst.md` — update paths + add source-of-truth reads
- `.claude/agents/knowledge-architect.md` — update paths + source-of-truth reads + new output dirs
- `.claude/agents/workflow-mapper.md` — update paths + source-of-truth reads + write to `operations/`
- `.claude/agents/source-of-truth-curator.md` — update paths + C2 write-protection + C5 KB-delta merge
- `.claude/commands/{onboard,ingest,brand,kb,workflows,status}.md` — update all `client/` path references
- `templates/{brand-guide,workflow,kb-entry,automation-opportunity}.md` — rename "client" → "SCLA"
- `CLAUDE.md` — update all `client/` directory references
- `README.md` — update all `client/` references
- `sync.sh` — update any `client/` references

**Delete:**
- `client/` — entire directory (after migration complete)
- `client.config.yml` — replaced by `scla.config.yml`

---

## Task 1: Merge onboard-flow Branch

**Files:** git only

- [ ] **Step 1: Fetch and inspect the branch**

```bash
git fetch origin
git log --oneline origin/claude/onboard-flow-WoTCI
```

Expected: 9 commits including "Stage 4: map workflows", "Stage 2+3: brand guide + knowledge base scaffolds", "Stage 1 ingest".

- [ ] **Step 2: Merge the branch**

```bash
git merge origin/claude/onboard-flow-WoTCI --no-ff -m "chore: merge onboard-flow — recover April 2026 pipeline data"
```

Expected: merge completes with no conflicts (main has no `client/` content).

- [ ] **Step 3: Verify migrated content exists**

```bash
find client/_raw/artifacts -name "*.md" | sort
find client/brand -name "*.md" | sort
find client/workflows -name "*.md" | sort
```

Expected: 5 meeting note/stakeholder files in `artifacts/`, 4 brand files, 5 workflow files.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: merge onboard-flow pipeline data into main"
```

---

## Task 2: Create SCLA Directory Structure

**Files:**
- Create: all `scla/` directories and stub files

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p scla/_raw/{web,docs,artifacts/inbox,assets}
mkdir -p scla/{brand,programs,members,operations,partnerships,knowledge-base}
mkdir -p scla/source-of-truth
mkdir -p scla/projects/{grants,campaigns,programs,content}
```

- [ ] **Step 2: Add .gitkeep to empty leaf directories**

```bash
touch scla/projects/grants/.gitkeep
touch scla/projects/campaigns/.gitkeep
touch scla/projects/programs/.gitkeep
touch scla/projects/content/.gitkeep
touch scla/partnerships/.gitkeep
```

- [ ] **Step 3: Create source-of-truth stub files**

Create `scla/source-of-truth/mission.md`:
```markdown
---
source: manual
generated_by: human
last_updated: 2026-05-10
confidence: high
---

# SCLA Mission

**Mission:** TODO: needs input — write the official SCLA mission statement here.

**Vision:** TODO: needs input — write the vision statement here.

**Core values:** TODO: needs input — list SCLA's stated core values.

**What success looks like this quarter (Q2 2026):**
1. Weekly News ships consistently — 4+ consecutive weeks without Sean/Shawn on the critical path
2. Member Journey funnel is documented and lives in Community Drive, reviewed by Kierra, presented to Amy
3. Community Google Drive is the single source of truth — every active project document lives there
4. Focus Modes content is on track for August 1 — Anushka's content build at least 50% complete
```

Create `scla/source-of-truth/program-names.md`:
```markdown
---
source: manual
generated_by: human
last_updated: 2026-05-10
confidence: high
---

# Canonical SCLA Program Names

Use these exact names in all generated content. Do not paraphrase or invent variants.

| Canonical Name | Description | Do Not Use |
|---|---|---|
| Career Readiness Certification | The flagship certification program | "career cert", "CRC" |
| ISPI Strengths Assessment | Strengths assessment tool | "personality test", "ISPI assessment" |
| Career Hub | AI-powered career guidance platform | "career portal", "AI hub" |
| CEO Speaker Series | Executive speaker programming | "speaker series", "CEO talks" |
| Focus Modes | Structured focus content program (Aug 1 launch) | "focus content" |
| Micro-Internships | Short-form work experience program | "micro internships" |

TODO: needs input — review and add any programs not listed here.
```

Create `scla/source-of-truth/voice-decisions.md`:
```markdown
---
source: manual
generated_by: human
last_updated: 2026-05-10
confidence: medium
---

# SCLA Voice Decisions

Authoritative decisions about how SCLA communicates. Brand-analyst reads this before extracting from web.

## Confirmed decisions
TODO: needs input — Amy or Kierra should document 3–5 "we always do this / we never do this" voice rules here.

## Examples of on-brand copy
TODO: needs input — paste 2–3 real SCLA sentences that exemplify the voice.
```

Create `scla/source-of-truth/decisions-log.md`:
```markdown
---
source: manual
generated_by: human
last_updated: 2026-05-10
confidence: high
---

# SCLA Decisions Log

Running log of notable team decisions. Append new entries at the top.

## 2026-05-10 — SCLA-Profile redesigned as SCLA-native knowledge base
**Decision:** Migrated from generic template to SCLA-native structure. Renamed all `client/` references to `scla/`. Separated programs, members, operations, partnerships into first-class directories.
**Rationale:** Generic template naming created confusion; SCLA-specific structure makes the knowledge base faster to navigate and easier for agents to target.
**Owner:** Kierra Woekel
```

Create `scla/source-of-truth/team-handbook.md`:
```markdown
---
source: manual
generated_by: human
last_updated: 2026-05-10
confidence: medium
---

# SCLA Community Team Handbook

## The team
Ten people driving member engagement, onboarding, content, and events. See `scla/operations/` for full team roster and role breakdown.

## Tools
- **Slack** — internal comms
- **Gmail** — external comms
- **Google Drive** — all documents (source of truth for finished work)
- **Zoom + Gemini** — meetings with auto-notes
- **Canva** — Team Projects tracker
- **Claude Pro** — AI assistance

## Meeting cadence
Community Team Mondays — every Monday at 4:00 PM CDT, ~60 min via Zoom. Amy sets the agenda. Starts with a warm-up (music, personal check-ins) — this is intentional.

## Document home
Community Google Drive. When a doc is added, ping Kierra in Slack so she can ingest it into Claude.

## How to update this handbook
Edit this file directly. It is human-maintained and will not be auto-overwritten by the pipeline.
```

- [ ] **Step 4: Commit**

```bash
git add scla/
git commit -m "feat: scaffold SCLA-native directory structure with source-of-truth stubs"
```

---

## Task 3: Migrate client/ Content into scla/

**Files:**
- Migrate: `client/_raw/**` → `scla/_raw/**`
- Migrate: `client/brand/**` → `scla/brand/**`
- Migrate: `client/workflows/**` → `scla/operations/**`
- Migrate: `client/knowledge-base/**` → split across `scla/knowledge-base/`, `scla/programs/`, `scla/members/`

- [ ] **Step 1: Migrate raw data**

```bash
cp -r client/_raw/web/. scla/_raw/web/
cp -r client/_raw/artifacts/. scla/_raw/artifacts/
cp -r client/_raw/assets/. scla/_raw/assets/
cp -r client/_raw/docs/. scla/_raw/docs/
cp client/_raw/MANIFEST.md scla/_raw/MANIFEST.md
cp client/_raw/INGEST_ERRORS.md scla/_raw/INGEST_ERRORS.md 2>/dev/null || true
```

- [ ] **Step 2: Migrate brand output**

```bash
cp client/brand/brand-guide.md scla/brand/
cp client/brand/voice-and-tone.md scla/brand/
cp client/brand/visual-identity.md scla/brand/
cp client/brand/TODOS.md scla/brand/
cp -r client/brand/assets/. scla/brand/assets/ 2>/dev/null || true
```

- [ ] **Step 3: Migrate workflows to operations/**

```bash
cp client/workflows/current-state.md scla/operations/
cp client/workflows/automation-opportunities.md scla/operations/
cp client/workflows/pain-points.md scla/operations/
cp client/workflows/drive-search-queries.md scla/operations/
```

- [ ] **Step 4: Migrate kb-deltas to _raw/ (for curator to process in Stage 5)**

```bash
cp client/workflows/kb-deltas.md scla/_raw/kb-deltas.md
```

- [ ] **Step 5: Migrate knowledge-base — split by content type**

General knowledge (FAQs, glossary, index) → `scla/knowledge-base/`:
```bash
cp client/knowledge-base/faqs.md scla/knowledge-base/
cp client/knowledge-base/glossary.md scla/knowledge-base/
cp client/knowledge-base/index.md scla/knowledge-base/
cp client/knowledge-base/TODOS.md scla/knowledge-base/
```

People → `scla/operations/` (team structure belongs there):
```bash
cp client/knowledge-base/people.md scla/operations/team-roster.md
```

Programs and services → `scla/programs/`:
```bash
cp client/knowledge-base/products-services.md scla/programs/programs-overview.md
```

- [ ] **Step 6: Update path references inside migrated files**

In all migrated markdown files, replace any remaining `client/` path references with `scla/`:

```bash
find scla/ -name "*.md" -exec sed -i '' 's|client/|scla/|g' {} +
```

- [ ] **Step 7: Verify file counts**

```bash
find scla/_raw/artifacts -name "*.md" | wc -l   # expect 5
find scla/brand -name "*.md" | wc -l             # expect 4
find scla/operations -name "*.md" | wc -l        # expect 6 (5 workflows + team-roster)
find scla/knowledge-base -name "*.md" | wc -l    # expect 4
find scla/programs -name "*.md" | wc -l          # expect 1
```

- [ ] **Step 8: Commit**

```bash
git add scla/
git commit -m "feat: migrate client/ pipeline output into scla/ SCLA-native structure"
```

---

## Task 4: Rename Config and Update Root Files

**Files:**
- Create: `scla.config.yml`
- Delete: `client.config.yml`
- Modify: `CLAUDE.md`, `README.md`, `sync.sh`

- [ ] **Step 1: Rename client.config.yml → scla.config.yml**

Copy and update all `client/` references inside:
```bash
cp client.config.yml scla.config.yml
```

Open `scla.config.yml` and make these edits:
- Line 1: Change `client:` → `scla:` (the top-level key)
- All `client/_raw/` path references → `scla/_raw/`
- The `docs.path: "inbox/"` should stay as-is (relative path inside `_raw/docs/`)

Final `scla.config.yml`:
```yaml
scla:
  name: "The Society for Collegiate Leadership & Achievement"
  slug: "the-scla"
  industry: "higher education / education services industry"
  primary_contact:
    name: "Kierra Woekel"
    email: "community@thescla.org"
    role: "Tech and Organization Lead"
    website: "https://www.thescla.org"

sources:
  websites:
    - url: "https://www.thescla.org"
      crawl_depth: 2
      include_assets: true

  docs:
    - path: "inbox/"
    - url: ""

  repos: []

  drives: []

  artifacts: []

targets:
  knowledge_base: true
  brand_guide: true
  workflow_map: true
  automation_opportunities: true
  source_of_truth: true

collab:
  canonical_home: ""
  channels:
    - name: "slack"
      handle: ""

gates:
  ingest: medium
  brand: medium
  knowledge_base: medium
  workflows: low
  source_of_truth: low
```

- [ ] **Step 2: Update CLAUDE.md**

Open `CLAUDE.md`. Replace every occurrence of `client/` with `scla/` and `client.config.yml` with `scla.config.yml`. The pipeline table in the middle of the file should update to:

```markdown
| Stage | Agent | Reads | Writes |
|---|---|---|---|
| 1. Ingest | `ingestor` | `scla.config.yml` | `scla/_raw/**` |
| 2. Brand | `brand-analyst` | `scla/_raw/web/`, `scla/_raw/assets/` | `scla/brand/**` |
| 3. Knowledge | `knowledge-architect` | `scla/_raw/docs/`, `scla/_raw/web/` | `scla/knowledge-base/**`, `scla/programs/**`, `scla/members/**`, `scla/partnerships/**` |
| 4. Workflows | `workflow-mapper` | `scla/_raw/artifacts/`, `scla/_raw/docs/` | `scla/operations/**` |
| 5. Curate | `source-of-truth-curator` | all of `scla/**` | `scla/source-of-truth/**` |
```

Also update the directory cheat sheet section at the bottom to match the new `scla/` structure and directories.

- [ ] **Step 3: Update README.md and sync.sh**

```bash
sed -i '' 's|client/|scla/|g' README.md
sed -i '' 's|client.config.yml|scla.config.yml|g' README.md
grep -n "client" sync.sh && sed -i '' 's|client/|scla/|g' sync.sh || true
```

- [ ] **Step 4: Commit**

```bash
git add scla.config.yml CLAUDE.md README.md sync.sh
git commit -m "chore: rename client.config.yml to scla.config.yml, update root file references"
```

---

## Task 5: Update Agent Definitions

**Files:**
- Modify: `.claude/agents/ingestor.md`
- Modify: `.claude/agents/brand-analyst.md`
- Modify: `.claude/agents/knowledge-architect.md`
- Modify: `.claude/agents/workflow-mapper.md`

- [ ] **Step 1: Update ingestor.md**

Replace the entire file with:

```markdown
---
name: ingestor
description: Scrapes every source listed in scla.config.yml into scla/_raw/. Use PROACTIVELY whenever sources change or SCLA content needs refreshing.
tools: Read, Write, Bash, WebFetch, WebSearch, Glob
model: sonnet
---

# Ingestor Agent

You are the **first stage** of the pipeline. Your only job is to turn what's
listed in `scla.config.yml` into faithful, dated snapshots inside `scla/_raw/`.

## Contract

- **Read**: `scla.config.yml`
- **Write**: `scla/_raw/web/`, `scla/_raw/docs/`, `scla/_raw/assets/`, `scla/_raw/artifacts/`
- **Never**: edit, summarize, or paraphrase the source material at this stage. Raw means raw.

## Process

1. Parse `scla.config.yml`. For each section, run the matching skill:
   - `sources.websites[]` → `.claude/skills/web-scraper`
   - `sources.docs[]` → `.claude/skills/doc-ingester`
   - `sources.artifacts[]` → copy into `scla/_raw/artifacts/` preserving filenames
   - `sources.drives[]` → read from `export_path`, unzip into `scla/_raw/docs/`

2. For every file you write, append a one-line entry to `scla/_raw/MANIFEST.md`:
   ```
   | YYYY-MM-DD | <source url or path> | <local path in _raw/> | <bytes> |
   ```

3. If a source fails (403, missing file, auth required), log it to
   `scla/_raw/INGEST_ERRORS.md` with the error and what the human needs to do.
   Never fail silently.

4. When done, print a summary:
   ```
   Ingested: X websites, Y docs, Z assets, N artifacts
   Errors:   M (see scla/_raw/INGEST_ERRORS.md)
   Next:     /brand or /kb
   ```

## Rules

- **One file per source.** Don't concatenate. Preserve the original structure.
- **Snapshot, don't re-format.** Convert HTML→markdown but keep the text verbatim.
- **Attribution in frontmatter.** Every scraped file gets:
  ```yaml
  ---
  source_url: <original>
  fetched_at: <ISO timestamp>
  ingestor_skill: <which skill was used>
  ---
  ```
- **Respect `crawl_depth` and `include_assets`.**
- **Do not write outside `scla/_raw/`.** That's for downstream agents.
```

- [ ] **Step 2: Update brand-analyst.md**

Replace frontmatter description:
```
description: Extracts voice, tone, and visual identity from scraped web pages and assets. Writes a brand guide the SCLA team can actually use. Use after ingestion.
```

Replace the Contract section:
```markdown
## Contract

- **Read first (source-of-truth)**: `scla/source-of-truth/mission.md`, `scla/source-of-truth/voice-decisions.md` — check these before generating any brand output. Canonical facts here override anything found in `_raw/`.
- **Read**: `scla/_raw/web/`, `scla/_raw/assets/`, any brand PDFs in `scla/_raw/docs/`
- **Write**: `scla/brand/brand-guide.md`, `scla/brand/voice-and-tone.md`,
  `scla/brand/visual-identity.md`, `scla/brand/assets/index.md`
- **Template**: `templates/brand-guide.md`
- **Write outside `scla/brand/`**: never.
```

Replace all remaining `client/` path references with `scla/`. Replace "the client's team" with "the SCLA team".

- [ ] **Step 3: Update knowledge-architect.md**

Replace frontmatter description:
```
description: Turns scraped docs and web pages into a navigable SCLA internal wiki. Writes to knowledge-base/, programs/, members/, and partnerships/. Use after ingestion.
```

Replace the Contract section:
```markdown
## Contract

- **Read first (source-of-truth)**: `scla/source-of-truth/program-names.md`, `scla/source-of-truth/decisions-log.md` — use canonical program names from `program-names.md` in all entries. Check `decisions-log.md` for org decisions that should be reflected in the wiki.
- **Read**: `scla/_raw/docs/`, `scla/_raw/web/`
- **Write**: `scla/knowledge-base/**` (history, FAQs, glossary), `scla/programs/**` (one file per program), `scla/members/**` (member journey, onboarding, pledge process), `scla/partnerships/**` (partner profiles and relationship data)
- **Template**: `templates/kb-entry.md`
- **One agent, multi-directory exception**: knowledge-architect is explicitly granted write access to knowledge-base/, programs/, members/, and partnerships/ — all are knowledge outputs from the same agent.
```

Replace all remaining `client/` path references with `scla/`. Replace "the client" / "the company" with "SCLA". Replace "customers" with "members".

- [ ] **Step 4: Update workflow-mapper.md**

Replace frontmatter description:
```
description: Maps SCLA's real-world workflows from artifacts (meeting notes, Slack exports) and surfaces automation opportunities. Writes to operations/. Use after ingestion.
```

Replace the Contract section:
```markdown
## Contract

- **Read first (source-of-truth)**: `scla/source-of-truth/decisions-log.md` — check for org decisions that explain current workflow choices before flagging them as pain points.
- **Read**: `scla/_raw/artifacts/`, `scla/_raw/docs/` (for SOPs), `scla/operations/team-roster.md` (if present)
- **Write**: `scla/operations/current-state.md`, `scla/operations/automation-opportunities.md`, `scla/operations/ship-fast-playbook.md`
- **KB gaps**: write to `scla/_raw/kb-deltas.md` (the source-of-truth-curator will merge these into `knowledge-base/` in Stage 5)
- **Templates**: `templates/workflow.md`, `templates/automation-opportunity.md`
```

Replace all remaining `client/` path references with `scla/`. Replace "the client's team" with "the SCLA team".

- [ ] **Step 5: Commit**

```bash
git add .claude/agents/
git commit -m "feat: update agent definitions to scla/ paths and add source-of-truth reads (C3)"
```

---

## Task 6: Update source-of-truth-curator Agent (C2 + C5)

**Files:**
- Modify: `.claude/agents/source-of-truth-curator.md`

- [ ] **Step 1: Rewrite source-of-truth-curator.md**

Replace the entire file content with:

```markdown
---
name: source-of-truth-curator
description: Stitches brand, knowledge-base, programs, members, operations, and partnerships into a living source of truth the SCLA team uses day-to-day. Run LAST. On re-runs, proposes changes instead of overwriting.
tools: Read, Write, Edit, Glob, Grep
model: sonnet
---

# Source-of-Truth Curator Agent

You are the final stage. All prior agents have produced their slice of the picture.
Your job is two things: knit them into something the SCLA team will actually open
every morning, and merge any KB gaps surfaced by the workflow-mapper.

## Contract

- **Read**: `scla/source-of-truth/` (check all existing files first), all of `scla/brand/`,
  `scla/knowledge-base/`, `scla/programs/`, `scla/members/`, `scla/operations/`, `scla/partnerships/`
- **Write**: `scla/source-of-truth/**` (merge-only on re-runs — see Write Protection below)
- **Merge**: `scla/_raw/kb-deltas.md` → `scla/knowledge-base/` (see KB-Delta Merge below)

## Write Protection (C2)

**Before writing anything to `scla/source-of-truth/`:**

1. Check whether each target file already has human-written content (not just the stub template).
2. **If the file has been edited beyond the stub** (look for content after TODO markers being filled in, or `last_updated` having been changed):
   - Do NOT overwrite it.
   - Instead, write your proposed additions/changes to `scla/source-of-truth/PROPOSED_CHANGES.md`.
   - Format each proposal as:
     ```
     ## [filename] — proposed change
     **What:** [what you want to add or change]
     **Why:** [which source in scla/ supports this]
     **Action required:** Review and apply manually if correct.
     ```
3. **If the file is still a stub** (all TODOs still present, `last_updated` is still `2026-05-10`):
   - Write to it normally. It has not been human-edited yet.

## What to produce (initial run)

Supplement the stub files in `scla/source-of-truth/` with content synthesized from pipeline outputs:

| File | Add from pipeline |
|---|---|
| `mission.md` | Enrich with mission/vision language found in `scla/_raw/web/` or `scla/brand/` |
| `program-names.md` | Add any program names from `scla/programs/` not already listed |
| `voice-decisions.md` | Pull confirmed voice patterns from `scla/brand/voice-and-tone.md` |
| `decisions-log.md` | Append entries for any significant patterns found across pipeline outputs |
| `team-handbook.md` | Add team structure details from `scla/operations/team-roster.md` |

Also produce:
- `scla/source-of-truth/onboarding.md` — first-week checklist for a new SCLA team member, synthesized from knowledge-base + operations
- `scla/source-of-truth/HANDOFF.md` — what's complete, what still says `TODO: needs input`, suggested first 3 edits for the team

## KB-Delta Merge (C5)

After writing to `scla/source-of-truth/`, check for `scla/_raw/kb-deltas.md`.

If it exists:
1. Read every entry in `kb-deltas.md`.
2. For each entry, find the correct file in `scla/knowledge-base/`, `scla/programs/`, `scla/members/`, or `scla/partnerships/` and add the entry.
3. If no matching file exists, create one using `templates/kb-entry.md`.
4. After all entries are merged, delete `scla/_raw/kb-deltas.md`.
5. Log what you merged in `scla/source-of-truth/HANDOFF.md`.

## Process

1. Read `scla/source-of-truth/` first to understand what's already settled.
2. Skim everything produced by other agents. Build an outline before writing.
3. Cross-link relentlessly — every program name links to its `scla/programs/` file.
4. Write for humans, not agents. Short sentences, active voice, SCLA brand voice.
5. Top each new file with: `> This page is the team's — edit it freely. Pipeline-assisted; human-maintained going forward.`
6. Run KB-delta merge last.

## Automation opportunity hook

If `scla/operations/automation-opportunities.md` contains P0 or P1 items,
surface the top 3 in `scla/source-of-truth/HANDOFF.md` under a **"Ship Faster"** section.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/source-of-truth-curator.md
git commit -m "feat: implement C2 write-protection and C5 KB-delta merge in source-of-truth-curator"
```

---

## Task 7: Update Commands and Templates

**Files:**
- Modify: `.claude/commands/{onboard,ingest,brand,kb,workflows,status}.md`
- Modify: `templates/{brand-guide,workflow,kb-entry,automation-opportunity}.md`

- [ ] **Step 1: Update all commands in batch**

```bash
find .claude/commands/ -name "*.md" -exec sed -i '' \
  -e 's|client/|scla/|g' \
  -e 's|client\.config\.yml|scla.config.yml|g' \
  -e 's|the client|SCLA|g' \
  -e "s|client's team|SCLA team|g" \
  {} +
```

- [ ] **Step 2: Update all templates in batch**

```bash
find templates/ -name "*.md" -exec sed -i '' \
  -e 's|client/|scla/|g' \
  -e 's|the client|SCLA|g' \
  -e "s|client's|SCLA's|g" \
  -e 's|customers|members|g' \
  {} +
```

- [ ] **Step 3: Verify no "client" references remain in commands/templates**

```bash
grep -rn "client" .claude/commands/ templates/
```

Expected: zero matches (or only legitimate uses of the word "client" in non-path context — review manually).

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/ templates/
git commit -m "chore: update commands and templates — client → SCLA, customers → members"
```

---

## Task 8: Upgrade Frontmatter Hook (C1)

**Files:**
- Modify: `.claude/hooks/stamp-frontmatter.sh`

- [ ] **Step 1: Replace stamp-frontmatter.sh with validator version**

Write the following to `.claude/hooks/stamp-frontmatter.sh`:

```bash
#!/usr/bin/env bash
# stamp-frontmatter.sh
# C1: Validates that every markdown file written to scla/ (excluding _raw/)
# has fully-filled frontmatter. Injects stubs if missing; warns loudly if
# required fields contain placeholder values.
#
# Claude Code passes a JSON payload on stdin describing the tool call.

set -euo pipefail

payload="$(cat || true)"
[[ -z "$payload" ]] && exit 0

file=""
if command -v jq >/dev/null 2>&1; then
  file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty')"
else
  file="$(printf '%s' "$payload" \
    | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]+"' \
    | head -n1 \
    | sed -E 's/.*"file_path"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')"
fi

[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0
[[ "$file" != *scla/* ]] && exit 0
[[ "$file" != *.md ]] && exit 0
[[ "$file" == *_raw/* ]] && exit 0
[[ "$file" == *source-of-truth/PROPOSED_CHANGES* ]] && exit 0

today="$(date +%Y-%m-%d)"

# If no frontmatter at all — inject stubs
if ! head -1 "$file" | grep -q '^---$'; then
  tmp="$(mktemp)"
  {
    echo "---"
    echo "source: TODO"
    echo "generated_by: unknown"
    echo "last_updated: ${today}"
    echo "confidence: low"
    echo "---"
    echo ""
    cat "$file"
  } > "$tmp"
  mv "$tmp" "$file"
  echo "⚠️  FRONTMATTER: Injected stub frontmatter into ${file}. Fill in source, generated_by, and confidence before committing." >&2
  exit 0
fi

# Frontmatter exists — validate required fields are not placeholders
has_todo_source=false
has_unknown_generated_by=false

if grep -q '^source: TODO' "$file"; then
  has_todo_source=true
fi
if grep -q '^generated_by: unknown' "$file"; then
  has_unknown_generated_by=true
fi

if $has_todo_source || $has_unknown_generated_by; then
  echo "" >&2
  echo "🚫 FRONTMATTER VALIDATION FAILED: ${file}" >&2
  echo "   The following required fields are still placeholders:" >&2
  $has_todo_source && echo "   - source: TODO  →  replace with the source URL or _raw/ path" >&2
  $has_unknown_generated_by && echo "   - generated_by: unknown  →  replace with the agent name (e.g. brand-analyst)" >&2
  echo "   Fix these before committing." >&2
  echo "" >&2
fi
```

- [ ] **Step 2: Make the hook executable**

```bash
chmod +x .claude/hooks/stamp-frontmatter.sh
```

- [ ] **Step 3: Test the hook manually**

Create a test file and verify behavior:
```bash
echo "# Test" > /tmp/test-scla.md
# Simulate a file inside scla/ (hook reads path from stdin payload)
echo '{"tool_input": {"file_path": "/Users/kierrawoekel/Documents/SCLA/SCLA-Profile/scla/brand/test.md"}}' \
  | bash .claude/hooks/stamp-frontmatter.sh
```
Expected: exits silently (file path not a real file — hook exits on `[[ ! -f "$file" ]]`).

Verify the path guard works for the `scla/` check:
```bash
grep -n "scla/" .claude/hooks/stamp-frontmatter.sh
```
Expected: line with `[[ "$file" != *scla/* ]]` present.

- [ ] **Step 4: Commit**

```bash
git add .claude/hooks/stamp-frontmatter.sh
git commit -m "feat: upgrade frontmatter hook to validator — warn on TODO/unknown placeholders (C1)"
```

---

## Task 9: Delete client/ Directory and client.config.yml

**Files:**
- Delete: `client/` (entire tree)
- Delete: `client.config.yml`

- [ ] **Step 1: Verify all content has been migrated**

```bash
# Every file in client/ should have a counterpart in scla/
diff <(find client/ -name "*.md" | sed 's|client/||' | sort) \
     <(find scla/ -name "*.md" | sed 's|scla/||' | sort)
```

Expected differences (all intentional — do not treat as errors):
- `workflows/*.md` → `operations/*.md` (directory renamed)
- `knowledge-base/people.md` → `operations/team-roster.md` (moved to operations)
- `knowledge-base/products-services.md` → `programs/programs-overview.md` (moved to programs)
- `_raw/kb-deltas.md` exists in scla/ but not client/ (moved for curator processing)
- `source-of-truth/*.md` stubs exist in scla/ but not client/ (created in Task 2)
- `projects/**/.gitkeep` entries exist in scla/ but not client/ (new directories)

Any other diff entries are unexpected — investigate before proceeding.

- [ ] **Step 2: Remove client/ and client.config.yml**

```bash
rm -rf client/
rm -f client.config.yml
```

- [ ] **Step 3: Verify no remaining client/ path references in tracked files**

```bash
grep -rn "client/" .claude/ templates/ CLAUDE.md README.md scla.config.yml 2>/dev/null | grep -v ".git"
```

Expected: zero matches.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove client/ directory and client.config.yml — migration complete"
```

---

## Task 10: Run Stage 5 — Source-of-Truth Curator

**Files:**
- Produces: `scla/source-of-truth/onboarding.md`, `scla/source-of-truth/HANDOFF.md`, updates to stub files, `kb-deltas.md` merged into knowledge-base/

- [ ] **Step 1: Verify pipeline input is present**

```bash
find scla/_raw/artifacts -name "*.md" | sort    # expect 5 meeting note files
find scla/brand -name "*.md" | sort             # expect 4 brand files
find scla/operations -name "*.md" | sort        # expect 6 files
find scla/knowledge-base -name "*.md" | sort    # expect 4 files
find scla/programs -name "*.md" | sort          # expect 1 file
ls scla/_raw/kb-deltas.md                       # expect file exists
```

- [ ] **Step 2: Run the source-of-truth-curator agent**

In a new Claude Code session (to keep context clean), invoke:
```
/source-of-truth-curator
```
Or instruct Claude: "Run the source-of-truth-curator agent against the scla/ directory."

The agent will:
1. Read all existing `source-of-truth/` stub files
2. Supplement stubs with content from pipeline outputs
3. Create `onboarding.md` and `HANDOFF.md`
4. Merge `scla/_raw/kb-deltas.md` into `scla/knowledge-base/`
5. Delete `kb-deltas.md`

- [ ] **Step 3: Verify outputs**

```bash
ls scla/source-of-truth/
# Expected: mission.md, program-names.md, voice-decisions.md, decisions-log.md,
#           team-handbook.md, onboarding.md, HANDOFF.md
# Optional: PROPOSED_CHANGES.md (only if curator detected human edits)

ls scla/_raw/kb-deltas.md 2>/dev/null && echo "ERROR: kb-deltas.md was not deleted" || echo "OK: kb-deltas.md merged and deleted"
```

- [ ] **Step 4: Review HANDOFF.md**

Read `scla/source-of-truth/HANDOFF.md`. It should list:
- What was completed
- Remaining `TODO: needs input` items for the team to fill in
- Top 3 automation opportunities from `scla/operations/automation-opportunities.md`

- [ ] **Step 5: Commit**

```bash
git add scla/
git commit -m "feat: run Stage 5 — generate initial source-of-truth from pipeline outputs (C5 KB-delta merged)"
```

---

## Verification Checklist

After all tasks complete, verify the following:

```bash
# 1. No client/ references remain anywhere
grep -rn "client/" . --include="*.md" --include="*.yml" --include="*.sh" \
  --exclude-dir=".git" --exclude-dir="docs"

# 2. source-of-truth/ has all expected files
ls scla/source-of-truth/

# 3. Frontmatter hook guards scla/ (not client/)
grep "scla/" .claude/hooks/stamp-frontmatter.sh

# 4. All agents reference scla/ paths
grep -l "scla/" .claude/agents/*.md | wc -l   # expect 5

# 5. kb-deltas.md is gone (merged)
ls scla/_raw/kb-deltas.md 2>/dev/null || echo "OK"
```

---

## Out of Scope (Next Milestone)

- Hybrid update triggers — scheduled cron for website and Drive refresh
- Pipeline state tracking (C4) — `pipeline.state.json` + `/onboard --resume`
- New raw ingestion runs — re-scraping thescla.org, importing new Drive docs
- `projects/` content population — directories created, filling them is ongoing team work
