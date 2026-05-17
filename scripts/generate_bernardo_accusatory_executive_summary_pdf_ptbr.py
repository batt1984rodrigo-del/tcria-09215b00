import json
from collections import Counter
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


INPUT_JSON = Path(
    "/Users/rodrigobaptistadasilva/Documents/New project/output/audit/"
    "tcr_gateway_bernardo_notion_test_audit_with_images_strict.json"
)
OUTPUT_PDF = Path(
    "/Users/rodrigobaptistadasilva/Documents/New project/output/audit/"
    "tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_1pagina_ptbr.pdf"
)


def pct(part: int, total: int) -> str:
    return f"{(100 * part / total):.1f}%" if total else "0.0%"


def fit_line(c: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> str:
    if stringWidth(text, font, size) <= max_width:
        return text
    ell = "..."
    while text and stringWidth(text + ell, font, size) > max_width:
        text = text[:-1]
    return text + ell


def draw_section_title(c, x, y, text, width):
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(x, y, text)
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(0.7)
    c.line(x, y - 3, x + width, y - 3)
    return y - 16


def bullet_list(c, x, y, width, items, font_size=8.5, leading=10.5):
    c.setFont("Helvetica", font_size)
    c.setFillColor(colors.HexColor("#111827"))
    for item in items:
        if y < 52:
            break
        line = fit_line(c, item, "Helvetica", font_size, width - 10)
        c.drawString(x, y, "-")
        c.drawString(x + 8, y, line)
        y -= leading
    return y


def main():
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    acc = data.get("accusation_set", [])
    total = len(acc)
    total_scanned = data.get("total_files_scanned", 0)

    outcome_counts = Counter(r.get("overall_outcome", "UNKNOWN") for r in acc)
    artifact_counts = Counter(r.get("artifact_type", "UNKNOWN") for r in acc)
    gate_status = {"prescriptiveGate": Counter(), "complianceGate": Counter(), "traceabilityCheck": Counter()}
    block_reasons = Counter()
    suffix_counts = Counter((r.get("suffix") or "").lower() for r in acc)

    all_items = data.get("accusation_set", []) + data.get("non_accusation_set", [])
    image_total = 0
    image_ocr_ok = 0
    for r in all_items:
        if (r.get("suffix") or "").lower() in {".png", ".jpg", ".jpeg", ".heic"}:
            image_total += 1
            if r.get("extraction_status") == "ok":
                image_ocr_ok += 1

    for r in acc:
        gates = r.get("gates") or {}
        for g in gate_status:
            gate_status[g][(gates.get(g) or {}).get("status", "UNKNOWN")] += 1
        for g in ("prescriptiveGate", "complianceGate"):
            gd = gates.get(g) or {}
            if gd.get("status") in {"BLOCKED", "FAIL"}:
                block_reasons[gd.get("reason", "Motivo nao informado")] += 1

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=letter)
    width, height = letter
    margin = 36

    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#ecfeff"))
    c.rect(margin, height - 88, width - 2 * margin, 52, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 14.5)
    c.setFillColor(colors.HexColor("#083344"))
    c.drawString(margin + 10, height - 58, "Resumo Executivo (1 pagina) - Arquivos Acusatorios (Strict + OCR)")
    c.setFont("Helvetica", 8.2)
    c.setFillColor(colors.HexColor("#334155"))
    subtitle = (
        f"Base: {INPUT_JSON.name} | Politica: compliance por tipo de artefato "
        f"(DECISION bloqueante / ANALYTICAL com aviso de responsabilidade)"
    )
    c.drawString(margin + 10, height - 73, fit_line(c, subtitle, "Helvetica", 8.2, width - 2 * margin - 20))

    left_w = (width - 2 * margin) * 0.58
    gap = 18
    left_x = margin
    right_x = left_x + left_w + gap
    right_w = width - margin - right_x
    y_left = height - 105
    y_right = height - 105

    y_left = draw_section_title(c, left_x, y_left, "Quadro Geral", left_w)
    y_left = bullet_list(
        c,
        left_x,
        y_left,
        left_w,
        [
            f"Arquivos varridos no lote: {total_scanned}",
            f"Arquivos acusatorios auditados: {total} ({pct(total, total_scanned)})",
            f"Imagens no lote: {image_total} | OCR com sucesso: {image_ocr_ok}",
            "Auditoria estatica: maturityGate e ledger runtime nao sao avaliaveis em arquivos.",
        ],
    )

    y_left -= 2
    y_left = draw_section_title(c, left_x, y_left, "Resultado dos 92 Arquivos Acusatorios", left_w)
    outcome_order = [
        "BLOCKED (complianceGate)",
        "BLOCKED (prescriptiveGate)",
        "PARTIAL_PASS (traceability warning; static audit)",
        "PARTIAL_PASS (static document audit; maturity/ledger not evaluated)",
    ]
    outcome_lines = []
    for k in outcome_order:
        v = outcome_counts.get(k, 0)
        if v:
            label = (
                "Bloqueado por complianceGate" if "complianceGate" in k else
                "Bloqueado por prescriptiveGate" if "prescriptiveGate" in k else
                "Aprovacao parcial (rastreabilidade em aviso)" if "traceability" in k else
                "Aprovacao parcial (auditoria estatica)"
            )
            outcome_lines.append(f"{v} ({pct(v, total)}) - {label}")
    y_left = bullet_list(c, left_x, y_left, left_w, outcome_lines, font_size=8.35, leading=10.2)

    y_left -= 2
    y_left = draw_section_title(c, left_x, y_left, "Status dos Gates (Acusatorios)", left_w)
    gate_lines = [
        f"prescriptiveGate: PASS={gate_status['prescriptiveGate'].get('PASS',0)} | BLOCKED={gate_status['prescriptiveGate'].get('BLOCKED',0)}",
        f"complianceGate: BLOCKED={gate_status['complianceGate'].get('BLOCKED',0)} | WARN={gate_status['complianceGate'].get('WARN',0)} | PASS={gate_status['complianceGate'].get('PASS',0)}",
        f"traceabilityCheck: PASS={gate_status['traceabilityCheck'].get('PASS',0)} | WARN={gate_status['traceabilityCheck'].get('WARN',0)}",
    ]
    y_left = bullet_list(c, left_x, y_left, left_w, gate_lines)

    y_left -= 2
    y_left = draw_section_title(c, left_x, y_left, "Tipos de Artefato (Acusatorios)", left_w)
    y_left = bullet_list(
        c,
        left_x,
        y_left,
        left_w,
        [
            f"ANALYTICAL_ARTIFACT: {artifact_counts.get('ANALYTICAL_ARTIFACT',0)}",
            f"DECISION_ARTIFACT: {artifact_counts.get('DECISION_ARTIFACT',0)}",
            "ANALYTICAL: ausencia de responsibleHuman gera WARN (nao bloqueia).",
            "DECISION: complianceGate permanece bloqueante.",
        ],
        font_size=8.25,
        leading=10.0,
    )

    y_right = draw_section_title(c, right_x, y_right, "Principais Motivos de Bloqueio", right_w)
    top_reasons = [f"{n}x {motivo}" for motivo, n in block_reasons.most_common(6)]
    y_right = bullet_list(c, right_x, y_right, right_w, top_reasons or ["Sem bloqueios registrados."])

    y_right -= 2
    y_right = draw_section_title(c, right_x, y_right, "Composicao dos Arquivos Acusatorios", right_w)
    y_right = bullet_list(
        c,
        right_x,
        y_right,
        right_w,
        [f"{suf or '[sem sufixo]'}: {n}" for suf, n in suffix_counts.most_common(8)],
    )

    y_right -= 2
    y_right = draw_section_title(c, right_x, y_right, "Leitura Juridico-Operacional", right_w)
    y_right = bullet_list(
        c,
        right_x,
        y_right,
        right_w,
        [
            "A nova politica reduziu bloqueios formais em artefatos analiticos, preservando rastreabilidade para triagem.",
            "Os bloqueios remanescentes concentram-se em artefatos classificados como decisorios sem campos formais completos.",
            "O lote esta apto para fluxo de saneamento documental por arquivo (CSV de 92 motivos).",
        ],
        font_size=8.2,
        leading=10.0,
    )

    y_right -= 2
    y_right = draw_section_title(c, right_x, y_right, "Proximos Passos Recomendados", right_w)
    y_right = bullet_list(
        c,
        right_x,
        y_right,
        right_w,
        [
            "Priorizar os 38 DECISION_ARTIFACT bloqueados para completar responsibleHuman, finalidade e aprovacao.",
            "Usar o CSV de 92 motivos como checklist de regularizacao e protocolo.",
            "Manter OCR ativo no pipeline para consolidacoes futuras de imagens/screenshots.",
        ],
        font_size=8.1,
        leading=9.8,
    )

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(margin, 34, width - margin, 34)
    c.setFont("Helvetica", 7.6)
    c.setFillColor(colors.HexColor("#475569"))
    rodape = "Resumo executivo automatico gerado a partir do JSON consolidado da auditoria TCR-IA (strict + OCR)."
    c.drawString(margin, 22, fit_line(c, rodape, "Helvetica", 7.6, width - 2 * margin))

    c.save()
    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
