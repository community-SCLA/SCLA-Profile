# Source of Truth

**This directory is owned by the client's team.** After first generation by
the `source-of-truth-curator` agent, it is never auto-overwritten. Edit
freely.

## First-time generation

Run `/onboard` through to stage 5, or run the curator directly. It produces:

- `README.md` — the front door (this file, eventually)
- `charter.md` — mission, vision, values, quarter's definition of success
- `decisions-log.md` — running log of notable decisions
- `team-handbook.md` — how we work: meeting cadence, norms, tool ownership
- `rituals.md` — recurring meetings, reviews, demos
- `onboarding.md` — first-week checklist for new hires
- `HANDOFF.md` — what's complete, what still needs human input

## After first generation

A marker file `.source-of-truth-generated` is written. Re-runs detect it and
fill in only missing files (never overwrite existing ones).

## Collaboration guidance

The curator writes a "Ship Faster" pinned section at the top of `README.md`
linking the top 3 automation opportunities from `client/workflows/`. Update
it as the team ships changes.
