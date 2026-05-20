from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from tcria.engine import TCRIAEngine

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "audit"
AUDIT_LOG_PATH = REPO_ROOT / "output" / "audit" / "mcp_audit_events.jsonl"
ARTIFACT_SIGNATURES_PATH = REPO_ROOT / "output" / "audit" / "artifact_signatures.jsonl"
JWT_ALGORITHM = os.getenv("TCRIA_MCP_JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("TCRIA_MCP_JWT_ISSUER", "tcria-mcp-gateway")
JWT_SECRET_ENV = "TCRIA_MCP_JWT_SECRET"
SIGNING_SECRET_ENV = "TCRIA_MCP_SIGNING_SECRET"
REQUIRE_AUTH = os.getenv("TCRIA_MCP_REQUIRE_AUTH", "true").lower() not in {"0", "false", "no"}

app = FastAPI(
    title="TCRIA MCP HTTP Gateway",
    version="0.3.0",
    description="Production-oriented HTTP/SSE gateway for TCRIA MCP governance workflows.",
)
engine = TCRIAEngine(repo_root=REPO_ROOT)


class AuditPathsRequest(BaseModel):
    paths: list[str]
    strict: bool = True
    output_stem: str = "tcria_mcp_http_audit"
    include_pdf: bool = True
    max_files: int | None = None
    max_total_bytes: int | None = None


class ArtifactReadRequest(BaseModel):
    path: str


class SignArtifactRequest(BaseModel):
    path: str
    purpose: str = "governance-artifact"


class ResponsesProxyRequest(BaseModel):
    input: str
    model: str = "gpt-4.1-mini"
    server_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def _now() -> int:
    return int(time.time())


def _request_id() -> str:
    return secrets.token_hex(16)


def _safe_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Path outside repository is not allowed: {value}") from exc
    return resolved


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _log_event(event_type: str, request: Request | None = None, **payload: Any) -> dict[str, Any]:
    event = {
        "event_id": _request_id(),
        "event_type": event_type,
        "timestamp": _now(),
        "payload": _jsonable(payload),
    }
    if request is not None:
        event["request"] = {
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else None,
        }
    _append_jsonl(AUDIT_LOG_PATH, event)
    return event


def _artifact_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _sign_payload(payload: dict[str, Any]) -> str:
    signing_secret = os.getenv(SIGNING_SECRET_ENV)
    if not signing_secret:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Set {SIGNING_SECRET_ENV} before signing artifacts.")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(signing_secret.encode("utf-8"), canonical, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")


def _decode_authorization(request: Request) -> dict[str, Any]:
    if not REQUIRE_AUTH:
        return {"sub": "auth-disabled", "role": "operator"}
    jwt_secret = os.getenv(JWT_SECRET_ENV)
    if not jwt_secret:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Set {JWT_SECRET_ENV} before enabling authenticated MCP gateway access.")
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = header.split(" ", 1)[1].strip()
    try:
        return jwt.decode(token, jwt_secret, algorithms=[JWT_ALGORITHM], issuer=JWT_ISSUER)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token: {exc}") from exc


def require_operator(request: Request) -> dict[str, Any]:
    claims = _decode_authorization(request)
    if claims.get("role") not in {"operator", "admin", "auditor"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient role")
    return claims


@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        _log_event("http_request", request, status_code=response.status_code, duration_ms=round((time.time() - start) * 1000, 2))
        return response
    except Exception as exc:
        _log_event("http_error", request, error=str(exc), duration_ms=round((time.time() - start) * 1000, 2))
        raise


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "tcria-mcp-http-gateway",
        "auth_required": REQUIRE_AUTH,
        "repo_root": str(REPO_ROOT),
    }


