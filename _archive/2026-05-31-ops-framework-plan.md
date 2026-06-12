# SCLA KB Ops Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create three ops-framework artifacts — `connections.md` (system registry), `.claude/skills/kb-audit/SKILL.md` (KB health-check skill), and `EXPANSIONS.md` (discipline doc) — piloted in SCLA-Profile using SCLA-native naming.

**Architecture:** Three independent markdown files. `connections.md` and `EXPANSIONS.md` live at repo root; the `/kb-audit` skill lives at `.claude/skills/kb-audit/SKILL.md`. No code dependencies between them; the skill reads `connections.md` at runtime for the Reach score.

**Tech Stack:** Markdown, Claude Code skills (YAML frontmatter + markdown), Bash (git log for Maintenance freshness checks)

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `connections.md` | Dual-purpose system registry: org inventory + AI-reachability map |
| Create | `EXPANSIONS.md` | Discipline doc: what to add, when, and what not to add |
| Create | `.claude/skills/kb-audit/SKILL.md` | Read-only KB health-check skill, scores /100 across 4 dimensions |

---

### Task 1: Create `connections.md`

**Files:**
- Create: `connections.md`

- [ ] **Step 1: Write `connections.md`**

Create `/workspaces/SCLA-Profile/connections.md` with this exact content:

```markdown
# Connections

Registry of every system SCLA runs on. Two views in one document:
- **Team view:** What systems does SCLA operate?
- **AI view:** Which can Claude reach right now, and how?

Update this file whenever a new tool is wired. When adding a reachable tool, also save `references/{tool}-api.md` (endpoints, auth flow, common queries — researched once, referenced forever). `/kb-audit` checks for this.

| # | Domain | System | Purpose | Claude can reach? | Mechanism | Auth state | Last checked |
|---|---|---|---|---|---|---|---|
| 1 | Community Platform | SCLA website (custom channels) | Member-facing community hub | No | not connected | — | — |
| 2 | Communication | Slack | Internal team comms | Yes | mcp | active | 2026-05-31 |
| 2 | Communication | Gmail | External email + member messaging | Yes | mcp | active | 2026-05-31 |
| 3 | Content & Design | Canva | Design assets, team projects tracker | Yes | mcp | active | 2026-05-31 |
| 3 | Content & Design | Figma | UI and visual design mockups | Yes | mcp | active | 2026-05-31 |
| 4 | Knowledge / Files | Google Drive | Shared team docs, source material | Yes | mcp | active | 2026-05-31 |
| 4 | Knowledge / Files | Notion | Knowledge base, project documentation | Yes | mcp | active | 2026-05-31 |
| 5 | Task & Project Tracking | Notion | Work tracking and ownership | Yes | mcp | active | 2026-05-31 |
| 6 | Email & Member Outreach | Gmail | Broadcast email, member comms | Yes | mcp | active | 2026-05-31 |
| 6 | Email & Member Outreach | MJML dashboard (SCLA) | Custom email template system | No | not connected | — | — |
| 7 | Membership Tracking | (TBD) | Member sign-ups, engagement, quarterly/annual goals | No | not connected | — | — |

**Mechanism values:** `mcp` · `script` · `export` · `key+ref` · `not connected`
**Auth state values:** `active` · `needs-auth` · `expired` · `—`

## Notes
- Notion appears in both Knowledge/Files (domain 4) and Task & Project Tracking (domain 5) — one MCP, two use cases.
- Gmail appears in both Communication (domain 2) and Email & Member Outreach (domain 6) — one MCP, two use cases.
- MCP connections are configured at the claude.ai account level, not in local `.mcp.json`.
- Membership Tracking system is TBD — update this row when the tracking system is identified.
- When a tool moves from `not connected` to connected, create `references/{tool}-api.md`.
```

- [ ] **Step 2: Verify reachable system count**

Run:
```bash
grep -c "| Yes |" connections.md
```
Expected: `7`

- [ ] **Step 3: Verify not-connected row count**

Run:
```bash
grep "| No |" connections.md | wc -l
```
Expected: `3` (Community Platform, MJML dashboard, Membership Tracking)

- [ ] **Step 4: Commit**

```bash
git add connections.md
git commit -m "feat: add connections.md system registry (org inventory + AI-reachability)"
```

---

### Task 2: Create `EXPANSIONS.md`

**Files:**
- Create: `EXPANSIONS.md`

- [ ] **Step 1: Write `EXPANSIONS.md`**

Create `/workspaces/SCLA-Profile/EXPANSIONS.md` with this exact content:

```markdown
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
```

- [ ] **Step 2: Verify the two-yeses test is present**

Run:
```bash
grep "Two yeses" EXPANSIONS.md
```
Expected: `Two yeses → add it. One yes → wait.`

- [ ] **Step 3: Verify all three sections are present**

Run:
```bash
grep "^## " EXPANSIONS.md
```
Expected:
```
## What ships (don't remove)
## What to add as you grow
## What NOT to add
## The two-yeses test
```

- [ ] **Step 4: Commit**

```bash
git add EXPANSIONS.md
git commit -m "feat: add EXPANSIONS.md discipline doc (what to add, when, and what not to add)"
```

