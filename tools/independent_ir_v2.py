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
MIN_COMPLETE = 10
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
    """Validate external gold independently from its current corpus mapping."""
    if gold.get("review_status") != "ACCEPTED_RETRIEVAL_GOLD":
        raise ValueError("Gold record is not accepted retrieval gold")
    units = gold.get("external_evidence_units", [])
    unit_ids = [unit.get("external_evidence_unit_id") for unit in units]
    if not units or len(unit_ids) != len(set(unit_ids)) or any(not x for x in unit_ids):
        raise ValueError("Gold must define unique external evidence units")
    source_ids = {src.get("source_id") for src in gold.get("evidence_sources", [])}
    if not source_ids or any(not src.get("source_id") or not src.get("sha256") or
            not src.get("source_url") for src in gold["evidence_sources"]):
        raise ValueError("Gold evidence must be backed by independently sourced material")
    if any(unit.get("source_id") not in source_ids or not unit.get("sha256") or
           not unit.get("source_url") or not unit.get("page") for unit in units):
        raise ValueError("External evidence unit lacks source identity or locator")
    external_sets = gold.get("external_minimal_evidence_sets", [])
    if not external_sets or any(not s or not set(s) <= set(unit_ids) for s in external_sets):
        raise ValueError("Gold must contain valid external minimal evidence sets")
    if gold.get("temporal_review_status") not in {"CURRENTLY_SUPPORTABLE", "HISTORICAL_ONLY", "NOT_APPLICABLE"}:
        raise ValueError("Gold temporal/legal applicability is unresolved")
    state = gold.get("corpus_coverage")
    if state not in COVERAGE_STATES:
        raise ValueError("Accepted gold has invalid corpus coverage")
    corpus_sets = gold.get("corpus_minimal_evidence_sets", [])
    mapping = gold.get("evidence_mapping")
    if not isinstance(mapping, dict) or set(mapping) != set(unit_ids):
        raise ValueError("External-to-corpus evidence mapping must cover every external unit")
    corpus_ids = {pid for passages in mapping.values() for pid in passages}
    if any(not isinstance(ids, list) for ids in mapping.values()):
        raise ValueError("Corpus evidence mapping values must be passage-ID lists")
    if state == "COMPLETE" and (not corpus_sets or any(not s for s in corpus_sets) or
                                 any(not set(s) <= corpus_ids for s in corpus_sets)):
        raise ValueError("COMPLETE coverage requires corpus-only minimal evidence sets")
    if state == "MISSING" and corpus_sets:
        raise ValueError("MISSING coverage cannot claim corpus passage IDs")
    if state == "MISSING" and gold.get("gold_document_ids"):
        raise ValueError("MISSING coverage cannot claim corpus document IDs")


def select_evaluation_subset(candidates: list[dict], gold_rows: list[dict]) -> tuple[list[dict], dict[str, dict]]:
    """Select only accepted gold in the frozen candidate queue; preserve all other candidates."""
    candidate_ids = [row.get("question_id") for row in candidates]
    gold_ids = [row.get("question_id") for row in gold_rows]
    if any(not qid for qid in candidate_ids + gold_ids):
        raise ValueError("Question IDs must be present")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Duplicate frozen candidate question IDs")
    if len(gold_ids) != len(set(gold_ids)):
        raise ValueError("Duplicate gold IDs")
    if not set(gold_ids) <= set(candidate_ids):
        raise ValueError("Gold ID is not a frozen candidate")
    gold = {row["question_id"]: row for row in gold_rows}
    for record in gold.values():
        validate_gold_record(record)
    if len(gold) < MIN_GOLD:
        raise PermissionError(f"GOLD_GATE_LOCKED: {len(gold)} accepted gold; minimum is {MIN_GOLD}")
    selected = [row for row in candidates if row["question_id"] in gold]
    return selected, gold


def hydrate_candidate_questions(candidates: list[dict], pool_rows: list[dict]) -> list[dict]:
    """Resolve exact wording from the ignored local official-source pool by frozen item number."""
    pool = {str(row.get("source_item_number")): row for row in pool_rows}
    if len(pool) != len(pool_rows):
        raise ValueError("Duplicate item numbers in ignored official question pool")
    hydrated = []
    for candidate in candidates:
        row = dict(candidate)
        if isinstance(row.get("question"), str) and row["question"].strip():
            hydrated.append(row)
            continue
        item = pool.get(str(row.get("source_item_number")))
        if not item or not isinstance(item.get("question_text"), str):
            raise ValueError(f"Exact source wording unavailable for {row.get('question_id')}")
        digest = hashlib.sha256(item["question_text"].encode("utf-8")).hexdigest()
        if digest != row.get("question_text_sha256"):
            raise ValueError(f"Ignored pool wording hash mismatch for {row.get('question_id')}")
        row["question"] = item["question_text"]
        hydrated.append(row)
    return hydrated


