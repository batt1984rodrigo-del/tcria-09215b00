from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from fastapi.responses import StreamingResponse
from io import BytesIO
from generate_unified_governance_report_pdf import generate_governance_pdf
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from tcria.cli import case_init, case_run, investigate, load_manifest, resolve_case_dir
from tcria.conclusion_engine import build_conclusion_report, render_final_conclusions_md
from tcria.engine import TCRIAEngine
from tcria.institutional_output import render_institutional_markdown
from tcria.openai_responses import (
    list_available_institutional_chat_profiles,
    list_audit_prompt_presets,
    run_institutional_output_prompt,
    run_audit_prompt,
)
from tcria.settings import load_env


load_env()
app = FastAPI(title="TCRIA API", version="0.2.0")
engine = TCRIAEngine()


class AuditRequest(BaseModel):
    path: str = Field(..., description="File or folder path to audit.")
    strict: bool = True
    out_dir: str = "output/audit"
    output_stem: str = "audit"
    include_pdf: bool = True
    max_files: int = Field(2000, ge=1, le=20000)
    max_total_bytes: int = Field(250_000_000, ge=1024, le=2_000_000_000)


class OpenAIResponsesAuditRequest(AuditRequest):
    model: str = Field("gpt-4.1-mini", description="OpenAI model used to explain the audit bundle.")
    audit_type: str = Field(
        "general_governance",
        description="Prompt preset used to analyze the audit bundle through the OpenAI Responses API.",
    )
    max_items: int = Field(8, ge=1, le=50, description="How many example records to send to OpenAI.")
    user_context: str | None = Field(
        default=None,
        description="Optional instruction that overrides or complements the preset prompt.",
    )


class CaseInitRequest(BaseModel):
    case: str = Field(..., description="Case id or absolute/relative case directory.")
    root: str = Field("cases", description="Root directory for case ids.")


class CaseRunRequest(CaseInitRequest):
    strict: bool = True
    paths: list[str] = Field(default_factory=list, description="Optional input paths. Defaults to case input dir.")
    top_k: int = Field(10, ge=1, le=100)
    output_stem: str | None = None


class CaseInvestigateRequest(CaseInitRequest):
    audit: str | None = None
    blocked: str | None = None
    preparation: str | None = None
    timeline: str | None = None


class BundleConclusionRequest(BaseModel):
    bundle_json_path: str = Field(..., description="Path to an audit bundle JSON.")


class InstitutionalOutputRequest(BaseModel):
    audit_data: dict[str, Any] = Field(
        ...,
        description="Structured process audit data used to build an institutional dispatch-ready output.",
    )
    chat_profile: str = Field(
        "fazendario_institucional",
        description="Named chat profile used to define the institutional drafting behavior.",
    )
    model: str = Field("gpt-4.1-mini", description="OpenAI model used for institutional drafting.")
    user_context: str | None = Field(
        default=None,
        description="Optional extra instruction for the institutional drafting module.",
    )
    system_prompt_override: str | None = Field(
        default=None,
        description="Optional system-prompt override when you want to define the chat behavior explicitly.",
    )


class LegacyGatewayAuditRequest(BaseModel):
    path: str = Field(..., description="File or folder path to audit with the legacy accusation gateway.")
    strict: bool = True
    output_dir: str = "output/audit"
    output_stem: str | None = None
    discovery_root: str | None = None


class FullInvestigationRunRequest(CaseRunRequest):
    audit_type: str = Field(
        "civil_criminal_investigative",
        description="Responses API preset used when analyze_with_openai=true.",
    )
    model: str = Field("gpt-4.1-mini", description="OpenAI model used for the final Responses API analysis.")
    analyze_with_openai: bool = Field(
        False,
        description="When true, run a final Responses API analysis over the resulting audit bundle.",
    )
    user_context: str | None = Field(
        default=None,
        description="Optional instruction that overrides or complements the preset prompt.",
    )
    max_items: int = Field(8, ge=1, le=50, description="How many example records to send to OpenAI.")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _allowed_input_roots() -> list[Path]:
    raw = os.getenv("TCRIA_ALLOWED_INPUT_ROOTS", "").strip()
    if not raw:
        return [Path.cwd().resolve()]
    return [Path(part.strip()).expanduser().resolve() for part in raw.split(",") if part.strip()]


def _resolve_and_validate_input_path(path_value: str) -> Path:
    resolved = Path(path_value).expanduser().resolve()
    if not resolved.exists():
        raise HTTPException(status_code=400, detail=f"Input path does not exist: {resolved}")

    allowed_roots = _allowed_input_roots()
    if not any(_is_within(resolved, root) for root in allowed_roots):
        joined = ", ".join(str(root) for root in allowed_roots)
        raise HTTPException(
            status_code=403,
            detail=f"Input path is outside allowed roots. Allowed roots: {joined}",
        )
    return resolved


