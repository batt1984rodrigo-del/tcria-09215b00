from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from tcria.runtime.events import GovernanceEvent


GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class LedgerEntry:
    index: int
    previous_hash: str
    event: dict[str, Any]
    entry_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "event": self.event,
            "entry_hash": self.entry_hash,
        }


class GovernanceLedger:
    def __init__(self) -> None:
        self.entries: list[LedgerEntry] = []

    @property
    def current_hash(self) -> str:
        if not self.entries:
            return GENESIS_HASH
        return self.entries[-1].entry_hash

    def append(self, event: GovernanceEvent) -> LedgerEntry:
        event_payload = event.to_dict()
        previous_hash = self.current_hash
        entry_hash = self._hash_entry(previous_hash, event_payload)
        entry = LedgerEntry(
            index=len(self.entries),
            previous_hash=previous_hash,
            event=event_payload,
            entry_hash=entry_hash,
        )
        self.entries.append(entry)
        return entry

    def to_list(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self.entries]

    @staticmethod
    def _hash_entry(previous_hash: str, event_payload: dict[str, Any]) -> str:
        canonical = json.dumps(
            {"previous_hash": previous_hash, "event": event_payload},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
