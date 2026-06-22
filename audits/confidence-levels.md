# Confidence Levels — Extracted Register

> **Why this file exists.** Confidence ratings used to live inline in each KB page
> (frontmatter `confidence:` lines, `**Confidence:**` bullets, source-note clauses, etc.).
> Per request, those markers were **removed from the files themselves** and collected
> here so the team can decide how to handle confidence tracking going forward (e.g. a
> single dashboard, a re-score pass, or retirement of the scale).
>
> Extracted: 2026-06-22. Scope: live KB only (`scla/`, `context/`, `decisions/`,
> `references/`). `_archive/` provenance and `hooks/` code were intentionally left alone.
> AI/Gemini `confidence >= 0.8` threshold content in the integration docs is **system
> design, not a KB trustworthiness rating**, and was left in place.

---

## 1. Page-level confidence (removed from frontmatter)

| File | Confidence |
| --- | --- |
| `scla/member-support/products-services.md` | high |
| `scla/member-support/glossary.md` | high |
| `scla/member-support/index.md` | low |
| `scla/member-support/people.md` | high |
| `scla/member-support/community-platform.md` | high |
| `scla/operations/current-state.md` | medium |
| `scla/operations/pain-points.md` | medium |
| `scla/operations/team-roster.md` | medium |
| `scla/operations/automation-opportunities.md` | medium |
| `scla/partnerships/NIC.md` | high |
| `scla/brand/brand-guide.md` | medium |
| `scla/brand/visual-identity.md` | high |
| `scla/brand/voice-and-tone.md` | medium |
| `scla/brand/assets/index.md` | high |
| `scla/programs/course-catalog.md` | high |
| `scla/programs/scla-leadership-program.md` | high |
| `scla/programs/career-readiness-accelerator.md` | high |
| `scla/programs/programs-overview.md` | medium |
| `scla/programs/credentials-framework.md` | medium |
| `scla/projects/grants/rfp-1980-pilot-readiness-package.md` | high |
| `scla/projects/grants/rfp-1980-innovation-concept-narrative.md` | high |
| `decisions/log.md` | high |
| `references/notion-api.md` | high |

23 pages carried a frontmatter rating.

---

## 2. Inline / granular confidence (removed from body text)

### `scla/member-support/glossary.md`
Per-term ratings removed (`- **Confidence:** high`):

| Glossary term | Confidence |
| --- | --- |
| SCLA | high |
| NAB | high |
| ISPI | high |
| Career Readiness Certification | high |
| 4 Pillars | high |

Source-note clause removed from the "Internal Jargon" section:
`*Source: Community Team Monday meeting notes. Confidence: medium.*` -> kept as
`*Source: Community Team Monday meeting notes.*` — **medium** (source: Community Team Monday meeting notes).

### `scla/operations/team-roster.md`
Blockquote (People section) ratings removed:
- Community team entries — **medium** (source: April 2026 meeting notes).
- Exec / web entries — **low** (pending scrape of `https://www.thescla.org/leadership-team`).

### `scla/brand/visual-identity.md`
- "Orientation Slides" source note — removed `(confidence: medium)` — **medium**.

### `scla/brand/voice-and-tone.md`
- Top-of-file NOTE declaration removed: `Confidence is MEDIUM.` — page-level **medium** (in addition to frontmatter).
- Voice-axes table: removed the `Confidence` column and its five row values (all **medium**):
  - Formal <-> Casual — medium
  - Technical <-> Plain — medium
  - Earnest <-> Playful — medium
  - Authoritative <-> Supportive — medium
  - Institutional <-> Human — medium
- Section heading de-rated: `## Blog title signals (supplementary, low confidence)` — **low** (removed the `low confidence` qualifier).

### `scla/programs/programs-overview.md`
- Source note clause removed: `*Source: Community Team Monday meeting notes (Apr 6, 13, 20, 2026). Confidence: medium.*` -> kept attribution, dropped clause — **medium**.

---

## 3. Ambiguous — left in place for the team to decide

These mention a confidence rating inside methodology/narrative prose rather than as a
discrete page marker, so they were **not** auto-removed. Review and decide whether to
reword, relocate here, or keep.

### `scla/member-support/index.md` — "## Confidence notice" section (verbatim)
> This knowledge base was built from Google search-index snippets only. The full SCLA
> website returned HTTP 403 during the ingest stage (the original ingest-error log was
> scratch and is no longer kept in the repo). Every page is marked **confidence: low**
> until a human exports the priority pages listed in
> [TODOS.md](../_archive/member-support/TODOS.md) and re-runs `/kb`.

Also left: a table row reading "What source material is still needed to raise confidence"
(plain prose, no rating).

### `scla/brand/brand-guide.md` — line 85 (verbatim)
> To upgrade confidence from low to high: see TODOS.md.

### `context/current-priorities.md` (verbatim)
- "Raise confidence by exporting these pages manually:"
- "Confidence is **low -> medium** across most files because the website blocked scraping."

---

## 4. Deliberately untouched (not KB confidence levels)

- **AI/Gemini threshold design** in `scla/member-support/member-support-integration.md`
  and `scla/member-support/kb-integration-plan.md` (`confidence >= 0.8`, `(answer, confidence, route)`,
  capture-queue `confidence` column, "Gemini confidence threshold"). System architecture, not a rating.
- **Brand-voice prose** in `scla/brand/voice-and-tone.md` ("Undercuts student confidence",
  member/professional confidence) — ordinary copy.
- **Course topic name** in `scla/programs/course-catalog.md`: "Imposter Syndrome / Confidence / Identity".
- **`_archive/` and `hooks/`** — out of scope per the agreed edit boundary.