def _resolve_case_path(case_value: str, root: str) -> Path:
    resolved = resolve_case_dir(case_value, root)
    allowed_roots = _allowed_input_roots()
    if not any(_is_within(resolved, allowed_root) for allowed_root in allowed_roots):
        joined = ", ".join(str(root_path) for root_path in allowed_roots)
        raise HTTPException(
            status_code=403,
            detail=f"Case path is outside allowed roots. Allowed roots: {joined}",
        )
    return resolved


def _load_json(path_value: str | Path) -> dict[str, object]:
    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        raise HTTPException(status_code=400, detail=f"JSON path does not exist: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read JSON: {path}: {exc}") from exc


def _parse_labeled_line(text: str, label: str) -> str | None:
    match = re.search(rf"^{re.escape(label)}\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def _run_legacy_gateway_audit(payload: LegacyGatewayAuditRequest) -> dict[str, object]:
    script_path = (Path(__file__).resolve().parent.parent / "audit_accusation_bundle_with_tcr_gateway.py").resolve()
    cmd = [
        sys.executable,
        str(script_path),
        "--path",
        str(_resolve_and_validate_input_path(payload.path)),
        "--output-dir",
        payload.output_dir,
    ]
    if payload.strict:
        cmd.append("--strict")
    if payload.output_stem:
        cmd.extend(["--output-stem", payload.output_stem])
    if payload.discovery_root:
        cmd.extend(["--discovery-root", payload.discovery_root])

    cp = subprocess.run(cmd, cwd=str(Path(__file__).resolve().parent.parent), text=True, capture_output=True)
    if cp.returncode != 0:
        raise HTTPException(status_code=400, detail=cp.stderr or cp.stdout or "Legacy gateway audit failed.")

    json_report = _parse_labeled_line(cp.stdout, "JSON report:")
    markdown_report = _parse_labeled_line(cp.stdout, "Markdown report:")
    if not json_report or not markdown_report:
        raise HTTPException(status_code=400, detail="Could not parse legacy gateway output artifact paths.")

    payload_json = _load_json(json_report)
    return {
        "stdout": cp.stdout,
        "json_report": json_report,
        "markdown_report": markdown_report,
        "bundle": payload_json,
    }


def _load_case_outputs(case_dir: Path, manifest: dict[str, Any]) -> dict[str, object]:
    latest_outputs = manifest.get("latest_outputs", {})

    def read_latest_json(key: str) -> dict[str, object] | None:
        rel = latest_outputs.get(key)
        if not isinstance(rel, str):
            return None
        path = case_dir / rel
        if not path.exists():
            return None
        return _load_json(path)

    audit_bundle = read_latest_json("official_audit_json")
    blocked_review = read_latest_json("blocked_review_json")
    preparation = read_latest_json("case_preparation_json")
    timeline = read_latest_json("timeline_json")
    investigation_report = read_latest_json("investigation_report_json")

    conclusions = build_conclusion_report(audit_bundle) if isinstance(audit_bundle, dict) else None

    return {
        "latest_outputs": latest_outputs,
        "audit_bundle": audit_bundle,
        "blocked_review": blocked_review,
        "preparation": preparation,
        "timeline": timeline,
        "investigation_report": investigation_report,
        "gateway_conclusions": conclusions,
        "gateway_conclusions_markdown": render_final_conclusions_md(conclusions) if isinstance(conclusions, dict) else None,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/capabilities")
def capabilities() -> dict[str, object]:
    return {
        "api": [
            "audit",
            "official_pipeline",
            "responses_audit",
            "responses_institutional_profiles",
            "case_init",
            "case_run",
            "case_investigate",
            "bundle_conclusions",
            "responses_institutional_output",
            "legacy_gateway_audit",
        ]
    }


@app.get("/responses/audit-types")
def get_response_audit_types() -> dict[str, object]:
    return {"audit_types": list_audit_prompt_presets()}


@app.get("/responses/institutional-profiles")
def get_institutional_chat_profiles() -> dict[str, object]:
    return {"chat_profiles": list_available_institutional_chat_profiles()}


@app.post("/audit")
def run_audit(payload: AuditRequest) -> dict[str, object]:
    validated_path = _resolve_and_validate_input_path(payload.path)
    try:
        return engine.run_audit(
            input_path=str(validated_path),
            strict=payload.strict,
            out_dir=payload.out_dir,
            output_stem=payload.output_stem,
            include_pdf=payload.include_pdf,
            max_files=payload.max_files,
            max_total_bytes=payload.max_total_bytes,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/audit/official-pipeline")
def run_official_pipeline(payload: AuditRequest) -> dict[str, str]:
    validated_path = _resolve_and_validate_input_path(payload.path)
    try:
        return engine.run_official_pipeline(
            input_path=str(validated_path),
            strict=payload.strict,
            output_stem=payload.output_stem,
            max_files=payload.max_files,
            max_total_bytes=payload.max_total_bytes,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/responses/audit")
def run_responses_audit(payload: OpenAIResponsesAuditRequest) -> dict[str, object]:
    validated_path = _resolve_and_validate_input_path(payload.path)
    try:
        result = engine.run_audit(
            input_path=str(validated_path),
            strict=payload.strict,
            out_dir=payload.out_dir,
            output_stem=payload.output_stem,
            include_pdf=payload.include_pdf,
            max_files=payload.max_files,
            max_total_bytes=payload.max_total_bytes,
        )
        bundle = result.get("bundle")
        if not isinstance(bundle, dict):
            raise RuntimeError("Audit result did not contain a bundle.")
        responses_result = run_audit_prompt(
            bundle,
            audit_type=payload.audit_type,
            model=payload.model,
            user_context=payload.user_context,
            max_items=payload.max_items,
        )
        return {"audit": result, "responses_analysis": responses_result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/audit/openai-summary")
def run_audit_openai_summary(payload: OpenAIResponsesAuditRequest) -> dict[str, object]:
    return run_responses_audit(payload)


@app.post("/cases/init")
def api_case_init(payload: CaseInitRequest) -> dict[str, object]:
    case_dir = _resolve_case_path(payload.case, payload.root)
    try:
        case_init(case_dir)
        manifest = load_manifest(case_dir / "case_manifest.json")
        return {
            "case_dir": str(case_dir),
            "manifest_path": str(case_dir / "case_manifest.json"),
            "manifest": manifest,
        }
    except SystemExit as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/cases/run")
def api_case_run(payload: CaseRunRequest) -> dict[str, object]:
    case_dir = _resolve_case_path(payload.case, payload.root)
    try:
        case_run(
            case_dir,
            strict=payload.strict,
            paths=payload.paths,
            top_k=payload.top_k,
            output_stem=payload.output_stem,
        )
        manifest = load_manifest(case_dir / "case_manifest.json")
        return {
            "case_dir": str(case_dir),
            "manifest": manifest,
            "latest_outputs": manifest.get("latest_outputs", {}),
        }
    except SystemExit as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/cases/investigate")
def api_case_investigate(payload: CaseInvestigateRequest) -> dict[str, object]:
    case_dir = _resolve_case_path(payload.case, payload.root)
    try:
        investigate(
            case_dir,
            audit=payload.audit,
            blocked=payload.blocked,
            preparation=payload.preparation,
            timeline=payload.timeline,
        )
        manifest = load_manifest(case_dir / "case_manifest.json")
        latest_outputs = manifest.get("latest_outputs", {})
        report_json = latest_outputs.get("investigation_report_json")
        report = _load_json(case_dir / report_json) if isinstance(report_json, str) else None
        return {
            "case_dir": str(case_dir),
            "manifest": manifest,
            "investigation_report": report,
        }
    except SystemExit as exc:
           raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/conclusions/from-bundle")
def api_bundle_conclusions(payload: BundleConclusionRequest) -> dict[str, object]:
    bundle = _load_json(payload.bundle_json_path)
    conclusions = build_conclusion_report(bundle)
    return {
        "conclusions": conclusions,
        "markdown": render_final_conclusions_md(conclusions),
    }


@app.post("/responses/institutional-output")
def api_run_institutional_output(payload: InstitutionalOutputRequest) -> dict[str, object]:
    result = run_institutional_output_prompt(
        payload.audit_data,
        model=payload.model,
        user_context=payload.user_context,
        chat_profile=payload.chat_profile,
        system_prompt_override=payload.system_prompt_override,
    )
    output = result["institutional_output"]
    return {
        "institutional_output": output,
        "markdown": render_institutional_markdown(output),
        "response_metadata": result["response_metadata"],
    }


@app.post("/gateways/legacy-accusation-audit")
def api_legacy_gateway_audit(payload: LegacyGatewayAuditRequest) -> dict[str, object]:
    return _run_legacy_gateway_audit(payload)


@app.post("/investigations/full-run")
def api_full_investigation_run(payload: FullInvestigationRunRequest) -> dict[str, object]:
    case_dir = _resolve_case_path(payload.case, payload.root)
    manifest_path = case_dir / "case_manifest.json"

    try:
        if not manifest_path.exists():
            case_init(case_dir)

        case_run(
            case_dir,
            strict=payload.strict,
            paths=payload.paths,
            top_k=payload.top_k,
            output_stem=payload.output_stem,
        )
        investigate(
            case_dir,
            audit=None,
            blocked=None,
            preparation=None,
            timeline=None,
        )

        manifest = load_manifest(manifest_path)
        outputs = _load_case_outputs(case_dir, manifest)

        responses_analysis = None
        audit_bundle = outputs.get("audit_bundle")
        if payload.analyze_with_openai and isinstance(audit_bundle, dict):
            responses_analysis = run_audit_prompt(
                audit_bundle,
                audit_type=payload.audit_type,
                model=payload.model,
                max_items=payload.max_items,
                user_context=payload.user_context,
            )

        return {
            "case_dir": str(case_dir),
            "manifest": manifest,
            **outputs,
            "responses_analysis": responses_analysis,
        }
except Exception as exc:
    raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/audit/report/pdf")
def generate_audit_report_pdf(payload: dict):
    try:
        pdf_bytes = generate_governance_pdf(
            audit=payload.get("audit", {}),
            blocked=payload.get("blocked", {}),
        )

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=tcria-governance-report.pdf"
            },
        )

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
