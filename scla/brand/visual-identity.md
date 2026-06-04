---
source: thescla.org live CSS (template_custom.min.css, template_theme-overrides.min.css, inline styles)
generated_by: brand-analyst
last_updated: 2026-06-04
confidence: high
---

# SCLA Visual Identity

> Source: Values extracted directly from production CSS at thescla.org (June 2026).
> Previous version was derived from Orientation Slides (confidence: medium) and contained
> several discrepancies — notably the primary color (`#002060` in slides vs. `#0d2437` on web).
> The web CSS is now the source of truth. Slide deck colors are preserved as a note below.
> TODO: obtain a formal brand guidelines document to resolve any remaining slide/web divergence.

## Colors

### Primary palette (web — source of truth)

| Role | CSS token | Hex | Usage |
| --- | --- | --- | --- |
| Primary | `--darkBlue` | `#0d2437` | H1/H2 color, dark section backgrounds, nav |
| Primary dark | `--darkBlue2` | `#0a1e2f` | Even darker backgrounds, footer |
| Secondary | `--blue` | `#3393d6` | H3–H6, links, accents, form titles, borders |
| Accent / CTA | `--yellow` | `#eaab2d` | Primary button fill, highlights |
| Body text | *(no token)* | `#292f35` | Default body copy color |
| White | `--white` | `#ffffff` | Default background |

### Supporting palette

| Role | CSS token | Hex | Usage |
| --- | --- | --- | --- |
| Light background | `--cultured` | `#f6f6f9` | Section fills |
| Light background alt | `--antiFlashWhite` | `#f0f2f9` | Alternate section fills |
| Subtle fill | `--bright-gray` | `#e5eff6` | Cards, subtle backgrounds |
| Subtle fill alt | `--lavender` | `#e3e7f4` | Cards, subtle backgrounds |
| Dividers / borders | `--light-periwinkle` | `#cccedf` | Borders, input outlines |
| Muted / placeholder | `--ceil` | `#98a4cc` | Form placeholders, muted UI text |
| Light gray | `--darkgray` | `#eaeaea` | Light gray backgrounds |
| Pure black | `--black` | `#000000` | Rare — high-contrast contexts only |

### Interactive states (not in `:root` vars)

| State | Hex | Usage |
| --- | --- | --- |
| Button hover | `#1a334e` | All button hover backgrounds |
| Button active | `#ffd355` | Button active/pressed state (lighter yellow) |
| Link default | `#0270e0` | Inline text links |
| Link hover | `#0048b8` | Inline text link hover |
| Link active | `#2a98ff` | Inline text link active |

> **Note — slide deck colors:** The Orientation Slides (.pptx, Drive ID `12MXTvGlvN-nEkOXHx1nU2VKaVAPwTBn3`)
> use `#002060` (Deep Navy), `#00205A` (Navy), `#334F7C` (Mid Navy), `#2F5597` (Steel Blue), and
> `#FFC000` (Gold) — none of which match the web palette exactly. Until a formal brand guidelines
> document is available, treat the web CSS values above as authoritative for digital work.

---

## Typography

**Primary font family:** Proxima Nova

Loaded two ways: self-hosted `.otf` files served from the HubSpot CDN (`hubfs/`), plus an Adobe
Typekit kit (`use.typekit.net/ysq3rar.css`). Proxima Nova is the brand font for **all** text — headings
and body — on the live website. The Arial / Calibri fallbacks documented in the previous version of
this file were slide-deck artifacts, not web typography.

### Weights in use

| Weight | Style | Use |
| --- | --- | --- |
| 100 | Regular + Italic | Thin display (rare) |
| 300 | Light + Italic | Supporting copy |
| 400 | Regular + Italic | Body copy |
| 600 | Semibold + Italic | Labels, nav, emphasis |
| 700 | Bold + Italic | H3, subheadings, buttons |
| 800 | Extrabold + Italic | Display / hero headings |
| 900 | Black + Italic | H1, H2 |

### Type scale

| Tag | Size | Weight | Color |
| --- | --- | --- | --- |
| H1 | 90px | 900 (Black) | `#0d2437` |
| H2 | 40px | 900 (Black) | `#0d2437` |
| H3 | 30px | 700 (Bold) | `#3393d6` |
| H4 | 24px | — | `#3393d6` |
| H5 | 16px | — | `#3393d6` |
| H6 | 14px | — | `#3393d6` |
| Body | 18px | 400 | `#292f35` |

---

## Buttons

Three named variants. All use pill-shaped border radius (`100px`), `Proxima Nova`, and a
`300ms ease-in-out` transition. Hover state is uniform: `#1a334e` background / white text.

