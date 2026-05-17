# Runbook

Regenerate the institutional demo from the repository root:

```bash
rm -f examples/institutional-demo-case/output/*
python3 run_governance_pipeline.py \
  --repo-root . \
  --path examples/institutional-demo-case/input \
  --strict \
  --output-dir examples/institutional-demo-case/output \
  --output-stem institutional_demo
```

Expected console summary:

```text
Total scanned: 2
Accusation set: 1
Blocked artifacts: 1
```

Expected governance facts:

- final state history includes `BLOCKED`;
- policy evaluation has `blocked_count = 1`;
- policy escalation is `GOVERNANCE_OWNER`;
- required action includes `BLOCK_PROMOTION`;
- ledger verification is `true`;
- artifact signatures are emitted.
