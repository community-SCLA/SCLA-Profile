# design.md — brand truth for this composition

Design source of record for `agent-native-m2`. Brand values come from
`brand/visual-identity.md` (SCLA web palette + Proxima Nova). Everything else on this
page was decided for **this** video, from scratch — no SCLA design-system template,
token file, or render-qa gate participates in this build.

## Concept angle

> Four transitions are not four lists — they are four positions on **one map**. The video
> builds that map once, in front of the viewer, and never leaves it.

Every scene is a state of the same 2×2 matrix: the axes draw, the grid crosses, each
quadrant fills and takes focus in turn, then all four resolve. The two axis questions are
the spine of the piece and return verbatim at the close.

Matrix semantics (from the script, not invented):

|                    | Adjacent leap        | New-field leap      |
| ------------------ | -------------------- | ------------------- |
| **You chose it**   | Pivot                | Reinvention         |
| **It chose you**   | Rebuild              | Forced Reinvention  |

## Palette (dark — professional/decision-making register)

| Role              | Hex                     | Use                                                    |
| ----------------- | ----------------------- | ------------------------------------------------------ |
| Page ground       | `#0a1e2f` (primary-dark)| Full-bleed background child (never on the root itself)  |
| Ground lift       | `#0d2437` (primary)     | Matrix field, panel fills, radial lift                  |
| Foreground        | `#ffffff`               | Display type, quadrant names                            |
| Body / secondary  | `rgba(255,255,255,.78)` | Body copy on navy (≈8:1 — safer than `--ceil` at size)  |
| Structure / label | `#3393d6` (secondary)   | Axis labels, rules, inactive quadrant strokes           |
| Focus accent      | `#eaab2d` (accent)      | **Reserved**: the active quadrant + the two questions   |

One accent hue, used for exactly one job — *what the video is pointing at right now*.
Yellow never decorates.

## Type

Proxima Nova only, self-hosted `woff2` (400 / 700 / 900) from
`brand/visual-identity.md`'s brand font, vendored into `assets/fonts/`.

House style suggests a serif + sans pairing; **overridden deliberately** — brand truth is
Proxima Nova for headings *and* body on every SCLA surface, and a serif here would be
off-brand. Hierarchy is carried by weight, size and colour instead of by family.

| Role            | Size  | Weight | Tracking |
| --------------- | ----- | ------ | -------- |
| Display / hook  | 104px | 900    | -0.02em  |
| Section heading | 72px  | 900    | -0.02em  |
| Quadrant name   | 56px  | 900    | -0.01em  |
| Body / detail   | 40px  | 400    | 0        |
| Axis + eyebrow  | 28px  | 700    | 0.14em, uppercase |

40px body floor — the same floor the SCLA pipeline landed on for phone viewing.

## Frame

- 1920×1080, 120px frame padding, nothing outside a 1680×840 safe box.
- Focal element: the matrix, optically centred at 960×560 (slightly high — the lower band
  carries body copy).
- Edge anchors: program eyebrow top-left, lesson title top-right hairline; no footer band.
- Supporting detail: axis labels sit *outside* the grid on its left and top edges.
- Background treatment: navy radial lift behind the matrix + a 120px hairline grid at 4%
  + one ghost word per act at 3%. All three carry a slow shared drift.

## Motion

- Entrances 0.4–0.7s, `power3.out`; exits 0.3s, `power2.in`.
- The matrix itself only ever *transforms* — it is never rebuilt or re-entered.
- Nothing already on screen re-animates in place once it has settled.
- Ambient: one shared 14s breath on the background layer, finite repeat count.
