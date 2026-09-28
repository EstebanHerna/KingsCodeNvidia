"""Retrieval-only matrix and frozen evidence for fair decoder comparisons."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from ..common import ROOT, file_hash, indexable, read_json, read_jsonl, write_json, write_jsonl
from ..reasoning.contracts import Question, load_questions, public_question
from ..reasoning.evaluation import official_hashes
from ..reasoning.experiments import fingerprint
from ..reasoning.guards import check_passages
from ..reasoning.query import normalize_query
from ..reasoning.routing import RetrieverGraphRouter, route_graph


def corpus_identity(corpus=ROOT / "corpus") -> dict:
    manifest = read_json(corpus / "manifest.json")
    for path, expected in manifest["hashes"].items():
        if file_hash(corpus / path) != expected:
            raise ValueError(f"Corpus changed: {path}")
    if file_hash(corpus / "index/bm25.json") != manifest["bm25_sha256"]:
        raise ValueError("BM25 hash mismatch")
    return {"version": manifest["version"], "hashes": manifest["hashes"], "bm25_sha256": manifest["bm25_sha256"]}


def retrieve_evidence(question: Question, retriever, adapter, *, mode: str, k: int):
    query = normalize_query(question.text)
    flat = retriever.retrieve(query.retrieval_text, k, "off")
    decision = route_graph(query, flat) if mode == "auto" else mode
    passages = flat
    if decision != "off":
        adapter.bind(query.retrieval_text, decision)
        passages = retriever.retrieve(query.retrieval_text, k, decision)
    check_passages(passages)
    return passages, {"query": query.record(), "requested_graph_mode": mode, "graph_decision": decision,
                      "flat_passage_ids": [p["passage_id"] for p in flat]}


def score_rankings(records: list[dict], corpus: Path) -> dict:
    # Evaluation boundary only. Labels never reach query/retrieval/decoder data.
    from ..evaluation import aggregate, ranking_metrics, targets_from_basis
    labels = {r["id"]: r for r in read_jsonl(ROOT / "data/sample_50.jsonl")}
    available = [p for p in read_jsonl(corpus / "passages.jsonl") if indexable(p)]
    from ..evaluation import supports
    rows, coverage = [], []
    for record in records:
        targets = targets_from_basis(labels[record["question"]["id"]].get("legal_basis"))
        rows.append({"latency_ms": record["latency_ms"], "metrics": ranking_metrics(record["passages"], targets)})
        if targets:
            coverage.append(sum(any(supports(p, t) for p in available) for t in targets) / len(targets))
    return {**aggregate(rows), "coverage": {"evaluable": len(coverage), "fully_covered": sum(v == 1 for v in coverage),
                                           "macro_target_coverage": sum(coverage) / len(coverage) if coverage else None}}


def run_retrieval(candidate: str, *, output_root=ROOT / "reports/retrieval_matrix", corpus=ROOT / "corpus") -> dict:
    from kingscode import Retriever
    matrix = read_json(ROOT / "config/experiment_matrix.json")
    spec = matrix["retrieval"][candidate]
    identity = corpus_identity(corpus)
    questions = load_questions(ROOT / "data/sample_50.jsonl")
    official = official_hashes()
    cuda = None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory = output_root / f"{stamp}-{candidate}"
    directory.mkdir(parents=True, exist_ok=False)
    record = {"status": "running", "candidate": candidate, "config": spec, "matrix": matrix,
              "corpus": identity, "official_hashes": official, "public_questions_sha256": fingerprint([q.public_record() for q in questions]),
              "decoder": None, "model_lock": read_json(ROOT / "config/models.lock.json"),
              "neural_config": read_json(ROOT / "config/neural.json"), "directory": str(directory.resolve())}
    records = []
    started = perf_counter()
    try:
        if spec["mode"] != "bm25" or spec["rerank"]:
            import torch
            from ..gpu_environment import require_cuda
            require_cuda(torch)
            if not record["neural_config"]["device"].startswith("cuda") or record["neural_config"]["dtype"] != "bfloat16":
                raise ValueError("Configure retrieval for CUDA/BF16 explicitly before neural matrix runs")
            cuda = torch.cuda
            cuda.reset_peak_memory_stats(0)
        adapter = RetrieverGraphRouter()
        retriever = Retriever(corpus, mode=spec["mode"], rerank=spec["rerank"], graph_router=adapter,
                              candidate_k=matrix["candidate_k"], graph_budget=matrix["graph_budget"])
        record["initialization_ms"] = (perf_counter() - started) * 1000
        for question in questions:
            start = perf_counter()
            passages, trace = retrieve_evidence(question, retriever, adapter, mode=spec["graph_mode"], k=matrix["k_metrics"])
            if cuda:
                cuda.synchronize()
            records.append({"question": question.public_record(), "passages": passages, "trace": trace,
                            "latency_ms": (perf_counter() - start) * 1000})
        write_jsonl(directory / "rankings.jsonl", records)
        record.update(status="passed", rankings_sha256=file_hash(directory / "rankings.jsonl"),
                      metrics=score_rankings(records, corpus), peak_vram_bytes=cuda.max_memory_allocated(0) if cuda else None)
    except Exception as exc:
        record.update(status="failed", error={"type": type(exc).__name__, "message": str(exc)}, completed=len(records),
                      peak_vram_bytes=cuda.max_memory_allocated(0) if cuda else None)
    finally:
        record["total_seconds"] = perf_counter() - started
        write_json(directory / "experiment.json", record)
    return record


def freeze_retrieval(run_dir: Path, destination: Path, *, corpus=ROOT / "corpus") -> dict:
    if destination.exists():
        raise FileExistsError("Freeze is immutable; choose a new destination")
    report = read_json(run_dir / "experiment.json")
    if report["status"] != "passed" or report["rankings_sha256"] != file_hash(run_dir / "rankings.jsonl"):
        raise ValueError("Only a successful, unmodified retrieval run can be frozen")
    if report["corpus"] != corpus_identity(corpus):
        raise ValueError("Retrieval corpus snapshot changed")
    records = read_jsonl(run_dir / "rankings.jsonl")
    public = [q.public_record() for q in load_questions(ROOT / "data/sample_50.jsonl")]
    if [r["question"] for r in records] != public or fingerprint(public) != report["public_questions_sha256"]:
        raise ValueError("Freeze must contain exactly the public sample, in order")
    frozen = {"version": "frozen-evidence-v1", "corpus": report["corpus"], "retrieval_config": report["config"],
              "matrix": report["matrix"], "source_report_sha256": file_hash(run_dir / "experiment.json"),
              "source_rankings_sha256": report["rankings_sha256"], "neural_config": report["neural_config"],
              "public_questions_sha256": report["public_questions_sha256"],
              "records": [{"question": r["question"], "passages": r["passages"][:report["matrix"]["k_evidence"]],
                           "trace": r["trace"]} for r in records]}
    frozen["fingerprint"] = fingerprint(frozen)
    write_json(destination, frozen)
    return {"path": str(destination.resolve()), "sha256": file_hash(destination), "fingerprint": frozen["fingerprint"]}


def load_freeze(path: Path, *, corpus=ROOT / "corpus") -> dict:
    frozen = read_json(path)
    if fingerprint({k: v for k, v in frozen.items() if k != "fingerprint"}) != frozen["fingerprint"]:
        raise ValueError("Frozen retrieval integrity failure")
    if frozen["corpus"] != corpus_identity(corpus):
        raise ValueError("Frozen evidence belongs to a different corpus")
    public = [q.public_record() for q in load_questions(ROOT / "data/sample_50.jsonl")]
    if [r["question"] for r in frozen["records"]] != public or fingerprint(public) != frozen["public_questions_sha256"]:
        raise ValueError("Frozen questions differ from the public sample")
    for record in frozen["records"]:
        public_question(record["question"])
        check_passages(record["passages"])
        if len(record["passages"]) > 10:
            raise ValueError("Too many frozen evidence passages")
    return frozen
