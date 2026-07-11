# Video Request Queue (Notion)

The team-facing intake for video production. Anyone at SCLA requests a video by
adding a row to the Notion queue — no Claude Code required. A Claude session
works the queue end-to-end; humans hold exactly two gates (script approval, QA).

**Database:** [SCLA Video Production Queue](https://app.notion.com/p/280a361540ab4fd6a0267c5fbea1e6bd)
(data source `collection://e99fc1e7-d9a1-4be9-9bda-b9d79ef9ae57`), a child of the
"SCLA Workspace" hub page. Team instructions live in Notion:
["How to Request a Video"](https://app.notion.com/p/3968dcf30bdb81bbb0ddecc352b23e22).

## The flow

| # | Status | Moved by | What happens |
|---|---|---|---|
| 1 | Requested | Team member | Create a row; fill Program, Video type, Due date, and **Script status** (Needs drafting · Provided as-is · Provided, needs refinement). Paste source material into the page body under a `## Source material` heading. If you already have a script — even a rough draft — paste it under `## Provided script` and set Script status accordingly (a rough draft you want Claude to tighten = **Provided, needs refinement**); put any change requests under `## Refinement notes`. Never leave source material out — Claude must not invent SCLA content. |
| 2 | Script drafting | Claude | Read Script status, the page body, **and Notes** before acting. **Needs drafting:** draft narration from the source material using the matching template in `script-templates/`. **Provided as-is:** don't redraft — file the provided script verbatim. **Provided, needs refinement:** refine the provided script per `## Refinement notes` + Notes, don't rewrite from scratch. In all three cases save to `lesson-scripts/<program-slug>/` (naming: `lesson-scripts/README.md`), set **Script location**, and paste the result into the page for review. |
| 3 | Script awaiting approval | Claude | Set when the draft/script is posted. Requester (or program owner) edits/comments directly on the page. |
| ↺ | Revision requested | Requester | Requester wants changes after reading the draft. Claude picks this row up, re-drafts from the page's current text + `## Refinement notes` + Notes, re-saves to the repo, and returns the row to **Script awaiting approval**. Loops until approved. |
| 4 | Script approved | **Human only** | The mandatory script gate — never automated. |
| 5 | In production | Claude | **First, sync the approved script:** copy the approved text from the Notion page back over the repo `.txt` — after approval the page is the source of truth, and production must render what was approved, not the pre-edit draft. Then build by Video type: **Illustrated** — per-lesson build workspace at `renders-hyperframes/<script-stem>/` per `design-system/CLAUDE.md`, in the assigned style package (`frame.md` → "Style packages"), `npm run check`, scene-midpoint snapshots posted to the page. **HeyGen avatar** — `avatar-pipeline/`. **Social clip** — draft with `script-templates/social-script-prompt.md`, then build on the illustrated or HeyGen path per the row. |
| 6 | QA review | Claude → human | Claude sets the status and posts snapshots/render; a human runs `script-templates/qa-checklist.md` (illustrated section) and records sign-off in **QA reviewer**. |
| 7 | Approved to publish | **Human only** | The mandatory QA gate — never automated. |
| 8 | Delivered | Claude | Final MP4 rendered and renamed to the script stem, then **uploaded to Wistia** — the `.mp4` is not committed to the repo; the approved `.txt` script stays in `lesson-scripts/<program-slug>/` as the source of truth. Set **Final video** to the Wistia share/embed URL and set **Delivered date**. Then retire the build workspace: `bash scripts/archive-lesson.sh <script-stem>` (moves it to `renders-hyperframes/_archive/<stem>/`, local-only — see `renders-hyperframes/README.md`). |

Blocked (any stage): set Status = Blocked and say why in Notes. To resume, a human moves the row back to the status it should re-enter at and clears the blocker note.

## Working the queue (Claude session)

1. Query the database for rows in Requested, **Revision requested**, Script
   approved, or Approved to publish. **Skip any row whose Name starts with
   `[EXAMPLE]`** — those are pinned samples, never work them. Work rows in
   **Priority order (Rush → High → Normal → Low), then earliest Due date**.
2. Advance each row through the transitions Claude owns: 1→2→3, Revision→3,
   4→5→6, 7→8.
3. **Never move 3→4 or 6→7** — those are the human gates.
4. **Verify gate preconditions before acting on a gate status.** On Script
   approved, confirm **Script location** is set and the repo `.txt` exists before
   entering production. On Approved to publish, confirm **QA reviewer** is filled.
   If a precondition is missing, set Status = Blocked with the reason instead of
   proceeding — a gate status alone isn't proof the work behind it happened.
5. **HeyGen avatar is currently blocked** — the HeyGen API key returns 403 on
   every endpoint (see `design-system/CLAUDE.md` → "Upgrade path"). Set any HeyGen
   row to Blocked citing the key issue rather than leaving it stuck in production.
6. **Program = Other:** there's no program slug, so file to
   `lesson-scripts/other/<request-slug>/` and set Script location explicitly. Flag in
   Notes so a human can refile if the video belongs to a real program.
7. Style package: use the row's pick; on "No preference (rotate)", count only that
   program's delivered `.mp4` files that have a matching illustrated script stem in
   `lesson-scripts/<program-slug>/` (ignore loose scripts and HeyGen deliveries) and take
   summit → horizon → cadence in order (count mod 3). Record the chosen package on
   the row so two same-program videos in flight at once don't collide on the count.
8. Post progress on the Notion page (script text, snapshot images, blockers) —
   the requester follows along there, not in the repo.

## Database schema

Name: **SCLA Video Production Queue**

| Property | Type | Options |
|---|---|---|
| Name | Title | Working title of the video |
| Program | Select | Early Career Boost · Career Readiness Accelerator · SCLA Leadership Program · Other |
| Video type | Select | Illustrated lesson (default) · HeyGen avatar · Social clip |
| Script status | Select | Needs drafting (default) · Provided as-is · Provided, needs refinement |
| Style package | Select | No preference (rotate) · Summit · Horizon · Cadence |
| Status | Select | Requested · Script drafting · Script awaiting approval · Revision requested · Script approved · In production · QA review · Approved to publish · Delivered · Blocked |
| Priority *(v2)* | Select | Rush · High · Normal (default) · Low — queue is worked in this order, then by Due date |
| Format *(v2)* | Select | 16:9 landscape (default) · 9:16 vertical · 1:1 square — social clips especially must say which |
| Requested by | Person | |
| Script approved by *(v2)* | Person | Who moved 3→4 — the script gate's audit trail, symmetric with QA reviewer |
| QA reviewer | Person | Who signed off the QA gate |
| Due date | Date | |
| Delivered date *(v2)* | Date | Set by Claude at Delivered — feeds throughput tracking against the monthly hours target |
| Requested date *(v2)* | Created time | Built-in Notion property — surfaces cycle time next to Delivered date |
| Target length | Select | ≤1 min · 1–3 min · 3–5 min · 5+ min |
| Source link | URL | Optional link to source doc; primary source material goes in the page body |
| Script location | Rich text | Repo path once drafted, e.g. `lesson-scripts/early-career-boost/<stem>.txt` |
| Final video | URL | Wistia share/embed URL of the delivered video (hosted on Wistia, not committed to the repo) |
| Notes | Rich text | Blockers, context. Change requests belong in the page body under `## Refinement notes`, not here — Notes is scanned but the page body is where the work happens. |

Properties marked *(v2)* are spec'd here but **not yet created in Notion** — this
session had no Notion access. First queue-working session: add them to the
database (defaults as noted), then delete this paragraph and the *(v2)* markers.
Until they exist, treat missing Priority as Normal and missing Format as 16:9.

**Deliberately not schema:** language (add a Language select only when the first
real translation request lands — HeyGen API is blocked anyway), workspace path
(derivable — see below), and per-scene detail (lives in the page body).

## Where every artifact lands (keyed off the script stem)

The script filename stem `<section>_<program-slug>_<YYYY-MM-DD>` (set at step 2,
recorded in **Script location**) determines every other location — nothing else
needs tracking:

| Artifact | Location | Git? |
|---|---|---|
| Approved script | `lesson-scripts/<program-slug>/<stem>.txt` | tracked |
| Build workspace (while in production) | `renders-hyperframes/<stem>/` | gitignored |
| Snapshots / draft / progress | the row's Notion page | Notion |
| Final video | **Wistia** (upload) + Wistia URL in the row's **Final video** field | not in git |
| Retired workspace (after Delivered) | `renders-hyperframes/_archive/<stem>/` | gitignored |

## Automation — how the queue runs without micromanagement

**Claude side (polling):** the **"SCLA video queue worker"** scheduled routine
(claude.ai cloud; ID + URL in `endpoints.md` → "Claude Code routines") runs
weekdays at 9:13 and 15:13 UTC against this repo with the Notion connector
attached, and works the queue per this file. Each run drains every transition
Claude owns and exits; rows at a human gate are untouched, and drafted scripts
arrive as PRs to `main`. Cadence is a dial — raise it when volume grows; runs
are idempotent (a run that finds nothing actionable does nothing). If a cloud
run can't complete a production step (local-toolchain renders), it sets the row
Blocked with the reason for a local session to pick up — cloud drafts, local
renders.

**Notion side (one-time manual setup, in the database's ⚡ Automations — the API
can't create these):**

1. Status → **Script awaiting approval**: notify **Requested by** ("your script
   is ready for review").
2. Status → **QA review**: notify the QA reviewer group/channel.
3. Status → **Blocked**: notify **Requested by** and the team channel.

Those three notifications close the loop on the human gates — the two statuses a
human must act on, plus the one that means the pipeline stalled. New-request
pings to Claude aren't needed: the polling routine picks up Requested rows on
the next run.

Page body of each row carries, under labeled headings: `## Source material` (from
the requester), optionally `## Provided script` and `## Refinement notes` (from the
requester), then the draft script and snapshot images (from Claude).

A worked-example row ("Better Decisions Come From Better Criteria") shows the team
what a filled-in request looks like. Keep it pinned with a **`[EXAMPLE]` Name
prefix** so the queue query skips it (see "Working the queue" step 1); don't
deliver it.
