# `scripts/`

Small utilities that run outside Claude Code.

## Which script do I want?

```
                 ┌───────────────────────────────────────┐
                 │  Starting a NEW client?               │
                 └───────────────┬───────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                          │
               Using GitHub?                Not using GitHub
                    │                          │
                    ▼                          ▼
     Press "Use this template"        ./scripts/bootstrap.sh
     on GitHub (preferred)            (local clone + git init)

                 ┌───────────────────────────────────────┐
                 │  Existing client repo, want latest    │
                 │  engine improvements?                 │
                 └───────────────┬───────────────────────┘
                                 ▼
                      ./scripts/update-engine.sh
```

## `bootstrap.sh` — local-only alternative to GitHub's template button

Clone this template into a fresh per-client directory:

```bash
./scripts/bootstrap.sh acme-corp
# → creates ../acme-corp-onboarding/ (initialized as its own git repo)
```

It:
1. Copies the template (excluding `.git` and any previously generated client content).
2. Replaces `<client-slug>` in `client.config.yml` with the slug you passed.
3. Initializes a fresh git repo with an initial commit.

After it runs, you edit `client.config.yml` inside the new directory and then
run `/onboard` in Claude Code.

**When to use this over GitHub's "Use this template":** if you're not pushing
to GitHub yet, working offline, or prototyping the template itself.

## `update-engine.sh` — pull latest engine into an existing client repo

Sync the `.claude/`, `templates/`, `scripts/`, and `docs/` folders from the
upstream template repo into the current repo. **Never touches** `client/` or
`client.config.yml`.

```bash
./scripts/update-engine.sh
```

Env vars (optional):

```bash
UPSTREAM_TEMPLATE_URL=https://github.com/your-org/client-onboarding \
UPSTREAM_BRANCH=main \
./scripts/update-engine.sh
```

After it runs, review with `git diff` and commit when happy.
