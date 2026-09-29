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
COVERAGE_STATES = {"COMPLETE", "PARTIAL", "MISSING", "AMBIGUOUS"}


def metric_population(gold_rows: list[dict]) -> dict:
    """Return coverage denominators and IDs eligible for pure ranking metrics."""
    by_state = {state: [] for state in COVERAGE_STATES}
    for row in gold_rows:
        state = row.get("corpus_coverage")
        if state not in COVERAGE_STATES:
            raise ValueError(f"Accepted gold has invalid corpus_coverage: {state!r}")
        by_state[state].append(row["question_id"])
    total = len(gold_rows)
    return {
        "coverage_n": total,
        "coverage_counts": {state: len(ids) for state, ids in sorted(by_state.items())},
        "ranking_n": len(by_state["COMPLETE"]),
        "ranking_question_ids": sorted(by_state["COMPLETE"]),
        "corpus_missing_rate": len(by_state["MISSING"]) / total if total else None,
    }


def validate_gold_record(gold: dict) -> None:
    """Validate gold from its independent sources without consulting the corpus."""
    if gold.get("review_status") != "ACCEPTED_RETRIEVAL_GOLD":
        raise ValueError("Gold record is not accepted retrieval gold")
    if not gold.get("minimal_evidence_sets") or any(not s for s in gold["minimal_evidence_sets"]):
        raise ValueError("Gold must contain nonempty alternative minimal evidence sets")
    if not gold.get("evidence_sources") or any(not src.get("source_id") or not src.get("sha256") or
            not src.get("source_url") for src in gold["evidence_sources"]):
        raise ValueError("Gold evidence must be backed by independently sourced primary material")
    if gold.get("temporal_review_status") not in {"CURRENTLY_SUPPORTABLE", "HISTORICAL_ONLY", "NOT_APPLICABLE"}:
        raise ValueError("Gold temporal/legal applicability is unresolved")
    if gold.get("corpus_coverage") not in COVERAGE_STATES:
        raise ValueError("Accepted gold has invalid corpus coverage")


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
    if any(q.get("review_status") != "ACCEPTED_RETRIEVAL_GOLD" or q.get("temporal_review_status") not in
           {"CURRENTLY_SUPPORTABLE", "HISTORICAL_ONLY", "NOT_APPLICABLE"} for q in questions):
        raise ValueError("DEV contains unreviewed or temporally uncertain items")
    if any(q.get("split") == "VALIDATION" or q.get("institution_family") == "universidad_libre_preparatorios"
           for q in questions):
        raise ValueError("Validation-family question leakage")
    for record in gold.values():
        validate_gold_record(record)
    return manifest, questions, gold


def _dcg(ids: list[str], gold: set[str]) -> float:
    return sum((1.0 if item in gold else 0.0) / math.log2(rank + 2)
               for rank, item in enumerate(ids[:10]))


def score(ranked: list[dict], gold: dict, corpus_docs: set[str]) -> dict:
    if gold.get("corpus_coverage") != "COMPLETE":
        raise ValueError("Pure ranking metrics require COMPLETE frozen-corpus coverage")
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
        metric = score(results, g, corpus_docs) if g["corpus_coverage"] == "COMPLETE" else None
        recovered_docs = {p.get("canonical_document_id") or p["doc_id"] for p in results[:10]}
        if g["corpus_coverage"] in {"MISSING", "PARTIAL"}:
            failure = "corpus_missing"
        elif g["corpus_coverage"] == "AMBIGUOUS":
            failure = "ambiguous_ground_truth"
        elif metric["Evidence Completeness@8"]:
            failure = "success"
        elif not (set(g["gold_document_ids"]) & recovered_docs):
            failure = "wrong_document"
        elif not any(set(s) & set(p["passage_id"] for p in results[:10]) for s in g["minimal_evidence_sets"]):
            failure = "correct_document_wrong_passage"
        else:
            failure = "ranking_failure"
        records.append({"question_id": q["question_id"], "ranking": ranked,
                        "metrics": metric, "latency_ms": latency, "failure_classification": failure})
    def pct(p):
        return sorted(latencies)[max(0, math.ceil(len(latencies) * p) - 1)] if latencies else None
    rank_rows = [row for row in records if row["metrics"] is not None]
    metrics = sorted({k for row in rank_rows for k in row["metrics"] if not k.endswith("diagnostic")})
    aggregate = {k: statistics.mean(row["metrics"][k] for row in rank_rows) for k in metrics} if rank_rows else {}
    populations = metric_population(list(gold.values()))
    coverage_n = populations["coverage_n"]
    coverage_rates = {state: (count / coverage_n if coverage_n else None)
                      for state, count in populations["coverage_counts"].items()}
    aggregate.update({"coverage_n": coverage_n, "ranking_n": populations["ranking_n"],
                      "coverage_counts": populations["coverage_counts"],
                      "coverage_rates": coverage_rates,
                      "Corpus Missing Rate": coverage_rates["MISSING"],
                      "Corpus Complete Rate": coverage_rates["COMPLETE"],
                      "Corpus Partial Rate": coverage_rates["PARTIAL"],
                      "metric_denominators": {name: populations["ranking_n"] for name in metrics}})
    aggregate.update({"latency_p50_ms": statistics.median(latencies), "latency_p95_ms": pct(.95),
                      "questions": len(records), "ranking_questions": len(rank_rows)})
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
