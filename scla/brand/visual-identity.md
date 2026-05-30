---
source: Google Drive — Orientation Slides .pptx (jheath@thescla.org; updated 2026-05-11)
generated_by: brand-analyst
last_updated: 2026-05-13
confidence: medium
---

# SCLA Visual Identity

> Source: Colors and typography extracted from the current Orientation Slides deck
> (Drive file ID: `12MXTvGlvN-nEkOXHx1nU2VKaVAPwTBn3`), the most recently updated
> branded SCLA presentation. Confidence is MEDIUM — values are derived from applied
> styles in production slides, not a formal brand guidelines document.
> TODO: confirm with SCLA staff and cross-check against thescla.org CSS.

## Colors

| Role | Name | Hex | Usage |
| --- | --- | --- | --- |
| Primary | Deep Navy | `#002060` | Headers, primary backgrounds, dominant slide color |
| Dark background | Dark Navy | `#0D2437` | Dark slide backgrounds, section dividers |
| Dark background alt | Navy | `#00205A` | Alternate dark backgrounds |
| Supporting | Mid Navy | `#334F7C` | Supporting elements, secondary backgrounds |
| Supporting alt | Steel Blue | `#2F5597` | Secondary text, supporting color |
| Accent | Gold | `#FFC000` | CTAs, highlights, accent elements |
| Neutral | Medium Gray | `#888888` | Secondary text, captions |
| Light | Near White | `#F2F2F2` | Light backgrounds |
| Base | White | `#FFFFFF` | Default background |
| Base | Black | `#000000` | Default body text |

## Typography

| Role | Family | Weight | Notes |
| --- | --- | --- | --- |
| Headline / Brand | Proxima Nova | Extrabold / Bold | Primary brand font — appears 290x in slides; intentional branded choice |
| Body / Fallback | Arial | Regular / Bold | Theme default; used throughout alongside Proxima Nova |
| Fallback | Calibri | Regular | Office default fallback |

> TODO: Confirm whether Proxima Nova is licensed org-wide or only in presentation assets.
> TODO: Verify font usage on thescla.org (may use a web font variant of Proxima Nova or substitute).

## Logo variants

TODO: needs input — Provide logo files (SVG preferred, PNG fallback) for
each variant. Drop files into `scla/brand/assets/` and re-run `/brand` to
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
