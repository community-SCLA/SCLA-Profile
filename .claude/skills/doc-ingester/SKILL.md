---
name: doc-ingester
description: Import documents (PDF, DOCX, Google Docs export, Notion export) from an inbox folder into scla/_raw/docs/ with normalized frontmatter.
---

# doc-ingester

Turns a pile of client-supplied documents into a registered, dated, searchable
set of markdown files in `scla/_raw/docs/`.

## When to use

Called by the `ingestor` agent for `sources.docs[]` and whenever there are
files in `scla/_raw/docs/inbox/`.

## Inputs

Accepts any of:
- **Inbox folder**: `scla/_raw/docs/inbox/*` (drag-and-drop from the human)
- **Public URL**: Google Doc / Notion public / PDF URL in `sources.docs[].url`
- **Direct path**: pre-staged file in `sources.docs[].path`

## Process

1. For every file in the inbox or at a given path:
   1. Detect kind by extension: `.pdf`, `.docx`, `.md`, `.html`, `.txt`.
   2. Convert to markdown if needed (preserve headings, lists, tables).
   3. Write to `scla/_raw/docs/<kind>/<slug>.md` where `<kind>` is one of
      `handbooks/`, `policies/`, `contracts/`, `specs/`, `misc/`. If unclear,
      use `misc/` and note it.
   4. Prepend frontmatter:
      ```yaml
      ---
      source_path: inbox/<original-filename>
      fetched_at: <ISO>
      original_kind: pdf|docx|gdoc|notion|html|txt
      ingestor_skill: doc-ingester
      ---
      ```
   5. Move (don't copy) the original from `inbox/` to `inbox/_processed/`
      so re-runs don't re-ingest.

2. For URL inputs: fetch → same pipeline as above, but filename is
   derived from the page title + a short hash.

3. Append one manifest row per file to `scla/_raw/MANIFEST.md`.

## Classification heuristic

If the doc kind isn't obvious from filename or frontmatter:
- Contains "SLA", "MSA", "NDA", "contract" → `contracts/`
- Contains "policy", "handbook", "code of conduct" → `policies/`
- Contains "spec", "RFC", "design doc" → `specs/`
- Contains "onboarding", "welcome", "getting started" → `handbooks/`
- Else → `misc/`

## Rules

- Text verbatim. No summarization.
- If conversion loses fidelity (complex tables, embedded images), keep the
  original binary in `scla/_raw/docs/_originals/` and reference it.
