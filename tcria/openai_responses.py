from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from tcria.institutional_profiles import get_institutional_chat_profile, list_institutional_chat_profiles
from tcria.institutional_output import INSTITUTIONAL_OUTPUT_SCHEMA, normalize_institutional_output
from tcria.settings import load_env


load_env()

DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"

SYSTEM_PROMPT = (
    "You are a TCRIA audit analyst. "
    "Summarize governance findings, accountability risks, documentary gaps, and operational next steps. "
    "Do not give legal advice or invent facts outside the bundle."
)

@dataclass(frozen=True)
class AuditPromptPreset:
    slug: str
    label: str
    description: str
    user_prompt: str


AUDIT_PROMPT_PRESETS: dict[str, AuditPromptPreset] = {
    "general_governance": AuditPromptPreset(
        slug="general_governance",
        label="General Governance",
        description="General TCRIA reading of governance gates, blocked items, support evidence, and unreadable documents.",
        user_prompt=(
            "Explain the TCRIA audit bundle for a legal operations user. "
            "Focus on what was scanned, what was classified as accusatory or supporting, "
            "where the governance/accountability risks are, and what should be reviewed first."
        ),
    ),
    "administrative_fiscal": AuditPromptPreset(
        slug="administrative_fiscal",
        label="Administrative Fiscal",
        description="Explain administrative/fiscal process bundles without inflating ordinary SEFAZ or PGE language into accusations.",
        user_prompt=(
            "Read this as an administrative/fiscal process bundle. "
            "Explain which documents are merely procedural or fiscal support, "
            "which ones actually matter for the claim, and whether the bundle looks administrative rather than accusatory."
        ),
    ),
    "restitution_accountability": AuditPromptPreset(
        slug="restitution_accountability",
        label="Restitution Accountability",
        description="Check whether a restitution-of-undue-payment request appears legally anchored and minimally documented.",
        user_prompt=(
            "Treat this as an accountability audit for requests for restitution of undue tax payment. "
            "Call out which requests appear to identify a concrete legal basis, which ones lack it, "
            "which documents support the calculation or the right claimed, and whether any request should be flagged "
            "under a strict rule because it asks for restitution without clearly showing the legal basis invoked."
        ),
    ),
    "icms_suspension_extension": AuditPromptPreset(
        slug="icms_suspension_extension",
        label="ICMS Suspension Extension",
        description="Analyze requests to extend ICMS suspension deadlines for repair, return, or industrialization cases.",
        user_prompt=(
            "Treat this as a bundle about extending ICMS suspension deadlines tied to invoices, DANFE, repair, return, or industrialization. "
            "Explain whether the documents look like ordinary fiscal support for the extension request, "
            "what decree/regulatory references appear, and which documents are central to the request."
        ),
    ),
    "civil_criminal_investigative": AuditPromptPreset(
        slug="civil_criminal_investigative",
        label="Civil/Criminal Investigative",
        description="Read the bundle as an investigative legal file set with focus on narrative coherence, evidentiary support, blocked items, and next investigative steps.",
        user_prompt=(
            "Treat this as a civil or criminal investigative bundle. "
            "Explain which documents appear central to the investigative narrative, "
            "which items are only contextual, what accountability or gateway blocks matter, "
            "and what a human investigator should review next."
        ),
    ),
    "gateway_conclusions": AuditPromptPreset(
        slug="gateway_conclusions",
        label="Gateway Conclusions",
        description="Explain the bundle in terms of final gateway conclusions, accountability minimums, traceability, compliance, and prescriptive blockers.",
        user_prompt=(
            "Explain this bundle as a gateway-conclusion review. "
            "Focus on whether the file set appears to satisfy accountability minimums, "
            "traceability, and compliance, and whether any prescriptive blocker prevents a stronger conclusion."
        ),
    ),
}


def list_audit_prompt_presets() -> list[dict[str, str]]:
    return [
        {
            "slug": preset.slug,
            "label": preset.label,
            "description": preset.description,
        }
        for preset in AUDIT_PROMPT_PRESETS.values()
    ]


def list_available_institutional_chat_profiles() -> list[dict[str, str]]:
    return list_institutional_chat_profiles()


def get_audit_prompt_preset(audit_type: str) -> AuditPromptPreset:
    preset = AUDIT_PROMPT_PRESETS.get(audit_type)
    if preset is None:
        available = ", ".join(sorted(AUDIT_PROMPT_PRESETS))
        raise RuntimeError(f"Unknown audit_type '{audit_type}'. Available values: {available}")
    return preset


def _compact_record(record: dict[str, Any]) -> dict[str, Any]:
    signals = record.get("key_signals") or {}
    interpretation = record.get("interpretation") or {}
    route_selection = interpretation.get("route_selection") or {}
    document_role = interpretation.get("document_role") or {}
    discursive_posture = interpretation.get("discursive_posture") or {}
    support_expectation = interpretation.get("support_expectation") or {}
    return {
        "file_name": record.get("file_name"),
        "classification": record.get("classification"),
        "artifact_type": record.get("artifact_type"),
        "overall_outcome": record.get("overall_outcome"),
        "classification_reasons": record.get("classification_reasons"),
        "selected_route": route_selection.get("selected_route"),
        "route_confidence": route_selection.get("confidence"),
        "document_role": document_role.get("value"),
        "document_role_confidence": document_role.get("confidence"),
        "discursive_posture": discursive_posture.get("value"),
        "posture_confidence": discursive_posture.get("confidence"),
        "support_expectation": {
            "legal_basis_expected": support_expectation.get("legal_basis_expected"),
            "factual_support_expected": support_expectation.get("factual_support_expected"),
            "traceability_expected": support_expectation.get("traceability_expected"),
        },
        "dates_found": signals.get("dates_found"),
        "currency_values_found": signals.get("currency_values_found"),
        "accusation_keyword_hits": signals.get("accusation_keyword_hits"),
        "evidence_marker_hits": signals.get("evidence_marker_hits"),
        "administrative_fiscal_marker_hits": signals.get("administrative_fiscal_marker_hits"),
        "restitution_request_hits": signals.get("restitution_request_hits"),
        "legal_basis_marker_hits": signals.get("legal_basis_marker_hits"),
        "accountability_support_hits": signals.get("accountability_support_hits"),
        "administrative_charge_hits": signals.get("administrative_charge_hits"),
        "icms_suspension_marker_hits": signals.get("icms_suspension_marker_hits"),
    }


