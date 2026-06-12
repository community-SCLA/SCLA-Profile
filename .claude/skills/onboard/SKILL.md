---
name: onboard
description: Interactive conversational wizard that personalizes this ops template for a new owner. Fills [PLACEHOLDER] values across the repo and commits the result. Use when someone has just cloned the template and wants to set it up.
---

# Onboarding Wizard

The front door for anyone who just cloned this template. It turns the blank
template into *their* personal ops repo — conversationally, with no terminal
commands required. Works in both the Claude Code desktop app and claude.ai.

## What this does

1. **Choose a path** — fresh start, import a local repo, or import from GitHub
2. **Gather context** — if importing, analyze the source so values can be pre-filled
3. **Fill the gaps** — ask only about what couldn't be confidently inferred
4. **Commit** — write every file and make one git commit

This skill only fills `[PLACEHOLDER]` tokens. It never deletes existing content.

## The flow

### Pre-check — ingest mode detection (runs before Step 1)

Before presenting any mode options, check whether `_inbox/INGEST_MANIFEST.md`
exists in the current repo root.

If it exists → do not run this wizard. Tell the user:

> "I found an ingest manifest. Running ingest mode now."

Then proceed to execute the ingest flow directly — follow the phases documented
in `.claude/skills/ingest/SKILL.md` starting at Phase 1. Do not continue the
onboard wizard.

If for any reason you cannot execute the ingest flow inline, tell the user:

> "Type `/ingest` to continue — your existing files are staged and ready to be
> organized into the framework."

If it does not exist → continue to Step 1 below.

---

### Step 1 — Pick a mode

Ask the user which one fits (use AskUserQuestion):

- **Fresh start** — answer all placeholder questions from scratch (~5 min)
- **Import a local repo** — read an existing project's files and pre-fill what you can
- **Import from GitHub** — same, but pull the repo from a GitHub URL

### Step 2 — Gather context (import modes only)

If importing, build a picture of the owner before asking anything:

- Read the source's `README`, `package.json`, `pyproject.toml`, `CLAUDE.md`, and similar
- Scan the folder structure
- Infer name, email, GitHub handle, timezone, tech stack, and focus areas

For **local import**, read from the filesystem with the Read/Glob tools.
For **GitHub import**, fetch the repo's files via WebFetch. If the repo is private
or unreachable, say so plainly and offer to switch to fresh mode.

### Step 3 — Fill the placeholders

Fill `[PLACEHOLDER]` values across the template files, using inferred values where
confident and asking the user only for the rest. Files that contain placeholders:

- `CLAUDE.md` — name, email, focus areas, timezone, tooling
- `context/me.md` — communication style and working preferences
- `context/goals.md` — career / business targets
- `context/work.md` — employment status / availability
- `connections.md` — tools in use (Notion, Slack, etc.)
- `endpoints.md` — GitHub username/repo, last-verified date
- `MAP.md` — name, focus areas, last-updated date (loaded every session via routing)
- `memory/MEMORY.md`, `memory/overview.md`, `memory/glossary.md`
- `decisions/log.md`
- `scheduled-tasks/example-task/README.md` — launchd label username

Do not fill placeholders inside instructional/example files — leave
`GOVERNANCE.md`, `REVIEW.md`, and the `.claude/skills/` files
as-is. Their brackets are documentation, not the owner's data.

The placeholder values you will need:

- Full name → `[YOUR_NAME]`
- Email address → `[YOUR_EMAIL]`
- GitHub username → `[YOUR_USERNAME]` (and repo name → `[YOUR_REPO]`)
- Timezone → `[TIMEZONE]` (PST, EST, CET, UTC, …)
- 2–3 focus areas → `[YOUR_FOCUS_AREAS]` (e.g. "Job search, AI consulting")
- The three main focus areas, labeled individually (skip if same as above)
- Today's date → `[DATE]` (use the current date for any "last updated" fields)
- (Optional) Main services / portfolio page name

If you cannot confidently infer a value, ask for it. Never invent personal details.

### Step 4 — Show and confirm

Before committing, show the user what was filled in (especially inferred values)
so they can correct anything. Then write all files with the Write tool.

### Step 5 — Sweep for leftovers (required)

After writing, run a final sweep so nothing personal is left blank. From the repo
root:

```bash
grep -rnE '\[YOUR_[A-Za-z_]*\]|\[TIMEZONE\]|\[DATE\]|\[ONE_LINE_SUMMARY[^\]]*\]|\[TOOLS_YOU_USE[^\]]*\]|\[FOCUS_AREA_[0-9][^\]]*\]' . \
  --include='*.md' \
  | grep -vE '\.git/|_archive/|_templates/|GOVERNANCE\.md|REVIEW\.md|\.claude/skills/'
```

- If it returns **nothing** → every owner placeholder is filled. Continue to commit.
- If it returns lines → those files still have gaps. Fill them (ask the user for any
  value you can't infer), then re-run the sweep until it comes back clean.

This catches files that were missed and is the safety net that makes onboarding
trustworthy — never commit with owner placeholders still present.

### Step 6 — Commit

```
Initial setup: personalized ops repo

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

## After the wizard

Tell the user:

1. **Review `CLAUDE.md`** and confirm everything reads correctly
2. **Add their voice** to longer sections like `context/me.md` that need real prose
3. **Connect tools** in `connections.md` if they use Notion, Slack, etc.
4. **(Optional, Claude Code only)** run `bash scripts/setup.sh` to copy Claude Code
   hooks and wire up settings. Web users can skip this; all core features work without it.

## Re-running

Safe to re-run. It only touches remaining `[PLACEHOLDER]` tokens, so already-filled
values are left alone. To undo a run: `git reset HEAD~1` (undo the commit) or
`git reset --hard` (revert to the clean template).

## Notes

- Everything happens inside Claude Code or claude.ai — no terminal needed.
- This is a manual command (`disable-model-invocation`): it runs only when the
  user types `/onboard`, never automatically, because it writes files and commits.
