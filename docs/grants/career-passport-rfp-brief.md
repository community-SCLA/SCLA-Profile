# California Career Passport Platform — RFP 1980 Brief
## Distilled for SCLA Application

---

## What This Is

An **RFP (Request for Proposal)**, not a traditional grant. SCLA applies as a **vendor** to design, build, and operate a learner-controlled digital credential wallet for California — the "Career Passport." Issued by Foothill-De Anza Community College District on behalf of the California Community Colleges Chancellor's Office (CCCCO).

**The wallet** lets Californians store, manage, and share verified records of skills, academic achievements, workforce experience, licenses, military service, and badges.

**Why SCLA fits:** Career development expertise + equity-centered mission + a tech builder = the combination this RFP is designed for. Most tech vendors won't have SCLA's depth on the populations served.

---

## Submission

- **Platform:** PlanetBids — must register as a vendor
- **Contact:** Annette Perez, perezannette@fhda.edu, (650) 949-6163
- **No paper submittals accepted**
- **Required Forms (1–4)** must be signed and submitted as one combined file alongside the proposal

---

## Key Dates

| Event | Date |
|-------|------|
| **Phase 1 Due** | May 14, 2026 at 2:00PM PST |
| Pilot Selection Notice | May 21, 2026 |
| Board Award Meeting | June 8, 2026 |
| Contracts Executed | June 16, 2026 |
| **Phase 2 Pilot Runs** | June 17 – August 24, 2026 |
| Pilot Interviews | August 27, 2026 |
| **Phase 3 Due** | September 10, 2026 at 2:00PM PST |
| Notice of Award | October 5, 2026 |

---

## Funding

- **Phase 2 pilot:** $125,000–$150,000 per selected proposer (approx. 5 selected)
- **Phase 3 contract:** Up to 5 years (amount negotiated)
- Pilot payment is milestone-based: 20% / 30% / 30% / 20%

---

## Phase 1 — What to Submit (Due May 14)

Two documents submitted together:

### Section One: Innovation Concept Narrative
**Max 20 pages total across 5 questions (~3 pages each)**

**Q1 — Vision of Equity (suggested 3 pages) [20 pts — highest weight]**
- Structural barriers preventing skill/credential recognition for: people without bachelor's degrees, low-income, immigrant/undocumented, military, formerly incarcerated
- How design centers these populations as requirements, not edge cases
- Specific scenario: a person from one of these groups uses the wallet and accesses an opportunity they couldn't before
- How it fits CA's shift from degree-based → skills-informed hiring
- Wallet interoperability: aggregating credentials from other wallets without starting over
- What success looks like at pilot end vs. statewide scale

**Q2 — Technical Architecture and Open Standards (suggested 3 pages) [25 pts — highest weight]**
- Custodial vs. non-custodial vs. hybrid architecture — who controls credential content and keys
- What happens to credentials if SCLA loses the contract or shuts down
- Credential exchange protocol(s) used — must be open standards (proprietary-only = disqualified)
- Privacy: selective disclosure, unlinkability, no metadata leakage to issuers
- Logging: what data is transmitted to vendor servers, who can access it, holder control
- Selective disclosure: comprehensible to users with low technical literacy
- Credential display evolution as standards mature

**Q3 — A Wallet for All Credentials (suggested 3 pages) [15 pts]**
- Handling W3C VCDM credentials with varying metadata richness (rich → sparse)
- Accommodating issuers ranging from large institutions to small workforce providers
- Graceful degradation: how the wallet handles unknown issuers or unfamiliar credential types
- Multi-issuer, multi-credential interoperability testing experience
- Credential lifecycle: revoked, superseded, issuer infrastructure changes
- Portability: how a holder takes credentials to a different wallet

