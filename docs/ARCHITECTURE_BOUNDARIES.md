# TCRIA Architecture Boundaries

This document defines the operational boundary between the governed TCRIA core and external integration layers such as CLI, API, MCP, web UI, automation, and deployment tooling.

The purpose of this boundary is to prevent integration work from contaminating the governed decision pipeline.

## 1. Architectural principle

TCRIA is a governed decision-support system.

Its value depends on preserving a clean, auditable, and traceable decision environment before any downstream decision layer consumes the output.

Therefore, integrations must not alter the meaning, sequence, or auditability of the core pipeline.

## 2. Core layer

The core layer is responsible for the governed audit flow.

Core responsibilities include:

- input inspection;
- evidence organization;
- official audit execution;
- prescriptive and compliance gates;
- blocked artifact review;
- traceable output generation;
- audit artifacts in JSON, Markdown, PDF, CSV, or equivalent structured formats;
- preservation of human responsibility and audit trail.

Examples of core areas include, but are not limited to:

- `tcria/engine.py`;
- audit report generation;
- gate logic;
- artifact writing;
- official pipeline execution;
- deterministic governance outputs.

## 3. Adapter layer

Adapters are external access or orchestration layers.

Adapters may call the core, but they must not redefine the core.

Adapter examples include:

- CLI commands;
- FastAPI endpoints;
- MCP tools;
- web interfaces;
- Azure deployment files;
- GitHub Actions workflows;
- scripts that wrap or orchestrate official outputs.

Adapters must be treated as replaceable access layers.

The system must remain understandable and testable even if an adapter is removed.

## 4. Non-extraction rule

Core logic must not be pulled, copied, duplicated, or reimplemented inside adapter layers.

Adapters must not contain their own versions of:

- gate logic;
- audit classification logic;
- official outcome rules;
- artifact eligibility rules;
- blocked-document promotion rules;
- decision-readiness rules;
- compliance or prescriptive filtering logic.

Adapters may only call documented core entry points.

If an adapter needs behavior that does not yet exist, the correct path is:

```text
request documented core contract
↓
review governance impact
↓
add or expose minimal core entry point
↓
adapter calls that entry point
```

The incorrect path is:

```text
copy core logic into API/MCP/CLI
↓
modify it locally
↓
produce unofficial decision behavior
```

This rule exists to prevent divergent governance behavior between the official pipeline and external access layers.

## 5. Mandatory rules for adapters

Adapters must follow these rules:

1. Do not modify core logic unless the change is explicitly classified as a core correction.
2. Do not copy, fork, or duplicate core logic into adapter code.
3. Do not introduce external AI calls into the official core pipeline without a separate governance review.
4. Do not change official audit outcomes.
5. Do not promote blocked or diagnostic material into official output without human review.
6. Do not bypass compliance, prescriptive, or traceability gates.
7. Do not write examples, curl commands, or integration snippets inside executable Python modules unless they are valid comments or tests.
8. Do not create new runtime contracts without documenting them.
9. Do not allow MCP, API, CLI, or web layers to become the source of truth for governance rules.
10. Do not make adapter convenience more important than auditability.

## 6. Contract discipline

Any adapter that calls a core function or script must respect an explicit contract.

A contract must define:

- input parameters;
- required and optional flags;
- output files;
- output location;
- error behavior;
- whether the operation changes official outcomes;
- whether human review is required.

If a caller passes an argument that the target does not accept, the adapter is wrong unless the target contract is intentionally updated.

Example failure mode:

```text
CLI calls PDF script with --title, but the script does not accept --title.
```

Corrective rule:

```text
Either update the target script contract minimally or remove the unsupported adapter argument.
Do not refactor unrelated layers.
```

## 7. MCP boundary

MCP is an adapter layer.

MCP may expose controlled tools, routes, or workflows, but it must not become a hidden decision layer.

MCP integrations must:

- call documented core contracts;
- preserve audit trails;
- return traceable artifacts;
- avoid undocumented side effects;
- avoid changing official outcomes;
- keep examples and test calls outside executable core files.

MCP must not:

- silently rewrite core logic;
- pull core logic into MCP tool handlers;
- duplicate official gate behavior;
- inject third-party model decisions into official audit output;
- bypass gates;
- create undocumented execution paths;
- mix demo commands with production code.

## 8. Pull request policy

Changes must be separated by layer.

Recommended PR categories:

- `fix/core`: correction inside governed pipeline;
- `fix/adapter`: correction in CLI, API, MCP, UI, or deployment wrapper;
- `docs/governance`: architecture, boundaries, rules, or contracts;
- `test/regression`: tests proving a previously broken flow now works.

A PR should not mix core logic changes with MCP/API/UI/deployment changes unless there is an explicit reason.

Any PR that moves logic from `tcria/` into API, MCP, CLI, web, or deployment code must be treated as a governance-risk PR and reviewed before merge.

## 9. Minimal correction policy

When fixing defects:

1. Identify the broken contract.
2. List the affected files before editing.
3. Apply the smallest possible change.
4. Avoid unrelated formatting or refactoring.
5. Run the narrowest relevant validation.
6. Document the evidence in the PR.

## 10. Human governance

TCRIA does not replace the responsible human decision-maker.

The system prepares, audits, blocks, organizes, and documents the decision environment.

Final institutional responsibility remains human.

This principle applies equally to the software architecture: automation may assist, but must not silently alter the governed decision core.
