---
source: scla/_raw/web/www.thescla.org/index.md, scla/_raw/INGEST_ERRORS.md, scla/_raw/web/ (HTML exports)
generated_by: brand-analyst
last_updated: 2026-05-13
confidence: medium
---

# Brand Guide — Open TODOs

Updated 2026-05-13: HTML exports scraped from thescla.org were processed.
Priorities 1, 4, and 5 are resolved. Priorities 2 and 3 still require files
from SCLA staff.

---

## ~~Priority 1 — Full website copy~~ ✓ RESOLVED (2026-05-13)

HTML exports were processed from `scla/_raw/web/`. The following was completed:

- voice-and-tone.md: 21 verbatim copy samples added, all 5 voice axes updated to `medium` confidence
- "Write this, not that" table fully populated (6 examples)
- "Phrases to avoid" list expanded
- brand-guide.md common mistakes section updated with confirmed name/article rules

**Remaining from this priority:** contact-us page not scraped (no HTML export available).

---

## Priority 2 — Logo files (unblocks visual identity, asset index)

No logo or icon files exist in `scla/_raw/assets/`.

**What to provide:** Drop into `scla/_raw/assets/`:
- Primary logo SVG (color, on light background)
- Primary logo SVG (reversed / on dark background)
- Icon / mark only SVG (for favicon and social avatar)
- PNG fallbacks at 2x resolution for each of the above

**What it unlocks:** assets/index.md rows (filename, kind, min size,
background rules), visual-identity.md logo variants section.

---

## Priority 3 — Brand guidelines PDF or style guide (unblocks visual identity)

No brand PDF is present in `scla/_raw/assets/` or `scla/_raw/docs/`.

**What to provide:** Any existing document specifying:
- Primary and secondary color palette with hex codes
- Typography families, weights, and usage rules
- Logo clear-space and minimum size rules
- Prohibited logo treatments (stretching, recoloring, drop shadows, etc.)

**What it unlocks:** visual-identity.md colors table, typography table,
design tokens YAML block, CSS custom-properties block — all of which are
currently `TODO`.

---

## ~~Priority 4 — Tagline confirmation~~ ✓ RESOLVED (2026-05-13)

Confirmed from HTML exports: "From Campus to Career" is the official tagline.
Appears in homepage title and used as core mission framing throughout the site.
Updated in brand-guide.md `At a glance` section.

**Still open:** Which contexts to use it in (email signatures, print, hero only) — needs SCLA staff confirmation.

---

## ~~Priority 5 — Name and article style~~ ✓ RESOLVED (2026-05-13)

Confirmed from HTML exports:

1. **Article usage** — "The SCLA" (capital T) in running prose
2. **Capitalization** — "Honor Society" is always capitalized as a proper noun
3. **Long-form** — "The Society for Collegiate Leadership & Achievement" on first reference in formal documents; "The SCLA" or "SCLA" thereafter

Updated in brand-guide.md `Common mistakes` section.

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
