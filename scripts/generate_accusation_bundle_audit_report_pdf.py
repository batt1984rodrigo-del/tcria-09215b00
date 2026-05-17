#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def safe_text(value: Any) -> str:
    text = str(value)
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    return text.encode("latin-1", "replace").decode("latin-1")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def styles():
    s = getSampleStyleSheet()
    s.add(
        ParagraphStyle(
            name="TitleX",
            parent=s["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        )
    )
    s.add(
        ParagraphStyle(
            name="BodyX",
            parent=s["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
        )
    )
    s.add(
        ParagraphStyle(
            name="SubtleX",
            parent=s["BodyText"],
            fontName="Helvetica",
            fontSize=8.3,
            leading=10.5,
            textColor=colors.HexColor("#64748b"),
        )
    )
    s.add(
        ParagraphStyle(
            name="H2X",
            parent=s["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    s.add(
        ParagraphStyle(
            name="H3X",
            parent=s["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#111827"),
            spaceBefore=6,
            spaceAfter=3,
        )
    )
    return s


def build_kv(rows: List[List[str]], widths: List[float]) -> Table:
    t = Table(rows, colWidths=widths)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dbe2ea")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def outcome_color(value: str):
    v = (value or "").lower()
    if "blocked" in v:
        return colors.HexColor("#b91c1c")
    if "partial_pass" in v or "partial pass" in v:
        return colors.HexColor("#b45309")
    return colors.HexColor("#166534")


def gate_color(value: str):
    v = (value or "").upper()
    if v == "BLOCKED":
        return colors.HexColor("#b91c1c")
    if v == "PASS":
        return colors.HexColor("#166534")
    if v == "WARN":
        return colors.HexColor("#b45309")
    return colors.HexColor("#6b7280")


def build_summary_table(accusation_set: List[Dict[str, Any]]) -> Table:
    rows = [["Arquivo", "Chars", "Compliance", "Traceability", "Resultado"]]
    for rec in accusation_set:
        gates = rec.get("gates") or {}
        rows.append(
            [
                safe_text(rec["file_name"])[:40],
                str(rec.get("text_chars", 0)),
                safe_text((gates.get("complianceGate") or {}).get("status", "-")),
                safe_text((gates.get("traceabilityCheck") or {}).get("status", "-")),
                safe_text(rec.get("overall_outcome", "-"))[:52],
            ]
        )

    t = Table(rows, colWidths=[2.9 * inch, 0.75 * inch, 0.95 * inch, 1.0 * inch, 1.6 * inch], repeatRows=1)
    st = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
    )
    for i, rec in enumerate(accusation_set, start=1):
        st.add("TEXTCOLOR", (4, i), (4, i), outcome_color(rec.get("overall_outcome", "")))
        gates = rec.get("gates") or {}
        st.add("TEXTCOLOR", (2, i), (3, i), colors.HexColor("#334155"))
        if (gates.get("complianceGate") or {}).get("status") == "BLOCKED":
            st.add("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#b91c1c"))
    t.setStyle(st)
    return t


def on_page(c, doc):
    c.saveState()
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setLineWidth(0.5)
    c.line(doc.leftMargin, doc.pagesize[1] - doc.topMargin + 8, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - doc.topMargin + 8)
    c.line(doc.leftMargin, doc.bottomMargin - 10, doc.pagesize[0] - doc.rightMargin, doc.bottomMargin - 10)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(doc.leftMargin, doc.bottomMargin - 24, "TCR-IA accusation bundle audit report")
    c.drawRightString(doc.pagesize[0] - doc.rightMargin, doc.bottomMargin - 24, f"Page {doc.page}")
    c.restoreState()


def build_doc(payload: Dict[str, Any], out_path: Path, title: str):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=safe_text(title),
        author="OpenAI Codex",
    )
    s = styles()
    story: List[Any] = []

    accusation_set = payload.get("accusation_set", [])
    non_accusation_set = payload.get("non_accusation_set", [])
    counts = payload.get("classification_counts", {})
    generated = payload.get("generated_at", datetime.now().isoformat(timespec="seconds"))

    story.append(Paragraph(safe_text(title), s["TitleX"]))
    story.append(Paragraph("Relatorio gerado a partir da auditoria em lote usando gates do projeto (estilo TCR-IA).", s["BodyX"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Gerado em: {safe_text(generated)}", s["SubtleX"]))
    story.append(Paragraph(f"Modo de complianceGate: {safe_text(payload.get('compliance_gate_mode', 'default-heuristic'))}", s["SubtleX"]))
    story.append(Paragraph(f"Base: {safe_text(payload.get('audit_basis', '-'))}", s["SubtleX"]))
    story.append(Spacer(1, 8))

    overview_rows = [
        ["Arquivos varridos", str(payload.get("total_files_scanned", 0))],
        ["Conjunto acusatorio auditado", str(payload.get("accusation_set_count", 0))],
        ["Contagens de classificacao", safe_text(counts)],
        ["Nao-acusatorios (suporte/contexto)", str(len(non_accusation_set))],
    ]
    story.append(Paragraph("Resumo executivo", s["H2X"]))
    story.append(build_kv(overview_rows, [2.0 * inch, 4.8 * inch]))
    story.append(Spacer(1, 8))

    if accusation_set:
        blocked = sum(1 for x in accusation_set if "BLOCKED" in (x.get("overall_outcome") or ""))
        partial = sum(1 for x in accusation_set if "PARTIAL_PASS" in (x.get("overall_outcome") or ""))
        pass_count = sum(1 for x in accusation_set if x.get("overall_outcome") == "PASS")
        outcome_rows = [
            ["BLOCKED", str(blocked)],
            ["PARTIAL_PASS", str(partial)],
            ["PASS", str(pass_count)],
        ]
        story.append(build_kv(outcome_rows, [2.0 * inch, 1.0 * inch]))
        story.append(Spacer(1, 8))
        story.append(build_summary_table(accusation_set))
    else:
        story.append(Paragraph("Nenhum arquivo foi classificado como acusatorio neste pacote.", s["BodyX"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Observacoes", s["H2X"]))
    story.append(
        Paragraph(
            "- Auditoria de forma/documentacao textual; nao valida veracidade juridica/fatica.<br/>"
            "- maturityGate e ledger/hash/HMAC dependem de runtime e nao sao inferiveis de arquivos estaticos.<br/>"
            "- Arquivos sensiveis (ex.: senhas) podem ser excluidos de leitura de conteudo.",
            s["BodyX"],
        )
    )

    # Detail pages: accusation set only.
    for idx, rec in enumerate(accusation_set, start=1):
        story.append(PageBreak())
        story.append(Paragraph(f"{idx}. {safe_text(rec['file_name'])}", s["H3X"]))
        story.append(Paragraph(safe_text(", ".join(rec.get("classification_reasons") or [])) or "-", s["BodyX"]))
        story.append(Spacer(1, 6))

        meta_rows = [
            ["Caminho", safe_text(rec.get("file_path", "-"))],
            ["Tipo", safe_text(rec.get("suffix", "-"))],
            ["Tamanho (bytes)", str(rec.get("size_bytes", 0))],
            ["SHA256 (prefixo)", safe_text(rec.get("sha256", ""))[:20]],
            ["Extracao", f"{safe_text(rec.get('extraction_status','-'))} via {safe_text(rec.get('extraction_method','-'))}"],
            ["Texto extraido", f"{rec.get('text_chars', 0)} chars ({safe_text(rec.get('text_quality','-'))})"],
            ["Resultado geral", safe_text(rec.get("overall_outcome", "-"))],
        ]
        story.append(Paragraph("Metadados", s["H2X"]))
        story.append(build_kv(meta_rows, [1.7 * inch, 4.95 * inch]))
        story.append(Spacer(1, 8))

        gates = rec.get("gates") or {}
        gate_rows = [["Gate", "Status", "Motivo", "Evidencia"]]
        for gate_name in ["prescriptiveGate", "complianceGate", "traceabilityCheck", "maturityGate", "ledgerRuntimeCheck"]:
            g = gates.get(gate_name) or {}
            gate_rows.append(
                [
                    safe_text(gate_name),
                    safe_text(g.get("status", "-")),
                    safe_text(g.get("reason", "-")),
                    safe_text(g.get("evidence", "-") or "-"),
                ]
            )
        gt = Table(gate_rows, colWidths=[1.2 * inch, 0.95 * inch, 2.5 * inch, 2.0 * inch], repeatRows=1)
        gts = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.4),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dbe2ea")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
        for r in range(1, len(gate_rows)):
            gts.add("TEXTCOLOR", (1, r), (1, r), gate_color(gate_rows[r][1]))
        gt.setStyle(gts)
        story.append(Paragraph("Gates", s["H2X"]))
        story.append(gt)
        story.append(Spacer(1, 8))

        ks = rec.get("key_signals") or {}
        signal_rows = [
            ["dates_found", str(ks.get("dates_found", 0))],
            ["currency_values_found", str(ks.get("currency_values_found", 0))],
            ["pix_mentions", str(ks.get("pix_mentions", 0))],
            ["email_mentions", str(ks.get("email_mentions", 0))],
            ["contains_objetivo_label", str(ks.get("contains_objetivo_label", False))],
            ["contains_autor_label", str(ks.get("contains_autor_label", False))],
            ["contains_summary_label", str(ks.get("contains_summary_label", False))],
        ]
        story.append(Paragraph("Sinais principais", s["H2X"]))
        story.append(build_kv(signal_rows, [2.2 * inch, 1.6 * inch]))
        story.append(Spacer(1, 4))

        acc_kw = ks.get("accusation_keyword_hits", {}) or {}
        ev_kw = ks.get("evidence_marker_hits", {}) or {}
        tgt_kw = ks.get("target_entity_hits", {}) or {}
        story.append(Paragraph(f"Accusation keywords: {safe_text(acc_kw)}", s["SubtleX"]))
        story.append(Paragraph(f"Evidence markers: {safe_text(ev_kw)}", s["SubtleX"]))
        story.append(Paragraph(f"Target entities: {safe_text(tgt_kw)}", s["SubtleX"]))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def validate_pdf(path: Path):
    reader = PdfReader(str(path))
    if len(reader.pages) < 1:
        raise RuntimeError("Generated PDF has no pages.")
    text = "\n".join((p.extract_text() or "") for p in reader.pages[:2])
    if "Resumo executivo" not in text:
        raise RuntimeError("Generated PDF missing expected summary heading.")
    return len(reader.pages)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PDF report from accusation-bundle audit JSON.")
    parser.add_argument("--input", required=True, help="Path to audit JSON")
    parser.add_argument("--output", required=True, help="Path to output PDF")
    parser.add_argument("--title", default="Nova Auditoria - Conjunto de Arquivos que Levantam Acusacao")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    payload = load_json(input_path)
    build_doc(payload, output_path, args.title)
    pages = validate_pdf(output_path)
    print(f"PDF report: {output_path}")
    print(f"Pages: {pages}")
    print("Validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
