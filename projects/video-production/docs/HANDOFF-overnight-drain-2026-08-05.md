# HANDOFF — Overnight drain, 2026-08-05 (owner-authorized, unattended)

**Mission:** every READY lesson (35 at handoff) built and published to Wistia
before ~06:00 UTC 2026-08-06. Owner authorization, 2026-08-05: "You can
bypass human approval. We just need to have them built and published on
Wistia as quickly as possible." The batch PILOT GATE is **satisfied** —
`career-building-is-a-repeatable-process_early-career-boost` was
owner-approved and shipped on 2026-08-05. Do NOT stop for another pilot and
do NOT wait for human previews. Stop-the-line conditions are listed at the
bottom; everything else is per-video triage.

## Orient (in this order, nothing else)

1. `bash scripts/batch-status.sh` — the live queue, read from disk. Trust it
   over this document; it is the resume key after any interruption.
2. If the pilot still shows anything short of PUBLISHED, finish it first:
   `bash scripts/batch-ship.sh career-building-is-a-repeatable-process_early-career-boost early-career-boost`
   → grade the sampled frames → same command with `--publish`.
3. `.claude/rules/video-production.md` auto-loads — the drain follows it,
   including tonight's new lines (parallel cloud renders, bounded retry).

## Tonight's deltas from the standard /render-lessons flow (owner-decided, see decisions/log.md 2026-08-05 "Cloud rendering, and the overnight drain")

1. **Render backend is CLOUD.** `renders-hyperframes/_run/RENDER-BACKEND`
   already says `cloud`; `batch-ship.sh` handles everything (HeyGen-hosted
   render, parallel-safe, no machine render lock). You never call the cloud
   CLI yourself.
2. **Four lanes, staggered ~10 minutes.** One cold builder subagent per
   video, up to 4 concurrent (the shared HeyGen TTS quota is the ceiling —
   a 5th lane just queues on 429s). `bash scripts/build-claim.sh <stem>
   <program>` is the only way a build starts; the workspace mkdir is the
   collision lock.
3. **No pilot stop, no human previews.** Approved above.
4. **Bounded retry.** A builder gets at most TWO revision passes against any
   failing gate, then quarantine the video and refill the lane. Never let
   one video eat a lane for hours.
5. **Taste: judge ONLY against the two APPROVED rows** in
   `design-system/docs/taste.md`. The shipped career-building cut is
   explicitly NOT a reference (owner). Concept competition per video runs as
   normal; a FLAT critic verdict buys exactly one revision pass (standing).
6. **Vision reviews are yours, on real pixels.** Precheck contact sheets and
   the post-render sampled frames are graded by the orchestrating session
   reading the images — never accept a builder's own claim of visual
   quality (standing certification rule).

## The per-video loop (what each lane does)

1. Claim: `bash scripts/build-claim.sh <stem> <program-slug>`
2. Concept competition (/render-lessons B2): two pitch lenses + one vision
   judge → `_concepts/<stem>/CONCEPT.md`. Run the next video's competition
   while the current one builds — keep it off the critical path.
3. Builder subagent authors per `renders-hyperframes/_run/BUILD-KIT.md`
   through `bash scripts/build-gate.sh <stem>` exit 0 + precheck OK.
4. Release: `bash scripts/build-release.sh <stem>`
5. Ship render: `bash scripts/batch-ship.sh <stem> <program-slug>` — cloud
   render + verify; ends with `AWAITING_VISION` + sampled frame paths.
   These run in PARALLEL across lanes (no lock on the cloud path).
6. Grade the frames (real pixels), then publish:
   `bash scripts/batch-ship.sh <stem> <program-slug> --publish`
   Publishes serialize on their own lock; each commits its ledger row
   before the next — that commit is what makes the run interruption-proof.

Queue order: exactly `batch-status.sh` order (early-career-boost first).
SKIP the NEEDS SCRIPT and RAW items — owner-blocked; do not refine, build,
or improvise them.

## Known landmines (owner-acknowledged)

- `m0_welcome-to-mid-career-momentum` says "hashtag questionsupport" — the
  channel can't be verified; owner was asked and chose to ship as written.
- **Disk:** ~9GB free at handoff; `batch-ship` quarantines below 4GB.
  Publishing prunes each workspace in place, which recovers space — if disk
  tightens, publish before claiming new builds.
- **HeyGen wallet:** $225.72 at handoff. Check every ~8 videos:
  `bash scripts/with-secrets.sh npx hyperframes auth status`. If the wallet
  falls below ~$40 with videos remaining, flip
  `renders-hyperframes/_run/RENDER-BACKEND` to `local` and continue — local
  renders serialize (~7 min each) but cost nothing.
- **TTS 429s** at ~30 req/window are normal; `audio.mjs` paces itself.
  They are why lanes stagger — never treat them as failures.

## Stop the line ONLY when

- A publish/commit fails (ledger integrity — a live-but-unrecorded video is
  the worst state; `batch-ship` writes the URL into the quarantine record).
- Two consecutive videos quarantine for the SAME cause — that's systemic;
  fix the cause before feeding it more videos.
- The wallet is exhausted AND the local fallback also fails.

## Close-out (before the 4-hour window ends, even mid-queue)

1. `bash scripts/batch-status.sh --write` (regenerates PIPELINE-STATUS.md).
2. Snag-log retro entry per `render-qa/logs/snag-log.md` header rules
   (hook-enforced).
3. Report, in lay terms: videos published (count + the Delivered table),
   quarantines with reasons, wallet remaining, and the exact resume command
   (it is always: reopen, `bash scripts/batch-status.sh`, continue this
   handoff from "Orient").

An interruption at ANY point strands nothing: published.tsv rows are
committed per video, and everything else is a folder on disk that
batch-status.sh reads. Resume is always safe.
