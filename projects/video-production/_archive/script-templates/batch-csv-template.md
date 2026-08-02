# Batch Video CSV Template Guide

Reference for structuring CSV files for bulk video generation in Synthesia and HeyGen.

---

## Synthesia Bulk Personalization CSV

Used for generating multiple personalized videos from one template.

### Column Structure

```csv
video_title,scene_1_script,scene_2_script,scene_3_script,scene_4_script,avatar_id,background_id
```

### Example Row

```csv
"Course 1 - Video 1: What is Leadership","Welcome to SCLA's Leadership Foundations course. In this video...","Leadership is the ability to...","Here's an example from a real student...","Your key takeaway today is...","avatar_001","bg_education_blue"
```

### Claude Prompt to Generate Synthesia CSV

```
I'm creating a complete course with [N] videos for SCLA.
Course: [COURSE NAME]
Outline: [PASTE OUTLINE]

For each video in the outline, write a 4-scene script:
- Scene 1: Hook + learning objective (75 words, ~30 sec)
- Scene 2: Core concept (150 words, ~60 sec)
- Scene 3: Example or application (150 words, ~60 sec)
- Scene 4: Summary + transition (75 words, ~30 sec)

Output as a CSV with these exact columns:
video_title, scene_1_script, scene_2_script, scene_3_script, scene_4_script

Use SCLA's warm, professional, encouraging voice.
No markdown in the script fields — plain text only.
Wrap all fields in double quotes. Escape internal quotes as "".
```

---

## HeyGen Batch Mode CSV

Used with HeyGen's Batch Video Creator for personalized or multi-variant generation.

### Column Structure (Standard)

```csv
variable_name,variable_value,video_title
```

### Column Structure (Personalized outreach)

```csv
recipient_name,recipient_role,topic,cta_link,video_title
```

### Example Rows

```csv
recipient_name,recipient_role,topic,cta_link,video_title
"Alex Chen","Student Leader","leadership fundamentals","https://scla.org/course1","Leadership Intro - Alex"
"Jordan Rivera","Chapter President","chapter management","https://scla.org/chapter","Chapter Management - Jordan"
```

### HeyGen Batch Upload Steps

1. Build your template in HeyGen with variable fields marked as `{{variable_name}}`
2. Prepare your CSV with one row per output video
3. HeyGen → **Batch Video Creator** → Upload CSV
4. Map CSV columns to template variables
5. Submit — HeyGen generates all videos concurrently (up to 10 simultaneous)

---

## HeyGen Bulk Translation CSV

Used with HeyGen's `/v2/video_translate` API endpoint.

### Column Structure

```csv
source_video_url,target_language_code,output_title,translation_mode
```

### Language Codes Reference (Common)

| Language | Code |
|---|---|
| Spanish (Latin America) | `es` |
| Portuguese (Brazil) | `pt` |
| French | `fr` |
| Mandarin Chinese | `zh` |
| Hindi | `hi` |
| Arabic | `ar` |
| Korean | `ko` |
| Japanese | `ja` |

Full list: 175+ supported. See HeyGen docs for complete codes.

### Example Rows

```csv
source_video_url,target_language_code,output_title,translation_mode
"https://host.example.com/media/abc123","es","Course 1 - Video 1 (Spanish)","hyperrealistic"
"https://host.example.com/media/abc123","pt","Course 1 - Video 1 (Portuguese)","hyperrealistic"
"https://host.example.com/media/abc123","fr","Course 1 - Video 1 (French)","audio_dubbing"
```

### Translation Mode Notes

- `hyperrealistic` — Full AI lip-sync re-animation. Best for AI avatar videos. Requires clear face visibility.
- `audio_dubbing` — Voice only, no lip sync. Best for live-actor footage.

---

## Hosting Platform Bulk Upload Metadata CSV

For setting metadata when batch-uploading finished videos to the hosting platform via API or Zapier. Column names are platform-neutral — map them to whatever host SCLA lands on.

### Column Structure

```csv
file_path,hosting_project_id,title,description,tags
```

### Example Row

```csv
"/exports/course1-video1.mp4","abc123xyz","Leadership Foundations: What is Leadership","An introduction to core leadership concepts for college students. Covers definitions, examples, and self-assessment.","leadership,foundations,course1,introduction,college"
```

### Claude Prompt for Upload Metadata

```
Generate hosting-platform upload metadata for [N] course videos.
Course: [NAME]

For each video, provide:
- title: SEO-friendly, under 60 characters, include course name
- description: 2–3 sentences. Include primary keywords. Written for college students.
- tags: 5–7 comma-separated tags (no spaces after commas)

Videos:
[PASTE video titles or script summaries]

Output as CSV with columns: video_number, title, description, tags
```
