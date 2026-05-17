#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pypdf import PdfReader


WORKSPACE = Path("/Users/rodrigobaptistadasilva/Documents/New project")
OUTPUT_DIR = WORKSPACE / "output" / "audit"
JSON_OUT = OUTPUT_DIR / "tcr_gateway_pdf_audit_results.json"
MD_OUT = OUTPUT_DIR / "tcr_gateway_pdf_audit_results.md"

FILES = [
    Path("/Users/rodrigobaptistadasilva/Downloads/Arquivos.pdf"),
    Path("/Users/rodrigobaptistadasilva/Downloads/Dossie_Fraude_Bradesco.pdf"),
    Path("/Users/rodrigobaptistadasilva/Downloads/Cópia de 📘 Dossiê Ampliado — Caso Vinícius Carvalho.pdf"),
]

# From the project RTF.
PRESCRIPTIVE_PATTERNS = [
    "você deve",
    "deve-se",
    "é obrigatório",
    "é necessario",
    "é necessário",
    "a única solução é",
]

RISK_KEYWORDS = [
    "fraude",
    "risco",
    "bloqueio",
    "prejuízo",
    "ressarcimento",
    "invasão",
    "não autorizado",
    "omissão",
    "dano",
    "auditoria",
]


@dataclass
class GateResult:
    status: str
    reason: str
    evidence: Optional[str] = None


@dataclass
class FileAuditResult:
    file_name: str
    file_path: str
    pages: int
    extractable_text_chars: int
    text_extraction_quality: str
    content_type_guess: str
    key_signals: Dict[str, object]
    gates: Dict[str, Dict[str, object]]
    overall_outcome: str
    summary: str
    caveats: List[str]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def to_lower(text: str) -> str:
    return normalize(text).lower()


def extract_pdf_text(pdf_path: Path) -> Tuple[str, int, List[int]]:
    reader = PdfReader(str(pdf_path))
    page_lengths: List[int] = []
    texts: List[str] = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        page_lengths.append(len(t))
        if t:
            texts.append(t)
    return "\n".join(texts), len(reader.pages), page_lengths


def classify_extraction_quality(chars: int, pages: int) -> str:
    if pages == 0:
        return "no-pages"
    avg = chars / pages
    if avg >= 800:
        return "high"
    if avg >= 250:
        return "medium"
    if avg > 0:
        return "low"
    return "none"


def guess_content_type(text_l: str) -> str:
    if "dossiê" in text_l or "dossie" in text_l:
        return "case_dossier_or_report"
    if "fatura" in text_l and "lançamento" in text_l:
        return "financial_statement_or_invoice_records"
    return "unknown_document"


def detect_prescriptive(text_l: str) -> GateResult:
    hits = [p for p in PRESCRIPTIVE_PATTERNS if p in text_l]
    if hits:
        return GateResult(
            status="BLOCKED",
            reason="Prescriptive language detected by compliance layer.",
            evidence=", ".join(hits[:5]),
        )
    return GateResult(
        status="PASS",
        reason="No project-defined prescriptive patterns detected in extracted text.",
    )


