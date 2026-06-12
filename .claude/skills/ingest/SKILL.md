---
name: ingest
description: Organizes existing repo content into the ops framework structure. Fires automatically when _inbox/INGEST_MANIFEST.md is detected. Reads, deduplicates, and synthesizes source files into the correct framework locations — nothing deleted, originals archived.
---

# Ingest Skill

This skill runs after `install.sh` has staged existing content in `_inbox/`.
It consolidates that content into the correct framework locations — conversationally,
with user confirmation before any files are written.

**Trigger:** Runs automatically when `_inbox/INGEST_MANIFEST.md` exists.
Can also be invoked manually with `/ingest`.

---

## The flow

### Phase 1 — Read everything

**Empty manifest guard:** Before reading any files, check whether the manifest
contains any file paths. If the manifest is empty or contains no readable file
paths, stop immediately and tell the user:

> "The ingest manifest is empty — there were no pre-existing files to organize.
> Your framework structure is already set up. Run /onboard to fill in your
> personal details."

Do not proceed through the remaining phases if the manifest is empty.

---

Read every file listed in `_inbox/INGEST_MANIFEST.md` in full.

**Missing file handling:** If a listed file cannot be read (deleted, moved, or
permission error), log it as missing: "Could not read: [path] — skipping."
Continue reading the remaining files. Collect all missing paths and include them
in the Phase 2 cluster report so the user is aware of what was skipped.

Do NOT make routing decisions yet. Build a complete picture of:
- What files exist and what they contain
- What topics are covered across the full set
- What this repo was originally used for
- Who the owner appears to be (name, email, timezone, tools, focus areas)

Only move to Phase 2 once you have read every file in the manifest.

---

### Phase 2 — Cluster by content

Group files by topic and theme overlap. Identify what is unique versus
duplicated within each cluster. Report your clusters to the user before
routing anything. Examples:

- "3 files contain overlapping project context"
- "2 files are both integration/tool lists"
- "4 files all contain goal or target information"

This step surfaces the shape of the content so the user can spot surprises
before anything gets written.

---

### Phase 3 — Map clusters to framework locations

For each cluster, determine the correct framework destination:

| Content type | Framework location |
|---|---|
| Who the person is, voice, communication style | `context/me.md` |
| Career goals, targets, aspirations | `context/goals.md` |
| Employment status, availability | `context/work.md` |
| Tool integrations, API connections | `connections.md` |
| Endpoint IDs, database IDs, URLs | `endpoints.md` |
| Active project work | `projects/<name>/CLAUDE.md` |
| Terminology, people, glossary | `memory/` |
| Architectural decisions | `decisions/log.md` |
| Scheduled or recurring tasks | `scheduled-tasks/` |

For ambiguous clusters — content that could reasonably go in more than one
place — ask the user **one question at a time** to resolve before continuing.
Do not batch ambiguous questions; resolve each before moving to the next.

---

### Phase 4 — Synthesize (not move)

Source files are NOT moved at this stage. Their content is read, deduplicated,
and written into the correct framework file.

Rules:
- **Multiple files → same destination:** merge content, remove duplicates,
  preserve all unique context
- **Contradictions between files:** flag for user to resolve before writing
  (e.g. "File A says you're available full-time; File B says part-time — which
  is current?")
- **Gaps:** if critical framework fields have no source content, ask the user
  to fill them directly rather than leaving placeholders

**Existing content conflict check:** Before writing to any framework file that
already contains non-placeholder content, check whether the synthesized content
contradicts what is already there. If it does, surface the conflict to the user:

> "I found a conflict in [filename]: existing content says X, new content says Y.
> Which should I keep?"

Resolve all conflicts before writing.

Before executing any writes, show the user a confirmation summary:

> "From X source files I've synthesized these Y framework files — [list with
> one-line description of each]. Does this look right?"

User must approve before any files are written.

---

### Phase 5 — Archive originals + fill CLAUDE.md + clean up

After user confirms:

**Commit gate:** Only proceed to steps 1–5 below after ALL of the following are
confirmed complete: (1) every source file has been moved to `_archive/`,
(2) CLAUDE.md placeholders are filled, (3) `_inbox/INGEST_MANIFEST.md` has been
deleted, (4) the placeholder sweep returned clean. If any step failed or
produced errors, stop and report to the user before committing.

1. **Archive source files** — first, create `_archive/inbox/` and any
   subdirectories needed to mirror the source paths (e.g. if moving
   `_inbox/notes/context.md`, ensure `_archive/inbox/notes/` exists before
   the move — if the destination directory doesn't exist, the move will fail).
   Then move all original files from `_inbox/` to `_archive/` preserving their
   original path structure (e.g. `_inbox/notes/context.md` →
   `_archive/inbox/notes/context.md`). Nothing is deleted — everything is
   recoverable.

2. **Fill CLAUDE.md placeholders** — use context learned during ingest to
   fill `[PLACEHOLDER]` tokens in `CLAUDE.md`: name, email, timezone, key
   tools, and focus areas.

3. **Delete `_inbox/INGEST_MANIFEST.md`** — manifest has been consumed;
   remove it so this skill does not re-trigger on the next session.

4. **Run the placeholder sweep** — confirm no owner placeholders remain:

   ```bash
   grep -rnE '\[YOUR_[A-Za-z_]*\]|\[TIMEZONE\]|\[DATE\]|\[ONE_LINE_SUMMARY[^\]]*\]|\[TOOLS_YOU_USE[^\]]*\]|\[FOCUS_AREA_[0-9][^\]]*\]' . \
     --include='*.md' \
     | grep -vE '\.git/|_archive/|_templates/|GOVERNANCE\.md|REVIEW\.md|\.claude/skills/'
   ```

   If it returns hits, fill them before committing.

5. **Commit:**

   ```
   feat: ingest and organize existing repo content into ops framework
   ```

---

## After ingest

Tell the user:

1. **Review `CLAUDE.md`** and confirm the filled values read correctly
2. **Check synthesized files** — especially `context/me.md`, which benefits
   from real prose rather than merged bullet points
3. **Original files** are in `_archive/inbox/` if anything needs to be
   recovered
4. **(Optional)** Run `/onboard` to fill any remaining gaps interactively

---

## Notes

- This skill only runs when `_inbox/INGEST_MANIFEST.md` exists, or when
  explicitly invoked with `/ingest`.
- It never deletes source content — archive-first, always.
- Synthesis (Phase 4) is the key step: the goal is one clean framework file
  per destination, not a dumping ground of appended raw content.
