from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from tcria.audit import build_audit_bundle, write_audit_artifacts
from tcria.classification import classify_artifact, infer_artifact_type
from tcria.governance import (
    evaluate_compliance_gate,
    evaluate_prescriptive_gate,
    evaluate_traceability_check,
)
from tcria.ingestion import load_documents
from tcria.models import AuditRecord
from tcria.signals import detect_signals


class TCRIAEngine:
    def __init__(self, repo_root: str | Path | None = None) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve() if repo_root else Path(__file__).resolve().parent.parent
        self.pipeline_script = self.repo_root / "run_governance_pipeline.py"

    def run_audit(
        self,
        input_path: str | None = None,
        *,
        input_paths: list[str] | None = None,
        strict: bool = True,
        out_dir: str | Path = "output/audit",
        output_stem: str = "audit",
        include_pdf: bool = True,
        max_files: int | None = None,
        max_total_bytes: int | None = None,
    ) -> dict[str, object]:
        paths = input_paths[:] if input_paths else ([input_path] if input_path else [])
        if not paths:
            raise ValueError("At least one input path is required.")

        documents = []
        for path_value in paths:
            documents.extend(
                load_documents(
                    path_value,
                    max_files=max_files,
                    max_total_bytes=max_total_bytes,
                )
            )
        records: list[AuditRecord] = []

        for doc in documents:
            signals = detect_signals(doc.text) if doc.extraction_status == "ok" else {
                "dates_found": 0,
                "currency_values_found": 0,
                "pix_mentions": 0,
                "email_mentions": 0,
                "transaction_terms": 0,
                "accusation_keyword_hits": {},
                "evidence_marker_hits": {},
                "administrative_fiscal_marker_hits": {},
                "restitution_request_hits": {},
                "legal_basis_marker_hits": {},
                "accountability_support_hits": {},
                "request_argument_hits": {},
                "defensive_argument_hits": {},
                "certifying_marker_hits": {},
                "routing_marker_hits": {},
                "decision_marker_hits": {},
                "calculation_marker_hits": {},
                "investigative_marker_hits": {},
                "administrative_charge_hits": {},
                "icms_suspension_marker_hits": {},
                "target_entity_hits": {},
                "contains_objetivo_label": False,
                "contains_autor_label": False,
                "contains_summary_label": False,
                "legal_pattern_counts": {"legal_strong": 0, "legal_medium": 0, "accusation": 0},
                "density_scores": {"legal_refs_density": 0.0, "accusation_density": 0.0},
                "legal_refs_density": 0.0,
                "legal_terms_density": 0.0,
                "accusation_density": 0.0,
            }
            classification, raises_accusation, reasons, interpretation = classify_artifact(doc, signals)
            artifact_type, artifact_type_reason = infer_artifact_type(doc)

            gates = None
            overall = None
            if raises_accusation:
                prescriptive = evaluate_prescriptive_gate(doc.text)
                compliance = evaluate_compliance_gate(doc.text, strict=strict)
                traceability = evaluate_traceability_check(signals)
                gates = {
                    "prescriptiveGate": asdict(prescriptive),
                    "complianceGate": asdict(compliance),
                    "traceabilityCheck": asdict(traceability),
                    "maturityGate": {
                        "status": "NOT_EVALUATED",
                        "reason": "KnowledgeCore.maturityScore is not available in static file content.",
                        "evidence": None,
                    },
                    "ledgerRuntimeCheck": {
                        "status": "NOT_APPLICABLE",
                        "reason": "Static files do not expose runtime ledger events or hash-chain state.",
                        "evidence": None,
                    },
                }
                if prescriptive.status == "BLOCKED":
                    overall = "BLOCKED (prescriptiveGate)"
                elif compliance.status == "BLOCKED":
                    overall = "BLOCKED (complianceGate)"
                elif traceability.status == "WARN":
                    overall = "PARTIAL_PASS (traceability warning; static audit)"
                else:
                    overall = "PARTIAL_PASS (static document audit; maturity/ledger not evaluated)"

            records.append(
                AuditRecord(
                    document=doc,
                    classification=classification,
                    artifact_type=artifact_type,
                    artifact_type_reason=artifact_type_reason,
                    interpretation=interpretation,
                    raises_accusation=raises_accusation,
                    classification_reasons=reasons,
                    signals=signals,
                    gates=gates,
                    overall_outcome=overall,
                )
            )

        bundle_input_repr = paths[0] if len(paths) == 1 else ",".join(paths)
        bundle = build_audit_bundle(records, input_path=bundle_input_repr, strict=strict)
        effective_stem = output_stem
        if strict and not effective_stem.endswith("_strict"):
            effective_stem = f"{effective_stem}_strict"
        artifacts = write_audit_artifacts(bundle, out_dir=out_dir, output_stem=effective_stem, include_pdf=include_pdf)
        return {"bundle": bundle, "artifacts": artifacts}

    def run_official_pipeline(
        self,
        input_path: str | None = None,
        *,
        input_paths: list[str] | None = None,
        strict: bool = True,
        output_stem: str | None = None,
        max_files: int | None = None,
        max_total_bytes: int | None = None,
    ) -> dict[str, str]:
        if not self.pipeline_script.exists():
            raise FileNotFoundError(f"Pipeline script not found: {self.pipeline_script}")

        paths = input_paths[:] if input_paths else ([input_path] if input_path else [])
        if not paths:
            raise ValueError("At least one input path is required for official pipeline execution.")

        cmd = [sys.executable, str(self.pipeline_script), "--repo-root", str(self.repo_root)]
        for p in paths:
            cmd.extend(["--path", p])
        if strict:
            cmd.append("--strict")
        if output_stem:
            cmd.extend(["--output-stem", output_stem])
        if max_files is not None:
            cmd.extend(["--max-files", str(max_files)])
        if max_total_bytes is not None:
            cmd.extend(["--max-total-bytes", str(max_total_bytes)])

        cp = subprocess.run(cmd, text=True, capture_output=True, cwd=str(self.repo_root))
        if cp.returncode != 0:
            raise RuntimeError(f"Official pipeline failed ({cp.returncode}): {cp.stderr or cp.stdout}")

        out = cp.stdout
        official = self._extract_line_value(out, r"^\[pipeline\] Official audit JSON:\s*(.+)$")
        blocked = self._extract_line_value(out, r"^\[pipeline\] Blocked review JSON:\s*(.+)$")
        blocked_md = self._extract_line_value(out, r"^\[pipeline\] Blocked review MD:\s*(.+)$")
        official_md = self._extract_line_value(out, r"^Markdown report:\s*(.+)$")
        if not official or not blocked or not blocked_md:
            raise RuntimeError("Could not parse pipeline output paths.")
        if not official_md:
            official_md = str(Path(official).with_suffix(".md"))
        return {
            "official_audit_json": official,
            "official_audit_md": official_md,
            "blocked_review_json": blocked,
            "blocked_review_md": blocked_md,
            "stdout": out,
        }

    @staticmethod
    def _extract_line_value(text: str, pattern: str) -> str | None:
        match = re.search(pattern, text, flags=re.MULTILINE)
        if not match:
            return None
        return match.group(1).strip()
