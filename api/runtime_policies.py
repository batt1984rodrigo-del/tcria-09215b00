from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GovernanceRuntimePolicy:
    name: str
    require_auth: bool
    allow_artifact_read: bool
    allow_artifact_signing: bool
    allow_streaming: bool
    allow_openai_bridge: bool
    max_files: int | None
    max_total_bytes: int | None
    human_review_required: bool = True


POLICIES: dict[str, GovernanceRuntimePolicy] = {
    "dev": GovernanceRuntimePolicy(
        name="dev",
        require_auth=False,
        allow_artifact_read=True,
        allow_artifact_signing=False,
        allow_streaming=True,
        allow_openai_bridge=True,
        max_files=25,
        max_total_bytes=25_000_000,
    ),
    "staging": GovernanceRuntimePolicy(
        name="staging",
        require_auth=True,
        allow_artifact_read=True,
        allow_artifact_signing=True,
        allow_streaming=True,
        allow_openai_bridge=True,
        max_files=100,
        max_total_bytes=100_000_000,
    ),
    "production": GovernanceRuntimePolicy(
        name="production",
        require_auth=True,
        allow_artifact_read=True,
        allow_artifact_signing=True,
        allow_streaming=True,
        allow_openai_bridge=True,
        max_files=250,
        max_total_bytes=250_000_000,
    ),
    "locked": GovernanceRuntimePolicy(
        name="locked",
        require_auth=True,
        allow_artifact_read=False,
        allow_artifact_signing=False,
        allow_streaming=False,
        allow_openai_bridge=False,
        max_files=0,
        max_total_bytes=0,
    ),
}


def active_policy() -> GovernanceRuntimePolicy:
    profile = os.getenv("TCRIA_MCP_RUNTIME_PROFILE", "production").lower()
    return POLICIES.get(profile, POLICIES["production"])


def enforce_policy(action: str, metadata: dict[str, Any] | None = None) -> None:
    policy = active_policy()
    metadata = metadata or {}

    if action == "artifact_read" and not policy.allow_artifact_read:
        raise PermissionError(f"Artifact read disabled by runtime policy: {policy.name}")
    if action == "artifact_sign" and not policy.allow_artifact_signing:
        raise PermissionError(f"Artifact signing disabled by runtime policy: {policy.name}")
    if action == "streaming" and not policy.allow_streaming:
        raise PermissionError(f"Streaming disabled by runtime policy: {policy.name}")
    if action == "openai_bridge" and not policy.allow_openai_bridge:
        raise PermissionError(f"OpenAI bridge disabled by runtime policy: {policy.name}")

    files_count = metadata.get("files_count")
    if files_count is not None and policy.max_files is not None and files_count > policy.max_files:
        raise PermissionError(f"files_count exceeds runtime policy limit: {files_count} > {policy.max_files}")

    total_bytes = metadata.get("total_bytes")
    if total_bytes is not None and policy.max_total_bytes is not None and total_bytes > policy.max_total_bytes:
        raise PermissionError(f"total_bytes exceeds runtime policy limit: {total_bytes} > {policy.max_total_bytes}")


def policy_status() -> dict[str, Any]:
    policy = active_policy()
    return {
        "name": policy.name,
        "require_auth": policy.require_auth,
        "allow_artifact_read": policy.allow_artifact_read,
        "allow_artifact_signing": policy.allow_artifact_signing,
        "allow_streaming": policy.allow_streaming,
        "allow_openai_bridge": policy.allow_openai_bridge,
        "max_files": policy.max_files,
        "max_total_bytes": policy.max_total_bytes,
        "human_review_required": policy.human_review_required,
    }
