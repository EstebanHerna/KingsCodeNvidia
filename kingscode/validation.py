"""Fail-closed artifact, provenance, graph and official-integrity validation."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import math

from jsonschema import Draft202012Validator
from .common import ROOT, file_hash, indexable, read_json, read_jsonl, write_json


def official_integrity() -> dict:
    results = {}
    for line in (ROOT / "docs/OFFICIAL_SHA256.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            expected, rel = line.split("  ", 1)
            actual = file_hash(ROOT / rel)
            if actual != expected:
                raise ValueError(f"Official starter pack modified: {rel}")
            results[rel] = actual
    return results


def verify(corpus: Path) -> dict:
    official = official_integrity()
    manifest = read_json(corpus / "manifest.json")
    for rel, expected in manifest["hashes"].items():
        if file_hash(corpus / rel) != expected:
            raise ValueError(f"Corpus hash mismatch: {rel}")
    if file_hash(corpus / "index/bm25.json") != manifest["bm25_sha256"]:
        raise ValueError("BM25 hash mismatch")
    passages = read_jsonl(corpus / "passages.jsonl")
    nodes = read_jsonl(corpus / "graph/nodes.jsonl")
    edges = read_jsonl(corpus / "graph/edges.jsonl")
    by_id = {p["passage_id"]: p for p in passages}
    node_ids = {n["node_id"] for n in nodes}
    if len(by_id) != len(passages) or len(node_ids) != len(nodes):
        raise ValueError("Duplicate passage/node IDs")
    texts = {}
    for d in manifest["documentos"]:
        for key, expected in [("raw_path", d["source_sha256"]), ("clean_path", d["sha256"])]:
            if file_hash(ROOT / d[key]) != expected:
                raise ValueError(f"Document provenance hash mismatch: {d['doc_id']}/{key}")
        if not d.get("tls_verified") or d["http_status"] != 200:
            raise ValueError("Unverified source transport")
        texts[d["doc_id"]] = (ROOT / d["clean_path"]).read_text(encoding="utf-8")
    validator = Draft202012Validator(read_json(ROOT / "config/corpus_passage.schema.json"))
    forbidden = {"legal_basis", "respuesta_correcta", "texto_respuesta_correcta", "expected_answer"}
    for p in passages:
        validator.validate(p)
        if forbidden & p.keys():
            raise ValueError("Evaluation label leaked into passage")
        expected = p["text_prefix"] + texts[p["doc_id"]][p["clean_start"]:p["clean_end"]]
        if p["text"] != expected:
            raise ValueError(f"Offset/text mismatch: {p['passage_id']}")
        if not set(p["graph_node_ids"]) <= node_ids:
            raise ValueError("Passage has dangling graph nodes")
        if p["retrieval_eligible"] != (not p["index_exclusion_reasons"]):
            raise ValueError("Index eligibility and exclusion reasons disagree")
        if p["duplicate_article_heading"] and indexable(p):
            raise ValueError("Ambiguous article was indexed")
    graph_schema = read_json(ROOT / "config/legal_graph.schema.json")
    for n in nodes:
        if not set(graph_schema["node_required_fields"]) <= n.keys() or n["node_type"] not in graph_schema["node_types"]:
            raise ValueError("Invalid graph node")
    for e in edges:
        if not set(graph_schema["edge_required_fields"]) <= e.keys() or e["relation"] not in graph_schema["edge_types"]:
            raise ValueError("Invalid graph edge")
        if e["source"] not in node_ids or e["target"] not in node_ids or e["evidence_passage_id"] not in by_id:
            raise ValueError("Dangling graph edge")
        if e["evidence_text"] not in by_id[e["evidence_passage_id"]]["text"]:
            raise ValueError(f"Graph evidence is not verbatim in passage: {e}")
    from .retrieval import Retriever
    r = Retriever(corpus)
    queries = ["libertad igualdad Constitución", "contrato de trabajo salario", "artículo modificado remite"]
    for q in queries:
        for mode in ["off", "auto", "on"]:
            first = r.retrieve(q, 8, mode)
            second = r.retrieve(q, 8, mode)
            if first != second:
                raise ValueError("Retrieval nondeterminism")
            if len(first) > 8 or len({p["passage_id"] for p in first}) != len(first):
                raise ValueError("Invalid retrieval length/deduplication")
            for p in first:
                validator.validate(p)
                if not indexable(p):
                    raise ValueError("Ineligible passage retrieved")
                if not math.isfinite(p["score"]):
                    raise ValueError("Invalid retrieval score")
    counts = Counter(p["doc_id"] for p in passages)
    if any(counts[d["doc_id"]] != d["n_fragmentos"] for d in manifest["documentos"]):
        raise ValueError("Manifest counts mismatch")
    result = {"ok": True, "official_files_unchanged": len(official), "documents": len(texts),
              "passages_valid": len(passages), "nodes_valid": len(nodes), "edges_grounded": len(edges),
              "offsets_verified": len(passages), "deterministic_query_checks": len(queries) * 3,
              "indexed_passages": len(r.passages), "excluded_passages": len(passages) - len(r.passages),
              "hashes": manifest["hashes"], "unresolved_external_nodes": sum(n.get("resolved") is False for n in nodes)}
    write_json(ROOT / "reports/member_a_verification.json", result)
    return result
