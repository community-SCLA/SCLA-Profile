---
source: scla/_raw/artifacts/inbox/Copy of Community Team Mondays - 2026_04_06 15_56 CDT - Notes by Gemini.md, scla/_raw/artifacts/inbox/Copy of Community Team Mondays - 2026_04_13 15_55 CDT - Notes by Gemini.md, scla/_raw/artifacts/inbox/Community Team Mondays - 2026_04_20 16_00 CDT - Notes by Gemini.md
generated_by: workflow-mapper
last_updated: 2026-04-24
confidence: high
---

# Targeted Google Drive Search Queries

The user agreed to a **targeted** Google Drive sweep — not shotgun — to
fill the biggest evidence gaps surfaced by the April meeting notes.
Queries are ordered by expected leverage. Each line notes what we're
hoping to find and which workflow/KB area it enriches.

Run these against SCLA's community Google Drive via the Drive MCP
(`search_files`, `read_file_content`, `list_recent_files`). Suggest
picking the top 5 and iterating from the first-pass results.

---

## Tier 1 — Fill the biggest KB / workflow gaps

| # | Query string | Why it matters | Expected artifact | Enriches |
|---|---|---|---|---|
| 1 | `member journey` | The funnel (Pledge → Info session → Orientation → Onboarding → Member support) is the core product loop but has no written spec in `_raw/`. | Slide deck, Figma export, process doc | `current-state.md` funnel; `kb/programs/` |
| 2 | `60-day playbook` OR `30-day onboarding` | Zeketra explicitly called out "an accidentally robust 60-day playbook for the Member Conversion Program and a full 30-day onboarding process." High-value, named artifact. | Google Doc | `current-state.md` onboarding |
| 3 | `Champions Ambassador` OR `ambassador program` | Yesse's new project — budget considerations, reward structures, playbook drafts. Named but content lives outside notes. | Doc + research notes | `kb/programs/`; new workflow |
| 4 | `focus modes` OR `dashboard mockup` | Figma doc for Aug 1 launch. Drives AI resume builder gating + content strategy. | Figma link, spec doc | Automation opp #5; product roadmap |
| 5 | `MJML` OR `email template source` | Sean/Shawn's three canonical MJML samples — direct input to automation opp #1. | `.mjml` or code files | Weekly news workflow |

---

## Tier 2 — Named programs / docs referenced without detail

| # | Query string | Why it matters | Expected artifact | Enriches |
|---|---|---|---|---|
| 6 | `course catalog` OR `syllabi` | 61–62 courses named; only ~2 complete. Mayeth's catalog work went to Nollie. | Spreadsheet + syllabi docs | Course production workflow |
| 7 | `micro-internship` contract OR partnership | Contracts + samples for partner engagement; $39/each revenue model. | Contract templates, partner list | `kb/programs/`; new workflow |
| 8 | `info session` OR `pledge project` | Jenna + Iman + Aman own; templates requested Apr 20. | Slide deck, email templates | Funnel workflow |
| 9 | `prospectus` | Kierra building the sales-team prospectus via Notebook LM; replaces current multi-attachment approach. | Draft doc | Sales workflow |
| 10 | `orientation` | Referenced as connecting info session → onboarding; details thin. | Slide deck, script | Funnel workflow |

---

## Tier 3 — Institutional & context docs

| # | Query string | Why it matters | Expected artifact | Enriches |
|---|---|---|---|---|
| 11 | `community charter` OR `team charter` OR `mission` | Foundation doc referenced indirectly. Needed for Stage 5 source-of-truth. | Founding doc, values statement | `source-of-truth/charter` |
| 12 | `advisor subcommittee` OR `AI subcommittee` OR `Chapter Engagement` OR `Assessment Impact` | Three subcommittees mentioned Apr 13; Zeketra is in one. Structure not documented. | Charter / roster | `kb/people.md`, `kb/programs.md` |
| 13 | `workforce development grant` OR `nonprofit scholarship` | Adjacent legal entity + funding stream. Yesse interested. | Grant app, charter | `kb/products` (scholarship arm) |
| 14 | `weekly announcements` Canva OR archive | Historical email content + design conventions — useful input for Claude MJML template generator. | Canva designs, exports | Automation opp #1 |
| 15 | `AI resume builder` PRD OR spec OR backlog | Amy explicitly called out the need for a PRD. If one exists in draft, we want it; if not, we know to write it. | Draft PRD | Automation opp #5 |

---

## Suggested first pass

Start with queries **1, 2, 4, 5, 11** — they unblock the most downstream
work (member journey KB entry, MJML automation, and the Stage-5 charter
doc). Results will tell us whether to widen into Tier 2 or re-focus.

## What I need from the user before running these

- Confirmation that the Drive MCP has access scoped to the **community**
  Drive (not Amy's personal drive).
- Any must-include / must-exclude folder hints (e.g. "skip /archive").
- Any concern about sensitive content (scholarship recipients, partner
  contracts with NDAs) so I can exclude those from raw capture.

Once confirmed, results will land in `scla/_raw/docs/inbox/` with
source URLs preserved in frontmatter, and Stage 4 can be re-run against
the fuller corpus.
