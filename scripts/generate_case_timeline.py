#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
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


def compact_hits(values: Dict[str, Any], limit: int = 4) -> Dict[str, int]:
    pairs: List[Tuple[str, int]] = []
    for k, v in (values or {}).items():
        iv = to_int(v)
        if iv > 0:
            pairs.append((str(k), iv))
    pairs.sort(key=lambda p: (-p[1], p[0]))
    return {k: v for k, v in pairs[:limit]}


def timeline_signal_score(rec: Dict[str, Any]) -> float:
    signals = rec.get("key_signals") or {}
    gates = rec.get("gates") or {}

    dates = to_int(signals.get("dates_found", 0))
    currency = to_int(signals.get("currency_values_found", 0))
    pix = to_int(signals.get("pix_mentions", 0))
    evidence_hits = sum(to_int(v) for v in (signals.get("evidence_marker_hits") or {}).values())

    score = 0.0
    score += min(7.0, dates * 0.10)
    score += min(5.0, currency * 0.03)
    score += min(3.0, pix * 0.20)
    score += min(2.0, evidence_hits * 0.15)
    if str((gates.get("traceabilityCheck") or {}).get("status", "")).upper() == "PASS":
        score += 1.5
    return round(score, 4)


def detect_years_in_name(name: str) -> List[int]:
    years = set()
    for y in re.findall(r"(20\d{2})", name):
        iy = int(y)
        if 2000 <= iy <= 2099:
            years.add(iy)
    return sorted(years)


def classify_timeline_confidence(score: float, dates: int) -> str:
    if score >= 8.0 and dates >= 10:
        return "high"
    if score >= 4.0 and dates >= 2:
        return "medium"
    return "low"


def build_timeline_entries(audit: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
    acc_set = list(audit.get("accusation_set") or [])
    ranked = sorted(acc_set, key=timeline_signal_score, reverse=True)

    entries: List[Dict[str, Any]] = []
    for rec in ranked:
        signals = rec.get("key_signals") or {}
        dates = to_int(signals.get("dates_found", 0))
        currency = to_int(signals.get("currency_values_found", 0))
        pix = to_int(signals.get("pix_mentions", 0))
        if dates <= 0 and currency <= 0 and pix <= 0:
            continue

        score = timeline_signal_score(rec)
        file_name = str(rec.get("file_name", ""))
        entries.append(
            {
                "file_name": file_name,
                "file_path": rec.get("file_path"),
                "overall_outcome": rec.get("overall_outcome"),
                "timeline_signal_score": score,
                "timeline_confidence": classify_timeline_confidence(score, dates),
                "dates_found": dates,
                "currency_values_found": currency,
                "pix_mentions": pix,
                "traceability_status": ((rec.get("gates") or {}).get("traceabilityCheck") or {}).get("status"),
                "date_anchors_hint": detect_years_in_name(file_name),
                "evidence_marker_hits": compact_hits(signals.get("evidence_marker_hits") or {}),
                "target_entity_hits": compact_hits(signals.get("target_entity_hits") or {}),
            }
        )
        if len(entries) >= top_k:
            break
    return entries


def infer_chronology_bands(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    year_counter: Dict[int, int] = {}
    for e in entries:
        for y in e.get("date_anchors_hint") or []:
            year_counter[y] = year_counter.get(y, 0) + 1

    out = []
    for y, count in sorted(year_counter.items()):
        out.append({"year": y, "supporting_documents": count})
    return out


def compute_next_actions(entries: List[Dict[str, Any]]) -> List[str]:
    blocked_top = sum(1 for e in entries if "BLOCKED" in str(e.get("overall_outcome", "")).upper())
    low_conf = sum(1 for e in entries if str(e.get("timeline_confidence")) == "low")
    actions: List[str] = []

    if blocked_top:
        actions.append("Sanear metadados/governanca dos itens bloqueados com maior sinal temporal antes de montar narrativa final.")
    if low_conf:
        actions.append("Reforcar extracao de datas nos itens de baixa confianca com OCR/revisao humana para aumentar qualidade da linha do tempo.")
    actions.append("Validar manualmente os eventos-chave dos 5 primeiros itens antes de uso em peticao/relatorio.")
    return actions


def write_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Case Timeline")
    lines.append("")
    lines.append("- Camada adicional: linha do tempo automatica, sem alterar gates oficiais.")
    lines.append(f"- Source audit: `{payload.get('source_audit')}`")
    lines.append(f"- Generated at: `{payload.get('generated_at')}`")
    lines.append(f"- Timeline entries: `{len(payload.get('timeline_entries') or [])}`")
    lines.append("")

    lines.append("## Timeline Entries")
    lines.append("")
    for idx, e in enumerate(payload.get("timeline_entries") or [], start=1):
        lines.append(
            f"{idx}. `{e.get('file_name')}` | score={e.get('timeline_signal_score')} | conf={e.get('timeline_confidence')} | "
            f"outcome={e.get('overall_outcome')} | dates={e.get('dates_found')} | currency={e.get('currency_values_found')} | pix={e.get('pix_mentions')}"
        )
    lines.append("")

    lines.append("## Chronology Bands")
    lines.append("")
    bands = payload.get("chronology_bands") or []
    if not bands:
        lines.append("- Nenhuma ancora anual foi inferida por nome de arquivo.")
    else:
        for b in bands:
            lines.append(f"- {b.get('year')}: {b.get('supporting_documents')} documentos com ancora anual no nome")
    lines.append("")

    lines.append("## Recommended Next Actions")
    lines.append("")
    for a in payload.get("recommended_next_actions") or []:
        lines.append(f"- {a}")
    lines.append("")
    return "\n".join(lines)


def infer_default_output_paths(audit_json: Path) -> Tuple[Path, Path]:
    base = re.sub(r"_strict$", "", audit_json.stem)
    parent = audit_json.parent
    return (
        parent / f"{base}_timeline.json",
        parent / f"{base}_timeline.md",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate automatic case timeline from audit signals.")
    parser.add_argument("--audit-json", required=True, help="Official audit JSON path.")
    parser.add_argument("--json-out", default=None, help="Output timeline JSON.")
    parser.add_argument("--md-out", default=None, help="Output timeline Markdown.")
    parser.add_argument("--top-k", type=int, default=30, help="Maximum timeline entries.")
    args = parser.parse_args()

    audit_json = Path(args.audit_json).expanduser().resolve()
    if not audit_json.exists():
        raise SystemExit(f"Missing audit JSON: {audit_json}")

    audit = load_json(audit_json)
    entries = build_timeline_entries(audit, top_k=max(1, args.top_k))
    bands = infer_chronology_bands(entries)
    actions = compute_next_actions(entries)

    payload: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_audit": str(audit_json),
        "note": "Automatic timeline layer. Complementary only; official outcomes are preserved.",
        "timeline_entries": entries,
        "chronology_bands": bands,
        "recommended_next_actions": actions,
    }

    if args.json_out or args.md_out:
        def_json, def_md = infer_default_output_paths(audit_json)
        json_out = Path(args.json_out).expanduser().resolve() if args.json_out else def_json
        md_out = Path(args.md_out).expanduser().resolve() if args.md_out else def_md
    else:
        json_out, md_out = infer_default_output_paths(audit_json)

    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_out.write_text(write_markdown(payload), encoding="utf-8")

    print(f"Source audit: {audit_json}")
    print(f"Timeline JSON: {json_out}")
    print(f"Timeline Markdown: {md_out}")
    print(f"Timeline entries: {len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
