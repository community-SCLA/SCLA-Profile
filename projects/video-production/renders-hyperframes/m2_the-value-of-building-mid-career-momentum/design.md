# Design — One Career Map

## Chosen concept

The revised video is one calm, full-frame career map. A single gold NEXT token
moves through a fixed field from accumulated experience to named direction.
The map stays present so the viewer never has to relearn the visual language.

## Visual carrier

- **Gold decision token:** the learner's deliberate next move.
- **Blue structures:** experience, available options, and the system around the
  choice.
- **Outlined paths:** relationships only; every line connects named states.
- **Paper panels:** moments when thinking becomes explicit and usable.

## Beat-to-frame map

- 0.000–12.240: oversized type establishes accumulated experience while the
  decision token remains unresolved at the map intersection.
- 12.240–28.450: frustration and ambition pull the decision token while a dense
  thought field contrasts with a nearly empty paper panel.
- 28.450–41.600: a closed activity loop demonstrates drift, then a named move
  physically opens it into direction.
- 41.600–53.750: pause, reassess, and choose lock in sequence; small steps then
  accumulate into a visibly compounding structure.
- 53.750–65.940: a gap breaks the chain, then the 90-day goal anchors the larger
  six-to-twelve-month horizon.
- 65.940–81.395: one role branches into promotion, lateral move, and role redesign.
- 81.395–106.665: the camera focuses on how each path changes a different
  dimension: scope, context, or role shape.
- 106.665–119.040: the paths appear equal until values, energy, and real-life
  constraints align one route to the learner's life now.
- 119.040–136.759: all valid routes share the same value; scattered noise
  collapses into one named move and a chain of small compounding steps.

## Frame system

- 1920 × 1080 with 120 px frame padding and content above 960 px.
- The program label is the only persistent chrome.
- Deep navy is the continuous environment. Full paper or cultured panels appear
  as objects inside it rather than as alternating slide backgrounds.
- The carrier fills nearly the whole safe frame. Copy stays above 38 px, with
  most headlines between 84 and 116 px and no dense explanatory paragraphs.
- The three paths use one shared comparison state, then receive distinct focus.
  The fit beat switches to filters, and the final beat switches to one paper goal.
- Most frames contain a strong text focal point and a separate teaching focal
  point connected by layout or motion.

## Typography and palette

Use the workspace Proxima Nova files at 900 / 700 / 400. Headlines are 66–104 px;
support copy is 34–44 px; labels are 20–24 px uppercase. Only local token colors
are used: deep navy and navy, paper and cultured, blue for structure, and gold for
the deliberate choice.

## Motion rules

- A single route line draws once and persists.
- The active route node changes only when the argument changes.
- Choice rows reveal in sequence; the selected relationship changes without
  rebuilding the frame.
- Text enters once, settles, and stays stable for the spoken thought.
- All motion is finite, deterministic, and attached to the single paused GSAP
  timeline.
