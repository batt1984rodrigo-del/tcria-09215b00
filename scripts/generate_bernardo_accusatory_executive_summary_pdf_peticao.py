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
    "tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_peticao_ready_1pagina.pdf"
)


def pct(part: int, total: int) -> str:
    return f"{(100 * part / total):.1f}%" if total else "0.0%"


def fit(c: canvas.Canvas, text: str, font: str, size: float, max_w: float) -> str:
    if stringWidth(text, font, size) <= max_w:
        return text
    ell = "..."
    while text and stringWidth(text + ell, font, size) > max_w:
        text = text[:-1]
    return text + ell


def section(c, x, y, w, title):
    c.setFont("Helvetica-Bold", 10.2)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(x, y, title)
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(0.6)
    c.line(x, y - 3, x + w, y - 3)
    return y - 15


def bullets(c, x, y, w, items, size=8.0, lead=9.7):
    c.setFont("Helvetica", size)
    c.setFillColor(colors.HexColor("#111827"))
    for item in items:
        if y < 52:
            break
        c.drawString(x, y, "-")
        c.drawString(x + 8, y, fit(c, item, "Helvetica", size, w - 10))
        y -= lead
    return y


def main():
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    acc = data.get("accusation_set", [])
    non = data.get("non_accusation_set", [])
    total = len(acc)
    total_scanned = int(data.get("total_files_scanned", 0))

    outcomes = Counter(r.get("overall_outcome", "UNKNOWN") for r in acc)
    artifacts = Counter(r.get("artifact_type", "UNKNOWN") for r in acc)
    gates = {"prescriptiveGate": Counter(), "complianceGate": Counter(), "traceabilityCheck": Counter()}
    reasons = Counter()
    for r in acc:
        gm = r.get("gates") or {}
        for g in gates:
            gates[g][(gm.get(g) or {}).get("status", "UNKNOWN")] += 1
        for g in ("prescriptiveGate", "complianceGate"):
            gd = gm.get(g) or {}
            if gd.get("status") in {"BLOCKED", "FAIL"}:
                reasons[gd.get("reason", "Motivo nao informado")] += 1

    image_total = 0
    image_ok = 0
    for r in acc + non:
        if (r.get("suffix") or "").lower() in {".png", ".jpg", ".jpeg", ".heic"}:
            image_total += 1
            if r.get("extraction_status") == "ok":
                image_ok += 1

    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=letter)
    w, h = letter
    m = 34

    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(m, h - 92, w - 2 * m, 58, stroke=1, fill=1)
    c.setStrokeColor(colors.HexColor("#e2e8f0"))

    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(m + 10, h - 58, "Resumo Executivo Tecnico (Peticao-Ready) - Lote Acusatorio")
    c.setFont("Helvetica", 7.8)
    c.setFillColor(colors.HexColor("#475569"))
    sub1 = "Auditoria TCR-IA (strict + OCR) com politica de compliance por tipo de artefato (DECISION x ANALYTICAL)."
    sub2 = f"Base probatoria auditada: {total} arquivos acusatorios dentro de {total_scanned} arquivos varridos no lote."
    c.drawString(m + 10, h - 72, fit(c, sub1, "Helvetica", 7.8, w - 2 * m - 20))
    c.drawString(m + 10, h - 82, fit(c, sub2, "Helvetica", 7.8, w - 2 * m - 20))

    left_w = (w - 2 * m) * 0.58
    gap = 16
    left_x = m
    right_x = left_x + left_w + gap
    right_w = w - m - right_x
    yl = h - 106
    yr = h - 106

    yl = section(c, left_x, yl, left_w, "1. Achados Principais")
    achados = [
        f"Foram auditados {total} arquivos acusatorios ({pct(total, total_scanned)} do lote total de {total_scanned}).",
        f"Resultado: {outcomes.get('BLOCKED (complianceGate)',0)} bloqueios por complianceGate e {outcomes.get('BLOCKED (prescriptiveGate)',0)} por prescriptiveGate.",
        f"Persistem {outcomes.get('PARTIAL_PASS (traceability warning; static audit)',0) + outcomes.get('PARTIAL_PASS (static document audit; maturity/ledger not evaluated)',0)} aprovacoes parciais em auditoria estatica.",
        f"OCR operante em imagens: {image_ok}/{image_total} com sucesso (incluindo conversao HEIC).",
    ]
    yl = bullets(c, left_x, yl, left_w, achados, size=8.05, lead=9.6)

    yl = section(c, left_x, yl - 1, left_w, "2. Fundamentacao Tecnica (Gates)")
    fund = [
        f"prescriptiveGate: PASS={gates['prescriptiveGate'].get('PASS',0)} | BLOCKED={gates['prescriptiveGate'].get('BLOCKED',0)}.",
        f"complianceGate: BLOCKED={gates['complianceGate'].get('BLOCKED',0)} | WARN={gates['complianceGate'].get('WARN',0)} | PASS={gates['complianceGate'].get('PASS',0)}.",
        f"traceabilityCheck: PASS={gates['traceabilityCheck'].get('PASS',0)} | WARN={gates['traceabilityCheck'].get('WARN',0)}.",
        "maturityGate e ledgerRuntimeCheck permanecem nao avaliaveis/nao aplicaveis em artefatos estaticos.",
    ]
    yl = bullets(c, left_x, yl, left_w, fund, size=7.95, lead=9.4)

    yl = section(c, left_x, yl - 1, left_w, "3. Politica por Tipo de Artefato")
    pol = [
        f"ANALYTICAL_ARTIFACT: {artifacts.get('ANALYTICAL_ARTIFACT',0)} arquivos (ausencia de responsibleHuman gera WARN, sem bloqueio automatico).",
        f"DECISION_ARTIFACT: {artifacts.get('DECISION_ARTIFACT',0)} arquivos (complianceGate permanece bloqueante).",
        "Efeito pratico: reducão de bloqueios formais em material analitico, preservando triagem e rastreabilidade.",
    ]
    yl = bullets(c, left_x, yl, left_w, pol, size=7.9, lead=9.3)

    yr = section(c, right_x, yr, right_w, "4. Motivos Predominantes de Bloqueio")
    mot = [f"{n}x {r}" for r, n in reasons.most_common(5)]
    yr = bullets(c, right_x, yr, right_w, mot or ["Sem bloqueios apurados."], size=7.85, lead=9.25)

    yr = section(c, right_x, yr - 1, right_w, "5. Limitacoes Metodologicas")
    lim = [
        "Auditoria de conformidade estrutural/documental, nao de veracidade fatico-juridica das alegacoes.",
        "Resultados dependem de texto extraivel/OCR; qualidade de imagem e legibilidade impactam sinais.",
        "Nao substitui pericia tecnica especializada (audio, imagem, autenticidade, cadeia de custodia).",
    ]
    yr = bullets(c, right_x, yr, right_w, lim, size=7.85, lead=9.2)

    yr = section(c, right_x, yr - 1, right_w, "6. Recomendacoes de Saneamento Documental")
    rec = [
        "Priorizar os artefatos decisorios bloqueados para completar: responsibleHuman, finalidade declarada e aprovacao.",
        "Utilizar o arquivo CSV de 92 motivos como checklist de regularizacao por documento.",
        "Segregar, na juntada, material analitico (contexto) e artefatos decisorios (ato/decisao) para reduzir ruido de compliance.",
        "Manter OCR no fluxo de ingestao e registrar metadados de extração para reprodutibilidade.",
    ]
    yr = bullets(c, right_x, yr, right_w, rec, size=7.75, lead=9.0)

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(m, 35, w - m, 35)
    c.setFont("Helvetica", 7.2)
    c.setFillColor(colors.HexColor("#64748b"))
    foot = (
        "Documento sintetico para uso executivo/tecnico. Referenciar conjuntamente: JSON/MD da auditoria strict + OCR, "
        "relatorio PDF completo (96 paginas) e lista de 92 arquivos com motivos."
    )
    c.drawString(m, 22, fit(c, foot, "Helvetica", 7.2, w - 2 * m))
    c.save()
    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
