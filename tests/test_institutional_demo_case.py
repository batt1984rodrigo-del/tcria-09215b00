from __future__ import annotations

import json
from pathlib import Path


def test_institutional_demo_case_packaged_outputs() -> None:
    demo_dir = Path(__file__).resolve().parents[1] / "examples" / "institutional-demo-case"
    output_dir = demo_dir / "output"

    audit = json.loads((output_dir / "institutional_demo_strict.json").read_text(encoding="utf-8"))
    telemetry = json.loads(
        (output_dir / "institutional_demo_strict_governance_telemetry.json").read_text(encoding="utf-8")
    )
    ledger = json.loads((output_dir / "institutional_demo_strict_governance_ledger.json").read_text(encoding="utf-8"))
    signatures = json.loads(
        (output_dir / "institutional_demo_strict_artifact_signatures.json").read_text(encoding="utf-8")
    )

    assert audit["total_files_scanned"] == 2
    assert audit["accusation_set_count"] == 1
    assert audit["accusation_set"][0]["overall_outcome"] == "BLOCKED (complianceGate)"
    assert telemetry["policy_evaluation"]["blocked_count"] == 1
    assert telemetry["policy_evaluation"]["escalation"] == "GOVERNANCE_OWNER"
    assert "BLOCK_PROMOTION" in telemetry["policy_evaluation"]["required_actions"]
    assert "BLOCKED" in telemetry["state"]["history"]
    assert ledger["verified"] is True
    assert signatures["artifacts"]

    for path in output_dir.glob("*.json"):
        assert "/Users/" not in path.read_text(encoding="utf-8")
