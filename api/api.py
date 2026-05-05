from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from generate_unified_governance_report_pdf import generate_governance_pdf
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

# =========================
# INIT
# =========================

load_env()
app = FastAPI(title="TCRIA API", version="0.2.0")
engine = TCRIAEngine()

# =========================
# MODELS
# =========================

class AuditRequest(BaseModel):
    path: str
    strict: bool = True
    out_dir: str = "output/audit"
    output_stem: str = "audit"

class FullInvestigationRunRequest(BaseModel):
    case: str
    root: str = "cases"
    strict: bool = True
    paths: list[str] = []
    top_k: int = 10
    output_stem: str | None = None
    analyze_with_openai: bool = False
    audit_type: str = "general_governance"
    model: str = "gpt-4.1-mini"
    user_context: str | None = None
    max_items: int = 8

# =========================
# HELPERS
# =========================

def _resolve_and_validate_input_path(path_value: str) -> Path:
    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        raise HTTPException(400, f"Path not found: {path}")
    return path

def _resolve_case_path(case_value: str, root: str) -> Path:
    return resolve_case_dir(case_value, root)

# =========================
# HEALTH
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# AUDIT
# =========================

@app.post("/audit")
def run_audit(payload: AuditRequest):
    try:
        path = _resolve_and_validate_input_path(payload.path)
        return engine.run_audit(
            input_path=str(path),
            strict=payload.strict,
            out_dir=payload.out_dir,
            output_stem=payload.output_stem,
        )
    except Exception as exc:
        raise HTTPException(400, str(exc))

# =========================
# FULL INVESTIGATION
# =========================

@app.post("/investigations/full-run")
def full_run(payload: FullInvestigationRunRequest):
    try:
        case_dir = _resolve_case_path(payload.case, payload.root)

        case_init(case_dir)

        case_run(
            case_dir,
            strict=payload.strict,
            paths=payload.paths,
            top_k=payload.top_k,
            output_stem=payload.output_stem,
        )

        investigate(case_dir)

        manifest = load_manifest(case_dir / "case_manifest.json")

        return {
            "case_dir": str(case_dir),
            "manifest": manifest,
        }

    except Exception as exc:
        raise HTTPException(400, str(exc))

# =========================
# PDF REPORT
# =========================

@app.post("/audit/report/pdf")
def generate_pdf(payload: dict):
    try:
        pdf_bytes = generate_governance_pdf(
            audit=payload.get("audit", {}),
            blocked=payload.get("blocked", {}),
        )

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=tcria-report.pdf"
            },
        )

    except Exception as exc:
        raise HTTPException(400, str(exc))
