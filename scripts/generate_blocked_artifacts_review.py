#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ENGINE_NAME = "tcria"
ENGINE_VERSION = "0.1.0"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def top_hits(values: Dict[str, Any], limit: int = 4) -> str:
    items: List[Tuple[str, int]] = []
    for k, v in values.items():
        try:
            iv = int(v)
        except Exception:
            continue
        if iv > 0:
            items.append((str(k), iv))
    if not items:
        return ""
    items.sort(key=lambda p: (-p[1], p[0]))
    return ", ".join(f"{k}={v}" for k, v in items[:limit])


def infer_document_kind(item: Dict[str, Any]) -> str:
    name_l = str(item.get("file_name", "")).lower()
    suffix = str(item.get("suffix", "")).lower()
    artifact_type = str(item.get("artifact_type", "")).upper()

    if suffix == ".csv":
        return "financial_or_dataset_annex"
    if suffix in {".png", ".jpg", ".jpeg", ".heic"}:
        return "visual_attachment"
    if suffix == ".webarchive":
        return "web_capture_or_email_record"
    if "peticao" in name_l or "petição" in name_l or "recurso" in name_l:
        return "petition_or_filing"
    if "dossie" in name_l or "dossiê" in name_l:
        return "dossier"
    if "extrato" in name_l or "fatura" in name_l:
        return "financial_evidence_bundle"
    if artifact_type == "ANALYTICAL_ARTIFACT":
        return "analytical_narrative"
    if artifact_type == "DECISION_ARTIFACT":
        return "decision_artifact"
    return "unclassified_document"


def summarize_content(item: Dict[str, Any]) -> str:
    signals = item.get("key_signals") or {}
    acc_hits = signals.get("accusation_keyword_hits") or {}
    evidence_hits = signals.get("evidence_marker_hits") or {}
    target_hits = signals.get("target_entity_hits") or {}
    dates = int(signals.get("dates_found", 0) or 0)
    currency = int(signals.get("currency_values_found", 0) or 0)
    pix = int(signals.get("pix_mentions", 0) or 0)

    parts: List[str] = []
    acc_txt = top_hits(acc_hits)
    if acc_txt:
        parts.append(f"Accusatory terms: {acc_txt}.")
    ev_txt = top_hits(evidence_hits)
    if ev_txt:
        parts.append(f"Evidence markers: {ev_txt}.")
    tgt_txt = top_hits(target_hits)
    if tgt_txt:
        parts.append(f"Theme entities: {tgt_txt}.")
    if dates > 0 or currency > 0 or pix > 0:
        parts.append(f"Traceability markers: dates={dates}, currency={currency}, pix={pix}.")

    if parts:
        return " ".join(parts)

    reasons = item.get("classification_reasons") or []
    if reasons:
        return f"Classification context: {reasons[0]}"
    return "No strong textual markers were detected in the source audit signals."


def blocked_gate_reason(item: Dict[str, Any]) -> Tuple[str, str]:
    overall = str(item.get("overall_outcome", ""))
    gates = item.get("gates") or {}

    preferred_gate = None
    m = re.search(r"\(([^)]+)\)", overall)
    if m:
        preferred_gate = m.group(1).strip()
    if preferred_gate and isinstance(gates.get(preferred_gate), dict):
        reason = str((gates.get(preferred_gate) or {}).get("reason") or "").strip()
        if reason:
            return preferred_gate, reason

    for gate_name in ["complianceGate", "prescriptiveGate", "traceabilityCheck", "maturityGate", "ledgerRuntimeCheck"]:
        gate = gates.get(gate_name) or {}
        status = str(gate.get("status", "")).upper()
        if status in {"BLOCKED", "FAIL", "WARN"}:
            reason = str(gate.get("reason") or "").strip()
            if reason:
                return gate_name, reason

    return "unknownGate", "No explicit blocking reason found in gate payload."


def theme_related(item: Dict[str, Any]) -> bool:
    signals = item.get("key_signals") or {}
    acc = signals.get("accusation_keyword_hits") or {}
    evidence = signals.get("evidence_marker_hits") or {}
    targets = signals.get("target_entity_hits") or {}
    return bool(acc or evidence or targets)


def organizational_issue_flags(item: Dict[str, Any]) -> List[str]:
    gates = item.get("gates") or {}
    signals = item.get("key_signals") or {}
    flags: List[str] = []

    compliance = gates.get("complianceGate") or {}
    if str(compliance.get("status", "")).upper() == "BLOCKED":
        flags.append("falta_metadado_governanca")
    if not bool(signals.get("contains_objetivo_label", False)):
        flags.append("sem_objetivo_explicito")
    if not bool(signals.get("contains_autor_label", False)):
        flags.append("sem_autor_responsavel_explicito")
    if str((gates.get("traceabilityCheck") or {}).get("status", "")).upper() == "WARN":
        flags.append("rastreabilidade_limitada")
    return flags


def potential_case_impact(item: Dict[str, Any], related: bool) -> str:
    gates = item.get("gates") or {}
    prescriptive_blocked = str((gates.get("prescriptiveGate") or {}).get("status", "")).upper() == "BLOCKED"
    compliance_blocked = str((gates.get("complianceGate") or {}).get("status", "")).upper() == "BLOCKED"
    traceability_status = str((gates.get("traceabilityCheck") or {}).get("status", "")).upper()

    if prescriptive_blocked and not related:
        return "hurts"
    if related and traceability_status == "PASS" and not prescriptive_blocked and not compliance_blocked:
        return "helps"
    if related:
        return "mixed"
    return "unclear"