def compact_bundle(bundle: dict[str, Any], max_items: int = 8) -> dict[str, Any]:
    accusation_set = bundle.get("accusation_set") or []
    non_accusation_set = bundle.get("non_accusation_set") or []

    supporting = [rec for rec in non_accusation_set if rec.get("classification") == "SUPPORTING_EVIDENCE_RELEVANT"]
    neutral = [rec for rec in non_accusation_set if rec.get("classification") == "NEUTRAL_OR_CONTEXT"]
    unreadable = [rec for rec in non_accusation_set if rec.get("classification") in {"UNREADABLE", "UNREADABLE_OR_EMPTY"}]

    return {
        "generated_at": bundle.get("generated_at"),
        "input_path": bundle.get("input_path"),
        "mode": bundle.get("mode"),
        "total_files_scanned": bundle.get("total_files_scanned"),
        "accusation_set_count": bundle.get("accusation_set_count"),
        "classification_counts": bundle.get("classification_counts"),
        "route_counts": bundle.get("route_counts"),
        "document_role_counts": bundle.get("document_role_counts"),
        "accusation_examples": [_compact_record(rec) for rec in accusation_set[:max_items]],
        "supporting_examples": [_compact_record(rec) for rec in supporting[:max_items]],
        "neutral_examples": [_compact_record(rec) for rec in neutral[:max_items]],
        "unreadable_examples": [_compact_record(rec) for rec in unreadable[:max_items]],
    }


def _extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output = getattr(response, "output", None)
    if not output:
        raise RuntimeError("OpenAI response did not contain text output.")

    chunks: list[str] = []
    for item in output:
        content = getattr(item, "content", None)
        if content is None and isinstance(item, dict):
            content = item.get("content")
        for part in content or []:
            text = getattr(part, "text", None)
            if text is None and isinstance(part, dict):
                text = part.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
    if not chunks:
        raise RuntimeError("OpenAI response did not contain readable text content.")
    return "\n\n".join(chunks)


def _response_metadata(response: Any) -> dict[str, Any]:
    response_id = getattr(response, "id", None)
    model = getattr(response, "model", None)
    return {
        "response_id": response_id,
        "model": model,
    }


def _parse_json_response(response: Any) -> dict[str, Any]:
    text = _extract_response_text(response)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"OpenAI response did not return valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("OpenAI response did not return a JSON object.")
    return payload


def run_audit_prompt(
    bundle: dict[str, Any],
    *,
    audit_type: str,
    model: str | None = None,
    max_items: int = 8,
    user_context: str | None = None,
) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError("OpenAI SDK is not installed. Run `pip install -e .` after adding the dependency.") from exc

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    preset = get_audit_prompt_preset(audit_type)
    client = OpenAI(api_key=api_key)
    prompt_payload = {
        "audit_type": preset.slug,
        "preset_description": preset.description,
        "user_context": user_context or preset.user_prompt,
        "bundle": compact_bundle(bundle, max_items=max_items),
    }

    response = client.responses.create(
        model=model or os.getenv("TCRIA_OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(prompt_payload, ensure_ascii=False, indent=2)}],
            },
        ],
    )
    return {
        "audit_type": preset.slug,
        "label": preset.label,
        "prompt_used": prompt_payload["user_context"],
        "response_text": _extract_response_text(response),
        "response_metadata": _response_metadata(response),
    }


def run_institutional_output_prompt(
    audit_data: dict[str, Any],
    *,
    model: str | None = None,
    user_context: str | None = None,
    chat_profile: str = "fazendario_institucional",
    system_prompt_override: str | None = None,
) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError("OpenAI SDK is not installed. Run `pip install -e .` after adding the dependency.") from exc

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    profile = get_institutional_chat_profile(chat_profile)
    client = OpenAI(api_key=api_key)
    prompt_payload = {
        "task": "Gerar saída institucional para auditoria processual.",
        "user_context": user_context or "Aplicar redação institucional formal, pronta para expediente.",
        "chat_profile": profile.slug,
        "schema": INSTITUTIONAL_OUTPUT_SCHEMA,
        "audit_data": audit_data,
    }

    response = client.responses.create(
        model=model or os.getenv("TCRIA_OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt_override or profile.system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(prompt_payload, ensure_ascii=False, indent=2)}],
            },
        ],
    )
    parsed = normalize_institutional_output(_parse_json_response(response))
    return {
        "institutional_output": parsed,
        "response_metadata": {
            **_response_metadata(response),
            "chat_profile": profile.slug,
        },
    }


def explain_audit_bundle(
    bundle: dict[str, Any],
    *,
    model: str | None = None,
    user_context: str | None = None,
    max_items: int = 8,
) -> str:
    return run_audit_prompt(
        bundle,
        audit_type="general_governance",
        model=model,
        user_context=user_context,
        max_items=max_items,
    )["response_text"]
