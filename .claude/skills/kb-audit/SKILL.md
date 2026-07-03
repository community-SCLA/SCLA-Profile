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
| `context/` has both core files or equivalent | 5 | Glob `context/*.md` — expect me.md and goals.md (goals + current priorities) or equivalent |
| Brand / voice is documented | 5 | Check `brand/` or equivalent for ≥1 voice or tone file |
| Decisions log has ≥1 entry | 5 | Check `decisions/log.md` or any file matching `*decisions*` |
| No major TODO stubs in source-of-truth | 5 | Grep `TODO: needs input` in `context/` and `operations/` — deduct 1 pt per stub found, floor 0 |

### Reach (25 pts) — "What can Claude actually access live?"

Read `connections.md` at repo root. If missing, score Reach as 0 and flag with 4× leverage multiplier.

| Criterion | Pts | How to detect |
|---|---|---|
| Reachable tool rows | 10 | Count rows in connections.md where "Claude can reach?" = Yes. 1.4 pts each, round to nearest 0.5, cap 10. (A tool appearing in multiple domains counts once per row — this is intentional, not double-counting.) |
| Reference doc per connected tool | 5 | For each reachable tool, check for `references/{tool}-api.md`. −1 per missing. Floor 0. |
| Auth / pipeline freshness | 5 | Count rows where Auth state = `needs-auth` or `expired`. −1 each. Floor 0. |
| `connections.md` populated | 3 | 0 if missing; 1 if sparse (<3 rows filled); 2 if most rows filled; 3 if all rows filled |
| At least one writable connection | 2 | Any row where Mechanism = `mcp` — assume MCP tools are writable (send, post, create). If all rows are `not connected` or `script`/`export`/`key+ref` with no write capability noted, score 0. |

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
| Decisions log has entry within 30 days | 10 | Run `git log --since=30.days --oneline -- decisions/log.md`. Any output = 10 pts. If no git result, check most recent `## YYYY-MM-DD` heading in the file. |
| Templates folder populated | 5 | Glob `templates/*.md` — ≥1 file = 5 pts. |

## Execution

### Step 1: Discover project shape

Read these paths (targeted reads only — do not load `docs/_archive/`):
- `CLAUDE.md` — word count and identity check
- `context/` — list files
- `brand/` — list files, look for voice or tone file
- `decisions/log.md` — first 20 lines to confirm entries exist
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
| ≤2 domains reachable (only applies when connections.md exists) | 3× |
| 0 skills installed | 2× |
| No decisions log entry within 30 days | 2× |
| All connections read-only | 2× |
| Connected tools missing reference docs | 1.5× |
| All others | 1× |

Sort by leverage descending. Take top 3. Write one concrete next-step for each:
- Missing `connections.md` → "Create `connections.md` at repo root using the schema in `_archive/2026-05-31-ops-framework-design-spec.md`."
- CLAUDE.md thin (<200 words) → "Expand CLAUDE.md to document org identity, project structure, key rules, and context file locations (target >200 words)."
- context/ files missing → "Create `context/me.md` and `context/goals.md` (goals + current priorities) with org identity and current focus."
- Brand/voice undocumented → "Create `brand/voice-and-tone.md` capturing the org's writing register and communication style."
- No reference doc for a connected tool → "Create `references/{tool}-api.md` documenting endpoints, auth flow, and common queries."
- No custom skill → "Create `.claude/skills/{name}/SKILL.md` with YAML frontmatter (name + description) and execution steps."
- No agent → "Create `.claude/agents/{name}.md` for a repeatable multi-step task."
- Stale decisions log → "Append a dated entry to `decisions/log.md`."
- No writable connection → "Confirm at least one MCP tool in `connections.md` has `mechanism: mcp` — MCP connections are writable by default."
- Templates folder empty → "Add at least one template to `templates/` (e.g. copy `templates/project-grant.md` pattern for a new content type)."

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
(If all dimensions score 0, omit this section and write: "No strengths yet — this is Stage 0. Start with the gaps below.")

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
2. **Flexible path detection.** Don't penalize non-canonical names if equivalent intent is present. `voice-decisions.md` in `brand/` counts as brand/voice documentation.
3. **Be honest, not generous.** A 90/100 is rare. Most setups land 40–70 on first run.
4. **Speed over thoroughness.** Read targeted files. Don't load the full archive. Under 60 seconds.
5. **Don't suggest skills that don't exist** in this Claude Code session.
