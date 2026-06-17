---
source: "Community Team — internal spec document (uploaded 2026-06-16, not in Drive)"
last_updated: 2026-06-16
confidence: high
notes: >
  Verbatim archive of the independently-authored Member Support Plan Spec.
  Reconciled with the FAQ knowledge-base system in scla/projects/member-support-integration.md.
---

**Member Support Plan Spec Doc** 

**Overview / Prompt** 

This document defines the product and workflow specifications for a unified Member Support plan that consolidates Member Support intake from email and the dashboard/platform into a single operational support system. The current support model already uses a single-source answers document, role-based routing, and a response expectation across inbound email, events, and portal (aka Dashboard) inquiries, so the new system should preserve those operating principles while removing channel fragmentation.

The target state is a single support queue with shared case records, unified routing, consistent templates, clear escalation rules, and bi-directional visibility across email and Dashboard messaging. The system should support both pre-join member and active-member inquiries while reusing the existing Tier 1 and Tier 2 response logic contained in the Member Experience & Support SOP Library.

**Problem Statement**

Members currently access support through multiple email channels and the Dashboard/platform, including messaging, channels, live events, and direct messages. The Dashboard messaging system can now collect questions and respond in-platform, but it is not aligned with the email system, which creates duplicate work, inconsistent visibility, fragmented reporting, and uneven handoffs.

The existing SOP also shows that multiple inboxes currently overlap in responsibilities: Membership@ handles broad member inquiries and refunds; Support@ handles advisor/chapter and technical issues; University Relations@ handles advisor and data-acquisition communication; and Community@ focuses on post-join member support. A comment in the SOP notes a preference to send everything to one (or two) person first and explicitly references "funneling to one vs. two inboxes," which supports the move toward a single front door.

There is an overarching desire for a connected system, viewable by everyone, and executable

**Objectives**

* **Keep, but align, the intake destination** for all Member Support inquiries, regardless of whether they originate from email or the Dashboard/platform.

* **Preserve channel-specific reply behavior**, so members receive responses in a timely and consistent manner.

* **Create one case record per issue** with a full timeline of messages, ownership, status, tags, reply clock, and escalation history.

* **Apply the existing two-tier support logic** to all channels, not only email.

* **Standardize templates**, macros, and decision trees using the existing answers document and SOP examples.

* **Reduce duplicate responses and make ownership visible** without requiring unnecessary behavioral changes, consistent with the current trust-based forwarding model.

**Scope**

**In Scope**

- [ ] Email intake consolidation into one primary support address *(membership@)*

- [ ] Dashboard and in-platform message ingestion into the same support queue *(Community Message Admin*)

- [ ] Case creation, routing, assignment, status tracking, resolutions, and escalation.

- [ ] Template library and macro support based on the current Tier 1 and Tier 2 SOPs

- [ ] Internal notes, handoffs, and audit history.

- [ ] **QUESTION:  In-scope or Out-of-Scope V1?**  Reporting on volume, response time, backlog, system mix, escalation rate, and template usage.

**Out of scope**

* Rewriting the substantive content of every existing response template.

* CRM replacement unless needed for support-case synchronization.

* Large-scale policy redesign outside support intake, routing, and response operations.

* Public knowledge base publishing, unless added in a later phase.

* **Other?**


**Users and Roles**

| Role | Responsibilities |
| ----- | ----- |
| Member / Member | Submits support requests by email or dashboard and receives updates in-channel. |
| Member Advocate (i.e. parent, guardian, spouse, etc.) | Query on behalf of the Member  |
| Advisor / Chapter Representative  | Responsible for invitations and chapter set-up; queries on behalf of members  |
| Member Support Manager / Community Team Member  | Reviews new cases, classifies issue type, replies using approved templates, resolves or escalates. Monitors backlog, reassigns cases, ensures adherence, approves exceptions, and manages escalations. |
| Specialist Team Member | Handles escalated-specific issues after routing. |
| IT/engineering | Resolves confirmed technical defects, integration failures, and system-level issues. Maintains templates, tags, routing rules, inbox settings, user permissions, and reporting. |

