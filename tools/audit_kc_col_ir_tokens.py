"""CPU-only token-length audit for the frozen KC-COL-IR controlled profile.

Loads only the pinned local tokenizers. It does not load model weights, query
retrieval, initialize CUDA, or write into the corpus/profile.
"""
from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, file_hash, read_json, read_jsonl, write_json
from kingscode.model_assets import resolve_model, verify_snapshot
from tools import independent_ir_v2 as benchmark


BENCH = ROOT / "benchmarks/kc_col_ir_v0.1"
PROFILE_DIR = ROOT / "tmp/kc_col_ir_v0.1/controlled_cuj2026_v1"


def percentile(values: list[int], p: float) -> int | None:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * p) - 1)] if ordered else None


def summary(values: list[int], max_length: int) -> dict:
    return {
        "count": len(values),
        "min": min(values) if values else None,
        "p50": int(statistics.median(values)) if values else None,
        "p95": percentile(values, 0.95),
        "max": max(values) if values else None,
        "configured_max_length": max_length,
        "over_limit_count": sum(value > max_length for value in values),
    }


def accepted_questions() -> list[dict]:
    candidates = read_jsonl(BENCH / "questions/dev.jsonl")
    candidate_ids = {row["question_id"] for row in candidates}
    for row in read_jsonl(BENCH / "review/expansion_batch_1_questions.jsonl"):
        if row["question_id"] not in candidate_ids:
            candidates.append(row)
            candidate_ids.add(row["question_id"])
    gold = read_jsonl(BENCH / "gold/dev.jsonl")
    benchmark.verify_controlled_profile_files(gold)
    selected, _ = benchmark.select_evaluation_subset(candidates, gold)
    pool = read_jsonl(ROOT / "tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl")
    return benchmark.hydrate_candidate_questions(selected, pool)


def load_tokenizer(repo_id: str, revision: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(
        repo_id,
        revision=revision,
        cache_dir=str(ROOT / "models"),
        local_files_only=True,
        trust_remote_code=False,
        padding_side="left",
    )


def run(output: Path) -> dict:
    neural = read_json(ROOT / "config/neural.json")
    locks = read_json(ROOT / "config/models.lock.json")
    profile = read_json(BENCH / "review/controlled_cuj2026_v1_profile.json")
    if profile.get("build_status") != "MATERIALIZED_VERIFIED":
        raise RuntimeError("CONTROLLED_PROFILE_NOT_MATERIALIZED")
    passages_path = PROFILE_DIR / "passages.jsonl"
    if file_hash(passages_path) != profile.get("passages_sha256"):
        raise ValueError("CONTROLLED_PROFILE_PASSAGES_HASH_MISMATCH")
    passages = read_jsonl(passages_path)
    questions = accepted_questions()

    encoder_id = neural["embedding_model"]
    reranker_id = neural["reranker_model"]
    encoder_revision = locks[encoder_id]["revision"]
    reranker_revision = locks[reranker_id]["revision"]
    if neural.get("local_files_only") is not True:
        raise RuntimeError("TOKEN_AUDIT_REQUIRES_LOCAL_SNAPSHOTS")
    encoder_snapshot = verify_snapshot(resolve_model(encoder_id))
    reranker_snapshot = verify_snapshot(resolve_model(reranker_id))
    encoder = load_tokenizer(encoder_id, encoder_revision)
    reranker = load_tokenizer(reranker_id, reranker_revision)

    encoder_query_lengths = []
    for question in questions:
        text = f"Instruct: {neural['instruction']}\nQuery: {question['question']}"
        encoder_query_lengths.append(len(encoder(text, truncation=False)["input_ids"]))
    encoder_passage_lengths = [
        len(encoder(passage["text"], truncation=False)["input_ids"])
        for passage in passages
    ]

    prefix = reranker.encode(
        '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n',
        add_special_tokens=False,
    )
    suffix = reranker.encode(
        '<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n',
        add_special_tokens=False,
    )
    reranker_pair_lengths = []
    pair_records = []
    for question in questions:
        for passage in passages:
            payload = (
                f"<Instruct>: {neural['instruction']}\n<Query>: {question['question']}"
                f"\n<Document>: {passage['text']}"
            )
            payload_ids = reranker(payload, add_special_tokens=False, truncation=False)["input_ids"]
            token_count = len(prefix) + len(payload_ids) + len(suffix)
            reranker_pair_lengths.append(token_count)
            if token_count > neural["max_length"]:
                pair_records.append({
                    "question_id": question["question_id"],
                    "passage_id": passage.get("passage_id"),
                    "document_id": passage.get("doc_id"),
                    "page": passage.get("page"),
                    "tokens": token_count,
                })

    result = {
        "audit": "KC-COL-IR-CUJ2026 token-length audit",
        "status": "PASS" if not pair_records and max(encoder_query_lengths + encoder_passage_lengths, default=0) <= neural["max_length"] else "OVER_LIMIT",
        "scope": "Pinned Qwen encoder and reranker inputs only; decoder prompt/context audit requires a selected retrieval freeze.",
        "execution": {"cuda_initialized": False, "model_weights_loaded": False, "retrieval_queries_run": 0},
        "identity": {
            "benchmark_manifest_sha256": file_hash(BENCH / "manifest.json"),
            "controlled_profile_sha256": file_hash(BENCH / "review/controlled_cuj2026_v1_profile.json"),
            "controlled_passages_sha256": file_hash(passages_path),
            "question_manifest_sha256": file_hash(BENCH / "questions/dev.jsonl"),
            "gold_sha256": file_hash(BENCH / "gold/dev.jsonl"),
            "encoder": {"repo_id": encoder_id, "revision": encoder_revision},
            "reranker": {"repo_id": reranker_id, "revision": reranker_revision},
            "encoder_snapshot_manifest_sha256": encoder_snapshot["manifest_sha256"],
            "reranker_snapshot_manifest_sha256": reranker_snapshot["manifest_sha256"],
            "max_length": neural["max_length"],
        },
        "counts": {"accepted_questions": len(questions), "controlled_passages": len(passages)},
        "encoder_query_tokens": summary(encoder_query_lengths, neural["max_length"]),
        "encoder_passage_tokens": summary(encoder_passage_lengths, neural["max_length"]),
        "reranker_query_passage_pair_tokens": summary(reranker_pair_lengths, neural["max_length"]),
        "reranker_over_limit_examples": pair_records[:20],
    }
    write_json(output, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/kc_col_ir_v0.1/token_audit.json")
    args = parser.parse_args()
    report = run(args.output)
    print(read_json(args.output))
    if report["status"] != "PASS":
        raise SystemExit(2)
