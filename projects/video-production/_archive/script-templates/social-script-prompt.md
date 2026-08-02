# Social Media Script Prompt Template

Use this prompt in Claude to generate scripts for social media videos.

**Target tool:** HeyGen  
**Target length:** 60–90 seconds  
**Output format:** Single script, line-by-line format

---

## Prompt (copy and fill in brackets)

```
Write a [60 / 90]-second social media script for SCLA's [PLATFORM: Instagram / TikTok / LinkedIn / YouTube Shorts] audience.

Audience: College students ages 18–24 interested in leadership and career development.
Topic: [TOPIC OR MESSAGE]
Goal: [AWARENESS / ENGAGEMENT / CTA TO REGISTER / CTA TO SHARE]
Format: [VERTICAL 9:16 / SQUARE 1:1]

Rules:
- Hook in the first 3 seconds — make it impossible to scroll past
- Short, punchy sentences — max one idea per line
- No jargon, no corporate speak
- End with one clear, specific CTA: [SPECIFIC CTA]
- Tone: [ENERGETIC / CALM AND AUTHORITATIVE / CONVERSATIONAL]

Output format:
- Line 1: Opening hook (spoken text)
- Line 2–N: Body (each line = one spoken sentence, ~3–5 sec each)
- Final line: CTA (spoken text)
- [CAPTION]: Suggested caption text for the post
- [HASHTAGS]: 5–8 relevant hashtags
```

---

## Platform-Specific Notes

| Platform | Format | Max Length | Tone |
|---|---|---|---|
| Instagram Reels | 9:16 vertical | 90 sec | Energetic, visual |
| TikTok | 9:16 vertical | 60 sec | Fast, relatable |
| LinkedIn | 1:1 square or 16:9 | 90 sec | Professional, value-forward |
| YouTube Shorts | 9:16 vertical | 60 sec | Hook-heavy, educational |

---

## HeyGen Video Settings for Social

- Template category: **Social** → select vertical or square based on platform
- Avatar: Choose expressive avatar from Business or Expressive category
- Background: Clean, branded (use SCLA brand color or simple gradient)
- Text overlays: Add key phrases as on-screen text for sound-off viewing

---

## Batch Social Variations

To create A/B test variants, ask Claude:

```
Take this approved social script and create 2 variations:
- Variation A: Same message, different opening hook
- Variation B: Same message, different CTA

Keep all variations under [X] seconds.

Original script:
[PASTE SCRIPT HERE]
```

Then use HeyGen Batch Mode with a CSV to generate all variants at once.
