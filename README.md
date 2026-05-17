# TCRIA

TCRIA is an experimental governance runtime for auditable AI-assisted evidence workflows.

It is built around one principle:

> AI does not promote authority without explicit governance.

The project is not a legal chatbot, a legal parser, or a summarizer. Its purpose is to control how sensitive evidence artifacts move through ingestion, audit, policy evaluation, promotion control, ledgering, telemetry, and human accountability checkpoints.

## What It Does

TCRIA helps operators:

- ingest legal or investigative document bundles;
- classify evidence and claim-bearing artifacts;
- apply governance gates before sensitive outputs are promoted;
- block promotion when accountability metadata is missing;
- emit audit artifacts, governance events, hash-chain ledger entries, telemetry, and artifact signatures.

## Runtime Center

The center of the system is `tcria/runtime/`:

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

The runtime records the full governance path:

```text
check started
ingestion recorded
official audit completed or explicitly skipped
complementary review completed
policies evaluated
promotion allowed or blocked
events, ledger, telemetry, signatures emitted
```

## Governance Rule

TCRIA separates artifact generation from authority promotion.

A document can be processed and reviewed, but it should not be promoted to stronger institutional authority if the official audit still contains blocked records.

Example outcome:

```json
{
  "official_outcome": "BLOCKED (complianceGate)",
  "required_actions": ["BLOCK_PROMOTION"],
  "escalation": "GOVERNANCE_OWNER"
}
```

## Institutional Demo

A compact demonstration case is included at:

[examples/institutional-demo-case](examples/institutional-demo-case)

It demonstrates the core behavior:

- 2 input documents;
- 1 supporting governed record;
- 1 sensitive ungoverned claim;
- `BLOCKED (complianceGate)`;
- policy action `BLOCK_PROMOTION`;
- escalation to `GOVERNANCE_OWNER`;
- verified governance ledger;
- runtime telemetry and artifact signatures.

Run it again:

```bash
python3 run_governance_pipeline.py \
  --repo-root . \
  --path examples/institutional-demo-case/input \
  --strict \
  --output-dir examples/institutional-demo-case/output \
  --output-stem institutional_demo
```

## Repository Structure

```text
tcria/                  reusable product package
tcria/runtime/          governance runtime core
tcria/audit/            audit bundle and report generation
tcria/governance/       gate-level evaluators
scripts/                operational helpers and legacy generators
docs/                   architecture and project documentation
examples/               demo cases and curated sample artifacts
tests/                  smoke and runtime tests
run_governance_pipeline.py
```

## Documentation

- [Architecture](docs/architecture.md)
- [Governance](GOVERNANCE.md)
- [Core Ruleset](GOVERNANCE_CORE_RULESET.md)
- [Version Manifest](VERSION_MANIFEST.md)
- [Technical Backlog](docs/technical-backlog.md)

## Install

```bash
git clone https://github.com/batt1984rodrigo-del/tcria-09215b00.git
cd tcria-09215b00
pip install -r requirements.txt
```

## Run

```bash
python3 run_governance_pipeline.py --path examples/institutional-demo-case/input --strict
```

## Safety Boundary

TCRIA does not autonomously determine guilt, liability, or legal responsibility.

It provides governance infrastructure for traceability, auditability, promotion control, and accountability. Human review remains mandatory.

## License

MIT License.
