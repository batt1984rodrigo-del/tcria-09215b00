# TCRIA technical backlog

This document captures the next professionalization steps for the repository based on the current codebase structure and the product boundaries described in the README.

---

## Priority 1 — architecture and workflow consolidation

### 1. Extract workflow services from `tcria/cli.py`

Current state:
- the CLI resolves paths;
- initializes case workspaces;
- runs the official pipeline;
- invokes supporting scripts through subprocesses;
- copies generated artifacts into case folders;
- updates the case manifest.

Why this matters:
- orchestration logic is concentrated in a single command module;
- API endpoints currently reuse part of this workflow directly;
- this makes testing and future maintenance harder than necessary.

Target state:
- move reusable orchestration into service-oriented modules such as:
  - `tcria/workflows/case_workflow.py`
  - `tcria/workflows/audit_workflow.py`
  - `tcria/services/artifact_registry.py`
- leave `tcria/cli.py` as an interface layer only.

### 2. Decouple API from CLI helpers

Current state:
- the FastAPI layer imports `case_init`, `case_run`, `investigate`, and path helpers from the CLI module.

Why this matters:
- API behavior should depend on domain/workflow services, not on terminal-oriented code;
- clearer boundaries improve error handling, reuse, and testability.

Target state:
- introduce shared workflow functions used by both CLI and API;
- keep parsing/printing behavior exclusive to the CLI.

### 3. Replace stdout parsing where possible

Current state:
- some downstream outputs are parsed from labeled stdout lines after script execution.

Why this matters:
- stdout contracts are fragile;
- structured return payloads are easier to validate.

Target state:
- migrate helper scripts to importable Python modules or structured JSON outputs;
- use typed return objects whenever possible.

---

## Priority 2 — governance reliability and regression coverage

### 4. Add focused tests for governance gates

Needed coverage:
- `prescriptiveGate` blocks condemnatory or prescriptive language;
- `complianceGate` requires explicit human accountability metadata in strict mode;
- `traceabilityCheck` detects dates, references, markers, and documentary evidence signals;
- generated bundles preserve expected governance metadata.

### 5. Add end-to-end tests for the case workspace flow

Needed coverage:
- `tcria case init` creates the expected workspace structure;
- `tcria case run` creates manifest and latest outputs correctly;
- `tcria investigate` produces final report artifacts;
- API endpoints mirror expected workflow behavior.

### 6. Validate artifact schemas

Needed coverage:
- version the JSON bundle shape;
- validate official audit, blocked review, preparation summary, timeline, and investigation report payloads;
- protect release-to-release compatibility.

---

## Priority 3 — packaging and repository hygiene

### 7. Reorganize script-oriented modules

Current state:
- several operational modules still live at repository root level.

Target state:
- move them into package-oriented locations such as `tcria/pipelines/` or `tcria/scripts/`;
- keep root-level entrypoints minimal and intentional.

### 8. Split optional dependencies

Current state:
- API, Streamlit, and OpenAI dependencies are all part of the base installation.

Target state:
- consider extras such as:
  - `tcria[api]`
  - `tcria[app]`
  - `tcria[ai]`
  - `tcria[dev]`

### 9. Improve release hygiene

Suggested additions:
- changelog;
- migration notes for output schema changes;
- minimal reproducible demo case;
- compatibility notes between modular audit mode and official pipeline mode.

---

## Priority 4 — operational hardening

### 10. Strengthen API operational controls

Suggested additions:
- explicit authentication or trusted deployment assumptions;
- structured request logging;
- stronger audit trail per run;
- clearer separation between local-governance endpoints and OpenAI-assisted endpoints.

### 11. Establish capability levels

Suggested documentation labels:
- supported;
- experimental;
- internal/legacy;
- governance-local;
- OpenAI-assisted.

This helps operators understand what is production-ready and what still depends on controlled usage.

---

## What may exist in the other repository

If the first saved repository contains earlier work, look there for:

1. better architecture notes or diagrams that describe the real governance pipeline;
2. earlier tests for gates, strict mode, or bundle generation;
3. helper modules that separate workflow logic from CLI code;
4. JSON examples that can become fixtures for regression tests;
5. legacy documentation explaining the official pipeline versus modular audit mode;
6. utility code for investigation report generation that could be packaged more cleanly here.

---

## Recommended implementation order

1. document architecture accurately;
2. extract workflow services from CLI;
3. decouple API from CLI internals;
4. add governance regression tests;
5. add schema validation and release hygiene improvements.
