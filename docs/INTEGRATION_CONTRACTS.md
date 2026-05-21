# TCRIA Governed Integration Contracts

This document defines how external layers may integrate with the TCRIA core without modifying, copying, or contaminating the governed decision pipeline.

## 1. Purpose

The integration model is based on one rule:

```text
Adapters call the core through documented contracts.
Adapters do not become the core.
```

This keeps MCP, API, CLI, web, Azure, and automation layers useful without allowing them to redefine audit logic, gate logic, or official outcomes.

## 2. Integration flow

Approved integration flow:

```text
adapter request
↓
contract validation
↓
core entry point
↓
governed artifacts
↓
regression evidence
```

Prohibited integration flow:

```text
adapter request
↓
copy core logic
↓
local adapter decision
↓
unofficial outcome
```

## 3. Adapter categories

| Adapter | Purpose | May call core? | May alter core? | May define governance rules? |
|---|---|---:|---:|---:|
| CLI | Local/manual execution | Yes | No | No |
| API | HTTP access | Yes | No | No |
| MCP | Tool orchestration | Yes | No | No |
| Web UI | Human interface | Yes, through API/contract | No | No |
| Azure/Deploy | Hosting/runtime | No direct governance role | No | No |
| GitHub Actions | Validation/CI | No direct governance role | No | No |

## 4. Core entry points

The following entry points are preferred for adapter calls.

### Official pipeline

Purpose: run the official governed audit pipeline.

Preferred caller:

```python
TCRIAEngine.run_official_pipeline(...)
```

Adapter responsibility:

- validate input path;
- call official pipeline;
- return artifact paths;
- not change official outcomes.

### Product audit

Purpose: run modular audit output for product/API use.

Preferred caller:

```python
TCRIAEngine.run_audit(...)
```

Adapter responsibility:

- validate path;
- pass strict/output parameters;
- return bundle and artifact metadata;
- not bypass gates.

### Case run

Purpose: execute layered case workflow.

Preferred caller:

```python
case_run(case_dir, strict, paths, top_k, output_stem)
```

Adapter responsibility:

- resolve and validate case directory;
- pass documented parameters;
- not duplicate case orchestration logic outside the case functions.

### Investigation report

Purpose: generate final investigation report from existing case artifacts.

Preferred caller:

```python
investigate(
    case_dir,
    audit=None,
    blocked=None,
    preparation=None,
    timeline=None,
)
```

Adapter responsibility:

- pass explicit optional arguments;
- let the core/CLI helper discover artifacts when arguments are `None`;
- not promote blocked materials without human re-audit.

## 5. Contract template

Every new integration must be documented using this template before or in the same PR that introduces it.

```md
## Contract: <name>

Adapter:
Core entry point:
Purpose:
Inputs:
Required parameters:
Optional parameters:
Outputs:
Artifacts produced:
Does it change official outcome? yes/no
Does it require human review? yes/no
Failure behavior:
Regression validation:
Governance notes:
```

## 6. MCP-specific contract

MCP tools must be thin orchestration wrappers.

MCP may:

- expose a documented operation;
- validate inputs;
- call CLI/API/core contract;
- return traceable artifact references;
- report failures transparently.

MCP must not:

- decide official outcomes;
- create hidden alternate audit logic;
- duplicate gate logic;
- inject external AI decisions into official output;
- write files into the core pipeline without a documented contract.

## 7. API-specific contract

API endpoints must map HTTP requests to documented core calls.

An API endpoint must document:

- request model;
- core function called;
- output returned;
- error behavior;
- whether artifacts are written;
- whether OpenAI or another external service is used.

If an endpoint depends on keys or environment variables, that dependency must remain outside the core.

## 8. Key and environment boundary

Keys are adapter/runtime concerns.

Examples:

- `OPENAI_API_KEY`;
- Azure credentials;
- deployment secrets;
- MCP connector credentials.

Keys must not be required for the official core pipeline unless explicitly approved by governance review.

If a key is missing, the adapter must fail transparently without modifying core behavior.

## 9. Release gate

Before any integration PR is merged, it should answer:

1. What core contract does this call?
2. Does it copy any logic from `tcria/`?
3. Does it change official outcomes?
4. Does it introduce an external AI decision into the official pipeline?
5. What artifact proves execution?
6. What test or command validates it?

If the answer to item 2, 3, or 4 is yes, the PR requires governance review before merge.

## 10. Summary rule

```text
Core decides according to governed rules.
Adapters request, transport, display, or deploy.
Adapters do not decide.
```