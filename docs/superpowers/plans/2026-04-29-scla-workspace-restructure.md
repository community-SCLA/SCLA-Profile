# SCLA Workspace Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate SCLA's two projects under a single `~/SCLA/` root with a top-level CLAUDE.md that establishes org context for every Claude Code session.

**Architecture:** Create `~/SCLA/projects/`, move both projects into it, write a lean org-level CLAUDE.md, migrate session memory keys, then delete the old directories. Git remotes are URL-based and require no changes.

**Tech Stack:** Bash (mv, cp, rm), Markdown (CLAUDE.md authoring)

---

### Task 1: Create the ~/SCLA/ root structure

**Files:**
- Create: `~/SCLA/projects/` (directory)

- [ ] **Step 1: Verify ~/SCLA/ does not already exist**

```bash
ls ~/SCLA 2>/dev/null && echo "EXISTS — stop and investigate" || echo "CLEAR — safe to proceed"
```
Expected: `CLEAR — safe to proceed`

- [ ] **Step 2: Create the directory**

```bash
mkdir -p ~/SCLA/projects
```

- [ ] **Step 3: Verify**

```bash
ls ~/SCLA/
```
Expected: `projects`

---

### Task 2: Move the dashboard

**Files:**
- Move: `~/Documents/design_handoff_scla_dashboard/` → `~/SCLA/projects/scla-dashboard/`

- [ ] **Step 1: Snapshot what's moving**

```bash
ls ~/Documents/design_handoff_scla_dashboard/
```
Expected: see `dashboard-ai.jsx`, `dashboard-data.js`, `dev.sh`, `firebase.json`, `netlify.toml`, `scla-dashboard/`, etc.

- [ ] **Step 2: Move the directory**

```bash
mv ~/Documents/design_handoff_scla_dashboard ~/SCLA/projects/scla-dashboard
```

- [ ] **Step 3: Verify files landed correctly**

```bash
ls ~/SCLA/projects/scla-dashboard/
```
Expected: same file list as Step 1 (`dashboard-ai.jsx`, `scla-dashboard/`, etc.)

- [ ] **Step 4: Verify git remote is intact**

```bash
git -C ~/SCLA/projects/scla-dashboard/scla-dashboard remote -v
```
Expected:
```
origin  https://github.com/community-SCLA/scla-dashboard.git (fetch)
origin  https://github.com/community-SCLA/scla-dashboard.git (push)
```

- [ ] **Step 5: Verify old location is gone**

```bash
ls ~/Documents/design_handoff_scla_dashboard 2>/dev/null && echo "STILL EXISTS — something went wrong" || echo "GONE — good"
```
Expected: `GONE — good`

---

### Task 3: Move the profile

**Files:**
- Move: `~/Documents/SCLA/SCLA-Profile/` → `~/SCLA/projects/scla-profile/`

- [ ] **Step 1: Snapshot what's moving**

```bash
ls ~/Documents/SCLA/SCLA-Profile/
```
Expected: `CLAUDE.md`, `client.config.yml`, `client/`, `templates/`, `scripts/`, `.claude/`, `docs/`, etc.

- [ ] **Step 2: Move the directory**

```bash
mv ~/Documents/SCLA/SCLA-Profile ~/SCLA/projects/scla-profile
```

- [ ] **Step 3: Verify files landed correctly**

```bash
ls ~/SCLA/projects/scla-profile/
```
Expected: same file list as Step 1

- [ ] **Step 4: Verify git remote is intact**

```bash
git -C ~/SCLA/projects/scla-profile remote -v
```
Expected:
```
origin  https://github.com/community-SCLA/SCLA-Profile.git (fetch)
origin  https://github.com/community-SCLA/SCLA-Profile.git (push)
```

- [ ] **Step 5: Verify old location is gone**

```bash
ls ~/Documents/SCLA/SCLA-Profile 2>/dev/null && echo "STILL EXISTS — something went wrong" || echo "GONE — good"
```
Expected: `GONE — good`

---

### Task 4: Move the design docs

**Files:**
- Move: `~/Documents/SCLA/docs/` → `~/SCLA/docs/`

- [ ] **Step 1: Move the docs folder**

```bash
mv ~/Documents/SCLA/docs ~/SCLA/docs
```

- [ ] **Step 2: Verify**

```bash
ls ~/SCLA/docs/superpowers/specs/ && ls ~/SCLA/docs/superpowers/plans/
```
Expected: both spec and plan markdown files are present

---

### Task 5: Write ~/SCLA/CLAUDE.md

