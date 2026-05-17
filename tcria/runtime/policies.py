from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


RECORD_KEYS = ("accusation_set", "records", "audit_records", "documents", "items")


def _iter_records(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    for key in RECORD_KEYS:
        value = bundle.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _blocked_gate_names(record: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    gates = record.get("gates")
    if not isinstance(gates, dict):
        return blocked

    for gate_name, gate_payload in gates.items():
        if not isinstance(gate_payload, dict):
            continue
        status = str(gate_payload.get("status", "")).upper()
        if status in {"BLOCKED", "FAIL"}:
            blocked.append(str(gate_name))
    return blocked


def _is_blocked(record: dict[str, Any]) -> bool:
    outcome = str(record.get("overall_outcome", "")).upper()
    return "BLOCKED" in outcome or bool(_blocked_gate_names(record))


@dataclass(frozen=True)
class PolicyEvaluation:
    record_source_keys: tuple[str, ...] = RECORD_KEYS
    total_records: int = 0
    blocked_count: int = 0
    warning_count: int = 0
    promotion_blocked: bool = False
    blocked_records: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_source_keys": list(self.record_source_keys),
            "total_records": self.total_records,
            "blocked_count": self.blocked_count,
            "warning_count": self.warning_count,
            "promotion_blocked": self.promotion_blocked,
            "blocked_records": self.blocked_records,
        }


class GovernancePolicyEngine:
    def evaluate(self, bundle: dict[str, Any]) -> PolicyEvaluation:
        records = _iter_records(bundle)
        blocked_records: list[dict[str, Any]] = []
        warning_count = 0

        for record in records:
            if _is_blocked(record):
                blocked_records.append(
                    {
                        "file_name": record.get("file_name"),
                        "file_path": record.get("file_path"),
                        "overall_outcome": record.get("overall_outcome"),
                        "blocked_gates": _blocked_gate_names(record),
                    }
                )
            elif "WARN" in str(record.get("overall_outcome", "")).upper():
                warning_count += 1

        return PolicyEvaluation(
            total_records=len(records),
            blocked_count=len(blocked_records),
            warning_count=warning_count,
            promotion_blocked=bool(blocked_records),
            blocked_records=blocked_records,
        )