@app.post("/tools/audit-paths")
def audit_paths(payload: AuditPathsRequest, request: Request, claims: dict[str, Any] = Depends(require_operator)) -> dict[str, Any]:
    if not payload.paths:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "At least one path is required.")
    paths = [str(_safe_path(p)) for p in payload.paths]
    result = engine.run_audit(
        input_paths=paths,
        strict=payload.strict,
        out_dir=DEFAULT_OUTPUT_DIR,
        output_stem=payload.output_stem,
        include_pdf=payload.include_pdf,
        max_files=payload.max_files,
        max_total_bytes=payload.max_total_bytes,
    )
    _log_event("audit_paths_completed", request, subject=claims.get("sub"), paths=paths, artifacts=result.get("artifacts"))
    return _jsonable(result)


@app.post("/tools/read-artifact")
def read_artifact(payload: ArtifactReadRequest, request: Request, claims: dict[str, Any] = Depends(require_operator)) -> dict[str, Any]:
    path = _safe_path(payload.path)
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Artifact not found: {path}")
    text = path.read_text(encoding="utf-8")
    _log_event("artifact_read", request, subject=claims.get("sub"), path=str(path))
    if path.suffix.lower() == ".json":
        return {"path": str(path), "content": json.loads(text)}
    return {"path": str(path), "content": text}


@app.post("/artifacts/sign")
def sign_artifact(payload: SignArtifactRequest, request: Request, claims: dict[str, Any] = Depends(require_operator)) -> dict[str, Any]:
    path = _safe_path(payload.path)
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Artifact not found: {path}")
    signature_payload = {
        "path": str(path.relative_to(REPO_ROOT)),
        "sha256": _artifact_digest(path),
        "purpose": payload.purpose,
        "signed_at": _now(),
        "signed_by": claims.get("sub"),
    }
    signature_payload["signature"] = _sign_payload(signature_payload)
    _append_jsonl(ARTIFACT_SIGNATURES_PATH, signature_payload)
    _log_event("artifact_signed", request, subject=claims.get("sub"), signature=signature_payload)
    return signature_payload


@app.get("/events/audit-log")
def audit_log(claims: dict[str, Any] = Depends(require_operator)) -> dict[str, Any]:
    if not AUDIT_LOG_PATH.exists():
        return {"events": []}
    events = [json.loads(line) for line in AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {"events": events[-200:]}


async def _sse_event(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(_jsonable(data), ensure_ascii=False)}\n\n"


@app.post("/stream/audit-paths")
async def stream_audit_paths(payload: AuditPathsRequest, request: Request, claims: dict[str, Any] = Depends(require_operator)) -> StreamingResponse:
    async def generator() -> AsyncIterator[str]:
        yield await _sse_event("started", {"message": "audit started", "paths": payload.paths})
        try:
            result = await asyncio.to_thread(audit_paths, payload, request, claims)
            yield await _sse_event("completed", result)
        except Exception as exc:
            yield await _sse_event("error", {"error": str(exc)})
    return StreamingResponse(generator(), media_type="text/event-stream")


@app.post("/openai/responses/stream")
async def openai_responses_stream(payload: ResponsesProxyRequest, request: Request, claims: dict[str, Any] = Depends(require_operator)) -> StreamingResponse:
    async def generator() -> AsyncIterator[str]:
        request_event = _log_event("openai_responses_stream_requested", request, subject=claims.get("sub"), model=payload.model, metadata=payload.metadata)
        yield await _sse_event("metadata", {"event_id": request_event["event_id"], "model": payload.model})
        yield await _sse_event("tool_hint", {
            "type": "mcp",
            "server_url": payload.server_url or os.getenv("TCRIA_MCP_PUBLIC_URL", "http://localhost:8000/mcp"),
            "recommended_tools": ["audit_paths", "run_governance_pipeline", "read_audit_artifact"],
        })
        yield await _sse_event("input", {"input": payload.input})
        yield await _sse_event("completed", {"status": "ready_for_openai_responses_bridge"})
    return StreamingResponse(generator(), media_type="text/event-stream")


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    _log_event("http_exception", request, status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
