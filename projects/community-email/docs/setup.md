# Setup and writing format

## Writing

Use paragraphs beginning `Subject: ` and `Preview: `, then write the email body below. Heading 2 starts an optional section. Delete an entire section to omit it; move blocks to reorder it. A paragraph containing only one linked label becomes a gold button. Links within a sentence remain normal links.

Images need a public HTTPS URL and a descriptive caption. Uploaded Notion image links expire and are rejected. Unsupported content stops generation rather than being silently omitted.

## Cloud connection

Planned flow: Notion button → authenticated hosted trigger → GitHub Actions → latest Notion page body → validated MJML returned to Notion.

The reusable template retains the SCLA header, signoff, colors, and merge fields. Generated copy is never committed to this public repository. The converter does not send email or write to the SCLA dashboard.

Activation still requires an approved Notion connection, Infisical access for the workflow, and a hosted trigger. No connection is active yet.
