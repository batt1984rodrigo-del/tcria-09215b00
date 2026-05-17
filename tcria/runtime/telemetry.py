from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from tcria.runtime.events import GovernanceEvent


ARTIFACT_PAYLOAD_KEYS = (
    "artifact_path",
    "audit_json",
    "audit_md",
    "review_json",
    "review_md",
    "ledger_json",
    "events_json",
    "telemetry_json",
    "signatures_json",
)


class RuntimeTelemetry:
    def __init__(self) -> None:
        self.started_at = datetime.now(timezone.utc)

    def collect(
        self,
        *,
        events: list[GovernanceEvent],
        state: dict[str, object],
        ledger_head: str,
        policy_evaluation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event_counts = Counter(event.event_type.value for event in events)
        artifacts = self._collect_artifacts(events)
        completed_at = datetime.now(timezone.utc)
        duration_ms = int((completed_at - self.started_at).total_seconds() * 1000)

        return {
            "started_at": self.started_at.isoformat(timespec="seconds"),
            "completed_at": completed_at.isoformat(timespec="seconds"),
            "duration_ms": duration_ms,
            "event_count": len(events),
            "event_counts": dict(sorted(event_counts.items())),
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
            "state": state,
            "ledger_head": ledger_head,
            "policy_evaluation": policy_evaluation or {},
        }

    @staticmethod
    def _collect_artifacts(events: list[GovernanceEvent]) -> list[str]:
        artifacts: list[str] = []
        seen: set[str] = set()
        for event in events:
            for key in ARTIFACT_PAYLOAD_KEYS:
                value = event.payload.get(key)
                if isinstance(value, str) and value and value not in seen:
                    seen.add(value)
                    artifacts.append(value)
        return artifacts
