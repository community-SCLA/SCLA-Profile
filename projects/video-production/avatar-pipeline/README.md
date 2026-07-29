# Avatar pipeline

Turns a finalized `.txt` script into a rendered MP4 via the HeyGen API. Batch, and
resumable — `state.json` at this folder's root is the resume key, so an interrupted
run picks up at the chunk it died on rather than re-spending credits.

**Agents: read `CLAUDE.md`.** This is the human door.

## Run it

```bash
bash scripts/with-secrets.sh python3 projects/video-production/avatar-pipeline/src/generate_videos.py
```

The Infisical wrapper is not optional — the HeyGen key lives there, never in the repo.

## Where things are

`src/` the code · `config/config.json` avatar, voice, and the lesson list ·
`docs/` an example lesson script · `requirements.txt` pinned deps.

Runtime artifacts (`state.json`, `output/`) are written at this folder's root and are
gitignored. Finished MP4s are filed to `../renders-mp4/<program-slug>/avatar/`.

## When to use this instead of the illustrated path

Translations and multilingual cuts, quick-turn social talking heads, and moments that
genuinely need a human presence on screen. Everything conceptual — frameworks,
processes, decision models — belongs in `../design-system/`, which costs no avatar
credits and stays on-brand by construction.
