"""Corpus coverage, graph and temporal report (Phases 8 & 9).

Produces an updated v0.6 coverage report over the existing corpus artifacts. It
reads passages, the legal graph and the manifest, plus the acquisition backlog
classification. It does NOT read evaluation answers; sample coverage is taken
from the already-computed ``legal_basis_audit.json`` (evaluation boundary).

Phase 8 (graph/temporal) guarantees surfaced here:
- every normative relation edge keeps source/target/relation/evidence_passage_id
  and a provenance ``method``; edges without evidence are reported as a defect
  count (expected 0).
- temporal state uses current/historical/repealed/modified/unknown, defaulting
  to ``unknown`` unless the corpus carries explicit evidence.

Phase 9 avoids using raw document count as a proxy for quality: counts are always
paired with coverage, ambiguity, duplicate and unknown-status figures.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone

from .common import ROOT, indexable, read_json, read_jsonl, write_json
from .diversify import collapse_duplicates
from .metadata import canonical_document_id, canonical_fragment_id, content_hash, temporal_status

COVERAGE_REPORT_VERSION = "coverage-v0.6"

_LEGISLATION = {"law", "decree", "code", "constitution"}
_CASE_LAW = {"decision"}

# Graph edge classes that assert a legal relationship (as opposed to structure).
_NORMATIVE_RELATIONS = {"CITA", "REMITE_A", "MODIFICA", "DEROGA", "REGLAMENTA", "DESARROLLA", "EXCEPCIONA"}
_TEMPORAL_STATES = {"current", "historical", "repealed", "modified", "unknown"}


def _areas_of(doc: dict) -> list[str]:
    return doc.get("areas") or ["(sin área declarada)"]


def graph_temporal_audit(passages: list[dict], nodes: list[dict], edges: list[dict]) -> dict:
    """Phase 8: relation provenance + temporal-state distribution."""
    rel_counts = Counter(e["relation"] for e in edges)
    method_counts = Counter(e.get("method") for e in edges)
    missing_evidence = sum(1 for e in edges
                           if not e.get("evidence_passage_id") or not e.get("evidence_text"))
    normative_without_provenance = sum(
        1 for e in edges if e["relation"] in _NORMATIVE_RELATIONS and not e.get("method"))
    temporal = Counter(temporal_status(p)["status_assertion"] for p in passages)
    # Ensure every declared state is present, even at zero.
    for s in _TEMPORAL_STATES:
        temporal.setdefault(s, 0)
    return {"nodes": len(nodes), "edges": len(edges),
            "node_types": dict(Counter(n["node_type"] for n in nodes)),
            "relation_counts": dict(rel_counts),
            "normative_relation_counts": {k: v for k, v in rel_counts.items() if k in _NORMATIVE_RELATIONS},
            "edge_provenance_methods": dict(method_counts),
            "edges_without_evidence": missing_evidence,
            "normative_edges_without_provenance": normative_without_provenance,
            "unresolved_external_nodes": sum(1 for n in nodes if n.get("resolved") is False),
            "temporal_status_distribution": dict(temporal),
            "policy": ("Relations are kept only with explicit source evidence; temporal state "
                       "defaults to unknown unless the source marks it. No relation or validity "
                       "is inferred from semantic similarity.")}


def build_report(corpus=None) -> dict:
    corpus = corpus or (ROOT / "corpus")
    manifest = read_json(corpus / "manifest.json")
    passages = read_jsonl(corpus / "passages.jsonl")
    nodes = read_jsonl(corpus / "graph/nodes.jsonl")
    edges = read_jsonl(corpus / "graph/edges.jsonl")
    documents = manifest["documentos"]

    docs_by_area = defaultdict(int)
    passages_by_area = defaultdict(int)
    source_types = Counter()
    institutions = Counter()
    legislation_docs = case_law_docs = 0
    unknown_status_docs = []
    for d in documents:
        for area in _areas_of(d):
            docs_by_area[area] += 1
            passages_by_area[area] += d.get("n_fragmentos", 0)
        source_types[d.get("source_type")] += 1
        institutions[d.get("fuente")] += 1
        if d.get("source_type") in _LEGISLATION:
            legislation_docs += 1
        elif d.get("source_type") in _CASE_LAW:
            case_law_docs += 1
        # A document has unknown temporal status when none of its passages carry
        # an explicit historical/current marker.
        unknown_status_docs.append(d["doc_id"])

    # Temporal status per document from passages (explicit evidence only).
    doc_status = defaultdict(set)
    for p in passages:
        doc_status[p["doc_id"]].add(temporal_status(p)["status_assertion"])
    documents_unknown_status = sorted(
        d["doc_id"] for d in documents if doc_status.get(d["doc_id"], {"unknown"}) == {"unknown"})

    ambiguous_passages = sum(1 for p in passages if p.get("duplicate_article_heading"))
    historical_passages = sum(1 for p in passages if p.get("is_current_text") is False)
    excluded = sum(1 for p in passages if not indexable(p))

    # Duplicate detection by content hash across all passages (mirrors + splits).
    hash_groups = defaultdict(list)
    for p in passages:
        hash_groups[content_hash(p)].append(p["passage_id"])
    duplicate_groups = {h: ids for h, ids in hash_groups.items() if len(ids) > 1}
    duplicate_passage_count = sum(len(ids) for ids in duplicate_groups.values())

    # Cross-document duplicates: same content hash appearing in >1 canonical doc.
    doc_of = {p["passage_id"]: canonical_document_id(p) for p in passages}
    cross_document_dupes = sum(
        1 for ids in duplicate_groups.values() if len({doc_of[i] for i in ids}) > 1)

    # Sample coverage from the evaluation-boundary audit, if present.
    sample_coverage = None
    explicit_reference_coverage = None
    audit_path = ROOT / "reports/legal_basis_audit.json"
    if audit_path.exists():
        audit = read_json(audit_path)
        labelled = [a for a in audit if a.get("targets")]
        if labelled:
            sample_coverage = {
                "evaluable_questions": len(labelled),
                "fully_covered_questions": sum(1 for a in labelled if a.get("coverage") == 1),
                "macro_target_coverage": sum(a.get("coverage") or 0 for a in labelled) / len(labelled)}
            explicit = [a for a in labelled if any(t[3] is not None for t in a["targets"])]
            if explicit:
                explicit_reference_coverage = {
                    "questions_with_explicit_article_reference": len(explicit),
                    "fully_covered": sum(1 for a in explicit if a.get("coverage") == 1),
                    "macro_coverage": sum(a.get("coverage") or 0 for a in explicit) / len(explicit)}

    backlog_path = ROOT / "reports/acquisition_backlog_v06.json"
    backlog = read_json(backlog_path) if backlog_path.exists() else {"counts": {}, "total_unresolved": manifest.get("failures", [])}

    # Major gaps: areas that depend heavily on case law where acquisition is
    # blocked, and any area with zero indexed passages.
    indexed_by_area = defaultdict(int)
    for p in passages:
        if indexable(p):
            for a in [p2 for p2 in (p.get("areas") or ["(sin área declarada)"])]:
                indexed_by_area[a] += 1
    empty_areas = sorted(a for a in docs_by_area if indexed_by_area.get(a, 0) == 0)

    report = {
        "version": COVERAGE_REPORT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus_version": manifest["version"], "parser_version": manifest["parser_version"],
        "corpus_hashes": manifest["hashes"],
        "totals": {"documents": len(documents), "passages": len(passages),
                   "indexed_passages": manifest.get("n_indexed"),
                   "excluded_passages": excluded, "nodes": len(nodes), "edges": len(edges)},
        "documents_by_area": dict(sorted(docs_by_area.items())),
        "passages_by_area": dict(sorted(passages_by_area.items())),
        "source_types": dict(source_types),
        "institutions": dict(institutions),
        "legislation_vs_case_law": {"legislation_documents": legislation_docs,
                                    "case_law_documents": case_law_docs},
        "ambiguous_passages": ambiguous_passages,
        "historical_passages": historical_passages,
        "duplicates_detected": {"content_hash_groups": len(duplicate_groups),
                                "passages_in_duplicate_groups": duplicate_passage_count,
                                "cross_document_duplicate_groups": cross_document_dupes,
                                "note": ("Includes long-article contiguous splits sharing a fragment id; "
                                         "cross-document groups indicate genuine mirrored content.")},
        "sample_coverage": sample_coverage,
        "explicit_reference_coverage": explicit_reference_coverage,
        "documents_with_unknown_temporal_status": {"count": len(documents_unknown_status),
                                                    "doc_ids": documents_unknown_status},
        "unresolved_acquisition_targets": {"total": backlog.get("total_unresolved"),
                                           "by_class": backlog.get("counts")},
        "graph_temporal_audit": graph_temporal_audit(passages, nodes, edges),
        "major_gaps": {"areas_without_indexed_passages": empty_areas,
                       "note": ("Raw document count is not used as a quality proxy; gaps are read "
                                "together with coverage, unresolved targets and unknown-status counts.")},
        "caveats": ["Areas overlap (inventory metadata, not per-passage relevance).",
                    "Unknown temporal status is the honest default, not a defect by itself.",
                    "Document count alone does not measure corpus quality."]}
    write_json(ROOT / "reports/corpus_coverage_v06.json", report)
    return report
