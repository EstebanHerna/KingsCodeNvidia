"""Evidence-set diagnostics for multi-view and graph retrieval experiments.

These functions consume rankings only. Callers must freeze every ranking before
loading annotation/gold, following the benchmark runner's leakage boundary.
"""
from __future__ import annotations


def _validate_sets(minimal_evidence_sets: list[list[str]]) -> list[set[str]]:
    if not isinstance(minimal_evidence_sets, list) or not minimal_evidence_sets:
        raise ValueError("at least one minimal evidence set is required")
    result = []
    for evidence_set in minimal_evidence_sets:
        if not isinstance(evidence_set, list) or not evidence_set:
            raise ValueError("minimal evidence sets must be non-empty lists")
        if any(not isinstance(pid, str) or not pid for pid in evidence_set):
            raise ValueError("passage IDs must be non-empty strings")
        if len(evidence_set) != len(set(evidence_set)):
            raise ValueError("duplicate passage ID within a minimal evidence set")
        result.append(set(evidence_set))
    return result


def _validate_k(k: int) -> None:
    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        raise ValueError("k must be a nonnegative integer")


def evidence_completeness(ranking: list[str], minimal_evidence_sets: list[list[str]], k: int) -> float:
    """Return best sufficient-set coverage fraction at k; accepts alternatives."""
    _validate_k(k)
    sets = _validate_sets(minimal_evidence_sets)
    found = set(ranking[:k])
    return max(len(found & required) / len(required) for required in sets)


def oracle_multi_view_recall(view_rankings: list[list[str]], minimal_evidence_sets: list[list[str]], k: int) -> float:
    """Best evidence-set coverage after taking the union of each view's top-k."""
    if not isinstance(view_rankings, list) or not view_rankings:
        raise ValueError("at least one view ranking is required")
    _validate_k(k)
    if any(not isinstance(row, list) for row in view_rankings):
        raise TypeError("each view ranking must be a list of passage IDs")
    union = list(dict.fromkeys(pid for ranking in view_rankings for pid in ranking[:k]))
    return evidence_completeness(union, minimal_evidence_sets, len(union))


def fusion_loss(view_rankings: list[list[str]], fused_ranking: list[str],
                minimal_evidence_sets: list[list[str]], k: int) -> dict:
    """Report oracle-minus-fusion evidence coverage and any fusion gain."""
    oracle = oracle_multi_view_recall(view_rankings, minimal_evidence_sets, k)
    fused = evidence_completeness(fused_ranking, minimal_evidence_sets, k)
    return {"oracle_multi_view_recall": oracle, "fused_evidence_completeness": fused,
            "fusion_loss": max(0.0, oracle - fused), "fusion_gain": max(0.0, fused - oracle)}


def graph_recovery_rate(initial_rankings: list[list[str]], graph_rankings: list[list[str]],
                        minimal_evidence_sets: list[list[str]], k: int) -> dict:
    """Measure graph recovery for questions with ranked initial and graph outcomes."""
    if not initial_rankings or len(initial_rankings) != len(graph_rankings):
        raise ValueError("initial and graph rankings must have the same nonzero question count")
    _validate_k(k)
    before = [evidence_completeness(r, minimal_evidence_sets, k) for r in initial_rankings]
    after = [evidence_completeness(r, minimal_evidence_sets, k) for r in graph_rankings]
    eligible = [i for i, score in enumerate(before) if score < 1.0]
    recovered = sum(after[i] == 1.0 for i in eligible)
    return {"questions": len(before), "initially_incomplete": len(eligible),
            "recovered_complete": recovered,
            "graph_recovery_rate": recovered / len(eligible) if eligible else None,
            "mean_evidence_completeness_delta": sum(a - b for a, b in zip(after, before)) / len(before)}
