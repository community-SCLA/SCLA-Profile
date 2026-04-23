# 🧱 This is the Template Repo

> **You are looking at the reusable starter.**
> **Do not put real client data here.**

---

## What this means

This repo is a **GitHub Template** (like a cookie cutter 🍪).
Every time you onboard a new client, you press **"Use this template"** on
GitHub and it stamps out a fresh, empty copy for that client.

The copy is its own repo. It has no git history from this one. You can make
it private, add only that client's team, and their data never mixes with
anyone else's.

```
         ┌──────────────────────────────┐
         │  client-onboarding           │   ← you are here (template)
         │  (public or internal;        │     keep it clean, no real client
         │   the engine only — no       │     data, updates go here first
         │   client data)               │
         └──────────────┬───────────────┘
                        │  "Use this template"
      ┌─────────────────┼─────────────────┬──────────────────┐
      ▼                 ▼                 ▼                  ▼
 acme-onboarding   globex-onboarding  initech-onboarding   ...
   (private)         (private)          (private)
```

---

## The rules for this repo

1. **Never commit real client content.**
   `client/_raw/**`, `client/brand/**`, `client/knowledge-base/**`,
   `client/workflows/**`, `client/source-of-truth/**` must stay empty
   (or contain only the README stubs).

2. **Engine-only changes belong here.**
   Updates to `.claude/agents/`, `.claude/commands/`, `.claude/skills/`,
   `.claude/hooks/`, `templates/`, `scripts/`, `CLAUDE.md` — yes.
   Anything client-specific — no.

3. **Test changes on a scratch client repo first.**
   Don't break the template and force every future client to inherit the break.

4. **Every engine change bumps the template.**
   After merging, existing client repos can pull the change with
   `./scripts/update-engine.sh` (see below).

---

## How to make this a GitHub Template (one-time setup)

You need **Admin** access to the repo on GitHub. Do these in the browser:

1. Go to the repo → **Settings** (top nav).
2. Scroll to **"Template repository"** → ✅ check the box.
3. *(Optional)* In **Danger Zone → Visibility**, set to **Private** if you
   don't want the template itself public.
4. *(Optional)* In **General → Repository name**, rename to
   `client-onboarding`.

After that, the repo page shows a green **"Use this template"** button.

---

## How clients get their repo (per-client workflow)

For each new client:

1. On this repo's GitHub page, click **"Use this template" → "Create a new repository"**.
2. Name it `<client-slug>-onboarding` (e.g. `acme-onboarding`).
3. Set **Private** (always — client data is confidential).
4. Add only the people who need to touch this client.
5. Clone locally → edit `client.config.yml` → open Claude Code → `/onboard`.

Full step-by-step with pictures is in [`docs/GUIDE.md`](./docs/GUIDE.md).

---

## How engine updates flow to existing clients

When you improve an agent, fix a skill, or add a command **in this template**,
existing client repos won't know about it automatically. They pull updates on
demand:

```bash
# in any client repo
./scripts/update-engine.sh
```

This pulls the latest `.claude/`, `templates/`, and `scripts/` from the
template without touching `client/` or `client.config.yml`. See
[`scripts/update-engine.sh`](./scripts/update-engine.sh).
