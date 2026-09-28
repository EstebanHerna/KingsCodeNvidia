"""Offline development benchmark. This is the ONLY layer allowed to read labels.

Legal-basis retrieval is a proxy: a document-only gold citation does not prove
that a returned passage answers the question. No generation/official QA score
is claimed by this report.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import math
import platform
import sys
from pathlib import Path
import statistics
import time

from scripts.citations import extract
from .common import ROOT, file_hash, read_json, read_jsonl, write_json, write_jsonl
from .retrieval import Retriever


def targets_from_basis(basis: str | None) -> set[tuple]:
    refs = extract(basis or "")
    # Don't give double credit for a bare code alias alongside its article.
    article_bodies = {r[:3] for r in refs if r[3] is not None}
    return {r for r in refs if r[3] is not None or r[:3] not in article_bodies}


def supports(passage: dict, target: tuple) -> bool:
    # A citation mentioned in an unrelated document is NOT evidence that the
    # cited source itself was retrieved. Match canonical metadata only.
    return tuple(passage["canonical_body"]) == target[:3] and (
        target[3] is None or passage.get("article") == target[3])


def ranking_metrics(result: list[dict], targets: set[tuple]) -> dict:
    if not targets:
        return {"evaluable": False}
    found, gains, first = set(), [], None
    recall = {}
    for rank, p in enumerate(result[:10], 1):
        matches = {t for t in targets if supports(p, t)}
        if matches and first is None:
            first = rank
        fresh = matches - found
        gains.append(1 if fresh else 0)
        found |= matches
        if rank in {1, 3, 5, 10}:
            recall[f"Recall@{rank}"] = len(found) / len(targets)
    for k in [1, 3, 5, 10]:
        recall.setdefault(f"Recall@{k}", len(found) / len(targets))
    dcg = sum(g / math.log2(i + 2) for i, g in enumerate(gains))
    idcg = sum(1 / math.log2(i + 2) for i in range(min(10, len(targets))))
    return {"evaluable": True, **recall, "MRR@10": 1 / first if first else 0,
            "nDCG@10_unique_targets": dcg / idcg if idcg else 0,
            "legal_basis_any@10": bool(found), "legal_basis_all@10": found == targets,
            "document_mismatch@1": bool(result) and not any(tuple(result[0]["canonical_body"]) == t[:3] for t in targets)}


def aggregate(rows: list[dict]) -> dict:
    eval_rows = [r for r in rows if r["metrics"]["evaluable"]]
    names = ["Recall@1", "Recall@3", "Recall@5", "Recall@10", "MRR@10", "nDCG@10_unique_targets",
             "legal_basis_any@10", "legal_basis_all@10", "document_mismatch@1"]
    times = sorted(r["latency_ms"] for r in rows)
    return {"questions": len(rows), "evaluable": len(eval_rows),
            **{name: sum(r["metrics"][name] for r in eval_rows) / len(eval_rows) if eval_rows else None for name in names},
            "latency_p50_ms": statistics.median(times) if times else None,
            "latency_p95_ms": times[max(0, math.ceil(len(times) * .95) - 1)] if times else None}


def benchmark(corpus: Path, *, mode: str = "bm25", rerank: bool = False) -> dict:
    sample = read_jsonl(ROOT / "data/sample_50.jsonl")
    retriever = Retriever(corpus, mode=mode, rerank=rerank)
    summaries, all_rows, audit = {}, [], []
    available = defaultdict(set)
    for p in retriever.passages:
        available[tuple(p["canonical_body"])].add(p["article"])
    for r in sample:
        targets = targets_from_basis(r.get("legal_basis"))
        covered = {t for t in targets if t[:3] in available and (t[3] is None or t[3] in available[t[:3]])}
        notes = []
        if not targets:
            notes.append("No unambiguous machine-extractable legal citation; excluded from retrieval metrics")
        if targets and not any(t[3] for t in targets):
            notes.append("Document-level label only; passage relevance unverified")
        if r["id"] == 58:
            notes.append("Original basis conflicts in norm number/year/name; official extractor aliases by number; review separately")
        if r["id"] == 308:
            notes.append("Bare law citation and article absent from acquired source; original label preserved")
        audit.append({"id": r["id"], "legal_basis": r.get("legal_basis"),
                      "targets": sorted(targets, key=str), "covered_targets": sorted(covered, key=str),
                      "coverage": len(covered) / len(targets) if targets else None, "notes": notes})
    for graph_mode in ["off", "auto", "on"]:
        cuda = None
        if retriever.dense or retriever.reranker:
            import torch
            if torch.cuda.is_available() and (retriever.dense.encoder.config if retriever.dense else retriever.reranker.config)["device"].startswith("cuda"):
                cuda = torch.cuda
                cuda.reset_peak_memory_stats()
        rows = []
        for r, gold in zip(sample, audit):
            targets = {tuple(t) for t in gold["targets"]}
            start = time.perf_counter()
            result = retriever.retrieve(r["pregunta"], 10, graph_mode)
            latency = (time.perf_counter() - start) * 1000
            row = {"id": r["id"], "area": r["area"], "format": r["formato"], "graph_mode": graph_mode,
                   "latency_ms": latency, "metrics": ranking_metrics(result, targets),
                   "coverage": gold["coverage"], "graph_active": any(p["retrieval"]["graph_active"] for p in result),
                   "passage_ids": [p["passage_id"] for p in result],
                   "retrieved_targets": [[*p["canonical_body"], p["article"]] for p in result]}
            rows.append(row)
        summaries[graph_mode] = aggregate(rows)
        summaries[graph_mode]["by_area"] = {area: aggregate([r for r in rows if r["area"] == area]) for area in sorted({r["area"] for r in rows})}
        summaries[graph_mode]["by_format"] = {fmt: aggregate([r for r in rows if r["format"] == fmt]) for fmt in sorted({r["format"] for r in rows})}
        summaries[graph_mode]["fully_covered_subset"] = aggregate([r for r in rows if r["coverage"] == 1])
        summaries[graph_mode]["graph_triggered_questions"] = sum(r["graph_active"] for r in rows)
        summaries[graph_mode]["peak_vram_bytes"] = cuda.max_memory_allocated() if cuda else None
        all_rows.extend(rows)
    label_rows = [a for a in audit if a["targets"]]
    manifest = read_json(corpus / "manifest.json")
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "corpus_version": manifest["version"],
              "runtime": {"python": sys.version, "platform": platform.platform()},
              "code_sha256": {p.name: file_hash(p) for p in sorted((ROOT / "kingscode").glob("*.py"))},
              "corpus_hashes": manifest["hashes"], "sample_sha256": file_hash(ROOT / "data/sample_50.jsonl"),
              "config": {"mode": mode, "reranker": rerank, "k1": retriever.bm25.k1, "b": retriever.bm25.b,
                         "candidate_k": retriever.candidate_k, "graph_budget": retriever.graph_budget,
                         "rrf_constant": 60, "graph_seeds": 5, "graph_neighbor_limit": 2,
                         "neural_config": read_json(ROOT / "config/neural.json") if mode != "bm25" or rerank else None,
                         "model_lock": read_json(ROOT / "config/models.lock.json") if mode != "bm25" or rerank else None,
                         "query_fields": ["pregunta"], "decoder": None, "prompt": None,
                         "official_score": None, "seed": 0},
              "coverage": {"evaluable_questions": len(label_rows), "fully_covered_questions": sum(a["coverage"] == 1 for a in label_rows),
                           "macro_target_coverage": sum(a["coverage"] for a in label_rows) / len(label_rows)},
              "runs": summaries,
              "limitations": ["Legal-basis matching proxy, not end-to-end QA score or passage-relevance judgments.",
                              "MRR is truncated at 10; missing ranks contribute zero.",
                              "Official citation parser has known alias/year ambiguity; original labels are not repaired.",
                              "nDCG gains count each distinct gold citation at most once.",
                              "No answer keys are passed to retrieve()."]}
    name = mode + ("_reranker" if rerank else "")
    write_json(ROOT / f"reports/retrieval_{name}.json", report)
    write_jsonl(ROOT / f"reports/retrieval_{name}_per_question.jsonl", all_rows)
    write_json(ROOT / "reports/legal_basis_audit.json", audit)
    write_json(ROOT / f"reports/experiment_{name}.json", report)
    return {"config": report["config"], "coverage": report["coverage"],
            "runs": {k: {m: v for m, v in x.items() if m not in {"by_area", "by_format"}} for k, x in summaries.items()}}
