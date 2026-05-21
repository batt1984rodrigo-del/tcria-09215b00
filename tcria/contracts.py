from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ExtractionStatus = Literal["ok", "error", "skipped", "unsupported"]
GateStatus = Literal["PASS", "WARN", "BLOCKED", "NOT_EVALUATED", "NOT_APPLICABLE"]
AuditOutcome = str | None


class TCRIAContract(BaseModel):
    """Base model for typed TCRIA data contracts.

    These models are intentionally additive: they formalize payload shapes without
    changing governance semantics or pipeline architecture.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class DocumentContract(TCRIAContract):
    path: Path
    relative_path: str
    suffix: str
    size_bytes: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)
    text: str = ""
    extraction_status: ExtractionStatus | str
    extraction_method: str

    @field_validator("suffix")
    @classmethod
    def normalize_suffix(cls, value: str) -> str:
        value = value.strip().lower()
        if value and not value.startswith("."):
            return f".{value}"
        return value


class GateResultContract(TCRIAContract):
    status: GateStatus | str
    reason: str
    evidence: str | None = None


class AuditRecordContract(TCRIAContract):
    document: DocumentContract
    classification: str
    artifact_type: str
    artifact_type_reason: str
    interpretation: dict[str, Any] | None = None
    raises_accusation: bool
    classification_reasons: list[str] = Field(default_factory=list)
    signals: dict[str, Any] = Field(default_factory=dict)
    gates: dict[str, GateResultContract | dict[str, Any]] | None = None
    overall_outcome: AuditOutcome = None


def validate_document_contract(payload: Any) -> DocumentContract:
    return DocumentContract.model_validate(payload)


def validate_gate_result_contract(payload: Any) -> GateResultContract:
    return GateResultContract.model_validate(payload)


def validate_audit_record_contract(payload: Any) -> AuditRecordContract:
    return AuditRecordContract.model_validate(payload)
