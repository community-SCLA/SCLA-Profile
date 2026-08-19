# Scene Harvest — rebuild kit

The live marking sheet: https://claude.ai/code/artifact/77be9454-6b63-45d5-96d3-ccbe68a31bed

That page is hosted on claude.ai and is independent of this repo and of any
codespace. Marks made on it are saved by its own Save button, which republishes
the page in place. Nothing here is needed to open, mark, or save the sheet.

This folder exists only so the sheet can be **regenerated** if it is ever lost.

| File | What it is |
| --- | --- |
| `lessons.json` | 37 lessons, their scenes, codes and metadata — the sheet's data |
| `thumbs/` | one folder per lesson, the captured scene stills the sheet displays |
| `template.html` | page shell + app JS |
| `build_sheet.py` | inlines data + thumbs into template.html → the publishable file |
| `extract_meta.py`, `capture_*.sh` | how lessons.json and thumbs/ were produced |

Rebuild: `python3 build_sheet.py` in this folder, then publish the output with
the Artifact tool passing the URL above so it updates in place rather than
creating a second sheet.
