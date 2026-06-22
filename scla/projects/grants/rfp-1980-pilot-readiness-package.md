---
source: internal
generated_by: claude-proposal-writer
last_updated: 2026-05-11
status: DRAFT — items marked CONFIRM require tech team input before submission
---

# Pilot Readiness Package
## California Career Passport Platform — RFP 1980

**Proposer:** The Society for Collegiate Leadership & Achievement (SCLA)
**Submitted to:** Foothill-De Anza Community College District / California Community Colleges Chancellor's Office
**Phase 1 Deadline:** May 14, 2026 at 2:00 PM PST

---

## Component 1: Technical Environment Document
*Max 2 pages | Written for the District's technical team*

### Platform overview

The Career Passport pilot will run on a dedicated pilot environment separate from SCLA's production platform at app.thescla.org. The production and pilot environments share no authentication systems, no credential data, and no issuance infrastructure. This separation ensures that pilot activity cannot affect production members and that pilot data can be cleanly archived at the end of Phase 2.

Pilot environment URL: [CONFIRM: e.g., pilot.thescla.org or passport-pilot.thescla.org]

### Technical stack

[CONFIRM WITH TECH TEAM: Complete the table below with actual stack details before submission.]

| Component | Technology |
|---|---|
| Frontend | [e.g., React / Next.js / Vue] |
| Backend | [e.g., Node.js / Python / Rails] |
| Database | [e.g., PostgreSQL — hosted in US-based, FERPA-compliant environment] |
| Credential issuance | VC-API compliant issuer endpoint |
| Credential verification | OID4VP-conformant verifier endpoint |
| Hosting | [e.g., AWS / GCP / Azure] — US-based data residency |
| Authentication | [e.g., OAuth 2.0 with email verification] |
| Revocation | Bitstring Status List v1.0 |
| Credential format | W3C VCDM 2.0, Open Badges v3.0 |

### Issuer endpoint requirements

For an issuing institution to push credentials into the Career Passport pilot, they need one of the following:

**Option A — API integration (for technically equipped institutions):**
- An HTTPS endpoint capable of sending a VC-API-formatted credential offer to SCLA's pilot issuer endpoint
- SCLA provides issuer API documentation and a sandbox testing environment within 15 days of pilot contract execution
- Estimated setup time for a technically equipped institution: 2–5 business days

**Option B — Issuer Portal (for institutions without API capability):**
- Web-based interface, no API integration required
- Issuer logs in, uploads a CSV of recipient names and emails, selects credential type, and clicks Issue
- Credentials are delivered to recipients' wallets automatically
- No developer required; any staff member can operate it after a 30-minute onboarding call

SCLA recommends all pilot issuers complete a test issuance in the sandbox environment before the cohort session begins.

### What the wallet needs from State issuance infrastructure

For credentials issued by State or District systems to appear in the Career Passport wallet:

1. The issuing system must be capable of producing a W3C VCDM 2.0-compliant credential, or SCLA's Issuer Portal can be used as the issuance layer
2. The issuing system must provide or accept a standard credential offer delivery mechanism (email link or VC-API offer endpoint)
3. If revocation is required, the issuing system must maintain a publicly accessible status list endpoint (Bitstring Status List v1.0 recommended)

SCLA requests the District's verifier tool documentation and integration requirements within 5 days of contract execution to begin the integration check process.

### Pilot environment setup timeline

| Milestone | Timeline |
|---|---|
| Pilot environment provisioned | Within 10 days of contract execution |
| Issuer onboarding documentation delivered | Within 15 days of contract execution |
| Integration check with District verifier tool | Within 30 days of contract execution (per RFP requirement) |
| Pilot cohort onboarding begins | Per District-provided schedule |

If the integration check at 30 days reveals issues, SCLA will provide a written remediation plan within 2 business days and implement fixes within the 5-business-day remediation window specified in the RFP.

### Known constraints and assumptions

