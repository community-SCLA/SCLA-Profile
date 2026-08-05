---
name: refine-scripts
description: Refine one explicitly selected SCLA lesson script and verify its claims against the supplied source.
argument-hint: "<stem>"
disable-model-invocation: true
---

# Refine SCLA Lesson Scripts

Named-item refinement is the default. Start with:

```bash
bash projects/video-production/run.sh refine --stem STEM
```

Do not scan or drain other inbox entries. Program or whole-queue work requires
an explicit `run.sh batch --program PROGRAM` or `run.sh batch --all` selection.

For the selected raw script only:

1. Preserve its teaching claims, order, examples, caveats, and useful callbacks.
   Remove capture noise, production directions, duplicated phrasing, and visual
   notes that are not narration. Do not pad a short source.
2. Keep every number, named framework, program name, URL, attribution, and CTA
   faithful to the supplied source. Do not add brand-language filler.
3. Run `qa-facts` with the raw/source path and candidate refined path. Fix only
   changes supported by that source. A missing source is a blocker.
4. Run the script-mode copy check. On success, move the stem from `inbox/` to
   `ready/` using the existing lifecycle and update the human ledger once.
5. Regenerate status mechanically, then report the selected stem and verdict.

Never build, synthesize, render, publish, or touch an unrelated stem.
