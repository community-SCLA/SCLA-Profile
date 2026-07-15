# Snag log — rolling render-session memory

**Read rule: ONLY the latest entry** — the first `## ` section below (use Read
with a line limit; never load the whole file). Every entry is self-contained:
its **Open** list carries every unresolved item forward, so the newest entry
is always the complete current state. Everything under it is append-only trail.

**Write rule** (every `/refine-scripts` / `/render-lessons` close-out;
hook-enforced after any render): **prepend** a new dated entry with three parts:

- **Open — owner-actionable only.** An item may roll forward ONLY if it
  genuinely needs the human: a decision, a credential/access, or an action
  outside the agent's reach. Anything the agent could do itself — code, config,
  a retry, filing an upstream bug — it MUST do this session; never roll
  agent-fixable work forward. Copy each still-unresolved owner item from the
  previous entry verbatim (keep its `since YYYY-MM-DD`), plus anything new this
  session hit that only the owner can clear. **If this list is non-empty, the
  session ASKS the human directly at close-out** — present each item as a
  decision (AskUserQuestion when the session is interactive), never as a log
  line the human has to go find. This file is the trail, not the human's inbox;
  the human should never have to open it. An item closes when resolved and then
  simply stops appearing.
- **Fixed this session** — snags hit and resolved, tagged
  `[env]/[tooling]/[authoring]/[upstream]/[defect]`, with resolution + time cost.
