---
source: client/_raw/assets/ , client/_raw/web/www.thescla.org/index.md
generated_by: brand-analyst
last_updated: 2026-04-23
confidence: low
---

# SCLA Visual Identity

> NOTE: Confidence is LOW. No logo files, brand PDFs, hero images, color
> samples, CSS stylesheets, or typography specimens are present in
> `client/_raw/assets/` or `client/_raw/web/`. The ingest stage was blocked
> from reaching thescla.org (HTTP 403). Every field below is a placeholder.
> Do not use any value from this file in production until confirmed by SCLA.

## Colors

TODO: needs input — Provide the primary and secondary color palette with
hex codes. Preferred sources in order:
1. A brand guidelines PDF (drop into `client/_raw/assets/` and re-run `/brand`)
2. Exported CSS from thescla.org (browser DevTools > computed styles, copy
   the relevant `color` and `background-color` declarations)
3. A screenshot of the live homepage with color picker readings noted

| Role | Name | Hex | Usage |
|---|---|---|---|
| Primary | `TODO` | `TODO` | `TODO` |
| Secondary | `TODO` | `TODO` | `TODO` |
| Accent | `TODO` | `TODO` | `TODO` |
| Background | `TODO` | `TODO` | `TODO` |
| Body text | `TODO` | `TODO` | `TODO` |
| Link / interactive | `TODO` | `TODO` | `TODO` |

## Typography

TODO: needs input — Provide font families, weights, and usage rules.
Preferred sources: brand guidelines PDF, or inspect `font-family` declarations
in thescla.org's CSS.

| Role | Family | Weight | Size guidance |
|---|---|---|---|
| Headline (H1) | `TODO` | `TODO` | `TODO` |
| Subheadline (H2–H3) | `TODO` | `TODO` | `TODO` |
| Body | `TODO` | `TODO` | `TODO` |
| Caption / label | `TODO` | `TODO` | `TODO` |
| Button / CTA | `TODO` | `TODO` | `TODO` |

## Logo variants

TODO: needs input — Provide logo files (SVG preferred, PNG fallback) for
each variant. Drop files into `client/_raw/assets/` and re-run `/brand` to
auto-populate the asset index.

Expected variants (confirm with SCLA):
- Primary lockup: full wordmark + crest/icon, on light background
- Reversed lockup: full wordmark + crest/icon, on dark/colored background
- Icon / mark only: for favicon, app icon, social profile avatar
- Monochrome black: single-color version for print on white
- Monochrome white: single-color version for dark background print

Minimum safe sizes, clear-space rules (usually expressed as a multiple of
the logo's x-height or cap height), and prohibited treatments (stretching,
recoloring, drop shadows) should be documented here once logo files are
reviewed.

## Imagery style

TODO: needs input — Describe the approved photographic and illustrative
style. SCLA staff should answer the following:

1. Do you use real student photography, stock photography, illustration,
   or a mix?
2. What setting / context is preferred — campus environment, professional
   office, a mix?
3. What is the emotional register — aspirational and polished, candid and
   authentic, documentary?
4. Are there approved stock image vendors or internal photo libraries?
5. Are there any subject-matter restrictions (no competitor logos visible
   in photos, specific diversity and inclusion representation guidelines)?

## Design tokens

The blocks below are intentionally empty. They will be populated once color
and typography values are confirmed by SCLA. Do not substitute placeholder
values in production code.

### YAML tokens

```yaml
# SCLA design tokens
# Status: INCOMPLETE — awaiting confirmed values from client
# Last attempted: 2026-04-23
colors:
  primary:    "TODO"  # TODO: needs input — hex code from brand guidelines
  secondary:  "TODO"  # TODO: needs input
  accent:     "TODO"  # TODO: needs input
  background: "TODO"  # TODO: needs input
  text:       "TODO"  # TODO: needs input
  link:       "TODO"  # TODO: needs input

typography:
  font_headline: "TODO"  # TODO: needs input — family name (e.g. "Inter")
  font_body:     "TODO"  # TODO: needs input
  weight_regular: "TODO" # TODO: needs input — e.g. 400
  weight_semibold: "TODO"
  weight_bold:   "TODO"  # TODO: needs input — e.g. 700
```

### CSS custom properties

```css
/* SCLA design tokens */
/* Status: INCOMPLETE — all values are placeholders; do not ship */
:root {
  --color-primary:      TODO; /* TODO: needs input */
  --color-secondary:    TODO;
  --color-accent:       TODO;
  --color-background:   TODO;
  --color-text:         TODO;
  --color-link:         TODO;

  --font-headline:      TODO; /* TODO: needs input */
  --font-body:          TODO;
  --font-weight-regular:  TODO;
  --font-weight-semibold: TODO;
  --font-weight-bold:     TODO;
}
```
