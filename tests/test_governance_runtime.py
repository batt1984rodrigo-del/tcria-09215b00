from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tcria.runtime import GovernanceLedger, GovernancePolicyEngine, sign_artifact
from tcria.runtime.events import GovernanceEvent, GovernanceEventType


def test_policy_engine_reads_real_tcria_accusation_set() -> None:
    bundle = {
        "accusation_set": [
            {
                "file_name": "blocked.txt",
                "file_path": "/case/blocked.txt",
                "overall_outcome": "BLOCKED (complianceGate)",
                "gates": {"complianceGate": {"status": "BLOCKED"}},
            }
        ],
        "records": [
            {
                "file_name": "legacy.txt",
                "overall_outcome": "PASS",
            }
        ],
    }

    result = GovernancePolicyEngine().evaluate(bundle)

    assert result.total_records == 1
    assert result.blocked_count == 1
    assert result.promotion_blocked is True
    assert result.escalation == "GOVERNANCE_OWNER"
    assert "BLOCK_PROMOTION" in result.required_actions
    assert result.findings[0]["severity"] == "CRITICAL"
    assert result.blocked_records[0]["file_name"] == "blocked.txt"


def test_governance_ledger_hash_chain_links_events() -> None:
    ledger = GovernanceLedger()

    first = ledger.append(GovernanceEvent(GovernanceEventType.CHECK_STARTED, {"case": "one"}))
    second = ledger.append(GovernanceEvent(GovernanceEventType.POLICY_EVALUATED, {"blocked_count": 1}))

    assert first.previous_hash == "0" * 64
    assert second.previous_hash == first.entry_hash
    assert ledger.current_hash == second.entry_hash
    assert ledger.verify() is True


def test_artifact_signature_is_stable_sha256(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    artifact.write_text('{"ok": true}\n', encoding="utf-8")

    signature = sign_artifact(artifact)

    assert signature.algorithm == "sha256"
    assert signature.size_bytes == artifact.stat().st_size
    assert len(signature.sha256) == 64


def test_skip_audit_pipeline_reaches_classified_and_counts_artifacts(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_json = tmp_path / "real_tcria_audit_strict.json"
    review_json = tmp_path / "review.json"
    review_md = tmp_path / "review.md"
    audit_json.write_text(
        json.dumps(
            {
                "accusation_set_count": 1,
                "accusation_set": [
                    {
                        "file_name": "blocked.txt",
                        "file_path": str(tmp_path / "blocked.txt"),
                        "overall_outcome": "BLOCKED (complianceGate)",
                        "gates": {"complianceGate": {"status": "BLOCKED", "reason": "Missing DecisionRecord."}},
                        "key_signals": {},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    cp = subprocess.run(
        [
            sys.executable,
            str(repo_root / "run_governance_pipeline.py"),
            "--repo-root",
            str(repo_root),
            "--skip-audit",
            "--audit-json",
            str(audit_json),
            "--review-json-out",
            str(review_json),
            "--review-md-out",
            str(review_md),
        ],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
    )

    assert cp.returncode == 0, cp.stderr or cp.stdout
    events_path = tmp_path / "real_tcria_audit_strict_governance_events.json"
    ledger_path = tmp_path / "real_tcria_audit_strict_governance_ledger.json"
    telemetry_path = tmp_path / "real_tcria_audit_strict_governance_telemetry.json"
    signatures_path = tmp_path / "real_tcria_audit_strict_artifact_signatures.json"
    assert events_path.exists()
    assert ledger_path.exists()
    assert telemetry_path.exists()
    assert signatures_path.exists()

    events = json.loads(events_path.read_text(encoding="utf-8"))
    telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    signatures = json.loads(signatures_path.read_text(encoding="utf-8"))

    event_types = [event["event_type"] for event in events]
    assert "OFFICIAL_AUDIT_SKIPPED" in event_types
    assert "PROMOTION_BLOCKED" in event_types
    assert events[0]["schema_version"] == "governance.event.v1"
    assert ledger["verified"] is True
    assert telemetry["state"]["history"][:3] == ["CREATED", "INGESTED", "CLASSIFIED"]
    assert telemetry["state"]["current"] == "COMPLETED"
    assert telemetry["policy_evaluation"]["blocked_count"] == 1
    assert telemetry["policy_evaluation"]["escalation"] == "GOVERNANCE_OWNER"
    assert telemetry["artifact_count"] >= 3
    assert len(signatures["artifacts"]) == 3
    assert all(len(item["sha256"]) == 64 for item in signatures["artifacts"])