**Guiding Rules & Principles** 

* One member issue should map to one case whenever possible, even if messages arrive through multiple channels.

* The system must support a 24-business-hour first-response timeframe because that is the current expectation in the SOP - **unless we want to adapt to a 48-hour rule?**  

* Forwarding should transfer ownership without requiring broad email 'CC chains for normal cases, matching the current operating principle.

* Bigger or more complex issues must allow triage, additional visibility, and SOP updates when patterns emerge.

* The Tier 1 and Tier 2 triage framework  - **what should that be?**  Keep the current Tier 1 for non-members and pre-payment inquiries, Tier 2 for active members, portal, certification, order, and support issues?  **Or Triage is defined by problem-type?**


**Service Design**

**Intake Architecture**

The system should create a **single front door** for support for **BOTH systems.** All member-facing support emails should ultimately route to one canonical support address (**membership@)**, and all Dashboard/platform inquiries should create or append to cases in the **Community Messaging Admin** queue.

Recommended model:

* Primary support address: one canonical inbox for all member support *(membership@).*

* Legacy aliases: existing inboxes remain as forwarding aliases during transition.

* Dashboard connector: all dashboard messages, channel questions, event questions, and direct messages create cases through an API or integration layer (*Community Messaging Admin)*.

* **Question:  Is this possible?  Unified queue:** all cases live in one case management layer regardless of origin.

* Reply adapter: replies are sent back through the originating channel when possible, or by email if the original channel cannot receive responses.

**Canonical Case Structure**

Each case might contain: **(IT can determine yes/no to this list)** 

* Case ID.

* Member identifiers: email, school name, full name, member status.

* Source channel: email, dashboard message, event chat, DM, channel post, internal handoff.

* Tier: Tier 1 or Tier 2.

* Category and subcategory.

* Priority.

* Assigned owner/team

* Status.

* Timestamps: created at, first response due, first response sent, resolved at.

* Conversation timeline across all linked channels.

* Internal notes and escalation log.

* Macro/template used.

* Attachments and screenshots.

**Functional Requirements for ONE Unified System**

**FR1. Unified intake**

* The platform must ingest messages from the primary email inbox and the dashboard/platform messaging system into one case queue. **Or into each?**  

* The platform must support forwarding from legacy inboxes without losing sender, timestamp, or thread context.

* The platform must deduplicate messages when the same member contacts support through multiple channels about the same issue.

**FR2. Identity resolution**

* The system must attempt to match incoming requests to an existing member/member profile using email address, dashboard ID, order/payment identifiers, and member account data.

* If identity confidence is low, the system must flag the case for manual review.

* If a member says they paid but no account appears, the workflow must support payment verification and, if confirmed, manual account creation, consistent with the current SOP.

**FR3. Triage and classification**

* The system must classify every case into Tier 1 or Tier 2.

* The system must support categories such as: about membership, benefits, fee/payment, invitation code, nomination/university affiliation, deadline extension, refund/account not found, unsubscribe, password reset, account not found, manual account creation, technical issue, international shipping, grad cords, major/career-fit question, accreditation/credit transfer, LinkedIn recommendation, advisor/chapter issue, community issue (career advice, life advice, professional advice), and others.

* The system should automatically recommend categories based on message content, with manual overrides by support staff.

**FR4. Routing and ownership**

* The system must assign a primary owner and/or team for each case.

* Routing rules must support automatic assignment by tier, category, member status, and channel.

* The system must allow reassignment without losing history.

* The system must support watcher/follower status for visibility without making followers responsible for response.

**FR5. In-channel response**

* Agents must be able to respond directly from the case record back to email or dashboard.

* The member should receive the reply in the same channel they used, unless policy or technical limitations require an email fallback.

* If a member contacts support in a public or semi-public channel, the system should support moving the case to a private thread or direct support conversation.

