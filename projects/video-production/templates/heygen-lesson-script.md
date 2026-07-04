---
type: content
status: draft
program: <program name>
owner: <name>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
---

# HeyGen Lesson Script — <Lesson Title>

Turn any SCLA program's lesson or course material into a produce-ready HeyGen video script in SCLA's **Style B** house format. Style B and its origins are documented in [`programs/early-career-boost/video-style.md`](../../../programs/early-career-boost/video-style.md) — that's the worked example this template generalizes, not a constraint on which program you're writing for.

> **Set the program parameters below first.** Presenter, length, and arc differ by program — nothing here is hard-wired to one track. The Style B *structure* (body copy → video asset → script with cues → shot list) and SCLA's brand voice are the only constants.

---

## Program parameters (set these first)

- **Presenter / persona:** <who is on camera — e.g. "a warm, encouraging career coach," "a peer mentor," "a subject-matter expert." Name them if the program uses a named presenter.> Keep this persona consistent across every video in the program.
- **Target length:** <set per program — e.g. 2–3 min, 5–7 min, 10–12 min.> Word budget ≈ minutes × ~130 spoken words. (5–7 min ≈ 450–650 words; adjust to your target.)
- **Narrative arc:** default is the Style B arc in section 3 below (hook → name the mistake → teach → hand off). Override it if the program's content calls for a different structure (e.g. step-by-step demo, story-driven, Q&A).
- **Voice:** SCLA brand voice — warm, professional, encouraging — per [`brand/voice-and-tone.md`](../../../brand/voice-and-tone.md). Add any program-specific voice note here.
- **Cue convention:** put visuals inline as `[On screen: …]` (text/data) and `[Graphic: …]` (diagrams/cards). Every cue is repeated in the shot list at the bottom so it drops straight into HeyGen.

---

## 0. Source material (fill first, then delete)

- **Lesson objective:** <the one thing the learner should leave with>
- **The misconception / mistake this lesson corrects:** <what people get wrong>
- **Key teaching points:** <the bullets from the lesson>
- **Concrete anchors:** <stats, studies, examples to cite>
- **Activity or tool this lesson leads into:** <what the learner does next>

---

## 1. Body copy (on-page text)

> The written teaching text that stays on the lesson page alongside the video. 2–4 short paragraphs. Plain, scannable, keeps the key points and any list.

<body copy>

---

## 2. Video asset

- **Title:** <punchy, curiosity-driven — e.g. "Who You Are Before Your Job Title">
- **Length:** <your target from the parameters above>

---

## 3. Full video script

> Narration for the HeyGen avatar, in the persona set above. The steps below are the default Style B arc — swap or reorder them if your program uses a different structure. Second person. Open with a hook, not a definition. Short punchy sentences mixed with longer ones. Use rhetorical questions to transition. End by pointing to the activity.

**Hook (myth-bust or provocative question)** — reframe the lesson objective:
<opening lines>

`[On screen: <reframe as a visual contrast — "X" vs "Y", with the right side highlighted>]`

**Name the common mistake, then reframe it:**
<the trap learners fall into → the better frame>

`[Graphic: <cards / labels appearing one at a time, if applicable>]`

**Teach the key points — one at a time, each with a concrete anchor:**
<point 1, expanded conversationally + example/stat>
<point 2 …>
<point 3 …>

`[Graphic: <bullets from the lesson appearing as cards / a wheel / a stack>]`

**Reassure, then hand off to action:**
<normalize the difficulty; then "In this module, you will…" pointing to the tool/activity>

---

## 4. Graphics and design notes (shot list)

> One bullet per visual, in order. Mirror every `[On screen:]` / `[Graphic:]` cue above.

- Title card: "<title>"
- <visual 2>
- <visual 3>
- <visual 4>

---

## Checklist before production

- [ ] Voice matches the persona set in the parameters — consistent across the program.
- [ ] Opens with a hook/myth-bust, not a definition (unless the program's arc says otherwise).
- [ ] Every key lesson point appears, each with a concrete anchor.
- [ ] Every bullet/framework/stat has a matching visual cue **and** a shot-list line.
- [ ] Closes by pointing to the next activity or tool.
- [ ] Length matches the program's target (word count ÷ ~130 = approx. minutes).
- [ ] **No citation residue** (`aspeninstitute+1`, `indeed+1`, etc.) or double/trailing spaces.
- [ ] Any SCLA fact in the script is real — if it's not in the source material, mark `TODO: needs input`, don't invent it.

## To render via the code pipeline

To batch-render this in HeyGen via [`heygen-pipeline/`](../heygen-pipeline/CLAUDE.md): copy **only the spoken narration** from section 3 into a plain `.txt` in `heygen-pipeline/scripts/` — drop every `[On screen:]`/`[Graphic:]` cue, heading, and the shot list (those guide the human building visuals, not the avatar). Then point a lesson at the file in `config.json`.
