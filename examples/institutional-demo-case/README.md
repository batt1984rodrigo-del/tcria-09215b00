# Institutional Demo Case

This case packages the TCRIA governance runtime as a small institutional demonstration.

It is designed to show one core behavior:

> A sensitive claim can be processed, but it cannot be promoted when governance metadata is missing.

## Inputs

```text
input/
  sample_decision_record.txt
  relatorio_ungoverned_claim.txt
```

- `sample_decision_record.txt` contains explicit DecisionRecord metadata and traceability markers.
- `relatorio_ungoverned_claim.txt` contains a sensitive investigative claim without DecisionRecord metadata.

## Result

The strict governance pipeline produced:

- total files scanned: `2`;
- accusation candidates: `1`;
- blocked artifacts: `1`;
- official blocked outcome: `BLOCKED (complianceGate)`;
- policy action: `BLOCK_PROMOTION`;
- escalation: `GOVERNANCE_OWNER`;
- final runtime state: `COMPLETED`, after `BLOCKED`;
- ledger verification: `true`.

## Output Package

```text
output/
  institutional_demo_strict.json
  institutional_demo_strict.md
  institutional_demo_strict_report.pdf
  institutional_demo_strict_blocked_artifacts_review.json
  institutional_demo_strict_blocked_artifacts_review.md
  institutional_demo_strict_governance_events.json
  institutional_demo_strict_governance_ledger.json
  institutional_demo_strict_governance_telemetry.json
  institutional_demo_strict_artifact_signatures.json
```

## Demo Command

```bash
python3 run_governance_pipeline.py \
  --repo-root . \
  --path examples/institutional-demo-case/input \
  --strict \
  --output-dir examples/institutional-demo-case/output \
  --output-stem institutional_demo
```

## Institutional Reading

This is not a demo of automatic legal conclusion generation.

It is a demo of governance enforcement:

- the runtime accepts the evidence bundle;
- the audit layer identifies the sensitive claim-bearing artifact;
- the compliance gate blocks promotion because explicit accountability metadata is missing;
- the policy engine records a critical finding;
- the ledger preserves the event sequence;
- telemetry and signatures make the run inspectable after the fact.
