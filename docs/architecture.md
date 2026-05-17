# TCRIA Architecture

TCRIA is organized around one operating principle:

> AI does not promote authority without explicit governance.

The project is therefore not just a document parser or legal summarizer. Its center is a governance runtime that supervises evidence processing, policy evaluation, promotion control, traceability, and auditability.

## Runtime Center

`tcria/runtime/` is the architectural center of the system.

```text
tcria/runtime/
  events.py       governance event model
  state.py        formal state machine
  policies.py     policy engine, registry, severity, actions, escalation
  ledger.py       immutable hash-chain audit ledger
  signatures.py   artifact signatures and content hashes
  telemetry.py    runtime observability
  runtime.py      central orchestrator
```

The runtime coordinates the governance lifecycle:

1. check starts;
2. ingestion is recorded;
3. official audit runs or is explicitly skipped;
4. complementary review runs;
5. policies are evaluated;
6. promotion is allowed or blocked;
7. events, ledger, telemetry, and artifact signatures are emitted.

## Pipeline Shape

```text
source files or existing audit JSON
        |
        v
run_governance_pipeline.py
        |
        v
tcria.runtime.GovernanceRuntime
        |
        +-- official audit artifacts
        +-- blocked review artifacts
        +-- policy evaluation
        +-- governance events
        +-- hash-chain ledger
        +-- telemetry
        +-- artifact signatures
```

`run_governance_pipeline.py` remains a root-level operational entrypoint. Supporting generators and legacy helpers live under `scripts/` so the repository root stays focused on package, docs, and primary entrypoints.

## Policy Engine

The policy engine is intentionally formal rather than ad hoc.

Current concepts:

- **registry**: named policy rules with stable IDs;
- **severity**: `INFO`, `WARN`, `HIGH`, `CRITICAL`;
- **actions**: `ALLOW`, `WARN`, `BLOCK_PROMOTION`, `REQUIRE_HUMAN_REVIEW`;
- **escalation**: `NONE`, `HUMAN_REVIEW`, `GOVERNANCE_OWNER`;
- **findings**: concrete rule outcomes tied to artifact subjects.

The engine reads real TCRIA audit bundles by checking `accusation_set` first, then legacy or generic containers such as `records`, `audit_records`, `documents`, and `items`.

This prevents false approval when blocked records are present inside the real audit JSON shape.

## Governance Events

Governance events use an explicit event model:

- event ID;
- schema version;
- event type;
- subject;
- actor;
- timestamp;
- structured payload.

These events are the raw material for runtime observability and the immutable ledger.

## Immutable Audit Chain

`GovernanceLedger` records each event in a hash chain:

```text
previous_hash + canonical_event -> entry_hash
```

The first entry starts from a genesis hash. Every subsequent entry points to the previous entry hash. The ledger can verify that the chain has not been mutated in place.

## Artifact Signatures

Generated artifacts are registered with SHA-256 signatures:

- official audit JSON;
- official audit Markdown;
- blocked review JSON;
- blocked review Markdown;
- runtime events JSON;
- runtime ledger JSON;
- runtime telemetry JSON.

This gives the runtime a concrete integrity layer for outputs, not only for events.

## Repository Organization

```text
tcria/                  reusable product package
tcria/runtime/          governance runtime core
tcria/audit/            audit bundle/report generation
tcria/governance/       gate-level evaluators
scripts/                operational helpers and legacy generators
docs/                   architecture and project documentation
tests/                  smoke and runtime tests
run_governance_pipeline.py
```

The intended direction is clear: reusable logic should move into `tcria/`, while script-shaped operational glue should stay in `scripts/`.

## Promotion Control

TCRIA treats promotion as a governed act.

An artifact may be generated, reviewed, and summarized, but it should not be promoted to stronger authority if the official audit still contains blocked records. This is the core distinction between ordinary automation and an executable governance runtime.
