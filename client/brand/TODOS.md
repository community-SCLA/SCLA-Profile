---
source: client/_raw/web/www.thescla.org/index.md, client/_raw/INGEST_ERRORS.md
generated_by: brand-analyst
last_updated: 2026-04-23
confidence: low
---

# Brand Guide — Open TODOs

This file lists exactly what SCLA staff must provide to upgrade the brand
guide from `confidence: low` to `confidence: high`. Items are ordered by
impact — completing item 1 unblocks the most downstream work.

---

## Priority 1 — Full website copy (unblocks voice, tone, common mistakes)

The ingest stage was blocked from reaching thescla.org by a sandbox proxy.
No page body text was retrieved — only Google search-index snippets.

**What to provide:** Export the pages below as PDF or plain-text HTML and
drop into `client/_raw/docs/inbox/`, then re-run `/ingest` and `/brand`.

| Priority | Page URL |
|---|---|
| 1 | https://www.thescla.org/ (homepage) |
| 2 | https://www.thescla.org/benefits |
| 3 | https://www.thescla.org/the-scla-difference |
| 4 | https://www.thescla.org/mission-history |
| 5 | https://www.thescla.org/program |
| 6 | https://www.thescla.org/faq |
| 7 | https://www.thescla.org/membership-eligibility |
| 8 | https://www.thescla.org/start-a-chapter |
| 9 | https://www.thescla.org/contact-us |
| 10 | https://www.thescla.org/leadership-team |
| 11 | https://www.thescla.org/administrator-faq |
| 12 | https://www.thescla.org/online-membership |
| 13 | https://www.thescla.org/blog (index + 3–5 individual posts) |

**What it unlocks:** voice-and-tone.md axis ratings (low → medium or high),
expanded "sounds like us" sample corpus (from 5 snippets to 30+), "write
this, not that" table, "phrases to avoid" list, common-mistakes section in
brand-guide.md.

---

## Priority 2 — Logo files (unblocks visual identity, asset index)

No logo or icon files exist in `client/_raw/assets/`.

**What to provide:** Drop into `client/_raw/assets/`:
- Primary logo SVG (color, on light background)
- Primary logo SVG (reversed / on dark background)
- Icon / mark only SVG (for favicon and social avatar)
- PNG fallbacks at 2x resolution for each of the above

**What it unlocks:** assets/index.md rows (filename, kind, min size,
background rules), visual-identity.md logo variants section.

---

## Priority 3 — Brand guidelines PDF or style guide (unblocks visual identity)

No brand PDF is present in `client/_raw/assets/` or `client/_raw/docs/`.

**What to provide:** Any existing document specifying:
- Primary and secondary color palette with hex codes
- Typography families, weights, and usage rules
- Logo clear-space and minimum size rules
- Prohibited logo treatments (stretching, recoloring, drop shadows, etc.)

**What it unlocks:** visual-identity.md colors table, typography table,
design tokens YAML block, CSS custom-properties block — all of which are
currently `TODO`.

---

## Priority 4 — Tagline confirmation

The page title in the search index reads "SCLA Honor Society | From Campus
to Career," which suggests "From Campus to Career" is the official tagline.
This has not been confirmed from a primary source.

**What to provide:** Confirm in writing:
1. Is "From Campus to Career" the official tagline?
2. In which contexts should it appear (email signatures, social profiles,
   printed materials, website hero only)?

**What it unlocks:** brand-guide.md "At a glance" tagline field.

---

## Priority 5 — Name and article style (unblocks common mistakes)

Two forms of the short name appear in available snippets: "SCLA" (page
title) and "The SCLA" (blog post title "What Is The SCLA?"). Capitalization
of "Honor Society" also varies between snippets ("Honor Society" vs.
"honor society").

**What to provide:** Confirm the correct:
1. Article usage — "SCLA" or "The SCLA" in running prose
2. Capitalization rule — "Honor Society" or "honor society"
3. Long-form vs. abbreviation — when to write the full name vs. "SCLA"

**What it unlocks:** voice-and-tone.md "phrases to avoid" section,
common-mistakes section in brand-guide.md.

---

## Non-blocking but recommended

- **Photography library or vendor license** — needed for the imagery style
  section in visual-identity.md. Without it, designers have no guidance on
  which stock images or photography styles are approved.
- **Writing samples beyond web copy** — emails to prospective members,
  social posts, event announcements. Needed to expand the voice corpus and
  confirm whether web copy voice matches CRM/social voice.
- **Primary contact details** — name, email, and role of the person
  responsible for brand decisions. Add to `client.config.yml` under
  `primary_contact`. Needed so the brand guide has an owner.
