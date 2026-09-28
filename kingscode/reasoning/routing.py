"""Two-pass graph routing through A's public API; no index/graph internals."""
from __future__ import annotations

from .policy import assess_evidence
from .query import NormalizedQuery, normalize_query

ROUTER_VERSION = "legal-router-v1"


def route_graph(question: str | NormalizedQuery, flat_passages: list[dict] | None) -> str:
    q = question if isinstance(question, NormalizedQuery) else normalize_query(question)
    if q.signals:
        return "on"
    if flat_passages is None:  # Callback used outside the two-pass coordinator.
        return "off"
    if not flat_passages:
        return "on"
    if not assess_evidence(q, flat_passages).sufficient:
        return "auto"
    return "off"


class RetrieverGraphRouter:
    """Boolean callback expected by A, with a bound decision for this query.

    A would treat the string 'off' as truthy. This adapter always returns bool.
    Use one adapter per sequential pipeline instance, not shared across threads.
    """
    def __init__(self):
        self._question = None
        self._decision = "off"

    def bind(self, question: str, decision: str) -> None:
        if decision not in {"off", "auto", "on"}:
            raise ValueError("Invalid graph decision")
        self._question, self._decision = question, decision

    def __call__(self, question: str) -> bool:
        return self._decision != "off" if question == self._question else route_graph(question, None) == "on"
