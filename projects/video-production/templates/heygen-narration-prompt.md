# HeyGen Narration Script Prompt Template

Use this prompt in Claude to generate **plain narration** for course/lesson videos rendered through the code pipeline.

**Target tool:** HeyGen — code path ([`heygen-pipeline/`](../heygen-pipeline/CLAUDE.md))
**Target length:** set per program (word budget ≈ target minutes × ~130 spoken words)
**Output format:** Plain narration only — the exact words the avatar speaks, nothing else

> **Set the bracketed parameters per program.** Presenter/persona, target length, audience, and the narrative arc are not fixed to one program — fill them in for the track you're writing. Only SCLA's brand voice and the "spoken words only" output rule are constant.

> **Why this is different from [`course-script-prompt.md`](course-script-prompt.md):** that prompt targets **Synthesia** and emits `[B-ROLL:]` markers and scene structure for a human building visuals. This one feeds the **HeyGen API pipeline**, which sends the raw `.txt` straight to the avatar — so any heading, cue, speaker name, or markdown symbol would be **read aloud**. Output here must be nothing but spoken sentences. For the rich, cue-annotated authoring doc, use [`heygen-lesson-script.md`](heygen-lesson-script.md) instead; this prompt is the fast path when you only need narration.

---

## Prompt (copy and fill in brackets)

```
Write the spoken narration for an SCLA [PROGRAM NAME] video. This text goes directly
to an AI avatar (HeyGen) that will read it aloud word-for-word, so output ONLY the
words to be spoken.

Lesson: [LESSON NUMBER] — [LESSON TITLE]
Audience: [WHO THIS PROGRAM SERVES — e.g. SCLA college-student members ages 18–24
preparing for TOPIC / CAREER AREA].
Target length: [SET PER PROGRAM — e.g. 2–3 min, 5–7 min. Word budget ≈ minutes × ~130.].

Presenter voice: [PERSONA — e.g. a warm, encouraging career coach; a peer mentor;
a subject-matter expert. Name them if the program uses a named presenter.] speaking
directly to one learner. Second person ("you"). Warm, professional, encouraging
(SCLA brand voice). Active voice. Short punchy sentences mixed with longer ones.
No jargon, no corporate speak.

Follow this arc (default — replace if the program uses a different structure):
1. Hook — open with a myth-bust or provocative question that reframes the lesson
   objective. Never open with a definition.
2. Name the common mistake — the trap learners fall into — then reframe it.
3. Teach the key points one at a time, each grounded in a concrete anchor
   (a stat, study, or real example). Use rhetorical questions to transition.
4. Reassure — normalize the difficulty — then hand off to the activity: point to
   what the learner does next in this module.

Hard rules:
- Output ONLY spoken words. NO headings, NO section labels, NO speaker names,
  NO timestamps, NO stage directions, NO [cues] or [B-ROLL] markers, NO markdown
  (no **bold**, #, -, or bullet symbols). Any such character will be read aloud.
- Separate paragraphs with a single blank line for readability. Nothing else.
- Do not invent any SCLA fact, stat, program name, or claim. If the source
  material does not support it, write "TODO: needs input" instead of guessing.
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

1. Read the full narration against the source material — flag any claim that isn't supported.
2. Confirm the voice matches the program's persona: second person, warm, direct, no jargon.
3. Check length: word count ÷ ~130 = approximate minutes (compare to the program's target).
4. Confirm it opens with a hook (not a definition) and closes by pointing to the activity.
5. Scan for stray markup, cue residue, or double spaces — remove any before saving.
6. Get human approval **before** rendering (script approval → render is a manual gate — see [`../CLAUDE.md`](../CLAUDE.md)).

---

## QA Prompt (run after narration is generated)

```
Review this narration for an SCLA lesson video that will be read aloud verbatim
by an AI avatar. Check for and flag with [REVIEW NEEDED] inline:
- Any character that isn't spoken words — headings, labels, [cues], markdown
  symbols, stage directions — that would be read aloud by mistake.
- Factual claims that need verification against source material.
- Tone: warm, professional, encouraging (SCLA brand voice); second person; no jargon or passive voice.
- Clarity for the program's audience (see the audience set in the prompt above).
- Opens with a hook (not a definition) and closes by pointing to the next activity.
- Citation residue or double/trailing spaces.

Narration:
[PASTE NARRATION HERE]
```

---

## Save Into the Pipeline

Once approved, this narration is ready to render — no stripping needed (unlike [`heygen-lesson-script.md`](heygen-lesson-script.md), which has cues to remove first):

1. Save the narration as a plain `.txt` in [`../heygen-pipeline/scripts/`](../heygen-pipeline/scripts/) — e.g. `lesson-1.0.txt`.
2. Add the lesson to `heygen-pipeline/config.json` under `lessons`:
   ```json
   "1.0": {
     "title": "Your Lesson Title",
     "source": "local",
     "file": "scripts/lesson-1.0.txt"
   }
   ```
3. Dry-run to preview chunking (the pipeline splits at sentence boundaries, ~200 words/chunk):
   `python generate_videos.py --lesson 1.0 --dry-run`
4. Render one chunk to verify, then the rest — see [`../heygen-pipeline/CLAUDE.md`](../heygen-pipeline/CLAUDE.md).
