from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tcria.runtime.events import GovernanceEvent, GovernanceEventType
from tcria.runtime.ledger import GovernanceLedger
from tcria.runtime.policies import GovernancePolicyEngine, PolicyEvaluation
from tcria.runtime.signatures import sign_artifact
from tcria.runtime.state import GovernanceState, GovernanceStateMachine
from tcria.runtime.telemetry import RuntimeTelemetry


class GovernanceRuntime:
    def __init__(self) -> None:
        self.state = GovernanceStateMachine()
        self.ledger = GovernanceLedger()
        self.telemetry = RuntimeTelemetry()
        self.policy_engine = GovernancePolicyEngine()
        self.events: list[GovernanceEvent] = []
        self.policy_evaluation: PolicyEvaluation | None = None

    def transition(self, next_state: GovernanceState) -> GovernanceState:
        return self.state.transition(next_state)

    def record_event(
        self,
        event_type: GovernanceEventType,
        payload: dict[str, Any] | None = None,
    ) -> GovernanceEvent:
        event = GovernanceEvent(event_type=event_type, payload=payload or {})
        self.events.append(event)
        self.ledger.append(event)
        return event

    def record_artifact(self, artifact_path: str | Path, *, artifact_type: str) -> GovernanceEvent:
        signature = sign_artifact(artifact_path)
        return self.record_event(
            GovernanceEventType.ARTIFACT_GENERATED,
            {
                "artifact_type": artifact_type,
                "artifact_path": signature.artifact_path,
                "artifact_signature": signature.to_dict(),
            },
        )

    def evaluate_policies(self, audit_bundle: dict[str, Any]) -> PolicyEvaluation:
        self.policy_evaluation = self.policy_engine.evaluate(audit_bundle)
        self.record_event(GovernanceEventType.POLICY_EVALUATED, self.policy_evaluation.to_dict())
        self.transition(GovernanceState.POLICY_EVALUATED)
        if self.policy_evaluation.promotion_blocked:
            self.record_event(
                GovernanceEventType.PROMOTION_BLOCKED,
                {
                    "blocked_count": self.policy_evaluation.blocked_count,
                    "reason": "One or more official audit records remain blocked.",
                },
            )
            self.transition(GovernanceState.BLOCKED)
        else:
            self.record_event(
                GovernanceEventType.PROMOTION_ALLOWED,
                {"reason": "No blocked official audit records were detected."},
            )
            self.transition(GovernanceState.APPROVED)
        return self.policy_evaluation

    def write_runtime_artifacts(self, output_dir: str | Path, *, output_stem: str) -> dict[str, str]:
        output_path = Path(output_dir).expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        events_path = output_path / f"{output_stem}_governance_events.json"
        ledger_path = output_path / f"{output_stem}_governance_ledger.json"
        telemetry_path = output_path / f"{output_stem}_governance_telemetry.json"
        signatures_path = output_path / f"{output_stem}_artifact_signatures.json"

        events_payload = [event.to_dict() for event in self.events]
        ledger_payload = {
            "ledger_head": self.ledger.current_hash,
            "verified": self.ledger.verify(),
            "entries": self.ledger.to_list(),
        }
        telemetry_payload = self.telemetry.collect(
            events=self.events,
            state=self.state.to_dict(),
            ledger_head=self.ledger.current_hash,
            policy_evaluation=self.policy_evaluation.to_dict() if self.policy_evaluation else None,
        )

        events_path.write_text(json.dumps(events_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        ledger_path.write_text(json.dumps(ledger_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        telemetry_path.write_text(json.dumps(telemetry_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        self.record_event(
            GovernanceEventType.RUNTIME_COMPLETED,
            {
                "events_json": str(events_path),
                "ledger_json": str(ledger_path),
                "telemetry_json": str(telemetry_path),
                "signatures_json": str(signatures_path),
            },
        )
        self.transition(GovernanceState.COMPLETED)

        events_payload = [event.to_dict() for event in self.events]
        ledger_payload = {
            "ledger_head": self.ledger.current_hash,
            "verified": self.ledger.verify(),
            "entries": self.ledger.to_list(),
        }
        telemetry_payload = self.telemetry.collect(
            events=self.events,
            state=self.state.to_dict(),
            ledger_head=self.ledger.current_hash,
            policy_evaluation=self.policy_evaluation.to_dict() if self.policy_evaluation else None,
        )
        events_path.write_text(json.dumps(events_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        ledger_path.write_text(json.dumps(ledger_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        telemetry_path.write_text(json.dumps(telemetry_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        signatures_payload = {
            "algorithm": "sha256",
            "artifacts": [
                sign_artifact(events_path).to_dict(),
                sign_artifact(ledger_path).to_dict(),
                sign_artifact(telemetry_path).to_dict(),
            ],
        }
        signatures_path.write_text(json.dumps(signatures_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "events_json": str(events_path),
            "ledger_json": str(ledger_path),
            "telemetry_json": str(telemetry_path),
            "signatures_json": str(signatures_path),
        }
