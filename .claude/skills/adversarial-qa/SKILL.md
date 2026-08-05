---
name: adversarial-qa
description: Run an explicit deep audit of one SCLA freeform video using deterministic evidence and the combined visual-review contract.
argument-hint: "<stem>"
disable-model-invocation: true
---

# Adversarial QA

This optional audit no longer routes to the retired template-lane timing,
layout, and presence agents. For one explicit stem:

1. Run the normal deterministic preflight and MP4 verification.
2. Give one reviewer `contracts/visual-review.md`, sampled frames, and the MP4.
3. If factual provenance is explicitly in scope, separately invoke `qa-facts`
   with the source and refined-script paths.
4. Return blocking defects separately from advisory taste findings.

Do not broaden scope, reinterpret gate output, or load historical logs as
instructions.
