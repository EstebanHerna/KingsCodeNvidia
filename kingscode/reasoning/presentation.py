"""Judge-facing view of one answer, separate from the debug trace (plan B8).

The passages shown are exactly the submission's pasajes_recuperados, in order.
A passage is "cited" when a norm cited in the answer is found in its text by the
official extractor; "declared_used" when the decoder attributed it explicitly.
Raw/normalized model text never reaches the judge-facing view.
"""
from __future__ import annotations

from copy import deepcopy

from .batch import answer_text
from .official import official_bodies

HIDDEN_TRACE_KEYS = {"raw_response", "normalized_response"}


def _scrub(value):
    if isinstance(value, dict):
        return {k: _scrub(v) for k, v in value.items() if k not in HIDDEN_TRACE_KEYS}
    if isinstance(value, list):
        return [_scrub(v) for v in value]
    return value


def view_model(row: dict, trace: dict) -> dict:
    diagnostics = trace.get("diagnostics") or {}
    used = set(diagnostics.get("evidence_ids_used") or [])
    cited = official_bodies(answer_text(row))
    cards = []
    for rank, p in enumerate(row["pasajes_recuperados"], 1):
        bodies = official_bodies(p.get("texto", ""))
        cards.append({"rank": rank, "passage_id": p.get("passage_id"), "norm_name": p.get("norm_name"),
                      "article": p.get("article"), "source_url": p.get("source_url"), "texto": p.get("texto", ""),
                      "cited": bool(bodies & cited), "declared_used": p.get("passage_id") in used})
    supported = set().union(*(official_bodies(p.get("texto", "")) for p in row["pasajes_recuperados"][:10])) if row["pasajes_recuperados"] else set()
    return {"abstained": row["abstencion"], "abstention_reason": trace.get("abstention_reason"),
            "abstention_source": trace.get("abstention_source"),
            "cited_norms": [{"body": list(b), "supported": b in supported} for b in sorted(cited, key=str)],
            "cited_passages": [c for c in cards if c["cited"] or c["declared_used"]],
            "other_passages": [c for c in cards if not (c["cited"] or c["declared_used"])],
            "submission": deepcopy(row)}


def debug_trace(trace: dict) -> dict:
    """Operator-only trace: everything except raw model text."""
    return _scrub(trace)
