## Current Priorities

### Pipeline Status (as of May 2026)
Stages 1–5 were run and live on the `claude/onboard-flow-WoTCI` branch. **Not yet merged into main.** Current main has only the ingest manifest.

**Immediate next step:** Merge the `claude/onboard-flow-WoTCI` branch into main, then re-run the pipeline with the documents already provided in `client/_raw/docs/inbox/`.

### Website Access
thescla.org returned HTTP 403 during the original ingest — use **Playwright MCP** to browse the site directly when re-running `/ingest`. This bypasses the block and produces real page content instead of Google search snippets. All KB content is currently `confidence: low` for this reason.

**Priority pages to scrape with Playwright:**
- https://www.thescla.org/mission-history
- https://www.thescla.org/leadership-team
- https://www.thescla.org/benefits
- https://www.thescla.org/program
- https://www.thescla.org/the-scla-difference

### Open Gaps
- Leadership team names and bios (leadership page was blocked in original run)
- Internal org chart — who reports to whom beyond Amy as lead
- CRM / member database details (app.thescla.org is auth-gated)
- Slack channel structure — which channels are process-relevant

### Q2 2026 Team Priorities (not pipeline-specific)
These are the community team's active work items this quarter (by June 30):
1. Weekly News shipping consistently — 4+ consecutive weeks, no single point of failure
2. Member Journey onboarding doc finalized — Zeketra + Alyssa → Kierra review → Amy presentation
3. Community Google Drive as the single source of truth for all project docs
4. Focus Modes content at 50% (Anushka) with clear production schedule toward August 1 launch