**FR6. Macros and templates**

* The system must store reusable macros/templates tied to the existing SOP scenarios, including the current Tier 1 and Tier 2 examples.

* Macros must support placeholders such as first name, invitation code, confirmed email, temporary password, case number, and links.

* The system must track which macro was used on each case.

**FR7. SLA and queue management**

* The system must measure the 24-hour **(or 48-hour)** first-response for all new cases.

* The system must show queue aging, overdue cases, unassigned cases, awaiting-member cases, and escalated cases.

* The system should support business-hours calendars and pause rules for waiting-on-member status.

**FR8. Escalation**

* The system must support escalation to IT for confirmed portal technical issues, backend errors, or system malfunctions, with follow-up expected within 24–48 hours as described in the SOP.

* The system must support escalation to finance/operations for refund and charge-verification issues.

* The system must support escalation to community/advisor/program teams when the issue owner is outside frontline support

**FR9. Audit trail (V2?)**

* The system must preserve full message history, routing actions, assignments, status changes, internal notes, and outbound responses.

* The system must record who responded, when, through which channel, and with which template.

**FR10. Reporting (V2?)**

* The system must provide dashboards for inbound volume by channel, category, tier, and owner.

* The system must provide attainment, resolution times, backlog trends, reopen rates, escalation rates, and duplicate-case rates.

* The system should support identifying FAQ candidates and SOP gaps based on repeated issue types.

**Data Model**

**Core objects**

| Object | Required fields |
| ----- | ----- |
| Contact | Contact ID, name, primary email, school name, status |
| Case | Case ID, subject, description, source, tier, category, priority, status, owner, team, created/resolved timestamps |
| Message | Message ID, case ID, direction, channel, sender, body, attachments, timestamp |
| Support record | Case ID, type, due timestamp, completed timestamp, breached flag |
| Escalation | Case ID, escalation type, target owner, reason, created timestamp, resolved timestamp |
| Macro | Macro ID, name, tier, category, content, placeholders, active flag |
| Tag | Tag ID, label, automation rules |

**Suggested statuses**

* New
* Triaged
* Waiting on Support
* Waiting on Member
* Escalated
* Resolved
* Closed
* Reopened

**Suggested priorities**

* **P1 Critical:** platform outage, widespread login failure, payment system failure.
* **P2 High:** Member cannot access paid benefits, urgent event-blocking issue, confirmed technical defect.
* **P3 Normal:** standard member or prospect questions.
* **P4 Low:** informational requests, feedback, non-urgent follow-up.

**Routing Rules**

**Primary routing logic**

| Condition | Route to | Notes |
| ----- | ----- | ----- |
| Non-member / pre-payment inquiry | Membership / frontline queue | Matches existing Tier 1 ownership pattern. |
| Invitation, nomination, fee, benefits | Membership / frontline queue | Use Tier 1 templates. |
| Refund or payment verification | Membership + finance/ops review | Membership currently manages refunds. |
| Active member account access | Member support queue | Use Tier 2 account workflows. |
| Confirmed technical issue | IT escalation queue | Follow 24–48 hour update expectation. |
| Advisor / chapter issue | Advisor-specialist queue | Current support inbox ownership indicates advisor/chapter routing |
| Community / post-join engagement issue | Community queue | Current SOP assigns post-join support to community with redirects as needed. |
| Accreditation / credit transfer question | Specialized macro + member support | Use controlled approved response. |
| Recommendation or Transcript request | Community then Membership | Mirrors documented handoff. |

**Fallback routing**

If the system cannot confidently classify a request, it should send the case to the frontline triage queue for manual review within the window.

**Workflow Designs**

**Workflow 1: New inbound case**

1. Member submits a request by email or Dashboard.
2. Integration layer creates or updates a case.
3. Identity resolution checks for existing contact/member match.
4. System assigns tier, category, and priority.
5. System routes to default owner/team.
6. Agent reviews suggested macro and responds in-channel.
7. Case moves to Waiting on member or Resolved.