def recommended_action(item: Dict[str, Any], issue_flags: List[str]) -> str:
    gates = item.get("gates") or {}
    actions: List[str] = []

    if "falta_metadado_governanca" in issue_flags:
        actions.append("Add explicit DecisionRecord metadata: responsibleHuman, declaredPurpose, approved.")
    if "rastreabilidade_limitada" in issue_flags:
        actions.append("Attach traceable anchors (dates, values, and linkable supporting files).")
    if str((gates.get("prescriptiveGate") or {}).get("status", "")).upper() == "BLOCKED":
        actions.append("Rewrite prescriptive language into factual and attributable statements.")

    if not actions:
        actions.append("Keep status as BLOCKED and submit for focused human review.")
    return " ".join(actions)


def build_blocked_review(item: Dict[str, Any]) -> Dict[str, Any]:
    gate_name, reason = blocked_gate_reason(item)
    related = theme_related(item)
    issue_flags = organizational_issue_flags(item)
    impact = potential_case_impact(item, related)
    identity = item.get("artifact_identity") or {
        "file_sha256": item.get("sha256"),
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "gate_policy_version": "unknown",
        "source_path": item.get("file_path"),
    }

    return {
        "file_name": item.get("file_name"),
        "file_path": item.get("file_path"),
        "official_outcome": item.get("overall_outcome"),
        "blocked_gate": gate_name,
        "blocked_reason": reason,
        "artifact_identity": identity,
        "diagnostic_guardrails": {
            "review_mode": "complementary_only",
            "changes_official_outcome": False,
            "eligible_for_promotion": False,
            "requires_human_re_audit_for_status_change": True,
        },
        "blockedArtifactReview": {
            "document_kind": infer_document_kind(item),
            "content_summary": summarize_content(item),
            "theme_related": related,
            "organizational_issue": bool(issue_flags),
            "organizational_issue_reasons": issue_flags,
            "traceability_gap_reason": reason,
            "potential_case_impact": impact,
            "recommended_action": recommended_action(item, issue_flags),
        },
    }


def write_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Analise complementar dos bloqueados")
    lines.append("")
    lines.append("Camada adicional: o status oficial do gate permanece inalterado.")
    lines.append("")
    lines.append(f"- Gerado em: `{payload.get('generated_at')}`")
    lines.append(f"- Fonte: `{payload.get('source_audit')}`")
    lines.append(f"- Bloqueados analisados: `{payload.get('blocked_count', 0)}`")
    lines.append("")

    for rec in payload.get("blocked_artifacts_review", []):
        review = rec.get("blockedArtifactReview") or {}
        identity = rec.get("artifact_identity") or {}
        lines.append(f"## {rec.get('file_name')}")
        lines.append(f"- Resultado oficial: `{rec.get('official_outcome')}`")
        lines.append(f"- Motivo do bloqueio: {rec.get('blocked_reason')}")
        lines.append(
            "- Identity: "
            f"sha256={str(identity.get('file_sha256', '-'))[:16]}..., "
            f"engine={identity.get('engine','-')}@{identity.get('engine_version','-')}, "
            f"policy={identity.get('gate_policy_version','-')}"
        )
        lines.append(f"- Tipo de documento: `{review.get('document_kind')}`")
        lines.append(f"- Conteudo: {review.get('content_summary')}")
        lines.append(f"- Relacao com o tema: `{review.get('theme_related')}`")
        lines.append(f"- Problema de organizacao/governanca: `{review.get('organizational_issue')}`")
        lines.append(f"- Razoes de organizacao/governanca: `{review.get('organizational_issue_reasons')}`")
        lines.append(f"- Impacto potencial no caso: `{review.get('potential_case_impact')}`")
        lines.append(f"- Acao recomendada: {review.get('recommended_action')}")
        lines.append("")

    return "\n".join(lines) + "\n"


def extract_records(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, dict):
        return list(data.get("accusation_set") or [])
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def is_blocked(item: Dict[str, Any]) -> bool:
    return "BLOCKED" in str(item.get("overall_outcome", "")).upper()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate complementary blocked-artifact review from an existing audit JSON.")
    parser.add_argument(
        "input",
        nargs="?",
        default="tcr_gateway_accusation_bundle_audit_strict.json",
        help="Path to the source audit JSON.",
    )
    parser.add_argument("--json-out", default=None, help="Output JSON path (default: next to input).")
    parser.add_argument("--md-out", default=None, help="Output Markdown path (default: next to input).")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    data = load_json(input_path)
    records = extract_records(data)
    blocked_records = [build_blocked_review(item) for item in records if is_blocked(item)]

    json_out = Path(args.json_out).expanduser().resolve() if args.json_out else input_path.with_name("tcr_gateway_blocked_artifacts_review.json")
    md_out = Path(args.md_out).expanduser().resolve() if args.md_out else input_path.with_name("tcr_gateway_blocked_artifacts_review.md")

    payload: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_audit": str(input_path),
        "blocked_count": len(blocked_records),
        "blocked_artifacts_review": blocked_records,
        "note": "Complementary analysis only. Official gate outcomes are preserved.",
    }

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_out.write_text(write_markdown(payload), encoding="utf-8")

    print(f"Source audit: {input_path}")
    print(f"Blocked artifacts: {len(blocked_records)}")
    print(f"JSON review: {json_out}")
    print(f"Markdown review: {md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
