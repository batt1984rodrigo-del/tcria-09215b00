# TCRIA — CORE GOVERNANCE RULESET

## PURPOSE

Define the minimum structural conditions for any information, decision, or artifact to be considered valid within the system.

The system enforces:
- traceability
- contextual integrity
- human accountability

---

## CORE PRINCIPLE

No element may exist without:
- context
- origin
- connection

If any of these are missing:
- the element is considered invalid or risky

---

## RULE GROUP 1: EXISTENCE VALIDATION

### RULE_1.1 — PROJECT ANCHOR

Every entity MUST be linked to at least one PROJECT.

IF NOT:
- STATUS: INVALID
- REASON: "Orphan entity"

### RULE_1.2 — CONTEXT REQUIREMENT

Every entity MUST contain contextual reference.

Context includes:
- purpose
- scope
- conditions

IF missing:
- STATUS: INVALID
- REASON: "Missing context"

---

## RULE GROUP 2: TRACEABILITY

### RULE_2.1 — EVIDENCE LINK

Every assertion, reflection, or claim MUST be linked to at least one EVIDENCE.

IF NOT:
- STATUS: WEAK
- RISK: "Unverifiable claim"

### RULE_2.2 — BIDIRECTIONAL TRACE

Every link must be:
- forward traceable
- backward traceable

The system must allow:
- origin reconstruction
- decision reconstruction

---

## RULE GROUP 3: ACTION GOVERNANCE

### RULE_3.1 — ACTION ORIGIN

Every action MUST reference:
- a DOCUMENT
- a CONTEXT

IF NOT:
- STATUS: INVALID
- REASON: "Unanchored action"

### RULE_3.2 — ACTION RECORD

Every action MUST register:
- WHO executed it
- WHAT was done
- WHEN it occurred

---

## RULE GROUP 4: ACCOUNTABILITY

### RULE_4.1 — HUMAN RESPONSIBILITY

Every critical output MUST have:
- responsibleHuman
- declaredPurpose

IF missing:
- STATUS: BLOCKED
- REASON: "No human accountability"

---

## RULE GROUP 5: OUTPUT VALIDATION

### RULE_5.1 — OUTPUT TRACEABILITY

Every output MUST be traceable to:
- source documents
- evidence chain
- decision path

IF NOT:
- STATUS: INVALID
- REASON: "Untraceable output"

---

## SYSTEM BEHAVIOR

### ON INPUT

- validate structure
- check required links
- block incomplete entries

### ON PROCESSING

- maintain trace links
- preserve context
- prevent orphan creation

### ON OUTPUT

- attach traceability metadata
- enforce accountability fields
- generate audit-ready structure

---

## FAILURE CONDITIONS

An element is considered compromised if:

- it has no project
- it has no context
- it has no evidence when evidence is required
- it has no responsible human for critical outputs
- it cannot be traced back to origin

---

## RELATION TO TCRIA GOVERNANCE GATES

This core ruleset informs and strengthens the repository governance checks.

- `prescriptiveGate` prevents condemnatory or prescriptive promotion that would bypass accountable human review.
- `complianceGate` enforces the accountability requirements described in RULE_4.1.
- `traceabilityCheck` enforces the traceability and output-validation expectations described in RULE GROUP 2 and RULE GROUP 5.

This means the ruleset is not only conceptual. It also serves as the policy basis for validation and blocking behavior in governed workflows.

---

## SYSTEM OBJECTIVE

- eliminate disconnected information
- enforce structured knowledge
- guarantee decision traceability
- enable defensible outputs