1. **Device access:** Pilot assumes participants have access to a personal device capable of running a modern web browser (Chrome 90+ or Safari 14+). SCLA will coordinate with the District on device access support options for participants without personal devices before the cohort session begins.

2. **District verifier tool compatibility:** Pilot integration assumes the District's verifier tool is conformant with OID4VP or VC-API presentation protocol. SCLA requests verifier tool documentation from the District within 5 days of contract execution to confirm compatibility before the 30-day integration check.

3. **Minimum issuer count:** Pilot requires credentials from at least 2 issuers. If only 1 external issuer can participate by the cohort start date, SCLA will issue a second credential type directly as a pilot issuer (e.g., a Career Readiness Badge) to meet the RFP minimum.

4. **Email deliverability:** Account creation and credential delivery require email access. SCLA will work with the District to identify participants who may not have reliable email access and develop an alternative delivery pathway before the cohort session.

---

## Component 2: Participant Guide Draft
*Max 5 pages | Plain language — zero unexplained jargon*

---

# YOUR CALIFORNIA CAREER PASSPORT
## A Guide for Participants

This guide will walk you through everything you need to do — one step at a time.

**You do not need any technical experience to complete these steps.**
If something doesn't work, tell your program coordinator. You are not expected to fix anything yourself.

---

### What is a Career Passport?

A Career Passport is a digital wallet that holds proof of what you've learned and what you can do.

Think of it like a folder on your phone that stores your certificates, skills, and achievements — and lets you share them with employers or schools by sending a link, the same way you would share a photo.

Unlike a paper certificate or a file on your computer, a Career Passport credential is **verified**. Anyone you share it with can instantly confirm it is real, who issued it, and when — without calling anyone, waiting for a letter, or paying a fee.

Your Career Passport belongs to you. No one can see what is in it unless you share it.

---

### What you will do today

You will complete five steps:
1. Open your Career Passport
2. Create your account
3. Receive your credential
4. Look at your credential
5. Share your credential with your program coordinator

The whole process takes about 10 minutes.

---

### Step 1: Open your Career Passport

On your phone or computer, open a web browser.

*(A web browser is the app you use to visit websites — like Chrome, Safari, or Firefox.)*

Type this address into the browser bar at the top of the screen:

> **[CONFIRM: pilot URL — e.g., pilot.thescla.org]**

Press Enter or Go.

You should see the Career Passport welcome screen.

**If the page doesn't load:**
Try a different browser. Chrome and Safari work best.
If it still doesn't load, tell your program coordinator.

---

### Step 2: Create your account

On the welcome screen, tap or click **"Create Account."**

You will need to enter:
- Your first and last name
- An email address you can open right now
- A password — choose anything with at least 8 characters

When you are done, tap **"Create Account"** again.

**Check your email.**
You will receive a message with the subject line: "Confirm your Career Passport account."
Open the email and tap or click the link inside.

This confirms that the email address is yours. After you tap the link, your account is ready.

**Common problems:**

| What happened | What to do |
|---|---|
| I don't see the confirmation email | Check your spam or junk folder |
| The link in the email says it expired | Go back to the Career Passport, tap "Resend confirmation," and try again |
| I can't access my email on this device | Tell your program coordinator |
| I got an error when creating my account | Tell your program coordinator and describe what the screen said |

---

### Step 3: Receive your credential

A **credential** is the official record that says you completed something. It is issued by an organization — like a school, a training program, or SCLA — and it appears in your Career Passport wallet.

Your credential will be sent to your wallet by your program coordinator or the issuing organization. You may also receive an email with the subject line: "You have a new credential."

If you receive that email:
- Open it
- Tap or click **"Add to My Career Passport"**
- Your credential will appear in your wallet within 30 seconds

If you do not receive an email and your wallet is empty after 5 minutes of creating your account, tell your program coordinator.

---

### Step 4: Look at your credential

In your wallet, you will see a card with your name and the name of your credential.

Tap or click the card to open it.