---

### Task 3: Create `.claude/skills/kb-audit/SKILL.md`

**Files:**
- Create: `.claude/skills/kb-audit/SKILL.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p .claude/skills/kb-audit
```

- [ ] **Step 2: Write the skill file**

Create `/workspaces/SCLA-Profile/.claude/skills/kb-audit/SKILL.md` with this exact content:

```markdown
---
name: kb-audit
description: Use when asked to audit the knowledge base, check KB health, score the repo, or run a structural review. Produces a four-dimension scoreboard (/100) and top-3 gap report. Run after first setup, then weekly. Read-only except for the optional audit save.
---

## What this skill does

Read-only structural health-check on the current Claude Code project. Scores four dimensions — Knowledge, Reach, Skills, Maintenance — out of 25 each (100 total). Surfaces the top 3 gaps ranked by leverage with concrete next steps.

Answers: "Is this KB built right?" Not: "What should we build next?"

First run establishes the baseline. Re-run weekly to watch the score climb.

## Today's date

Run `date +%Y-%m-%d` to get today's date for the report header.

## Scoring dimensions (25 pts each)

### Knowledge (25 pts) — "Does the KB know what it needs to know?"

| Criterion | Pts | How to detect |
|---|---|---|
| CLAUDE.md is substantive (>200 words) | 5 | Read CLAUDE.md and count words |
| `context/` has all three core files or equivalent | 5 | Glob `context/*.md` — expect me.md, goals.md, current-priorities.md or equivalent |
| Brand / voice is documented | 5 | Check `scla/brand/` or equivalent for ≥1 voice or tone file |
| Decisions log has ≥1 entry | 5 | Check `scla/source-of-truth/decisions-log.md` or any file matching `*decisions*` |
| No major TODO stubs in source-of-truth | 5 | Grep `TODO: needs input` in `scla/source-of-truth/` — deduct 1 pt per stub found, floor 0 |

### Reach (25 pts) — "What can Claude actually access live?"

Read `connections.md` at repo root. If missing, score Reach as 0 and flag with 4× leverage multiplier.

| Criterion | Pts | How to detect |
|---|---|---|
| Domain coverage | 10 | Count rows in connections.md where "Claude can reach?" = Yes. 1.4 pts each, round to nearest 0.5, cap 10. |
| Reference doc per connected tool | 5 | For each reachable tool, check for `references/{tool}-api.md`. −1 per missing. Floor 0. |
| Auth / pipeline freshness | 5 | Count rows where Auth state = `needs-auth` or `expired`. −1 each. Floor 0. |
| `connections.md` populated | 3 | 0 if missing; 1 if sparse (<3 rows filled); 2 if most rows filled; 3 if all rows filled |
| At least one writable connection | 2 | Any row where Mechanism ≠ `not connected` and system can write (send message, post update, create doc). 0 if all read-only. |

### Skills (25 pts) — "Are there reusable workflows installed?"

| Criterion | Pts | How to detect |
|---|---|---|
| 3+ skills installed | 10 | Count `.claude/skills/*/SKILL.md`. 10 if ≥3; 5 if 2; 0 if ≤1. |
| 1+ custom-built skill | 10 | Skill name not in canonical defaults list below. 10 if ≥1 custom skill found. |
| 1+ agent defined | 5 | Count `.claude/agents/*.md`. 5 if ≥1, else 0. |

Canonical defaults (don't count as custom): `onboard`, `audit`, `kb-audit`, `level-up`, `skill-creator`, `brainstorming`, `writing-plans`, `systematic-debugging`, `verification-before-completion`, `frontend-design`, `code-review`, `remember`, `update-config`, `executing-plans`, `subagent-driven-development`, `using-git-worktrees`, `finishing-a-development-branch`, `requesting-code-review`, `receiving-code-review`.

### Maintenance (25 pts) — "Is the KB actively tended?"

| Criterion | Pts | How to detect |
|---|---|---|
| Skills modified within 30 days | 10 | Run `git log --since=30.days --oneline -- .claude/skills/`. Any output = 10 pts. |
| Decisions log has entry within 30 days | 10 | Run `git log --since=30.days --oneline -- scla/source-of-truth/decisions-log.md`. Any output = 10 pts. If no git result, check most recent `## YYYY-MM-DD` heading in the file. |
| Templates folder populated | 5 | Glob `templates/*.md` — ≥1 file = 5 pts. |

## Execution

### Step 1: Discover project shape

Read these paths (targeted reads only — do not load `docs/_archive/`):
- `CLAUDE.md` — word count and identity check
- `context/` — list files
- `scla/brand/` — list files, look for voice or tone file
- `scla/source-of-truth/decisions-log.md` — first 20 lines to confirm entries exist
- `connections.md` — full read
- `.claude/skills/` — list subdirectories and read each SKILL.md frontmatter only
- `.claude/agents/` — list files (if directory exists)
- `templates/` — list files

### Step 2: Score each dimension

Apply criteria above. Keep a running tally per dimension. Note which criteria gained or lost points — you'll use this for the gap analysis.

### Step 3: Identify top 3 gaps by leverage

For each criterion that scored below its maximum:
- leverage = points_lost × multiplier

| Condition | Multiplier |
|---|---|
| `connections.md` missing entirely | 4× |
| CLAUDE.md missing or thin (<200 words) | 3× |
| ≤2 domains reachable | 3× |
| 0 skills installed | 2× |
| No decisions log entry within 30 days | 2× |
| All connections read-only | 2× |
| Connected tools missing reference docs | 1.5× |
| All others | 1× |

Sort by leverage descending. Take top 3. Write one concrete next-step for each:
- Missing `connections.md` → "Create `connections.md` at repo root using the schema in `docs/superpowers/specs/2026-05-31-ops-framework-design.md`."
- No reference doc for a connected tool → "Create `references/{tool}-api.md` documenting endpoints, auth flow, and common queries."
- No custom skill → "Create `.claude/skills/{name}/SKILL.md` with YAML frontmatter (name + description) and execution steps."
- No agent → "Create `.claude/agents/{name}.md` for a repeatable multi-step task."
- Stale decisions log → "Append a dated entry to `scla/source-of-truth/decisions-log.md`."
- No writable connection → "Configure write scope for an existing MCP (e.g. Slack send, Gmail draft, Notion create page)."

### Step 4: Print report

```
# KB Audit — {date}
**Score: {total}/100** ({stage})

Stage thresholds:
  0–39   → Stage 0: Foundation
  40–69  → Stage 1: Built
  70–89  → Stage 2: Compounding
  90–100 → Stage 3: Autonomous

## Scoreboard
Knowledge     {bar}  {n}/25  {label}
Reach         {bar}  {n}/25  {label}
Skills        {bar}  {n}/25  {label}
Maintenance   {bar}  {n}/25  {label}

(bar = ## per 5 pts; Strong ≥20 · Solid 15–19 · Thin 8–14 · Missing <8)

## Strengths
- {1–3 bullets from highest-scoring criteria}

## Top 3 Gaps (ranked by leverage)
1. **{gap name}** (−{pts} × {multiplier}×) → {concrete next step}
2. **{gap name}** (−{pts} × {multiplier}×) → {concrete next step}
3. **{gap name}** (−{pts} × {multiplier}×) → {concrete next step}

## Suggested next: {single highest-leverage action in one sentence}

---
Structural audit only. To plan what the KB should DO next, open a gap-closing session.
```

### Step 5: Offer to save

After printing, ask: "Save this audit to `audits/audit-{date}.md`?" If yes, write it (create `audits/` folder if needed). This is the only writable side effect of the skill.

## Implementation rules

1. **Read-only by default.** Never modify CLAUDE.md, skills, agents, connections.md, or any project files. Only writable side effect is the optional audit save.
2. **Flexible path detection.** Don't penalize non-canonical names if equivalent intent is present. `voice-decisions.md` in `scla/brand/` counts as brand/voice documentation.
3. **Be honest, not generous.** A 90/100 is rare. Most setups land 40–70 on first run.
4. **Speed over thoroughness.** Read targeted files. Don't load the full archive. Under 60 seconds.
5. **Don't suggest skills that don't exist** in this Claude Code session.
```

- [ ] **Step 3: Verify valid YAML frontmatter**

Run:
```bash
head -5 .claude/skills/kb-audit/SKILL.md
```
Expected:
```
---
name: kb-audit
description: Use when asked to audit the knowledge base, check KB health, score the repo, or run a structural review. Produces a four-dimension scoreboard (/100) and top-3 gap report. Run after first setup, then weekly. Read-only except for the optional audit save.
---
```

- [ ] **Step 4: Verify all four scoring sections are present**

Run:
```bash
grep "^### " .claude/skills/kb-audit/SKILL.md
```
Expected:
```
### Knowledge (25 pts) — "Does the KB know what it needs to know?"
### Reach (25 pts) — "What can Claude actually access live?"
### Skills (25 pts) — "Are there reusable workflows installed?"
### Maintenance (25 pts) — "Is the KB actively tended?"
```

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/kb-audit/SKILL.md
git commit -m "feat: add /kb-audit skill — KB health-check scoring Knowledge/Reach/Skills/Maintenance /100"
```

---

### Task 4: First `/kb-audit` run and baseline save

- [ ] **Step 1: Invoke the skill**

In a Claude Code session on this repo, type:
```
/kb-audit
```

- [ ] **Step 2: Verify output format**

The response must include all four elements:
- Score line: `**Score: {n}/100** ({stage})`
- Scoreboard with four rows: Knowledge, Reach, Skills, Maintenance
- "Top 3 Gaps" section with concrete next steps
- "Suggested next" line

If any element is missing, check `.claude/skills/kb-audit/SKILL.md` Step 4 under Execution.

- [ ] **Step 3: Save the baseline audit**

When prompted "Save this audit to `audits/audit-{date}.md`?", answer yes.

- [ ] **Step 4: Commit the baseline**

```bash
git add audits/
git commit -m "docs: save baseline /kb-audit score (first run)"
```
