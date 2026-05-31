# Design: SCLA KB Ops Framework
**Date:** 2026-05-31
**Status:** Approved
**Source:** Adapted from AIS-OS (github.com/nateherkai/AIS-OS, MIT) — concepts borrowed, SCLA-native naming, no trademarked terms.

---

## Background

Evaluated the AIS-OS ops framework against the SCLA-Profile repo. ~60% of the framework already exists under different names. Three elements are genuinely missing and worth building:

1. A system registry (`connections.md`) — dual-purpose: org systems inventory + AI-reachability map
2. A KB health-check skill (`/kb-audit`) — scores the repo /100 across four dimensions
3. A discipline doc (`EXPANSIONS.md`) — what to add, when, and what not to add

**Scope:** Pilot in SCLA-Profile first. Templatize for other repos after learning what works.

---

## Artifact 1 — `connections.md`

**Location:** `/workspaces/SCLA-Profile/connections.md` (repo root)

**Purpose:** Single document that answers two questions at once:
- (Team view) What systems does SCLA run on?
- (AI view) Which of those can Claude reach right now, and how?

**Schema:**

```
| # | Domain | System | Purpose | Claude can reach? | Mechanism | Auth state | Last checked |
```

**Mechanism values:** `mcp` · `script` · `export` · `key+ref` · `not connected`

**Auth state values:** `active` · `needs-auth` · `expired` · `—`

**Domains (7):**

| # | Domain | Description |
|---|---|---|
| 1 | Community Platform | The primary member-facing platform (custom channels within scla website) |
| 2 | Communication | Internal comms and external member messaging (Slack, Gmail) |
| 3 | Content & Design | Asset creation and design tooling (Claude Designm Canva) |
| 4 | Knowledge / Files | Document storage and shared team knowledge (Google Drive, Notion) |
| 5 | Task & Project Tracking | Where work is tracked and owned (Notion) |
| 6 | Email & Member Outreach | Broadcast email and outreach tooling (Gmail, custom MJML email tamplates in SCLA dashboard) |
| 7 | Membership Tracking | Member sign-ups, engagement metrics, quarterly/annual goals |

**Companion rule:** When a new tool is wired, also save `references/{tool}-api.md` (endpoints, auth flow, common queries). Research once, reference forever. `/kb-audit` checks for this.

---

## Artifact 2 — `/kb-audit` skill

**Location:** `.claude/skills/kb-audit/SKILL.md`

**Purpose:** Read-only structural health-check. Scores the KB /100. Run on Day 7, then weekly. Watch the score climb. Answers "is the KB built right?" — not "what should we build next?"

