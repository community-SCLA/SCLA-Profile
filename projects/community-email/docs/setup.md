# Notion → GitHub → MJML

## What is implemented

The converter reads native Notion blocks, applies the saved SCLA design, validates with MJML, and creates a new export under a configured private Notion results page. Earlier exports are left alone. It does not send email or access the SCLA dashboard.

The hosted trigger starts the workflow on main. Its request cannot choose another repository, branch, source or output. Drafts stay out of this public repository, artifacts and logs.

**Not activated:** Notion access, Infisical trust and trigger hosting still need configuration. The existing Notion database experiment and dashboard templates are unchanged.

## Writing

For the first activation, use one working draft; successful generations create dated exports. The source is configured privately rather than passed in button payloads.

1. Begin with plain paragraphs: `Subject: Your subject` and `Preview: Your preview`.
2. Write normally below. Heading 2 starts a section. Delete an entire section to omit it; move blocks to reorder it.
3. A paragraph containing only one linked label becomes a gold button. Sentence links remain normal links.
4. Use lasting public HTTPS image URLs with descriptive captions. Notion uploads expire and are rejected.

Bold, italic, underline and strikethrough are preserved. Mentions, nested blocks, lists, tables, inline code and other unsupported content stop generation. Limit subject to 200 characters and preview to 500.

Put the writing in a content container, such as a toggle, with Subject and Preview as its first children. Configure that container's block ID as the source. Keep buttons and instructions outside the container. No database is needed.

Stop editing briefly while generating; a second read detects changes before publication. Copy the complete MJML code block from the newest successful export, and paste the subject separately into SCLA. Preview and test there before sending. The dashboard's own compiler version and email-client rendering have not been verified.

## One-time activation

Leave `COMMUNITY_EMAIL_ENABLED` unset until configuration is complete.

1. Approve a Notion connection with Read content and Insert content. Share only the isolated writing area and a separate private results page.
2. In Infisical, create a dedicated `/community-email` folder with `SCLA_EMAIL_NOTION_TOKEN`, `SCLA_EMAIL_SOURCE_BLOCK_ID` and `SCLA_EMAIL_OUTPUT_PAGE_ID`. Do not publish these values.
3. Configure a dedicated Infisical identity with GitHub OIDC trust restricted to the exact repository, main ref and this workflow. Allow only the email folder. Do not reuse the broader video identity or copy Infisical credentials into GitHub.
4. Configure Actions variables `COMMUNITY_EMAIL_INFISICAL_IDENTITY_ID`, `COMMUNITY_EMAIL_INFISICAL_PROJECT_SLUG` and `COMMUNITY_EMAIL_INFISICAL_ENV_SLUG`. Restrict the `community-email` GitHub environment to main and the owner's chosen approval protection.
5. Deploy `src/relay.py` on an approved HTTPS host using a production WSGI server, entry point `relay:application`. Include the repository's existing endpoint registry and add the project's `src` directory to the Python import path. Configure request timeouts, a 64 KB body limit, rate limiting and no body logging. Hosting is not provisioned here.
6. Inject `SCLA_EMAIL_DISPATCH_TOKEN` and `SCLA_EMAIL_TRIGGER_SECRET` into that host from Infisical. Use a fine-grained GitHub token restricted to this repository's Actions write permission, without contents-write access. Use a random trigger secret of at least 32 characters.
7. A Notion **Send webhook** button posts to the host's `/generate` path with the `X-SCLA-Trigger` header. That header needs a copy of the trigger secret; the GitHub token never goes into Notion. Restrict button-configuration access and rotate exposed trigger secrets. Notion requires a paid plan; workspace settings may restrict webhooks.
8. Set `COMMUNITY_EMAIL_ENABLED` to `true`. Run manually with the practice draft and verify the complete Notion export. Then connect and test the button, including rejected content and a successful retry. Do not call it live before these checks.

A 202 response means generation was requested, not completed. Open the Notion results page after the run. Failures create a dated notice when Notion remains reachable; an API outage can prevent that notice. Inspect results before retrying uncertain requests. Repeated clicks can create multiple exports, but cannot send email.

To pause, unset `COMMUNITY_EMAIL_ENABLED` and disable the hosted trigger.

## Checks

`bash scripts/lint-refs.sh` includes the email unit tests. The email workflow also installs the locked compiler and compiles synthetic content. Dependencies install before secrets are fetched, with lifecycle scripts disabled. The live job is manual-dispatch only, main-only and disabled unless explicitly enabled.

Host configuration, Infisical trust and Notion sharing require separate live verification.

Sources: [Notion webhooks](https://www.notion.com/help/webhook-actions), [Notion reads](https://developers.notion.com/reference/get-block-children), [Notion limits](https://developers.notion.com/reference/request-limits), [Infisical OIDC](https://infisical.com/docs/integrations/cicd/githubactions), [MJML validation](https://documentation.mjml.io/).
