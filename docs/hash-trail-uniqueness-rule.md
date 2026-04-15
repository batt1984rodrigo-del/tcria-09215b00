# Hash-based trail uniqueness rule

This document complements the TCRIA core governance ruleset without changing the existing gate architecture.

---

## RULE GROUP 2: TRACEABILITY

### RULE_2.3 — TRAIL UNIQUENESS BY HASH

Every document or governed artifact admitted into the trail MUST have a canonical content hash.

The same canonical hash MUST NOT pass through the governed trail more than once.

If a previously registered hash is detected again:
- the element MUST be recognized as already known
- it MUST NOT be admitted as a new trail element
- it MUST preserve linkage to the original registered occurrence

IF violated:
- STATUS: DUPLICATE
- REASON: "Hash already registered in trail"

---

## EFFECT

This rule exists to:
- prevent duplicate custody admission
- avoid false novelty
- preserve a single auditable trail for the same artifact
- maintain clean origin and decision reconstruction

---

## SYSTEM BEHAVIOR

On ingestion or trail admission:
- compute canonical hash
- check whether the hash already exists in the governed trail
- if it exists, block new admission and link to the prior record
- if it does not exist, allow first admission and register it as canonical

---

## COMPATIBILITY NOTE

This rule is policy-aligned with the TCRIA core governance ruleset and strengthens traceability discipline.

It does not require changing the existing gate architecture.
