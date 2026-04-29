# SCLA Profile — Pipeline Review & Template Patch Design

**Date:** 2026-04-29
**Status:** Approved
**Scope:** Merge completed pipeline run to main; identify and apply template patches

---

## What this spec covers

The scla-profile project was initialized from a template. A full 5-stage onboarding pipeline run was completed on a feature branch (`claude/review-dashboard-handoff-GKn4l`). This spec documents:

1. What the pipeline actually produced
2. What broke or was missing
3. The template patches required to prevent the same gaps for the next client

---

## Pipeline run results

### What succeeded
- Artifacts pipeline (4 meeting notes + stakeholder doc) — high confidence, full output
- All 5 output stages generated scaffold files (brand, kb, workflows, source-of-truth)
- `INGEST_ERRORS.md` correctly documented every failure with actionable remediation
- Frontmatter stamping hook ran correctly on all writes
- Agent contracts (one agent, one directory) held throughout

### What was blocked
- **Website ingest (Stage 1):** Sandbox egress proxy returned HTTP 403 for all `thescla.org` URLs. The web-scraper fell back to Google search index snippets — approximately 7 KB of low-confidence text.
- **Docs inbox (Stage 1):** Empty at run time. No PDFs or Google Doc exports were dropped in.
- **Empty URL field in config:** `sources.docs[1].url: ""` triggered ERROR-003. A blank string should be ignored, not treated as an error.
- **Artifacts not auto-detected:** Files were placed in `_raw/artifacts/inbox/` manually but skipped by the ingestor because `sources.artifacts` was empty in the config. A human had to register them in `client.config.yml` mid-run.

### Confidence at completion

| Stage | Confidence | Root cause of gap |
|---|---|---|
| Ingest | Partial | Egress proxy blocked website |
| Brand | Low | Depends on website copy |
| Knowledge Base | Low | Depends on website copy |
| Workflows | High | Artifacts were high-quality |
| Source of Truth | High | Synthesized from available data |

---

## Template patches required

### Patch 1 — `web-scraper/SKILL.md`: Add egress fallback strategy

**Problem:** The skill says "log 403 to INGEST_ERRORS.md, continue" but gives no guidance on what to do with blocked environments. The agent improvised a Google snippet fallback that wasn't codified anywhere.

**Fix:** Add a `## Egress-blocked environments` section:
- If `WebFetch` returns 403 for all paths, attempt a Google search index snapshot as a low-confidence fallback
- Stamp the file with `fetch_status: 403_BLOCKED` in frontmatter
- Document Option B (run from external machine) as the preferred path, not a fallback

---

### Patch 2 — `client.config.yml` template: Remove empty URL placeholder

**Problem:** `sources.docs: [- url: ""]` is an empty string that the ingestor treats as a URL to fetch, producing ERROR-003.

**Fix:** Comment it out or remove it from the default template. Only list real values.

---

### Patch 3 — `ingestor` agent: Auto-scan artifact inbox

**Problem:** Files placed in `client/_raw/artifacts/inbox/` were silently skipped because `sources.artifacts` was an empty list. A human had to register them mid-run.

**Fix:** The ingestor should always scan `client/_raw/artifacts/inbox/` for files and process any it finds, regardless of whether they appear in `sources.artifacts`. The config list is for labeling/tracking, not gating.

---

### Patch 4 — `/onboard` preflight: Expand validation

**Problem:** The preflight only checks `client.name` and `client.slug`. Three other fields caused problems:
- `primary_contact.email` was never filled (empty throughout the run)
- `sources.websites[0].url` was still `example.com` in early iterations
- `collab.canonical_home` was empty when Stage 5 ran (source-of-truth README has no home to point to)

**Fix:** Add to preflight:
1. Warn if `primary_contact.email` is empty
2. Error if any website URL is still `example.com`
3. Warn before Stage 5 if `collab.canonical_home` is empty

---

### Patch 5 — `/status` command: Remove dead `gates.*` reference

**Problem:** The `/status` command says "compare each stage's confidence to `client.config.yml → gates.*`" but no `gates` key exists in the config template. This is a broken reference.

**Fix:** Either add a `gates:` block to the config template, or remove the reference from `/status` and hard-code minimum confidence thresholds.

---

### Patch 6 — `CLAUDE.md`: Warn about sandbox egress constraints

**Problem:** `CLAUDE.md` instructs Claude to scrape client websites as if `WebFetch` always works. In Claude's execution sandbox, most external domains are blocked by an egress proxy.

**Fix:** Add a note under the ingest stage:

> **Egress note:** `WebFetch` is blocked for most external domains in Claude's sandbox environment. If the ingestor returns 403 for all website URLs, run the web-scraper from a machine outside the sandbox and commit results under `client/_raw/web/`. Do not rely on Option A (manual page export) as the primary path — it is slow and error-prone at scale.

---

## What does NOT need patching

- Agent contracts (one agent, one directory) — held correctly, no changes needed
- Frontmatter hook — ran on every write without intervention
- `INGEST_ERRORS.md` format — well-structured and actionable, no changes
- Pipeline gate structure — human gates between stages worked as intended
- `.source-of-truth-generated` marker — correctly prevented Stage 5 re-runs
