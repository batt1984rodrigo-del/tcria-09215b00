#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def top_hits_total(values: Dict[str, Any]) -> int:
    total = 0
    for v in values.values():
        total += to_int(v)
    return total


def compact_hits(values: Dict[str, Any], limit: int = 4) -> Dict[str, int]:
    pairs: List[Tuple[str, int]] = []
    for k, v in values.items():
        iv = to_int(v)
        if iv > 0:
            pairs.append((str(k), iv))
    pairs.sort(key=lambda x: (-x[1], x[0]))
    return {k: v for k, v in pairs[:limit]}


def evidence_score(rec: Dict[str, Any]) -> float:
    gates = rec.get("gates") or {}
    signals = rec.get("key_signals") or {}

    score = 0.0
    if str((gates.get("traceabilityCheck") or {}).get("status", "")).upper() == "PASS":
        score += 3.0
    if str((gates.get("complianceGate") or {}).get("status", "")).upper() == "PASS":
        score += 1.5

    score += min(3.0, to_int(signals.get("dates_found", 0)) * 0.1)
    score += min(3.0, to_int(signals.get("currency_values_found", 0)) * 0.06)
    score += min(2.0, to_int(signals.get("pix_mentions", 0)) * 0.15)
    score += min(3.0, top_hits_total(signals.get("evidence_marker_hits") or {}) * 0.2)
    score += min(1.5, top_hits_total(signals.get("target_entity_hits") or {}) * 0.05)
    return round(score, 4)


def narrative_score(rec: Dict[str, Any]) -> float:
    signals = rec.get("key_signals") or {}
    artifact_type = str(rec.get("artifact_type", "")).upper()

    score = 0.0
    if artifact_type == "ANALYTICAL_ARTIFACT":
        score += 2.5
    score += min(2.0, top_hits_total(signals.get("accusation_keyword_hits") or {}) * 0.08)
    score += min(2.0, top_hits_total(signals.get("target_entity_hits") or {}) * 0.08)
    score += min(1.0, float(signals.get("accusation_density", 0.0) or 0.0) * 4.0)
    score += min(1.0, float(signals.get("legal_refs_density", 0.0) or 0.0) * 4.0)
    score += min(1.5, to_int(rec.get("text_chars", 0)) / 8000.0)
    return round(score, 4)


