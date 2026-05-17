from __future__ import annotations

from enum import Enum


class GovernanceState(str, Enum):
    CREATED = "CREATED"
    INGESTED = "INGESTED"
    CLASSIFIED = "CLASSIFIED"
    UNDER_REVIEW = "UNDER_REVIEW"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    BLOCKED = "BLOCKED"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"


_ALLOWED_TRANSITIONS: dict[GovernanceState, set[GovernanceState]] = {
    GovernanceState.CREATED: {GovernanceState.INGESTED},
    GovernanceState.INGESTED: {GovernanceState.CLASSIFIED},
    GovernanceState.CLASSIFIED: {GovernanceState.UNDER_REVIEW},
    GovernanceState.UNDER_REVIEW: {GovernanceState.POLICY_EVALUATED},
    GovernanceState.POLICY_EVALUATED: {GovernanceState.BLOCKED, GovernanceState.APPROVED},
    GovernanceState.BLOCKED: {GovernanceState.COMPLETED},
    GovernanceState.APPROVED: {GovernanceState.COMPLETED},
    GovernanceState.COMPLETED: set(),
}


class GovernanceStateMachine:
    def __init__(self) -> None:
        self.current = GovernanceState.CREATED
        self.history: list[str] = [self.current.value]

    def transition(self, next_state: GovernanceState) -> GovernanceState:
        allowed = _ALLOWED_TRANSITIONS[self.current]
        if next_state not in allowed:
            raise ValueError(f"Invalid governance transition: {self.current.value} -> {next_state.value}")
        self.current = next_state
        self.history.append(next_state.value)
        return self.current

    def to_dict(self) -> dict[str, object]:
        return {"current": self.current.value, "history": self.history}
