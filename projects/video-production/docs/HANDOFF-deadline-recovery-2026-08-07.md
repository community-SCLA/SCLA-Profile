I only see one workspace populated for review. Which ones are ready for review? # HANDOFF — Deadline recovery and pipeline reconciliation, 2026-08-07

**Mission:** continue the SCLA lesson-video factory without rebuilding completed
work, losing approvals, or touching work owned by another session. The owner has
a hard four-hour deadline. Return every gate-clean workspace for rolling review
immediately, then render and publish each approved lesson independently.

**This handoff supersedes the review-bypass instructions in
`HANDOFF-overnight-drain-2026-08-05.md`.** Current owner direction requires
rolling review and durable per-lesson approval.

## Non-negotiable session boundary

- **Do not touch** `m2_welcome-and-using-career-transitions-as-leaps-ahead`.
  A separate local session owns it. At 2026-08-07 15:58 UTC that session had
  correctly recorded it as `APPROVED — ready to render`.
- Do not run, approve, render, publish, retry, preview, or change shared backend
  settings for that stem unless the owner/local session explicitly hands it
  back.
- Do not redelegate any stem that already has a workspace. Resume its files.
- Never delete narration, timing, snapshots, or a workspace to reacquire work.
- Never load or route to `_archive/`.

## Fresh-session boot sequence

Read only the standard video route, then use the live control plane:

```bash
bash projects/video-production/run.sh status --json
bash scripts/batch-status.sh
```

Trust those commands over the counts in this handoff. Then:

1. Exclude the Welcome stem above.
2. Start previews for the three `NEEDS REVIEW` stems listed below.
3. Continue existing design-only workspaces locally in unique parallel lanes.
4. Do not run `run.sh batch --all` merely to resume work; selection used to
   erase durable state and is unnecessary for existing folders.

## Verified checkpoint — approximately 16:21 UTC

Live totals:

- 14 published
- 3 needs review
- 1 approved (the separately owned Welcome lesson)
- 2 rejected and recoverable
- 9 stalled design-only workspaces
- 10 queued scripts with no workspace
- 1 raw script
- 1 `NEEDS SCRIPT` content blocker
- 0 rendered and waiting to publish

### Gate-clean and ready for owner review now

These have production HeyGen narration, timing, mounted audio, snapshots, and a
green deterministic gate. They have **not** been approved, rendered, or
published:

1. `m2_the-value-of-building-mid-career-momentum`
   - Live preview:
     `https://curly-journey-6vgr9pwpp59jh4wv-3004.app.github.dev/#project/m2_the-value-of-building-mid-career-momentum`
   - 21 beats, 136.759s, exact 348/348 script match
   - Existing narration was sliced losslessly; no new TTS call
   - pace 9.21 beats/min; carrier churn 5.89%
2. `m5_skills-for-the-ai-era`
   - 36 beats, 207.338s, exact 525/525 script match
   - pace 10.42 beats/min; carrier churn 5.79%
3. `m3_the-two-sided-work`
   - 27 beats, 170.910s, exact script match
   - pace 9.48 beats/min; carrier churn 5.96%
   - nonblocking warning: no `narration.words.json`, so the flat-word adapter
     deferred the in-scene silence rule

Launch rolling previews one stem at a time:

```bash
bash scripts/review.sh m2_the-value-of-building-mid-career-momentum
bash scripts/review.sh m5_skills-for-the-ai-era
bash scripts/review.sh m3_the-two-sided-work
```

Record only approvals the owner actually gives. Approval must survive later
batch selection after the control-plane fix below.

## What the overnight work actually produced

“Design-only” means a real HyperFrames folder with `index.html`, concept, and
design source. It does **not** mean review-ready. The overnight Cloud authoring
contract explicitly said `Do not call HeyGen`; the local coordinator never
resumed the returned sources through narration, timing, snapshots, and gates.

The initial ten planned workspaces all had HTML but lacked production audio,
`qa/PREFLIGHT-OK`, and MP4s. `m3_the-two-sided-work` had the same state. The
HeyGen key was not the limiting factor; the TTS stage was never invoked.

Today, production narration succeeded through `scripts/video-audio.sh` for the
recovered workspaces. A sandboxed Infisical call can return empty JSON; when
that occurs, rerun the approved wrapper with required network escalation. Do
not bypass the wrapper or replace the configured voice.

## Confirmed bookkeeping defects and fixes

At 2026-08-07 07:15 UTC, whole-queue selection called `new_run()` and created a
fresh `run.json`. The old implementation reset:

- `review.stems` and its approval timestamp
- cloud clean-render history
- circuit-breaker state
- recorded results/closeout facts

It also wrote `stage: ready` for every ready script even if a workspace already
existed. That is why an owner-approved lesson appeared unapproved and why
existing work looked untouched.

Uncommitted fixes are present in:

- `projects/video-production/render-qa/src/run_state.py`
- `projects/video-production/render-qa/tests/test_control_plane.py`

The fixes preserve approvals and operational history across reselection and
label existing folders `workspace`. The exact regression suite passed:

```text
python3 projects/video-production/render-qa/tests/test_control_plane.py
51 passed, 0 failed
```

The repository's only full lint/test entry point also passed at handoff:

