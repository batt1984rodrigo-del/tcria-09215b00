# Institutional Demo Case Summary

## Positioning

TCRIA is demonstrated here as a governance runtime for auditable AI-assisted evidence workflows.

The point of the demo is not to prove or disprove a legal claim. The point is to show that the system can prevent sensitive material from being promoted when governance conditions are not satisfied.

## Scenario

The input bundle contains two records:

1. A governed supporting record with explicit DecisionRecord metadata.
2. An ungoverned investigative claim that mentions a sensitive allegation without accountability metadata.

## Runtime Outcome

The runtime completed the audit and blocked promotion.

Key outputs:

- `total_files_scanned`: `2`
- `accusation_set_count`: `1`
- blocked artifact: `relatorio_ungoverned_claim.txt`
- official outcome: `BLOCKED (complianceGate)`
- policy escalation: `GOVERNANCE_OWNER`
- required action: `BLOCK_PROMOTION`
- ledger verified: `true`

## Why It Matters

This demonstrates the core TCRIA principle:

> AI does not promote authority without explicit governance.

The system still generates audit artifacts, review artifacts, telemetry, ledger entries, and signatures. But it does not treat artifact generation as institutional approval.

## Files To Inspect

- `output/institutional_demo_strict.json`
- `output/institutional_demo_strict_blocked_artifacts_review.json`
- `output/institutional_demo_strict_governance_events.json`
- `output/institutional_demo_strict_governance_ledger.json`
- `output/institutional_demo_strict_governance_telemetry.json`
- `output/institutional_demo_strict_artifact_signatures.json`