**Files:**
- Create: `~/SCLA/CLAUDE.md`

- [ ] **Step 1: Write the file**

Create `~/SCLA/CLAUDE.md` with this exact content:

```markdown
# SCLA Workspace

This is the root workspace for **The Society for Collegiate Leadership & Achievement (SCLA)**.

---

## Identity

- Org: The Society for Collegiate Leadership & Achievement
- Website: https://www.thescla.org
- Contact: community@thescla.org

## GitHub Account

All SCLA work uses the **`community-SCLA`** GitHub account (`community@thescla.org`).
NEVER use a personal GitHub account (kwoekel or any other) for anything in this workspace.

## Projects

| Project | Path | Purpose |
|---|---|---|
| SCLA Dashboard | `projects/scla-dashboard/scla-dashboard/` | Team ops tool — project tracking, task management for SCLA staff |
| SCLA Profile | `projects/scla-profile/` | Company knowledge base — brand, workflows, source of truth |

Each project has its own CLAUDE.md with project-specific instructions. This file provides org context only.

## Hard Rules

- These two projects NEVER cross-reference or share data with each other.
- This workspace NEVER shares context, directories, or credentials with any other organization (kwoekel, Tampico Coral Farms, Rock N Roll Reefs, or any personal project).
- When committing, always verify you are on the `community-SCLA` GitHub account.
```

- [ ] **Step 2: Verify the file exists**

```bash
ls ~/SCLA/CLAUDE.md
```
Expected: file listed

---

### Task 6: Migrate .claude-scla/ memory keys

The `.claude-scla/` directory stores session memory keyed by the project's absolute path (with `/` replaced by `-`). The old key is `-Users-kierrawoekel-Documents-SCLA`. The new key will be `-Users-kierrawoekel-SCLA`.

**Files:**
- Copy: `~/.claude-scla/projects/-Users-kierrawoekel-Documents-SCLA/` → `~/.claude-scla/projects/-Users-kierrawoekel-SCLA/`

- [ ] **Step 1: Check what exists under the old key**

```bash
ls ~/.claude-scla/projects/-Users-kierrawoekel-Documents-SCLA/ 2>/dev/null || echo "NO OLD KEY — skip this task"
```

- [ ] **Step 2: Create the new key directory and copy memory files**

Only run this if Step 1 showed files (not `NO OLD KEY`):

```bash
mkdir -p ~/.claude-scla/projects/-Users-kierrawoekel-SCLA
cp -r ~/.claude-scla/projects/-Users-kierrawoekel-Documents-SCLA/. ~/.claude-scla/projects/-Users-kierrawoekel-SCLA/
```

- [ ] **Step 3: Verify the copy**

```bash
ls ~/.claude-scla/projects/-Users-kierrawoekel-SCLA/
```
Expected: `memory/` directory (and any other session files that were present)

---

### Task 7: Delete old directories

Only run this after confirming Tasks 2–4 succeeded.

- [ ] **Step 1: Confirm ~/Documents/SCLA/ only has leftovers**

```bash
ls ~/Documents/SCLA/
```
Expected: empty or only system files (the `SCLA-Profile/` and `docs/` should already be gone)

- [ ] **Step 2: Delete the empty directory**

```bash
rmdir ~/Documents/SCLA 2>/dev/null && echo "DELETED" || echo "NOT EMPTY — check contents before deleting"
```

If `NOT EMPTY`, run `ls ~/Documents/SCLA/` to see what's left, then manually remove or relocate before deleting.

- [ ] **Step 3: Confirm final structure**

```bash
find ~/SCLA -not -path "*/node_modules/*" -not -path "*/.git/*" -maxdepth 4 | sort
```
Expected output (abbreviated):
```
/Users/kierrawoekel/SCLA
/Users/kierrawoekel/SCLA/CLAUDE.md
/Users/kierrawoekel/SCLA/docs
/Users/kierrawoekel/SCLA/projects
/Users/kierrawoekel/SCLA/projects/scla-dashboard
/Users/kierrawoekel/SCLA/projects/scla-profile
```

---

### Task 8: Reopen Claude Code from ~/SCLA/

- [ ] **Step 1: Close this Claude Code session**

This session's working directory is `/Users/kierrawoekel/Documents/SCLA` which no longer exists after the migration. Close it.

- [ ] **Step 2: Open Claude Code from the new root**

```bash
cd ~/SCLA && claude
```

Or open `~/SCLA/` in VSCode and launch Claude Code from there. Claude will now load `~/SCLA/CLAUDE.md` as the top-level context on every session.
