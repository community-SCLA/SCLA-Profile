## Current Priorities

### Next Up: Run the Pipeline
The pipeline infrastructure is complete. The knowledge base has not been built yet.

**Step 1** — Run `/ingest` to crawl thescla.org and populate `client/_raw/web/`
**Step 2** — Drop any existing SCLA docs (PDFs, exports) into `client/_raw/docs/inbox/`
**Step 3** — Run `/onboard` to execute all five stages end-to-end
**Step 4** — Review `client/source-of-truth/` and fill in gaps that require human input (per `HANDOFF.md`)

### Open Questions
- Are there Slack exports or Google Drive docs to include in the initial ingest?
- Is the thescla.org crawl depth of 2 sufficient, or should it go deeper?

### Not Started Yet
- Figma/brand assets import
- Workflow mapping (needs Slack or ticket data)
- Automation opportunity review
