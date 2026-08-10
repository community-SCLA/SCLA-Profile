# Combined Visual Review Contract

Review one gate-clean composition before render. Inspect representative stills
and the composition in motion. Do not rewrite the lesson, change machine gates,
or add a new human checkpoint.

The reviewer must be different from the concept author. For control-v3 builds,
record at least three inspected frame paths, one weakest frame, the number of
materially different layout families, and at least five beat-level descriptions
of what changed visually. The control plane hashes those snapshot files into the
receipt. Fewer than three layout families cannot proceed. Contract paraphrases
are not findings; cite visible evidence.

Return both verdicts independently:

```text
BLOCKING_DEFECT: PASS|FAIL
BLOCKING_FINDINGS:
- <timing, clipping, overlap, unreadable text, broken asset, false claim, or none>

TASTE: ALIVE|FLAT
TASTE_NOTES:
- <specific note about visual thesis, progression, rhythm, hierarchy, or none>

RECOMMENDATION: PROCEED|REVISE
```

Record the verdict through `run.sh visual-review` with `--reviewer`, repeated
`--evidence-frame`, `--weakest-frame`, and `--change-note` arguments plus
`--layout-families`. Never hand-write `qa/VISUAL-REVIEW.json`.

When the owner rejects a cut, first add a named fixture under
`render-qa/tests/fixtures/owner-rejections/` and its registry row. The shared
test iterates every row and proves its named rule fires. Only then record the
rejection with `run.sh reject`; the command refuses unarmed feedback.

`BLOCKING_DEFECT` covers visible correctness failures that make the cut unsafe
to render. A playback progress bar, rail, scrubber, signal trace, or sliding
completion line anywhere in the frame is always blocking. That includes a line
that fills for one scene's duration; it cannot substitute for explanatory scene
motion. Persistent module/scene numbers and repeated current/total counters are
also blocking because the deliverable is an MP4, not a slide deck.
Any whole-scene exit, entrance, or transition that interrupts a sentence is
also blocking. Treat adjacent clips that repeat unchanged graphics as one scene:
the visual carrier must persist while meaning-bearing elements evolve inside it,
and a new scene must wait for both a completed sentence and a material change in
idea or visual carrier.
Inspect the most crowded settled frame in every scene. Overlapping elements,
cramped near-collisions, labels laid across unrelated illustrations, inaccurate
structural geometry, or text that bounces, blinks, flickers, ripples, or
repeatedly pulses are blocking.
Treat scale and balance as correctness, not polish. Meaningful foreground detail
must use the whole content field while retaining the required padding. A large
copy block paired with an undersized teaching graphic, a tiny card cluster beside
an empty field, or repeated frames whose useful content stays confined to one
strip are blocking. For any spoken list or comparison, scrub through the
narration: the item being named must enter, highlight, transform, or resolve at
that point. Showing every item at once, then leaving all of them stagnant, is
blocking. Re-entering the same cloned carrier in consecutive scenes is also
blocking; persistence only earns credit when its meaning-bearing state develops.
Treat false interface affordances as blocking: an arrow, tab, button, or label
must not imply navigation or clicking in a non-interactive MP4. Also fail a cut
whose main visual content is confined to a small region for most of the lesson
while a large usable portion of the 16:9 frame remains unintentionally empty.
`TASTE` covers whether the piece has a clear visual idea, evolving
composition, intentional rhythm, and enough variation to hold attention. A
flat result can require revision without being mislabeled as mechanically
broken. Illustrations must clarify a mechanism, relationship, sequence,
comparison, or change; visual activity with no explanatory value requires
revision. Repeatedly exiting and repopulating the same list beside headings that
duplicate it is flat; one persistent list must visibly focus or transform as the
narration advances. A lively result cannot excuse a blocking defect.
