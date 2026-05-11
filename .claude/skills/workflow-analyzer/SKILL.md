---
name: workflow-analyzer
description: Detect repeated process patterns in artifacts (Slack exports, tickets, meeting notes) and classify them for automation. Use when workflow-mapper needs pattern detection.
---

# workflow-analyzer

Pattern-detector used by the `workflow-mapper` agent.

## What it produces

A scratch report (stdout, not persisted) listing detected patterns:

```yaml
patterns:
  - name: "customer request intake"
    occurrences: 14
    tools_touched: ["Slack", "Linear", "Figma"]
    handoffs: 3         # how many people touch it on average
    avg_cycle_time_hours: 72
    evidence:
      - "scla/_raw/artifacts/slack-general-2026-04.md:L1240"
      - "scla/_raw/artifacts/linear-export-2026-04.csv:R78"
    automation_classification:
      - type: "integration"            # copy-paste between tools
        signal: "message-template copied from Slack to Linear description 11/14 times"
      - type: "deterministic-rule"     # decision dressed up as judgement
        signal: "tickets always routed to same engineer based on keyword in title"
    pain_quotes:
      - '"This always gets lost in Slack, had to chase down 3 people" — @pm 2026-04-12'
```

## Heuristics

- **Integration candidate**: same text appearing across two different tool
  exports within a short window.
- **Rule candidate**: a human decision that correlates ≥90% with one
  observable feature (keyword, sender, time of day).
- **Context-loss candidate**: questions like "wait, what was decided?" or
  "can someone send me the context?" in threads.
- **Meeting replacement candidate**: meeting notes that are ≥80% status
  updates with no decisions.

## Process

1. Walk `scla/_raw/artifacts/`. Parse each file by type:
   - Slack exports (JSON or MD) → threaded messages
   - Ticket CSVs → rows
   - Meeting notes (MD) → sections
   - Loom transcripts → utterances
2. Build a timeline. Cluster events by shared entities (customer name,
   ticket ID, feature name).
3. For each cluster ≥3 occurrences, emit a pattern entry.
4. Tag each with automation classifications where the heuristics fire.

## Rules

- **Ground every pattern in evidence.** Provide file:line references.
- **Quote pain, don't summarize it.** The client's team needs to recognize
  their own words.
- **Don't write files** — let `workflow-mapper` compose the final output.