**Q4 — Integration with CA Education and Workforce Ecosystem (suggested 3 pages) [10 pts]**
- Credential presentation across: colleges, employer ATS systems, government HR, workforce agencies, licensing boards
- Relationship to CA digital identity infrastructure (e.g., CA DMV mobile driver's license)
- Making it practical for employers of varying sizes and tech sophistication
- Ecosystem-strengthening vs. platform-centering philosophy

**Q5 — Governance, Trust, and Long-term Stewardship (suggested 3 pages) [10 pts]**
- Credential portability/continuity if organization is acquired or loses contract
- Open verifier ecosystem — any conformant verifier can receive presentations without prior relationship or proprietary tooling
- How the organization stays current with evolving open standards
- Governance: community input, user feedback, State oversight
- Software changes communicated in plain language; accessibility and language access as ongoing commitments
- Security and incident response at statewide scale

---

### Section Two: Pilot Readiness Package
**Max 12 pages total across 3 components**

**Component 1 — Technical Environment Document (max 2 pages)**
Written for the District's technical team. Plain text preferred over diagrams.
- Technical stack, core dependencies, hosting environment
- Issuer endpoint requirements
- What the wallet needs from State issuance infrastructure to receive and display credentials
- Pilot environment setup (separate from production)
- Known constraints, dependencies, assumptions about external systems

**Component 2 — Participant Guide Draft (max 5 pages)**
Plain language, zero jargon without explanation. Must cover:
- Step-by-step: access wallet → create account → receive one test credential
- What the credential is and why it matters to the participant
- Suitable for printing as handout or slide deck
- Screenshots not required; mockups/wireframes acceptable
- Guides with unexplained technical language rated unfavorably

**Component 3 — Facilitator Guide Draft (max 5 pages)**
Written for a non-technical program coordinator. Must cover:
- Step-by-step: wallet access, account creation, identity verification
- Explicit guidance for: incompatible device / can't create account / can't receive credential
- What facilitators may and may not do (process support only — no technical troubleshooting, no directing to UI elements)
- Vendor staff will NOT be present during cohort activity — guides must be self-sufficient
- How the task completion log will be administered

---

## Phase 1 Scoring (100 points)

| Category | Points |
|----------|--------|
| Company Background & Experience | 10 |
| Q1 — Vision of Equity | 20 |
| Q2 — Technical Architecture & Open Standards | 25 |
| Q3 — Wallet for All Credentials | 15 |
| Q4 — Integration with CA Education/Workforce Ecosystem | 10 |
| Q5 — Governance, Trust, Long-term Stewardship | 10 |
| Pilot Readiness — Technical Design | 8 |
| Pilot Readiness — Participant Guide | 1 |
| Pilot Readiness — Facilitator Guide | 1 |
| **Total** | **100** |

---

## Phase 2 — Pilot (June 17–Aug 24, 2026)

Only ~5 selected proposers participate. SCLA would receive $125K–$150K to run this.

**Requirements:**
- Cohort of ~50 California students, workers, or jobseekers assigned by the District
- Pre-pilot integration check within 30 days of selection (must pass or contract terminated at 0% pay)
- Credential diversity: minimum 3 credential types from at least 2 issuers, spanning at least 2 categories (academic, workforce, badge, other W3C VCDM)
- Pilot runs without vendor staff present — participants use guides only
- Live verification during cohort activity (not a controlled test)
- Two instruments: paper task completion log + experience debrief survey

**Three evaluation tiers:**
- Tier 1 — Interoperability: hard pass/fail. Credential must verify via District's verifier tool during live cohort, no vendor intervention. One remediation window (5 business days). Fail = disqualified from Phase 3.
- Tier 2 — Usability: significant portion of participants must complete full workflow independently. Failure is not auto-disqualifying but must be addressed in Phase 3 proposal.
- Tier 3 — Accessibility: structured observation by District. Findings delivered to vendor; must be addressed in Phase 3 proposal.

---

## Phase 3 — Production Proposal (Due Sept 10, 2026)

**Max 25 pages** (excluding cost proposal and forms). Only invited after successful Phase 2.

**Five required sections:**

**A. Refined Production Architecture**
- How architecture evolved from pilot findings
- Statewide scale with State-provided centralized issuance infrastructure
- Privacy properties maintained at scale
- Product roadmap: UX/UI features, accessibility enhancements, functionality
- Standards evolution without disruptive redesign

**B. Implementation and Rollout Plan**
- Reaching populations: unconnected to institutions, limited digital literacy, shared/low-end devices, non-English speakers
- State-directed sequencing dependencies
- Joint operating model for learner support (who owns first-line support, escalation path)
- Measuring and reporting learner adoption/retention by population

**C. Governance and Operating Model**
- Open verifier ecosystem commitment
- State oversight model
- Plain language change communication + accessibility as contractual obligation
- Credential portability across ecosystem evolution

**D. Security, Privacy, and Risk Management**
- Response to pilot accessibility findings (required — proposals without this are incomplete)
- Data minimization and behavioral privacy certification — no credential activity data to vendor/third-party without holder consent, auditable by State
- Value-added analytical services: external data sources, processing location, retention, consent
- Incident response and plain language holder communication

**E. Cost Proposal** (separate from narrative)
- One-time implementation costs
- Ongoing operational costs
- Licensing/subscription fees
- Cost scaling assumptions (per institution, per user, per transaction)
- Multi-year projections

**F. Performance Metrics**
- Learner-facing: onboarding completion rate, credential acceptance rate, presentation success rate, support request rate, user retention
- Accessibility/equity: completion rates by device type/OS, accessibility audit compliance, language access coverage
- Privacy/trust: opt-in rate for value-added services, data minimization compliance
- Disaggregated data for populations the program is designed to serve

---

## Technical Standards SCLA Must Address

These come up across multiple questions and will be evaluated by technical reviewers:

- **W3C Verifiable Credentials Data Model (VCDM) 2.0** — the credential format standard
- **Open Badges v3.0 (OBv3)** — for badge-type credentials
- **Credential exchange protocols** — must use open standards (VC-API/VCALM, OID4VP, or similar); proprietary-only = disqualified
- **Selective disclosure** — user can choose which credential claims to share
- **Unlinkability** — presentations can't be correlated across uses without holder knowledge
- **No metadata leakage** — issuers/verifiers can't track when credentials are used
- **Holder key control** — cryptographic keys stay with the holder, not the vendor

---

## Required Forms (all must be signed and submitted)

1. **Form 1 — Proposal Certification** (truthfulness, understanding of RFP, legal compliance)
2. **Form 2 — Statement of Non-Collusion**
3. **Form 3 — Declaration of Non-Discrimination**
4. **Form 4 — References** — minimum 3 references, projects completed within past 5 years, relevant to: digital credential wallets, credential/identity deployment to diverse populations, education/workforce system integration, or tech pilots with non-traditional learners

---

## Context SCLA Needs to Provide for Writing

For the next chat, gather:
1. SCLA full legal name + year founded
2. Mission (1–2 sentences)
3. Specific populations served (veterans, formerly incarcerated, undocumented, low-income, adults without degrees — which?)
4. Programs offered (especially any credential, digital skills, or workforce-related)
5. Any existing California Community College partnerships or relationships
6. Tech person's background: what they've built, any credential/identity/API experience
7. 3 reference organizations/contacts who can speak to SCLA's work
8. Any existing digital tools or platforms SCLA has built or used
