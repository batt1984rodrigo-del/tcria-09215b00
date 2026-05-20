from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
EVENT_BUS_PATH = REPO_ROOT / "output" / "audit" / "governance_event_bus.jsonl"


class GovernanceEventBus:
    """Simple append-only governance event bus.

    This intentionally uses JSONL so events remain:
    - immutable-ish
    - auditable
    - stream-friendly
    - easy to ship into SIEM/log pipelines
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or EVENT_BUS_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": int(time.time()),
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return rows[-limit:]
