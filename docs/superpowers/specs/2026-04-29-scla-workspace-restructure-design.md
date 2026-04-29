# SCLA Workspace Restructure — Design Spec
_Date: 2026-04-29_

## Problem

SCLA's two projects live in disconnected, poorly-named directories with no shared context:
- Dashboard: `~/Documents/design_handoff_scla_dashboard/`
- Profile: `~/Documents/SCLA/SCLA-Profile/`

No top-level CLAUDE.md governs the SCLA workspace. Opening either project in Claude Code gives no org-level context (GitHub account, team, separation rules).

## Goal

Consolidate both projects under `~/SCLA/` with a top-level `CLAUDE.md` that establishes SCLA org context for every Claude Code session opened anywhere under that root.

## Hard Constraints

- SCLA must **never** share a root, context, or credentials with kwoekel / Tampico / RNR
- GitHub account for all SCLA work: `community-SCLA` / `community@thescla.org`
- The two SCLA projects (dashboard, profile) must not cross-reference or share data

## Final Directory Structure

```
~/SCLA/
├── CLAUDE.md                                   ← new: org-level context
└── projects/
    ├── scla-dashboard/                         ← moved from ~/Documents/design_handoff_scla_dashboard/
    │   ├── dashboard-ai.jsx
    │   ├── dashboard-data.js
    │   ├── dev.sh
    │   ├── firebase.json
    │   ├── netlify.toml
    │   ├── ... (other loose files)
    │   └── scla-dashboard/                     ← Next.js app (keeps its own CLAUDE.md)
    └── scla-profile/                           ← moved from ~/Documents/SCLA/SCLA-Profile/
        ├── CLAUDE.md                           ← existing pipeline CLAUDE.md (unchanged)
        ├── client.config.yml
        └── ...
```

## CLAUDE.md Hierarchy

### `~/SCLA/CLAUDE.md` (new)
Org-level only. Contains:
- SCLA identity and purpose
- GitHub account rule: always `community-SCLA` / `community@thescla.org`
- What each project is (dashboard = team ops tool, profile = company knowledge base)
- Hard separation rule between projects

### `~/SCLA/projects/scla-dashboard/scla-dashboard/CLAUDE.md` (existing, unchanged)
Dashboard-specific: Next.js app, Firebase, Slack integration, known pending issues.

### `~/SCLA/projects/scla-profile/CLAUDE.md` (existing, unchanged)
Pipeline-specific: 5-stage onboarding pipeline, agent contracts, directory rules.

## Migration Steps

1. Create `~/SCLA/projects/`
2. Move `~/Documents/design_handoff_scla_dashboard/` → `~/SCLA/projects/scla-dashboard/`
3. Move `~/Documents/SCLA/SCLA-Profile/` → `~/SCLA/projects/scla-profile/`
4. Write `~/SCLA/CLAUDE.md`
5. Verify both projects intact
6. Delete old directories: `~/Documents/design_handoff_scla_dashboard/` and `~/Documents/SCLA/`

## What Is Unaffected

- Git remotes (URL-based, not path-based — no changes needed)
- Internal project CLAUDE.md files (both stay as-is)
- `.claude-scla/` config directory (path reference will need updating after move)

## Post-Migration

- Reopen Claude Code from `~/SCLA/` to pick up the new top-level CLAUDE.md
- `.claude-scla/` stores memory/session data keyed by project path. The old key `-Users-kierrawoekel-Documents-SCLA` will no longer match. Existing memory files should be copied to the new key `-Users-kierrawoekel-SCLA` so session context carries over.
