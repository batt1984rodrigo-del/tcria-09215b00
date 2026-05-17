#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


WORKSPACE = Path("/Users/rodrigobaptistadasilva/Documents/New project")
INPUT_JSON = WORKSPACE / "output" / "audit" / "tcr_gateway_pdf_audit_results.json"
OUTPUT_PDF = WORKSPACE / "output" / "audit" / "tcr_gateway_pdf_audit_report.pdf"


def safe_pdf_text(value: Any) -> str:
    text = str(value)
    # Keep Portuguese accents; replace unsupported characters (e.g., emoji).
    text = text.encode("latin-1", "replace").decode("latin-1")
    # Normalize long dashes to ASCII hyphen to avoid glyph/render inconsistencies.
    return text.replace("\u2014", "-").replace("\u2013", "-")


def load_results() -> List[Dict[str, Any]]:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Audit JSON not found: {INPUT_JSON}")
    return json.loads(INPUT_JSON.read_text(encoding="utf-8"))


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subtle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="FileHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.black,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MonoSmall",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
        )
    )
    return styles


def outcome_color(outcome: str):
    out = outcome.lower()
    if "blocked" in out:
        return colors.HexColor("#b91c1c")
    if "partial_pass" in out or "partial pass" in out:
        return colors.HexColor("#b45309")
    return colors.HexColor("#166534")


def gate_status_color(status: str):
    s = (status or "").upper()
    if s == "BLOCKED":
        return colors.HexColor("#b91c1c")
    if s in {"NOT_EVALUATED", "NOT_APPLICABLE"}:
        return colors.HexColor("#6b7280")
    return colors.HexColor("#166534")


def artifact_identity_line(item: Dict[str, Any]) -> str:
    identity = item.get("artifact_identity") or {}
    file_sha = identity.get("file_sha256") or item.get("sha256") or "-"
    engine = identity.get("engine") or item.get("engine") or "tcria"
    engine_version = identity.get("engine_version") or item.get("engine_version") or "unknown"
    policy = identity.get("gate_policy_version") or item.get("gate_policy_version") or "unknown"
    return f"Identity: sha256={safe_pdf_text(str(file_sha)[:16])}..., engine={safe_pdf_text(engine)}@{safe_pdf_text(engine_version)}, policy={safe_pdf_text(policy)}"


def build_summary_table(results: List[Dict[str, Any]]) -> Table:
    rows = [["Arquivo", "Pags", "Tipo", "Prescriptive", "Compliance", "Resultado"]]
    for item in results:
        rows.append(
            [
                safe_pdf_text(item["file_name"])[:40],
                str(item["pages"]),
                safe_pdf_text(item["content_type_guess"]),
                safe_pdf_text(item["gates"]["prescriptiveGate"]["status"]),
                safe_pdf_text(item["gates"]["complianceGate"]["status"]),
                safe_pdf_text(item["overall_outcome"])[:52],
            ]
        )

    col_widths = [2.45 * inch, 0.45 * inch, 1.8 * inch, 0.9 * inch, 0.9 * inch, 1.7 * inch]
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
    )
    for idx, item in enumerate(results, start=1):
        style.add("TEXTCOLOR", (5, idx), (5, idx), outcome_color(item["overall_outcome"]))
        style.add("TEXTCOLOR", (3, idx), (4, idx), colors.HexColor("#334155"))
    table.setStyle(style)
    return table