def compute_top_evidence(acc_set: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    ranked = sorted(acc_set, key=evidence_score, reverse=True)[:top_k]
    out: List[Dict[str, Any]] = []
    for rec in ranked:
        signals = rec.get("key_signals") or {}
        out.append(
            {
                "file_name": rec.get("file_name"),
                "file_path": rec.get("file_path"),
                "overall_outcome": rec.get("overall_outcome"),
                "evidence_score": evidence_score(rec),
                "traceability_status": (rec.get("gates") or {}).get("traceabilityCheck", {}).get("status"),
                "dates_found": to_int(signals.get("dates_found", 0)),
                "currency_values_found": to_int(signals.get("currency_values_found", 0)),
                "pix_mentions": to_int(signals.get("pix_mentions", 0)),
                "evidence_marker_hits": compact_hits(signals.get("evidence_marker_hits") or {}),
            }
        )
    return out


def compute_top_narrative(acc_set: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    ranked = sorted(acc_set, key=narrative_score, reverse=True)[:top_k]
    out: List[Dict[str, Any]] = []
    for rec in ranked:
        signals = rec.get("key_signals") or {}
        out.append(
            {
                "file_name": rec.get("file_name"),
                "file_path": rec.get("file_path"),
                "overall_outcome": rec.get("overall_outcome"),
                "artifact_type": rec.get("artifact_type"),
                "narrative_score": narrative_score(rec),
                "accusation_hits": compact_hits(signals.get("accusation_keyword_hits") or {}),
                "target_entity_hits": compact_hits(signals.get("target_entity_hits") or {}),
                "accusation_density": signals.get("accusation_density"),
            }
        )
    return out


def compute_blocked_but_relevant(blocked_review: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
    items = blocked_review.get("blocked_artifacts_review") or []
    relevant = []
    for rec in items:
        review = rec.get("blockedArtifactReview") or {}
        if bool(review.get("theme_related")) and str(review.get("potential_case_impact", "")).lower() in {"helps", "mixed"}:
            relevant.append(
                {
                    "file_name": rec.get("file_name"),
                    "official_outcome": rec.get("official_outcome"),
                    "blocked_gate": rec.get("blocked_gate"),
                    "blocked_reason": rec.get("blocked_reason"),
                    "potential_case_impact": review.get("potential_case_impact"),
                    "organizational_issue": review.get("organizational_issue"),
                    "recommended_action": review.get("recommended_action"),
                }
            )
    return relevant[:top_k]


def compute_governance_gaps(acc_set: List[Dict[str, Any]], blocked_review: Dict[str, Any]) -> List[Dict[str, Any]]:
    counters = Counter()
    examples: Dict[str, List[str]] = {
        "missing_responsibleHuman": [],
        "missing_declaredPurpose": [],
        "missing_approved": [],
        "traceability_limited": [],
        "prescriptive_language_blocked": [],
    }

    for rec in acc_set:
        file_name = str(rec.get("file_name", ""))
        gates = rec.get("gates") or {}
        compliance = gates.get("complianceGate") or {}
        traceability = gates.get("traceabilityCheck") or {}
        prescriptive = gates.get("prescriptiveGate") or {}

        reason = str(compliance.get("reason", ""))
        if str(compliance.get("status", "")).upper() == "BLOCKED":
            if "responsibleHuman" in reason:
                counters["missing_responsibleHuman"] += 1
                if len(examples["missing_responsibleHuman"]) < 3:
                    examples["missing_responsibleHuman"].append(file_name)
            if "declaredPurpose" in reason:
                counters["missing_declaredPurpose"] += 1
                if len(examples["missing_declaredPurpose"]) < 3:
                    examples["missing_declaredPurpose"].append(file_name)
            if "approved" in reason:
                counters["missing_approved"] += 1
                if len(examples["missing_approved"]) < 3:
                    examples["missing_approved"].append(file_name)

        if str(traceability.get("status", "")).upper() == "WARN":
            counters["traceability_limited"] += 1
            if len(examples["traceability_limited"]) < 3:
                examples["traceability_limited"].append(file_name)

        if str(prescriptive.get("status", "")).upper() == "BLOCKED":
            counters["prescriptive_language_blocked"] += 1
            if len(examples["prescriptive_language_blocked"]) < 3:
                examples["prescriptive_language_blocked"].append(file_name)

    for rec in blocked_review.get("blocked_artifacts_review") or []:
        review = rec.get("blockedArtifactReview") or {}
        for flag in review.get("organizational_issue_reasons") or []:
            if flag == "rastreabilidade_limitada":
                counters["traceability_limited"] += 1
                if len(examples["traceability_limited"]) < 3:
                    examples["traceability_limited"].append(str(rec.get("file_name", "")))

    out = []
    for gap in [
        "missing_responsibleHuman",
        "missing_declaredPurpose",
        "missing_approved",
        "traceability_limited",
        "prescriptive_language_blocked",
    ]:
        out.append(
            {
                "gap": gap,
                "count": int(counters.get(gap, 0)),
                "examples": examples.get(gap) or [],
            }
        )
    return out


def compute_timeline_candidates(acc_set: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    sorted_items = sorted(
        acc_set,
        key=lambda r: to_int((r.get("key_signals") or {}).get("dates_found", 0)),
        reverse=True,
    )
    out: List[Dict[str, Any]] = []
    for rec in sorted_items:
        signals = rec.get("key_signals") or {}
        dates = to_int(signals.get("dates_found", 0))
        if dates <= 0:
            continue
        out.append(
            {
                "file_name": rec.get("file_name"),
                "overall_outcome": rec.get("overall_outcome"),
                "dates_found": dates,
                "currency_values_found": to_int(signals.get("currency_values_found", 0)),
                "pix_mentions": to_int(signals.get("pix_mentions", 0)),
            }
        )
        if len(out) >= top_k:
            break
    return out


def compute_case_readiness(acc_set: List[Dict[str, Any]], blocked_review: Dict[str, Any]) -> str:
    total = len(acc_set)
    if total == 0:
        return "low"

    blocked = sum(1 for r in acc_set if "BLOCKED" in str(r.get("overall_outcome", "")).upper())
    traceability_pass = sum(
        1
        for r in acc_set
        if str(((r.get("gates") or {}).get("traceabilityCheck") or {}).get("status", "")).upper() == "PASS"
    )
    blocked_ratio = blocked / total
    traceability_ratio = traceability_pass / total
    relevant_blocked = len(compute_blocked_but_relevant(blocked_review, top_k=9999))

    if traceability_ratio >= 0.55 and blocked_ratio <= 0.35 and relevant_blocked <= max(2, total // 10):
        return "high"
    if traceability_ratio >= 0.25 and blocked_ratio <= 0.75:
        return "medium"
    return "low"


def compute_recommended_actions(gaps: List[Dict[str, Any]], blocked_relevant_count: int, timeline_count: int) -> List[str]:
    gap_map = {g["gap"]: int(g.get("count", 0)) for g in gaps}
    actions: List[str] = []

    if gap_map.get("missing_responsibleHuman", 0) or gap_map.get("missing_declaredPurpose", 0) or gap_map.get("missing_approved", 0):
        actions.append(
            "Padronizar DecisionRecord nos arquivos prioritarios (responsibleHuman, declaredPurpose, approved) antes de nova rodada."
        )
    if gap_map.get("prescriptive_language_blocked", 0):
        actions.append("Reescrever linguagem prescritiva/conclusiva em formato factual e rastreavel nos arquivos bloqueados por prescriptiveGate.")
    if gap_map.get("traceability_limited", 0):
        actions.append("Fortalecer rastreabilidade com ancoras de data/valor e vinculo explicito aos anexos relevantes.")
    if blocked_relevant_count:
        actions.append("Priorizar saneamento dos bloqueados relevantes (impacto helps/mixed) para reduzir perda de material util.")
    if timeline_count:
        actions.append("Consolidar cronologia minima com os arquivos de maior densidade temporal para preparacao de narrativa processual.")
    if not actions:
        actions.append("Manter fluxo atual e executar revisao humana final do pacote.")
    return actions


def write_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Case Preparation Summary")
    lines.append("")
    lines.append("- Camada adicional: interpretativa, sem alterar resultado oficial de gates.")
    lines.append(f"- Source audit: `{payload.get('source_audit')}`")
    lines.append(f"- Source blocked review: `{payload.get('source_blocked_review')}`")
    lines.append(f"- Generated at: `{payload.get('generated_at')}`")
    lines.append(f"- Case readiness: `{payload.get('case_readiness')}`")
    lines.append("")

    lines.append("## Top Evidence Files")
    lines.append("")
    for rec in payload.get("top_evidence_files") or []:
        lines.append(
            f"- `{rec.get('file_name')}` | score={rec.get('evidence_score')} | outcome={rec.get('overall_outcome')} | "
            f"traceability={rec.get('traceability_status')} | dates={rec.get('dates_found')} | currency={rec.get('currency_values_found')} | pix={rec.get('pix_mentions')}"
        )
    lines.append("")

    lines.append("## Top Narrative Files")
    lines.append("")
    for rec in payload.get("top_narrative_files") or []:
        lines.append(
            f"- `{rec.get('file_name')}` | score={rec.get('narrative_score')} | artifact_type={rec.get('artifact_type')} | outcome={rec.get('overall_outcome')}"
        )
    lines.append("")

    lines.append("## Blocked But Relevant")
    lines.append("")
    for rec in payload.get("blocked_but_relevant") or []:
        lines.append(
            f"- `{rec.get('file_name')}` | gate={rec.get('blocked_gate')} | impact={rec.get('potential_case_impact')} | outcome={rec.get('official_outcome')}"
        )
    lines.append("")

    lines.append("## Governance Gaps")
    lines.append("")
    for rec in payload.get("governance_gaps") or []:
        lines.append(f"- `{rec.get('gap')}`: {rec.get('count')} (examples: {rec.get('examples')})")
    lines.append("")

    lines.append("## Timeline Candidates")
    lines.append("")
    for rec in payload.get("timeline_candidates") or []:
        lines.append(
            f"- `{rec.get('file_name')}` | dates={rec.get('dates_found')} | currency={rec.get('currency_values_found')} | pix={rec.get('pix_mentions')} | outcome={rec.get('overall_outcome')}"
        )
    lines.append("")

    lines.append("## Recommended Next Actions")
    lines.append("")
    for action in payload.get("recommended_next_actions") or []:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def infer_default_output_paths(audit_json: Path) -> Tuple[Path, Path]:
    base = re.sub(r"_strict$", "", audit_json.stem)
    parent = audit_json.parent
    return (
        parent / f"{base}_case_preparation_summary.json",
        parent / f"{base}_case_preparation_summary.md",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate layer-5 case preparation summary from audit + blocked review.")
    parser.add_argument("--audit-json", required=True, help="Official audit JSON path.")
    parser.add_argument("--blocked-json", required=True, help="Blocked artifacts review JSON path.")
    parser.add_argument("--json-out", default=None, help="Output JSON path.")
    parser.add_argument("--md-out", default=None, help="Output Markdown path.")
    parser.add_argument("--top-k", type=int, default=10, help="Top K files for evidence/narrative/timeline lists.")
    args = parser.parse_args()

    audit_json = Path(args.audit_json).expanduser().resolve()
    blocked_json = Path(args.blocked_json).expanduser().resolve()
    if not audit_json.exists():
        raise SystemExit(f"Missing audit JSON: {audit_json}")
    if not blocked_json.exists():
        raise SystemExit(f"Missing blocked review JSON: {blocked_json}")

    audit = load_json(audit_json)
    blocked = load_json(blocked_json)
    acc_set = list(audit.get("accusation_set") or [])

    top_evidence = compute_top_evidence(acc_set, top_k=max(1, args.top_k))
    top_narrative = compute_top_narrative(acc_set, top_k=max(1, args.top_k))
    blocked_relevant = compute_blocked_but_relevant(blocked, top_k=max(1, args.top_k))
    governance_gaps = compute_governance_gaps(acc_set, blocked)
    timeline_candidates = compute_timeline_candidates(acc_set, top_k=max(1, args.top_k))
    case_readiness = compute_case_readiness(acc_set, blocked)
    next_actions = compute_recommended_actions(governance_gaps, len(blocked_relevant), len(timeline_candidates))

    payload: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_audit": str(audit_json),
        "source_blocked_review": str(blocked_json),
        "note": "Layer-5 case preparation summary. Complementary only; official gate outcomes are preserved.",
        "case_readiness": case_readiness,
        "top_evidence_files": top_evidence,
        "top_narrative_files": top_narrative,
        "blocked_but_relevant": blocked_relevant,
        "governance_gaps": governance_gaps,
        "timeline_candidates": timeline_candidates,
        "recommended_next_actions": next_actions,
    }

    if args.json_out or args.md_out:
        default_json, default_md = infer_default_output_paths(audit_json)
        json_out = Path(args.json_out).expanduser().resolve() if args.json_out else default_json
        md_out = Path(args.md_out).expanduser().resolve() if args.md_out else default_md
    else:
        json_out, md_out = infer_default_output_paths(audit_json)

    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_out.write_text(write_markdown(payload), encoding="utf-8")

    print(f"Source audit: {audit_json}")
    print(f"Source blocked review: {blocked_json}")
    print(f"Case readiness: {case_readiness}")
    print(f"JSON summary: {json_out}")
    print(f"Markdown summary: {md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
