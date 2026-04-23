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
No page body text was retrieved.

**What to provide:** Export the following pages as PDF or plain-text HTML
and drop into `client/_raw/docs/inbox/`, then re-run `/ingest` and `/brand`.

Priority page list:
1. https://www.thescla.org/ (home)
2. https://www.thescla.org/benefits
3. https://www.thescla.org/the-scla-difference
4. https://www.thescla.org/mission-history
5. https://www.thescla.org/program
6. https://www.thescla.org/faq
7. https://www.thescla.org/membership-eligibility
8. https://www.thescla.org/start-a-chapter
9. https://www.thescla.org/contact-us
10. https://www.thescla.org/leadership-team
11. https://www.thescla.org/administrator-faq
12. https://www.thescla.org/online-membership
13. https://www.thescla.org/blog (index + 3–5 individual posts)

**Unlocks:** voice-and-tone.md axes (will rise to medium or high confidence),
"sounds like us" examples, "write this, not that" table, common-mistakes
section in brand-guide.md.

---

## Priority 2 — Logo files (unblocks visual identity, asset index)

No logo or icon files exist in `client/_raw/assets/`.

**What to provide:** Drop into `client/_raw/assets/`:
- Primary logo SVG (color, on light background)
- Primary logo SVG (reversed / on dark background)
- Icon / mark only SVG (for favicon and social)
- Any PNG fallbacks at 2x resolution

**Unlocks:** assets/index.md (filename, kind, recommended use, min size,
background rules), visual-identity.md logo variants section.

---

## Priority 3 — Brand guidelines PDF or style guide (unblocks visual identity)

No brand PDF is present in `client/_raw/assets/` or `client/_raw/docs/`.

**What to provide:** Any existing document that specifies:
- Primary and secondary color palette with hex codes
- Typography families, weights, and usage rules
- Logo clear-space and minimum size rules
- Prohibited logo treatments

**Unlocks:** visual-identity.md colors table, typography table, design
tokens YAML block, CSS custom-properties block.

---

## Priority 4 — Tagline confirmation

The page title "SCLA Honor Society | From Campus to Career" suggests
"From Campus to Career" may be the official tagline. This is not confirmed.

**What to provide:** Confirm in writing whether "From Campus to Career" is
the official tagline and in what contexts it should appear.

**Unlocks:** brand-guide.md "At a glance" tagline field.

---

## Priority 5 — Name and article style

Two forms appear in available snippets: "SCLA" (page title) and "The SCLA"
(blog post title "What Is The SCLA?"). Capitalization of "Honor Society"
also varies between snippets.

**What to provide:** Confirm the correct:
1. Article usage — "SCLA" or "The SCLA" in running text
2. Capitalization — "Honor Society" or "honor society"
3. Long-form usage — when to use full name vs. abbreviation

**Unlocks:** voice-and-tone.md "phrases to avoid" section, common-mistakes
section in brand-guide.md.

---

## Non-blocking but recommended

- Photography library or vendor license — needed for imagery style section
  in visual-identity.md
- Approved writing samples (emails, social posts, blog drafts) — needed to
  expand "sounds like us" corpus beyond 5 snippets
- Primary contact name and email — needed for client.config.yml
  (`primary_contact.name`, `.email`, `.role`)