**Portable by design:** Detects structure flexibly (doesn't penalize non-canonical names if equivalent intent is present). Meaningful on other repos even if folder layout differs.

### Four scoring dimensions (25 pts each)

#### Knowledge (25 pts) — "Does the KB know what it needs to know?"

| Criterion | Pts | How to detect |
|---|---|---|
| CLAUDE.md is substantive (>200 words) | 5 | Read and count |
| `context/` has all three files (me.md, goals.md, current-priorities.md) or equivalent | 5 | Glob check |
| Brand / voice is documented | 5 | `scla/brand/` or equivalent has ≥1 voice/tone file |
| Decisions log has ≥1 entry | 5 | `scla/source-of-truth/decisions-log.md` or any decisions file |
| No major TODO stubs in source-of-truth | 5 | Grep for `TODO: needs input` in `scla/source-of-truth/` |

#### Reach (25 pts) — "What can Claude actually access live?"

| Criterion | Pts | How to detect |
|---|---|---|
| Domain coverage | 10 | 1.4 pts per tier-1 domain reachable in `connections.md`. Round to 0.5. Cap 10. |
| Reference doc per connected tool | 5 | −1 per connected tool with no `references/{tool}-api.md`. Floor 0. |
| Auth / pipeline freshness | 5 | −1 per `needs-auth` or `expired` entry. Floor 0. |
| `connections.md` exists and is populated | 3 | 0 if missing; 1 sparse; 2 most rows filled; 3 all rows filled |
| At least one writable connection | 2 | Any connection that can write (send message, post update, create doc). 0 if all read-only. |

#### Skills (25 pts) — "Are there reusable workflows installed?"

| Criterion | Pts | How to detect |
|---|---|---|
| 3+ skills installed | 10 | Count `.claude/skills/*/SKILL.md` |
| 1+ custom-built skill (not a shipped default) | 10 | Skill name not in canonical defaults list |
| 1+ agent defined | 5 | Count `.claude/agents/*.md` ≥ 1 |

Canonical defaults (don't count as custom): `onboard`, `audit`, `kb-audit`, `level-up`, `skill-creator`, `brainstorming`, `writing-plans`, `systematic-debugging`, `verification-before-completion`, `frontend-design`, `code-review`, `remember`, `update-config`.

#### Maintenance (25 pts) — "Is the KB actively tended?"

| Criterion | Pts | How to detect |
|---|---|---|
| Skills modified within 30 days | 10 | `git log --since=30.days -- .claude/skills/` has commits |
| Decisions log has entry within 30 days | 10 | `git log --since=30.days -- scla/source-of-truth/decisions-log.md` has commits, OR most recent `## YYYY-MM-DD` heading is within 30 days |
| Templates folder populated | 5 | `templates/` has ≥1 file |

### Output format

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

(bar = ## per 5pts; label: Strong ≥20 · Solid 15–19 · Thin 8–14 · Missing <8)

## Strengths
- {1–3 bullets from highest-scoring criteria}

## Top 3 Gaps (ranked by leverage)
1. **{gap}** (−{pts} × {multiplier}) → {concrete next step}
2. **{gap}** (−{pts} × {multiplier}) → {concrete next step}
3. **{gap}** (−{pts} × {multiplier}) → {concrete next step}

## Suggested next: {single most leveraged action}
```

### Gap leverage multipliers

| Condition | Multiplier |
|---|---|
| `connections.md` missing entirely | 4× |
| CLAUDE.md missing or thin (<200 words) | 3× |
| ≤2 domains reachable | 3× |
| 0 skills | 2× |
| No entry in decisions log within 30 days | 2× |
| All connections read-only | 2× |
| Connected tools with no reference doc | 1.5× |
| All others | 1× |

### Writable side effect

After printing, offer: "Save this audit to `audits/audit-{date}.md`?" If yes, write it (create `audits/` folder if needed). Only writable side effect.

---

## Artifact 3 — `EXPANSIONS.md`

**Location:** `/workspaces/SCLA-Profile/EXPANSIONS.md` (repo root)

**Purpose:** Discipline doc. Answers "what do I add to this repo, and when?" Prevents both under-investment (missing structure) and over-investment (org theater, folder hoarding).

### What ships (don't remove)

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Root operating manual |
| `context/` | Org identity, goals, current priorities |
| `scla/brand/` | Voice, tone, visual identity |
| `scla/source-of-truth/` | Charter, decisions log, team handbook, onboarding |
| `scla/operations/` | How the team operates, pain points, automation opportunities |
| `scla/knowledge-base/` | Glossary, people, products & services, FAQs |
| `scla/programs/` | Program documentation |
| `scla/partnerships/` | Partner org docs |
| `scla/projects/` | Active project tracking |
| `docs/grants/` | Grant briefs and RFP working docs |
| `templates/` | Reusable project/content/grant scaffolds |
| `connections.md` | System registry (org + AI-reachability) |
| `.claude/skills/` | Installed skills |
| `docs/_archive/source-dumps/` | Raw Drive exports for provenance tracing only |

### What to add as you grow

| Add | When | Why |
|---|---|---|
| `audits/` | After first `/kb-audit` run | Track score over time |
| `references/{tool}-api.md` | Each time a new tool is wired in `connections.md` | Research once, reference forever |
| `scla/operations/sops/` | When a recurring process gets handed to someone new | Consistent execution without re-explaining |
| `.claude/agents/` | When a repeatable multi-step research/writing task emerges | Keeps main session lean |
| Scoped `CLAUDE.md` in a sub-area | When a sub-project (e.g. a major grant, a new program) needs isolated context | Scoped context without polluting root |
| `scripts/` | When connecting a tool that has no MCP and needs a custom API script | Most second connections are scripts, not MCPs |

### What NOT to add

- **Don't dump raw Drive exports into `scla/` or `references/`.** That's what `docs/_archive/source-dumps/` is for. Interpreted facts only in the live KB.
- **Don't create `notes/`, `misc/`, `tmp/`, or `inbox/` folders.** Graveyards. Use `docs/_archive/` if it's old; write a proper file in the right place if it's new.
- **Don't pre-create folders you don't need yet.** Empty folders are noise.
- **Don't fork `CLAUDE.md`.** One canonical root file. Sub-areas can have scoped ones; the root is authoritative.
- **Don't add parallel decisions files.** One decisions log at `scla/source-of-truth/decisions-log.md`.

### The two-yeses test

Before creating any new folder, ask:
1. Is this conceptually distinct from everything that already exists?
2. Will we touch this 3+ times in the next month?

Two yeses → add. One yes → wait.

---

## Portability notes

These three artifacts are designed to drop into any repo:

- `connections.md` schema is generic — swap in the relevant domains
- `/kb-audit` detects structure flexibly — doesn't require SCLA-specific paths
- `EXPANSIONS.md` structure (what ships / what to add / what not to add / two-yeses test) is repo-agnostic

When piloting in other repos: copy the three files, update `connections.md` with that repo's domains and systems, run `/kb-audit` to get a baseline score.
