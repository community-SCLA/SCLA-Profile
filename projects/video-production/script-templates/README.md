# Script templates

Claude prompt scaffolds for producing lesson narration, plus the human QA checklist.

These are **prompts and scaffolds, not video templates.** The actual scene templates —
the twelve `scla-*.html` sub-compositions — live in `../design-system/compositions/`.
The two got confused often enough that this folder was renamed from `templates/` in
July 2026 to stop it happening again.

## What each is for

Pick by output path, not by name:

- **Illustrated lesson videos** (the default) don't start here. They start at
  `/refine-scripts`, which drains raw `.txt` files from `../lesson-scripts/<program>/`.
- **HeyGen avatar work** uses `heygen-lesson-script.md` (the scaffold) and
  `heygen-narration-prompt.md` (plain narration, no cues to strip → `../avatar-pipeline/`).
- **Synthesia course/certificate videos** use `course-script-prompt.md` (B-roll markers).
- **Social** uses `social-script-prompt.md`.
- **Bulk generation** CSV specs are in `batch-csv-template.md`.
- **`qa-checklist.md`** is the human review step, not an agent gate. The mechanized
  gates live in `../render-qa/`.

## The rule that outranks everything here

Never fabricate SCLA course content. Work only from provided outlines and source
material. This is enforced by the qa-facts pass at `/refine-scripts` and the
script-vs-transcript diff in `../render-qa/src/preflight.py` — but the templates are
where the temptation starts.