- **Promoted to docs** — durable lessons do NOT accumulate here: fix the owning
  doc (the skill's command block, `frame.md`, a preflight/verify check) in the
  same session and note where it went. The doc is the memory; this log is the
  trail that proves the loop ran.

Sibling: `BUILD-LOG.md` (dated build/overhaul/run records).

## 2026-07-15 · SHIP+PUBLISH `what-energizes-me`; demo reel re-rendered; fixed navy depth-drift under-registering at QA sampling

`/render-lessons SHIP what-energizes-me_early-career-boost_2026-07-10`, then owner-directed PUBLISH
and a demo-reel render, all in one session.

**SHIP.** Owner approved the hyperframe gate. Workspace already held three renders from the
build/preview loop; newest (`..._18-24-45.mp4`, 15.9 MB, 163.6s) post-dated `index.html` (17:55)
with no source file newer than it, so I **did not re-render** — verified the existing cut instead of
burning ~7 min. `verify_render.py` → **PASS** (container 163.63s video / 163.65s audio, presence 328
frames 0 violations). Cold vision subagent frame self-review → **PASS** (all 18 summit scenes depict
their sentence, on-cue, no clip/placeholder/dead/ghost; scenes 03 & 07 FLIP morphs resolve cleanly).
Filed `renders-mp4/early-career-boost/what-energizes-me_early-career-boost_2026-07-15.mp4` + `.qa/`
packet (verify-summary + 54 frames); ledger row 36 updated.

**PUBLISH.** Owner directed publish + waived MP4 review on the record. Uploaded via headless API
(`upload.wistia.com`, `WISTIA_API` from Infisical) to Wistia **"Early Career Boost"** (id `10733647`);
hashedId **`of5caanz21`**, https://sclc.wistia.com/medias/of5caanz21, duration 163.648s. Ledger row 36
= published + URL; script `git mv` `refined/`→`rendered/`; workspace archived via `archive-lesson.sh`.

**Demo reel.** Owner said render it. `npm run check` clean (0 lint, 46 text els pass WCAG AA — the
`scla-steps` label contrast now clears, so that prior Open item is resolved). Included the two
uncommitted template fixes (`scla-chips` ghost-ring amplitude + subBeats bug note; `scla-morph` loser
opacity 0.55→0.72 for contrast). Rendered `design-system_2026-07-15_19-04-01.mp4` (6.8 MB, 1m46s,
silent style-guide reel). `verify_render.py` → FAIL, but it's a lesson gate run on a SILENT reel
("no audio stream" + "while narration speaks" thresholds are N/A). Substantive signal is real: a 5.5s
pixel-static region at 64–69.5s (**`scla-stat`**, 62–70s) plus gray-zone static tails on `scla-quote`
(50–62s) and `scla-steps`. Root cause (diagnosed, NOT yet fixed — see Open): the 2026-07-15 depth-drift
amplitude re-tune landed on `scla-chips` ONLY (24/14→110/70px, after proving 24/14 moved <1 gray level
per 48×27 QA thumbnail px). All five navy depth-drift heroes still sit at 16–30px — under the checker's
registration threshold — so a narration-timed pure-hold navy scene would go static and fail the gate.

**Open:**
- [owner] **`scla-chips` `subBeats` renders inert** ([defect], found 2026-07-15) — the `.cc-subbeat`
  element never appears in rendered output (confirmed at two cue points on `what-energizes-me`), though
  chips built the same appendChild+gsap.fromTo way render fine. Ghost-ring amplitude is a workaround,
  not a fix; `subBeats` is silently unusable until repro'd in live devtools. Needs a live-devtools/
  upstream repro session — decide whether to prioritize it or leave `subBeats` marked unusable
  (since 2026-07-15).
- [owner] **Who/what rendered `better-decisions`?** Provenance-blocked, never at the gate;
  aborted temp render dir preserved as evidence. Decide: provide the lesson body/outline to
  clear its facts blocker, or park the workspace (since 2026-07-15).
- [owner] **Wistia publish/credential audit trail** — no entry records who cleared the
  earlier "reads 403" state or ran the earlier unlogged Wistia publishes; the disputed
  `career-building` cut `zyr1fq35t7` is now **404/gone** (an out-of-band delete — the `WISTIA_API`
  token still lacks delete scope). Audit question stands (since 2026-07-15).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path and
  `avatar-pipeline/` (since 2026-07-07).

**Fixed this session:**
- [authoring] **Navy depth-drift amplitude raised to the QA-registering band** (owner-approved at
  close-out). Bumped all 5 navy heroes from 16–30px to ~85–120px translate (`scla-title`,
  `scla-statement`: 120/72, 100/52, 70/44; `scla-outro`: 115/66, 108/58; `scla-quote`: 110/70, 92/52;
  `scla-stat`: 110/68, 84/52), each with an inline note pointing at the chips finding. `npm run check`
  clean → re-rendered the reel (`design-system_2026-07-15_21-10-31.mp4`) → `verify_render.py` presence
  **PASS, 0 violations** (the prior 5.5s hard-static on `scla-quote` cleared). Eyeballed title/statement/
  quote frames: 110/70px reads as gentle corner parallax, on-brand, not distracting. ~15 min incl. two
  reel renders. NOTE: 3 residual gray-zone (3–5s) warnings remain on `scla-career-map` (a LIGHT
  template, not a navy hero — no depth-drift; cue-driven in real lessons) and a `scla-chips` tail —
  within the checker's "lane judges" tolerance on a silent reel, not gate failures.
- [tooling] Avoided a redundant ~7-min re-render on SHIP by mtime-checking source vs. newest render
  (no source file post-dated the existing cut) — verified the existing MP4 instead. No cost.
- [authoring] Cleared the stale **`scla-steps` contrast** Open item: `npm run check` confirms the label
  now passes WCAG AA (46/46 text elements) — already resolved in the template, only the log lagged. Dropped.
- [authoring] Cleared the stale **SKILL PUBLISH web-UI** Open item: the `/render-lessons` PUBLISH block
  (lines 188–195) already documents the headless `upload.wistia.com` API flow and marks the web-UI flow
  retired. Was already fixed in the prior publish session; the Open item just wasn't cleared. Dropped.

**Promoted to docs:**
- `frame.md` depth-drift row (line ~419): "16–30px" → "~85–120px" with the reason (small amplitudes
  move <1 gray level per 48×27 QA thumbnail px and read static), plus a note that all heroes were
  raised to the registering band 2026-07-15. The spec is now empirically correct.

## 2026-07-15 · BUILD: `what-energizes-me` built gate-clean to the hyperframe gate (career-map skipped per owner)

`/render-lessons BUILD`. Queue was 2 (refined minus already-built): `using-the-career-map-tool`
and `what-energizes-me`. Owner said "skip career map for now", so only `what-energizes-me` built.
Started-build count for early-career-boost = 9 (7 live + 2 archived) → theme `summit` (9 mod 3 = 0).
One cold general-purpose build subagent, all-template approach following the newest gate-clean
reference (`skills-for-the-ai-era-future`): 18 scenes, two living icons (`examine`, `done`) on
single-focus beats. Gates green — compile_timeline PASS, orchestrator's independent preflight
re-run PASS (exit 0, 0 boundary violations, theme=summit all scenes, script_match 438/438 =
0.00%), `npm run check` exit 0. No render (correct — BUILD stops at the gate). Preview served on
:3002; handed the owner the gate. Nothing owed on this build but the human ship decision.

**Open:**
- [owner] **`scla-steps` contrast warnings (label 2.99:1, ghost numeral 1.12:1)** — surfaced
  by `npm run check` on this build at t≈118s; warnings only (gate passed), and template-owned
  so a single build can't fix them without forking. The ghost numeral is intentionally faint;
  the section label at 2.99:1 sits just under AA-large. A design-token decision on the label —
  fold into the already-owed demo-reel re-render if you want it addressed (since 2026-07-15).
- [owner] **SKILL PUBLISH step still describes the retired no-token web-UI flow** —
  headless API upload is now proven a second time this session; the `/render-lessons` PUBLISH
  block still says "the upload itself is the human's move in the web UI." Edit was previously
  held as agent self-modification of the governing skill — needs owner OK or explicit direction
  to correct it (since 2026-07-15). **Asked at close-out this session.**
- [owner] **Who/what rendered `better-decisions`?** Provenance-blocked, never at the gate;
  aborted temp render dir preserved as evidence. Decide: provide the lesson body/outline to
  clear its facts blocker, or park the workspace (since 2026-07-15).
- [owner] **Wistia publish/credential audit trail** — no entry records who cleared the
  earlier "reads 403" state or ran the earlier unlogged Wistia publishes; the disputed
  `career-building` cut `zyr1fq35t7` is now **404/gone** (a delete happened out-of-band — the
  `WISTIA_API` token still lacks delete scope, so this was an owner/web-UI or rotated-token
  action, unlogged). Audit question stands (since 2026-07-15).
- [owner] **Demo-reel render still owed** before the next *ship* (style guide has drifted
  ahead of the templates: animacy re-tune + `scla-statement`/`scla-steps` icon slots). Say
  the word and it renders (since 2026-07-15).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path and
  `avatar-pipeline/` (since 2026-07-07).

**Fixed this session:**
- Nothing broke. Clean single-build run; no snags hit.

**Promoted to docs:**
- None this session (no durable authoring/env lesson emerged — the one new item is an
  owner-side design-token decision, logged Open above, not a doc fix).

## 2026-07-15 · Owner-directed PUBLISH of the three early-career-boost cuts to Wistia (MP4-review gate waived, on the record)

Owner invoked `/render-lessons SHIP` for `do-not-just-ask-what-ai-replaces`,
`career-building-is-a-repeatable-process`, `finding-creating-a-career-purpose-statement`,
then immediately corrected ("STOP! These are already complete — they just need to be
uploaded to wistia"): the three 2026-07-15 MP4s in `renders-mp4/early-career-boost/` are
the final cuts, no re-render owed. I had started one `npm run render` (do-not-just-ask)
under the initial SHIP reading — **stopped it via TaskStop** the moment the owner
corrected; the filed MP4s are untouched (render writes to the workspace `out/`, not
`renders-mp4/`). Uploaded all three to the existing Wistia **"Early Career Boost"** project
(id `10733647` / hashedId `miuwd520zj`) via headless API (`upload.wistia.com`, `WISTIA_API`
from Infisical) — all `queued`→`processing`, project media 3→6. Hashed ids: do-not-just-ask
`n18la37w3o`, career-building `lsgkfzu60w`, finding-creating `cnmkchs5dt`. Owner explicitly
directed the upload and **waived the MP4-review gate** — recorded here and in the ledger so
this batch's authorization is on the record (unlike the earlier disputed publishes). Ledger
rows 29–31 updated with URLs + published status; `endpoints.md` Wistia project row filled in.

**Open:**
- [owner] **SKILL PUBLISH step still describes the retired no-token web-UI flow** —
  headless API upload is now proven a second time this session; the `/render-lessons`
  PUBLISH block still says "the upload itself is the human's move in the web UI." Edit was
  previously held as agent self-modification of the governing skill — needs owner OK or
  explicit direction to correct it (since 2026-07-15). **Asked at close-out this session.**
- [owner] **Who/what rendered `better-decisions`?** Provenance-blocked, never at the gate;
  aborted temp render dir preserved as evidence. Decide: provide the lesson body/outline to
  clear its facts blocker, or park the workspace (since 2026-07-15).
- [owner] **Wistia publish/credential audit trail** — no entry records who cleared the
  earlier "reads 403" state or ran the earlier unlogged Wistia publishes; the disputed
  `career-building` cut `zyr1fq35t7` is now **404/gone** (a delete happened out-of-band — the
  `WISTIA_API` token still lacks delete scope, so this was an owner/web-UI or rotated-token
  action, unlogged). Audit question stands (since 2026-07-15).
- [owner] **Demo-reel render still owed** before the next *ship* (style guide has drifted
  ahead of the templates: animacy re-tune + `scla-statement`/`scla-steps` icon slots). Say
  the word and it renders (since 2026-07-15).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path and
  `avatar-pipeline/` (since 2026-07-07).

**Fixed this session:**
- `[tooling]` **Wistia "Lesson-videos project id = TODO" closed for early-career-boost.**
  Found the existing "Early Career Boost" project (id `10733647`) via `GET /v1/projects.json`
  and filed all three there instead of the account default; recorded the id in `endpoints.md`
  and the ledger. Confirmed the three stems were not already present (no duplicates) and that
  the superseded `zyr1fq35t7` is 404. ~5 min.
- `[authoring]` **Misread the initial `SHIP` as needing a re-render.** Owner clarified the
  MP4s were already final; caught after one render start, stopped cleanly with no wasted
  output on the filed artifacts. ~2 min.

**Promoted to docs:**
- `endpoints.md` → Wistia: "Lesson videos project/folder" row now records the per-program
  filing model and the Early Career Boost project id (was `TODO: needs input`).
- `refinement-log.md` rows 29–31: the three cuts marked **published 2026-07-15** with Wistia
  URLs and the owner-directed / gate-waived authorization noted.

## 2026-07-15 · Living-icon slot added to `scla-statement`/`scla-steps`; `finding-creating` gets icons "where relevant"; `check_boundaries` reads sentence-end from the script

Owner asked to add icons to the gate-pending `finding-creating-a-career-purpose-statement`
build — "not every frame, just where relevant" — and (at the clarifying prompt) chose the
broader scope. Widened the living-icon reservation from condition-only to "novel, not on
every frame": `scla-statement` + `scla-steps` gained an **optional `icon` variable** (empty
default → unchanged), icon geometry mirrored from `scla-condition`. In the build: scene 05
"three ingredients" split into three condition cards (bulb/two-people/growth), and icons
added to the question/structure/write-it beats. Narration word-identical (per-scene TTS
re-synth; `script_match` 363/363). 14→16 scenes, all timing recompiled. Gates green:
preflight PASS, `npm run check` 0 errors / 35/35 AA / 0 layout, render-qa suite 36/36,
design-system demo reel still validates clean.

**Open:**
- [owner] **RULED 2026-07-15, execution BLOCKED on Wistia token scope: career-building
  comes off Wistia and all three vetoed cuts get re-made.** Owner approved the
  take-down of zyr1fq35t7 and the re-cut of all three 2026-07-15 videos on the
  stripped templates. **The delete cannot run with the current secret:** the
  `WISTIA_API` token is read+write only and every `DELETE` returns 401 (proven this
  session — see entry above; `endpoints.md` → Wistia). To delete media, **rotate
  `WISTIA_API` in Infisical to a token minted with `read-write-delete-all-data`
  permission** (Wistia account settings — owner/Wistia-admin action); the DELETE
  command then succeeds. Re-cut runs in a fresh session (handoff prompt given to
  owner 2026-07-15). The original question — whether any gate bypass was actually
  directed for this batch — remains open for the record (since 2026-07-15).
- [owner] **Who/what rendered better-decisions?** It is provenance-blocked and
  was never at the gate; the aborted temp render dir is preserved as evidence.
  Also decide: provide the lesson body/outline to clear its facts blocker, or
  park the workspace (since 2026-07-15). Related provenance gap: the credential's
  *health* is now settled (verified 2026-07-15 — identity `SCLA-PROJECTS`, full
  chain green, `endpoints.md`), but the **audit** question stands — no entry
  records who cleared the earlier "reads 403" state or when, and this is the
  credential that enabled the unlogged Wistia publishes (since 2026-07-15).
- [owner] **Demo-reel render still owed** before the next ship (promotion
  decision 2026-07-15 said "not rendered — owner instruction"; today's animacy
  re-tune, prior template fixes, and **this session's `scla-statement`/`scla-steps`
  icon-slot additions** widen the gap between the live style guide and the
  templates). Say the word and it renders (since 2026-07-15).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path
  and `avatar-pipeline/` (since 2026-07-07).
- [owner] **Wistia Lesson-videos project id still `TODO` in endpoints.md** —
  both published lessons sit in the account default project (since 2026-07-15).
- [owner] **SKILL PUBLISH step still describes the retired no-token web-UI
  flow** — headless API upload is proven; edit was blocked as agent
  self-modification, needs owner hand or explicit direction (since 2026-07-15).

**Fixed this session:**
- `[defect]` **`check_boundaries.py` false mid-sentence-cut at a clean split.** The
  `…coming alive **in.** | **Second,**…` boundary tripped `mid-sentence-cut`: Whisper
  back-dated the next scene's first word ("Second,") into this scene's window — its
  *start* drifted before this scene's sample-exact audio end and its longer *end*
  won `max(end)`, so it was picked as the spurious last word. No timing window
  separates a drifted next word from a real last word whose end Whisper pads into the
  air gap. Fix: read `sentence_end`/`is_question` from the scene's `data-narration`
  **script text** (authoritative for sentence boundaries), keeping the manifest +
  Whisper only for air/gap/mid-word timing. Suite 36/36. ~40 min (two wrong
  timing-threshold attempts first — both over-corrected and truncated every real last
  word; the script-text source is the correct one).
- `[env]` **`npx hyperframes tts` needs `HYPERFRAMES_PYTHON`** pointed at the kokoro
  venv (`command -v python3` here has `kokoro_onnx`; the CLI's own interpreter
  detection does not). Documented landmine (B0); noting it recurred on the per-scene
  re-synth. No fix owed — export the var per session.

**Promoted to docs:**
- `frame.md` → "Living icon library": reservation reworded from *condition-only* to
  "novel, not on every frame"; documents the optional `icon` slot on `scla-statement`
  (right-side hero, narrows text) + `scla-steps` (header top-right, replaces ghost
  numeral) and that the `ICONS` map is mirrored into both from `scla-condition` (the
  source of truth — edit there, sync the mirrors).
- `decisions/log.md`: 2026-07-15 entry — scope-widening decision, gate fix, gate results.
- Templates `scla-statement.html` + `scla-steps.html` (design-system source **and** the
  build copies) carry the new optional `icon` slot; demo reel unaffected (icon empty by
  default).

## 2026-07-15 · Ops: "Infisical 401" run to ground — it is a Wistia token-scope 401, not Infisical

Owner reported `scripts/with-secrets.sh … DELETE …zyr1fq35t7… -> HTTP 401` and
asked to confirm the right Infisical machine identity is being called. **Infisical
is healthy; the 401 is Wistia's.** Live probes: login exit 0 as identity
`SCLA-PROJECTS` (`identityId 12f0b20a-2ac1-44f6-902c-cb8ef121d210`), `with-secrets.sh`
injects both project secrets (the "Injecting 2 Infisical secrets" line is success),
`GET /account.json` → 200, `GET /medias/zyr1fq35t7.json` → 200, but **every
`DELETE /medias/*.json` → 401** — reproduced with the `api_password` query param
*and* `Authorization: Bearer`, even against a bogus id. Reads/writes work, deletes
don't: the `WISTIA_API` token is **read+write but lacks delete scope** (Wistia 401s
on an operation above the token's permission tier). Recorded in `endpoints.md`
(Infisical note + Wistia token-scope note + last-verified 2026-07-15).

**Open:**
- [owner] **RULED 2026-07-15, execution BLOCKED on Wistia token scope: career-building
  comes off Wistia and all three vetoed cuts get re-made.** Owner approved the
  take-down of zyr1fq35t7 and the re-cut of all three 2026-07-15 videos on the
  stripped templates. **The delete cannot run with the current secret:** the
  `WISTIA_API` token is read+write only and every `DELETE` returns 401 (proven this
  session — see entry above; `endpoints.md` → Wistia). To delete media, **rotate
  `WISTIA_API` in Infisical to a token minted with `read-write-delete-all-data`
  permission** (Wistia account settings — owner/Wistia-admin action); the DELETE
  command then succeeds. Re-cut runs in a fresh session (handoff prompt given to
  owner 2026-07-15). The original question — whether any gate bypass was actually
  directed for this batch — remains open for the record (since 2026-07-15).
- [owner] **Who/what rendered better-decisions?** It is provenance-blocked and
  was never at the gate; the aborted temp render dir is preserved as evidence.
  Also decide: provide the lesson body/outline to clear its facts blocker, or
  park the workspace (since 2026-07-15). Related provenance gap: the credential's
  *health* is now settled (verified 2026-07-15 — identity `SCLA-PROJECTS`, full
  chain green, `endpoints.md`), but the **audit** question stands — no entry
  records who cleared the earlier "reads 403" state or when, and this is the
  credential that enabled the unlogged Wistia publishes (since 2026-07-15).
- [owner] **Demo-reel render still owed** before the next ship (promotion
  decision 2026-07-15 said "not rendered — owner instruction"; today's animacy
  re-tune + this session's template fixes widen the gap between the live style
  guide and the templates). Say the word and it renders (since 2026-07-15).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path
  and `avatar-pipeline/` (since 2026-07-07).
- [owner] **Wistia Lesson-videos project id still `TODO` in endpoints.md** —
  both published lessons sit in the account default project (since 2026-07-15).
- [owner] **SKILL PUBLISH step still describes the retired no-token web-UI
  flow** — headless API upload is proven; edit was blocked as agent
  self-modification, needs owner hand or explicit direction (since 2026-07-15).

**Fixed this session:**
- `[env]` **Ran the "Infisical 401" to ground — misattribution, not a real
  Infisical fault.** Root cause is Wistia rejecting the DELETE for lack of delete
  scope (evidence in the entry above). Infisical login, identity, and secret
  injection all verified green. `endpoints.md` updated: Infisical identity name +
  health, Wistia token-scope limit, last-verified 2026-07-15. No credential change
  possible from here (token rotation is a Wistia-admin action — carried in Open).

**Promoted to docs:**
- `endpoints.md` now records the durable facts: the Infisical machine identity is
  `SCLA-PROJECTS` and the chain is verified green; the `WISTIA_API` token is
  read+write **without delete**, so media deletion needs a rotated
  `read-write-delete-all-data` token. That doc is the memory; this is the trail.

## 2026-07-15 · RE-CUT the three vetoed videos on the veto-stripped templates (staged-beat hold coverage); all gate-clean, no render

Owner directed a re-cut of the three 2026-07-15 vetoed cuts — `career-building`,
`do-not-just-ask`, `finding-creating` — per decisions/log.md 2026-07-15
"In-place keep-alive motion stays banned." One independent cold build subagent
per video, run in parallel (`/dev/shm` raised 512M→1.5G first, to fit three
concurrent headless-Chrome `validate` runs). Each subagent: synced the
veto-stripped `design-system/` templates + `frame.md` into its workspace
(overwriting the frozen copies that still carried the banned in-place motion —
workspace `scla-statement` had 6 motion-token hits vs the stripped source's 3),
re-authored every exposed long hold with **staged beats only** (scene splits /
supporting `lines` / `subBeats`·`subCues` — never in-place re-animation), re-ran
`synth_narration` → `transcribe` → `compile_timeline --apply` → `preflight` →
`npm run check` to green, and STOPPED at the hyperframe gate (no render).
Orchestrator independently re-ran `preflight.py` on all three (exit 0 each) and
confirmed no new MP4 was produced (every `renders/*.mp4` predates the session —
the vetoed cuts, untouched).

Results (theme preserved; scenes before→after; preflight exit 0, 0 boundary
violations each; worst reveal gap ≤4.6s per video, all under the 5.0s
`check_presence` tripwire; no content scene relies on in-place motion or on
decorative depth-drift as its hold cover):
- `career-building` horizon 15→21 · script 471=471, 0.00%
- `do-not-just-ask` cadence 12→14 · script 401=401, 0.25% WARN (Whisper
  "then"→"often" @w150; anchor moved off it — harmless, not a violation) ·
  05/06/08 approved `subBeats` intact (now scenes 07/08/10 after splits)
- `finding-creating` horizon 12→14 · script 363=363, 0.00% · one flagged
  judgment item: outro (sc14) holds ~5s past its last word — structurally one
  unsplittable sentence with frame.md's mandated ≥1s end-hold, covered only by
  the sanctioned finite translate-only depth-drift; surfaced to owner at the gate.

**Open:**
- [owner] **RE-CUT DONE (this session), take-down still pending.** All three
  vetoed cuts are re-made and gate-clean on the stripped templates. The paired
  ruling — `career-building` comes off Wistia (`zyr1fq35t7`) — is still
  unexecuted: the irreversible external delete needs the owner to name the
  video in-session ("delete Wistia media zyr1fq35t7") or run:
  `scripts/with-secrets.sh sh -c 'curl -s -X DELETE "https://api.wistia.com/v1/medias/zyr1fq35t7.json?api_password=$WISTIA_API" -w "HTTP %{http_code}\n" -o /dev/null'`
  (since 2026-07-15).
- [owner] **`.claude/skills/render-lessons/SKILL.md` build-sequence narration
  steps are STALE** — they still show the retired single-take
  `npx hyperframes tts "$(cat script)"` + assemble-index-after flow; the live
  contract (decisions/log.md 2026-07-14) is per-scene
  `render-qa/synth_narration.py`, which reads `data-narration` from index.html,
  so index.html is authored FIRST. The 2026-07-14 "promoted to docs" claim did
  not actually land in the SKILL. I handed subagents the correct flow this
  session; the fix is a factual command correction but edits the running skill,
  so — consistent with the standing SKILL-edit sign-off norm — it is filed for
  owner direction rather than self-applied (since 2026-07-15).
- [owner] **Who/what rendered better-decisions?** Provenance-blocked, never at
  the gate; aborted temp render dir preserved as evidence. Decide: provide the
  lesson body/outline to clear its facts blocker, or park the workspace. Related
  Infisical provenance gap (403 vs "read access" with no clearing record)
  (since 2026-07-15).
- [owner] **Demo-reel render still owed** before the next ship (promotion
  decision 2026-07-15; today's veto strip + re-cuts widen the gap between the
  live style guide and the templates) (since 2026-07-15).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path
  and `avatar-pipeline/` (since 2026-07-07).
- [owner] **Wistia Lesson-videos project id still `TODO` in endpoints.md** —
  both published lessons sit in the account default project (since 2026-07-15).
- [owner] **SKILL PUBLISH step still describes the retired no-token web-UI
  flow** — headless API upload is proven; edit blocked as self-modification
  (since 2026-07-15).

**Fixed this session:**
- `[authoring]` The three re-cuts above — veto-stripped-template sync + staged-beat
  hold coverage, gate-clean, no render. Each hold covered by a scene split,
  supporting `lines`, or `subBeats`/`subCues`; ambient depth-drift left decorative,
  never load-bearing.
- `[env]` `hyperframes transcribe` returned `whisper-cli ETIMEDOUT` on cold
  attempts under 3-way CPU contention (actual DTW run ~65–75s vs the wrapper's
  5-min spawn timeout tripping cold). Two of three agents hit it; resolved by
  clearing competing whisper procs and re-running transcribe in the FOREGROUND,
  warm — completed natively, correct transcript. No package patch.
- `[tooling]` One build subagent fell into an idle loop: it backgrounded
  synth+transcribe under contention and kept yielding to wait on a Monitor that
  wasn't delivering. Coordinator redirected it to run synth→transcribe→compile→
  preflight→check strictly in the FOREGROUND (blocking per step); gates then went
  green. Durable lesson below.

**Promoted to docs:** parallel-build CPU-bound narration steps run in the
FOREGROUND, never backgrounded-with-Monitor — added to this session's dispatch
practice (the SKILL already says builds run sequentially "share the toolchain and
`/dev/shm`"; when parallelising, size `/dev/shm` up AND keep synth/transcribe
foreground). The SKILL narration doc-drift is filed as an owner decision above,
not self-applied.

## 2026-07-15 · Full pipeline review of today's changes; animacy-sweep gaps fixed; three unlogged renders + one uncorroborated publish surfaced

Owner-requested full review of today's pipeline changes (promotion commit
9a6735e, rail wiring 03c2319, the uncommitted animacy re-tune sweep) plus the
outputs rendered after them. Three parallel review lanes (template diffs /
rendered outputs / logs-vs-state). Outcomes: the promoted upgrades ARE in all
three 2026-07-15 renders (rail spec-conformant and visible in sampled frames;
workspaces carry the re-tuned templates; all three verify PASS — career-building
166.9s/2 gray-zone warnings, do-not-just-ask 149.5s/0, finding-creating
127.2s/1). But the sweep missed one template and two of its tweens drifted
elements away from their anchored siblings (fixed below), and **today's ships
ran outside the checkpoints**: no snag-log entry exists for any of the three
renders (hook rule), no `ship` authorization is recorded anywhere, and
career-building was **published to Wistia** (zyr1fq35t7 — verified live) on a
"owner directed gate bypass" claim corroborated by nothing (this log listed
that video as still AT the hyperframe gate). Also found: an aborted, unlogged
render attempt of better-decisions (which carries a facts-provenance blocker) —
temp dir `renders-hyperframes/better-decisions.../renders/work-90fddb46*`
left in place as evidence — and the published pilot's filed verify-summary
clobbered by a post-archive verify re-run (evidence note + fresh ffprobe
restored in the .qa packet). Residual cosmetic items in the sweep noted, not
changed (three videos rendered+verified on this exact code today): navy
late-phase tweens ungated vs light's sdur>7.5 gate; the [0.6,0.84] double
placement collapsing to one cascade when lastCue+1.2 ≥ sdur*0.84; title's
late tween outrunning min-length scenes; odd drift cycles ending displaced
(background-only). Light-theme points/chips still hold 3–3.5s between reveals
(gray zone, lane judges) — parallax only exists on templates with decorative
layers.

**Open:**
- [owner] **RULED 2026-07-15, execution pending: career-building comes off
  Wistia and all three vetoed cuts get re-made.** Owner approved the take-down
  of zyr1fq35t7 and the re-cut of all three 2026-07-15 videos on the stripped
  templates. The API deletion was attempted same-session but blocked by the
  tool-permission gate (irreversible external delete needs the owner to name
  the video explicitly) — owner: either say "delete Wistia media zyr1fq35t7"
  in-session, or run:
  `scripts/with-secrets.sh sh -c 'curl -s -X DELETE "https://api.wistia.com/v1/medias/zyr1fq35t7.json?api_password=$WISTIA_API" -w "HTTP %{http_code}\n" -o /dev/null'`
  then this row + refinement-log get closed out. Re-cut runs in a fresh
  session (handoff prompt given to owner 2026-07-15). The original question —
  whether any gate bypass was actually directed for this batch — remains open
  for the record (since 2026-07-15).
- [owner] **Who/what rendered better-decisions?** It is provenance-blocked and
  was never at the gate; the aborted temp render dir is preserved as evidence.
  Also decide: provide the lesson body/outline to clear its facts blocker, or
  park the workspace (since 2026-07-15). Related provenance gap: the decision
  log's last recorded Infisical state is "machine identity reads 403", but
  endpoints.md (commit ef94c0c, 2026-07-15 00:47) says "verified 2026-07-14:
  read access" with no entry recording who cleared it or when — this is the
  credential that enabled the unlogged Wistia publishes (since 2026-07-15).
- [owner] **Demo-reel render still owed** before the next ship (promotion
  decision 2026-07-15 said "not rendered — owner instruction"; today's animacy
  re-tune + this session's template fixes widen the gap between the live style
  guide and the templates). Say the word and it renders (since 2026-07-15).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path
  and `avatar-pipeline/` (since 2026-07-07).
- [owner] **Wistia Lesson-videos project id still `TODO` in endpoints.md** —
  both published lessons sit in the account default project (since 2026-07-15).
- [owner] **SKILL PUBLISH step still describes the retired no-token web-UI
  flow** — headless API upload is proven; edit was blocked as agent
  self-modification, needs owner hand or explicit direction (since 2026-07-15).

**Fixed this session:**
- `[design-system]` **OWNER VETO applied — all in-place motion of settled
  content stripped from every template** (decisions/log.md 2026-07-15 "In-place
  keep-alive motion stays banned"). The owner watched career-building, saw
  "text jumping around," and reaffirmed the 2026-07-14 ban the unlogged session
  had silently reversed. Removed: statement reading ripple, every late-phase
  resolve/re-mark (statement/points/chips/steps/condition/morph/title/stat/
  outro/quote), every pre-first-cue keep-alive, points' inter-cue nudges.
  Kept: background depth-drift yoyo re-tune (decorative layers only) and the
  condition living-icon bob (illustration, not text — owner may veto on view).
  `scla-career-map.html` reverted to its committed promoted state. (Earlier
  this session, before the veto, three sweep bugs had been fixed in place —
  career-map's missing coverage, quote's 8px card seam, statement's underline
  gap; the veto then removed those tweens entirely, which also moots them.)
- `[docs]` `frame.md` — animacy rules restored to the ban: long holds are an
  authoring defect (cover with cued items, `lines`, `subBeats`, or a split);
  background drift is texture, never a cover. Verified after the strip:
  `npm run check` green (0 lint errors/warnings, 0 console errors, 43/43 AA,
  0 layout issues); render-qa suite 36/36 pass (earlier this session).
- `[consequence]` All three 2026-07-15 MP4s contain the banned motion —
  do-not-just-ask + finding-creating need re-author (staged-beat coverage for
  long holds) + re-render through the gates; the disputed career-building
  Wistia publish carries it too (one more reason for the take-down ruling).
- `[bookkeeping]` refinement-log: filled the missing SHIP rows for
  do-not-just-ask + finding-creating; replaced career-building's uncorroborated
  "published / owner directed gate bypass" note with the flagged factual state.
  status.md Production Status refreshed (was pre-dating all four videos).
  Pilot .qa verify-summary evidence restored. `.gitignore` now covers the
  `renders-mp4/**/*.qa/` packets (renders-mp4 is documented as local-only).

**Promoted to docs:** the frame.md corrections above (spec now matches the
shipped template code). Nothing else durable — the checkpoint-provenance
question is an owner decision, filed above.

## 2026-07-15 · SHIP+PUBLISH what-makes-for-a-dream-job (owner waived the MP4-review gate); Wistia headless upload confirmed working

Owner instructed: bypass the MP4-review checkpoint and publish this one straight
to Wistia. Rendered the gate-clean pilot workspace (theme summit, 15 scenes,
187.5s), `verify_render.py` **PASS** (0 violations; 13 stagnant-frame warnings
all in the 3–5s gray zone), filed MP4 + QA packet to
`renders-mp4/early-career-boost/`, uploaded via the Wistia Upload API →
`hashed_id 6g95getfl2` (https://sclc.wistia.com/medias/6g95getfl2). Script moved
`refined/`→`rendered/`, workspace archived. This is the first end-to-end
headless publish — the SKILL's "no wired API token, human web-UI move" wording is
now stale (token works; see below).

**Open:**
- [owner] **Four workspaces still at the HYPERFRAME GATE** — `career-building`,
  `do-not-just-ask`, `finding-creating`, `build-direction`. Preview each
  (`bash scripts/preview.sh <stem>`) and say `ship <stem>` or ask for changes.
  The still-pending pilot-preview decisions (five candidate design-system
  upgrades + the `subBeats` live line on `do-not-just-ask` 05/06/08) were NOT
  resolved — the owner waived the pilot preview rather than reviewing it, so
  those design calls still need a look (since 2026-07-14).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path
  (HeyGen TTS = better pronunciation + native word timestamps, which would also
  remove the transcribe step) and `avatar-pipeline/`. Fix = key with API access
  / `npx hyperframes auth login` (since 2026-07-07).
- [owner] **Wistia Lesson-videos project id is still `TODO` in endpoints.md** —
  so this publish landed in the account default project, not a dedicated
  lessons folder. Provide the project hashed id to file future lessons (and to
  backfill/move this one); the upload command already supports `-F project_id=`
  (since 2026-07-15).
- [owner] **SKILL PUBLISH step is stale + should be corrected, but the edit was
  blocked as a self-modification** (it reads Wistia as a no-token web-UI upload;
  the `WISTIA_API` token is wired and the API upload returns 200 headless). I
  did not rewrite the guard myself. Decide whether to update
  `.claude/skills/render-lessons/SKILL.md` PUBLISH step to the API path, and
  whether headless publish should be standing behavior or stay owner-waived
  per video (since 2026-07-15).

**Fixed this session:**
- `[tooling]` Wistia headless upload proven end to end — `scripts/with-secrets.sh`
  injects `WISTIA_API` (64 chars); `curl -F api_password -F name -F file@`
  `https://upload.wistia.com/` → HTTP 200 + `hashed_id`. No web-UI step needed.
  Single-session, no rework.

**Promoted to docs:** none landed — the one durable lesson (SKILL PUBLISH step →
API path) was blocked as a self-modification and is filed as an owner decision
above instead.

## 2026-07-14 · per-scene narration synthesis replaces single-take + inserted silence; all gate-pending workspaces re-cut; dead-hold re-staging shipped

Owner-reported audio defects (dropouts between frames, "mispronounced" words)
root-caused to `insert_silences` splicing digital-zero into a 0.03s-gap Kokoro
take at ±100ms Whisper timestamps — plus an orphaned mid-sentence hole left by
re-anchoring. Rebuilt the flow around `synth_narration.py` (per-scene TTS, real
boundary silence, sample-exact `scene-times.json` manifest; `data-anchor-end`
retired for new builds). Full record: `decisions/log.md` 2026-07-14. All five
workspaces at the hyperframe gate re-cut/migrated, gates green, audio verified
by energy scan (silent gaps, zero mid-word splices, zero click onsets).

**Open:**
- [owner] **Five workspaces are gate-clean and waiting at the HYPERFRAME GATE**
  (`what-makes-for-a-dream-job` pilot + `career-building` + `do-not-just-ask` +
  `finding-creating` + `build-direction`) — preview each
  (`bash scripts/preview.sh <stem>`) and say `ship <stem>` or ask for changes.
  The pilot preview also decides the five candidate design-system upgrades AND
  the new `subBeats` live line (on `do-not-just-ask` 05/06/08) (since 2026-07-14).
- [owner] **HeyGen API key still 403s** — blocks the pinned-voice upgrade path
  (HeyGen TTS = better pronunciation + native word timestamps, which would also
  remove the transcribe step) and `avatar-pipeline/`. Fix = key with API access
  / `npx hyperframes auth login` (since 2026-07-07, re-surfaced because Kokoro
  pronunciation is now the narration's main remaining quality ceiling).

**Fixed this session:**
- `[defect]` boundary splices landing inside voiced audio + orphaned inserted
  silence (the owner-heard dropouts/mangled words) — per-scene synthesis, see
  above. Pilot + 3 workspaces re-cut, `build-direction` (pre-anchor era, 7
  boundary violations) fully migrated. ~half-day root-cause-to-verified.
- `[defect]` `check_boundaries.py`/`compile_timeline.py` trusted Whisper word
  ends/starts that drift into boundary silence (false mid-word-cut flags,
  cue-window misses) — manifest is now ground truth for windows, spoken ends,
  and question flags.
- `[authoring]` stale cue anchors vs the new takes: `career-building` "In
  Module 1"→"In module one" (Kokoro speaks digits as words), `finding-creating`
  em-dash compound "buzzwords—just" → "buzzwords. Just" and one anchor whose
  final word Whisper timed into the gap. Fixed in-place; landmine already
  documented in the SKILL.
- `[authoring]` deferred dead-hold re-staging (owner-approved design)
  IMPLEMENTED: `subBeats`/`subCues` narration-synced live line in
  `scla-steps`/`scla-points`/`scla-chips` (variable-gated off, seek-safe) +
  `subCues` in the compiler whitelist (pipe-separated pair `subBeats`);
  authored on `do-not-just-ask` 05/06/08 — worst static run now ≤4.8s (<5s
  presence tripwire). Design-system `npm run check` green; demo reel unaffected
  (feature absent when unset).
- `[tooling]` `how-to-make-strong-career-decisions` abandoned init-stub
  workspace silently shadowed its refined script out of the BUILD queue —
  stub deleted; the script is buildable again.
- `[tooling]` `tests/run_tests.py` hardcoded another session's scratchpad path
  (suite unrunnable elsewhere) — now `tempfile`-based. Suite 20→36 fixtures.
- `[owner-delegated]` preflight number-word fold KEPT (owner: "make the best
  decision"); already recorded in `decisions/log.md` 2026-07-14.

**Promoted to docs:**
- The whole narration contract: `/render-lessons` build sequence (author
  `index.html` FIRST, then synth → transcribe → compile), `frame.md` timing
  contract (`data-narration`, manifest, anchor-end legacy-only),
  `render-qa/README.md` (tool table + 2026-07-14 flow note), `PIPELINE-MAP.md`
  BUILD step. The decision itself: `decisions/log.md` 2026-07-14.

## 2026-07-14 · PILOT build — five candidate design-system upgrades on what-makes-for-a-dream-job (gate-clean; awaiting hyperframe review)

Built the pilot for five owner-approved candidate upgrades (living icons, morph/FLIP
hand-off, depth-drift parallax, host-root progress rail, stat rings) on
`what-makes-for-a-dream-job_early-career-boost` — 15 scenes, summit, all three gates exit-0,
preflight re-verified by the orchestrator (0 boundary violations). Features are built into
workspace-local `pilot-*` sub-comps only; `frame.md` and the `scla-*` templates were NOT
touched (promotion waits on the human's hyperframe review). Brief:
scratchpad `pilot-brief.md`; per-scene map: workspace `PILOT-NOTES.md`.

**Open:**
- [owner] **`render-qa/preflight.py` number-word fold — accept or revert.** The build added a
  symmetric spelled-number→digit fold (`_fold_number_words`) to the script-vs-transcript
  tokenizer, because this stat-dense lesson tripped `script_match` at 2.24% purely on format
  noise ("eighty thousand"/"forty-thousand-dollar" vs Whisper "80,000"/"$40,000"); rate → 0.56%
  after, render-qa suite still 20/20. It is strictly-better (folds format noise, keeps value
  fidelity — a real misread still lands on different digits) but it is the ONE change outside the
  gitignored pilot workspace and it alters a deterministic gate. Keep it (→ needs a
  `decisions/log.md` entry) or revert. `preflight.py` had no prior WIP, so no conflict with the
  deferred render-qa toolchain work (since 2026-07-14).
- [owner] Dead-hold re-staging DEFERRED (owner decision 2026-07-14). Removing the in-place
  keep-alive motion exposed genuine ≥5s static holds while narration speaks in
  `do-not-just-ask-what-ai-replaces`: scene 05 (THE METHOD, 3 internal holds), 06 (tail), 08
  (tail), borderline 04/09 — these FAIL `check_presence` at ship. Approved fix = staged sub-beats
  revealed on the spoken cue; needs a new cue key in `compile_timeline.py` (`CUE_KEYS` whitelist)
  + its 20-fixture test suite + per-template sub-beat rendering. Held until the uncommitted
  render-qa toolchain WIP (declick + air-timing retune) is committed (since 2026-07-14).

**Fixed this session:**
- `[authoring]` scene-7 mid-sentence cut — Whisper comma-joined "…heavy lifting, so if it is not
  passion…" as one run. Re-anchored the money scene to sentence end "far less gain"; moved the
  "engagement and meaning" line to open scene 08. ~5 min.
- `[defect]` bespoke sub-comp root styled by its own class (`#root.navy`) renders **unstyled**
  under render-time composition scoping though it passes every static/preview check. Moved the
  navy/light canvas class onto a child wrapper. ~10 min. Promoted below.

**Promoted to docs:**
- "Never qualify a bespoke sub-comp root by its own class/attribute — style it via `#root {}` +
  descendant selectors only; a `#root.navy`-style rule passes static checks but renders unstyled
  under composition scoping." Added to the `/render-lessons` build-sequence Standing landmines.

## 2026-07-14 · de-jitter do-not-just-ask-what-ai-replaces (removed in-place keep-alive motion; sub-beat re-staging deferred)

**Open:**
- [owner] Dead-hold re-staging DEFERRED (owner decision 2026-07-14). Removing the
  in-place keep-alive motion (see Fixed) exposed genuine ≥5s static holds while
  narration speaks: scene 05 (THE METHOD, 3 internal holds), 06 (tail), 08 (tail),
  borderline 04/09 — these will FAIL `check_presence` at ship. Approved fix =
  staged sub-beats revealed on the spoken cue (e.g. scene 05's judgment /
  relationships / creativity / oversight enumeration). Needs a new cue key in
  `compile_timeline.py` (`CUE_KEYS` whitelist) + its 20-fixture test suite +
  per-template sub-beat rendering. Held until the uncommitted render-qa toolchain
  WIP (declick + air-timing retune across compile_timeline/check_boundaries/
  hfp_common/verify_render) is committed, to avoid building a gate feature on top
  of unfinished work with no render to verify (since 2026-07-14).
- [owner] `better-decisions` release blocked: the lesson body/outline was never
  filed as source material, so the facts lane cannot verify its framework
  (since 2026-07-10).
- [owner] Unattended build phases still prompt for permissions: `npm`, `npx`,
  `pkill`, `sudo mount`, `ffmpeg`, `ffprobe`, `bash scripts/archive-lesson.sh`
  are not in `.claude/settings.json` allow (since 2026-07-13).
- [env] claude-mem plugin worker can go unreachable; its PreToolUse hook then
  hard-blocks the Read tool (workaround: allowlisted Bash) (since 2026-07-13).
- [upstream] scale+SVG-opacity streaming-encode ghost (scla-career-map,
  2026-07-10) still not filed upstream — repro evidence retained in the
  archived workspace; the translate-only rule is already promoted
  (since 2026-07-10).
- [owner] `mini-syllabus` MP4 delivered 2026-07-08 but its Wistia upload/URL
  was never confirmed — ledger row says `TODO: needs input` (since 2026-07-13).

**Fixed this session:**
- [authoring/defect] In-place "keep-alive" motion made settled elements wiggle in
  place — the "reading ripples", "late-phase resolve", and "inter-cue gap coverage"
  devices. Reported as jitter in the hyperframe preview; because the render seeks a
  paused timeline deterministically, it bakes into the MP4 identically (not a
  preview glitch). Owner ruled No-Dead-Frames is for illustrative elements entering/
  exiting, never for re-animating on-screen elements. Removed all three from all 9
  scene templates in BOTH the workspace and the `design-system/` source; kept the
  ambient ring-breath. `hyperframes validate` clean (0 err / 0 warn / 1 pre-existing
  contrast note). ~30 min.

**Promoted to docs:**
- `frame.md` → "Every scene earns its seconds" animacy rules rewritten: the
  reading-ripple / late-phase-resolve mandate (two bullets + the `scla-statement`
  template-table row) replaced with **"Cover long holds with staged content, never
  in-place re-animation."** `check_presence`'s ≥5s rule stays; the only allowed
  cover is a new cued beat / an illustration that enters / splitting the scene —
  never drifting, bobbing, or re-marking settled elements. Ambient ring-breath is
  texture, not motion.

## 2026-07-14 · re-render do-not-just-ask-what-ai-replaces (hyperframe only; picks up 2026-07-14 timing/de-click fixes)

**Open:**
- [owner] `better-decisions` release blocked: the lesson body/outline was never
  filed as source material, so the facts lane cannot verify its framework
  (since 2026-07-10).
- [owner] Unattended build phases still prompt for permissions: `npm`, `npx`,
  `pkill`, `sudo mount`, `ffmpeg`, `ffprobe`, `bash scripts/archive-lesson.sh`
  are not in `.claude/settings.json` allow (since 2026-07-13).
- [env] claude-mem plugin worker can go unreachable; its PreToolUse hook then
  hard-blocks the Read tool (workaround: allowlisted Bash) (since 2026-07-13).
- [upstream] scale+SVG-opacity streaming-encode ghost (scla-career-map,
  2026-07-10) still not filed upstream — repro evidence retained in the
  archived workspace; the translate-only rule is already promoted
  (since 2026-07-10).
- [owner] `mini-syllabus` MP4 delivered 2026-07-08 but its Wistia upload/URL
  was never confirmed — ledger row says `TODO: needs input` (since 2026-07-13).

**Fixed this session:**
- [defect/tooling] Re-render blocked at compile: every scene's
  `data-variable-values` in the built `index.html` was HTML-entity-encoded
  (double-quote-wrapped attr, inner quotes as `&quot;`) — a browser decodes it
  fine (the render would work), but the Python parser's regex `get_attr`
  handed raw `&quot;` to `json.loads`, crashing all 12 scenes at
  `parse_scenes`. Cause: a post-build serialize pass (Studio/preview) rewrote
  the attributes to double-quote/entity form; the writer's canonical form is
  single-quote + literal `"`. Fixed by HTML-unescaping JSON attribute values
  before `json.loads` in `hfp_common.parse_scenes` (new `_load_json_attr`
  helper) — no-op on canonical HTML, tolerant of entity-encoded HTML. ~15 min.
- [tooling] `.pre-pad` restore for re-render: the workspace's `narration.wav`
  was already padded under the old 0.5s/0.8s rule, so a naïve `--apply` would
  double-pad. Restored `narration.wav`/`transcript.json` from their `.pre-pad`
  backups (backups are preserved — `insert_silences` only copies when absent),
  then recompiled: padding +8.29s → +4.69s and the de-click fence applied.
  ~5 min.

**Promoted to docs:**
- The parse fix lives in the shared parser (`render-qa/hfp_common.py`
  `parse_scenes` / `_load_json_attr`), so compile/preflight/check/verify all
  inherit it. Compiler suite still 20/20.
- Re-render procedure (restore from `.pre-pad` before `--apply` so new timing
  constants apply cleanly, never double-pad) is now proven; the `.pre-pad`
  backup contract is already documented in `compile_timeline.py:insert_silences`.

## 2026-07-14 · BUILD batch — 3 early-career-boost hyperframes to the gate (no render)

Built and gate-cleaned three workspaces (do-not-just-ask… · cadence · 12 scenes;
how-to-make-strong-career-decisions · summit · 15; skills-for-the-ai-era-future ·
horizon · 19). All three PASS on independent preflight; sitting at the HYPERFRAME
GATE. 3 of 6 queued built (batch cap); 3 left for next run.

**Why this run was slow (owner asked):** ~50 min wall-clock, three causes —
(1) *cold toolchain*: the container shipped without the TTS/transcribe deps, so
the first build paid a one-time install tax before any voice existed (see Open);
(2) *builds are inherently heavy + strictly sequential*: each is ~3 min of TTS +
Whisper transcription + an assemble→compile→preflight→check loop of 150–300 tool
calls, and they share `/dev/shm` so they cannot run in parallel; (3) *one
subagent stalled*: build 3 yielded mid-build waiting on a background step instead
of driving to gate-clean, costing an orchestrator resume round-trip.

**Open:**
- [owner] Devcontainer image ships **without the TTS/transcribe toolchain** —
  `kokoro-onnx`+`soundfile` (Kokoro TTS) and `ffmpeg` (Whisper transcribe) were
  both absent. Installed in-session, but they vanish on container rebuild and the
  first build of every fresh container re-pays the install tax. Bake into the
  devcontainer image (or a `postCreate` step) to kill the recurring cost
  (since 2026-07-14).
- [owner] `better-decisions` release blocked: the lesson body/outline was never
  filed as source material, so the facts lane cannot verify its framework
  (since 2026-07-10).
- [owner] Unattended build phases still prompt for permissions: `npm`, `npx`,
  `pkill`, `sudo mount`, `ffmpeg`, `ffprobe`, `bash scripts/archive-lesson.sh`
  are not in `.claude/settings.json` allow (since 2026-07-13).
- [env] claude-mem plugin worker can go unreachable; its PreToolUse hook then
  hard-blocks the Read tool (workaround: allowlisted Bash) (since 2026-07-13).
- [upstream] scale+SVG-opacity streaming-encode ghost (scla-career-map,
  2026-07-10) still not filed upstream — repro evidence retained in the
  archived workspace; the translate-only rule is already promoted
  (since 2026-07-10).
- [owner] `mini-syllabus` MP4 delivered 2026-07-08 but its Wistia upload/URL
  was never confirmed — ledger row says `TODO: needs input` (since 2026-07-13).
- [owner] Contrast **warning** (non-blocking) in the shared `scla-morph.html`
  card-A subtitle: `#cnA 1.82:1` at t≈10.3s. Lives in a shared template
  (frame.md says don't fork) — a design-system owner should lift the subtitle
  colour, not a single build (since 2026-07-14).

**Fixed this session:**
- [env] `hyperframes tts` failed on missing `kokoro_onnx` → `pip install
  kokoro-onnx soundfile`, ran TTS with `HYPERFRAMES_PYTHON` pointed at the
  interpreter that now has it. (Recurs on fresh container — see Open.)
- [env] `hyperframes transcribe` failed with no `ffmpeg` → `sudo apt-get install
  -y ffmpeg`. (Recurs on fresh container — see Open.)
- [authoring] Build 2 chip labels with internal commas (`"Vague in, vague out"`)
  split into extra chips and failed the count-vs-cue check → reworded. Rule
  promoted to `frame.md` (cue-anchor contract).
- [tooling] Build 3 subagent yielded mid-build ("Awaiting the Monitor event")
  instead of driving to gate-clean → resumed via SendMessage; completed clean.

**Promoted to docs:** reveal-cue chip/step labels may not contain an internal
comma (splits the element list, fails preflight's count-vs-cue check) →
`frame.md` cue-anchor contract. The three slowness causes above are recorded
here as the trail; the durable fix (bake deps into the image) is the Open item.

---

## 2026-07-13 · pipeline v3 — folder-state model, three-phase render-lessons (no render this session)

**Open:**
- [owner] `better-decisions` release blocked: the lesson body/outline was never
  filed as source material, so the facts lane cannot verify its framework
  (since 2026-07-10).
- [owner] Unattended build phases still prompt for permissions: `npm`, `npx`,
  `pkill`, `sudo mount`, `ffmpeg`, `ffprobe`, `bash scripts/archive-lesson.sh`
  are not in `.claude/settings.json` allow (since 2026-07-13).
- [env] claude-mem plugin worker can go unreachable; its PreToolUse hook then
  hard-blocks the Read tool (workaround: allowlisted Bash) (since 2026-07-13).
- [upstream] scale+SVG-opacity streaming-encode ghost (scla-career-map,
  2026-07-10) still not filed upstream — repro evidence retained in the
  archived workspace; the translate-only rule is already promoted
  (since 2026-07-10).
- [owner] `mini-syllabus` MP4 delivered 2026-07-08 but its Wistia upload/URL
  was never confirmed — ledger row says `TODO: needs input` (since 2026-07-13).

**Fixed this session:** none hit — docs/skills restructure only, no build or render.

**Promoted to docs:** the former standing "Known snags" list now lives where
builders actually read: pkill bracket, /dev/shm ≥256M, CLI pin 0.7.45+/#2064,
`HYPERFRAMES_PYTHON` → `/render-lessons` B0; `tts` without `--provider`
(removed in 0.7.56), whisper em-dash compound tokens, translate-only idle
pulses → `/render-lessons` Build sequence. Resolved-structurally classes
(hand-typed timing, zero-gap padding, bare-canvas flashes) are owned by the
compiler/templates since 2026-07-10..13.

---

## Trail (older entries + pre-v3 session notes, append-only)

### 2026-07-13 · finding-creating-a-career-purpose-statement (first post-refactor run)
- [upstream] `tts --provider` flag rejected by CLI 0.7.56 (flag removed upstream;
  kokoro is the sole built-in engine) → dropped the flag. ~3 min. Skill command
  block updated (now in /render-lessons Build sequence).
- [observation] whisper transcript reads "I am honest enough" where the script
  says "Specific enough" (~24s) — resolved: base.en cross-check proved the audio
  correct (transcription mishear, not a TTS misread); drove the script-vs-transcript
  diff gate now in preflight.py. Full run report: `BUILD-LOG.md` (2026-07-13 run).

### 2026-07-12 · career-building_early-career-boost (seed)
- [env] `npx hyperframes tts` resolved the wrong Python; `kokoro_onnx` was missing
  on that interpreter → set `HYPERFRAMES_PYTHON` to the env that has it. ~15 min.

### 2026-07-13 · pipeline overhaul (no render)
- [defect] `compile_timeline.py --check` crashed (2-tuple unpack after the
  3-tuple insertions migration) → fixed line 248; tests 20/20. This is what made
  preflight print a traceback instead of "run --apply".
- [tooling] `hooks/pre-tool.sh` hard-blocked every session at 80 tool calls —
  a full build needs 150–300 → defaults raised to 500/350.
- [tooling] check_boundaries.py `attr()` regex matched `data-hf-id` when asked
  for `id` → anchored with a lookbehind; scene ids in findings are now correct.
