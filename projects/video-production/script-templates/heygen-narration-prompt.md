# HeyGen Narration Script Prompt Template

Use this prompt in Claude to generate **plain narration** — the exact words the avatar speaks, nothing else. This feeds the HeyGen API pipeline, which sends the raw `.txt` straight to the avatar, so any heading, cue, speaker name, or markdown symbol would be **read aloud**. Output must be spoken sentences only.

**Target length:** set per program (word budget ≈ target minutes × ~130 spoken words)

> Set the bracketed parameters per program. Presenter/persona, length, audience, and structure are yours to fill in — only SCLA's brand voice and the "spoken words only" rule are fixed.

---

## Prompt (copy and fill in brackets)

```
Write the spoken narration for an SCLA [PROGRAM NAME] video. This text goes directly
to an AI avatar (HeyGen) that will read it aloud word-for-word, so output ONLY the
words to be spoken.

Lesson: [LESSON NUMBER] — [LESSON TITLE]
Audience: [WHO THIS PROGRAM SERVES].
Target length: [SET PER PROGRAM — e.g. 2–3 min, 5–7 min. Word budget ≈ minutes × ~130.].

Presenter voice: [PERSONA — e.g. a warm career coach; a peer mentor; a subject-matter
expert. Name them if the program uses a named presenter.] speaking directly to one
learner. Second person ("you"). Warm, professional, encouraging (SCLA brand voice).
Active voice. Short punchy sentences mixed with longer ones. No jargon.

Structure: [SET PER PROGRAM — e.g. step-by-step demo, story-driven, Q&A. A common
default: hook (reframe the objective, never a definition) → name the common mistake
and reframe it → teach the key points one at a time, each grounded in a concrete
anchor → hand off to the activity the learner does next.]

Hard rules:
- Output ONLY spoken words. NO headings, NO section labels, NO speaker names,
  NO timestamps, NO stage directions, NO [cues] or [B-ROLL] markers, NO markdown
  (no **bold**, #, -, or bullet symbols). Any such character will be read aloud.
- Separate paragraphs with a single blank line. Nothing else.
- Do not invent any SCLA fact, stat, program name, or claim. If the source material
  does not support it, write "TODO: needs input" instead of guessing.
- No citation residue (e.g. "aspeninstitute+1", "indeed+1") and no double or
  trailing spaces.

Source material:
- Lesson objective (the one thing the learner should leave with): [FILL IN]
- The misconception this lesson corrects: [FILL IN]
- Key teaching points (3–6): [FILL IN]
- Concrete anchors (stats, studies, examples to cite): [FILL IN]
- Activity or tool this lesson leads into: [FILL IN]
- Additional source content / course outline: [PASTE HERE]
```

---

## After Receiving the Script

1. Read the narration against the source material — flag any unsupported claim.
2. Confirm the voice matches the program's persona: second person, warm, direct, no jargon.
3. Check length: word count ÷ ~130 ≈ minutes (compare to the program's target).
4. Confirm it opens with a hook (not a definition) and closes by pointing to the activity.
5. Scan for stray markup, cue residue, or double spaces — remove any before saving.
6. Get human approval **before** rendering (script approval → render is a manual gate).

---

## QA Prompt (run after narration is generated)

```
Review this narration for an SCLA lesson video that will be read aloud verbatim
by an AI avatar. Flag issues inline with [REVIEW NEEDED]:
- Any character that isn't spoken words — headings, labels, [cues], markdown
  symbols, stage directions — that would be read aloud by mistake.
- Factual claims that need verification against source material.
- Tone: warm, professional, encouraging (SCLA brand voice); second person; no jargon or passive voice.
- Clarity for the program's audience.
- Opens with a hook (not a definition) and closes by pointing to the next activity.
- Citation residue or double/trailing spaces.

Narration:
[PASTE NARRATION HERE]
```

---

## Save Into the Pipeline

Once approved, the narration is ready to render:

1. Save it as a plain `.txt` directly in [`../lesson-scripts/<program-slug>/`](../lesson-scripts/README.md) — its permanent curated home — named per that folder's convention, e.g. `lesson-1.0_early-career-boost_2026-07-06.txt`.
2. Add the lesson to `avatar-pipeline/config.json` under `lessons`:
   ```json
   "1.0": {
     "title": "Your Lesson Title",
     "source": "local",
     "file": "../lesson-scripts/early-career-boost/lesson-1.0_early-career-boost_2026-07-06.txt"
   }
   ```
3. Dry-run to preview chunking: `python generate_videos.py --lesson 1.0 --dry-run`
4. Render one chunk to verify, then the rest — see [`../avatar-pipeline/CLAUDE.md`](../avatar-pipeline/CLAUDE.md).