def preflight() -> tuple[dict, list[dict], dict[str, dict]]:
    manifest = read_json(BENCH / "manifest.json")
    candidates = read_jsonl(BENCH / "questions/dev.jsonl")
    gold_rows = read_jsonl(BENCH / "gold/dev.jsonl")
    if manifest.get("benchmark") != "KC-COL-IR-v0.1":
        raise ValueError("Unexpected benchmark identity")
    if manifest.get("question_manifest_sha256") != file_hash(BENCH / "questions/dev.jsonl"):
        raise ValueError("DEV questions hash mismatch")
    if manifest.get("source_manifest_sha256") != file_hash(BENCH / "source_manifest.jsonl"):
        raise ValueError("Source manifest hash mismatch")
    if manifest["counts"].get("accepted_retrieval_gold", 0) != len(gold_rows):
        raise ValueError("Accepted-gold count mismatch")
    if any(q.get("split") == "VALIDATION" or q.get("institution_family") == "universidad_libre_preparatorios"
           for q in candidates):
        raise ValueError("Validation-family question leakage")
    evaluation_questions, gold = select_evaluation_subset(candidates, gold_rows)
    sample = read_json(BENCH / "sampling_manifest.json")
    pool_path = ROOT / "tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl"
    if not pool_path.exists() or file_hash(pool_path) != sample.get("pool_artifact_sha256"):
        raise ValueError("Frozen ignored official question pool missing or hash mismatch")
    evaluation_questions = hydrate_candidate_questions(evaluation_questions, read_jsonl(pool_path))
    population = metric_population(list(gold.values()))
    gold_gate = len(gold) >= MIN_GOLD
    ranking_gate = population["ranking_n"] >= MIN_COMPLETE
    if not gold_gate:
        raise PermissionError(f"GOLD_GATE_LOCKED: {len(gold)} accepted gold; minimum is {MIN_GOLD}")
    if not ranking_gate:
        raise PermissionError(f"RANKING_GATE_LOCKED: {population['ranking_n']} COMPLETE corpus gold; minimum is {MIN_COMPLETE}")
    if manifest.get("gold_gate", {}).get("unlocked") is not True:
        raise PermissionError("GOLD_GATE_LOCKED: manifest has not recorded independent gold review")
    if manifest.get("ranking_gate", {}).get("unlocked") is not True:
        raise PermissionError("RANKING_GATE_LOCKED: manifest has not recorded corpus-complete gold review")
    if manifest.get("cuda_ready") is not True or manifest.get("baseline_gate", {}).get("unlocked") is not True:
        raise PermissionError("CUDA_READY=false: ranking/configuration comparison remains locked")
    return manifest, evaluation_questions, gold

def _dcg(ids: list[str], gold: set[str]) -> float:
    return sum((1.0 if item in gold else 0.0) / math.log2(rank + 2)
               for rank, item in enumerate(ids[:10]))


def score(ranked: list[dict], gold: dict, corpus_docs: set[str]) -> dict:
    if gold.get("corpus_coverage") != "COMPLETE":
        raise ValueError("Pure ranking metrics require COMPLETE frozen-corpus coverage")
    ids = [p["passage_id"] for p in ranked]
    docs = [p.get("canonical_document_id") or p["doc_id"] for p in ranked]
    alternatives = gold["corpus_minimal_evidence_sets"]
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
    ranking_questions = [q for q in questions if gold[q["question_id"]]["corpus_coverage"] == "COMPLETE"]
    for q in ranking_questions:
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
        elif not any(set(s) & set(p["passage_id"] for p in results[:10]) for s in g["corpus_minimal_evidence_sets"]):
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
        manifest = read_json(BENCH / "manifest.json")
        rows = read_jsonl(BENCH / "gold/dev.jsonl")
        population = metric_population(rows)
        print(json.dumps({"status": "GATED", "benchmark": "KC-COL-IR-v0.1",
                          "cuda_ready": manifest["cuda_ready"],
                          "gold_gate": {"accepted": len(rows), "minimum": MIN_GOLD, "unlocked": len(rows) >= MIN_GOLD},
                          "ranking_gate": {"ranking_n": population["ranking_n"], "minimum_complete": MIN_COMPLETE,
                                           "unlocked": population["ranking_n"] >= MIN_COMPLETE},
                          "candidate_count": len(read_jsonl(BENCH / "questions/dev.jsonl")),
                          "validated_subset_only": True}, indent=2))
    elif not args.component:
        parser.error("run requires --component C0|C1|C2|C3")
    else:
        print(json.dumps(run(args.component, args.config), ensure_ascii=False, indent=2))