**Workflow 2: Email consolidation**

1. Member emails any legacy support address.
2. Legacy address auto-forwards to the canonical support inbox.
3. Case is created in the unified queue with original recipient preserved as metadata.
4. Auto-reply confirms receipt and case number.
5. Agent handles the case in the unified workspace.
6. Reporting tracks the original inbound alias to measure transition progress.

**Workflow 3: Dashboard message handling**

1. Member asks a question in dashboard messaging, event chat, channel thread, or DM.
2. Integration creates a case and labels the source channel.
3. If message is public/semi-public, agent can convert or continue in a private support thread.
4. Agent responds from the case record back to the dashboard channel.
5. All follow-ups sync to the same case timeline.

**Workflow 4: Duplicate-channel merge**

1. Member submits the same issue by dashboard and email.
2. System attempts duplicate detection using contact, time window, subject similarity, and category.
3. Agent is prompted to merge or link the cases.
4. One case remains the source of truth, with all messages preserved.
5. Member receives one consolidated response path.

**Workflow 5: Tier 1 prospect question**

1. Case identified as non-Member/prospect.
2. System suggests one of the Tier 1 macros: About SCLA, Benefits, Fee, Payment Options, Invitation Code, Nomination/Affiliation, Deadline Extension, Refund/Account Not Found, or Unsubscribe.
3. Agent confirms classification and sends the approved response.
4. Case is resolved unless additional follow-up occurs.

**Workflow 6: Tier 2 Member account access**

1. Case identified as active Member and login/account issue.
2. If account exists, agent triggers password reset workflow and sends access instructions.
3. If account is not found, agent requests payment proof, verifies payment, and creates an account manually if confirmed.
4. If issue persists, agent requests a screenshot and escalates to IT if needed.
5. Case remains escalated until update or resolution is posted.

**Workflow 7: Technical escalation**

1. Agent identifies confirmed portal technical issue, backend error, or malfunction.
2. Agent adds reproduction details, screenshots, and impact notes.
3. Case status changes to Escalated and routes to IT.
4. Member receives escalation acknowledgment.
5. IT updates the case; support communicates resolution back to the Member.

**Workflow 8: Refund / payment investigation**

1. Member reports charge, dispute, or missing account after payment.
2. Agent requests screenshot or proof of charge if not already attached.
3. Finance/ops verifies payment source, following the current account-not-found process.
4. If payment is confirmed and account missing, create account or process refund per policy.
5. Case is resolved with confirmation to the Member.

**Workflow 9: Public-channel to private support**

1. Member posts a support question in a public channel or live event context.
2. Moderator/support agent acknowledges receipt publicly with a short redirection message.
3. System opens or links a private support case.
4. Agent continues support privately to protect account and payment information.
5. Public thread is marked as redirected.

**Recommended Macro Library**

**Tier 1 macros**

* About organization inquiry.
* Membership benefits inquiry.
* Membership fee questions.
* Payment options / financial concerns
* Invitation code request.
* Nomination / university affiliation questions
* Deadline extension.
* Refund request (account not found)
* Unsubscribe / stop emails.

**Tier 2 macros**

* Account found - password reset.
* Account not found.
* Manual account creation.
* Password reset issue persisting.
* IT escalation acknowledgment.
* International shipping.
* Free grad cords.
* Major / career-fit response, including major-specific variants.
* Accreditation / transfer-credit response.
* Letter of Recommendation or Transcript handoff.

**Macro governance**

* Every macro should have an owner.
* Every macro should have a last-reviewed date.
* Sensitive claims such as accreditation or credit transfer should be approval-controlled and editable only by designated admins because the SOP contains highly specific institutional language.

**Automation Rules**