```text
bash scripts/lint-refs.sh
16/16 checks healthy; render-qa suite 97 assertions pass
```

Do not discard these edits. Review and commit them intentionally without
scooping up unrelated workspace files.

## The “upload signature” failure

This is unrelated to Codex Cloud source authoring, Codex-driven narration, or
the owner's HeyGen API key. For
`m2_four-kinds-of-career-transition_career-transitions`, HyperFrames completed
source/audio/preflight, zipped the workspace, and attempted a direct upload to
HeyGen-hosted AWS storage. AWS returned:

```text
403 Forbidden — SignatureDoesNotMatch
```

Evidence:

`projects/video-production/renders-hyperframes/m2_four-kinds-of-career-transition_career-transitions/qa/logs/20260806T235012Z-cloud-render.log`

Do not rebuild this lesson. After the Welcome-owning local session is finished,
either verify that the cloud signing cause changed and authorize one bounded
retry, or use the local render backend as the deadline-safe fallback. The
backend switch is shared state; coordinate it before changing it.

The other rejected workspace,
`m2_four-kinds-of-career-transition_mid-career-momentum`, already has narration
and `PREFLIGHT-OK`. It was incorrectly sent through the publish/release path
without a current `qa/VERIFIED` MP4 marker. Its failure receipt recorded
`command: unknown`, so recover by rendering and verifying after its approval;
do not rebuild its source or narration.

## Remaining existing workspaces — resume locally

These contain source but still need narration, timing, gate repair, and rolling
review. Use one worker per unique stem and enforce the shared TTS limit of two:

### Mid-Career Momentum

- `m6_youve-built-momentum`

### Career Transitions

- `m4_building-your-carry-forward-inventory`
- `m5_testing-your-next-chapter`
- `m5_the-story-that-makes-the-change-legible`
- `m7_your-reinvention-roadmap`

### Entrepreneur Accelerator

- `m1_reframing-entrepreneurship-and-going-solo`
- `m3_choosing-your-solo-model`
- `m4_building-visibility-on-your-own`
- `m5_making-solo-work-sustainable`

The successful recovery pattern was:

1. Claim the existing stem through the required build lifecycle.
2. Preserve existing work and narration.
3. Run `scripts/video-audio.sh` only if production narration is absent.
4. Replace oversized placeholder scenes with semantic beats while preserving
   the exact script.
5. Generate timing through the shared timing tool.
6. Mount framework-owned audio for every beat.
7. Capture midpoint snapshots and run the full gate with network access where
   the HyperFrames inspector requires npm.
8. Fix measured findings, release the lease, launch its preview, and refill the
   lane immediately.

## Untouched queue after workspace recovery

Ten Mid-Career Momentum scripts remain queued with no workspace. Build these
only after refilling available lanes around existing-workspace recovery:

- `m2_mid-career-mindsets-and-limiting-beliefs`
- `m3_building-your-future-you-resume-pt1`
- `m3_discover-experiences-that-support-your-next-move`
- `m3_from-history-to-signal`
- `m3_how-to-reposition-your-career`
- `m3_rewrite-your-linkedin-for-future-you`
- `m3_using-the-resume-builder-tool-pt2`
- `m4_finding-new-peers-sponsors-and-opportunity-holders`
- `m4_visibility-actions`
- `m4_who-will-walk-this-next-chapter-with-you`

## Content blockers — do not improvise

- `m4_visibility-actions-what-they-are-and-how-to-practice-them` is `NEEDS
  SCRIPT`. Its body duplicates another lesson and never teaches visibility
  actions. It requires real owner-supplied narration.
- `m2_why-build-your-own-path` remains raw and needs the explicit script
  refinement workflow before video authoring.

These two items make a literal “everything published in four hours” promise
impossible without new content/authorization. Surface them clearly; never hide
them as pipeline delay.

## Deadline proposal

1. **Review the three clean previews immediately.** Do not wait for siblings.
2. **Resume the nine design-only workspaces in three-worker waves.** The source
   concepts already exist; do not re-author them from scratch.
3. **Keep TTS at two concurrent jobs.** HeyGen production narration is working.
4. **Render approved lessons independently.** If cloud direct-upload signing
   remains broken, coordinate a switch to serial local rendering. A local
   render is slower but avoids the failed AWS upload path.
5. **Recover both rejected lessons from their current artifacts.** No source or
   narration rebuild.
6. **Start untouched scripts as lanes free up**, but never let them displace a
   nearly review-ready workspace.
7. **Publish serially and trust `published.tsv` for completion.** Never upload
   an unverified MP4 or redo an already published stem.

## Dirty-worktree warning

The overnight source workspaces and today's recovery edits are uncommitted.
They belong to the owner/current sessions. Do not reset, delete, or bulk-clean
the tree. Scope any commit carefully and preserve unrelated changes.

## Definition of done for the next session

- Every gate-clean stem has a live review URL immediately.
- Every owner approval is recorded and remains present after any scope change.
- Every approved stem is rendered, verified, and published independently.
- Existing workspace artifacts are reused; no duplicated TTS or authoring.
- Rejections have one exact cause and recovery record.
- The Welcome lesson remains untouched until its local session hands it back.
- Final reporting distinguishes published, awaiting review, recoverable,
  queued, and owner-blocked work in plain language.