You will see:
- **What the credential is** — the name and description of what you completed
- **Who issued it** — the name of the organization that gave it to you
- **When it was issued** — the date it was created
- **What it represents** — the skills or achievements it recognizes

This is your verified record. It is yours to keep.

---

### Step 5: Share your credential

Tap or click the **"Share"** button on your credential card.

You will see two options:
- A **link** you can copy and paste into an email or a job application
- A **QR code** — a square image that anyone can scan with their phone camera

For today's pilot, show the QR code to your program coordinator. They will scan it to confirm that sharing works.

That's it. You are done.

---

### Your credential is yours to keep

Your Career Passport does not disappear when the pilot ends. Your account and your credentials stay with you. You can log back in at any time and share your credentials with anyone.

---

### Questions?

If anything in this guide was confusing, tell your program coordinator. You can also write down your question and hand it to them — you do not have to explain it out loud if you prefer not to.

---

## Component 3: Facilitator Guide Draft
*Max 5 pages | Written for a non-technical program coordinator*

---

# CALIFORNIA CAREER PASSPORT PILOT
## Facilitator Guide

**Who this guide is for:** Program coordinators running the Career Passport pilot with a participant cohort.

**What this guide covers:** How to set up, run, and close out a pilot session.

**You do not need technical experience.** Your job is to help participants complete the steps in their Participant Guide, log what happens, and report issues to SCLA after the session.

---

### Your role — what you may and may not do

**You may:**
- Read the Participant Guide instructions aloud
- Tell a participant which step they are on
- Point to a part of the screen to help orient a participant
- Log issues on the task completion log
- Answer general questions about what the program is and why it exists

**You may not:**
- Enter a participant's password, email, or personal information on their device
- Direct a participant to tap or click a specific button (you may point to the area of the screen, but let the participant tap)
- Attempt to troubleshoot technical errors — log them and move on
- Allow participants to share devices for account creation (each participant needs their own account)

**Why these limits matter:**
The pilot is measuring whether participants can complete the steps on their own, using the guide. If you complete steps for them, the measurement is invalid. Your job is to keep the session moving and capture accurate data — not to ensure every participant succeeds.

---

### Before the session: Setup checklist

Complete this checklist at least one hour before participants arrive.

- [ ] Confirm the pilot URL with SCLA: **[CONFIRM: pilot URL]**
- [ ] Open the pilot URL on a device similar to what participants will use (smartphone, tablet, or computer) and confirm it loads
- [ ] Confirm you have the participant roster with participant IDs (not names — use IDs on the task completion log)
- [ ] Print or share the Participant Guide with each participant (or confirm they received it in advance)
- [ ] Have the task completion log ready — paper or digital, one row per participant
- [ ] Confirm SCLA pilot support contact: **[CONFIRM: support email or phone number for day-of issues]**
- [ ] Review this guide in full

---

### Step 1: Wallet access

Ask participants to open a browser on their device and go to: **[CONFIRM: pilot URL]**

Observe each participant and note the following on the task completion log:
- Device type: smartphone / tablet / computer
- Browser: Chrome / Safari / Firefox / other

**If a participant's device cannot load the page:**
- Note on the task completion log: "Step 1 — device incompatible — [device type if known]"
- Do not delay the group to troubleshoot
- If more than 3 participants cannot load the page, contact SCLA pilot support immediately

---

### Step 2: Account creation

Ask participants to tap "Create Account" and complete the form with their name, email, and a password.

After submitting, they will receive a confirmation email. They need to open it and tap the confirmation link.

Allow up to 5 minutes for this step.

**Common issues and what to do:**

| Issue | What to do |
|---|---|
| Confirmation email not in inbox | Ask participant to check spam. If not there after 2 minutes, log as "confirmation email not received" |
| Link in email says expired | Ask participant to return to the site and tap "Resend confirmation email." If that fails, log the issue |
| Participant has no email access on this device | If they can access email on another device, allow them to do so. If not, log as "no email access" and move to the next participant |
| Account creation shows an error message | Write down the exact error message on the task completion log. Do not attempt to resolve it |
| Participant forgot the password they just created | They can tap "Forgot password" on the login screen to reset it |

