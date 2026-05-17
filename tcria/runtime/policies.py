from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
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


class PolicySeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PolicyAction(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK_PROMOTION = "BLOCK_PROMOTION"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"


class PolicyEscalation(str, Enum):
    NONE = "NONE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    GOVERNANCE_OWNER = "GOVERNANCE_OWNER"


@dataclass(frozen=True)
class PolicyRule:
    rule_id: str
    description: str
    severity: PolicySeverity
    action: PolicyAction
    escalation: PolicyEscalation

    def to_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "severity": self.severity.value,
            "action": self.action.value,
            "escalation": self.escalation.value,
        }


@dataclass(frozen=True)
class PolicyFinding:
    rule_id: str
    severity: str
    action: str
    escalation: str
    subject: dict[str, Any]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "action": self.action,
            "escalation": self.escalation,
            "subject": self.subject,
            "reason": self.reason,
        }


class PolicyRegistry:
    def __init__(self, rules: list[PolicyRule] | None = None) -> None:
        self.rules = {rule.rule_id: rule for rule in (rules or DEFAULT_POLICY_RULES)}

    def get(self, rule_id: str) -> PolicyRule:
        return self.rules[rule_id]

    def to_list(self) -> list[dict[str, str]]:
        return [rule.to_dict() for rule in self.rules.values()]


DEFAULT_POLICY_RULES = [
    PolicyRule(
        rule_id="official_blocked_record",
        description="Official audit records with blocked gates cannot be promoted.",
        severity=PolicySeverity.CRITICAL,
        action=PolicyAction.BLOCK_PROMOTION,
        escalation=PolicyEscalation.GOVERNANCE_OWNER,
    ),
    PolicyRule(
        rule_id="official_warning_record",
        description="Official audit warning outcomes require explicit human attention before promotion.",
        severity=PolicySeverity.WARN,
        action=PolicyAction.REQUIRE_HUMAN_REVIEW,
        escalation=PolicyEscalation.HUMAN_REVIEW,
    ),
]


@dataclass(frozen=True)
class PolicyEvaluation:
    record_source_keys: tuple[str, ...] = RECORD_KEYS
    registry: list[dict[str, str]] = field(default_factory=list)
    total_records: int = 0
    blocked_count: int = 0
    warning_count: int = 0
    promotion_blocked: bool = False
    required_actions: list[str] = field(default_factory=list)
    escalation: str = PolicyEscalation.NONE.value
    findings: list[dict[str, Any]] = field(default_factory=list)
    blocked_records: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_source_keys": list(self.record_source_keys),
            "registry": self.registry,
            "total_records": self.total_records,
            "blocked_count": self.blocked_count,
            "warning_count": self.warning_count,
            "promotion_blocked": self.promotion_blocked,
            "required_actions": self.required_actions,
            "escalation": self.escalation,
            "findings": self.findings,
            "blocked_records": self.blocked_records,
        }


class GovernancePolicyEngine:
    def __init__(self, registry: PolicyRegistry | None = None) -> None:
        self.registry = registry or PolicyRegistry()

    def evaluate(self, bundle: dict[str, Any]) -> PolicyEvaluation:
        records = _iter_records(bundle)
        blocked_records: list[dict[str, Any]] = []
        warning_count = 0
        findings: list[PolicyFinding] = []

        for record in records:
            if _is_blocked(record):
                rule = self.registry.get("official_blocked_record")
                subject = {
                    "file_name": record.get("file_name"),
                    "file_path": record.get("file_path"),
                    "overall_outcome": record.get("overall_outcome"),
                    "blocked_gates": _blocked_gate_names(record),
                }
                blocked_records.append(
                    subject
                )
                findings.append(
                    PolicyFinding(
                        rule_id=rule.rule_id,
                        severity=rule.severity.value,
                        action=rule.action.value,
                        escalation=rule.escalation.value,
                        subject=subject,
                        reason="Official audit outcome is blocked.",
                    )
                )
            elif "WARN" in str(record.get("overall_outcome", "")).upper():
                rule = self.registry.get("official_warning_record")
                warning_count += 1
                findings.append(
                    PolicyFinding(
                        rule_id=rule.rule_id,
                        severity=rule.severity.value,
                        action=rule.action.value,
                        escalation=rule.escalation.value,
                        subject={
                            "file_name": record.get("file_name"),
                            "file_path": record.get("file_path"),
                            "overall_outcome": record.get("overall_outcome"),
                        },
                        reason="Official audit outcome contains a warning.",
                    )
                )

        required_actions = sorted({finding.action for finding in findings})
        escalation = PolicyEscalation.NONE.value
        if blocked_records:
            escalation = PolicyEscalation.GOVERNANCE_OWNER.value
        elif warning_count:
            escalation = PolicyEscalation.HUMAN_REVIEW.value

        return PolicyEvaluation(
            registry=self.registry.to_list(),
            total_records=len(records),
            blocked_count=len(blocked_records),
            warning_count=warning_count,
            promotion_blocked=bool(blocked_records),
            required_actions=required_actions,
            escalation=escalation,
            findings=[finding.to_dict() for finding in findings],
            blocked_records=blocked_records,
        )
