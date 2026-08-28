# Notion → GitHub → same-page MJML

## Writing and generation

Use one shared working draft. Write email content in the page body, beginning with Subject and Preview paragraphs. A Heading 2 named **End of email** marks where writing ends. Keep instructions, the Generate MJML button, request list and generated output below that marker.

Click **Generate MJML** once after editing. The button adds a Queued request to the private Email generation requests database. GitHub checks every ten minutes, reads the current saved draft, validates MJML and writes a code block inside **Generated MJML — copy into SCLA** on the same page. The code caption shows its generation time. Copy the subject separately.

Request states: Queued → Processing → Ready, or Error. Read Note for the result. While Queued or Processing, earlier code is not the current output. After Error, do not assume earlier code includes your changes. Fix the draft and request another generation. Stop editing while Processing; changes detected during conversion stop publication.

Heading 2 begins an email section. Delete or reorder sections freely. A paragraph with just one linked label becomes a gold button; links inside sentences remain links. Bold, italic, underline and strikethrough are preserved. Images need lasting public HTTPS links and descriptive captions. Notion uploads expire and are rejected. Nested content, lists, tables, mentions and inline code are not supported. Subject maximum: 200 characters; preview: 500.

Successful runs append and read back the complete new code before removing earlier generator-owned code blocks. Teammate notes are left alone. Uncertain completion acknowledgements are recovered without converting the same request twice. Requests contain no target page or branch controls: this installation always uses its privately configured draft.

Duplicate-page support is not part of this first installation. Reuse the configured working draft each week; duplicating its button does not change the destination. Preserve a draft separately if you want an editorial archive.

## One-time activation

1. A Notion workspace owner creates or approves an internal connection with Read, Insert and Update content, then shares only the isolated test draft and request database with it. The database needs title **Name**, select **Status** (Queued, Processing, Ready, Error), and text **Note**.
2. Add a button below End of email. Action: Add page to **Email generation requests**; Name: Generate MJML; Status: Queued. Add a confirmation asking people to finish editing before requesting generation.
3. Store these values in the existing Infisical project's dedicated **/community-email** folder: **SCLA_EMAIL_NOTION_TOKEN**, **SCLA_EMAIL_SOURCE_PAGE_ID**, **SCLA_EMAIL_QUEUE_DATA_SOURCE_ID**. The last is the data-source ID, not the database ID. No draft identifiers or content go in the public repository.
4. Create an Infisical machine identity restricted to reading this folder. Configure GitHub OIDC trust for this exact repository, main ref, community-email environment and workflow; restrict claims and audience. Do not reuse the video identity or copy credentials into GitHub. Follow [Infisical's current OIDC instructions](https://infisical.com/docs/integrations/cicd/githubactions); match the actual GitHub subject format.
5. In GitHub, restrict the **community-email** environment to main. Set Actions variables **COMMUNITY_EMAIL_INFISICAL_IDENTITY_ID**, **COMMUNITY_EMAIL_INFISICAL_PROJECT_SLUG**, **COMMUNITY_EMAIL_INFISICAL_ENV_SLUG**. The environment must allow the authorized scheduled worker to run unattended.
6. Set repository variable **COMMUNITY_EMAIL_ENABLED** to **true** only after the connection is configured. Click the test button and manually run **Community email** once; verify Ready and copy the complete same-page code. Also test an invalid draft, corrected retry and duplicate click. Then verify an actual scheduled run.

To pause, set COMMUNITY_EMAIL_ENABLED to false. No relay, webhook host, Zapier, Make, Codex subscription change or local computer is required. Infisical remains the existing secret store.

GitHub schedules can be delayed or dropped, and public-repository schedules automatically disable after 60 days without repository activity. Keep a manual Run workflow link in the team guide and assign an owner to re-enable an inactive schedule; no automatic keepalive commits. Manual runs still process only queued requests.

## Verification and safety

Run **bash scripts/lint-refs.sh** for repository checks, **bash projects/community-email/run.sh test** for email tests, and **bash projects/community-email/run.sh compile** after installing locked compiler dependencies. CI runs tests and compilation before fetching private settings. Scheduled runs serialize and process at most five requests; unfinished requests remain in Notion for a later run.

Private content stays in memory and Notion, never public logs, commits or Actions artifacts. Error messages are generic. The original Notion database experiment and all SCLA templates remain untouched. The worker cannot send email.

The SCLA dashboard compiler, email-client rendering and test delivery require a human preview/test before member delivery. Passing automated tests alone does not establish a live Notion connection.
