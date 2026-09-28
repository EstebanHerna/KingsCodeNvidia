"""Metadata-aware retrieval experiments R6/R7/R8 (Phase 6) — Member A only.

These are optional, deterministic experiments layered on top of the public
``retrieve(...)`` contract. They never replace R0–R5 (owned by member B's
frozen-evidence harness) and never change the default retrieval path.

- R6 = R3 + exact legal locator / metadata features (soft prior, candidate union)
- R7 = document-first -> passage retrieval
- R8 = R3 + diversification

Explicit-reference policy (Ley X de YYYY / Artículo N / Sentencia / Código):
    exact structured locator  +  general BM25/dense retrieval
        -> candidate union -> ranking
Hard metadata filters are NOT the default; metadata only re-scores a union.

Each experiment yields the same passage-shaped records as ``retrieve``, plus an
auditable ``experiment`` block describing which features fired. Runnable on CPU
with ``mode='bm25'``; the neural (hybrid+rerank) variants are prepared for the
target GPU and require an explicit mode, exactly like the existing benchmark.
"""
from __future__ import annotations

from .diversify import (
    collapse_duplicates,
    diversify,
    locator_boost,
    metadata_features,
    parse_reference,
)
from .metadata import canonical_document_id
from .retrieval import Retriever

EXPERIMENTS = ("R6", "R7", "R8")


def _rescore(passages: list[dict], question: str, ref: dict) -> list[dict]:
    """Attach metadata features + bounded locator boost; stable re-sort."""
    scored = []
    for p in passages:
        feats = metadata_features(question, p, ref)
        boost = locator_boost(feats)
        q = dict(p)
        base = p.get("score", 0) or 0
        q["metadata_features"] = feats
        q["locator_boost"] = boost
        q["score_with_metadata"] = base + boost
        scored.append(q)
    scored.sort(key=lambda x: (-x["score_with_metadata"], x["passage_id"]))
    return scored


def run_r6(retriever: Retriever, question: str, k: int = 8, *, candidate_multiplier: int = 4) -> list[dict]:
    """R6: exact locator + general retrieval -> candidate union -> metadata rerank.

    Never filters by metadata: the union is the general retrieval candidates; the
    metadata features only provide a bounded additive prior over that union.
    """
    ref = parse_reference(question)
    pool = retriever.retrieve(question, max(k * candidate_multiplier, k), "off")
    ranked = _rescore(pool, question, ref)
    for rank, p in enumerate(ranked[:k], 1):
        p["experiment"] = {"name": "R6", "reference": ref, "rank": rank}
    return ranked[:k]


def run_r7(retriever: Retriever, question: str, k: int = 8, *, doc_pool: int = 24) -> list[dict]:
    """R7: document-first, then passage retrieval within the leading documents.

    Deterministic two-stage: identify the leading canonical documents from a
    general pass, then keep passages that belong to those documents, ordered by
    the document's best rank then the passage score. No labels, no GPU required
    in bm25 mode.
    """
    ref = parse_reference(question)
    pool = retriever.retrieve(question, max(doc_pool, k), "off")
    doc_rank: dict[str, int] = {}
    for i, p in enumerate(pool):
        doc = canonical_document_id(p)
        doc_rank.setdefault(doc, i)
    def key(p):
        return (doc_rank.get(canonical_document_id(p), 10_000), -(p.get("score", 0) or 0), p["passage_id"])
    ordered = sorted(pool, key=key)
    for rank, p in enumerate(ordered[:k], 1):
        p["experiment"] = {"name": "R7", "reference": ref, "rank": rank,
                           "document_rank": doc_rank.get(canonical_document_id(p))}
    return ordered[:k]


def run_r8(retriever: Retriever, question: str, k: int = 8, *, level: str = "document",
           max_per_group: int = 2) -> list[dict]:
    """R8: R3-style retrieval + diversification (collapse mirrors, then diversify)."""
    ref = parse_reference(question)
    pool = retriever.retrieve(question, max(k * 4, k), "off")
    collapsed = collapse_duplicates(pool, level="content")
    diversified = diversify(collapsed, k, level=level, max_per_group=max_per_group)
    for rank, p in enumerate(diversified, 1):
        p["experiment"] = {"name": "R8", "reference": ref, "rank": rank,
                           "diversify": {"level": level, "max_per_group": max_per_group}}
    return diversified


def run_experiment(name: str, retriever: Retriever, question: str, k: int = 8, **kw) -> list[dict]:
    if name == "R6":
        return run_r6(retriever, question, k, **kw)
    if name == "R7":
        return run_r7(retriever, question, k, **kw)
    if name == "R8":
        return run_r8(retriever, question, k, **kw)
    raise ValueError(f"Unknown experiment {name!r}; expected one of {EXPERIMENTS}")
