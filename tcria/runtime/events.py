from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


EVENT_SCHEMA_VERSION = "governance.event.v1"


class GovernanceEventType(str, Enum):
    CHECK_STARTED = "CHECK_STARTED"
    INGESTION_STARTED = "INGESTION_STARTED"
    INGESTION_COMPLETED = "INGESTION_COMPLETED"
    OFFICIAL_AUDIT_STARTED = "OFFICIAL_AUDIT_STARTED"
    OFFICIAL_AUDIT_COMPLETED = "OFFICIAL_AUDIT_COMPLETED"
    OFFICIAL_AUDIT_SKIPPED = "OFFICIAL_AUDIT_SKIPPED"
    COMPLEMENTARY_REVIEW_STARTED = "COMPLEMENTARY_REVIEW_STARTED"
    COMPLEMENTARY_REVIEW_COMPLETED = "COMPLEMENTARY_REVIEW_COMPLETED"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    PROMOTION_BLOCKED = "PROMOTION_BLOCKED"
    PROMOTION_ALLOWED = "PROMOTION_ALLOWED"
    ARTIFACT_GENERATED = "ARTIFACT_GENERATED"
    TRACEABILITY_FAILED = "TRACEABILITY_FAILED"
    RUNTIME_COMPLETED = "RUNTIME_COMPLETED"


@dataclass(frozen=True)
class GovernanceEvent:
    event_type: GovernanceEventType
    payload: dict[str, Any] = field(default_factory=dict)
    subject: str = "governance_runtime"
    actor: str = "tcria"
    schema_version: str = EVENT_SCHEMA_VERSION
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "schema_version": self.schema_version,
            "event_type": self.event_type.value,
            "subject": self.subject,
            "actor": self.actor,
            "created_at": self.created_at,
            "payload": self.payload,
        }
