"""Deduplication, diversification and metadata retrieval features (Phases 4, 6).

Everything here operates on the *result* of the existing public ``retrieve(...)``
contract. Nothing changes the default retrieval path: these are opt-in,
deterministic, auditable post-processing steps suitable for ablation. Provenance
is never discarded — duplicates are grouped, not deleted, and the grouping keeps
every source mirror for audit.

Key ideas
---------
- Group retrieved passages by ``canonical_document_id`` / ``canonical_fragment_id``
  / ``content_hash`` so top-k is not dominated by one legal fragment mirrored
  across several official sources.
- Diversification is configurable and defaults to OFF; it is only meant to be
  measured as an ablation, never silently made the default.
- Metadata features for an explicit legal reference (Ley X de YYYY, Artículo N,
  Sentencia ..., Código ...) are computed as deterministic booleans/ints. They
  are optional signals for a *soft* re-rank of a candidate union, never a hard
  metadata filter.
"""
from __future__ import annotations

import re

from .metadata import canonical_document_id, canonical_fragment_id, content_hash

DIVERSIFY_VERSION = "diversify-v0.6"

# Explicit reference detectors. Deterministic, finite, auditable — no LLM.
_NORM_RE = re.compile(r"\b(ley|decreto(?:\s+ley)?)\s+(\d{1,5})\s+de\s+(\d{4})\b", re.I)
_ARTICLE_RE = re.compile(r"\bart[ií]culo?s?\s+(\d+[a-z]?(?:\s*[.,]\s*\d+)*)", re.I)
_DECISION_RE = re.compile(r"\b(sentencia\s+)?((?:C|T|SU|SL|SP|SC|AC|AP)\s*-?\s*\d+)\s*(?:de\s+|/)?\s*(\d{4})\b", re.I)
_CODE_RE = re.compile(r"\bc[oó]digo\s+([a-záéíóúñ ]+?)(?=[.,;:]|\bde\b|$)", re.I)


def dedup_key(passage: dict, level: str = "fragment") -> str:
    """Return the grouping key for a passage at the requested level."""
    if level == "document":
        return canonical_document_id(passage)
    if level == "fragment":
        return canonical_fragment_id(passage)
    if level == "content":
        return content_hash(passage)
    raise ValueError("level must be document, fragment or content")


def group_duplicates(passages: list[dict], level: str = "content") -> dict[str, list[dict]]:
    """Group passages by dedup key, preserving order and all provenance."""
    groups: dict[str, list[dict]] = {}
    for p in passages:
        groups.setdefault(dedup_key(p, level), []).append(p)
    return groups


def collapse_duplicates(passages: list[dict], level: str = "content") -> list[dict]:
    """Keep the first (highest-ranked) passage per key, recording mirrors.

    The kept passage gains a ``duplicate_group`` field listing the passage_ids and
    source_urls of the collapsed mirrors, so no provenance is lost.
    """
    seen: dict[str, dict] = {}
    order: list[str] = []
    for p in passages:
        key = dedup_key(p, level)
        if key not in seen:
            kept = dict(p)
            kept["duplicate_group"] = {"level": level, "key": key,
                                       "members": [{"passage_id": p.get("passage_id"),
                                                    "source_url": p.get("source_url")}]}
            seen[key] = kept
            order.append(key)
        else:
            seen[key]["duplicate_group"]["members"].append(
                {"passage_id": p.get("passage_id"), "source_url": p.get("source_url")})
    return [seen[k] for k in order]


def diversify(passages: list[dict], k: int, *, level: str = "document", max_per_group: int = 2) -> list[dict]:
    """Prevent one legal work/fragment from dominating the top-k.

    Deterministic round-robin: walk the ranked list and cap how many passages of
    the same group appear before pulling from other groups; overflow is appended
    afterwards so nothing is lost. ``max_per_group`` and ``level`` are the
    ablation knobs. This function is never applied by default.
    """
    if max_per_group < 1:
        raise ValueError("max_per_group must be >= 1")
    counts: dict[str, int] = {}
    primary: list[dict] = []
    overflow: list[dict] = []
    for p in passages:
        key = dedup_key(p, level)
        counts[key] = counts.get(key, 0) + 1
        (primary if counts[key] <= max_per_group else overflow).append(p)
    return (primary + overflow)[:k]