| Variant | Class | Default bg | Text | Border | Hover bg |
| --- | --- | --- | --- | --- | --- |
| Primary CTA (yellow) | `.btn-yellow` | `#eaab2d` | `#ffffff` | `#eaab2d` | `#0d2437` |
| Secondary (blue) | `.btn-blue` | `#0d2437` | `#ffffff` | `#0d2437` | `#0d2437` |
| Tertiary (white / ghost) | `.btn-white` | `#ffffff` | `#0d2437` | `#ffffff` | `#0d2437` |

Button specs: `font-size: 18px`, `font-weight: 600`, `padding: 17px 36px`, `border-radius: 100px`.

---

## Layout tokens

| Token | Value | Notes |
| --- | --- | --- |
| `--outerContainer` | 1568px | Full bleed outer wrapper |
| `--container` | 1444px | Standard content container |
| Content wrapper max-width | 1240px | HubSpot `.content-wrapper` |
| `--gap` | 15px | Grid column gap |
| `--radius` | 12px | Card / module border radius |
| Section padding | `80px 1rem` | Default `.dnd-section` vertical rhythm |
| Transition | `all 300ms ease-in-out` | `--animate` token |

---

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

---

## Imagery style

TODO: needs input — Describe the approved photographic and illustrative
style. SCLA staff should answer the following:

1. Do you use real student photography, stock photography, illustration, or a mix?
2. What setting / context is preferred — campus environment, professional office, a mix?
3. What is the emotional register — aspirational and polished, candid and authentic, documentary?
4. Are there approved stock image vendors or internal photo libraries?
5. Are there any subject-matter restrictions (no competitor logos visible in photos,
   specific diversity and inclusion representation guidelines)?

---

## Design tokens

Populated from live production CSS (June 2026). Safe to use in code.

### YAML tokens

```yaml
# SCLA design tokens — sourced from thescla.org production CSS, June 2026
colors:
  primary:        "#0d2437"   # Dark Navy — H1/H2, dark backgrounds
  primary_dark:   "#0a1e2f"   # Darker Navy — footer, deepest backgrounds
  secondary:      "#3393d6"   # Blue — H3–H6, links, accents
  accent:         "#eaab2d"   # Yellow — CTA buttons, highlights
  text:           "#292f35"   # Body copy
  background:     "#ffffff"   # Default white
  background_alt: "#f6f6f9"   # Cultured — light section fills
  muted:          "#98a4cc"   # Ceil — placeholder, muted UI
  link:           "#0270e0"   # Default link
  link_hover:     "#0048b8"   # Link hover

typography:
  font_primary:    "Proxima Nova"
  weight_thin:     100
  weight_light:    300
  weight_regular:  400
  weight_semibold: 600
  weight_bold:     700
  weight_extrabold: 800
  weight_black:    900
  size_body:       "18px"
  size_h1:         "90px"
  size_h2:         "40px"
  size_h3:         "30px"
  size_h4:         "24px"
  size_h5:         "16px"
  size_h6:         "14px"
```

### CSS custom properties

```css
/* SCLA design tokens — sourced from thescla.org production CSS, June 2026 */
:root {
  /* Core colors */
  --color-primary:        #0d2437;   /* Dark Navy */
  --color-primary-dark:   #0a1e2f;   /* Darker Navy */
  --color-secondary:      #3393d6;   /* Blue */
  --color-accent:         #eaab2d;   /* Yellow — CTA */
  --color-text:           #292f35;   /* Body copy */
  --color-background:     #ffffff;
  --color-background-alt: #f6f6f9;   /* Cultured */
  --color-muted:          #98a4cc;   /* Ceil */
  --color-link:           #0270e0;
  --color-link-hover:     #0048b8;

  /* Supporting fills */
  --color-fill-light:     #f0f2f9;   /* Anti-flash white */
  --color-fill-subtle:    #e5eff6;   /* Bright gray */
  --color-fill-lavender:  #e3e7f4;
  --color-border:         #cccedf;   /* Light periwinkle */
  --color-divider:        #eaeaea;   /* Dark gray */

  /* Typography */
  --font-primary:           "Proxima Nova", proxima-nova, Arial, sans-serif;
  --font-weight-regular:    400;
  --font-weight-semibold:   600;
  --font-weight-bold:       700;
  --font-weight-black:      900;
  --font-size-body:         18px;

  /* Layout */
  --container-outer:  1568px;
  --container:        1444px;
  --gap:              15px;
  --radius:           12px;
  --radius-pill:      100px;
  --animate:          all 300ms ease-in-out;
}
```
