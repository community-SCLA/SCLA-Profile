---
source: Google Drive — SCLA Visual Identity Guide (community@thescla.org, updated 2026-05-13)
generated_by: brand-analyst
last_updated: 2026-05-28
---

# SCLA Visual Identity

> Source: Google Drive "SCLA Visual Identity" in the Branding & Communications folder.

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

### Color usage principles

- Deep Navy is the dominant brand color. Lead with it.
- Gold is an accent only — use it sparingly and with intention (CTAs, highlights, key callouts).
- Do not use light backgrounds as the primary frame for brand-forward materials. Navy backgrounds project authority and prestige.
- Maintain sufficient contrast between text and background for accessibility (minimum 4.5:1 ratio for body text).

## Typography

| Role | Family | Weight | Notes |
| --- | --- | --- | --- |
| Headline / Brand | Proxima Nova | Extrabold / Bold | Primary brand font for all headlines, display text, and brand-forward elements |
| Body / Supporting | Arial | Regular / Bold | Used alongside Proxima Nova for body copy, slide content, and supporting text |
| Fallback | Calibri | Regular | Office default fallback only — not for intentional brand use |

### Typography usage guidance

- Proxima Nova should lead all brand communications wherever possible.
- Arial is appropriate for documents, email, and contexts where Proxima Nova is unavailable.
- Do not substitute decorative or display fonts not listed here.
- Confirm whether Proxima Nova is licensed org-wide or only in presentation assets before expanding use to new formats.

## Logo variants

The following logo variants should exist for all brand-approved use cases. See [Asset Index](./assets/index.md) for available files.

| Variant | Use |
| --- | --- |
| Primary lockup | Full wordmark + crest/icon on light background |
| Reversed lockup | Full wordmark + crest/icon on dark or colored background |
| Icon / mark only | Favicon, app icon, social profile avatar |
| Monochrome black | Single-color version for print on white |
| Monochrome white | Single-color version for dark background print |

### Logo rules

- Do not stretch, recolor, or apply drop shadows to the logo.
- Maintain clear space around the logo at all times.
- Use the reversed lockup on dark navy or gold backgrounds only.

## Imagery style

- Prioritize imagery that reflects real, diverse college students in professional and campus contexts.
- Tone should be aspirational and polished — not overly staged or stock-photo generic.
- Avoid imagery that looks passive or disconnected. SCLA's brand is active and forward-moving.
- When in doubt, choose imagery that reinforces the "campus to career" journey.

## Design tokens

### YAML tokens

```yaml
# SCLA design tokens
colors:
  primary:    "#002060"   # Deep Navy
  secondary:  "#334F7C"   # Mid Navy
  accent:     "#FFC000"   # Gold
  background: "#FFFFFF"   # White
  text:       "#000000"   # Black
  link:       "TODO"      # not specified in brand guide — confirm with team

typography:
  font_headline:      "Proxima Nova"
  font_body:          "Arial"
  weight_regular:     400
  weight_semibold:    600
  weight_bold:        700
```

### CSS custom properties

```css
/* SCLA design tokens */
:root {
  --color-primary:      #002060;   /* Deep Navy */
  --color-secondary:    #334F7C;   /* Mid Navy */
  --color-accent:       #FFC000;   /* Gold */
  --color-background:   #FFFFFF;
  --color-text:         #000000;
  --color-link:         TODO;      /* not specified in brand guide */

  --font-headline:      "Proxima Nova", Arial, sans-serif;
  --font-body:          Arial, sans-serif;
  --font-weight-regular:  400;
  --font-weight-semibold: 600;
  --font-weight-bold:     700;
}
```
