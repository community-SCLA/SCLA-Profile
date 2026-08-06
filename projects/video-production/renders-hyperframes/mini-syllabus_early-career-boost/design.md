# Design — Career Route

## Chosen concept

A single career route advances from **START HERE** to the learner’s first submitted commitment. It is one developing idea: every beat changes the route’s state, adds a milestone, or redirects it toward action.

## Visual carrier

The carrier is a gold route line with navy/blue milestone nodes. It begins as an orientation coordinate, becomes the track’s progress rail, loops through doing-based activities, passes a mindset switch, branches into career questions and practical moves, then merges Workbook and AI-tool inputs into a completed first milestone.

## Beat-to-frame map

| Beat | Narration role | Frame change |
| --- | --- | --- |
| s01 | Welcome | START HERE node activates beside the program title. |
| s02 | Reassurance | A warm arrival pulse expands from the starting node. |
| s03 | Broader journey | The route stretches from exploration through “what’s next.” |
| s04 | Foundation | The route becomes a rising foundation stair. |
| s05 | Milestones/progress | Checkpoints activate and a progress rail reveals ahead/complete states. |
| s06 | Learn by doing | The route cycles through click, reflect, upload actions. |
| s07 | Career Mapping Tool | A central map node branches to three possible pathways. |
| s08 | Help | The path detours one click to #questionsupport and rejoins. |
| s09 | Learning reveal | A route-marker wipe introduces “What you’ll learn.” |
| s10 | Mindset | A compass-like switch points from stuck to growth. |
| s11 | Beliefs transform | A limiting-belief barrier opens into an upward growth path. |
| s12 | Dream job | The first question branch draws to a destination marker. |
| s13 | AI-era skills | The second branch activates around a human/AI skill axis. |
| s14 | Practical movement | Networking, résumé, and search steps form one moving sequence. |
| s15 | Commitment statement | Workbook and AI-tool lanes merge into one statement line. |
| s16 | Choice/practice | Both lanes illuminate, then settle into one shared route. |
| s17 | Submit first step | The commitment locks into milestone one with a check. |
| s18 | Continue toward goals | Activities, milestones, and skills light ahead; route exits frame. |

## Motion logic

- One synchronous, paused GSAP timeline owns all motion.
- Every scene establishes its main claim in the first 1.2 seconds through transform and opacity only.
- Route segments reveal with `scaleX` or `scaleY`; nodes activate through scale, color, and opacity.
- Supporting elements settle before the narration completes. The final second adds one check, connection, merge, or forward extension.
- Each outgoing content layer fades and shifts in 0.3 seconds; backgrounds and footer furniture remain stable.
- IDs are fixed and there are no loops, random values, async callbacks, or sub-compositions.