# ---------------------------------------------------------------------------
# Explicit reference parsing + metadata features (Phase 6)
# ---------------------------------------------------------------------------

def parse_reference(question: str) -> dict:
    """Extract explicit structured legal locators from a query. Deterministic."""
    norms = [{"kind": ("decreto" if m.group(1).lower().startswith("decreto") else "ley"),
              "number": str(int(m.group(2))), "year": m.group(3)} for m in _NORM_RE.finditer(question)]
    articles = []
    for m in _ARTICLE_RE.finditer(question):
        raw = re.sub(r"\s+", "", m.group(1)).replace(",", ".")
        articles.append(raw)
    decisions = [{"id": re.sub(r"\s*-?\s*", "-", m.group(2).upper(), count=1).replace(" ", ""),
                  "year": m.group(3)} for m in _DECISION_RE.finditer(question)]
    codes = [m.group(1).strip() for m in _CODE_RE.finditer(question)]
    return {"norms": norms, "articles": articles, "decisions": decisions, "codes": codes,
            "has_explicit_reference": bool(norms or decisions or (codes and articles) or articles)}


def _norm_matches(passage: dict, ref: dict) -> bool:
    body = passage.get("canonical_body") or []
    if len(body) < 3:
        return False
    kind, number, year = body[0], body[1], body[2]
    for n in ref["norms"]:
        if kind in {n["kind"], "law" if n["kind"] == "ley" else "decree"} and str(number) == n["number"] and str(year) == n["year"]:
            return True
    return False


def _decision_matches(passage: dict, ref: dict) -> bool:
    doc = canonical_document_id(passage)
    for d in ref["decisions"]:
        sala_seq = d["id"].replace("-", "").lower()
        if doc.endswith(f":{sala_seq}:{d['year']}") or f":{sala_seq}:" in doc + ":":
            if str(d["year"]) in doc:
                return True
    return False


def metadata_features(question: str, passage: dict, ref: dict | None = None) -> dict:
    """Deterministic, auditable metadata features for one candidate passage.

    All features are optional signals. None of them filters a candidate out.
    ``graph_distance`` is left as ``None`` here because it depends on the graph
    traversal already recorded in ``passage['retrieval']['graph_evidence']``; it
    is populated by the experiment layer when available.
    """
    ref = ref or parse_reference(question)
    article = (passage.get("article") or "")
    article_norm = re.sub(r"\s+", "", str(article)).replace(",", ".").lower()
    exact_article = bool(article_norm) and any(article_norm == a.lower() for a in ref["articles"])
    exact_norm = _norm_matches(passage, ref) or _decision_matches(passage, ref)
    source_type = passage.get("source_type")
    ref_wants_decision = bool(ref["decisions"])
    ref_wants_norm = bool(ref["norms"])
    source_type_match = ((ref_wants_decision and source_type == "decision")
                         or (ref_wants_norm and source_type in {"law", "decree", "code"}))
    graph_ev = (passage.get("retrieval") or {}).get("graph_evidence") or []
    return {"exact_norm_match": exact_norm,
            "exact_article_match": exact_article,
            "same_document": exact_norm,
            "source_type_match": bool(source_type_match),
            "temporal_match": passage.get("is_current_text") is not False,
            "graph_distance": 0 if graph_ev else None}


def locator_boost(features: dict) -> float:
    """Small, bounded, declared additive boost from metadata features.

    Deterministic and auditable. Used only by the R6 experiment as a soft prior
    over the candidate union; it never removes candidates and is bounded so it
    cannot swamp the base retrieval score.
    """
    weights = {"exact_norm_match": 0.6, "exact_article_match": 0.3,
               "source_type_match": 0.05, "temporal_match": 0.05}
    return round(sum(w for key, w in weights.items() if features.get(key)), 6)