Mark Step 2 as complete on the task log when the participant successfully confirms their account and sees their wallet dashboard.

---

### Step 3: Credential delivery

Credentials will be issued to participants' accounts by **[CONFIRM: issuing institution name]**. Participants may also receive an email with the subject line "You have a new credential."

Allow up to 5 minutes after account confirmation for credentials to appear.

**If a participant does not see a credential after 5 minutes:**
- Note on the task completion log: "Step 3 — credential not received — [participant ID]"
- Do not contact SCLA support during the session for individual delivery issues
- Collect all "credential not received" cases and report them to SCLA after the session ends

Mark Step 3 as complete when the participant's wallet shows at least one credential card.

---

### Step 4: Credential viewing

Ask participants to tap their credential card to open the full view.

Observe (but do not prompt): Can the participant identify (a) what the credential is called, and (b) who issued it?

Note any visible confusion — for example, if a participant asks "what does this mean?" or spends more than 30 seconds looking at the screen without responding. These observations go in the experience debrief survey, not the task log.

Mark Step 4 as complete when the participant opens their credential and has viewed it for at least a few seconds.

---

### Step 5: Credential sharing and task log completion

Ask participants to tap the "Share" button on their credential.

Ask them to show you the QR code on the screen.

Use your phone camera to scan the QR code. A verification result should appear within 3 seconds.

If the QR code scan produces a verification result (any result, including "credential details loaded"), mark Step 5 as complete for that participant.

If the QR scan fails or produces an error:
- Write down exactly what appeared on your screen
- Note on the task log: "Step 5 — share/verify issue — [describe what happened]"
- Still mark whether the participant was able to tap Share and produce a QR code (partial completion)

---

### Task completion log

Record the following for every participant:

| Field | What to record |
|---|---|
| Participant ID | Use the ID from your roster — not the participant's name |
| Steps completed | Check each: Step 1 / Step 2 / Step 3 / Step 4 / Step 5 |
| Device type | Smartphone / tablet / computer |
| Browser | Chrome / Safari / Firefox / other |
| Issues encountered | Describe each issue, including exact error messages if visible |
| Notes | Any observation worth flagging (confusion, accessibility needs, language barrier, etc.) |

---

### After the session

Within 24 hours of the cohort session:

- [ ] Submit the completed task completion log to: **[CONFIRM: District contact name, submission method (email / portal / form)]**
- [ ] Send a copy of the task log to SCLA pilot support: **[CONFIRM: SCLA support email]**
- [ ] Report any participants with "credential not received" issues to SCLA so they can investigate and remediate before the next session

SCLA will administer the experience debrief survey digitally to all participants within 48 hours of each cohort session. You do not need to distribute or collect the survey.

---

### If something goes wrong during the session

**Most tech issues:** Log them and move on. The session is not a troubleshooting exercise.

**If the pilot site is completely unreachable for all participants:** Contact SCLA pilot support immediately: **[CONFIRM: support phone number for day-of outages]**

**If a participant has a concern about their personal data:** Direct them to the privacy notice at **[CONFIRM: privacy notice URL]** and to contact SCLA at community@thescla.org

**If a participant needs language support:** **[CONFIRM: note available languages and any interpreter arrangements for the pilot]**

---

### Contact information

| Contact | Purpose |
|---|---|
| SCLA pilot support email: **[CONFIRM]** | Non-urgent issues, post-session reports |
| SCLA pilot support phone: **[CONFIRM]** | Day-of issues, site outages |
| District contact: **[CONFIRM]** | Task log submission, participant roster questions |

---

*End of Pilot Readiness Package*
*This document should be combined with the Innovation Concept Narrative and all four required forms into a single submission file on PlanetBids.*
