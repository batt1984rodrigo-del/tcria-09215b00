# TCRIA — Legal Evidence Chain-of-Custody and Governance System

TCRIA is a **legal evidence chain-of-custody and governance system**.

It ingests heterogeneous collections of documents and produces an **auditable bundle** that records classification, traceability signals, governance gates, and accountability metadata.

Its role is **not to write legal pleadings or decide legal theses**.  
Instead, it preserves a controlled **documentary chain of custody** before human legal decision-making.

---

# Purpose

Legal cases often begin with **large collections of mixed documents**, such as:

- PDFs
- DOCX files
- notes
- reports
- emails
- drafts
- contextual material

Most tools only extract text or rank files.

TCRIA introduces a **governance layer** that ensures:

- accusatory narratives are not promoted without accountability
- documentary evidence remains traceable
- responsibility for narrative promotion is explicit
- heterogeneous archives can be processed without producing uncontrolled conclusions

The system therefore acts as a **custody and governance layer for legal documentation**.

---

# Why this exists

Most document analyzers simply extract text and rank files.

TCRIA adds **governance gates** so that accusatory content does not "pass" unless it carries explicit accountability metadata (`DecisionRecord`) and avoids prescriptive or condemnatory language.

This protects the **chain of custody of narrative responsibility**.

---

# Core concept: documentary chain of custody

TCRIA treats document processing as a **custody workflow**, not merely analysis.

The system records how documents move through the pipeline:

document ingestion
↓
classification
↓
traceability signals
↓
governance gates
↓
audit bundle 

This produces a **controlled evidentiary trail** before human interpretation.

---

# Features (MVP)

### Document ingestion

Scan folders of mixed files:

- PDF
- DOCX
- TXT
- MD

---

### Evidence classification

Artifacts are classified as:

- neutral / context
- supporting evidence
- relevant evidence
- accusatory candidates

---

### Governance gates

Three governance checks protect the custody chain:

**prescriptiveGate**

Blocks condemnatory or prescriptive language.

**complianceGate**

Requires explicit accountability metadata in strict mode.

**traceabilityCheck**

Looks for signals such as:

- dates
- references
- evidentiary markers
- currency indicators

---

### Audit bundle output

Each run produces:

- JSON audit bundle
- Markdown report
- PDF audit report

These outputs document how the system interpreted the collection.

Blocked artifacts are **not reprocessed by the engine**.

Instead they generate a **diagnostic report** analyzing potential evidentiary relevance without promoting them to the official accusation bundle.

---

# Accountability metadata

To promote accusatory content through the compliance gate, the document must include a **DecisionRecord** header.

Example:

```text
[TCR-IA DECISION RECORD]
responsibleHuman: Rodrigo Baptista da Silva
declaredPurpose: Auditoria documental e organização de evidências para fins jurídicos
approved: YES
approvedAt: 2026-03-05
[/TCR-IA DECISION RECORD]
```

This ensures that **responsibility for narrative promotion remains human-declared**.

---

# What TCRIA does NOT do

TCRIA intentionally does **not**:

- generate legal pleadings
- write accusations
- construct legal theses
- produce petitions automatically

Those activities require **human legal judgment and responsibility**.

TCRIA instead provides a **governed evidentiary foundation** that can later support human legal workflows.

---

# Installation

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

# CLI usage

Run from the repository root:

```bash
tcria scan ~/Downloads -o output/audit --strict
```

If your audit script is located elsewhere:

```bash
tcria scan ~/Downloads --script path/to/audit_accusation_bundle_with_tcr_gateway.py
```

# Web interface

A simple web interface is available via Streamlit:

```bash
streamlit run app.py
```

# Outputs

Each run produces an audit bundle:

```text
output/audit/
    audit.json
    audit.md
    audit_report.pdf
```

These artifacts document:

- classification results
- governance gate outcomes
- traceability signals
- compliance diagnostics