* Auto-acknowledge new inbound cases with expected response time and case number.
* Auto-assign tier based on member status if known.
* Auto-suggest macros based on category classification.
* Auto-escalate overdue unassigned cases to the queue manager.
* Auto-remind owners before SLA breach.
* Auto-close resolved cases after a configurable inactivity period, with reopen support.
* Auto-tag recurring issues for SOP review when a threshold is exceeded.

**Non-Functional Requirements**

* Reliability: inbound message capture should be fault-tolerant with retry logic.
* Security: protect member PII, payment evidence, and account information with role-based permissions.
* Compliance: maintain audit logs for support actions and access.
* Performance: new messages should appear in the queue within 1 minute of receipt.
* Usability: frontline agents should be able to classify and reply in fewer than 3 clicks for common cases.
* Maintainability: templates, routing rules, and tags should be editable by operations staff without engineering support.

**Integrations**

**Required**

* Primary email system.
* Dashboard/platform messaging system.
* Member database (dashboard)
* Payment systems / Shop Sales 
* Internal escalation channel for IT and specialist handoff.

**Nice to have**

* Knowledge base integration (currently in Notion - Member Support SOP Library).
* Analytics warehouse or BI dashboard.
* Slack integration / notifications for escalations

**Permissions**

| Role | View cases | Reply | Reassign | Edit macros | Manage routing | View payment evidence |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| Queue manager & frontline manager | Yes | Yes | Yes | Yes | Yes | Yes |
| Team Specialist | Assigned / shared | Yes | Limited | No | No | As needed |
| IT | Escalated technical only | Internal or limited external | No | No | No | No |
| Admin / ops | Yes | Optional | Yes | Yes | Yes | Yes |

**Success Metrics**

* 95%+ of inbound member support requests create a case in the unified queue.
* 90%+ first responses within 24 business hours.
* Reduction in duplicate cases created across email and dashboard.
* Reduction in average reassignment count per case.
* Increase in template usage for standard issues.
* Clear reporting by tier, channel, and category.

**Implementation Phases**

**Phase 1: Foundation**

* Define canonical inbox.
* Keep legacy inboxes as forwarding aliases.
* Build unified case schema.
* Import macro library from current SOP.
* Stand up basic dashboard-message ingestion.

**Phase 2: Routing** 

* Add member identity resolution.
* Add auto-classification, routing rules, and timers.
* Add queue views and manager dashboards.
* Add IT escalation workflow.

**Phase 3: Optimization**

* Add duplicate detection and merge support.
* Add advanced reporting and taxonomy refinement.
* Add SOP-gap reporting and FAQ insights.
* Add public-to-private conversion workflows for community channels and live events.

**Open Questions for IT and Ops**

* What should the single canonical member-facing support email address be?
* Which existing inboxes remain externally visible during transition, and for how long?
* Should public channel questions always be moved to private support, or only when account/payment information is involved?
* Which system becomes the system of record for case ownership: help desk, CRM, or dashboard support module?
* What fields are available from the dashboard messaging API for identity matching and threading?
* Should community, advisor, and university-relations cases live in the same unified queue or in segmented team queues with shared reporting?
* Which templates need legal or leadership approval before being exposed as macros?

**Acceptance Criteria**

* A member can contact support by either email or dashboard and the issue appears in one shared queue.
* An agent can see complete case history, owner, status, and prior messages in one screen.
* An agent can reply back through the originating channel from the same case record.
* The system supports Tier 1 and Tier 2 triage and macro suggestions aligned to the existing SOP
* Technical issues can be escalated to IT with screenshots and tracked follow-up.
* Reporting shows case volume, response SLA, backlog, and escalation data by channel and category.

**Recommended Next-Step Build Order**

1. Stand up the canonical support inbox and forward all legacy inboxes into it.
2. Define the case schema, taxonomy, statuses, priorities, and rules.
3. Connect dashboard messaging to the same case object.
4. Load the Tier 1 and Tier 2 macro library from the current SOP.
5. Implement routing, assignment, and IT escalation.
6. Add duplicate detection, analytics, and optimization layers.
