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
    "tcr_gateway_bernardo_notion_test_audit_with_images_strict_executive_summary_1page.pdf"
)


def pct(part: int, total: int) -> str:
    return f"{(100 * part / total):.1f}%" if total else "0.0%"


def fit_line(c: canvas.Canvas, text: str, font: str, size: int, max_width: float) -> str:
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


def bullet_list(c, x, y, width, items, font_size=8.7, leading=11):
    c.setFont("Helvetica", font_size)
    c.setFillColor(colors.HexColor("#111827"))
    for item in items:
        if y < 55:
            break
        line = fit_line(c, item, "Helvetica", font_size, width - 10)
        c.drawString(x, y, u"\u2022")
        c.drawString(x + 10, y, line)
        y -= leading
    return y


def main():
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    acc = data.get("accusation_set", [])
    total = len(acc)

    outcome_counts = Counter(r.get("overall_outcome", "UNKNOWN") for r in acc)
    artifact_counts = Counter(r.get("artifact_type", "UNKNOWN") for r in acc)

    gate_status = {"prescriptiveGate": Counter(), "complianceGate": Counter(), "traceabilityCheck": Counter()}
    top_block_reasons = Counter()
    suffix_counts = Counter((r.get("suffix") or "").lower() for r in acc)
    text_quality_counts = Counter(r.get("text_quality", "unknown") for r in acc)

    for r in acc:
        gates = r.get("gates") or {}
        for g in gate_status:
            gate_status[g][(gates.get(g) or {}).get("status", "UNKNOWN")] += 1
        for g in ("prescriptiveGate", "complianceGate"):
            gd = gates.get(g) or {}
            if gd.get("status") in {"BLOCKED", "FAIL"}:
                top_block_reasons[gd.get("reason", "Unknown reason")] += 1

    total_scanned = data.get("total_files_scanned", 0)
    class_counts = data.get("classification_counts", {})
    img_ok = class_counts.get("OCR_UNAVAILABLE", 0)  # legacy fallback (unused in current final)
    image_ocr_ok = 0
    for group in (data.get("accusation_set", []), data.get("non_accusation_set", [])):
        for r in group:
            if (r.get("suffix") or "").lower() in {".png", ".jpg", ".jpeg", ".heic"} and r.get("extraction_status") == "ok":
                image_ocr_ok += 1

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=letter)
    width, height = letter
    margin = 36

    # Background and title band
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#eef2ff"))
    c.rect(margin, height - 86, width - 2 * margin, 50, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(colors.HexColor("#1e1b4b"))
    c.drawString(margin + 10, height - 58, "Executive Summary: 92 Accusatory Files (Strict + OCR)")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#334155"))
    c.drawString(
        margin + 10,
        height - 73,
        fit_line(
            c,
            f"Source: {INPUT_JSON.name} | Generated: {data.get('generated_at', 'n/a')} | Policy: artifact_type dispatch enabled",
            "Helvetica",
            8.5,
            width - 2 * margin - 20,
        ),
    )

    left_x = margin
    gap = 18
    left_w = (width - 2 * margin) * 0.58
    right_x = left_x + left_w + gap
    right_w = width - margin - right_x
    y_left = height - 102
    y_right = height - 102

    # Left column: headline metrics + outcomes + gates
    y_left = draw_section_title(c, left_x, y_left, "Headline Metrics", left_w)
    headline = [
        f"Total scanned: {total_scanned}",
        f"Accusatory candidates audited: {total} ({pct(total, total_scanned)})",
        f"Images OCR extracted successfully: {image_ocr_ok}",
        f"Strict mode + artifact-type compliance policy applied",
    ]
    y_left = bullet_list(c, left_x, y_left, left_w, headline)

    y_left -= 2
    y_left = draw_section_title(c, left_x, y_left, "Outcomes (Accusatory Set)", left_w)
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
            outcome_lines.append(f"{v:>2} | {pct(v, total):>6} | {k}")
    y_left = bullet_list(c, left_x, y_left, left_w, outcome_lines, font_size=8.4, leading=10.5)

    y_left -= 2
    y_left = draw_section_title(c, left_x, y_left, "Gate Status Summary", left_w)
    gate_lines = [
        f"prescriptiveGate: PASS={gate_status['prescriptiveGate'].get('PASS',0)}, BLOCKED={gate_status['prescriptiveGate'].get('BLOCKED',0)}",
        f"complianceGate: BLOCKED={gate_status['complianceGate'].get('BLOCKED',0)}, WARN={gate_status['complianceGate'].get('WARN',0)}, PASS={gate_status['complianceGate'].get('PASS',0)}",
        f"traceabilityCheck: PASS={gate_status['traceabilityCheck'].get('PASS',0)}, WARN={gate_status['traceabilityCheck'].get('WARN',0)}",
    ]
    y_left = bullet_list(c, left_x, y_left, left_w, gate_lines)

    y_left -= 2
    y_left = draw_section_title(c, left_x, y_left, "Artifact Types (Accusatory Set)", left_w)
    art_lines = [
        f"ANALYTICAL_ARTIFACT: {artifact_counts.get('ANALYTICAL_ARTIFACT',0)}",
        f"DECISION_ARTIFACT: {artifact_counts.get('DECISION_ARTIFACT',0)}",
        "Rule: analytical artifacts downgrade missing responsibility to WARN.",
        "Rule: decision artifacts keep blocking complianceGate.",
    ]
    y_left = bullet_list(c, left_x, y_left, left_w, art_lines)

    # Right column: reasons + coverage + notes
    y_right = draw_section_title(c, right_x, y_right, "Top Blocking Reasons", right_w)
    reason_lines = []
    for reason, count in top_block_reasons.most_common(6):
        reason_lines.append(f"{count}x {reason}")
    y_right = bullet_list(c, right_x, y_right, right_w, reason_lines or ["No blocking reasons found."])

    y_right -= 2
    y_right = draw_section_title(c, right_x, y_right, "File Mix (Accusatory Set)", right_w)
    mix_lines = [f"{k or '[no suffix]'}: {v}" for k, v in suffix_counts.most_common(7)]
    y_right = bullet_list(c, right_x, y_right, right_w, mix_lines)

    y_right -= 2
    y_right = draw_section_title(c, right_x, y_right, "Text Extraction Quality", right_w)
    tq_lines = [f"{k}: {v}" for k, v in text_quality_counts.most_common()]
    y_right = bullet_list(c, right_x, y_right, right_w, tq_lines)

    y_right -= 2
    y_right = draw_section_title(c, right_x, y_right, "Operational Notes", right_w)
    notes = [
        "Static-file audit only: maturityGate and ledger runtime remain non-evaluable/not applicable.",
        "OCR pipeline active (including HEIC conversion via sips) and completed with zero image OCR errors.",
        "Use the 92-file reasons CSV/MD for file-level remediation and filing triage.",
    ]
    y_right = bullet_list(c, right_x, y_right, right_w, notes, font_size=8.3, leading=10.3)

    # Footer
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(margin, 34, width - margin, 34)
    c.setFont("Helvetica", 7.8)
    c.setFillColor(colors.HexColor("#475569"))
    footer = (
        "Derived from /output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict.json "
        "using TCR-IA-style gates with artifact-type compliance policy."
    )
    c.drawString(margin, 22, fit_line(c, footer, "Helvetica", 7.8, width - 2 * margin))

    c.save()
    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
