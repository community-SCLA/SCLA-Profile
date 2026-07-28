---
name: new-from-template
description: Start a new, greenfield project under projects/ from one of the four scaffolds in templates/. Use when the user wants to begin a new grant, campaign, content, or program project.
---

# Skill: new-from-template

Use this skill to start a **new, greenfield** project under `projects/`.

## Steps

1. **Pick the scaffold** that matches the work (see `templates/README.md`):
   - `templates/project-grant.md` — grant applications
   - `templates/project-campaign.md` — outreach, recruitment, marketing campaigns
   - `templates/project-content.md` — newsletters, social posts, blog drafts
   - `templates/project-program.md` — program development projects
2. **Copy it** to `projects/<project-name>/CLAUDE.md` (create the folder).
3. **Fill the frontmatter and placeholders** — infer what you can, ask the user for the rest. Delete the template's instruction blocks. Leave any placeholder you can't fill visible (`[KEY]`) so nothing is silently wrong.
4. **Add a routing row** to root `CLAUDE.md`'s Task Routing table if sessions will need to find this project by task.

## Notes

- Video work never starts here — the video pipeline has its own entry points (`/produce-video`, `projects/video-production/CLAUDE.md`).
- If the target file already exists, treat it as an existing project — confirm before overwriting.
