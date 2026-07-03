---
source: Live platform — app.thescla.org/member/programs/early-career-boost (observed 2026-07-03 via the learn API; read-only)
---

# Early Career Boost — Lesson Script & Video Style

How SCLA's lesson videos and scripts are built, reverse-engineered from the **Early Career Boost** track so we can generate HeyGen scripts directly from course material. Companion template: [`templates/heygen-lesson-script.md`](../../templates/heygen-lesson-script.md).

> Method: read every section and lesson in the live member app through the platform's `learn` API (read-only, nothing edited). Polls, forms, and the AI-chat component were skipped per scope. Lesson bodies are TipTap rich-text docs; the "script" lives *inside* the lesson body as dedicated blocks.

---

## Program shape

Six sections, 24 components. Component types seen: `lesson`, `segmented lesson`, `poll`, `form`, `chat`, plus an intro `instruction`.

| # | Section | Components (lessons only) |
|---|---|---|
| 1 | Learning Overview | Mini-Syllabus |
| 2 | Clarify Your Direction | What Makes for a Dream Job?; Five Criteria of Engaging Work (segmented); Clarify Your Career Direction; Build Direction Before You Build a Plan; AI Activity – Pattern Finder; Module 1 Check-In |
| 3 | How to Make Quality Career Decisions | Using the Career Mapping Tool; How to Make Strong Career Decisions; Finding & Creating a Career Purpose Statement; The Career Decision Making Process; Better Decisions Come From Better Criteria; Activity 2; Compare 3-5 Career Paths; AI Activity – Career Decision Maker |
| 4 | BONUS: Career Planning for the AI-Era | Skills for the AI-Era Future; Do Not Just Ask What AI Replaces; How Might AI Touch My Fields? |
| 5 | Completion & Next Steps | Congratulations! |
| 6 | Resources | Early Career Boost Resources |

Typical lesson runs **1–8 min** of study time; a section is **~20–50 min**.

---

## Current video state (why we need HeyGen)

- **Videos are hosted on Wistia** (`sclc.wistia.com`).
- **Only ~4 lessons are actually produced** to video today: Mini-Syllabus, Using the Career Mapping Tool (×2 clips), How to Make Strong Career Decisions.
- **Most lessons are text + a drafted "video script" that has never been produced.** That gap is exactly what HeyGen fills.
- Navigation gate: learners **must watch the video and scroll to the bottom** before the "Continue" button unlocks (`nextDisabled: scroll_to_bottom`). Every lesson with a video slot expects a video to exist.

---

## Presenter persona

The on-camera voice is **"Ann," a career coach and educator** (introduced in the Mini-Syllabus). Scripts are written first-person-as-Ann / direct-to-learner. HeyGen avatar + voice should stay consistent with a warm, encouraging coach — not a corporate narrator.

---

## Two script styles in the wild

The track contains **two generations of script**. Style B is the one to standardize on.

### Style A — inline conversational (older, 80,000-Hours-derived lessons)
Blocks headed **`Video Script: [Segment Name]`** dropped straight into the lesson body, often 2+ per lesson. Long, essay-like spoken prose (~700–1,600 words/lesson across segments). Heavy rhetorical questions, casual asides ("Whoa!", "That's crazy, right?"), references to the poll the learner just answered. No separate visual direction.
*Example — "What Makes for a Dream Job?" opens on-page with a 1-sentence hook, then a `Video Script: Opening` block that expands the same hook into ~250 spoken words.*

### Style B — structured production spec (newer lessons) ✅ target
A clean, HeyGen-ready package with four labeled blocks:

1. **`Body copy`** — the on-page written teaching text (what stays on screen).
2. **`Video asset`** — `Title:` + `Length:` (5–7 min).
3. **`Full video script`** — narration with inline visual cues: `[On screen: …]` and `[Graphic: …]`.
4. **`Graphics and design notes`** — a bulleted shot list of every title card / diagram.

Style B scripts run **~400–650 words** per lesson video. Adopt Style B for all new work.

---

## Anatomy of a lesson → script mapping

The reverse-engineering payoff — how written lesson material becomes the spoken script:

| Lesson material | Becomes in the script |
|---|---|
| Lesson objective / section goal | **Opening hook** — reframed as a provocative question or a myth to bust ("people imagine there is one right answer… most decisions don't work that way") |
| The common mistake the lesson corrects | Stated early, then **reframed** ("shift from pressure to process") |
| Key teaching points / bullet list | Narration body — **each point expanded conversationally** with one concrete example or stat |
| On-page bullets, frameworks, data | **Visual cues** — bullets become `[Graphic: cards appear…]`, charts become `[On screen: …]` |
| The tool or activity the lesson leads into | **Closing** — "In this module, you will…" hands off to the activity/tool |
| — | Warm sign-off that lowers anxiety ("you do not need to panic… you do need to adapt") |

---

## Voice & style rules (observed)

- **Second person, direct address.** "You are starting your career at a time when…"
- **Open with a hook or myth-bust**, not a definition.
- **Short punchy sentences interleaved with longer explanatory ones.** Fragments are used for rhythm ("Intern. Analyst. Coordinator.").
- **Rhetorical questions** to carry transitions ("So what should you do?").
- **Concrete anchors** — real numbers and studies (80,000 hours; the Canadian-students passion survey; income-vs-happiness data). Module 1 content derives from the **80,000 Hours** career guide.
- **Coaching, reassuring tone** — normalize uncertainty, then give a process.
- **End by pointing to action** — the next activity, tool, or reflection.
- **Length target: 5–7 min (~450–650 words).**

---

## Known cleanup items for reuse

- **Citation residue.** Style B scripts contain trailing AI-research artifacts like `aspeninstitute+1`, `americasucceeds+1`, `indeed+1`, `ocs.yale+1`, and a stray `docs.yale+1`. These are Perplexity-style source tags left in the narration — **strip them before production.**
- **Double-spaces and trailing spaces** in headings/titles are common.
- Some images are inline **base64** (heavy); others are `/api/shared/file/{id}` references.

---

## How to use this

1. Take any lesson's written material (objective + key points + the tool/activity it feeds).
2. Run it through [`templates/heygen-lesson-script.md`](../../templates/heygen-lesson-script.md), which encodes the Style B structure and the voice rules above.
3. Keep Ann's coaching voice, 5–7 min length, and the `[On screen:]` / `[Graphic:]` cue convention so the shot list drops straight into HeyGen.
