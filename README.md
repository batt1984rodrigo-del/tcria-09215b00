# TCRIA — AI Governance for Legal Evidence

TCRIA is a governance-driven platform for legal evidence processing, chain-of-custody control, and auditable document workflows.

It enables organizations to structure, audit, and validate complex evidence collections while preserving human accountability over legal conclusions.

---

## Why TCRIA exists

Modern legal and investigative workflows face critical risks:

- fragmented and unstructured evidence sources  
- lack of traceability and auditability  
- uncontrolled AI-generated narratives  
- exposure to legal risk from automated accusations  

TCRIA solves this by introducing a **governed evidence pipeline** that enforces structure, traceability, and accountability.

---

## What TCRIA does

TCRIA transforms document processing into a controlled governance workflow:

- Evidence ingestion from heterogeneous sources  
- Artifact classification and organization  
- Traceability signal generation  
- Governance gates for risk control  
- Auditable output generation (JSON, Markdown, PDF)

---

## Governance-first architecture

TCRIA is built on a core principle:

> Automation can organize and audit evidence —  
> but accountability for interpretation must remain human.

The system enforces:

- **prescriptiveGate** — blocks accusatory or condemnatory language  
- **complianceGate** — requires explicit human responsibility  
- **traceabilityCheck** — validates references, dates, and evidence signals  

---

## Who TCRIA is for

- Legal teams and auditors  
- Compliance and investigation units  
- Public sector institutions  
- Forensic and documentary analysis teams  
- AI governance and risk teams  

---

## What makes TCRIA different

- Governance-first (not AI-first)  
- Designed to prevent misuse of automation  
- Built for auditability and accountability  
- Supports institutional and regulatory environments  
- Ready for integration into enterprise workflows  

---

## SaaS readiness

TCRIA is designed to operate as a service platform.

It can be deployed as:

- API-based SaaS (FastAPI backend)  
- Evidence audit engine  
- Investigation workflow system  
- Governance layer for AI-assisted processes  

Supported environments:

- Azure App Service  
- Containerized infrastructure (Docker)  
- Enterprise internal deployments  

---

## Quick start

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### CLI usage

```bash
tcria scan ~/Documents --strict
```

```bash
tcria product-audit ~/Documents --strict --output-stem audit
```

### Full pipeline

```bash
python3 run_governance_pipeline.py --path ~/Documents --strict --output-stem case_analysis
```

---

## API

Run locally:

```bash
uvicorn api.api:app --reload
```

Production:

```bash
gunicorn -k uvicorn.workers.UvicornWorker api.api:app --bind 0.0.0.0:8000
```

Main endpoints:

- `POST /audit`
- `POST /audit/official-pipeline`
- `POST /cases/run`
- `POST /investigations/full-run`
- `POST /conclusions/from-bundle`

---

## Use cases

- Legal audits and compliance reviews  
- Evidence organization for investigations  
- Controlled preparation of case materials  
- AI governance and risk mitigation  
- Institutional documentation pipelines  

---

## What TCRIA does NOT do

TCRIA intentionally does not:

- generate legal accusations  
- produce legal pleadings  
- create autonomous legal conclusions  
- replace human legal judgment  

This ensures safe and responsible use in regulated environments.

---

## Example decision record

```
[TCR-IA DECISION RECORD]
responsibleHuman: Rodrigo Baptista da Silva
declaredPurpose: Evidence audit and legal documentation structuring
approved: YES
approvedAt: 2026-03-05
[/TCR-IA DECISION RECORD]
```

---

## Architecture overview

- `tcria/` — core engine and governance logic  
- `api/` — FastAPI service layer  
- `app/` — application/UI layer  
- `scripts/` — operational tooling  
- `docs/` — architecture and documentation  
- `examples/` — sample inputs and outputs  

---

## Strategic positioning

TCRIA is not just a tool — it is a governance layer for AI-assisted legal workflows.

It is designed to support:

- institutional adoption  
- regulatory alignment  
- responsible AI usage in legal contexts  

---

## License

MIT License

---

## Contact / Deployment

For enterprise deployment, SaaS integration, or institutional adoption:

→ Deploy via Azure or internal infrastructure  
→ Integrate with existing legal workflows  
→ Extend via API and automation pipelines  

---

TCRIA — bringing structure, accountability, and governance to legal evidence systems.
