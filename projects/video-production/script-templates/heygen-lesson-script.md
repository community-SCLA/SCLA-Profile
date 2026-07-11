---
type: content
status: draft
program: <program name>
owner: <name>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
---

# HeyGen Lesson Script — <Lesson Title>

Turn any SCLA program's lesson material into a produce-ready HeyGen video script. Fill the parameters, then the sections. Nothing here is tied to a specific program — presenter, length, and structure are all yours to set.

The only constants are **SCLA's brand voice** and the section structure below (body copy → video asset → script with cues → shot list), which keeps every lesson script in a shape the visual builder and the render pipeline both expect.

---

## Program parameters (set these first)

- **Presenter / persona:** <who is on camera — e.g. a warm career coach, a peer mentor, a subject-matter expert. Name them if the program uses a named presenter, and keep them consistent across the program.>
- **Target length:** <e.g. 2–3 min, 5–7 min, 10–12 min.> Word budget ≈ minutes × ~130 spoken words.
- **Structure:** <how this video is organized — e.g. step-by-step demo, story-driven, Q&A, or the sample teaching arc in section 3.>
- **Voice:** SCLA brand voice. Add any program-specific voice note here.
- **Cue convention:** visuals go inline as `[On screen: …]` (text/data) and `[Graphic: …]` (diagrams/cards). Every cue is repeated in the shot list so it drops straight into HeyGen.

---

## 0. Source material (fill first, then delete)

- **Lesson objective:** <the one thing the learner should leave with>
- **Misconception this lesson corrects (if any):** <what people get wrong>
- **Key teaching points:** <the bullets from the lesson>
- **Concrete anchors:** <stats, studies, examples to cite>
- **Activity or tool this lesson leads into:** <what the learner does next>

---

## 1. Body copy (on-page text)

> The written teaching text that stays on the lesson page alongside the video. 2–4 short paragraphs. Plain, scannable, keeps the key points and any list.

<body copy>

---

## 2. Video asset

- **Title:** <punchy, curiosity-driven>
- **Length:** <your target from the parameters above>

---

## 3. Full video script

> Narration for the HeyGen avatar, in the persona set above. Second person. Open with a hook, not a definition. Short punchy sentences mixed with longer ones. End by pointing to the activity.

The steps below are **one sample arc** — swap or reorder them to fit your program's structure.

**Hook** — reframe the lesson objective with a question or contrast:
<opening lines>

`[On screen: <a visual contrast — "X" vs "Y", right side highlighted>]`

**Name a common mistake, then reframe it:**
<the trap learners fall into → the better frame>

`[Graphic: <cards / labels appearing one at a time, if applicable>]`

**Teach the key points — one at a time, each with a concrete anchor:**
<point 1, expanded conversationally + example/stat>
<point 2 …>

`[Graphic: <bullets appearing as cards / a wheel / a stack>]`

**Hand off to action:**
<normalize the difficulty, then "In this module, you will…" pointing to the tool/activity>

---

## 4. Graphics and design notes (shot list)

> One bullet per visual, in order. Mirror every `[On screen:]` / `[Graphic:]` cue above.

- Title card: "<title>"
- <visual 2>
- <visual 3>

---

## Checklist before production

- [ ] Voice matches the persona set in the parameters — consistent across the program.
- [ ] Opens with a hook, not a definition (unless the program's structure says otherwise).
- [ ] Every key lesson point appears, each with a concrete anchor.
- [ ] Every bullet/framework/stat has a matching visual cue **and** a shot-list line.
- [ ] Closes by pointing to the next activity or tool.
- [ ] Length matches the target (word count ÷ ~130 ≈ minutes).
- [ ] No citation residue (`aspeninstitute+1`, etc.) or double/trailing spaces.
- [ ] Every SCLA fact is real — if it's not in the source material, mark `TODO: needs input`, don't invent it.

## To render via the code pipeline

Copy **only the spoken narration** from section 3 into a plain `.txt` saved directly in `lesson-scripts/<program-slug>/` — drop every cue, heading, and the shot list (those guide the human building visuals, not the avatar). Then point a lesson at the file in `avatar-pipeline/config.json`. See [`avatar-pipeline/CLAUDE.md`](../avatar-pipeline/CLAUDE.md).