def build_kv_table(rows: List[List[str]], col_widths: List[float]) -> Table:
    table = Table(rows, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dbe2ea")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setStrokeColor(colors.HexColor("#e2e8f0"))
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(doc.leftMargin, doc.height + doc.topMargin + 8, doc.pagesize[0] - doc.rightMargin, doc.height + doc.topMargin + 8)
    canvas_obj.line(doc.leftMargin, doc.bottomMargin - 10, doc.pagesize[0] - doc.rightMargin, doc.bottomMargin - 10)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#64748b"))
    canvas_obj.drawString(doc.leftMargin, doc.bottomMargin - 24, "TCR-IA-style PDF Audit Report")
    canvas_obj.drawRightString(doc.pagesize[0] - doc.rightMargin, doc.bottomMargin - 24, f"Page {doc.page}")
    canvas_obj.restoreState()


def build_report(results: List[Dict[str, Any]]):
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="TCR-IA-style PDF Audit Report",
        author="OpenAI Codex",
    )
    styles = make_styles()
    story = []

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocked = sum(1 for r in results if "BLOCKED" in r["overall_outcome"])
    partial = sum(1 for r in results if "PARTIAL_PASS" in r["overall_outcome"])
    passed = sum(1 for r in results if r["overall_outcome"] == "PASS")

    story.append(Paragraph("TCR-IA-style PDF Audit Report", styles["TitleCustom"]))
    story.append(Paragraph("Auditoria de PDFs usando conceitos de gates do projeto (prescriptive/compliance) em documentos estaticos.", styles["BodySmall"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Gerado em: {generated_at}", styles["Subtle"]))
    story.append(Paragraph(f"Escopo: {len(results)} arquivos PDF fornecidos pelo usuario.", styles["Subtle"]))
    story.append(Spacer(1, 10))

    overview_rows = [
        ["Total de arquivos", str(len(results))],
        ["BLOCKED", str(blocked)],
        ["PARTIAL_PASS", str(partial)],
        ["PASS", str(passed)],
        ["Modelo aplicado", "prescriptiveGate + complianceGate (heuristico); maturity/ledger nao avaliaveis em PDF estatico"],
    ]
    story.append(Paragraph("Resumo executivo", styles["Section"]))
    story.append(build_kv_table(overview_rows, [1.9 * inch, 4.7 * inch]))
    story.append(Spacer(1, 10))
    story.append(build_summary_table(results))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Limites da auditoria", styles["Section"]))
    story.append(Paragraph("- Nao verifica a veracidade juridica/fatica das alegacoes.<br/>- Baseada em texto extraido; imagens/OCR/assinaturas podem nao aparecer.<br/>- maturityGate e controles de ledger/hash/HMAC sao de runtime e nao inferiveis de PDF estatico.", styles["BodySmall"]))

    for index, item in enumerate(results, start=1):
        story.append(PageBreak())
        file_name = safe_pdf_text(item["file_name"])
        story.append(Paragraph(f"{index}. {file_name}", styles["FileHeading"]))
        story.append(Paragraph(safe_pdf_text(item["summary"]), styles["BodySmall"]))
        story.append(Spacer(1, 6))

        meta_rows = [
            ["Caminho", safe_pdf_text(item["file_path"])],
            ["Paginas", str(item["pages"])],
            ["Chars extraidos", str(item["extractable_text_chars"])],
            ["Qualidade extracao", safe_pdf_text(item["text_extraction_quality"])],
            ["Tipo (heuristica)", safe_pdf_text(item["content_type_guess"])],
            ["Resultado geral", safe_pdf_text(item["overall_outcome"])],
        ]
        story.append(Paragraph("Metadados e classificacao", styles["Section"]))
        story.append(build_kv_table(meta_rows, [1.6 * inch, 5.0 * inch]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(artifact_identity_line(item), styles["BodySmall"]))
        story.append(Spacer(1, 6))

        gate_rows = [["Gate", "Status", "Motivo", "Evidencia"]]
        for gate_name in ["prescriptiveGate", "maturityGate", "complianceGate", "ledgerRuntimeCheck"]:
            gate = item["gates"][gate_name]
            gate_rows.append(
                [
                    safe_pdf_text(gate_name),
                    safe_pdf_text(gate["status"]),
                    safe_pdf_text(gate["reason"]),
                    safe_pdf_text(gate.get("evidence") or "-"),
                ]
            )
        gate_table = Table(gate_rows, colWidths=[1.2 * inch, 0.9 * inch, 2.4 * inch, 2.1 * inch], repeatRows=1)
        gate_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.8),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dbe2ea")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
        for row_idx in range(1, len(gate_rows)):
            status_val = gate_rows[row_idx][1]
            gate_style.add("TEXTCOLOR", (1, row_idx), (1, row_idx), gate_status_color(status_val))
        gate_table.setStyle(gate_style)
        story.append(Paragraph("Resultados dos gates", styles["Section"]))
        story.append(gate_table)
        story.append(Spacer(1, 8))

        ks = item["key_signals"]
        signals_rows = [
            ["Valores monetarios (R$)", str(ks.get("currency_values_found", 0))],
            ["Datas detectadas", str(ks.get("date_values_found", 0))],
            ["PIX (mentions)", str(ks.get("pix_mentions", 0))],
            ["Marcadores de timeline", str(ks.get("timeline_markers", 0))],
            ["Contem 'Objetivo:'", str(ks.get("contains_objective_label", False))],
            ["Contem 'Resumo'", str(ks.get("contains_summary_label", False))],
        ]
        story.append(Paragraph("Sinais extraidos", styles["Section"]))
        story.append(build_kv_table(signals_rows, [2.1 * inch, 4.5 * inch]))
        story.append(Spacer(1, 6))

        risk_hits = ks.get("risk_keyword_hits", {}) or {}
        if risk_hits:
            risk_text = ", ".join(f"{safe_pdf_text(k)}={v}" for k, v in sorted(risk_hits.items()))
        else:
            risk_text = "Nenhum termo-chave de risco do conjunto configurado foi encontrado."
        story.append(Paragraph(f"Termos de risco (heuristica): {safe_pdf_text(risk_text)}", styles["BodySmall"]))
        story.append(Spacer(1, 6))

        caveats = item.get("caveats", [])
        if caveats:
            caveat_html = "<br/>".join(f"- {safe_pdf_text(c)}" for c in caveats[:4])
            story.append(Paragraph("Caveats", styles["Section"]))
            story.append(Paragraph(caveat_html, styles["BodySmall"]))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def validate_report() -> int:
    reader = PdfReader(str(OUTPUT_PDF))
    page_count = len(reader.pages)
    extracted = "\n".join((p.extract_text() or "") for p in reader.pages[:2])
    required = ["TCR-IA-style PDF Audit Report", "Resumo executivo"]
    missing = [s for s in required if s not in extracted]
    if missing:
        raise RuntimeError(f"Generated report is missing expected text: {missing}")
    return page_count


def main() -> int:
    results = load_results()
    build_report(results)
    pages = validate_report()
    print(f"PDF report: {OUTPUT_PDF}")
    print(f"Pages: {pages}")
    print("Validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
