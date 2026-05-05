#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from io import BytesIO
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# =========================
# STYLES
# =========================

def styles():
    s = getSampleStyleSheet()

    s.add(ParagraphStyle(
        name="TitleX",
        parent=s["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.HexColor("#0f172a"),
    ))

    s.add(ParagraphStyle(
        name="BodyX",
        parent=s["BodyText"],
        fontSize=9,
    ))

    s.add(ParagraphStyle(
        name="H2X",
        parent=s["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
    ))

    return s


# =========================
# CORE ENGINE (SaaS READY)
# =========================

def generate_governance_pdf(
    audit: Dict[str, Any],
    blocked: Dict[str, Any],
    title: str = "TCRIA Governance Audit Report"
) -> bytes:

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=title,
        author="TCRIA Governance Engine",
    )

    s = styles()
    story: List[Any] = []

    accusation_set = audit.get("accusation_set", [])
    blocked_items = blocked.get("blocked_artifacts_review", [])

    # =========================
    # HEADER
    # =========================
    story.append(Paragraph("TCRIA", s["TitleX"]))
    story.append(Paragraph("AI Governance for Legal Evidence", s["BodyX"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(title, s["H2X"]))
    story.append(Spacer(1, 10))

    # =========================
    # SUMMARY
    # =========================
    summary = [
        ["Total files", str(audit.get("total_files_scanned", 0))],
        ["Accusation set", str(len(accusation_set))],
        ["Blocked", str(sum("BLOCKED" in str(x.get("overall_outcome", "")) for x in accusation_set))],
    ]

    table = Table(summary, colWidths=[200, 200])
    story.append(table)

    story.append(Spacer(1, 20))

    # =========================
    # ACCUSATION TABLE
    # =========================
    rows = [["File", "Outcome"]]

    for rec in accusation_set:
        rows.append([
            rec.get("file_name", "")[:40],
            rec.get("overall_outcome", "")
        ])

    t = Table(rows)
    story.append(Paragraph("Official Results", s["H2X"]))
    story.append(t)

    story.append(PageBreak())

    # =========================
    # BLOCKED SECTION
    # =========================
    story.append(Paragraph("Blocked Diagnostics", s["H2X"]))

    for rec in blocked_items:
        story.append(Paragraph(rec.get("file_name", ""), s["BodyX"]))
        story.append(Paragraph(str(rec.get("blocked_reason", "")), s["BodyX"]))
        story.append(Spacer(1, 10))

    doc.build(story)

    buffer.seek(0)
    return buffer.read()


# =========================
# CLI (mantido)
# =========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-json", required=True)
    parser.add_argument("--blocked-json", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    audit = json.loads(Path(args.audit_json).read_text())
    blocked = json.loads(Path(args.blocked_json).read_text())

    pdf = generate_governance_pdf(audit, blocked)

    Path(args.output).write_bytes(pdf)

    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
