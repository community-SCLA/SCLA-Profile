# Taste — the judged layer above the gates

**What this is.** Calibration for the three places an agent exercises visual
judgment: the concept judge (`/render-lessons` B2), the advisory taste lane in
the precheck vision review, and the builder's own contact-sheet self-review.
It is NOT a gate and must never become one: every numeric floor in this
pipeline was calibrated against a real rejected build, and the taste bracket
below is three cuts — enough to point judges, not enough to fix constants.
The 2026-08-04 incident (a constant set that approved the boring cut and
quarantined the approved one) is why taste lives in judges and numbers live
in `render-qa/src/`.

## The target, one sentence

**One concrete, nameable carrying object — rich enough to sustain the whole
runtime — that visibly gains, loses, or re-arranges something as the argument
advances, and pays off**: the closing frame could not have been drawn at 0:10.

## The bracket — three reference cuts, all verdicts owner-given

| Verdict | Cut | Signature | Evidence (local) |
| --- | --- | --- | --- |
| **APPROVED — rich carrier** | `m1_mini-syllabus` freeform trial (2026-08-05) | One map/object built early, then only ever re-read; ~10 beats/min | `experiments/m1-mini-syllabus-freeform-trial/` — `design.md` + `snapshots/contact-sheet-*.jpg` |
| **APPROVED — rich carrier** | `build-direction-before-you-build-a-plan` Jul 30–31 cut | A field of 48 marks arrives once, then is only ever re-grouped; 10.26 beats/min, churn 3.34% | `renders-hyperframes/build-direction-before-you-build-a-plan_early-career-boost/` — `design.md` (snapshots pruned; numbers in `decisions/log.md` 2026-08-04) |
| **REJECTED — slow** ("SO boring") | same lesson, 2026-08-04 pilot | 6.47 beats/min, each idea takes ~9s, nothing accumulates. Now caught by `check_pace.py` | `renders-hyperframes/_reference/…_2026-08-04-freeform-backup/snapshots/` |
| **REJECTED — thin** ("lackluster illustrations") | `career-building-is-a-repeatable-process`, 2026-08-05 pilot | Passed every gate incl. pace; carrier is a 6-dot circle on near-empty frames, never gains detail, no payoff — the cheapest legal pass | `renders-hyperframes/_reference/…_2026-08-05-thin-carrier-backup/snapshots/contact-sheet-*.jpg` |
| **SHIPPED — not a reference** | `career-building-is-a-repeatable-process`, 2026-08-05 rebuilt cut (the one delivered) | Gate-clean after the taste re-author; owner shipped it under the 24-hour deadline while calling it "definitely not my favorite" — never cite it as approved, never anchor a concept or design element on it | `renders-hyperframes/career-building-is-a-repeatable-process_early-career-boost/` |

**A shipped cut is not automatically a reference.** The 2026-08-05
career-building ship was a deadline call; the owner's standing instruction is
to keep judging against the two APPROVED rows alone.

The two rejections fail in OPPOSITE directions. The slow cut had churn and no
pace; the thin cut had pace and no substance. The approved cuts sit between:
low churn, high idea-rate, and a carrier that *earns* its persistence by
accumulating. `renders-hyperframes/` is local-only — if an evidence path is
missing on this machine, judge from the descriptions and numbers here.

## Concept-judge questions (B2 — before any HTML exists)

Grade each pitched concept on these; pick the winner, graft the loser's best
idea, and write the result to `_concepts/<stem>/CONCEPT.md`:

1. **Name the object.** Is the carrier a concrete, drawable thing (a map, a
   field of marks, a loop with stations, a path being walked) — or an
   abstraction wearing a shape ("dots on a circle")? If you can't say what
   it depicts, the builder can't draw it richly.
2. **The four-frame test.** Describe the frame at 25 / 50 / 75 / 100% of
   runtime. Are the four descriptions genuinely different pictures? If two
   read the same, the concept has dead stretches built in.
3. **What accumulates?** What is visibly MORE (or re-arranged, or resolved)
   at the end than at the start? "The highlight moves around" is not
   accumulation — that was the thin cut.
4. **Where is the payoff?** Name the beat where the object completes or
   re-reads (the whole loop visible at once, the field re-sorted into its
   final grouping). No payoff beat → no reason to persist an object at all.
5. **The lazy-build test.** Could a builder satisfy this concept with heading
   swaps against a static prop? If yes, the concept — not the builder — is
   the defect. Milestone frames in CONCEPT.md are the contract that closes
   this hole.

## Critic-lane questions (precheck — real pixels, viewer's eyes)

Read the contact sheets cold, as a viewer, alongside the reference sheets:

1. **The shuffle test.** Could you restore the sheet's order from the
   pictures alone? On the approved cuts you can — the object accumulates, so
   time has a direction. On the thin cut you cannot.
2. **Is the carrier earning its frame?** How much of the canvas does the
   object use, and does it reward a second look — or is it a small prop
   beside large empty space?
3. **Does anything gain detail?** Pick three sheets apart in time — has the
   object grown, filled, re-sorted, or resolved between them?
4. **Where do you check out?** Name the first beat range where a viewer's
   eyes have nothing new to do. Name specific beats — "beats 12–19 are the
   same picture with new headings" is actionable; "feels flat" is not.

**Verdict protocol:** `ALIVE` or `FLAT`, with the beats named. FLAT is
**advisory**: it buys exactly ONE revision pass (re-author the flat beats,
re-snapshot, re-gate) and then the build proceeds on the reviser's honest
report — it never quarantines a video by itself and never blocks the batch.

## Anti-patterns (each one already rejected by the owner)

- **Answering "boring" with motion or churn.** The slow rejected cut had the
  MOST inter-beat change of all four references. Richness is the object
  earning more, never the picture swapping faster. Idle wobble on settled
  content is separately banned (`check_motion.py`).
- **Splitting beats to hit pace numbers.** Caught by `twin-share`; also
  visible to the shuffle test.
- **Promoting any question above into a constant.** Bracket is n=3. A new
  reference verdict updates THIS file and `decisions/log.md`; thresholds
  change only with an owner-pinned reference build.
