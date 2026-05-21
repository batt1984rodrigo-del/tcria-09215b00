#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_audit(audit: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(audit.get("summary"), dict):
        summary = audit["summary"]
        return {
            "total_files": summary.get("total_files"),
            "accusatory_candidates": summary.get("accusatory_candidates"),
            "blocked_by_prescriptive_gate": summary.get("blocked_by_prescriptive_gate"),
            "blocked_by_compliance_gate": summary.get("blocked_by_compliance_gate"),
        }

    accusation_set = list(audit.get("accusation_set") or [])
    blocked_prescriptive = 0
    blocked_compliance = 0
    for rec in accusation_set:
        outcome = str(rec.get("overall_outcome", ""))
        if "prescriptiveGate" in outcome:
            blocked_prescriptive += 1
        if "complianceGate" in outcome:
            blocked_compliance += 1
    return {
        "total_files": audit.get("total_files_scanned"),
        "accusatory_candidates": audit.get("accusation_set_count", len(accusation_set)),
        "blocked_by_prescriptive_gate": blocked_prescriptive,
        "blocked_by_compliance_gate": blocked_compliance,
    }


def normalize_blocked_documents(blocked: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(blocked.get("blocked_artifacts"), list):
        docs = []
        for item in blocked["blocked_artifacts"]:
            docs.append(
                {
                    "file": item.get("file") or item.get("file_name"),
                    "reason": item.get("reason") or item.get("blocked_reason"),
                }
            )
        return docs

    docs = []
    for item in blocked.get("blocked_artifacts_review") or []:
        docs.append(
            {
                "file": item.get("file_name"),
                "reason": item.get("blocked_reason"),
            }
        )
    return docs


def normalize_timeline_events(timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(timeline.get("events"), list):
        return list(timeline["events"])

    events = []
    for item in timeline.get("timeline_entries") or []:
        years = item.get("date_anchors_hint") or []
        date_hint = str(years[0]) if years else "unknown-date"
        desc = (
            f"{item.get('file_name')} | outcome={item.get('overall_outcome')} | "
            f"dates={item.get('dates_found')} currency={item.get('currency_values_found')} pix={item.get('pix_mentions')}"
        )
        events.append({"date": date_hint, "description": desc})
    return events


def build_report(audit: Dict[str, Any], blocked: Dict[str, Any], preparation: Dict[str, Any], timeline: Dict[str, Any]) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "case_readiness": preparation.get("case_readiness"),
        "top_evidence_files": preparation.get("top_evidence_files", []),
        "top_narrative_files": preparation.get("top_narrative_files", []),
        "blocked_documents": normalize_blocked_documents(blocked),
        "governance_gaps": preparation.get("governance_gaps", []),
        "timeline_events": normalize_timeline_events(timeline),
        "recommended_next_actions": preparation.get("recommended_next_actions", []),
        "audit_summary": summarize_audit(audit),
        "guardrails": {
            "complementary_layers_do_not_change_official_outcome": True,
            "status_promotion_requires_human_re_audit": True,
        },
    }
    return report


def summarize_item(item: Any) -> str:
    if isinstance(item, dict):
        keys = [
            "file_name",
            "file",
            "overall_outcome",
            "official_outcome",
            "evidence_score",
            "narrative_score",
            "gap",
            "count",
            "reason",
            "blocked_reason",
        ]
        parts = []
        for k in keys:
            if k in item and item.get(k) not in (None, ""):
                parts.append(f"{k}={item.get(k)}")
        if parts:
            return "; ".join(parts)
        return json.dumps(item, ensure_ascii=False)
    return str(item)


def build_markdown(report: Dict[str, Any]) -> str:
    md: List[str] = []
    md.append("# TCRIA Investigation Report\n")
    md.append(f"Generated at: {report['generated_at']}\n")

    md.append("## Case Readiness\n")
    md.append(f"{report.get('case_readiness')}\n")

    md.append("## Audit Summary\n")
    for k, v in (report.get("audit_summary") or {}).items():
        md.append(f"- {k}: {v}")

    md.append("\n## Key Evidence Files\n")
    for f in report.get("top_evidence_files", []):
        md.append(f"- {summarize_item(f)}")

    md.append("\n## Narrative Documents\n")
    for f in report.get("top_narrative_files", []):
        md.append(f"- {summarize_item(f)}")

    md.append("\n## Governance Gaps\n")
    for g in report.get("governance_gaps", []):
        md.append(f"- {summarize_item(g)}")

    md.append("\n## Blocked Documents\n")
    for b in report.get("blocked_documents", []):
        md.append(f"- {b.get('file')} — {b.get('reason')}")

    md.append("\n## Timeline\n")
    for e in report.get("timeline_events", []):
        md.append(f"- {e.get('date')} — {e.get('description')}")

    md.append("\n## Recommended Next Actions\n")
    for a in report.get("recommended_next_actions", []):
        md.append(f"- {a}")

    md.append("\n## Guardrails\n")
    for k, v in (report.get("guardrails") or {}).items():
        md.append(f"- {k}: {v}")

    return "\n".join(md)


def build_pdf(markdown_text: str, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    story = []

    for line in markdown_text.split("\n"):
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Heading1"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("- "):
            story.append(Paragraph(line, styles["Normal"]))
        elif line.strip() == "":
            story.append(Spacer(1, 6))
            continue
        else:
            story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    doc.build(story)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True)
    parser.add_argument("--blocked", required=True)
    parser.add_argument("--preparation", required=True)
    parser.add_argument("--timeline", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    audit = load_json(Path(args.audit).expanduser().resolve())
    blocked = load_json(Path(args.blocked).expanduser().resolve())
    preparation = load_json(Path(args.preparation).expanduser().resolve())
    timeline = load_json(Path(args.timeline).expanduser().resolve())

    report = build_report(audit, blocked, preparation, timeline)

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    json_out = out_dir / "investigation_report.json"
    md_out = out_dir / "investigation_report.md"
    pdf_out = out_dir / "investigation_report.pdf"

    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = build_markdown(report)
    md_out.write_text(markdown, encoding="utf-8")
    build_pdf(markdown, pdf_out)

    print("Investigation report generated:")
    print(json_out)
    print(md_out)
    print(pdf_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