def detect_declared_purpose(text: str, text_l: str) -> Tuple[bool, Optional[str]]:
    patterns = [
        r"\bobjetivo\s*:\s*([^\n]{0,160})",
        r"\bfinalidade\s*:\s*([^\n]{0,160})",
        r"\b(?:este|essa|o presente)\s+(?:documento|dossi[eê])\s+visa\s+([^\n]{0,180})",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            snippet = normalize(m.group(0))[:180]
            return True, snippet
    return False, None


def detect_responsible_actor(text: str, text_l: str) -> Tuple[bool, Optional[str]]:
    label_patterns = [
        r"\brespons[áa]vel(?:\s+humano)?\s*:\s*([^\n]{1,120})",
        r"\bautor\s*:\s*([^\n]{1,120})",
        r"\bassinado por\s*:\s*([^\n]{1,120})",
    ]
    for pat in label_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return True, normalize(m.group(0))[:140]

    # Heuristic fallback: detect common personal-name phrases in context.
    name_hits = re.findall(r"\bRodrigo Baptista da Silva\b|\bVin[ií]cius Carvalho\b", text, flags=re.IGNORECASE)
    if name_hits:
        return True, "Named individual(s) found in document body (heuristic, not explicit responsibility field)."
    return False, None


def detect_explicit_approval(text: str, text_l: str) -> Tuple[bool, Optional[str]]:
    approval_patterns = [
        r"\baprovad[oa]\b",
        r"\baprova[cç][aã]o\b",
        r"\bassinatura\b",
        r"\bassinado\b",
    ]
    for pat in approval_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return True, normalize(m.group(0))
    return False, None


def compliance_gate(text: str) -> GateResult:
    text_l = to_lower(text)
    has_actor, actor_ev = detect_responsible_actor(text, text_l)
    has_purpose, purpose_ev = detect_declared_purpose(text, text_l)
    has_approval, approval_ev = detect_explicit_approval(text, text_l)

    missing = []
    if not has_actor:
        missing.append("responsibleHuman")
    if not has_purpose:
        missing.append("declaredPurpose")
    if not has_approval:
        missing.append("approved")

    evidence_parts = []
    if actor_ev:
        evidence_parts.append(f"actor={actor_ev}")
    if purpose_ev:
        evidence_parts.append(f"purpose={purpose_ev}")
    if approval_ev:
        evidence_parts.append(f"approval={approval_ev}")
    evidence = " | ".join(evidence_parts) if evidence_parts else None

    if missing:
        return GateResult(
            status="BLOCKED",
            reason=f"DecisionRecord incomplete (missing {', '.join(missing)}).",
            evidence=evidence,
        )
    return GateResult(
        status="PASS",
        reason="Heuristic check found actor, purpose, and approval indicators in document text.",
        evidence=evidence,
    )


def maturity_gate() -> GateResult:
    return GateResult(
        status="NOT_EVALUATED",
        reason="KnowledgeCore.maturityScore is not present in PDF content and no repo runtime was provided.",
    )


def ledger_persistence_check() -> GateResult:
    return GateResult(
        status="NOT_APPLICABLE",
        reason="Static PDFs do not provide runtime ledger append events (LLM_RETURNED / DECISION_APPROVED / POSTCHECK_BLOCKED).",
    )


def gather_signals(text: str) -> Dict[str, object]:
    text_l = to_lower(text)
    risk_counts = {kw: text_l.count(kw) for kw in RISK_KEYWORDS}
    risk_counts = {k: v for k, v in risk_counts.items() if v > 0}

    currency_hits = re.findall(r"R\$\s*[\d\.,]+", text)
    dates_numeric = re.findall(r"\b\d{2}/\d{2}/\d{4}\b", text)
    pix_mentions = len(re.findall(r"\bpix\b", text_l))
    timeline_markers = len(re.findall(r"\b\d{2}/\d{2}/\d{4}\b\s*[–-]", text))

    return {
        "risk_keyword_hits": risk_counts,
        "currency_values_found": len(currency_hits),
        "date_values_found": len(dates_numeric),
        "pix_mentions": pix_mentions,
        "timeline_markers": timeline_markers,
        "contains_objective_label": bool(re.search(r"\bobjetivo\s*:", text, flags=re.IGNORECASE)),
        "contains_summary_label": bool(re.search(r"\bresumo\b", text, flags=re.IGNORECASE)),
    }


def build_summary(file_name: str, content_type: str, prescriptive: GateResult, compliance: GateResult) -> str:
    base = []
    if content_type == "financial_statement_or_invoice_records":
        base.append("Documento parece ser extrato/fatura com alta densidade transacional.")
    elif content_type == "case_dossier_or_report":
        base.append("Documento parece dossiê narrativo/estruturado de caso.")
    else:
        base.append("Tipo documental não classificado com alta confiança.")

    if prescriptive.status == "PASS":
        base.append("Sem linguagem prescritiva bloqueante pelos padrões do projeto.")
    else:
        base.append("Bloqueado por linguagem prescritiva.")

    if compliance.status == "PASS":
        base.append("Tem sinais heurísticos de DecisionRecord (ator/finalidade/aprovação).")
    else:
        base.append("Não atende integralmente ao gate de responsabilidade humana em formato verificável.")

    return " ".join(base)


def audit_file(pdf_path: Path) -> FileAuditResult:
    text, pages, page_lengths = extract_pdf_text(pdf_path)
    text_l = to_lower(text)
    chars = len(text)
    quality = classify_extraction_quality(chars, pages)
    content_type = guess_content_type(text_l)

    prescriptive = detect_prescriptive(text_l)
    maturity = maturity_gate()
    compliance = compliance_gate(text)
    ledger = ledger_persistence_check()
    signals = gather_signals(text)
    signals["page_text_lengths"] = page_lengths

    # "processOutputPersisted" style overall approximation:
    # prescriptive + compliance are blocking; maturity is unavailable (not evaluated).
    if prescriptive.status == "BLOCKED":
        overall = "BLOCKED (prescriptiveGate)"
    elif compliance.status == "BLOCKED":
        overall = "BLOCKED (complianceGate)"
    else:
        overall = "PARTIAL_PASS (static document only; maturity/ledger runtime not evaluated)"

    caveats = [
        "This is a document-content audit using project gate concepts, not a legal/factual verification of claims.",
        "PDF text extraction may omit images, scans, signatures, or formatting evidence.",
        "maturityGate cannot be evaluated from static PDFs because KnowledgeCore metadata is absent.",
        "Ledger/hash/HMAC checks are runtime/system controls and are not inferable from document text alone.",
    ]

    return FileAuditResult(
        file_name=pdf_path.name,
        file_path=str(pdf_path),
        pages=pages,
        extractable_text_chars=chars,
        text_extraction_quality=quality,
        content_type_guess=content_type,
        key_signals=signals,
        gates={
            "prescriptiveGate": asdict(prescriptive),
            "maturityGate": asdict(maturity),
            "complianceGate": asdict(compliance),
            "ledgerRuntimeCheck": asdict(ledger),
        },
        overall_outcome=overall,
        summary=build_summary(pdf_path.name, content_type, prescriptive, compliance),
        caveats=caveats,
    )


def write_markdown(results: List[FileAuditResult]) -> str:
    lines: List[str] = []
    lines.append("# TCR-IA-style PDF Audit Results")
    lines.append("")
    lines.append("Audit basis: project gates (prescriptive language, human responsibility) adapted to static PDF content.")
    lines.append("")
    lines.append("Important: this is not legal verification of factual claims.")
    lines.append("")

    for r in results:
        lines.append(f"## {r.file_name}")
        lines.append("")
        lines.append(f"- Path: `{r.file_path}`")
        lines.append(f"- Pages: {r.pages}")
        lines.append(f"- Extractable text chars: {r.extractable_text_chars}")
        lines.append(f"- Text extraction quality: `{r.text_extraction_quality}`")
        lines.append(f"- Content type guess: `{r.content_type_guess}`")
        lines.append(f"- Overall outcome: `{r.overall_outcome}`")
        lines.append(f"- Summary: {r.summary}")
        lines.append("")
        lines.append("### Gate results")
        for gate_name, gate in r.gates.items():
            ev = gate.get("evidence")
            lines.append(f"- `{gate_name}`: `{gate['status']}` - {gate['reason']}")
            if ev:
                lines.append(f"  Evidence: {ev}")
        lines.append("")
        lines.append("### Key signals")
        signals = r.key_signals
        lines.append(f"- Currency values found: {signals['currency_values_found']}")
        lines.append(f"- Date values found: {signals['date_values_found']}")
        lines.append(f"- PIX mentions: {signals['pix_mentions']}")
        lines.append(f"- Timeline markers: {signals['timeline_markers']}")
        lines.append(f"- Contains `Objetivo:` label: {signals['contains_objective_label']}")
        lines.append(f"- Contains `Resumo` label: {signals['contains_summary_label']}")
        lines.append(f"- Risk keyword hits: {signals['risk_keyword_hits']}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    missing = [str(f) for f in FILES if not f.exists()]
    if missing:
        raise SystemExit(f"Missing input files: {missing}")

    results = [audit_file(f) for f in FILES]
    JSON_OUT.write_text(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2), encoding="utf-8")
    MD_OUT.write_text(write_markdown(results), encoding="utf-8")

    print(f"JSON report: {JSON_OUT}")
    print(f"Markdown report: {MD_OUT}")
    for r in results:
        print(f"- {r.file_name}: {r.overall_outcome}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
