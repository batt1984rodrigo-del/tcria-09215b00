#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

try:
    from tcria.engine import TCRIAEngine
except Exception:  # pragma: no cover - lets diagnostic tool report import failures
    TCRIAEngine = None  # type: ignore[assignment]


mcp = FastMCP("tcria-governance")
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "audit"


def _safe_path(value: str) -> Path:
    """Resolve a user path and keep access scoped to this repository tree."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Path outside repository is not allowed: {value}") from exc
    return resolved


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


@mcp.tool()
def health() -> dict[str, Any]:
    """Return MCP server and TCRIA engine health information."""
    return {
        "server": "tcria-governance",
        "repo_root": str(REPO_ROOT),
        "engine_imported": TCRIAEngine is not None,
        "default_output_dir": str(DEFAULT_OUTPUT_DIR),
    }


@mcp.tool()
def audit_paths(
    paths: list[str],
    strict: bool = False,
    output_stem: str = "tcria_mcp_audit",
    include_pdf: bool = True,
    max_files: int | None = None,
    max_total_bytes: int | None = None,
) -> dict[str, Any]:
    """Run the TCRIA governance audit engine against files or directories inside the repository."""
    if TCRIAEngine is None:
        raise RuntimeError("Could not import tcria.engine.TCRIAEngine")
    if not paths:
        raise ValueError("At least one path is required.")

    resolved_paths = [str(_safe_path(p)) for p in paths]
    engine = TCRIAEngine(repo_root=REPO_ROOT)
    result = engine.run_audit(
        input_paths=resolved_paths,
        strict=strict,
        out_dir=DEFAULT_OUTPUT_DIR,
        output_stem=output_stem,
        include_pdf=include_pdf,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
    )
    return _jsonable(result)


@mcp.tool()
def run_governance_pipeline(
    paths: list[str],
    strict: bool = False,
    output_stem: str = "tcria_mcp_pipeline_audit",
    max_files: int | None = None,
    max_total_bytes: int | None = None,
) -> dict[str, Any]:
    """Run the official audit plus complementary blocked-artifact review pipeline."""
    if not paths:
        raise ValueError("At least one path is required.")

    cmd = [
        sys.executable,
        str(REPO_ROOT / "run_governance_pipeline.py"),
        "--repo-root",
        str(REPO_ROOT),
        "--output-dir",
        str(DEFAULT_OUTPUT_DIR.relative_to(REPO_ROOT)),
        "--output-stem",
        output_stem,
    ]
    if strict:
        cmd.append("--strict")
    if max_files is not None:
        cmd.extend(["--max-files", str(max_files)])
    if max_total_bytes is not None:
        cmd.extend(["--max-total-bytes", str(max_total_bytes)])
    for path in paths:
        cmd.extend(["--path", str(_safe_path(path))])

    cp = subprocess.run(cmd, cwd=str(REPO_ROOT), text=True, capture_output=True)
    return {
        "returncode": cp.returncode,
        "stdout": cp.stdout,
        "stderr": cp.stderr,
        "command": cmd,
    }


@mcp.tool()
def read_audit_artifact(path: str) -> dict[str, Any]:
    """Read a generated JSON or Markdown audit artifact from the repository."""
    artifact_path = _safe_path(path)
    if not artifact_path.exists():
        raise FileNotFoundError(str(artifact_path))
    text = artifact_path.read_text(encoding="utf-8")
    if artifact_path.suffix.lower() == ".json":
        return {"path": str(artifact_path), "content": json.loads(text)}
    return {"path": str(artifact_path), "content": text}


if __name__ == "__main__":
    mcp.run()
