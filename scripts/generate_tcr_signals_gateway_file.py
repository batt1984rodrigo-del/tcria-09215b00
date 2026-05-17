#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


WORKSPACE = Path("/Users/rodrigobaptistadasilva/Documents/New project")
DEFAULT_AUDIT_JSON = WORKSPACE / "output" / "audit" / "tcr_gateway_accusation_bundle_audit.json"
STRICT_AUDIT_JSON = WORKSPACE / "output" / "audit" / "tcr_gateway_accusation_bundle_audit_strict.json"
OUTPUT_JSON = WORKSPACE / "output" / "gateway" / "tcr_signals_gateway_file.json"


@dataclass
class JoinedRecord:
    key: Tuple[str, str]
    default: Dict[str, Any]
    strict: Dict[str, Any] | None


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def index_records(payload: Dict[str, Any]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    idx: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for group in ("accusation_set", "non_accusation_set"):
        for rec in payload.get(group, []):
            key = (rec.get("file_name", ""), rec.get("sha256", ""))
            idx[key] = rec
    return idx


def outcome_headline(outcome: str | None) -> str:
    if not outcome:
        return "NO_DECISION"
    text = outcome.upper()
    if "BLOCKED" in text:
        return "BLOCKED"
    if "PARTIAL_PASS" in text:
        return "PARTIAL_PASS"
    if "PASS" in text:
        return "PASS"
    return "UNKNOWN"


def gate_status(rec: Dict[str, Any] | None, gate_name: str) -> str:
    if not rec:
        return "NOT_AVAILABLE"
    gates = rec.get("gates") or {}
    gate = gates.get(gate_name) or {}
    return gate.get("status", "NOT_AVAILABLE")


def gate_reason(rec: Dict[str, Any] | None, gate_name: str) -> str | None:
    if not rec:
        return None
    gates = rec.get("gates") or {}
    gate = gates.get(gate_name) or {}
    return gate.get("reason")


def sum_map_values(m: Dict[str, Any] | None) -> int:
    if not isinstance(m, dict):
        return 0
    total = 0
    for v in m.values():
        try:
            total += int(v)
        except Exception:
            pass
    return total


def clamp10(x: float) -> int:
    return int(max(0, min(10, round(x))))


def compute_structural_scores(result: dict, strict: bool = False):
    gates = result.get("gates", {})
    signals = result.get("signals", {})

    prescriptive_status = gates.get("prescriptiveGate", {}).get("status", "UNKNOWN")
    compliance_status = gates.get("complianceGate", {}).get("status", "UNKNOWN")

    dates = int(signals.get("dates_count", 0) or 0)
    money = int(signals.get("money_values_count", 0) or 0)
    pix = int(signals.get("pix_mentions", 0) or 0)
    text_len = int(signals.get("text_length", 0) or 0)

    # If a density is not present upstream, callers should provide a fallback.
    legal_density = float(signals.get("legal_terms_density", 0.0) or 0.0)

    # 1) CNE
    text_factor = min(1.0, text_len / 10000)
    legal_factor = min(1.0, legal_density * 5)
    cne = clamp10(2 + 5 * text_factor + 3 * legal_factor)

    # 2) AF
    d = min(1.0, dates / 25)
    m = min(1.0, money / 20)
    p = min(1.0, pix / 8)
    af = clamp10(1 + 4 * d + 4 * m + 2 * p)

    # 3) RF
    rf = clamp10(1 + 6 * legal_factor + 2 * d + 1 * m)

    # 4) GPI
    if prescriptive_status == "PASS":
        gpi = 9
    elif prescriptive_status in ("WARN", "PARTIAL_PASS"):
        gpi = 6
    elif prescriptive_status in ("FAIL", "BLOCKED"):
        gpi = 2
    else:
        gpi = 7

    # 5) MCE
    base_mce = clamp10(2 + 3 * text_factor + 3 * d + 2 * legal_factor)
    if strict and compliance_status in ("BLOCKED", "FAIL"):
        base_mce = max(0, base_mce - 3)
    mce = base_mce

    # Final IEE
    w_cne, w_af, w_rf, w_gpi, w_mce = 0.22, 0.22, 0.20, 0.18, 0.18
    iee = clamp10(
        (cne * w_cne)
        + (af * w_af)
        + (rf * w_rf)
        + (gpi * w_gpi)
        + (mce * w_mce)
    )

    if iee <= 3:
        band = "ALTO_RISCO_ESTRUTURAL"
    elif iee <= 5:
        band = "ESTRUTURA_INSTAVEL"
    elif iee <= 7:
        band = "ESTRUTURA_ACEITAVEL"
    elif iee <= 9:
        band = "ESTRUTURA_CONFIAVEL"
    else:
        band = "ESTRUTURA_AUDITAVEL_PREMIUM"

    return {
        "CNE": cne,
        "AF": af,
        "RF": rf,
        "GPI": gpi,
        "MCE": mce,
        "IEE": iee,
        "BAND": band,
    }


def estimate_legal_terms_density(ks: Dict[str, Any], text_length: int) -> float:
    density_scores = ks.get("density_scores") or {}
    for key in ("legal_refs_density", "legal_terms_density"):
        value = density_scores.get(key, ks.get(key))
        if value is None:
            continue
        try:
            return round(max(0.0, min(1.0, float(value))), 6)
        except Exception:
            continue

    # Legacy fallback for old audit outputs without regex densities.
    legal_count = sum_map_values(ks.get("accusation_keyword_hits"))
    if text_length <= 0:
        return 0.0
    density = legal_count / max(1.0, (text_length / 100.0))
    return round(max(0.0, min(1.0, density)), 6)


def estimate_accusation_density(ks: Dict[str, Any], text_length: int) -> float:
    density_scores = ks.get("density_scores") or {}
    value = density_scores.get("accusation_density", ks.get("accusation_density"))
    if value is not None:
        try:
            return round(max(0.0, min(1.0, float(value))), 6)
        except Exception:
            pass

    if text_length <= 0:
        return 0.0
    accusations = sum_map_values(ks.get("accusation_keyword_hits"))
    density = (accusations / (text_length / 1000.0)) * 0.08
    return round(max(0.0, min(1.0, density)), 6)


def normalize_disposition(default_rec: Dict[str, Any], strict_rec: Dict[str, Any] | None) -> str:
    classification = default_rec.get("classification", "")
    if classification == "SENSITIVE_EXCLUDED":
        return "SENSITIVE_EXCLUDED"
    if classification in {"UNREADABLE_OR_EMPTY", "UNREADABLE", "UNSUPPORTED"}:
        return "UNPROCESSABLE"

    strict_outcome = outcome_headline((strict_rec or {}).get("overall_outcome"))
    default_outcome = outcome_headline(default_rec.get("overall_outcome"))

    if strict_outcome == "BLOCKED":
        return "BLOCKED_STRICT"
    if default_outcome == "BLOCKED":
        return "BLOCKED"
    if default_outcome == "PARTIAL_PASS" and default_rec.get("raises_accusation"):
        return "REVIEW_REQUIRED"
    if classification == "ACCUSATORY_CANDIDATE":
        return "REVIEW_REQUIRED"
    if classification == "SUPPORTING_EVIDENCE_RELEVANT":
        return "SUPPORTING_EVIDENCE_RELEVANT"
    if classification == "SUPPORTING_EVIDENCE":
        return "SUPPORTING_EVIDENCE"
    return classification or "UNKNOWN"


def derive_priority(default_rec: Dict[str, Any], strict_rec: Dict[str, Any] | None) -> str:
    disposition = normalize_disposition(default_rec, strict_rec)
    ks = default_rec.get("key_signals") or {}
    pattern_counts = ks.get("legal_pattern_counts") or {}
    accusation_hits = max(
        sum_map_values(ks.get("accusation_keyword_hits")),
        int(pattern_counts.get("accusation", 0) or 0),
    )
    evidence_hits = sum_map_values(ks.get("evidence_marker_hits"))
    dates = int(ks.get("dates_found", 0) or 0)
    money = int(ks.get("currency_values_found", 0) or 0)

    if disposition == "SENSITIVE_EXCLUDED":
        return "sensitive"
    if disposition == "UNPROCESSABLE":
        return "low"
    if disposition == "BLOCKED_STRICT":
        if default_rec.get("raises_accusation") and (accusation_hits > 0 or evidence_hits > 0 or dates > 0 or money > 0):
            return "high"
        return "medium"
    if disposition in {"BLOCKED", "REVIEW_REQUIRED"}:
        return "medium"
    if disposition.startswith("SUPPORTING"):
        return "low"
    return "low"


def flatten_signal_counts(ks: Dict[str, Any]) -> Dict[str, int]:
    legal_pattern_counts = ks.get("legal_pattern_counts") or {}
    return {
        "dates_found": int(ks.get("dates_found", 0) or 0),
        "currency_values_found": int(ks.get("currency_values_found", 0) or 0),
        "pix_mentions": int(ks.get("pix_mentions", 0) or 0),
        "email_mentions": int(ks.get("email_mentions", 0) or 0),
        "transaction_terms": int(ks.get("transaction_terms", 0) or 0),
        "accusation_keyword_total": sum_map_values(ks.get("accusation_keyword_hits")),
        "evidence_marker_total": sum_map_values(ks.get("evidence_marker_hits")),
        "target_entity_total": sum_map_values(ks.get("target_entity_hits")),
        "legal_strong_pattern_total": int(legal_pattern_counts.get("legal_strong", 0) or 0),
        "legal_medium_pattern_total": int(legal_pattern_counts.get("legal_medium", 0) or 0),
        "accusation_pattern_total": int(legal_pattern_counts.get("accusation", 0) or 0),
    }


def build_score_input_shape(
    rec: Dict[str, Any] | None,
    ks: Dict[str, Any],
    text_length: int,
    legal_terms_density: float,
    accusation_density: float,
) -> Dict[str, Any] | None:
    if rec is None:
        return None
    return {
        "gates": {
            "prescriptiveGate": {"status": gate_status(rec, "prescriptiveGate")},
            "complianceGate": {"status": gate_status(rec, "complianceGate")},
        },
        "signals": {
            # Canonical + fallbacks/aliases for downstream compatibility.
            "dates_count": int(ks.get("dates_found", 0) or 0),
            "money_values_count": int(ks.get("currency_values_found", 0) or 0),
            "pix_mentions": int(ks.get("pix_mentions", 0) or 0),
            "text_length": int(text_length or 0),
            "legal_terms_density": float(legal_terms_density or 0.0),
            "accusation_density": float(accusation_density or 0.0),
            # Explicit repeated aliases (fallback layer).
            "dates_found": int(ks.get("dates_found", 0) or 0),
            "currency_values_found": int(ks.get("currency_values_found", 0) or 0),
            "text_chars": int(text_length or 0),
        },
    }


def build_gateway_record(jr: JoinedRecord) -> Dict[str, Any]:
    d = jr.default
    s = jr.strict
    ks = d.get("key_signals") or {}
    normalized = normalize_disposition(d, s)
    text_length = int(d.get("text_chars", 0) or 0)
    legal_terms_density = estimate_legal_terms_density(ks, text_length)
    accusation_density = estimate_accusation_density(ks, text_length)
    counts = flatten_signal_counts(ks)
    signal_fallbacks = {
        "dates_count": counts["dates_found"],
        "money_values_count": counts["currency_values_found"],
        "text_length": text_length,
        "text_chars": text_length,
        "legal_terms_density": legal_terms_density,
        "accusation_density": accusation_density,
        "dates_found": counts["dates_found"],
        "currency_values_found": counts["currency_values_found"],
    }
    default_score_input = build_score_input_shape(d, ks, text_length, legal_terms_density, accusation_density)
    strict_score_input = build_score_input_shape(s, ks, text_length, legal_terms_density, accusation_density) if s else None
    default_structural_scores = compute_structural_scores(default_score_input or {"gates": {}, "signals": {}}, strict=False)
    strict_structural_scores = (
        compute_structural_scores(strict_score_input or {"gates": {}, "signals": {}}, strict=True) if strict_score_input else None
    )

    return {
        "gatewayRecordVersion": "1.0",
        "recordId": f"{(d.get('sha256') or '')[:16]}:{d.get('file_name','')}",
        "file": {
            "name": d.get("file_name"),
            "path": d.get("file_path"),
            "suffix": d.get("suffix"),
            "sizeBytes": d.get("size_bytes"),
            "sha256": d.get("sha256"),
        },
        "pipeline": {
            "extractionStatus": d.get("extraction_status"),
            "extractionMethod": d.get("extraction_method"),
            "textChars": d.get("text_chars"),
            "textQuality": d.get("text_quality"),
            "sensitiveHandling": d.get("sensitive_handling"),
        },
        "classification": {
            "label": d.get("classification"),
            "raisesAccusation": bool(d.get("raises_accusation")),
            "reasons": d.get("classification_reasons") or [],
        },
        "signals": {
            "counts": counts,
            "derived": {
                "legalTermsDensity": legal_terms_density,
                "accusationDensity": accusation_density,
                "densitySource": "regex_patterns_v1 if present in audit key_signals, else legacy fallback",
                "legalTermsDensityModel": "legal_refs_density regex-based (preferred) or legacy fallback",
            },
            "fallbacks": signal_fallbacks,
            "flags": {
                "containsObjetivoLabel": bool(ks.get("contains_objetivo_label")),
                "containsAutorLabel": bool(ks.get("contains_autor_label")),
                "containsSummaryLabel": bool(ks.get("contains_summary_label")),
            },
            "keywordHits": {
                "accusation": ks.get("accusation_keyword_hits") or {},
                "evidence": ks.get("evidence_marker_hits") or {},
                "targetEntity": ks.get("target_entity_hits") or {},
            },
        },
        "scoreInputs": {
            "default": default_score_input,
            "strict": strict_score_input,
        },
        "gatewayAssessment": {
            "normalizedDisposition": normalized,
            "reviewPriority": derive_priority(d, s),
            "defaultMode": {
                "mode": "default-heuristic",
                "overallOutcome": d.get("overall_outcome"),
                "gateStatus": {
                    "prescriptiveGate": gate_status(d, "prescriptiveGate"),
                    "complianceGate": gate_status(d, "complianceGate"),
                    "traceabilityCheck": gate_status(d, "traceabilityCheck"),
                    "maturityGate": gate_status(d, "maturityGate"),
                    "ledgerRuntimeCheck": gate_status(d, "ledgerRuntimeCheck"),
                },
            },
            "strictMode": {
                "mode": "strict-explicit-decision-record",
                "overallOutcome": (s or {}).get("overall_outcome"),
                "gateStatus": {
                    "prescriptiveGate": gate_status(s, "prescriptiveGate"),
                    "complianceGate": gate_status(s, "complianceGate"),
                    "traceabilityCheck": gate_status(s, "traceabilityCheck"),
                    "maturityGate": gate_status(s, "maturityGate"),
                    "ledgerRuntimeCheck": gate_status(s, "ledgerRuntimeCheck"),
                },
            }
            if s
            else None,
            "notes": {
                "strictComplianceReason": gate_reason(s, "complianceGate"),
                "defaultComplianceReason": gate_reason(d, "complianceGate"),
            },
            "structuralScores": {
                "default": default_structural_scores,
                "strict": strict_structural_scores,
            },
        },
    }


def build_summary(records: List[Dict[str, Any]], default_payload: Dict[str, Any], strict_payload: Dict[str, Any] | None) -> Dict[str, Any]:
    disposition_counts = Counter(r["gatewayAssessment"]["normalizedDisposition"] for r in records)
    priority_counts = Counter(r["gatewayAssessment"]["reviewPriority"] for r in records)

    accusation_records = [r for r in records if r["classification"]["raisesAccusation"]]
    default_blocked = sum(
        1
        for r in accusation_records
        if (r["gatewayAssessment"]["defaultMode"]["overallOutcome"] or "").upper().find("BLOCKED") >= 0
    )
    default_partial = sum(
        1
        for r in accusation_records
        if (r["gatewayAssessment"]["defaultMode"]["overallOutcome"] or "").upper().find("PARTIAL_PASS") >= 0
    )
    strict_blocked = 0
    if strict_payload:
        for r in accusation_records:
            strict_mode = r["gatewayAssessment"].get("strictMode") or {}
            if (strict_mode.get("overallOutcome") or "").upper().find("BLOCKED") >= 0:
                strict_blocked += 1

    default_iee_bands = Counter(
        ((r.get("gatewayAssessment") or {}).get("structuralScores") or {}).get("default", {}).get("BAND", "UNKNOWN")
        for r in records
    )
    strict_iee_bands = Counter(
        ((r.get("gatewayAssessment") or {}).get("structuralScores") or {}).get("strict", {}).get("BAND", "UNKNOWN")
        for r in records
        if ((r.get("gatewayAssessment") or {}).get("structuralScores") or {}).get("strict") is not None
    )

    return {
        "totalRecords": len(records),
        "accusationCandidates": len(accusation_records),
        "defaultMode": {
            "complianceGateMode": default_payload.get("compliance_gate_mode"),
            "blockedAccusationCandidates": default_blocked,
            "partialPassAccusationCandidates": default_partial,
        },
        "strictMode": {
            "complianceGateMode": (strict_payload or {}).get("compliance_gate_mode"),
            "blockedAccusationCandidates": strict_blocked,
        }
        if strict_payload
        else None,
        "normalizedDispositionCounts": dict(sorted(disposition_counts.items())),
        "reviewPriorityCounts": dict(sorted(priority_counts.items())),
        "structuralBands": {
            "default": dict(sorted(default_iee_bands.items())),
            "strict": dict(sorted(strict_iee_bands.items())),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate consolidated TCR signals gateway JSON file from audit outputs.")
    parser.add_argument("--default-audit", default=str(DEFAULT_AUDIT_JSON), help="Path to default audit JSON")
    parser.add_argument("--strict-audit", default=str(STRICT_AUDIT_JSON), help="Path to strict audit JSON (optional)")
    parser.add_argument("--out", default=str(OUTPUT_JSON), help="Output gateway JSON path")
    args = parser.parse_args()

    default_path = Path(args.default_audit)
    strict_path = Path(args.strict_audit)
    out_path = Path(args.out)

    default_payload = load_json(default_path)
    strict_payload = load_json(strict_path) if strict_path.exists() else None

    default_idx = index_records(default_payload)
    strict_idx = index_records(strict_payload) if strict_payload else {}

    joined: List[JoinedRecord] = []
    for key, d_rec in sorted(default_idx.items(), key=lambda kv: kv[0][0].lower()):
        joined.append(JoinedRecord(key=key, default=d_rec, strict=strict_idx.get(key)))

    records = [build_gateway_record(j) for j in joined]
    summary = build_summary(records, default_payload, strict_payload)

    payload = {
        "gatewayFileVersion": "1.0",
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "generator": {
            "script": str((WORKSPACE / "scripts" / "generate_tcr_signals_gateway_file.py")),
            "workspace": str(WORKSPACE),
        },
        "policyContext": {
            "policyVersion": "policy-v1.0.0",
            "auditBasis": "TCR-IA-style static document audit using project gates (prescriptive/compliance/traceability)",
            "note": "maturityGate and ledgerRuntimeCheck remain not evaluable/not applicable for static files.",
        },
        "sourceArtifacts": {
            "defaultAuditJson": str(default_path),
            "strictAuditJson": str(strict_path) if strict_payload else None,
        },
        "summary": summary,
        "records": records,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"TCR signals gateway file: {out_path}")
    print(f"Records: {len(records)}")
    print(f"Accusation candidates: {summary['accusationCandidates']}")
    print(f"Disposition counts: {summary['normalizedDispositionCounts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
