# design.md — brand truth for `m1-mini-syllabus-freeform-trial`

Design source of record for this one video. Brand values are LOADED from the
workspace's own `tokens.yml` copy (colors, type floors, spacing, the pinned
Oxana voice); nothing here restates a hex value that a gate also reads.

Lesson: `lesson-scripts/mid-career-momentum/ready/m1_mini-syllabus.txt`.
Lane: freeform (agent-native) — no templates, no `scenes.json`, no compiler.
This is a one-off trial sited outside `renders-hyperframes/`, so it takes no
build lock and cannot collide with the live `m1_mini-syllabus` workspace.

## Concept angle

> The course is ONE career track drawn end to end, and the mid-career
> checkpoint is a single marked node on it — every beat of this lesson is
> another thing read off that same track, never a new picture.

**Persistence: beats s01 → s17, i.e. 100% of the 104.8s runtime.** The rail and
its five nodes are drawn once in the opening beat and are never rebuilt, never
cleared and never left. Everything the script names is a re-reading of it:

| Beats | What the track is asked to say | Script line it comes from |
| --- | --- | --- |
| s01–s02 | the track exists; what "more" means sits above it | "ready for more — more impact, more recognition, or simply a role that fits you better" |
| s03–s04 | the centre node is named the mid-career checkpoint | "the mid-career checkpoint in your career map" |
| s05 | the travelled part of the rail fills — the progress bar IS the rail | "you'll see your progress bar update" |
| s06–s07 | tools and support hang off the travelled segment | "click-through activities, short reflections, uploads, and a handful of AI-powered prompts" |
| s08–s09 | the road ahead of the checkpoint goes uncertain; constraints sit under it | "family responsibilities, leadership expectations, and a full calendar" |
| s10–s12 | three forks leave the checkpoint, one per beat | "Should I push for a promotion? Redesign my role to fit better? Or change lanes entirely?" |
| s13–s14 | a window is bracketed on the rail just past the checkpoint | "your next realistic move over the next 6 to 12 months" |
| s15–s16 | a marker is planted inside that window | "Over the next 90 days, my main career goal is…" |
| s17 | the track's far end becomes the CTA | "click Next to begin" |

**The rule, stated out loud:** *if an element cannot be justified as another way
of reading the same track, it does not exist.* No element on this frame is
introduced except as a mark ON the rail, a label ABOVE it, or a detail HANGING
UNDER it. There is no second illustration and no decorative object.

Why this angle and not another: the script itself supplies it twice — the
lesson calls itself "the mid-career checkpoint in your career map" and then
promises a progress bar. A slideshow of unrelated pictures is exactly the shape
the owner rejected on 2026-08-04; a persisting object that re-sorts is the shape
they approved.

## Palette

Every value comes from `tokens.yml colors:` (loaded by `check_brand.py`, which
fails any literal that is not one of them at any alpha). Roles for this video:

| Role | Token | Use |
| --- | --- | --- |
| Page ground | `navy-deep` | full-bleed background child, never the root |
| Ground lift | `navy` | radial lift behind the track, panel fills |
| Foreground | `paper` | display type, node numerals |
| Body / secondary | `paper` at ~0.78 alpha | body copy on navy |
| Structure | `blue` | the rail itself, inactive nodes, hairlines, labels |
| Focus accent | `gold` | **reserved**: the checkpoint node, the active fork, the CTA |

One accent hue with one job — *what the track is pointing at right now*. Gold
never decorates.

## Type

Proxima Nova only, the vendored `woff2` 400/700/900 in `assets/fonts/`.
Hierarchy is weight, size and colour — never a second family.

| Role | Size | Weight |
| --- | --- | --- |
| Lesson title (title card) | 104px | 900 |
| Beat heading | 68px | 900 |
| Body / detail | 44px | 400 |
| Node numeral | 44px | 900 |
| Label / eyebrow / chip | 26px | 700, uppercase, 0.14em |

Body floor is the tokens.yml floor (40px); nothing viewer-read is set at it.
Headings are `data-role="heading"` and Title Case with no terminal period.

## Frame

- 1920×1080. Nothing content-bearing crosses the safe area, the frame padding
  or the content-bottom band — all three LOADED from `tokens.yml` and graded on
  real pixels by `check_ink.py`.
- The rail sits at y=620, x=200→1720: optically centred, with the headline band
  above it (y 210→560) and the detail band below it (y 690→930).
- The program eyebrow is the only element in the top keep-out, inside the
  `chrome-regions` rectangle `tokens.yml` declares by name.

## Motion

- Entrances only: 0.45–0.7s, `power3.out`, pinned to the word timestamp that
  earns them. Nothing settled re-animates in place.
- The rail is only ever *extended, marked or re-lit* — it is never rebuilt.
- One ambient breath, on the background glow alone, declared inline with
  `/* motion-allow: … */`.
