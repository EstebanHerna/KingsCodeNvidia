"""Gated independent KC-COL-IR runner. Refuses incomplete/unfrozen gold."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, file_hash, read_json, read_jsonl, write_json

BENCH = ROOT / "benchmarks/kc_col_ir_v0.1"
MIN_GOLD = 10
COMPONENTS = ("C0", "C1", "C2", "C3")


def preflight() -> tuple[dict, list[dict], dict[str, dict]]:
    manifest = read_json(BENCH / "manifest.json")
    questions = read_jsonl(BENCH / "questions/dev.jsonl")
    gold_rows = read_jsonl(BENCH / "gold/dev.jsonl")
    if manifest.get("benchmark") != "KC-COL-IR-v0.1":
        raise ValueError("Unexpected benchmark identity")
    if manifest.get("cuda_ready") is not True or manifest.get("baseline_gate", {}).get("unlocked") is not True:
        raise PermissionError("BASELINE_GATE_LOCKED: CUDA_READY requires >=10 accepted independent DEV retrieval-gold items")
    if len(gold_rows) < MIN_GOLD or manifest["counts"].get("accepted_retrieval_gold", 0) < MIN_GOLD:
        raise PermissionError("BASELINE_GATE_LOCKED: fewer than 10 accepted DEV retrieval-gold items")
    if manifest.get("question_manifest_sha256") != file_hash(BENCH / "questions/dev.jsonl"):
        raise ValueError("DEV questions hash mismatch")
    if manifest.get("source_manifest_sha256") != file_hash(BENCH / "source_manifest.jsonl"):
        raise ValueError("Source manifest hash mismatch")
    if len(questions) != len(gold_rows):
        raise ValueError("Question/gold row count mismatch")
    gold = {row["question_id"]: row for row in gold_rows}
    if len(gold) != len(gold_rows) or set(gold) != {row["question_id"] for row in questions}:
        raise ValueError("Question/gold ID mismatch or duplicate")
    if any(q.get("review_status") != "ACCEPTED" or q.get("temporal_review_status") not in
           {"CURRENTLY_SUPPORTABLE", "HISTORICAL_ONLY", "NOT_APPLICABLE"} for q in questions):
        raise ValueError("DEV contains unreviewed or temporally uncertain items")
    if any(q.get("split") == "VALIDATION" or q.get("institution_family") == "universidad_libre_preparatorios"
           for q in questions):
        raise ValueError("Validation-family question leakage")
    if any(g.get("review_status") != "ACCEPTED" or not g.get("minimal_evidence_sets") for g in gold.values()):
        raise ValueError("Gold must contain accepted alternative minimal evidence sets")
    return manifest, questions, gold


def _dcg(ids: list[str], gold: set[str]) -> float:
    return sum((1.0 if item in gold else 0.0) / math.log2(rank + 2)
               for rank, item in enumerate(ids[:10]))


def score(ranked: list[dict], gold: dict, corpus_docs: set[str]) -> dict:
    ids = [p["passage_id"] for p in ranked]
    docs = [p.get("canonical_document_id") or p["doc_id"] for p in ranked]
    alternatives = gold["minimal_evidence_sets"]
    union = set().union(*(set(s) for s in alternatives))
    found8 = set(ids[:8]); found10 = set(ids[:10])
    complete = any(set(s) <= found8 for s in alternatives)
    complete10 = any(set(s) <= found10 for s in alternatives)
    first = next((i for i, item in enumerate(ids[:10], 1) if item in union), None)
    dcg = _dcg(ids, union)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(union), 10)))
    gold_docs = set(gold["gold_document_ids"])
    found_docs = set(docs[:10])
    return {"Evidence Completeness@8": float(complete), "Complete Evidence Set@8": float(complete),
            "Recall@10": len(found10 & union) / len(union) if union else 0.0,
            "MRR@10": 1 / first if first else 0.0, "nDCG@10": dcg / ideal if ideal else 0.0,
            "Document Recall": len(found_docs & gold_docs) / len(gold_docs) if gold_docs else 0.0,
            "Corpus Missing Rate": float(not (gold_docs & corpus_docs)),
            "complete_set_at_10_diagnostic": complete10}


def run(component: str, config_path: Path) -> dict:
    if component not in COMPONENTS:
        raise ValueError(f"component must be one of {COMPONENTS}")
    manifest, questions, gold = preflight()
    cfg = read_json(config_path)
    from kingscode.retrieval import Retriever
    spec = cfg["components"][component]
    started = time.perf_counter()
    if spec["mode"] == "bm25":
        retriever = Retriever(ROOT / cfg["corpus"], mode="bm25", rerank=False,
                              candidate_k=cfg["candidate_k"], graph_budget=0, exact_locator=False,
                              graph_router=lambda _: False)
    else:
        from kingscode.benchmark_runtime import NeuralRuntime
        # The shared neural runtime verifies immutable model snapshots, CUDA,
        # BF16 and the dense index before the first question is executed.
        from kingscode.benchmark_runtime import ENCODERS, RERANKER
        from kingscode.neural import configuration
        neural = configuration()
        if neural.get("embedding_model") != ENCODERS["QWEN"] or (spec["reranker"] and neural.get("reranker_model") != RERANKER):
            raise ValueError("Locked Qwen encoder/reranker configuration required")
        runtime_cfg = {"mode": spec["mode"], "rerank": bool(spec["reranker"]), "encoder": "QWEN",
                       "graph_mode": "off", "graph_budget": 0, "candidate_k": cfg["candidate_k"],
                       "k_metrics": cfg["metrics_k"], "evidence_k": cfg["evidence_k"],
                       "rrf_constant": 60, "seed": 0, "diagnostic": False,
                       "query_transform": "none; exact source wording only"}
        runtime = NeuralRuntime(ROOT / cfg["corpus"], runtime_cfg)
        retriever = runtime
    passages = read_jsonl(ROOT / cfg["corpus"] / "passages.jsonl")
    corpus_docs = {p.get("canonical_document_id") or p["doc_id"] for p in passages}
    records, latencies = [], []
    out_k = max(cfg["metrics_k"], cfg["evidence_k"])
    for q in questions:
        question = q.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Question text unavailable for {q['question_id']}; exact wording review incomplete")
        t0 = time.perf_counter()
        if component == "C0":
            results = retriever.retrieve(question, out_k, "off")
        else:
            results = retriever.retrieve(question, out_k)
        latency = (time.perf_counter() - t0) * 1000; latencies.append(latency)
        g = gold[q["question_id"]]
        ranked = [{"rank": rank, "passage_id": p["passage_id"],
                   "doc_id": p["doc_id"], "canonical_document_id": p.get("canonical_document_id"),
                   "scores": p.get("scores", {}), "source_url": p.get("source_url")}
                  for rank, p in enumerate(results, 1)]
        metric = score(results, g, corpus_docs)
        recovered_docs = {p.get("canonical_document_id") or p["doc_id"] for p in results[:10]}
        failure = "success" if metric["Evidence Completeness@8"] else (
            "corpus_missing" if not (set(g["gold_document_ids"]) & corpus_docs) else
            "wrong_document" if not (set(g["gold_document_ids"]) & recovered_docs) else
            "ranking_or_evidence_incomplete")
        records.append({"question_id": q["question_id"], "ranking": ranked,
                        "metrics": metric, "latency_ms": latency, "failure_classification": failure})
    def pct(p):
        return sorted(latencies)[max(0, math.ceil(len(latencies) * p) - 1)] if latencies else None
    metrics = sorted({k for row in records for k in row["metrics"] if not k.endswith("diagnostic")})
    aggregate = {k: statistics.mean(row["metrics"][k] for row in records) for k in metrics}
    aggregate.update({"latency_p50_ms": statistics.median(latencies), "latency_p95_ms": pct(.95),
                      "questions": len(records)})
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    result = {"benchmark": "KC-COL-IR-v0.1", "component": component, "split": "DEV",
              "git_sha": head, "benchmark_manifest_sha256": file_hash(BENCH / "manifest.json"),
              "corpus_manifest_sha256": file_hash(ROOT / cfg["corpus"] / "manifest.json"),
              "config": spec, "graph_mode": "off", "metrics": aggregate,
              "per_question": records, "initialization_seconds": time.perf_counter() - started}
    output = ROOT / cfg["output_dir"] / component
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "report.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "run"))
    parser.add_argument("--component", choices=COMPONENTS)
    parser.add_argument("--config", type=Path, default=BENCH / "runner.json")
    args = parser.parse_args()
    if args.command == "check":
        print(json.dumps({"status": "GATED", "benchmark": "KC-COL-IR-v0.1",
                          "cuda_ready": read_json(BENCH / "manifest.json")["cuda_ready"],
                          "minimum_accepted_gold": MIN_GOLD}, indent=2))
    elif not args.component:
        parser.error("run requires --component C0|C1|C2|C3")
    else:
        print(json.dumps(run(args.component, args.config), ensure_ascii=False, indent=2))
