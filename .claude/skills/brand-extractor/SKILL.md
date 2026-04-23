---
name: brand-extractor
description: Extract colors, typography, logos, and voice samples from scraped web pages and assets. Use when the brand-analyst agent needs design tokens.
---

# brand-extractor

Low-level scanner that the `brand-analyst` agent delegates to when it needs
raw signal from `client/_raw/`.

## What it produces

A structured scratch report (stdout, not persisted) of:

```yaml
colors:
  - hex: "#0A2540"
    count: 47            # occurrences across scraped pages
    contexts:            # where it was seen
      - "primary CTA background on homepage"
      - "nav bar"
typography:
  - family: "Inter"
    weights_seen: [400, 500, 600, 700]
    usage:
      - "body text"
      - "headings"
logos:
  - path: "client/_raw/assets/web/acme.com/logo.svg"
    variant: "primary"
    has_dark_variant: true
voice_samples:
  - sentence: "We ship tools our customers actually want to use."
    source: "client/_raw/web/acme.com/about.md"
    tone_signals: ["earnest", "plain", "first-person plural"]
```

## Process

1. **Colors**: grep CSS snippets in `_raw/web/**` for `#[0-9a-f]{3,6}`,
   `rgb(`, `hsl(`. Count occurrences. Skip neutral grays unless branded.
2. **Typography**: grep `font-family:` declarations. Extract unique families.
   For each, scan weights used.
3. **Logos**: glob `_raw/assets/**` for `logo*`, `brandmark*`, `icon*`.
   Classify variants by filename suffix (`-dark`, `-light`, `-mono`).
4. **Voice**: sample sentences from `_raw/web/**` — the client's own copy.
   Flag sentences with strong tone signals (rhetorical questions,
   imperatives, sensory words, etc.).

## Rules

- **Don't write files.** Return structured data to the calling agent.
- **Evidence-only.** Every output must have a `source:` or `count:` field.
  No guessing.
