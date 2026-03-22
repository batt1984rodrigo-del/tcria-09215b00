# TCRIA

**TCRIA** is a governance-oriented system for legal evidence processing.

It is designed to help organize heterogeneous legal materials, preserve documentary traceability, and generate auditable bundles without turning the system into an automatic accusation engine. The core objective is to keep evidence processing structured while leaving legal judgment and narrative responsibility with the human operator.

---

## Executive summary

TCRIA helps teams and operators:

- ingest mixed legal document collections;
- classify documentary artifacts;
- record traceability and governance signals;
- block or warn on risky accusatory content;
- generate auditable outputs in JSON, Markdown, and PDF.

The project is intentionally focused on **organization, chain of custody, and governance discipline**.

---

## What the system does

TCRIA treats document processing as a **custody workflow**:

1. document ingestion;
2. classification;
3. traceability signals;
4. governance gates;
5. audit bundle generation.

This makes the system useful for:

- legal audits;
- investigation support;
- evidence organization;
- documentary review workflows;
- controlled preparation of governed case materials.

---

## Governance boundaries

TCRIA is built around a simple rule: **automation can organize and audit evidence, but accountability for accusatory narrative promotion must remain human-declared**.

The system therefore applies governance checks such as:

- **prescriptiveGate** — blocks condemnatory or prescriptive language;
- **complianceGate** — requires explicit human accountability metadata in strict mode;
- **traceabilityCheck** — looks for dates, references, markers, and evidence signals.

### Decision record example

```text
[TCR-IA DECISION RECORD]
responsibleHuman: Rodrigo Baptista da Silva
declaredPurpose: Auditoria documental e organização de evidências para fins jurídicos
approved: YES
approvedAt: 2026-03-05
[/TCR-IA DECISION RECORD]
```

---

## What TCRIA does not do

TCRIA intentionally does **not**:

- generate legal pleadings;
- write accusations automatically;
- construct legal theses autonomously;
- replace human legal judgment.

---

## Repository structure

The repository is organized so that code, operational scripts, documentation, and example artifacts are visually separated.

```text
.
├── tcria/                  # Core package: engine, models, CLI support, settings
├── api/                    # FastAPI application
├── app/                    # Streamlit entrypoints / app layer
├── scripts/                # Script-oriented utilities and legacy helpers
├── docs/                   # Architecture and domain documentation
│   └── project-snapshots/  # Saved project structure snapshots and diffs
├── examples/
│   ├── audit-artifacts/    # Versioned sample outputs and reports
│   └── demo_case_documents/# Example input materials
├── tests/                  # Automated tests
├── run_governance_pipeline.py
├── app.py
└── pyproject.toml
```

### Folder conventions

- **`tcria/`**: reusable product logic.
- **`api/`**: HTTP entrypoints and request/response orchestration.
- **`app/`**: UI/app runtime layer.
- **`scripts/`**: operational scripts and support generators.
- **`docs/`**: conceptual documentation and project snapshots.
- **`examples/`**: curated example inputs and sample generated artifacts.

---

## Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

---

## CLI usage

### Basic scan

```bash
tcria scan ~/Downloads --strict
```

### Modular product audit

```bash
tcria product-audit ~/Downloads --strict --out-dir output/audit --output-stem audit
```

### Official pipeline mode

```bash
tcria product-audit ~/Downloads --strict --official-pipeline --output-stem my_case
```

### Direct pipeline command

```bash
python3 run_governance_pipeline.py --path ~/Downloads --strict --output-stem my_case
python3 run_governance_pipeline.py --path ~/Downloads --strict --legacy-audit-script --output-stem my_case
```

### Case workspace flow

```bash
tcria case init complice
tcria case run complice --strict
tcria investigate complice
```

---

## API

Run the API locally:

```bash
uvicorn api.api:app --reload
```

Main endpoints:

- `GET /health`
- `GET /capabilities`
- `POST /audit`
- `POST /audit/official-pipeline`
- `GET /responses/audit-types`
- `POST /responses/audit`
- `POST /audit/openai-summary`
- `POST /cases/init`
- `POST /cases/run`
- `POST /cases/investigate`
- `POST /investigations/full-run`
- `POST /conclusions/from-bundle`

---

## Architecture note

The architecture overview in `docs/architecture-overview.md` is kept as the project's current high-level representation. Operational implementation remains package- and script-oriented, and the repository structure is organized to support that working style cleanly.

---

## Sample artifacts and snapshots

To keep the repository root clean and professional:

- curated generated sample outputs are stored in `examples/audit-artifacts/`;
- project-structure snapshots and diffs are stored in `docs/project-snapshots/`;
- runtime outputs can continue to be generated in local working directories such as `output/` or case folders.

---

## Current professionalization goals

This repository now prioritizes:

- consistent structure;
- executive README presentation;
- visual separation between code, scripts, docs, and artifacts;
- predictable folder naming;
- less noise in the repository root.
