# Video production — for people

This folder turns SCLA lesson scripts into branded, fully-illustrated MP4s and
publishes them on Wistia, one video per lesson, across four programs:
Early Career Boost, Mid-Career Momentum, Career Transitions and Entrepreneur
Accelerator.

This page is orientation for a human reader. It carries no rules. The rules an
agent follows live in `PROCESS.md` and in the executable checks beside it —
if the two ever disagree, `PROCESS.md` and the checks are right.

## How to read the board

Every lesson has one small record on disk saying where it stands. To see all of
them at once, from the repo root:

```bash
python3 projects/video-production/checks/status.py
```

It prints, in order:

1. **Blocked on you** — lessons waiting on an owner decision, with the reason
   and how long they have been waiting. This is the only part that needs you.
2. **One table per program** — every lesson's stem, its stage, and the next
   action queued for it.
3. **A tally** — how many lessons sit at each stage.

The board reads the records at the moment you run it, so it is never stale.
There is no dashboard file to refresh and nothing to set up on a fresh clone.

A lesson moves through six stages: **scripted → narrated → composed → rendered
→ published**, plus **blocked** for anything waiting on a person. "Published"
means the video is live on Wistia and plays.

## What is where

| Path | What it holds |
| --- | --- |
| `brief.md` | The owner's original brief — the job, the taste, the constraints |
| `PROCESS.md` | The agent contract: the six stages and what must be true to leave each |
| `lesson-scripts/<program>/refined/` | The narration scripts — the durable source |
| `lesson-scripts/<program>/unrefined/` | Drafted, not yet narration-ready |
| `lesson-scripts/<program>/blocked/` | Quarantined pending an owner decision |
| `lessons/<program>/<stem>/` | One folder per lesson: its status record and, later, its build |
| `design-system/` | Tokens, fonts and logos — every visual choice traces here |
| `checks/` | The executable gates, plus the board reader |

Finished MP4s are not committed. Wistia is the delivery surface; the repo keeps
the scripts, the workspaces and the status records.

## If something looks wrong

Run the repo linter — `bash scripts/lint-refs.sh` from the repo root. It runs
the status-record gate along with every other repo check, and names the file
and the reason for anything it does not like.
