# Combined Visual Review Contract

Review one gate-clean composition before render. Inspect representative stills
and the composition in motion. Do not rewrite the lesson, change machine gates,
or add a new human checkpoint.

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

`BLOCKING_DEFECT` covers visible correctness failures that make the cut unsafe
to render. `TASTE` covers whether the piece has a clear visual idea, evolving
composition, intentional rhythm, and enough variation to hold attention. A
flat result can require revision without being mislabeled as mechanically
broken. A lively result cannot excuse a blocking defect.
