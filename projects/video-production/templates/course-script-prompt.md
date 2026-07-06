# Course Script Prompt Template

Use this prompt in Claude to generate scene-by-scene scripts for course and certificate videos.

**Target tool:** Synthesia  
**Target length:** 5–15 minutes  
**Output format:** Scene-by-scene with B-roll markers

---

## Prompt (copy and fill in brackets)

```
I'm creating a training video for an SCLA course called [COURSE NAME].

Audience: [SCLA MEMBER SEGMENT] [TOPIC/CAREER AREA].
Video number: [NUMBER] of [TOTAL] in this course.
Video title: [TITLE]
Target duration: [X] minutes
Style: AI avatar with B-roll and motion graphics

Structure each video as:
1. Hook / Problem Statement — open with a relatable challenge or question
2. Key Concept Explanation — clear, jargon-free explanation
3. Practical Example or Story — concrete, real-world application
4. Key Takeaways — 2–3 bullet-point summary
5. Call to Action — what to do or think about next

Tone: Warm, professional, encouraging. Active voice. No jargon.
Format: Write each section as a separate paragraph.
Mark [B-ROLL: description] anywhere motion graphics or visuals should appear.
Keep each paragraph to approximately 30 seconds of speaking time (75–90 words).
Do NOT include stage directions, speaker names, or timestamps.

Source material:
[PASTE COURSE OUTLINE, NOTES, OR SOURCE CONTENT HERE]
```

---

## After Receiving the Script

1. Read the complete script — check for factual accuracy against source material
2. Verify tone matches SCLA brand voice
3. Confirm length (word count ÷ 130 = approximate minutes)
4. Mark any sections needing revision before sending to Synthesia
5. Copy approved script into Synthesia template scene fields

---

## QA Prompt (run after script is generated)

```
Review this AI-generated script for an SCLA training video.
Check for:
- Factual accuracy (flag any claims that need verification)
- Tone alignment with SCLA brand (warm, professional, encouraging)
- Clarity for college students ages 18–24
- Any awkward phrasing or passive voice
- B-roll markers that are unclear or impractical

Flag issues with [REVIEW NEEDED] and suggest fixes inline.

Script:
[PASTE SCRIPT HERE]
```
