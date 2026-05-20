from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cache-Control": "no-store",
}


async def security_headers_middleware(request: Any, call_next: Callable[[Any], Awaitable[Any]]) -> Any:
    response = await call_next(request)
    for key, value in SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    return response
