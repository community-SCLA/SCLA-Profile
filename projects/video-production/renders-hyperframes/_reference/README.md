# _reference/ — build workspaces kept as evidence, not as work

Underscore folders are skipped by every workspace scan (`batch-status.sh`,
`theme_for.py`, `preflight`), so a build filed here stops reporting as an ORPHAN
and can never be mistaken for something waiting to ship. That is the whole
mechanism: naming is the disposition.

**`renders-hyperframes/` is gitignored, so everything here is LOCAL-ONLY.** It
survives on the machine that built it and nowhere else. The durable record is
always the numbers written into `decisions/log.md`; these folders are the
artifact those numbers were measured from, kept so a future session can re-run a
gate against a build whose verdict is already known.

## What is here

- **`build-direction-before-you-build-a-plan_early-career-boost_2026-08-04-freeform-backup`**
  — the cut the owner rejected as "SO boring" on 2026-08-04: 17 beats, 6.47
  beats/min, median 9.12s, longest static span 3.75s. It passed every gate in
  `render-qa/src/` clean, which is what exposed that the gate set was measuring
  animacy while the owner was responding to idea rate. One of the two reference
  points the `check_pace.py` thresholds are calibrated between; the other is the
  APPROVED cut of the same lesson, still live at the Wistia URL in
  `published.tsv`. See `decisions/log.md` 2026-08-04 "Owner verdict: gate set
  approved the rejected cut, quarantined the approved one".

- **`career-building-is-a-repeatable-process_early-career-boost_2026-08-05-thin-carrier-backup`**
  — the cut the owner rejected on 2026-08-05 as "pretty boring … lackluster
  illustrations": 42 beats, gate-clean INCLUDING the armed pace gates. Its
  carrier is a minimal 6-dot circle on near-empty navy frames for the whole
  runtime — the cheapest legal satisfaction of carrier persistence + low churn.
  The third calibration point for taste: rejected-THIN, opposite failure to the
  2026-08-04 rejected-SLOW cut above. Its `snapshots/contact-sheet-*.jpg` are
  the visual evidence the taste judges grade against. See `decisions/log.md`
  2026-08-05 "Taste becomes a judged stage" and
  `design-system/docs/taste.md`.

Never route a build here, and never copy compositions out of it — a rejected cut
is a measurement, not a model.
