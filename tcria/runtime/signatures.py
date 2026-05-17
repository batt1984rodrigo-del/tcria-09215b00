from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ArtifactSignature:
    artifact_path: str
    sha256: str
    size_bytes: int
    algorithm: str = "sha256"

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_path": self.artifact_path,
            "algorithm": self.algorithm,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


def sign_artifact(path: str | Path) -> ArtifactSignature:
    artifact_path = Path(path).expanduser().resolve()
    digest = hashlib.sha256()
    with artifact_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return ArtifactSignature(
        artifact_path=str(artifact_path),
        sha256=digest.hexdigest(),
        size_bytes=artifact_path.stat().st_size,
    )
